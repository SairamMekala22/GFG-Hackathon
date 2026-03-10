"""Root cause analysis for period-over-period changes."""

from __future__ import annotations

import re

import pandas as pd

from services.dataframe_service import categorical_columns, coerce_datetime, infer_time_column, numeric_columns


def _pick_metric_from_prompt(prompt: str, metrics: list[str]) -> str | None:
    lowered = prompt.lower()
    ranked = sorted(metrics, key=len, reverse=True)
    for metric in ranked:
        if metric.lower() in lowered:
            return metric
    return None


def _period_granularity(user_prompt: str, timestamps: pd.Series) -> str:
    prompt = user_prompt.lower()
    if "quarter" in prompt:
        return "Q"
    if any(month in prompt for month in (
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    )):
        return "M"
    unique_days = timestamps.dt.normalize().nunique()
    unique_months = timestamps.dt.to_period("M").nunique()
    return "M" if unique_days > unique_months else "D"


def _parse_period_reference(user_prompt: str, timestamps: pd.Series) -> tuple[pd.Period | None, pd.Period | None, str]:
    prompt = user_prompt.lower()
    valid = timestamps.dropna().sort_values()
    if len(valid) < 2:
        return None, None, "M"

    granularity = _period_granularity(user_prompt, valid)
    periods = valid.dt.to_period(granularity)
    unique_periods = periods.drop_duplicates().sort_values()
    if len(unique_periods) < 2:
        return None, None, granularity

    current = unique_periods.iloc[-1]
    previous = unique_periods.iloc[-2]

    month_names = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    for name, month in month_names.items():
        if name in prompt:
            current_matches = unique_periods[unique_periods.dt.month == month]
            if len(current_matches):
                current = current_matches.iloc[-1]
                previous_matches = unique_periods[unique_periods < current]
                previous = previous_matches.iloc[-1] if len(previous_matches) else None
            break
    quarter_match = re.search(r"q([1-4])", prompt)
    if quarter_match:
        quarter = int(quarter_match.group(1))
        quarter_matches = unique_periods[unique_periods.dt.quarter == quarter]
        if len(quarter_matches):
            current = quarter_matches.iloc[-1]
            previous_matches = unique_periods[unique_periods < current]
            previous = previous_matches.iloc[-1] if len(previous_matches) else None
    return current, previous, granularity


def analyze_root_causes(dataframe: pd.DataFrame, user_prompt: str) -> dict:
    """Identify biggest contributors to a change between comparable periods."""
    time_column = infer_time_column(dataframe)
    metrics = [col for col in numeric_columns(dataframe) if col.lower() not in {"id", "index"}]
    metric = _pick_metric_from_prompt(user_prompt, metrics) or next(
        (col for col in metrics if any(token in col.lower() for token in ("revenue", "sales", "conversion", "lead", "click", "roi", "cost"))),
        metrics[0] if metrics else None,
    )
    dimensions = categorical_columns(dataframe)
    if not time_column or not metric or not dimensions:
        return {"root_causes": [], "metric": metric, "time_column": time_column, "confidence": "low"}

    timestamps = coerce_datetime(dataframe, time_column)
    values = pd.to_numeric(dataframe[metric], errors="coerce")
    working = dataframe.copy()
    working[time_column] = timestamps
    working[metric] = values
    working = working.dropna(subset=[time_column, metric])
    if len(working) < 4:
        return {"root_causes": [], "metric": metric, "time_column": time_column, "confidence": "low"}

    current_period, previous_period, granularity = _parse_period_reference(user_prompt, working[time_column])
    if current_period is None or previous_period is None:
        return {"root_causes": [], "metric": metric, "time_column": time_column, "confidence": "low"}

    working = working.assign(period=working[time_column].dt.to_period(granularity))
    current_df = working[working["period"] == current_period]
    previous_df = working[working["period"] == previous_period]
    overall_current = float(current_df[metric].sum())
    overall_previous = float(previous_df[metric].sum())
    overall_delta = overall_current - overall_previous
    if overall_delta == 0:
        return {
            "root_causes": ["No material change detected between the selected comparison periods."],
            "metric": metric,
            "time_column": time_column,
            "confidence": "high",
            "current_period": str(current_period),
            "previous_period": str(previous_period),
        }

    best_dimension = None
    best_combined = None
    best_score = -1.0
    max_cardinality = 20

    for dimension in dimensions:
        if working[dimension].nunique(dropna=True) > max_cardinality:
            continue
        current_grouped = current_df.groupby(dimension)[metric].sum()
        previous_grouped = previous_df.groupby(dimension)[metric].sum()
        combined = (
            pd.concat(
                [
                    previous_grouped.rename("previous"),
                    current_grouped.rename("current"),
                ],
                axis=1,
            )
            .fillna(0)
            .assign(delta=lambda frame: frame["current"] - frame["previous"])
        )
        if combined.empty:
            continue
        explained = combined["delta"].abs().sum()
        score = explained / max(abs(overall_delta), 1)
        if score > best_score:
            best_score = score
            best_dimension = dimension
            best_combined = combined

    if best_dimension is None or best_combined is None:
        return {"root_causes": [], "metric": metric, "time_column": time_column, "confidence": "low"}

    combined = best_combined.sort_values("delta")
    root_causes = []
    target_negative = overall_delta < 0
    ranked = combined.sort_values("delta", ascending=target_negative)
    contributors = ranked[ranked["delta"] < 0] if overall_delta < 0 else ranked[ranked["delta"] > 0]
    offsets = ranked[ranked["delta"] > 0] if overall_delta < 0 else ranked[ranked["delta"] < 0]
    contributor_base = max(abs(float(contributors["delta"].sum())) if len(contributors) else 0.0, 1.0)
    offset_base = max(abs(float(offsets["delta"].sum())) if len(offsets) else 0.0, 1.0)

    for index, row in contributors.head(3).iterrows():
        contribution_share = abs(row["delta"]) / contributor_base * 100
        baseline_pct = (abs(row["delta"]) / row["previous"] * 100) if row["previous"] else 0
        direction = "decline" if overall_delta < 0 else "increase"
        root_causes.append(
            f"{index} represented {contribution_share:.1f}% of the segment-level {direction}, with {metric.replace('_', ' ')} changing by {baseline_pct:.1f}% versus the prior period."
        )

    for index, row in offsets.head(2).iterrows():
        contribution_share = abs(row["delta"]) / offset_base * 100
        if contribution_share < 5:
            continue
        action = "offset the drop" if overall_delta < 0 else "tempered the increase"
        root_causes.append(
            f"{index} {action}, accounting for {contribution_share:.1f}% of the opposing movement."
        )

    confidence = "high" if len(current_df) >= 10 and best_score >= 0.8 else "medium" if best_score >= 0.4 else "low"
    if not root_causes:
        root_causes = [
            "No reliable segment-level driver could be isolated from the available comparison periods."
        ]

    return {
        "root_causes": root_causes[:5],
        "metric": metric,
        "time_column": time_column,
        "dimension": best_dimension,
        "current_period": str(current_period),
        "previous_period": str(previous_period),
        "overall_delta": round(overall_delta, 2),
        "confidence": confidence,
    }

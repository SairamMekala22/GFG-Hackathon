"""Grounded chart explanation helpers."""

from __future__ import annotations

from typing import Any

import pandas as pd

from services.anomaly_service import detect_anomalies
from services.gemini_service import gemini_service
from services.insight_generator import choose_primary_metric, format_metric_value


def _time_like(column: str | None) -> bool:
    if not column:
        return False
    lowered = column.lower()
    return any(token in lowered for token in ("date", "time", "month", "year", "period"))


def _fallback_explanation(dataframe: pd.DataFrame, chart_type: str, metadata: dict[str, Any]) -> list[str]:
    if dataframe.empty:
        return ["This chart has no data points yet, so there is nothing reliable to explain."]

    rows = dataframe.to_dict(orient="records")
    x_axis = metadata.get("x_axis")
    y_axis = metadata.get("y_axis") or choose_primary_metric(rows[0])
    explanations: list[str] = []

    if y_axis and y_axis in dataframe.columns:
        numeric_values = pd.to_numeric(dataframe[y_axis], errors="coerce")
        valid = dataframe.assign(_metric=numeric_values).dropna(subset=["_metric"])
        if not valid.empty:
            peak = valid.loc[valid["_metric"].idxmax()]
            trough = valid.loc[valid["_metric"].idxmin()]
            explanations.append(
                f"{y_axis.replace('_', ' ').title()} ranges from {format_metric_value(trough['_metric'])} to {format_metric_value(peak['_metric'])}."
            )

            if x_axis and x_axis in valid.columns:
                explanations.append(
                    f"The highest point occurs at {peak[x_axis]} and the weakest point occurs at {trough[x_axis]}."
                )

            if _time_like(x_axis) and len(valid) > 1:
                first = valid.iloc[0]
                last = valid.iloc[-1]
                change = float(last["_metric"] - first["_metric"])
                pct = (change / float(first["_metric"]) * 100) if first["_metric"] else 0
                direction = "increased" if change >= 0 else "decreased"
                explanations.append(
                    f"The overall trend {direction} by {abs(pct):.1f}% from the first point to the latest point."
                )

    anomalies = detect_anomalies(
        dataframe,
        metric=y_axis if y_axis in dataframe.columns else None,
        time_column=x_axis if x_axis in dataframe.columns else None,
    ).get("anomalies", [])
    if anomalies:
        top_anomaly = max(anomalies, key=lambda item: item.get("score", 0))
        point = top_anomaly.get(x_axis) if x_axis else None
        explanations.append(
            f"An unusual movement was detected at {point or 'one data point'}, with {y_axis or 'the primary metric'} reaching {format_metric_value(top_anomaly.get('value'))}."
        )

    if chart_type == "pie" and x_axis and y_axis and x_axis in dataframe.columns and y_axis in dataframe.columns:
        totals = dataframe[[x_axis, y_axis]].copy()
        totals[y_axis] = pd.to_numeric(totals[y_axis], errors="coerce")
        totals = totals.dropna().sort_values(y_axis, ascending=False)
        if not totals.empty:
            leader = totals.iloc[0]
            share = (float(leader[y_axis]) / float(totals[y_axis].sum()) * 100) if float(totals[y_axis].sum()) else 0
            explanations.append(
                f"{leader[x_axis]} is the largest slice, contributing {share:.1f}% of the total."
            )

    return explanations[:4] or [
        "The chart summarizes the returned query result and is ready for further drill-down."
    ]


def explain_chart(chart_data: list[dict[str, Any]], chart_type: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Explain a rendered chart using grounded stats with optional Gemini phrasing."""
    metadata = metadata or {}
    dataframe = pd.DataFrame(chart_data or [])
    explanations = _fallback_explanation(dataframe, chart_type, metadata)

    if not dataframe.empty and gemini_service.is_configured():
        prompt = (
            "You explain business charts using only provided facts.\n"
            "Convert these grounded observations into 3 concise executive bullets.\n"
            "Return JSON with a single key named explanation containing an array of strings.\n\n"
            f"Chart type: {chart_type}\n"
            f"Metadata: {metadata}\n"
            f"Grounded observations: {explanations}\n"
        )
        try:
            response = gemini_service.generate_json(prompt)
            llm_explanations = response.get("explanation")
            if isinstance(llm_explanations, list) and llm_explanations:
                explanations = [str(item) for item in llm_explanations[:4]]
        except Exception:  # noqa: BLE001
            pass

    return {"explanation": explanations}

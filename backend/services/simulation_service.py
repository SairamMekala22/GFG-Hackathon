"""More defensive what-if simulation helpers."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from services.dataframe_service import numeric_columns


def _pick_metric_from_prompt(prompt: str, candidates: list[str]) -> str | None:
    lowered = prompt.lower()
    ranked = sorted(candidates, key=len, reverse=True)
    for column in ranked:
        if column.lower() in lowered:
            return column
    return None


def _confidence_label(r_squared: float, observations: int) -> str:
    if observations >= 30 and r_squared >= 0.65:
        return "high"
    if observations >= 15 and r_squared >= 0.35:
        return "medium"
    return "low"


def simulate_decision(dataframe: pd.DataFrame, user_prompt: str) -> dict:
    """Estimate the effect of a hypothetical percentage change using direct scaling or regression."""
    prompt = user_prompt.lower()
    percent_match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*%", prompt)
    if not percent_match:
        return {"simulation": None}

    percentage = float(percent_match.group(1))
    numeric = [column for column in numeric_columns(dataframe) if column.lower() not in {"id", "index"}]
    if not numeric:
        return {"simulation": None}

    mentioned_metric = _pick_metric_from_prompt(prompt, numeric)
    target = None
    driver = None

    impact_match = re.search(r"(impact|effect|change)\s+(on|to)\s+([a-zA-Z_ ]+)", prompt)
    if impact_match:
        target = _pick_metric_from_prompt(impact_match.group(3), numeric)

    if "if" in prompt:
        driver = mentioned_metric
    if not driver:
        driver = mentioned_metric or next((column for column in numeric if "spend" in column.lower() or "cost" in column.lower()), numeric[0])

    if not target:
        # If the prompt only mentions one metric, simulate that metric directly rather than hallucinating another target.
        target = mentioned_metric if mentioned_metric else next((column for column in numeric if column != driver and "revenue" in column.lower()), None)
    if not target:
        target = driver

    if not driver or not target:
        return {"simulation": None}

    if driver == target:
        series = pd.to_numeric(dataframe[driver], errors="coerce").dropna()
        if len(series) < 3:
            return {"simulation": None}
        current_driver = float(series.mean())
        new_driver = current_driver * (1 + percentage / 100)
        estimated_value = new_driver
        return {
            "simulation": {
                "scenario": f"{driver} {percentage:+.0f}%",
                "driver_metric": driver,
                "target_metric": target,
                "predicted_target_change": f"{percentage:+.1f}%",
                "estimated_target_value": round(float(max(0, estimated_value)), 2),
                "confidence": "high",
                "method": "direct scaling",
                "sample_size": int(len(series)),
            }
        }

    frame = dataframe[[driver, target]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(frame) < 5:
        return {"simulation": None}

    current_driver = float(frame[driver].mean())
    new_driver = current_driver * (1 + percentage / 100)

    x = frame[driver].to_numpy()
    y = frame[target].to_numpy()
    if np.std(x) == 0 or np.std(y) == 0:
        return {"simulation": None}

    correlation = float(np.corrcoef(x, y)[0, 1])
    if np.isnan(correlation):
        return {"simulation": None}

    slope, intercept = np.polyfit(x, y, 1)
    current_prediction = slope * current_driver + intercept
    new_prediction = slope * new_driver + intercept
    residuals = y - (slope * x + intercept)
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot else 0
    if abs(correlation) < 0.3 or r_squared < 0.15:
        return {
            "simulation": {
                "scenario": f"{driver} {percentage:+.0f}%",
                "driver_metric": driver,
                "target_metric": target,
                "predicted_target_change": "insufficient signal",
                "estimated_target_value": None,
                "confidence": "low",
                "method": "relationship too weak for reliable simulation",
                "sample_size": int(len(frame)),
                "correlation": round(correlation, 2),
                "r_squared": round(r_squared, 2),
            }
        }

    delta_pct = ((new_prediction - current_prediction) / current_prediction * 100) if current_prediction else 0
    estimated_value = max(0, float(new_prediction)) if (frame[target] >= 0).all() else float(new_prediction)

    return {
        "simulation": {
            "scenario": f"{driver} {percentage:+.0f}%",
            "driver_metric": driver,
            "target_metric": target,
            "predicted_target_change": f"{delta_pct:+.1f}%",
            "estimated_target_value": round(estimated_value, 2),
            "confidence": _confidence_label(r_squared, len(frame)),
            "method": "single-variable linear regression",
            "sample_size": int(len(frame)),
            "correlation": round(correlation, 2),
            "r_squared": round(r_squared, 2),
        }
    }

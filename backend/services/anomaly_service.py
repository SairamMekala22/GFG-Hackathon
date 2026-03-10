"""Automatic anomaly detection for time series metrics."""

from __future__ import annotations

import pandas as pd

from services.dataframe_service import coerce_datetime, infer_time_column, numeric_columns


def detect_anomalies(dataframe: pd.DataFrame, metric: str | None = None, time_column: str | None = None) -> dict:
    """Detect anomalies using rolling z-score style deviation."""
    if dataframe.empty:
        return {"anomalies": [], "metric": metric, "time_column": time_column}

    time_column = time_column or infer_time_column(dataframe)
    numeric = numeric_columns(dataframe)
    metric = metric or next((column for column in numeric if column.lower() not in {"id", "index"}), None)
    if not metric or not time_column:
        return {"anomalies": [], "metric": metric, "time_column": time_column}

    timestamps = coerce_datetime(dataframe, time_column)
    values = pd.to_numeric(dataframe[metric], errors="coerce")
    series = pd.DataFrame({time_column: timestamps, metric: values}).dropna().sort_values(time_column)
    if len(series) < 5:
        return {"anomalies": [], "metric": metric, "time_column": time_column}

    rolling_mean = series[metric].rolling(window=min(5, len(series)), min_periods=3).mean()
    rolling_std = series[metric].rolling(window=min(5, len(series)), min_periods=3).std().replace(0, pd.NA)
    z_scores = ((series[metric] - rolling_mean) / rolling_std).abs().fillna(0)

    anomalies = []
    for _, row in series.assign(score=z_scores).iterrows():
        if row["score"] >= 2.5:
            anomalies.append(
                {
                    time_column: row[time_column].strftime("%Y-%m-%d"),
                    "value": float(row[metric]),
                    "score": round(float(row["score"]), 2),
                }
            )

    return {"anomalies": anomalies, "metric": metric, "time_column": time_column}

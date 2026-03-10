"""Dataset quality analysis helpers."""

from __future__ import annotations

import pandas as pd

from services.dataframe_service import infer_time_column, numeric_columns


def analyze_data_quality(dataframe: pd.DataFrame) -> dict:
    """Return a structured dataset quality report."""
    missing_values = {
        column: int(dataframe[column].isna().sum())
        for column in dataframe.columns
        if int(dataframe[column].isna().sum()) > 0
    }

    duplicate_rows = int(dataframe.duplicated().sum())

    inconsistent_types = {}
    for column in dataframe.columns:
        if dataframe[column].dtype == "object":
            numeric_cast = pd.to_numeric(dataframe[column], errors="coerce")
            if 0 < numeric_cast.notna().sum() < len(dataframe[column]):
                inconsistent_types[column] = "mixed numeric/text values"

    outliers = {}
    for column in numeric_columns(dataframe):
        series = pd.to_numeric(dataframe[column], errors="coerce").dropna()
        if len(series) < 5:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        mask = (series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)
        if int(mask.sum()) > 0:
            outliers[column] = int(mask.sum())

    warnings = []
    if missing_values:
        warnings.append("Dataset contains missing values that may affect aggregations.")
    if duplicate_rows:
        warnings.append("Duplicate rows detected; totals may be inflated.")
    if inconsistent_types:
        warnings.append("Mixed data types detected in one or more columns.")
    if not infer_time_column(dataframe):
        warnings.append("No reliable time column detected for trend analysis.")

    return {
        "missing_values": missing_values,
        "duplicates": duplicate_rows,
        "inconsistent_types": inconsistent_types,
        "outliers": outliers,
        "warnings": warnings,
    }

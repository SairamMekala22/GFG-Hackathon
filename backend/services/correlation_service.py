"""Cross-metric correlation discovery."""

from __future__ import annotations

import pandas as pd

from services.dataframe_service import numeric_columns


def discover_correlations(dataframe: pd.DataFrame) -> dict:
    """Return the strongest correlations between numeric columns."""
    numeric = numeric_columns(dataframe)
    if len(numeric) < 2:
        return {"correlations": []}

    numeric_frame = dataframe[numeric].apply(pd.to_numeric, errors="coerce")
    corr = numeric_frame.corr(numeric_only=True)
    pairs = []
    for i, col_a in enumerate(corr.columns):
        for col_b in corr.columns[i + 1:]:
            value = corr.loc[col_a, col_b]
            if pd.isna(value):
                continue
            pairs.append(
                {
                    "metric_a": col_a,
                    "metric_b": col_b,
                    "value": round(float(value), 2),
                }
            )

    pairs.sort(key=lambda item: abs(item["value"]), reverse=True)
    return {"correlations": pairs[:6]}

"""Helpers for loading and inspecting active datasets as Pandas dataframes."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sqlalchemy import inspect, text

from services.table_repair import repair_table_headers_if_needed


@dataclass
class DatasetContext:
    table_name: str
    dataframe: pd.DataFrame
    columns: list[str]


def load_table_dataframe(engine, table_name: str) -> DatasetContext:
    """Load the active SQLite table into a dataframe after repairing headers if needed."""
    repair_table_headers_if_needed(engine, table_name)
    dataframe = pd.read_sql_query(text(f"SELECT * FROM {table_name}"), engine)
    columns = dataframe.columns.tolist()
    return DatasetContext(table_name=table_name, dataframe=dataframe, columns=columns)


def get_table_columns(engine, table_name: str) -> list[str]:
    """Return the normalized column names for a table."""
    repair_table_headers_if_needed(engine, table_name)
    inspector = inspect(engine)
    return [column["name"] for column in inspector.get_columns(table_name)]


def infer_time_column(dataframe: pd.DataFrame) -> str | None:
    """Choose the best time-like column if one exists."""
    for column in dataframe.columns:
        lower = column.lower()
        if any(token in lower for token in ("date", "time", "month", "year", "period")):
            return column
    return None


def coerce_datetime(dataframe: pd.DataFrame, column: str | None) -> pd.Series | None:
    """Convert a column to datetime with multiple parsing strategies."""
    if not column or column not in dataframe.columns:
        return None

    base = dataframe[column]
    default_series = pd.to_datetime(base, errors="coerce")
    dayfirst_series = pd.to_datetime(base, errors="coerce", dayfirst=True)

    default_count = int(default_series.notna().sum())
    dayfirst_count = int(dayfirst_series.notna().sum())
    if dayfirst_count > default_count:
        return dayfirst_series
    return default_series


def numeric_columns(dataframe: pd.DataFrame) -> list[str]:
    """Return columns that can be interpreted as numeric."""
    numeric = []
    for column in dataframe.columns:
        converted = pd.to_numeric(dataframe[column], errors="coerce")
        if converted.notna().sum() > 0:
            numeric.append(column)
    return numeric


def categorical_columns(dataframe: pd.DataFrame) -> list[str]:
    """Return likely categorical dimensions."""
    dimensions = []
    for column in dataframe.columns:
        lower = column.lower()
        if lower in {"id", "index"}:
            continue
        if any(token in lower for token in ("date", "time", "month", "year", "period")):
            continue
        if dataframe[column].dtype == "object":
            dimensions.append(column)
    return dimensions

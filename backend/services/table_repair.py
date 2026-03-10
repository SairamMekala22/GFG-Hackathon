import re

import pandas as pd


def normalize_column_name(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", str(value).strip()).strip("_").lower()
    return cleaned or fallback


def looks_like_header_row(values: list) -> bool:
    if not values:
        return False
    normalized = [str(value).strip() for value in values]
    if any(not value for value in normalized):
        return False
    if len(set(normalized)) != len(normalized):
        return False
    return all(any(character.isalpha() for character in value) for value in normalized)


def repair_table_headers_if_needed(engine, table_name: str) -> bool:
    dataframe = pd.read_sql_table(table_name, engine)
    if dataframe.empty:
        return False

    if not all(str(column).lower().startswith("unnamed_") for column in dataframe.columns):
        return False

    first_row = dataframe.iloc[0].tolist()
    if not looks_like_header_row(first_row):
        return False

    new_columns = [
        normalize_column_name(value, f"column_{index}")
        for index, value in enumerate(first_row)
    ]
    if len(set(new_columns)) != len(new_columns):
        return False

    repaired = dataframe.iloc[1:].reset_index(drop=True).copy()
    repaired.columns = new_columns
    repaired.to_sql(table_name, engine, if_exists="replace", index=False)
    return True

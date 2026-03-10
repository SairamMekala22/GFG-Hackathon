import json

import pandas as pd
from sqlalchemy import inspect, text

from services.gemini_service import gemini_service


def build_dataset_profile(engine, table_name: str) -> dict:
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    column_names = [column["name"] for column in columns]

    sample_query = text(f"SELECT * FROM {table_name} LIMIT 8")
    count_query = text(f"SELECT COUNT(*) AS row_count FROM {table_name}")

    with engine.connect() as connection:
        sample_rows = [dict(row._mapping) for row in connection.execute(sample_query)]
        row_count = connection.execute(count_query).scalar_one()

    dataframe = pd.DataFrame(sample_rows)
    column_profiles = []
    for column_name in column_names:
        series = dataframe[column_name] if column_name in dataframe.columns else pd.Series(dtype="object")
        non_null = int(series.notna().sum()) if not series.empty else 0
        null_count = int(series.isna().sum()) if not series.empty else 0
        examples = []
        if not series.empty:
            examples = [str(value) for value in series.dropna().astype(str).head(3).tolist()]

        column_profiles.append(
            {
                "name": column_name,
                "type": next(
                    (str(column.get("type")) for column in columns if column["name"] == column_name),
                    "unknown",
                ),
                "non_null_sample_count": non_null,
                "null_sample_count": null_count,
                "examples": examples,
            }
        )

    return {
        "table_name": table_name,
        "row_count": int(row_count),
        "columns": column_profiles,
        "sample_rows": sample_rows,
    }


def local_dataset_answer(profile: dict, user_prompt: str) -> str:
    column_names = ", ".join(column["name"] for column in profile["columns"])
    return (
        f"The active dataset is `{profile['table_name']}` with {profile['row_count']} rows. "
        f"It includes these columns: {column_names}. Ask for a chart, comparison, or filter if you want the data queried."
    )


def answer_dataset_question(engine, table_name: str, user_prompt: str) -> tuple[str, dict]:
    profile = build_dataset_profile(engine, table_name)

    if not gemini_service.is_configured():
        return local_dataset_answer(profile, user_prompt), profile

    prompt = f"""
You are a data analyst answering questions about a dataset.

User question:
{user_prompt}

Dataset profile:
{json.dumps(profile, default=str)}

Answer the user's question in 2-4 concise sentences.
If the question asks about fields, coverage, row counts, examples, missing values, date range, or what the dataset contains, answer directly from the profile.
If the question is ambiguous, say what the dataset clearly contains and suggest a follow-up analytical question.
"""
    try:
        return gemini_service.generate_text(prompt), profile
    except Exception:  # noqa: BLE001
        return local_dataset_answer(profile, user_prompt), profile

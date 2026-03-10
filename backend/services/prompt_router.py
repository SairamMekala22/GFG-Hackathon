import json

from services.gemini_service import gemini_service

QUERY_HINTS = {
    "show",
    "plot",
    "chart",
    "graph",
    "trend",
    "compare",
    "filter",
    "group",
    "aggregate",
    "sum",
    "average",
    "count",
    "top",
    "highest",
    "lowest",
    "distribution",
    "breakdown",
    "revenue",
    "sales",
    "monthly",
    "quarterly",
}

QUESTION_HINTS = {
    "what",
    "which columns",
    "describe",
    "explain",
    "about this dataset",
    "summary of this dataset",
    "how many columns",
    "what fields",
    "data types",
    "missing values",
}


def heuristic_route_prompt(user_prompt: str) -> str:
    prompt = user_prompt.lower().strip()
    if any(token in prompt for token in QUESTION_HINTS):
        return "dataset_qa"
    if any(token in prompt for token in QUERY_HINTS):
        return "query"
    if "?" in prompt and not any(token in prompt for token in QUERY_HINTS):
        return "dataset_qa"
    return "query"


def route_prompt(user_prompt: str, schema: dict, active_table: str, context: str = "") -> str:
    if not gemini_service.is_configured():
        return heuristic_route_prompt(user_prompt)

    prompt = f"""
Classify the user's intent for a business intelligence dataset assistant.

Available tables:
{json.dumps(schema)}

Active table:
{active_table}

Recent conversation:
{context or "None"}

User prompt:
{user_prompt}

Return exactly one label:
- query: if the user wants data retrieval, filtering, aggregation, charting, comparison, trends, rankings, or metrics from the dataset
- dataset_qa: if the user is asking about the dataset itself, such as available columns, meaning of fields, data quality, coverage, row counts, date range, or descriptive questions that should be answered without generating SQL first
"""
    try:
        label = gemini_service.generate_text(prompt).strip().lower()
        return "dataset_qa" if "dataset" in label else "query"
    except Exception:  # noqa: BLE001
        return heuristic_route_prompt(user_prompt)

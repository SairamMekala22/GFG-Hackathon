import re
from typing import Optional

from sqlalchemy import text

from services.gemini_service import gemini_service

READ_ONLY_SQL = re.compile(r"^\s*select\b", re.IGNORECASE)
FORBIDDEN_SQL = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|attach|detach|pragma|create|replace)\b",
    re.IGNORECASE,
)
IDENTIFIER_CANDIDATE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
SQL_KEYWORDS = {
    "select",
    "from",
    "where",
    "group",
    "by",
    "order",
    "limit",
    "as",
    "and",
    "or",
    "sum",
    "avg",
    "count",
    "min",
    "max",
    "desc",
    "asc",
    "case",
    "when",
    "then",
    "else",
    "end",
    "distinct",
    "having",
    "on",
    "join",
    "left",
    "right",
    "inner",
    "outer",
    "not",
    "null",
    "is",
    "in",
    "like",
}


def build_schema_description(schema: dict) -> str:
    lines = []
    for table_name, columns in schema.items():
        lines.append(f"{table_name}({', '.join(columns)})")
    return "\n".join(lines)


def validate_sql(sql: str) -> str:
    cleaned = sql.strip().strip(";")
    if not READ_ONLY_SQL.match(cleaned):
        raise ValueError("Only SELECT queries are allowed.")
    if FORBIDDEN_SQL.search(cleaned):
        raise ValueError("Unsafe SQL detected.")
    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed.")
    return cleaned


def heuristic_sql(user_prompt: str, active_table: str) -> str:
    return heuristic_sql_for_columns(user_prompt, [], active_table)


def heuristic_sql_for_columns(user_prompt: str, columns: list[str], active_table: str) -> str:
    prompt = user_prompt.lower()
    date_column = first_matching_column(columns, ["date", "month", "year", "time", "period"]) or "date"
    region_column = first_matching_column(columns, ["region", "state", "zone", "city", "market", "location"]) or "region"
    category_column = first_matching_column(columns, ["category", "product", "brand", "segment", "channel"]) or "product_category"
    customer_column = first_matching_column(columns, ["customer", "signup", "user", "lead", "account"]) or "customers"
    revenue_column = first_matching_numeric_like_column(columns, ["revenue", "sales", "amount", "gmv", "income"]) or "revenue"

    if ("monthly" in prompt or "trend" in prompt or "last 12 months" in prompt) and date_column and revenue_column:
        return (
            f"SELECT {date_column}, SUM({revenue_column}) AS {revenue_column} FROM {active_table} "
            f"GROUP BY {date_column} ORDER BY {date_column}"
        )
    if "region" in prompt and revenue_column and region_column:
        return (
            f"SELECT {region_column}, SUM({revenue_column}) AS {revenue_column} FROM {active_table} "
            f"GROUP BY {region_column} ORDER BY {revenue_column} DESC"
        )
    if ("category" in prompt or "product" in prompt) and category_column and revenue_column:
        return (
            f"SELECT {category_column}, SUM({revenue_column}) AS {revenue_column} FROM {active_table} "
            f"GROUP BY {category_column} ORDER BY {revenue_column} DESC"
        )
    if ("customer" in prompt or "signup" in prompt) and date_column and customer_column:
        return (
            f"SELECT {date_column}, SUM({customer_column}) AS {customer_column} FROM {active_table} "
            f"GROUP BY {date_column} ORDER BY {date_column}"
        )
    return f"SELECT * FROM {active_table} LIMIT 50"


def first_matching_column(columns: list[str], hints: list[str]) -> Optional[str]:
    lowered = [(column, column.lower()) for column in columns]
    for hint in hints:
        for original, lower in lowered:
            if hint in lower:
                return original
    return columns[0] if columns else None


def first_matching_numeric_like_column(columns: list[str], hints: list[str]) -> Optional[str]:
    lowered = [(column, column.lower()) for column in columns]
    for hint in hints:
        for original, lower in lowered:
            if hint in lower:
                return original
    for original, lower in lowered:
        if any(token in lower for token in ["amount", "value", "total", "count", "metric"]):
            return original
    return None


def normalize_sql_identifiers(sql: str, schema: dict, active_table: str) -> str:
    table_columns = schema.get(active_table, [])
    if not table_columns:
        return sql

    lookup = {column.lower(): column for column in table_columns}
    normalized_variants = {
        re.sub(r"[^a-z0-9]+", "", column.lower()): column for column in table_columns
    }

    def replace_identifier(match):
        token = match.group(0)
        token_lower = token.lower()
        if token_lower in SQL_KEYWORDS:
            return token
        if token_lower == active_table.lower():
            return active_table
        if token_lower in lookup:
            return lookup[token_lower]

        compact = re.sub(r"[^a-z0-9]+", "", token_lower)
        if compact in normalized_variants:
            return normalized_variants[compact]

        return token

    return IDENTIFIER_CANDIDATE.sub(replace_identifier, sql)


def generate_sql(user_prompt: str, schema: dict, active_table: str, context: Optional[str] = None) -> str:
    if not gemini_service.is_configured():
        return validate_sql(heuristic_sql_for_columns(user_prompt, schema.get(active_table, []), active_table))

    schema_description = build_schema_description(schema)
    context_block = f"\nConversation context:\n{context}\n" if context else ""
    prompt = f"""
You are a SQL generator.

Database schema:
{schema_description}
{context_block}
User request:
{user_prompt}

Return only valid SQL.
The response must return pure SQL only.
Use only the tables listed in the schema.
"""
    try:
        sql = gemini_service.generate_text(prompt)
        sql = sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()
        sql = normalize_sql_identifiers(sql, schema, active_table)
        return validate_sql(sql)
    except Exception:  # noqa: BLE001
        return validate_sql(heuristic_sql_for_columns(user_prompt, schema.get(active_table, []), active_table))


def execute_sql(sql: str, engine, schema: Optional[dict] = None, active_table: Optional[str] = None):
    safe_sql = validate_sql(sql)
    if schema and active_table:
        safe_sql = normalize_sql_identifiers(safe_sql, schema, active_table)
    with engine.connect() as connection:
        result = connection.execute(text(safe_sql))
        rows = [dict(row._mapping) for row in result]
    return rows

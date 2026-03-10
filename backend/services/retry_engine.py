from services.gemini_service import gemini_service
from services.sql_generator import normalize_sql_identifiers, validate_sql


def repair_sql(sql: str, error: str, schema: dict | None = None, active_table: str | None = None) -> str:
    if not gemini_service.is_configured():
        if schema and active_table:
            return validate_sql(normalize_sql_identifiers(sql, schema, active_table))
        raise RuntimeError("Gemini is required for SQL repair but is not configured.")

    prompt = f"""
The following SQL query failed.

Query:
{sql}

Error:
{error}

Available schema:
{schema}

Active table:
{active_table}

Fix the SQL query.
Return only corrected SQL.
"""
    try:
        fixed_sql = gemini_service.generate_text(prompt)
        fixed_sql = fixed_sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()
        if schema and active_table:
            fixed_sql = normalize_sql_identifiers(fixed_sql, schema, active_table)
        return validate_sql(fixed_sql)
    except Exception:
        if schema and active_table:
            return validate_sql(normalize_sql_identifiers(sql, schema, active_table))
        raise


def execute_with_retry(sql: str, executor, retries: int = 3, schema: dict | None = None, active_table: str | None = None):
    last_error = None
    current_sql = sql

    for _ in range(retries):
        try:
            rows = executor(current_sql)
            return current_sql, rows
        except Exception as error:  # noqa: BLE001
            last_error = error
            current_sql = repair_sql(current_sql, str(error), schema=schema, active_table=active_table)

    raise RuntimeError(f"SQL execution failed after {retries} retries: {last_error}") from last_error

from collections import defaultdict

from flask import Blueprint, jsonify, request
from sqlalchemy import inspect

from database.db import engine
from extensions import limiter
from services.chart_selector import infer_chart_type
from services.dataset_qa import answer_dataset_question
from services.insight_generator import generate_insight, generate_summary_cards
from services.prompt_router import route_prompt
from services.retry_engine import execute_with_retry
from services.sql_generator import execute_sql, generate_sql

query_bp = Blueprint("query", __name__)

conversation_state = defaultdict(lambda: {"history": [], "active_table": "sales_data"})


def get_schema():
    inspector = inspect(engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = [column["name"] for column in inspector.get_columns(table_name)]
        schema[table_name] = columns
    return schema


def build_context(session_id: str) -> str:
    history = conversation_state[session_id]["history"][-5:]
    return "\n".join(f"User: {item['prompt']}\nSQL: {item['sql']}" for item in history)


def build_response(prompt: str, session_id: str):
    schema = get_schema()
    active_table = conversation_state[session_id]["active_table"]
    context = build_context(session_id)
    intent = route_prompt(prompt, schema, active_table, context)

    if intent == "dataset_qa":
        answer, profile = answer_dataset_question(engine, active_table, prompt)
        summary_cards = generate_summary_cards(profile["sample_rows"], prompt)
        conversation_state[session_id]["history"].append({"prompt": prompt, "sql": ""})
        return {
            "sql": "",
            "chart_type": "table",
            "chart_metadata": {"chart_type": "table", "x_axis": "", "y_axis": ""},
            "data": profile["sample_rows"],
            "insight": answer,
            "summary_cards": summary_cards,
            "dataset": active_table,
            "title": f"Dataset overview: {active_table}",
            "replace_dashboard": False,
            "intent": "dataset_qa",
        }

    sql = generate_sql(prompt, schema, active_table, context=context)
    resolved_sql, rows = execute_with_retry(
        sql,
        lambda statement: execute_sql(statement, engine, schema=schema, active_table=active_table),
        schema=schema,
        active_table=active_table,
    )

    metadata = infer_chart_type(rows)
    insight = generate_insight(rows, prompt)
    summary_cards = generate_summary_cards(rows, prompt)

    conversation_state[session_id]["history"].append({"prompt": prompt, "sql": resolved_sql})
    return {
        "sql": resolved_sql,
        "chart_type": metadata["chart_type"],
        "chart_metadata": metadata,
        "data": rows,
        "insight": insight,
        "summary_cards": summary_cards,
        "dataset": active_table,
        "title": prompt,
        "replace_dashboard": False,
        "intent": "query",
    }


@query_bp.post("/generate-dashboard")
@limiter.limit("10 per minute")
def generate_dashboard_route():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    session_id = payload.get("session_id", "default")

    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    try:
        result = build_response(prompt, session_id)
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@query_bp.post("/follow-up")
@limiter.limit("12 per minute")
def follow_up_route():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    session_id = payload.get("session_id", "default")

    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    try:
        result = build_response(prompt, session_id)
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400

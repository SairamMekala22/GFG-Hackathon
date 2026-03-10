from collections import defaultdict
from uuid import uuid4

from flask import Blueprint, jsonify, request
from sqlalchemy import inspect

from database.db import engine
from extensions import limiter
from services.chart_selector import infer_chart_type
from services.dataset_qa import answer_dataset_question
from services.followup_generator import generate_follow_up_prompts
from services.insight_generator import generate_insight, generate_summary_cards
from services.prompt_router import route_prompt
from services.retry_engine import execute_with_retry
from services.sql_generator import execute_sql, generate_sql
from services.table_repair import repair_table_headers_if_needed
from workers.async_analysis_worker import submit_async_analysis

query_bp = Blueprint("query", __name__)

conversation_state = defaultdict(lambda: {"history": [], "active_table": "sales_data"})


def get_schema():
    for table_name in inspect(engine).get_table_names():
        repair_table_headers_if_needed(engine, table_name)

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
        follow_up_prompts = generate_follow_up_prompts(prompt, profile["sample_rows"], active_table, context)
        conversation_state[session_id]["history"].append({"prompt": prompt, "sql": ""})
        return {
            "sql": "",
            "chart_type": "table",
            "chart_metadata": {"chart_type": "table", "x_axis": "", "y_axis": ""},
            "data": profile["sample_rows"],
            "chart_data": profile["sample_rows"],
            "insight": answer,
            "basic_insights": answer,
            "summary_cards": summary_cards,
            "follow_up_prompts": follow_up_prompts,
            "dataset": active_table,
            "title": f"Dataset overview: {active_table}",
            "source_prompt": prompt,
            "replace_dashboard": False,
            "intent": "dataset_qa",
            "analysis_pending": False,
            "job_id": None,
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
    follow_up_prompts = generate_follow_up_prompts(prompt, rows, active_table, context)
    widget_id = f"widget-{uuid4()}"
    job_id = str(uuid4())

    conversation_state[session_id]["history"].append({"prompt": prompt, "sql": resolved_sql})
    submit_async_analysis(
        session_id=session_id,
        job_id=job_id,
        widget_id=widget_id,
        prompt=prompt,
        rows=rows,
        chart_metadata=metadata,
        basic_insight=insight,
        summary_cards=summary_cards,
        active_table=active_table,
    )
    return {
        "widget_id": widget_id,
        "sql": resolved_sql,
        "chart_type": metadata["chart_type"],
        "chart_metadata": metadata,
        "data": rows,
        "chart_data": rows,
        "insight": insight,
        "basic_insights": insight,
        "summary_cards": summary_cards,
        "follow_up_prompts": follow_up_prompts,
        "anomalies": [],
        "root_cause": None,
        "dataset": active_table,
        "title": prompt,
        "source_prompt": prompt,
        "replace_dashboard": False,
        "intent": "query",
        "analysis_pending": True,
        "job_id": job_id,
    }


def _handle_query_request():
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


@query_bp.post("/query")
@limiter.limit("10 per minute")
def query_route():
    return _handle_query_request()


@query_bp.post("/generate-dashboard")
@limiter.limit("10 per minute")
def generate_dashboard_route():
    return _handle_query_request()


@query_bp.post("/follow-up")
@limiter.limit("12 per minute")
def follow_up_route():
    return _handle_query_request()

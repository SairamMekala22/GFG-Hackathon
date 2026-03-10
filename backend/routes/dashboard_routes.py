"""Routes for dashboard auto-generation and chart editing."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from database.db import engine
from routes.query_routes import conversation_state
from services.chart_edit_service import apply_chart_edit
from services.dashboard_generator_service import autogenerate_dashboard
from services.dataframe_service import load_table_dataframe

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.post("/dashboard/autogenerate")
def autogenerate_dashboard_route():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id", "default")
    try:
        table_name = conversation_state[session_id]["active_table"]
        context = load_table_dataframe(engine, table_name)
        result = autogenerate_dashboard(context.dataframe, context.table_name)
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@dashboard_bp.post("/chart/edit")
def chart_edit_route():
    payload = request.get_json(silent=True) or {}
    widget = payload.get("widget") or {}
    edit_prompt = (payload.get("edit_prompt") or "").strip()
    if not edit_prompt:
        return jsonify({"error": "edit_prompt is required."}), 400

    try:
        return jsonify(apply_chart_edit(widget, edit_prompt))
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400

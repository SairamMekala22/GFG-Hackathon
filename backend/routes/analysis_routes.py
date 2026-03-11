"""Routes for advanced decision-intelligence analyses."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from database.db import engine
from routes.query_routes import conversation_state
from services.anomaly_service import detect_anomalies
from services.dataframe_service import load_table_dataframe
from services.explain_chart_service import explain_chart
from services.recommendation_service import generate_recommendations
from services.root_cause_service import analyze_root_causes
from services.simulation_service import simulate_decision
from utils.cache_manager import get_or_compute_correlations, get_or_compute_quality_report

analysis_bp = Blueprint("analysis", __name__)


def _active_dataframe(session_id: str):
    table_name = conversation_state[session_id]["active_table"]
    context = load_table_dataframe(engine, table_name)
    return context.table_name, context.dataframe


@analysis_bp.get("/dataset/quality-report")
def quality_report_route():
    session_id = request.args.get("session_id", "default")
    try:
        table_name, _ = _active_dataframe(session_id)
        report = get_or_compute_quality_report(engine, table_name)
        report["dataset"] = table_name
        return jsonify(report)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@analysis_bp.post("/analysis/anomalies")
def anomalies_route():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id", "default")
    metric = payload.get("metric")
    time_column = payload.get("time_column")
    try:
        table_name, dataframe = _active_dataframe(session_id)
        result = detect_anomalies(dataframe, metric=metric, time_column=time_column)
        result["dataset"] = table_name
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@analysis_bp.post("/analysis/correlations")
def correlations_route():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id", "default")
    try:
        table_name, _ = _active_dataframe(session_id)
        result = get_or_compute_correlations(engine, table_name)
        result["dataset"] = table_name
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@analysis_bp.post("/analysis/root-cause")
def root_cause_route():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id", "default")
    prompt = (payload.get("prompt") or "").strip()
    try:
        table_name, dataframe = _active_dataframe(session_id)
        result = analyze_root_causes(dataframe, prompt)
        result["dataset"] = table_name
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@analysis_bp.post("/analysis/simulate")
def simulate_route():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id", "default")
    prompt = (payload.get("prompt") or "").strip()
    try:
        table_name, dataframe = _active_dataframe(session_id)
        result = simulate_decision(dataframe, prompt)
        result["dataset"] = table_name
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@analysis_bp.post("/analysis/explain-chart")
def explain_chart_route():
    payload = request.get_json(silent=True) or {}
    chart_data = payload.get("chart_data") or []
    chart_type = payload.get("chart_type") or "bar"
    metadata = payload.get("metadata") or {}

    try:
        return jsonify(explain_chart(chart_data, chart_type, metadata))
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400


@analysis_bp.post("/analysis/recommendations")
def recommendations_route():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(
            generate_recommendations(
                insights=payload.get("insights") or [],
                metrics=payload.get("metrics") or {},
                anomalies=payload.get("anomalies") or [],
                correlations=payload.get("correlations") or [],
                root_causes=payload.get("root_causes") or [],
            )
        )
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400

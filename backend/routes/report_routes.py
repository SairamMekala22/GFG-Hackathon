"""Routes for executive report generation."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.executive_report_service import generate_report_payload

report_bp = Blueprint("report", __name__)


@report_bp.post("/report/generate")
def generate_report_route():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(generate_report_payload(payload))
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400

from flask import Blueprint, jsonify, request

from database.db import engine
from routes.query_routes import conversation_state
from utils.cache_manager import get_or_compute_dataset_profile

dataset_bp = Blueprint("dataset", __name__)


@dataset_bp.get("/dataset-profile")
def dataset_profile_route():
    session_id = request.args.get("session_id", "default")
    active_table = conversation_state[session_id]["active_table"]

    try:
        return jsonify(get_or_compute_dataset_profile(engine, active_table))
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400

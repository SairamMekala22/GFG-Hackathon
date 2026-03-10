from flask import Blueprint, jsonify, request

from database.db import engine
from extensions import limiter
from routes.query_routes import conversation_state
from services.dataset_profile import get_dataset_profile
from utils.csv_loader import load_csv_to_sqlite

upload_bp = Blueprint("upload", __name__)


@upload_bp.post("/upload-csv")
@limiter.limit("6 per minute")
def upload_csv_route():
    file = request.files.get("file")
    session_id = request.form.get("session_id", "default")

    if not file or not file.filename:
        return jsonify({"error": "A CSV file is required."}), 400

    try:
        result = load_csv_to_sqlite(file)
        conversation_state[session_id]["active_table"] = result["table_name"]
        result["profile"] = get_dataset_profile(engine, result["table_name"])
        return jsonify(result)
    except Exception as error:  # noqa: BLE001
        return jsonify({"error": str(error)}), 400

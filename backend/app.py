import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv(override=True)

from database.db import init_db
from extensions import limiter, socketio
from routes.analysis_routes import analysis_bp
from routes.dataset_routes import dataset_bp
from routes.dashboard_routes import dashboard_bp
from routes.query_routes import query_bp
from routes.report_routes import report_bp
from routes.upload_routes import upload_bp
from routes.websocket_routes import register_socket_events


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "development-secret")
    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
    app.config["RATELIMIT_STORAGE_URI"] = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    CORS(app, resources={r"/*": {"origins": "*"}})
    limiter.init_app(app)
    socketio.init_app(app)
    init_db()

    app.register_blueprint(query_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(upload_bp)
    register_socket_events(socketio)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(413)
    def file_too_large(_error):
        return jsonify({"error": "CSV file is too large. Maximum size is 25 MB."}), 413

    return app


app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "5050")), debug=True)

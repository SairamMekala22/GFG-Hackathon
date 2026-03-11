from collections import defaultdict

from flask_socketio import emit, join_room

session_dashboards = defaultdict(
    lambda: {
        "widgets": [],
        "filters": {},
        "insight": "",
        "summary_cards": [],
        "follow_up_prompts": [],
        "recommendations": [],
        "root_cause": None,
        "correlations": [],
        "analysis_pending": False,
    }
)


def store_analysis_update(session_id: str, payload: dict) -> None:
    session_dashboards[session_id]["root_cause"] = payload.get("root_cause")
    session_dashboards[session_id]["correlations"] = payload.get("correlations", [])
    session_dashboards[session_id]["recommendations"] = payload.get("recommendations", [])
    session_dashboards[session_id]["analysis_pending"] = payload.get("analysis_pending", False)
    if payload.get("insight"):
        session_dashboards[session_id]["insight"] = payload["insight"]
    widget_id = payload.get("widget_id")
    if widget_id:
        updated_widgets = []
        for widget in session_dashboards[session_id]["widgets"]:
            if widget.get("id") == widget_id:
                metadata = widget.get("metadata", {})
                updated_widgets.append(
                    {
                        **widget,
                        "analysisLoading": False,
                        "metadata": {
                            **metadata,
                            "anomalies": payload.get("anomalies", metadata.get("anomalies", [])),
                        },
                    }
                )
            else:
                updated_widgets.append(widget)
        session_dashboards[session_id]["widgets"] = updated_widgets


def register_socket_events(socketio):
    @socketio.on("join_session")
    def join_session_event(payload):
        session_id = payload.get("session_id", "default")
        join_room(session_id)
        emit("dashboard_updated", session_dashboards[session_id])

    @socketio.on("dashboard_update")
    def dashboard_update_event(payload):
        session_id = payload.get("session_id", "default")
        session_dashboards[session_id]["widgets"] = payload.get("widgets", [])
        session_dashboards[session_id]["insight"] = payload.get("insight", "")
        session_dashboards[session_id]["summary_cards"] = payload.get("summary_cards", [])
        session_dashboards[session_id]["follow_up_prompts"] = payload.get("follow_up_prompts", [])
        session_dashboards[session_id]["recommendations"] = payload.get("recommendations", [])
        session_dashboards[session_id]["analysis_pending"] = payload.get("analysis_pending", False)
        emit("dashboard_updated", session_dashboards[session_id], room=session_id, include_self=False)

    @socketio.on("filter_change")
    def filter_change_event(payload):
        session_id = payload.get("session_id", "default")
        widget_id = payload.get("widget_id")
        if widget_id:
            session_dashboards[session_id]["filters"][widget_id] = payload.get("range")
        emit("dashboard_updated", session_dashboards[session_id], room=session_id, include_self=False)

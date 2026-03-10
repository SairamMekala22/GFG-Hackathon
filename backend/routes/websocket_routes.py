from collections import defaultdict

from flask_socketio import emit, join_room

session_dashboards = defaultdict(lambda: {"widgets": [], "filters": {}})


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
        emit("dashboard_updated", session_dashboards[session_id], room=session_id, include_self=False)

    @socketio.on("filter_change")
    def filter_change_event(payload):
        session_id = payload.get("session_id", "default")
        widget_id = payload.get("widget_id")
        if widget_id:
            session_dashboards[session_id]["filters"][widget_id] = payload.get("range")
        emit("dashboard_updated", session_dashboards[session_id], room=session_id, include_self=False)

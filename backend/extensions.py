from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")
limiter = Limiter(key_func=get_remote_address, default_limits=["120 per hour", "20 per minute"])

from flask_socketio import SocketIO

# Socket.IO instance to be initialized in app factory
socketio = SocketIO(cors_allowed_origins="*")

from flask import session
from flask_socketio import join_room, leave_room
from .extensions import socketio


@socketio.on('join_doctor')
def join_doctor(data):
    """Join a room for a specific doctor to receive live queue updates."""
    doctor_id = data.get('doctor_id')
    if not doctor_id:
        return

    room = f'doctor_{doctor_id}'
    join_room(room)


@socketio.on('leave_doctor')
def leave_doctor(data):
    """Leave a doctor's room."""
    doctor_id = data.get('doctor_id')
    if not doctor_id:
        return

    room = f'doctor_{doctor_id}'
    leave_room(room)

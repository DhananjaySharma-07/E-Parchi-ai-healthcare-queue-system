from flask import Blueprint, jsonify, request
from ..services.queue_service import QueueService
from ..services.token_service import TokenService

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/api/doctor/<int:doctor_id>/status')
def get_doctor_queue_status(doctor_id):
    """Get real-time queue status for a doctor"""
    queue_status = QueueService.get_queue_status(doctor_id)
    if not queue_status:
        return jsonify({'error': 'Doctor not found'}), 404

    return jsonify({
        'doctor_name': queue_status['doctor'].name,
        'current_token': queue_status['current_token'].token_number if queue_status['current_token'] else None,
        'waiting_count': queue_status['queue_length'],
        'next_token': queue_status['next_token'].token_number if queue_status['next_token'] else None,
        'is_paused': queue_status['is_paused'],
        'paused_reason': queue_status['paused_reason'],
        'waiting_tokens': [token.token_number for token in queue_status['waiting_tokens']]
    })

@queue_bp.route('/api/global_status')
def get_global_queue_status():
    """Get queue status for all doctors"""
    from ..models import Doctor
    doctors = Doctor.query.filter_by(is_active=True).all()

    status_data = {}
    for doctor in doctors:
        queue_status = QueueService.get_queue_status(doctor.id)
        if queue_status:
            status_data[doctor.doctor_id] = {
                'name': doctor.name,
                'department': doctor.department.name if doctor.department else 'Unknown',
                'current_token': queue_status['current_token'].token_number if queue_status['current_token'] else None,
                'waiting_count': queue_status['queue_length'],
                'is_paused': queue_status['is_paused']
            }

    return jsonify(status_data)

@queue_bp.route('/api/stats')
def get_queue_stats():
    """Get overall queue statistics"""
    from ..models import Token, Doctor
    from datetime import datetime, timedelta

    # Today's stats
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)

    today_tokens = Token.query.filter(Token.created_time >= today_start).all()
    completed_today = len([t for t in today_tokens if t.status == 'completed'])
    waiting_now = len([t for t in today_tokens if t.status in ['waiting', 'serving']])

    # Average wait times
    completed_tokens = Token.query.filter(Token.status == 'completed', Token.actual_wait_time.isnot(None)).all()
    avg_wait_time = sum(t.actual_wait_time for t in completed_tokens) / len(completed_tokens) if completed_tokens else 0

    # Active doctors
    active_doctors = Doctor.query.filter_by(is_active=True).count()

    return jsonify({
        'today_tokens': len(today_tokens),
        'completed_today': completed_today,
        'currently_waiting': waiting_now,
        'average_wait_time': round(avg_wait_time, 1),
        'active_doctors': active_doctors
    })
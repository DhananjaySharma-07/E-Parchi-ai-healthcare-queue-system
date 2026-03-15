from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from ..models import Doctor
from ..services.doctor_service import DoctorService
from ..services.queue_service import QueueService
from ..services.token_service import TokenService

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id') or (request.json and request.json.get('doctor_id'))
        password = request.form.get('password') or (request.json and request.json.get('password'))

        if not doctor_id or not password:
            flash('Please provide both doctor ID and password.')
            return render_template('doctor_login.html')

        doctor = DoctorService.authenticate_doctor(doctor_id, password)
        if doctor:
            login_user(doctor)
            session['doctor_id'] = doctor.id
            return redirect(url_for('doctor.dashboard'))
        else:
            flash('Invalid doctor ID or password')

    return render_template('doctor_login.html')

@doctor_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('doctor_id', None)
    return redirect(url_for('doctor.login'))

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return redirect(url_for('doctor.login'))

    dashboard_data = DoctorService.get_doctor_dashboard_data(doctor_id)
    if not dashboard_data:
        return redirect(url_for('doctor.login'))

    return render_template('doctor_dashboard.html', **dashboard_data)

@doctor_bp.route('/create_emergency_token', methods=['POST'])
@login_required
def create_emergency_token():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    name = request.form.get('name') or request.json.get('name') if request.json else None
    phone = request.form.get('phone') or request.json.get('phone') if request.json else ''
    age = request.form.get('age') or request.json.get('age') if request.json else 0
    gender = request.form.get('gender') or request.json.get('gender') if request.json else 'Other'
    symptoms = request.form.get('symptoms') or request.json.get('symptoms') if request.json else 'Emergency condition'

    if not name:
        return jsonify({'error': 'Patient name is required'}), 400

    patient_data = {
        'name': name,
        'phone': phone,
        'age': int(age) if age else 0,
        'gender': gender,
        'symptoms': symptoms
    }

    patient, token = TokenService.create_emergency_token(patient_data, doctor.id, doctor.hospital_id)
    return jsonify({'success': True, 'token_number': token.token_number, 'priority_level': token.priority_level})

# Queue Control Routes
@doctor_bp.route('/start_consultation', methods=['POST'])
@login_required
def start_consultation():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    token = QueueService.start_consultation(doctor_id)
    if token:
        return jsonify({
            'success': True,
            'token_number': token.token_number,
            'message': f'Now serving token {token.token_number}'
        })
    else:
        return jsonify({'error': 'No patients in queue'}), 400

@doctor_bp.route('/finish_consultation', methods=['POST'])
@login_required
def finish_consultation():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    token = QueueService.finish_consultation(doctor_id)
    if token:
        return jsonify({
            'success': True,
            'next_token': token.token_number,
            'message': f'Consultation completed. Now serving token {token.token_number}'
        })
    else:
        return jsonify({'success': True, 'message': 'Consultation completed. No more patients in queue'})

@doctor_bp.route('/call_next', methods=['POST'])
@login_required
def call_next():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    token = QueueService.call_next_patient(doctor_id)
    if token:
        return jsonify({
            'success': True,
            'token_number': token.token_number,
            'message': f'Calling token {token.token_number}'
        })
    else:
        return jsonify({'error': 'No patients waiting'}), 400

@doctor_bp.route('/pause_queue', methods=['POST'])
@login_required
def pause_queue():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    reason = request.form.get('reason', 'Doctor on break')
    queue = QueueService.pause_queue(doctor_id, reason)

    return jsonify({
        'success': True,
        'message': f'Queue paused: {reason}'
    })

@doctor_bp.route('/resume_queue', methods=['POST'])
@login_required
def resume_queue():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    queue = QueueService.resume_queue(doctor_id)

    return jsonify({
        'success': True,
        'message': 'Queue resumed'
    })

# API Routes for real-time updates
@doctor_bp.route('/api/queue_status')
@login_required
def get_queue_status():
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    queue_status = QueueService.get_queue_status(doctor_id)
    if not queue_status:
        return jsonify({'error': 'Doctor not found'}), 404

    return jsonify({
        'current_token': queue_status['current_token'].token_number if queue_status['current_token'] else None,
        'waiting_count': queue_status['queue_length'],
        'emergency_waiting_count': queue_status['emergency_waiting_count'],
        'avg_severity': queue_status['avg_severity'],
        'waiting_tokens': [
            {
                'token_number': token.token_number,
                'priority_level': token.priority_level,
                'patient_name': token.patient.name if token.patient else 'Patient',
                'created_time': token.created_time.strftime('%I:%M %p'),
                'severity_score': token.patient.severity_score if token.patient else 0,
                'triage_note': token.patient.triage_notes if token.patient else '',
                'emergency_flag': bool(token.patient and token.patient.emergency_flag)
            }
            for token in queue_status['waiting_tokens']
        ],
        'next_tokens': [token.token_number for token in queue_status['waiting_tokens'][:5]],
        'is_paused': queue_status['is_paused'],
        'paused_reason': queue_status['paused_reason']
    })

@doctor_bp.route('/api/patient_details/<int:token_id>')
@login_required
def get_patient_details(token_id):
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return jsonify({'error': 'Not authenticated'}), 401

    # Verify the token belongs to this doctor
    from ..models import Token
    token = Token.query.filter_by(id=token_id, doctor_id=doctor_id).first()
    if not token:
        return jsonify({'error': 'Token not found'}), 404

    return jsonify({
        'token_number': token.token_number,
        'patient_name': token.patient.name,
        'patient_phone': token.patient.phone,
        'patient_age': token.patient.age,
        'patient_gender': token.patient.gender,
        'symptoms': token.patient.symptoms,
        'status': token.status,
        'created_time': token.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        'severity_score': token.patient.severity_score,
        'emergency_flag': token.patient.emergency_flag,
        'triage_note': token.patient.triage_notes
    })
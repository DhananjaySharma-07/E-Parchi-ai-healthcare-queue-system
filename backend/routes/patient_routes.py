from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from ..models import db, Hospital, Department, Doctor, Patient, Token
from ..services.queue_service import QueueService
from ..services.smart_triage_service import SmartTriageService
from ..services.token_service import TokenService

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/')
def home():
    return redirect(url_for('patient.dashboard'))

@patient_bp.route('/dashboard')
def dashboard():
    token_id = session.get('token_id')
    return render_template('dashboard.html', token_id=token_id)

@patient_bp.route('/process_qr')
def process_qr():
    hospital_id = request.args.get('hospital_id')
    hospital = Hospital.query.get(hospital_id)
    if hospital:
        session['hospital_id'] = hospital_id
        return jsonify({'success': True})
    return jsonify({'success': False})

@patient_bp.route('/scan_qr')
def scan_qr():
    return render_template('scan_qr.html')

@patient_bp.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        hospital_id = request.args.get('hospital_id') or session.get('hospital_id')
        if not hospital_id:
            flash('Hospital ID is required. Please scan a valid QR code.')
            return redirect(url_for('patient.scan_qr'))

        try:
            hospital_id = int(hospital_id)
        except ValueError:
            flash('Invalid hospital identifier.')
            return redirect(url_for('patient.scan_qr'))

        hospital = Hospital.query.get(hospital_id)
        if not hospital:
            flash('Hospital not found. Please scan a valid QR code.')
            return redirect(url_for('patient.scan_qr'))

        patient_data = {
            'name': request.form.get('name', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'age': int(request.form.get('age', 0)),
            'gender': request.form.get('gender', 'Other'),
            'symptoms': request.form.get('symptoms', '')
        }

        department_id = request.form.get('department_id')
        doctor_id = request.form.get('doctor_id')

        if not patient_data['name'] or not patient_data['phone'] or not department_id or not doctor_id:
            flash('Please fill in all required registration fields.')
            return redirect(url_for('patient.register_patient', hospital_id=hospital_id))

        try:
            doctor_id = int(doctor_id)
        except ValueError:
            flash('Invalid doctor selected. Please choose a doctor.')
            return redirect(url_for('patient.register_patient', hospital_id=hospital_id))

        doctor = Doctor.query.filter_by(id=doctor_id, hospital_id=hospital_id, is_active=True).first()
        if not doctor:
            flash('Selected doctor not found or unavailable. Please choose another doctor.')
            return redirect(url_for('patient.register_patient', hospital_id=hospital_id))

        patient, token = TokenService.create_patient_token(patient_data, doctor.id, hospital_id)

        session['patient_id'] = patient.id
        session['token_id'] = token.id
        if patient.emergency_flag:
            flash('Emergency symptoms detected. Staff have been alerted and your case has been fast-tracked.', 'warning')

        return redirect(url_for('patient.token_confirmation'))

    # GET request - show registration form
    hospital_id = request.args.get('hospital_id')
    if not hospital_id:
        flash('Hospital ID is required. Please scan a valid QR code.')
        return redirect(url_for('patient.scan_qr'))

    session['hospital_id'] = hospital_id
    return render_template('register_patient.html')

@patient_bp.route('/token_confirmation')
def token_confirmation():
    token_id = session.get('token_id')
    if not token_id:
        return redirect(url_for('patient.home'))

    token_details = TokenService.get_token_details(token_id)
    if not token_details:
        return redirect(url_for('patient.home'))

    return render_template('token_confirmation.html', **token_details)

@patient_bp.route('/remote/<string:doctor_token>/', methods=['GET', 'POST'])
def remote_join(doctor_token):
    doctor = Doctor.query.filter_by(doctor_id=doctor_token.upper()).first()
    if not doctor:
        flash('Invalid doctor token link.')
        return redirect(url_for('patient.home'))

    if request.method == 'POST':
        hospital_id = doctor.department.hospital_id
        patient_data = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'age': int(request.form['age']),
            'gender': request.form['gender'],
            'symptoms': request.form.get('symptoms', '')
        }

        patient, token = TokenService.create_patient_token(patient_data, doctor.id, hospital_id, requires_otp=True)
        session['patient_id'] = patient.id
        session['token_id'] = token.id
        return redirect(url_for('patient.verify_otp'))

    return render_template('remote_join.html', doctor=doctor)

@patient_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    token_id = session.get('token_id')
    if not token_id:
        flash('No token to verify. Please register first.')
        return redirect(url_for('patient.home'))

    if request.method == 'POST':
        otp = request.form.get('otp')
        if TokenService.verify_token_otp(token_id, otp):
            flash('OTP verified. Your token is confirmed and queued.')
            return redirect(url_for('patient.token_confirmation'))
        flash('Invalid OTP. Please try again.')

    token = Token.query.get(token_id)
    return render_template('verify_otp.html', token=token)

@patient_bp.route('/check_in/<int:token_id>')
def check_in(token_id):
    token = Token.query.get(token_id)
    if not token:
        flash('Token not found')
        return redirect(url_for('patient.home'))

    if TokenService.check_in_token(token_id):
        flash('Check-in confirmed. Please wait for your turn.')
    else:
        flash('Cannot check in. Token is not in waiting state.')

    return redirect(url_for('patient.token_confirmation'))

@patient_bp.route('/register_kiosk', methods=['GET', 'POST'])
def register_kiosk():
    if request.method == 'POST':
        patient_data = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'age': int(request.form['age']),
            'gender': request.form['gender'],
            'symptoms': request.form.get('symptoms', '')
        }
        doctor_id = request.form['doctor_id']
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            flash('Doctor not found')
            return redirect(url_for('patient.register_kiosk'))

        patient, token = TokenService.create_patient_token(patient_data, doctor.id, doctor.department.hospital_id)
        session['token_id'] = token.id
        session['patient_id'] = patient.id
        return redirect(url_for('patient.token_confirmation'))
    doctors = Doctor.query.filter_by(is_active=True).all()
    return render_template('register_kiosk.html', doctors=doctors)

@patient_bp.route('/reception_entry', methods=['GET', 'POST'])
def reception_entry():
    if request.method == 'POST':
        patient_data = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'age': int(request.form['age']),
            'gender': request.form['gender'],
            'symptoms': request.form.get('symptoms', '')
        }
        doctor_id = request.form['doctor_id']
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            flash('Doctor not found')
            return redirect(url_for('patient.reception_entry'))

        patient, token = TokenService.create_patient_token(patient_data, doctor.id, doctor.department.hospital_id)
        session['token_id'] = token.id
        session['patient_id'] = patient.id
        return redirect(url_for('patient.token_confirmation'))

    doctors = Doctor.query.filter_by(is_active=True).all()
    return render_template('reception_entry.html', doctors=doctors)

@patient_bp.route('/display')
def display_board():
    from ..services.queue_service import QueueService
    from ..models import Doctor
    doctors = Doctor.query.filter_by(is_active=True).all()
    board = []
    for doctor in doctors:
        status = QueueService.get_queue_status(doctor.id)
        board.append({
            'doctor_name': doctor.name,
            'department': doctor.department.name if doctor.department else '',
            'current_token': status['current_token'].token_number if status['current_token'] else 'None',
            'next_tokens': [t.token_number for t in status['waiting_tokens'][:3]]
        })
    return render_template('display.html', board=board)

@patient_bp.route('/tokens')
def tokens():
    patient_id = session.get('patient_id')
    if not patient_id:
        return redirect(url_for('patient.home'))

    tokens = TokenService.get_patient_tokens(patient_id)
    return render_template('tokens.html', tokens=tokens)

@patient_bp.route('/profile')
def profile():
    patient_id = session.get('patient_id')
    if not patient_id:
        return redirect(url_for('patient.home'))

    patient = Patient.query.get(patient_id)
    return render_template('profile.html', patient=patient)

@patient_bp.route('/records')
def records():
    patient_id = session.get('patient_id')
    if not patient_id:
        return redirect(url_for('patient.home'))

    tokens = TokenService.get_patient_tokens(patient_id)
    completed_tokens = [token for token in tokens if token.status == 'completed']
    return render_template('records.html', tokens=completed_tokens)

@patient_bp.route('/nearby')
def nearby():
    import os
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    return render_template('nearby.html', google_maps_api_key=google_maps_api_key)

# API Routes
@patient_bp.route('/api/hospital/<int:hospital_id>')
def get_hospital(hospital_id):
    hospital = Hospital.query.get(hospital_id)
    if not hospital:
        return jsonify({'error': 'Hospital not found'}), 404

    return jsonify({
        'id': hospital.id,
        'name': hospital.name,
        'address': hospital.address
    })

@patient_bp.route('/api/departments')
def get_departments():
    hospital_id = request.args.get('hospital_id')
    query = Department.query
    if hospital_id:
        query = query.filter_by(hospital_id=hospital_id)
    departments = query.all()
    return jsonify([{
        'id': dept.id,
        'name': dept.name,
        'hospital_id': dept.hospital_id
    } for dept in departments])

@patient_bp.route('/api/doctors')
def get_doctors():
    department_id = request.args.get('department_id')
    hospital_id = request.args.get('hospital_id')

    query = Doctor.query
    if department_id:
        query = query.filter_by(department_id=department_id)
    if hospital_id:
        query = query.join(Department).filter(Department.hospital_id == hospital_id)

    doctors = query.filter(Doctor.is_active == True).all()
    return jsonify([{
        'id': doctor.id,
        'name': doctor.name,
        'specialization': doctor.name.split()[-1] if len(doctor.name.split()) > 1 else 'General Physician',
        'department_id': doctor.department_id,
        'avg_consultation_time': doctor.avg_consultation_time,
        'predicted_wait': doctor.queue_length * doctor.avg_consultation_time,
        'emergency_waiting_count': sum(1 for token in doctor.waiting_tokens if token.priority_level == 'EMERGENCY')
    } for doctor in doctors])


@patient_bp.route('/api/triage_assessment', methods=['POST'])
def triage_assessment():
    payload = request.get_json(silent=True) or request.form
    assessment = SmartTriageService.assess_patient({
        'age': payload.get('age', 0),
        'symptoms': payload.get('symptoms', ''),
    })
    return jsonify(assessment)

@patient_bp.route('/api/queue_status')
def queue_status():
    token_id = request.args.get('token_id') or session.get('token_id')
    if not token_id:
        return jsonify({'error': 'Token ID is required'})

    queue_info = QueueService.get_patient_queue_info(token_id)
    if not queue_info:
        return jsonify({'error': 'Token not found'})

    # Check if user owns this token
    patient_id = session.get('patient_id')
    if not patient_id or queue_info['token'].patient_id != patient_id:
        # allow secure token access if only token_id is passed from owner
        return jsonify({'error': 'Unauthorized access to token'})

    return jsonify({
        'your_token': queue_info['token'].token_number,
        'current_token': queue_info['current_token'].token_number if queue_info['current_token'] else 'None',
        'patients_ahead': queue_info['patients_ahead'],
        'est_wait_time': queue_info['estimated_wait'],
        'is_paused': queue_info['is_paused'],
        'paused_reason': queue_info['paused_reason'],
        'priority_level': queue_info['token'].priority_level,
        'severity_score': queue_info['severity_score'],
        'emergency_flag': queue_info['emergency_flag'],
        'triage_note': queue_info['triage_note']
    })
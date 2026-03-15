from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, Hospital, Department, DepartmentMaster, Doctor, Token
from ..services.doctor_service import DoctorService
from ..services.token_service import TokenService
from qr_generator import generate_qr

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hospital = Hospital.query.filter_by(admin_username=username).first()
        if hospital and hospital.check_password(password):
            login_user(hospital)
            return redirect(url_for('admin.admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@admin_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    hospital = current_user
    doctors = Doctor.query.join(Department).filter(Department.hospital_id == hospital.id).all()
    master_departments = DepartmentMaster.query.all()

    # Build queue summary for each doctor
    doctor_queues = []
    total_pending_tokens = 0
    for doctor in doctors:
        current_token = Token.query.filter_by(doctor_id=doctor.id, status='serving').first()
        waiting_tokens = doctor.waiting_tokens
        waiting_count = len(waiting_tokens)
        total_pending_tokens += waiting_count
        next_token = waiting_tokens[0].token_number if waiting_tokens else None
        estimated_wait_minutes = waiting_count * doctor.avg_consultation_time

        doctor_queues.append({
            'doctor': doctor,
            'current_token': current_token.token_number if current_token else 'None',
            'waiting_count': waiting_count,
            'next_token': next_token or 'None',
            'estimated_wait_minutes': estimated_wait_minutes,
            'emergency_count': sum(1 for token in waiting_tokens if token.priority_level == 'EMERGENCY'),
            'avg_severity': int(sum((token.patient.severity_score or 0) for token in waiting_tokens) / waiting_count) if waiting_count else 0,
            'waiting_tokens': [token.token_number for token in waiting_tokens[:5]],
        })

    return render_template('admin_dashboard.html', hospital=hospital, doctors=doctors, doctor_queues=doctor_queues, master_departments=master_departments, total_pending_tokens=total_pending_tokens)

@admin_bp.route('/register_hospital', methods=['GET', 'POST'])
def register_hospital():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        admin_username = request.form['admin_username']
        password = request.form['password']

        # Check if username already exists
        existing = Hospital.query.filter_by(admin_username=admin_username).first()
        if existing:
            flash('Admin username already exists')
            return redirect(url_for('admin.register_hospital'))

        hospital = Hospital(name=name, address=address, admin_username=admin_username)
        hospital.set_password(password)
        db.session.add(hospital)
        db.session.commit()

        # Generate QR for hospital
        qr_filename = generate_qr(hospital.id, output_path='static/hospital_qr/', filename=f"{hospital.name.lower().replace(' ', '_').replace('.', '').replace(',', '')}_qr.png")
        hospital.qr_code = qr_filename
        db.session.commit()

        flash('Hospital registered successfully')
        return redirect(url_for('admin.admin_login'))

    return render_template('register_hospital.html')

@admin_bp.route('/add_department', methods=['POST'])
@login_required
def add_department():
    master_id = request.form.get('master_department')
    if not master_id:
        flash('Please select a department from the master list')
        return redirect(url_for('admin.admin_dashboard'))

    hospital_id = current_user.id
    master = DepartmentMaster.query.get(master_id)
    if not master:
        flash('Selected department not found')
        return redirect(url_for('admin.admin_dashboard'))

    existing = Department.query.filter_by(hospital_id=hospital_id, master_department_id=master.id).first()
    if existing:
        flash('Department already added for this hospital')
        return redirect(url_for('admin.admin_dashboard'))

    department = Department(hospital_id=hospital_id, master_department_id=master.id)
    db.session.add(department)
    db.session.commit()

    flash('Department added successfully')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/create_emergency_token', methods=['POST'])
@login_required
def create_emergency_token():
    doctor_id = request.form.get('doctor_id')
    name = request.form.get('name')
    phone = request.form.get('phone', '')
    age = request.form.get('age', 0)
    gender = request.form.get('gender', 'Other')
    symptoms = request.form.get('symptoms', 'Emergency')

    if not doctor_id or not name:
        flash('Doctor and patient name are required for emergency tokens')
        return redirect(url_for('admin.admin_dashboard'))

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        flash('Doctor not found')
        return redirect(url_for('admin.admin_dashboard'))

    patient_data = {'name': name, 'phone': phone, 'age': int(age), 'gender': gender, 'symptoms': symptoms}
    TokenService.create_emergency_token(patient_data, doctor.id, doctor.hospital_id)
    flash('Emergency token created and inserted next in queue.')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id') or f"DOC{Doctor.query.count() + 1:03d}"
        name = request.form.get('name')
        department_id = request.form.get('department_id') or request.form.get('department')
        password = request.form.get('password') or 'password123'
        avg_consultation_time = int(request.form.get('avg_consultation_time') or request.form.get('avg_time') or 7)

        if not name or not department_id:
            flash('Doctor name and department are required')
            return redirect(url_for('admin.admin_dashboard'))

        existing = Doctor.query.filter_by(doctor_id=doctor_id).first()
        if existing:
            flash('Doctor ID already exists')
            return redirect(url_for('admin.admin_dashboard'))

        department = Department.query.get(department_id)
        if not department:
            flash('Department not found')
            return redirect(url_for('admin.admin_dashboard'))

        doctor = Doctor(
            doctor_id=doctor_id,
            name=name,
            hospital_id=department.hospital_id,
            department_id=department.id,
            avg_consultation_time=avg_consultation_time
        )
        doctor.set_password(password)

        db.session.add(doctor)
        db.session.commit()

        flash('Doctor added successfully')
        return redirect(url_for('admin.admin_dashboard'))

    # GET: redirect back to admin dashboard (form is embedded there)
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/manage_queue/<int:doctor_id>')
@login_required
def manage_queue(doctor_id):
    # Verify doctor belongs to this hospital
    doctor = Doctor.query.join(Department).filter(
        Doctor.id == doctor_id,
        Department.hospital_id == current_user.id
    ).first()

    if not doctor:
        flash('Doctor not found')
        return redirect(url_for('admin.admin_dashboard'))

    # Get queue data
    tokens = TokenService.get_doctor_tokens(doctor_id)
    current_token = None
    waiting_tokens = []

    for token in tokens:
        if token.status == 'serving':
            current_token = token
        elif token.status == 'waiting':
            waiting_tokens.append(token)

    flash(f'Queue for {doctor.name}: {len(waiting_tokens)} waiting, current: {current_token.token_number if current_token else "None"}')
    return redirect(url_for('admin.admin_dashboard'))
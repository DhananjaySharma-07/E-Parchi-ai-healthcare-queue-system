from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

from flask_login import UserMixin

class Hospital(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    admin_username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    qr_code = db.Column(db.String(100), nullable=True)
    departments = db.relationship('Department', backref='hospital', lazy=True)
    tokens = db.relationship('Token', backref='hospital', lazy=True)

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    doctors = db.relationship('Doctor', backref='department', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avg_consultation_time = db.Column(db.Integer, nullable=False)  # in minutes
    tokens = db.relationship('Token', backref='doctor', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.Text, nullable=True)
    tokens = db.relationship('Token', backref='patient', lazy=True)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    token_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, serving, completed
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    served_time = db.Column(db.DateTime, nullable=True)
    completed_time = db.Column(db.DateTime, nullable=True)
    estimated_wait_time = db.Column(db.Integer, nullable=True)  # in minutes
    actual_wait_time = db.Column(db.Integer, nullable=True)  # in minutes
    consultation_notes = db.Column(db.Text, nullable=True)

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    token_id = db.Column(db.Integer, db.ForeignKey('token.id'), nullable=False)
    consultation_date = db.Column(db.DateTime, default=datetime.utcnow)
    symptoms = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
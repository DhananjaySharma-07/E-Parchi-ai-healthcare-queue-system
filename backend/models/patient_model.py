from datetime import datetime

from .hospital_model import db


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.Text, nullable=True)
    severity_score = db.Column(db.Integer, default=10)
    arrival_time = db.Column(db.DateTime, default=datetime.utcnow)
    emergency_flag = db.Column(db.Boolean, default=False)
    triage_notes = db.Column(db.Text, nullable=True)

    # Relationships
    tokens = db.relationship('Token', backref='patient', lazy=True)
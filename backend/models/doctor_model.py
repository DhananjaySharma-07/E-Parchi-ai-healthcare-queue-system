from .hospital_model import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import case

class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.String(20), unique=True, nullable=False)  # DOC101, DOC102, etc.
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avg_consultation_time = db.Column(db.Integer, nullable=False)  # in minutes
    is_active = db.Column(db.Boolean, default=True)
    is_on_break = db.Column(db.Boolean, default=False)

    hospital = db.relationship('Hospital', backref='doctors')

    # Relationships
    tokens = db.relationship('Token', backref='doctor', lazy=True)

    def get_id(self):
        return f"doctor_{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def current_token(self):
        """Get the currently serving token for this doctor"""
        from .token_model import Token
        return Token.query.filter_by(doctor_id=self.id, status='serving').first()

    @property
    def waiting_tokens(self):
        """Get all waiting tokens for this doctor, ordered by emergency priority and severity."""
        from .patient_model import Patient
        from .token_model import Token

        priority_order = case(
            (Token.priority_level == 'EMERGENCY', 3),
            (Token.priority_level == 'PRIORITY', 2),
            else_=1
        )
        return Token.query.join(Patient, Patient.id == Token.patient_id).filter(
            Token.doctor_id == self.id,
            Token.status == 'waiting'
        ).order_by(
            priority_order.desc(),
            Patient.severity_score.desc(),
            Token.created_time.asc()
        ).all()

    @property
    def next_token(self):
        """Get the next token to be served"""
        waiting = self.waiting_tokens
        return waiting[0] if waiting else None

    @property
    def queue_length(self):
        """Get the number of patients waiting"""
        return len(self.waiting_tokens)
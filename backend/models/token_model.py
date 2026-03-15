from .hospital_model import db
from datetime import datetime


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    token_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='waiting')  # pending, waiting, serving, completed, cancelled
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    served_time = db.Column(db.DateTime, nullable=True)
    completed_time = db.Column(db.DateTime, nullable=True)
    estimated_wait_time = db.Column(db.Integer, nullable=True)  # in minutes
    actual_wait_time = db.Column(db.Integer, nullable=True)  # in minutes
    consultation_notes = db.Column(db.Text, nullable=True)
    otp_code = db.Column(db.String(10), nullable=True)
    otp_verified = db.Column(db.Boolean, default=False)
    check_in_time = db.Column(db.DateTime, nullable=True)
    consultation_fee = db.Column(db.Integer, default=0)
    needs_payment = db.Column(db.Boolean, default=False)
    is_paid = db.Column(db.Boolean, default=True)
    priority_level = db.Column(db.String(20), default='NORMAL')  # NORMAL, PRIORITY, EMERGENCY
    session_type = db.Column(db.String(50), nullable=True)
    session_date = db.Column(db.Date, nullable=True)

    @property
    def is_emergency(self):
        return self.priority_level == 'EMERGENCY'

    @property
    def patients_ahead(self):
        """Calculate how many patients are ahead after smart triage ordering."""
        if not self.doctor:
            return 0

        ahead = 0
        if self.status == 'waiting' and self.doctor.current_token:
            ahead += 1

        waiting_tokens = self.doctor.waiting_tokens
        for index, token in enumerate(waiting_tokens):
            if token.id == self.id:
                return ahead + index
        return ahead

    @property
    def position(self):
        return self.patients_ahead + 1

    @property
    def estimated_wait_minutes(self):
        """Calculate estimated wait time based on doctor's consultation time."""
        if not self.doctor:
            return 0
        if self.estimated_wait_time is not None:
            return self.estimated_wait_time
        return self.patients_ahead * self.doctor.avg_consultation_time

    @property
    def is_no_show(self):
        return self.status in ['pending', 'waiting'] and self.created_time and (datetime.utcnow() - self.created_time).total_seconds() > 1800

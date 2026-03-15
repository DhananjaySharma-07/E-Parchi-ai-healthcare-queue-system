from .hospital_model import db
from datetime import datetime

class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    is_paused = db.Column(db.Boolean, default=False)
    paused_at = db.Column(db.DateTime, nullable=True)
    paused_reason = db.Column(db.String(200), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctor = db.relationship('Doctor', backref='queue', uselist=False)

    @classmethod
    def get_or_create_for_doctor(cls, doctor_id):
        """Get or create queue for a doctor"""
        queue = cls.query.filter_by(doctor_id=doctor_id).first()
        if not queue:
            queue = cls(doctor_id=doctor_id)
            db.session.add(queue)
            db.session.commit()
        return queue

    def pause_queue(self, reason="Doctor on break"):
        """Pause the queue"""
        self.is_paused = True
        self.paused_at = datetime.utcnow()
        self.paused_reason = reason
        db.session.commit()

    def resume_queue(self):
        """Resume the queue"""
        self.is_paused = False
        self.paused_at = None
        self.paused_reason = None
        db.session.commit()
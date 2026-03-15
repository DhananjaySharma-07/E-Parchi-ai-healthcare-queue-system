from datetime import datetime
import re

from ..models import db, Doctor, Patient, Queue, Token


class QueueService:
    @staticmethod
    def _refresh_wait_times(doctor_id):
        """Update estimated wait time for all waiting tokens for a doctor."""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return

        waiting_tokens = doctor.waiting_tokens
        offset = 1 if doctor.current_token else 0
        for idx, token in enumerate(waiting_tokens):
            token.estimated_wait_time = (idx + offset) * doctor.avg_consultation_time
        db.session.commit()

    @staticmethod
    def generate_token_number(doctor_id):
        """Generate the next token number for a doctor."""
        last_token = Token.query.filter_by(doctor_id=doctor_id).order_by(Token.id.desc()).first()
        if not last_token:
            return 'A-01'

        match = re.match(r'([A-Z])-(\d+)', last_token.token_number)
        if match:
            letter = match.group(1)
            num = int(match.group(2)) + 1
            return f'{letter}-{num:02d}'

        return 'A-01'

    @staticmethod
    def create_token(patient_id, doctor_id, hospital_id, status='waiting', priority_level='NORMAL', otp_code=None, needs_payment=False, consultation_fee=0, session_type=None, session_date=None, **kwargs):
        """Create a new token for a patient."""
        token_number = QueueService.generate_token_number(doctor_id)
        now = datetime.utcnow()
        if not session_type:
            hour = now.hour
            if 9 <= hour < 13:
                session_type = 'Morning'
            elif 13 <= hour < 17:
                session_type = 'Afternoon'
            else:
                session_type = 'Evening'
        if not session_date:
            session_date = now.date()

        token = Token(
            patient_id=patient_id,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            token_number=token_number,
            status=status,
            priority_level=priority_level,
            otp_code=otp_code,
            needs_payment=needs_payment,
            consultation_fee=consultation_fee,
            is_paid=not needs_payment,
            session_type=session_type,
            session_date=session_date,
        )

        db.session.add(token)
        db.session.flush()
        QueueService._refresh_wait_times(doctor_id)
        db.session.commit()
        return token

    @staticmethod
    def _complete_current_token(doctor):
        """Mark the currently serving token as completed."""
        current_token = doctor.current_token
        if not current_token:
            return None

        current_token.status = 'completed'
        current_token.completed_time = datetime.utcnow()

        if current_token.served_time:
            current_token.actual_wait_time = int((datetime.utcnow() - current_token.served_time).total_seconds() / 60)

        return current_token

    @staticmethod
    def start_consultation(doctor_id):
        """Begin serving the next patient in the queue."""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None

        queue = Queue.get_or_create_for_doctor(doctor_id)
        if queue.is_paused:
            return None

        current = doctor.current_token
        if current:
            return current

        next_token = doctor.next_token
        if not next_token:
            return None

        next_token.status = 'serving'
        next_token.served_time = datetime.utcnow()
        db.session.commit()
        QueueService._refresh_wait_times(doctor_id)
        return next_token

    @staticmethod
    def call_next_patient(doctor_id):
        """Move the queue to the next patient, completing the current one."""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None

        QueueService._complete_current_token(doctor)
        next_token = QueueService.start_consultation(doctor_id)
        QueueService._refresh_wait_times(doctor_id)
        db.session.commit()
        return next_token

    @staticmethod
    def finish_consultation(doctor_id):
        """Finish the current consultation and advance the queue."""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None

        finished_token = QueueService._complete_current_token(doctor)
        if not finished_token:
            return None

        next_token = QueueService.start_consultation(doctor_id)
        QueueService._refresh_wait_times(doctor_id)
        db.session.commit()
        return next_token

    @staticmethod
    def pause_queue(doctor_id, reason='Doctor on break'):
        queue = Queue.get_or_create_for_doctor(doctor_id)
        queue.pause_queue(reason)
        return queue

    @staticmethod
    def resume_queue(doctor_id):
        queue = Queue.get_or_create_for_doctor(doctor_id)
        queue.resume_queue()

        doctor = Doctor.query.get(doctor_id)
        if doctor and not doctor.current_token:
            QueueService.start_consultation(doctor_id)

        return queue

    @staticmethod
    def get_queue_status(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None

        queue = Queue.get_or_create_for_doctor(doctor_id)
        current_token = doctor.current_token
        waiting_tokens = doctor.waiting_tokens
        finished_count = Token.query.filter_by(doctor_id=doctor_id, status='completed').count()
        active_total = finished_count + len(waiting_tokens) + (1 if current_token else 0)
        progress = int((finished_count / active_total) * 100) if active_total else 0
        emergency_waiting_count = sum(1 for token in waiting_tokens if token.priority_level == 'EMERGENCY')
        avg_severity = int(sum((token.patient.severity_score or 0) for token in waiting_tokens) / len(waiting_tokens)) if waiting_tokens else 0

        return {
            'doctor': doctor,
            'current_token': current_token,
            'waiting_tokens': waiting_tokens,
            'next_token': waiting_tokens[0] if waiting_tokens else None,
            'queue_length': len(waiting_tokens),
            'is_paused': queue.is_paused,
            'paused_reason': queue.paused_reason,
            'paused_at': queue.paused_at,
            'finished_count': finished_count,
            'progress': progress,
            'emergency_waiting_count': emergency_waiting_count,
            'avg_severity': avg_severity,
        }

    @staticmethod
    def get_patient_queue_info(token_id):
        token = Token.query.get(token_id)
        if not token:
            return None

        doctor = token.doctor
        queue = Queue.get_or_create_for_doctor(doctor.id)
        queue_status = QueueService.get_queue_status(doctor.id)

        return {
            'token': token,
            'doctor': doctor,
            'department': doctor.department,
            'hospital': token.hospital,
            'patients_ahead': token.patients_ahead,
            'estimated_wait': token.estimated_wait_minutes,
            'current_token': doctor.current_token,
            'is_paused': queue.is_paused,
            'paused_reason': queue.paused_reason,
            'queue_progress': queue_status['progress'] if queue_status else 0,
            'severity_score': token.patient.severity_score if token.patient else 0,
            'emergency_flag': bool(token.patient and token.patient.emergency_flag),
            'triage_note': token.patient.triage_notes if token.patient else '',
        }

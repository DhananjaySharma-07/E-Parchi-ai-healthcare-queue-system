from datetime import datetime

from ..models import db, Doctor, Hospital, Patient, Token
from .emergency_service import EmergencyService
from .queue_service import QueueService
from .smart_triage_service import SmartTriageService


class TokenService:
    @staticmethod
    def create_patient_token(patient_data, doctor_id, hospital_id, requires_otp=False, needs_payment=False, consultation_fee=0):
        """Create a patient and token with smart triage and emergency override."""
        triage = SmartTriageService.assess_patient(patient_data)

        if triage['emergency_flag']:
            patient, token = EmergencyService.create_emergency_case(patient_data, doctor_id, hospital_id, triage)
            return patient, token

        patient = Patient(
            name=patient_data['name'],
            phone=patient_data['phone'],
            age=patient_data.get('age', 0),
            gender=patient_data.get('gender', 'Other'),
            symptoms=patient_data.get('symptoms', ''),
            severity_score=triage['severity_score'],
            arrival_time=datetime.utcnow(),
            emergency_flag=False,
            triage_notes=triage['triage_note'],
        )

        db.session.add(patient)
        db.session.flush()

        status = 'pending' if requires_otp else 'waiting'
        token = QueueService.create_token(
            patient.id,
            doctor_id,
            hospital_id,
            status=status,
            priority_level=triage['priority_level'],
            needs_payment=needs_payment,
            consultation_fee=consultation_fee,
        )

        db.session.commit()
        return patient, token

    @staticmethod
    def verify_token_otp(token_id, otp_code):
        token = Token.query.get(token_id)
        if not token or token.status != 'pending':
            return False
        if token.otp_code and token.otp_code == otp_code:
            token.otp_verified = True
            token.status = 'waiting'
            token.otp_code = None
            db.session.commit()
            QueueService._refresh_wait_times(token.doctor_id)
            return True
        return False

    @staticmethod
    def check_in_token(token_id):
        token = Token.query.get(token_id)
        if not token or token.status not in ['waiting', 'pending']:
            return False
        token.check_in_time = datetime.utcnow()
        token.status = 'waiting'
        db.session.commit()
        return True

    @staticmethod
    def get_patient_tokens(patient_id):
        return Token.query.filter_by(patient_id=patient_id).order_by(Token.created_time.desc()).all()

    @staticmethod
    def get_token_details(token_id):
        token = Token.query.get(token_id)
        if not token:
            return None
        return QueueService.get_patient_queue_info(token_id)

    @staticmethod
    def update_token_status(token_id, status, notes=None):
        token = Token.query.get(token_id)
        if not token:
            return None

        token.status = status

        if status == 'serving' and not token.served_time:
            token.served_time = datetime.utcnow()
        elif status == 'completed' and not token.completed_time:
            token.completed_time = datetime.utcnow()
            if token.served_time:
                token.actual_wait_time = int((datetime.utcnow() - token.served_time).total_seconds() / 60)

        if notes:
            token.consultation_notes = notes

        db.session.commit()
        return token

    @staticmethod
    def get_doctor_tokens(doctor_id, status=None):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return []
        if status == 'waiting':
            return doctor.waiting_tokens

        query = Token.query.filter_by(doctor_id=doctor_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Token.created_time.desc()).all()

    @staticmethod
    def create_emergency_token(patient_data, doctor_id, hospital_id):
        triage = SmartTriageService.assess_patient({**patient_data, 'symptoms': patient_data.get('symptoms', 'Emergency')})
        triage['severity_score'] = max(triage['severity_score'], 95)
        triage['emergency_flag'] = True
        triage['priority_level'] = 'EMERGENCY'
        triage['triage_note'] = 'Emergency override activated by hospital staff.'
        return EmergencyService.create_emergency_case(patient_data, doctor_id, hospital_id, triage)

    @staticmethod
    def get_active_tokens():
        return Token.query.filter(Token.status.in_(['waiting', 'serving'])).order_by(Token.created_time).all()

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

from ..models import db, Patient, Doctor
from .queue_service import QueueService


class EmergencyService:
    """Separately handles emergency cases and triggers immediate override behavior."""

    @staticmethod
    def create_emergency_case(patient_data: Dict[str, Any], doctor_id: int, hospital_id: int, triage_result: Dict[str, Any]) -> Tuple[Patient, Any]:
        patient = Patient(
            name=patient_data['name'],
            phone=patient_data.get('phone', ''),
            age=patient_data.get('age', 0),
            gender=patient_data.get('gender', 'Other'),
            symptoms=patient_data.get('symptoms', 'Emergency condition'),
            severity_score=max(int(triage_result.get('severity_score', 100)), 90),
            arrival_time=datetime.utcnow(),
            emergency_flag=True,
            triage_notes=triage_result.get('triage_note', 'Emergency override activated.'),
        )
        db.session.add(patient)
        db.session.flush()

        token = QueueService.create_token(
            patient.id,
            doctor_id,
            hospital_id,
            status='waiting',
            priority_level='EMERGENCY',
        )

        doctor = Doctor.query.get(doctor_id)
        if doctor and not doctor.current_token:
            token.status = 'serving'
            token.served_time = datetime.utcnow()
            db.session.commit()

        QueueService._refresh_wait_times(doctor_id)
        return patient, token

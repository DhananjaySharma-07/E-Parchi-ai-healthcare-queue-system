from ..models import db, Doctor, Department, Hospital
from .queue_service import QueueService

class DoctorService:
    @staticmethod
    def authenticate_doctor(doctor_id, password):
        """Authenticate a doctor with doctor_id and password"""
        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
        if doctor and doctor.check_password(password) and doctor.is_active:
            return doctor
        return None

    @staticmethod
    def get_doctor_dashboard_data(doctor_id):
        """Get all data needed for doctor dashboard"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None

        queue_status = QueueService.get_queue_status(doctor_id)

        return {
            'doctor': doctor,
            'department': doctor.department,
            'hospital': doctor.department.hospital if doctor.department else None,
            'queue_status': queue_status
        }

    @staticmethod
    def get_doctors_by_department(department_id):
        """Get all active doctors in a department"""
        return Doctor.query.filter(Doctor.department_id == department_id, Doctor.is_active == True).all()

    @staticmethod
    def get_doctors_by_hospital(hospital_id):
        """Get all active doctors in a hospital"""
        return Doctor.query.join(Department).filter(
            Department.hospital_id == hospital_id,
            Doctor.is_active == True
        ).all()

    @staticmethod
    def update_doctor_status(doctor_id, is_active=None, is_on_break=None):
        """Update doctor's status"""
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None

        if is_active is not None:
            doctor.is_active = is_active
        if is_on_break is not None:
            doctor.is_on_break = is_on_break

        db.session.commit()
        return doctor

    @staticmethod
    def get_doctor_by_id(doctor_id):
        """Get doctor by their doctor_id (not primary key)"""
        return Doctor.query.filter_by(doctor_id=doctor_id).first()
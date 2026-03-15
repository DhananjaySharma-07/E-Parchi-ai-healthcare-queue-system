from .hospital_model import db, Hospital
from .department_model import Department, DepartmentMaster
from .doctor_model import Doctor
from .patient_model import Patient
from .token_model import Token
from .queue_model import Queue

__all__ = ['db', 'Hospital', 'Department', 'DepartmentMaster', 'Doctor', 'Patient', 'Token', 'Queue']
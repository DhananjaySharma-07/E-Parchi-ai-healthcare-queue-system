from .hospital_model import db

class DepartmentMaster(db.Model):
    __tablename__ = 'departments_master'
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.String(50), unique=True, nullable=False)
    english_name = db.Column(db.String(100), nullable=False)
    hindi_name = db.Column(db.String(100), nullable=False)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    master_department_id = db.Column(db.Integer, db.ForeignKey('departments_master.id'), nullable=False)

    # Relationships
    doctors = db.relationship('Doctor', backref='department', lazy=True)
    master_department = db.relationship('DepartmentMaster', backref='hospital_departments')

    @property
    def name(self):
        return self.master_department.english_name if self.master_department else 'Unknown'

    @property
    def hindi_name(self):
        return self.master_department.hindi_name if self.master_department else ''
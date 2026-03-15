from ..models import db, Hospital, Department, DepartmentMaster, Doctor, Patient, Token, Queue
from qr_generator import generate_qr


def slugify(text):
    return ''.join(c.lower() if c.isalnum() else '-' for c in text).replace('--', '-').strip('-')


def seed_database():
    # Seed master departments first
    master_departments = [
        ('GM', 'General Medicine', 'सामान्य चिकित्सा'),
        ('Dental', 'Dental', 'दंत चिकित्सा'),
        ('ENT', 'ENT', 'नाक कान गला'),
        ('Orthopedic', 'Orthopedic', 'हड्डी रोग'),
        ('Dermatology', 'Dermatology', 'त्वचा रोग'),
        ('Pediatrics', 'Pediatrics', 'बाल रोग'),
        ('Cardiology', 'Cardiology', 'हृदय रोग'),
        ('Gynecology', 'Gynecology', 'स्त्री रोग')
    ]
    for dept_id, eng, hin in master_departments:
        existing_master = DepartmentMaster.query.filter_by(department_id=dept_id).first()
        if not existing_master:
            db.session.add(DepartmentMaster(department_id=dept_id, english_name=eng, hindi_name=hin))
    db.session.commit()

    # Avoid duplicates by hospital admin username
    if Hospital.query.first():
        print('Database already seeded. Skipping...')
        return

    print('Seeding database with demo data...')

    hospital_templates = [
        {
            'name': 'CityCare Hospital Jaipur',
            'address': 'MI Road, Jaipur, Rajasthan 302001',
            'admin_username': 'admin_citycare',
            'admin_password': 'admin123',
            'departments': {
                'General Medicine': [
                    {'doctor_id': 'DOC101', 'name': 'Dr Neha Gupta', 'avg_consultation_time': 6},
                    {'doctor_id': 'DOC102', 'name': 'Dr Amit Sharma', 'avg_consultation_time': 7}
                ],
                'Dermatology': [
                    {'doctor_id': 'DOC103', 'name': 'Dr Kavita Singh', 'avg_consultation_time': 7},
                    {'doctor_id': 'DOC104', 'name': 'Dr Ritu Agarwal', 'avg_consultation_time': 6}
                ],
                'Pediatrics': [
                    {'doctor_id': 'DOC105', 'name': 'Dr Meera Joshi', 'avg_consultation_time': 8},
                    {'doctor_id': 'DOC106', 'name': 'Dr Rohit Verma', 'avg_consultation_time': 7}
                ]
            },
            'qr_file': 'citycare_hospital_qr.png'
        },
        {
            'name': 'Apex Multispeciality Clinic Jaipur',
            'address': 'Malviya Nagar, Jaipur, Rajasthan 302017',
            'admin_username': 'admin_apex',
            'admin_password': 'admin123',
            'departments': {
                'Orthopedic': [
                    {'doctor_id': 'DOC201', 'name': 'Dr Rajesh Mehta', 'avg_consultation_time': 10},
                    {'doctor_id': 'DOC202', 'name': 'Dr Sunil Gupta', 'avg_consultation_time': 9}
                ],
                'ENT': [
                    {'doctor_id': 'DOC203', 'name': 'Dr Anil Kapoor', 'avg_consultation_time': 7},
                    {'doctor_id': 'DOC204', 'name': 'Dr Preeti Sharma', 'avg_consultation_time': 8}
                ],
                'General Medicine': [
                    {'doctor_id': 'DOC205', 'name': 'Dr Siddharth Jain', 'avg_consultation_time': 6},
                    {'doctor_id': 'DOC206', 'name': 'Dr Rakesh Gupta', 'avg_consultation_time': 7}
                ]
            },
            'qr_file': 'apex_clinic_qr.png'
        },
        {
            'name': 'Sunrise Health Centre Jaipur',
            'address': 'Vaishali Nagar, Jaipur, Rajasthan 302021',
            'admin_username': 'admin_sunrise',
            'admin_password': 'admin123',
            'departments': {
                'General Medicine': [
                    {'doctor_id': 'DOC301', 'name': 'Dr Priya Singh', 'avg_consultation_time': 6},
                    {'doctor_id': 'DOC302', 'name': 'Dr Arjun Mehta', 'avg_consultation_time': 7}
                ],
                'Dermatology': [
                    {'doctor_id': 'DOC303', 'name': 'Dr Kavita Patel', 'avg_consultation_time': 7},
                    {'doctor_id': 'DOC304', 'name': 'Dr Sangeeta Rana', 'avg_consultation_time': 6}
                ]
            },
            'qr_file': 'sunrise_health_qr.png'
        },
        {
            'name': 'Metro Dental Clinic Jaipur',
            'address': 'Ajmer Road, Jaipur, Rajasthan 302006',
            'admin_username': 'admin_metro',
            'admin_password': 'admin123',
            'departments': {
                'Dental': [
                    {'doctor_id': 'DOC401', 'name': 'Dr Rakesh Verma', 'avg_consultation_time': 6},
                    {'doctor_id': 'DOC402', 'name': 'Dr Pooja Bansal', 'avg_consultation_time': 5},
                    {'doctor_id': 'DOC403', 'name': 'Dr Nisha Roy', 'avg_consultation_time': 6}
                ]
            },
            'qr_file': 'metro_dental_qr.png'
        },
        {
            'name': 'HealthyLife Family Clinic Jaipur',
            'address': 'C Scheme, Jaipur, Rajasthan 302001',
            'admin_username': 'admin_healthylife',
            'admin_password': 'admin123',
            'departments': {
                'General Medicine': [
                    {'doctor_id': 'DOC501', 'name': 'Dr Anjali Verma', 'avg_consultation_time': 6},
                    {'doctor_id': 'DOC502', 'name': 'Dr Manish Jain', 'avg_consultation_time': 7}
                ],
                'Pediatrics': [
                    {'doctor_id': 'DOC503', 'name': 'Dr Meera Joshi', 'avg_consultation_time': 8},
                    {'doctor_id': 'DOC504', 'name': 'Dr Ritu Sharma', 'avg_consultation_time': 7}
                ]
            },
            'qr_file': 'healthylife_clinic_qr.png'
        },
        {
            'name': 'Sharma ENT Centre Jaipur',
            'address': 'Pratap Nagar, Jaipur, Rajasthan 302033',
            'admin_username': 'admin_sharmaent',
            'admin_password': 'admin123',
            'departments': {
                'ENT': [
                    {'doctor_id': 'DOC601', 'name': 'Dr Anil Kapoor', 'avg_consultation_time': 7},
                    {'doctor_id': 'DOC602', 'name': 'Dr Pooja Sharma', 'avg_consultation_time': 8}
                ]
            },
            'qr_file': 'sharma_ent_qr.png'
        }
    ]

    created = []
    for hdata in hospital_templates:
        existing = Hospital.query.filter_by(admin_username=hdata['admin_username']).first()
        if existing:
            print(f"Skipping existing hospital: {hdata['name']}")
            continue

        hospital = Hospital(
            name=hdata['name'],
            address=hdata['address'],
            admin_username=hdata['admin_username']
        )
        hospital.set_password(hdata['admin_password'])
        db.session.add(hospital)
        db.session.commit()

        for dept_name, docs in hdata['departments'].items():
            master = DepartmentMaster.query.filter_by(english_name=dept_name).first()
            if not master:
                master = DepartmentMaster(department_id=dept_name.lower().replace(' ', '_'), english_name=dept_name, hindi_name=dept_name)
                db.session.add(master)
                db.session.commit()

            department = Department(hospital_id=hospital.id, master_department_id=master.id)
            db.session.add(department)
            db.session.commit()
            for doc in docs:
                doctor = Doctor(
                    doctor_id=doc['doctor_id'],
                    name=doc['name'],
                    hospital_id=hospital.id,
                    department_id=department.id,
                    avg_consultation_time=doc['avg_consultation_time']
                )
                doctor.set_password('password123')
                db.session.add(doctor)
            db.session.commit()

        qr_filename = hdata['qr_file']
        generate_qr(hospital.id, output_path='static/hospital_qr/', filename=qr_filename)
        hospital.qr_code = qr_filename
        db.session.commit()

        created.append((hospital.name, hospital.admin_username, hdata['admin_password'], qr_filename))

    print('\nDEMO DATA READY\n')
    print('ADMIN ACCOUNTS')
    for name, admin, pwd, qr in created:
        print(f"{admin} / {pwd}")
    print('\nHOSPITAL QR CODES')
    for name, admin, pwd, qr in created:
        print(f"{name}\nstatic/hospital_qr/{qr}\n")

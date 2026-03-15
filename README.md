# E-Parchi - Smart Hospital Queue Management System

A modern, production-ready hospital queue management platform built with Flask, featuring real-time queue tracking, doctor dashboards, and AI-powered health assistance.

## 🚀 Features

### Patient Features
- **QR Code Scanning**: Scan hospital QR codes to join queues
- **Smart Registration**: Multi-step patient registration with validation
- **Real-time Queue Tracking**: Live queue status and estimated wait times
- **Token Management**: View all your queue tokens and visit history
- **AI Health Assistant**: Get medical advice and health information

### Doctor Features
- **Secure Login**: Doctor authentication with unique IDs
- **Queue Control**: Start, finish, and manage consultations
- **Real-time Dashboard**: Live queue status and patient information
- **Break Management**: Pause/resume queue functionality
- **Patient Details**: Access patient information and symptoms

### Admin Features
- **Hospital Management**: Register and manage hospitals
- **Doctor Management**: Add and manage doctors
- **Queue Monitoring**: Monitor all doctors' queues
- **Department Management**: Organize doctors by departments

## 🏗️ Architecture

The application follows a modular architecture:

```
backend/
├── models/           # Database models
│   ├── hospital_model.py
│   ├── department_model.py
│   ├── doctor_model.py
│   ├── patient_model.py
│   ├── token_model.py
│   └── queue_model.py
├── services/         # Business logic
│   ├── queue_service.py
│   ├── token_service.py
│   └── doctor_service.py
├── routes/           # API endpoints
│   ├── patient_routes.py
│   ├── doctor_routes.py
│   ├── admin_routes.py
│   └── queue_routes.py
└── seed/             # Database seeding
    └── seed_data.py
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- SQLite (default) or PostgreSQL/MySQL

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd e-parchi
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your-secret-key-change-in-production
   DATABASE_URL=sqlite:///database.db
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Patient Portal: http://localhost:5000
   - Doctor Login: http://localhost:5000/doctor/login
   - Admin Login: http://localhost:5000/admin/login

## 🎯 Demo Credentials

### Hospital Admins
- **CityCare Hospital**: citycare_admin / admin123
- **Apex Multispeciality Clinic**: apex_admin / admin123
- **Sunrise Health Centre**: sunrise_admin / admin123

### Doctors (All use password: password123)
- **Dr Neha Gupta (DOC101)** - General Medicine
- **Dr Amit Sharma (DOC102)** - General Medicine
- **Dr Rakesh Verma (DOC103)** - Dental
- **Dr Kavita Singh (DOC104)** - Dermatology
- **Dr Rajesh Mehta (DOC105)** - Orthopedic
- **Dr Anil Kapoor (DOC106)** - ENT
- **Dr Meera Joshi (DOC107)** - Pediatrics

## 🚀 Deployment

### Render Deployment

1. **Create a Render account** at https://render.com

2. **Connect your repository**
   - Create a new Web Service
   - Connect your GitHub repository

3. **Configure build settings**
   ```bash
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Set environment variables**
   ```
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=sqlite:///database.db
   ```

5. **Deploy**
   - Render will automatically build and deploy your application
   - Your app will be available at `https://your-app-name.onrender.com`

### Other Platforms

The application can be deployed to any platform supporting Python/Flask:

- **Heroku**: Use `Procfile` with `web: gunicorn app:app`
- **AWS Elastic Beanstalk**: Standard Python application
- **Google App Engine**: Standard Python application
- **DigitalOcean App Platform**: Connect repository and configure

## 📊 Database Schema

### Core Tables
- **Hospital**: Hospital information and admin credentials
- **Department**: Hospital departments (General Medicine, Dental, etc.)
- **Doctor**: Doctor profiles with authentication
- **Patient**: Patient information
- **Token**: Queue tokens with status tracking
- **Queue**: Doctor queue states (active/paused)

### Relationships
- Hospital → Departments → Doctors
- Doctor → Tokens → Patients
- Doctor → Queue (1:1)

## 🔄 Queue Logic

### Token Generation
- Sequential numbering per doctor (A-01, A-02, etc.)
- Automatic wait time calculation
- Real-time queue position updates

### Doctor Queue Control
- **Start Consultation**: Begin serving next patient
- **Finish Consultation**: Complete current consultation, advance queue
- **Call Next**: Manually advance to next patient
- **Pause/Resume**: Temporary queue suspension

### Real-time Updates
- Patients see live queue status
- Doctors see real-time queue changes
- Automatic refresh every 10 seconds

## 🤖 AI Health Assistant

Powered by OpenAI GPT, the assistant provides:
- Medical information and advice
- Symptom analysis
- Health recommendations
- General wellness tips

## 🔒 Security Features

- Secure password hashing
- Session management
- CSRF protection
- Input validation
- SQL injection prevention

## 📱 Responsive Design

- Mobile-first approach
- Bootstrap 5 framework
- Modern card-based UI
- Touch-friendly interfaces

## 🧪 Testing

Run the application and test:
1. Patient registration flow
2. Doctor queue management
3. Real-time updates
3. Multi-user scenarios
4. AI assistant functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions, please open an issue in the repository.

- Multiple hospitals support
- Online appointments
- Doctor schedules
- Notifications
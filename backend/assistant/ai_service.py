"""
AI Healthcare Assistant Service for E-Parchi Platform
Provides intelligent healthcare guidance and platform navigation assistance.
"""

from openai import OpenAI
from flask import session
from ..models import Hospital, Department, Doctor, Token
import os
from typing import Dict, List, Optional

class HealthcareAssistant:
    """
    AI-powered healthcare assistant that provides symptom guidance,
    department recommendations, and platform navigation help.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"OpenAI client init failed: {e}")
                self.client = None

        # Emergency symptoms for urgent triage
        self.emergency_symptoms = [
            'chest pain', 'difficulty breathing', 'shortness of breath', 'unconscious',
            'severe bleeding', 'seizure', 'stroke', 'loss of consciousness', 'poisoning',
            'major trauma', 'extreme pain', 'sudden weakness', 'sudden confusion',
            'slurred speech', 'severe abdominal pain', 'severe allergic reaction'
        ]

        # Symptom to department mapping
        self.symptom_department_map = {
            # Dental
            'tooth': 'Dental', 'teeth': 'Dental', 'dental': 'Dental', 'mouth': 'Dental',
            'gum': 'Dental', 'jaw': 'Dental',

            # ENT (Ear, Nose, Throat)
            'ear': 'ENT', 'hearing': 'ENT', 'nose': 'ENT', 'throat': 'ENT',
            'sinus': 'ENT', 'tonsil': 'ENT',

            # Dermatology
            'skin': 'Dermatology', 'rash': 'Dermatology', 'acne': 'Dermatology',
            'allergy': 'Dermatology', 'itching': 'Dermatology', 'hair': 'Dermatology',

            # Ophthalmology
            'eye': 'Ophthalmology', 'vision': 'Ophthalmology', 'sight': 'Ophthalmology',
            'blind': 'Ophthalmology', 'glasses': 'Ophthalmology',

            # Gastroenterology
            'stomach': 'Gastroenterology', 'digest': 'Gastroenterology', 'nausea': 'Gastroenterology',
            'vomiting': 'Gastroenterology', 'diarrhea': 'Gastroenterology', 'liver': 'Gastroenterology',

            # General Medicine
            'fever': 'General Medicine', 'headache': 'General Medicine', 'cold': 'General Medicine',
            'flu': 'General Medicine', 'cough': 'General Medicine', 'pain': 'General Medicine',
            'tired': 'General Medicine', 'weak': 'General Medicine',

            # Cardiology
            'heart': 'Cardiology', 'chest': 'Cardiology', 'blood pressure': 'Cardiology',
            'palpitations': 'Cardiology',

            # Orthopedics
            'bone': 'Orthopedics', 'joint': 'Orthopedics', 'fracture': 'Orthopedics',
            'back': 'Orthopedics', 'knee': 'Orthopedics', 'shoulder': 'Orthopedics',

            # Pediatrics
            'child': 'Pediatrics', 'baby': 'Pediatrics', 'infant': 'Pediatrics',
            'pediatric': 'Pediatrics',

            # Gynecology
            'pregnant': 'Gynecology', 'period': 'Gynecology', 'menstrual': 'Gynecology',
            'gynecology': 'Gynecology', 'obstetrics': 'Gynecology',

            # Neurology
            'headache': 'Neurology', 'migraine': 'Neurology', 'seizure': 'Neurology',
            'nerve': 'Neurology', 'brain': 'Neurology'
        }

    def detect_emergency(self, symptoms: str) -> bool:
        """
        Detect if symptoms indicate a medical emergency.
        """
        symptoms_lower = symptoms.lower()
        return any(emergency in symptoms_lower for emergency in self.emergency_symptoms)

    def get_user_token_context(self) -> Dict:
        """
        Get information about the user's current token and queue status.
        """
        patient_id = session.get('patient_id')
        if not patient_id:
            return {'has_token': False}

        # Get the most recent active token for this patient
        from ..models import Token
        token = Token.query.filter_by(
            patient_id=patient_id,
            status='waiting'
        ).order_by(Token.created_time.desc()).first()

        if not token:
            return {'has_token': False}

        # Calculate queue position
        patients_ahead = Token.query.filter(
            Token.doctor_id == token.doctor_id,
            Token.status == 'waiting',
            Token.created_time < token.created_time
        ).count()

        # Calculate estimated wait time
        est_wait = patients_ahead * token.doctor.avg_consultation_time

        return {
            'has_token': True,
            'token_number': token.token_number,
            'doctor_name': token.doctor.name,
            'department_name': token.doctor.department.name,
            'patients_ahead': patients_ahead,
            'estimated_wait': est_wait,
            'created_time': token.created_time.strftime('%H:%M')
        }

    def get_hospital_context(self) -> Dict:
        """
        Get context information about the current hospital and available services.
        """
        hospital_id = session.get('hospital_id')
        if not hospital_id:
            return {
                'has_hospital': False,
                'message': 'Please scan a hospital QR code first to get personalized recommendations.'
            }

        hospital = Hospital.query.get(hospital_id)
        if not hospital:
            return {
                'has_hospital': False,
                'message': 'Hospital information not found. Please scan the QR code again.'
            }

        departments = Department.query.filter_by(hospital_id=hospital_id).all()
        department_names = [dept.name for dept in departments]

        # Get queue information
        queue_info = []
        for dept in departments:
            doctors = Doctor.query.filter_by(department_id=dept.id).all()
            for doctor in doctors:
                waiting_count = Token.query.filter_by(doctor_id=doctor.id, status='waiting').count()
                est_wait = waiting_count * doctor.avg_consultation_time
                queue_info.append({
                    'doctor': doctor.name,
                    'department': dept.name,
                    'waiting': waiting_count,
                    'est_wait': est_wait
                })

        return {
            'has_hospital': True,
            'hospital_name': hospital.name,
            'departments': department_names,
            'queue_info': queue_info
        }

    def suggest_department_from_symptoms(self, symptoms: str) -> Optional[str]:
        """
        Suggest department based on mentioned symptoms.
        """
        symptoms_lower = symptoms.lower()

        for symptom_keyword, department in self.symptom_department_map.items():
            if symptom_keyword in symptoms_lower:
                return department

        return None

    def get_queue_recommendations(self, context: Dict) -> str:
        """
        Generate queue recommendations based on current hospital context.
        """
        if not context.get('has_hospital', False):
            return ""

        queue_info = context.get('queue_info', [])
        if not queue_info:
            return "No doctors currently available in the queue system."

        # Find doctor with shortest wait time
        best_doctor = min(queue_info, key=lambda x: x['est_wait'])

        recommendations = f"\n\n**Current Queue Status:**\n"
        for info in sorted(queue_info, key=lambda x: x['est_wait']):
            recommendations += f"• Dr. {info['doctor']} ({info['department']}): {info['waiting']} waiting, ~{info['est_wait']} min wait\n"

        recommendations += f"\n**Recommended:** Dr. {best_doctor['doctor']} in {best_doctor['department']} (shortest wait: ~{best_doctor['est_wait']} min)"

        return recommendations

    def build_system_prompt(self, context: Dict, token_context: Dict = None) -> str:
        """
        Build comprehensive system prompt for the AI assistant.
        """
        hospital_info = ""
        if context.get('has_hospital', False):
            hospital_name = context['hospital_name']
            departments = context['departments']
            hospital_info = f"""
You are assisting a patient at {hospital_name}.
Available departments: {', '.join(departments)}
{self.get_queue_recommendations(context)}
"""
        else:
            hospital_info = """
The patient hasn't scanned a hospital QR code yet.
Guide them to scan the hospital QR code first for personalized recommendations.
"""

        token_info = ""
        if token_context and token_context.get('has_token', False):
            token_info = f"""
Current patient token information:
- Token: {token_context['token_number']}
- Doctor: {token_context['doctor_name']}
- Department: {token_context['department_name']}
- Patients ahead: {token_context['patients_ahead']}
- Estimated wait: {token_context['estimated_wait']} minutes
- Token created: {token_context['created_time']}
"""

        base_prompt = f"""You are an AI healthcare assistant integrated into the E-Parchi hospital platform.

Your role is to:
1. Help patients identify the correct hospital department based on their symptoms
2. Provide basic healthcare guidance and explain hospital procedures
3. Guide users through the E-Parchi platform navigation
4. Give queue recommendations when patients ask about wait times
5. Answer questions about their current token status and queue position

IMPORTANT: You should NEVER give serious medical diagnoses or treatment advice.
Instead, guide patients to the appropriate department or healthcare professional.

{hospital_info}
{token_info}

Symptom-to-Department Guidelines:
- Dental issues (tooth pain, gum problems) → Dental Department
- Ear/Nose/Throat problems → ENT Department
- Skin conditions, rashes, allergies → Dermatology Department
- Eye problems, vision issues → Ophthalmology Department
- Stomach/digestion issues → Gastroenterology Department
- General symptoms (fever, headache, cold) → General Medicine Department
- Heart/chest problems → Cardiology Department
- Bone/joint issues → Orthopedics Department
- Children's health → Pediatrics Department
- Women's health/pregnancy → Gynecology Department
- Severe headaches, neurological symptoms → Neurology Department

Platform Navigation:
- To get a token: Scan QR → Register → Select Department → Choose Doctor → Get Token
- Check queue status: Use the "My Tokens" section
- Access medical records: Use the "Medical Records" section
- Get health guidance: Use this AI assistant

Always be helpful, professional, and encourage patients to seek appropriate medical care.
If symptoms sound serious, recommend immediate medical attention."""

        return base_prompt

    def get_response(self, user_message: str) -> str:
        """
        Get AI response for user message with full context awareness.
        """
        try:
            # Check for emergency symptoms first
            if self.detect_emergency(user_message):
                return """⚠️ **EMERGENCY SYMPTOMS DETECTED**

Your symptoms may indicate a medical emergency. Please:

1. **Seek immediate medical attention**
2. **Call emergency services** (911 or local emergency number)
3. **Go to the nearest emergency room**

**Do not wait in line for these symptoms:**
- Chest pain or tightness
- Difficulty breathing
- Severe bleeding
- Loss of consciousness
- Severe allergic reactions

**This is a safety feature to protect patient health.**"""

            # Get hospital and token context
            context = self.get_hospital_context()
            token_context = self.get_user_token_context()

            # Build system prompt
            system_prompt = self.build_system_prompt(context, token_context)

            # Check for quick symptom-based suggestions
            suggested_dept = self.suggest_department_from_symptoms(user_message)
            if suggested_dept and context.get('has_hospital', False):
                if suggested_dept in context.get('departments', []):
                    user_message += f"\n\n[SYSTEM NOTE: Patient mentioned symptoms suggesting {suggested_dept} department, which is available at this hospital]"
                else:
                    user_message += f"\n\n[SYSTEM NOTE: Patient mentioned symptoms suggesting {suggested_dept} department, but it's not available at {context['hospital_name']}]"

            # If OpenAI client cannot be used, fallback to local rules
            if not self.client:
                recommended_dept = self.suggest_department_from_symptoms(user_message)
                if recommended_dept:
                    return f"It seems your symptoms match {recommended_dept}. Please consult the {recommended_dept} department at your hospital."
                return "I can help you with general hospital navigation and queue guidance. Please describe your symptoms or ask about how the queue works."

            # Get AI response (OpenAI may be configured)
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API call failed: {e}")
                # fallback local response
                suggested_dept = self.suggest_department_from_symptoms(user_message)
                if suggested_dept:
                    return f"Based on your symptoms, I recommend the {suggested_dept} department. Please select that department for your visit."
                return "I can guide you on departments and queue steps. Please ask your question again."

        except Exception as e:
            print(f"AI Assistant Error: {str(e)}")
            return "Sorry, I'm having trouble connecting right now. Please try again in a moment, or contact hospital staff for immediate assistance."

# Global assistant instance
_assistant_instance = None

def get_assistant() -> HealthcareAssistant:
    """Get or create the healthcare assistant instance."""
    global _assistant_instance
    if _assistant_instance is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                _assistant_instance = HealthcareAssistant(api_key)
            except Exception as e:
                print(f"Failed initializing OpenAI assistant: {e}")
                _assistant_instance = HealthcareAssistant(None)
        else:
            print("OPENAI_API_KEY not set. Using local fallback assistant.")
            _assistant_instance = HealthcareAssistant(None)
    return _assistant_instance
from __future__ import annotations

from typing import Any, Dict, List


class SmartTriageService:
    """Heuristic triage engine for hackathon-friendly AI queue prioritization."""

    EMERGENCY_SIGNALS = {
        'chest pain': 45,
        'difficulty breathing': 50,
        'shortness of breath': 45,
        'unconscious': 60,
        'loss of consciousness': 60,
        'seizure': 50,
        'stroke': 55,
        'slurred speech': 45,
        'severe bleeding': 55,
        'major trauma': 55,
        'poisoning': 50,
        'heart attack': 60,
        'not breathing': 70,
        'severe allergic reaction': 55,
        'anaphylaxis': 60,
        'extreme pain': 35,
    }

    PRIORITY_SIGNALS = {
        'high fever': 24,
        'fever': 12,
        'vomiting': 12,
        'dehydration': 18,
        'fracture': 30,
        'pregnancy pain': 25,
        'migraine': 18,
        'fainting': 24,
        'dizziness': 14,
        'abdominal pain': 18,
        'infection': 18,
        'burn': 24,
        'bleeding': 20,
        'allergy': 18,
        'asthma': 22,
        'wheezing': 24,
    }

    @classmethod
    def assess_patient(cls, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        symptoms = (patient_data.get('symptoms') or '').strip().lower()
        age = int(patient_data.get('age') or 0)
        score = 10
        matched_signals: List[str] = []

        for signal, weight in cls.EMERGENCY_SIGNALS.items():
            if signal in symptoms:
                score += weight
                matched_signals.append(signal)

        for signal, weight in cls.PRIORITY_SIGNALS.items():
            if signal in symptoms and signal not in matched_signals:
                score += weight
                matched_signals.append(signal)

        if age and age <= 5:
            score += 10
            matched_signals.append('young child risk')
        elif age >= 70:
            score += 15
            matched_signals.append('elderly risk')

        if any(word in symptoms for word in ['severe', 'sudden', 'unable to', 'collapsed', 'critical']):
            score += 15
            matched_signals.append('critical language')

        score = min(score, 100)
        emergency_flag = any(signal in symptoms for signal in cls.EMERGENCY_SIGNALS) or score >= 85

        if emergency_flag:
            priority_level = 'EMERGENCY'
            recommendation = 'Immediate medical response required. Patient bypasses the regular queue.'
        elif score >= 60:
            priority_level = 'PRIORITY'
            recommendation = 'Fast-track this patient ahead of routine visits and monitor closely.'
        else:
            priority_level = 'NORMAL'
            recommendation = 'Standard queue placement is appropriate.'

        return {
            'severity_score': score,
            'emergency_flag': emergency_flag,
            'priority_level': priority_level,
            'matched_signals': matched_signals,
            'triage_note': recommendation,
        }

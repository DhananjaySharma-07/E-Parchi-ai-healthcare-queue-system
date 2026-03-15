"""
AI Assistant Routes for E-Parchi Platform
Handles API endpoints for the healthcare assistant functionality.
"""

from flask import Blueprint, request, jsonify, render_template
from backend.assistant.ai_service import get_assistant

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/assistant')
def assistant_page():
    return render_template('assistant.html')

@assistant_bp.route('/assistant/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for AI healthcare assistant.
    Expects JSON payload with 'message' field.
    Returns JSON response with 'reply' field.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Invalid request format',
                'reply': 'Please provide a valid message.'
            }), 400

        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({
                'reply': 'Please provide a message to continue our conversation.'
            })

        # Get AI response
        assistant = get_assistant()
        reply = assistant.get_response(user_message)

        return jsonify({'reply': reply})

    except ValueError as e:
        return jsonify({
            'error': 'Configuration error',
            'reply': 'The assistant service is not properly configured. Please contact support.'
        }), 500

    except Exception as e:
        print(f"Assistant API Error: {str(e)}")
        return jsonify({
            'error': 'Service temporarily unavailable',
            'reply': 'Sorry, the assistant is temporarily unavailable. Please try again later or contact hospital staff for immediate assistance.'
        }), 500

@assistant_bp.route('/assistant/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify assistant service is working.
    """
    try:
        assistant = get_assistant()
        # Simple test to verify API key works
        return jsonify({
            'status': 'healthy',
            'message': 'AI Assistant service is operational'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
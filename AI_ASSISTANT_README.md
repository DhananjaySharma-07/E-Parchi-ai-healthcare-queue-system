# E-Parchi AI Healthcare Assistant

## Overview

E-Parchi is a smart hospital queue management system enhanced with an AI-powered healthcare assistant that provides intelligent guidance for patients navigating healthcare services.

## AI Assistant Features

### 🤖 Smart Healthcare Guidance
- **Symptom-to-Department Mapping**: Automatically suggests appropriate hospital departments based on patient symptoms
- **Context-Aware Responses**: Provides personalized recommendations based on the scanned hospital
- **Queue Intelligence**: Offers real-time queue status and wait time recommendations
- **Platform Navigation**: Guides users through the E-Parchi system workflow

### 🏥 Department Recommendations
The AI assistant can recommend departments for various symptoms:

| Symptom Category | Department |
|-----------------|------------|
| Dental issues (tooth pain, gum problems) | Dental |
| Ear/Nose/Throat problems | ENT |
| Skin conditions, rashes, allergies | Dermatology |
| Eye problems, vision issues | Ophthalmology |
| Stomach/digestion issues | Gastroenterology |
| General symptoms (fever, headache, cold) | General Medicine |
| Heart/chest problems | Cardiology |
| Bone/joint issues | Orthopedics |
| Children's health | Pediatrics |
| Women's health/pregnancy | Gynecology |
| Severe headaches, neurological symptoms | Neurology |

### 💬 Chat Interface Features
- **Modern UI**: Clean, mobile-responsive chat interface with message bubbles
- **Suggestion Chips**: Quick-access buttons for common questions
- **Typing Indicators**: Visual feedback during AI processing
- **Error Handling**: Graceful handling of API failures
- **Context Preservation**: Maintains conversation context throughout the session

## Technical Implementation

### Backend Architecture
```
backend/
├── assistant/
│   ├── ai_service.py          # Core AI service with OpenAI integration
│   └── assistant_routes.py    # Flask routes for assistant endpoints
```

### Key Components

#### AI Service (`ai_service.py`)
- **HealthcareAssistant Class**: Main service class handling AI interactions
- **Context Awareness**: Retrieves hospital and queue information from database
- **Symptom Analysis**: Maps symptoms to appropriate departments
- **System Prompts**: Comprehensive prompts defining assistant behavior
- **Error Handling**: Robust error handling for API failures

#### API Endpoints
- `POST /api/assistant/chat`: Main chat endpoint
- `GET /api/assistant/health`: Health check endpoint

### Frontend Implementation
- **Enhanced Chat UI**: Modern chat interface with improved styling
- **Real-time Communication**: AJAX calls to backend API
- **Responsive Design**: Mobile-friendly interface
- **Accessibility**: Screen reader friendly and keyboard navigation

## Usage Examples

### Example Conversations

**User**: "I have a toothache"
**Assistant**: "You should visit the Dental department. You can scan the hospital QR code and book a token with a dentist."

**User**: "Which doctor should I see?"
**Assistant**: "In CityCare Hospital, you can consult Dr. Neha Gupta in the General Medicine department (shortest wait: ~15 min)."

**User**: "How does the queue system work?"
**Assistant**: "The E-Parchi system works by: 1) Scan hospital QR code, 2) Register as patient, 3) Select department, 4) Choose doctor, 5) Get token, 6) Track your position in real-time."

## Security & Privacy

### API Key Management
- API keys stored securely in environment variables
- Never exposed in client-side code
- Server-side only API calls

### Data Handling
- No personal health data stored in conversations
- Session-based context only
- Compliant with healthcare data protection guidelines

### Content Guidelines
- AI responses avoid medical diagnoses
- Clear disclaimers about emergency situations
- Guides users to appropriate professional care

## Configuration

### Environment Setup
1. Copy `key.env` to your environment
2. Ensure `OPENAI_API_KEY` is set with valid API key
3. Install required packages: `pip install openai flask python-dotenv`

### Model Configuration
- **Model**: GPT-4o-mini (optimized for speed and cost)
- **Max Tokens**: 500 tokens per response
- **Temperature**: 0.7 (balanced creativity and accuracy)

## Error Handling

### API Failures
- Graceful degradation with user-friendly messages
- Automatic retry logic for transient failures
- Fallback responses when service unavailable

### Network Issues
- Client-side timeout handling
- Offline detection and messaging
- Service availability monitoring

## Future Enhancements

### Planned Features
- **Multilingual Support**: Support for multiple languages
- **Voice Integration**: Voice-to-text and text-to-voice
- **Advanced Analytics**: Conversation insights and usage patterns
- **Integration APIs**: Connect with hospital management systems
- **Personalized Recommendations**: Learning from user preferences

### Performance Optimizations
- Response caching for common queries
- Load balancing for high-traffic scenarios
- Background processing for complex queries

## Development

### Testing
- Unit tests for AI service functions
- Integration tests for API endpoints
- UI tests for chat interface
- Load testing for concurrent users

### Monitoring
- API usage tracking
- Response time monitoring
- Error rate analytics
- User satisfaction metrics

## Contributing

When extending the AI assistant:

1. **Maintain Medical Safety**: Never provide medical diagnoses
2. **Preserve Context**: Ensure hospital and queue context is maintained
3. **Handle Errors Gracefully**: Always provide fallback responses
4. **Test Thoroughly**: Validate with various symptom scenarios
5. **Document Changes**: Update this README with new features

## Support

For technical support or feature requests:
- Check the application logs for error details
- Verify API key configuration
- Test with simple queries first
- Contact development team for complex issues
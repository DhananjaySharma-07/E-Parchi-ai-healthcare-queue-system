#!/usr/bin/env python3
"""
Test script for E-Parchi AI Healthcare Assistant
Tests the AI service functionality and API endpoints.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('key.env')

def test_ai_service():
    """Test the AI service directly"""
    try:
        # Import the AI service
        sys.path.append('.')
        from backend.assistant.ai_service import get_assistant

        assistant = get_assistant()

        # Test basic response
        test_messages = [
            "I have a toothache",
            "Which department for fever?",
            "How does the queue system work?",
            "What doctors are available?"
        ]

        print("🧪 Testing AI Service...")
        for message in test_messages:
            print(f"\n📝 Testing: '{message}'")
            response = assistant.get_response(message)
            print(f"🤖 Response: {response[:100]}...")

        print("\n✅ AI Service tests completed successfully!")

    except Exception as e:
        print(f"❌ AI Service test failed: {str(e)}")
        return False

    return True

def test_api_endpoint(base_url="http://localhost:5000"):
    """Test the API endpoint"""
    try:
        print("🌐 Testing API Endpoint...")

        # Test health check
        health_response = requests.get(f"{base_url}/api/assistant/health")
        if health_response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False

        # Test chat endpoint
        test_message = "I have a headache"
        chat_response = requests.post(
            f"{base_url}/api/assistant/chat",
            json={"message": test_message},
            headers={"Content-Type": "application/json"}
        )

        if chat_response.status_code == 200:
            data = chat_response.json()
            if "reply" in data:
                print(f"✅ Chat API test passed: {data['reply'][:50]}...")
                return True
            else:
                print(f"❌ Chat API response missing 'reply' field: {data}")
                return False
        else:
            print(f"❌ Chat API test failed: {chat_response.status_code} - {chat_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {base_url}. Is the Flask app running?")
        return False
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 E-Parchi AI Assistant Test Suite")
    print("=" * 50)

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in key.env")
        return False

    if len(api_key) < 50:  # Basic validation
        print("⚠️  OPENAI_API_KEY seems too short. Please verify it's correct.")
        return False

    print("✅ API key found")

    # Test AI service
    service_test = test_ai_service()

    # Test API endpoint
    api_test = test_api_endpoint()

    print("\n" + "=" * 50)
    if service_test and api_test:
        print("🎉 All tests passed! AI Assistant is working correctly.")
        return True
    else:
        print("💥 Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
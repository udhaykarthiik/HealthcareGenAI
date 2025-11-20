"""
Quick test to verify Gemini AI is working
"""
import warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our AI utilities
from documents.ai_utils import MedicalAIAssistant

# Test data - sample medical note
sample_medical_text = """
Patient: John Doe, 45-year-old male
Date: November 20, 2025

Chief Complaint: Persistent chest pain for 2 days

History: Patient presents with acute chest pain radiating to left arm. 
Pain started 2 days ago, worsens with exertion. No previous cardiac history.

Vital Signs:
- BP: 145/95 mmHg
- Pulse: 88 bpm
- Temperature: 98.6°F

Diagnosis: Acute coronary syndrome, possible angina

Treatment Plan:
- Aspirin 325mg daily
- Atorvastatin 40mg at bedtime
- Nitroglycerin sublingual as needed
- Referral to cardiology for stress test
- Follow-up in 1 week

Advised patient to avoid strenuous activity and seek immediate care if pain worsens.
"""

def test_gemini():
    """Test Gemini connection and summarization"""
    
    print("=" * 60)
    print("🧪 TESTING GEMINI AI INTEGRATION")
    print("=" * 60)
    
    try:
        # Initialize AI assistant
        print("\n1️⃣ Initializing Gemini Pro...")
        assistant = MedicalAIAssistant()
        
        # Test entity extraction
        print("\n2️⃣ Testing entity extraction...")
        entities = assistant.extract_medical_entities(sample_medical_text)
        print("\n📋 Extracted Entities:")
        for key, value in entities.items():
            print(f"   • {key}: {value}")
        
        # Test summary generation
        print("\n3️⃣ Testing summary generation...")
        summary = assistant.generate_summary(sample_medical_text, "consultation note")
        print("\n📝 AI-Generated Summary:")
        print("-" * 60)
        print(summary)
        print("-" * 60)
        
        print("\n✅ ALL TESTS PASSED! Gemini is working perfectly!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has GOOGLE_API_KEY")
        print("2. Verify the API key is valid at https://aistudio.google.com/")
        print("3. Ensure you have internet connection")
        print("=" * 60)

if __name__ == "__main__":
    test_gemini()

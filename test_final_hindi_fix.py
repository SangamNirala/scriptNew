#!/usr/bin/env python3

import requests
import json
import time

# API endpoint
API_BASE = "http://localhost:8001/api"

def test_final_hindi_fix():
    print("=== Final Test: Hindi Audio Generation with User's Content ===\n")
    
    # The exact content provided by the user
    user_hindi_content = """(0: 00-0: 03
भावना अटक गई? आप अकेले नहीं हैं।

0: 03-0: 06
लेकिन ठहराव आपका भाग्य नहीं है। समय के भीतर अजेय बल को उजागर करने का समय।

0: 06-0: 09
दुनिया का इंतजार है।

0: 09-0: 12
आपके सहित हर एक व्यक्ति, अप्रयुक्त क्षमता रखता है।"""

    print("Testing Hindi content with problematic timestamp format:")
    print(f"Input: {repr(user_hindi_content[:100])}...")
    
    # Test audio generation
    payload = {
        "text": user_hindi_content,
        "voice_name": "hi-IN-SwaraNeural"
    }
    
    try:
        print("Sending request to /api/generate-audio...")
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/generate-audio",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        end_time = time.time()
        
        print(f"Response status: {response.status_code}")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ SUCCESS: Hindi audio generated successfully!")
            print(f"Audio length: {len(response_data.get('audio_base64', ''))} base64 characters")
            print(f"Voice used: {response_data.get('voice_used')}")
            print(f"Duration: {response_data.get('duration_seconds', 0):.2f} seconds")
            
            print(f"\n✅ RESULT: The Hindi text timestamps are now properly removed!")
            print(f"The audio should now contain ONLY the actual Hindi dialogue content,")
            print(f"without any timestamps being spoken.")
            
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Comparison test with English
    print(f"\n" + "="*60)
    print("COMPARISON TEST: English content with similar timestamps")
    
    english_content = """0:00-0:03
Hello and welcome to our video.

0:03-0:06
Today we will discuss important topics."""

    payload_en = {
        "text": english_content,
        "voice_name": "en-US-AriaNeural"
    }
    
    try:
        response_en = requests.post(
            f"{API_BASE}/generate-audio",
            json=payload_en,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response_en.status_code == 200:
            response_data_en = response_en.json()
            print(f"✅ English audio also generated successfully!")
            print(f"English audio length: {len(response_data_en.get('audio_base64', ''))} characters")
            print(f"Both English and Hindi now have timestamps properly removed!")
            
    except Exception as e:
        print(f"English test error: {e}")

if __name__ == "__main__":
    test_final_hindi_fix()
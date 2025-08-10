#!/usr/bin/env python3

import requests
import json
import time

# API endpoint
API_BASE = "http://localhost:8001/api"

def test_hindi_audio_generation():
    print("=== Testing Hindi Audio Generation API ===\n")
    
    # Test case 1: Pure Hindi dialogue with bare timestamps (the exact issue reported)
    hindi_dialogue_content = """0:00-0:03
नमस्ते और हमारे वीडियो में आपका स्वागत है। आज हम स्वस्थ खाना बनाने के टिप्स पर चर्चा करेंगे।

0:04-0:07
पहले, आइए ताजे अवयवों और उनके महत्व के बारे में बात करते हैं।

0:08-0:11
ताजे फल और सब्जियां आपके स्वास्थ्य के लिए बहुत अच्छी होती हैं।"""

    print("1. HINDI DIALOGUE CONTENT WITH TIMESTAMPS:")
    print(f"Input content: {repr(hindi_dialogue_content[:100])}...")
    
    # First, get available voices
    try:
        voices_response = requests.get(f"{API_BASE}/voices")
        if voices_response.status_code == 200:
            voices = voices_response.json()
            hindi_voices = [v for v in voices if v['language'].startswith('hi-')]
            print(f"Found {len(hindi_voices)} Hindi voices: {[v['name'] for v in hindi_voices]}")
            
            if hindi_voices:
                selected_voice = hindi_voices[0]['name']  # Use first Hindi voice
            else:
                selected_voice = "hi-IN-SwaraNeural"  # Fallback
        else:
            print(f"Failed to get voices: {voices_response.status_code}")
            selected_voice = "hi-IN-SwaraNeural"  # Fallback
            
    except Exception as e:
        print(f"Error getting voices: {e}")
        selected_voice = "hi-IN-SwaraNeural"  # Fallback
    
    # Now test audio generation
    payload = {
        "text": hindi_dialogue_content,
        "voice_name": selected_voice
    }
    
    print(f"Using voice: {selected_voice}")
    print("Sending request to /api/generate-audio...")
    
    try:
        start_time = time.time()
        audio_response = requests.post(
            f"{API_BASE}/generate-audio",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        end_time = time.time()
        
        print(f"Response status: {audio_response.status_code}")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        
        if audio_response.status_code == 200:
            response_data = audio_response.json()
            print(f"✅ SUCCESS: Audio generated successfully")
            print(f"Audio length: {len(response_data.get('audio_base64', ''))} base64 characters")
            print(f"Voice used: {response_data.get('voice_used')}")
            print(f"Duration: {response_data.get('duration_seconds', 0):.2f} seconds")
            
            # The key test: Check backend logs for the cleaned text
            # We'll use the debug output to see what text was actually sent to TTS
            
        else:
            print(f"❌ FAILED: {audio_response.status_code}")
            print(f"Error: {audio_response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Test case 2: English content for comparison
    print("\n" + "="*50)
    print("2. ENGLISH DIALOGUE CONTENT WITH TIMESTAMPS (for comparison):")
    
    english_dialogue_content = """0:00-0:03
Hello and welcome to our video. Today we will discuss healthy cooking tips.

0:04-0:07
First, let's talk about fresh ingredients and their importance."""

    print(f"Input content: {repr(english_dialogue_content)}")
    
    payload_english = {
        "text": english_dialogue_content,
        "voice_name": "en-US-AriaNeural"
    }
    
    try:
        start_time = time.time()
        audio_response_en = requests.post(
            f"{API_BASE}/generate-audio",
            json=payload_english,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        end_time = time.time()
        
        print(f"Response status: {audio_response_en.status_code}")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        
        if audio_response_en.status_code == 200:
            response_data_en = audio_response_en.json()
            print(f"✅ SUCCESS: English audio generated successfully")
            print(f"Audio length: {len(response_data_en.get('audio_base64', ''))} base64 characters")
            print(f"Voice used: {response_data_en.get('voice_used')}")
            
        else:
            print(f"❌ FAILED: {audio_response_en.status_code}")
            print(f"Error: {audio_response_en.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n" + "="*50)
    print("3. CHECKING BACKEND LOGS FOR TIMESTAMP REMOVAL EVIDENCE:")
    
    # Let's check the backend logs to see the cleaned text
    try:
        import subprocess
        log_result = subprocess.run(
            ["tail", "-50", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True
        )
        
        if log_result.returncode == 0:
            print("Recent backend logs:")
            print(log_result.stdout[-1000:])  # Last 1000 characters
        else:
            print("Could not read backend logs")
            
    except Exception as e:
        print(f"Error reading logs: {e}")

if __name__ == "__main__":
    test_hindi_audio_generation()
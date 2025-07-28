#!/usr/bin/env python3

import requests
import json

# Create a simple test to see the exact cleaned text being sent to TTS
def test_clean_output():
    backend_url = "https://f9b94224-42ab-48b2-af99-c98bceaa65d6.preview.emergentagent.com"
    
    test_text = "(0:30 - 0:45) Welcome to our video! This is the important content that should be spoken. (1:00 - 1:15) We have more information here. Remember to subscribe!"
    
    print(f"Original text: {test_text}")
    print("=" * 80)
    
    # Get available voices
    try:
        voices_response = requests.get(f"{backend_url}/api/voices")
        voices = voices_response.json()
        test_voice = voices[0]["name"]
        
        # Generate audio and see what text was actually processed
        audio_response = requests.post(
            f"{backend_url}/api/generate-audio",
            json={
                "text": test_text,
                "voice_name": test_voice
            }
        )
        
        if audio_response.status_code == 200:
            result = audio_response.json()
            print("✅ Audio generation successful")
            print(f"Has audio data: {'audio_base64' in result}")
            
            # Check if the backend logs show the cleaned text (it should in the logs)
            print("\n📝 The cleaned text should be visible in backend logs")
            print("💡 Check backend logs to see the 'Cleaned text' output")
            
        else:
            print(f"❌ Failed: {audio_response.status_code} - {audio_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_clean_output()
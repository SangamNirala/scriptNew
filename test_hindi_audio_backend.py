#!/usr/bin/env python3
"""
Test the actual backend audio generation API with Hindi content to identify where the bug occurs.
"""

import requests
import json
import base64

# Backend URL
BACKEND_URL = "http://localhost:8001"

def test_hindi_audio_generation():
    print("🔍 TESTING ACTUAL BACKEND API FOR HINDI AUDIO GENERATION")
    print("=" * 70)
    
    # 1. Test voice availability first
    print("📋 Step 1: Testing voice availability...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/voices")
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ Found {len(voices)} available voices")
            for voice in voices:
                print(f"   - {voice['name']} ({voice['display_name']}) - {voice['language']} - {voice['gender']}")
            print()
        else:
            print(f"❌ Failed to get voices: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting voices: {e}")
        return
    
    # 2. Test Hindi audio generation with dialogue-only format
    print("📋 Step 2: Testing Hindi audio generation...")
    
    # This is the exact format sent by frontend after translation
    hindi_dialogue_content = """0:00-0:03
नमस्ते और हमारे वीडियो में आपका स्वागत है।

0:03-0:06
आज हम स्वस्थ खाना पकाने की युक्तियों पर चर्चा करेंगे।"""
    
    print(f"📝 Input text (first 100 chars): {hindi_dialogue_content[:100]}...")
    print()
    
    # Test with a Hindi-compatible voice
    test_voice = "en-US-AriaNeural"  # This should handle Hindi
    
    audio_request = {
        "text": hindi_dialogue_content,
        "voice_name": test_voice
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/generate-audio", json=audio_request)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Audio generated successfully")
            print(f"📊 Audio data length: {len(result.get('audio_base64', ''))} characters")
            print(f"📊 Voice used: {result.get('voice_name', 'N/A')}")
            
            # The key test: Check what text was actually processed
            # We need to examine the backend logs or response to see what text was sent to TTS
            
        else:
            print(f"❌ Audio generation failed: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
    
    print()
    
    # 3. Test with English content for comparison
    print("📋 Step 3: Testing English baseline...")
    
    english_dialogue_content = """0:00-0:03
Hello and welcome to our video.

0:03-0:06
Today we will discuss healthy cooking tips."""
    
    english_request = {
        "text": english_dialogue_content,
        "voice_name": test_voice
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/generate-audio", json=english_request)
        print(f"📊 English response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ English audio generated successfully")
            print(f"📊 English audio data length: {len(result.get('audio_base64', ''))} characters")
        else:
            print(f"❌ English audio generation failed: {response.status_code}")
            print(f"📄 English error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error generating English audio: {e}")

def test_with_logs():
    print("\n" + "=" * 70)
    print("🔍 TESTING WITH BACKEND LOG MONITORING")
    print("=" * 70)
    print("The key is to monitor backend logs to see exactly what text is being sent to Edge-TTS...")
    print("If logs show timestamps in the cleaned text, that's where the bug is!")

if __name__ == "__main__":
    print("🚨 BACKEND API TEST: Hindi Audio Generation Bug")
    print()
    
    test_hindi_audio_generation()
    test_with_logs()
    
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print("1. Monitor backend logs during audio generation")
    print("2. Check if extract_clean_script is receiving translated Hindi content")
    print("3. Verify what text is actually passed to Edge-TTS")
    print("4. Test if Edge-TTS voice selection works with Hindi content")
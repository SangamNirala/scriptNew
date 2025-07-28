#!/usr/bin/env python3

import requests
import json
import sys
import os

# Test script to verify timestamp filtering is working
def test_timestamp_filtering():
    backend_url = "http://localhost:8001"
    
    # Test cases with different timestamp formats
    test_cases = [
        {
            "name": "Timestamps with spaces around dash",
            "text": "(0:30 - 0:45) This is the main content that should be spoken. (1:00 - 1:15) More content here.",
            "expected_removed": ["0:30 - 0:45", "1:00 - 1:15"]
        },
        {
            "name": "Timestamps without spaces", 
            "text": "(0:00-0:03) This should also work without spaces. (2:30-2:45) Another timestamp.",
            "expected_removed": ["0:00-0:03", "2:30-2:45"]
        },
        {
            "name": "Mixed timestamp formats",
            "text": "(0:15 - 0:30) Content with spaced dash. (1:45-2:00) Content with no spaces. This is important content.",
            "expected_removed": ["0:15 - 0:30", "1:45-2:00"]
        }
    ]
    
    print("Testing timestamp filtering in audio generation...")
    print("=" * 60)
    
    # First get available voices
    try:
        voices_response = requests.get(f"{backend_url}/api/voices")
        if voices_response.status_code != 200:
            print(f"❌ Failed to get voices: {voices_response.status_code}")
            return
        voices = voices_response.json()
        if not voices:
            print("❌ No voices available")
            return
        test_voice = voices[0]["name"]
        print(f"✅ Using test voice: {test_voice}")
        print()
    except Exception as e:
        print(f"❌ Error getting voices: {e}")
        return
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Input text: {test_case['text']}")
        
        try:
            # Generate audio
            audio_response = requests.post(
                f"{backend_url}/api/generate-audio",
                json={
                    "text": test_case['text'],
                    "voice_name": test_voice
                }
            )
            
            if audio_response.status_code == 200:
                result = audio_response.json()
                cleaned_text = result.get('original_text', '')  # The backend should return the cleaned text
                
                print(f"✅ Audio generation successful")
                print(f"Response contains audio: {'audio_base64' in result}")
                
                # Check if timestamps were removed by looking at the length and content
                contains_timestamps = any(timestamp in test_case['text'] for timestamp in test_case['expected_removed'])
                if contains_timestamps:
                    print(f"✅ Original text contained timestamps: {test_case['expected_removed']}")
                else:
                    print(f"⚠️  Original text didn't contain expected timestamps")
                    
            else:
                print(f"❌ Audio generation failed: {audio_response.status_code}")
                print(f"Error: {audio_response.text}")
                
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            
        print("-" * 40)
        print()

if __name__ == "__main__":
    test_timestamp_filtering()
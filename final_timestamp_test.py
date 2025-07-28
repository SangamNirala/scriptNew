#!/usr/bin/env python3

import requests
import json

def test_timestamp_removal():
    backend_url = "https://f9b94224-42ab-48b2-af99-c98bceaa65d6.preview.emergentagent.com"
    
    # Test case with the user's specific format
    test_text = "(0:30 - 0:45) Welcome to our amazing product! This text should be spoken without timestamps. (1:00 - 1:15) Here's more important information about our service. Don't forget to subscribe!"
    
    print("🧪 TIMESTAMP REMOVAL TEST")
    print("=" * 80)
    print(f"📝 Original text:\n{test_text}\n")
    
    try:
        # Get voices
        voices_response = requests.get(f"{backend_url}/api/voices")
        voices = voices_response.json()
        test_voice = voices[0]["name"]
        
        print(f"🎵 Using voice: {test_voice}\n")
        
        # Generate audio
        audio_response = requests.post(
            f"{backend_url}/api/generate-audio",
            json={
                "text": test_text,
                "voice_name": test_voice
            }
        )
        
        if audio_response.status_code == 200:
            result = audio_response.json()
            
            print("✅ Audio generation successful!")
            print(f"🔊 Generated audio data: {len(result['audio_base64'])} characters")
            
            if 'cleaned_text' in result:
                cleaned = result['cleaned_text']
                print(f"\n🧹 Cleaned text (what was actually spoken):\n{cleaned}\n")
                
                # Check if timestamps were removed
                original_timestamps = ["0:30 - 0:45", "1:00 - 1:15"]
                timestamps_found = [ts for ts in original_timestamps if ts in cleaned]
                
                if not timestamps_found:
                    print("✅ SUCCESS: Timestamps were properly removed from audio!")
                    print("🎯 The TTS will NOT speak the timestamp portions")
                else:
                    print(f"❌ FAILURE: Found timestamps in cleaned text: {timestamps_found}")
                    
                # Show length comparison
                print(f"\n📊 Text processing stats:")
                print(f"   Original length: {len(test_text)} characters")
                print(f"   Cleaned length:  {len(cleaned)} characters")
                print(f"   Reduction:       {len(test_text) - len(cleaned)} characters removed")
                
            else:
                print("⚠️  Cleaned text not available in response")
                
        else:
            print(f"❌ Error: {audio_response.status_code} - {audio_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_timestamp_removal()
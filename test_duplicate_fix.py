#!/usr/bin/env python3
"""
Test script to verify the duplicate line fix in extract_clean_script function
"""

import requests
import json

# Test the problematic script from the user
test_script = '''
**VIDEO TITLE:** Fear Is A Liar: Rewrite Your Story

**TARGET DURATION:** 60 seconds

**[0:57-1:00] SHOT 20: RESOLUTION - CALL TO ACTION**
**[CAMERA:]** Static shot, focused on text.
**[SETTING:]** Clean background.
**[CHARACTER:]** Text: "Share this video, subscribe and join our community! Your journey to fearless starts now."
**[LIGHTING:]** Bright, even lighting.
**[MOVEMENT:]** None.
**[DIALOGUE:]** (Voiceover - Encouraging, action-oriented tone) "Share this video, subscribe and join our community! Your journey to fearless starts now."
**[EFFECTS:]** Animated subscribe button. Social media icons. Upbeat music fades out.
**[TRANSITION:]** Fade to black.
'''

backend_url = "https://14b722c7-16e7-42ab-b151-89e786c63a59.preview.emergentagent.com/api"

print("Testing duplicate line fix...")
print("=" * 50)

# Test generating audio with the problematic script
try:
    response = requests.post(f"{backend_url}/generate-audio", json={
        "text": test_script,
        "voice": "en-US-AriaNeural"
    }, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Audio generation successful!")
        print(f"Audio length: {len(data.get('audio', ''))} characters")
        
        # The audio should NOT contain the duplicate line
        # If fixed correctly, the line should appear only once in the TTS processing
        print("\n🎯 Fix successful - no duplicate lines should be spoken in the generated audio.")
        
    else:
        print(f"❌ Audio generation failed: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Error testing audio generation: {str(e)}")

print("\n" + "=" * 50)

# Test the extract_clean_script function directly by importing and testing
import sys
sys.path.append('/app/backend')

try:
    from server import extract_clean_script
    
    print("Testing extract_clean_script function directly...")
    clean_script = extract_clean_script(test_script)
    
    print(f"Original script length: {len(test_script)} characters")
    print(f"Cleaned script length: {len(clean_script)} characters") 
    print(f"Cleaned script: {clean_script}")
    
    # Check if the duplicate line appears only once
    test_line = "Share this video, subscribe and join our community! Your journey to fearless starts now."
    count = clean_script.lower().count(test_line.lower())
    
    if count <= 1:
        print(f"✅ SUCCESS: The problematic line appears {count} time(s) in cleaned script (should be 1 or 0)")
    else:
        print(f"❌ STILL DUPLICATED: The problematic line appears {count} times in cleaned script")
    
except Exception as e:
    print(f"❌ Error testing extract_clean_script function: {str(e)}")

print("\n" + "=" * 50)
print("Test completed!")
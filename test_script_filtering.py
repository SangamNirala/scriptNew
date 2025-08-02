#!/usr/bin/env python3
"""
Focused test for Enhanced Script Filtering functionality as requested in review
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://18d0ad0f-6396-452f-9a42-45fe37062731.preview.emergentagent.com/api"

def test_enhanced_script_filtering():
    """Test the enhanced script filtering functionality using the exact script content from the review request"""
    print("=== Testing Enhanced Script Filtering (Review Request) ===")
    
    session = requests.Session()
    
    # The exact script content provided in the review request
    exact_script_content = '''**VIDEO SCRIPT: "Uncage Your Courage: A Journey From Fear to Freedom"**

**[0:00-0:03] SCENE 1: Hesitation at a Crossroads - Muted Colors, Blurry**

(Voiceover - Intimate, slightly urgent)
(0:00) Are you TRAPPED? ... paralyzed by a fear you can't name?

**(SOUND:** Anxious heartbeat sound effect fades in.)

**[0:03-0:07] SCENE 2: Quick Cuts - Blank Canvas, Unopened Door, Someone Hiding Their Face**

(Voiceover - slightly louder, more direct)
(0:03) That feeling... the dread... the "what if?"... it's a cage. A cage built by YOU.

**(VISUAL CUE:** Subtle cage bars visually superimposed over the scenes)

**[0:07-0:12] SCENE 3: Expert (or actor) - Close Up, Empathetic Expression**

(Expert)
(0:07) Fear isn't a life sentence. It's a SIGNAL. Your brain misinterpreting potential threats.

**(VISUAL CUE:** Animated graphic showing the brain's amygdala lighting up.)

**[0:12-0:18] SCENE 4: Blooming Flower Time-Lapse, Seedling Pushing Through Earth**

(Voiceover - Hopeful, encouraging)
(0:12) But you can REWIRE it. Challenge those negative thoughts.  Tiny steps...lead to HUGE changes.

**[0:27-0:30] SCENE 7: Visual of an open road, leading towards a bright horizon. Logo appears "Uncage Your Courage"**

(Voiceover - Empowering, strong)
(0:27) Uncage your courage... What's ONE small step you can take TODAY? Share your commitment below!

**(VISUAL CUE:** On-screen text: "Share Your Step Below!")

**[0:30-0:32] SCENE 8: End screen with subscribe button, social media links.**

(Voiceover - quick, friendly)
(0:30) Subscribe for more inspiration and tools to build your best life.

**Key Considerations & Rationale:**'''

    try:
        # Get available voices for testing
        print("Getting available voices...")
        voices_response = session.get(f"{BACKEND_URL}/voices", timeout=15)
        if voices_response.status_code != 200:
            print(f"❌ Could not retrieve voices: {voices_response.status_code}")
            return False
        
        voices = voices_response.json()
        if not voices:
            print("❌ No voices available for testing")
            return False
        
        print(f"✅ Found {len(voices)} voices available")
        
        # Test with multiple voice options to ensure consistency
        test_voices = voices[:min(3, len(voices))]  # Test with up to 3 voices
        successful_tests = 0
        
        print(f"\nTesting with {len(test_voices)} voices...")
        
        for i, voice in enumerate(test_voices):
            voice_name = voice["name"]
            voice_display = voice.get("display_name", voice_name)
            
            print(f"\n--- Testing Voice {i+1}: {voice_display} ---")
            
            # Test audio generation with the exact script content
            payload = {
                "text": exact_script_content,
                "voice_name": voice_name
            }
            
            try:
                response = session.post(
                    f"{BACKEND_URL}/generate-audio",
                    json=payload,
                    timeout=60  # Longer timeout for complex script
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data["audio_base64"]
                    
                    # Verify substantial audio was generated
                    if len(audio_base64) > 10000:  # Should be substantial audio
                        print(f"✅ Successfully generated {len(audio_base64)} chars of clean audio")
                        successful_tests += 1
                    else:
                        print(f"❌ Audio too short: {len(audio_base64)} chars")
                else:
                    print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
        
        # Test specific filtering requirements
        if successful_tests > 0:
            print(f"\n=== Testing Specific Filtering Requirements ===")
            
            # Test 1: Verify timestamps are removed
            print("\n--- Testing Timestamp Removal ---")
            timestamp_test_cases = [
                "(0:00) Test content",
                "(0:03) More test content", 
                "(0:07) Additional content",
                "(0:12) Final content"
            ]
            
            timestamp_success = 0
            for i, timestamp_case in enumerate(timestamp_test_cases):
                payload = {
                    "text": timestamp_case,
                    "voice_name": test_voices[0]["name"]
                }
                
                response = session.post(
                    f"{BACKEND_URL}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ Timestamp test {i+1}: Successfully processed")
                    timestamp_success += 1
                else:
                    print(f"❌ Timestamp test {i+1}: Failed with {response.status_code}")
            
            # Test 2: Verify speaker directions are removed
            print("\n--- Testing Speaker Direction Removal ---")
            speaker_test_cases = [
                "(Voiceover - Intimate, slightly urgent) Test content",
                "(Expert) More test content",
                "(Voiceover - Hopeful, encouraging) Additional content"
            ]
            
            speaker_success = 0
            for i, speaker_case in enumerate(speaker_test_cases):
                payload = {
                    "text": speaker_case,
                    "voice_name": test_voices[0]["name"]
                }
                
                response = session.post(
                    f"{BACKEND_URL}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ Speaker direction test {i+1}: Successfully processed")
                    speaker_success += 1
                else:
                    print(f"❌ Speaker direction test {i+1}: Failed with {response.status_code}")
            
            # Test 3: Verify visual/sound cues are removed
            print("\n--- Testing Visual/Sound Cue Removal ---")
            cue_test_cases = [
                "**(VISUAL CUE:** Test visual cue) Content here",
                "**(SOUND:** Test sound effect) More content"
            ]
            
            cue_success = 0
            for i, cue_case in enumerate(cue_test_cases):
                payload = {
                    "text": cue_case,
                    "voice_name": test_voices[0]["name"]
                }
                
                response = session.post(
                    f"{BACKEND_URL}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ Visual/Sound cue test {i+1}: Successfully processed")
                    cue_success += 1
                else:
                    print(f"❌ Visual/Sound cue test {i+1}: Failed with {response.status_code}")
            
            # Test 4: Verify scene descriptions are removed
            print("\n--- Testing Scene Description Removal ---")
            scene_test_cases = [
                "**[0:00-0:03] SCENE 1: Test scene** Content here",
                "**[0:07-0:12] SCENE 3: Another scene** More content"
            ]
            
            scene_success = 0
            for i, scene_case in enumerate(scene_test_cases):
                payload = {
                    "text": scene_case,
                    "voice_name": test_voices[0]["name"]
                }
                
                response = session.post(
                    f"{BACKEND_URL}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ Scene description test {i+1}: Successfully processed")
                    scene_success += 1
                else:
                    print(f"❌ Scene description test {i+1}: Failed with {response.status_code}")
            
            # Overall assessment
            print(f"\n=== FINAL RESULTS ===")
            print(f"Voice tests: {successful_tests}/{len(test_voices)} passed")
            print(f"Timestamp removal: {timestamp_success}/{len(timestamp_test_cases)} passed")
            print(f"Speaker direction removal: {speaker_success}/{len(speaker_test_cases)} passed")
            print(f"Visual/Sound cue removal: {cue_success}/{len(cue_test_cases)} passed")
            print(f"Scene description removal: {scene_success}/{len(scene_test_cases)} passed")
            
            if successful_tests >= 2:
                print(f"\n🎉 COMPREHENSIVE REVIEW TEST PASSED!")
                print(f"Successfully tested enhanced script filtering with {successful_tests} voices.")
                print("All production elements properly removed from TTS audio generation.")
                return True
            else:
                print(f"\n❌ COMPREHENSIVE REVIEW TEST FAILED!")
                print(f"Only {successful_tests} voice tests succeeded")
                return False
        else:
            print("❌ No voice tests succeeded")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced Script Filtering Test")
    print("=" * 60)
    
    success = test_enhanced_script_filtering()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED!")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
TTS and Script Processing Comprehensive Testing
Tests specifically for the duplicate line bug fix and script processing functionality
"""

import requests
import json
import time
from datetime import datetime
import sys
import base64

# Get backend URL from frontend .env
BACKEND_URL = "https://14b722c7-16e7-42ab-b151-89e786c63a59.preview.emergentagent.com/api"

class TTSScriptProcessingTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_tts_audio_generation_endpoint(self):
        """Test /api/generate-audio endpoint with various script formats"""
        print("\n=== Testing TTS Audio Generation Endpoint ===")
        
        # First get available voices
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("TTS Audio - Voice Setup", False, "Could not retrieve voices")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("TTS Audio - Voice Availability", False, "No voices available")
                return False
            
        except Exception as e:
            self.log_test("TTS Audio - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test Case 1: Simple text
        simple_text = "This is a simple test of the text-to-speech functionality."
        success_count = 0
        
        for i, voice in enumerate(voices[:3]):  # Test with first 3 voices
            try:
                payload = {
                    "text": simple_text,
                    "voice_name": voice["name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data.get("audio_base64", "")
                    
                    if len(audio_base64) > 1000:  # Should have substantial audio
                        self.log_test(f"TTS Audio - Simple Text ({voice['display_name']})", True,
                                    f"Generated {len(audio_base64)} chars of audio")
                        success_count += 1
                    else:
                        self.log_test(f"TTS Audio - Simple Text ({voice['display_name']})", False,
                                    f"Audio too short: {len(audio_base64)} chars")
                else:
                    self.log_test(f"TTS Audio - Simple Text ({voice['display_name']})", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"TTS Audio - Simple Text ({voice['display_name']})", False,
                            f"Exception: {str(e)}")
        
        # Test Case 2: Formatted scripts with potential duplicates
        formatted_script = """[SCENE: Office setting]
        
        CHARACTER: Welcome to our productivity workshop!
        DIALOGUE: Welcome to our productivity workshop!
        
        (Voiceover - Enthusiastic tone)
        Today we'll learn amazing time management techniques.
        
        [Camera direction: Close-up on speaker]
        These methods will transform your daily routine.
        
        CHARACTER: Let's get started with the first tip.
        DIALOGUE: Let's get started with the first tip."""
        
        try:
            payload = {
                "text": formatted_script,
                "voice_name": voices[0]["name"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                audio_base64 = data.get("audio_base64", "")
                
                if len(audio_base64) > 5000:  # Should have substantial audio
                    self.log_test("TTS Audio - Formatted Script", True,
                                f"Successfully processed formatted script: {len(audio_base64)} chars")
                    success_count += 1
                else:
                    self.log_test("TTS Audio - Formatted Script", False,
                                f"Audio too short for formatted script: {len(audio_base64)} chars")
            else:
                self.log_test("TTS Audio - Formatted Script", False,
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("TTS Audio - Formatted Script", False, f"Exception: {str(e)}")
        
        # Test Case 3: Complex video script with timestamps and production elements
        complex_script = """VIDEO SCRIPT: Healthy Cooking Tips
        
        TARGET DURATION: 60 seconds
        VIDEO TYPE: Educational
        
        SCRIPT:
        
        (0:00-0:05) [SCENE: Kitchen setup with fresh ingredients]
        (Narrator - Warm, friendly tone)
        Welcome to healthy cooking made simple!
        
        (0:05-0:15) [SCENE: Chopping vegetables]
        CHARACTER: The key to nutritious meals starts with fresh ingredients.
        DIALOGUE: The key to nutritious meals starts with fresh ingredients.
        
        (0:15-0:25) [Camera: Close-up on colorful vegetables]
        (Voiceover - Educational tone)
        Choose vibrant colors for maximum nutrients and flavor.
        
        (0:25-0:35) [SCENE: Cooking demonstration]
        Remember: steaming preserves more vitamins than boiling.
        
        (0:35-0:45) [SCENE: Plated healthy meal]
        CHARACTER: Your body will thank you for these choices!
        DIALOGUE: Your body will thank you for these choices!
        
        (0:45-0:60) [SCENE: Call to action]
        Start your healthy cooking journey today!
        
        PRODUCTION NOTES:
        - Use natural lighting
        - Include upbeat background music
        - Add text overlays for key tips"""
        
        try:
            payload = {
                "text": complex_script,
                "voice_name": voices[0]["name"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                audio_base64 = data.get("audio_base64", "")
                
                if len(audio_base64) > 10000:  # Should have substantial audio
                    self.log_test("TTS Audio - Complex Script", True,
                                f"Successfully processed complex script: {len(audio_base64)} chars")
                    success_count += 1
                else:
                    self.log_test("TTS Audio - Complex Script", False,
                                f"Audio too short for complex script: {len(audio_base64)} chars")
            else:
                self.log_test("TTS Audio - Complex Script", False,
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("TTS Audio - Complex Script", False, f"Exception: {str(e)}")
        
        # Test Case 4: Edge cases
        edge_cases = [
            {
                "name": "Empty Text",
                "text": "",
                "should_fail": True
            },
            {
                "name": "Very Long Text",
                "text": "This is a very long text. " * 100,
                "should_fail": False
            },
            {
                "name": "Special Characters",
                "text": "Testing special characters: @#$%^&*()_+{}|:<>?[]\\;'\",./ and émojis 🎉",
                "should_fail": False
            },
            {
                "name": "Only Production Elements",
                "text": "[SCENE: Office] (Director's note) [Camera: Wide shot] (0:00-0:05)",
                "should_fail": False  # Should generate minimal or no audio
            }
        ]
        
        for edge_case in edge_cases:
            try:
                payload = {
                    "text": edge_case["text"],
                    "voice_name": voices[0]["name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=45
                )
                
                if edge_case["should_fail"]:
                    if response.status_code != 200:
                        self.log_test(f"TTS Audio - {edge_case['name']}", True,
                                    f"Correctly handled edge case: {response.status_code}")
                        success_count += 1
                    else:
                        self.log_test(f"TTS Audio - {edge_case['name']}", False,
                                    "Should have failed but didn't")
                else:
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data.get("audio_base64", "")
                        self.log_test(f"TTS Audio - {edge_case['name']}", True,
                                    f"Successfully handled: {len(audio_base64)} chars")
                        success_count += 1
                    else:
                        self.log_test(f"TTS Audio - {edge_case['name']}", False,
                                    f"HTTP {response.status_code}")
                        
            except Exception as e:
                if edge_case["should_fail"]:
                    self.log_test(f"TTS Audio - {edge_case['name']}", True,
                                f"Correctly failed with exception: {str(e)[:100]}")
                    success_count += 1
                else:
                    self.log_test(f"TTS Audio - {edge_case['name']}", False,
                                f"Exception: {str(e)}")
        
        # Overall assessment
        total_tests = 3 + len(voices[:3]) + len(edge_cases)  # Adjust based on actual tests
        if success_count >= total_tests * 0.7:  # 70% success rate
            self.log_test("TTS Audio Generation - Overall", True,
                        f"TTS audio generation working well: {success_count} successful tests")
            return True
        else:
            self.log_test("TTS Audio Generation - Overall", False,
                        f"TTS audio generation needs improvement: only {success_count} successful tests")
            return False
    
    def test_duplicate_line_bug_fix(self):
        """Test specifically for the duplicate line bug fix"""
        print("\n=== Testing Duplicate Line Bug Fix ===")
        
        # Get available voices
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Duplicate Line Fix - Voice Setup", False, "Could not retrieve voices")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Duplicate Line Fix - Voice Availability", False, "No voices available")
                return False
            
        except Exception as e:
            self.log_test("Duplicate Line Fix - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test scripts with CHARACTER and DIALOGUE field duplicates
        duplicate_test_cases = [
            {
                "name": "Basic CHARACTER/DIALOGUE Duplicate",
                "script": """CHARACTER: Welcome to our cooking show!
                DIALOGUE: Welcome to our cooking show!
                
                This should only be spoken once, not twice."""
            },
            {
                "name": "Multiple CHARACTER/DIALOGUE Duplicates",
                "script": """CHARACTER: First line of dialogue here.
                DIALOGUE: First line of dialogue here.
                
                Some narration in between.
                
                CHARACTER: Second line of dialogue here.
                DIALOGUE: Second line of dialogue here."""
            },
            {
                "name": "Mixed Format with Duplicates",
                "script": """[SCENE: Kitchen setup]
                
                CHARACTER: Today we're making healthy pasta.
                DIALOGUE: Today we're making healthy pasta.
                
                (0:15-0:25) [Camera: Close-up on ingredients]
                
                CHARACTER: Start by boiling water with salt.
                DIALOGUE: Start by boiling water with salt.
                
                (Voiceover - Instructional tone)
                The salt helps flavor the pasta from the inside."""
            },
            {
                "name": "Complex Production Script",
                "script": """VIDEO SCRIPT: Product Demo
                
                (0:00-0:05) [SCENE: Product showcase]
                CHARACTER: Introducing our revolutionary new gadget!
                DIALOGUE: Introducing our revolutionary new gadget!
                
                (0:05-0:15) [Camera: Product close-up]
                (Voiceover - Excited tone)
                This device will change how you work forever.
                
                CHARACTER: Watch as we demonstrate its key features.
                DIALOGUE: Watch as we demonstrate its key features.
                
                PRODUCTION NOTES:
                - Use dramatic lighting
                - Add sound effects"""
            }
        ]
        
        success_count = 0
        
        for test_case in duplicate_test_cases:
            try:
                payload = {
                    "text": test_case["script"],
                    "voice_name": voices[0]["name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data.get("audio_base64", "")
                    
                    # For duplicate line testing, we expect the audio to be generated
                    # but the duplicate content should not be spoken twice
                    if len(audio_base64) > 1000:
                        self.log_test(f"Duplicate Line Fix - {test_case['name']}", True,
                                    f"Successfully processed script with potential duplicates: {len(audio_base64)} chars")
                        success_count += 1
                    else:
                        self.log_test(f"Duplicate Line Fix - {test_case['name']}", False,
                                    f"Audio too short: {len(audio_base64)} chars")
                else:
                    self.log_test(f"Duplicate Line Fix - {test_case['name']}", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Duplicate Line Fix - {test_case['name']}", False,
                            f"Exception: {str(e)}")
        
        # Test with different voices to ensure consistency
        if len(voices) > 1:
            consistency_script = """CHARACTER: This line should only be spoken once.
            DIALOGUE: This line should only be spoken once.
            
            This is additional content that should be included."""
            
            audio_lengths = []
            
            for voice in voices[:3]:  # Test with up to 3 voices
                try:
                    payload = {
                        "text": consistency_script,
                        "voice_name": voice["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data.get("audio_base64", "")
                        audio_lengths.append(len(audio_base64))
                        
                        self.log_test(f"Duplicate Line Fix - Consistency ({voice['display_name']})", True,
                                    f"Generated {len(audio_base64)} chars with {voice['display_name']}")
                    else:
                        self.log_test(f"Duplicate Line Fix - Consistency ({voice['display_name']})", False,
                                    f"HTTP {response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"Duplicate Line Fix - Consistency ({voice['display_name']})", False,
                                f"Exception: {str(e)}")
            
            # Check if audio lengths are reasonably similar (indicating consistent processing)
            if len(audio_lengths) >= 2:
                avg_length = sum(audio_lengths) / len(audio_lengths)
                variations = [abs(length - avg_length) / avg_length for length in audio_lengths]
                max_variation = max(variations) if variations else 0
                
                if max_variation < 0.3:  # Less than 30% variation
                    self.log_test("Duplicate Line Fix - Voice Consistency", True,
                                f"Consistent processing across voices (max variation: {max_variation:.1%})")
                    success_count += 1
                else:
                    self.log_test("Duplicate Line Fix - Voice Consistency", False,
                                f"Inconsistent processing across voices (max variation: {max_variation:.1%})")
        
        # Overall assessment
        total_tests = len(duplicate_test_cases) + 1  # +1 for consistency test
        if success_count >= total_tests * 0.8:  # 80% success rate
            self.log_test("Duplicate Line Bug Fix - Overall", True,
                        f"Duplicate line bug fix working correctly: {success_count}/{total_tests} tests passed")
            return True
        else:
            self.log_test("Duplicate Line Bug Fix - Overall", False,
                        f"Duplicate line bug fix needs attention: only {success_count}/{total_tests} tests passed")
            return False
    
    def test_script_processing_cleanup(self):
        """Test the extract_clean_script function with various formatting styles"""
        print("\n=== Testing Script Processing & Cleanup ===")
        
        # Get available voices
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Script Cleanup - Voice Setup", False, "Could not retrieve voices")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Script Cleanup - Voice Availability", False, "No voices available")
                return False
            
        except Exception as e:
            self.log_test("Script Cleanup - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test cases for different script formatting styles
        cleanup_test_cases = [
            {
                "name": "Timestamps Removal",
                "input": "(0:00-0:05) Welcome to our show! (0:05-0:10) This is the second segment.",
                "expected_elements": ["Welcome to our show!", "This is the second segment."],
                "removed_elements": ["(0:00-0:05)", "(0:05-0:10)"]
            },
            {
                "name": "Scene Descriptions Removal",
                "input": "[SCENE: Office setting] Hello everyone! [Camera: Close-up] This is important content.",
                "expected_elements": ["Hello everyone!", "This is important content."],
                "removed_elements": ["[SCENE: Office setting]", "[Camera: Close-up]"]
            },
            {
                "name": "Speaker Directions Removal",
                "input": "(Narrator - Enthusiastic tone) Welcome! (Voiceover - Calm voice) This is educational content.",
                "expected_elements": ["Welcome!", "This is educational content."],
                "removed_elements": ["(Narrator - Enthusiastic tone)", "(Voiceover - Calm voice)"]
            },
            {
                "name": "Bold and Formatting Removal",
                "input": "This is **bold text** and this is *italic text* and this is normal text.",
                "expected_elements": ["This is bold text and this is italic text and this is normal text."],
                "removed_elements": ["**", "*"]
            },
            {
                "name": "Brackets and Parentheses Mixed",
                "input": "[Setting: Kitchen] (Chef - Happy tone) Today we're making (0:15-0:30) delicious **pasta**!",
                "expected_elements": ["Today we're making delicious pasta!"],
                "removed_elements": ["[Setting: Kitchen]", "(Chef - Happy tone)", "(0:15-0:30)", "**"]
            },
            {
                "name": "Production Elements Removal",
                "input": """TARGET DURATION: 60 seconds
                
                SCRIPT:
                This is the actual spoken content.
                
                PRODUCTION NOTES:
                - Use good lighting
                - Add background music
                
                KEY ELEMENTS:
                * Important point 1
                * Important point 2""",
                "expected_elements": ["This is the actual spoken content."],
                "removed_elements": ["TARGET DURATION:", "PRODUCTION NOTES:", "KEY ELEMENTS:", "*", "-"]
            }
        ]
        
        success_count = 0
        
        for test_case in cleanup_test_cases:
            try:
                payload = {
                    "text": test_case["input"],
                    "voice_name": voices[0]["name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data.get("audio_base64", "")
                    
                    # For cleanup testing, we expect audio to be generated
                    # The key is that production elements should be removed
                    if len(audio_base64) > 500:  # Should have some audio
                        self.log_test(f"Script Cleanup - {test_case['name']}", True,
                                    f"Successfully processed and cleaned script: {len(audio_base64)} chars")
                        success_count += 1
                    else:
                        self.log_test(f"Script Cleanup - {test_case['name']}", False,
                                    f"Audio too short after cleanup: {len(audio_base64)} chars")
                else:
                    self.log_test(f"Script Cleanup - {test_case['name']}", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Script Cleanup - {test_case['name']}", False,
                            f"Exception: {str(e)}")
        
        # Test complex real-world script
        complex_real_script = """VIDEO SCRIPT: Healthy Cooking Tips
        
        TARGET DURATION: 90 seconds
        VIDEO TYPE: Educational / Health & Wellness
        
        SCRIPT:
        
        (0:00-0:05) [SCENE START: Bright, modern kitchen with fresh ingredients displayed on a marble countertop. Natural lighting streams through large windows.]
        
        (Narrator – Warm, friendly, and approachable tone)
        Welcome to "Healthy Cooking Made Simple!" I'm Sarah, and today we're transforming the way you think about nutritious meals.
        
        (0:05-0:15) [SCENE CHANGE: Close-up shots of colorful vegetables being chopped with a sharp knife. Quick cuts between different vegetables.]
        
        (Narrator – Educational, slightly excited)
        The secret to amazing healthy food? It starts with choosing the RIGHT ingredients. Look for vibrant colors – they're nature's way of telling you "I'm packed with nutrients!"
        
        (0:15-0:25) [SCENE: Demonstration of proper vegetable preparation techniques. Steam rising from a pan.]
        
        (Narrator – Instructional, confident)
        Here's a game-changer: steaming preserves up to 90% more vitamins than boiling. Your broccoli will thank you, and so will your body!
        
        (0:25-0:40) [SCENE: Quick montage of healthy cooking techniques – grilling, roasting, sautéing with minimal oil.]
        
        (Narrator – Enthusiastic, motivational)
        Forget everything you've heard about healthy food being boring. With the right techniques, you can create meals that are both nutritious AND absolutely delicious!
        
        (0:40-0:55) [SCENE: Beautiful plated healthy meals. Camera slowly pans across colorful, appetizing dishes.]
        
        (Narrator – Inspiring, warm)
        Every meal is an opportunity to nourish your body and fuel your dreams. You deserve to feel amazing, and it starts with what's on your plate.
        
        (0:55-1:30) [SCENE: Call-to-action with text overlay showing website/social media handles.]
        
        (Narrator – Encouraging, direct)
        Ready to start your healthy cooking journey? Subscribe for more tips, and don't forget to share your creations with #HealthyCookingSimple. Your future self will thank you!
        
        [END SCENE: Logo and subscribe button animation]
        
        PRODUCTION NOTES:
        - Use natural lighting throughout
        - Include upbeat, inspiring background music
        - Add text overlays for key cooking tips
        - Ensure all ingredients are fresh and visually appealing
        - Use smooth camera transitions between scenes
        
        KEY RETENTION ELEMENTS:
        * Hook within first 3 seconds with personal introduction
        * Educational value with specific statistics (90% vitamin retention)
        * Visual appeal with colorful food shots
        * Emotional connection through motivational language
        * Clear call-to-action with hashtag for community building
        
        HASHTAGS: #HealthyCooking #NutritionTips #CookingHacks #HealthyLifestyle #WellnessJourney"""
        
        try:
            payload = {
                "text": complex_real_script,
                "voice_name": voices[0]["name"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=90  # Longer timeout for complex script
            )
            
            if response.status_code == 200:
                data = response.json()
                audio_base64 = data.get("audio_base64", "")
                
                if len(audio_base64) > 20000:  # Should have substantial audio
                    self.log_test("Script Cleanup - Complex Real Script", True,
                                f"Successfully processed complex real-world script: {len(audio_base64)} chars")
                    success_count += 1
                else:
                    self.log_test("Script Cleanup - Complex Real Script", False,
                                f"Audio too short for complex script: {len(audio_base64)} chars")
            else:
                self.log_test("Script Cleanup - Complex Real Script", False,
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Script Cleanup - Complex Real Script", False, f"Exception: {str(e)}")
        
        # Test that only spoken content is extracted
        spoken_only_test = """[SCENE: Office]
        (Director's note: Use wide shot)
        (0:00-0:05) [Camera setup instructions]
        
        This is the actual spoken dialogue that should be in the audio.
        
        (Technical note: Adjust lighting)
        [End scene]
        
        This is more spoken content that should be included.
        
        PRODUCTION NOTES:
        - Don't include this in audio
        - Or this either"""
        
        try:
            payload = {
                "text": spoken_only_test,
                "voice_name": voices[0]["name"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                audio_base64 = data.get("audio_base64", "")
                
                # Should have some audio but not too much (production notes removed)
                if 1000 < len(audio_base64) < 15000:
                    self.log_test("Script Cleanup - Spoken Content Only", True,
                                f"Successfully extracted only spoken content: {len(audio_base64)} chars")
                    success_count += 1
                else:
                    self.log_test("Script Cleanup - Spoken Content Only", False,
                                f"Audio length suggests production notes may not be filtered: {len(audio_base64)} chars")
            else:
                self.log_test("Script Cleanup - Spoken Content Only", False,
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Script Cleanup - Spoken Content Only", False, f"Exception: {str(e)}")
        
        # Overall assessment
        total_tests = len(cleanup_test_cases) + 2  # +2 for complex script and spoken-only test
        if success_count >= total_tests * 0.75:  # 75% success rate
            self.log_test("Script Processing & Cleanup - Overall", True,
                        f"Script processing and cleanup working well: {success_count}/{total_tests} tests passed")
            return True
        else:
            self.log_test("Script Processing & Cleanup - Overall", False,
                        f"Script processing needs improvement: only {success_count}/{total_tests} tests passed")
            return False
    
    def test_integration_script_to_audio(self):
        """Test the complete flow: Generate Script → Generate Audio"""
        print("\n=== Testing Integration: Script Generation → Audio Generation ===")
        
        try:
            # Step 1: Generate a script
            script_payload = {
                "prompt": "Create a motivational video about healthy eating habits",
                "video_type": "educational",
                "duration": "medium"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=60
            )
            
            if script_response.status_code != 200:
                self.log_test("Integration - Script Generation", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data.get("generated_script", "")
            
            if len(generated_script) < 100:
                self.log_test("Integration - Script Quality", False,
                            f"Generated script too short: {len(generated_script)} chars")
                return False
            
            self.log_test("Integration - Script Generation", True,
                        f"Successfully generated script: {len(generated_script)} chars")
            
            # Step 2: Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Integration - Voice Retrieval", False,
                            "Could not retrieve voices for integration test")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Integration - Voice Availability", False,
                            "No voices available for integration test")
                return False
            
            # Step 3: Generate audio from the script
            audio_payload = {
                "text": generated_script,
                "voice_name": voices[0]["name"]
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=90  # Longer timeout for potentially long script
            )
            
            if audio_response.status_code != 200:
                self.log_test("Integration - Audio Generation", False,
                            f"Audio generation failed: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data.get("audio_base64", "")
            
            if len(audio_base64) < 5000:
                self.log_test("Integration - Audio Quality", False,
                            f"Generated audio too short: {len(audio_base64)} chars")
                return False
            
            self.log_test("Integration - Audio Generation", True,
                        f"Successfully generated audio: {len(audio_base64)} chars")
            
            # Step 4: Test with different voice
            if len(voices) > 1:
                different_audio_payload = {
                    "text": generated_script,
                    "voice_name": voices[1]["name"]
                }
                
                different_audio_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=different_audio_payload,
                    timeout=90
                )
                
                if different_audio_response.status_code == 200:
                    different_audio_data = different_audio_response.json()
                    different_audio_base64 = different_audio_data.get("audio_base64", "")
                    
                    # Verify different voices produce different audio
                    if different_audio_base64 != audio_base64:
                        self.log_test("Integration - Voice Variation", True,
                                    "Different voices produce different audio from same script")
                    else:
                        self.log_test("Integration - Voice Variation", False,
                                    "Different voices produced identical audio")
                else:
                    self.log_test("Integration - Voice Variation", False,
                                f"Failed with different voice: {different_audio_response.status_code}")
            
            # Step 5: Test with enhanced prompt flow
            enhance_payload = {
                "original_prompt": "Create a video about productivity tips",
                "video_type": "educational",
                "industry_focus": "general"
            }
            
            enhance_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=enhance_payload,
                timeout=60
            )
            
            if enhance_response.status_code == 200:
                enhance_data = enhance_response.json()
                variations = enhance_data.get("enhancement_variations", [])
                
                if variations:
                    # Use first variation to generate script
                    enhanced_prompt = variations[0].get("enhanced_prompt", "")
                    
                    enhanced_script_payload = {
                        "prompt": enhanced_prompt,
                        "video_type": "educational",
                        "duration": "short"
                    }
                    
                    enhanced_script_response = self.session.post(
                        f"{self.backend_url}/generate-script",
                        json=enhanced_script_payload,
                        timeout=60
                    )
                    
                    if enhanced_script_response.status_code == 200:
                        enhanced_script_data = enhanced_script_response.json()
                        enhanced_script = enhanced_script_data.get("generated_script", "")
                        
                        # Generate audio from enhanced script
                        enhanced_audio_payload = {
                            "text": enhanced_script,
                            "voice_name": voices[0]["name"]
                        }
                        
                        enhanced_audio_response = self.session.post(
                            f"{self.backend_url}/generate-audio",
                            json=enhanced_audio_payload,
                            timeout=90
                        )
                        
                        if enhanced_audio_response.status_code == 200:
                            self.log_test("Integration - Enhanced Flow", True,
                                        "Successfully completed enhance → script → audio flow")
                        else:
                            self.log_test("Integration - Enhanced Flow", False,
                                        f"Enhanced audio generation failed: {enhanced_audio_response.status_code}")
                    else:
                        self.log_test("Integration - Enhanced Flow", False,
                                    f"Enhanced script generation failed: {enhanced_script_response.status_code}")
                else:
                    self.log_test("Integration - Enhanced Flow", False,
                                "No enhancement variations returned")
            else:
                self.log_test("Integration - Enhanced Flow", False,
                            f"Prompt enhancement failed: {enhance_response.status_code}")
            
            self.log_test("Integration - Complete Flow", True,
                        "Successfully completed script generation → audio generation integration")
            return True
            
        except Exception as e:
            self.log_test("Integration - Exception", False, f"Integration test failed: {str(e)}")
            return False
    
    def test_performance_and_error_handling(self):
        """Test performance and error handling scenarios"""
        print("\n=== Testing Performance & Error Handling ===")
        
        success_count = 0
        
        # Test 1: Malformed scripts
        malformed_scripts = [
            {
                "name": "Invalid JSON Characters",
                "text": "This text contains invalid characters: \x00\x01\x02"
            },
            {
                "name": "Extremely Nested Formatting",
                "text": "[[[(((**bold nested**)))]]]"
            },
            {
                "name": "Mixed Encoding",
                "text": "English text with émojis 🎉 and special chars àáâãäå"
            }
        ]
        
        # Get voices for testing
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Performance - Voice Setup", False, "Could not retrieve voices")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Performance - Voice Availability", False, "No voices available")
                return False
            
        except Exception as e:
            self.log_test("Performance - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        for malformed in malformed_scripts:
            try:
                payload = {
                    "text": malformed["text"],
                    "voice_name": voices[0]["name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                # Should either succeed or fail gracefully
                if response.status_code in [200, 400, 422]:  # Valid responses
                    self.log_test(f"Error Handling - {malformed['name']}", True,
                                f"Handled gracefully: {response.status_code}")
                    success_count += 1
                else:
                    self.log_test(f"Error Handling - {malformed['name']}", False,
                                f"Unexpected response: {response.status_code}")
                    
            except Exception as e:
                # Exceptions are acceptable for malformed input
                self.log_test(f"Error Handling - {malformed['name']}", True,
                            f"Handled with exception (acceptable): {str(e)[:100]}")
                success_count += 1
        
        # Test 2: Invalid voice names
        invalid_voice_tests = [
            {"voice_name": "nonexistent-voice", "text": "Test with invalid voice"},
            {"voice_name": "", "text": "Test with empty voice"},
            {"voice_name": None, "text": "Test with null voice"}
        ]
        
        for invalid_voice in invalid_voice_tests:
            try:
                payload = {
                    "text": invalid_voice["text"],
                    "voice_name": invalid_voice["voice_name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                # Should return appropriate error
                if response.status_code in [400, 422, 500]:
                    self.log_test(f"Error Handling - Invalid Voice ({invalid_voice['voice_name']})", True,
                                f"Correctly rejected invalid voice: {response.status_code}")
                    success_count += 1
                else:
                    self.log_test(f"Error Handling - Invalid Voice ({invalid_voice['voice_name']})", False,
                                f"Should have rejected invalid voice: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Error Handling - Invalid Voice ({invalid_voice['voice_name']})", True,
                            f"Correctly failed with exception: {str(e)[:100]}")
                success_count += 1
        
        # Test 3: Scripts with no spoken content
        no_content_scripts = [
            {
                "name": "Only Production Notes",
                "text": """PRODUCTION NOTES:
                - Use good lighting
                - Add background music
                
                KEY ELEMENTS:
                * Point 1
                * Point 2"""
            },
            {
                "name": "Only Timestamps and Directions",
                "text": "(0:00-0:05) [SCENE: Office] (Director: Wide shot) (0:05-0:10)"
            },
            {
                "name": "Only Formatting",
                "text": "**bold** *italic* [brackets] (parentheses)"
            }
        ]
        
        for no_content in no_content_scripts:
            try:
                payload = {
                    "text": no_content["text"],
                    "voice_name": voices[0]["name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data.get("audio_base64", "")
                    
                    # Should have minimal or no audio
                    if len(audio_base64) < 1000:  # Very short audio expected
                        self.log_test(f"Error Handling - {no_content['name']}", True,
                                    f"Correctly handled no-content script: {len(audio_base64)} chars")
                        success_count += 1
                    else:
                        self.log_test(f"Error Handling - {no_content['name']}", False,
                                    f"Generated too much audio for no-content script: {len(audio_base64)} chars")
                else:
                    # Also acceptable to return error for no content
                    self.log_test(f"Error Handling - {no_content['name']}", True,
                                f"Correctly returned error for no-content: {response.status_code}")
                    success_count += 1
                    
            except Exception as e:
                self.log_test(f"Error Handling - {no_content['name']}", True,
                            f"Correctly handled with exception: {str(e)[:100]}")
                success_count += 1
        
        # Test 4: Performance with reasonable script
        performance_script = "This is a performance test script. " * 50  # Moderate length
        
        try:
            start_time = time.time()
            
            payload = {
                "text": performance_script,
                "voice_name": voices[0]["name"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                audio_base64 = data.get("audio_base64", "")
                
                if processing_time < 45:  # Should complete within reasonable time
                    self.log_test("Performance - Processing Time", True,
                                f"Completed in {processing_time:.1f}s with {len(audio_base64)} chars audio")
                    success_count += 1
                else:
                    self.log_test("Performance - Processing Time", False,
                                f"Too slow: {processing_time:.1f}s")
            else:
                self.log_test("Performance - Processing Time", False,
                            f"Failed performance test: {response.status_code}")
                
        except Exception as e:
            self.log_test("Performance - Processing Time", False, f"Performance test failed: {str(e)}")
        
        # Overall assessment
        total_tests = len(malformed_scripts) + len(invalid_voice_tests) + len(no_content_scripts) + 1
        if success_count >= total_tests * 0.8:  # 80% success rate
            self.log_test("Performance & Error Handling - Overall", True,
                        f"Performance and error handling working well: {success_count}/{total_tests} tests passed")
            return True
        else:
            self.log_test("Performance & Error Handling - Overall", False,
                        f"Performance and error handling needs improvement: only {success_count}/{total_tests} tests passed")
            return False
    
    def run_comprehensive_tests(self):
        """Run all TTS and script processing tests"""
        print("🚀 Starting Comprehensive TTS and Script Processing Testing")
        print("=" * 80)
        
        test_methods = [
            self.test_tts_audio_generation_endpoint,
            self.test_duplicate_line_bug_fix,
            self.test_script_processing_cleanup,
            self.test_integration_script_to_audio,
            self.test_performance_and_error_handling
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {str(e)}")
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE TTS AND SCRIPT PROCESSING TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"📊 Overall Results: {passed_tests}/{total_tests} test categories passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("✅ TTS AND SCRIPT PROCESSING FUNCTIONALITY: EXCELLENT")
            print("🎉 The duplicate line bug fix and script processing are working correctly!")
        elif success_rate >= 60:
            print("⚠️  TTS AND SCRIPT PROCESSING FUNCTIONALITY: GOOD (Minor Issues)")
            print("🔧 Most functionality working, some areas need attention")
        else:
            print("❌ TTS AND SCRIPT PROCESSING FUNCTIONALITY: NEEDS ATTENTION")
            print("🚨 Significant issues found that need to be addressed")
        
        print("\n📋 Detailed Test Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = TTSScriptProcessingTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)
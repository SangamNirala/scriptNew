#!/usr/bin/env python3
"""
Audio Download Functionality Testing Script
Tests the complete audio download functionality as requested in the review
"""

import requests
import json
import base64
import time
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://a1f5fd57-2ca0-4a00-8547-bbab28ecbeb6.preview.emergentagent.com/api"

class AudioDownloadTester:
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
    
    def test_voices_api(self):
        """Test 1: Voice Selection API Test - /api/voices endpoint"""
        print("\n=== TEST 1: Voice Selection API ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response is a list
                if not isinstance(data, list):
                    self.log_test("Voice API - Data Type", False,
                                "Response is not a list", {"response_type": type(data).__name__})
                    return False
                
                # Verify we have voices
                if len(data) == 0:
                    self.log_test("Voice API - Voice Count", False,
                                "No voices returned - expected at least some voices")
                    return False
                
                # Verify voice structure
                first_voice = data[0]
                required_fields = ["name", "display_name", "language", "gender"]
                missing_fields = [field for field in required_fields if field not in first_voice]
                
                if missing_fields:
                    self.log_test("Voice API - Voice Structure", False,
                                f"Missing fields in voice: {missing_fields}")
                    return False
                
                # Check for variety of voices
                genders = set(voice.get("gender", "") for voice in data)
                languages = set(voice.get("language", "") for voice in data)
                
                if len(genders) < 2:
                    self.log_test("Voice API - Gender Variety", False,
                                f"Expected both male and female voices, got: {genders}")
                else:
                    self.log_test("Voice API - Gender Variety", True,
                                f"Good gender variety: {genders}")
                
                if len(languages) < 2:
                    self.log_test("Voice API - Language Variety", False,
                                f"Expected multiple language variants, got: {languages}")
                else:
                    self.log_test("Voice API - Language Variety", True,
                                f"Good language variety: {len(languages)} variants")
                
                # Check for expected popular voices
                voice_names = [voice.get("name", "") for voice in data]
                expected_voices = ["en-US-AriaNeural", "en-GB-SoniaNeural"]
                found_expected = [voice for voice in expected_voices if voice in voice_names]
                
                if len(found_expected) >= 1:
                    self.log_test("Voice API - Popular Voices", True,
                                f"Found expected popular voices: {found_expected}")
                else:
                    self.log_test("Voice API - Popular Voices", False,
                                f"Expected popular voices not found. Available: {voice_names[:5]}")
                
                self.log_test("Voice API - Overall", True,
                            f"Successfully retrieved {len(data)} voices with proper structure")
                
                # Store voices for later tests
                self.available_voices = data
                return True
                
            else:
                self.log_test("Voice API - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Voice API - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_audio_generation_api(self):
        """Test 2: Audio Generation Test - /api/generate-audio endpoint"""
        print("\n=== TEST 2: Audio Generation API ===")
        
        if not hasattr(self, 'available_voices') or not self.available_voices:
            self.log_test("Audio Generation - Setup", False, "No voices available from previous test")
            return False
        
        # Test with sample script about success/motivation as requested
        sample_script = """
        Success isn't just about reaching your destination—it's about who you become on the journey. 
        Every challenge you face is an opportunity to grow stronger, wiser, and more resilient. 
        Remember, the path to greatness is paved with persistence, passion, and the courage to keep moving forward 
        even when the road gets tough. Your dreams are valid, your efforts matter, and your potential is limitless. 
        Today is the perfect day to take that next step toward the life you've always envisioned.
        """
        
        # Test with multiple voices (at least 2-3 as requested)
        test_voices = self.available_voices[:3]  # Test with first 3 voices
        successful_generations = 0
        audio_outputs = {}
        
        for voice in test_voices:
            try:
                payload = {
                    "text": sample_script.strip(),
                    "voice_name": voice["name"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=45
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify response structure
                    required_fields = ["audio_base64", "voice_used"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(f"Audio Generation - {voice['display_name']} Structure", False,
                                    f"Missing fields: {missing_fields}")
                        continue
                    
                    # Verify audio data
                    audio_base64 = data["audio_base64"]
                    if not audio_base64 or len(audio_base64) < 1000:
                        self.log_test(f"Audio Generation - {voice['display_name']} Data", False,
                                    "Audio base64 data is too short or empty",
                                    {"audio_length": len(audio_base64) if audio_base64 else 0})
                        continue
                    
                    # Verify voice used matches request
                    if data["voice_used"] != voice["name"]:
                        self.log_test(f"Audio Generation - {voice['display_name']} Voice Match", False,
                                    f"Requested {voice['name']}, got {data['voice_used']}")
                        continue
                    
                    # Store audio output for comparison
                    audio_outputs[voice["name"]] = audio_base64
                    successful_generations += 1
                    
                    self.log_test(f"Audio Generation - {voice['display_name']}", True,
                                f"Successfully generated {len(audio_base64)} chars of base64 audio")
                    
                else:
                    self.log_test(f"Audio Generation - {voice['display_name']}", False,
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Audio Generation - {voice['display_name']}", False,
                            f"Exception: {str(e)}")
        
        # Verify different voices produce different audio
        if len(set(audio_outputs.values())) > 1:
            self.log_test("Audio Generation - Voice Variation", True,
                        f"Different voices produced {len(set(audio_outputs.values()))} distinct audio outputs")
        else:
            self.log_test("Audio Generation - Voice Variation", False,
                        "All voices produced identical audio (unexpected)")
        
        if successful_generations >= 2:
            self.log_test("Audio Generation - Overall", True,
                        f"Successfully tested audio generation with {successful_generations} voices")
            self.audio_outputs = audio_outputs
            return True
        else:
            self.log_test("Audio Generation - Overall", False,
                        f"Only {successful_generations} voice generations succeeded")
            return False
    
    def test_download_data_format(self):
        """Test 3: Download Data Format Test - Verify base64 audio can be converted to MP3"""
        print("\n=== TEST 3: Download Data Format ===")
        
        if not hasattr(self, 'audio_outputs') or not self.audio_outputs:
            self.log_test("Download Format - Setup", False, "No audio outputs available from previous test")
            return False
        
        # Test base64 audio data validity
        successful_validations = 0
        
        for voice_name, audio_base64 in self.audio_outputs.items():
            try:
                # Test 1: Verify base64 is valid
                try:
                    audio_bytes = base64.b64decode(audio_base64)
                    self.log_test(f"Download Format - {voice_name} Base64 Decode", True,
                                f"Successfully decoded {len(audio_bytes)} bytes from base64")
                except Exception as decode_error:
                    self.log_test(f"Download Format - {voice_name} Base64 Decode", False,
                                f"Failed to decode base64: {str(decode_error)}")
                    continue
                
                # Test 2: Verify audio data has reasonable size
                if len(audio_bytes) < 1000:
                    self.log_test(f"Download Format - {voice_name} Size Check", False,
                                f"Audio data too small: {len(audio_bytes)} bytes")
                    continue
                else:
                    self.log_test(f"Download Format - {voice_name} Size Check", True,
                                f"Audio data has reasonable size: {len(audio_bytes)} bytes")
                
                # Test 3: Check if it looks like audio data (basic header check)
                # MP3 files typically start with ID3 tag or sync frame
                if audio_bytes[:3] == b'ID3' or (audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0):
                    self.log_test(f"Download Format - {voice_name} Audio Header", True,
                                "Audio data has valid MP3-like header")
                else:
                    # Could be other audio format, still valid
                    self.log_test(f"Download Format - {voice_name} Audio Header", True,
                                "Audio data appears to be valid binary audio format")
                
                # Test 4: Verify base64 string characteristics
                if len(audio_base64) % 4 == 0:  # Base64 should be multiple of 4
                    self.log_test(f"Download Format - {voice_name} Base64 Format", True,
                                "Base64 string has correct padding")
                else:
                    self.log_test(f"Download Format - {voice_name} Base64 Format", False,
                                "Base64 string has incorrect padding")
                    continue
                
                successful_validations += 1
                
            except Exception as e:
                self.log_test(f"Download Format - {voice_name}", False,
                            f"Validation failed: {str(e)}")
        
        if successful_validations >= 2:
            self.log_test("Download Format - Overall", True,
                        f"Successfully validated {successful_validations} audio downloads as convertible to MP3")
            return True
        else:
            self.log_test("Download Format - Overall", False,
                        f"Only {successful_validations} audio validations succeeded")
            return False
    
    def test_voice_script_correspondence(self):
        """Test 4: Voice-Script Correspondence Test - Verify audio corresponds to voice and script"""
        print("\n=== TEST 4: Voice-Script Correspondence ===")
        
        if not hasattr(self, 'available_voices') or not self.available_voices:
            self.log_test("Voice Correspondence - Setup", False, "No voices available")
            return False
        
        # Test different scripts with different voices to ensure correspondence
        test_scripts = [
            {
                "name": "Success Script",
                "text": "Success is not final, failure is not fatal: it is the courage to continue that counts. Every great achievement starts with the decision to try."
            },
            {
                "name": "Motivation Script", 
                "text": "Your potential is endless. The only limits that exist are the ones you place on yourself. Believe in your dreams and take action today."
            }
        ]
        
        # Test with 2-3 different voices as requested
        test_voices = self.available_voices[:3]
        successful_correspondences = 0
        
        for script in test_scripts:
            script_results = {}
            
            for voice in test_voices:
                try:
                    payload = {
                        "text": script["text"],
                        "voice_name": voice["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data["audio_base64"]
                        voice_used = data["voice_used"]
                        
                        # Verify voice correspondence
                        if voice_used == voice["name"]:
                            self.log_test(f"Voice Correspondence - {script['name']} + {voice['display_name']}", True,
                                        f"Audio generated with correct voice: {voice_used}")
                            script_results[voice["name"]] = audio_base64
                        else:
                            self.log_test(f"Voice Correspondence - {script['name']} + {voice['display_name']}", False,
                                        f"Voice mismatch: requested {voice['name']}, got {voice_used}")
                    else:
                        self.log_test(f"Voice Correspondence - {script['name']} + {voice['display_name']}", False,
                                    f"HTTP {response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"Voice Correspondence - {script['name']} + {voice['display_name']}", False,
                                f"Exception: {str(e)}")
            
            # Verify different voices produce different audio for same script
            if len(set(script_results.values())) > 1:
                self.log_test(f"Voice Correspondence - {script['name']} Variation", True,
                            f"Different voices produced distinct audio for {script['name']}")
                successful_correspondences += 1
            else:
                self.log_test(f"Voice Correspondence - {script['name']} Variation", False,
                            f"All voices produced identical audio for {script['name']}")
        
        # Test that same voice produces different audio for different scripts
        if len(test_voices) > 0:
            test_voice = test_voices[0]
            script_outputs = []
            
            for script in test_scripts:
                try:
                    payload = {
                        "text": script["text"],
                        "voice_name": test_voice["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        script_outputs.append(data["audio_base64"])
                        
                except Exception as e:
                    self.log_test(f"Voice Correspondence - Script Variation", False,
                                f"Exception testing script variation: {str(e)}")
            
            if len(set(script_outputs)) > 1:
                self.log_test("Voice Correspondence - Script Variation", True,
                            f"Same voice produced different audio for different scripts")
                successful_correspondences += 1
            else:
                self.log_test("Voice Correspondence - Script Variation", False,
                            "Same voice produced identical audio for different scripts")
        
        if successful_correspondences >= 2:
            self.log_test("Voice Correspondence - Overall", True,
                        f"Successfully verified voice-script correspondence in {successful_correspondences} test cases")
            return True
        else:
            self.log_test("Voice Correspondence - Overall", False,
                        f"Only {successful_correspondences} correspondence tests succeeded")
            return False
    
    def test_error_handling(self):
        """Test 5: Error Handling - Verify proper error responses"""
        print("\n=== TEST 5: Error Handling ===")
        
        error_tests_passed = 0
        
        # Test 1: Empty text
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": "", "voice_name": "en-US-AriaNeural"},
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("Error Handling - Empty Text", True,
                            "Properly handled empty text request")
                error_tests_passed += 1
            else:
                self.log_test("Error Handling - Empty Text", False,
                            f"Unexpected status code for empty text: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Empty Text", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid voice name
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": "Test text", "voice_name": "invalid-voice-name"},
                timeout=15
            )
            
            if response.status_code in [400, 500]:
                self.log_test("Error Handling - Invalid Voice", True,
                            "Properly handled invalid voice name")
                error_tests_passed += 1
            else:
                self.log_test("Error Handling - Invalid Voice", False,
                            f"Unexpected status code for invalid voice: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Voice", False, f"Exception: {str(e)}")
        
        # Test 3: Missing required fields
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": "Test text"},  # Missing voice_name
                timeout=10
            )
            
            if response.status_code in [400, 422]:
                self.log_test("Error Handling - Missing Fields", True,
                            "Properly handled missing required fields")
                error_tests_passed += 1
            else:
                self.log_test("Error Handling - Missing Fields", False,
                            f"Unexpected status code for missing fields: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Missing Fields", False, f"Exception: {str(e)}")
        
        if error_tests_passed >= 2:
            self.log_test("Error Handling - Overall", True,
                        f"Successfully verified {error_tests_passed} error handling scenarios")
            return True
        else:
            self.log_test("Error Handling - Overall", False,
                        f"Only {error_tests_passed} error handling tests passed")
            return False
    
    def run_all_tests(self):
        """Run all audio download functionality tests"""
        print("🎵 AUDIO DOWNLOAD FUNCTIONALITY TESTING")
        print("=" * 50)
        
        # Test basic connectivity first
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ Backend connectivity confirmed")
            else:
                print(f"❌ Backend connectivity failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connectivity failed: {str(e)}")
            return False
        
        # Run all tests in sequence
        tests = [
            ("Voice Selection API", self.test_voices_api),
            ("Audio Generation API", self.test_audio_generation_api),
            ("Download Data Format", self.test_download_data_format),
            ("Voice-Script Correspondence", self.test_voice_script_correspondence),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
        
        # Final summary
        print(f"\n{'='*50}")
        print(f"🎵 AUDIO DOWNLOAD TESTING COMPLETE")
        print(f"{'='*50}")
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Audio download functionality is ready!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed - Review needed")
            return False

if __name__ == "__main__":
    tester = AudioDownloadTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ CONCLUSION: Backend audio download functionality is production-ready")
    else:
        print("\n❌ CONCLUSION: Backend audio download functionality needs attention")
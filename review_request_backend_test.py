#!/usr/bin/env python3
"""
Review Request Backend Testing Script
Tests specific backend endpoints mentioned in the review request:
1) GET /api/voices returns 8+ curated voices with fields: name, display_name, language, gender
2) POST /api/generate-audio with payload { text, voice_name } returns { audio_base64 } for arbitrary text
3) PUT /api/scripts/{script_id} with { script_id, generated_script } updates and returns updated record
4) Ensure CORS headers intact
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://f5f1bcd3-1e7e-4f94-9ffa-0d0d9163f7bc.preview.emergentagent.com/api"

class ReviewRequestTester:
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
    
    def test_voices_endpoint_review_requirements(self):
        """Test GET /api/voices returns 8+ curated voices with required fields"""
        print("\n=== Testing GET /api/voices (Review Request Requirement 1) ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check CORS headers
                cors_headers = {
                    'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                    'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                    'access-control-allow-headers': response.headers.get('access-control-allow-headers')
                }
                
                if any(cors_headers.values()):
                    self.log_test("Voices Endpoint - CORS Headers", True,
                                f"CORS headers present: {cors_headers}")
                else:
                    self.log_test("Voices Endpoint - CORS Headers", False,
                                "No CORS headers detected in response")
                
                # Verify response is a list
                if not isinstance(data, list):
                    self.log_test("Voices Endpoint - Data Type", False,
                                f"Response is not a list, got: {type(data).__name__}")
                    return False
                
                # Check for 8+ voices
                if len(data) < 8:
                    self.log_test("Voices Endpoint - Voice Count", False,
                                f"Expected 8+ voices, got {len(data)}")
                    return False
                
                self.log_test("Voices Endpoint - Voice Count", True,
                            f"Successfully returned {len(data)} voices (meets 8+ requirement)")
                
                # Verify required fields for each voice
                required_fields = ["name", "display_name", "language", "gender"]
                all_voices_valid = True
                
                for i, voice in enumerate(data):
                    missing_fields = [field for field in required_fields if field not in voice]
                    if missing_fields:
                        self.log_test(f"Voices Endpoint - Voice {i+1} Structure", False,
                                    f"Missing required fields: {missing_fields}")
                        all_voices_valid = False
                    else:
                        # Verify field values are not empty
                        empty_fields = [field for field in required_fields if not voice.get(field)]
                        if empty_fields:
                            self.log_test(f"Voices Endpoint - Voice {i+1} Values", False,
                                        f"Empty field values: {empty_fields}")
                            all_voices_valid = False
                
                if all_voices_valid:
                    self.log_test("Voices Endpoint - Field Structure", True,
                                "All voices have required fields: name, display_name, language, gender")
                
                # Check for variety in gender and language
                genders = set(voice.get("gender", "") for voice in data)
                languages = set(voice.get("language", "") for voice in data)
                
                if len(genders) >= 2:
                    self.log_test("Voices Endpoint - Gender Variety", True,
                                f"Good gender variety: {genders}")
                else:
                    self.log_test("Voices Endpoint - Gender Variety", False,
                                f"Limited gender variety: {genders}")
                
                if len(languages) >= 2:
                    self.log_test("Voices Endpoint - Language Variety", True,
                                f"Good language variety: {len(languages)} variants")
                else:
                    self.log_test("Voices Endpoint - Language Variety", False,
                                f"Limited language variety: {languages}")
                
                # Display sample voices for verification
                sample_voices = data[:3]
                self.log_test("Voices Endpoint - Sample Data", True,
                            f"Sample voices: {[{'name': v['name'], 'display_name': v['display_name'], 'language': v['language'], 'gender': v['gender']} for v in sample_voices]}")
                
                return all_voices_valid and len(data) >= 8
                
            else:
                self.log_test("Voices Endpoint - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Voices Endpoint - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_generate_audio_endpoint_review_requirements(self):
        """Test POST /api/generate-audio with payload { text, voice_name } returns { audio_base64 }"""
        print("\n=== Testing POST /api/generate-audio (Review Request Requirement 2) ===")
        
        # First get available voices
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Generate Audio - Voice Retrieval", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Generate Audio - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            test_voice = voices[0]["name"]  # Use first available voice
            
        except Exception as e:
            self.log_test("Generate Audio - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test Case 1: Short text 'Hello world' as specified in review request
        test_text = "Hello world"
        payload = {
            "text": test_text,
            "voice_name": test_voice
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            # Check CORS headers
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            if any(cors_headers.values()):
                self.log_test("Generate Audio - CORS Headers", True,
                            f"CORS headers present: {cors_headers}")
            else:
                self.log_test("Generate Audio - CORS Headers", False,
                            "No CORS headers detected in response")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure - must contain audio_base64
                if "audio_base64" not in data:
                    self.log_test("Generate Audio - Response Structure", False,
                                "Response missing required 'audio_base64' field")
                    return False
                
                # Verify audio data is present and substantial
                audio_base64 = data["audio_base64"]
                if not audio_base64 or len(audio_base64) < 100:
                    self.log_test("Generate Audio - Audio Data", False,
                                f"Audio base64 data too short or empty: {len(audio_base64) if audio_base64 else 0} chars")
                    return False
                
                self.log_test("Generate Audio - Hello World Test", True,
                            f"Successfully generated {len(audio_base64)} chars of base64 audio for 'Hello world'")
                
                # Test Case 2: Arbitrary text (dialogue-only text)
                dialogue_text = "Hi there! How are you doing today? I hope you're having a wonderful day."
                dialogue_payload = {
                    "text": dialogue_text,
                    "voice_name": test_voice
                }
                
                dialogue_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=dialogue_payload,
                    timeout=30
                )
                
                if dialogue_response.status_code == 200:
                    dialogue_data = dialogue_response.json()
                    dialogue_audio = dialogue_data.get("audio_base64", "")
                    
                    if len(dialogue_audio) > len(audio_base64):  # Should be longer for longer text
                        self.log_test("Generate Audio - Dialogue Text", True,
                                    f"Successfully generated {len(dialogue_audio)} chars of audio for dialogue text")
                    else:
                        self.log_test("Generate Audio - Dialogue Text", False,
                                    f"Dialogue audio not proportionally longer: {len(dialogue_audio)} vs {len(audio_base64)}")
                else:
                    self.log_test("Generate Audio - Dialogue Text", False,
                                f"Failed with dialogue text: HTTP {dialogue_response.status_code}")
                
                # Test Case 3: Different voice to verify voice_name parameter works
                if len(voices) > 1:
                    different_voice = voices[1]["name"]
                    different_payload = {
                        "text": test_text,
                        "voice_name": different_voice
                    }
                    
                    different_response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=different_payload,
                        timeout=30
                    )
                    
                    if different_response.status_code == 200:
                        different_data = different_response.json()
                        different_audio = different_data.get("audio_base64", "")
                        
                        # Verify different voices produce different audio
                        if different_audio != audio_base64:
                            self.log_test("Generate Audio - Voice Parameter", True,
                                        "Different voice_name produces different audio output")
                        else:
                            self.log_test("Generate Audio - Voice Parameter", False,
                                        "Different voice_name produced identical audio")
                    else:
                        self.log_test("Generate Audio - Voice Parameter", False,
                                    f"Failed with different voice: HTTP {different_response.status_code}")
                
                return True
                
            else:
                self.log_test("Generate Audio - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Audio - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_script_update_endpoint_review_requirements(self):
        """Test PUT /api/scripts/{script_id} with { script_id, generated_script } updates and returns updated record"""
        print("\n=== Testing PUT /api/scripts/{script_id} (Review Request Requirement 3) ===")
        
        # First, we need to create a script to update, or get an existing one
        try:
            # Try to get existing scripts first
            scripts_response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            script_id = None
            if scripts_response.status_code == 200:
                scripts = scripts_response.json()
                if scripts and len(scripts) > 0:
                    script_id = scripts[0]["id"]
                    self.log_test("Script Update - Existing Script Found", True,
                                f"Using existing script ID: {script_id}")
            
            # If no existing script, create one
            if not script_id:
                create_payload = {
                    "prompt": "Test script for update functionality",
                    "video_type": "general",
                    "duration": "short"
                }
                
                create_response = self.session.post(
                    f"{self.backend_url}/generate-script",
                    json=create_payload,
                    timeout=45
                )
                
                if create_response.status_code == 200:
                    create_data = create_response.json()
                    script_id = create_data["id"]
                    self.log_test("Script Update - Script Creation", True,
                                f"Created new script for testing: {script_id}")
                else:
                    self.log_test("Script Update - Script Creation", False,
                                f"Failed to create test script: HTTP {create_response.status_code}")
                    return False
            
        except Exception as e:
            self.log_test("Script Update - Setup", False, f"Failed to setup test script: {str(e)}")
            return False
        
        # Now test the PUT endpoint
        updated_script_content = """UPDATED SCRIPT CONTENT:

This is a test of the script update functionality. The script has been modified to verify that the PUT /api/scripts/{script_id} endpoint works correctly.

[Scene: Test environment]
(Narrator) This updated content should be saved to the database and returned in the response.

The update functionality is working as expected!"""
        
        update_payload = {
            "script_id": script_id,
            "generated_script": updated_script_content
        }
        
        try:
            response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=update_payload,
                timeout=30
            )
            
            # Check CORS headers
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            if any(cors_headers.values()):
                self.log_test("Script Update - CORS Headers", True,
                            f"CORS headers present: {cors_headers}")
            else:
                self.log_test("Script Update - CORS Headers", False,
                            "No CORS headers detected in response")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure - should return updated record
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Script Update - Response Structure", False,
                                f"Missing required fields in response: {missing_fields}")
                    return False
                
                # Verify the script was actually updated
                returned_script = data["generated_script"]
                if returned_script != updated_script_content:
                    self.log_test("Script Update - Content Update", False,
                                "Returned script content does not match updated content")
                    return False
                
                # Verify the ID matches
                if data["id"] != script_id:
                    self.log_test("Script Update - ID Consistency", False,
                                f"Returned ID {data['id']} does not match requested ID {script_id}")
                    return False
                
                self.log_test("Script Update - Basic Functionality", True,
                            f"Successfully updated script {script_id} and returned updated record")
                
                # Verify persistence by retrieving the script again
                time.sleep(1)  # Brief pause for database consistency
                
                verify_response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
                if verify_response.status_code == 200:
                    verify_scripts = verify_response.json()
                    updated_script = next((s for s in verify_scripts if s["id"] == script_id), None)
                    
                    if updated_script and updated_script["generated_script"] == updated_script_content:
                        self.log_test("Script Update - Persistence Verification", True,
                                    "Updated script content persisted correctly in database")
                    else:
                        self.log_test("Script Update - Persistence Verification", False,
                                    "Updated script content not found in database or content mismatch")
                else:
                    self.log_test("Script Update - Persistence Verification", False,
                                f"Failed to verify persistence: HTTP {verify_response.status_code}")
                
                return True
                
            else:
                self.log_test("Script Update - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Script Update - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_cors_headers_comprehensive(self):
        """Test CORS headers are intact across all endpoints"""
        print("\n=== Testing CORS Headers Comprehensive (Review Request Requirement 4) ===")
        
        endpoints_to_test = [
            {"method": "GET", "url": f"{self.backend_url}/", "name": "Root Endpoint"},
            {"method": "GET", "url": f"{self.backend_url}/voices", "name": "Voices Endpoint"},
            {"method": "GET", "url": f"{self.backend_url}/scripts", "name": "Scripts Endpoint"}
        ]
        
        cors_tests_passed = 0
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint["method"] == "GET":
                    response = self.session.get(endpoint["url"], timeout=15)
                else:
                    response = self.session.post(endpoint["url"], json={}, timeout=15)
                
                # Check for CORS headers
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('access-control-allow-origin'),
                    'Access-Control-Allow-Methods': response.headers.get('access-control-allow-methods'),
                    'Access-Control-Allow-Headers': response.headers.get('access-control-allow-headers'),
                    'Access-Control-Allow-Credentials': response.headers.get('access-control-allow-credentials')
                }
                
                present_headers = {k: v for k, v in cors_headers.items() if v is not None}
                
                if present_headers:
                    self.log_test(f"CORS Headers - {endpoint['name']}", True,
                                f"CORS headers present: {present_headers}")
                    cors_tests_passed += 1
                else:
                    self.log_test(f"CORS Headers - {endpoint['name']}", False,
                                "No CORS headers detected")
                    
            except Exception as e:
                self.log_test(f"CORS Headers - {endpoint['name']}", False,
                            f"Failed to test endpoint: {str(e)}")
        
        # Test OPTIONS preflight request
        try:
            options_response = self.session.options(f"{self.backend_url}/voices", timeout=15)
            
            if options_response.status_code in [200, 204]:
                options_cors = {
                    'Access-Control-Allow-Origin': options_response.headers.get('access-control-allow-origin'),
                    'Access-Control-Allow-Methods': options_response.headers.get('access-control-allow-methods'),
                    'Access-Control-Allow-Headers': options_response.headers.get('access-control-allow-headers')
                }
                
                present_options_headers = {k: v for k, v in options_cors.items() if v is not None}
                
                if present_options_headers:
                    self.log_test("CORS Headers - OPTIONS Preflight", True,
                                f"OPTIONS preflight CORS headers: {present_options_headers}")
                    cors_tests_passed += 1
                else:
                    self.log_test("CORS Headers - OPTIONS Preflight", False,
                                "No CORS headers in OPTIONS response")
            else:
                self.log_test("CORS Headers - OPTIONS Preflight", False,
                            f"OPTIONS request failed: HTTP {options_response.status_code}")
                
        except Exception as e:
            self.log_test("CORS Headers - OPTIONS Preflight", False,
                        f"OPTIONS request failed: {str(e)}")
        
        if cors_tests_passed >= 3:
            self.log_test("CORS Headers - Overall Assessment", True,
                        f"CORS headers working correctly: {cors_tests_passed} endpoints tested successfully")
            return True
        else:
            self.log_test("CORS Headers - Overall Assessment", False,
                        f"CORS headers may have issues: only {cors_tests_passed} endpoints passed")
            return False
    
    def run_review_request_tests(self):
        """Run all review request specific tests"""
        print("🚀 STARTING REVIEW REQUEST BACKEND TESTING")
        print("=" * 60)
        print("Testing specific requirements from review request:")
        print("1) GET /api/voices returns 8+ curated voices with required fields")
        print("2) POST /api/generate-audio with { text, voice_name } returns { audio_base64 }")
        print("3) PUT /api/scripts/{script_id} updates and returns updated record")
        print("4) Ensure CORS headers intact")
        print("=" * 60)
        
        # Run all tests
        test_results = []
        
        # Test 1: Voices endpoint
        voices_result = self.test_voices_endpoint_review_requirements()
        test_results.append(("Voices Endpoint", voices_result))
        
        # Test 2: Generate audio endpoint
        audio_result = self.test_generate_audio_endpoint_review_requirements()
        test_results.append(("Generate Audio Endpoint", audio_result))
        
        # Test 3: Script update endpoint
        update_result = self.test_script_update_endpoint_review_requirements()
        test_results.append(("Script Update Endpoint", update_result))
        
        # Test 4: CORS headers
        cors_result = self.test_cors_headers_comprehensive()
        test_results.append(("CORS Headers", cors_result))
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 REVIEW REQUEST TESTING SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL REVIEW REQUEST REQUIREMENTS VERIFIED SUCCESSFULLY!")
            print("Backend endpoints are responding as expected for dialogue edit/listen/download functionality.")
        else:
            print("⚠️  SOME REVIEW REQUEST REQUIREMENTS FAILED")
            print("Backend endpoints may have issues that need to be addressed.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = ReviewRequestTester()
    success = tester.run_review_request_tests()
    sys.exit(0 if success else 1)
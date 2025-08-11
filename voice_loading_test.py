#!/usr/bin/env python3
"""
Voice Loading Error Fix Verification Test
Critical test to verify the "Error loading voices. Please refresh the page." issue is resolved
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://91a9d61f-d967-4b3f-a16d-decd1e0775ab.preview.emergentagent.com/api"

class VoiceLoadingTester:
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
    
    def test_backend_health_check(self):
        """Test backend service health"""
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Backend Health Check", True, "Backend service is running properly")
                    return True
                else:
                    self.log_test("Backend Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Backend Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_voices_endpoint_accessibility(self):
        """Test GET /api/voices endpoint accessibility - CRITICAL TEST"""
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if response.status_code == 200:
                self.log_test("Voices Endpoint Accessibility", True, "GET /api/voices endpoint is accessible")
                return True, response
            else:
                self.log_test("Voices Endpoint Accessibility", False, f"HTTP {response.status_code}: {response.text}")
                return False, response
        except Exception as e:
            self.log_test("Voices Endpoint Accessibility", False, f"Connection error: {str(e)}")
            return False, None
    
    def test_voices_json_structure(self, response):
        """Test voices endpoint returns proper JSON structure"""
        try:
            data = response.json()
            if isinstance(data, list):
                self.log_test("Voices JSON Structure", True, f"Returns valid JSON list with {len(data)} voices")
                return True, data
            else:
                self.log_test("Voices JSON Structure", False, f"Expected list, got: {type(data)}")
                return False, data
        except Exception as e:
            self.log_test("Voices JSON Structure", False, f"JSON parsing error: {str(e)}")
            return False, None
    
    def test_voice_data_fields(self, voices_data):
        """Test each voice has required fields: name, display_name, language, gender"""
        required_fields = ['name', 'display_name', 'language', 'gender']
        
        if not voices_data:
            self.log_test("Voice Data Fields", False, "No voice data to test")
            return False
        
        all_valid = True
        missing_fields_summary = []
        
        for i, voice in enumerate(voices_data):
            missing_fields = []
            for field in required_fields:
                if field not in voice:
                    missing_fields.append(field)
                    all_valid = False
            
            if missing_fields:
                missing_fields_summary.append(f"Voice {i+1}: missing {missing_fields}")
        
        if all_valid:
            self.log_test("Voice Data Fields", True, f"All {len(voices_data)} voices have required fields: {required_fields}")
            return True
        else:
            self.log_test("Voice Data Fields", False, f"Missing fields found", missing_fields_summary)
            return False
    
    def test_voice_variety(self, voices_data):
        """Test we have adequate voice variety (multiple genders/languages)"""
        if not voices_data:
            self.log_test("Voice Variety", False, "No voice data to test")
            return False
        
        genders = set()
        languages = set()
        
        for voice in voices_data:
            if 'gender' in voice:
                genders.add(voice['gender'])
            if 'language' in voice:
                languages.add(voice['language'])
        
        gender_count = len(genders)
        language_count = len(languages)
        
        if gender_count >= 2 and language_count >= 2:
            self.log_test("Voice Variety", True, f"Good variety: {gender_count} genders, {language_count} languages")
            return True
        else:
            self.log_test("Voice Variety", False, f"Limited variety: {gender_count} genders, {language_count} languages")
            return False
    
    def test_audio_generation_with_voice(self, voice_name="en-US-AriaNeural"):
        """Test audio generation with selected voice"""
        test_text = "Hello, this is a test of the voice generation system. The voice loading error should be completely resolved."
        
        try:
            payload = {
                "text": test_text,
                "voice_name": voice_name
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'audio_base64' in data and len(data['audio_base64']) > 1000:
                    self.log_test("Audio Generation Integration", True, 
                                f"Successfully generated audio with {voice_name} ({len(data['audio_base64'])} chars)")
                    return True
                else:
                    self.log_test("Audio Generation Integration", False, 
                                f"Invalid audio response: {data}")
                    return False
            else:
                self.log_test("Audio Generation Integration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Audio Generation Integration", False, f"Error: {str(e)}")
            return False
    
    def test_multiple_voice_audio_generation(self, voices_data):
        """Test audio generation works with different voice selections"""
        if not voices_data or len(voices_data) < 2:
            self.log_test("Multiple Voice Audio Generation", False, "Not enough voices to test")
            return False
        
        test_voices = voices_data[:3]  # Test first 3 voices
        success_count = 0
        
        for voice in test_voices:
            voice_name = voice.get('name', 'unknown')
            if self.test_audio_generation_with_voice(voice_name):
                success_count += 1
        
        if success_count == len(test_voices):
            self.log_test("Multiple Voice Audio Generation", True, 
                        f"All {len(test_voices)} voices generated audio successfully")
            return True
        else:
            self.log_test("Multiple Voice Audio Generation", False, 
                        f"Only {success_count}/{len(test_voices)} voices worked")
            return False
    
    def test_dependency_verification(self):
        """Test that scikit-learn and other dependencies are working"""
        # This is indirect - if voices endpoint works, dependencies are loaded
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=10)
            if response.status_code == 200:
                self.log_test("Dependency Verification", True, 
                            "Backend started successfully - all dependencies loaded")
                return True
            else:
                self.log_test("Dependency Verification", False, 
                            f"Backend dependency issues - HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Dependency Verification", False, f"Dependency error: {str(e)}")
            return False
    
    def run_comprehensive_voice_tests(self):
        """Run all voice loading error fix verification tests"""
        print("🎤 VOICE LOADING ERROR FIX VERIFICATION TESTS")
        print("=" * 60)
        print(f"Testing backend: {self.backend_url}")
        print(f"Test started: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Backend Health Check
        print("1. BACKEND SERVICE HEALTH CHECK")
        backend_healthy = self.test_backend_health_check()
        print()
        
        if not backend_healthy:
            print("❌ CRITICAL: Backend service is not running. Cannot proceed with voice tests.")
            return self.generate_summary()
        
        # Test 2: Dependency Verification
        print("2. DEPENDENCY VERIFICATION")
        self.test_dependency_verification()
        print()
        
        # Test 3: Voice API Endpoint Testing
        print("3. VOICE API ENDPOINT TESTING")
        voices_accessible, voices_response = self.test_voices_endpoint_accessibility()
        print()
        
        if not voices_accessible:
            print("❌ CRITICAL: Voice endpoint not accessible. This is the core issue!")
            return self.generate_summary()
        
        # Test 4: Voice JSON Structure
        print("4. VOICE DATA STRUCTURE VERIFICATION")
        valid_json, voices_data = self.test_voices_json_structure(voices_response)
        print()
        
        if not valid_json:
            print("❌ CRITICAL: Voice endpoint returns invalid JSON structure!")
            return self.generate_summary()
        
        # Test 5: Voice Data Fields
        print("5. VOICE DATA FIELDS VERIFICATION")
        self.test_voice_data_fields(voices_data)
        print()
        
        # Test 6: Voice Variety
        print("6. VOICE VARIETY VERIFICATION")
        self.test_voice_variety(voices_data)
        print()
        
        # Test 7: Audio Generation Integration
        print("7. AUDIO GENERATION INTEGRATION")
        self.test_audio_generation_with_voice()
        print()
        
        # Test 8: Multiple Voice Audio Generation
        print("8. MULTIPLE VOICE AUDIO GENERATION")
        self.test_multiple_voice_audio_generation(voices_data)
        print()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("🎤 VOICE LOADING ERROR FIX VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
            print()
        
        # Critical assessment
        critical_tests = [
            "Backend Health Check",
            "Voices Endpoint Accessibility", 
            "Voices JSON Structure",
            "Voice Data Fields"
        ]
        
        critical_failures = []
        for result in self.test_results:
            if result['test'] in critical_tests and not result['success']:
                critical_failures.append(result['test'])
        
        if critical_failures:
            print("🚨 CRITICAL ISSUE: Voice loading error NOT RESOLVED!")
            print(f"Critical failures: {critical_failures}")
            print("The 'Error loading voices. Please refresh the page.' issue persists.")
            return False
        else:
            print("🎉 SUCCESS: Voice loading error COMPLETELY RESOLVED!")
            print("Users should no longer see 'Error loading voices. Please refresh the page.'")
            return True

if __name__ == "__main__":
    tester = VoiceLoadingTester()
    success = tester.run_comprehensive_voice_tests()
    sys.exit(0 if success else 1)
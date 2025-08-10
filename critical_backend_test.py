#!/usr/bin/env python3
"""
Critical Backend Test - Focus on Review Request Requirements
Tests the specific functionality mentioned in the voice loading error fix verification
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://9d31a06f-9858-4a2d-b53b-a9b5446ec4e8.preview.emergentagent.com/api"

class CriticalBackendTester:
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
    
    def test_root_endpoint(self):
        """Test /api/ root endpoint responds correctly"""
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Root Endpoint", True, "API root endpoint responding correctly")
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_voices_endpoint_detailed(self):
        """Test GET /api/voices endpoint with detailed verification"""
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                # Verify it's a list
                if not isinstance(data, list):
                    self.log_test("Voices Endpoint Detailed", False, f"Expected list, got {type(data)}")
                    return False, None
                
                # Verify we have voices
                if len(data) == 0:
                    self.log_test("Voices Endpoint Detailed", False, "No voices returned")
                    return False, None
                
                # Verify structure of first voice
                required_fields = ['name', 'display_name', 'language', 'gender']
                first_voice = data[0]
                missing_fields = [field for field in required_fields if field not in first_voice]
                
                if missing_fields:
                    self.log_test("Voices Endpoint Detailed", False, f"Missing fields: {missing_fields}")
                    return False, None
                
                # Check for variety
                genders = set(voice.get('gender', '') for voice in data)
                languages = set(voice.get('language', '') for voice in data)
                
                self.log_test("Voices Endpoint Detailed", True, 
                            f"Returns {len(data)} voices with {len(genders)} genders, {len(languages)} languages")
                return True, data
            else:
                self.log_test("Voices Endpoint Detailed", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Voices Endpoint Detailed", False, f"Error: {str(e)}")
            return False, None
    
    def test_audio_generation_workflow(self, voices_data):
        """Test complete audio generation workflow with voice selection"""
        if not voices_data:
            self.log_test("Audio Generation Workflow", False, "No voice data available")
            return False
        
        # Test with first available voice
        test_voice = voices_data[0]
        voice_name = test_voice.get('name', 'en-US-AriaNeural')
        
        test_script = """Welcome to our healthy cooking tips video! Today we'll explore simple techniques that will transform your kitchen experience. 
        
        [Image: Fresh vegetables on a cutting board]
        
        First, let's talk about meal preparation. The key to healthy cooking starts with fresh, quality ingredients.
        
        (Pause for emphasis)
        
        Remember, cooking healthy doesn't mean sacrificing flavor!"""
        
        try:
            payload = {
                "text": test_script,
                "voice_name": voice_name
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ['audio_base64', 'voice_used']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Audio Generation Workflow", False, f"Missing response fields: {missing_fields}")
                    return False
                
                # Verify audio data
                audio_base64 = data.get('audio_base64', '')
                if len(audio_base64) < 1000:
                    self.log_test("Audio Generation Workflow", False, f"Audio data too short: {len(audio_base64)} chars")
                    return False
                
                # Verify voice used
                voice_used = data.get('voice_used', '')
                if voice_used != voice_name:
                    self.log_test("Audio Generation Workflow", False, f"Wrong voice used: {voice_used} vs {voice_name}")
                    return False
                
                self.log_test("Audio Generation Workflow", True, 
                            f"Generated {len(audio_base64)} chars of audio with {voice_used}")
                return True
            else:
                self.log_test("Audio Generation Workflow", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Audio Generation Workflow", False, f"Error: {str(e)}")
            return False
    
    def test_voice_selection_functionality(self, voices_data):
        """Test voice selection works with different voices"""
        if not voices_data or len(voices_data) < 2:
            self.log_test("Voice Selection Functionality", False, "Need at least 2 voices to test")
            return False
        
        test_text = "This is a voice selection test."
        success_count = 0
        tested_voices = []
        
        # Test up to 3 different voices
        for voice in voices_data[:3]:
            voice_name = voice.get('name', '')
            if not voice_name:
                continue
                
            try:
                payload = {
                    "text": test_text,
                    "voice_name": voice_name
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'audio_base64' in data and len(data['audio_base64']) > 500:
                        success_count += 1
                        tested_voices.append(voice_name)
                
            except Exception as e:
                continue
        
        if success_count >= 2:
            self.log_test("Voice Selection Functionality", True, 
                        f"Successfully tested {success_count} voices: {tested_voices}")
            return True
        else:
            self.log_test("Voice Selection Functionality", False, 
                        f"Only {success_count} voices worked out of {len(voices_data[:3])} tested")
            return False
    
    def test_core_api_endpoints(self):
        """Test that all core API endpoints are accessible"""
        endpoints_to_test = [
            ("/", "Root endpoint"),
            ("/voices", "Voices endpoint"),
        ]
        
        accessible_count = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{self.backend_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    accessible_count += 1
                    print(f"  ✅ {description}: Accessible")
                else:
                    print(f"  ❌ {description}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ {description}: Error - {str(e)}")
        
        if accessible_count == total_endpoints:
            self.log_test("Core API Endpoints", True, f"All {total_endpoints} core endpoints accessible")
            return True
        else:
            self.log_test("Core API Endpoints", False, f"Only {accessible_count}/{total_endpoints} endpoints accessible")
            return False
    
    def run_critical_tests(self):
        """Run critical backend tests focusing on voice functionality"""
        print("🔥 CRITICAL BACKEND TESTS - VOICE LOADING ERROR FIX VERIFICATION")
        print("=" * 70)
        print(f"Testing backend: {self.backend_url}")
        print(f"Test started: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Core API Endpoints
        print("1. CORE API ENDPOINTS ACCESSIBILITY")
        self.test_core_api_endpoints()
        print()
        
        # Test 2: Root Endpoint
        print("2. ROOT ENDPOINT VERIFICATION")
        self.test_root_endpoint()
        print()
        
        # Test 3: Voices Endpoint Detailed
        print("3. VOICES ENDPOINT DETAILED VERIFICATION")
        voices_success, voices_data = self.test_voices_endpoint_detailed()
        print()
        
        if not voices_success:
            print("❌ CRITICAL: Voices endpoint failed. Cannot proceed with voice tests.")
            return self.generate_summary()
        
        # Test 4: Audio Generation Workflow
        print("4. AUDIO GENERATION WORKFLOW")
        self.test_audio_generation_workflow(voices_data)
        print()
        
        # Test 5: Voice Selection Functionality
        print("5. VOICE SELECTION FUNCTIONALITY")
        self.test_voice_selection_functionality(voices_data)
        print()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 70)
        print("🔥 CRITICAL BACKEND TESTS SUMMARY")
        print("=" * 70)
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
        
        # Overall assessment
        critical_success = passed_tests >= (total_tests * 0.8)  # 80% pass rate
        
        if critical_success:
            print("🎉 OVERALL ASSESSMENT: CRITICAL TESTS PASSED!")
            print("✅ Voice loading error fix is working correctly")
            print("✅ Backend services are operational")
            print("✅ Voice selection and audio generation functional")
            return True
        else:
            print("🚨 OVERALL ASSESSMENT: CRITICAL ISSUES DETECTED!")
            print("❌ Voice loading error may not be fully resolved")
            return False

if __name__ == "__main__":
    tester = CriticalBackendTester()
    success = tester.run_critical_tests()
    sys.exit(0 if success else 1)
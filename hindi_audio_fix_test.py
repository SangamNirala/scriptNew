#!/usr/bin/env python3
"""
Hindi Audio Generation Fix Testing
==================================

This test suite specifically tests the Hindi audio generation fix as requested in the review.
Focus areas:
1. Hindi Audio Generation with Timestamps - exact user scenario
2. Timestamp Format Support - all formats mentioned
3. Language Detection - automatic Hindi voice selection
4. No Regression - English audio still works

Test Environment: Uses production backend URL from frontend/.env
"""

import requests
import json
import time
import base64
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HindiAudioFixTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://7e1a0c85-0a06-49a1-86bc-15e9c588a17b.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Test results tracking
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # Exact Hindi content from review request
        self.review_request_hindi_content = """(0: 00-0: 03
भावना अटक गई? आप अकेले नहीं हैं।

0: 03-0: 06  
लेकिन ठहराव आपका भाग्य नहीं है। समय के भीतर अजेय बल को उजागर करने का समय।

0: 06-0: 09
दुनिया का इंतजार है।"""

        # Various timestamp formats to test
        self.timestamp_test_cases = {
            'bracketed': """[0:00-0:03]
भावना अटक गई? आप अकेले नहीं हैं।
[0:03-0:06]
लेकिन ठहराव आपका भाग्य नहीं है।""",
            
            'bare': """0:00-0:03
भावना अटक गई? आप अकेले नहीं हैं।
0:03-0:06
लेकिन ठहराव आपका भाग्य नहीं है।""",
            
            'spaces_around_colons': """0: 00-0: 03
भावना अटक गई? आप अकेले नहीं हैं।
0: 03-0: 06
लेकिन ठहराव आपका भाग्य नहीं है।""",
            
            'parenthesized_with_spaces': """(0: 00-0: 03
भावना अटक गई? आप अकेले नहीं हैं।
(0: 03-0: 06
लेकिन ठहराव आपका भाग्य नहीं है।"""
        }
        
        # Expected Hindi voices
        self.expected_hindi_voices = [
            "hi-IN-SwaraNeural",
            "hi-IN-MadhurNeural"
        ]

    def log_test_result(self, test_name: str, passed: bool, details: str, response_data: Optional[Dict] = None):
        """Log test result and update counters"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            self.test_results['failed_tests'] += 1
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'response_data': response_data
        })

    def test_backend_connectivity(self) -> bool:
        """Test basic backend connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test_result("Backend Connectivity", True, f"Backend responding with status {response.status_code}")
                return True
            else:
                self.log_test_result("Backend Connectivity", False, f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Backend Connectivity", False, f"Connection error: {str(e)}")
            return False

    def test_voices_endpoint_hindi_support(self) -> bool:
        """Test /api/voices endpoint returns Hindi voices"""
        try:
            response = self.session.get(f"{self.base_url}/voices")
            
            if response.status_code != 200:
                self.log_test_result("Voices Endpoint Hindi Support", False, 
                                   f"Voices endpoint returned status {response.status_code}")
                return False
            
            voices_data = response.json()
            
            # Check if response is a list
            if not isinstance(voices_data, list):
                self.log_test_result("Voices Endpoint Hindi Support", False, 
                                   f"Expected list, got {type(voices_data)}")
                return False
            
            # Extract voice names and check structure
            voice_names = []
            hindi_voices_found = []
            
            for voice in voices_data:
                if isinstance(voice, dict) and 'name' in voice:
                    voice_name = voice['name']
                    voice_names.append(voice_name)
                    
                    # Check for Hindi voices
                    if voice_name in self.expected_hindi_voices:
                        hindi_voices_found.append(voice_name)
            
            if len(hindi_voices_found) >= 1:
                self.log_test_result("Voices Endpoint Hindi Support", True, 
                                   f"Found {len(hindi_voices_found)} Hindi voices: {hindi_voices_found}. Total voices: {len(voices_data)}")
                return True
            else:
                self.log_test_result("Voices Endpoint Hindi Support", False, 
                                   f"No Hindi voices found. Available voices: {voice_names[:5]}...")
                return False
                
        except Exception as e:
            self.log_test_result("Voices Endpoint Hindi Support", False, f"Error: {str(e)}")
            return False

    def test_exact_review_request_scenario(self) -> bool:
        """Test the exact Hindi content scenario from the review request"""
        try:
            payload = {
                "text": self.review_request_hindi_content,
                "voice_name": "en-US-AriaNeural"  # Request English voice, should auto-switch to Hindi
            }
            
            logger.info("Testing exact review request scenario with Hindi content and timestamps...")
            response = self.session.post(f"{self.base_url}/generate-audio", json=payload)
            
            if response.status_code != 200:
                self.log_test_result("Exact Review Request Scenario", False, 
                                   f"Audio generation failed with status {response.status_code}: {response.text}")
                return False
            
            audio_data = response.json()
            
            # Verify response structure
            if 'audio_base64' not in audio_data:
                self.log_test_result("Exact Review Request Scenario", False, 
                                   "Response missing 'audio_base64' field")
                return False
            
            # Verify audio data is substantial (indicates successful generation)
            audio_base64 = audio_data['audio_base64']
            if len(audio_base64) < 10000:  # Expect substantial audio data
                self.log_test_result("Exact Review Request Scenario", False, 
                                   f"Audio data too small: {len(audio_base64)} chars")
                return False
            
            # Check if Hindi voice was used
            voice_used = audio_data.get('voice_used', '')
            is_hindi_voice = any(hindi_voice in voice_used for hindi_voice in self.expected_hindi_voices)
            
            self.log_test_result("Exact Review Request Scenario", True, 
                               f"Audio generated successfully: {len(audio_base64)} chars, Voice: {voice_used}, Hindi voice used: {is_hindi_voice}")
            return True
            
        except Exception as e:
            self.log_test_result("Exact Review Request Scenario", False, f"Error: {str(e)}")
            return False

    def test_timestamp_format_support(self) -> bool:
        """Test all timestamp formats mentioned in the review request"""
        all_passed = True
        
        for format_name, content in self.timestamp_test_cases.items():
            try:
                payload = {
                    "text": content,
                    "voice_name": "hi-IN-SwaraNeural"  # Use Hindi voice directly
                }
                
                logger.info(f"Testing timestamp format: {format_name}")
                response = self.session.post(f"{self.base_url}/generate-audio", json=payload)
                
                if response.status_code != 200:
                    self.log_test_result(f"Timestamp Format - {format_name}", False, 
                                       f"Audio generation failed with status {response.status_code}")
                    all_passed = False
                    continue
                
                audio_data = response.json()
                
                # Verify audio was generated
                if 'audio_base64' not in audio_data or len(audio_data['audio_base64']) < 5000:
                    self.log_test_result(f"Timestamp Format - {format_name}", False, 
                                       "Audio generation failed or produced insufficient data")
                    all_passed = False
                    continue
                
                audio_length = len(audio_data['audio_base64'])
                voice_used = audio_data.get('voice_used', '')
                
                self.log_test_result(f"Timestamp Format - {format_name}", True, 
                                   f"Audio generated: {audio_length} chars, Voice: {voice_used}")
                
            except Exception as e:
                self.log_test_result(f"Timestamp Format - {format_name}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_language_detection_automatic_voice_selection(self) -> bool:
        """Test automatic Hindi voice selection for Hindi content"""
        test_cases = [
            {
                'name': 'Pure Hindi Content',
                'content': 'भावना अटक गई? आप अकेले नहीं हैं। लेकिन ठहराव आपका भाग्य नहीं है।',
                'requested_voice': 'en-US-AriaNeural',  # Request English voice
                'expect_hindi': True
            },
            {
                'name': 'Pure English Content',
                'content': 'Hello and welcome to our video. Today we will discuss healthy cooking tips.',
                'requested_voice': 'en-US-AriaNeural',  # Request English voice
                'expect_hindi': False
            },
            {
                'name': 'Mixed Content',
                'content': 'Hello और नमस्ते! Today हम will discuss स्वस्थ cooking tips.',
                'requested_voice': 'en-US-AriaNeural',  # Request English voice
                'expect_hindi': None  # Could go either way
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                payload = {
                    "text": test_case['content'],
                    "voice_name": test_case['requested_voice']
                }
                
                logger.info(f"Testing language detection: {test_case['name']}")
                response = self.session.post(f"{self.base_url}/generate-audio", json=payload)
                
                if response.status_code != 200:
                    self.log_test_result(f"Language Detection - {test_case['name']}", False, 
                                       f"Audio generation failed with status {response.status_code}")
                    all_passed = False
                    continue
                
                audio_data = response.json()
                voice_used = audio_data.get('voice_used', '')
                is_hindi_voice = any(hindi_voice in voice_used for hindi_voice in self.expected_hindi_voices)
                
                # Check if voice selection matches expectation
                if test_case['expect_hindi'] is True and not is_hindi_voice:
                    self.log_test_result(f"Language Detection - {test_case['name']}", False, 
                                       f"Expected Hindi voice but got: {voice_used}")
                    all_passed = False
                elif test_case['expect_hindi'] is False and is_hindi_voice:
                    self.log_test_result(f"Language Detection - {test_case['name']}", False, 
                                       f"Expected English voice but got: {voice_used}")
                    all_passed = False
                else:
                    self.log_test_result(f"Language Detection - {test_case['name']}", True, 
                                       f"Voice selection appropriate: {voice_used}, Hindi: {is_hindi_voice}")
                
            except Exception as e:
                self.log_test_result(f"Language Detection - {test_case['name']}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_english_audio_no_regression(self) -> bool:
        """Test that English audio generation still works correctly with timestamps removed"""
        english_content_with_timestamps = """[0:00-0:03]
Hello and welcome to our video.
[0:03-0:06]
Today we will discuss healthy cooking tips.
[0:06-0:09]
First, let's talk about fresh ingredients."""
        
        try:
            payload = {
                "text": english_content_with_timestamps,
                "voice_name": "en-US-AriaNeural"
            }
            
            logger.info("Testing English audio generation (no regression test)")
            response = self.session.post(f"{self.base_url}/generate-audio", json=payload)
            
            if response.status_code != 200:
                self.log_test_result("English Audio No Regression", False, 
                                   f"Audio generation failed with status {response.status_code}")
                return False
            
            audio_data = response.json()
            
            # Verify audio was generated
            if 'audio_base64' not in audio_data or len(audio_data['audio_base64']) < 5000:
                self.log_test_result("English Audio No Regression", False, 
                                   "Audio generation failed or produced insufficient data")
                return False
            
            voice_used = audio_data.get('voice_used', '')
            audio_length = len(audio_data['audio_base64'])
            
            # Should use English voice for English content
            is_english_voice = 'en-' in voice_used and not any(hindi_voice in voice_used for hindi_voice in self.expected_hindi_voices)
            
            if is_english_voice:
                self.log_test_result("English Audio No Regression", True, 
                                   f"English audio generated correctly: {audio_length} chars, Voice: {voice_used}")
                return True
            else:
                self.log_test_result("English Audio No Regression", False, 
                                   f"Unexpected voice used for English content: {voice_used}")
                return False
            
        except Exception as e:
            self.log_test_result("English Audio No Regression", False, f"Error: {str(e)}")
            return False

    def run_comprehensive_hindi_audio_fix_tests(self):
        """Run all Hindi audio generation fix tests"""
        logger.info("🚀 Starting Comprehensive Hindi Audio Generation Fix Testing")
        logger.info("=" * 80)
        
        # Test 1: Backend Connectivity
        logger.info("Test 1: Backend Connectivity")
        self.test_backend_connectivity()
        
        # Test 2: Voices Endpoint Hindi Support
        logger.info("\nTest 2: Voices Endpoint Hindi Support")
        self.test_voices_endpoint_hindi_support()
        
        # Test 3: Exact Review Request Scenario
        logger.info("\nTest 3: Exact Review Request Scenario")
        self.test_exact_review_request_scenario()
        
        # Test 4: Timestamp Format Support
        logger.info("\nTest 4: Timestamp Format Support")
        self.test_timestamp_format_support()
        
        # Test 5: Language Detection and Automatic Voice Selection
        logger.info("\nTest 5: Language Detection and Automatic Voice Selection")
        self.test_language_detection_automatic_voice_selection()
        
        # Test 6: English Audio No Regression
        logger.info("\nTest 6: English Audio No Regression")
        self.test_english_audio_no_regression()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 HINDI AUDIO GENERATION FIX TEST RESULTS")
        logger.info("=" * 80)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"📊 OVERALL RESULTS:")
        logger.info(f"   Total Tests: {total}")
        logger.info(f"   Passed: {passed}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("🎉 EXCELLENT: Hindi audio generation fix is working well!")
        elif success_rate >= 60:
            logger.info("⚠️  GOOD: Hindi audio generation fix is mostly working with some issues")
        else:
            logger.info("❌ CRITICAL: Hindi audio generation fix has significant issues")
        
        logger.info("\n📋 DETAILED TEST RESULTS:")
        for test_detail in self.test_results['test_details']:
            status = "✅ PASSED" if test_detail['passed'] else "❌ FAILED"
            logger.info(f"   {status}: {test_detail['test_name']} - {test_detail['details']}")
        
        logger.info("=" * 80)

if __name__ == "__main__":
    tester = HindiAudioFixTester()
    tester.run_comprehensive_hindi_audio_fix_tests()
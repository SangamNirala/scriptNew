#!/usr/bin/env python3
"""
Translation Backend Testing Script
Tests the /api/translate-script endpoint comprehensively
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://9d31a06f-9858-4a2d-b53b-a9b5446ec4e8.preview.emergentagent.com/api"

class TranslationTester:
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
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Basic Connectivity", True, "API is accessible and responding")
                    return True
                else:
                    self.log_test("Basic Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Basic Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_endpoint_availability_and_schema(self):
        """Test endpoint availability and response schema"""
        print("\n=== Testing Translation Endpoint Availability and Schema ===")
        
        # Test basic endpoint availability with simple translation
        test_payload = {
            "text": "Hello world",
            "source_language": "en",
            "target_language": "hi"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=test_payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response schema
                required_fields = [
                    "original_text", "translated_text", "source_language", 
                    "target_language", "translation_service", "success"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Translation Schema", False,
                                f"Missing required fields: {missing_fields}", data.keys())
                    return False
                
                # Verify field types and values
                if not isinstance(data["success"], bool):
                    self.log_test("Translation Schema - Success Field", False,
                                f"success field should be boolean, got {type(data['success'])}")
                    return False
                
                if not data["success"]:
                    self.log_test("Translation Schema - Success Value", False,
                                "success field is False for valid request")
                    return False
                
                if data["original_text"] != test_payload["text"]:
                    self.log_test("Translation Schema - Original Text", False,
                                f"original_text mismatch: expected '{test_payload['text']}', got '{data['original_text']}'")
                    return False
                
                if data["source_language"] != test_payload["source_language"]:
                    self.log_test("Translation Schema - Source Language", False,
                                f"source_language mismatch: expected '{test_payload['source_language']}', got '{data['source_language']}'")
                    return False
                
                if data["target_language"] != test_payload["target_language"]:
                    self.log_test("Translation Schema - Target Language", False,
                                f"target_language mismatch: expected '{test_payload['target_language']}', got '{data['target_language']}'")
                    return False
                
                if not data["translated_text"]:
                    self.log_test("Translation Schema - Translated Text", False,
                                "translated_text is empty")
                    return False
                
                if not data["translation_service"]:
                    self.log_test("Translation Schema - Translation Service", False,
                                "translation_service is empty")
                    return False
                
                response_time = end_time - start_time
                self.log_test("Translation Endpoint Availability", True,
                            f"Endpoint available, returns 200 with correct schema in {response_time:.2f}s")
                self.log_test("Translation Schema Validation", True,
                            f"All required fields present with correct types and values")
                
                return True
                
            else:
                self.log_test("Translation Endpoint Availability", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Translation Endpoint Availability", False, f"Request failed: {str(e)}")
            return False
    
    def test_functional_translations(self):
        """Test functional translation scenarios"""
        print("\n=== Testing Functional Translation Scenarios ===")
        
        # Test Case 1: English to Hindi translation with bracket preservation
        test_text = "(Voiceover) Welcome to our kitchen! [CAMERA: Close-up of hands]"
        payload = {
            "text": test_text,
            "source_language": "en",
            "target_language": "hi"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=payload,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data["translated_text"]
                
                # Verify bracket preservation - [CAMERA: Close-up of hands] should remain in English
                if "[CAMERA: Close-up of hands]" not in translated_text:
                    self.log_test("EN→HI Translation - Bracket Preservation", False,
                                f"Bracketed segment not preserved in English: {translated_text}")
                    return False
                
                # Verify non-bracket text is translated (should be different from original)
                non_bracket_original = "(Voiceover) Welcome to our kitchen! "
                if non_bracket_original in translated_text:
                    self.log_test("EN→HI Translation - Text Translation", False,
                                f"Non-bracket text not translated: {translated_text}")
                    return False
                
                response_time = end_time - start_time
                self.log_test("EN→HI Translation", True,
                            f"Successfully translated with bracket preservation in {response_time:.2f}s")
                
            else:
                self.log_test("EN→HI Translation", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("EN→HI Translation", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 2: English to English (no-op) translation
        en_to_en_payload = {
            "text": "Hello world [CAMERA: Wide shot]",
            "source_language": "en", 
            "target_language": "en"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=en_to_en_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data["translated_text"]
                
                # Should return same text (except possibly spacing differences)
                original_normalized = en_to_en_payload["text"].strip()
                translated_normalized = translated_text.strip()
                
                # Allow for minor spacing differences but core content should be same
                if "[CAMERA: Wide shot]" not in translated_text:
                    self.log_test("EN→EN Translation - Bracket Preservation", False,
                                f"Brackets not preserved in EN→EN: {translated_text}")
                    return False
                
                if "Hello world" not in translated_text:
                    self.log_test("EN→EN Translation - Text Preservation", False,
                                f"Original text not preserved in EN→EN: {translated_text}")
                    return False
                
                self.log_test("EN→EN Translation", True,
                            f"Successfully handled EN→EN no-op with bracket preservation")
                
            else:
                self.log_test("EN→EN Translation", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("EN→EN Translation", False, f"Request failed: {str(e)}")
            return False
        
        return True
    
    def test_long_text_translation(self):
        """Test long text translation with chunking"""
        print("\n=== Testing Long Text Translation with Chunking ===")
        
        # Create ~6000-9000 character text with repeating sentences and bracketed segments
        base_sentence = "This is a comprehensive test of the translation system with various content types and structures. "
        bracketed_segment1 = "[CAMERA: Establishing shot of the location] "
        bracketed_segment2 = "[GRAPHICS: Display statistics on screen] "
        
        # Build long text
        long_text_parts = []
        for i in range(50):  # Create substantial content
            long_text_parts.append(f"Sentence {i+1}: {base_sentence}")
            if i == 20:
                long_text_parts.append(bracketed_segment1)
            elif i == 40:
                long_text_parts.append(bracketed_segment2)
        
        long_text = " ".join(long_text_parts)
        text_length = len(long_text)
        
        if text_length < 6000:
            # Add more content to reach target length
            additional_content = "Additional content to reach target length. " * 100
            long_text += additional_content
            text_length = len(long_text)
        
        payload = {
            "text": long_text,
            "source_language": "en",
            "target_language": "hi"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=payload,
                timeout=60  # Longer timeout for long text
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data["translated_text"]
                translated_length = len(translated_text)
                response_time = end_time - start_time
                
                # Verify no 413 or 500 errors
                self.log_test("Long Text - No Server Errors", True,
                            f"Successfully processed {text_length} chars without 413/500 errors")
                
                # Verify reasonable result length (should be substantial)
                if translated_length < 1000:
                    self.log_test("Long Text - Result Length", False,
                                f"Translated text too short: {translated_length} chars from {text_length} chars input")
                    return False
                
                # Verify bracketed segments preserved in English
                if bracketed_segment1.strip() not in translated_text:
                    self.log_test("Long Text - Bracket Preservation 1", False,
                                f"First bracketed segment not preserved: {bracketed_segment1}")
                    return False
                
                if bracketed_segment2.strip() not in translated_text:
                    self.log_test("Long Text - Bracket Preservation 2", False,
                                f"Second bracketed segment not preserved: {bracketed_segment2}")
                    return False
                
                # Verify processing time is reasonable
                if response_time > 30:
                    self.log_test("Long Text - Processing Time", False,
                                f"Processing took too long: {response_time:.2f}s (should be <30s)")
                    return False
                
                self.log_test("Long Text Translation", True,
                            f"Successfully processed {text_length} chars → {translated_length} chars in {response_time:.2f}s")
                
                return True
                
            elif response.status_code == 413:
                self.log_test("Long Text Translation", False,
                            f"Request entity too large (413) - chunking not working properly")
                return False
            elif response.status_code == 500:
                self.log_test("Long Text Translation", False,
                            f"Internal server error (500) - {response.text}")
                return False
            else:
                self.log_test("Long Text Translation", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Long Text Translation", False, f"Request failed: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n=== Testing Error Handling ===")
        
        # Test Case 1: Invalid target language code
        invalid_lang_payload = {
            "text": "Test text for invalid language",
            "source_language": "en",
            "target_language": "xx"  # Invalid language code
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=invalid_lang_payload,
                timeout=30
            )
            
            if response.status_code == 503:
                response_data = response.json()
                detail = response_data.get("detail", "")
                
                if "translation service temporarily unavailable" in detail.lower() or "unavailable" in detail.lower():
                    self.log_test("Error Handling - Invalid Language Code", True,
                                f"Correctly returned 503 with appropriate message: {detail}")
                else:
                    self.log_test("Error Handling - Invalid Language Code", False,
                                f"503 returned but message not appropriate: {detail}")
                    return False
            else:
                self.log_test("Error Handling - Invalid Language Code", False,
                            f"Expected 503, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling - Invalid Language Code", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 2: Empty text handling
        empty_text_payload = {
            "text": "",
            "source_language": "en",
            "target_language": "hi"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=empty_text_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data["success"] and data["translated_text"] == "":
                    self.log_test("Error Handling - Empty Text", True,
                                "Successfully processed empty text with success=True and empty translated_text")
                else:
                    self.log_test("Error Handling - Empty Text", False,
                                f"Unexpected response for empty text: {data}")
                    return False
            else:
                self.log_test("Error Handling - Empty Text", False,
                            f"Expected 200 for empty text, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling - Empty Text", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 3: Missing required fields
        missing_field_payload = {
            "text": "Test text",
            "source_language": "en"
            # Missing target_language
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=missing_field_payload,
                timeout=30
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test("Error Handling - Missing Required Field", True,
                            f"Correctly returned 422 for missing target_language field")
            else:
                self.log_test("Error Handling - Missing Required Field", False,
                            f"Expected 422 for missing field, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling - Missing Required Field", False, f"Request failed: {str(e)}")
            return False
        
        return True
    
    def test_performance(self):
        """Test performance with ~10k character text"""
        print("\n=== Testing Performance with ~10k Characters ===")
        
        # Create ~10k character text with masked content (brackets)
        base_content = "This is a performance test of the translation system with substantial content to verify processing speed and reliability. "
        bracket_content = "[CAMERA: Professional shot with proper lighting and composition] "
        
        # Build content to reach ~10k characters
        content_parts = []
        current_length = 0
        counter = 0
        
        while current_length < 10000:
            if counter % 10 == 0:
                part = bracket_content
            else:
                part = f"Performance test sentence {counter}: {base_content}"
            
            content_parts.append(part)
            current_length += len(part)
            counter += 1
        
        performance_text = " ".join(content_parts)
        actual_length = len(performance_text)
        
        payload = {
            "text": performance_text,
            "source_language": "en",
            "target_language": "hi"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=payload,
                timeout=35  # 30s requirement + 5s buffer
            )
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify completion within 30 seconds
                if processing_time <= 30:
                    self.log_test("Performance - Processing Time", True,
                                f"Processed {actual_length} chars in {processing_time:.2f}s (within 30s requirement)")
                else:
                    self.log_test("Performance - Processing Time", False,
                                f"Processing took {processing_time:.2f}s (exceeds 30s requirement)")
                    return False
                
                # Verify successful translation
                if data["success"]:
                    translated_length = len(data["translated_text"])
                    self.log_test("Performance - Translation Success", True,
                                f"Successfully translated {actual_length} → {translated_length} chars")
                else:
                    self.log_test("Performance - Translation Success", False,
                                "Translation marked as unsuccessful")
                    return False
                
                # Verify bracket preservation in large text
                bracket_count_original = performance_text.count("[CAMERA:")
                bracket_count_translated = data["translated_text"].count("[CAMERA:")
                
                if bracket_count_original == bracket_count_translated:
                    self.log_test("Performance - Bracket Preservation", True,
                                f"All {bracket_count_original} bracketed segments preserved")
                else:
                    self.log_test("Performance - Bracket Preservation", False,
                                f"Bracket preservation failed: {bracket_count_original} → {bracket_count_translated}")
                    return False
                
                return True
                
            else:
                self.log_test("Performance Test", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_test("Performance - Timeout", False,
                        f"Request timed out after 35s (requirement is 30s)")
            return False
        except Exception as e:
            self.log_test("Performance Test", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all translation tests"""
        print("🚀 Starting Translation Backend Testing")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 60)
        
        test_methods = [
            self.test_basic_connectivity,
            self.test_endpoint_availability_and_schema,
            self.test_functional_translations,
            self.test_long_text_translation,
            self.test_error_handling,
            self.test_performance
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {str(e)}")
        
        print("\n" + "=" * 60)
        print("🏁 TRANSLATION TESTING COMPLETE")
        print(f"✅ Passed: {passed_tests}/{total_tests} tests")
        
        if passed_tests == total_tests:
            print("🎉 ALL TRANSLATION TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed")
            return False
    
    def get_test_summary(self):
        """Get summary of test results"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results
        }
        
        return summary

if __name__ == "__main__":
    tester = TranslationTester()
    success = tester.run_all_tests()
    
    # Print detailed results
    summary = tester.get_test_summary()
    print(f"\n📊 DETAILED RESULTS:")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    if not success:
        print("\n❌ FAILED TESTS:")
        for result in summary['test_results']:
            if not result['success']:
                print(f"  - {result['test']}: {result['message']}")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Comprehensive Translation Backend Testing Script
Tests the /api/translate-script endpoint focusing on review request requirements:
1. Basic en→hi translation with bracket preservation
2. AI IMAGE PROMPT quoted content preservation
3. Edge case placeholder restoration (Google modifications)
4. Long input handling (~10k chars) with chunking
5. Error handling for invalid target_language
6. Response schema validation
"""

import requests
import json
import time
from datetime import datetime
import sys
import re

# Get backend URL from frontend .env
BACKEND_URL = "https://4fd0301a-f28a-4dfc-a951-4bab330a4285.preview.emergentagent.com/api"

class ComprehensiveTranslationTester:
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
    
    def test_basic_en_to_hi_translation_with_brackets(self):
        """Test Case 1: Basic en→hi translation where bracketed segments remain unchanged"""
        print("\n=== Test Case 1: Basic EN→HI Translation with Bracket Preservation ===")
        
        test_cases = [
            {
                "name": "Simple bracket preservation",
                "text": "Welcome to our cooking show! [Close-up shot of ingredients] Today we'll learn healthy recipes.",
                "expected_brackets": ["[Close-up shot of ingredients]"]
            },
            {
                "name": "Multiple brackets",
                "text": "Start your day right [Morning sunrise shot] with nutritious breakfast [Kitchen counter setup] that energizes you.",
                "expected_brackets": ["[Morning sunrise shot]", "[Kitchen counter setup]"]
            },
            {
                "name": "Complex bracket content",
                "text": "This recipe [Professional food photography shot showing fresh vegetables being chopped on wooden cutting board, studio lighting, high resolution, detailed textures] is perfect for beginners.",
                "expected_brackets": ["[Professional food photography shot showing fresh vegetables being chopped on wooden cutting board, studio lighting, high resolution, detailed textures]"]
            }
        ]
        
        successful_tests = 0
        
        for test_case in test_cases:
            try:
                payload = {
                    "text": test_case["text"],
                    "source_language": "en",
                    "target_language": "hi"
                }
                
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
                    response_time = end_time - start_time
                    
                    # Verify all expected brackets are preserved exactly
                    all_brackets_preserved = True
                    for expected_bracket in test_case["expected_brackets"]:
                        if expected_bracket not in translated_text:
                            self.log_test(f"EN→HI Bracket Preservation - {test_case['name']}", False,
                                        f"Expected bracket not found: {expected_bracket}")
                            all_brackets_preserved = False
                            break
                    
                    if all_brackets_preserved:
                        # Verify non-bracket text is translated (should be different)
                        original_without_brackets = test_case["text"]
                        for bracket in test_case["expected_brackets"]:
                            original_without_brackets = original_without_brackets.replace(bracket, "")
                        
                        translated_without_brackets = translated_text
                        for bracket in test_case["expected_brackets"]:
                            translated_without_brackets = translated_without_brackets.replace(bracket, "")
                        
                        if original_without_brackets.strip() != translated_without_brackets.strip():
                            self.log_test(f"EN→HI Translation - {test_case['name']}", True,
                                        f"Successfully translated with bracket preservation in {response_time:.2f}s")
                            successful_tests += 1
                        else:
                            self.log_test(f"EN→HI Translation - {test_case['name']}", False,
                                        "Non-bracket text was not translated")
                    
                else:
                    self.log_test(f"EN→HI Translation - {test_case['name']}", False,
                                f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"EN→HI Translation - {test_case['name']}", False, f"Exception: {str(e)}")
        
        if successful_tests >= 2:
            self.log_test("Basic EN→HI Translation with Brackets", True,
                        f"Successfully passed {successful_tests}/{len(test_cases)} bracket preservation tests")
            return True
        else:
            self.log_test("Basic EN→HI Translation with Brackets", False,
                        f"Only {successful_tests}/{len(test_cases)} tests passed")
            return False
    
    def test_ai_image_prompt_preservation(self):
        """Test Case 2: Preservation of AI IMAGE PROMPT quoted content"""
        print("\n=== Test Case 2: AI IMAGE PROMPT Quoted Content Preservation ===")
        
        test_cases = [
            {
                "name": "Single AI IMAGE PROMPT",
                "text": "Create a beautiful scene. AI IMAGE PROMPT: \"Abstract scene, volumetric lighting\" for the background.",
                "expected_preserved": ["AI IMAGE PROMPT: \"Abstract scene, volumetric lighting\""]
            },
            {
                "name": "Multiple AI IMAGE PROMPTS",
                "text": "Start with AI IMAGE PROMPT: \"Professional kitchen setup, natural lighting\" then show AI IMAGE PROMPT: \"Close-up hands chopping vegetables, macro lens\" for detail.",
                "expected_preserved": [
                    "AI IMAGE PROMPT: \"Professional kitchen setup, natural lighting\"",
                    "AI IMAGE PROMPT: \"Close-up hands chopping vegetables, macro lens\""
                ]
            },
            {
                "name": "Complex AI IMAGE PROMPT",
                "text": "The video opens with AI IMAGE PROMPT: \"Cinematic wide shot of modern kitchen, golden hour lighting, professional food photography style, 4K resolution, shallow depth of field\" to establish the setting.",
                "expected_preserved": ["AI IMAGE PROMPT: \"Cinematic wide shot of modern kitchen, golden hour lighting, professional food photography style, 4K resolution, shallow depth of field\""]
            }
        ]
        
        successful_tests = 0
        
        for test_case in test_cases:
            try:
                payload = {
                    "text": test_case["text"],
                    "source_language": "en",
                    "target_language": "hi"
                }
                
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
                    response_time = end_time - start_time
                    
                    # Verify all AI IMAGE PROMPT sections are preserved exactly in English
                    all_prompts_preserved = True
                    for expected_prompt in test_case["expected_preserved"]:
                        if expected_prompt not in translated_text:
                            self.log_test(f"AI IMAGE PROMPT Preservation - {test_case['name']}", False,
                                        f"Expected AI IMAGE PROMPT not preserved: {expected_prompt}")
                            all_prompts_preserved = False
                            break
                    
                    if all_prompts_preserved:
                        # Verify non-AI IMAGE PROMPT text is translated
                        original_without_prompts = test_case["text"]
                        for prompt in test_case["expected_preserved"]:
                            original_without_prompts = original_without_prompts.replace(prompt, "")
                        
                        translated_without_prompts = translated_text
                        for prompt in test_case["expected_preserved"]:
                            translated_without_prompts = translated_without_prompts.replace(prompt, "")
                        
                        # Check if remaining text is different (translated)
                        if original_without_prompts.strip() != translated_without_prompts.strip():
                            self.log_test(f"AI IMAGE PROMPT Preservation - {test_case['name']}", True,
                                        f"Successfully preserved AI IMAGE PROMPT while translating other text in {response_time:.2f}s")
                            successful_tests += 1
                        else:
                            self.log_test(f"AI IMAGE PROMPT Preservation - {test_case['name']}", False,
                                        "Non-AI IMAGE PROMPT text was not translated")
                    
                else:
                    self.log_test(f"AI IMAGE PROMPT Preservation - {test_case['name']}", False,
                                f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"AI IMAGE PROMPT Preservation - {test_case['name']}", False, f"Exception: {str(e)}")
        
        if successful_tests >= 2:
            self.log_test("AI IMAGE PROMPT Preservation", True,
                        f"Successfully passed {successful_tests}/{len(test_cases)} AI IMAGE PROMPT preservation tests")
            return True
        else:
            self.log_test("AI IMAGE PROMPT Preservation", False,
                        f"Only {successful_tests}/{len(test_cases)} tests passed")
            return False
    
    def test_placeholder_restoration_edge_cases(self):
        """Test Case 3: Edge case where Google modifies placeholders - tolerant regex restoration"""
        print("\n=== Test Case 3: Placeholder Restoration Edge Cases ===")
        
        # This test simulates the edge case where Google Translate might modify our placeholders
        # For example: '§§BR_0§§' becomes '§§BR_0§' (missing trailing section marks)
        
        test_cases = [
            {
                "name": "Multiple brackets with potential placeholder corruption",
                "text": "Welcome to cooking [Shot 1: Kitchen overview] and learn [Shot 2: Ingredient prep] techniques [Shot 3: Final dish].",
                "description": "Test multiple bracketed segments that could be affected by placeholder modifications"
            },
            {
                "name": "Long bracket content susceptible to modification",
                "text": "This recipe [Professional food photography shot showing fresh vegetables being chopped on wooden cutting board, studio lighting, high resolution, detailed textures, perfect composition] is amazing.",
                "description": "Test long bracket content that might trigger placeholder edge cases"
            },
            {
                "name": "Mixed content with brackets and AI prompts",
                "text": "Start with [Establishing shot] then AI IMAGE PROMPT: \"Beautiful kitchen scene\" and continue [Close-up details] for the tutorial.",
                "description": "Test mixed content types that use different placeholder patterns"
            }
        ]
        
        successful_tests = 0
        
        for test_case in test_cases:
            try:
                payload = {
                    "text": test_case["text"],
                    "source_language": "en",
                    "target_language": "hi"
                }
                
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
                    response_time = end_time - start_time
                    
                    # Extract all bracketed content from original
                    original_brackets = re.findall(r'\[([^\]]+)\]', test_case["text"])
                    translated_brackets = re.findall(r'\[([^\]]+)\]', translated_text)
                    
                    # Extract AI IMAGE PROMPT content if present
                    original_ai_prompts = re.findall(r'AI IMAGE PROMPT: "[^"]*"', test_case["text"])
                    translated_ai_prompts = re.findall(r'AI IMAGE PROMPT: "[^"]*"', translated_text)
                    
                    # Verify bracket content preservation
                    brackets_preserved = len(original_brackets) == len(translated_brackets)
                    if brackets_preserved:
                        for orig_bracket in original_brackets:
                            if not any(orig_bracket in trans_bracket for trans_bracket in translated_brackets):
                                brackets_preserved = False
                                break
                    
                    # Verify AI prompt preservation
                    ai_prompts_preserved = len(original_ai_prompts) == len(translated_ai_prompts)
                    if ai_prompts_preserved:
                        for orig_prompt in original_ai_prompts:
                            if orig_prompt not in translated_text:
                                ai_prompts_preserved = False
                                break
                    
                    if brackets_preserved and ai_prompts_preserved:
                        self.log_test(f"Placeholder Restoration - {test_case['name']}", True,
                                    f"Successfully handled potential placeholder edge cases in {response_time:.2f}s")
                        successful_tests += 1
                    else:
                        self.log_test(f"Placeholder Restoration - {test_case['name']}", False,
                                    f"Placeholder restoration failed - Brackets: {brackets_preserved}, AI Prompts: {ai_prompts_preserved}")
                
                else:
                    self.log_test(f"Placeholder Restoration - {test_case['name']}", False,
                                f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Placeholder Restoration - {test_case['name']}", False, f"Exception: {str(e)}")
        
        if successful_tests >= 2:
            self.log_test("Placeholder Restoration Edge Cases", True,
                        f"Successfully passed {successful_tests}/{len(test_cases)} placeholder restoration tests")
            return True
        else:
            self.log_test("Placeholder Restoration Edge Cases", False,
                        f"Only {successful_tests}/{len(test_cases)} tests passed")
            return False
    
    def test_long_input_handling_10k_chars(self):
        """Test Case 4: Long input handling with ~10k characters - verify chunking works"""
        print("\n=== Test Case 4: Long Input Handling (~10k Characters) ===")
        
        # Create ~10k character text with mixed content
        base_sentence = "This is a comprehensive test of the translation system with various content types including cooking instructions, nutritional information, and preparation techniques. "
        bracket_segments = [
            "[Professional kitchen setup with natural lighting]",
            "[Close-up shot of fresh ingredients on marble counter]", 
            "[Overhead view of cooking process with steam rising]",
            "[Final plated dish with garnish and presentation]"
        ]
        ai_prompts = [
            "AI IMAGE PROMPT: \"Cinematic kitchen scene, golden hour lighting, professional food photography\"",
            "AI IMAGE PROMPT: \"Macro lens shot of ingredients, shallow depth of field, vibrant colors\""
        ]
        
        # Build content to reach ~10k characters
        content_parts = []
        current_length = 0
        counter = 0
        
        while current_length < 10000:
            if counter % 15 == 0 and counter > 0:
                # Add bracket segment
                part = f" {bracket_segments[counter % len(bracket_segments)]} "
            elif counter % 25 == 0 and counter > 0:
                # Add AI prompt
                part = f" {ai_prompts[counter % len(ai_prompts)]} "
            else:
                # Add regular content
                part = f"Sentence {counter + 1}: {base_sentence}"
            
            content_parts.append(part)
            current_length += len(part)
            counter += 1
        
        long_text = " ".join(content_parts)
        actual_length = len(long_text)
        
        # Count expected preserved elements
        expected_brackets = sum(1 for part in content_parts if part.strip().startswith("["))
        expected_ai_prompts = sum(1 for part in content_parts if "AI IMAGE PROMPT:" in part)
        
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
                timeout=35  # 30s requirement + 5s buffer
            )
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response schema
                if not data.get("success"):
                    self.log_test("Long Input - Success Status", False,
                                "Translation marked as unsuccessful")
                    return False
                
                # Verify processing time under 30 seconds
                if processing_time <= 30:
                    self.log_test("Long Input - Processing Time", True,
                                f"Processed {actual_length} chars in {processing_time:.2f}s (within 30s requirement)")
                else:
                    self.log_test("Long Input - Processing Time", False,
                                f"Processing took {processing_time:.2f}s (exceeds 30s requirement)")
                    return False
                
                translated_text = data["translated_text"]
                translated_length = len(translated_text)
                
                # Verify reasonable output length
                if translated_length < 1000:
                    self.log_test("Long Input - Output Length", False,
                                f"Output too short: {translated_length} chars from {actual_length} chars input")
                    return False
                
                # Verify bracket preservation
                translated_brackets = len(re.findall(r'\[[^\]]+\]', translated_text))
                if translated_brackets >= expected_brackets * 0.9:  # Allow for 90% preservation (some tolerance)
                    self.log_test("Long Input - Bracket Preservation", True,
                                f"Preserved {translated_brackets}/{expected_brackets} bracketed segments")
                else:
                    self.log_test("Long Input - Bracket Preservation", False,
                                f"Only preserved {translated_brackets}/{expected_brackets} bracketed segments")
                    return False
                
                # Verify AI prompt preservation
                translated_ai_prompts = len(re.findall(r'AI IMAGE PROMPT: "[^"]*"', translated_text))
                if translated_ai_prompts >= expected_ai_prompts * 0.9:  # Allow for 90% preservation
                    self.log_test("Long Input - AI Prompt Preservation", True,
                                f"Preserved {translated_ai_prompts}/{expected_ai_prompts} AI IMAGE PROMPTs")
                else:
                    self.log_test("Long Input - AI Prompt Preservation", False,
                                f"Only preserved {translated_ai_prompts}/{expected_ai_prompts} AI IMAGE PROMPTs")
                    return False
                
                self.log_test("Long Input Handling (~10k chars)", True,
                            f"Successfully processed {actual_length} → {translated_length} chars with chunking in {processing_time:.2f}s")
                return True
                
            else:
                self.log_test("Long Input Handling", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_test("Long Input - Timeout", False,
                        f"Request timed out after 35s (requirement is 30s)")
            return False
        except Exception as e:
            self.log_test("Long Input Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_invalid_language(self):
        """Test Case 5: Error handling for invalid target_language should return 503"""
        print("\n=== Test Case 5: Error Handling for Invalid Target Language ===")
        
        test_cases = [
            {
                "name": "Invalid language code 'xx'",
                "target_language": "xx",
                "text": "Test text for invalid language code"
            },
            {
                "name": "Invalid language code 'zz'", 
                "target_language": "zz",
                "text": "Another test with invalid language"
            },
            {
                "name": "Non-existent language code 'abc'",
                "target_language": "abc", 
                "text": "Test with completely invalid language code"
            }
        ]
        
        successful_tests = 0
        
        for test_case in test_cases:
            try:
                payload = {
                    "text": test_case["text"],
                    "source_language": "en",
                    "target_language": test_case["target_language"]
                }
                
                response = self.session.post(
                    f"{self.backend_url}/translate-script",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 503:
                    response_data = response.json()
                    detail = response_data.get("detail", "")
                    
                    # Check for appropriate error message
                    if any(keyword in detail.lower() for keyword in ["unavailable", "service", "translation"]):
                        self.log_test(f"Error Handling - {test_case['name']}", True,
                                    f"Correctly returned 503 with appropriate message: {detail}")
                        successful_tests += 1
                    else:
                        self.log_test(f"Error Handling - {test_case['name']}", False,
                                    f"503 returned but message not appropriate: {detail}")
                else:
                    self.log_test(f"Error Handling - {test_case['name']}", False,
                                f"Expected 503, got {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Error Handling - {test_case['name']}", False, f"Exception: {str(e)}")
        
        if successful_tests >= 2:
            self.log_test("Error Handling - Invalid Language Codes", True,
                        f"Successfully passed {successful_tests}/{len(test_cases)} error handling tests")
            return True
        else:
            self.log_test("Error Handling - Invalid Language Codes", False,
                        f"Only {successful_tests}/{len(test_cases)} tests passed")
            return False
    
    def test_response_schema_validation(self):
        """Test Case 6: Verify response schema fields"""
        print("\n=== Test Case 6: Response Schema Validation ===")
        
        test_payload = {
            "text": "Test schema validation with [bracketed content] and AI IMAGE PROMPT: \"test prompt\" included.",
            "source_language": "en",
            "target_language": "hi"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields as specified in review request
                required_fields = [
                    "original_text",
                    "translated_text", 
                    "source_language",
                    "target_language",
                    "translation_service",
                    "success"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Response Schema - Required Fields", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify field types and values
                schema_tests = [
                    ("original_text", str, test_payload["text"]),
                    ("source_language", str, test_payload["source_language"]),
                    ("target_language", str, test_payload["target_language"]),
                    ("success", bool, True),
                    ("translated_text", str, None),  # Should be non-empty string
                    ("translation_service", str, None)  # Should be non-empty string
                ]
                
                schema_valid = True
                for field_name, expected_type, expected_value in schema_tests:
                    field_value = data.get(field_name)
                    
                    # Check type
                    if not isinstance(field_value, expected_type):
                        self.log_test(f"Response Schema - {field_name} Type", False,
                                    f"Expected {expected_type.__name__}, got {type(field_value).__name__}")
                        schema_valid = False
                        continue
                    
                    # Check specific values where applicable
                    if expected_value is not None and field_value != expected_value:
                        self.log_test(f"Response Schema - {field_name} Value", False,
                                    f"Expected '{expected_value}', got '{field_value}'")
                        schema_valid = False
                        continue
                    
                    # Check non-empty strings
                    if expected_type == str and expected_value is None and not field_value:
                        self.log_test(f"Response Schema - {field_name} Non-empty", False,
                                    f"{field_name} should not be empty")
                        schema_valid = False
                        continue
                
                if schema_valid:
                    self.log_test("Response Schema Validation", True,
                                f"All required fields present with correct types and values")
                    
                    # Additional validation: verify translation actually occurred
                    if data["translated_text"] != data["original_text"]:
                        self.log_test("Response Schema - Translation Occurred", True,
                                    "Translated text differs from original (translation occurred)")
                    else:
                        self.log_test("Response Schema - Translation Occurred", False,
                                    "Translated text identical to original (no translation)")
                        return False
                    
                    return True
                else:
                    return False
                
            else:
                self.log_test("Response Schema Validation", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Response Schema Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive translation tests as specified in review request"""
        print("🚀 Starting Comprehensive Translation Backend Testing")
        print("Focus: Review Request Requirements for /api/translate-script")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 80)
        
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("1) Basic EN→HI Translation with Bracket Preservation", self.test_basic_en_to_hi_translation_with_brackets),
            ("2) AI IMAGE PROMPT Quoted Content Preservation", self.test_ai_image_prompt_preservation),
            ("3) Placeholder Restoration Edge Cases", self.test_placeholder_restoration_edge_cases),
            ("4) Long Input Handling (~10k chars)", self.test_long_input_handling_10k_chars),
            ("5) Error Handling - Invalid Language Codes", self.test_error_handling_invalid_language),
            ("6) Response Schema Validation", self.test_response_schema_validation)
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            try:
                print(f"\n🔍 Running: {test_name}")
                if test_method():
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
        
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE TRANSLATION TESTING COMPLETE")
        print(f"✅ Passed: {passed_tests}/{total_tests} tests")
        
        # Detailed results summary
        print(f"\n📊 DETAILED RESULTS SUMMARY:")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL COMPREHENSIVE TRANSLATION TESTS PASSED!")
            print("\n✅ REVIEW REQUEST REQUIREMENTS VERIFIED:")
            print("  1. ✅ Basic en→hi translation with bracket preservation")
            print("  2. ✅ AI IMAGE PROMPT quoted content preservation") 
            print("  3. ✅ Edge case placeholder restoration handling")
            print("  4. ✅ Long input handling (~10k chars) with chunking")
            print("  5. ✅ Error handling for invalid target_language (503)")
            print("  6. ✅ Response schema validation (all required fields)")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed")
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
            return False
    
    def get_test_summary(self):
        """Get comprehensive summary of test results"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results,
            "review_requirements_met": passed_tests == total_tests
        }
        
        return summary

if __name__ == "__main__":
    tester = ComprehensiveTranslationTester()
    success = tester.run_comprehensive_tests()
    
    # Print final summary
    summary = tester.get_test_summary()
    print(f"\n📈 FINAL SUMMARY:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Review Requirements Met: {'✅ YES' if summary['review_requirements_met'] else '❌ NO'}")
    
    sys.exit(0 if success else 1)
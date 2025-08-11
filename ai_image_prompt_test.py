#!/usr/bin/env python3
"""
AI IMAGE PROMPT Preservation Testing Script
Focused testing for the critical AI IMAGE PROMPT preservation issue in /api/translate-script endpoint
"""

import requests
import json
import time
from datetime import datetime
import sys
import re

# Get backend URL from frontend .env
BACKEND_URL = "https://6b14fb28-7a71-4ce9-9040-059c518ea0a8.preview.emergentagent.com/api"

class AIImagePromptTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.failed_tests = 0
        self.passed_tests = 0
        
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
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
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
            self.log_test("Basic Connectivity", False, f"Connection error: {str(e)}")
            return False

    def test_ai_image_prompt_preservation_simple(self):
        """Test AI IMAGE PROMPT preservation with simple cases"""
        test_cases = [
            {
                "name": "Double Quotes Format",
                "input": 'AI IMAGE PROMPT: "Abstract scene, volumetric lighting"',
                "expected_preserved": 'AI IMAGE PROMPT: "Abstract scene, volumetric lighting"'
            },
            {
                "name": "Single Quotes Format", 
                "input": "AI IMAGE PROMPT: 'Professional photography setup'",
                "expected_preserved": "AI IMAGE PROMPT: 'Professional photography setup'"
            },
            {
                "name": "Lowercase Format",
                "input": 'ai image prompt: "Modern minimalist design"',
                "expected_preserved": 'ai image prompt: "Modern minimalist design"'
            }
        ]
        
        for case in test_cases:
            try:
                # Test translation from English to Hindi
                payload = {
                    "script_content": case["input"],
                    "target_language": "hindi"
                }
                
                response = self.session.post(
                    f"{self.backend_url}/translate-script",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    translated_content = data.get("translated_script", "")
                    
                    # Check if AI IMAGE PROMPT is preserved exactly
                    if case["expected_preserved"] in translated_content:
                        self.log_test(
                            f"AI IMAGE PROMPT Preservation - {case['name']}", 
                            True, 
                            "AI IMAGE PROMPT preserved correctly in English"
                        )
                    else:
                        self.log_test(
                            f"AI IMAGE PROMPT Preservation - {case['name']}", 
                            False, 
                            "AI IMAGE PROMPT not preserved correctly",
                            {
                                "input": case["input"],
                                "expected": case["expected_preserved"],
                                "actual_output": translated_content,
                                "found_ai_prompts": self.extract_ai_image_prompts(translated_content)
                            }
                        )
                else:
                    self.log_test(
                        f"AI IMAGE PROMPT Preservation - {case['name']}", 
                        False, 
                        f"API error: HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test(
                    f"AI IMAGE PROMPT Preservation - {case['name']}", 
                    False, 
                    f"Test error: {str(e)}"
                )

    def test_ai_image_prompt_in_full_script(self):
        """Test AI IMAGE PROMPT preservation in full script content"""
        full_script = """This is a video script about cooking. 

AI IMAGE PROMPT: "Professional kitchen setup with modern appliances, bright lighting, high resolution"

Welcome to today's cooking lesson. Let's learn how to make healthy meals.

AI IMAGE PROMPT: "Close-up shot of fresh vegetables on wooden cutting board, natural lighting"

First, we'll prepare the ingredients carefully."""

        try:
            payload = {
                "script_content": full_script,
                "target_language": "hindi"
            }
            
            response = self.session.post(
                f"{self.backend_url}/translate-script",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                translated_content = data.get("translated_script", "")
                
                # Extract AI IMAGE PROMPTS from original and translated
                original_prompts = self.extract_ai_image_prompts(full_script)
                translated_prompts = self.extract_ai_image_prompts(translated_content)
                
                print(f"\n🔍 DEBUGGING AI IMAGE PROMPT PRESERVATION:")
                print(f"Original AI IMAGE PROMPTS found: {len(original_prompts)}")
                for i, prompt in enumerate(original_prompts):
                    print(f"  {i+1}. {prompt}")
                
                print(f"Translated AI IMAGE PROMPTS found: {len(translated_prompts)}")
                for i, prompt in enumerate(translated_prompts):
                    print(f"  {i+1}. {prompt}")
                
                # Check if all original prompts are preserved
                all_preserved = True
                missing_prompts = []
                
                for original_prompt in original_prompts:
                    if original_prompt not in translated_content:
                        all_preserved = False
                        missing_prompts.append(original_prompt)
                
                if all_preserved and len(original_prompts) == len(translated_prompts):
                    self.log_test(
                        "Full Script AI IMAGE PROMPT Preservation", 
                        True, 
                        f"All {len(original_prompts)} AI IMAGE PROMPTS preserved correctly"
                    )
                else:
                    self.log_test(
                        "Full Script AI IMAGE PROMPT Preservation", 
                        False, 
                        f"AI IMAGE PROMPT preservation failed",
                        {
                            "original_prompts_count": len(original_prompts),
                            "translated_prompts_count": len(translated_prompts),
                            "missing_prompts": missing_prompts,
                            "original_script": full_script,
                            "translated_script": translated_content
                        }
                    )
                
                # Additional check: Verify script text is translated but prompts are not
                self.verify_translation_vs_preservation(full_script, translated_content)
                
            else:
                self.log_test(
                    "Full Script AI IMAGE PROMPT Preservation", 
                    False, 
                    f"API error: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Full Script AI IMAGE PROMPT Preservation", 
                False, 
                f"Test error: {str(e)}"
            )

    def extract_ai_image_prompts(self, text):
        """Extract AI IMAGE PROMPT patterns from text"""
        # Multiple regex patterns to catch different formats
        patterns = [
            r'AI\s+IMAGE\s+PROMPT\s*:\s*"[^"]*"',  # Double quotes
            r"AI\s+IMAGE\s+PROMPT\s*:\s*'[^']*'",  # Single quotes
            r'ai\s+image\s+prompt\s*:\s*"[^"]*"',  # Lowercase double quotes
            r"ai\s+image\s+prompt\s*:\s*'[^']*'",  # Lowercase single quotes
        ]
        
        found_prompts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_prompts.extend(matches)
        
        return found_prompts

    def verify_translation_vs_preservation(self, original, translated):
        """Verify that script text is translated but AI IMAGE PROMPTS are preserved"""
        # Extract non-AI-IMAGE-PROMPT text from both
        original_text_only = self.remove_ai_image_prompts(original)
        translated_text_only = self.remove_ai_image_prompts(translated)
        
        # Check if the non-prompt text appears to be translated (different from original)
        text_appears_translated = original_text_only.strip() != translated_text_only.strip()
        
        if text_appears_translated:
            self.log_test(
                "Script Text Translation Verification", 
                True, 
                "Script text appears to be translated while AI IMAGE PROMPTS preserved"
            )
        else:
            self.log_test(
                "Script Text Translation Verification", 
                False, 
                "Script text does not appear to be translated",
                {
                    "original_text_only": original_text_only,
                    "translated_text_only": translated_text_only
                }
            )

    def remove_ai_image_prompts(self, text):
        """Remove AI IMAGE PROMPT patterns from text to isolate script content"""
        patterns = [
            r'AI\s+IMAGE\s+PROMPT\s*:\s*"[^"]*"',
            r"AI\s+IMAGE\s+PROMPT\s*:\s*'[^']*'",
            r'ai\s+image\s+prompt\s*:\s*"[^"]*"',
            r"ai\s+image\s+prompt\s*:\s*'[^']*'",
        ]
        
        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        return cleaned_text

    def test_regex_pattern_debugging(self):
        """Debug the specific regex pattern used in the backend"""
        # This is the regex pattern mentioned in the review request
        backend_regex = r"(AI\s+IMAGE\s+PROMPT\s*:?\s*)([\"'])([^\"']+)([\"'])"
        
        test_strings = [
            'AI IMAGE PROMPT: "Professional kitchen setup with modern appliances, bright lighting, high resolution"',
            "AI IMAGE PROMPT: 'Close-up shot of fresh vegetables on wooden cutting board, natural lighting'",
            'ai image prompt: "Modern minimalist design"'
        ]
        
        print(f"\n🔧 DEBUGGING REGEX PATTERN: {backend_regex}")
        
        for i, test_string in enumerate(test_strings):
            matches = re.findall(backend_regex, test_string, re.IGNORECASE)
            print(f"\nTest String {i+1}: {test_string}")
            print(f"Matches found: {len(matches)}")
            
            if matches:
                for j, match in enumerate(matches):
                    print(f"  Match {j+1}: {match}")
                    # Reconstruct the full match
                    reconstructed = f"{match[0]}{match[1]}{match[2]}{match[3]}"
                    print(f"  Reconstructed: {reconstructed}")
                    
                    # Test if reconstruction matches original
                    if reconstructed in test_string:
                        print(f"  ✅ Reconstruction matches original")
                    else:
                        print(f"  ❌ Reconstruction does NOT match original")
            else:
                print(f"  ❌ No matches found")

    def run_comprehensive_ai_image_prompt_tests(self):
        """Run all AI IMAGE PROMPT preservation tests"""
        print("🚀 STARTING COMPREHENSIVE AI IMAGE PROMPT PRESERVATION TESTING")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Cannot proceed - backend not accessible")
            return False
        
        print("\n📋 TESTING AI IMAGE PROMPT PRESERVATION...")
        
        # Test simple cases
        self.test_ai_image_prompt_preservation_simple()
        
        # Test full script
        self.test_ai_image_prompt_in_full_script()
        
        # Debug regex pattern
        self.test_regex_pattern_debugging()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 AI IMAGE PROMPT PRESERVATION TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.passed_tests}")
        print(f"❌ Tests Failed: {self.failed_tests}")
        print(f"📊 Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n🚨 CRITICAL ISSUE IDENTIFIED:")
            print(f"AI IMAGE PROMPT preservation is failing in {self.failed_tests} test cases")
            print(f"This confirms the issue reported in test_result.md")
            
            # Provide specific debugging information
            print(f"\n🔍 DEBUGGING RECOMMENDATIONS:")
            print(f"1. Check the regex pattern: r\"(AI\\s+IMAGE\\s+PROMPT\\s*:?\\s*)([\\\"'])([^\\\"']+)([\\\"'])\"")
            print(f"2. Verify the masking with §§IP_i§§ tokens is working correctly")
            print(f"3. Verify the restoration process after translation")
            print(f"4. Check if Google Translator is truncating or modifying the masked tokens")
            
        return self.failed_tests == 0

def main():
    """Main test execution"""
    tester = AIImagePromptTester()
    success = tester.run_comprehensive_ai_image_prompt_tests()
    
    if success:
        print("\n🎉 ALL AI IMAGE PROMPT PRESERVATION TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n💥 AI IMAGE PROMPT PRESERVATION TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Backend Testing Script for Script Generation App
Tests all backend API endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://76a6bebc-4978-414e-97cc-2bdf67dbe8d2.preview.emergentagent.com/api"

class ScriptGenerationTester:
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
    
    def test_enhance_prompt_endpoint(self):
        """Test the /api/enhance-prompt endpoint"""
        print("\n=== Testing Prompt Enhancement Endpoint ===")
        
        # Test Case 1: Basic motivational video prompt
        test_prompt = "motivational video about success"
        payload = {
            "original_prompt": test_prompt,
            "video_type": "general"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["original_prompt", "enhanced_prompt", "enhancement_explanation"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhance Prompt - Structure", False, 
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify content quality
                original = data["original_prompt"]
                enhanced = data["enhanced_prompt"]
                explanation = data["enhancement_explanation"]
                
                if len(enhanced) <= len(original):
                    self.log_test("Enhance Prompt - Enhancement Quality", False,
                                "Enhanced prompt is not longer/more detailed than original",
                                {"original_length": len(original), "enhanced_length": len(enhanced)})
                    return False
                
                if not explanation or len(explanation) < 20:
                    self.log_test("Enhance Prompt - Explanation Quality", False,
                                "Enhancement explanation is too short or missing",
                                {"explanation_length": len(explanation)})
                    return False
                
                self.log_test("Enhance Prompt - Basic Functionality", True,
                            f"Successfully enhanced prompt from {len(original)} to {len(enhanced)} characters")
                
                # Test Case 2: Different video types
                video_types = ["educational", "entertainment", "marketing"]
                for video_type in video_types:
                    test_payload = {
                        "original_prompt": "create engaging content about technology",
                        "video_type": video_type
                    }
                    
                    type_response = self.session.post(
                        f"{self.backend_url}/enhance-prompt",
                        json=test_payload,
                        timeout=30
                    )
                    
                    if type_response.status_code == 200:
                        self.log_test(f"Enhance Prompt - {video_type.title()} Type", True,
                                    f"Successfully processed {video_type} video type")
                    else:
                        self.log_test(f"Enhance Prompt - {video_type.title()} Type", False,
                                    f"Failed for {video_type}: {type_response.status_code}")
                
                return True
                
            else:
                self.log_test("Enhance Prompt - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhance Prompt - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_generate_script_endpoint(self):
        """Test the /api/generate-script endpoint"""
        print("\n=== Testing Script Generation Endpoint ===")
        
        # Test Case 1: Basic script generation
        test_prompt = "Create a motivational video about overcoming challenges and achieving success"
        payload = {
            "prompt": test_prompt,
            "video_type": "general",
            "duration": "short"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Generate Script - Structure", False,
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify content quality
                script = data["generated_script"]
                if len(script) < 100:
                    self.log_test("Generate Script - Content Length", False,
                                "Generated script is too short", {"script_length": len(script)})
                    return False
                
                # Check for storytelling elements
                storytelling_indicators = [
                    "[", "]",  # Scene descriptions
                    "(", ")",  # Speaker directions
                ]
                
                has_formatting = any(indicator in script for indicator in storytelling_indicators)
                if not has_formatting:
                    self.log_test("Generate Script - Formatting", False,
                                "Script lacks proper formatting (scene descriptions, speaker directions)")
                else:
                    self.log_test("Generate Script - Formatting", True,
                                "Script includes proper formatting elements")
                
                self.log_test("Generate Script - Basic Functionality", True,
                            f"Successfully generated {len(script)} character script")
                
                # Test Case 2: Different video types and durations
                test_combinations = [
                    {"video_type": "educational", "duration": "medium"},
                    {"video_type": "entertainment", "duration": "long"},
                    {"video_type": "marketing", "duration": "short"}
                ]
                
                for combo in test_combinations:
                    test_payload = {
                        "prompt": "Create engaging content about innovation",
                        **combo
                    }
                    
                    combo_response = self.session.post(
                        f"{self.backend_url}/generate-script",
                        json=test_payload,
                        timeout=45
                    )
                    
                    if combo_response.status_code == 200:
                        combo_data = combo_response.json()
                        self.log_test(f"Generate Script - {combo['video_type']}/{combo['duration']}", True,
                                    f"Successfully generated script for {combo['video_type']} {combo['duration']} video")
                    else:
                        self.log_test(f"Generate Script - {combo['video_type']}/{combo['duration']}", False,
                                    f"Failed: {combo_response.status_code}")
                
                return True
                
            else:
                self.log_test("Generate Script - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Script - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_scripts_retrieval_endpoint(self):
        """Test the /api/scripts endpoint"""
        print("\n=== Testing Scripts Retrieval Endpoint ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Scripts Retrieval - Data Type", False,
                                "Response is not a list", {"response_type": type(data).__name__})
                    return False
                
                if len(data) == 0:
                    self.log_test("Scripts Retrieval - Empty List", True,
                                "No scripts found (expected if no scripts generated yet)")
                    return True
                
                # Verify script structure
                first_script = data[0]
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in first_script]
                
                if missing_fields:
                    self.log_test("Scripts Retrieval - Script Structure", False,
                                f"Missing fields in script: {missing_fields}")
                    return False
                
                # Check chronological order (newest first)
                if len(data) > 1:
                    timestamps = [script["created_at"] for script in data]
                    is_sorted = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
                    
                    if is_sorted:
                        self.log_test("Scripts Retrieval - Chronological Order", True,
                                    "Scripts are properly sorted in reverse chronological order")
                    else:
                        self.log_test("Scripts Retrieval - Chronological Order", False,
                                    "Scripts are not sorted in reverse chronological order")
                
                self.log_test("Scripts Retrieval - Basic Functionality", True,
                            f"Successfully retrieved {len(data)} scripts")
                return True
                
            else:
                self.log_test("Scripts Retrieval - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Scripts Retrieval - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_integration_flow(self):
        """Test the complete integration flow"""
        print("\n=== Testing Integration Flow ===")
        
        try:
            # Step 1: Enhance a prompt
            original_prompt = "fitness motivation for beginners"
            enhance_payload = {
                "original_prompt": original_prompt,
                "video_type": "motivational"
            }
            
            enhance_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=enhance_payload,
                timeout=30
            )
            
            if enhance_response.status_code != 200:
                self.log_test("Integration Flow - Enhance Step", False,
                            f"Enhance prompt failed: {enhance_response.status_code}")
                return False
            
            enhanced_data = enhance_response.json()
            enhanced_prompt = enhanced_data["enhanced_prompt"]
            
            # Step 2: Generate script with enhanced prompt
            script_payload = {
                "prompt": enhanced_prompt,
                "video_type": "motivational",
                "duration": "medium"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Integration Flow - Script Generation Step", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            script_id = script_data["id"]
            
            # Step 3: Retrieve scripts and verify our script is there
            time.sleep(1)  # Brief pause to ensure database consistency
            
            retrieval_response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if retrieval_response.status_code != 200:
                self.log_test("Integration Flow - Retrieval Step", False,
                            f"Script retrieval failed: {retrieval_response.status_code}")
                return False
            
            scripts = retrieval_response.json()
            script_found = any(script["id"] == script_id for script in scripts)
            
            if not script_found:
                self.log_test("Integration Flow - Data Persistence", False,
                            "Generated script not found in retrieval results")
                return False
            
            self.log_test("Integration Flow - Complete", True,
                        "Successfully completed enhance → generate → retrieve flow")
            return True
            
        except Exception as e:
            self.log_test("Integration Flow - Exception", False, f"Integration test failed: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid enhance-prompt request
        try:
            invalid_enhance = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json={},  # Missing required fields
                timeout=10
            )
            
            if invalid_enhance.status_code == 422:  # Validation error expected
                self.log_test("Error Handling - Invalid Enhance Request", True,
                            "Properly handled invalid enhance-prompt request")
            else:
                self.log_test("Error Handling - Invalid Enhance Request", False,
                            f"Unexpected status code: {invalid_enhance.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Enhance Request", False, f"Exception: {str(e)}")
        
        # Test invalid generate-script request
        try:
            invalid_script = self.session.post(
                f"{self.backend_url}/generate-script",
                json={},  # Missing required fields
                timeout=10
            )
            
            if invalid_script.status_code == 422:  # Validation error expected
                self.log_test("Error Handling - Invalid Script Request", True,
                            "Properly handled invalid generate-script request")
            else:
                self.log_test("Error Handling - Invalid Script Request", False,
                            f"Unexpected status code: {invalid_script.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Script Request", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Testing for Script Generation App")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("\n❌ Basic connectivity failed. Stopping tests.")
            return False
        
        # Run all test suites
        test_methods = [
            self.test_enhance_prompt_endpoint,
            self.test_generate_script_endpoint,
            self.test_scripts_retrieval_endpoint,
            self.test_integration_flow,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test suite {test_method.__name__} failed with exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = ScriptGenerationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
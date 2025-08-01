#!/usr/bin/env python3
"""
Chain-of-Thought Script Generation Backend Testing
Tests the new /api/generate-script-cot endpoint specifically
"""

import requests
import json
import time
from datetime import datetime
import sys

# Use local backend URL for testing
BACKEND_URL = "http://localhost:8001/api"

class CoTScriptTester:
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
            self.log_test("Basic Connectivity", False, f"Connection error: {str(e)}")
            return False

    def test_cot_script_generation_basic(self):
        """Test Chain-of-Thought script generation with basic request"""
        try:
            # Test data from review request
            test_data = {
                "prompt": "Create a video about the benefits of morning exercise routines",
                "video_type": "educational", 
                "duration": "medium",
                "industry_focus": "health",
                "target_platform": "youtube",
                "include_reasoning_chain": True
            }
            
            print(f"Testing CoT endpoint with data: {json.dumps(test_data, indent=2)}")
            
            response = self.session.post(
                f"{self.backend_url}/generate-script-cot",
                json=test_data,
                timeout=120  # Extended timeout for complex AI processing
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("CoT Script Generation - Basic", True, 
                            f"Successfully generated CoT script (Response size: {len(str(data))} chars)")
                return data
            else:
                self.log_test("CoT Script Generation - Basic", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("CoT Script Generation - Basic", False, f"Request error: {str(e)}")
            return None

    def test_cot_response_structure(self, response_data):
        """Test that CoT response contains all expected fields"""
        if not response_data:
            self.log_test("CoT Response Structure", False, "No response data to validate")
            return False
            
        try:
            required_fields = [
                "generated_script",
                "reasoning_chain", 
                "final_analysis",
                "generation_metadata"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in response_data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("CoT Response Structure", False, 
                            f"Missing required fields: {missing_fields}")
                return False
            
            # Check that fields have content
            empty_fields = []
            for field in required_fields:
                if not response_data.get(field):
                    empty_fields.append(field)
            
            if empty_fields:
                self.log_test("CoT Response Structure", False, 
                            f"Empty required fields: {empty_fields}")
                return False
                
            self.log_test("CoT Response Structure", True, 
                        "All required fields present and populated")
            return True
            
        except Exception as e:
            self.log_test("CoT Response Structure", False, f"Structure validation error: {str(e)}")
            return False

    def test_reasoning_chain_structure(self, response_data):
        """Test that reasoning_chain contains the expected 6-step structure"""
        if not response_data or not response_data.get("reasoning_chain"):
            self.log_test("Reasoning Chain Structure", False, "No reasoning chain data to validate")
            return False
            
        try:
            reasoning_chain = response_data["reasoning_chain"]
            
            # Expected 6 steps from the review request
            expected_steps = [
                "step_1",  # Analysis and Understanding
                "step_2",  # Audience and Context Mapping
                "step_3",  # Narrative Architecture Design
                "step_4",  # Engagement Strategy Planning
                "step_5",  # Content Development
                "step_6"   # Quality Validation and Refinement
            ]
            
            missing_steps = []
            for step in expected_steps:
                if step not in reasoning_chain:
                    missing_steps.append(step)
            
            if missing_steps:
                self.log_test("Reasoning Chain Structure", False, 
                            f"Missing reasoning steps: {missing_steps}")
                return False
            
            # Verify step content
            empty_steps = []
            for step in expected_steps:
                step_data = reasoning_chain.get(step)
                if not step_data or (isinstance(step_data, dict) and not any(step_data.values())):
                    empty_steps.append(step)
            
            if empty_steps:
                self.log_test("Reasoning Chain Structure", False, 
                            f"Empty reasoning steps: {empty_steps}")
                return False
            
            self.log_test("Reasoning Chain Structure", True, 
                        f"All 6 reasoning steps present and populated ({len(reasoning_chain)} total steps)")
            
            # Log step details for verification
            for step in expected_steps:
                step_data = reasoning_chain.get(step)
                if isinstance(step_data, dict):
                    step_content_length = sum(len(str(v)) for v in step_data.values())
                else:
                    step_content_length = len(str(step_data))
                print(f"   {step}: {step_content_length} characters of reasoning content")
            
            return True
            
        except Exception as e:
            self.log_test("Reasoning Chain Structure", False, f"Reasoning chain validation error: {str(e)}")
            return False

    def test_script_quality(self, response_data):
        """Test that the generated script is sophisticated and detailed"""
        if not response_data or not response_data.get("generated_script"):
            self.log_test("Script Quality", False, "No generated script to validate")
            return False
            
        try:
            script = response_data["generated_script"]
            script_length = len(script)
            
            # Check minimum length for sophisticated content
            if script_length < 1000:
                self.log_test("Script Quality", False, 
                            f"Script too short for sophisticated content: {script_length} chars")
                return False
            
            # Check for script formatting elements
            formatting_elements = [
                "[",  # Scene descriptions
                "(",  # Speaker directions
                ":",  # Dialogue markers
                "\n"  # Proper line breaks
            ]
            
            missing_formatting = []
            for element in formatting_elements:
                if element not in script:
                    missing_formatting.append(element)
            
            if len(missing_formatting) > 2:  # Allow some flexibility
                self.log_test("Script Quality", False, 
                            f"Script lacks proper formatting elements: {missing_formatting}")
                return False
            
            self.log_test("Script Quality", True, 
                        f"Script is sophisticated and detailed ({script_length} characters)")
            return True
            
        except Exception as e:
            self.log_test("Script Quality", False, f"Script quality validation error: {str(e)}")
            return False

    def test_final_analysis_structure(self, response_data):
        """Test that final_analysis contains quality validation results"""
        if not response_data or not response_data.get("final_analysis"):
            self.log_test("Final Analysis Structure", False, "No final analysis data to validate")
            return False
            
        try:
            final_analysis = response_data["final_analysis"]
            
            # Expected analysis components
            expected_components = [
                "quality_scores",
                "improvements",
                "validation_score"
            ]
            
            present_components = []
            for component in expected_components:
                if component in final_analysis or any(component in str(k).lower() for k in final_analysis.keys()):
                    present_components.append(component)
            
            if len(present_components) < 2:  # At least 2 components should be present
                self.log_test("Final Analysis Structure", False, 
                            f"Final analysis lacks quality validation components. Found: {list(final_analysis.keys())}")
                return False
            
            self.log_test("Final Analysis Structure", True, 
                        f"Final analysis contains quality validation results ({len(final_analysis)} components)")
            return True
            
        except Exception as e:
            self.log_test("Final Analysis Structure", False, f"Final analysis validation error: {str(e)}")
            return False

    def test_generation_metadata(self, response_data):
        """Test that generation_metadata contains method info and timestamps"""
        if not response_data or not response_data.get("generation_metadata"):
            self.log_test("Generation Metadata", False, "No generation metadata to validate")
            return False
            
        try:
            metadata = response_data["generation_metadata"]
            
            # Check for method information
            method_indicators = ["method", "chain_of_thought", "cot", "reasoning", "generation"]
            has_method_info = any(indicator in str(metadata).lower() for indicator in method_indicators)
            
            if not has_method_info:
                self.log_test("Generation Metadata", False, 
                            "Metadata lacks method information")
                return False
            
            # Check for timestamp information
            timestamp_indicators = ["timestamp", "time", "created", "generated", "duration"]
            has_timestamp_info = any(indicator in str(metadata).lower() for indicator in timestamp_indicators)
            
            if not has_timestamp_info:
                self.log_test("Generation Metadata", False, 
                            "Metadata lacks timestamp information")
                return False
            
            self.log_test("Generation Metadata", True, 
                        f"Generation metadata contains method info and timestamps ({len(metadata)} fields)")
            return True
            
        except Exception as e:
            self.log_test("Generation Metadata", False, f"Metadata validation error: {str(e)}")
            return False

    def test_database_storage(self):
        """Test that CoT scripts are stored in database correctly"""
        try:
            # Get recent scripts to verify storage
            response = self.session.get(f"{self.backend_url}/scripts", timeout=30)
            
            if response.status_code == 200:
                scripts = response.json()
                
                # Look for CoT scripts in recent entries
                cot_scripts = []
                for script in scripts[:5]:  # Check last 5 scripts
                    if (script.get("generation_method") == "chain_of_thought" or 
                        "reasoning_chain" in script or
                        "cot" in str(script).lower()):
                        cot_scripts.append(script)
                
                if cot_scripts:
                    self.log_test("Database Storage", True, 
                                f"CoT scripts properly stored in database ({len(cot_scripts)} found)")
                    return True
                else:
                    self.log_test("Database Storage", False, 
                                "No CoT scripts found in recent database entries")
                    return False
            else:
                self.log_test("Database Storage", False, 
                            f"Could not retrieve scripts for verification: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Storage", False, f"Database verification error: {str(e)}")
            return False

    def test_cot_without_reasoning_chain(self):
        """Test CoT endpoint with include_reasoning_chain=False"""
        try:
            test_data = {
                "prompt": "Create a video about healthy morning habits",
                "video_type": "educational", 
                "duration": "short",
                "industry_focus": "health",
                "target_platform": "youtube",
                "include_reasoning_chain": False
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-script-cot",
                json=test_data,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Should still have script and analysis, but reasoning_chain should be None
                if (data.get("generated_script") and 
                    data.get("final_analysis") and 
                    data.get("reasoning_chain") is None):
                    self.log_test("CoT Without Reasoning Chain", True, 
                                "Successfully generated script without reasoning chain")
                    return True
                else:
                    self.log_test("CoT Without Reasoning Chain", False, 
                                f"Unexpected response structure: reasoning_chain={data.get('reasoning_chain')}")
                    return False
            else:
                self.log_test("CoT Without Reasoning Chain", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("CoT Without Reasoning Chain", False, f"Request error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Chain-of-Thought tests"""
        print("🚀 Starting Chain-of-Thought Script Generation Backend Tests")
        print("=" * 70)
        
        # Test 1: Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed - aborting tests")
            return self.generate_summary()
        
        # Test 2: CoT script generation
        print("\n📝 Testing Chain-of-Thought Script Generation...")
        cot_response = self.test_cot_script_generation_basic()
        
        if cot_response:
            # Test 3: Response structure
            print("\n🔍 Testing Response Structure...")
            self.test_cot_response_structure(cot_response)
            
            # Test 4: Reasoning chain structure
            print("\n🧠 Testing Reasoning Chain Structure...")
            self.test_reasoning_chain_structure(cot_response)
            
            # Test 5: Script quality
            print("\n📊 Testing Script Quality...")
            self.test_script_quality(cot_response)
            
            # Test 6: Final analysis
            print("\n📈 Testing Final Analysis...")
            self.test_final_analysis_structure(cot_response)
            
            # Test 7: Generation metadata
            print("\n⏰ Testing Generation Metadata...")
            self.test_generation_metadata(cot_response)
        
        # Test 8: Database storage
        print("\n💾 Testing Database Storage...")
        self.test_database_storage()
        
        # Test 9: CoT without reasoning chain
        print("\n🔄 Testing CoT Without Reasoning Chain...")
        self.test_cot_without_reasoning_chain()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 70)
        print("📊 CHAIN-OF-THOUGHT TESTING SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        print("\n🎯 KEY FINDINGS:")
        
        # Analyze specific CoT functionality
        cot_tests = [r for r in self.test_results if "CoT" in r["test"] or "Chain" in r["test"] or "Reasoning" in r["test"]]
        cot_passed = sum(1 for r in cot_tests if r["success"])
        
        if cot_passed == len(cot_tests):
            print("   ✅ Chain-of-Thought script generation is fully functional")
        elif cot_passed > len(cot_tests) // 2:
            print("   ⚠️  Chain-of-Thought script generation is partially functional")
        else:
            print("   ❌ Chain-of-Thought script generation has significant issues")
        
        # Check critical components
        structure_tests = [r for r in self.test_results if "Structure" in r["test"]]
        if all(r["success"] for r in structure_tests):
            print("   ✅ All response structures are properly implemented")
        
        quality_tests = [r for r in self.test_results if "Quality" in r["test"] or "Script" in r["test"]]
        if any(r["success"] for r in quality_tests):
            print("   ✅ Script quality meets sophistication requirements")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    tester = CoTScriptTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["failed_tests"] == 0 else 1)
#!/usr/bin/env python3
"""
Phase 3.1 Video Type Customization System - Comprehensive Backend Testing
Testing the enhanced template customization framework with video type adaptations
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class Phase31VideoTypeCustomizationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Connectivity", True, f"Backend responding on {API_BASE}")
                return True
            else:
                self.log_test("Backend Connectivity", False, f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_customize_template_endpoint(self):
        """Test POST /api/customize-template endpoint"""
        try:
            # Test with educational video type
            test_data = {
                "base_template": {
                    "template_id": "test_template_001",
                    "duration_category": "extended_15",
                    "system_prompt": "Create a comprehensive video script",
                    "template_content": "Base template content for testing"
                },
                "video_type": "educational"
            }
            
            response = requests.post(f"{API_BASE}/customize-template", 
                                   json=test_data, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["customized_template", "video_type", "customization_metadata"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Customize Template Endpoint - Response Structure", 
                                False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check if Phase 3.1 customizations are applied
                customized_template = data["customized_template"]
                if "video_type_customization" in customized_template:
                    customization = customized_template["video_type_customization"]
                    
                    # Validate educational video type customizations
                    if customization.get("video_type") == "educational":
                        framework = customization.get("customization_framework", {})
                        focus_areas = framework.get("focus_areas", [])
                        
                        # Check for educational-specific elements
                        educational_elements = [
                            "learning_objective_focus", "knowledge_checkpoints", 
                            "progressive_complexity_building", "interactive_engagement"
                        ]
                        
                        found_elements = [elem for elem in educational_elements if elem in focus_areas]
                        
                        if len(found_elements) >= 2:
                            self.log_test("Customize Template Endpoint - Educational Customization", 
                                        True, f"Found {len(found_elements)} educational elements: {found_elements}")
                        else:
                            self.log_test("Customize Template Endpoint - Educational Customization", 
                                        False, f"Only found {len(found_elements)} educational elements: {found_elements}")
                    else:
                        self.log_test("Customize Template Endpoint - Video Type Validation", 
                                    False, f"Expected 'educational', got '{customization.get('video_type')}'")
                else:
                    self.log_test("Customize Template Endpoint - Customization Structure", 
                                False, "Missing 'video_type_customization' in response")
                    return False
                
                self.log_test("Customize Template Endpoint", True, 
                            f"Successfully customized template for educational video type")
                return True
                
            else:
                self.log_test("Customize Template Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Customize Template Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_all_video_types_customization(self):
        """Test customization for all 4 video types"""
        video_types = ["educational", "marketing", "entertainment", "general"]
        success_count = 0
        
        base_template = {
            "template_id": "multi_type_test",
            "duration_category": "extended_20",
            "system_prompt": "Create a comprehensive video script",
            "template_content": "Base template for multi-type testing"
        }
        
        for video_type in video_types:
            try:
                test_data = {
                    "base_template": base_template,
                    "video_type": video_type
                }
                
                response = requests.post(f"{API_BASE}/customize-template", 
                                       json=test_data, 
                                       timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    customized_template = data.get("customized_template", {})
                    
                    # Check for video type specific customization
                    customization = customized_template.get("video_type_customization", {})
                    if customization.get("video_type") == video_type:
                        
                        # Validate video type specific elements
                        framework = customization.get("customization_framework", {})
                        focus_areas = framework.get("focus_areas", [])
                        
                        # Check for type-specific focus areas
                        type_specific_checks = {
                            "educational": ["learning_objective_focus", "knowledge_checkpoints"],
                            "marketing": ["conversion_optimization", "persuasive_storytelling"],
                            "entertainment": ["engagement_maximization", "emotional_roller_coaster"],
                            "general": ["universal_appeal", "balanced_content"]
                        }
                        
                        expected_elements = type_specific_checks.get(video_type, [])
                        found_elements = [elem for elem in expected_elements if elem in focus_areas]
                        
                        if len(found_elements) >= 1:
                            success_count += 1
                            self.log_test(f"Video Type Customization - {video_type.title()}", 
                                        True, f"Found {len(found_elements)} specific elements: {found_elements}")
                        else:
                            self.log_test(f"Video Type Customization - {video_type.title()}", 
                                        False, f"No specific elements found. Expected: {expected_elements}, Got: {focus_areas}")
                    else:
                        self.log_test(f"Video Type Customization - {video_type.title()}", 
                                    False, f"Video type mismatch: expected {video_type}, got {customization.get('video_type')}")
                else:
                    self.log_test(f"Video Type Customization - {video_type.title()}", 
                                False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Video Type Customization - {video_type.title()}", 
                            False, f"Request failed: {str(e)}")
        
        # Overall success rate
        success_rate = (success_count / len(video_types)) * 100
        if success_rate >= 75:
            self.log_test("All Video Types Customization", True, 
                        f"Success rate: {success_rate}% ({success_count}/{len(video_types)})")
        else:
            self.log_test("All Video Types Customization", False, 
                        f"Low success rate: {success_rate}% ({success_count}/{len(video_types)})")

    def test_video_type_frameworks_endpoint(self):
        """Test GET /api/video-type-frameworks endpoint"""
        try:
            response = requests.get(f"{API_BASE}/video-type-frameworks", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required framework information
                required_keys = ["available_video_types", "customization_frameworks"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Video Type Frameworks Endpoint - Structure", 
                                False, f"Missing keys: {missing_keys}")
                    return False
                
                # Validate available video types
                available_types = data.get("available_video_types", [])
                expected_types = ["educational", "marketing", "entertainment", "general"]
                
                if all(vtype in available_types for vtype in expected_types):
                    self.log_test("Video Type Frameworks Endpoint - Available Types", 
                                True, f"All expected types found: {available_types}")
                else:
                    missing_types = [vtype for vtype in expected_types if vtype not in available_types]
                    self.log_test("Video Type Frameworks Endpoint - Available Types", 
                                False, f"Missing types: {missing_types}")
                
                # Validate frameworks structure
                frameworks = data.get("customization_frameworks", {})
                if len(frameworks) >= 4:
                    self.log_test("Video Type Frameworks Endpoint - Frameworks Count", 
                                True, f"Found {len(frameworks)} frameworks")
                else:
                    self.log_test("Video Type Frameworks Endpoint - Frameworks Count", 
                                False, f"Only found {len(frameworks)} frameworks, expected at least 4")
                
                # Check for Phase 3.1 specific elements in educational framework
                if "educational" in frameworks:
                    edu_framework = frameworks["educational"]
                    phase31_elements = ["learning_objectives", "knowledge_retention", "interactive_elements"]
                    found_elements = [elem for elem in phase31_elements if elem in edu_framework]
                    
                    if len(found_elements) >= 2:
                        self.log_test("Video Type Frameworks Endpoint - Phase 3.1 Elements", 
                                    True, f"Found Phase 3.1 elements: {found_elements}")
                    else:
                        self.log_test("Video Type Frameworks Endpoint - Phase 3.1 Elements", 
                                    False, f"Limited Phase 3.1 elements: {found_elements}")
                
                self.log_test("Video Type Frameworks Endpoint", True, 
                            "Successfully retrieved video type frameworks")
                return True
                
            else:
                self.log_test("Video Type Frameworks Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Video Type Frameworks Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_template_customization_test_endpoint(self):
        """Test POST /api/template-customization-test endpoint"""
        try:
            response = requests.post(f"{API_BASE}/template-customization-test", 
                                   json={}, 
                                   timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check test results structure
                required_fields = ["test_status", "total_tests", "successful_tests", "success_rate"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Template Customization Test Endpoint - Structure", 
                                False, f"Missing fields: {missing_fields}")
                    return False
                
                # Validate test results
                success_rate = data.get("success_rate", 0)
                total_tests = data.get("total_tests", 0)
                successful_tests = data.get("successful_tests", 0)
                
                if success_rate >= 75 and total_tests >= 4:
                    self.log_test("Template Customization Test Endpoint - Test Results", 
                                True, f"Success rate: {success_rate}% ({successful_tests}/{total_tests})")
                else:
                    self.log_test("Template Customization Test Endpoint - Test Results", 
                                False, f"Low success rate: {success_rate}% ({successful_tests}/{total_tests})")
                
                # Check for detailed test results
                if "test_results" in data:
                    test_results = data["test_results"]
                    if len(test_results) >= 4:
                        self.log_test("Template Customization Test Endpoint - Detailed Results", 
                                    True, f"Found {len(test_results)} detailed test results")
                    else:
                        self.log_test("Template Customization Test Endpoint - Detailed Results", 
                                    False, f"Only {len(test_results)} detailed results found")
                
                self.log_test("Template Customization Test Endpoint", True, 
                            "Test endpoint executed successfully")
                return True
                
            else:
                self.log_test("Template Customization Test Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Template Customization Test Endpoint", False, f"Request failed: {str(e)}")
            return False

    def test_different_base_templates(self):
        """Test customization with different base template durations"""
        durations = ["extended_15", "extended_20", "extended_25"]
        success_count = 0
        
        for duration in durations:
            try:
                base_template = {
                    "template_id": f"duration_test_{duration}",
                    "duration_category": duration,
                    "system_prompt": f"Create a {duration} video script",
                    "template_content": f"Base template for {duration} duration testing"
                }
                
                test_data = {
                    "base_template": base_template,
                    "video_type": "marketing"  # Test with marketing type
                }
                
                response = requests.post(f"{API_BASE}/customize-template", 
                                       json=test_data, 
                                       timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    customized_template = data.get("customized_template", {})
                    
                    # Check if duration is preserved
                    if customized_template.get("duration_category") == duration:
                        success_count += 1
                        self.log_test(f"Base Template Duration - {duration}", 
                                    True, f"Duration preserved and customized successfully")
                    else:
                        self.log_test(f"Base Template Duration - {duration}", 
                                    False, f"Duration not preserved: expected {duration}, got {customized_template.get('duration_category')}")
                else:
                    self.log_test(f"Base Template Duration - {duration}", 
                                False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Base Template Duration - {duration}", 
                            False, f"Request failed: {str(e)}")
        
        # Overall assessment
        success_rate = (success_count / len(durations)) * 100
        if success_rate >= 66:
            self.log_test("Different Base Templates", True, 
                        f"Success rate: {success_rate}% ({success_count}/{len(durations)})")
        else:
            self.log_test("Different Base Templates", False, 
                        f"Low success rate: {success_rate}% ({success_count}/{len(durations)})")

    def test_video_type_specific_adaptations(self):
        """Test specific adaptations for each video type"""
        
        # Educational video type test
        try:
            educational_template = {
                "template_id": "educational_adaptation_test",
                "duration_category": "extended_15",
                "system_prompt": "Educational content creation",
                "template_content": "Educational base content"
            }
            
            response = requests.post(f"{API_BASE}/customize-template", 
                                   json={"base_template": educational_template, "video_type": "educational"}, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                customized = data.get("customized_template", {})
                customization = customized.get("video_type_customization", {})
                
                # Check for educational-specific adaptations
                specialized_elements = customization.get("specialized_elements", {})
                
                educational_checks = [
                    "learning_objectives" in specialized_elements,
                    "knowledge_retention" in specialized_elements,
                    "interactive_elements" in specialized_elements
                ]
                
                if sum(educational_checks) >= 2:
                    self.log_test("Educational Video Adaptations", True, 
                                f"Found {sum(educational_checks)}/3 educational adaptations")
                else:
                    self.log_test("Educational Video Adaptations", False, 
                                f"Only found {sum(educational_checks)}/3 educational adaptations")
            else:
                self.log_test("Educational Video Adaptations", False, 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Educational Video Adaptations", False, f"Request failed: {str(e)}")
        
        # Marketing video type test
        try:
            marketing_template = {
                "template_id": "marketing_adaptation_test",
                "duration_category": "extended_20",
                "system_prompt": "Marketing content creation",
                "template_content": "Marketing base content"
            }
            
            response = requests.post(f"{API_BASE}/customize-template", 
                                   json={"base_template": marketing_template, "video_type": "marketing"}, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                customized = data.get("customized_template", {})
                customization = customized.get("video_type_customization", {})
                
                # Check for marketing-specific adaptations
                specialized_elements = customization.get("specialized_elements", {})
                
                marketing_checks = [
                    "conversion_structure" in specialized_elements,
                    "emotional_triggers" in specialized_elements,
                    "social_proof" in specialized_elements
                ]
                
                if sum(marketing_checks) >= 2:
                    self.log_test("Marketing Video Adaptations", True, 
                                f"Found {sum(marketing_checks)}/3 marketing adaptations")
                else:
                    self.log_test("Marketing Video Adaptations", False, 
                                f"Only found {sum(marketing_checks)}/3 marketing adaptations")
            else:
                self.log_test("Marketing Video Adaptations", False, 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Marketing Video Adaptations", False, f"Request failed: {str(e)}")

    def test_integration_with_existing_system(self):
        """Test integration with existing DurationSpecificPromptGenerator"""
        try:
            # Test that existing functionality still works
            base_template = {
                "template_id": "integration_test",
                "duration_category": "extended_25",
                "system_prompt": "Integration test content",
                "template_content": "Testing integration with existing system"
            }
            
            response = requests.post(f"{API_BASE}/customize-template", 
                                   json={"base_template": base_template, "video_type": "general"}, 
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                customized = data.get("customized_template", {})
                
                # Check that Phase 3.1 metadata is present
                phase31_metadata = customized.get("phase_3_1_metadata", {})
                
                integration_checks = [
                    phase31_metadata.get("implementation_version") == "3.1.0",
                    phase31_metadata.get("validation_status") == "phase_3_1_compliant",
                    "video_type_customization" in customized,
                    customized.get("duration_category") == "extended_25"
                ]
                
                if sum(integration_checks) >= 3:
                    self.log_test("Integration with Existing System", True, 
                                f"Passed {sum(integration_checks)}/4 integration checks")
                else:
                    self.log_test("Integration with Existing System", False, 
                                f"Only passed {sum(integration_checks)}/4 integration checks")
            else:
                self.log_test("Integration with Existing System", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Integration with Existing System", False, f"Request failed: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all Phase 3.1 Video Type Customization System tests"""
        print("🚀 Starting Phase 3.1 Video Type Customization System Comprehensive Testing")
        print("=" * 80)
        print()
        
        # Test 1: Basic connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed. Stopping tests.")
            return 0
        
        # Test 2: Core functionality
        print("📋 Testing Core Functionality...")
        self.test_customize_template_endpoint()
        
        # Test 3: All video types
        print("🎯 Testing All Video Types...")
        self.test_all_video_types_customization()
        
        # Test 4: API endpoints
        print("🔗 Testing API Endpoints...")
        self.test_video_type_frameworks_endpoint()
        self.test_template_customization_test_endpoint()
        
        # Test 5: Different base templates
        print("📝 Testing Different Base Templates...")
        self.test_different_base_templates()
        
        # Test 6: Video type specific adaptations
        print("🎨 Testing Video Type Specific Adaptations...")
        self.test_video_type_specific_adaptations()
        
        # Test 7: Integration testing
        print("🔧 Testing Integration with Existing System...")
        self.test_integration_with_existing_system()
        
        # Final results
        print("=" * 80)
        print("🏁 PHASE 3.1 VIDEO TYPE CUSTOMIZATION SYSTEM TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        print()
        
        # Categorize results
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}")
        
        if failed_tests:
            print()
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print()
        
        # Overall assessment
        if success_rate >= 85:
            print("🎉 EXCELLENT: Phase 3.1 Video Type Customization System is working excellently!")
        elif success_rate >= 70:
            print("✅ GOOD: Phase 3.1 Video Type Customization System is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Phase 3.1 Video Type Customization System has some issues that need attention.")
        else:
            print("❌ CRITICAL: Phase 3.1 Video Type Customization System has significant issues.")
        
        return success_rate

if __name__ == "__main__":
    print("Phase 3.1 Video Type Customization System - Backend Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = Phase31VideoTypeCustomizationTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)
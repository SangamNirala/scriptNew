#!/usr/bin/env python3
"""
Phase 3.2 Template Integration Manager Backend Testing
Comprehensive testing for the new Template Integration Manager implementation

Test Coverage:
1. Template Integration Manager Statistics Endpoint
2. Template Integration Workflow Test Endpoint  
3. Template-Integrated Script Generation Endpoint
4. System Integration Verification
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://692556dc-9a80-418a-8d12-65b2cbc6f397.preview.emergentagent.com/api"

class Phase32TemplateIntegrationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test_name": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_template_integration_statistics(self):
        """Test 1: Template Integration Manager Statistics Endpoint"""
        print("🧪 TEST 1: Template Integration Manager Statistics Endpoint")
        print("=" * 60)
        
        try:
            response = requests.get(f"{BACKEND_URL}/template-integration-manager/statistics", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["phase_implementation", "statistics", "system_integrations", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Statistics Endpoint Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Verify phase implementation
                if data.get("phase_implementation") != "3.2_template_integration":
                    self.log_test(
                        "Phase Implementation Verification",
                        False,
                        f"Expected '3.2_template_integration', got '{data.get('phase_implementation')}'",
                        data
                    )
                    return
                
                # Verify system integrations
                system_integrations = data.get("system_integrations", {})
                expected_integrations = [
                    "enhanced_prompt_architecture",
                    "duration_specific_templates", 
                    "advanced_script_generator",
                    "chain_of_thought_generator",
                    "segmentation_engine"
                ]
                
                integration_status = {}
                for integration in expected_integrations:
                    status = system_integrations.get(integration, "❌ Missing")
                    integration_status[integration] = status
                
                # Verify statistics data
                statistics = data.get("statistics", {})
                
                self.log_test(
                    "Template Integration Manager Statistics",
                    True,
                    f"Successfully retrieved statistics with {len(statistics)} metrics. System integrations: {integration_status}",
                    {
                        "statistics_count": len(statistics),
                        "system_integrations": integration_status,
                        "phase": data.get("phase_implementation")
                    }
                )
                
            else:
                self.log_test(
                    "Template Integration Manager Statistics",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Template Integration Manager Statistics",
                False,
                f"Exception: {str(e)}",
                {"error": str(e)}
            )

    def test_template_integration_workflow(self):
        """Test 2: Template Integration Workflow Test Endpoint"""
        print("🧪 TEST 2: Template Integration Workflow Test Endpoint")
        print("=" * 60)
        
        try:
            response = requests.post(f"{BACKEND_URL}/template-integration-workflow-test", timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["phase_implementation", "test_summary", "detailed_results", "integration_manager_stats", "system_integration_verification"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Workflow Test Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Verify test summary
                test_summary = data.get("test_summary", {})
                total_scenarios = test_summary.get("total_scenarios", 0)
                successful_scenarios = test_summary.get("successful_scenarios", 0)
                success_rate = test_summary.get("success_rate_percent", 0)
                
                # Verify detailed results for all three duration categories
                detailed_results = data.get("detailed_results", {})
                expected_scenarios = [
                    "Extended 15-20 Min Educational",
                    "Extended 20-25 Min Marketing", 
                    "Extended 25-30 Min Entertainment"
                ]
                
                scenario_results = {}
                for scenario in expected_scenarios:
                    if scenario in detailed_results:
                        result = detailed_results[scenario]
                        scenario_results[scenario] = {
                            "success": result.get("success", False),
                            "processing_time": result.get("processing_time", 0),
                            "script_length": result.get("script_length", 0),
                            "template_used": result.get("template_used", "Unknown"),
                            "segmentation_applied": result.get("segmentation_applied", False)
                        }
                    else:
                        scenario_results[scenario] = {"success": False, "error": "Scenario not found in results"}
                
                # Verify system integration verification
                system_verification = data.get("system_integration_verification", {})
                expected_verifications = [
                    "template_selection",
                    "template_customization",
                    "segmentation_integration", 
                    "enhanced_prompt_generation",
                    "advanced_script_generation",
                    "quality_validation"
                ]
                
                verification_status = {}
                for verification in expected_verifications:
                    status = system_verification.get(verification, "❌ Missing")
                    verification_status[verification] = status
                
                self.log_test(
                    "Template Integration Workflow Test",
                    success_rate >= 66.7,  # At least 2 out of 3 scenarios should pass
                    f"Success rate: {success_rate}% ({successful_scenarios}/{total_scenarios}). Scenario results: {scenario_results}. System verification: {verification_status}",
                    {
                        "success_rate": success_rate,
                        "scenario_results": scenario_results,
                        "system_verification": verification_status
                    }
                )
                
            else:
                self.log_test(
                    "Template Integration Workflow Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Template Integration Workflow Test",
                False,
                f"Exception: {str(e)}",
                {"error": str(e)}
            )

    def test_template_integrated_script_generation(self):
        """Test 3: Template-Integrated Script Generation Endpoint"""
        print("🧪 TEST 3: Template-Integrated Script Generation Endpoint")
        print("=" * 60)
        
        # Test with the exact sample from review request
        test_request = {
            "prompt": "Create a comprehensive guide to artificial intelligence for beginners",
            "duration": "extended_20",
            "video_type": "educational", 
            "complexity_preference": "moderate",
            "focus_areas": ["technical_accuracy", "educational_value"],
            "enable_segmentation": True,
            "enable_narrative_continuity": True,
            "enable_content_depth": True,
            "enable_advanced_generation": True
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/generate-script-template-integrated",
                json=test_request,
                timeout=180  # 3 minutes for complex generation
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["generated_script", "template_config", "segmentation_plan", "enhanced_prompt", "integration_metadata", "performance_metrics", "success"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Template-Integrated Script Generation Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Verify success status
                if not data.get("success", False):
                    self.log_test(
                        "Template-Integrated Script Generation Success",
                        False,
                        "Integration reported as unsuccessful",
                        data
                    )
                    return
                
                # Verify generated script quality
                generated_script = data.get("generated_script", "")
                script_length = len(generated_script)
                
                # For extended_20 (20-25 min), expect substantial content
                min_expected_length = 3000  # Minimum characters for 20+ minute content
                
                if script_length < min_expected_length:
                    self.log_test(
                        "Template-Integrated Script Quality",
                        False,
                        f"Script too short for extended_20 duration: {script_length} chars (expected >{min_expected_length})",
                        {"script_length": script_length, "generated_script": generated_script[:500] + "..."}
                    )
                    return
                
                # Verify template configuration
                template_config = data.get("template_config", {})
                template_name = template_config.get("template_name", "Unknown")
                
                # Verify segmentation plan
                segmentation_plan = data.get("segmentation_plan", {})
                segments_planned = segmentation_plan.get("total_segments", 0)
                
                # Verify performance metrics
                performance_metrics = data.get("performance_metrics", {})
                processing_time = performance_metrics.get("total_processing_time_seconds", 0)
                
                # Verify integration metadata
                integration_metadata = data.get("integration_metadata", {})
                
                self.log_test(
                    "Template-Integrated Script Generation",
                    True,
                    f"Successfully generated {script_length} char script using '{template_name}' template with {segments_planned} segments in {processing_time:.2f}s",
                    {
                        "script_length": script_length,
                        "template_name": template_name,
                        "segments_planned": segments_planned,
                        "processing_time": processing_time,
                        "integration_systems": len([k for k, v in integration_metadata.get("integration_request", {}).items() if k.startswith("enable_") and v])
                    }
                )
                
            else:
                self.log_test(
                    "Template-Integrated Script Generation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_test(
                "Template-Integrated Script Generation",
                False,
                f"Exception: {str(e)}",
                {"error": str(e)}
            )

    def test_system_integration_verification(self):
        """Test 4: System Integration Verification"""
        print("🧪 TEST 4: System Integration Verification")
        print("=" * 60)
        
        # Test different duration categories and video types
        test_scenarios = [
            {
                "name": "Extended 15 Educational Integration",
                "request": {
                    "prompt": "Explain quantum computing fundamentals",
                    "duration": "extended_15",
                    "video_type": "educational",
                    "complexity_preference": "moderate",
                    "focus_areas": ["technical_accuracy"]
                }
            },
            {
                "name": "Extended 25 Marketing Integration", 
                "request": {
                    "prompt": "Create a product launch strategy presentation",
                    "duration": "extended_25",
                    "video_type": "marketing",
                    "complexity_preference": "advanced",
                    "focus_areas": ["conversion_optimization"]
                }
            }
        ]
        
        integration_results = {}
        
        for scenario in test_scenarios:
            scenario_name = scenario["name"]
            print(f"Testing {scenario_name}...")
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate-script-template-integrated",
                    json=scenario["request"],
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    integration_results[scenario_name] = {
                        "success": data.get("success", False),
                        "script_generated": len(data.get("generated_script", "")) > 1000,
                        "template_selected": bool(data.get("template_config", {}).get("template_name")),
                        "segmentation_applied": bool(data.get("segmentation_plan", {}).get("total_segments", 0) > 0),
                        "enhanced_prompt_created": len(data.get("enhanced_prompt", "")) > 100,
                        "performance_tracked": bool(data.get("performance_metrics", {})),
                        "processing_time": data.get("performance_metrics", {}).get("total_processing_time_seconds", 0)
                    }
                else:
                    integration_results[scenario_name] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text[:200]}"
                    }
                    
            except Exception as e:
                integration_results[scenario_name] = {
                    "success": False,
                    "error": str(e)[:200]
                }
        
        # Calculate overall integration success
        successful_integrations = sum(1 for result in integration_results.values() if result.get("success", False))
        total_integrations = len(test_scenarios)
        integration_success_rate = (successful_integrations / total_integrations) * 100
        
        # Verify core system components
        system_components = {
            "enhanced_prompt_architecture": all(result.get("enhanced_prompt_created", False) for result in integration_results.values() if result.get("success")),
            "duration_specific_templates": all(result.get("template_selected", False) for result in integration_results.values() if result.get("success")),
            "advanced_script_generator": all(result.get("script_generated", False) for result in integration_results.values() if result.get("success")),
            "segmentation_engine": all(result.get("segmentation_applied", False) for result in integration_results.values() if result.get("success")),
            "performance_tracking": all(result.get("performance_tracked", False) for result in integration_results.values() if result.get("success"))
        }
        
        working_components = sum(1 for working in system_components.values() if working)
        total_components = len(system_components)
        component_success_rate = (working_components / total_components) * 100
        
        self.log_test(
            "System Integration Verification",
            integration_success_rate >= 50 and component_success_rate >= 80,
            f"Integration success: {integration_success_rate}% ({successful_integrations}/{total_integrations}). Component success: {component_success_rate}% ({working_components}/{total_components}). Results: {integration_results}",
            {
                "integration_success_rate": integration_success_rate,
                "component_success_rate": component_success_rate,
                "integration_results": integration_results,
                "system_components": system_components
            }
        )

    def run_all_tests(self):
        """Run all Phase 3.2 Template Integration Manager tests"""
        print("🚀 PHASE 3.2 TEMPLATE INTEGRATION MANAGER TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        self.test_template_integration_statistics()
        self.test_template_integration_workflow()
        self.test_template_integrated_script_generation()
        self.test_system_integration_verification()
        
        # Print summary
        print("=" * 80)
        print("🎯 PHASE 3.2 TEMPLATE INTEGRATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print()
        
        # Print detailed results
        print("📊 DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.test_results:
            print(f"{result['status']}: {result['test_name']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print(f"Test Completion Time: {datetime.now().isoformat()}")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": (self.passed_tests/self.total_tests)*100,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    tester = Phase32TemplateIntegrationTester()
    results = tester.run_all_tests()
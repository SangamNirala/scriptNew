#!/usr/bin/env python3
"""
Phase 4.2: Enhanced Prompt Template API Endpoints Implementation - Comprehensive Backend Testing

This test suite validates all Phase 4.2 Enhanced Prompt Template API endpoints as specified in the review request:

CRITICAL ENDPOINTS TO TEST:
1. GET /api/enhanced-prompt-templates - List all available enhanced templates with metadata
2. POST /api/enhanced-prompt-templates - Test template generation for any duration with customization options  
3. GET /api/enhanced-prompt-templates/{duration} - Retrieve specific duration template details and metadata
4. POST /api/enhanced-prompt-templates/{duration} - Generate enhanced system prompt for specific duration with video type customization
5. POST /api/validate-template-compatibility - Validate template compatibility with segmentation system

TEST SCENARIOS COVERED:
- Template Listing Tests
- Template Generation Tests  
- Duration-Specific Tests
- Compatibility Validation Tests
- Integration Tests
- Error Handling Tests
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL Configuration
BACKEND_URL = "https://692556dc-9a80-418a-8d12-65b2cbc6f397.preview.emergentagent.com/api"

class Phase42EnhancedPromptTemplateAPITester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def run_all_tests(self):
        """Run comprehensive Phase 4.2 Enhanced Prompt Template API testing"""
        print("🚀 PHASE 4.2: ENHANCED PROMPT TEMPLATE API ENDPOINTS - COMPREHENSIVE BACKEND TESTING")
        print("=" * 100)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 100)
        
        # Test Categories
        test_categories = [
            ("Template Listing Tests", self.test_template_listing),
            ("Template Generation Tests", self.test_template_generation),
            ("Duration-Specific Tests", self.test_duration_specific_operations),
            ("Compatibility Validation Tests", self.test_compatibility_validation),
            ("Integration Tests", self.test_integration_points),
            ("Error Handling Tests", self.test_error_handling)
        ]
        
        for category_name, test_method in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 80)
            await test_method()
        
        # Print comprehensive results
        await self.print_final_results()
        
    async def test_template_listing(self):
        """Test GET /api/enhanced-prompt-templates endpoint"""
        print("🔍 Testing Template Listing Endpoint...")
        
        # Test 1: List all enhanced templates
        success = await self.test_endpoint(
            "GET Enhanced Prompt Templates List",
            "GET",
            "/enhanced-prompt-templates",
            expected_status=200,
            validation_func=self.validate_template_list_response
        )
        
        if success:
            print("✅ Template listing endpoint working correctly")
        else:
            print("❌ Template listing endpoint failed")
    
    async def test_template_generation(self):
        """Test POST /api/enhanced-prompt-templates endpoint"""
        print("🧪 Testing Template Generation Endpoint...")
        
        # Test different video types and durations
        test_cases = [
            {
                "name": "Educational Video - Extended 15",
                "payload": {
                    "duration": "extended_15",
                    "video_type": "educational",
                    "enable_customization": True,
                    "customization_options": {
                        "focus_area": "learning_objectives",
                        "complexity_level": "intermediate"
                    }
                }
            },
            {
                "name": "Marketing Video - Extended 20", 
                "payload": {
                    "duration": "extended_20",
                    "video_type": "marketing",
                    "enable_customization": True,
                    "customization_options": {
                        "focus_area": "conversion_optimization",
                        "tone": "persuasive"
                    }
                }
            },
            {
                "name": "Entertainment Video - Extended 25",
                "payload": {
                    "duration": "extended_25",
                    "video_type": "entertainment",
                    "enable_customization": False
                }
            },
            {
                "name": "General Video - Extended 15 (No Customization)",
                "payload": {
                    "duration": "extended_15",
                    "video_type": "general",
                    "enable_customization": False
                }
            }
        ]
        
        for test_case in test_cases:
            success = await self.test_endpoint(
                f"Template Generation - {test_case['name']}",
                "POST",
                "/enhanced-prompt-templates",
                payload=test_case["payload"],
                expected_status=200,
                validation_func=self.validate_enhanced_prompt_response
            )
            
            if success:
                print(f"✅ {test_case['name']} generation successful")
            else:
                print(f"❌ {test_case['name']} generation failed")
    
    async def test_duration_specific_operations(self):
        """Test duration-specific GET and POST endpoints"""
        print("⏱️ Testing Duration-Specific Operations...")
        
        durations = ["extended_15", "extended_20", "extended_25"]
        
        for duration in durations:
            # Test GET /api/enhanced-prompt-templates/{duration}
            success_get = await self.test_endpoint(
                f"Get Template Details - {duration}",
                "GET",
                f"/enhanced-prompt-templates/{duration}",
                expected_status=200,
                validation_func=self.validate_template_details_response
            )
            
            # Test POST /api/enhanced-prompt-templates/{duration}
            test_payload = {
                "duration": duration,  # This will be overridden by URL parameter
                "video_type": "educational",
                "enable_customization": True,
                "customization_options": {
                    "focus_area": "engagement_optimization",
                    "complexity_level": "advanced"
                }
            }
            
            success_post = await self.test_endpoint(
                f"Generate Enhanced Prompt - {duration}",
                "POST", 
                f"/enhanced-prompt-templates/{duration}",
                payload=test_payload,
                expected_status=200,
                validation_func=self.validate_enhanced_prompt_response
            )
            
            if success_get and success_post:
                print(f"✅ {duration} operations successful")
            else:
                print(f"❌ {duration} operations failed (GET: {success_get}, POST: {success_post})")
    
    async def test_compatibility_validation(self):
        """Test POST /api/validate-template-compatibility endpoint"""
        print("🔍 Testing Template Compatibility Validation...")
        
        # Test different compatibility scenarios
        test_cases = [
            {
                "name": "Compatible Segmentation Plan - Extended 15",
                "payload": {
                    "duration": "extended_15",
                    "segmentation_plan": {
                        "total_segments": 3,
                        "segment_duration_minutes": 6,
                        "total_duration_minutes": 18,
                        "complexity_level": "moderate",
                        "focus_strategy": "balanced_pacing_engagement"
                    }
                }
            },
            {
                "name": "Compatible Segmentation Plan - Extended 20",
                "payload": {
                    "duration": "extended_20", 
                    "segmentation_plan": {
                        "total_segments": 4,
                        "segment_duration_minutes": 5.5,
                        "total_duration_minutes": 22,
                        "complexity_level": "advanced",
                        "focus_strategy": "sustained_engagement_algorithms"
                    }
                }
            },
            {
                "name": "Compatible Segmentation Plan - Extended 25",
                "payload": {
                    "duration": "extended_25",
                    "segmentation_plan": {
                        "total_segments": 5,
                        "segment_duration_minutes": 5.5,
                        "total_duration_minutes": 27.5,
                        "complexity_level": "expert",
                        "focus_strategy": "peak_engagement_distribution"
                    }
                }
            },
            {
                "name": "Incompatible Segmentation Plan - Too Many Segments",
                "payload": {
                    "duration": "extended_15",
                    "segmentation_plan": {
                        "total_segments": 10,  # Too many for extended_15
                        "segment_duration_minutes": 2,
                        "total_duration_minutes": 20,
                        "complexity_level": "basic",
                        "focus_strategy": "simple_engagement"
                    }
                }
            }
        ]
        
        for test_case in test_cases:
            success = await self.test_endpoint(
                f"Compatibility Validation - {test_case['name']}",
                "POST",
                "/validate-template-compatibility",
                payload=test_case["payload"],
                expected_status=200,
                validation_func=self.validate_compatibility_response
            )
            
            if success:
                print(f"✅ {test_case['name']} validation successful")
            else:
                print(f"❌ {test_case['name']} validation failed")
    
    async def test_integration_points(self):
        """Test integration with existing enhanced_prompt_architecture instance"""
        print("🔗 Testing Integration Points...")
        
        # Test 1: Verify enhanced_prompt_architecture integration
        success_arch = await self.test_endpoint(
            "Enhanced Prompt Architecture Integration",
            "POST",
            "/enhanced-prompt-templates",
            payload={
                "duration": "extended_20",
                "video_type": "marketing",
                "enable_customization": True
            },
            expected_status=200,
            validation_func=self.validate_architecture_integration
        )
        
        # Test 2: Verify template_registry integration
        success_registry = await self.test_endpoint(
            "Template Registry Integration",
            "GET",
            "/enhanced-prompt-templates",
            expected_status=200,
            validation_func=self.validate_registry_integration
        )
        
        # Test 3: Test segmentation system compatibility
        success_segmentation = await self.test_endpoint(
            "Segmentation System Integration",
            "POST",
            "/validate-template-compatibility",
            payload={
                "duration": "extended_25",
                "segmentation_plan": {
                    "total_segments": 5,
                    "segment_duration_minutes": 5.5,
                    "total_duration_minutes": 27.5,
                    "complexity_level": "expert",
                    "focus_strategy": "peak_engagement_distribution"
                }
            },
            expected_status=200,
            validation_func=self.validate_segmentation_integration
        )
        
        if success_arch and success_registry and success_segmentation:
            print("✅ All integration points working correctly")
        else:
            print(f"❌ Integration issues detected (Arch: {success_arch}, Registry: {success_registry}, Segmentation: {success_segmentation})")
    
    async def test_error_handling(self):
        """Test error handling with invalid requests"""
        print("⚠️ Testing Error Handling...")
        
        # Test 1: Invalid duration
        await self.test_endpoint(
            "Invalid Duration Error Handling",
            "GET",
            "/enhanced-prompt-templates/invalid_duration",
            expected_status=400,
            validation_func=self.validate_error_response
        )
        
        # Test 2: Missing required fields
        await self.test_endpoint(
            "Missing Required Fields Error Handling",
            "POST",
            "/enhanced-prompt-templates",
            payload={},  # Missing required duration field
            expected_status=422,  # Pydantic validation error
            validation_func=self.validate_error_response
        )
        
        # Test 3: Invalid compatibility request
        await self.test_endpoint(
            "Invalid Compatibility Request Error Handling",
            "POST",
            "/validate-template-compatibility",
            payload={
                "duration": "invalid_duration",
                "segmentation_plan": {}
            },
            expected_status=400,
            validation_func=self.validate_error_response
        )
        
        print("✅ Error handling tests completed")
    
    async def test_endpoint(self, test_name: str, method: str, endpoint: str, 
                          payload: Dict = None, expected_status: int = 200,
                          validation_func = None) -> bool:
        """Test a specific endpoint"""
        self.total_tests += 1
        start_time = time.time()
        
        try:
            url = f"{self.backend_url}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url) as response:
                        status = response.status
                        data = await response.json()
                elif method == "POST":
                    async with session.post(url, json=payload) as response:
                        status = response.status
                        data = await response.json()
                else:
                    raise ValueError(f"Unsupported method: {method}")
            
            duration = time.time() - start_time
            
            # Check status code
            if status != expected_status:
                self.record_test_result(test_name, False, f"Expected status {expected_status}, got {status}", duration, data)
                return False
            
            # Run validation function if provided
            if validation_func:
                validation_result = validation_func(data)
                if not validation_result["valid"]:
                    self.record_test_result(test_name, False, validation_result["error"], duration, data)
                    return False
            
            self.record_test_result(test_name, True, "Success", duration, data)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_test_result(test_name, False, f"Exception: {str(e)}", duration, None)
            return False
    
    def validate_template_list_response(self, data: Dict) -> Dict[str, Any]:
        """Validate template list response structure"""
        try:
            # Check required fields
            required_fields = ["available_templates", "total_templates", "registry_info"]
            for field in required_fields:
                if field not in data:
                    return {"valid": False, "error": f"Missing required field: {field}"}
            
            # Validate available_templates structure
            templates = data["available_templates"]
            if not isinstance(templates, list):
                return {"valid": False, "error": "available_templates should be a list"}
            
            # Check if we have enhanced templates (extended_15, extended_20, extended_25)
            template_durations = [t.get("duration") for t in templates if t.get("duration")]
            expected_durations = ["extended_15", "extended_20", "extended_25"]
            
            for duration in expected_durations:
                if duration not in template_durations:
                    return {"valid": False, "error": f"Missing expected duration: {duration}"}
            
            # Validate template metadata
            for template in templates:
                required_template_fields = ["template_id", "duration", "template_name", "description"]
                for field in required_template_fields:
                    if field not in template:
                        return {"valid": False, "error": f"Template missing required field: {field}"}
            
            # Validate registry_info
            registry_info = data["registry_info"]
            if not isinstance(registry_info, dict):
                return {"valid": False, "error": "registry_info should be a dictionary"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation exception: {str(e)}"}
    
    def validate_enhanced_prompt_response(self, data: Dict) -> Dict[str, Any]:
        """Validate enhanced prompt response structure"""
        try:
            # Check required fields
            required_fields = ["template_info", "enhanced_system_prompt", "segmentation_compatibility", 
                             "customizations_applied", "generation_metadata"]
            for field in required_fields:
                if field not in data:
                    return {"valid": False, "error": f"Missing required field: {field}"}
            
            # Validate template_info
            template_info = data["template_info"]
            required_template_fields = ["template_id", "template_name", "duration", "video_type", "suitability_score"]
            for field in required_template_fields:
                if field not in template_info:
                    return {"valid": False, "error": f"template_info missing required field: {field}"}
            
            # Validate enhanced_system_prompt
            prompt = data["enhanced_system_prompt"]
            if not isinstance(prompt, str) or len(prompt) < 100:
                return {"valid": False, "error": "enhanced_system_prompt should be a substantial string"}
            
            # Validate segmentation_compatibility
            segmentation = data["segmentation_compatibility"]
            if not isinstance(segmentation, dict):
                return {"valid": False, "error": "segmentation_compatibility should be a dictionary"}
            
            # Validate customizations_applied
            customizations = data["customizations_applied"]
            if not isinstance(customizations, list):
                return {"valid": False, "error": "customizations_applied should be a list"}
            
            # Validate generation_metadata
            metadata = data["generation_metadata"]
            if not isinstance(metadata, dict):
                return {"valid": False, "error": "generation_metadata should be a dictionary"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation exception: {str(e)}"}
    
    def validate_template_details_response(self, data: Dict) -> Dict[str, Any]:
        """Validate template details response structure"""
        try:
            # Check required sections
            required_sections = ["template_details", "template_specifications", "usage_statistics", 
                               "supported_video_types", "integration_compatibility"]
            for section in required_sections:
                if section not in data:
                    return {"valid": False, "error": f"Missing required section: {section}"}
            
            # Validate template_details
            details = data["template_details"]
            required_detail_fields = ["template_id", "duration", "template_name", "description"]
            for field in required_detail_fields:
                if field not in details:
                    return {"valid": False, "error": f"template_details missing required field: {field}"}
            
            # Validate template_specifications
            specs = data["template_specifications"]
            required_spec_fields = ["complexity_level", "focus_strategy", "expertise_areas", "word_count"]
            for field in required_spec_fields:
                if field not in specs:
                    return {"valid": False, "error": f"template_specifications missing required field: {field}"}
            
            # Validate supported_video_types
            video_types = data["supported_video_types"]
            expected_types = ["educational", "marketing", "entertainment", "general"]
            if not all(vtype in video_types for vtype in expected_types):
                return {"valid": False, "error": "Missing expected video types"}
            
            # Validate integration_compatibility
            integration = data["integration_compatibility"]
            expected_integrations = ["segmentation_system", "narrative_continuity", "content_depth_scaling", "quality_consistency"]
            for integration_type in expected_integrations:
                if integration_type not in integration or not integration[integration_type]:
                    return {"valid": False, "error": f"Missing or false integration: {integration_type}"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation exception: {str(e)}"}
    
    def validate_compatibility_response(self, data: Dict) -> Dict[str, Any]:
        """Validate compatibility response structure"""
        try:
            # Check required fields
            required_fields = ["compatible", "compatibility_score", "analysis", "recommendations"]
            for field in required_fields:
                if field not in data:
                    return {"valid": False, "error": f"Missing required field: {field}"}
            
            # Validate compatibility_score
            score = data["compatibility_score"]
            if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                return {"valid": False, "error": "compatibility_score should be a float between 0.0 and 1.0"}
            
            # Validate analysis structure
            analysis = data["analysis"]
            required_analysis_fields = ["overall_assessment", "detailed_analysis", "template_info", "segmentation_plan_summary"]
            for field in required_analysis_fields:
                if field not in analysis:
                    return {"valid": False, "error": f"analysis missing required field: {field}"}
            
            # Validate recommendations
            recommendations = data["recommendations"]
            if not isinstance(recommendations, list) or len(recommendations) == 0:
                return {"valid": False, "error": "recommendations should be a non-empty list"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation exception: {str(e)}"}
    
    def validate_architecture_integration(self, data: Dict) -> Dict[str, Any]:
        """Validate enhanced_prompt_architecture integration"""
        try:
            # Check that template selection and generation worked
            template_info = data.get("template_info", {})
            if not template_info.get("template_id"):
                return {"valid": False, "error": "No template_id in response - architecture integration failed"}
            
            if not template_info.get("suitability_score"):
                return {"valid": False, "error": "No suitability_score - template selection failed"}
            
            # Check enhanced system prompt generation
            prompt = data.get("enhanced_system_prompt", "")
            if len(prompt) < 500:  # Enhanced prompts should be substantial
                return {"valid": False, "error": "Enhanced system prompt too short - generation failed"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Architecture integration validation exception: {str(e)}"}
    
    def validate_registry_integration(self, data: Dict) -> Dict[str, Any]:
        """Validate template_registry integration"""
        try:
            # Check registry_info presence and structure
            registry_info = data.get("registry_info", {})
            if not registry_info:
                return {"valid": False, "error": "No registry_info - registry integration failed"}
            
            # Check for registry statistics
            if "total_templates_in_registry" not in registry_info:
                return {"valid": False, "error": "Missing registry statistics"}
            
            # Check that templates are loaded
            total_templates = data.get("total_templates", 0)
            if total_templates == 0:
                return {"valid": False, "error": "No templates loaded - registry integration failed"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Registry integration validation exception: {str(e)}"}
    
    def validate_segmentation_integration(self, data: Dict) -> Dict[str, Any]:
        """Validate segmentation system integration"""
        try:
            # Check analysis structure
            analysis = data.get("analysis", {})
            detailed_analysis = analysis.get("detailed_analysis", {})
            
            # Check for segmentation-specific analysis
            required_analyses = ["segment_count_compatibility", "duration_compatibility", "segment_duration_compatibility"]
            for analysis_type in required_analyses:
                if analysis_type not in detailed_analysis:
                    return {"valid": False, "error": f"Missing segmentation analysis: {analysis_type}"}
            
            # Check compatibility scoring
            score = data.get("compatibility_score", 0)
            if not isinstance(score, (int, float)):
                return {"valid": False, "error": "Invalid compatibility score format"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Segmentation integration validation exception: {str(e)}"}
    
    def validate_error_response(self, data: Dict) -> Dict[str, Any]:
        """Validate error response structure"""
        try:
            # Error responses should have detail field
            if "detail" not in data:
                return {"valid": False, "error": "Error response missing detail field"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Error response validation exception: {str(e)}"}
    
    def record_test_result(self, test_name: str, passed: bool, message: str, duration: float, response_data: Any):
        """Record test result"""
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        result = {
            "test_name": test_name,
            "status": status,
            "passed": passed,
            "message": message,
            "duration": f"{duration:.2f}s",
            "response_size": len(str(response_data)) if response_data else 0
        }
        
        self.test_results.append(result)
        print(f"{status} {test_name} ({duration:.2f}s) - {message}")
    
    async def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 100)
        print("🎯 PHASE 4.2 ENHANCED PROMPT TEMPLATE API ENDPOINTS - FINAL TEST RESULTS")
        print("=" * 100)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({self.failed_tests}):")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test_name']}: {result['message']}")
        
        print(f"\n✅ PASSED TESTS ({self.passed_tests}):")
        for result in self.test_results:
            if result["passed"]:
                print(f"   • {result['test_name']} ({result['duration']})")
        
        # Endpoint-specific summary
        print(f"\n📋 ENDPOINT TESTING SUMMARY:")
        endpoint_results = {}
        for result in self.test_results:
            endpoint = "Unknown"
            if "Template List" in result["test_name"]:
                endpoint = "GET /enhanced-prompt-templates"
            elif "Template Generation" in result["test_name"]:
                endpoint = "POST /enhanced-prompt-templates"
            elif "Get Template Details" in result["test_name"]:
                endpoint = "GET /enhanced-prompt-templates/{duration}"
            elif "Generate Enhanced Prompt" in result["test_name"]:
                endpoint = "POST /enhanced-prompt-templates/{duration}"
            elif "Compatibility Validation" in result["test_name"]:
                endpoint = "POST /validate-template-compatibility"
            elif "Integration" in result["test_name"]:
                endpoint = "Integration Tests"
            elif "Error Handling" in result["test_name"]:
                endpoint = "Error Handling"
            
            if endpoint not in endpoint_results:
                endpoint_results[endpoint] = {"passed": 0, "total": 0}
            endpoint_results[endpoint]["total"] += 1
            if result["passed"]:
                endpoint_results[endpoint]["passed"] += 1
        
        for endpoint, stats in endpoint_results.items():
            success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
            print(f"   {status} {endpoint}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Critical findings
        print(f"\n🔍 CRITICAL FINDINGS:")
        if success_rate >= 90:
            print("   ✅ Phase 4.2 Enhanced Prompt Template API endpoints are working excellently")
            print("   ✅ All critical endpoints responding correctly")
            print("   ✅ Template listing, generation, and compatibility validation functional")
            print("   ✅ Integration with enhanced_prompt_architecture and template_registry working")
        elif success_rate >= 70:
            print("   ⚠️ Phase 4.2 endpoints mostly working with some issues")
            print("   ⚠️ Core functionality operational but needs attention")
        else:
            print("   ❌ Phase 4.2 endpoints have significant issues")
            print("   ❌ Critical functionality may be impaired")
        
        print(f"\n⏰ Test completed at: {datetime.now().isoformat()}")
        print("=" * 100)

async def main():
    """Main test execution"""
    tester = Phase42EnhancedPromptTemplateAPITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Phase 5.1 Enhanced Prompt Architecture Backend Testing Suite
Comprehensive testing for Enhanced Prompt Architecture system (phases 1.1-4.2)

Testing Focus:
1. Enhanced Prompt Architecture API Endpoints
2. Main Script Generation Integration  
3. Template System Validation
4. Quality Validation
5. Backward Compatibility
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://ca44aec9-802c-40f7-9f2c-fff4bef11fc8.preview.emergentagent.com/api"

class EnhancedPromptArchitectureTestSuite:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def setup(self):
        """Initialize test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        )
        
    async def teardown(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, passed: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASSED"
        else:
            self.failed_tests += 1
            status = "❌ FAILED"
            
        result = {
            "test_name": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    response_data = await response.json()
                    return response.status == 200, response_data, response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    response_data = await response.json()
                    return response.status == 200, response_data, response.status
                    
        except Exception as e:
            return False, {"error": str(e)}, 500
            
    # ========================================
    # 1. ENHANCED PROMPT ARCHITECTURE API ENDPOINTS TESTING
    # ========================================
    
    async def test_enhanced_prompt_templates_list_endpoint(self):
        """Test GET /api/enhanced-prompt-templates - List all templates"""
        success, response, status = await self.make_request("GET", "/enhanced-prompt-templates")
        
        if not success:
            self.log_test("Enhanced Prompt Templates List Endpoint", False, 
                         f"Request failed with status {status}: {response}")
            return
            
        # Validate response structure
        required_fields = ["available_templates", "total_templates", "registry_info"]
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            self.log_test("Enhanced Prompt Templates List Endpoint", False,
                         f"Missing required fields: {missing_fields}")
            return
            
        # Validate we have 3 enhanced templates
        templates = response.get("available_templates", [])
        expected_durations = ["extended_15", "extended_20", "extended_25"]
        found_durations = [t.get("duration") for t in templates]
        
        if len(templates) != 3:
            self.log_test("Enhanced Prompt Templates List Endpoint", False,
                         f"Expected 3 templates, got {len(templates)}")
            return
            
        missing_durations = [d for d in expected_durations if d not in found_durations]
        if missing_durations:
            self.log_test("Enhanced Prompt Templates List Endpoint", False,
                         f"Missing duration templates: {missing_durations}")
            return
            
        # Validate template metadata
        for template in templates:
            required_template_fields = ["duration", "template_name", "description", "word_count", "complexity_level"]
            missing_template_fields = [field for field in required_template_fields if field not in template]
            if missing_template_fields:
                self.log_test("Enhanced Prompt Templates List Endpoint", False,
                             f"Template missing fields: {missing_template_fields}")
                return
                
        self.log_test("Enhanced Prompt Templates List Endpoint", True,
                     f"Successfully retrieved {len(templates)} templates with complete metadata")
                     
    async def test_enhanced_prompt_templates_generation_endpoint(self):
        """Test POST /api/enhanced-prompt-templates - Test template generation"""
        test_data = {
            "duration": "extended_15",
            "video_type": "educational",
            "customization_options": {
                "focus_area": "engagement",
                "complexity_level": "intermediate"
            }
        }
        
        success, response, status = await self.make_request("POST", "/enhanced-prompt-templates", test_data)
        
        if not success:
            self.log_test("Enhanced Prompt Templates Generation Endpoint", False,
                         f"Request failed with status {status}: {response}")
            return
            
        # Validate response structure
        required_fields = ["template_info", "enhanced_prompt", "generation_metadata"]
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            self.log_test("Enhanced Prompt Templates Generation Endpoint", False,
                         f"Missing required fields: {missing_fields}")
            return
            
        # Validate enhanced prompt quality
        enhanced_prompt = response.get("enhanced_prompt", "")
        if len(enhanced_prompt) < 1000:
            self.log_test("Enhanced Prompt Templates Generation Endpoint", False,
                         f"Enhanced prompt too short: {len(enhanced_prompt)} chars (expected 1000+)")
            return
            
        # Check for professional terminology
        professional_terms = ["expertise", "framework", "optimization", "strategy", "methodology"]
        found_terms = [term for term in professional_terms if term.lower() in enhanced_prompt.lower()]
        
        if len(found_terms) < 3:
            self.log_test("Enhanced Prompt Templates Generation Endpoint", False,
                         f"Insufficient professional terminology: {found_terms}")
            return
            
        self.log_test("Enhanced Prompt Templates Generation Endpoint", True,
                     f"Generated enhanced prompt: {len(enhanced_prompt)} chars with professional terminology")
                     
    async def test_duration_specific_template_endpoints(self):
        """Test GET/POST /api/enhanced-prompt-templates/{duration} for all durations"""
        durations = ["extended_15", "extended_20", "extended_25"]
        video_types = ["educational", "marketing", "entertainment", "general"]
        
        for duration in durations:
            # Test GET endpoint
            success, response, status = await self.make_request("GET", f"/enhanced-prompt-templates/{duration}")
            
            if not success:
                self.log_test(f"Duration-Specific Template GET ({duration})", False,
                             f"Request failed with status {status}: {response}")
                continue
                
            # Validate template details
            required_fields = ["template_details", "specifications", "usage_statistics", "compatibility_info"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                self.log_test(f"Duration-Specific Template GET ({duration})", False,
                             f"Missing required fields: {missing_fields}")
                continue
                
            self.log_test(f"Duration-Specific Template GET ({duration})", True,
                         "Successfully retrieved template details")
            
            # Test POST endpoint with different video types (limit to 2 for efficiency)
            for video_type in video_types[:2]:
                test_data = {
                    "video_type": video_type,
                    "customization_options": {
                        "focus_area": "quality",
                        "complexity_level": "advanced"
                    }
                }
                
                success, response, status = await self.make_request("POST", f"/enhanced-prompt-templates/{duration}", test_data)
                
                if not success:
                    self.log_test(f"Duration-Specific Template POST ({duration}, {video_type})", False,
                                 f"Request failed with status {status}: {response}")
                    continue
                    
                # Validate enhanced prompt generation
                enhanced_prompt = response.get("enhanced_prompt", "")
                if len(enhanced_prompt) < 1000:
                    self.log_test(f"Duration-Specific Template POST ({duration}, {video_type})", False,
                                 f"Enhanced prompt too short: {len(enhanced_prompt)} chars")
                    continue
                    
                self.log_test(f"Duration-Specific Template POST ({duration}, {video_type})", True,
                             f"Generated {len(enhanced_prompt)} char enhanced prompt")
                             
    async def test_template_compatibility_validation_endpoint(self):
        """Test POST /api/validate-template-compatibility"""
        test_data = {
            "duration": "extended_20",
            "segmentation_plan": {
                "total_segments": 4,
                "segment_duration": 5.6,
                "complexity_level": "advanced"
            }
        }
        
        success, response, status = await self.make_request("POST", "/validate-template-compatibility", test_data)
        
        if not success:
            self.log_test("Template Compatibility Validation Endpoint", False,
                         f"Request failed with status {status}: {response}")
            return
            
        # Validate response structure
        required_fields = ["compatibility_score", "analysis", "recommendations"]
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            self.log_test("Template Compatibility Validation Endpoint", False,
                         f"Missing required fields: {missing_fields}")
            return
            
        # Validate compatibility score
        compatibility_score = response.get("compatibility_score", 0)
        if not isinstance(compatibility_score, (int, float)) or not (0 <= compatibility_score <= 1):
            self.log_test("Template Compatibility Validation Endpoint", False,
                         f"Invalid compatibility score: {compatibility_score}")
            return
            
        self.log_test("Template Compatibility Validation Endpoint", True,
                     f"Compatibility analysis completed with score: {compatibility_score}")
                     
    # ========================================
    # 2. MAIN SCRIPT GENERATION INTEGRATION TESTING
    # ========================================
    
    async def test_enhanced_script_generation_integration(self):
        """Test /api/generate-script with enhanced architecture for extended durations"""
        enhanced_durations = ["extended_15", "extended_20", "extended_25"]
        video_types = ["educational", "marketing"]  # Limit for efficiency
        
        for duration in enhanced_durations:
            for video_type in video_types:
                test_data = {
                    "prompt": f"Create a comprehensive {video_type} video about sustainable living practices",
                    "video_type": video_type,
                    "duration": duration
                }
                
                success, response, status = await self.make_request("POST", "/generate-script", test_data)
                
                if not success:
                    self.log_test(f"Enhanced Script Generation ({duration}, {video_type})", False,
                                 f"Request failed with status {status}: {response}")
                    continue
                    
                # Validate enhanced metadata is present
                generation_metadata = response.get("generation_metadata", {})
                enhanced_fields = ["enhanced_architecture_used", "template_id", "template_name", "suitability_score"]
                missing_enhanced_fields = [field for field in enhanced_fields if field not in generation_metadata]
                
                if missing_enhanced_fields:
                    self.log_test(f"Enhanced Script Generation ({duration}, {video_type})", False,
                                 f"Missing enhanced metadata fields: {missing_enhanced_fields}")
                    continue
                    
                # Validate enhanced architecture was used
                if not generation_metadata.get("enhanced_architecture_used", False):
                    self.log_test(f"Enhanced Script Generation ({duration}, {video_type})", False,
                                 "Enhanced architecture not used for extended duration")
                    continue
                    
                # Validate script quality
                generated_script = response.get("generated_script", "")
                if len(generated_script) < 500:
                    self.log_test(f"Enhanced Script Generation ({duration}, {video_type})", False,
                                 f"Generated script too short: {len(generated_script)} chars")
                    continue
                    
                self.log_test(f"Enhanced Script Generation ({duration}, {video_type})", True,
                             f"Enhanced script generated: {len(generated_script)} chars with metadata")
                             
    async def test_backward_compatibility_script_generation(self):
        """Test /api/generate-script maintains backward compatibility for standard durations"""
        standard_durations = ["short", "medium", "long"]
        
        for duration in standard_durations:
            test_data = {
                "prompt": "Create a video about healthy cooking tips",
                "video_type": "general",
                "duration": duration
            }
            
            success, response, status = await self.make_request("POST", "/generate-script", test_data)
            
            if not success:
                self.log_test(f"Backward Compatibility Script Generation ({duration})", False,
                             f"Request failed with status {status}: {response}")
                continue
                
            # Validate standard script generation still works
            generated_script = response.get("generated_script", "")
            if len(generated_script) < 100:
                self.log_test(f"Backward Compatibility Script Generation ({duration})", False,
                             f"Generated script too short: {len(generated_script)} chars")
                continue
                
            # For standard durations, enhanced architecture should not be used
            generation_metadata = response.get("generation_metadata", {})
            enhanced_used = generation_metadata.get("enhanced_architecture_used", False)
            
            if enhanced_used:
                self.log_test(f"Backward Compatibility Script Generation ({duration})", False,
                             "Enhanced architecture incorrectly used for standard duration")
                continue
                
            self.log_test(f"Backward Compatibility Script Generation ({duration})", True,
                         f"Standard script generated: {len(generated_script)} chars")
                         
    # ========================================
    # 3. TEMPLATE SYSTEM VALIDATION TESTING
    # ========================================
    
    async def test_template_registry_validation(self):
        """Test that all 3 templates are properly registered and accessible"""
        success, response, status = await self.make_request("GET", "/enhanced-prompt-templates")
        
        if not success:
            self.log_test("Template Registry Validation", False,
                         f"Cannot access template registry: {response}")
            return
            
        templates = response.get("available_templates", [])
        
        # Validate template specifications
        expected_templates = {
            "extended_15": {
                "min_word_count": 1200,
                "template_name_contains": "15-20 Minute",
                "complexity": "moderate"
            },
            "extended_20": {
                "min_word_count": 1400,
                "template_name_contains": "20-25 Minute",
                "complexity": "advanced"
            },
            "extended_25": {
                "min_word_count": 1900,
                "template_name_contains": "25-30 Minute",
                "complexity": "expert"
            }
        }
        
        validation_errors = []
        
        for template in templates:
            duration = template.get("duration")
            if duration not in expected_templates:
                validation_errors.append(f"Unexpected template duration: {duration}")
                continue
                
            expected = expected_templates[duration]
            
            # Validate word count
            word_count = template.get("word_count", 0)
            if word_count < expected["min_word_count"]:
                validation_errors.append(f"{duration}: Word count {word_count} < {expected['min_word_count']}")
                
            # Validate template name
            template_name = template.get("template_name", "")
            if expected["template_name_contains"] not in template_name:
                validation_errors.append(f"{duration}: Template name missing '{expected['template_name_contains']}'")
                
            # Validate complexity level
            complexity = template.get("complexity_level", "")
            if expected["complexity"] not in complexity:
                validation_errors.append(f"{duration}: Expected complexity '{expected['complexity']}', got '{complexity}'")
                
        if validation_errors:
            self.log_test("Template Registry Validation", False,
                         f"Template validation errors: {validation_errors}")
            return
            
        self.log_test("Template Registry Validation", True,
                     "All 3 templates properly registered with correct specifications")
                     
    async def test_video_type_customization(self):
        """Test template customization for different video types"""
        video_types = ["educational", "marketing", "entertainment", "general"]
        duration = "extended_20"  # Use middle duration for testing
        
        customization_results = {}
        
        for video_type in video_types:
            test_data = {
                "duration": duration,
                "video_type": video_type,
                "customization_options": {
                    "focus_area": "engagement",
                    "complexity_level": "intermediate"
                }
            }
            
            success, response, status = await self.make_request("POST", "/enhanced-prompt-templates", test_data)
            
            if not success:
                self.log_test(f"Video Type Customization ({video_type})", False,
                             f"Request failed: {response}")
                continue
                
            enhanced_prompt = response.get("enhanced_prompt", "")
            customization_results[video_type] = enhanced_prompt
            
        # Validate that different video types produce different customizations
        unique_prompts = set(customization_results.values())
        if len(unique_prompts) < len(video_types):
            self.log_test("Video Type Customization", False,
                         "Video type customization not producing unique results")
            return
            
        # Validate video type specific terminology
        video_type_terms = {
            "educational": ["learning", "knowledge", "understanding", "educational"],
            "marketing": ["conversion", "engagement", "brand", "marketing"],
            "entertainment": ["engaging", "entertaining", "fun", "entertainment"],
            "general": ["audience", "content", "video", "general"]
        }
        
        customization_errors = []
        for video_type, prompt in customization_results.items():
            expected_terms = video_type_terms.get(video_type, [])
            found_terms = [term for term in expected_terms if term.lower() in prompt.lower()]
            
            if len(found_terms) < 2:
                customization_errors.append(f"{video_type}: Insufficient specific terminology")
                
        if customization_errors:
            self.log_test("Video Type Customization", False,
                         f"Customization errors: {customization_errors}")
            return
            
        self.log_test("Video Type Customization", True,
                     f"Successfully customized templates for {len(video_types)} video types")
                     
    # ========================================
    # 4. QUALITY VALIDATION TESTING
    # ========================================
    
    async def test_enhanced_prompt_quality_validation(self):
        """Test that enhanced prompts contain professional terminology and advanced structures"""
        test_data = {
            "duration": "extended_25",
            "video_type": "educational",
            "customization_options": {
                "focus_area": "quality",
                "complexity_level": "expert"
            }
        }
        
        success, response, status = await self.make_request("POST", "/enhanced-prompt-templates", test_data)
        
        if not success:
            self.log_test("Enhanced Prompt Quality Validation", False,
                         f"Request failed: {response}")
            return
            
        enhanced_prompt = response.get("enhanced_prompt", "")
        
        # Quality validation criteria
        quality_checks = {
            "length": len(enhanced_prompt) >= 1000,
            "professional_terms": any(term in enhanced_prompt.lower() for term in 
                                    ["expertise", "framework", "methodology", "optimization", "strategy"]),
            "advanced_structures": any(structure in enhanced_prompt.lower() for structure in 
                                     ["systematic", "comprehensive", "multi-layered", "advanced", "professional"]),
            "technical_depth": any(term in enhanced_prompt.lower() for term in 
                                 ["analysis", "implementation", "validation", "integration", "architecture"]),
            "engagement_elements": any(element in enhanced_prompt.lower() for element in 
                                     ["engagement", "retention", "audience", "psychology", "triggers"])
        }
        
        failed_checks = [check for check, passed in quality_checks.items() if not passed]
        
        if failed_checks:
            self.log_test("Enhanced Prompt Quality Validation", False,
                         f"Quality checks failed: {failed_checks}")
            return
            
        # Calculate quality score
        quality_score = sum(quality_checks.values()) / len(quality_checks)
        
        self.log_test("Enhanced Prompt Quality Validation", True,
                     f"Quality validation passed: {quality_score:.1%} score, {len(enhanced_prompt)} chars")
                     
    async def test_segmentation_integration_validation(self):
        """Test that enhanced system integrates properly with segmentation"""
        test_data = {
            "duration": "extended_20",
            "segmentation_plan": {
                "total_segments": 4,
                "segment_duration": 5.6,
                "complexity_level": "advanced",
                "narrative_structure": "progressive"
            }
        }
        
        success, response, status = await self.make_request("POST", "/validate-template-compatibility", test_data)
        
        if not success:
            self.log_test("Segmentation Integration Validation", False,
                         f"Request failed: {response}")
            return
            
        # Validate compatibility analysis
        analysis = response.get("analysis", {})
        required_analysis_fields = ["segment_compatibility", "duration_alignment", "complexity_match"]
        missing_analysis_fields = [field for field in required_analysis_fields if field not in analysis]
        
        if missing_analysis_fields:
            self.log_test("Segmentation Integration Validation", False,
                         f"Missing analysis fields: {missing_analysis_fields}")
            return
            
        # Validate compatibility score
        compatibility_score = response.get("compatibility_score", 0)
        if compatibility_score < 0.7:  # Expect high compatibility for well-matched plans
            self.log_test("Segmentation Integration Validation", False,
                         f"Low compatibility score: {compatibility_score}")
            return
            
        self.log_test("Segmentation Integration Validation", True,
                     f"Segmentation integration validated with {compatibility_score:.3f} compatibility")
                     
    # ========================================
    # 5. PERFORMANCE AND ERROR HANDLING TESTING
    # ========================================
    
    async def test_error_handling_validation(self):
        """Test proper error handling for invalid requests"""
        error_test_cases = [
            {
                "name": "Invalid Duration",
                "endpoint": "/enhanced-prompt-templates/invalid_duration",
                "method": "GET",
                "expected_status": 400
            },
            {
                "name": "Missing Required Fields",
                "endpoint": "/enhanced-prompt-templates",
                "method": "POST",
                "data": {"invalid_field": "test"},
                "expected_status": 422
            },
            {
                "name": "Invalid Compatibility Request",
                "endpoint": "/validate-template-compatibility",
                "method": "POST",
                "data": {"duration": "invalid"},
                "expected_status": 400
            }
        ]
        
        for test_case in error_test_cases:
            if test_case["method"] == "GET":
                success, response, status = await self.make_request("GET", test_case["endpoint"])
            else:
                success, response, status = await self.make_request("POST", test_case["endpoint"], test_case.get("data", {}))
                
            expected_status = test_case["expected_status"]
            
            if status == expected_status:
                self.log_test(f"Error Handling - {test_case['name']}", True,
                             f"Correctly returned status {status}")
            else:
                self.log_test(f"Error Handling - {test_case['name']}", False,
                             f"Expected status {expected_status}, got {status}")
                             
    async def test_system_performance_validation(self):
        """Test system performance and response times"""
        performance_tests = [
            {
                "name": "Template List Performance",
                "endpoint": "/enhanced-prompt-templates",
                "method": "GET",
                "max_time": 5.0
            },
            {
                "name": "Template Generation Performance",
                "endpoint": "/enhanced-prompt-templates",
                "method": "POST",
                "data": {
                    "duration": "extended_15",
                    "video_type": "general",
                    "customization_options": {}
                },
                "max_time": 30.0
            }
        ]
        
        for test in performance_tests:
            start_time = time.time()
            
            if test["method"] == "GET":
                success, response, status = await self.make_request("GET", test["endpoint"])
            else:
                success, response, status = await self.make_request("POST", test["endpoint"], test.get("data", {}))
                
            end_time = time.time()
            duration = end_time - start_time
            
            if success and duration <= test["max_time"]:
                self.log_test(f"Performance - {test['name']}", True,
                             f"Completed in {duration:.2f}s (limit: {test['max_time']}s)")
            else:
                self.log_test(f"Performance - {test['name']}", False,
                             f"Failed or too slow: {duration:.2f}s (limit: {test['max_time']}s)")
                             
    # ========================================
    # MAIN TEST EXECUTION
    # ========================================
    
    async def run_all_tests(self):
        """Run all Enhanced Prompt Architecture tests"""
        print("🚀 Starting Phase 5.1 Enhanced Prompt Architecture Backend Testing Suite")
        print("=" * 80)
        print()
        
        await self.setup()
        
        try:
            # 1. Enhanced Prompt Architecture API Endpoints Testing
            print("📋 1. ENHANCED PROMPT ARCHITECTURE API ENDPOINTS TESTING")
            print("-" * 60)
            await self.test_enhanced_prompt_templates_list_endpoint()
            await self.test_enhanced_prompt_templates_generation_endpoint()
            await self.test_duration_specific_template_endpoints()
            await self.test_template_compatibility_validation_endpoint()
            print()
            
            # 2. Main Script Generation Integration Testing
            print("🔗 2. MAIN SCRIPT GENERATION INTEGRATION TESTING")
            print("-" * 60)
            await self.test_enhanced_script_generation_integration()
            await self.test_backward_compatibility_script_generation()
            print()
            
            # 3. Template System Validation Testing
            print("🎯 3. TEMPLATE SYSTEM VALIDATION TESTING")
            print("-" * 60)
            await self.test_template_registry_validation()
            await self.test_video_type_customization()
            print()
            
            # 4. Quality Validation Testing
            print("✨ 4. QUALITY VALIDATION TESTING")
            print("-" * 60)
            await self.test_enhanced_prompt_quality_validation()
            await self.test_segmentation_integration_validation()
            print()
            
            # 5. Performance and Error Handling Testing
            print("⚡ 5. PERFORMANCE AND ERROR HANDLING TESTING")
            print("-" * 60)
            await self.test_error_handling_validation()
            await self.test_system_performance_validation()
            print()
            
        finally:
            await self.teardown()
            
        # Print final results
        self.print_final_results()
        
    def print_final_results(self):
        """Print comprehensive test results summary"""
        print("=" * 80)
        print("🎉 PHASE 5.1 ENHANCED PROMPT ARCHITECTURE TESTING RESULTS")
        print("=" * 80)
        print()
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test_name']}: {result['details']}")
            print()
            
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["passed"]:
                print(f"   • {result['test_name']}")
        print()
        
        # Assessment
        if success_rate >= 90:
            assessment = "🎉 EXCELLENT - System is production-ready"
        elif success_rate >= 75:
            assessment = "✅ GOOD - System is mostly functional with minor issues"
        elif success_rate >= 50:
            assessment = "⚠️ FAIR - System has significant issues requiring attention"
        else:
            assessment = "❌ POOR - System has critical issues requiring major fixes"
            
        print(f"🏆 ASSESSMENT: {assessment}")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Analyze results by category
        categories = {
            "API Endpoints": [r for r in self.test_results if "endpoint" in r["test_name"].lower()],
            "Script Generation": [r for r in self.test_results if "script generation" in r["test_name"].lower()],
            "Template System": [r for r in self.test_results if "template" in r["test_name"].lower() and "endpoint" not in r["test_name"].lower()],
            "Quality Validation": [r for r in self.test_results if "quality" in r["test_name"].lower()],
            "Performance": [r for r in self.test_results if "performance" in r["test_name"].lower() or "error handling" in r["test_name"].lower()]
        }
        
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for t in tests if t["passed"])
                total = len(tests)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"   • {category}: {passed}/{total} ({rate:.1f}%)")
                
        print()
        print("=" * 80)

async def main():
    """Main test execution function"""
    test_suite = EnhancedPromptArchitectureTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
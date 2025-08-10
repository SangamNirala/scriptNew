#!/usr/bin/env python3
"""
Phase 2.3 Implementation Testing: 20-25 Minute Deep Dive Content Expert Template
Backend Testing Suite for Duration-Specific Template System

This test suite validates the Phase 2.3 implementation of the 20-25 Minute Deep Dive Content Expert
template functionality as specified in the review request.

Test Coverage:
1. Test create_20_25_minute_template() method in DurationSpecificPromptGenerator
2. Verify template meets all Phase 2.3 requirements
3. Test template word count validation (500+ words)
4. Test async generate_20_25_minute_template() method
5. Verify integration with enhanced prompt architecture
6. Check implementation status shows Phase 2.3 as complete
7. Test template system status endpoint
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.insert(0, '/app/backend')

# Import required modules
import requests
from lib.duration_specific_templates import (
    DurationSpecificPromptGenerator, 
    TemplateArchitectureConfig,
    DURATION_PROMPT_TEMPLATES,
    TemplateValidationError
)
from lib.prompt_template_registry import PromptTemplateRegistry, TemplateContent
from lib.enhanced_prompt_architecture import EnhancedPromptArchitecture

# Test configuration
BACKEND_URL = "https://f5f1bcd3-1e7e-4f94-9ffa-0d0d9163f7bc.preview.emergentagent.com"
API_BASE_URL = f"{BACKEND_URL}/api"

class Phase23TestSuite:
    """Comprehensive test suite for Phase 2.3 implementation"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = time.time()
        
        # Initialize components for testing
        self.config = TemplateArchitectureConfig(
            minimum_word_count=500,
            expertise_depth_requirement="professional",
            framework_integration_required=True,
            video_type_customization=True,
            segmentation_compatibility=True,
            quality_validation_enabled=True,
            performance_optimization=True
        )
        
        self.generator = DurationSpecificPromptGenerator(self.config)
        
        print("🚀 Phase 2.3 Implementation Testing: 20-25 Minute Deep Dive Content Expert")
        print("=" * 80)
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Log test result with details"""
        self.total_tests += 1
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
            "details": details,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def test_create_20_25_minute_template_method(self):
        """Test 1: Test the create_20_25_minute_template() method"""
        try:
            template = self.generator.create_20_25_minute_template()
            
            # Verify template structure
            required_keys = [
                "template_id", "template_name", "duration_category", 
                "expertise_level", "complexity", "focus", "template_content",
                "specification", "creation_metadata"
            ]
            
            missing_keys = [key for key in required_keys if key not in template]
            if missing_keys:
                self.log_test_result(
                    "create_20_25_minute_template() - Structure",
                    False,
                    error=f"Missing required keys: {missing_keys}"
                )
                return
            
            # Verify template content structure
            template_content = template.get("template_content")
            if not isinstance(template_content, TemplateContent):
                self.log_test_result(
                    "create_20_25_minute_template() - Content Type",
                    False,
                    error="template_content is not a TemplateContent instance"
                )
                return
            
            self.log_test_result(
                "create_20_25_minute_template() - Method Execution",
                True,
                f"Template created successfully with ID: {template['template_id'][:8]}..."
            )
            
            return template
            
        except Exception as e:
            self.log_test_result(
                "create_20_25_minute_template() - Method Execution",
                False,
                error=str(e)
            )
            return None
    
    def test_template_phase_23_requirements(self):
        """Test 2: Verify template meets all Phase 2.3 requirements"""
        try:
            template = self.generator.create_20_25_minute_template()
            
            # Test template name requirement
            expected_name = "20-25 Minute Deep Dive Content Expert"
            actual_name = template.get("template_name", "")
            
            if actual_name != expected_name:
                self.log_test_result(
                    "Phase 2.3 Requirements - Template Name",
                    False,
                    error=f"Expected '{expected_name}', got '{actual_name}'"
                )
                return
            
            # Test expertise requirement
            expected_expertise = "expert"
            actual_expertise = template.get("expertise_level", "")
            
            if actual_expertise != expected_expertise:
                self.log_test_result(
                    "Phase 2.3 Requirements - Expertise Level",
                    False,
                    error=f"Expected '{expected_expertise}', got '{actual_expertise}'"
                )
                return
            
            # Test segment optimization requirement (4-5 segments)
            spec = template.get("specification", {})
            segment_count_range = spec.get("segment_count_range", [])
            
            if segment_count_range != [4, 5]:
                self.log_test_result(
                    "Phase 2.3 Requirements - Segment Optimization",
                    False,
                    error=f"Expected [4, 5] segments, got {segment_count_range}"
                )
                return
            
            # Test content depth requirement
            expected_complexity = "deep_dive_content_structuring"
            actual_complexity = spec.get("complexity", "")
            
            if expected_complexity not in actual_complexity:
                self.log_test_result(
                    "Phase 2.3 Requirements - Content Depth",
                    False,
                    error=f"Expected deep dive content structuring, got '{actual_complexity}'"
                )
                return
            
            # Test engagement strategy requirement
            expected_focus = "sustained_engagement_algorithms"
            actual_focus = spec.get("focus", "")
            
            if expected_focus not in actual_focus:
                self.log_test_result(
                    "Phase 2.3 Requirements - Engagement Strategy",
                    False,
                    error=f"Expected sustained engagement algorithms, got '{actual_focus}'"
                )
                return
            
            self.log_test_result(
                "Phase 2.3 Requirements - All Requirements Met",
                True,
                f"Template name: {actual_name}, Expertise: {actual_expertise}, Segments: {segment_count_range}, Complexity: Deep dive, Focus: Sustained engagement"
            )
            
        except Exception as e:
            self.log_test_result(
                "Phase 2.3 Requirements - Verification",
                False,
                error=str(e)
            )
    
    def test_template_word_count_validation(self):
        """Test 3: Test template word count validation (500+ words)"""
        try:
            template = self.generator.create_20_25_minute_template()
            template_content = template.get("template_content")
            
            if not template_content:
                self.log_test_result(
                    "Word Count Validation - Content Exists",
                    False,
                    error="No template_content found"
                )
                return
            
            word_count = template_content.get_word_count()
            
            if word_count < 500:
                self.log_test_result(
                    "Word Count Validation - Minimum Requirement",
                    False,
                    error=f"Word count {word_count} is below minimum 500 words"
                )
                return
            
            # Test individual sections have substantial content
            sections = {
                "system_prompt": template_content.system_prompt,
                "expertise_description": template_content.expertise_description,
                "framework_instructions": template_content.framework_instructions,
                "segment_guidelines": template_content.segment_guidelines,
                "quality_standards": template_content.quality_standards
            }
            
            section_word_counts = {}
            for section_name, content in sections.items():
                section_word_count = len(content.split()) if content else 0
                section_word_counts[section_name] = section_word_count
            
            # Verify system prompt is substantial (should be majority of content)
            system_prompt_words = section_word_counts.get("system_prompt", 0)
            if system_prompt_words < 300:
                self.log_test_result(
                    "Word Count Validation - System Prompt Depth",
                    False,
                    error=f"System prompt only {system_prompt_words} words, expected 300+"
                )
                return
            
            self.log_test_result(
                "Word Count Validation - 500+ Words Requirement",
                True,
                f"Total word count: {word_count} words (exceeds 500+ requirement). System prompt: {system_prompt_words} words"
            )
            
        except Exception as e:
            self.log_test_result(
                "Word Count Validation - Test Execution",
                False,
                error=str(e)
            )
    
    async def test_async_generate_20_25_minute_template(self):
        """Test 4: Test async generate_20_25_minute_template() method"""
        try:
            # Test with different video types
            video_types = ["general", "educational", "marketing", "entertainment"]
            
            for video_type in video_types:
                template = await self.generator.generate_20_25_minute_template(
                    video_type=video_type,
                    customization_options={"test_mode": True}
                )
                
                # Verify template was generated
                if not template:
                    self.log_test_result(
                        f"Async Generate Template - {video_type}",
                        False,
                        error="No template returned"
                    )
                    continue
                
                # Verify generation metadata
                gen_metadata = template.get("generation_metadata", {})
                if gen_metadata.get("video_type") != video_type:
                    self.log_test_result(
                        f"Async Generate Template - {video_type} Metadata",
                        False,
                        error=f"Video type mismatch in metadata"
                    )
                    continue
                
                # Verify customization was applied
                if not gen_metadata.get("customization_applied"):
                    self.log_test_result(
                        f"Async Generate Template - {video_type} Customization",
                        False,
                        error="Customization not applied"
                    )
                    continue
            
            self.log_test_result(
                "Async Generate Template - All Video Types",
                True,
                f"Successfully generated templates for {len(video_types)} video types with customization"
            )
            
        except Exception as e:
            self.log_test_result(
                "Async Generate Template - Method Execution",
                False,
                error=str(e)
            )
    
    def test_enhanced_prompt_architecture_integration(self):
        """Test 5: Verify integration with enhanced prompt architecture for extended_20 duration"""
        try:
            # Test that extended_20 is supported
            supported_durations = self.generator.get_supported_durations()
            
            if "extended_20" not in supported_durations:
                self.log_test_result(
                    "Enhanced Prompt Architecture Integration - Duration Support",
                    False,
                    error="extended_20 duration not in supported durations"
                )
                return
            
            # Test template specification exists for extended_20
            if "extended_20" not in DURATION_PROMPT_TEMPLATES:
                self.log_test_result(
                    "Enhanced Prompt Architecture Integration - Template Spec",
                    False,
                    error="extended_20 template specification not found"
                )
                return
            
            # Test template specification details
            spec = DURATION_PROMPT_TEMPLATES["extended_20"]
            
            # Verify specification matches Phase 2.3 requirements
            if spec.name != "20-25 Minute Deep Dive Content Expert":
                self.log_test_result(
                    "Enhanced Prompt Architecture Integration - Spec Name",
                    False,
                    error=f"Spec name mismatch: {spec.name}"
                )
                return
            
            if spec.expertise_level.value != "expert":
                self.log_test_result(
                    "Enhanced Prompt Architecture Integration - Spec Expertise",
                    False,
                    error=f"Expertise level mismatch: {spec.expertise_level.value}"
                )
                return
            
            if spec.segment_count_range != (4, 5):
                self.log_test_result(
                    "Enhanced Prompt Architecture Integration - Spec Segments",
                    False,
                    error=f"Segment count range mismatch: {spec.segment_count_range}"
                )
                return
            
            self.log_test_result(
                "Enhanced Prompt Architecture Integration - extended_20 Duration",
                True,
                f"extended_20 fully integrated with correct specification: {spec.name}, {spec.expertise_level.value}, {spec.segment_count_range} segments"
            )
            
        except Exception as e:
            self.log_test_result(
                "Enhanced Prompt Architecture Integration - Test Execution",
                False,
                error=str(e)
            )
    
    def test_implementation_status_phase_23_complete(self):
        """Test 6: Check implementation status shows Phase 2.3 as complete"""
        try:
            status = self.generator.get_implementation_status()
            
            # Check if Phase 2.3 is marked as complete
            if not status.get("phase_2_3_complete", False):
                self.log_test_result(
                    "Implementation Status - Phase 2.3 Complete Flag",
                    False,
                    error="phase_2_3_complete not set to True"
                )
                return
            
            # Check extended_20 template status
            extended_20_status = status.get("extended_20_template", "")
            if extended_20_status != "implemented":
                self.log_test_result(
                    "Implementation Status - extended_20 Template",
                    False,
                    error=f"extended_20_template status is '{extended_20_status}', expected 'implemented'"
                )
                return
            
            # Check current milestone
            current_milestone = status.get("current_milestone", "")
            if "Phase 2.3" not in current_milestone:
                self.log_test_result(
                    "Implementation Status - Current Milestone",
                    False,
                    error=f"Current milestone doesn't mention Phase 2.3: {current_milestone}"
                )
                return
            
            self.log_test_result(
                "Implementation Status - Phase 2.3 Complete",
                True,
                f"Phase 2.3 marked as complete, extended_20 template implemented, milestone: {current_milestone}"
            )
            
        except Exception as e:
            self.log_test_result(
                "Implementation Status - Test Execution",
                False,
                error=str(e)
            )
    
    def test_template_system_status_endpoint(self):
        """Test 7: Test /api/template-system-status endpoint for new template availability"""
        try:
            response = requests.get(f"{API_BASE_URL}/template-system-status", timeout=30)
            
            if response.status_code != 200:
                self.log_test_result(
                    "Template System Status Endpoint - HTTP Response",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return
            
            data = response.json()
            
            # Check overall status
            if data.get("status") != "operational":
                self.log_test_result(
                    "Template System Status Endpoint - System Status",
                    False,
                    error=f"System status is '{data.get('status')}', expected 'operational'"
                )
                return
            
            # Check Phase 2.3 completion in integration verification
            integration_verification = data.get("integration_verification", {})
            if not integration_verification.get("phase_2_3_complete", False):
                self.log_test_result(
                    "Template System Status Endpoint - Phase 2.3 Integration",
                    False,
                    error="phase_2_3_complete not True in integration_verification"
                )
                return
            
            # Check Phase 2.3 template test results
            phase_2_3_test = data.get("duration_specific_generator", {}).get("phase_2_3_template_test", {})
            
            if not phase_2_3_test.get("creation_successful", False):
                self.log_test_result(
                    "Template System Status Endpoint - Phase 2.3 Template Creation",
                    False,
                    error="Phase 2.3 template creation test failed"
                )
                return
            
            word_count = phase_2_3_test.get("word_count", 0)
            if word_count < 500:
                self.log_test_result(
                    "Template System Status Endpoint - Phase 2.3 Word Count",
                    False,
                    error=f"Phase 2.3 template word count {word_count} below 500"
                )
                return
            
            template_name = phase_2_3_test.get("template_name", "")
            if template_name != "20-25 Minute Deep Dive Content Expert":
                self.log_test_result(
                    "Template System Status Endpoint - Phase 2.3 Template Name",
                    False,
                    error=f"Template name mismatch: {template_name}"
                )
                return
            
            # Check current milestone
            current_milestone = data.get("next_phases", {}).get("current_milestone", "")
            if "Phase 2.3 Complete" not in current_milestone:
                self.log_test_result(
                    "Template System Status Endpoint - Current Milestone",
                    False,
                    error=f"Current milestone doesn't indicate Phase 2.3 complete: {current_milestone}"
                )
                return
            
            self.log_test_result(
                "Template System Status Endpoint - Phase 2.3 Template Available",
                True,
                f"Template available via API: {template_name}, {word_count} words, creation successful, Phase 2.3 complete"
            )
            
        except requests.exceptions.RequestException as e:
            self.log_test_result(
                "Template System Status Endpoint - Network Request",
                False,
                error=f"Request failed: {str(e)}"
            )
        except Exception as e:
            self.log_test_result(
                "Template System Status Endpoint - Test Execution",
                False,
                error=str(e)
            )
    
    def test_template_content_structure_validation(self):
        """Test 8: Validate template content structure includes all required sections"""
        try:
            template = self.generator.create_20_25_minute_template()
            template_content = template.get("template_content")
            
            if not template_content:
                self.log_test_result(
                    "Template Content Structure - Content Exists",
                    False,
                    error="No template_content found"
                )
                return
            
            # Check required sections exist
            required_sections = [
                "system_prompt", "expertise_description", "framework_instructions",
                "segment_guidelines", "quality_standards"
            ]
            
            missing_sections = []
            for section in required_sections:
                content = getattr(template_content, section, "")
                if not content or len(content.strip()) == 0:
                    missing_sections.append(section)
            
            if missing_sections:
                self.log_test_result(
                    "Template Content Structure - Required Sections",
                    False,
                    error=f"Missing or empty sections: {missing_sections}"
                )
                return
            
            # Check system prompt contains key expertise indicators
            system_prompt = template_content.system_prompt
            expertise_indicators = [
                "20-25 Minute Deep Dive Content Expert",
                "master of long-form video content",
                "4-5 segment advanced structuring",
                "sustained engagement algorithms",
                "deep dive content structuring"
            ]
            
            missing_indicators = []
            for indicator in expertise_indicators:
                if indicator.lower() not in system_prompt.lower():
                    missing_indicators.append(indicator)
            
            if missing_indicators:
                self.log_test_result(
                    "Template Content Structure - Expertise Indicators",
                    False,
                    error=f"Missing expertise indicators in system prompt: {missing_indicators}"
                )
                return
            
            # Check segment guidelines mention 4-5 segments
            segment_guidelines = template_content.segment_guidelines
            if "4-5 segment" not in segment_guidelines:
                self.log_test_result(
                    "Template Content Structure - Segment Guidelines",
                    False,
                    error="Segment guidelines don't mention 4-5 segments"
                )
                return
            
            self.log_test_result(
                "Template Content Structure - All Required Sections",
                True,
                f"All {len(required_sections)} required sections present with proper content and expertise indicators"
            )
            
        except Exception as e:
            self.log_test_result(
                "Template Content Structure - Test Execution",
                False,
                error=str(e)
            )
    
    async def run_all_tests(self):
        """Run all Phase 2.3 implementation tests"""
        print("Starting Phase 2.3 Implementation Test Suite...")
        print()
        
        # Test 1: Basic method execution
        self.test_create_20_25_minute_template_method()
        
        # Test 2: Phase 2.3 requirements verification
        self.test_template_phase_23_requirements()
        
        # Test 3: Word count validation
        self.test_template_word_count_validation()
        
        # Test 4: Async method testing
        await self.test_async_generate_20_25_minute_template()
        
        # Test 5: Enhanced prompt architecture integration
        self.test_enhanced_prompt_architecture_integration()
        
        # Test 6: Implementation status verification
        self.test_implementation_status_phase_23_complete()
        
        # Test 7: API endpoint testing
        self.test_template_system_status_endpoint()
        
        # Test 8: Template content structure validation
        self.test_template_content_structure_validation()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        print("=" * 80)
        print("🎯 PHASE 2.3 IMPLEMENTATION TEST RESULTS")
        print("=" * 80)
        print()
        
        print(f"📊 TEST SUMMARY:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"   Duration: {duration:.2f} seconds")
        print()
        
        if self.failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test_name']}")
                    if result["error"]:
                        print(f"     Error: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["passed"]:
                print(f"   • {result['test_name']}")
                if result["details"]:
                    print(f"     Details: {result['details']}")
        print()
        
        # Critical validation points summary
        print("🔍 CRITICAL VALIDATION POINTS:")
        
        critical_tests = [
            "create_20_25_minute_template() - Method Execution",
            "Phase 2.3 Requirements - All Requirements Met", 
            "Word Count Validation - 500+ Words Requirement",
            "Template System Status Endpoint - Phase 2.3 Template Available",
            "Implementation Status - Phase 2.3 Complete"
        ]
        
        critical_passed = 0
        for test_name in critical_tests:
            result = next((r for r in self.test_results if r["test_name"] == test_name), None)
            if result and result["passed"]:
                critical_passed += 1
                print(f"   ✅ {test_name}")
            else:
                print(f"   ❌ {test_name}")
        
        print()
        print(f"Critical Tests Passed: {critical_passed}/{len(critical_tests)}")
        
        # Overall assessment
        if self.failed_tests == 0:
            print("🎉 PHASE 2.3 IMPLEMENTATION: FULLY SUCCESSFUL")
            print("   All tests passed. The 20-25 Minute Deep Dive Content Expert template")
            print("   functionality is working correctly and meets all requirements.")
        elif critical_passed == len(critical_tests):
            print("✅ PHASE 2.3 IMPLEMENTATION: CORE FUNCTIONALITY WORKING")
            print("   All critical tests passed. Minor issues detected but core functionality")
            print("   is operational and meets Phase 2.3 requirements.")
        else:
            print("⚠️  PHASE 2.3 IMPLEMENTATION: ISSUES DETECTED")
            print("   Some critical tests failed. Review failed tests for implementation issues.")
        
        print()
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": self.passed_tests/self.total_tests*100 if self.total_tests > 0 else 0,
            "duration": duration,
            "critical_tests_passed": critical_passed,
            "critical_tests_total": len(critical_tests),
            "overall_status": "success" if self.failed_tests == 0 else "partial_success" if critical_passed == len(critical_tests) else "failure",
            "test_results": self.test_results
        }

async def main():
    """Main test execution function"""
    test_suite = Phase23TestSuite()
    
    try:
        await test_suite.run_all_tests()
        report = test_suite.generate_test_report()
        
        # Save detailed results to file
        with open('/app/phase_23_test_results.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Detailed test results saved to: /app/phase_23_test_results.json")
        
        return report
        
    except Exception as e:
        print(f"❌ Test suite execution failed: {str(e)}")
        return {"error": str(e), "status": "execution_failed"}

if __name__ == "__main__":
    # Run the test suite
    result = asyncio.run(main())
    
    # Exit with appropriate code
    if result.get("overall_status") == "success":
        sys.exit(0)
    else:
        sys.exit(1)
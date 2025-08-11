#!/usr/bin/env python3
"""
Backend Testing Suite for Phase 2.4: 25-30 Minute Template Implementation
Enhanced Prompt Engineering Architecture Testing

This test suite validates the Phase 2.4 implementation of the 25-30 Minute Template
for the Enhanced Prompt Engineering Architecture system.

Test Coverage:
1. New Template Creation Test (create_25_30_minute_template)
2. Template Generation Test (generate_25_30_minute_template)
3. Integration Status Verification (/api/template-system-status)
4. Template Specification Validation
5. Duration Support Test
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.append('/app/backend')

# Import backend components for direct testing
from lib.duration_specific_templates import DurationSpecificPromptGenerator, DURATION_PROMPT_TEMPLATES
from lib.enhanced_prompt_architecture import EnhancedPromptArchitecture

class Phase24TemplateTestSuite:
    """Comprehensive test suite for Phase 2.4: 25-30 Minute Template Implementation"""
    
    def __init__(self):
        self.backend_url = "https://7ddca776-a8d1-40eb-a60b-df8e9c11de93.preview.emergentagent.com/api"
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Initialize components for direct testing
        self.duration_generator = DurationSpecificPromptGenerator()
        
        print("🚀 Phase 2.4: 25-30 Minute Template Implementation Test Suite")
        print("=" * 80)
    
    async def run_all_tests(self):
        """Run all Phase 2.4 tests"""
        print(f"⏰ Starting comprehensive Phase 2.4 testing at {datetime.now().isoformat()}")
        print()
        
        # Test 1: New Template Creation Test
        await self.test_create_25_30_minute_template()
        
        # Test 2: Template Generation Test
        await self.test_generate_25_30_minute_template()
        
        # Test 3: Integration Status Verification
        await self.test_integration_status_verification()
        
        # Test 4: Template Specification Validation
        await self.test_template_specification_validation()
        
        # Test 5: Duration Support Test
        await self.test_duration_support()
        
        # Print final results
        self.print_final_results()
    
    async def test_create_25_30_minute_template(self):
        """Test 1: New Template Creation Test"""
        print("🧪 TEST 1: New Template Creation Test")
        print("-" * 50)
        
        try:
            # Test create_25_30_minute_template() method
            template = self.duration_generator.create_25_30_minute_template()
            
            # Validate template structure
            required_fields = ['template_id', 'template_name', 'duration_category', 'expertise_level', 
                             'complexity', 'focus', 'template_content', 'specification']
            
            missing_fields = [field for field in required_fields if field not in template]
            if missing_fields:
                self.record_test_result("Template Structure Validation", False, 
                                      f"Missing required fields: {missing_fields}")
                return
            
            self.record_test_result("Template Structure Validation", True, 
                                  f"All required fields present: {list(template.keys())}")
            
            # Validate template content
            template_content = template.get('template_content')
            if not template_content:
                self.record_test_result("Template Content Validation", False, "Template content is missing")
                return
            
            # Check word count (must be 500+ words)
            word_count = template_content.get_word_count()
            word_count_pass = word_count >= 500
            
            self.record_test_result("Word Count Validation (500+ words)", word_count_pass, 
                                  f"Word count: {word_count} words")
            
            # Validate template name matches specification
            expected_name = "25-30 Minute Comprehensive Content Architect"
            actual_name = template.get('template_name', '')
            name_match = expected_name == actual_name
            
            self.record_test_result("Template Name Validation", name_match, 
                                  f"Expected: '{expected_name}', Got: '{actual_name}'")
            
            # Validate expertise level
            expected_expertise = "architect"
            actual_expertise = template.get('expertise_level', '')
            expertise_match = expected_expertise == actual_expertise
            
            self.record_test_result("Expertise Level Validation", expertise_match, 
                                  f"Expected: '{expected_expertise}', Got: '{actual_expertise}'")
            
            # Validate complexity
            expected_complexity = "comprehensive_content_architecture"
            actual_complexity = template.get('complexity', '')
            complexity_match = expected_complexity == actual_complexity
            
            self.record_test_result("Complexity Validation", complexity_match, 
                                  f"Expected: '{expected_complexity}', Got: '{actual_complexity}'")
            
            # Validate focus strategy
            expected_focus = "peak_engagement_distribution"
            actual_focus = template.get('focus', '')
            focus_match = expected_focus == actual_focus
            
            self.record_test_result("Focus Strategy Validation", focus_match, 
                                  f"Expected: '{expected_focus}', Got: '{actual_focus}'")
            
            print(f"✅ Template creation successful: {template['template_id']}")
            print(f"📊 Template metrics: {word_count} words, {actual_expertise} level")
            print()
            
        except Exception as e:
            self.record_test_result("Template Creation", False, f"Exception: {str(e)}")
            print(f"❌ Template creation failed: {str(e)}")
            print()
    
    async def test_generate_25_30_minute_template(self):
        """Test 2: Template Generation Test with different video types"""
        print("🧪 TEST 2: Template Generation Test")
        print("-" * 50)
        
        video_types = ["educational", "marketing", "entertainment", "general"]
        
        for video_type in video_types:
            try:
                print(f"  Testing video type: {video_type}")
                
                # Test generate_25_30_minute_template() method
                customization_options = {
                    "complexity_preference": "comprehensive",
                    "focus_areas": ["engagement", "expertise"]
                }
                
                generated_template = await self.duration_generator.generate_25_30_minute_template(
                    video_type=video_type,
                    customization_options=customization_options
                )
                
                # Validate generated template
                if not generated_template:
                    self.record_test_result(f"Template Generation ({video_type})", False, 
                                          "Generated template is empty")
                    continue
                
                # Check if customization was applied
                generation_metadata = generated_template.get('generation_metadata', {})
                video_type_match = generation_metadata.get('video_type') == video_type
                customization_applied = generation_metadata.get('customization_applied', False)
                
                self.record_test_result(f"Template Generation ({video_type})", True, 
                                      f"Generated successfully with customization: {customization_applied}")
                
                # Validate template content word count
                template_content = generated_template.get('template_content')
                if template_content:
                    word_count = template_content.get_word_count()
                    word_count_pass = word_count >= 500
                    
                    self.record_test_result(f"Generated Template Word Count ({video_type})", word_count_pass, 
                                          f"Word count: {word_count} words")
                
                print(f"    ✅ {video_type.title()} template generated successfully")
                
            except Exception as e:
                self.record_test_result(f"Template Generation ({video_type})", False, f"Exception: {str(e)}")
                print(f"    ❌ {video_type.title()} template generation failed: {str(e)}")
        
        print()
    
    async def test_integration_status_verification(self):
        """Test 3: Integration Status Verification"""
        print("🧪 TEST 3: Integration Status Verification")
        print("-" * 50)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test /api/template-system-status endpoint
                async with session.get(f"{self.backend_url}/template-system-status") as response:
                    if response.status != 200:
                        self.record_test_result("API Endpoint Access", False, 
                                              f"HTTP {response.status}: {await response.text()}")
                        return
                    
                    status_data = await response.json()
                    
                    # Validate Phase 2.4 completion status
                    integration_verification = status_data.get('integration_verification', {})
                    phase_2_4_complete = integration_verification.get('phase_2_4_complete', False)
                    
                    self.record_test_result("Phase 2.4 Complete Status", phase_2_4_complete, 
                                          f"Phase 2.4 marked as complete: {phase_2_4_complete}")
                    
                    # Validate phase_2_4_template_test results
                    duration_generator_data = status_data.get('duration_specific_generator', {})
                    phase_2_4_test = duration_generator_data.get('phase_2_4_template_test', {})
                    
                    creation_successful = phase_2_4_test.get('creation_successful', False)
                    word_count = phase_2_4_test.get('word_count', 0)
                    meets_500_requirement = phase_2_4_test.get('meets_500_word_requirement', False)
                    template_name = phase_2_4_test.get('template_name', '')
                    
                    self.record_test_result("Phase 2.4 Template Test - Creation", creation_successful, 
                                          f"Template creation successful: {creation_successful}")
                    
                    self.record_test_result("Phase 2.4 Template Test - Word Count", meets_500_requirement, 
                                          f"Word count: {word_count}, Meets 500+ requirement: {meets_500_requirement}")
                    
                    expected_template_name = "25-30 Minute Comprehensive Content Architect"
                    name_match = template_name == expected_template_name
                    
                    self.record_test_result("Phase 2.4 Template Test - Name", name_match, 
                                          f"Expected: '{expected_template_name}', Got: '{template_name}'")
                    
                    # Validate implementation_status shows "extended_25" as "implemented"
                    implementation_status = duration_generator_data.get('implementation_status', {})
                    extended_25_status = implementation_status.get('extended_25_template', '')
                    extended_25_implemented = extended_25_status == "implemented"
                    
                    self.record_test_result("Extended_25 Implementation Status", extended_25_implemented, 
                                          f"extended_25 status: '{extended_25_status}'")
                    
                    print(f"✅ Integration status verification completed")
                    print(f"📊 Phase 2.4 status: Complete={phase_2_4_complete}, Word count={word_count}")
                    print()
                    
        except Exception as e:
            self.record_test_result("Integration Status Verification", False, f"Exception: {str(e)}")
            print(f"❌ Integration status verification failed: {str(e)}")
            print()
    
    async def test_template_specification_validation(self):
        """Test 4: Template Specification Validation"""
        print("🧪 TEST 4: Template Specification Validation")
        print("-" * 50)
        
        try:
            # Get extended_25 template specification
            extended_25_spec = DURATION_PROMPT_TEMPLATES.get('extended_25')
            
            if not extended_25_spec:
                self.record_test_result("Template Specification Exists", False, 
                                      "extended_25 specification not found")
                return
            
            self.record_test_result("Template Specification Exists", True, 
                                  "extended_25 specification found")
            
            # Validate 5-6 segment support
            segment_count_range = extended_25_spec.segment_count_range
            expected_range = (5, 6)
            segment_range_correct = segment_count_range == expected_range
            
            self.record_test_result("5-6 Segment Support", segment_range_correct, 
                                  f"Segment range: {segment_count_range}, Expected: {expected_range}")
            
            # Validate expertise level is "architect"
            expertise_level = extended_25_spec.expertise_level.value
            expected_expertise = "architect"
            expertise_correct = expertise_level == expected_expertise
            
            self.record_test_result("Expertise Level 'architect'", expertise_correct, 
                                  f"Expertise level: '{expertise_level}', Expected: '{expected_expertise}'")
            
            # Validate complexity is "comprehensive"
            complexity = extended_25_spec.complexity.value
            expected_complexity = "comprehensive_content_architecture"
            complexity_correct = complexity == expected_complexity
            
            self.record_test_result("Complexity 'comprehensive'", complexity_correct, 
                                  f"Complexity: '{complexity}', Expected: '{expected_complexity}'")
            
            # Validate focus strategy is "peak_engagement_distribution"
            focus_strategy = extended_25_spec.focus.value
            expected_focus = "peak_engagement_distribution"
            focus_correct = focus_strategy == expected_focus
            
            self.record_test_result("Focus Strategy 'peak_engagement_distribution'", focus_correct, 
                                  f"Focus strategy: '{focus_strategy}', Expected: '{expected_focus}'")
            
            # Validate target minutes (25.0, 30.0)
            target_minutes = extended_25_spec.target_minutes
            expected_minutes = (25.0, 30.0)
            minutes_correct = target_minutes == expected_minutes
            
            self.record_test_result("Target Minutes (25-30)", minutes_correct, 
                                  f"Target minutes: {target_minutes}, Expected: {expected_minutes}")
            
            print(f"✅ Template specification validation completed")
            print(f"📊 Specification: {extended_25_spec.name}")
            print(f"    Segments: {segment_count_range}, Expertise: {expertise_level}")
            print(f"    Complexity: {complexity}")
            print(f"    Focus: {focus_strategy}")
            print()
            
        except Exception as e:
            self.record_test_result("Template Specification Validation", False, f"Exception: {str(e)}")
            print(f"❌ Template specification validation failed: {str(e)}")
            print()
    
    async def test_duration_support(self):
        """Test 5: Duration Support Test"""
        print("🧪 TEST 5: Duration Support Test")
        print("-" * 50)
        
        try:
            # Test get_supported_durations()
            supported_durations = self.duration_generator.get_supported_durations()
            
            # Verify "extended_25" is now supported
            extended_25_supported = "extended_25" in supported_durations
            
            self.record_test_result("Extended_25 Duration Support", extended_25_supported, 
                                  f"Supported durations: {supported_durations}")
            
            # Test get_implementation_status()
            implementation_status = self.duration_generator.get_implementation_status()
            
            # Check all three templates are complete
            expected_statuses = {
                "extended_15": "Phase 2.2 Complete - Full 500+ word implementation ready",
                "extended_20": "Phase 2.3 Complete - Full 500+ word implementation ready", 
                "extended_25": "Phase 2.4 Complete - Full 500+ word implementation ready"
            }
            
            all_complete = True
            for duration, expected_status in expected_statuses.items():
                actual_status = implementation_status.get(duration, '')
                status_match = expected_status in actual_status
                
                self.record_test_result(f"Implementation Status - {duration}", status_match, 
                                      f"Status: '{actual_status}'")
                
                if not status_match:
                    all_complete = False
            
            self.record_test_result("All Templates Complete", all_complete, 
                                  f"Implementation status: {implementation_status}")
            
            # Validate expected durations are present
            expected_durations = ["extended_15", "extended_20", "extended_25"]
            all_durations_present = all(duration in supported_durations for duration in expected_durations)
            
            self.record_test_result("All Expected Durations Present", all_durations_present, 
                                  f"Expected: {expected_durations}, Got: {supported_durations}")
            
            print(f"✅ Duration support test completed")
            print(f"📊 Supported durations: {len(supported_durations)} total")
            print(f"    Durations: {supported_durations}")
            print()
            
        except Exception as e:
            self.record_test_result("Duration Support Test", False, f"Exception: {str(e)}")
            print(f"❌ Duration support test failed: {str(e)}")
            print()
    
    def record_test_result(self, test_name: str, passed: bool, details: str):
        """Record a test result"""
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
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        print(f"  {status}: {test_name}")
        print(f"    Details: {details}")
    
    def print_final_results(self):
        """Print comprehensive test results summary"""
        print("=" * 80)
        print("🏁 PHASE 2.4: 25-30 MINUTE TEMPLATE IMPLEMENTATION TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
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
        
        # Phase 2.4 specific summary
        print("🎯 PHASE 2.4 IMPLEMENTATION SUMMARY:")
        
        # Check key Phase 2.4 requirements
        key_tests = [
            "Template Creation",
            "Word Count Validation (500+ words)",
            "Template Name Validation", 
            "Expertise Level Validation",
            "Complexity Validation",
            "Focus Strategy Validation",
            "Phase 2.4 Complete Status",
            "Extended_25 Implementation Status"
        ]
        
        phase_24_passed = 0
        for result in self.test_results:
            if any(key_test in result["test_name"] for key_test in key_tests) and result["passed"]:
                phase_24_passed += 1
        
        phase_24_total = len([r for r in self.test_results if any(key_test in r["test_name"] for key_test in key_tests)])
        phase_24_success = (phase_24_passed / phase_24_total * 100) if phase_24_total > 0 else 0
        
        print(f"   Core Phase 2.4 Tests: {phase_24_passed}/{phase_24_total} passed ({phase_24_success:.1f}%)")
        
        if phase_24_success >= 90:
            print("   🎉 Phase 2.4 implementation is EXCELLENT and ready for production!")
        elif phase_24_success >= 75:
            print("   ✅ Phase 2.4 implementation is GOOD with minor issues to address")
        elif phase_24_success >= 50:
            print("   ⚠️  Phase 2.4 implementation has MODERATE issues requiring attention")
        else:
            print("   ❌ Phase 2.4 implementation has CRITICAL issues requiring immediate fixes")
        
        print()
        print(f"🕐 Test completed at: {datetime.now().isoformat()}")
        print("=" * 80)

async def main():
    """Main test execution function"""
    test_suite = Phase24TemplateTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Phase 2.3 Backend Testing - 20-25 Minute Deep Dive Content Expert Template Implementation
Comprehensive testing for Phase 2.3 backend functionality as specified in review request.

Test Focus:
1. Template Creation Test - Call create_20_25_minute_template() method and verify template name, word count, sections, structure
2. API Endpoint Testing - Test /api/template-system-status endpoint for Phase 2.3 completion status
3. Template Integration Testing - Verify template integrates with enhanced prompt architecture
4. Phase 2.3 Requirements Validation - Check all requirements are met

Key Issues to Investigate:
- Template name inconsistency (expected: "20-25 Minute Deep Dive Content Expert")
- Missing Phase 2.3 completion flags
- Implementation status verification
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
import traceback

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Backend URL from environment
BACKEND_URL = "https://467011d2-4cab-470e-9ba7-13bd14a7440b.preview.emergentagent.com/api"

class Phase23BackendTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = None
        
    async def setup_session(self):
        """Setup HTTP session for testing"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120),
            headers={'Content-Type': 'application/json'}
        )
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: dict, error: str = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if error:
            print(f"   Error: {error}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()
    
    async def test_template_system_status_endpoint(self):
        """Test 1: API Endpoint Testing - /api/template-system-status endpoint"""
        test_name = "Template System Status Endpoint"
        try:
            url = f"{self.backend_url}/template-system-status"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    self.log_test_result(
                        test_name, 
                        False, 
                        {"status_code": response.status}, 
                        f"HTTP {response.status} - Backend service not responding correctly"
                    )
                    return False
                
                data = await response.json()
                
                # Verify response structure
                required_keys = ["status", "components_loaded", "duration_specific_generator", "integration_verification"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test_result(
                        test_name, 
                        False, 
                        {"missing_keys": missing_keys}, 
                        f"Missing required response keys: {missing_keys}"
                    )
                    return False
                
                # Check Phase 2.3 specific data
                phase_23_data = data.get("duration_specific_generator", {}).get("phase_2_3_template_test", {})
                integration_data = data.get("integration_verification", {})
                
                details = {
                    "endpoint_status": data.get("status"),
                    "phase_2_3_template_test": phase_23_data,
                    "phase_2_3_complete_flag": integration_data.get("phase_2_3_complete"),
                    "template_name_returned": phase_23_data.get("template_name"),
                    "creation_successful": phase_23_data.get("creation_successful"),
                    "word_count": phase_23_data.get("word_count"),
                    "meets_500_word_requirement": phase_23_data.get("meets_500_word_requirement")
                }
                
                # Verify Phase 2.3 completion status
                phase_23_complete = integration_data.get("phase_2_3_complete", False)
                template_creation_success = phase_23_data.get("creation_successful", False)
                expected_template_name = "20-25 Minute Deep Dive Content Expert"
                actual_template_name = phase_23_data.get("template_name", "")
                
                success = (
                    data.get("status") == "operational" and
                    phase_23_complete and
                    template_creation_success and
                    actual_template_name == expected_template_name
                )
                
                if not success:
                    error_details = []
                    if data.get("status") != "operational":
                        error_details.append(f"Service status: {data.get('status')}")
                    if not phase_23_complete:
                        error_details.append("Phase 2.3 not marked as complete")
                    if not template_creation_success:
                        error_details.append("Template creation failed")
                    if actual_template_name != expected_template_name:
                        error_details.append(f"Template name mismatch: expected '{expected_template_name}', got '{actual_template_name}'")
                    
                    error_msg = "; ".join(error_details)
                else:
                    error_msg = None
                
                self.log_test_result(test_name, success, details, error_msg)
                return success
                
        except Exception as e:
            self.log_test_result(
                test_name, 
                False, 
                {"exception": str(e)}, 
                f"Exception during endpoint test: {str(e)}"
            )
            return False
    
    async def test_direct_template_creation(self):
        """Test 2: Template Creation Test - Direct method call verification"""
        test_name = "Direct Template Creation Test"
        try:
            # Import the backend modules directly
            from lib.duration_specific_templates import DurationSpecificPromptGenerator
            
            # Create generator instance
            generator = DurationSpecificPromptGenerator()
            
            # Test create_20_25_minute_template() method
            template_result = generator.create_20_25_minute_template()
            
            # Verify template structure
            if not isinstance(template_result, dict):
                self.log_test_result(
                    test_name, 
                    False, 
                    {"result_type": type(template_result).__name__}, 
                    "Template creation did not return a dictionary"
                )
                return False
            
            # Check for required template fields
            required_fields = ["template_content", "template_metadata", "validation_results"]
            missing_fields = [field for field in required_fields if field not in template_result]
            
            if missing_fields:
                self.log_test_result(
                    test_name, 
                    False, 
                    {"missing_fields": missing_fields, "available_fields": list(template_result.keys())}, 
                    f"Missing required template fields: {missing_fields}"
                )
                return False
            
            # Get template content and metadata
            template_content = template_result.get("template_content")
            template_metadata = template_result.get("template_metadata")
            
            # Verify template name
            template_name = None
            if hasattr(template_content, 'name'):
                template_name = template_content.name
            elif isinstance(template_metadata, dict):
                template_name = template_metadata.get("name")
            elif hasattr(template_metadata, 'name'):
                template_name = template_metadata.name
            
            expected_name = "20-25 Minute Deep Dive Content Expert"
            name_matches = template_name == expected_name
            
            # Calculate word count
            word_count = 0
            if hasattr(template_content, 'get_word_count'):
                word_count = template_content.get_word_count()
            elif isinstance(template_content, dict):
                # Count words in all text fields
                text_fields = ["system_prompt", "expertise_description", "framework_instructions", "segment_guidelines"]
                total_text = ""
                for field in text_fields:
                    if field in template_content:
                        total_text += str(template_content[field]) + " "
                word_count = len(total_text.split())
            
            meets_word_requirement = word_count >= 500
            
            # Check for required sections
            required_sections = ["system_prompt", "expertise_description", "framework_instructions", "segment_guidelines"]
            available_sections = []
            
            if isinstance(template_content, dict):
                available_sections = [section for section in required_sections if section in template_content]
            elif hasattr(template_content, '__dict__'):
                available_sections = [section for section in required_sections if hasattr(template_content, section)]
            
            sections_complete = len(available_sections) >= len(required_sections) * 0.8  # At least 80% of sections
            
            # Verify template structure
            structure_valid = (
                template_result is not None and
                template_content is not None and
                template_metadata is not None
            )
            
            details = {
                "template_name": template_name,
                "expected_name": expected_name,
                "name_matches": name_matches,
                "word_count": word_count,
                "meets_500_word_requirement": meets_word_requirement,
                "required_sections": required_sections,
                "available_sections": available_sections,
                "sections_complete": sections_complete,
                "structure_valid": structure_valid,
                "template_fields": list(template_result.keys()) if isinstance(template_result, dict) else "Not a dict"
            }
            
            success = (
                name_matches and
                meets_word_requirement and
                sections_complete and
                structure_valid
            )
            
            if not success:
                error_details = []
                if not name_matches:
                    error_details.append(f"Template name mismatch: expected '{expected_name}', got '{template_name}'")
                if not meets_word_requirement:
                    error_details.append(f"Word count too low: {word_count} (minimum: 500)")
                if not sections_complete:
                    error_details.append(f"Missing sections: {len(available_sections)}/{len(required_sections)}")
                if not structure_valid:
                    error_details.append("Invalid template structure")
                
                error_msg = "; ".join(error_details)
            else:
                error_msg = None
            
            self.log_test_result(test_name, success, details, error_msg)
            return success
            
        except Exception as e:
            self.log_test_result(
                test_name, 
                False, 
                {"exception": str(e), "traceback": traceback.format_exc()}, 
                f"Exception during direct template creation: {str(e)}"
            )
            return False
    
    async def test_template_integration_architecture(self):
        """Test 3: Template Integration Testing - Enhanced prompt architecture integration"""
        test_name = "Template Integration Architecture Test"
        try:
            # Import required modules
            from lib.duration_specific_templates import DurationSpecificPromptGenerator
            
            # Test integration components
            generator = DurationSpecificPromptGenerator()
            
            # Test template specifications
            all_specs = generator.get_all_template_specifications()
            extended_20_spec = all_specs.get("extended_20")
            
            if not extended_20_spec:
                self.log_test_result(
                    test_name, 
                    False, 
                    {"available_specs": list(all_specs.keys())}, 
                    "extended_20 specification not found in template specifications"
                )
                return False
            
            # Verify specification details
            spec_name = extended_20_spec.name
            expected_spec_name = "20-25 Minute Deep Dive Content Expert"
            spec_name_matches = spec_name == expected_spec_name
            
            # Check expertise level
            expertise_level = extended_20_spec.expertise_level.value if hasattr(extended_20_spec.expertise_level, 'value') else str(extended_20_spec.expertise_level)
            expected_expertise = "expert"
            expertise_matches = expertise_level == expected_expertise
            
            # Check segment configuration
            segments = extended_20_spec.segments
            expected_segments = "4-5 segments"
            segments_match = segments == expected_segments
            
            # Check target minutes
            target_minutes = extended_20_spec.target_minutes
            expected_target = (20.0, 25.0)
            target_matches = target_minutes == expected_target
            
            # Check specialization areas
            specialization_areas = extended_20_spec.specialization_areas
            required_specializations = [
                "Long-form content architecture",
                "4-5 segment advanced structuring", 
                "Deep dive content methodology",
                "Sustained engagement algorithms"
            ]
            
            specialization_coverage = 0
            for req in required_specializations:
                for area in specialization_areas:
                    if any(keyword in area.lower() for keyword in req.lower().split()[:3]):
                        specialization_coverage += 1
                        break
            
            specialization_complete = specialization_coverage >= len(required_specializations) * 0.75
            
            details = {
                "specification_found": True,
                "spec_name": spec_name,
                "expected_spec_name": expected_spec_name,
                "spec_name_matches": spec_name_matches,
                "expertise_level": expertise_level,
                "expected_expertise": expected_expertise,
                "expertise_matches": expertise_matches,
                "segments": segments,
                "expected_segments": expected_segments,
                "segments_match": segments_match,
                "target_minutes": target_minutes,
                "expected_target": expected_target,
                "target_matches": target_matches,
                "specialization_areas": specialization_areas,
                "required_specializations": required_specializations,
                "specialization_coverage": f"{specialization_coverage}/{len(required_specializations)}",
                "specialization_complete": specialization_complete
            }
            
            success = (
                spec_name_matches and
                expertise_matches and
                segments_match and
                target_matches and
                specialization_complete
            )
            
            if not success:
                error_details = []
                if not spec_name_matches:
                    error_details.append(f"Spec name mismatch: expected '{expected_spec_name}', got '{spec_name}'")
                if not expertise_matches:
                    error_details.append(f"Expertise level mismatch: expected '{expected_expertise}', got '{expertise_level}'")
                if not segments_match:
                    error_details.append(f"Segments mismatch: expected '{expected_segments}', got '{segments}'")
                if not target_matches:
                    error_details.append(f"Target minutes mismatch: expected {expected_target}, got {target_minutes}")
                if not specialization_complete:
                    error_details.append(f"Insufficient specialization coverage: {specialization_coverage}/{len(required_specializations)}")
                
                error_msg = "; ".join(error_details)
            else:
                error_msg = None
            
            self.log_test_result(test_name, success, details, error_msg)
            return success
            
        except Exception as e:
            self.log_test_result(
                test_name, 
                False, 
                {"exception": str(e), "traceback": traceback.format_exc()}, 
                f"Exception during integration test: {str(e)}"
            )
            return False
    
    async def test_phase_23_requirements_validation(self):
        """Test 4: Phase 2.3 Requirements Validation - Comprehensive requirements check"""
        test_name = "Phase 2.3 Requirements Validation"
        try:
            # Import required modules
            from lib.duration_specific_templates import DurationSpecificPromptGenerator
            
            generator = DurationSpecificPromptGenerator()
            
            # Create the template
            template_result = generator.create_20_25_minute_template()
            
            # Get template content
            template_content = template_result.get("template_content")
            
            # Requirement 1: Expertise verification
            expertise_requirement = "20-25 Minute Deep Dive Content Expert, master of long-form video content"
            
            # Check system prompt for expertise indicators
            system_prompt = ""
            if isinstance(template_content, dict):
                system_prompt = template_content.get("system_prompt", "")
            elif hasattr(template_content, 'system_prompt'):
                system_prompt = template_content.system_prompt
            
            expertise_keywords = ["20-25 minute", "deep dive", "content expert", "master", "long-form"]
            expertise_coverage = sum(1 for keyword in expertise_keywords if keyword.lower() in system_prompt.lower())
            expertise_meets_requirement = expertise_coverage >= len(expertise_keywords) * 0.6
            
            # Requirement 2: Segment Optimization verification
            segment_requirement = "4-5 segments with advanced narrative arc management"
            
            segment_keywords = ["4-5 segment", "advanced", "narrative arc", "management"]
            segment_coverage = sum(1 for keyword in segment_keywords if keyword.lower() in system_prompt.lower())
            segment_meets_requirement = segment_coverage >= len(segment_keywords) * 0.5
            
            # Requirement 3: Content Depth verification
            content_depth_requirement = "Deep dive content structuring with comprehensive topic breakdown"
            
            depth_keywords = ["deep dive", "content structuring", "comprehensive", "topic breakdown"]
            depth_coverage = sum(1 for keyword in depth_keywords if keyword.lower() in system_prompt.lower())
            depth_meets_requirement = depth_coverage >= len(depth_keywords) * 0.5
            
            # Requirement 4: Engagement Strategy verification
            engagement_requirement = "Sustained engagement algorithms for extended duration"
            
            engagement_keywords = ["sustained engagement", "algorithms", "extended duration"]
            engagement_coverage = sum(1 for keyword in engagement_keywords if keyword.lower() in system_prompt.lower())
            engagement_meets_requirement = engagement_coverage >= len(engagement_keywords) * 0.5
            
            # Requirement 5: Template Length verification (500+ words)
            word_count = 0
            if hasattr(template_content, 'get_word_count'):
                word_count = template_content.get_word_count()
            elif isinstance(template_content, dict):
                text_fields = ["system_prompt", "expertise_description", "framework_instructions", "segment_guidelines"]
                total_text = ""
                for field in text_fields:
                    if field in template_content:
                        total_text += str(template_content[field]) + " "
                word_count = len(total_text.split())
            
            length_meets_requirement = word_count >= 500
            
            details = {
                "expertise_requirement": expertise_requirement,
                "expertise_keywords_found": expertise_coverage,
                "expertise_keywords_total": len(expertise_keywords),
                "expertise_meets_requirement": expertise_meets_requirement,
                
                "segment_requirement": segment_requirement,
                "segment_keywords_found": segment_coverage,
                "segment_keywords_total": len(segment_keywords),
                "segment_meets_requirement": segment_meets_requirement,
                
                "content_depth_requirement": content_depth_requirement,
                "depth_keywords_found": depth_coverage,
                "depth_keywords_total": len(depth_keywords),
                "depth_meets_requirement": depth_meets_requirement,
                
                "engagement_requirement": engagement_requirement,
                "engagement_keywords_found": engagement_coverage,
                "engagement_keywords_total": len(engagement_keywords),
                "engagement_meets_requirement": engagement_meets_requirement,
                
                "length_requirement": "500+ words of specialized instructions",
                "actual_word_count": word_count,
                "length_meets_requirement": length_meets_requirement,
                
                "system_prompt_length": len(system_prompt),
                "system_prompt_preview": system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
            }
            
            # Overall success criteria
            success = (
                expertise_meets_requirement and
                segment_meets_requirement and
                depth_meets_requirement and
                engagement_meets_requirement and
                length_meets_requirement
            )
            
            if not success:
                error_details = []
                if not expertise_meets_requirement:
                    error_details.append(f"Expertise requirement not met: {expertise_coverage}/{len(expertise_keywords)} keywords found")
                if not segment_meets_requirement:
                    error_details.append(f"Segment optimization requirement not met: {segment_coverage}/{len(segment_keywords)} keywords found")
                if not depth_meets_requirement:
                    error_details.append(f"Content depth requirement not met: {depth_coverage}/{len(depth_keywords)} keywords found")
                if not engagement_meets_requirement:
                    error_details.append(f"Engagement strategy requirement not met: {engagement_coverage}/{len(engagement_keywords)} keywords found")
                if not length_meets_requirement:
                    error_details.append(f"Length requirement not met: {word_count} words (minimum: 500)")
                
                error_msg = "; ".join(error_details)
            else:
                error_msg = None
            
            self.log_test_result(test_name, success, details, error_msg)
            return success
            
        except Exception as e:
            self.log_test_result(
                test_name, 
                False, 
                {"exception": str(e), "traceback": traceback.format_exc()}, 
                f"Exception during requirements validation: {str(e)}"
            )
            return False
    
    async def run_comprehensive_phase_23_tests(self):
        """Run all Phase 2.3 backend tests"""
        print("🚀 PHASE 2.3 BACKEND TESTING - 20-25 MINUTE DEEP DIVE CONTENT EXPERT TEMPLATE")
        print("=" * 80)
        print()
        
        await self.setup_session()
        
        try:
            # Test 1: API Endpoint Testing
            print("TEST 1: API Endpoint Testing - /api/template-system-status")
            test1_success = await self.test_template_system_status_endpoint()
            
            # Test 2: Template Creation Test
            print("TEST 2: Template Creation Test - Direct method call")
            test2_success = await self.test_direct_template_creation()
            
            # Test 3: Template Integration Testing
            print("TEST 3: Template Integration Testing - Enhanced prompt architecture")
            test3_success = await self.test_template_integration_architecture()
            
            # Test 4: Phase 2.3 Requirements Validation
            print("TEST 4: Phase 2.3 Requirements Validation - Comprehensive requirements check")
            test4_success = await self.test_phase_23_requirements_validation()
            
            # Summary
            total_tests = 4
            passed_tests = sum([test1_success, test2_success, test3_success, test4_success])
            
            print("=" * 80)
            print("🎯 PHASE 2.3 BACKEND TESTING SUMMARY")
            print("=" * 80)
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            print()
            
            if passed_tests == total_tests:
                print("🎉 ALL PHASE 2.3 TESTS PASSED - Template implementation is working correctly!")
                print("✅ Template name: '20-25 Minute Deep Dive Content Expert' verified")
                print("✅ Word count exceeds 500+ words requirement")
                print("✅ All required sections are present")
                print("✅ Template structure is correct")
                print("✅ Phase 2.3 completion status properly set")
                print("✅ Template integrates with enhanced prompt architecture")
            else:
                print("❌ SOME PHASE 2.3 TESTS FAILED - Issues found in template implementation")
                
                # Identify specific issues
                if not test1_success:
                    print("❌ API endpoint issues detected")
                if not test2_success:
                    print("❌ Template creation issues detected")
                if not test3_success:
                    print("❌ Template integration issues detected")
                if not test4_success:
                    print("❌ Requirements validation issues detected")
            
            print()
            return passed_tests == total_tests
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = Phase23BackendTester()
    success = await tester.run_comprehensive_phase_23_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Phase 1 Advanced Script Generation Logic System Testing
======================================================

This test suite comprehensively tests the newly implemented Phase 1 Advanced Script Generation 
Logic system with Core Segmentation functionality as specified in the review request.

Test Coverage:
1. Core Segmentation System Testing
2. Specific Test Cases with different durations
3. Response Structure Validation
4. Helper Endpoint Testing
5. Integration Testing

Review Request Requirements:
- Test `/api/generate-script-advanced` endpoint with different duration options
- Verify segmentation logic for short vs long durations
- Test duration-based segment calculation accuracy
- Verify segment planning and coordination system
- Test helper endpoint `/api/advanced-script-context/{script_id}/segment/{segment_number}`
- Validate response structure and all required fields
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase1AdvancedScriptTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://5f52b486-d0b4-46b2-8fa8-5d44d397cf85.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Test results tracking
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # Store generated script IDs for helper endpoint testing
        self.generated_script_ids = []
        
        # Test scenarios for comprehensive coverage
        self.test_scenarios = [
            # Short durations - should use single_pass
            {
                "name": "Short Duration - Medium (No Segmentation)",
                "prompt": "Create a video about healthy cooking tips",
                "video_type": "educational",
                "duration": "medium",
                "expected_strategy": "single_pass",
                "expected_segments": 1,
                "should_segment": False
            },
            {
                "name": "Short Duration - Long (No Segmentation)",
                "prompt": "Create a marketing video about our new product features",
                "video_type": "marketing", 
                "duration": "long",
                "expected_strategy": "single_pass",
                "expected_segments": 1,
                "should_segment": False
            },
            # Extended durations - should use multi-segment
            {
                "name": "Extended 15min Duration (Multi-Segment)",
                "prompt": "Create an educational video about advanced Python programming concepts",
                "video_type": "educational",
                "duration": "extended_15",
                "expected_strategy": "segmented",
                "expected_segments": 3,  # ~17.5 min / 6 min per segment
                "should_segment": True
            },
            {
                "name": "Extended 20min Duration (Multi-Segment)",
                "prompt": "Create an entertainment video series about travel adventures",
                "video_type": "entertainment",
                "duration": "extended_20", 
                "expected_strategy": "segmented",
                "expected_segments": 4,  # ~22.5 min / 6 min per segment
                "should_segment": True
            },
            {
                "name": "Extended 25min Duration (Multi-Segment)",
                "prompt": "Create a comprehensive marketing presentation about digital transformation",
                "video_type": "marketing",
                "duration": "extended_25",
                "expected_strategy": "segmented", 
                "expected_segments": 5,  # ~27.5 min / 6 min per segment
                "should_segment": True
            }
        ]

    def log_test_result(self, test_name: str, passed: bool, details: str, response_data: Optional[Dict] = None):
        """Log test result with details"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            self.test_results['failed_tests'] += 1
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'response_data': response_data
        })

    async def test_backend_connectivity(self) -> bool:
        """Test basic backend connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test_result("Backend Connectivity", True, f"Backend responding with status {response.status_code}")
                return True
            else:
                self.log_test_result("Backend Connectivity", False, f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Backend Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_duration_validation_endpoint(self):
        """Test duration validation helper endpoint"""
        try:
            # Test valid durations
            valid_durations = ["short", "medium", "long", "extended_15", "extended_20", "extended_25"]
            
            for duration in valid_durations:
                response = self.session.post(f"{self.base_url}/validate-duration", 
                                           json={"duration": duration})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid") == True and data.get("duration") == duration:
                        self.log_test_result(f"Duration Validation - {duration}", True, 
                                           f"Valid duration accepted: {data.get('display_name')}")
                    else:
                        self.log_test_result(f"Duration Validation - {duration}", False, 
                                           f"Unexpected validation response: {data}")
                else:
                    self.log_test_result(f"Duration Validation - {duration}", False, 
                                       f"HTTP {response.status_code}: {response.text}")
            
            # Test invalid duration
            response = self.session.post(f"{self.base_url}/validate-duration", 
                                       json={"duration": "invalid_duration"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") == False:
                    self.log_test_result("Duration Validation - Invalid", True, 
                                       "Invalid duration correctly rejected")
                else:
                    self.log_test_result("Duration Validation - Invalid", False, 
                                       f"Invalid duration not rejected: {data}")
            
        except Exception as e:
            self.log_test_result("Duration Validation Endpoint", False, f"Error: {str(e)}")

    def test_advanced_script_generation(self, scenario: Dict[str, Any]) -> Optional[str]:
        """Test advanced script generation with specific scenario"""
        try:
            test_name = f"Advanced Script Generation - {scenario['name']}"
            
            # Prepare request
            request_data = {
                "prompt": scenario["prompt"],
                "video_type": scenario["video_type"],
                "duration": scenario["duration"],
                "enable_segmentation": True
            }
            
            logger.info(f"🎬 Testing {scenario['name']} with duration {scenario['duration']}")
            
            # Make request
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/generate-script-advanced", 
                                       json=request_data)
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test_result(test_name, False, 
                                   f"HTTP {response.status_code}: {response.text}")
                return None
            
            data = response.json()
            
            # Validate response structure
            required_fields = [
                "id", "original_prompt", "video_type", "duration", 
                "segmentation_analysis", "segment_plan", "coordination_context",
                "generation_strategy", "ready_for_generation", "phase_completed", "next_steps"
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test_result(test_name, False, 
                                   f"Missing required fields: {missing_fields}", data)
                return None
            
            # Validate segmentation analysis
            segmentation = data.get("segmentation_analysis", {})
            expected_segments = scenario["expected_segments"]
            expected_strategy = scenario["expected_strategy"]
            should_segment = scenario["should_segment"]
            
            # Check segmentation logic
            requires_segmentation = segmentation.get("requires_segmentation", False)
            total_segments = segmentation.get("total_segments", 1)
            generation_strategy = data.get("generation_strategy", "single_pass")
            
            validation_results = []
            
            # Validate segmentation requirement
            if requires_segmentation == should_segment:
                validation_results.append("✅ Segmentation requirement correct")
            else:
                validation_results.append(f"❌ Segmentation requirement wrong: expected {should_segment}, got {requires_segmentation}")
            
            # Validate segment count (allow ±1 tolerance for calculation variations)
            if abs(total_segments - expected_segments) <= 1:
                validation_results.append(f"✅ Segment count acceptable: {total_segments} (expected ~{expected_segments})")
            else:
                validation_results.append(f"❌ Segment count wrong: {total_segments} (expected ~{expected_segments})")
            
            # Validate generation strategy
            if generation_strategy == expected_strategy:
                validation_results.append(f"✅ Generation strategy correct: {generation_strategy}")
            else:
                validation_results.append(f"❌ Generation strategy wrong: {generation_strategy} (expected {expected_strategy})")
            
            # Validate segmentation analysis fields for multi-segment scenarios
            if should_segment:
                seg_fields = ["segment_duration_minutes", "total_duration_minutes", "content_density"]
                missing_seg_fields = [field for field in seg_fields if field not in segmentation]
                if not missing_seg_fields:
                    validation_results.append("✅ Segmentation analysis fields complete")
                else:
                    validation_results.append(f"❌ Missing segmentation fields: {missing_seg_fields}")
            
            # Validate segment plan structure
            segment_plan = data.get("segment_plan", {})
            if should_segment and segment_plan.get("segmentation_required", False):
                plan_data = segment_plan.get("segment_plan", {})
                if "segment_outlines" in plan_data and "coordination_strategy" in plan_data:
                    validation_results.append("✅ Segment plan structure complete")
                else:
                    validation_results.append("❌ Segment plan structure incomplete")
            
            # Validate coordination context
            coordination = data.get("coordination_context", {})
            if coordination and isinstance(coordination, dict):
                validation_results.append("✅ Coordination context initialized")
            else:
                validation_results.append("❌ Coordination context missing or invalid")
            
            # Overall test result
            failed_validations = [v for v in validation_results if v.startswith("❌")]
            test_passed = len(failed_validations) == 0
            
            details = f"Processing time: {processing_time:.2f}s. Validations: {'; '.join(validation_results)}"
            
            self.log_test_result(test_name, test_passed, details, {
                "segmentation_analysis": segmentation,
                "generation_strategy": generation_strategy,
                "processing_time": processing_time
            })
            
            # Store script ID for helper endpoint testing
            if test_passed:
                script_id = data.get("id")
                if script_id:
                    self.generated_script_ids.append({
                        "id": script_id,
                        "segments": total_segments,
                        "scenario": scenario["name"]
                    })
            
            return data.get("id") if test_passed else None
            
        except Exception as e:
            self.log_test_result(f"Advanced Script Generation - {scenario['name']}", False, 
                               f"Exception: {str(e)}")
            return None

    def test_segment_context_helper_endpoint(self):
        """Test the segment context helper endpoint"""
        if not self.generated_script_ids:
            self.log_test_result("Segment Context Helper", False, 
                               "No generated script IDs available for testing")
            return
        
        try:
            # Test with multi-segment scripts
            multi_segment_scripts = [s for s in self.generated_script_ids if s["segments"] > 1]
            
            if not multi_segment_scripts:
                self.log_test_result("Segment Context Helper", False, 
                                   "No multi-segment scripts available for testing")
                return
            
            # Test with first multi-segment script
            test_script = multi_segment_scripts[0]
            script_id = test_script["id"]
            total_segments = test_script["segments"]
            
            # Test each segment
            for segment_num in range(1, min(total_segments + 1, 4)):  # Test up to 3 segments
                test_name = f"Segment Context - Script {script_id[:8]} Segment {segment_num}"
                
                response = self.session.get(
                    f"{self.base_url}/advanced-script-context/{script_id}/segment/{segment_num}"
                )
                
                if response.status_code != 200:
                    self.log_test_result(test_name, False, 
                                       f"HTTP {response.status_code}: {response.text}")
                    continue
                
                data = response.json()
                
                # Validate response structure
                required_fields = ["status", "script_id", "segment_context", "original_script_data", 
                                 "ready_for_segment_generation"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test_result(test_name, False, 
                                       f"Missing required fields: {missing_fields}")
                    continue
                
                # Validate segment context structure
                segment_context = data.get("segment_context", {})
                context_fields = ["segment_position", "coordination_requirements"]
                
                missing_context_fields = [field for field in context_fields if field not in segment_context]
                if missing_context_fields:
                    self.log_test_result(test_name, False, 
                                       f"Missing segment context fields: {missing_context_fields}")
                    continue
                
                # Validate segment position data
                position = segment_context.get("segment_position", {})
                if (position.get("current") == segment_num and 
                    position.get("total") == total_segments):
                    self.log_test_result(test_name, True, 
                                       f"Segment context valid for segment {segment_num}/{total_segments}")
                else:
                    self.log_test_result(test_name, False, 
                                       f"Segment position data incorrect: {position}")
            
            # Test invalid segment number
            invalid_segment_test = f"Segment Context - Invalid Segment Number"
            response = self.session.get(
                f"{self.base_url}/advanced-script-context/{script_id}/segment/999"
            )
            
            # Should still return 200 but with appropriate handling
            if response.status_code == 200:
                self.log_test_result(invalid_segment_test, True, 
                                   "Invalid segment number handled gracefully")
            else:
                self.log_test_result(invalid_segment_test, False, 
                                   f"Invalid segment number not handled properly: {response.status_code}")
                
        except Exception as e:
            self.log_test_result("Segment Context Helper Endpoint", False, f"Exception: {str(e)}")

    def test_invalid_script_id_handling(self):
        """Test helper endpoint with invalid script ID"""
        try:
            invalid_id = "invalid-script-id-12345"
            response = self.session.get(
                f"{self.base_url}/advanced-script-context/{invalid_id}/segment/1"
            )
            
            if response.status_code == 404:
                self.log_test_result("Invalid Script ID Handling", True, 
                                   "Invalid script ID correctly returns 404")
            else:
                self.log_test_result("Invalid Script ID Handling", False, 
                                   f"Invalid script ID returned {response.status_code} instead of 404")
                
        except Exception as e:
            self.log_test_result("Invalid Script ID Handling", False, f"Exception: {str(e)}")

    def test_duration_calculation_accuracy(self):
        """Test duration-based segment calculation accuracy"""
        try:
            # Test specific duration calculations
            duration_tests = [
                {"duration": "extended_15", "expected_minutes": 17.5, "expected_segments_range": (2, 4)},
                {"duration": "extended_20", "expected_minutes": 22.5, "expected_segments_range": (3, 5)},
                {"duration": "extended_25", "expected_minutes": 27.5, "expected_segments_range": (4, 6)}
            ]
            
            for test_case in duration_tests:
                # Find a generated script with this duration
                matching_script = None
                for script_data in self.test_results['test_details']:
                    if (script_data.get('response_data', {}).get('segmentation_analysis', {}).get('total_duration_minutes') 
                        == test_case['expected_minutes']):
                        matching_script = script_data
                        break
                
                if matching_script:
                    segmentation = matching_script['response_data']['segmentation_analysis']
                    total_segments = segmentation.get('total_segments', 1)
                    segment_duration = segmentation.get('segment_duration_minutes', 0)
                    
                    # Validate segment count is in expected range
                    min_segments, max_segments = test_case['expected_segments_range']
                    if min_segments <= total_segments <= max_segments:
                        # Validate segment duration calculation
                        expected_duration_per_segment = test_case['expected_minutes'] / total_segments
                        duration_diff = abs(segment_duration - expected_duration_per_segment)
                        
                        if duration_diff <= 1.0:  # Allow 1 minute tolerance
                            self.log_test_result(f"Duration Calculation - {test_case['duration']}", True,
                                               f"Accurate calculation: {total_segments} segments of {segment_duration}min each")
                        else:
                            self.log_test_result(f"Duration Calculation - {test_case['duration']}", False,
                                               f"Inaccurate duration: {segment_duration}min vs expected ~{expected_duration_per_segment:.1f}min")
                    else:
                        self.log_test_result(f"Duration Calculation - {test_case['duration']}", False,
                                           f"Segment count {total_segments} outside expected range {min_segments}-{max_segments}")
                else:
                    self.log_test_result(f"Duration Calculation - {test_case['duration']}", False,
                                       "No matching script found for duration calculation test")
                    
        except Exception as e:
            self.log_test_result("Duration Calculation Accuracy", False, f"Exception: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all Phase 1 Advanced Script Generation tests"""
        logger.info("🚀 Starting Phase 1 Advanced Script Generation Logic System Testing")
        logger.info("=" * 80)
        
        # Test 1: Backend Connectivity
        logger.info("📡 Testing Backend Connectivity...")
        if not self.test_backend_connectivity():
            logger.error("❌ Backend connectivity failed. Aborting tests.")
            return self.test_results
        
        # Test 2: Duration Validation Endpoint
        logger.info("⏱️ Testing Duration Validation Endpoint...")
        self.test_duration_validation_endpoint()
        
        # Test 3: Core Segmentation System Testing
        logger.info("🎬 Testing Core Segmentation System...")
        for scenario in self.test_scenarios:
            self.test_advanced_script_generation(scenario)
            time.sleep(1)  # Brief pause between tests
        
        # Test 4: Helper Endpoint Testing
        logger.info("🔧 Testing Segment Context Helper Endpoint...")
        self.test_segment_context_helper_endpoint()
        
        # Test 5: Invalid Script ID Handling
        logger.info("🚫 Testing Invalid Script ID Handling...")
        self.test_invalid_script_id_handling()
        
        # Test 6: Duration Calculation Accuracy
        logger.info("📊 Testing Duration Calculation Accuracy...")
        self.test_duration_calculation_accuracy()
        
        # Final Results
        logger.info("=" * 80)
        logger.info("🏁 Phase 1 Advanced Script Generation Testing Complete")
        logger.info(f"📊 Results: {self.test_results['passed_tests']}/{self.test_results['total_tests']} tests passed")
        
        if self.test_results['failed_tests'] > 0:
            logger.warning(f"⚠️ {self.test_results['failed_tests']} tests failed")
            
        return self.test_results

    def print_detailed_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 80)
        print("PHASE 1 ADVANCED SCRIPT GENERATION - DETAILED TEST RESULTS")
        print("=" * 80)
        
        print(f"\n📊 SUMMARY:")
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        print(f"Success Rate: {(self.test_results['passed_tests']/self.test_results['total_tests']*100):.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test in self.test_results['test_details']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"{status} | {test['test_name']}")
            print(f"     Details: {test['details']}")
            if not test['passed'] and test.get('response_data'):
                print(f"     Response: {json.dumps(test['response_data'], indent=2)[:200]}...")
            print()

if __name__ == "__main__":
    tester = Phase1AdvancedScriptTester()
    results = tester.run_comprehensive_tests()
    tester.print_detailed_results()
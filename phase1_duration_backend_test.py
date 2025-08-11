#!/usr/bin/env python3
"""
Phase 1 Duration Management System Enhancement Testing
=====================================================

This test suite focuses specifically on testing the Phase 1 Duration Management System
Enhancement that was just implemented. The enhancement adds new extended duration options
and improves the duration validation and script generation system.

Key areas tested:
1. New Duration Options Availability - /api/durations endpoint
2. Duration Validation - /api/validate-duration endpoint with all new options
3. Script Generation with New Durations - /api/generate-script with extended durations
4. Backend Integration - Verify existing functionality still works with new durations

Test Environment: Uses production backend URL from frontend/.env
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase1DurationTester:
    def __init__(self):
        # Use production backend URL from frontend/.env
        self.base_url = "https://91a9d61f-d967-4b3f-a16d-decd1e0775ab.preview.emergentagent.com/api"
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
        
        # Expected new duration options from Phase 1 enhancement
        self.expected_durations = {
            "short": "Short (30s-1min)",
            "medium": "Medium (1-3min)", 
            "long": "Long (3-5min)",
            "extended_5": "Extended (5-10min)",
            "extended_10": "Extended (10-15min)",
            "extended_15": "Extended (15-20min)",
            "extended_20": "Extended (20-25min)",
            "extended_25": "Extended (25-30min)"
        }
        
        # Test script prompt for comprehensive testing
        self.test_prompt = "Create a comprehensive educational video about climate change"
        
    def log_test_result(self, test_name: str, passed: bool, details: str, response_data: Any = None):
        """Log test result and update counters"""
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

    def test_backend_connectivity(self) -> bool:
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
            self.log_test_result("Backend Connectivity", False, f"Connection error: {str(e)}")
            return False

    def test_durations_endpoint(self) -> bool:
        """Test 1: New Duration Options Availability - /api/durations endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/durations")
            
            if response.status_code != 200:
                self.log_test_result("Durations Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check response structure
            if 'available_durations' not in data:
                self.log_test_result("Durations Endpoint", False, "Missing 'available_durations' field in response")
                return False
            
            if 'default_duration' not in data:
                self.log_test_result("Durations Endpoint", False, "Missing 'default_duration' field in response")
                return False
            
            available_durations = data['available_durations']
            
            # Check all expected durations are present
            missing_durations = []
            for duration_key, duration_display in self.expected_durations.items():
                if duration_key not in available_durations:
                    missing_durations.append(duration_key)
                elif available_durations[duration_key] != duration_display:
                    missing_durations.append(f"{duration_key} (incorrect display name)")
            
            if missing_durations:
                self.log_test_result("Durations Endpoint", False, f"Missing or incorrect durations: {missing_durations}", data)
                return False
            
            # Check for new extended durations specifically
            extended_durations = [k for k in available_durations.keys() if k.startswith('extended_')]
            if len(extended_durations) != 5:
                self.log_test_result("Durations Endpoint", False, f"Expected 5 extended durations, found {len(extended_durations)}: {extended_durations}", data)
                return False
            
            self.log_test_result("Durations Endpoint", True, f"All {len(available_durations)} duration options available including {len(extended_durations)} new extended options", data)
            return True
            
        except Exception as e:
            self.log_test_result("Durations Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_duration_validation_valid(self) -> bool:
        """Test 2a: Duration Validation - Valid durations"""
        valid_tests_passed = 0
        total_valid_tests = len(self.expected_durations)
        
        for duration_key in self.expected_durations.keys():
            try:
                response = self.session.post(f"{self.base_url}/validate-duration", 
                                           json={"duration": duration_key})
                
                if response.status_code != 200:
                    self.log_test_result(f"Duration Validation Valid ({duration_key})", False, f"HTTP {response.status_code}: {response.text}")
                    continue
                
                data = response.json()
                
                # Check response structure for valid duration
                if not data.get('valid', False):
                    self.log_test_result(f"Duration Validation Valid ({duration_key})", False, f"Duration marked as invalid: {data}")
                    continue
                
                if data.get('duration') != duration_key:
                    self.log_test_result(f"Duration Validation Valid ({duration_key})", False, f"Duration mismatch: expected {duration_key}, got {data.get('duration')}")
                    continue
                
                if data.get('display_name') != self.expected_durations[duration_key]:
                    self.log_test_result(f"Duration Validation Valid ({duration_key})", False, f"Display name mismatch: expected {self.expected_durations[duration_key]}, got {data.get('display_name')}")
                    continue
                
                valid_tests_passed += 1
                
            except Exception as e:
                self.log_test_result(f"Duration Validation Valid ({duration_key})", False, f"Exception: {str(e)}")
                continue
        
        success = valid_tests_passed == total_valid_tests
        self.log_test_result("Duration Validation Valid", success, f"Passed {valid_tests_passed}/{total_valid_tests} valid duration tests")
        return success

    def test_duration_validation_invalid(self) -> bool:
        """Test 2b: Duration Validation - Invalid durations"""
        invalid_durations = ["invalid", "super_long", "", "short_extended", "extended_30"]
        invalid_tests_passed = 0
        
        for invalid_duration in invalid_durations:
            try:
                response = self.session.post(f"{self.base_url}/validate-duration", 
                                           json={"duration": invalid_duration})
                
                if response.status_code != 200:
                    self.log_test_result(f"Duration Validation Invalid ({invalid_duration})", False, f"HTTP {response.status_code}: {response.text}")
                    continue
                
                data = response.json()
                
                # Check that invalid duration is properly rejected
                if data.get('valid', True):
                    self.log_test_result(f"Duration Validation Invalid ({invalid_duration})", False, f"Invalid duration marked as valid: {data}")
                    continue
                
                if 'error' not in data:
                    self.log_test_result(f"Duration Validation Invalid ({invalid_duration})", False, f"Missing error message for invalid duration: {data}")
                    continue
                
                if 'available_durations' not in data:
                    self.log_test_result(f"Duration Validation Invalid ({invalid_duration})", False, f"Missing available_durations in error response: {data}")
                    continue
                
                invalid_tests_passed += 1
                
            except Exception as e:
                self.log_test_result(f"Duration Validation Invalid ({invalid_duration})", False, f"Exception: {str(e)}")
                continue
        
        success = invalid_tests_passed == len(invalid_durations)
        self.log_test_result("Duration Validation Invalid", success, f"Passed {invalid_tests_passed}/{len(invalid_durations)} invalid duration tests")
        return success

    def test_duration_validation_missing_parameter(self) -> bool:
        """Test 2c: Duration Validation - Missing duration parameter"""
        try:
            response = self.session.post(f"{self.base_url}/validate-duration", json={})
            
            if response.status_code != 400:
                self.log_test_result("Duration Validation Missing Parameter", False, f"Expected HTTP 400, got {response.status_code}: {response.text}")
                return False
            
            # For missing parameter, we expect a 400 error from FastAPI
            self.log_test_result("Duration Validation Missing Parameter", True, f"Correctly returned HTTP 400 for missing parameter")
            return True
            
        except Exception as e:
            self.log_test_result("Duration Validation Missing Parameter", False, f"Exception: {str(e)}")
            return False

    def test_script_generation_extended_durations(self) -> bool:
        """Test 3: Script Generation with New Extended Durations"""
        extended_durations = ["extended_5", "extended_10", "extended_25"]
        extended_tests_passed = 0
        
        for duration in extended_durations:
            try:
                request_data = {
                    "prompt": self.test_prompt,
                    "video_type": "educational",
                    "duration": duration
                }
                
                logger.info(f"Testing script generation with {duration} duration...")
                response = self.session.post(f"{self.base_url}/generate-script", json=request_data)
                
                if response.status_code != 200:
                    self.log_test_result(f"Script Generation ({duration})", False, f"HTTP {response.status_code}: {response.text}")
                    continue
                
                data = response.json()
                
                # Check response structure
                required_fields = ['id', 'original_prompt', 'generated_script', 'video_type', 'duration', 'created_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(f"Script Generation ({duration})", False, f"Missing fields: {missing_fields}")
                    continue
                
                # Check that duration is correctly set
                if data.get('duration') != duration:
                    self.log_test_result(f"Script Generation ({duration})", False, f"Duration mismatch: expected {duration}, got {data.get('duration')}")
                    continue
                
                # Check script content quality for extended durations
                script_content = data.get('generated_script', '')
                script_length = len(script_content)
                
                # Extended durations should generate longer, more detailed scripts
                min_expected_length = 2000 if duration == "extended_5" else 3000 if duration == "extended_10" else 4000
                
                if script_length < min_expected_length:
                    self.log_test_result(f"Script Generation ({duration})", False, f"Script too short for {duration}: {script_length} chars (expected >{min_expected_length})")
                    continue
                
                # Check for educational content structure
                if 'climate change' not in script_content.lower():
                    self.log_test_result(f"Script Generation ({duration})", False, f"Script doesn't contain expected topic content")
                    continue
                
                extended_tests_passed += 1
                self.log_test_result(f"Script Generation ({duration})", True, f"Generated {script_length} char script with proper structure")
                
            except Exception as e:
                self.log_test_result(f"Script Generation ({duration})", False, f"Exception: {str(e)}")
                continue
        
        success = extended_tests_passed == len(extended_durations)
        self.log_test_result("Script Generation Extended Durations", success, f"Passed {extended_tests_passed}/{len(extended_durations)} extended duration script generation tests")
        return success

    def test_script_generation_regression(self) -> bool:
        """Test 4: Backend Integration - Verify existing durations still work"""
        legacy_durations = ["short", "medium", "long"]
        regression_tests_passed = 0
        
        for duration in legacy_durations:
            try:
                request_data = {
                    "prompt": self.test_prompt,
                    "video_type": "educational", 
                    "duration": duration
                }
                
                logger.info(f"Testing regression with {duration} duration...")
                response = self.session.post(f"{self.base_url}/generate-script", json=request_data)
                
                if response.status_code != 200:
                    self.log_test_result(f"Regression Test ({duration})", False, f"HTTP {response.status_code}: {response.text}")
                    continue
                
                data = response.json()
                
                # Check basic response structure
                if 'generated_script' not in data or 'duration' not in data:
                    self.log_test_result(f"Regression Test ({duration})", False, f"Missing required fields in response")
                    continue
                
                # Check that duration is correctly set
                if data.get('duration') != duration:
                    self.log_test_result(f"Regression Test ({duration})", False, f"Duration mismatch: expected {duration}, got {data.get('duration')}")
                    continue
                
                # Check script was generated
                script_content = data.get('generated_script', '')
                if len(script_content) < 500:
                    self.log_test_result(f"Regression Test ({duration})", False, f"Script too short: {len(script_content)} chars")
                    continue
                
                regression_tests_passed += 1
                self.log_test_result(f"Regression Test ({duration})", True, f"Legacy duration {duration} works correctly")
                
            except Exception as e:
                self.log_test_result(f"Regression Test ({duration})", False, f"Exception: {str(e)}")
                continue
        
        success = regression_tests_passed == len(legacy_durations)
        self.log_test_result("Script Generation Regression", success, f"Passed {regression_tests_passed}/{len(legacy_durations)} regression tests")
        return success

    def run_comprehensive_test_suite(self):
        """Run all Phase 1 Duration Management System tests"""
        logger.info("🚀 Starting Phase 1 Duration Management System Enhancement Testing")
        logger.info("=" * 80)
        
        # Test 1: Backend connectivity
        if not self.test_backend_connectivity():
            logger.error("❌ Backend connectivity failed - aborting tests")
            return self.test_results
        
        # Test 2: New Duration Options Availability
        logger.info("\n📋 Testing New Duration Options Availability...")
        self.test_durations_endpoint()
        
        # Test 3: Duration Validation
        logger.info("\n🔍 Testing Duration Validation...")
        self.test_duration_validation_valid()
        self.test_duration_validation_invalid()
        self.test_duration_validation_missing_parameter()
        
        # Test 4: Script Generation with New Durations
        logger.info("\n📝 Testing Script Generation with Extended Durations...")
        self.test_script_generation_extended_durations()
        
        # Test 5: Backend Integration (Regression)
        logger.info("\n🔄 Testing Backend Integration (Regression)...")
        self.test_script_generation_regression()
        
        # Final results
        logger.info("\n" + "=" * 80)
        logger.info("🎯 PHASE 1 DURATION MANAGEMENT SYSTEM TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {self.test_results['total_tests']}")
        logger.info(f"Passed: {self.test_results['passed_tests']} ✅")
        logger.info(f"Failed: {self.test_results['failed_tests']} ❌")
        
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100 if self.test_results['total_tests'] > 0 else 0
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 PHASE 1 DURATION MANAGEMENT SYSTEM ENHANCEMENT: EXCELLENT RESULTS")
        elif success_rate >= 75:
            logger.info("✅ PHASE 1 DURATION MANAGEMENT SYSTEM ENHANCEMENT: GOOD RESULTS")
        else:
            logger.info("⚠️ PHASE 1 DURATION MANAGEMENT SYSTEM ENHANCEMENT: NEEDS ATTENTION")
        
        return self.test_results

if __name__ == "__main__":
    tester = Phase1DurationTester()
    results = tester.run_comprehensive_test_suite()
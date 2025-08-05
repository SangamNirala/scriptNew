#!/usr/bin/env python3
"""
CRITICAL PRIORITY: Review Status Endpoint Testing
Testing the GET /api/attorney/review/status/{review_id} endpoint after frontend fix
"""

import requests
import json
import uuid
import time
from datetime import datetime

class ReviewStatusTester:
    def __init__(self, base_url="https://fc97b1b7-4b93-4d34-bd23-377526b1046f.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.review_id = None
        self.attorney_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'List with ' + str(len(response_data)) + ' items'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_test_data(self):
        """Create attorney and submit document for review to get valid review_id"""
        print("\n🔧 Setting up test data...")
        
        # Step 1: Create an attorney
        attorney_data = {
            "email": f"test.attorney.{int(time.time())}@legalmate.ai",
            "first_name": "Test",
            "last_name": "Attorney",
            "bar_number": f"BAR{int(time.time())}",
            "jurisdiction": "US",
            "role": "reviewing_attorney",
            "specializations": ["contract_law", "business_law"],
            "years_experience": 5,
            "password": "SecurePassword123!"
        }
        
        success, response = self.run_test(
            "Create Test Attorney",
            "POST",
            "attorney/create",
            200,
            attorney_data
        )
        
        if not success:
            print("❌ Failed to create test attorney")
            return False
        
        # Step 2: Login attorney to get attorney_id
        login_data = {
            "email": attorney_data["email"],
            "password": attorney_data["password"]
        }
        
        success, response = self.run_test(
            "Attorney Login",
            "POST",
            "attorney/login",
            200,
            login_data
        )
        
        if success and 'attorney' in response:
            self.attorney_id = response['attorney'].get('id')
            print(f"   Attorney ID: {self.attorney_id}")
        else:
            print("❌ Failed to login attorney")
            return False
        
        # Step 3: Submit document for review
        review_data = {
            "document_content": "This is a test contract for review status endpoint testing. The contract contains standard terms and conditions for a service agreement between two parties.",
            "document_type": "contract",
            "client_id": f"client_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            "original_request": {
                "contract_type": "service_agreement",
                "jurisdiction": "US",
                "parties": {
                    "party1_name": "Test Company Inc.",
                    "party2_name": "Service Provider LLC"
                }
            },
            "priority": "normal"
        }
        
        success, response = self.run_test(
            "Submit Document for Review",
            "POST",
            "attorney/review/submit",
            200,
            review_data
        )
        
        if success and 'review_id' in response:
            self.review_id = response['review_id']
            print(f"   Review ID: {self.review_id}")
            return True
        else:
            print("❌ Failed to submit document for review")
            return False

    def test_review_status_valid_id(self):
        """Test GET /api/attorney/review/status/{review_id} with valid review_id"""
        if not self.review_id:
            print("⚠️  Skipping valid review status test - no review ID available")
            return False, {}
        
        success, response = self.run_test(
            "Review Status - Valid ID",
            "GET",
            f"attorney/review/status/{self.review_id}",
            200
        )
        
        if success:
            # Verify response structure
            expected_fields = [
                'review_id', 'status', 'created_at', 'estimated_completion_time',
                'priority', 'progress_percentage', 'assigned_attorney', 'comments'
            ]
            
            missing_fields = []
            for field in expected_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️  Missing expected fields: {missing_fields}")
            else:
                print(f"   ✅ All expected fields present in response")
            
            # Verify specific field values
            if response.get('review_id') == self.review_id:
                print(f"   ✅ Review ID matches: {self.review_id}")
            else:
                print(f"   ❌ Review ID mismatch - Expected: {self.review_id}, Got: {response.get('review_id')}")
            
            # Check status value
            status = response.get('status')
            valid_statuses = ['pending', 'in_review', 'approved', 'rejected', 'needs_revision']
            if status in valid_statuses:
                print(f"   ✅ Valid status: {status}")
            else:
                print(f"   ❌ Invalid status: {status} (expected one of {valid_statuses})")
            
            # Check progress percentage
            progress = response.get('progress_percentage')
            if isinstance(progress, (int, float)) and 0 <= progress <= 100:
                print(f"   ✅ Valid progress percentage: {progress}%")
            else:
                print(f"   ❌ Invalid progress percentage: {progress}")
            
            # Check assigned attorney info
            assigned_attorney = response.get('assigned_attorney')
            if assigned_attorney and isinstance(assigned_attorney, dict):
                print(f"   ✅ Assigned attorney info present: {assigned_attorney.get('name', 'Unknown')}")
            else:
                print(f"   ⚠️  No assigned attorney info or invalid format")
            
            # Check timestamps
            created_at = response.get('created_at')
            if created_at:
                print(f"   ✅ Created timestamp present: {created_at}")
            else:
                print(f"   ❌ Missing created_at timestamp")
            
            print(f"   📊 Full response structure:")
            for key, value in response.items():
                if isinstance(value, dict):
                    print(f"      {key}: {type(value).__name__} with {len(value)} fields")
                elif isinstance(value, list):
                    print(f"      {key}: {type(value).__name__} with {len(value)} items")
                else:
                    print(f"      {key}: {value}")
        
        return success, response

    def test_review_status_invalid_id(self):
        """Test GET /api/attorney/review/status/{review_id} with invalid review_id"""
        invalid_review_id = "invalid-review-id-12345"
        
        success, response = self.run_test(
            "Review Status - Invalid ID",
            "GET",
            f"attorney/review/status/{invalid_review_id}",
            404
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for invalid review ID")
            if 'error' in response or 'message' in response:
                error_msg = response.get('error') or response.get('message')
                print(f"   ✅ Error message provided: {error_msg}")
        
        return success, response

    def test_review_status_nonexistent_uuid(self):
        """Test GET /api/attorney/review/status/{review_id} with valid UUID format but non-existent"""
        nonexistent_id = str(uuid.uuid4())
        
        success, response = self.run_test(
            "Review Status - Non-existent UUID",
            "GET",
            f"attorney/review/status/{nonexistent_id}",
            404
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for non-existent review ID")
            print(f"   Test UUID: {nonexistent_id}")
        
        return success, response

    def test_review_status_multiple_calls(self):
        """Test multiple calls to review status endpoint for stability"""
        if not self.review_id:
            print("⚠️  Skipping multiple calls test - no review ID available")
            return False, {}
        
        print(f"\n🔄 Testing endpoint stability with multiple calls...")
        
        all_success = True
        responses = []
        
        for i in range(3):
            print(f"   Call {i+1}/3...")
            success, response = self.run_test(
                f"Review Status - Call {i+1}",
                "GET",
                f"attorney/review/status/{self.review_id}",
                200
            )
            
            if success:
                responses.append(response)
            else:
                all_success = False
                break
            
            # Small delay between calls
            time.sleep(0.5)
        
        if all_success and len(responses) == 3:
            # Check consistency across calls
            first_response = responses[0]
            consistent = True
            
            for i, response in enumerate(responses[1:], 2):
                if response.get('review_id') != first_response.get('review_id'):
                    print(f"   ❌ Review ID inconsistent in call {i}")
                    consistent = False
                if response.get('status') != first_response.get('status'):
                    print(f"   ❌ Status inconsistent in call {i}")
                    consistent = False
            
            if consistent:
                print(f"   ✅ All 3 calls returned consistent data")
            else:
                print(f"   ❌ Inconsistent data across multiple calls")
                all_success = False
        
        return all_success, {"calls": len(responses), "responses": responses}

    def test_review_status_endpoint_performance(self):
        """Test review status endpoint response time"""
        if not self.review_id:
            print("⚠️  Skipping performance test - no review ID available")
            return False, {}
        
        print(f"\n⏱️  Testing endpoint performance...")
        
        start_time = time.time()
        success, response = self.run_test(
            "Review Status - Performance Test",
            "GET",
            f"attorney/review/status/{self.review_id}",
            200
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"   Response time: {response_time:.3f} seconds")
        
        if response_time < 2.0:
            print(f"   ✅ Good response time (< 2 seconds)")
        elif response_time < 5.0:
            print(f"   ⚠️  Acceptable response time (< 5 seconds)")
        else:
            print(f"   ❌ Slow response time (> 5 seconds)")
        
        return success, {"response_time": response_time, "response": response}

    def run_all_tests(self):
        """Run all review status endpoint tests"""
        print("=" * 80)
        print("🎯 CRITICAL PRIORITY: Review Status Endpoint Testing")
        print("Testing GET /api/attorney/review/status/{review_id} after frontend fix")
        print("=" * 80)
        
        # Setup test data
        if not self.setup_test_data():
            print("\n❌ CRITICAL FAILURE: Could not set up test data")
            return False
        
        print(f"\n📋 Running Review Status Endpoint Tests...")
        print(f"   Review ID: {self.review_id}")
        print(f"   Attorney ID: {self.attorney_id}")
        
        # Run all tests
        test_results = []
        
        # Test 1: Valid review ID
        success, response = self.test_review_status_valid_id()
        test_results.append(("Valid Review ID", success))
        
        # Test 2: Invalid review ID
        success, response = self.test_review_status_invalid_id()
        test_results.append(("Invalid Review ID", success))
        
        # Test 3: Non-existent UUID
        success, response = self.test_review_status_nonexistent_uuid()
        test_results.append(("Non-existent UUID", success))
        
        # Test 4: Multiple calls for stability
        success, response = self.test_review_status_multiple_calls()
        test_results.append(("Multiple Calls Stability", success))
        
        # Test 5: Performance test
        success, response = self.test_review_status_endpoint_performance()
        test_results.append(("Performance Test", success))
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 REVIEW STATUS ENDPOINT TEST RESULTS")
        print("=" * 80)
        
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 Overall Results:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} test scenarios)")
        
        if success_rate >= 80:
            print(f"\n🎉 REVIEW STATUS ENDPOINT: WORKING CORRECTLY")
            print(f"   The frontend 'Failed to fetch review status' issue should be resolved!")
        else:
            print(f"\n❌ REVIEW STATUS ENDPOINT: ISSUES DETECTED")
            print(f"   The endpoint may still have problems that need attention.")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ReviewStatusTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n✅ CRITICAL SUCCESS: Review Status endpoint is working correctly!")
        exit(0)
    else:
        print(f"\n❌ CRITICAL FAILURE: Review Status endpoint has issues!")
        exit(1)
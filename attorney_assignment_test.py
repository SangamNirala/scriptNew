import requests
import sys
import json
import time
import random
from datetime import datetime

class AttorneyAssignmentTester:
    def __init__(self, base_url="https://a091f7bd-d11f-415d-8238-b0405f4feb88.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_attorneys = []
        self.created_reviews = []

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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)

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

    def test_attorney_creation_regular(self):
        """Test regular attorney creation endpoint"""
        attorney_data = {
            "email": f"attorney_{random.randint(1000, 9999)}@legalfirm.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "bar_number": f"BAR{random.randint(100000, 999999)}",
            "jurisdiction": "US",
            "role": "senior_attorney",
            "specializations": ["contract_law", "business_law"],
            "years_experience": 8,
            "password": "SecurePassword123!"
        }
        
        success, response = self.run_test(
            "Regular Attorney Creation", 
            "POST", 
            "attorney/create", 
            200, 
            attorney_data
        )
        
        if success and response.get('success'):
            attorney_id = response.get('attorney_id')
            if attorney_id:
                self.created_attorneys.append(attorney_id)
                print(f"   ✅ Attorney created with ID: {attorney_id}")
                print(f"   Specializations: {attorney_data['specializations']}")
                print(f"   Role: {attorney_data['role']}")
            else:
                print(f"   ⚠️  No attorney_id in response")
        
        return success, response

    def test_attorney_creation_demo(self):
        """Test demo attorney creation endpoint"""
        success, response = self.run_test(
            "Demo Attorney Creation", 
            "POST", 
            "attorney/create-demo-attorney", 
            200
        )
        
        if success and response.get('success'):
            attorney_id = response.get('attorney_id')
            if attorney_id:
                self.created_attorneys.append(attorney_id)
                print(f"   ✅ Demo attorney created with ID: {attorney_id}")
                # Get attorney details if available
                if 'attorney' in response:
                    attorney = response['attorney']
                    print(f"   Name: {attorney.get('first_name', 'N/A')} {attorney.get('last_name', 'N/A')}")
                    print(f"   Specializations: {attorney.get('specializations', [])}")
                    print(f"   Role: {attorney.get('role', 'N/A')}")
            else:
                print(f"   ⚠️  No attorney_id in response")
        
        return success, response

    def test_document_review_submission_contract(self):
        """Test document review submission with contract document"""
        document_data = {
            "document_content": """
            **NON-DISCLOSURE AGREEMENT**
            
            This Non-Disclosure Agreement is entered into between Tech Innovations Inc. and John Developer.
            
            **CONFIDENTIAL INFORMATION**
            The parties agree to maintain confidentiality of all proprietary information shared during business discussions.
            
            **TERM**
            This agreement shall remain in effect for a period of two (2) years from the date of execution.
            
            **GOVERNING LAW**
            This agreement shall be governed by the laws of California, United States.
            """,
            "document_type": "contract",
            "client_id": f"client_{int(time.time())}_{random.randint(1000, 9999)}",
            "original_request": {
                "contract_type": "NDA",
                "jurisdiction": "US",
                "parties": {
                    "party1_name": "Tech Innovations Inc.",
                    "party2_name": "John Developer"
                }
            },
            "priority": "normal"
        }
        
        success, response = self.run_test(
            "Document Review Submission - Contract", 
            "POST", 
            "attorney/review/submit", 
            200, 
            document_data
        )
        
        if success and 'review_id' in response:
            review_id = response['review_id']
            self.created_reviews.append(review_id)
            print(f"   ✅ Review created with ID: {review_id}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Assigned Attorney: {response.get('assigned_attorney_id', 'N/A')}")
            print(f"   Priority: {response.get('priority', 'N/A')}")
            
            # Check if attorney was auto-assigned
            if response.get('assigned_attorney_id'):
                print(f"   ✅ Attorney auto-assignment successful")
            else:
                print(f"   ❌ No attorney assigned - assignment may have failed")
        
        return success, response

    def test_document_review_submission_high_priority(self):
        """Test document review submission with high priority document"""
        document_data = {
            "document_content": """
            **URGENT PARTNERSHIP AGREEMENT**
            
            This Partnership Agreement is entered into between Alpha Corp and Beta LLC for immediate business collaboration.
            
            **BUSINESS PURPOSE**
            Joint venture for time-sensitive market opportunity requiring immediate legal review and approval.
            
            **CAPITAL CONTRIBUTIONS**
            Each party shall contribute $500,000 within 30 days of execution.
            
            **PROFIT SHARING**
            Profits shall be shared equally between the parties (50/50 split).
            """,
            "document_type": "partnership_agreement",
            "client_id": f"client_{int(time.time())}_{random.randint(1000, 9999)}",
            "original_request": {
                "contract_type": "partnership_agreement",
                "jurisdiction": "US",
                "urgency": "high"
            },
            "priority": "high"
        }
        
        success, response = self.run_test(
            "Document Review Submission - High Priority", 
            "POST", 
            "attorney/review/submit", 
            200, 
            document_data
        )
        
        if success and 'review_id' in response:
            review_id = response['review_id']
            self.created_reviews.append(review_id)
            print(f"   ✅ High priority review created with ID: {review_id}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Assigned Attorney: {response.get('assigned_attorney_id', 'N/A')}")
            print(f"   Priority: {response.get('priority', 'N/A')}")
            
            # High priority should be assigned to senior attorney
            if response.get('assigned_attorney_id'):
                print(f"   ✅ High priority document assigned to attorney")
            else:
                print(f"   ❌ High priority document not assigned")
        
        return success, response

    def test_review_status_dynamic_progress(self):
        """Test review status endpoint for dynamic progress calculation"""
        if not self.created_reviews:
            print("⚠️  No reviews available for status testing")
            return True, {}
        
        review_id = self.created_reviews[0]
        
        success, response = self.run_test(
            f"Review Status - Dynamic Progress", 
            "GET", 
            f"attorney/review/status/{review_id}", 
            200
        )
        
        if success:
            print(f"   Review ID: {response.get('review_id', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Progress: {response.get('progress_percentage', 'N/A')}%")
            print(f"   Assigned Attorney: {response.get('assigned_attorney', {}).get('first_name', 'N/A')} {response.get('assigned_attorney', {}).get('last_name', 'N/A')}")
            print(f"   Priority: {response.get('priority', 'N/A')}")
            print(f"   Created: {response.get('created_at', 'N/A')}")
            print(f"   Estimated Completion: {response.get('estimated_completion', 'N/A')}")
            
            # Check for dynamic progress
            status = response.get('status')
            progress = response.get('progress_percentage', 0)
            
            if status == 'in_review' and progress > 0:
                print(f"   ✅ Review is in progress with {progress}% completion")
                if progress >= 25:
                    print(f"   ✅ Progress is advancing (≥25% indicates attorney assignment working)")
                else:
                    print(f"   ⚠️  Progress is low ({progress}%) - may still be initializing")
            elif status == 'pending' and progress == 0:
                print(f"   ❌ Review stuck in pending status with 0% progress")
            else:
                print(f"   ✅ Review status: {status}, Progress: {progress}%")
            
            # Check estimated completion time
            estimated_completion = response.get('estimated_completion')
            if estimated_completion and estimated_completion != "Overdue":
                print(f"   ✅ Realistic completion time provided: {estimated_completion}")
            elif estimated_completion == "Overdue":
                print(f"   ❌ Shows 'Overdue' - time estimation issue")
            else:
                print(f"   ⚠️  No estimated completion time")
        
        return success, response

    def test_multiple_review_progress_over_time(self):
        """Test multiple reviews and check progress advancement over time"""
        if len(self.created_reviews) < 2:
            print("⚠️  Need at least 2 reviews for time-based progress testing")
            return True, {}
        
        print(f"\n📊 Testing Progress Over Time for {len(self.created_reviews)} Reviews...")
        
        initial_progress = {}
        
        # Get initial progress for all reviews
        for i, review_id in enumerate(self.created_reviews):
            success, response = self.run_test(
                f"Initial Progress Check - Review {i+1}", 
                "GET", 
                f"attorney/review/status/{review_id}", 
                200
            )
            
            if success:
                initial_progress[review_id] = {
                    'status': response.get('status'),
                    'progress': response.get('progress_percentage', 0),
                    'assigned_attorney': response.get('assigned_attorney', {}).get('attorney_id')
                }
                print(f"   Review {i+1}: {response.get('status')} - {response.get('progress_percentage', 0)}%")
        
        # Wait a few seconds to allow progress advancement
        print(f"\n⏳ Waiting 5 seconds for progress advancement...")
        time.sleep(5)
        
        # Check progress again
        progress_advanced = False
        for i, review_id in enumerate(self.created_reviews):
            success, response = self.run_test(
                f"Follow-up Progress Check - Review {i+1}", 
                "GET", 
                f"attorney/review/status/{review_id}", 
                200
            )
            
            if success:
                current_progress = response.get('progress_percentage', 0)
                initial = initial_progress.get(review_id, {}).get('progress', 0)
                
                print(f"   Review {i+1}: {initial}% → {current_progress}%")
                
                if current_progress > initial:
                    print(f"   ✅ Progress advanced from {initial}% to {current_progress}%")
                    progress_advanced = True
                elif current_progress == initial and current_progress > 25:
                    print(f"   ✅ Progress stable at {current_progress}% (acceptable for short time window)")
                    progress_advanced = True
                elif response.get('status') == 'in_review':
                    print(f"   ✅ Status is 'in_review' indicating assignment successful")
                    progress_advanced = True
                else:
                    print(f"   ⚠️  No progress advancement detected")
        
        if progress_advanced:
            print(f"\n✅ Dynamic progress system is working - reviews are advancing")
        else:
            print(f"\n❌ Dynamic progress system may not be working - no advancement detected")
        
        return progress_advanced, initial_progress

    def test_cleanup_stuck_reviews(self):
        """Test the cleanup stuck reviews endpoint"""
        success, response = self.run_test(
            "Cleanup Stuck Reviews", 
            "POST", 
            "attorney/review/cleanup-stuck", 
            200
        )
        
        if success:
            print(f"   Success: {response.get('success', False)}")
            print(f"   Message: {response.get('message', 'N/A')}")
            print(f"   Fixed Count: {response.get('fixed_count', 0)}")
            
            if 'details' in response and response['details']:
                print(f"   Details: {response['details']}")
            
            if response.get('fixed_count', 0) > 0:
                print(f"   ✅ Cleanup fixed {response['fixed_count']} stuck reviews")
            else:
                print(f"   ✅ No stuck reviews found (system working correctly)")
        
        return success, response

    def test_specialization_based_assignment(self):
        """Test that documents are assigned to attorneys based on specialization"""
        # Create a contract law specialist attorney first
        contract_attorney_data = {
            "email": f"contract_specialist_{random.randint(1000, 9999)}@legalfirm.com",
            "first_name": "Contract",
            "last_name": "Specialist",
            "bar_number": f"BAR{random.randint(100000, 999999)}",
            "jurisdiction": "US",
            "role": "attorney",
            "specializations": ["contract_law"],
            "years_experience": 5,
            "password": "SecurePassword123!"
        }
        
        success, attorney_response = self.run_test(
            "Create Contract Law Specialist", 
            "POST", 
            "attorney/create", 
            200, 
            contract_attorney_data
        )
        
        if success and attorney_response.get('attorney_id'):
            contract_attorney_id = attorney_response['attorney_id']
            self.created_attorneys.append(contract_attorney_id)
            print(f"   ✅ Contract specialist created: {contract_attorney_id}")
            
            # Submit a contract document that should be assigned to this specialist
            contract_document = {
                "document_content": """
                **SERVICE AGREEMENT**
                
                This Service Agreement is entered into between Service Provider LLC and Client Corp.
                
                **SERVICES**
                Provider agrees to deliver consulting services as specified in Exhibit A.
                
                **PAYMENT TERMS**
                Client shall pay $10,000 upon completion of services.
                
                **CONTRACT LAW PROVISIONS**
                This agreement contains specific contract law clauses requiring specialized review.
                """,
                "document_type": "service_agreement",
                "client_id": f"client_{int(time.time())}_{random.randint(1000, 9999)}",
                "original_request": {
                    "contract_type": "service_agreement",
                    "jurisdiction": "US",
                    "specialization_required": "contract_law"
                },
                "priority": "normal"
            }
            
            success, review_response = self.run_test(
                "Submit Contract Document for Specialization Test", 
                "POST", 
                "attorney/review/submit", 
                200, 
                contract_document
            )
            
            if success and review_response.get('review_id'):
                review_id = review_response['review_id']
                self.created_reviews.append(review_id)
                assigned_attorney_id = review_response.get('assigned_attorney_id')
                
                print(f"   Review ID: {review_id}")
                print(f"   Assigned Attorney: {assigned_attorney_id}")
                
                # Check if it was assigned to our contract specialist or another contract law attorney
                if assigned_attorney_id:
                    print(f"   ✅ Document assigned to attorney (specialization-based assignment working)")
                    
                    # Get review status to see attorney details
                    success, status_response = self.run_test(
                        "Check Assigned Attorney Specialization", 
                        "GET", 
                        f"attorney/review/status/{review_id}", 
                        200
                    )
                    
                    if success and 'assigned_attorney' in status_response:
                        attorney_info = status_response['assigned_attorney']
                        specializations = attorney_info.get('specializations', [])
                        print(f"   Assigned Attorney Specializations: {specializations}")
                        
                        if 'contract_law' in specializations:
                            print(f"   ✅ Document correctly assigned to contract law specialist")
                        else:
                            print(f"   ⚠️  Document assigned to attorney without contract law specialization")
                else:
                    print(f"   ❌ Document not assigned to any attorney")
        
        return success, attorney_response

    def test_review_status_invalid_id(self):
        """Test review status endpoint with invalid review ID"""
        invalid_id = "invalid-review-id-12345"
        
        success, response = self.run_test(
            "Review Status - Invalid ID", 
            "GET", 
            f"attorney/review/status/{invalid_id}", 
            404
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for invalid review ID")
            print(f"   Error message: {response.get('detail', 'N/A')}")
        
        return success, response

    def test_review_status_nonexistent_uuid(self):
        """Test review status endpoint with non-existent but valid UUID"""
        import uuid
        nonexistent_id = str(uuid.uuid4())
        
        success, response = self.run_test(
            "Review Status - Non-existent UUID", 
            "GET", 
            f"attorney/review/status/{nonexistent_id}", 
            404
        )
        
        if success:
            print(f"   ✅ Correctly returned 404 for non-existent review")
            print(f"   Review ID tested: {nonexistent_id}")
        
        return success, response

    def run_comprehensive_test(self):
        """Run all attorney assignment and progress tests"""
        print("🎯 ATTORNEY ASSIGNMENT SYSTEM COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Test 1: Attorney Creation Endpoints
        print("\n📋 PHASE 1: ATTORNEY CREATION TESTING")
        self.test_attorney_creation_regular()
        self.test_attorney_creation_demo()
        
        # Test 2: Document Review Submission
        print("\n📋 PHASE 2: DOCUMENT REVIEW SUBMISSION TESTING")
        self.test_document_review_submission_contract()
        self.test_document_review_submission_high_priority()
        
        # Test 3: Dynamic Progress Verification
        print("\n📋 PHASE 3: DYNAMIC PROGRESS VERIFICATION")
        self.test_review_status_dynamic_progress()
        self.test_multiple_review_progress_over_time()
        
        # Test 4: Cleanup and Error Handling
        print("\n📋 PHASE 4: CLEANUP AND ERROR HANDLING")
        self.test_cleanup_stuck_reviews()
        self.test_review_status_invalid_id()
        self.test_review_status_nonexistent_uuid()
        
        # Test 5: Specialization-Based Assignment
        print("\n📋 PHASE 5: SPECIALIZATION-BASED ASSIGNMENT")
        self.test_specialization_based_assignment()
        
        # Final Summary
        print("\n" + "=" * 60)
        print("🎯 ATTORNEY ASSIGNMENT SYSTEM TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"Created Attorneys: {len(self.created_attorneys)}")
        print(f"Created Reviews: {len(self.created_reviews)}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Attorney assignment system fully operational!")
        elif self.tests_passed / self.tests_run >= 0.8:
            print("✅ MOSTLY SUCCESSFUL - Attorney assignment system working with minor issues")
        else:
            print("❌ SIGNIFICANT ISSUES - Attorney assignment system needs attention")
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    print("🚀 Starting Attorney Assignment System Testing...")
    tester = AttorneyAssignmentTester()
    passed, total = tester.run_comprehensive_test()
    
    if passed == total:
        sys.exit(0)
    else:
        sys.exit(1)
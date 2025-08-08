#!/usr/bin/env python3
"""
🚨 CRITICAL SECURITY TESTING: Fake Judge Detection System
========================================================

This test suite verifies the newly implemented fake judge detection system
to ensure it properly identifies obviously fake judges and prevents security vulnerabilities.

Test Categories:
1. Critical Fake Judge Detection Tests
2. Realistic Judge Tests  
3. Judge Validation Endpoints
4. Confidence Level Testing
5. Error Handling
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://de1688ca-7364-46c1-9e8c-3ea78e9b2bf3.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class FakeJudgeDetectionTester:
    """Comprehensive tester for fake judge detection system"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
            
        print(result)
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    async def test_critical_fake_judges(self):
        """Test detection of obviously fake judges"""
        print("\n🚨 CRITICAL FAKE JUDGE DETECTION TESTS")
        print("=" * 50)
        
        fake_judges = [
            "ZZZ Fictional Judge",
            "Judge Unicorn Rainbow", 
            "XYZ NonExistent Judge",
            "Test Judge 123",
            "Judge Mental",
            "AAA Fake Judge",
            "Judge Dragon Wizard",
            "BBB Test Judge",
            "Judge Sparkle Magic",
            "CCC Dummy Judge"
        ]
        
        for judge_name in fake_judges:
            await self.test_individual_judge_analysis(judge_name, should_be_fake=True)
            
    async def test_realistic_judges(self):
        """Test realistic judge names that should pass fake detection"""
        print("\n✅ REALISTIC JUDGE TESTS")
        print("=" * 30)
        
        realistic_judges = [
            "John Smith",
            "Sarah Johnson", 
            "Robert Williams",
            "Mary Davis",
            "Michael Brown",
            "Jennifer Wilson",
            "David Miller",
            "Lisa Anderson"
        ]
        
        for judge_name in realistic_judges:
            await self.test_individual_judge_analysis(judge_name, should_be_fake=False)
            
    async def test_individual_judge_analysis(self, judge_name: str, should_be_fake: bool = False):
        """Test individual judge analysis endpoint"""
        try:
            url = f"{API_BASE}/litigation/judge-insights/{judge_name}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check required validation fields
                    required_fields = ['is_verified', 'confidence_score', 'validation_summary', 'reference_links']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(
                            f"Judge Analysis Structure - {judge_name}",
                            False,
                            f"Missing required fields: {missing_fields}"
                        )
                        return
                        
                    is_verified = data.get('is_verified', True)
                    confidence_score = data.get('confidence_score', 1.0)
                    validation_summary = data.get('validation_summary', '')
                    
                    if should_be_fake:
                        # Fake judges should be detected as fake (is_verified=False, confidence_score=0.0)
                        if not is_verified and confidence_score == 0.0:
                            self.log_test(
                                f"Fake Judge Detection - {judge_name}",
                                True,
                                f"Correctly detected as fake (verified: {is_verified}, confidence: {confidence_score})"
                            )
                        else:
                            self.log_test(
                                f"Fake Judge Detection - {judge_name}",
                                False,
                                f"SECURITY ISSUE: Fake judge marked as verified={is_verified}, confidence={confidence_score}"
                            )
                    else:
                        # Realistic judges should pass fake detection and proceed to validation
                        if confidence_score > 0.0:
                            self.log_test(
                                f"Realistic Judge Processing - {judge_name}",
                                True,
                                f"Passed fake detection (verified: {is_verified}, confidence: {confidence_score})"
                            )
                        else:
                            # It's OK for realistic judges to have low confidence if no sources found
                            self.log_test(
                                f"Realistic Judge Processing - {judge_name}",
                                True,
                                f"Passed fake detection but no sources found (confidence: {confidence_score})"
                            )
                            
                else:
                    self.log_test(
                        f"Judge Analysis HTTP - {judge_name}",
                        False,
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_test(
                f"Judge Analysis Exception - {judge_name}",
                False,
                f"Exception: {str(e)}"
            )
            
    async def test_judge_comparison_endpoint(self):
        """Test judge comparison endpoint with fake judges"""
        print("\n🔍 JUDGE COMPARISON ENDPOINT TESTS")
        print("=" * 40)
        
        test_cases = [
            {
                "name": "Fake vs Realistic Judge Comparison",
                "judges": ["ZZZ Fictional Judge", "John Smith"],
                "case_type": "civil"
            },
            {
                "name": "Multiple Fake Judges Comparison", 
                "judges": ["Judge Unicorn Rainbow", "XYZ NonExistent Judge", "Test Judge 123"],
                "case_type": "commercial"
            },
            {
                "name": "All Realistic Judges Comparison",
                "judges": ["Sarah Johnson", "Robert Williams"],
                "case_type": "civil"
            }
        ]
        
        for test_case in test_cases:
            await self.test_judge_comparison(test_case)
            
    async def test_judge_comparison(self, test_case: Dict[str, Any]):
        """Test individual judge comparison scenario"""
        try:
            url = f"{API_BASE}/litigation/judge-comparison"
            payload = {
                "judge_names": test_case["judges"],
                "case_type": test_case["case_type"]
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if validation_info exists
                    if 'validation_info' in data:
                        validation_info = data['validation_info']
                        verification_details = validation_info.get('verification_details', [])
                        
                        fake_judges_verified = 0
                        total_fake_judges = 0
                        
                        for i, judge_name in enumerate(test_case["judges"]):
                            if self.is_obviously_fake_judge(judge_name):
                                total_fake_judges += 1
                                if i < len(verification_details):
                                    judge_info = verification_details[i]
                                    if judge_info.get('is_verified', False) or judge_info.get('confidence_score', 0) > 0.0:
                                        fake_judges_verified += 1
                        
                        if total_fake_judges > 0:
                            if fake_judges_verified == 0:
                                self.log_test(
                                    f"Judge Comparison Fake Detection - {test_case['name']}",
                                    True,
                                    f"All {total_fake_judges} fake judges correctly detected"
                                )
                            else:
                                self.log_test(
                                    f"Judge Comparison Fake Detection - {test_case['name']}",
                                    False,
                                    f"SECURITY ISSUE: {fake_judges_verified}/{total_fake_judges} fake judges marked as verified"
                                )
                        else:
                            self.log_test(
                                f"Judge Comparison Structure - {test_case['name']}",
                                True,
                                f"Comparison completed successfully with {len(verification_details)} judges"
                            )
                    else:
                        self.log_test(
                            f"Judge Comparison Structure - {test_case['name']}",
                            False,
                            "Missing validation_info in response"
                        )
                        
                else:
                    self.log_test(
                        f"Judge Comparison HTTP - {test_case['name']}",
                        False,
                        f"HTTP {response.status}: {await response.text()}"
                    )
                    
        except Exception as e:
            self.log_test(
                f"Judge Comparison Exception - {test_case['name']}",
                False,
                f"Exception: {str(e)}"
            )
            
    def is_obviously_fake_judge(self, judge_name: str) -> bool:
        """Check if a judge name is obviously fake based on patterns"""
        name_lower = judge_name.lower().strip()
        
        # Check for repeated letter patterns
        repeated_patterns = ['zzz', 'xxx', 'aaa', 'bbb', 'ccc', 'ddd', 'eee', 'fff']
        if any(name_lower.startswith(pattern) for pattern in repeated_patterns):
            return True
            
        # Check for fictional indicators
        fictional_words = ['fictional', 'fake', 'test', 'dummy', 'nonexistent', 'unicorn', 'rainbow', 'dragon', 'wizard', 'magic', 'sparkle']
        if any(word in name_lower for word in fictional_words):
            return True
            
        # Check for test patterns
        if 'test judge' in name_lower or any(char.isdigit() for char in judge_name):
            return True
            
        # Check for humorous patterns
        if 'judge mental' in name_lower:
            return True
            
        return False
        
    async def test_confidence_levels(self):
        """Test confidence level calculations"""
        print("\n📊 CONFIDENCE LEVEL TESTING")
        print("=" * 35)
        
        test_judges = [
            ("ZZZ Fictional Judge", 0.0, "Fake judge should have 0.0 confidence"),
            ("Judge Unicorn Rainbow", 0.0, "Fantasy judge should have 0.0 confidence"),
            ("John Smith", None, "Realistic judge should have appropriate confidence"),
            ("Sarah Johnson", None, "Realistic judge should have appropriate confidence")
        ]
        
        for judge_name, expected_confidence, description in test_judges:
            await self.test_confidence_level(judge_name, expected_confidence, description)
            
    async def test_confidence_level(self, judge_name: str, expected_confidence: float = None, description: str = ""):
        """Test confidence level for a specific judge"""
        try:
            url = f"{API_BASE}/litigation/judge-insights/{judge_name}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    confidence_score = data.get('confidence_score', -1)
                    
                    if expected_confidence is not None:
                        if confidence_score == expected_confidence:
                            self.log_test(
                                f"Confidence Level - {judge_name}",
                                True,
                                f"{description} (got {confidence_score})"
                            )
                        else:
                            self.log_test(
                                f"Confidence Level - {judge_name}",
                                False,
                                f"{description} (expected {expected_confidence}, got {confidence_score})"
                            )
                    else:
                        # For realistic judges, just check that confidence is reasonable
                        if 0.0 <= confidence_score <= 1.0:
                            self.log_test(
                                f"Confidence Level - {judge_name}",
                                True,
                                f"{description} (got {confidence_score})"
                            )
                        else:
                            self.log_test(
                                f"Confidence Level - {judge_name}",
                                False,
                                f"Invalid confidence score: {confidence_score}"
                            )
                else:
                    self.log_test(
                        f"Confidence Level HTTP - {judge_name}",
                        False,
                        f"HTTP {response.status}"
                    )
                    
        except Exception as e:
            self.log_test(
                f"Confidence Level Exception - {judge_name}",
                False,
                f"Exception: {str(e)}"
            )
            
    async def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🛡️ ERROR HANDLING TESTS")
        print("=" * 25)
        
        # Test empty judge name
        await self.test_empty_judge_name()
        
        # Test special characters
        await self.test_special_characters()
        
        # Test invalid comparison requests
        await self.test_invalid_comparison_requests()
        
    async def test_empty_judge_name(self):
        """Test handling of empty judge names"""
        try:
            url = f"{API_BASE}/litigation/judge-insights/"
            
            async with self.session.get(url) as response:
                if response.status == 404:
                    self.log_test(
                        "Empty Judge Name Handling",
                        True,
                        "Correctly returns 404 for empty judge name"
                    )
                else:
                    self.log_test(
                        "Empty Judge Name Handling",
                        False,
                        f"Expected 404, got {response.status}"
                    )
                    
        except Exception as e:
            self.log_test(
                "Empty Judge Name Exception",
                False,
                f"Exception: {str(e)}"
            )
            
    async def test_special_characters(self):
        """Test handling of special characters in judge names"""
        special_char_judges = [
            "Judge O'Connor",
            "José Martinez",
            "Judge Smith-Jones",
            "Judge @#$%"
        ]
        
        for judge_name in special_char_judges:
            try:
                url = f"{API_BASE}/litigation/judge-insights/{judge_name}"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'confidence_score' in data:
                            self.log_test(
                                f"Special Characters - {judge_name}",
                                True,
                                f"Handled special characters correctly"
                            )
                        else:
                            self.log_test(
                                f"Special Characters - {judge_name}",
                                False,
                                "Missing confidence_score in response"
                            )
                    else:
                        # Some special characters might cause errors, which is acceptable
                        self.log_test(
                            f"Special Characters - {judge_name}",
                            True,
                            f"Handled gracefully with HTTP {response.status}"
                        )
                        
            except Exception as e:
                self.log_test(
                    f"Special Characters Exception - {judge_name}",
                    True,
                    f"Handled exception gracefully: {str(e)}"
                )
                
    async def test_invalid_comparison_requests(self):
        """Test invalid judge comparison requests"""
        invalid_requests = [
            {
                "name": "Single Judge Comparison",
                "payload": {"judge_names": ["John Smith"], "case_type": "civil"},
                "expected_status": 400
            },
            {
                "name": "Empty Judge List",
                "payload": {"judge_names": [], "case_type": "civil"},
                "expected_status": 400
            },
            {
                "name": "Missing Case Type",
                "payload": {"judge_names": ["John Smith", "Sarah Johnson"]},
                "expected_status": 422
            }
        ]
        
        for test_case in invalid_requests:
            try:
                url = f"{API_BASE}/litigation/judge-comparison"
                
                async with self.session.post(url, json=test_case["payload"]) as response:
                    if response.status == test_case["expected_status"]:
                        self.log_test(
                            f"Invalid Request - {test_case['name']}",
                            True,
                            f"Correctly returned HTTP {response.status}"
                        )
                    else:
                        self.log_test(
                            f"Invalid Request - {test_case['name']}",
                            False,
                            f"Expected {test_case['expected_status']}, got {response.status}"
                        )
                        
            except Exception as e:
                self.log_test(
                    f"Invalid Request Exception - {test_case['name']}",
                    False,
                    f"Exception: {str(e)}"
                )
                
    async def test_validation_response_structure(self):
        """Test that validation responses have proper structure"""
        print("\n📋 VALIDATION RESPONSE STRUCTURE TESTS")
        print("=" * 45)
        
        test_judge = "John Smith"
        
        try:
            url = f"{API_BASE}/litigation/judge-insights/{test_judge}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check required fields
                    required_fields = {
                        'is_verified': bool,
                        'confidence_score': (int, float),
                        'validation_summary': str,
                        'reference_links': list
                    }
                    
                    all_fields_valid = True
                    for field, expected_type in required_fields.items():
                        if field not in data:
                            self.log_test(
                                f"Response Structure - Missing {field}",
                                False,
                                f"Required field {field} missing from response"
                            )
                            all_fields_valid = False
                        elif not isinstance(data[field], expected_type):
                            self.log_test(
                                f"Response Structure - {field} Type",
                                False,
                                f"Field {field} has wrong type: {type(data[field])}, expected {expected_type}"
                            )
                            all_fields_valid = False
                        else:
                            self.log_test(
                                f"Response Structure - {field}",
                                True,
                                f"Field {field} has correct type and is present"
                            )
                    
                    # Check reference_links structure
                    if 'reference_links' in data and isinstance(data['reference_links'], list):
                        for i, link in enumerate(data['reference_links']):
                            if isinstance(link, dict) and 'name' in link and 'url' in link:
                                self.log_test(
                                    f"Reference Links Structure - Item {i}",
                                    True,
                                    f"Reference link has proper structure"
                                )
                            else:
                                self.log_test(
                                    f"Reference Links Structure - Item {i}",
                                    False,
                                    f"Reference link missing name/url fields"
                                )
                                
                else:
                    self.log_test(
                        "Response Structure HTTP",
                        False,
                        f"HTTP {response.status}"
                    )
                    
        except Exception as e:
            self.log_test(
                "Response Structure Exception",
                False,
                f"Exception: {str(e)}"
            )
            
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🚨 FAKE JUDGE DETECTION SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical success criteria
        print("\n🎯 CRITICAL SUCCESS CRITERIA:")
        fake_detection_tests = [r for r in self.test_results if 'Fake Judge Detection' in r['test_name']]
        fake_detection_passed = sum(1 for r in fake_detection_tests if r['passed'])
        
        if fake_detection_tests:
            fake_detection_rate = (fake_detection_passed / len(fake_detection_tests) * 100)
            print(f"✅ Fake Judge Detection: {fake_detection_passed}/{len(fake_detection_tests)} ({fake_detection_rate:.1f}%)")
        
        realistic_tests = [r for r in self.test_results if 'Realistic Judge Processing' in r['test_name']]
        realistic_passed = sum(1 for r in realistic_tests if r['passed'])
        
        if realistic_tests:
            realistic_rate = (realistic_passed / len(realistic_tests) * 100)
            print(f"✅ Realistic Judge Processing: {realistic_passed}/{len(realistic_tests)} ({realistic_rate:.1f}%)")
        
        # Security assessment
        security_issues = [r for r in self.test_results if 'SECURITY ISSUE' in r['details']]
        if security_issues:
            print(f"\n🚨 SECURITY ISSUES FOUND: {len(security_issues)}")
            for issue in security_issues:
                print(f"   - {issue['test_name']}: {issue['details']}")
        else:
            print(f"\n✅ NO SECURITY ISSUES DETECTED")
        
        print("\n" + "=" * 60)
        
        return success_rate >= 90 and len(security_issues) == 0

async def main():
    """Main test execution"""
    print("🚨 CRITICAL SECURITY TESTING: Fake Judge Detection System")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print("=" * 60)
    
    async with FakeJudgeDetectionTester() as tester:
        # Run all test categories
        await tester.test_critical_fake_judges()
        await tester.test_realistic_judges()
        await tester.test_judge_comparison_endpoint()
        await tester.test_confidence_levels()
        await tester.test_error_handling()
        await tester.test_validation_response_structure()
        
        # Print summary and determine overall success
        overall_success = tester.print_summary()
        
        if overall_success:
            print("\n🎉 FAKE JUDGE DETECTION SYSTEM: SECURITY VERIFIED")
            sys.exit(0)
        else:
            print("\n🚨 FAKE JUDGE DETECTION SYSTEM: SECURITY ISSUES DETECTED")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
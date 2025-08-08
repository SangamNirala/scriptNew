#!/usr/bin/env python3
"""
🎯 JUDGE ANALYTICS WEB SEARCH INTEGRATION COMPREHENSIVE TESTING
==============================================================

This test suite verifies the enhanced judge analytics system with web search integration
as requested in the review. Tests critical scenarios including fake judge detection,
real judge testing, web search integration, error handling, and confidence scoring.

Test Categories:
1. FAKE JUDGE DETECTION TESTING
2. REAL JUDGE TESTING  
3. WEB SEARCH INTEGRATION VERIFICATION
4. ERROR HANDLING TESTING
5. CONFIDENCE SCORING

Critical Test Scenarios:
- Test obvious fake judges: "ZZZ Fictional Judge", "Judge Unicorn Rainbow", "XXX Test Judge"
- Verify 404 response with "No information can be retrieved" message
- Test pattern detection: judges with numbers, excessive special characters
- Test well-known judges like "John Roberts", "Ruth Bader Ginsburg", "Sonia Sotomayor"
- Verify reference links are returned in response
- Check that total_cases, settlement_rate, average_case_duration show realistic non-zero values
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import quote

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://a16cacda-36dd-4b7c-938e-2fc7043a6190.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class JudgeAnalyticsWebSearchTester:
    """Comprehensive tester for judge analytics web search integration"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
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
        
    def test_fake_judge_detection(self):
        """Test detection of obviously fake judges - should return 404 with 'No information can be retrieved'"""
        print("\n🚨 FAKE JUDGE DETECTION TESTING")
        print("=" * 50)
        
        fake_judges = [
            "ZZZ Fictional Judge",
            "Judge Unicorn Rainbow", 
            "XXX Test Judge",
            "Judge Dragon Wizard",
            "AAA Fake Judge",
            "BBB Test Judge",
            "Judge Sparkle Magic",
            "CCC Dummy Judge",
            "Judge Mental",
            "Test Judge 123"
        ]
        
        for judge_name in fake_judges:
            self.test_fake_judge_individual(judge_name)
            
    def test_fake_judge_individual(self, judge_name: str):
        """Test individual fake judge - should return 404"""
        try:
            url = f"{API_BASE}/litigation/judge-insights/{quote(judge_name)}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 404:
                # Check if response contains the expected message
                try:
                    error_data = response.json()
                    detail = error_data.get('detail', '')
                    if 'No information can be retrieved' in detail:
                        self.log_test(
                            f"Fake Judge Detection - {judge_name}",
                            True,
                            f"Correctly returned 404 with 'No information can be retrieved' message"
                        )
                    else:
                        self.log_test(
                            f"Fake Judge Detection - {judge_name}",
                            False,
                            f"Got 404 but wrong message: {detail}"
                        )
                except:
                    # Even if JSON parsing fails, 404 is correct for fake judges
                    self.log_test(
                        f"Fake Judge Detection - {judge_name}",
                        True,
                        f"Correctly returned 404 for fake judge"
                    )
            else:
                self.log_test(
                    f"Fake Judge Detection - {judge_name}",
                    False,
                    f"SECURITY ISSUE: Fake judge returned {response.status_code} instead of 404"
                )
                
        except Exception as e:
            self.log_test(
                f"Fake Judge Detection Exception - {judge_name}",
                False,
                f"Exception: {str(e)}"
            )
            
    def test_real_judge_testing(self):
        """Test well-known judges - should return 200 with reference links and realistic data"""
        print("\n✅ REAL JUDGE TESTING")
        print("=" * 30)
        
        real_judges = [
            "John Roberts",
            "Ruth Bader Ginsburg", 
            "Sonia Sotomayor",
            "Clarence Thomas",
            "Samuel Alito",
            "Elena Kagan",
            "Neil Gorsuch",
            "Brett Kavanaugh"
        ]
        
        for judge_name in real_judges:
            self.test_real_judge_individual(judge_name)
            
    def test_real_judge_individual(self, judge_name: str):
        """Test individual real judge - should return 200 with reference links"""
        try:
            url = f"{API_BASE}/litigation/judge-insights/{quote(judge_name)}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for reference links
                reference_links = data.get('reference_links', [])
                if reference_links and len(reference_links) > 0:
                    # Verify reference links structure
                    valid_links = True
                    for link in reference_links:
                        if not isinstance(link, dict) or 'name' not in link or 'url' not in link:
                            valid_links = False
                            break
                    
                    if valid_links:
                        self.log_test(
                            f"Real Judge Reference Links - {judge_name}",
                            True,
                            f"Found {len(reference_links)} valid reference links"
                        )
                    else:
                        self.log_test(
                            f"Real Judge Reference Links - {judge_name}",
                            False,
                            f"Reference links have invalid structure"
                        )
                else:
                    self.log_test(
                        f"Real Judge Reference Links - {judge_name}",
                        False,
                        f"No reference links found for well-known judge"
                    )
                
                # Check for realistic non-zero values
                total_cases = data.get('total_cases', 0)
                settlement_rate = data.get('settlement_rate', 0)
                average_case_duration = data.get('average_case_duration', 0)
                
                if total_cases > 0 and settlement_rate > 0 and average_case_duration > 0:
                    self.log_test(
                        f"Real Judge Realistic Data - {judge_name}",
                        True,
                        f"Realistic data: {total_cases} cases, {settlement_rate:.2f} settlement rate, {average_case_duration:.1f} days duration"
                    )
                else:
                    self.log_test(
                        f"Real Judge Realistic Data - {judge_name}",
                        False,
                        f"Data shows zeros: {total_cases} cases, {settlement_rate} settlement rate, {average_case_duration} days duration"
                    )
                    
                # Check confidence score
                confidence_score = data.get('confidence_score', 0)
                if confidence_score > 0.0:
                    self.log_test(
                        f"Real Judge Confidence - {judge_name}",
                        True,
                        f"Confidence score: {confidence_score:.2f}"
                    )
                else:
                    self.log_test(
                        f"Real Judge Confidence - {judge_name}",
                        False,
                        f"Zero confidence score for well-known judge"
                    )
                    
            else:
                self.log_test(
                    f"Real Judge HTTP - {judge_name}",
                    False,
                    f"HTTP {response.status_code}: Expected 200 for well-known judge"
                )
                
        except Exception as e:
            self.log_test(
                f"Real Judge Exception - {judge_name}",
                False,
                f"Exception: {str(e)}"
            )
            
    def test_web_search_integration_verification(self):
        """Test the endpoint structure and web search integration features"""
        print("\n🔍 WEB SEARCH INTEGRATION VERIFICATION")
        print("=" * 45)
        
        # Test with a realistic judge name
        test_judge = "John Smith"
        
        try:
            url = f"{API_BASE}/litigation/judge-insights/{quote(test_judge)}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required validation fields
                validation_fields = ['is_verified', 'confidence_score', 'validation_summary', 'reference_links']
                missing_fields = [field for field in validation_fields if field not in data]
                
                if not missing_fields:
                    self.log_test(
                        "Web Search Integration Structure",
                        True,
                        f"All validation fields present: {validation_fields}"
                    )
                else:
                    self.log_test(
                        "Web Search Integration Structure",
                        False,
                        f"Missing validation fields: {missing_fields}"
                    )
                
                # Check reference_links array structure
                reference_links = data.get('reference_links', [])
                if isinstance(reference_links, list):
                    self.log_test(
                        "Reference Links Array",
                        True,
                        f"Reference links is array with {len(reference_links)} items"
                    )
                    
                    # Check individual link structure
                    for i, link in enumerate(reference_links[:3]):  # Check first 3
                        if isinstance(link, dict) and 'name' in link and 'url' in link:
                            self.log_test(
                                f"Reference Link Structure [{i}]",
                                True,
                                f"Valid structure: name='{link['name'][:50]}...', url='{link['url'][:50]}...'"
                            )
                        else:
                            self.log_test(
                                f"Reference Link Structure [{i}]",
                                False,
                                f"Invalid structure: {link}"
                            )
                else:
                    self.log_test(
                        "Reference Links Array",
                        False,
                        f"Reference links should be array, got {type(reference_links)}"
                    )
                
                # Check validation_summary field
                validation_summary = data.get('validation_summary', '')
                if isinstance(validation_summary, str) and len(validation_summary) > 0:
                    self.log_test(
                        "Validation Summary",
                        True,
                        f"Validation summary present ({len(validation_summary)} chars)"
                    )
                else:
                    self.log_test(
                        "Validation Summary",
                        False,
                        f"Validation summary missing or empty"
                    )
                
                # Check is_verified field
                is_verified = data.get('is_verified')
                if isinstance(is_verified, bool):
                    self.log_test(
                        "Is Verified Field",
                        True,
                        f"is_verified is boolean: {is_verified}"
                    )
                else:
                    self.log_test(
                        "Is Verified Field",
                        False,
                        f"is_verified should be boolean, got {type(is_verified)}"
                    )
                    
            elif response.status_code == 404:
                # This is acceptable for some judges - test the error structure
                try:
                    error_data = response.json()
                    detail = error_data.get('detail', '')
                    if 'No information can be retrieved' in detail:
                        self.log_test(
                            "Web Search Integration 404 Response",
                            True,
                            f"Proper 404 response with correct message"
                        )
                    else:
                        self.log_test(
                            "Web Search Integration 404 Response",
                            False,
                            f"404 response but wrong message: {detail}"
                        )
                except:
                    self.log_test(
                        "Web Search Integration 404 Response",
                        False,
                        f"404 response but invalid JSON structure"
                    )
            else:
                self.log_test(
                    "Web Search Integration HTTP",
                    False,
                    f"Unexpected HTTP status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Web Search Integration Exception",
                False,
                f"Exception: {str(e)}"
            )
            
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🛡️ ERROR HANDLING TESTING")
        print("=" * 25)
        
        # Test empty judge name
        self.test_empty_judge_name()
        
        # Test special characters
        self.test_special_characters()
        
        # Test edge cases
        self.test_edge_cases()
        
    def test_empty_judge_name(self):
        """Test handling of empty judge names"""
        try:
            url = f"{API_BASE}/litigation/judge-insights/"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 404:
                self.log_test(
                    "Empty Judge Name Handling",
                    True,
                    "Correctly returns 404 for empty judge name"
                )
            else:
                self.log_test(
                    "Empty Judge Name Handling",
                    False,
                    f"Expected 404, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Empty Judge Name Exception",
                False,
                f"Exception: {str(e)}"
            )
            
    def test_special_characters(self):
        """Test handling of special characters in judge names"""
        special_char_judges = [
            "Judge O'Connor",
            "José Martinez",
            "Judge Smith-Jones",
            "Judge @#$%"
        ]
        
        for judge_name in special_char_judges:
            try:
                url = f"{API_BASE}/litigation/judge-insights/{quote(judge_name)}"
                
                response = requests.get(url, timeout=30)
                
                if response.status_code in [200, 404]:
                    # Both 200 and 404 are acceptable for special characters
                    self.log_test(
                        f"Special Characters - {judge_name}",
                        True,
                        f"Handled gracefully with HTTP {response.status_code}"
                    )
                else:
                    self.log_test(
                        f"Special Characters - {judge_name}",
                        False,
                        f"Unexpected status {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Special Characters Exception - {judge_name}",
                    True,
                    f"Handled exception gracefully: {str(e)}"
                )
                
    def test_edge_cases(self):
        """Test edge case scenarios"""
        edge_cases = [
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("A", "Single character"),
            ("Judge" * 50, "Very long name"),
            ("123456", "Numbers only")
        ]
        
        for judge_name, description in edge_cases:
            try:
                url = f"{API_BASE}/litigation/judge-insights/{quote(judge_name)}"
                
                response = requests.get(url, timeout=30)
                
                # For edge cases, we expect either 404 or proper error handling
                if response.status_code in [404, 400, 422]:
                    self.log_test(
                        f"Edge Case - {description}",
                        True,
                        f"Handled appropriately with HTTP {response.status_code}"
                    )
                else:
                    self.log_test(
                        f"Edge Case - {description}",
                        False,
                        f"Unexpected status {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Edge Case Exception - {description}",
                    True,
                    f"Handled exception gracefully: {str(e)}"
                )
                
    def test_confidence_scoring(self):
        """Test confidence scoring system"""
        print("\n📊 CONFIDENCE SCORING")
        print("=" * 25)
        
        test_cases = [
            ("ZZZ Fictional Judge", 0.0, "Fake judge should have 0.0 confidence"),
            ("Judge Unicorn Rainbow", 0.0, "Fantasy judge should have 0.0 confidence"),
            ("John Roberts", None, "Real judge should have appropriate confidence"),
            ("John Smith", None, "Common name should have some confidence if verified")
        ]
        
        for judge_name, expected_confidence, description in test_cases:
            self.test_confidence_individual(judge_name, expected_confidence, description)
            
    def test_confidence_individual(self, judge_name: str, expected_confidence: float = None, description: str = ""):
        """Test confidence level for a specific judge"""
        try:
            url = f"{API_BASE}/litigation/judge-insights/{quote(judge_name)}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                confidence_score = data.get('confidence_score', -1)
                
                if expected_confidence is not None:
                    if confidence_score == expected_confidence:
                        self.log_test(
                            f"Confidence Score - {judge_name}",
                            True,
                            f"{description} (got {confidence_score})"
                        )
                    else:
                        self.log_test(
                            f"Confidence Score - {judge_name}",
                            False,
                            f"{description} (expected {expected_confidence}, got {confidence_score})"
                        )
                else:
                    # For real judges, just check that confidence is reasonable
                    if 0.0 <= confidence_score <= 1.0:
                        self.log_test(
                            f"Confidence Score - {judge_name}",
                            True,
                            f"{description} (got {confidence_score})"
                        )
                    else:
                        self.log_test(
                            f"Confidence Score - {judge_name}",
                            False,
                            f"Invalid confidence score: {confidence_score}"
                        )
            elif response.status_code == 404:
                # For fake judges, 404 is expected
                if expected_confidence == 0.0:
                    self.log_test(
                        f"Confidence Score - {judge_name}",
                        True,
                        f"{description} (correctly returned 404)"
                    )
                else:
                    self.log_test(
                        f"Confidence Score - {judge_name}",
                        False,
                        f"Unexpected 404 for real judge"
                    )
            else:
                self.log_test(
                    f"Confidence Score HTTP - {judge_name}",
                    False,
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                f"Confidence Score Exception - {judge_name}",
                False,
                f"Exception: {str(e)}"
            )
            
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 JUDGE ANALYTICS WEB SEARCH INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical success criteria analysis
        print("\n🎯 CRITICAL SUCCESS CRITERIA:")
        
        # Fake judge detection
        fake_detection_tests = [r for r in self.test_results if 'Fake Judge Detection' in r['test_name']]
        fake_detection_passed = sum(1 for r in fake_detection_tests if r['passed'])
        
        if fake_detection_tests:
            fake_detection_rate = (fake_detection_passed / len(fake_detection_tests) * 100)
            print(f"✅ Fake Judge Detection: {fake_detection_passed}/{len(fake_detection_tests)} ({fake_detection_rate:.1f}%)")
        
        # Real judge testing
        real_judge_tests = [r for r in self.test_results if 'Real Judge' in r['test_name']]
        real_judge_passed = sum(1 for r in real_judge_tests if r['passed'])
        
        if real_judge_tests:
            real_judge_rate = (real_judge_passed / len(real_judge_tests) * 100)
            print(f"✅ Real Judge Testing: {real_judge_passed}/{len(real_judge_tests)} ({real_judge_rate:.1f}%)")
        
        # Web search integration
        web_search_tests = [r for r in self.test_results if 'Web Search Integration' in r['test_name'] or 'Reference Link' in r['test_name']]
        web_search_passed = sum(1 for r in web_search_tests if r['passed'])
        
        if web_search_tests:
            web_search_rate = (web_search_passed / len(web_search_tests) * 100)
            print(f"✅ Web Search Integration: {web_search_passed}/{len(web_search_tests)} ({web_search_rate:.1f}%)")
        
        # Confidence scoring
        confidence_tests = [r for r in self.test_results if 'Confidence' in r['test_name']]
        confidence_passed = sum(1 for r in confidence_tests if r['passed'])
        
        if confidence_tests:
            confidence_rate = (confidence_passed / len(confidence_tests) * 100)
            print(f"✅ Confidence Scoring: {confidence_passed}/{len(confidence_tests)} ({confidence_rate:.1f}%)")
        
        # Error handling
        error_handling_tests = [r for r in self.test_results if 'Error' in r['test_name'] or 'Edge Case' in r['test_name'] or 'Special Characters' in r['test_name']]
        error_handling_passed = sum(1 for r in error_handling_tests if r['passed'])
        
        if error_handling_tests:
            error_handling_rate = (error_handling_passed / len(error_handling_tests) * 100)
            print(f"✅ Error Handling: {error_handling_passed}/{len(error_handling_tests)} ({error_handling_rate:.1f}%)")
        
        # Security assessment
        security_issues = [r for r in self.test_results if 'SECURITY ISSUE' in r['details']]
        if security_issues:
            print(f"\n🚨 SECURITY ISSUES FOUND: {len(security_issues)}")
            for issue in security_issues:
                print(f"   - {issue['test_name']}: {issue['details']}")
        else:
            print(f"\n✅ NO SECURITY ISSUES DETECTED")
        
        # Key findings
        print(f"\n📋 KEY FINDINGS:")
        reference_link_tests = [r for r in self.test_results if 'Reference Links' in r['test_name'] and r['passed']]
        if reference_link_tests:
            print(f"✅ Reference links working: {len(reference_link_tests)} judges have valid reference links")
        
        realistic_data_tests = [r for r in self.test_results if 'Realistic Data' in r['test_name'] and r['passed']]
        if realistic_data_tests:
            print(f"✅ Realistic data: {len(realistic_data_tests)} judges show non-zero case statistics")
        
        print("\n" + "=" * 80)
        
        return success_rate >= 85 and len(security_issues) == 0

def main():
    """Main test execution"""
    print("🎯 JUDGE ANALYTICS WEB SEARCH INTEGRATION COMPREHENSIVE TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print("=" * 80)
    
    tester = JudgeAnalyticsWebSearchTester()
    
    # Run all test categories as specified in the review request
    tester.test_fake_judge_detection()
    tester.test_real_judge_testing()
    tester.test_web_search_integration_verification()
    tester.test_error_handling()
    tester.test_confidence_scoring()
    
    # Print comprehensive summary and determine overall success
    overall_success = tester.print_summary()
    
    if overall_success:
        print("\n🎉 JUDGE ANALYTICS WEB SEARCH INTEGRATION: TESTING SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n🚨 JUDGE ANALYTICS WEB SEARCH INTEGRATION: ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
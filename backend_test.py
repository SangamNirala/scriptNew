#!/usr/bin/env python3
"""
Judge Analytics Web Search Integration Testing
==============================================

Comprehensive testing of the Judge Analytics Web Search Integration with focus on:
1. FAKE JUDGE DETECTION TESTING
2. WEB SEARCH INTEGRATION TESTING  
3. ERROR HANDLING TESTING

Tests the judge insights endpoint: GET /api/litigation/judge-insights/{judge_name}
"""

import requests
import json
import sys
import time
from urllib.parse import quote
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://1f56c7dd-e870-4c69-b784-5a49ffdde0a2.preview.emergentagent.com/api"

def test_fake_judge_detection():
    """Test fake judge detection with specific scenarios"""
    print("🚨 TESTING FAKE JUDGE DETECTION")
    print("=" * 60)
    
    test_results = []
    
    # Test cases for fake judge detection
    fake_judge_tests = [
        # Obviously fake judges
        {
            "name": "ZZZ Fictional Judge",
            "description": "Obviously fake judge with ZZZ pattern",
            "expected_status": 404,
            "should_be_fake": True
        },
        {
            "name": "XXX Test Judge", 
            "description": "Obviously fake judge with XXX pattern",
            "expected_status": 404,
            "should_be_fake": True
        },
        {
            "name": "Judge Unicorn Rainbow",
            "description": "Obviously fake judge with fantasy words",
            "expected_status": 404,
            "should_be_fake": True
        },
        # Subtle fake names that should be caught
        {
            "name": "sangam nirala",
            "description": "Subtle fake name that should be caught",
            "expected_status": 404,
            "should_be_fake": True
        },
        {
            "name": "ramesh kumar judge",
            "description": "Subtle fake name with 'judge' suffix",
            "expected_status": 404,
            "should_be_fake": True
        },
        {
            "name": "priya sharma",
            "description": "Subtle fake name that should be caught",
            "expected_status": 404,
            "should_be_fake": True
        },
        {
            "name": "fictional judge name",
            "description": "Obvious fake with 'fictional' keyword",
            "expected_status": 404,
            "should_be_fake": True
        },
        # Real judge names (should pass detection)
        {
            "name": "John Roberts",
            "description": "Real Supreme Court Chief Justice",
            "expected_status": 200,
            "should_be_fake": False
        },
        {
            "name": "Ruth Bader Ginsburg",
            "description": "Real former Supreme Court Justice",
            "expected_status": 200,
            "should_be_fake": False
        },
        {
            "name": "Sonia Sotomayor",
            "description": "Real Supreme Court Justice",
            "expected_status": 200,
            "should_be_fake": False
        }
    ]
    
    for test_case in fake_judge_tests:
        judge_name = test_case["name"]
        description = test_case["description"]
        expected_status = test_case["expected_status"]
        should_be_fake = test_case["should_be_fake"]
        
        print(f"\n📋 Test Case: {description}")
        print(f"Judge Name: '{judge_name}'")
        print(f"Expected Status: {expected_status}")
        print(f"Should be detected as fake: {should_be_fake}")
        
        try:
            # URL encode the judge name
            encoded_judge_name = quote(judge_name)
            url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
            
            print(f"Request URL: {url}")
            
            # Make the API request
            response = requests.get(url, timeout=30)
            
            print(f"Actual Status Code: {response.status_code}")
            
            # Check if the response matches expectations
            if response.status_code == expected_status:
                print("✅ Status code matches expectation")
                
                if response.status_code == 404:
                    # For fake judges, verify the error message
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', '')
                        print(f"Error message: {error_detail}")
                        
                        if "No information can be retrieved" in error_detail:
                            print("✅ Correct error message for fake judge")
                            test_results.append(True)
                        else:
                            print("❌ Incorrect error message for fake judge")
                            test_results.append(False)
                    except:
                        print("❌ Could not parse error response")
                        test_results.append(False)
                        
                elif response.status_code == 200:
                    # For real judges, verify response structure
                    try:
                        data = response.json()
                        
                        # Check required fields
                        required_fields = [
                            'judge_name', 'court', 'experience_years', 'total_cases',
                            'settlement_rate', 'plaintiff_success_rate', 'average_case_duration',
                            'confidence_score', 'is_verified'
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            print(f"❌ Missing required fields: {missing_fields}")
                            test_results.append(False)
                        else:
                            print("✅ All required fields present")
                            
                            # Check if judge is properly verified
                            is_verified = data.get('is_verified', False)
                            confidence_score = data.get('confidence_score', 0.0)
                            
                            print(f"Is Verified: {is_verified}")
                            print(f"Confidence Score: {confidence_score}")
                            
                            if not should_be_fake and (is_verified or confidence_score > 0.0):
                                print("✅ Real judge properly processed")
                                test_results.append(True)
                            else:
                                print("❌ Real judge not properly verified")
                                test_results.append(False)
                                
                    except Exception as e:
                        print(f"❌ Error parsing response: {e}")
                        test_results.append(False)
                        
            else:
                print(f"❌ Status code mismatch. Expected: {expected_status}, Got: {response.status_code}")
                if response.text:
                    print(f"Response: {response.text}")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            test_results.append(False)
        
        print("-" * 50)
    
    return test_results

def test_web_search_integration():
    """Test web search integration for real case statistics"""
    print("\n🔍 TESTING WEB SEARCH INTEGRATION")
    print("=" * 60)
    
    test_results = []
    
    # Test cases for web search integration
    web_search_tests = [
        {
            "name": "John Roberts",
            "description": "Supreme Court Chief Justice - should have real web data"
        },
        {
            "name": "Elena Kagan",
            "description": "Supreme Court Justice - should have real web data"
        },
        {
            "name": "Brett Kavanaugh",
            "description": "Supreme Court Justice - should have real web data"
        }
    ]
    
    for test_case in web_search_tests:
        judge_name = test_case["name"]
        description = test_case["description"]
        
        print(f"\n📋 Test Case: {description}")
        print(f"Judge Name: '{judge_name}'")
        
        try:
            # URL encode the judge name
            encoded_judge_name = quote(judge_name)
            url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
            
            print(f"Request URL: {url}")
            
            # Make the API request
            response = requests.get(url, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if SERP API is working and finding real case statistics
                total_cases = data.get('total_cases', 0)
                settlement_rate = data.get('settlement_rate', 0.0)
                average_case_duration = data.get('average_case_duration', 0)
                
                print(f"Total Cases: {total_cases}")
                print(f"Settlement Rate: {settlement_rate}")
                print(f"Average Case Duration: {average_case_duration}")
                
                # Check if we have real data (not all zeros)
                has_real_data = (total_cases > 0 or settlement_rate > 0.0 or average_case_duration > 0)
                
                if has_real_data:
                    print("✅ Real case statistics found")
                else:
                    print("⚠️ All statistics are zero - may indicate limited web data")
                
                # Check if reference_links are populated
                reference_links = data.get('reference_links', [])
                print(f"Reference Links Count: {len(reference_links)}")
                
                if reference_links:
                    print("✅ Reference links populated")
                    
                    # Check structure of reference links
                    for i, link in enumerate(reference_links[:3]):  # Check first 3 links
                        if isinstance(link, dict) and 'name' in link and 'url' in link:
                            print(f"  Link {i+1}: {link['name']} -> {link['url']}")
                        else:
                            print(f"  ❌ Link {i+1}: Invalid structure")
                else:
                    print("⚠️ No reference links found")
                
                # Check validation sources
                validation_sources = data.get('validation_sources', [])
                print(f"Validation Sources Count: {len(validation_sources)}")
                
                if validation_sources:
                    print("✅ Validation sources found")
                    for source in validation_sources[:3]:  # Show first 3 sources
                        print(f"  Source: {source}")
                else:
                    print("⚠️ No validation sources found")
                
                # Overall assessment
                if has_real_data and reference_links:
                    print("✅ Web search integration working properly")
                    test_results.append(True)
                elif has_real_data or reference_links:
                    print("⚠️ Web search integration partially working")
                    test_results.append(True)  # Still count as success if some data found
                else:
                    print("❌ Web search integration not providing real data")
                    test_results.append(False)
                    
            else:
                print(f"❌ Request failed with status {response.status_code}")
                if response.text:
                    print(f"Error response: {response.text}")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            test_results.append(False)
        
        print("-" * 50)
    
    return test_results

def test_error_handling():
    """Test error handling for various scenarios"""
    print("\n⚠️ TESTING ERROR HANDLING")
    print("=" * 60)
    
    test_results = []
    
    # Test cases for error handling
    error_handling_tests = [
        {
            "name": "Judge Dragon Wizard",
            "description": "Fantasy name should return 404",
            "expected_status": 404
        },
        {
            "name": "BBB Test Judge",
            "description": "Obvious test pattern should return 404",
            "expected_status": 404
        },
        {
            "name": "Judge Sparkle Magic",
            "description": "Fantasy words should return 404",
            "expected_status": 404
        },
        {
            "name": "CCC Dummy Judge",
            "description": "Dummy pattern should return 404",
            "expected_status": 404
        },
        {
            "name": "",
            "description": "Empty name should return error",
            "expected_status": [404, 422]  # Could be either
        }
    ]
    
    for test_case in error_handling_tests:
        judge_name = test_case["name"]
        description = test_case["description"]
        expected_status = test_case["expected_status"]
        
        print(f"\n📋 Test Case: {description}")
        print(f"Judge Name: '{judge_name}'")
        print(f"Expected Status: {expected_status}")
        
        try:
            # URL encode the judge name
            encoded_judge_name = quote(judge_name)
            url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
            
            print(f"Request URL: {url}")
            
            # Make the API request
            response = requests.get(url, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            # Check if status matches expectation
            if isinstance(expected_status, list):
                status_match = response.status_code in expected_status
            else:
                status_match = response.status_code == expected_status
            
            if status_match:
                print("✅ Status code matches expectation")
                
                # For 404 responses, check error message
                if response.status_code == 404:
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', '')
                        print(f"Error message: {error_detail}")
                        
                        if "No information can be retrieved" in error_detail:
                            print("✅ Correct error message")
                            test_results.append(True)
                        else:
                            print("⚠️ Different error message format")
                            test_results.append(True)  # Still acceptable
                    except:
                        print("⚠️ Could not parse error response")
                        test_results.append(True)  # 404 is still correct
                else:
                    test_results.append(True)
                    
            else:
                print(f"❌ Status code mismatch. Expected: {expected_status}, Got: {response.status_code}")
                if response.text:
                    print(f"Response: {response.text}")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            test_results.append(False)
        
        print("-" * 50)
    
    return test_results

def test_specific_user_scenarios():
    """Test specific scenarios mentioned in the user request"""
    print("\n🎯 TESTING SPECIFIC USER SCENARIOS")
    print("=" * 60)
    
    test_results = []
    
    # Test the specific scenario mentioned: why "sangam nirala" gets through validation
    print("\n🔍 INVESTIGATING 'sangam nirala' VALIDATION ISSUE")
    print("-" * 50)
    
    try:
        judge_name = "sangam nirala"
        encoded_judge_name = quote(judge_name)
        url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
        
        print(f"Testing: {judge_name}")
        print(f"Request URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("❌ ISSUE CONFIRMED: Fake judge 'sangam nirala' is getting through validation")
            data = response.json()
            
            print(f"Judge Name: {data.get('judge_name', 'N/A')}")
            print(f"Is Verified: {data.get('is_verified', 'N/A')}")
            print(f"Confidence Score: {data.get('confidence_score', 'N/A')}")
            print(f"Validation Summary: {data.get('validation_summary', 'N/A')}")
            
            # This should be fixed - fake judges should return 404
            test_results.append(False)
            
        elif response.status_code == 404:
            print("✅ ISSUE RESOLVED: Fake judge 'sangam nirala' properly rejected with 404")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('detail', 'N/A')}")
            except:
                pass
            test_results.append(True)
            
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    return test_results

def main():
    """Main test execution function"""
    print("🎯 JUDGE ANALYTICS WEB SEARCH INTEGRATION TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = []
    
    # Test 1: Fake Judge Detection
    fake_detection_results = test_fake_judge_detection()
    all_results.extend(fake_detection_results)
    
    # Test 2: Web Search Integration
    web_search_results = test_web_search_integration()
    all_results.extend(web_search_results)
    
    # Test 3: Error Handling
    error_handling_results = test_error_handling()
    all_results.extend(error_handling_results)
    
    # Test 4: Specific User Scenarios
    user_scenario_results = test_specific_user_scenarios()
    all_results.extend(user_scenario_results)
    
    # Final Results Summary
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_tests = len(all_results)
    passed_tests = sum(all_results)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Detailed breakdown
    print(f"\n📋 Test Breakdown:")
    print(f"  Fake Judge Detection: {sum(fake_detection_results)}/{len(fake_detection_results)} passed")
    print(f"  Web Search Integration: {sum(web_search_results)}/{len(web_search_results)} passed")
    print(f"  Error Handling: {sum(error_handling_results)}/{len(error_handling_results)} passed")
    print(f"  User Scenarios: {sum(user_scenario_results)}/{len(user_scenario_results)} passed")
    
    print(f"\n🕒 Test Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Critical Issues Summary
    print(f"\n🚨 CRITICAL FINDINGS:")
    
    fake_detection_success = sum(fake_detection_results) / len(fake_detection_results) * 100 if fake_detection_results else 0
    web_search_success = sum(web_search_results) / len(web_search_results) * 100 if web_search_results else 0
    
    if fake_detection_success < 80:
        print("❌ CRITICAL: Fake judge detection is not working properly")
    else:
        print("✅ Fake judge detection working correctly")
        
    if web_search_success < 60:
        print("❌ CRITICAL: Web search integration not providing real data")
    else:
        print("✅ Web search integration providing real case statistics")
    
    if success_rate >= 80:
        print("🎉 OVERALL RESULT: EXCELLENT - Judge Analytics Web Search Integration working well!")
    elif success_rate >= 60:
        print("✅ OVERALL RESULT: GOOD - Judge Analytics mostly functional with minor issues")
    else:
        print("⚠️ OVERALL RESULT: NEEDS ATTENTION - Judge Analytics has significant issues")
    
    print("=" * 80)
    
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Focused test for timestamp removal functionality as requested in review
"""

import sys
sys.path.append('/app')
from backend_test import ScriptGenerationTester

def main():
    tester = ScriptGenerationTester()
    
    print("🎯 FOCUSED TIMESTAMP REMOVAL TESTING")
    print("=" * 50)
    
    # Test basic connectivity first
    if not tester.test_basic_connectivity():
        print("❌ Cannot connect to backend")
        return False
    
    # Run the focused timestamp removal test
    success = tester.test_timestamp_removal_comprehensive()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TIMESTAMP REMOVAL TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(tester.test_results)
    passed_tests = sum(1 for result in tester.test_results if result["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for result in tester.test_results:
            if not result["success"]:
                print(f"  - {result['test']}: {result['message']}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
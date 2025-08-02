#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import LegalMateAPITester

def main():
    print("🏭 Testing Production Optimization & Performance Analytics System")
    print("=" * 80)
    
    tester = LegalMateAPITester()
    
    # Test production optimization endpoints
    tester.run_production_optimization_tests()
    
    # Print results
    print("\n" + "="*60)
    print("📊 PRODUCTION TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All production tests passed!")
        return 0
    else:
        print("❌ Some production tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
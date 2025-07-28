#!/usr/bin/env python3
"""
Comprehensive test for audio content filtering and TTS functionality as requested in review
"""

import sys
sys.path.append('/app')
from backend_test import ScriptGenerationTester

def main():
    tester = ScriptGenerationTester()
    
    print("🎯 COMPREHENSIVE AUDIO CONTENT FILTERING & TTS TESTING")
    print("=" * 60)
    
    # Test basic connectivity first
    if not tester.test_basic_connectivity():
        print("❌ Cannot connect to backend")
        return False
    
    # Run focused tests as requested in review
    test_methods = [
        ("Timestamp Removal Testing", tester.test_timestamp_removal_comprehensive),
        ("TTS Audio Generation", tester.test_generate_audio_endpoint),
        ("Voice Selection", tester.test_voices_endpoint),
        ("Audio Error Handling", tester.test_audio_error_handling),
        ("Voice-Audio Integration", tester.test_voice_audio_integration)
    ]
    
    for test_name, test_method in test_methods:
        print(f"\n🔍 Running {test_name}...")
        try:
            success = test_method()
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            print(f"❌ FAILED: {test_name} - Exception: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE AUDIO & TTS TEST SUMMARY")
    print("=" * 60)
    
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
    
    # Specific findings for review request
    print("\n" + "=" * 60)
    print("🎯 REVIEW REQUEST FINDINGS")
    print("=" * 60)
    
    timestamp_tests = [r for r in tester.test_results if "Timestamp Removal" in r["test"]]
    audio_tests = [r for r in tester.test_results if "Generate Audio" in r["test"]]
    voice_tests = [r for r in tester.test_results if "Voices" in r["test"]]
    
    print(f"✅ Timestamp Removal: {len([t for t in timestamp_tests if t['success']])}/{len(timestamp_tests)} tests passed")
    print(f"✅ TTS Audio Generation: {len([t for t in audio_tests if t['success']])}/{len(audio_tests)} tests passed")
    print(f"✅ Voice Selection: {len([t for t in voice_tests if t['success']])}/{len(voice_tests)} tests passed")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
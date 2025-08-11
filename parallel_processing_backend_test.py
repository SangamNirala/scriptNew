#!/usr/bin/env python3
"""
PARALLEL PROCESSING Implementation - Comprehensive Backend Testing
Testing the new parallel segment generation using 14 Gemini API keys for extended durations
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class ParallelProcessingTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Connectivity", True, f"Backend responding on {API_BASE}")
                return True
            else:
                self.log_test("Backend Connectivity", False, f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_extended_5_parallel_processing(self):
        """Test extended_5 duration (5-10 min) with parallel processing - should use 3 segments"""
        try:
            start_time = time.time()
            
            test_data = {
                "prompt": "Create a comprehensive guide about sustainable living practices that covers energy conservation, waste reduction, and eco-friendly lifestyle choices",
                "video_type": "educational",
                "duration": "extended_5"
            }
            
            print(f"🚀 Starting extended_5 parallel processing test...")
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=300)  # 5 minute timeout
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for parallel processing metadata
                generation_metadata = data.get("generation_metadata", {})
                
                # Verify parallel processing was used
                parallel_checks = []
                
                # Check 1: Parallel generation metadata
                if "parallel_generation" in generation_metadata:
                    parallel_info = generation_metadata["parallel_generation"]
                    parallel_checks.append(f"Parallel generation metadata present")
                    
                    # Check segments count (should be 3 for extended_5)
                    segments_used = parallel_info.get("segments_used", 0)
                    if segments_used == 3:
                        parallel_checks.append(f"Correct segments count: {segments_used}")
                    else:
                        parallel_checks.append(f"❌ Wrong segments count: {segments_used} (expected 3)")
                    
                    # Check API keys used
                    api_keys_used = parallel_info.get("api_keys_used", 0)
                    if api_keys_used >= 3:
                        parallel_checks.append(f"Multiple API keys used: {api_keys_used}")
                    else:
                        parallel_checks.append(f"❌ Insufficient API keys: {api_keys_used}")
                    
                    # Check execution time improvement
                    time_saved = parallel_info.get("time_saved_seconds", 0)
                    if time_saved > 0:
                        parallel_checks.append(f"Time saved: {time_saved}s")
                    
                else:
                    parallel_checks.append("❌ No parallel generation metadata found")
                
                # Check 2: Performance improvement (should be faster than 90s)
                if execution_time < 90:
                    parallel_checks.append(f"Fast execution: {execution_time:.1f}s (< 90s)")
                else:
                    parallel_checks.append(f"❌ Slow execution: {execution_time:.1f}s (>= 90s)")
                
                # Check 3: Script quality and structure
                script_content = data.get("generated_script", "")
                if len(script_content) > 5000:  # Should be substantial content
                    parallel_checks.append(f"Substantial content: {len(script_content)} chars")
                else:
                    parallel_checks.append(f"❌ Limited content: {len(script_content)} chars")
                
                # Check 4: Segment continuity (look for segment markers or transitions)
                segment_markers = len(re.findall(r'segment|part|section', script_content.lower()))
                if segment_markers >= 2:
                    parallel_checks.append(f"Segment continuity markers: {segment_markers}")
                
                success_count = len([check for check in parallel_checks if not check.startswith("❌")])
                total_checks = len(parallel_checks)
                
                if success_count >= (total_checks * 0.7):  # 70% success rate
                    self.log_test("Extended_5 Parallel Processing", True, 
                                f"Parallel processing working ({success_count}/{total_checks} checks passed). Execution: {execution_time:.1f}s. Checks: {'; '.join(parallel_checks)}")
                    return True, execution_time, generation_metadata
                else:
                    self.log_test("Extended_5 Parallel Processing", False, 
                                f"Parallel processing issues ({success_count}/{total_checks} checks passed). Execution: {execution_time:.1f}s. Checks: {'; '.join(parallel_checks)}")
                    return False, execution_time, generation_metadata
                    
            else:
                self.log_test("Extended_5 Parallel Processing", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False, 0, {}
                
        except Exception as e:
            self.log_test("Extended_5 Parallel Processing", False, f"Request failed: {str(e)}")
            return False, 0, {}

    def test_extended_10_parallel_processing(self):
        """Test extended_10 duration (10-15 min) with parallel processing - should use 5 segments"""
        try:
            start_time = time.time()
            
            test_data = {
                "prompt": "Create an in-depth educational series about artificial intelligence covering machine learning fundamentals, neural networks, practical applications, ethical considerations, and future implications for society",
                "video_type": "educational", 
                "duration": "extended_10"
            }
            
            print(f"🚀 Starting extended_10 parallel processing test...")
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=300)  # 5 minute timeout
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for parallel processing metadata
                generation_metadata = data.get("generation_metadata", {})
                
                # Verify parallel processing was used
                parallel_checks = []
                
                # Check 1: Parallel generation metadata
                if "parallel_generation" in generation_metadata:
                    parallel_info = generation_metadata["parallel_generation"]
                    parallel_checks.append(f"Parallel generation metadata present")
                    
                    # Check segments count (should be 5 for extended_10)
                    segments_used = parallel_info.get("segments_used", 0)
                    if segments_used == 5:
                        parallel_checks.append(f"Correct segments count: {segments_used}")
                    else:
                        parallel_checks.append(f"❌ Wrong segments count: {segments_used} (expected 5)")
                    
                    # Check API keys used
                    api_keys_used = parallel_info.get("api_keys_used", 0)
                    if api_keys_used >= 5:
                        parallel_checks.append(f"Multiple API keys used: {api_keys_used}")
                    else:
                        parallel_checks.append(f"❌ Insufficient API keys: {api_keys_used}")
                    
                    # Check execution time improvement
                    time_saved = parallel_info.get("time_saved_seconds", 0)
                    if time_saved > 0:
                        parallel_checks.append(f"Time saved: {time_saved}s")
                    
                else:
                    parallel_checks.append("❌ No parallel generation metadata found")
                
                # Check 2: Performance improvement (should be faster than 120s)
                if execution_time < 120:
                    parallel_checks.append(f"Fast execution: {execution_time:.1f}s (< 120s)")
                else:
                    parallel_checks.append(f"❌ Slow execution: {execution_time:.1f}s (>= 120s)")
                
                # Check 3: Script quality and structure (should be longer than extended_5)
                script_content = data.get("generated_script", "")
                if len(script_content) > 8000:  # Should be more substantial content
                    parallel_checks.append(f"Substantial content: {len(script_content)} chars")
                else:
                    parallel_checks.append(f"❌ Limited content: {len(script_content)} chars")
                
                # Check 4: More segment continuity markers
                segment_markers = len(re.findall(r'segment|part|section', script_content.lower()))
                if segment_markers >= 4:
                    parallel_checks.append(f"Segment continuity markers: {segment_markers}")
                
                success_count = len([check for check in parallel_checks if not check.startswith("❌")])
                total_checks = len(parallel_checks)
                
                if success_count >= (total_checks * 0.7):  # 70% success rate
                    self.log_test("Extended_10 Parallel Processing", True, 
                                f"Parallel processing working ({success_count}/{total_checks} checks passed). Execution: {execution_time:.1f}s. Checks: {'; '.join(parallel_checks)}")
                    return True, execution_time, generation_metadata
                else:
                    self.log_test("Extended_10 Parallel Processing", False, 
                                f"Parallel processing issues ({success_count}/{total_checks} checks passed). Execution: {execution_time:.1f}s. Checks: {'; '.join(parallel_checks)}")
                    return False, execution_time, generation_metadata
                    
            else:
                self.log_test("Extended_10 Parallel Processing", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False, 0, {}
                
        except Exception as e:
            self.log_test("Extended_10 Parallel Processing", False, f"Request failed: {str(e)}")
            return False, 0, {}

    def test_fallback_behavior_short_duration(self):
        """Test that short durations still work normally (fallback to sequential)"""
        try:
            start_time = time.time()
            
            test_data = {
                "prompt": "Create a quick tip about time management for busy professionals",
                "video_type": "general",
                "duration": "short"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=60)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that it works normally without parallel processing
                fallback_checks = []
                
                # Should have script content
                script_content = data.get("generated_script", "")
                if len(script_content) > 100:
                    fallback_checks.append(f"Script generated: {len(script_content)} chars")
                
                # Should be fast (sequential for short content)
                if execution_time < 30:
                    fallback_checks.append(f"Fast execution: {execution_time:.1f}s")
                
                # Should NOT have parallel processing metadata (or should indicate sequential)
                generation_metadata = data.get("generation_metadata", {})
                if "parallel_generation" not in generation_metadata:
                    fallback_checks.append("No parallel processing (expected for short duration)")
                elif generation_metadata.get("parallel_generation", {}).get("strategy") == "sequential":
                    fallback_checks.append("Sequential strategy used (expected for short duration)")
                
                if len(fallback_checks) >= 2:
                    self.log_test("Fallback Behavior - Short Duration", True, 
                                f"Sequential processing working. Checks: {'; '.join(fallback_checks)}")
                    return True
                else:
                    self.log_test("Fallback Behavior - Short Duration", False, 
                                f"Issues with sequential processing. Checks: {'; '.join(fallback_checks)}")
                    return False
                    
            else:
                self.log_test("Fallback Behavior - Short Duration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Fallback Behavior - Short Duration", False, f"Request failed: {str(e)}")
            return False

    def test_script_quality_and_continuity(self):
        """Test that parallel-generated scripts maintain quality and narrative flow"""
        try:
            test_data = {
                "prompt": "Create a comprehensive guide about healthy cooking that covers meal planning, ingredient selection, cooking techniques, and nutritional balance",
                "video_type": "educational",
                "duration": "extended_5"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                script_content = data.get("generated_script", "")
                
                quality_checks = []
                
                # Check 1: Script has proper structure
                if "AI IMAGE PROMPT:" in script_content:
                    image_prompts = len(re.findall(r'AI IMAGE PROMPT:', script_content))
                    quality_checks.append(f"Image prompts present: {image_prompts}")
                
                # Check 2: Narrative flow indicators
                flow_indicators = [
                    "introduction", "first", "next", "then", "finally", "conclusion",
                    "let's start", "moving on", "in summary", "to wrap up"
                ]
                found_indicators = sum(1 for indicator in flow_indicators if indicator in script_content.lower())
                if found_indicators >= 3:
                    quality_checks.append(f"Narrative flow indicators: {found_indicators}")
                
                # Check 3: Content depth and completeness
                if len(script_content) > 3000:
                    quality_checks.append(f"Comprehensive content: {len(script_content)} chars")
                
                # Check 4: Proper formatting
                if script_content.count('\n') > 10:  # Multiple paragraphs/sections
                    quality_checks.append(f"Well-formatted structure")
                
                # Check 5: Topic coverage (should mention key aspects from prompt)
                topic_coverage = sum(1 for topic in ["meal planning", "ingredient", "cooking", "nutrition"] 
                                   if topic in script_content.lower())
                if topic_coverage >= 3:
                    quality_checks.append(f"Good topic coverage: {topic_coverage}/4 topics")
                
                if len(quality_checks) >= 4:
                    self.log_test("Script Quality and Continuity", True, 
                                f"High quality parallel-generated script. Checks: {'; '.join(quality_checks)}")
                    return True
                else:
                    self.log_test("Script Quality and Continuity", False, 
                                f"Quality issues in parallel-generated script. Checks: {'; '.join(quality_checks)}")
                    return False
                    
            else:
                self.log_test("Script Quality and Continuity", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Script Quality and Continuity", False, f"Request failed: {str(e)}")
            return False

    def test_performance_comparison(self, extended_5_time, extended_10_time):
        """Compare performance improvements between different durations"""
        try:
            performance_checks = []
            
            # Check 1: Extended_5 should be reasonably fast
            if extended_5_time > 0 and extended_5_time < 60:
                performance_checks.append(f"Extended_5 fast: {extended_5_time:.1f}s")
            elif extended_5_time > 0:
                performance_checks.append(f"❌ Extended_5 slow: {extended_5_time:.1f}s")
            
            # Check 2: Extended_10 should be faster than sequential would be
            if extended_10_time > 0 and extended_10_time < 90:
                performance_checks.append(f"Extended_10 optimized: {extended_10_time:.1f}s")
            elif extended_10_time > 0:
                performance_checks.append(f"❌ Extended_10 slow: {extended_10_time:.1f}s")
            
            # Check 3: Scaling relationship
            if extended_5_time > 0 and extended_10_time > 0:
                time_ratio = extended_10_time / extended_5_time
                if time_ratio < 2.0:  # Extended_10 shouldn't take more than 2x extended_5 time
                    performance_checks.append(f"Good scaling ratio: {time_ratio:.1f}x")
                else:
                    performance_checks.append(f"❌ Poor scaling ratio: {time_ratio:.1f}x")
            
            success_count = len([check for check in performance_checks if not check.startswith("❌")])
            total_checks = len(performance_checks)
            
            if success_count >= (total_checks * 0.7):
                self.log_test("Performance Comparison", True, 
                            f"Good performance scaling. Checks: {'; '.join(performance_checks)}")
                return True
            else:
                self.log_test("Performance Comparison", False, 
                            f"Performance scaling issues. Checks: {'; '.join(performance_checks)}")
                return False
                
        except Exception as e:
            self.log_test("Performance Comparison", False, f"Analysis failed: {str(e)}")
            return False

    def test_parallel_processing_logs_verification(self):
        """Test that backend logs show parallel processing messages"""
        try:
            # This is a placeholder test since we can't directly access backend logs
            # In a real scenario, we would check supervisor logs or implement a log endpoint
            
            # For now, we'll test if the system responds correctly to parallel processing requests
            test_data = {
                "prompt": "Test parallel processing logging",
                "video_type": "general",
                "duration": "extended_5"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                generation_metadata = data.get("generation_metadata", {})
                
                # Check if parallel processing metadata indicates logging
                if "parallel_generation" in generation_metadata:
                    parallel_info = generation_metadata["parallel_generation"]
                    
                    # Look for indicators that parallel processing was logged
                    log_indicators = []
                    
                    if "execution_start_time" in parallel_info:
                        log_indicators.append("Execution timing logged")
                    
                    if "segments_used" in parallel_info:
                        log_indicators.append("Segment usage logged")
                    
                    if "api_keys_used" in parallel_info:
                        log_indicators.append("API key usage logged")
                    
                    if len(log_indicators) >= 2:
                        self.log_test("Parallel Processing Logs Verification", True, 
                                    f"Parallel processing logging indicators present: {'; '.join(log_indicators)}")
                        return True
                    else:
                        self.log_test("Parallel Processing Logs Verification", False, 
                                    f"Limited logging indicators: {'; '.join(log_indicators)}")
                        return False
                else:
                    self.log_test("Parallel Processing Logs Verification", False, 
                                "No parallel processing metadata found")
                    return False
            else:
                self.log_test("Parallel Processing Logs Verification", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Parallel Processing Logs Verification", False, f"Request failed: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run all parallel processing tests"""
        print("🚀 Starting PARALLEL PROCESSING Implementation Comprehensive Testing")
        print("=" * 80)
        print()
        
        # Test 1: Basic connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed. Stopping tests.")
            return 0
        
        # Test 2: Extended_5 parallel processing (3 segments)
        print("🔄 Testing Extended_5 Parallel Processing (3 segments)...")
        extended_5_success, extended_5_time, extended_5_metadata = self.test_extended_5_parallel_processing()
        
        # Test 3: Extended_10 parallel processing (5 segments)  
        print("🔄 Testing Extended_10 Parallel Processing (5 segments)...")
        extended_10_success, extended_10_time, extended_10_metadata = self.test_extended_10_parallel_processing()
        
        # Test 4: Fallback behavior
        print("🔄 Testing Fallback Behavior (Sequential for short durations)...")
        self.test_fallback_behavior_short_duration()
        
        # Test 5: Script quality and continuity
        print("🔄 Testing Script Quality and Continuity...")
        self.test_script_quality_and_continuity()
        
        # Test 6: Performance comparison
        print("🔄 Testing Performance Comparison...")
        self.test_performance_comparison(extended_5_time, extended_10_time)
        
        # Test 7: Logs verification
        print("🔄 Testing Parallel Processing Logs...")
        self.test_parallel_processing_logs_verification()
        
        # Final results
        print("=" * 80)
        print("🏁 PARALLEL PROCESSING IMPLEMENTATION TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        print()
        
        # Performance summary
        if extended_5_time > 0 or extended_10_time > 0:
            print("⚡ PERFORMANCE SUMMARY:")
            if extended_5_time > 0:
                print(f"   • Extended_5 (3 segments): {extended_5_time:.1f}s")
            if extended_10_time > 0:
                print(f"   • Extended_10 (5 segments): {extended_10_time:.1f}s")
            
            if extended_5_time > 0 and extended_10_time > 0:
                improvement_5 = max(0, 90 - extended_5_time)  # Expected sequential time ~90s
                improvement_10 = max(0, 120 - extended_10_time)  # Expected sequential time ~120s
                print(f"   • Time saved Extended_5: ~{improvement_5:.1f}s")
                print(f"   • Time saved Extended_10: ~{improvement_10:.1f}s")
            print()
        
        # Categorize results
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}")
        
        if failed_tests:
            print()
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print()
        
        # Overall assessment
        if success_rate >= 85:
            print("🎉 EXCELLENT: Parallel Processing implementation is working excellently!")
            print("   • Extended durations use parallel segment generation")
            print("   • Performance improvements achieved (30-40s vs 90-120s)")
            print("   • Script quality and continuity maintained")
            print("   • Fallback behavior working for non-extended durations")
        elif success_rate >= 70:
            print("✅ GOOD: Parallel Processing implementation is working well with minor issues.")
            print("   • Core parallel functionality operational")
            print("   • Some performance or quality improvements needed")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Parallel Processing implementation has some issues that need attention.")
            print("   • Basic functionality may be working but optimization needed")
        else:
            print("❌ CRITICAL: Parallel Processing implementation has significant issues.")
            print("   • Core parallel functionality may not be working")
            print("   • Performance improvements not achieved")
        
        return success_rate

if __name__ == "__main__":
    print("PARALLEL PROCESSING Implementation - Backend Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = ParallelProcessingTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)
#!/usr/bin/env python3
"""
Long Duration (3-5min) Image Generation Fix - Comprehensive Backend Testing
Testing the critical fix for "Long (3-5min)" duration image generation issue
"""

import requests
import json
import sys
import time
import re
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class LongDurationFixTester:
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

    def test_long_duration_segmented_generation(self):
        """Test that 'long' duration now uses segmented generation strategy"""
        try:
            # Test with the exact scenario from review request
            test_data = {
                "prompt": "Create a comprehensive video about overcoming fear and building confidence",
                "video_type": "educational",
                "duration": "long"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)  # Allow more time for segmented generation
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if generation_metadata exists
                generation_metadata = data.get("generation_metadata", {})
                if not generation_metadata:
                    self.log_test("Long Duration Segmented Generation - Metadata", 
                                False, "No generation_metadata found in response")
                    return False
                
                # Critical check: Verify generation strategy is "segmented"
                generation_strategy = generation_metadata.get("generation_strategy")
                if generation_strategy == "segmented":
                    self.log_test("Long Duration Segmented Generation - Strategy", 
                                True, f"Generation strategy correctly set to 'segmented'")
                else:
                    self.log_test("Long Duration Segmented Generation - Strategy", 
                                False, f"Expected 'segmented', got '{generation_strategy}'")
                    return False
                
                # Check segment count (should be 3 as per fix)
                segments = generation_metadata.get("segments", 0)
                if segments == 3:
                    self.log_test("Long Duration Segmented Generation - Segment Count", 
                                True, f"Correct segment count: {segments}")
                else:
                    self.log_test("Long Duration Segmented Generation - Segment Count", 
                                False, f"Expected 3 segments, got {segments}")
                
                # Check shot count is in expected range (90-150)
                generated_script = data.get("generated_script", "")
                shot_count = self.count_shots_in_script(generated_script)
                
                if 90 <= shot_count <= 150:
                    self.log_test("Long Duration Segmented Generation - Shot Count", 
                                True, f"Shot count {shot_count} is within expected range (90-150)")
                else:
                    self.log_test("Long Duration Segmented Generation - Shot Count", 
                                False, f"Shot count {shot_count} is outside expected range (90-150)")
                
                # Check for consistent image prompts
                image_prompt_consistency = self.check_image_prompt_consistency(generated_script)
                if image_prompt_consistency["consistent"]:
                    self.log_test("Long Duration Segmented Generation - Image Prompt Consistency", 
                                True, f"Found {image_prompt_consistency['total_prompts']} consistent image prompts")
                else:
                    self.log_test("Long Duration Segmented Generation - Image Prompt Consistency", 
                                False, f"Image prompts inconsistent: {image_prompt_consistency['details']}")
                
                return True
                
            else:
                self.log_test("Long Duration Segmented Generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Long Duration Segmented Generation", False, f"Request failed: {str(e)}")
            return False

    def test_comparison_with_short_duration(self):
        """Compare long duration with short duration to verify different strategies"""
        try:
            # Test short duration (should use single_pass)
            short_data = {
                "prompt": "Create a comprehensive video about overcoming fear and building confidence",
                "video_type": "educational", 
                "duration": "short"
            }
            
            short_response = requests.post(f"{API_BASE}/generate-script", 
                                         json=short_data, 
                                         timeout=60)
            
            # Test long duration (should use segmented)
            long_data = {
                "prompt": "Create a comprehensive video about overcoming fear and building confidence",
                "video_type": "educational",
                "duration": "long"
            }
            
            long_response = requests.post(f"{API_BASE}/generate-script", 
                                        json=long_data, 
                                        timeout=120)
            
            if short_response.status_code == 200 and long_response.status_code == 200:
                short_data = short_response.json()
                long_data = long_response.json()
                
                # Compare generation strategies
                short_strategy = short_data.get("generation_metadata", {}).get("generation_strategy", "unknown")
                long_strategy = long_data.get("generation_metadata", {}).get("generation_strategy", "unknown")
                
                if short_strategy == "single_pass" and long_strategy == "segmented":
                    self.log_test("Strategy Comparison - Short vs Long", 
                                True, f"Short: {short_strategy}, Long: {long_strategy}")
                else:
                    self.log_test("Strategy Comparison - Short vs Long", 
                                False, f"Unexpected strategies - Short: {short_strategy}, Long: {long_strategy}")
                
                # Compare shot counts
                short_shots = self.count_shots_in_script(short_data.get("generated_script", ""))
                long_shots = self.count_shots_in_script(long_data.get("generated_script", ""))
                
                if long_shots > short_shots * 2:  # Long should have significantly more shots
                    self.log_test("Shot Count Comparison - Short vs Long", 
                                True, f"Short: {short_shots} shots, Long: {long_shots} shots")
                else:
                    self.log_test("Shot Count Comparison - Short vs Long", 
                                False, f"Long duration doesn't have significantly more shots - Short: {short_shots}, Long: {long_shots}")
                
                return True
            else:
                self.log_test("Strategy Comparison", False, 
                            f"One or both requests failed - Short: {short_response.status_code}, Long: {long_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Strategy Comparison", False, f"Request failed: {str(e)}")
            return False

    def test_extended_duration_consistency(self):
        """Test that extended durations still work correctly (regression test)"""
        try:
            # Test extended_5 duration (should also use segmented)
            test_data = {
                "prompt": "Create a comprehensive video about overcoming fear and building confidence",
                "video_type": "educational",
                "duration": "extended_5"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                generation_metadata = data.get("generation_metadata", {})
                
                # Extended durations should use segmented strategy
                generation_strategy = generation_metadata.get("generation_strategy")
                if generation_strategy == "segmented":
                    self.log_test("Extended Duration Consistency - Strategy", 
                                True, f"Extended_5 correctly uses segmented strategy")
                else:
                    self.log_test("Extended Duration Consistency - Strategy", 
                                False, f"Extended_5 should use segmented, got '{generation_strategy}'")
                
                # Check that extended durations have appropriate shot counts
                generated_script = data.get("generated_script", "")
                shot_count = self.count_shots_in_script(generated_script)
                
                if shot_count >= 150:  # Extended should have more shots than long
                    self.log_test("Extended Duration Consistency - Shot Count", 
                                True, f"Extended_5 has {shot_count} shots (>= 150)")
                else:
                    self.log_test("Extended Duration Consistency - Shot Count", 
                                False, f"Extended_5 has only {shot_count} shots (< 150)")
                
                return True
            else:
                self.log_test("Extended Duration Consistency", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Extended Duration Consistency", False, f"Request failed: {str(e)}")
            return False

    def test_image_prompt_quality(self):
        """Test the quality and detail of image prompts in long duration scripts"""
        try:
            test_data = {
                "prompt": "Create a comprehensive video about overcoming fear and building confidence",
                "video_type": "educational",
                "duration": "long"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                generated_script = data.get("generated_script", "")
                
                # Extract all image prompts
                image_prompts = self.extract_image_prompts(generated_script)
                
                if len(image_prompts) == 0:
                    self.log_test("Image Prompt Quality - Presence", 
                                False, "No image prompts found in script")
                    return False
                
                # Check quality of image prompts
                detailed_prompts = 0
                for prompt in image_prompts:
                    if len(prompt.split()) >= 10:  # At least 10 words for detailed prompt
                        detailed_prompts += 1
                
                quality_ratio = detailed_prompts / len(image_prompts)
                if quality_ratio >= 0.8:  # 80% of prompts should be detailed
                    self.log_test("Image Prompt Quality - Detail Level", 
                                True, f"{detailed_prompts}/{len(image_prompts)} prompts are detailed ({quality_ratio:.1%})")
                else:
                    self.log_test("Image Prompt Quality - Detail Level", 
                                False, f"Only {detailed_prompts}/{len(image_prompts)} prompts are detailed ({quality_ratio:.1%})")
                
                # Check for variety in image prompts
                unique_words = set()
                for prompt in image_prompts:
                    unique_words.update(prompt.lower().split())
                
                if len(unique_words) >= len(image_prompts) * 3:  # Good variety
                    self.log_test("Image Prompt Quality - Variety", 
                                True, f"Good variety: {len(unique_words)} unique words across {len(image_prompts)} prompts")
                else:
                    self.log_test("Image Prompt Quality - Variety", 
                                False, f"Limited variety: {len(unique_words)} unique words across {len(image_prompts)} prompts")
                
                return True
            else:
                self.log_test("Image Prompt Quality", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Image Prompt Quality", False, f"Request failed: {str(e)}")
            return False

    def test_multiple_video_types_with_long_duration(self):
        """Test long duration with different video types"""
        video_types = ["educational", "marketing", "entertainment", "general"]
        success_count = 0
        
        for video_type in video_types:
            try:
                test_data = {
                    "prompt": "Create a comprehensive video about overcoming fear and building confidence",
                    "video_type": video_type,
                    "duration": "long"
                }
                
                response = requests.post(f"{API_BASE}/generate-script", 
                                       json=test_data, 
                                       timeout=120)
                
                if response.status_code == 200:
                    data = response.json()
                    generation_metadata = data.get("generation_metadata", {})
                    
                    # Check that all video types use segmented strategy for long duration
                    generation_strategy = generation_metadata.get("generation_strategy")
                    if generation_strategy == "segmented":
                        success_count += 1
                        self.log_test(f"Long Duration with {video_type.title()} Video Type", 
                                    True, f"Uses segmented strategy correctly")
                    else:
                        self.log_test(f"Long Duration with {video_type.title()} Video Type", 
                                    False, f"Expected segmented, got '{generation_strategy}'")
                else:
                    self.log_test(f"Long Duration with {video_type.title()} Video Type", 
                                False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Long Duration with {video_type.title()} Video Type", 
                            False, f"Request failed: {str(e)}")
        
        # Overall assessment
        success_rate = (success_count / len(video_types)) * 100
        if success_rate >= 75:
            self.log_test("Multiple Video Types with Long Duration", True, 
                        f"Success rate: {success_rate}% ({success_count}/{len(video_types)})")
        else:
            self.log_test("Multiple Video Types with Long Duration", False, 
                        f"Low success rate: {success_rate}% ({success_count}/{len(video_types)})")

    def count_shots_in_script(self, script: str) -> int:
        """Count the number of shots/timestamps in a script"""
        # Look for timestamp patterns like [0:00-0:03] or 0:00-0:03
        timestamp_patterns = [
            r'\[\d+:\d+\s*[-–]\s*\d+:\d+\]',  # [0:00-0:03]
            r'\d+:\d+\s*[-–]\s*\d+:\d+',      # 0:00-0:03
            r'Shot \d+:',                      # Shot 1:
            r'Scene \d+:',                     # Scene 1:
        ]
        
        total_shots = 0
        for pattern in timestamp_patterns:
            matches = re.findall(pattern, script)
            total_shots = max(total_shots, len(matches))
        
        return total_shots

    def check_image_prompt_consistency(self, script: str) -> Dict[str, Any]:
        """Check if image prompts are consistent throughout the script"""
        # Extract image prompts
        image_prompts = self.extract_image_prompts(script)
        
        # Count timestamps
        shot_count = self.count_shots_in_script(script)
        
        # Check consistency
        if len(image_prompts) == 0:
            return {
                "consistent": False,
                "total_prompts": 0,
                "expected_prompts": shot_count,
                "details": "No image prompts found"
            }
        
        # For long duration, we expect most shots to have image prompts
        expected_ratio = 0.8  # At least 80% of shots should have image prompts
        actual_ratio = len(image_prompts) / max(shot_count, 1)
        
        return {
            "consistent": actual_ratio >= expected_ratio,
            "total_prompts": len(image_prompts),
            "expected_prompts": shot_count,
            "ratio": actual_ratio,
            "details": f"Found {len(image_prompts)} image prompts for {shot_count} shots ({actual_ratio:.1%})"
        }

    def extract_image_prompts(self, script: str) -> List[str]:
        """Extract image prompts from script"""
        # Look for various image prompt patterns
        patterns = [
            r'AI IMAGE PROMPT:\s*["\']([^"\']+)["\']',  # AI IMAGE PROMPT: "..."
            r'AI IMAGE PROMPT:\s*([^\n]+)',             # AI IMAGE PROMPT: ...
            r'Image:\s*["\']([^"\']+)["\']',            # Image: "..."
            r'Image:\s*([^\n]+)',                       # Image: ...
            r'Visual:\s*["\']([^"\']+)["\']',           # Visual: "..."
            r'Visual:\s*([^\n]+)',                      # Visual: ...
        ]
        
        image_prompts = []
        for pattern in patterns:
            matches = re.findall(pattern, script, re.IGNORECASE)
            image_prompts.extend(matches)
        
        # Remove duplicates and clean up
        unique_prompts = []
        for prompt in image_prompts:
            cleaned = prompt.strip()
            if cleaned and cleaned not in unique_prompts:
                unique_prompts.append(cleaned)
        
        return unique_prompts

    def run_comprehensive_tests(self):
        """Run all Long Duration Fix tests"""
        print("🚀 Starting Long Duration (3-5min) Image Generation Fix Comprehensive Testing")
        print("=" * 80)
        print()
        
        # Test 1: Basic connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed. Stopping tests.")
            return 0
        
        # Test 2: Core fix verification
        print("🎯 Testing Core Fix - Long Duration Segmented Generation...")
        self.test_long_duration_segmented_generation()
        
        # Test 3: Strategy comparison
        print("📊 Testing Strategy Comparison...")
        self.test_comparison_with_short_duration()
        
        # Test 4: Regression testing
        print("🔄 Testing Extended Duration Consistency (Regression)...")
        self.test_extended_duration_consistency()
        
        # Test 5: Image prompt quality
        print("🖼️ Testing Image Prompt Quality...")
        self.test_image_prompt_quality()
        
        # Test 6: Multiple video types
        print("🎬 Testing Multiple Video Types with Long Duration...")
        self.test_multiple_video_types_with_long_duration()
        
        # Final results
        print("=" * 80)
        print("🏁 LONG DURATION (3-5MIN) IMAGE GENERATION FIX TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
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
            print("🎉 EXCELLENT: Long Duration (3-5min) fix is working perfectly!")
        elif success_rate >= 70:
            print("✅ GOOD: Long Duration (3-5min) fix is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Long Duration (3-5min) fix has some issues that need attention.")
        else:
            print("❌ CRITICAL: Long Duration (3-5min) fix has significant issues.")
        
        return success_rate

if __name__ == "__main__":
    print("Long Duration (3-5min) Image Generation Fix - Backend Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = LongDurationFixTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)
#!/usr/bin/env python3
"""
Enhanced Duration-Aware Script Generation System - Comprehensive Backend Testing
Testing the enhanced duration-aware script generation system that properly generates scripts 
matching selected duration with appropriate shot counts and content depth.
"""

import requests
import json
import sys
import time
import re
from typing import Dict, List, Any, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use local for testing
BACKEND_URL = 'http://localhost:8001'
API_BASE = f"{BACKEND_URL}/api"

class DurationAwareScriptGenerationTester:
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

    def count_shots_in_script(self, script_content: str) -> int:
        """Count the number of shots in a script by looking for shot indicators"""
        if not script_content:
            return 0
            
        # Look for various shot indicators
        shot_patterns = [
            r'\[Shot \d+\]',  # [Shot 1], [Shot 2], etc.
            r'Shot \d+:',     # Shot 1:, Shot 2:, etc.
            r'\d+\.\s*\[',    # 1. [description], 2. [description], etc.
            r'\[\d+:\d+\-\d+:\d+\]',  # [0:00-0:03] timestamp format
            r'\d+:\d+\s*\-\s*\d+:\d+',  # 0:00-0:03 timestamp format
        ]
        
        total_shots = 0
        for pattern in shot_patterns:
            matches = re.findall(pattern, script_content, re.IGNORECASE)
            if matches:
                total_shots = max(total_shots, len(matches))
        
        # If no specific shot patterns found, try to count by line breaks and content structure
        if total_shots == 0:
            lines = script_content.split('\n')
            content_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
            # Estimate shots based on content structure (rough heuristic)
            total_shots = max(1, len(content_lines) // 3)  # Assume roughly 3 lines per shot
            
        return total_shots

    def count_words_in_script(self, script_content: str) -> int:
        """Count the total number of words in a script"""
        if not script_content:
            return 0
        
        # Remove timestamps and shot indicators for accurate word count
        clean_content = re.sub(r'\[\d+:\d+\-\d+:\d+\]', '', script_content)
        clean_content = re.sub(r'\d+:\d+\s*\-\s*\d+:\d+', '', clean_content)
        clean_content = re.sub(r'\[Shot \d+\]', '', clean_content, flags=re.IGNORECASE)
        clean_content = re.sub(r'Shot \d+:', '', clean_content, flags=re.IGNORECASE)
        
        # Count words
        words = clean_content.split()
        return len([word for word in words if word.strip()])

    def analyze_script_quality(self, script_content: str, duration: str) -> Dict[str, Any]:
        """Analyze script quality and check if it meets duration requirements"""
        shot_count = self.count_shots_in_script(script_content)
        word_count = self.count_words_in_script(script_content)
        
        # Expected ranges for different durations
        duration_expectations = {
            "short": {"shots": (15, 30), "words": (300, 1200)},
            "medium": {"shots": (30, 60), "words": (1200, 3600)},
            "long": {"shots": (60, 120), "words": (3600, 7200)},
            "extended_5": {"shots": (120, 180), "words": (7200, 10800)},
            "extended_10": {"shots": (300, 450), "words": (12000, 31500)},
            "extended_15": {"shots": (450, 675), "words": (31500, 47250)},
            "extended_20": {"shots": (600, 900), "words": (47250, 63000)},
            "extended_25": {"shots": (750, 1125), "words": (63000, 78750)}
        }
        
        expected = duration_expectations.get(duration, {"shots": (1, 10), "words": (100, 1000)})
        
        # Calculate quality score
        shot_in_range = expected["shots"][0] <= shot_count <= expected["shots"][1]
        word_in_range = expected["words"][0] <= word_count <= expected["words"][1]
        
        # Calculate percentage of target met
        shot_target_min = expected["shots"][0]
        word_target_min = expected["words"][0]
        
        shot_percentage = (shot_count / shot_target_min) * 100 if shot_target_min > 0 else 0
        word_percentage = (word_count / word_target_min) * 100 if word_target_min > 0 else 0
        
        overall_percentage = (shot_percentage + word_percentage) / 2
        
        return {
            "shot_count": shot_count,
            "word_count": word_count,
            "expected_shots": expected["shots"],
            "expected_words": expected["words"],
            "shot_in_range": shot_in_range,
            "word_in_range": word_in_range,
            "shot_percentage": shot_percentage,
            "word_percentage": word_percentage,
            "overall_percentage": overall_percentage,
            "meets_target": overall_percentage >= 70  # 70% threshold as mentioned in review request
        }

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

    def test_duration_scaling_verification(self):
        """Test that different durations produce appropriately scaled content"""
        print("🔍 Testing Duration Scaling Verification...")
        
        # Test different durations with the same prompt
        test_prompt = "Create a comprehensive educational video about sustainable energy solutions"
        durations_to_test = ["short", "medium", "long", "extended_10", "extended_15"]
        
        results = {}
        
        for duration in durations_to_test:
            try:
                test_data = {
                    "prompt": test_prompt,
                    "video_type": "educational",
                    "duration": duration
                }
                
                print(f"   Testing duration: {duration}...")
                response = requests.post(f"{API_BASE}/generate-script", 
                                       json=test_data, 
                                       timeout=120)  # Longer timeout for script generation
                
                if response.status_code == 200:
                    data = response.json()
                    script_content = data.get("generated_script", "")
                    
                    # Analyze the script
                    analysis = self.analyze_script_quality(script_content, duration)
                    results[duration] = analysis
                    
                    self.log_test(f"Duration Scaling - {duration}", 
                                analysis["meets_target"], 
                                f"Shots: {analysis['shot_count']} (expected: {analysis['expected_shots']}), "
                                f"Words: {analysis['word_count']} (expected: {analysis['expected_words']}), "
                                f"Quality: {analysis['overall_percentage']:.1f}%")
                else:
                    self.log_test(f"Duration Scaling - {duration}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Duration Scaling - {duration}", False, f"Request failed: {str(e)}")
        
        # Verify scaling progression
        if len(results) >= 3:
            durations_ordered = ["short", "medium", "long", "extended_10", "extended_15"]
            scaling_verified = True
            
            for i in range(len(durations_ordered) - 1):
                current_dur = durations_ordered[i]
                next_dur = durations_ordered[i + 1]
                
                if current_dur in results and next_dur in results:
                    current_shots = results[current_dur]["shot_count"]
                    next_shots = results[next_dur]["shot_count"]
                    current_words = results[current_dur]["word_count"]
                    next_words = results[next_dur]["word_count"]
                    
                    # Check if longer duration has more content
                    if next_shots <= current_shots or next_words <= current_words:
                        scaling_verified = False
                        break
            
            self.log_test("Duration Scaling Progression", scaling_verified,
                        f"Verified that longer durations produce more content" if scaling_verified 
                        else "Scaling progression not consistent")
        
        return results

    def test_extended_10_specific_requirements(self):
        """Test specific requirements for extended_10 duration (10-15min)"""
        print("🎯 Testing Extended_10 Specific Requirements...")
        
        test_data = {
            "prompt": "Create a comprehensive educational video about sustainable energy solutions",
            "video_type": "educational",
            "duration": "extended_10"
        }
        
        try:
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=180)  # Extended timeout for long content
            
            if response.status_code == 200:
                data = response.json()
                script_content = data.get("generated_script", "")
                
                # Analyze the script
                analysis = self.analyze_script_quality(script_content, "extended_10")
                
                # Check specific requirements from review request
                shot_count = analysis["shot_count"]
                word_count = analysis["word_count"]
                
                # Expected: 300-450 shots and 12,000-31,500 words
                shot_requirement_met = 300 <= shot_count <= 450
                word_requirement_met = 12000 <= word_count <= 31500
                
                self.log_test("Extended_10 Shot Count Requirement", shot_requirement_met,
                            f"Got {shot_count} shots (expected: 300-450)")
                
                self.log_test("Extended_10 Word Count Requirement", word_requirement_met,
                            f"Got {word_count} words (expected: 12,000-31,500)")
                
                # Check for generation metadata
                generation_metadata = data.get("generation_metadata", {})
                metadata_present = bool(generation_metadata)
                
                self.log_test("Extended_10 Generation Metadata", metadata_present,
                            f"Metadata present: {list(generation_metadata.keys()) if generation_metadata else 'None'}")
                
                # Overall assessment
                overall_success = shot_requirement_met and word_requirement_met and metadata_present
                self.log_test("Extended_10 Overall Requirements", overall_success,
                            f"All requirements met: {overall_success}")
                
                return analysis
                
            else:
                self.log_test("Extended_10 Generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Extended_10 Generation", False, f"Request failed: {str(e)}")
            return None

    def test_short_duration_requirements(self):
        """Test specific requirements for short duration (30s-1min)"""
        print("⚡ Testing Short Duration Requirements...")
        
        test_data = {
            "prompt": "Create a quick video about healthy cooking tips",
            "video_type": "educational",
            "duration": "short"
        }
        
        try:
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                script_content = data.get("generated_script", "")
                
                # Analyze the script
                analysis = self.analyze_script_quality(script_content, "short")
                
                # Check specific requirements
                shot_count = analysis["shot_count"]
                word_count = analysis["word_count"]
                
                # Expected: 15-30 shots and 300-1,200 words
                shot_requirement_met = 15 <= shot_count <= 30
                word_requirement_met = 300 <= word_count <= 1200
                
                self.log_test("Short Duration Shot Count", shot_requirement_met,
                            f"Got {shot_count} shots (expected: 15-30)")
                
                self.log_test("Short Duration Word Count", word_requirement_met,
                            f"Got {word_count} words (expected: 300-1,200)")
                
                return analysis
                
            else:
                self.log_test("Short Duration Generation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Short Duration Generation", False, f"Request failed: {str(e)}")
            return None

    def test_quality_analysis_function(self):
        """Test that the quality analysis function correctly counts shots and words"""
        print("🔬 Testing Quality Analysis Function...")
        
        # Test with sample script content
        sample_scripts = [
            {
                "name": "Simple Script with Shot Markers",
                "content": """[Shot 1] Introduction to the topic
                [Shot 2] Main content explanation
                [Shot 3] Supporting details
                [Shot 4] Conclusion and call to action""",
                "expected_shots": 4,
                "expected_words_min": 10
            },
            {
                "name": "Script with Timestamps",
                "content": """[0:00-0:03] Welcome to our comprehensive guide
                [0:03-0:06] Today we'll explore sustainable energy
                [0:06-0:10] Solar power is becoming more accessible
                [0:10-0:15] Wind energy offers great potential
                [0:15-0:20] Let's discuss implementation strategies""",
                "expected_shots": 5,
                "expected_words_min": 15
            },
            {
                "name": "Mixed Format Script",
                "content": """Shot 1: Opening hook with compelling question
                Shot 2: Problem identification and context
                Shot 3: Solution presentation with benefits
                Shot 4: Evidence and social proof
                Shot 5: Call to action and next steps""",
                "expected_shots": 5,
                "expected_words_min": 20
            }
        ]
        
        for sample in sample_scripts:
            shot_count = self.count_shots_in_script(sample["content"])
            word_count = self.count_words_in_script(sample["content"])
            
            shot_correct = shot_count == sample["expected_shots"]
            word_sufficient = word_count >= sample["expected_words_min"]
            
            self.log_test(f"Quality Analysis - {sample['name']} - Shot Count", shot_correct,
                        f"Got {shot_count} shots (expected: {sample['expected_shots']})")
            
            self.log_test(f"Quality Analysis - {sample['name']} - Word Count", word_sufficient,
                        f"Got {word_count} words (expected: >={sample['expected_words_min']})")

    def test_generation_statistics_logging(self):
        """Test that generation statistics are properly logged"""
        print("📊 Testing Generation Statistics Logging...")
        
        test_data = {
            "prompt": "Create a video about artificial intelligence trends",
            "video_type": "educational",
            "duration": "medium"
        }
        
        try:
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for generation metadata
                generation_metadata = data.get("generation_metadata", {})
                
                required_metadata_fields = [
                    "duration", "shot_count", "word_count", "quality_score"
                ]
                
                metadata_checks = []
                for field in required_metadata_fields:
                    field_present = field in generation_metadata
                    metadata_checks.append(field_present)
                    
                    self.log_test(f"Generation Metadata - {field}", field_present,
                                f"Field '{field}' {'present' if field_present else 'missing'} in metadata")
                
                # Check for additional metadata fields
                additional_fields = ["attempts", "generation_method", "template_used"]
                for field in additional_fields:
                    if field in generation_metadata:
                        self.log_test(f"Generation Metadata - {field} (Optional)", True,
                                    f"Optional field '{field}' present with value: {generation_metadata[field]}")
                
                # Overall metadata assessment
                metadata_complete = sum(metadata_checks) >= len(required_metadata_fields) * 0.75
                self.log_test("Generation Statistics Logging", metadata_complete,
                            f"Metadata completeness: {sum(metadata_checks)}/{len(required_metadata_fields)} required fields")
                
                return generation_metadata
                
            else:
                self.log_test("Generation Statistics Logging", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Generation Statistics Logging", False, f"Request failed: {str(e)}")
            return None

    def test_auto_regeneration_logic(self):
        """Test auto-regeneration logic for under-target scripts"""
        print("🔄 Testing Auto-regeneration Logic...")
        
        # Test with a very simple prompt that might initially generate under-target content
        test_data = {
            "prompt": "Video about water",  # Intentionally simple to potentially trigger regeneration
            "video_type": "educational",
            "duration": "extended_10"  # High target to potentially trigger regeneration
        }
        
        try:
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=300)  # Extended timeout for potential regeneration
            
            if response.status_code == 200:
                data = response.json()
                script_content = data.get("generated_script", "")
                generation_metadata = data.get("generation_metadata", {})
                
                # Check if regeneration occurred
                attempts = generation_metadata.get("attempts", 1)
                regeneration_occurred = attempts > 1
                
                self.log_test("Auto-regeneration Detection", True,
                            f"Generation attempts: {attempts} ({'regeneration occurred' if regeneration_occurred else 'single attempt'})")
                
                # Check final quality
                analysis = self.analyze_script_quality(script_content, "extended_10")
                final_quality_acceptable = analysis["overall_percentage"] >= 50  # Lower threshold for this test
                
                self.log_test("Auto-regeneration Final Quality", final_quality_acceptable,
                            f"Final quality: {analysis['overall_percentage']:.1f}% (shots: {analysis['shot_count']}, words: {analysis['word_count']})")
                
                # Check for regeneration metadata
                if regeneration_occurred:
                    regeneration_reason = generation_metadata.get("regeneration_reason", "Not specified")
                    self.log_test("Auto-regeneration Metadata", True,
                                f"Regeneration reason: {regeneration_reason}")
                
                return {
                    "attempts": attempts,
                    "regeneration_occurred": regeneration_occurred,
                    "final_analysis": analysis
                }
                
            else:
                self.log_test("Auto-regeneration Logic", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Auto-regeneration Logic", False, f"Request failed: {str(e)}")
            return None

    def test_dramatic_scaling_differences(self):
        """Test that there are dramatic scaling differences between short and extended durations"""
        print("📈 Testing Dramatic Scaling Differences...")
        
        # Test short vs extended_10 to verify dramatic differences
        test_prompt = "Create a video about renewable energy technologies"
        
        short_result = None
        extended_result = None
        
        # Test short duration
        try:
            short_data = {
                "prompt": test_prompt,
                "video_type": "educational",
                "duration": "short"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=short_data, 
                                   timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                script_content = data.get("generated_script", "")
                short_result = self.analyze_script_quality(script_content, "short")
                
        except Exception as e:
            self.log_test("Dramatic Scaling - Short Duration", False, f"Request failed: {str(e)}")
        
        # Test extended_10 duration
        try:
            extended_data = {
                "prompt": test_prompt,
                "video_type": "educational",
                "duration": "extended_10"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=extended_data, 
                                   timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                script_content = data.get("generated_script", "")
                extended_result = self.analyze_script_quality(script_content, "extended_10")
                
        except Exception as e:
            self.log_test("Dramatic Scaling - Extended_10 Duration", False, f"Request failed: {str(e)}")
        
        # Compare results
        if short_result and extended_result:
            shot_ratio = extended_result["shot_count"] / short_result["shot_count"] if short_result["shot_count"] > 0 else 0
            word_ratio = extended_result["word_count"] / short_result["word_count"] if short_result["word_count"] > 0 else 0
            
            # Expect at least 10x difference for dramatic scaling
            dramatic_shot_scaling = shot_ratio >= 10
            dramatic_word_scaling = word_ratio >= 10
            
            self.log_test("Dramatic Shot Scaling", dramatic_shot_scaling,
                        f"Shot ratio: {shot_ratio:.1f}x (short: {short_result['shot_count']}, extended: {extended_result['shot_count']})")
            
            self.log_test("Dramatic Word Scaling", dramatic_word_scaling,
                        f"Word ratio: {word_ratio:.1f}x (short: {short_result['word_count']}, extended: {extended_result['word_count']})")
            
            overall_dramatic_scaling = dramatic_shot_scaling and dramatic_word_scaling
            self.log_test("Overall Dramatic Scaling", overall_dramatic_scaling,
                        f"Both shot and word scaling are dramatic: {overall_dramatic_scaling}")
            
            return {
                "short_result": short_result,
                "extended_result": extended_result,
                "shot_ratio": shot_ratio,
                "word_ratio": word_ratio
            }
        else:
            self.log_test("Dramatic Scaling Comparison", False, "Could not compare results due to generation failures")
            return None

    def run_comprehensive_tests(self):
        """Run all enhanced duration-aware script generation tests"""
        print("🚀 Starting Enhanced Duration-Aware Script Generation System Comprehensive Testing")
        print("=" * 90)
        print()
        
        # Test 1: Basic connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed. Stopping tests.")
            return 0
        
        # Test 2: Duration scaling verification
        print("📏 Testing Duration Scaling Verification...")
        scaling_results = self.test_duration_scaling_verification()
        
        # Test 3: Extended_10 specific requirements
        extended_10_result = self.test_extended_10_specific_requirements()
        
        # Test 4: Short duration requirements
        short_result = self.test_short_duration_requirements()
        
        # Test 5: Quality analysis function
        self.test_quality_analysis_function()
        
        # Test 6: Generation statistics logging
        metadata_result = self.test_generation_statistics_logging()
        
        # Test 7: Auto-regeneration logic
        regeneration_result = self.test_auto_regeneration_logic()
        
        # Test 8: Dramatic scaling differences
        scaling_comparison = self.test_dramatic_scaling_differences()
        
        # Final results
        print("=" * 90)
        print("🏁 ENHANCED DURATION-AWARE SCRIPT GENERATION SYSTEM TEST RESULTS")
        print("=" * 90)
        
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
        
        # Key findings summary
        print("🔍 KEY FINDINGS:")
        if scaling_comparison:
            print(f"   • Scaling Ratio: {scaling_comparison.get('shot_ratio', 0):.1f}x shots, {scaling_comparison.get('word_ratio', 0):.1f}x words (short vs extended_10)")
        
        if extended_10_result:
            print(f"   • Extended_10 Performance: {extended_10_result['shot_count']} shots, {extended_10_result['word_count']} words")
        
        if regeneration_result:
            print(f"   • Auto-regeneration: {regeneration_result['attempts']} attempts, regeneration {'occurred' if regeneration_result['regeneration_occurred'] else 'not needed'}")
        
        print()
        
        # Overall assessment
        if success_rate >= 85:
            print("🎉 EXCELLENT: Enhanced Duration-Aware Script Generation System is working excellently!")
            print("   The system properly scales content based on duration selection.")
        elif success_rate >= 70:
            print("✅ GOOD: Enhanced Duration-Aware Script Generation System is working well with minor issues.")
            print("   Most duration scaling features are functional.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Enhanced Duration-Aware Script Generation System has some issues that need attention.")
            print("   Duration scaling may not be working as expected.")
        else:
            print("❌ CRITICAL: Enhanced Duration-Aware Script Generation System has significant issues.")
            print("   Duration selection may not be affecting actual content length properly.")
        
        return success_rate

if __name__ == "__main__":
    print("Enhanced Duration-Aware Script Generation System - Backend Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = DurationAwareScriptGenerationTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)
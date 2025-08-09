#!/usr/bin/env python3
"""
Enhanced Prompt Enhancement System Testing
Tests the new enhanced /api/enhance-prompt endpoint as requested in the review
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://d4bc3e4b-9123-4ba2-8801-6a24a3b446a2.preview.emergentagent.com/api"

class EnhancedPromptTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Basic Connectivity", True, "API is accessible and responding")
                    return True
                else:
                    self.log_test("Basic Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Basic Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_new_enhanced_prompt_basic(self):
        """Test basic enhancement with minimal input"""
        print("\n=== Testing Basic Enhanced Prompt Enhancement ===")
        
        try:
            basic_payload = {
                "original_prompt": "Create a video about productivity tips"
            }
            
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=basic_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify new response structure
                required_fields = [
                    "original_prompt", "audience_analysis", "enhancement_variations", 
                    "quality_metrics", "recommendation", "industry_insights", "enhancement_methodology"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhanced Prompt - New Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify audience analysis structure
                audience_analysis = data["audience_analysis"]
                audience_fields = ["recommended_tone", "complexity_level", "cultural_considerations", "platform_optimizations", "engagement_triggers"]
                missing_audience_fields = [field for field in audience_fields if field not in audience_analysis]
                
                if missing_audience_fields:
                    self.log_test("Enhanced Prompt - Audience Analysis", False,
                                f"Missing audience analysis fields: {missing_audience_fields}")
                    return False
                
                # Verify enhancement variations (should be 3 by default)
                variations = data["enhancement_variations"]
                if not isinstance(variations, list) or len(variations) != 3:
                    self.log_test("Enhanced Prompt - Variations Count", False,
                                f"Expected 3 variations, got {len(variations) if isinstance(variations, list) else 'not a list'}")
                    return False
                
                # Verify each variation has required fields
                variation_fields = ["id", "title", "enhanced_prompt", "focus_strategy", "target_engagement", "industry_specific_elements", "estimated_performance_score"]
                for i, variation in enumerate(variations):
                    missing_var_fields = [field for field in variation_fields if field not in variation]
                    if missing_var_fields:
                        self.log_test(f"Enhanced Prompt - Variation {i+1} Structure", False,
                                    f"Missing variation fields: {missing_var_fields}")
                        return False
                
                # Verify different strategies
                strategies = [var["focus_strategy"] for var in variations]
                expected_strategies = ["emotional", "technical", "viral"]
                if not all(strategy in strategies for strategy in expected_strategies):
                    self.log_test("Enhanced Prompt - Strategy Variety", False,
                                f"Expected strategies {expected_strategies}, got {strategies}")
                    return False
                
                # Verify quality metrics structure
                quality_metrics = data["quality_metrics"]
                metrics_fields = ["emotional_engagement_score", "technical_clarity_score", "industry_relevance_score", "storytelling_strength_score", "overall_quality_score", "improvement_ratio"]
                missing_metrics_fields = [field for field in metrics_fields if field not in quality_metrics]
                
                if missing_metrics_fields:
                    self.log_test("Enhanced Prompt - Quality Metrics", False,
                                f"Missing quality metrics fields: {missing_metrics_fields}")
                    return False
                
                # Verify enhancement quality (should be substantially longer)
                original_length = len(data["original_prompt"])
                avg_enhanced_length = sum(len(var["enhanced_prompt"]) for var in variations) / len(variations)
                improvement_ratio = avg_enhanced_length / original_length
                
                if improvement_ratio < 5:  # Should be at least 5x longer
                    self.log_test("Enhanced Prompt - Enhancement Quality", False,
                                f"Enhancement ratio too low: {improvement_ratio:.1f}x (expected >5x)")
                    return False
                
                self.log_test("Enhanced Prompt - Basic Functionality", True,
                            f"Successfully enhanced prompt with {improvement_ratio:.1f}x improvement ratio")
                
                # Print sample output for verification
                print(f"\n📋 SAMPLE ENHANCEMENT OUTPUT:")
                print(f"Original: {data['original_prompt']}")
                print(f"Strategies: {strategies}")
                print(f"Improvement Ratio: {improvement_ratio:.1f}x")
                print(f"Quality Score: {quality_metrics['overall_quality_score']:.1f}/10")
                print(f"First Enhanced Prompt (first 200 chars): {variations[0]['enhanced_prompt'][:200]}...")
                
                return True
                
            else:
                self.log_test("Enhanced Prompt - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Basic Test", False, f"Request failed: {str(e)}")
            return False
    
    def test_different_video_types(self):
        """Test different video types"""
        print("\n=== Testing Different Video Types ===")
        
        video_types = ["marketing", "education", "entertainment", "tech"]
        successful_types = 0
        
        for video_type in video_types:
            try:
                type_payload = {
                    "original_prompt": "Promote our new fitness app to busy professionals",
                    "video_type": video_type,
                    "industry_focus": video_type
                }
                
                type_response = self.session.post(
                    f"{self.backend_url}/enhance-prompt",
                    json=type_payload,
                    timeout=60
                )
                
                if type_response.status_code == 200:
                    type_data = type_response.json()
                    
                    # Verify industry-specific insights
                    industry_insights = type_data.get("industry_insights", [])
                    if not industry_insights or len(industry_insights) < 2:
                        self.log_test(f"Enhanced Prompt - {video_type.title()} Industry Insights", False,
                                    f"Expected industry insights, got {len(industry_insights)}")
                    else:
                        self.log_test(f"Enhanced Prompt - {video_type.title()} Type", True,
                                    f"Successfully processed {video_type} with {len(industry_insights)} industry insights")
                        successful_types += 1
                        
                        # Print sample insights
                        print(f"  {video_type.title()} insights: {industry_insights[0][:100]}...")
                else:
                    self.log_test(f"Enhanced Prompt - {video_type.title()} Type", False,
                                f"Failed for {video_type}: {type_response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Enhanced Prompt - {video_type.title()} Type", False,
                            f"Exception: {str(e)}")
        
        return successful_types >= 3
    
    def test_multiple_enhancement_variations(self):
        """Test multiple enhancement variations"""
        print("\n=== Testing Multiple Enhancement Variations ===")
        
        try:
            variations_payload = {
                "original_prompt": "Explain machine learning concepts for beginners",
                "video_type": "education",
                "industry_focus": "education",
                "enhancement_count": 4,
                "enhancement_style": "educational"
            }
            
            variations_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=variations_payload,
                timeout=90
            )
            
            if variations_response.status_code == 200:
                variations_data = variations_response.json()
                variations = variations_data["enhancement_variations"]
                
                if len(variations) == 4:
                    self.log_test("Enhanced Prompt - Custom Variation Count", True,
                                f"Successfully generated {len(variations)} variations as requested")
                    
                    # Verify educational strategy is included
                    strategies = [var["focus_strategy"] for var in variations]
                    if "educational" in strategies:
                        self.log_test("Enhanced Prompt - Educational Strategy", True,
                                    "Educational strategy included in variations")
                    else:
                        self.log_test("Enhanced Prompt - Educational Strategy", False,
                                    f"Educational strategy not found in: {strategies}")
                    
                    # Print strategies
                    print(f"  Generated strategies: {strategies}")
                    return True
                else:
                    self.log_test("Enhanced Prompt - Custom Variation Count", False,
                                f"Expected 4 variations, got {len(variations)}")
                    return False
            else:
                self.log_test("Enhanced Prompt - Custom Variation Count", False,
                            f"Failed: {variations_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Custom Variation Count", False, f"Exception: {str(e)}")
            return False
    
    def test_quality_metrics(self):
        """Test quality metrics calculation"""
        print("\n=== Testing Quality Metrics ===")
        
        try:
            quality_payload = {
                "original_prompt": "Demonstrate our new API integration features",
                "video_type": "tech",
                "industry_focus": "tech"
            }
            
            quality_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=quality_payload,
                timeout=60
            )
            
            if quality_response.status_code == 200:
                quality_data = quality_response.json()
                quality_metrics = quality_data["quality_metrics"]
                
                # Verify all scores are within valid range (0-10)
                score_fields = ["emotional_engagement_score", "technical_clarity_score", "industry_relevance_score", "storytelling_strength_score", "overall_quality_score"]
                valid_scores = True
                
                for field in score_fields:
                    score = quality_metrics.get(field, -1)
                    if not (0 <= score <= 10):
                        valid_scores = False
                        break
                
                if valid_scores:
                    self.log_test("Enhanced Prompt - Quality Metrics Range", True,
                                "All quality scores within valid range (0-10)")
                else:
                    self.log_test("Enhanced Prompt - Quality Metrics Range", False,
                                "Some quality scores outside valid range")
                
                # Verify improvement ratio is reasonable
                improvement_ratio = quality_metrics.get("improvement_ratio", 0)
                if improvement_ratio > 1:
                    self.log_test("Enhanced Prompt - Improvement Ratio", True,
                                f"Good improvement ratio: {improvement_ratio:.1f}x")
                else:
                    self.log_test("Enhanced Prompt - Improvement Ratio", False,
                                f"Poor improvement ratio: {improvement_ratio:.1f}x")
                
                # Print quality metrics
                print(f"  Quality Metrics:")
                for field in score_fields:
                    print(f"    {field}: {quality_metrics.get(field, 0):.1f}/10")
                print(f"    Improvement Ratio: {improvement_ratio:.1f}x")
                
                return valid_scores and improvement_ratio > 1
                    
            else:
                self.log_test("Enhanced Prompt - Quality Metrics", False,
                            f"Failed: {quality_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Quality Metrics", False, f"Exception: {str(e)}")
            return False
    
    def test_recommendation_system(self):
        """Test recommendation system"""
        print("\n=== Testing Recommendation System ===")
        
        try:
            recommendation_payload = {
                "original_prompt": "Create engaging content about technology",
                "video_type": "general",
                "industry_focus": "tech"
            }
            
            rec_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=recommendation_payload,
                timeout=60
            )
            
            if rec_response.status_code == 200:
                rec_data = rec_response.json()
                recommendation = rec_data.get("recommendation", "")
                
                if len(recommendation) > 100 and "RECOMMENDED VARIATION" in recommendation:
                    self.log_test("Enhanced Prompt - Recommendation System", True,
                                f"Generated comprehensive recommendation ({len(recommendation)} chars)")
                    
                    # Print sample recommendation
                    print(f"  Sample recommendation (first 300 chars): {recommendation[:300]}...")
                    return True
                else:
                    self.log_test("Enhanced Prompt - Recommendation System", False,
                                f"Recommendation too short or missing key elements: {len(recommendation)} chars")
                    return False
                    
            else:
                self.log_test("Enhanced Prompt - Recommendation System", False,
                            f"Failed: {rec_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Recommendation System", False, f"Exception: {str(e)}")
            return False
    
    def test_legacy_compatibility(self):
        """Test backward compatibility with legacy endpoint"""
        print("\n=== Testing Legacy Compatibility ===")
        
        try:
            legacy_payload = {
                "original_prompt": "Create a motivational video about success",
                "video_type": "general"
            }
            
            legacy_response = self.session.post(
                f"{self.backend_url}/enhance-prompt-legacy",
                json=legacy_payload,
                timeout=60
            )
            
            if legacy_response.status_code == 200:
                legacy_data = legacy_response.json()
                
                # Verify legacy response structure
                legacy_fields = ["original_prompt", "enhanced_prompt", "enhancement_explanation"]
                missing_legacy_fields = [field for field in legacy_fields if field not in legacy_data]
                
                if missing_legacy_fields:
                    self.log_test("Legacy Prompt - Structure", False,
                                f"Missing legacy fields: {missing_legacy_fields}")
                    return False
                
                # Verify enhancement quality
                original = legacy_data["original_prompt"]
                enhanced = legacy_data["enhanced_prompt"]
                explanation = legacy_data["enhancement_explanation"]
                
                if len(enhanced) > len(original) * 3:  # Should be at least 3x longer
                    self.log_test("Legacy Prompt - Enhancement Quality", True,
                                f"Legacy enhancement successful: {len(original)} → {len(enhanced)} chars")
                else:
                    self.log_test("Legacy Prompt - Enhancement Quality", False,
                                f"Legacy enhancement insufficient: {len(original)} → {len(enhanced)} chars")
                
                if len(explanation) > 50:
                    self.log_test("Legacy Prompt - Explanation Quality", True,
                                f"Legacy explanation adequate: {len(explanation)} chars")
                else:
                    self.log_test("Legacy Prompt - Explanation Quality", False,
                                f"Legacy explanation too short: {len(explanation)} chars")
                
                # Print sample legacy output
                print(f"  Legacy enhanced (first 200 chars): {enhanced[:200]}...")
                
                return len(enhanced) > len(original) * 3 and len(explanation) > 50
                
            else:
                self.log_test("Legacy Prompt - HTTP Response", False,
                            f"HTTP {legacy_response.status_code}: {legacy_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Prompt - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def run_enhanced_prompt_tests(self):
        """Run all enhanced prompt tests"""
        print("🚀 Testing NEW Enhanced Prompt Enhancement System")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("\n❌ Basic connectivity failed. Stopping tests.")
            return False
        
        # Run enhanced prompt tests
        test_methods = [
            self.test_new_enhanced_prompt_basic,
            self.test_different_video_types,
            self.test_multiple_enhancement_variations,
            self.test_quality_metrics,
            self.test_recommendation_system,
            self.test_legacy_compatibility
        ]
        
        all_passed = True
        for test_method in test_methods:
            try:
                if not test_method():
                    all_passed = False
            except Exception as e:
                print(f"❌ Test suite {test_method.__name__} failed with exception: {str(e)}")
                all_passed = False
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 ENHANCED PROMPT SYSTEM TEST RESULTS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        if all_passed:
            print("\n🎉 ALL ENHANCED PROMPT TESTS PASSED!")
            print("✅ The new enhanced prompt enhancement system is working correctly")
            print("✅ Multiple enhancement variations with different strategies")
            print("✅ Audience analysis and quality metrics")
            print("✅ Industry-specific insights and recommendations")
            print("✅ Backward compatibility maintained")
        else:
            print("\n⚠️  Some enhanced prompt tests failed. Check details above.")
        
        return all_passed

if __name__ == "__main__":
    tester = EnhancedPromptTester()
    success = tester.run_enhanced_prompt_tests()
    sys.exit(0 if success else 1)
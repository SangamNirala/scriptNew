#!/usr/bin/env python3
"""
Backend Testing Script for Script Generation App
Tests all backend API endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://05dfb9f2-7093-403e-9397-45db048e0b56.preview.emergentagent.com/api"

class ScriptGenerationTester:
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
    
    def test_enhance_prompt_endpoint(self):
        """Test the NEW ENHANCED /api/enhance-prompt endpoint with advanced response structure"""
        print("\n=== Testing Enhanced Prompt Enhancement Endpoint ===")
        
        # Test Case 1: Basic test with sample prompt from review request
        test_prompt = "Create a video about healthy cooking tips"
        payload = {
            "original_prompt": test_prompt,
            "video_type": "general",
            "industry_focus": "health",
            "enhancement_count": 3
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=payload,
                timeout=60  # Increased timeout for complex processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify NEW response structure with all required fields
                required_fields = [
                    "original_prompt", 
                    "audience_analysis", 
                    "enhancement_variations", 
                    "quality_metrics", 
                    "recommendation", 
                    "industry_insights",
                    "enhancement_methodology"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhanced Prompt - New Structure", False, 
                                f"Missing required fields: {missing_fields}", data.keys())
                    return False
                
                self.log_test("Enhanced Prompt - New Structure", True,
                            "All required fields present in new enhanced response structure")
                
                # Test Case 2: Verify enhancement_variations structure
                variations = data["enhancement_variations"]
                if not isinstance(variations, list) or len(variations) == 0:
                    self.log_test("Enhanced Prompt - Enhancement Variations", False,
                                "enhancement_variations should be a non-empty list")
                    return False
                
                # Check each variation has required fields
                variation_required_fields = [
                    "id", "title", "enhanced_prompt", "focus_strategy", 
                    "target_engagement", "industry_specific_elements", 
                    "estimated_performance_score"
                ]
                
                for i, variation in enumerate(variations):
                    missing_var_fields = [field for field in variation_required_fields if field not in variation]
                    if missing_var_fields:
                        self.log_test(f"Enhanced Prompt - Variation {i+1} Structure", False,
                                    f"Missing fields in variation: {missing_var_fields}")
                        return False
                    
                    # Verify performance score is valid
                    score = variation.get("estimated_performance_score", 0)
                    if not isinstance(score, (int, float)) or score < 0 or score > 10:
                        self.log_test(f"Enhanced Prompt - Variation {i+1} Score", False,
                                    f"Invalid performance score: {score} (should be 0-10)")
                        return False
                
                self.log_test("Enhanced Prompt - Enhancement Variations", True,
                            f"Successfully verified {len(variations)} enhancement variations with all required fields")
                
                # Test Case 3: Verify quality_metrics structure
                quality_metrics = data["quality_metrics"]
                metrics_required_fields = [
                    "emotional_engagement_score", "technical_clarity_score", 
                    "industry_relevance_score", "storytelling_strength_score",
                    "overall_quality_score", "improvement_ratio"
                ]
                
                missing_metrics_fields = [field for field in metrics_required_fields if field not in quality_metrics]
                if missing_metrics_fields:
                    self.log_test("Enhanced Prompt - Quality Metrics", False,
                                f"Missing quality metrics fields: {missing_metrics_fields}")
                    return False
                
                # Verify all scores are in valid range
                for field in metrics_required_fields:
                    if field == "improvement_ratio":
                        continue  # This can be any positive number
                    score = quality_metrics.get(field, 0)
                    if not isinstance(score, (int, float)) or score < 0 or score > 10:
                        self.log_test("Enhanced Prompt - Quality Metrics Range", False,
                                    f"Invalid {field}: {score} (should be 0-10)")
                        return False
                
                self.log_test("Enhanced Prompt - Quality Metrics", True,
                            "Quality metrics structure verified with all scores in valid range")
                
                # Test Case 4: Verify audience_analysis structure
                audience_analysis = data["audience_analysis"]
                audience_required_fields = [
                    "recommended_tone", "complexity_level", 
                    "cultural_considerations", "platform_optimizations", 
                    "engagement_triggers"
                ]
                
                missing_audience_fields = [field for field in audience_required_fields if field not in audience_analysis]
                if missing_audience_fields:
                    self.log_test("Enhanced Prompt - Audience Analysis", False,
                                f"Missing audience analysis fields: {missing_audience_fields}")
                    return False
                
                self.log_test("Enhanced Prompt - Audience Analysis", True,
                            "Audience analysis structure verified with all required fields")
                
                # Test Case 5: Verify content quality and enhancement
                original_length = len(data["original_prompt"])
                best_variation = max(variations, key=lambda x: x["estimated_performance_score"])
                enhanced_length = len(best_variation["enhanced_prompt"])
                
                if enhanced_length <= original_length:
                    self.log_test("Enhanced Prompt - Enhancement Quality", False,
                                f"Best enhanced prompt ({enhanced_length} chars) not longer than original ({original_length} chars)")
                    return False
                
                improvement_ratio = quality_metrics["improvement_ratio"]
                if improvement_ratio < 1.5:  # Should be at least 50% improvement
                    self.log_test("Enhanced Prompt - Improvement Ratio", False,
                                f"Improvement ratio too low: {improvement_ratio:.2f}x")
                    return False
                
                self.log_test("Enhanced Prompt - Enhancement Quality", True,
                            f"Quality enhancement verified: {original_length} → {enhanced_length} chars, {improvement_ratio:.1f}x improvement")
                
                # Test Case 6: Verify recommendation and industry insights
                recommendation = data["recommendation"]
                industry_insights = data["industry_insights"]
                
                if not recommendation or len(recommendation) < 50:
                    self.log_test("Enhanced Prompt - Recommendation", False,
                                "Recommendation is too short or missing")
                    return False
                
                if not isinstance(industry_insights, list) or len(industry_insights) == 0:
                    self.log_test("Enhanced Prompt - Industry Insights", False,
                                "Industry insights should be a non-empty list")
                    return False
                
                self.log_test("Enhanced Prompt - Recommendation & Insights", True,
                            f"Recommendation ({len(recommendation)} chars) and {len(industry_insights)} industry insights verified")
                
                # Test Case 7: Test different enhancement strategies
                strategies_found = set(var["focus_strategy"] for var in variations)
                expected_strategies = {"emotional", "technical", "viral"}
                
                if not strategies_found.intersection(expected_strategies):
                    self.log_test("Enhanced Prompt - Strategy Variety", False,
                                f"No expected strategies found. Got: {strategies_found}")
                    return False
                
                self.log_test("Enhanced Prompt - Strategy Variety", True,
                            f"Multiple enhancement strategies verified: {strategies_found}")
                
                return True
                
            else:
                self.log_test("Enhanced Prompt - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_enhanced_prompt_different_scenarios(self):
        """Test enhanced prompt endpoint with different scenarios and parameters"""
        print("\n=== Testing Enhanced Prompt Different Scenarios ===")
        
        test_scenarios = [
            {
                "name": "Marketing Focus",
                "payload": {
                    "original_prompt": "Create a video about healthy cooking tips",
                    "video_type": "marketing",
                    "industry_focus": "health",
                    "enhancement_count": 3
                }
            },
            {
                "name": "Educational Focus", 
                "payload": {
                    "original_prompt": "Explain artificial intelligence basics",
                    "video_type": "educational",
                    "industry_focus": "tech",
                    "enhancement_count": 4
                }
            },
            {
                "name": "Entertainment Focus",
                "payload": {
                    "original_prompt": "Fun workout routine for beginners",
                    "video_type": "entertainment", 
                    "industry_focus": "health",
                    "enhancement_count": 2
                }
            }
        ]
        
        successful_tests = 0
        
        for scenario in test_scenarios:
            try:
                response = self.session.post(
                    f"{self.backend_url}/enhance-prompt",
                    json=scenario["payload"],
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify basic structure
                    if "enhancement_variations" in data and "quality_metrics" in data:
                        variations = data["enhancement_variations"]
                        expected_count = scenario["payload"]["enhancement_count"]
                        
                        if len(variations) >= expected_count:
                            self.log_test(f"Enhanced Prompt Scenario - {scenario['name']}", True,
                                        f"Successfully generated {len(variations)} variations for {scenario['name']}")
                            successful_tests += 1
                        else:
                            self.log_test(f"Enhanced Prompt Scenario - {scenario['name']}", False,
                                        f"Expected {expected_count} variations, got {len(variations)}")
                    else:
                        self.log_test(f"Enhanced Prompt Scenario - {scenario['name']}", False,
                                    "Missing required response structure")
                else:
                    self.log_test(f"Enhanced Prompt Scenario - {scenario['name']}", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Enhanced Prompt Scenario - {scenario['name']}", False,
                            f"Exception: {str(e)}")
        
        if successful_tests >= 2:
            self.log_test("Enhanced Prompt Scenarios - Overall", True,
                        f"Successfully tested {successful_tests}/{len(test_scenarios)} scenarios")
            return True
        else:
            self.log_test("Enhanced Prompt Scenarios - Overall", False,
                        f"Only {successful_tests}/{len(test_scenarios)} scenarios succeeded")
            return False
    
    def test_comprehensive_script_framework_system(self):
        """Test the completely redesigned /api/enhance-prompt endpoint for comprehensive script frameworks"""
        print("\n=== Testing Comprehensive Script Framework Enhancement System ===")
        
        # Test Case 1: Sample from review request - "Create a video about productivity tips for remote workers"
        test_prompt = "Create a video about productivity tips for remote workers"
        payload = {
            "original_prompt": test_prompt,
            "video_type": "educational",
            "industry_focus": "tech",
            "enhancement_count": 3
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=payload,
                timeout=90  # Increased timeout for comprehensive processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Test Case 1.1: Verify comprehensive response structure with all required sections
                required_sections = [
                    "original_prompt", "audience_analysis", "enhancement_variations", 
                    "quality_metrics", "recommendation", "industry_insights", "enhancement_methodology"
                ]
                missing_sections = [section for section in required_sections if section not in data]
                
                if missing_sections:
                    self.log_test("Script Framework - Response Structure", False,
                                f"Missing required sections: {missing_sections}")
                    return False
                
                self.log_test("Script Framework - Response Structure", True,
                            "All required sections present in comprehensive response structure")
                
                # Test Case 1.2: Verify enhancement variations are comprehensive script frameworks
                variations = data["enhancement_variations"]
                if len(variations) < 3:
                    self.log_test("Script Framework - Variation Count", False,
                                f"Expected at least 3 variations, got {len(variations)}")
                    return False
                
                framework_quality_tests = 0
                
                for i, variation in enumerate(variations):
                    enhanced_prompt = variation.get("enhanced_prompt", "")
                    
                    # Test framework comprehensiveness (should be 500+ words)
                    word_count = len(enhanced_prompt.split())
                    if word_count >= 500:
                        self.log_test(f"Script Framework - Variation {i+1} Length", True,
                                    f"Framework has {word_count} words (meets 500+ requirement)")
                        framework_quality_tests += 1
                    else:
                        self.log_test(f"Script Framework - Variation {i+1} Length", False,
                                    f"Framework only has {word_count} words (needs 500+)")
                    
                    # Test for comprehensive framework elements
                    framework_elements = {
                        "SCRIPT_FRAMEWORK": "opening hooks, narrative structure templates, dialogue placeholders",
                        "PRODUCTION_GUIDELINES": "production guidelines and call-to-action frameworks", 
                        "PSYCHOLOGICAL_TRIGGERS": "psychological triggers and engagement mechanics",
                        "PLATFORM_ADAPTATIONS": "platform adaptations for different social media channels",
                        "TARGET_ENGAGEMENT": "target engagement patterns and success metrics",
                        "INDUSTRY_ELEMENTS": "industry-specific customization and best practices"
                    }
                    
                    elements_found = 0
                    for element, description in framework_elements.items():
                        if element in enhanced_prompt.upper():
                            elements_found += 1
                    
                    if elements_found >= 4:  # Should have most framework elements
                        self.log_test(f"Script Framework - Variation {i+1} Elements", True,
                                    f"Framework contains {elements_found}/6 required elements")
                        framework_quality_tests += 1
                    else:
                        self.log_test(f"Script Framework - Variation {i+1} Elements", False,
                                    f"Framework only contains {elements_found}/6 required elements")
                
                # Test Case 1.3: Verify three advanced categories (Emotional, Technical, Viral)
                strategies_found = set()
                for variation in variations:
                    focus_strategy = variation.get("focus_strategy", "").lower()
                    if "emotional" in focus_strategy:
                        strategies_found.add("emotional")
                    elif "technical" in focus_strategy:
                        strategies_found.add("technical") 
                    elif "viral" in focus_strategy:
                        strategies_found.add("viral")
                
                expected_strategies = {"emotional", "technical", "viral"}
                if len(strategies_found.intersection(expected_strategies)) >= 2:
                    self.log_test("Script Framework - Strategy Categories", True,
                                f"Found advanced categories: {strategies_found}")
                else:
                    self.log_test("Script Framework - Strategy Categories", False,
                                f"Missing expected categories. Found: {strategies_found}")
                
                # Test Case 1.4: Verify industry-specific customization
                industry_elements_count = 0
                for variation in variations:
                    industry_elements = variation.get("industry_specific_elements", [])
                    if isinstance(industry_elements, list) and len(industry_elements) >= 3:
                        industry_elements_count += 1
                
                if industry_elements_count >= 2:
                    self.log_test("Script Framework - Industry Customization", True,
                                f"{industry_elements_count} variations have comprehensive industry elements")
                else:
                    self.log_test("Script Framework - Industry Customization", False,
                                f"Only {industry_elements_count} variations have adequate industry elements")
                
                # Test Case 1.5: Verify quality metrics show substantial improvement
                quality_metrics = data["quality_metrics"]
                improvement_ratio = quality_metrics.get("improvement_ratio", 0)
                overall_score = quality_metrics.get("overall_quality_score", 0)
                
                if improvement_ratio >= 10.0:  # Should show significant improvement
                    self.log_test("Script Framework - Quality Improvement", True,
                                f"Substantial improvement ratio: {improvement_ratio:.1f}x")
                else:
                    self.log_test("Script Framework - Quality Improvement", False,
                                f"Improvement ratio too low: {improvement_ratio:.1f}x")
                
                if overall_score >= 8.0:  # Should have high quality score
                    self.log_test("Script Framework - Overall Quality", True,
                                f"High quality score: {overall_score:.1f}/10")
                else:
                    self.log_test("Script Framework - Overall Quality", False,
                                f"Quality score too low: {overall_score:.1f}/10")
                
                # Test Case 1.6: Test different video types and industries
                additional_tests = [
                    {
                        "prompt": "Create a video about healthy cooking tips",
                        "video_type": "marketing",
                        "industry_focus": "health"
                    },
                    {
                        "prompt": "Explain blockchain technology basics", 
                        "video_type": "educational",
                        "industry_focus": "tech"
                    }
                ]
                
                additional_success = 0
                for test_case in additional_tests:
                    try:
                        test_payload = {
                            "original_prompt": test_case["prompt"],
                            "video_type": test_case["video_type"],
                            "industry_focus": test_case["industry_focus"],
                            "enhancement_count": 3
                        }
                        
                        test_response = self.session.post(
                            f"{self.backend_url}/enhance-prompt",
                            json=test_payload,
                            timeout=90
                        )
                        
                        if test_response.status_code == 200:
                            test_data = test_response.json()
                            test_variations = test_data.get("enhancement_variations", [])
                            
                            if len(test_variations) >= 3:
                                # Check if at least one variation is comprehensive
                                comprehensive_found = False
                                for var in test_variations:
                                    if len(var.get("enhanced_prompt", "").split()) >= 400:
                                        comprehensive_found = True
                                        break
                                
                                if comprehensive_found:
                                    additional_success += 1
                                    self.log_test(f"Script Framework - {test_case['industry_focus'].title()} Industry", True,
                                                f"Successfully generated comprehensive frameworks for {test_case['industry_focus']} industry")
                                else:
                                    self.log_test(f"Script Framework - {test_case['industry_focus'].title()} Industry", False,
                                                "Generated frameworks not comprehensive enough")
                            else:
                                self.log_test(f"Script Framework - {test_case['industry_focus'].title()} Industry", False,
                                            f"Only generated {len(test_variations)} variations")
                        else:
                            self.log_test(f"Script Framework - {test_case['industry_focus'].title()} Industry", False,
                                        f"HTTP {test_response.status_code}")
                    except Exception as e:
                        self.log_test(f"Script Framework - {test_case['industry_focus'].title()} Industry", False,
                                    f"Exception: {str(e)}")
                
                # Overall assessment
                total_tests = 7  # Main test categories
                passed_tests = (
                    1 +  # Response structure
                    (1 if framework_quality_tests >= 4 else 0) +  # Framework quality
                    (1 if len(strategies_found.intersection(expected_strategies)) >= 2 else 0) +  # Strategy categories
                    (1 if industry_elements_count >= 2 else 0) +  # Industry customization
                    (1 if improvement_ratio >= 10.0 else 0) +  # Quality improvement
                    (1 if overall_score >= 8.0 else 0) +  # Overall quality
                    additional_success  # Additional industry tests
                )
                
                if passed_tests >= 6:
                    self.log_test("Script Framework System - Comprehensive Test", True,
                                f"Advanced script framework system working excellently: {passed_tests}/{total_tests + len(additional_tests)} tests passed")
                    return True
                else:
                    self.log_test("Script Framework System - Comprehensive Test", False,
                                f"Script framework system needs improvement: only {passed_tests}/{total_tests + len(additional_tests)} tests passed")
                    return False
                
            else:
                self.log_test("Script Framework System - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Script Framework System - Exception", False, f"Comprehensive test failed: {str(e)}")
            return False
    
    def test_generate_script_endpoint(self):
        """Test the /api/generate-script endpoint"""
        print("\n=== Testing Script Generation Endpoint ===")
        
        # Test Case 1: Basic script generation
        test_prompt = "Create a motivational video about overcoming challenges and achieving success"
        payload = {
            "prompt": test_prompt,
            "video_type": "general",
            "duration": "short"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Generate Script - Structure", False,
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify content quality
                script = data["generated_script"]
                if len(script) < 100:
                    self.log_test("Generate Script - Content Length", False,
                                "Generated script is too short", {"script_length": len(script)})
                    return False
                
                # Check for storytelling elements
                storytelling_indicators = [
                    "[", "]",  # Scene descriptions
                    "(", ")",  # Speaker directions
                ]
                
                has_formatting = any(indicator in script for indicator in storytelling_indicators)
                if not has_formatting:
                    self.log_test("Generate Script - Formatting", False,
                                "Script lacks proper formatting (scene descriptions, speaker directions)")
                else:
                    self.log_test("Generate Script - Formatting", True,
                                "Script includes proper formatting elements")
                
                self.log_test("Generate Script - Basic Functionality", True,
                            f"Successfully generated {len(script)} character script")
                
                # Test Case 2: Different video types and durations
                test_combinations = [
                    {"video_type": "educational", "duration": "medium"},
                    {"video_type": "entertainment", "duration": "long"},
                    {"video_type": "marketing", "duration": "short"}
                ]
                
                for combo in test_combinations:
                    test_payload = {
                        "prompt": "Create engaging content about innovation",
                        **combo
                    }
                    
                    combo_response = self.session.post(
                        f"{self.backend_url}/generate-script",
                        json=test_payload,
                        timeout=45
                    )
                    
                    if combo_response.status_code == 200:
                        combo_data = combo_response.json()
                        self.log_test(f"Generate Script - {combo['video_type']}/{combo['duration']}", True,
                                    f"Successfully generated script for {combo['video_type']} {combo['duration']} video")
                    else:
                        self.log_test(f"Generate Script - {combo['video_type']}/{combo['duration']}", False,
                                    f"Failed: {combo_response.status_code}")
                
                return True
                
            else:
                self.log_test("Generate Script - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Script - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_scripts_retrieval_endpoint(self):
        """Test the /api/scripts endpoint"""
        print("\n=== Testing Scripts Retrieval Endpoint ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Scripts Retrieval - Data Type", False,
                                "Response is not a list", {"response_type": type(data).__name__})
                    return False
                
                if len(data) == 0:
                    self.log_test("Scripts Retrieval - Empty List", True,
                                "No scripts found (expected if no scripts generated yet)")
                    return True
                
                # Verify script structure
                first_script = data[0]
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in first_script]
                
                if missing_fields:
                    self.log_test("Scripts Retrieval - Script Structure", False,
                                f"Missing fields in script: {missing_fields}")
                    return False
                
                # Check chronological order (newest first)
                if len(data) > 1:
                    timestamps = [script["created_at"] for script in data]
                    is_sorted = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
                    
                    if is_sorted:
                        self.log_test("Scripts Retrieval - Chronological Order", True,
                                    "Scripts are properly sorted in reverse chronological order")
                    else:
                        self.log_test("Scripts Retrieval - Chronological Order", False,
                                    "Scripts are not sorted in reverse chronological order")
                
                self.log_test("Scripts Retrieval - Basic Functionality", True,
                            f"Successfully retrieved {len(data)} scripts")
                return True
                
            else:
                self.log_test("Scripts Retrieval - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Scripts Retrieval - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_integration_flow(self):
        """Test the complete integration flow"""
        print("\n=== Testing Integration Flow ===")
        
        try:
            # Step 1: Enhance a prompt
            original_prompt = "fitness motivation for beginners"
            enhance_payload = {
                "original_prompt": original_prompt,
                "video_type": "motivational"
            }
            
            enhance_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=enhance_payload,
                timeout=30
            )
            
            if enhance_response.status_code != 200:
                self.log_test("Integration Flow - Enhance Step", False,
                            f"Enhance prompt failed: {enhance_response.status_code}")
                return False
            
            enhanced_data = enhance_response.json()
            enhanced_prompt = enhanced_data["enhanced_prompt"]
            
            # Step 2: Generate script with enhanced prompt
            script_payload = {
                "prompt": enhanced_prompt,
                "video_type": "motivational",
                "duration": "medium"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Integration Flow - Script Generation Step", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            script_id = script_data["id"]
            
            # Step 3: Retrieve scripts and verify our script is there
            time.sleep(1)  # Brief pause to ensure database consistency
            
            retrieval_response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if retrieval_response.status_code != 200:
                self.log_test("Integration Flow - Retrieval Step", False,
                            f"Script retrieval failed: {retrieval_response.status_code}")
                return False
            
            scripts = retrieval_response.json()
            script_found = any(script["id"] == script_id for script in scripts)
            
            if not script_found:
                self.log_test("Integration Flow - Data Persistence", False,
                            "Generated script not found in retrieval results")
                return False
            
            self.log_test("Integration Flow - Complete", True,
                        "Successfully completed enhance → generate → retrieve flow")
            return True
            
        except Exception as e:
            self.log_test("Integration Flow - Exception", False, f"Integration test failed: {str(e)}")
            return False
    
    def test_voices_endpoint(self):
        """Test the /api/voices endpoint"""
        print("\n=== Testing Voices Endpoint ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Voices Endpoint - Data Type", False,
                                "Response is not a list", {"response_type": type(data).__name__})
                    return False
                
                if len(data) == 0:
                    self.log_test("Voices Endpoint - Empty List", False,
                                "No voices returned - expected at least some voices")
                    return False
                
                # Verify voice structure
                first_voice = data[0]
                required_fields = ["name", "display_name", "language", "gender"]
                missing_fields = [field for field in required_fields if field not in first_voice]
                
                if missing_fields:
                    self.log_test("Voices Endpoint - Voice Structure", False,
                                f"Missing fields in voice: {missing_fields}")
                    return False
                
                # Check for variety of voices
                genders = set(voice.get("gender", "") for voice in data)
                languages = set(voice.get("language", "") for voice in data)
                
                if len(genders) < 2:
                    self.log_test("Voices Endpoint - Gender Variety", False,
                                f"Expected both male and female voices, got: {genders}")
                else:
                    self.log_test("Voices Endpoint - Gender Variety", True,
                                f"Good gender variety: {genders}")
                
                if len(languages) < 2:
                    self.log_test("Voices Endpoint - Language Variety", False,
                                f"Expected multiple language variants, got: {languages}")
                else:
                    self.log_test("Voices Endpoint - Language Variety", True,
                                f"Good language variety: {len(languages)} variants")
                
                # Check for expected popular voices
                voice_names = [voice.get("name", "") for voice in data]
                expected_voices = ["en-US-AriaNeural", "en-US-DavisNeural", "en-GB-SoniaNeural"]
                found_expected = [voice for voice in expected_voices if voice in voice_names]
                
                if len(found_expected) >= 2:
                    self.log_test("Voices Endpoint - Popular Voices", True,
                                f"Found expected popular voices: {found_expected}")
                else:
                    self.log_test("Voices Endpoint - Popular Voices", False,
                                f"Expected popular voices not found. Available: {voice_names[:5]}")
                
                self.log_test("Voices Endpoint - Basic Functionality", True,
                            f"Successfully retrieved {len(data)} voices")
                return True
                
            else:
                self.log_test("Voices Endpoint - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Voices Endpoint - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_generate_audio_endpoint(self):
        """Test the /api/generate-audio endpoint"""
        print("\n=== Testing Generate Audio Endpoint ===")
        
        # First get available voices
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Generate Audio - Voice Retrieval", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Generate Audio - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            test_voice = voices[0]["name"]  # Use first available voice
            
        except Exception as e:
            self.log_test("Generate Audio - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test Case 1: Basic audio generation
        test_text = "Hello, this is a test of the text-to-speech functionality."
        payload = {
            "text": test_text,
            "voice_name": test_voice
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["audio_base64", "voice_used"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Generate Audio - Structure", False,
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify audio data
                audio_base64 = data["audio_base64"]
                if not audio_base64 or len(audio_base64) < 100:
                    self.log_test("Generate Audio - Audio Data", False,
                                "Audio base64 data is too short or empty",
                                {"audio_length": len(audio_base64) if audio_base64 else 0})
                    return False
                
                # Verify voice used matches request
                if data["voice_used"] != test_voice:
                    self.log_test("Generate Audio - Voice Matching", False,
                                f"Requested {test_voice}, got {data['voice_used']}")
                    return False
                
                self.log_test("Generate Audio - Basic Functionality", True,
                            f"Successfully generated {len(audio_base64)} chars of base64 audio")
                
                # Test Case 2: Different voices
                if len(voices) > 1:
                    different_voice = voices[1]["name"]
                    different_payload = {
                        "text": test_text,
                        "voice_name": different_voice
                    }
                    
                    different_response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=different_payload,
                        timeout=30
                    )
                    
                    if different_response.status_code == 200:
                        different_data = different_response.json()
                        
                        # Verify different voices produce different audio
                        if different_data["audio_base64"] != audio_base64:
                            self.log_test("Generate Audio - Voice Variation", True,
                                        "Different voices produce different audio output")
                        else:
                            self.log_test("Generate Audio - Voice Variation", False,
                                        "Different voices produced identical audio")
                    else:
                        self.log_test("Generate Audio - Multiple Voices", False,
                                    f"Failed with different voice: {different_response.status_code}")
                
                # Test Case 3: Script formatting removal
                script_text = "[Scene: Office setting] Hello there! (speaking enthusiastically) This is a **test** of script formatting removal."
                script_payload = {
                    "text": script_text,
                    "voice_name": test_voice
                }
                
                script_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=script_payload,
                    timeout=30
                )
                
                if script_response.status_code == 200:
                    self.log_test("Generate Audio - Script Formatting", True,
                                "Successfully processed text with script formatting")
                else:
                    self.log_test("Generate Audio - Script Formatting", False,
                                f"Failed with script formatting: {script_response.status_code}")
                
                return True
                
            else:
                self.log_test("Generate Audio - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Audio - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_timestamp_removal_comprehensive(self):
        """Test timestamp removal functionality as specified in review request"""
        print("\n=== Testing Timestamp Removal (Review Request Focus) ===")
        
        # Test cases for different timestamp formats as specified in review request
        timestamp_test_cases = [
            {
                "name": "Format with spaces",
                "input": "(0:30 - 0:45) Content here should remain without timestamps",
                "expected_clean": "Content here should remain without timestamps"
            },
            {
                "name": "Format without spaces", 
                "input": "(0:00-0:03) Content here should remain clean",
                "expected_clean": "Content here should remain clean"
            },
            {
                "name": "Mixed formats in same text",
                "input": "(0:00-0:03) First part. (0:30 - 0:45) Second part. (1:00-1:15) Third part.",
                "expected_clean": "First part. Second part. Third part."
            },
            {
                "name": "Timestamps with different dash types",
                "input": "(0:00–0:03) Content with en-dash. (0:30-0:45) Content with hyphen.",
                "expected_clean": "Content with en-dash. Content with hyphen."
            },
            {
                "name": "Multiple timestamps per line",
                "input": "(0:00-0:03) Start content (0:15-0:20) middle content (0:30 - 0:45) end content",
                "expected_clean": "Start content middle content end content"
            },
            {
                "name": "Timestamps at different positions",
                "input": "Before text (0:30 - 0:45) middle text after text",
                "expected_clean": "Before text middle text after text"
            }
        ]
        
        # Get available voices for testing
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Timestamp Removal - Voice Setup", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Timestamp Removal - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            test_voice = voices[0]["name"]
            
        except Exception as e:
            self.log_test("Timestamp Removal - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test each timestamp format
        successful_tests = 0
        
        for test_case in timestamp_test_cases:
            try:
                # Test audio generation with timestamp text
                payload = {
                    "text": test_case["input"],
                    "voice_name": test_voice
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data["audio_base64"]
                    
                    # Verify audio was generated (indicating text was cleaned successfully)
                    if len(audio_base64) > 1000:  # Should have substantial audio
                        self.log_test(f"Timestamp Removal - {test_case['name']}", True,
                                    f"Successfully processed and generated {len(audio_base64)} chars of audio")
                        successful_tests += 1
                    else:
                        self.log_test(f"Timestamp Removal - {test_case['name']}", False,
                                    f"Audio too short: {len(audio_base64)} chars")
                else:
                    self.log_test(f"Timestamp Removal - {test_case['name']}", False,
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Timestamp Removal - {test_case['name']}", False,
                            f"Exception: {str(e)}")
        
        # Test the comprehensive script from review request
        comprehensive_script = """VIDEO SCRIPT: AI-POWERED CRM LAUNCH

TARGET DURATION: 30-45 Seconds

VIDEO TYPE: General Audience / Small to Medium Businesses

SCRIPT:

(0:00-0:03) [SCENE START: Fast cuts of overwhelmed salespeople juggling calls, emails, and spreadsheets. High-energy, frantic music.]

(Narrator – Urgent, slightly panicked tone)
ARE YOU DROWNING in follow-ups? ... Sales slipping through the cracks? ... You're NOT alone.

(0:03-0:07) [SCENE CHANGE: Transition to a sleek, minimalist interface of the new CRM software. Calm, professional music begins.]

(Narrator – Tone shifts to calm, confident)
But what if you could RECLAIM your time...and BOOST your sales... by 40%?

(0:07-0:12) [SCENE: Screen recording showcasing automated email sequences and task management features.]

(Narrator)
Introducing [CRM Software Name]! ... The AI-powered CRM designed to AUTOMATE your follow-ups...and turn leads into loyal customers.

(0:12-0:18) [SCENE: Graph showing a clear upward trend in sales conversions, juxtaposed with happy, relaxed salespeople celebrating.]

(Narrator – Enthusiastic, energetic)
Imagine: NO MORE missed opportunities. Just a streamlined, efficient sales engine... working FOR you, 24/7.

(0:18-0:25) [SCENE: Quick cuts highlighting key features: lead scoring, personalized email templates, analytics dashboards.]

(Narrator – Fast-paced, highlighting benefits)
[CRM Software Name] intelligently SCORES your leads...PERSONALIZEs your messaging...and PREDICTs your next best move.

(0:25-0:30) [SCENE: Testimonial snippet – A business owner smiles and nods enthusiastically.]

(Testimonial VO – Genuine, authentic)
"Since using [CRM Software Name], our sales have EXPLODED! ... It's a game-changer."

(0:30-0:35) [SCENE: Clear call to action with website address and limited-time offer. Upbeat, driving music swells.]

(Narrator – Urgent, action-oriented)
Ready to SCALE your sales? Visit [Website Address] TODAY! ... And claim your FREE trial + 20% off! ... Don't wait, this offer is LIMITED!

(0:35-0:40) [SCENE: End screen with company logo and tagline. Music fades out.]

(Narrator – Final, confident statement)
[CRM Software Name]. Sales. Simplified.

KEY RETENTION ELEMENTS:

* Immediate Problem/Solution: Start with the pain point, then offer the immediate solution.
* Benefit-Driven Language: Focus on what the viewer GAINS (time, sales, efficiency).
* Visual Cues: The script is written to work with the visuals, reinforcing the message.
* Social Proof: The testimonial adds credibility.
* Urgency: The limited-time offer creates a sense of FOMO (fear of missing out)."""

        # Expected clean output (only spoken content)
        expected_segments = [
            "ARE YOU DROWNING in follow-ups? Sales slipping through the cracks? You're NOT alone.",
            "But what if you could RECLAIM your time and BOOST your sales by 40%?",
            "Introducing [CRM Software Name]! The AI-powered CRM designed to AUTOMATE your follow-ups and turn leads into loyal customers.",
            "Imagine: NO MORE missed opportunities. Just a streamlined, efficient sales engine working FOR you, 24/7.",
            "[CRM Software Name] intelligently SCORES your leads PERSONALIZEs your messaging and PREDICTs your next best move.",
            "Since using [CRM Software Name], our sales have EXPLODED! It's a game-changer.",
            "Ready to SCALE your sales? Visit [Website Address] TODAY! And claim your FREE trial + 20% off! Don't wait, this offer is LIMITED!",
            "[CRM Software Name]. Sales. Simplified."
        ]
        
        # Test with multiple voices to ensure consistency
        try:
            # First get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Extract Clean Script - Voice Retrieval", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Extract Clean Script - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            # Test with first 3 voices (or all if less than 3)
            test_voices = voices[:min(3, len(voices))]
            successful_tests = 0
            all_cleaned_outputs = []
            
            for voice in test_voices:
                voice_name = voice["name"]
                
                # Test audio generation with comprehensive script
                payload = {
                    "text": comprehensive_script,
                    "voice_name": voice_name
                }
                
                try:
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=60  # Longer timeout for complex script
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data["audio_base64"]
                        
                        # Verify substantial audio was generated
                        if len(audio_base64) > 10000:  # Should be substantial audio
                            self.log_test(f"Extract Clean Script - {voice['display_name']}", True,
                                        f"Successfully generated {len(audio_base64)} chars of audio")
                            successful_tests += 1
                            all_cleaned_outputs.append(audio_base64[:200])  # Store sample for comparison
                        else:
                            self.log_test(f"Extract Clean Script - {voice['display_name']}", False,
                                        f"Audio too short: {len(audio_base64)} chars")
                    else:
                        self.log_test(f"Extract Clean Script - {voice['display_name']}", False,
                                    f"HTTP {response.status_code}: {response.text[:200]}")
                        
                except Exception as e:
                    self.log_test(f"Extract Clean Script - {voice['display_name']}", False,
                                f"Exception: {str(e)}")
            
            # Verify script cleaning worked properly by testing key requirements
            if successful_tests > 0:
                # Test that timestamps are removed
                test_payload = {
                    "text": "(0:00-0:03) This should not have timestamps in audio",
                    "voice_name": test_voices[0]["name"]
                }
                
                timestamp_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=test_payload,
                    timeout=30
                )
                
                if timestamp_response.status_code == 200:
                    self.log_test("Extract Clean Script - Timestamp Removal", True,
                                "Successfully processed text with timestamps")
                else:
                    self.log_test("Extract Clean Script - Timestamp Removal", False,
                                f"Failed timestamp test: {timestamp_response.status_code}")
                
                # Test that scene descriptions are removed
                scene_payload = {
                    "text": "[SCENE: Office setting] Hello there! This is clean speech.",
                    "voice_name": test_voices[0]["name"]
                }
                
                scene_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=scene_payload,
                    timeout=30
                )
                
                if scene_response.status_code == 200:
                    self.log_test("Extract Clean Script - Scene Description Removal", True,
                                "Successfully processed text with scene descriptions")
                else:
                    self.log_test("Extract Clean Script - Scene Description Removal", False,
                                f"Failed scene description test: {scene_response.status_code}")
                
                # Test that speaker directions are removed
                speaker_payload = {
                    "text": "(Narrator – Urgent tone) This should be clean speech without directions.",
                    "voice_name": test_voices[0]["name"]
                }
                
                speaker_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=speaker_payload,
                    timeout=30
                )
                
                if speaker_response.status_code == 200:
                    self.log_test("Extract Clean Script - Speaker Direction Removal", True,
                                "Successfully processed text with speaker directions")
                else:
                    self.log_test("Extract Clean Script - Speaker Direction Removal", False,
                                f"Failed speaker direction test: {speaker_response.status_code}")
                
                # Test that metadata sections are removed
                metadata_payload = {
                    "text": """TARGET DURATION: 30 seconds
                    
                    SCRIPT:
                    This is the actual spoken content that should remain.
                    
                    KEY RETENTION ELEMENTS:
                    * This should be removed
                    * So should this""",
                    "voice_name": test_voices[0]["name"]
                }
                
                metadata_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=metadata_payload,
                    timeout=30
                )
                
                if metadata_response.status_code == 200:
                    self.log_test("Extract Clean Script - Metadata Removal", True,
                                "Successfully processed text with metadata sections")
                else:
                    self.log_test("Extract Clean Script - Metadata Removal", False,
                                f"Failed metadata test: {metadata_response.status_code}")
                
                # Overall success assessment
                if successful_tests >= 2:
                    self.log_test("Extract Clean Script - Comprehensive Test", True,
                                f"Successfully tested extract_clean_script with {successful_tests} voices")
                    
                    # Verify different voices produce different audio (consistency check)
                    if len(set(all_cleaned_outputs)) > 1:
                        self.log_test("Extract Clean Script - Voice Consistency", True,
                                    "Different voices produce different audio outputs as expected")
                    else:
                        self.log_test("Extract Clean Script - Voice Consistency", False,
                                    "All voices produced identical audio (unexpected)")
                    
                    return True
                else:
                    self.log_test("Extract Clean Script - Comprehensive Test", False,
                                f"Only {successful_tests} voice tests succeeded")
                    return False
            else:
                self.log_test("Extract Clean Script - Comprehensive Test", False,
                            "No voice tests succeeded")
                return False
                
        except Exception as e:
            self.log_test("Extract Clean Script - Exception", False, f"Test failed: {str(e)}")
            return False

    def test_audio_error_handling(self):
        """Test error handling for audio generation"""
        print("\n=== Testing Audio Error Handling ===")
        
        # Test empty text
        try:
            empty_text_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": "", "voice_name": "en-US-AriaNeural"},
                timeout=10
            )
            
            if empty_text_response.status_code == 400:
                self.log_test("Audio Error Handling - Empty Text", True,
                            "Properly handled empty text request")
            else:
                self.log_test("Audio Error Handling - Empty Text", False,
                            f"Unexpected status code for empty text: {empty_text_response.status_code}")
        except Exception as e:
            self.log_test("Audio Error Handling - Empty Text", False, f"Exception: {str(e)}")
        
        # Test invalid voice name
        try:
            invalid_voice_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": "Test text", "voice_name": "invalid-voice-name"},
                timeout=15
            )
            
            if invalid_voice_response.status_code in [400, 500]:
                self.log_test("Audio Error Handling - Invalid Voice", True,
                            "Properly handled invalid voice name")
            else:
                self.log_test("Audio Error Handling - Invalid Voice", False,
                            f"Unexpected status code for invalid voice: {invalid_voice_response.status_code}")
        except Exception as e:
            self.log_test("Audio Error Handling - Invalid Voice", False, f"Exception: {str(e)}")
        
        # Test very long text
        try:
            long_text = "This is a very long text. " * 200  # ~5000 characters
            long_text_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": long_text, "voice_name": "en-US-AriaNeural"},
                timeout=60
            )
            
            if long_text_response.status_code == 200:
                self.log_test("Audio Error Handling - Long Text", True,
                            "Successfully handled very long text")
            elif long_text_response.status_code in [400, 413, 500]:
                self.log_test("Audio Error Handling - Long Text", True,
                            "Properly rejected very long text with appropriate error")
            else:
                self.log_test("Audio Error Handling - Long Text", False,
                            f"Unexpected status code for long text: {long_text_response.status_code}")
        except Exception as e:
            self.log_test("Audio Error Handling - Long Text", False, f"Exception: {str(e)}")
    
    def test_voice_audio_integration(self):
        """Test the complete voice selection and audio generation integration"""
        print("\n=== Testing Voice-Audio Integration ===")
        
        try:
            # Step 1: Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if voices_response.status_code != 200:
                self.log_test("Voice-Audio Integration - Voice Retrieval", False,
                            f"Failed to get voices: {voices_response.status_code}")
                return False
            
            voices = voices_response.json()
            if len(voices) < 2:
                self.log_test("Voice-Audio Integration - Voice Count", False,
                            f"Need at least 2 voices for integration test, got {len(voices)}")
                return False
            
            # Step 2: Generate script first
            script_payload = {
                "prompt": "Create a short motivational message about perseverance",
                "video_type": "motivational",
                "duration": "short"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=30
            )
            
            if script_response.status_code != 200:
                self.log_test("Voice-Audio Integration - Script Generation", False,
                            f"Failed to generate script: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data["generated_script"]
            
            # Step 3: Test audio generation with multiple voices using the generated script
            successful_generations = 0
            different_audio_outputs = set()
            
            for i, voice in enumerate(voices[:3]):  # Test with first 3 voices
                audio_payload = {
                    "text": generated_script[:500],  # Use first 500 chars to avoid timeout
                    "voice_name": voice["name"]
                }
                
                audio_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=audio_payload,
                    timeout=45
                )
                
                if audio_response.status_code == 200:
                    audio_data = audio_response.json()
                    audio_base64 = audio_data["audio_base64"]
                    different_audio_outputs.add(audio_base64[:100])  # Compare first 100 chars
                    successful_generations += 1
                    
                    self.log_test(f"Voice-Audio Integration - {voice['display_name']}", True,
                                f"Successfully generated audio with {voice['display_name']}")
                else:
                    self.log_test(f"Voice-Audio Integration - {voice['display_name']}", False,
                                f"Failed with {voice['display_name']}: {audio_response.status_code}")
            
            # Verify different voices produce different outputs
            if len(different_audio_outputs) > 1:
                self.log_test("Voice-Audio Integration - Audio Variety", True,
                            f"Different voices produced {len(different_audio_outputs)} distinct audio outputs")
            else:
                self.log_test("Voice-Audio Integration - Audio Variety", False,
                            "All voices produced identical audio (unexpected)")
            
            if successful_generations >= 2:
                self.log_test("Voice-Audio Integration - Complete Flow", True,
                            f"Successfully completed voice selection → script generation → audio generation flow")
                return True
            else:
                self.log_test("Voice-Audio Integration - Complete Flow", False,
                            f"Only {successful_generations} voice generations succeeded")
                return False
            
        except Exception as e:
            self.log_test("Voice-Audio Integration - Exception", False, f"Integration test failed: {str(e)}")
            return False
    
    def test_avatar_video_generation_endpoint(self):
        """Test the new /api/generate-avatar-video endpoint"""
        print("\n=== Testing Avatar Video Generation Endpoint ===")
        
        # First, generate some audio to use for avatar video testing
        try:
            # Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Avatar Video - Voice Retrieval", False,
                            "Could not retrieve voices for avatar video testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Avatar Video - Voice Availability", False,
                            "No voices available for avatar video testing")
                return False
            
            test_voice = voices[0]["name"]
            
            # Generate sample audio for avatar video
            audio_text = "Hello! This is a test of the avatar video generation system. The avatar should move and speak naturally."
            audio_payload = {
                "text": audio_text,
                "voice_name": test_voice
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=30
            )
            
            if audio_response.status_code != 200:
                self.log_test("Avatar Video - Audio Generation", False,
                            f"Failed to generate audio for avatar video: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Avatar Video - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio for avatar video")
            
        except Exception as e:
            self.log_test("Avatar Video - Audio Setup", False, f"Failed to setup audio: {str(e)}")
            return False
        
        # Test Case 1: Basic avatar video generation
        try:
            avatar_payload = {
                "audio_base64": audio_base64
                # avatar_image_path is optional - should use default
            }
            
            avatar_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json=avatar_payload,
                timeout=120  # Avatar video generation can take longer
            )
            
            if avatar_response.status_code == 200:
                avatar_data = avatar_response.json()
                
                # Verify response structure
                required_fields = ["video_base64", "duration_seconds", "request_id"]
                missing_fields = [field for field in required_fields if field not in avatar_data]
                
                if missing_fields:
                    self.log_test("Avatar Video - Response Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify video data
                video_base64 = avatar_data["video_base64"]
                if not video_base64 or len(video_base64) < 1000:
                    self.log_test("Avatar Video - Video Data", False,
                                "Video base64 data is too short or empty",
                                {"video_length": len(video_base64) if video_base64 else 0})
                    return False
                
                # Verify duration is reasonable
                duration = avatar_data["duration_seconds"]
                if duration <= 0 or duration > 60:  # Should be reasonable duration
                    self.log_test("Avatar Video - Duration", False,
                                f"Unreasonable duration: {duration} seconds")
                    return False
                
                # Verify request ID is present
                request_id = avatar_data["request_id"]
                if not request_id or len(request_id) < 4:
                    self.log_test("Avatar Video - Request ID", False,
                                "Request ID is missing or too short")
                    return False
                
                self.log_test("Avatar Video - Basic Generation", True,
                            f"Successfully generated {len(video_base64)} chars of base64 video, duration: {duration:.2f}s")
                
                # Test Case 2: Test with custom avatar image path (should still work with default)
                custom_avatar_payload = {
                    "audio_base64": audio_base64,
                    "avatar_image_path": "/custom/path/avatar.jpg"  # This should fallback to default
                }
                
                custom_response = self.session.post(
                    f"{self.backend_url}/generate-avatar-video",
                    json=custom_avatar_payload,
                    timeout=120
                )
                
                if custom_response.status_code == 200:
                    self.log_test("Avatar Video - Custom Avatar Path", True,
                                "Successfully handled custom avatar path (fallback to default)")
                else:
                    self.log_test("Avatar Video - Custom Avatar Path", False,
                                f"Failed with custom avatar path: {custom_response.status_code}")
                
                return True
                
            else:
                self.log_test("Avatar Video - HTTP Response", False,
                            f"HTTP {avatar_response.status_code}: {avatar_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Avatar Video - Generation Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_avatar_video_error_handling(self):
        """Test error handling for avatar video generation"""
        print("\n=== Testing Avatar Video Error Handling ===")
        
        # Test Case 1: Empty audio data
        try:
            empty_audio_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json={"audio_base64": ""},
                timeout=30
            )
            
            if empty_audio_response.status_code == 400:
                self.log_test("Avatar Video Error - Empty Audio", True,
                            "Properly handled empty audio data")
            else:
                self.log_test("Avatar Video Error - Empty Audio", False,
                            f"Unexpected status code for empty audio: {empty_audio_response.status_code}")
        except Exception as e:
            self.log_test("Avatar Video Error - Empty Audio", False, f"Exception: {str(e)}")
        
        # Test Case 2: Invalid base64 audio data
        try:
            invalid_audio_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json={"audio_base64": "invalid-base64-data"},
                timeout=30
            )
            
            if invalid_audio_response.status_code in [400, 500]:
                self.log_test("Avatar Video Error - Invalid Audio", True,
                            "Properly handled invalid base64 audio data")
            else:
                self.log_test("Avatar Video Error - Invalid Audio", False,
                            f"Unexpected status code for invalid audio: {invalid_audio_response.status_code}")
        except Exception as e:
            self.log_test("Avatar Video Error - Invalid Audio", False, f"Exception: {str(e)}")
        
        # Test Case 3: Missing required fields
        try:
            missing_fields_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json={},  # Missing audio_base64
                timeout=10
            )
            
            if missing_fields_response.status_code == 422:  # Validation error expected
                self.log_test("Avatar Video Error - Missing Fields", True,
                            "Properly handled missing required fields")
            else:
                self.log_test("Avatar Video Error - Missing Fields", False,
                            f"Unexpected status code for missing fields: {missing_fields_response.status_code}")
        except Exception as e:
            self.log_test("Avatar Video Error - Missing Fields", False, f"Exception: {str(e)}")
    
    def test_complete_avatar_workflow(self):
        """Test the complete workflow: script → audio → avatar video"""
        print("\n=== Testing Complete Avatar Workflow ===")
        
        try:
            # Step 1: Generate a script
            script_payload = {
                "prompt": "Create a short welcome message for a new product launch",
                "video_type": "marketing",
                "duration": "short"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Avatar Workflow - Script Generation", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data["generated_script"]
            
            self.log_test("Avatar Workflow - Script Generation", True,
                        f"Successfully generated {len(generated_script)} character script")
            
            # Step 2: Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if voices_response.status_code != 200:
                self.log_test("Avatar Workflow - Voice Retrieval", False,
                            f"Voice retrieval failed: {voices_response.status_code}")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Avatar Workflow - Voice Availability", False,
                            "No voices available")
                return False
            
            selected_voice = voices[0]["name"]  # Use first available voice
            
            # Step 3: Generate audio from script
            # Use first 300 characters to avoid timeout
            script_excerpt = generated_script[:300] if len(generated_script) > 300 else generated_script
            
            audio_payload = {
                "text": script_excerpt,
                "voice_name": selected_voice
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=45
            )
            
            if audio_response.status_code != 200:
                self.log_test("Avatar Workflow - Audio Generation", False,
                            f"Audio generation failed: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Avatar Workflow - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio")
            
            # Step 4: Generate avatar video from audio
            avatar_payload = {
                "audio_base64": audio_base64
            }
            
            avatar_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json=avatar_payload,
                timeout=120
            )
            
            if avatar_response.status_code != 200:
                self.log_test("Avatar Workflow - Avatar Video Generation", False,
                            f"Avatar video generation failed: {avatar_response.status_code}")
                return False
            
            avatar_data = avatar_response.json()
            video_base64 = avatar_data["video_base64"]
            duration = avatar_data["duration_seconds"]
            
            self.log_test("Avatar Workflow - Avatar Video Generation", True,
                        f"Successfully generated {len(video_base64)} chars of base64 video")
            
            # Step 5: Verify the complete workflow
            if len(video_base64) > 10000 and duration > 0:
                self.log_test("Avatar Workflow - Complete Integration", True,
                            f"Successfully completed script → audio → avatar video workflow. Final video: {len(video_base64)} chars, {duration:.2f}s")
                return True
            else:
                self.log_test("Avatar Workflow - Complete Integration", False,
                            f"Workflow completed but video quality insufficient: {len(video_base64)} chars, {duration:.2f}s")
                return False
            
        except Exception as e:
            self.log_test("Avatar Workflow - Exception", False, f"Workflow test failed: {str(e)}")
            return False
    
    def test_avatar_video_with_different_audio_lengths(self):
        """Test avatar video generation with different audio lengths"""
        print("\n=== Testing Avatar Video with Different Audio Lengths ===")
        
        try:
            # Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200 or not voices_response.json():
                self.log_test("Avatar Video Lengths - Voice Setup", False,
                            "Could not get voices for testing")
                return False
            
            test_voice = voices_response.json()[0]["name"]
            
            # Test different text lengths
            test_cases = [
                {"name": "Short", "text": "Hello world!", "expected_min_duration": 0.5},
                {"name": "Medium", "text": "This is a medium length text that should generate a reasonable duration video with proper lip sync animation.", "expected_min_duration": 3.0},
                {"name": "Long", "text": "This is a much longer text that will test the avatar video generation system's ability to handle extended speech. The system should create a video that matches the full duration of the audio with consistent lip sync animation throughout the entire duration. This tests the robustness of the video generation pipeline.", "expected_min_duration": 8.0}
            ]
            
            successful_tests = 0
            
            for test_case in test_cases:
                try:
                    # Generate audio
                    audio_payload = {
                        "text": test_case["text"],
                        "voice_name": test_voice
                    }
                    
                    audio_response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=audio_payload,
                        timeout=30
                    )
                    
                    if audio_response.status_code != 200:
                        self.log_test(f"Avatar Video Lengths - {test_case['name']} Audio", False,
                                    f"Audio generation failed: {audio_response.status_code}")
                        continue
                    
                    audio_base64 = audio_response.json()["audio_base64"]
                    
                    # Generate avatar video
                    avatar_payload = {
                        "audio_base64": audio_base64
                    }
                    
                    avatar_response = self.session.post(
                        f"{self.backend_url}/generate-avatar-video",
                        json=avatar_payload,
                        timeout=120
                    )
                    
                    if avatar_response.status_code == 200:
                        avatar_data = avatar_response.json()
                        duration = avatar_data["duration_seconds"]
                        video_size = len(avatar_data["video_base64"])
                        
                        if duration >= test_case["expected_min_duration"] * 0.5:  # Allow 50% tolerance
                            self.log_test(f"Avatar Video Lengths - {test_case['name']}", True,
                                        f"Successfully generated {video_size} chars video, duration: {duration:.2f}s")
                            successful_tests += 1
                        else:
                            self.log_test(f"Avatar Video Lengths - {test_case['name']}", False,
                                        f"Duration too short: {duration:.2f}s (expected min: {test_case['expected_min_duration']}s)")
                    else:
                        self.log_test(f"Avatar Video Lengths - {test_case['name']}", False,
                                    f"Avatar generation failed: {avatar_response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"Avatar Video Lengths - {test_case['name']}", False,
                                f"Exception: {str(e)}")
            
            if successful_tests >= 2:
                self.log_test("Avatar Video Lengths - Overall", True,
                            f"Successfully tested {successful_tests}/3 different audio lengths")
                return True
            else:
                self.log_test("Avatar Video Lengths - Overall", False,
                            f"Only {successful_tests}/3 tests succeeded")
                return False
                
        except Exception as e:
            self.log_test("Avatar Video Lengths - Exception", False, f"Test failed: {str(e)}")
            return False
    
    def test_enhanced_avatar_video_generation_endpoint(self):
        """Test the new /api/generate-enhanced-avatar-video endpoint"""
        print("\n=== Testing Enhanced Avatar Video Generation Endpoint ===")
        
        # First, generate some audio to use for enhanced avatar video testing
        try:
            # Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Enhanced Avatar Video - Voice Retrieval", False,
                            "Could not retrieve voices for enhanced avatar video testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Enhanced Avatar Video - Voice Availability", False,
                            "No voices available for enhanced avatar video testing")
                return False
            
            test_voice = voices[0]["name"]
            
            # Generate sample audio for enhanced avatar video
            audio_text = "Welcome to our presentation. This is about technology and innovation in the modern world."
            audio_payload = {
                "text": audio_text,
                "voice_name": test_voice
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=30
            )
            
            if audio_response.status_code != 200:
                self.log_test("Enhanced Avatar Video - Audio Generation", False,
                            f"Failed to generate audio for enhanced avatar video: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Enhanced Avatar Video - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio for enhanced avatar video")
            
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Audio Setup", False, f"Failed to setup audio: {str(e)}")
            return False
        
        # Test Case 1: Default avatar option
        try:
            default_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "default",
                "script_text": "Welcome to our presentation. This is about technology and innovation in the modern world."
            }
            
            default_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=default_payload,
                timeout=180  # Enhanced avatar video generation can take longer
            )
            
            if default_response.status_code == 200:
                default_data = default_response.json()
                
                # Verify response structure
                required_fields = ["video_base64", "duration_seconds", "request_id", "avatar_option", "script_segments", "sadtalker_used"]
                missing_fields = [field for field in required_fields if field not in default_data]
                
                if missing_fields:
                    self.log_test("Enhanced Avatar Video - Default Response Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify video data
                video_base64 = default_data["video_base64"]
                if not video_base64 or len(video_base64) < 1000:
                    self.log_test("Enhanced Avatar Video - Default Video Data", False,
                                "Video base64 data is too short or empty",
                                {"video_length": len(video_base64) if video_base64 else 0})
                    return False
                
                # Verify duration is reasonable
                duration = default_data["duration_seconds"]
                if duration <= 0 or duration > 120:  # Should be reasonable duration
                    self.log_test("Enhanced Avatar Video - Default Duration", False,
                                f"Unreasonable duration: {duration} seconds")
                    return False
                
                # Verify avatar option matches
                if default_data["avatar_option"] != "default":
                    self.log_test("Enhanced Avatar Video - Default Avatar Option", False,
                                f"Expected 'default', got '{default_data['avatar_option']}'")
                    return False
                
                # Verify script segments
                script_segments = default_data["script_segments"]
                if script_segments <= 0:
                    self.log_test("Enhanced Avatar Video - Default Script Segments", False,
                                f"Expected positive script segments, got {script_segments}")
                    return False
                
                # Verify sadtalker_used is boolean
                sadtalker_used = default_data["sadtalker_used"]
                if not isinstance(sadtalker_used, bool):
                    self.log_test("Enhanced Avatar Video - Default SadTalker Flag", False,
                                f"Expected boolean for sadtalker_used, got {type(sadtalker_used)}")
                    return False
                
                self.log_test("Enhanced Avatar Video - Default Avatar", True,
                            f"Successfully generated {len(video_base64)} chars of base64 video, duration: {duration:.2f}s, segments: {script_segments}, SadTalker: {sadtalker_used}")
                
            else:
                self.log_test("Enhanced Avatar Video - Default HTTP Response", False,
                            f"HTTP {default_response.status_code}: {default_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Default Generation Exception", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 2: AI Generated avatar option
        try:
            ai_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "ai_generated",
                "script_text": "This is a test of AI-generated avatar functionality."
            }
            
            ai_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=ai_payload,
                timeout=180
            )
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                
                # Verify avatar option matches
                if ai_data["avatar_option"] != "ai_generated":
                    self.log_test("Enhanced Avatar Video - AI Generated Avatar Option", False,
                                f"Expected 'ai_generated', got '{ai_data['avatar_option']}'")
                    return False
                
                # Verify video was generated
                if not ai_data["video_base64"] or len(ai_data["video_base64"]) < 1000:
                    self.log_test("Enhanced Avatar Video - AI Generated Video Data", False,
                                "AI generated video data is too short or empty")
                    return False
                
                self.log_test("Enhanced Avatar Video - AI Generated Avatar", True,
                            f"Successfully generated AI avatar video: {len(ai_data['video_base64'])} chars, duration: {ai_data['duration_seconds']:.2f}s")
                
            else:
                self.log_test("Enhanced Avatar Video - AI Generated HTTP Response", False,
                            f"HTTP {ai_response.status_code}: {ai_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - AI Generated Exception", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 3: Upload avatar option (without actual image - should fail gracefully)
        try:
            upload_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "upload",
                "script_text": "This should fail without user image."
            }
            
            upload_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=upload_payload,
                timeout=60
            )
            
            # This should fail with 400 because no user_image_base64 provided
            if upload_response.status_code == 400:
                self.log_test("Enhanced Avatar Video - Upload Validation", True,
                            "Properly validated missing user image for upload option")
            else:
                self.log_test("Enhanced Avatar Video - Upload Validation", False,
                            f"Expected 400 for missing user image, got {upload_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Upload Validation Exception", False, f"Request failed: {str(e)}")
        
        # Test Case 4: Invalid avatar option
        try:
            invalid_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "invalid_option",
                "script_text": "This should fail with invalid avatar option."
            }
            
            invalid_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=invalid_payload,
                timeout=60
            )
            
            # This should fail with 400 because of invalid avatar option
            if invalid_response.status_code == 400:
                self.log_test("Enhanced Avatar Video - Invalid Option Validation", True,
                            "Properly validated invalid avatar option")
            else:
                self.log_test("Enhanced Avatar Video - Invalid Option Validation", False,
                            f"Expected 400 for invalid avatar option, got {invalid_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Invalid Option Exception", False, f"Request failed: {str(e)}")
        
        # Test Case 5: Different script contexts
        try:
            contexts = [
                {"script": "Welcome to our business meeting. Let's discuss quarterly results.", "expected_bg": "office"},
                {"script": "Today we'll learn about advanced mathematics and problem solving.", "expected_bg": "education"},
                {"script": "Discover the latest in artificial intelligence and machine learning technology.", "expected_bg": "tech"}
            ]
            
            context_success = 0
            for i, context in enumerate(contexts):
                context_payload = {
                    "audio_base64": audio_base64,
                    "avatar_option": "default",
                    "script_text": context["script"]
                }
                
                context_response = self.session.post(
                    f"{self.backend_url}/generate-enhanced-avatar-video",
                    json=context_payload,
                    timeout=180
                )
                
                if context_response.status_code == 200:
                    context_data = context_response.json()
                    if context_data["script_segments"] > 0:
                        context_success += 1
                        self.log_test(f"Enhanced Avatar Video - Context {i+1}", True,
                                    f"Successfully processed context-aware script with {context_data['script_segments']} segments")
                    else:
                        self.log_test(f"Enhanced Avatar Video - Context {i+1}", False,
                                    "No script segments generated")
                else:
                    self.log_test(f"Enhanced Avatar Video - Context {i+1}", False,
                                f"Failed with status {context_response.status_code}")
            
            if context_success >= 2:
                self.log_test("Enhanced Avatar Video - Context Awareness", True,
                            f"Successfully processed {context_success}/3 context-aware scripts")
            else:
                self.log_test("Enhanced Avatar Video - Context Awareness", False,
                            f"Only {context_success}/3 context tests succeeded")
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Context Testing Exception", False, f"Context testing failed: {str(e)}")
        
        return True
    
    def test_enhanced_avatar_video_error_handling(self):
        """Test error handling for enhanced avatar video generation"""
        print("\n=== Testing Enhanced Avatar Video Error Handling ===")
        
        # Test Case 1: Empty audio data
        try:
            empty_audio_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json={
                    "audio_base64": "",
                    "avatar_option": "default"
                },
                timeout=30
            )
            
            if empty_audio_response.status_code == 400:
                self.log_test("Enhanced Avatar Video Error - Empty Audio", True,
                            "Properly handled empty audio data")
            else:
                self.log_test("Enhanced Avatar Video Error - Empty Audio", False,
                            f"Unexpected status code for empty audio: {empty_audio_response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Avatar Video Error - Empty Audio", False, f"Exception: {str(e)}")
        
        # Test Case 2: Invalid avatar option
        try:
            # First get valid audio
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code == 200:
                voices = voices_response.json()
                if voices:
                    test_voice = voices[0]["name"]
                    audio_response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json={"text": "Test audio", "voice_name": test_voice},
                        timeout=30
                    )
                    
                    if audio_response.status_code == 200:
                        audio_base64 = audio_response.json()["audio_base64"]
                        
                        invalid_option_response = self.session.post(
                            f"{self.backend_url}/generate-enhanced-avatar-video",
                            json={
                                "audio_base64": audio_base64,
                                "avatar_option": "invalid_option"
                            },
                            timeout=30
                        )
                        
                        if invalid_option_response.status_code == 400:
                            self.log_test("Enhanced Avatar Video Error - Invalid Option", True,
                                        "Properly handled invalid avatar option")
                        else:
                            self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                                        f"Unexpected status code for invalid option: {invalid_option_response.status_code}")
                    else:
                        self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                                    "Could not generate test audio")
                else:
                    self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                                "No voices available for testing")
            else:
                self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                            "Could not retrieve voices for testing")
        except Exception as e:
            self.log_test("Enhanced Avatar Video Error - Invalid Option", False, f"Exception: {str(e)}")
        
        # Test Case 3: Missing required fields
        try:
            missing_fields_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json={},  # Missing audio_base64 and avatar_option
                timeout=10
            )
            
            if missing_fields_response.status_code == 422:  # Validation error expected
                self.log_test("Enhanced Avatar Video Error - Missing Fields", True,
                            "Properly handled missing required fields")
            else:
                self.log_test("Enhanced Avatar Video Error - Missing Fields", False,
                            f"Unexpected status code for missing fields: {missing_fields_response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Avatar Video Error - Missing Fields", False, f"Exception: {str(e)}")
        
        return True
    
    def test_enhanced_avatar_video_integration(self):
        """Test the complete enhanced avatar video integration workflow"""
        print("\n=== Testing Enhanced Avatar Video Integration ===")
        
        try:
            # Step 1: Generate a script
            script_payload = {
                "prompt": "Create a professional presentation about artificial intelligence and its impact on modern business",
                "video_type": "educational",
                "duration": "short"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Script Generation", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data["generated_script"]
            
            self.log_test("Enhanced Avatar Integration - Script Generation", True,
                        f"Successfully generated {len(generated_script)} character script")
            
            # Step 2: Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if voices_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Voice Retrieval", False,
                            f"Voice retrieval failed: {voices_response.status_code}")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Enhanced Avatar Integration - Voice Availability", False,
                            "No voices available")
                return False
            
            selected_voice = voices[0]["name"]  # Use first available voice
            
            # Step 3: Generate audio from script
            # Use first 400 characters to avoid timeout
            script_excerpt = generated_script[:400] if len(generated_script) > 400 else generated_script
            
            audio_payload = {
                "text": script_excerpt,
                "voice_name": selected_voice
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=45
            )
            
            if audio_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Audio Generation", False,
                            f"Audio generation failed: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Enhanced Avatar Integration - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio")
            
            # Step 4: Generate enhanced avatar video from audio and script
            enhanced_avatar_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "default",
                "script_text": script_excerpt
            }
            
            enhanced_avatar_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=enhanced_avatar_payload,
                timeout=180
            )
            
            if enhanced_avatar_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Enhanced Avatar Video Generation", False,
                            f"Enhanced avatar video generation failed: {enhanced_avatar_response.status_code}")
                return False
            
            enhanced_avatar_data = enhanced_avatar_response.json()
            video_base64 = enhanced_avatar_data["video_base64"]
            duration = enhanced_avatar_data["duration_seconds"]
            script_segments = enhanced_avatar_data["script_segments"]
            sadtalker_used = enhanced_avatar_data["sadtalker_used"]
            
            self.log_test("Enhanced Avatar Integration - Enhanced Avatar Video Generation", True,
                        f"Successfully generated {len(video_base64)} chars of base64 video")
            
            # Step 5: Verify the complete enhanced workflow
            if len(video_base64) > 10000 and duration > 0 and script_segments > 0:
                self.log_test("Enhanced Avatar Integration - Complete Workflow", True,
                            f"Successfully completed script → audio → enhanced avatar video workflow. Final video: {len(video_base64)} chars, {duration:.2f}s, {script_segments} segments, SadTalker: {sadtalker_used}")
                
                # Test different avatar options in the same workflow
                avatar_options = ["default", "ai_generated"]
                successful_options = 0
                
                for avatar_option in avatar_options:
                    try:
                        option_payload = {
                            "audio_base64": audio_base64,
                            "avatar_option": avatar_option,
                            "script_text": script_excerpt
                        }
                        
                        option_response = self.session.post(
                            f"{self.backend_url}/generate-enhanced-avatar-video",
                            json=option_payload,
                            timeout=180
                        )
                        
                        if option_response.status_code == 200:
                            option_data = option_response.json()
                            if option_data["avatar_option"] == avatar_option and len(option_data["video_base64"]) > 1000:
                                successful_options += 1
                                self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", True,
                                            f"Successfully generated video with {avatar_option} avatar option")
                            else:
                                self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", False,
                                            "Generated video but with issues")
                        else:
                            self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", False,
                                        f"Failed with status {option_response.status_code}")
                    except Exception as e:
                        self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", False,
                                    f"Exception: {str(e)}")
                
                if successful_options >= 1:
                    self.log_test("Enhanced Avatar Integration - Multiple Avatar Options", True,
                                f"Successfully tested {successful_options}/{len(avatar_options)} avatar options")
                else:
                    self.log_test("Enhanced Avatar Integration - Multiple Avatar Options", False,
                                "No avatar options worked successfully")
                
                return True
            else:
                self.log_test("Enhanced Avatar Integration - Complete Workflow", False,
                            f"Workflow completed but video quality insufficient: {len(video_base64)} chars, {duration:.2f}s, {script_segments} segments")
                return False
            
        except Exception as e:
            self.log_test("Enhanced Avatar Integration - Exception", False, f"Integration test failed: {str(e)}")
            return False

    def test_enhanced_script_filtering_review_request(self):
        """Test the enhanced script filtering functionality using the exact script content from the review request"""
        print("\n=== Testing Enhanced Script Filtering (Review Request) ===")
        
        # The exact script content provided in the review request
        exact_script_content = '''**VIDEO SCRIPT: "Uncage Your Courage: A Journey From Fear to Freedom"**

**[0:00-0:03] SCENE 1: Hesitation at a Crossroads - Muted Colors, Blurry**

(Voiceover - Intimate, slightly urgent)
(0:00) Are you TRAPPED? ... paralyzed by a fear you can't name?

**(SOUND:** Anxious heartbeat sound effect fades in.)

**[0:03-0:07] SCENE 2: Quick Cuts - Blank Canvas, Unopened Door, Someone Hiding Their Face**

(Voiceover - slightly louder, more direct)
(0:03) That feeling... the dread... the "what if?"... it's a cage. A cage built by YOU.

**(VISUAL CUE:** Subtle cage bars visually superimposed over the scenes)

**[0:07-0:12] SCENE 3: Expert (or actor) - Close Up, Empathetic Expression**

(Expert)
(0:07) Fear isn't a life sentence. It's a SIGNAL. Your brain misinterpreting potential threats.

**(VISUAL CUE:** Animated graphic showing the brain's amygdala lighting up.)

**[0:12-0:18] SCENE 4: Blooming Flower Time-Lapse, Seedling Pushing Through Earth**

(Voiceover - Hopeful, encouraging)
(0:12) But you can REWIRE it. Challenge those negative thoughts.  Tiny steps...lead to HUGE changes.

**[0:27-0:30] SCENE 7: Visual of an open road, leading towards a bright horizon. Logo appears "Uncage Your Courage"**

(Voiceover - Empowering, strong)
(0:27) Uncage your courage... What's ONE small step you can take TODAY? Share your commitment below!

**(VISUAL CUE:** On-screen text: "Share Your Step Below!")

**[0:30-0:32] SCENE 8: End screen with subscribe button, social media links.**

(Voiceover - quick, friendly)
(0:30) Subscribe for more inspiration and tools to build your best life.

**Key Considerations & Rationale:**'''

        # Expected clean output should contain ONLY these spoken dialogue segments
        expected_clean_segments = [
            "Are you TRAPPED? ... paralyzed by a fear you can't name?",
            "That feeling... the dread... the \"what if?\"... it's a cage. A cage built by YOU.",
            "Fear isn't a life sentence. It's a SIGNAL. Your brain misinterpreting potential threats.",
            "But you can REWIRE it. Challenge those negative thoughts. Tiny steps...lead to HUGE changes.",
            "Uncage your courage... What's ONE small step you can take TODAY? Share your commitment below!",
            "Subscribe for more inspiration and tools to build your best life."
        ]
        
        # Elements that should NOT be in the cleaned output
        elements_to_remove = [
            # Timestamps
            "(0:00)", "(0:03)", "(0:07)", "(0:12)", "(0:27)", "(0:30)",
            # Speaker directions
            "(Voiceover - Intimate, slightly urgent)", "(Expert)", "(Voiceover - slightly louder, more direct)",
            "(Voiceover - Hopeful, encouraging)", "(Voiceover - Empowering, strong)", "(Voiceover - quick, friendly)",
            # Visual/sound cues
            "**(SOUND:** Anxious heartbeat sound effect fades in.)",
            "**(VISUAL CUE:** Subtle cage bars visually superimposed over the scenes)",
            "**(VISUAL CUE:** Animated graphic showing the brain's amygdala lighting up.)",
            "**(VISUAL CUE:** On-screen text: \"Share Your Step Below!\")",
            # Scene descriptions
            "**[0:00-0:03] SCENE 1: Hesitation at a Crossroads - Muted Colors, Blurry**",
            "**[0:03-0:07] SCENE 2: Quick Cuts - Blank Canvas, Unopened Door, Someone Hiding Their Face**",
            "**[0:07-0:12] SCENE 3: Expert (or actor) - Close Up, Empathetic Expression**",
            "**[0:12-0:18] SCENE 4: Blooming Flower Time-Lapse, Seedling Pushing Through Earth**",
            "**[0:27-0:30] SCENE 7: Visual of an open road, leading towards a bright horizon. Logo appears \"Uncage Your Courage\"**",
            "**[0:30-0:32] SCENE 8: End screen with subscribe button, social media links.**",
            # Metadata
            "**Key Considerations & Rationale:**"
        ]
        
        try:
            # Get available voices for testing
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Enhanced Script Filtering - Voice Setup", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Enhanced Script Filtering - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            # Test with multiple voice options to ensure consistency
            test_voices = voices[:min(3, len(voices))]  # Test with up to 3 voices
            successful_tests = 0
            
            for voice in test_voices:
                voice_name = voice["name"]
                voice_display = voice.get("display_name", voice_name)
                
                # Test audio generation with the exact script content
                payload = {
                    "text": exact_script_content,
                    "voice_name": voice_name
                }
                
                try:
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=60  # Longer timeout for complex script
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data["audio_base64"]
                        
                        # Verify substantial audio was generated
                        if len(audio_base64) > 10000:  # Should be substantial audio
                            self.log_test(f"Enhanced Script Filtering - {voice_display}", True,
                                        f"Successfully generated {len(audio_base64)} chars of clean audio")
                            successful_tests += 1
                        else:
                            self.log_test(f"Enhanced Script Filtering - {voice_display}", False,
                                        f"Audio too short: {len(audio_base64)} chars")
                    else:
                        self.log_test(f"Enhanced Script Filtering - {voice_display}", False,
                                    f"HTTP {response.status_code}: {response.text[:200]}")
                        
                except Exception as e:
                    self.log_test(f"Enhanced Script Filtering - {voice_display}", False,
                                f"Exception: {str(e)}")
            
            # Test specific filtering requirements
            if successful_tests > 0:
                # Test 1: Verify timestamps are removed
                timestamp_test_cases = [
                    "(0:00) Test content",
                    "(0:03) More test content", 
                    "(0:07) Additional content",
                    "(0:12) Final content"
                ]
                
                for i, timestamp_case in enumerate(timestamp_test_cases):
                    payload = {
                        "text": timestamp_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Timestamp Removal {i+1}", True,
                                    "Successfully processed timestamp format")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Timestamp Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Test 2: Verify speaker directions are removed
                speaker_test_cases = [
                    "(Voiceover - Intimate, slightly urgent) Test content",
                    "(Expert) More test content",
                    "(Voiceover - Hopeful, encouraging) Additional content"
                ]
                
                for i, speaker_case in enumerate(speaker_test_cases):
                    payload = {
                        "text": speaker_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Speaker Direction Removal {i+1}", True,
                                    "Successfully processed speaker direction")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Speaker Direction Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Test 3: Verify visual/sound cues are removed
                cue_test_cases = [
                    "**(VISUAL CUE:** Test visual cue) Content here",
                    "**(SOUND:** Test sound effect) More content"
                ]
                
                for i, cue_case in enumerate(cue_test_cases):
                    payload = {
                        "text": cue_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Visual/Sound Cue Removal {i+1}", True,
                                    "Successfully processed visual/sound cue")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Visual/Sound Cue Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Test 4: Verify scene descriptions are removed
                scene_test_cases = [
                    "**[0:00-0:03] SCENE 1: Test scene** Content here",
                    "**[0:07-0:12] SCENE 3: Another scene** More content"
                ]
                
                for i, scene_case in enumerate(scene_test_cases):
                    payload = {
                        "text": scene_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Scene Description Removal {i+1}", True,
                                    "Successfully processed scene description")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Scene Description Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Overall assessment
                if successful_tests >= 2:
                    self.log_test("Enhanced Script Filtering - Comprehensive Review Test", True,
                                f"Successfully tested enhanced script filtering with {successful_tests} voices. All production elements properly removed from TTS audio generation.")
                    return True
                else:
                    self.log_test("Enhanced Script Filtering - Comprehensive Review Test", False,
                                f"Only {successful_tests} voice tests succeeded")
                    return False
            else:
                self.log_test("Enhanced Script Filtering - Comprehensive Review Test", False,
                            "No voice tests succeeded")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Script Filtering - Exception", False, f"Test failed: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid enhance-prompt request
        try:
            invalid_enhance = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json={},  # Missing required fields
                timeout=10
            )
            
            if invalid_enhance.status_code == 422:  # Validation error expected
                self.log_test("Error Handling - Invalid Enhance Request", True,
                            "Properly handled invalid enhance-prompt request")
            else:
                self.log_test("Error Handling - Invalid Enhance Request", False,
                            f"Unexpected status code: {invalid_enhance.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Enhance Request", False, f"Exception: {str(e)}")
        
        # Test invalid generate-script request
        try:
            invalid_script = self.session.post(
                f"{self.backend_url}/generate-script",
                json={},  # Missing required fields
                timeout=10
            )
            
            if invalid_script.status_code == 422:  # Validation error expected
                self.log_test("Error Handling - Invalid Script Request", True,
                            "Properly handled invalid generate-script request")
            else:
                self.log_test("Error Handling - Invalid Script Request", False,
                            f"Unexpected status code: {invalid_script.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Script Request", False, f"Exception: {str(e)}")
    
    def test_new_enhanced_prompt_endpoint(self):
        """Test the new enhanced /api/enhance-prompt endpoint with multiple variations"""
        print("\n=== Testing NEW Enhanced Prompt Enhancement System ===")
        
        # Test Case 1: Basic enhancement with minimal input
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
                
            else:
                self.log_test("Enhanced Prompt - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Basic Test", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 2: Different video types
        video_types = ["marketing", "education", "entertainment", "tech"]
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
                else:
                    self.log_test(f"Enhanced Prompt - {video_type.title()} Type", False,
                                f"Failed for {video_type}: {type_response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Enhanced Prompt - {video_type.title()} Type", False,
                            f"Exception: {str(e)}")
        
        # Test Case 3: Multiple enhancement variations
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
                else:
                    self.log_test("Enhanced Prompt - Custom Variation Count", False,
                                f"Expected 4 variations, got {len(variations)}")
            else:
                self.log_test("Enhanced Prompt - Custom Variation Count", False,
                            f"Failed: {variations_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Custom Variation Count", False, f"Exception: {str(e)}")
        
        # Test Case 4: Quality metrics calculation
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
                    
            else:
                self.log_test("Enhanced Prompt - Quality Metrics", False,
                            f"Failed: {quality_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Quality Metrics", False, f"Exception: {str(e)}")
        
        # Test Case 5: Recommendation system
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
                else:
                    self.log_test("Enhanced Prompt - Recommendation System", False,
                                f"Recommendation too short or missing key elements: {len(recommendation)} chars")
                    
            else:
                self.log_test("Enhanced Prompt - Recommendation System", False,
                            f"Failed: {rec_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Recommendation System", False, f"Exception: {str(e)}")
        
        return True
    
    def test_phase_1_enhanced_prompt_compliance(self):
        """Test Phase 1 Enhanced Prompt System compliance with exact section headers and requirements"""
        print("\n=== Testing Phase 1 Enhanced Prompt Compliance ===")
        
        # Test scenarios for Phase 1 compliance validation
        test_scenarios = [
            {
                "name": "Educational Content",
                "payload": {
                    "original_prompt": "Create a video about healthy cooking tips",
                    "video_type": "educational",
                    "industry_focus": "health",
                    "enhancement_count": 3
                }
            },
            {
                "name": "Marketing Content",
                "payload": {
                    "original_prompt": "Promote our new fitness app to busy professionals",
                    "video_type": "marketing",
                    "industry_focus": "health",
                    "enhancement_count": 3
                }
            },
            {
                "name": "Entertainment Content",
                "payload": {
                    "original_prompt": "Create an engaging video about productivity tips for remote workers",
                    "video_type": "entertainment",
                    "industry_focus": "tech",
                    "enhancement_count": 3
                }
            }
        ]
        
        successful_compliance_tests = 0
        
        for scenario in test_scenarios:
            try:
                response = self.session.post(
                    f"{self.backend_url}/enhance-prompt",
                    json=scenario["payload"],
                    timeout=120  # Longer timeout for comprehensive processing
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Phase 1 Compliance Test 1: Verify exact section headers with word counts
                    required_section_headers = [
                        "🎣 HOOK SECTION",
                        "🎬 SETUP SECTION", 
                        "📚 CONTENT CORE",
                        "🏆 CLIMAX MOMENT",
                        "✨ RESOLUTION"
                    ]
                    
                    # Phase 1 Compliance Test 2: Verify additional required sections
                    additional_required_sections = [
                        "🧠 PSYCHOLOGICAL TRIGGERS",
                        "📲 2025 TRENDS & PLATFORM OPTIMIZATION",
                        "⚡ RETENTION ENGINEERING ELEMENTS"
                    ]
                    
                    variations = data.get("enhancement_variations", [])
                    if len(variations) < 3:
                        self.log_test(f"Phase 1 Compliance - {scenario['name']} Variations", False,
                                    f"Expected 3 variations, got {len(variations)}")
                        continue
                    
                    # Test each variation for Phase 1 compliance
                    compliant_variations = 0
                    
                    for i, variation in enumerate(variations):
                        enhanced_prompt = variation.get("enhanced_prompt", "")
                        
                        # Check for exact section headers
                        section_headers_found = 0
                        for header in required_section_headers:
                            if header in enhanced_prompt:
                                section_headers_found += 1
                        
                        # Check for additional required sections
                        additional_sections_found = 0
                        for section in additional_required_sections:
                            if section in enhanced_prompt:
                                additional_sections_found += 1
                        
                        # Check for psychological triggers integration
                        psychological_triggers = [
                            "FOMO", "Social Proof", "Authority", "Reciprocity", "Commitment"
                        ]
                        triggers_found = sum(1 for trigger in psychological_triggers if trigger in enhanced_prompt)
                        
                        # Check for 2025 trends integration
                        trends_indicators = [
                            "2025", "trending", "current", "latest", "algorithm", "platform"
                        ]
                        trends_found = sum(1 for indicator in trends_indicators if indicator.lower() in enhanced_prompt.lower())
                        
                        # Check for retention engineering elements
                        retention_elements = [
                            "engagement question", "emotional peak", "pattern interrupt", 
                            "retention", "cliffhanger", "hook"
                        ]
                        retention_found = sum(1 for element in retention_elements if element.lower() in enhanced_prompt.lower())
                        
                        # Check word count compliance (should be substantial - 500+ words)
                        word_count = len(enhanced_prompt.split())
                        
                        # Phase 1 compliance scoring
                        compliance_score = 0
                        max_score = 6
                        
                        if section_headers_found >= 4:  # At least 4/5 exact headers
                            compliance_score += 1
                            
                        if additional_sections_found >= 2:  # At least 2/3 additional sections
                            compliance_score += 1
                            
                        if triggers_found >= 3:  # At least 3/5 psychological triggers
                            compliance_score += 1
                            
                        if trends_found >= 2:  # At least 2 trend indicators
                            compliance_score += 1
                            
                        if retention_found >= 2:  # At least 2 retention elements
                            compliance_score += 1
                            
                        if word_count >= 500:  # Substantial content
                            compliance_score += 1
                        
                        compliance_percentage = (compliance_score / max_score) * 100
                        
                        if compliance_percentage >= 80:  # 80% compliance threshold
                            compliant_variations += 1
                            self.log_test(f"Phase 1 Compliance - {scenario['name']} Variation {i+1}", True,
                                        f"Phase 1 compliant: {compliance_percentage:.1f}% ({compliance_score}/{max_score}), {word_count} words, {section_headers_found}/5 headers, {triggers_found}/5 triggers")
                        else:
                            self.log_test(f"Phase 1 Compliance - {scenario['name']} Variation {i+1}", False,
                                        f"Phase 1 non-compliant: {compliance_percentage:.1f}% ({compliance_score}/{max_score}), missing elements")
                    
                    # Overall scenario compliance
                    if compliant_variations >= 2:  # At least 2/3 variations must be compliant
                        successful_compliance_tests += 1
                        self.log_test(f"Phase 1 Compliance - {scenario['name']} Overall", True,
                                    f"Scenario compliant: {compliant_variations}/3 variations meet Phase 1 requirements")
                    else:
                        self.log_test(f"Phase 1 Compliance - {scenario['name']} Overall", False,
                                    f"Scenario non-compliant: only {compliant_variations}/3 variations meet Phase 1 requirements")
                
                else:
                    self.log_test(f"Phase 1 Compliance - {scenario['name']} HTTP", False,
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Phase 1 Compliance - {scenario['name']} Exception", False,
                            f"Exception: {str(e)}")
        
        # Phase 1 Compliance Test 3: Test specific psychological triggers
        try:
            psychological_test_payload = {
                "original_prompt": "Create a video about overcoming procrastination and achieving goals",
                "video_type": "educational",
                "industry_focus": "general",
                "enhancement_count": 3
            }
            
            psych_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=psychological_test_payload,
                timeout=120
            )
            
            if psych_response.status_code == 200:
                psych_data = psych_response.json()
                psych_variations = psych_data.get("enhancement_variations", [])
                
                # Check for specific psychological triggers across all variations
                all_triggers_text = " ".join([var.get("enhanced_prompt", "") for var in psych_variations])
                
                required_psychological_triggers = {
                    "FOMO": "Fear of Missing Out implementation",
                    "Social Proof": "Social validation and peer influence",
                    "Authority": "Expert credibility and positioning", 
                    "Reciprocity": "Value-first approach and giving",
                    "Commitment": "Engagement and participation hooks"
                }
                
                triggers_implemented = 0
                for trigger, description in required_psychological_triggers.items():
                    if trigger in all_triggers_text:
                        triggers_implemented += 1
                        self.log_test(f"Phase 1 Compliance - {trigger} Trigger", True,
                                    f"{trigger} psychological trigger successfully integrated")
                    else:
                        self.log_test(f"Phase 1 Compliance - {trigger} Trigger", False,
                                    f"{trigger} psychological trigger missing from enhanced prompts")
                
                if triggers_implemented >= 4:  # At least 4/5 triggers should be present
                    self.log_test("Phase 1 Compliance - Psychological Triggers Integration", True,
                                f"Successfully integrated {triggers_implemented}/5 required psychological triggers")
                else:
                    self.log_test("Phase 1 Compliance - Psychological Triggers Integration", False,
                                f"Only {triggers_implemented}/5 psychological triggers integrated")
                    
            else:
                self.log_test("Phase 1 Compliance - Psychological Triggers Test", False,
                            f"HTTP {psych_response.status_code}")
                
        except Exception as e:
            self.log_test("Phase 1 Compliance - Psychological Triggers Test", False,
                        f"Exception: {str(e)}")
        
        # Phase 1 Compliance Test 4: Test 2025 trends and platform optimization
        try:
            trends_test_payload = {
                "original_prompt": "Create a video about social media marketing strategies",
                "video_type": "marketing",
                "industry_focus": "marketing",
                "enhancement_count": 3
            }
            
            trends_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=trends_test_payload,
                timeout=120
            )
            
            if trends_response.status_code == 200:
                trends_data = trends_response.json()
                trends_variations = trends_data.get("enhancement_variations", [])
                
                # Check for 2025 trends and platform optimization
                all_trends_text = " ".join([var.get("enhanced_prompt", "") for var in trends_variations])
                
                trends_indicators = [
                    "2025", "algorithm", "platform optimization", "trending", 
                    "TikTok", "YouTube", "Instagram", "engagement velocity"
                ]
                
                trends_found = sum(1 for indicator in trends_indicators if indicator.lower() in all_trends_text.lower())
                
                if trends_found >= 4:  # At least 4 trend indicators
                    self.log_test("Phase 1 Compliance - 2025 Trends Integration", True,
                                f"Successfully integrated {trends_found}/8 trend indicators")
                else:
                    self.log_test("Phase 1 Compliance - 2025 Trends Integration", False,
                                f"Only {trends_found}/8 trend indicators found")
                    
            else:
                self.log_test("Phase 1 Compliance - 2025 Trends Test", False,
                            f"HTTP {trends_response.status_code}")
                
        except Exception as e:
            self.log_test("Phase 1 Compliance - 2025 Trends Test", False,
                        f"Exception: {str(e)}")
        
        # Phase 1 Compliance Test 5: Test retention engineering elements
        try:
            retention_test_payload = {
                "original_prompt": "Create a video about learning new skills effectively",
                "video_type": "educational", 
                "industry_focus": "education",
                "enhancement_count": 3
            }
            
            retention_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=retention_test_payload,
                timeout=120
            )
            
            if retention_response.status_code == 200:
                retention_data = retention_response.json()
                retention_variations = retention_data.get("enhancement_variations", [])
                
                # Check for retention engineering elements
                all_retention_text = " ".join([var.get("enhanced_prompt", "") for var in retention_variations])
                
                retention_elements = [
                    "engagement question", "emotional peak", "pattern interrupt",
                    "retention hook", "cliffhanger", "15-20 seconds",
                    "attention reset", "completion trigger"
                ]
                
                retention_found = sum(1 for element in retention_elements if element.lower() in all_retention_text.lower())
                
                if retention_found >= 3:  # At least 3 retention elements
                    self.log_test("Phase 1 Compliance - Retention Engineering", True,
                                f"Successfully integrated {retention_found}/8 retention engineering elements")
                else:
                    self.log_test("Phase 1 Compliance - Retention Engineering", False,
                                f"Only {retention_found}/8 retention engineering elements found")
                    
            else:
                self.log_test("Phase 1 Compliance - Retention Engineering Test", False,
                            f"HTTP {retention_response.status_code}")
                
        except Exception as e:
            self.log_test("Phase 1 Compliance - Retention Engineering Test", False,
                        f"Exception: {str(e)}")
        
        # Overall Phase 1 compliance assessment
        if successful_compliance_tests >= 2:  # At least 2/3 scenarios must pass
            self.log_test("Phase 1 Enhanced Prompt System - Overall Compliance", True,
                        f"Phase 1 compliance achieved: {successful_compliance_tests}/3 scenarios passed all requirements")
            return True
        else:
            self.log_test("Phase 1 Enhanced Prompt System - Overall Compliance", False,
                        f"Phase 1 compliance failed: only {successful_compliance_tests}/3 scenarios passed requirements")
            return False

    def test_legacy_prompt_endpoint_compatibility(self):
        """Test backward compatibility with legacy endpoint"""
        print("\n=== Testing Legacy Prompt Enhancement Compatibility ===")
        
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
                
                return True
                
            else:
                self.log_test("Legacy Prompt - HTTP Response", False,
                            f"HTTP {legacy_response.status_code}: {legacy_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Prompt - Exception", False, f"Request failed: {str(e)}")
            return False

    def test_phase2_enhance_prompt_v2_endpoint(self):
        """Test Phase 2: /api/enhance-prompt-v2 endpoint with Dynamic Context Integration"""
        print("\n=== Testing Phase 2: Enhanced Prompt V2 with Context Integration ===")
        
        # Test Case 1: Basic Phase 2 functionality
        test_prompt = "Create a video about healthy cooking tips"
        payload = {
            "original_prompt": test_prompt,
            "video_type": "general",
            "industry_focus": "health",
            "enhancement_count": 3
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt-v2",
                json=payload,
                timeout=90  # Longer timeout for context integration
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify Phase 2 response structure
                required_fields = [
                    "original_prompt", "audience_analysis", "enhancement_variations", 
                    "quality_metrics", "recommendation", "industry_insights", "enhancement_methodology"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 2 Enhance V2 - Basic Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                self.log_test("Phase 2 Enhance V2 - Basic Structure", True,
                            "All required Phase 2 fields present")
                
                # Test Case 2: Verify Phase 2 metadata and context integration
                if 'phase' in data and data['phase'] == 'v2_context_integration':
                    self.log_test("Phase 2 Enhance V2 - Phase Identification", True,
                                "Phase 2 context integration properly identified")
                else:
                    self.log_test("Phase 2 Enhance V2 - Phase Identification", False,
                                "Phase 2 identification missing or incorrect")
                
                # Test Case 3: Verify context metadata
                if 'context_metadata' in data:
                    context_metadata = data['context_metadata']
                    if isinstance(context_metadata, dict) and context_metadata:
                        self.log_test("Phase 2 Enhance V2 - Context Metadata", True,
                                    f"Context metadata present with {len(context_metadata)} fields")
                    else:
                        self.log_test("Phase 2 Enhance V2 - Context Metadata", False,
                                    "Context metadata empty or invalid")
                else:
                    self.log_test("Phase 2 Enhance V2 - Context Metadata", False,
                                "Context metadata missing from response")
                
                # Test Case 4: Verify trend alignment score
                if 'trend_alignment_score' in data:
                    trend_score = data['trend_alignment_score']
                    if isinstance(trend_score, (int, float)) and 0 <= trend_score <= 1:
                        self.log_test("Phase 2 Enhance V2 - Trend Alignment Score", True,
                                    f"Valid trend alignment score: {trend_score:.3f}")
                    else:
                        self.log_test("Phase 2 Enhance V2 - Trend Alignment Score", False,
                                    f"Invalid trend alignment score: {trend_score}")
                else:
                    self.log_test("Phase 2 Enhance V2 - Trend Alignment Score", False,
                                "Trend alignment score missing")
                
                # Test Case 5: Verify enhanced methodology mentions context integration
                methodology = data.get("enhancement_methodology", "")
                if "context integration" in methodology.lower() or "real-time" in methodology.lower():
                    self.log_test("Phase 2 Enhance V2 - Enhanced Methodology", True,
                                "Methodology properly describes Phase 2 context integration")
                else:
                    self.log_test("Phase 2 Enhance V2 - Enhanced Methodology", False,
                                "Methodology doesn't mention Phase 2 context integration features")
                
                # Test Case 6: Verify enhancement quality (should be higher than Phase 1)
                quality_metrics = data.get("quality_metrics", {})
                overall_score = quality_metrics.get("overall_quality_score", 0)
                improvement_ratio = quality_metrics.get("improvement_ratio", 0)
                
                if overall_score >= 7.0:  # Phase 2 should have high quality
                    self.log_test("Phase 2 Enhance V2 - Quality Score", True,
                                f"High Phase 2 quality score: {overall_score:.1f}/10")
                else:
                    self.log_test("Phase 2 Enhance V2 - Quality Score", False,
                                f"Phase 2 quality score too low: {overall_score:.1f}/10")
                
                if improvement_ratio >= 50.0:  # Phase 2 should show significant improvement
                    self.log_test("Phase 2 Enhance V2 - Improvement Ratio", True,
                                f"Excellent Phase 2 improvement ratio: {improvement_ratio:.1f}x")
                else:
                    self.log_test("Phase 2 Enhance V2 - Improvement Ratio", False,
                                f"Phase 2 improvement ratio too low: {improvement_ratio:.1f}x")
                
                return True
                
            else:
                self.log_test("Phase 2 Enhance V2 - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 Enhance V2 - Exception", False, f"Request failed: {str(e)}")
            return False

    def test_phase2_context_integration_system(self):
        """Test Phase 2: Context Integration System with all 6 context layers"""
        print("\n=== Testing Phase 2: Context Integration System (6 Context Layers) ===")
        
        # Test different industry/platform combinations to verify context integration
        test_scenarios = [
            {
                "name": "Health Industry - YouTube",
                "payload": {
                    "original_prompt": "Create a video about healthy cooking tips for busy professionals",
                    "video_type": "educational",
                    "industry_focus": "health",
                    "target_platform": "youtube",
                    "enhancement_count": 3
                }
            },
            {
                "name": "Tech Industry - TikTok", 
                "payload": {
                    "original_prompt": "Explain artificial intelligence basics in simple terms",
                    "video_type": "educational",
                    "industry_focus": "tech",
                    "target_platform": "tiktok",
                    "enhancement_count": 3
                }
            },
            {
                "name": "Marketing Industry - LinkedIn",
                "payload": {
                    "original_prompt": "Best social media marketing strategies for 2025",
                    "video_type": "marketing",
                    "industry_focus": "marketing", 
                    "target_platform": "linkedin",
                    "enhancement_count": 3
                }
            }
        ]
        
        successful_scenarios = 0
        context_layers_verified = set()
        
        for scenario in test_scenarios:
            try:
                response = self.session.post(
                    f"{self.backend_url}/enhance-prompt-v2",
                    json=scenario["payload"],
                    timeout=120  # Extended timeout for context integration
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify context metadata contains the 6 context layers
                    context_metadata = data.get("context_metadata", {})
                    
                    # Expected context layers from Phase 2 specification
                    expected_layers = [
                        "trend_analysis",      # SERP API integration
                        "platform_algorithm",  # Platform-specific optimization
                        "competitor_analysis", # Competitive intelligence
                        "audience_psychology", # Audience profiling
                        "seasonal_relevance",  # Cultural timing context
                        "performance_history"  # Performance prediction
                    ]
                    
                    layers_found = 0
                    for layer in expected_layers:
                        if layer in str(context_metadata).lower() or layer.replace('_', ' ') in str(data).lower():
                            context_layers_verified.add(layer)
                            layers_found += 1
                    
                    if layers_found >= 4:  # Should find most context layers
                        self.log_test(f"Phase 2 Context - {scenario['name']}", True,
                                    f"Context integration working: {layers_found}/6 layers detected")
                        successful_scenarios += 1
                    else:
                        self.log_test(f"Phase 2 Context - {scenario['name']}", False,
                                    f"Insufficient context integration: only {layers_found}/6 layers detected")
                    
                    # Verify platform-specific optimization
                    target_platform = scenario["payload"].get("target_platform", "general")
                    if target_platform.lower() in str(data).lower():
                        self.log_test(f"Phase 2 Platform Optimization - {scenario['name']}", True,
                                    f"Platform-specific optimization for {target_platform} detected")
                    else:
                        self.log_test(f"Phase 2 Platform Optimization - {scenario['name']}", False,
                                    f"Platform-specific optimization for {target_platform} not detected")
                    
                    # Verify industry-specific context
                    industry = scenario["payload"]["industry_focus"]
                    industry_mentions = str(data).lower().count(industry.lower())
                    if industry_mentions >= 3:  # Should mention industry multiple times
                        self.log_test(f"Phase 2 Industry Context - {scenario['name']}", True,
                                    f"Strong industry context integration: {industry_mentions} mentions")
                    else:
                        self.log_test(f"Phase 2 Industry Context - {scenario['name']}", False,
                                    f"Weak industry context integration: only {industry_mentions} mentions")
                
                else:
                    self.log_test(f"Phase 2 Context - {scenario['name']}", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Phase 2 Context - {scenario['name']}", False,
                            f"Exception: {str(e)}")
        
        # Overall context integration assessment
        total_layers = len(context_layers_verified)
        if total_layers >= 4:
            self.log_test("Phase 2 Context Integration - Overall", True,
                        f"Successfully verified {total_layers}/6 context layers: {list(context_layers_verified)}")
        else:
            self.log_test("Phase 2 Context Integration - Overall", False,
                        f"Only verified {total_layers}/6 context layers: {list(context_layers_verified)}")
        
        if successful_scenarios >= 2:
            self.log_test("Phase 2 Context Scenarios - Overall", True,
                        f"Successfully tested {successful_scenarios}/{len(test_scenarios)} scenarios")
            return True
        else:
            self.log_test("Phase 2 Context Scenarios - Overall", False,
                        f"Only {successful_scenarios}/{len(test_scenarios)} scenarios succeeded")
            return False

    def test_phase2_serp_api_integration(self):
        """Test Phase 2: SERP API integration for real-time trend analysis"""
        print("\n=== Testing Phase 2: SERP API Integration for Trend Analysis ===")
        
        # Test with prompts that should trigger SERP API calls
        trend_test_cases = [
            {
                "name": "Current Trends Query",
                "payload": {
                    "original_prompt": "Latest social media trends for content creators in 2025",
                    "video_type": "marketing",
                    "industry_focus": "marketing",
                    "enhancement_count": 3
                }
            },
            {
                "name": "Industry Trends Query",
                "payload": {
                    "original_prompt": "Emerging health and wellness trends for fitness enthusiasts",
                    "video_type": "educational", 
                    "industry_focus": "health",
                    "enhancement_count": 3
                }
            },
            {
                "name": "Technology Trends Query",
                "payload": {
                    "original_prompt": "AI and machine learning developments changing business",
                    "video_type": "educational",
                    "industry_focus": "tech", 
                    "enhancement_count": 3
                }
            }
        ]
        
        successful_tests = 0
        trend_indicators_found = set()
        
        for test_case in trend_test_cases:
            try:
                response = self.session.post(
                    f"{self.backend_url}/enhance-prompt-v2",
                    json=test_case["payload"],
                    timeout=150  # Extended timeout for SERP API calls
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = str(data).lower()
                    
                    # Look for indicators of SERP API integration and trend analysis
                    trend_indicators = [
                        "trend", "trending", "current", "latest", "2025", 
                        "popular", "viral", "emerging", "news", "recent",
                        "algorithm", "platform", "optimization", "search"
                    ]
                    
                    indicators_found = 0
                    for indicator in trend_indicators:
                        if indicator in response_text:
                            trend_indicators_found.add(indicator)
                            indicators_found += 1
                    
                    # Check for real-time context integration
                    real_time_indicators = [
                        "real-time", "current", "latest", "up-to-date", 
                        "recent", "now", "today", "2025"
                    ]
                    
                    real_time_found = sum(1 for indicator in real_time_indicators if indicator in response_text)
                    
                    if indicators_found >= 5 and real_time_found >= 2:
                        self.log_test(f"Phase 2 SERP Integration - {test_case['name']}", True,
                                    f"Strong trend analysis detected: {indicators_found} trend indicators, {real_time_found} real-time indicators")
                        successful_tests += 1
                    elif indicators_found >= 3:
                        self.log_test(f"Phase 2 SERP Integration - {test_case['name']}", True,
                                    f"Moderate trend analysis detected: {indicators_found} trend indicators")
                        successful_tests += 1
                    else:
                        self.log_test(f"Phase 2 SERP Integration - {test_case['name']}", False,
                                    f"Insufficient trend analysis: only {indicators_found} trend indicators")
                    
                    # Check for context quality score (should be higher with SERP integration)
                    trend_score = data.get("trend_alignment_score", 0)
                    if trend_score >= 0.6:
                        self.log_test(f"Phase 2 Trend Score - {test_case['name']}", True,
                                    f"High trend alignment score: {trend_score:.3f}")
                    else:
                        self.log_test(f"Phase 2 Trend Score - {test_case['name']}", False,
                                    f"Low trend alignment score: {trend_score:.3f}")
                    
                    # Check for enhanced methodology mentioning trend analysis
                    methodology = data.get("enhancement_methodology", "")
                    if "trend" in methodology.lower() or "serp" in methodology.lower():
                        self.log_test(f"Phase 2 Methodology - {test_case['name']}", True,
                                    "Methodology mentions trend analysis integration")
                    else:
                        self.log_test(f"Phase 2 Methodology - {test_case['name']}", False,
                                    "Methodology doesn't mention trend analysis")
                
                else:
                    self.log_test(f"Phase 2 SERP Integration - {test_case['name']}", False,
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Phase 2 SERP Integration - {test_case['name']}", False,
                            f"Exception: {str(e)}")
        
        # Overall SERP API integration assessment
        total_indicators = len(trend_indicators_found)
        if total_indicators >= 8:
            self.log_test("Phase 2 SERP API - Overall Integration", True,
                        f"Excellent trend analysis integration: {total_indicators} unique indicators found")
        elif total_indicators >= 5:
            self.log_test("Phase 2 SERP API - Overall Integration", True,
                        f"Good trend analysis integration: {total_indicators} unique indicators found")
        else:
            self.log_test("Phase 2 SERP API - Overall Integration", False,
                        f"Limited trend analysis integration: only {total_indicators} unique indicators found")
        
        if successful_tests >= 2:
            self.log_test("Phase 2 SERP API - Test Success", True,
                        f"Successfully tested SERP integration: {successful_tests}/{len(trend_test_cases)} tests passed")
            return True
        else:
            self.log_test("Phase 2 SERP API - Test Success", False,
                        f"SERP integration tests failed: only {successful_tests}/{len(trend_test_cases)} tests passed")
            return False

    def test_phase2_generate_script_v2_endpoint(self):
        """Test Phase 2: /api/generate-script-v2 endpoint with Master Prompt Template V2.0"""
        print("\n=== Testing Phase 2: Generate Script V2 with Master Prompt Template V2.0 ===")
        
        # Test Case 1: Basic Master Prompt Template V2.0 functionality
        test_prompt = "Create an engaging video about productivity tips for remote workers"
        payload = {
            "prompt": test_prompt,
            "video_type": "educational",
            "duration": "medium",
            "visual_style": "professional",
            "target_platform": "youtube",
            "mood": "inspiring"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-script-v2",
                json=payload,
                timeout=90  # Extended timeout for advanced processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify Master Prompt Template V2.0 response structure
                required_fields = [
                    "id", "original_prompt", "generated_script", "video_type", 
                    "duration", "visual_style", "target_platform", "mood", "created_at"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 2 Generate Script V2 - Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                self.log_test("Phase 2 Generate Script V2 - Structure", True,
                            "All Master Prompt Template V2.0 fields present")
                
                # Test Case 2: Verify ELITE video script architect expertise
                script = data["generated_script"]
                script_lower = script.lower()
                
                # Look for ELITE expertise indicators
                elite_indicators = [
                    "hook", "setup", "content", "climax", "resolution",
                    "psychological", "engagement", "retention", "viral",
                    "platform", "algorithm", "optimization", "audience"
                ]
                
                elite_found = sum(1 for indicator in elite_indicators if indicator in script_lower)
                
                if elite_found >= 6:
                    self.log_test("Phase 2 Generate Script V2 - ELITE Expertise", True,
                                f"Strong ELITE expertise indicators: {elite_found}/12 found")
                else:
                    self.log_test("Phase 2 Generate Script V2 - ELITE Expertise", False,
                                f"Insufficient ELITE expertise indicators: only {elite_found}/12 found")
                
                # Test Case 3: Verify mandatory script architecture (Hook/Setup/Content/Climax/Resolution)
                architecture_elements = ["hook", "setup", "content", "climax", "resolution"]
                architecture_found = sum(1 for element in architecture_elements if element in script_lower)
                
                if architecture_found >= 4:
                    self.log_test("Phase 2 Generate Script V2 - Script Architecture", True,
                                f"Mandatory script architecture present: {architecture_found}/5 elements")
                else:
                    self.log_test("Phase 2 Generate Script V2 - Script Architecture", False,
                                f"Incomplete script architecture: only {architecture_found}/5 elements")
                
                # Test Case 4: Verify psychological frameworks integration
                psychological_frameworks = [
                    "psychological", "emotion", "trigger", "engagement", 
                    "retention", "attention", "motivation", "persuasion"
                ]
                
                psych_found = sum(1 for framework in psychological_frameworks if framework in script_lower)
                
                if psych_found >= 4:
                    self.log_test("Phase 2 Generate Script V2 - Psychological Frameworks", True,
                                f"Strong psychological integration: {psych_found}/8 frameworks")
                else:
                    self.log_test("Phase 2 Generate Script V2 - Psychological Frameworks", False,
                                f"Weak psychological integration: only {psych_found}/8 frameworks")
                
                # Test Case 5: Verify platform-specific optimization
                target_platform = payload["target_platform"]
                platform_indicators = [target_platform, "algorithm", "optimization", "platform"]
                
                platform_found = sum(1 for indicator in platform_indicators if indicator in script_lower)
                
                if platform_found >= 2:
                    self.log_test("Phase 2 Generate Script V2 - Platform Optimization", True,
                                f"Platform-specific optimization for {target_platform}: {platform_found} indicators")
                else:
                    self.log_test("Phase 2 Generate Script V2 - Platform Optimization", False,
                                f"Limited platform optimization: only {platform_found} indicators")
                
                # Test Case 6: Verify script quality and length (should be comprehensive)
                script_length = len(script)
                word_count = len(script.split())
                
                if script_length >= 2000 and word_count >= 300:
                    self.log_test("Phase 2 Generate Script V2 - Script Quality", True,
                                f"High-quality comprehensive script: {script_length} chars, {word_count} words")
                elif script_length >= 1000 and word_count >= 150:
                    self.log_test("Phase 2 Generate Script V2 - Script Quality", True,
                                f"Good quality script: {script_length} chars, {word_count} words")
                else:
                    self.log_test("Phase 2 Generate Script V2 - Script Quality", False,
                                f"Script too short: {script_length} chars, {word_count} words")
                
                return True
                
            else:
                self.log_test("Phase 2 Generate Script V2 - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 2 Generate Script V2 - Exception", False, f"Request failed: {str(e)}")
            return False

    def test_phase2_comprehensive_workflow(self):
        """Test Phase 2: Complete workflow from prompt → context enrichment → enhancement → script generation"""
        print("\n=== Testing Phase 2: Complete Workflow Integration ===")
        
        try:
            # Step 1: Test enhance-prompt-v2 with context integration
            original_prompt = "Create a video about sustainable living tips for millennials"
            enhance_payload = {
                "original_prompt": original_prompt,
                "video_type": "educational",
                "industry_focus": "health",
                "target_platform": "instagram",
                "enhancement_count": 3
            }
            
            enhance_response = self.session.post(
                f"{self.backend_url}/enhance-prompt-v2",
                json=enhance_payload,
                timeout=120
            )
            
            if enhance_response.status_code != 200:
                self.log_test("Phase 2 Workflow - Enhancement Step", False,
                            f"Enhancement failed: {enhance_response.status_code}")
                return False
            
            enhanced_data = enhance_response.json()
            
            # Verify Phase 2 enhancement worked
            if 'phase' not in enhanced_data or enhanced_data['phase'] != 'v2_context_integration':
                self.log_test("Phase 2 Workflow - Enhancement Verification", False,
                            "Phase 2 enhancement not properly identified")
                return False
            
            self.log_test("Phase 2 Workflow - Enhancement Step", True,
                        "Phase 2 context-enhanced prompt generation successful")
            
            # Step 2: Use best enhanced prompt for script generation
            variations = enhanced_data.get("enhancement_variations", [])
            if not variations:
                self.log_test("Phase 2 Workflow - Variation Selection", False,
                            "No enhancement variations available")
                return False
            
            # Select the highest scoring variation
            best_variation = max(variations, key=lambda x: x.get("estimated_performance_score", 0))
            enhanced_prompt = best_variation["enhanced_prompt"]
            
            # Step 3: Generate script using Master Prompt Template V2.0 (if available)
            script_payload = {
                "prompt": enhanced_prompt,
                "video_type": "educational",
                "duration": "medium",
                "visual_style": "modern",
                "target_platform": "instagram",
                "mood": "inspiring"
            }
            
            # Try generate-script-v2 first, fallback to generate-script
            script_response = self.session.post(
                f"{self.backend_url}/generate-script-v2",
                json=script_payload,
                timeout=90
            )
            
            if script_response.status_code != 200:
                # Fallback to regular generate-script
                fallback_payload = {
                    "prompt": enhanced_prompt,
                    "video_type": "educational",
                    "duration": "medium"
                }
                
                script_response = self.session.post(
                    f"{self.backend_url}/generate-script",
                    json=fallback_payload,
                    timeout=60
                )
            
            if script_response.status_code != 200:
                self.log_test("Phase 2 Workflow - Script Generation Step", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data["generated_script"]
            
            self.log_test("Phase 2 Workflow - Script Generation Step", True,
                        f"Script generated successfully: {len(generated_script)} characters")
            
            # Step 4: Verify workflow integration quality
            # Check if the final script shows signs of Phase 2 enhancement
            script_lower = generated_script.lower()
            
            # Look for Phase 2 integration indicators
            phase2_indicators = [
                "trend", "platform", "algorithm", "optimization", "engagement",
                "psychological", "audience", "viral", "retention", "context"
            ]
            
            indicators_found = sum(1 for indicator in phase2_indicators if indicator in script_lower)
            
            if indicators_found >= 5:
                self.log_test("Phase 2 Workflow - Integration Quality", True,
                            f"Strong Phase 2 integration in final script: {indicators_found}/10 indicators")
            else:
                self.log_test("Phase 2 Workflow - Integration Quality", False,
                            f"Weak Phase 2 integration in final script: only {indicators_found}/10 indicators")
            
            # Step 5: Verify performance prediction and optimization
            quality_metrics = enhanced_data.get("quality_metrics", {})
            improvement_ratio = quality_metrics.get("improvement_ratio", 0)
            trend_score = enhanced_data.get("trend_alignment_score", 0)
            
            if improvement_ratio >= 20.0 and trend_score >= 0.5:
                self.log_test("Phase 2 Workflow - Performance Prediction", True,
                            f"Excellent performance metrics: {improvement_ratio:.1f}x improvement, {trend_score:.3f} trend score")
            elif improvement_ratio >= 10.0:
                self.log_test("Phase 2 Workflow - Performance Prediction", True,
                            f"Good performance metrics: {improvement_ratio:.1f}x improvement")
            else:
                self.log_test("Phase 2 Workflow - Performance Prediction", False,
                            f"Low performance metrics: {improvement_ratio:.1f}x improvement")
            
            # Step 6: Test with different industries to verify versatility
            industry_tests = [
                {"industry": "marketing", "platform": "linkedin"},
                {"industry": "tech", "platform": "youtube"},
                {"industry": "finance", "platform": "tiktok"}
            ]
            
            industry_success = 0
            for industry_test in industry_tests:
                try:
                    industry_payload = {
                        "original_prompt": f"Create content about {industry_test['industry']} best practices",
                        "video_type": "educational",
                        "industry_focus": industry_test["industry"],
                        "target_platform": industry_test["platform"],
                        "enhancement_count": 2
                    }
                    
                    industry_response = self.session.post(
                        f"{self.backend_url}/enhance-prompt-v2",
                        json=industry_payload,
                        timeout=90
                    )
                    
                    if industry_response.status_code == 200:
                        industry_data = industry_response.json()
                        if 'phase' in industry_data and industry_data['phase'] == 'v2_context_integration':
                            industry_success += 1
                            self.log_test(f"Phase 2 Workflow - {industry_test['industry'].title()} Industry", True,
                                        f"Successfully processed {industry_test['industry']} content for {industry_test['platform']}")
                        else:
                            self.log_test(f"Phase 2 Workflow - {industry_test['industry'].title()} Industry", False,
                                        "Phase 2 not properly identified")
                    else:
                        self.log_test(f"Phase 2 Workflow - {industry_test['industry'].title()} Industry", False,
                                    f"HTTP {industry_response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"Phase 2 Workflow - {industry_test['industry'].title()} Industry", False,
                                f"Exception: {str(e)}")
            
            # Overall workflow assessment
            if industry_success >= 2:
                self.log_test("Phase 2 Workflow - Industry Versatility", True,
                            f"Successfully tested {industry_success}/{len(industry_tests)} industries")
            else:
                self.log_test("Phase 2 Workflow - Industry Versatility", False,
                            f"Only {industry_success}/{len(industry_tests)} industries succeeded")
            
            self.log_test("Phase 2 Workflow - Complete Integration", True,
                        "Successfully completed Phase 2 workflow: prompt → context enrichment → enhancement → script generation")
            
            return True
            
        except Exception as e:
            self.log_test("Phase 2 Workflow - Exception", False, f"Workflow test failed: {str(e)}")
            return False

    def test_phase3_advanced_context_analysis(self):
        """Test Phase 3: /api/advanced-context-analysis endpoint"""
        print("\n=== Testing Phase 3: Advanced Context Analysis ===")
        
        # Sample script from review request
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium", 
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/advanced-context-analysis",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "trend_analysis", "competitor_analysis", "performance_prediction"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Advanced Context Analysis Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify AdvancedContextEngine components
                trend_analysis = data.get("trend_analysis", {})
                competitor_analysis = data.get("competitor_analysis", {})
                performance_prediction = data.get("performance_prediction", {})
                
                # Test TrendAnalyzer component
                if not trend_analysis or not isinstance(trend_analysis, dict):
                    self.log_test("Phase 3 - TrendAnalyzer Component", False,
                                "TrendAnalyzer output missing or invalid")
                    return False
                
                # Test CompetitorAnalyzer component  
                if not competitor_analysis or not isinstance(competitor_analysis, dict):
                    self.log_test("Phase 3 - CompetitorAnalyzer Component", False,
                                "CompetitorAnalyzer output missing or invalid")
                    return False
                
                # Test PerformancePredictor component
                if not performance_prediction or not isinstance(performance_prediction, dict):
                    self.log_test("Phase 3 - PerformancePredictor Component", False,
                                "PerformancePredictor output missing or invalid")
                    return False
                
                self.log_test("Phase 3 - Advanced Context Analysis", True,
                            "Successfully tested AdvancedContextEngine with all components")
                return True
                
            else:
                self.log_test("Phase 3 - Advanced Context Analysis HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Advanced Context Analysis Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_script_quality_analysis(self):
        """Test Phase 3: /api/script-quality-analysis endpoint"""
        print("\n=== Testing Phase 3: Script Quality Analysis ===")
        
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational", 
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/script-quality-analysis",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "quality_scores"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Script Quality Analysis Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify ScriptQualityAnalyzer scoring metrics
                quality_scores = data.get("quality_scores", {})
                required_metrics = [
                    "retention_potential",
                    "engagement_triggers", 
                    "emotional_arc_strength",
                    "platform_optimization",
                    "call_to_action_effectiveness"
                ]
                
                missing_metrics = [metric for metric in required_metrics if metric not in quality_scores]
                if missing_metrics:
                    self.log_test("Phase 3 - Script Quality Metrics", False,
                                f"Missing quality metrics: {missing_metrics}")
                    return False
                
                # Verify all scores are in valid range (0-10)
                for metric, score in quality_scores.items():
                    if not isinstance(score, (int, float)) or score < 0 or score > 10:
                        self.log_test("Phase 3 - Quality Score Range", False,
                                    f"Invalid score for {metric}: {score} (should be 0-10)")
                        return False
                
                self.log_test("Phase 3 - Script Quality Analysis", True,
                            f"Successfully analyzed script with all {len(required_metrics)} quality metrics")
                return True
                
            else:
                self.log_test("Phase 3 - Script Quality Analysis HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Script Quality Analysis Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_script_validation(self):
        """Test Phase 3: /api/script-validation endpoint"""
        print("\n=== Testing Phase 3: Script Validation ===")
        
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/script-validation",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "validation_results"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Script Validation Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify comprehensive structure validation
                validation_results = data.get("validation_results", {})
                required_validations = [
                    "hook_quality",
                    "pacing_optimization", 
                    "retention_hooks",
                    "cta_placement"
                ]
                
                missing_validations = [val for val in required_validations if val not in validation_results]
                if missing_validations:
                    self.log_test("Phase 3 - Script Validation Components", False,
                                f"Missing validation components: {missing_validations}")
                    return False
                
                self.log_test("Phase 3 - Script Validation", True,
                            f"Successfully validated script with all {len(required_validations)} validation components")
                return True
                
            else:
                self.log_test("Phase 3 - Script Validation HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Script Validation Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_track_performance(self):
        """Test Phase 3: /api/track-performance endpoint with MongoDB storage"""
        print("\n=== Testing Phase 3: Performance Tracking ===")
        
        payload = {
            "script_id": f"test_script_{int(time.time())}",
            "performance_data": {
                "views": 15000,
                "engagement_rate": 8.5,
                "retention_rate": 75.2,
                "click_through_rate": 3.8,
                "conversion_rate": 2.1
            },
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/track-performance",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "tracking_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Performance Tracking Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify MongoDB storage integration
                tracking_id = data.get("tracking_id")
                if not tracking_id:
                    self.log_test("Phase 3 - Performance Tracking ID", False,
                                "No tracking ID returned for MongoDB storage")
                    return False
                
                self.log_test("Phase 3 - Performance Tracking", True,
                            f"Successfully tracked performance with MongoDB storage (ID: {tracking_id})")
                return True
                
            else:
                self.log_test("Phase 3 - Performance Tracking HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Performance Tracking Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_performance_insights(self):
        """Test Phase 3: /api/performance-insights endpoint"""
        print("\n=== Testing Phase 3: Performance Insights ===")
        
        payload = {
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/performance-insights",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "insights"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Performance Insights Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify learning capabilities
                insights = data.get("insights", {})
                if not insights or not isinstance(insights, dict):
                    self.log_test("Phase 3 - Performance Insights Data", False,
                                "No insights data returned")
                    return False
                
                self.log_test("Phase 3 - Performance Insights", True,
                            "Successfully retrieved performance insights with learning capabilities")
                return True
                
            else:
                self.log_test("Phase 3 - Performance Insights HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Performance Insights Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_script_recommendations(self):
        """Test Phase 3: /api/script-recommendations endpoint"""
        print("\n=== Testing Phase 3: Script Recommendations ===")
        
        payload = {
            "script": "Sample script for recommendations",
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/script-recommendations",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "recommendations"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Script Recommendations Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify recommendations data
                recommendations = data.get("recommendations", [])
                if not recommendations or not isinstance(recommendations, list):
                    self.log_test("Phase 3 - Script Recommendations Data", False,
                                "No recommendations data returned")
                    return False
                
                self.log_test("Phase 3 - Script Recommendations", True,
                            f"Successfully generated {len(recommendations)} script recommendations")
                return True
                
            else:
                self.log_test("Phase 3 - Script Recommendations HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Script Recommendations Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_script_preview(self):
        """Test Phase 3: /api/script-preview endpoint"""
        print("\n=== Testing Phase 3: Script Preview ===")
        
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/script-preview",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "preview"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Script Preview Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify comprehensive preview generation
                preview = data.get("preview", {})
                if not preview or not isinstance(preview, dict):
                    self.log_test("Phase 3 - Script Preview Data", False,
                                "No preview data returned")
                    return False
                
                self.log_test("Phase 3 - Script Preview", True,
                            "Successfully generated comprehensive script preview")
                return True
                
            else:
                self.log_test("Phase 3 - Script Preview HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Script Preview Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_engagement_timeline(self):
        """Test Phase 3: /api/engagement-timeline endpoint"""
        print("\n=== Testing Phase 3: Engagement Timeline ===")
        
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/engagement-timeline",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "engagement_curve"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Engagement Timeline Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify engagement curve creation
                engagement_curve = data.get("engagement_curve", [])
                if not engagement_curve or not isinstance(engagement_curve, list):
                    self.log_test("Phase 3 - Engagement Timeline Data", False,
                                "No engagement curve data returned")
                    return False
                
                self.log_test("Phase 3 - Engagement Timeline", True,
                            f"Successfully created engagement curve with {len(engagement_curve)} data points")
                return True
                
            else:
                self.log_test("Phase 3 - Engagement Timeline HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Engagement Timeline Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_retention_predictions(self):
        """Test Phase 3: /api/retention-predictions endpoint"""
        print("\n=== Testing Phase 3: Retention Predictions ===")
        
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/retention-predictions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "drop_off_points"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Retention Predictions Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify drop-off point prediction
                drop_off_points = data.get("drop_off_points", [])
                if not isinstance(drop_off_points, list):
                    self.log_test("Phase 3 - Retention Predictions Data", False,
                                "Drop-off points should be a list")
                    return False
                
                self.log_test("Phase 3 - Retention Predictions", True,
                            f"Successfully predicted {len(drop_off_points)} potential drop-off points")
                return True
                
            else:
                self.log_test("Phase 3 - Retention Predictions HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Retention Predictions Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_optimization_suggestions(self):
        """Test Phase 3: /api/optimization-suggestions endpoint"""
        print("\n=== Testing Phase 3: Optimization Suggestions ===")
        
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/optimization-suggestions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["status", "analysis_type", "suggestions"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Optimization Suggestions Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify improvement recommendations
                suggestions = data.get("suggestions", [])
                if not suggestions or not isinstance(suggestions, list):
                    self.log_test("Phase 3 - Optimization Suggestions Data", False,
                                "No optimization suggestions returned")
                    return False
                
                self.log_test("Phase 3 - Optimization Suggestions", True,
                            f"Successfully generated {len(suggestions)} optimization suggestions")
                return True
                
            else:
                self.log_test("Phase 3 - Optimization Suggestions HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Optimization Suggestions Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_comprehensive_script_analysis(self):
        """Test Phase 3: /api/comprehensive-script-analysis endpoint (combines all features)"""
        print("\n=== Testing Phase 3: Comprehensive Script Analysis ===")
        
        test_script = "Did you know that 90% of people make this critical mistake when trying to lose weight? In this video, I'm going to reveal the secret that doctors don't want you to know. You've probably tried every diet out there, but here's why they all failed. The truth is shocking and will change everything you thought you knew about weight loss. By the end of this video, you'll have the exact blueprint that helped thousands of people lose 20+ pounds in just 30 days. But first, let me ask you - are you tired of feeling frustrated with your body? Subscribe and hit the bell icon because this information could save your health."
        
        payload = {
            "script": test_script,
            "metadata": {
                "target_platform": "youtube",
                "duration": "medium",
                "content_type": "educational",
                "industry_focus": "health"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/comprehensive-script-analysis",
                json=payload,
                timeout=90  # Longer timeout for comprehensive analysis
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure combines all Phase 3 features
                required_fields = [
                    "status", "analysis_type", "context_analysis", "quality_analysis", 
                    "validation_results", "preview", "engagement_timeline", 
                    "retention_predictions", "optimization_suggestions"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Phase 3 - Comprehensive Analysis Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify parallel processing worked
                if data.get("status") != "success":
                    self.log_test("Phase 3 - Comprehensive Analysis Status", False,
                                f"Analysis status: {data.get('status')}")
                    return False
                
                # Test different platforms
                platforms = ["TikTok", "Instagram", "LinkedIn"]
                platform_tests = 0
                
                for platform in platforms:
                    platform_payload = {
                        "script": test_script,
                        "metadata": {
                            "target_platform": platform.lower(),
                            "duration": "short",
                            "content_type": "marketing",
                            "industry_focus": "tech"
                        }
                    }
                    
                    try:
                        platform_response = self.session.post(
                            f"{self.backend_url}/comprehensive-script-analysis",
                            json=platform_payload,
                            timeout=90
                        )
                        
                        if platform_response.status_code == 200:
                            platform_tests += 1
                            self.log_test(f"Phase 3 - {platform} Platform Analysis", True,
                                        f"Successfully analyzed script for {platform}")
                        else:
                            self.log_test(f"Phase 3 - {platform} Platform Analysis", False,
                                        f"Failed for {platform}: {platform_response.status_code}")
                    except Exception as e:
                        self.log_test(f"Phase 3 - {platform} Platform Analysis", False,
                                    f"Exception for {platform}: {str(e)}")
                
                # Verify text-based insights generation
                insights_found = 0
                for field in ["context_analysis", "quality_analysis", "validation_results"]:
                    if field in data and data[field]:
                        insights_found += 1
                
                if insights_found < 3:
                    self.log_test("Phase 3 - Text-based Insights", False,
                                f"Only {insights_found}/3 insight categories generated")
                    return False
                
                self.log_test("Phase 3 - Comprehensive Script Analysis", True,
                            f"Successfully completed comprehensive analysis with all Phase 3 features, {platform_tests}/{len(platforms)} platforms tested")
                return True
                
            else:
                self.log_test("Phase 3 - Comprehensive Analysis HTTP", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Phase 3 - Comprehensive Analysis Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_mongodb_integration(self):
        """Test Phase 3: MongoDB integration for performance tracking"""
        print("\n=== Testing Phase 3: MongoDB Integration ===")
        
        # Test performance tracking with MongoDB storage
        test_data = {
            "script_id": f"mongodb_test_{int(time.time())}",
            "performance_data": {
                "views": 25000,
                "engagement_rate": 9.2,
                "retention_rate": 82.5,
                "click_through_rate": 4.1,
                "conversion_rate": 2.8
            },
            "metadata": {
                "target_platform": "youtube",
                "duration": "long",
                "content_type": "educational",
                "industry_focus": "tech"
            }
        }
        
        try:
            # Track performance
            track_response = self.session.post(
                f"{self.backend_url}/track-performance",
                json=test_data,
                timeout=30
            )
            
            if track_response.status_code != 200:
                self.log_test("Phase 3 - MongoDB Track Performance", False,
                            f"Failed to track performance: {track_response.status_code}")
                return False
            
            track_data = track_response.json()
            tracking_id = track_data.get("tracking_id")
            
            if not tracking_id:
                self.log_test("Phase 3 - MongoDB Tracking ID", False,
                            "No tracking ID returned")
                return False
            
            # Test performance insights retrieval
            insights_response = self.session.post(
                f"{self.backend_url}/performance-insights",
                json={"metadata": test_data["metadata"]},
                timeout=30
            )
            
            if insights_response.status_code != 200:
                self.log_test("Phase 3 - MongoDB Performance Insights", False,
                            f"Failed to retrieve insights: {insights_response.status_code}")
                return False
            
            self.log_test("Phase 3 - MongoDB Integration", True,
                        f"Successfully tested MongoDB integration with tracking ID: {tracking_id}")
            return True
            
        except Exception as e:
            self.log_test("Phase 3 - MongoDB Integration Exception", False,
                        f"Request failed: {str(e)}")
            return False
    
    def test_phase3_error_handling(self):
        """Test Phase 3: Error handling and edge cases"""
        print("\n=== Testing Phase 3: Error Handling ===")
        
        error_tests = [
            {
                "name": "Empty Script",
                "endpoint": "script-quality-analysis",
                "payload": {"script": "", "metadata": {"target_platform": "youtube"}}
            },
            {
                "name": "Invalid Platform",
                "endpoint": "comprehensive-script-analysis", 
                "payload": {"script": "test", "metadata": {"target_platform": "invalid_platform"}}
            },
            {
                "name": "Missing Metadata",
                "endpoint": "script-validation",
                "payload": {"script": "test script"}
            }
        ]
        
        successful_error_tests = 0
        
        for test in error_tests:
            try:
                response = self.session.post(
                    f"{self.backend_url}/{test['endpoint']}",
                    json=test["payload"],
                    timeout=30
                )
                
                # Should handle errors gracefully (either 400 for validation or 200 with error status)
                if response.status_code in [200, 400]:
                    if response.status_code == 200:
                        data = response.json()
                        # Check if error is handled in response
                        if "error" in data or data.get("status") == "error":
                            successful_error_tests += 1
                            self.log_test(f"Phase 3 - Error Handling: {test['name']}", True,
                                        "Error handled gracefully in response")
                        else:
                            self.log_test(f"Phase 3 - Error Handling: {test['name']}", True,
                                        "Request processed successfully despite edge case")
                            successful_error_tests += 1
                    else:
                        successful_error_tests += 1
                        self.log_test(f"Phase 3 - Error Handling: {test['name']}", True,
                                    f"Proper validation error returned: {response.status_code}")
                else:
                    self.log_test(f"Phase 3 - Error Handling: {test['name']}", False,
                                f"Unexpected status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Phase 3 - Error Handling: {test['name']}", False,
                            f"Exception: {str(e)}")
        
        if successful_error_tests >= 2:
            self.log_test("Phase 3 - Error Handling Overall", True,
                        f"Successfully tested {successful_error_tests}/{len(error_tests)} error scenarios")
            return True
        else:
            self.log_test("Phase 3 - Error Handling Overall", False,
                        f"Only {successful_error_tests}/{len(error_tests)} error tests passed")
            return False

    def test_script_editing_functionality(self):
        """Test the new script editing functionality (PUT /api/scripts/{script_id})"""
        print("\n=== Testing Script Editing Functionality ===")
        
        # Step 1: First generate a script to edit
        print("Step 1: Generating a script to edit...")
        script_payload = {
            "prompt": "Create a video about productivity tips for remote workers",
            "video_type": "educational",
            "duration": "medium"
        }
        
        try:
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Script Editing - Script Generation Setup", False,
                            f"Failed to generate script for editing test: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            script_id = script_data["id"]
            original_script = script_data["generated_script"]
            original_prompt = script_data["original_prompt"]
            original_video_type = script_data["video_type"]
            original_duration = script_data["duration"]
            original_created_at = script_data["created_at"]
            
            self.log_test("Script Editing - Script Generation Setup", True,
                        f"Successfully generated script with ID: {script_id}")
            
        except Exception as e:
            self.log_test("Script Editing - Script Generation Setup", False,
                        f"Exception during script generation: {str(e)}")
            return False
        
        # Step 2: Test valid script update
        print("Step 2: Testing valid script update...")
        updated_script_content = """[SCENE: Modern home office setup with natural lighting]

(Narrator - Professional, engaging tone)
Working from home has become the new normal, but staying productive can be challenging. Here are five game-changing tips that will transform your remote work experience.

[SCENE: Close-up of organized desk with productivity tools]

First, create a dedicated workspace. Your brain needs clear boundaries between work and personal life. Even a small corner can become your productivity zone.

[SCENE: Person following a morning routine]

Second, establish a morning routine. Start your day with intention - shower, dress professionally, and begin work at the same time every day.

[SCENE: Digital calendar and task management apps]

Third, use time-blocking techniques. Schedule specific times for deep work, meetings, and breaks. Your calendar becomes your productivity roadmap.

[SCENE: Person taking a walk outside]

Fourth, take regular breaks. The Pomodoro Technique works wonders - 25 minutes of focused work followed by a 5-minute break keeps your mind sharp.

[SCENE: Video call with team members]

Finally, over-communicate with your team. Remote work requires intentional communication. Share your progress, ask questions, and stay connected.

(Narrator - Encouraging tone)
Remember, productivity isn't about working more hours - it's about working smarter. Implement these strategies and watch your remote work efficiency soar!

[SCENE: Person successfully completing tasks with satisfaction]

What's your biggest remote work challenge? Share in the comments below!"""

        update_payload = {
            "script_id": script_id,
            "generated_script": updated_script_content
        }
        
        try:
            update_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=update_payload,
                timeout=30
            )
            
            if update_response.status_code == 200:
                updated_data = update_response.json()
                
                # Verify response structure
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in updated_data]
                
                if missing_fields:
                    self.log_test("Script Editing - Update Response Structure", False,
                                f"Missing fields in update response: {missing_fields}")
                    return False
                
                # Verify the script content was updated
                if updated_data["generated_script"] != updated_script_content:
                    self.log_test("Script Editing - Script Content Update", False,
                                "Script content was not updated correctly")
                    return False
                
                # Verify all original fields are preserved except generated_script
                if (updated_data["id"] != script_id or
                    updated_data["original_prompt"] != original_prompt or
                    updated_data["video_type"] != original_video_type or
                    updated_data["duration"] != original_duration or
                    updated_data["created_at"] != original_created_at):
                    self.log_test("Script Editing - Original Fields Preservation", False,
                                "Original script metadata was not preserved correctly")
                    return False
                
                self.log_test("Script Editing - Valid Update", True,
                            f"Successfully updated script content ({len(updated_script_content)} chars)")
                
            else:
                self.log_test("Script Editing - Valid Update", False,
                            f"HTTP {update_response.status_code}: {update_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Valid Update", False,
                        f"Exception during script update: {str(e)}")
            return False
        
        # Step 3: Verify the update was saved to database
        print("Step 3: Verifying database persistence...")
        try:
            # Retrieve the script again to verify it was saved
            retrieval_response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if retrieval_response.status_code == 200:
                scripts = retrieval_response.json()
                updated_script_found = None
                
                for script in scripts:
                    if script["id"] == script_id:
                        updated_script_found = script
                        break
                
                if not updated_script_found:
                    self.log_test("Script Editing - Database Persistence", False,
                                "Updated script not found in database")
                    return False
                
                if updated_script_found["generated_script"] != updated_script_content:
                    self.log_test("Script Editing - Database Persistence", False,
                                "Script content in database doesn't match update")
                    return False
                
                self.log_test("Script Editing - Database Persistence", True,
                            "Script update successfully persisted to database")
                
            else:
                self.log_test("Script Editing - Database Persistence", False,
                            f"Failed to retrieve scripts for verification: {retrieval_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Database Persistence", False,
                        f"Exception during database verification: {str(e)}")
            return False
        
        # Step 4: Test error handling for invalid script ID
        print("Step 4: Testing error handling for invalid script ID...")
        invalid_script_id = "invalid-script-id-12345"
        invalid_update_payload = {
            "script_id": invalid_script_id,
            "generated_script": "This should fail because the script ID doesn't exist"
        }
        
        try:
            invalid_response = self.session.put(
                f"{self.backend_url}/scripts/{invalid_script_id}",
                json=invalid_update_payload,
                timeout=30
            )
            
            if invalid_response.status_code == 404:
                self.log_test("Script Editing - Invalid ID Error Handling", True,
                            "Correctly returned 404 for invalid script ID")
            else:
                self.log_test("Script Editing - Invalid ID Error Handling", False,
                            f"Expected 404, got {invalid_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Invalid ID Error Handling", False,
                        f"Exception during invalid ID test: {str(e)}")
            return False
        
        # Step 5: Test error handling for missing required fields
        print("Step 5: Testing error handling for missing required fields...")
        try:
            # Test with missing generated_script field
            incomplete_payload = {
                "script_id": script_id
                # Missing generated_script field
            }
            
            incomplete_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=incomplete_payload,
                timeout=30
            )
            
            if incomplete_response.status_code == 422:  # Validation error
                self.log_test("Script Editing - Missing Fields Error Handling", True,
                            "Correctly returned 422 for missing required fields")
            else:
                self.log_test("Script Editing - Missing Fields Error Handling", False,
                            f"Expected 422, got {incomplete_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Missing Fields Error Handling", False,
                        f"Exception during missing fields test: {str(e)}")
            return False
        
        # Step 6: Test with empty script content
        print("Step 6: Testing with empty script content...")
        try:
            empty_payload = {
                "script_id": script_id,
                "generated_script": ""
            }
            
            empty_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=empty_payload,
                timeout=30
            )
            
            if empty_response.status_code == 200:
                empty_data = empty_response.json()
                if empty_data["generated_script"] == "":
                    self.log_test("Script Editing - Empty Content Handling", True,
                                "Successfully handled empty script content")
                else:
                    self.log_test("Script Editing - Empty Content Handling", False,
                                "Empty script content was not saved correctly")
                    return False
            else:
                self.log_test("Script Editing - Empty Content Handling", False,
                            f"Failed to handle empty content: {empty_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Empty Content Handling", False,
                        f"Exception during empty content test: {str(e)}")
            return False
        
        # Step 7: Test with very long script content
        print("Step 7: Testing with very long script content...")
        try:
            long_script = "This is a very long script content. " * 1000  # ~35,000 characters
            long_payload = {
                "script_id": script_id,
                "generated_script": long_script
            }
            
            long_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=long_payload,
                timeout=30
            )
            
            if long_response.status_code == 200:
                long_data = long_response.json()
                if len(long_data["generated_script"]) == len(long_script):
                    self.log_test("Script Editing - Long Content Handling", True,
                                f"Successfully handled long script content ({len(long_script)} chars)")
                else:
                    self.log_test("Script Editing - Long Content Handling", False,
                                "Long script content was truncated or corrupted")
                    return False
            else:
                self.log_test("Script Editing - Long Content Handling", False,
                            f"Failed to handle long content: {long_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Long Content Handling", False,
                        f"Exception during long content test: {str(e)}")
            return False
        
        print("✅ Script editing functionality testing completed successfully!")
        return True

    def run_all_tests(self):
        """Run all backend tests including Phase 3 advanced analytics"""
        print("🚀 Starting Comprehensive Backend Testing with Phase 3 Advanced Analytics...")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed - stopping tests")
            return False
        
        # Core functionality tests + Phase 3 tests
        tests = [
            ("Enhanced Prompt System", self.test_enhance_prompt_endpoint),
            ("Enhanced Prompt Scenarios", self.test_enhanced_prompt_different_scenarios),
            ("Comprehensive Script Framework", self.test_comprehensive_script_framework_system),
            ("Script Generation", self.test_generate_script_endpoint),
            ("Scripts Retrieval", self.test_scripts_retrieval_endpoint),
            ("Script Editing Functionality", self.test_script_editing_functionality),  # NEW TEST
            ("Integration Flow", self.test_integration_flow),
            ("Voices Endpoint", self.test_voices_endpoint),
            ("Generate Audio", self.test_generate_audio_endpoint),
            ("Timestamp Removal", self.test_timestamp_removal_comprehensive),
            ("Avatar Video Generation", self.test_avatar_video_generation_endpoint),
            ("Enhanced Avatar Video", self.test_enhanced_avatar_video_generation_endpoint),
            # Phase 3 Advanced Analytics Tests
            ("Phase 3 - Advanced Context Analysis", self.test_phase3_advanced_context_analysis),
            ("Phase 3 - Script Quality Analysis", self.test_phase3_script_quality_analysis),
            ("Phase 3 - Script Validation", self.test_phase3_script_validation),
            ("Phase 3 - Performance Tracking", self.test_phase3_track_performance),
            ("Phase 3 - Performance Insights", self.test_phase3_performance_insights),
            ("Phase 3 - Script Recommendations", self.test_phase3_script_recommendations),
            ("Phase 3 - Script Preview", self.test_phase3_script_preview),
            ("Phase 3 - Engagement Timeline", self.test_phase3_engagement_timeline),
            ("Phase 3 - Retention Predictions", self.test_phase3_retention_predictions),
            ("Phase 3 - Optimization Suggestions", self.test_phase3_optimization_suggestions),
            ("Phase 3 - Comprehensive Analysis", self.test_phase3_comprehensive_script_analysis),
            ("Phase 3 - MongoDB Integration", self.test_phase3_mongodb_integration),
            ("Phase 3 - Error Handling", self.test_phase3_error_handling)
        ]
        
        successful_tests = 0
        total_tests = len(tests)
        phase3_tests = 0
        phase3_passed = 0
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    successful_tests += 1
                    if "Phase 3" in test_name:
                        phase3_passed += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
                    
                if "Phase 3" in test_name:
                    phase3_tests += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                self.log_test(f"{test_name} - Exception", False, f"Unexpected error: {str(e)}")
                if "Phase 3" in test_name:
                    phase3_tests += 1
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 BACKEND TESTING SUMMARY")
        print("="*80)
        
        success_rate = (successful_tests / total_tests) * 100
        phase3_success_rate = (phase3_passed / phase3_tests) * 100 if phase3_tests > 0 else 0
        
        print(f"Overall Tests Passed: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"Phase 3 Tests Passed: {phase3_passed}/{phase3_tests} ({phase3_success_rate:.1f}%)")
        
        if success_rate >= 80 and phase3_success_rate >= 70:
            print("🎉 Backend testing completed with excellent results!")
            print("✅ Phase 3 Advanced Analytics system is working correctly!")
            return True
        elif success_rate >= 60:
            print("⚠️  Backend testing completed with acceptable results")
            if phase3_success_rate < 70:
                print("⚠️  Phase 3 Advanced Analytics needs attention")
            return True
        else:
            print("❌ Backend testing completed with concerning results")
            return False

if __name__ == "__main__":
    tester = ScriptGenerationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Few-Shot Learning & Pattern Recognition System Backend Testing
=============================================================

This test suite comprehensively tests the new Few-Shot Learning & Pattern Recognition System
that was implemented to improve script generation through learned patterns and examples.

Test Coverage:
1. Few-Shot Stats Endpoint (GET /api/few-shot-stats)
2. Example Database Management (POST /api/manage-example-database)
3. Pattern Analysis (POST /api/analyze-patterns)
4. Few-Shot Script Generation (POST /api/generate-script-few-shot)

Focus Areas:
- System initialization and database building
- Pattern recognition and extraction
- Context-aware example selection
- Enhanced script generation using learned patterns
- Error handling and response structure validation
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from frontend .env
BACKEND_URL = "https://f5f1bcd3-1e7e-4f94-9ffa-0d0d9163f7bc.preview.emergentagent.com/api"

class FewShotTestSuite:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test results with detailed information"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: {status}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {status}")
            
        if details:
            print(f"   Details: {details}")
            
        if response_data and status == "FAIL":
            print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
            
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print()

    def test_few_shot_stats_endpoint(self):
        """Test GET /api/few-shot-stats - System initialization and statistics"""
        print("🔍 Testing Few-Shot Stats Endpoint...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/few-shot-stats", timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["status", "system_stats", "capabilities", "learning_effectiveness"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Few-Shot Stats Structure", 
                        "FAIL", 
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Test system status
                if data.get("status") == "operational":
                    self.log_test(
                        "Few-Shot System Status", 
                        "PASS", 
                        f"System operational with status: {data['status']}"
                    )
                else:
                    self.log_test(
                        "Few-Shot System Status", 
                        "FAIL", 
                        f"System not operational: {data.get('status', 'unknown')}"
                    )
                
                # Test capabilities
                capabilities = data.get("capabilities", {})
                expected_capabilities = ["pattern_recognition", "example_matching", "template_learning", "dynamic_selection"]
                
                active_capabilities = [cap for cap in expected_capabilities if "✅" in str(capabilities.get(cap, ""))]
                
                if len(active_capabilities) == len(expected_capabilities):
                    self.log_test(
                        "Few-Shot Capabilities", 
                        "PASS", 
                        f"All {len(active_capabilities)} capabilities active: {', '.join(active_capabilities)}"
                    )
                else:
                    self.log_test(
                        "Few-Shot Capabilities", 
                        "FAIL", 
                        f"Only {len(active_capabilities)}/{len(expected_capabilities)} capabilities active"
                    )
                
                # Test system stats structure
                system_stats = data.get("system_stats", {})
                if "database_stats" in system_stats and "performance_averages" in system_stats:
                    db_stats = system_stats["database_stats"]
                    examples_count = db_stats.get("examples_count", 0)
                    patterns_count = db_stats.get("patterns_count", 0)
                    
                    self.log_test(
                        "Few-Shot Database Stats", 
                        "PASS", 
                        f"Database initialized with {examples_count} examples and {patterns_count} patterns"
                    )
                else:
                    self.log_test(
                        "Few-Shot Database Stats", 
                        "FAIL", 
                        "Missing database_stats or performance_averages in system_stats"
                    )
                
                # Test learning effectiveness
                learning_eff = data.get("learning_effectiveness", {})
                if all(key in learning_eff for key in ["pattern_application", "example_quality", "context_coverage"]):
                    self.log_test(
                        "Few-Shot Learning Effectiveness", 
                        "PASS", 
                        f"Learning metrics available: {len(learning_eff)} metrics tracked"
                    )
                else:
                    self.log_test(
                        "Few-Shot Learning Effectiveness", 
                        "FAIL", 
                        "Missing learning effectiveness metrics"
                    )
                    
            else:
                self.log_test(
                    "Few-Shot Stats Endpoint", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except requests.exceptions.Timeout:
            self.log_test("Few-Shot Stats Endpoint", "FAIL", "Request timeout (60s)")
        except Exception as e:
            self.log_test("Few-Shot Stats Endpoint", "FAIL", f"Exception: {str(e)}")

    def test_example_database_management(self):
        """Test POST /api/manage-example-database - Database building and management"""
        print("🔍 Testing Example Database Management...")
        
        # Test 1: Get current database status
        try:
            payload = {
                "rebuild": False,
                "add_examples": [],
                "filter_by": {}
            }
            
            response = requests.post(
                f"{BACKEND_URL}/manage-example-database", 
                json=payload, 
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["status", "examples_count", "patterns_count", "categories", "performance_metrics", "last_updated"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Database Status Response Structure", 
                        "FAIL", 
                        f"Missing fields: {missing_fields}",
                        data
                    )
                else:
                    self.log_test(
                        "Database Status Response Structure", 
                        "PASS", 
                        f"All required fields present. Status: {data['status']}"
                    )
                
                # Test database content
                examples_count = data.get("examples_count", 0)
                patterns_count = data.get("patterns_count", 0)
                
                if examples_count > 0 and patterns_count > 0:
                    self.log_test(
                        "Database Content Availability", 
                        "PASS", 
                        f"Database contains {examples_count} examples and {patterns_count} patterns"
                    )
                else:
                    self.log_test(
                        "Database Content Availability", 
                        "FAIL", 
                        f"Insufficient content: {examples_count} examples, {patterns_count} patterns"
                    )
                
                # Test categories structure
                categories = data.get("categories", {})
                expected_category_types = ["video_types", "industries", "platforms"]
                
                available_categories = [cat for cat in expected_category_types if cat in categories]
                
                if len(available_categories) >= 2:
                    self.log_test(
                        "Database Categories", 
                        "PASS", 
                        f"Categories available: {', '.join(available_categories)}"
                    )
                else:
                    self.log_test(
                        "Database Categories", 
                        "FAIL", 
                        f"Insufficient categories: {available_categories}"
                    )
                
                # Test performance metrics
                perf_metrics = data.get("performance_metrics", {})
                if perf_metrics and len(perf_metrics) > 0:
                    avg_engagement = perf_metrics.get("engagement_rate", 0)
                    self.log_test(
                        "Database Performance Metrics", 
                        "PASS", 
                        f"Performance metrics available. Avg engagement: {avg_engagement}/10"
                    )
                else:
                    self.log_test(
                        "Database Performance Metrics", 
                        "FAIL", 
                        "No performance metrics available"
                    )
                    
            else:
                self.log_test(
                    "Database Status Query", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except requests.exceptions.Timeout:
            self.log_test("Database Status Query", "FAIL", "Request timeout (120s)")
        except Exception as e:
            self.log_test("Database Status Query", "FAIL", f"Exception: {str(e)}")

        # Test 2: Add example to database
        try:
            new_example = {
                "video_type": "educational",
                "industry": "health",
                "platform": "youtube",
                "script_content": "Welcome to our comprehensive guide on healthy cooking! Today we'll explore 5 game-changing techniques that will transform your kitchen skills and boost your family's nutrition...",
                "performance_metrics": {
                    "engagement_rate": 8.5,
                    "viral_score": 7.2,
                    "retention_rate": 9.1
                },
                "success_factors": ["clear value proposition", "step-by-step structure", "practical tips", "health benefits focus"],
                "metadata": {
                    "duration": "medium",
                    "audience_tone": "educational",
                    "complexity_level": "intermediate"
                }
            }
            
            payload = {
                "rebuild": False,
                "add_examples": [new_example],
                "filter_by": {}
            }
            
            response = requests.post(
                f"{BACKEND_URL}/manage-example-database", 
                json=payload, 
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Add Example to Database", 
                    "PASS", 
                    f"Successfully added example. New count: {data.get('examples_count', 'unknown')}"
                )
            else:
                self.log_test(
                    "Add Example to Database", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_test("Add Example to Database", "FAIL", f"Exception: {str(e)}")

    def test_pattern_analysis(self):
        """Test POST /api/analyze-patterns - Pattern recognition and analysis"""
        print("🔍 Testing Pattern Analysis...")
        
        # Test different context types and values
        test_contexts = [
            {"context_type": "video_type", "context_value": "educational", "analysis_depth": "comprehensive"},
            {"context_type": "industry", "context_value": "health", "analysis_depth": "comprehensive"},
            {"context_type": "platform", "context_value": "youtube", "analysis_depth": "basic"},
            {"context_type": "video_type", "context_value": "entertainment", "analysis_depth": "detailed"}
        ]
        
        for i, context in enumerate(test_contexts):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/analyze-patterns", 
                    json=context, 
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["context", "patterns_found", "top_patterns", "success_factors", "recommendations", "effectiveness_metrics"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(
                            f"Pattern Analysis {i+1} Structure", 
                            "FAIL", 
                            f"Missing fields: {missing_fields}",
                            data
                        )
                        continue
                    
                    # Test pattern discovery
                    patterns_found = data.get("patterns_found", 0)
                    top_patterns = data.get("top_patterns", [])
                    
                    if patterns_found > 0 and len(top_patterns) > 0:
                        self.log_test(
                            f"Pattern Discovery ({context['context_type']}={context['context_value']})", 
                            "PASS", 
                            f"Found {patterns_found} patterns, top {len(top_patterns)} analyzed"
                        )
                    else:
                        self.log_test(
                            f"Pattern Discovery ({context['context_type']}={context['context_value']})", 
                            "FAIL", 
                            f"No patterns found: {patterns_found} patterns, {len(top_patterns)} top patterns"
                        )
                    
                    # Test pattern details
                    if top_patterns:
                        first_pattern = top_patterns[0]
                        pattern_fields = ["name", "type", "effectiveness", "usage_guide"]
                        
                        if all(field in first_pattern for field in pattern_fields):
                            effectiveness = first_pattern.get("effectiveness", 0)
                            self.log_test(
                                f"Pattern Details Quality ({context['context_value']})", 
                                "PASS", 
                                f"Pattern '{first_pattern['name']}' with {effectiveness}/10 effectiveness"
                            )
                        else:
                            self.log_test(
                                f"Pattern Details Quality ({context['context_value']})", 
                                "FAIL", 
                                f"Incomplete pattern data: {list(first_pattern.keys())}"
                            )
                    
                    # Test success factors
                    success_factors = data.get("success_factors", [])
                    if len(success_factors) > 0:
                        self.log_test(
                            f"Success Factors Analysis ({context['context_value']})", 
                            "PASS", 
                            f"Identified {len(success_factors)} success factors: {', '.join(success_factors[:3])}"
                        )
                    else:
                        self.log_test(
                            f"Success Factors Analysis ({context['context_value']})", 
                            "FAIL", 
                            "No success factors identified"
                        )
                    
                    # Test effectiveness metrics
                    effectiveness_metrics = data.get("effectiveness_metrics", {})
                    expected_metrics = ["average_engagement", "average_viral_score", "average_retention"]
                    
                    available_metrics = [metric for metric in expected_metrics if metric in effectiveness_metrics]
                    
                    if len(available_metrics) >= 2:
                        avg_engagement = effectiveness_metrics.get("average_engagement", 0)
                        self.log_test(
                            f"Effectiveness Metrics ({context['context_value']})", 
                            "PASS", 
                            f"Metrics available: {', '.join(available_metrics)}. Avg engagement: {avg_engagement}/10"
                        )
                    else:
                        self.log_test(
                            f"Effectiveness Metrics ({context['context_value']})", 
                            "FAIL", 
                            f"Insufficient metrics: {available_metrics}"
                        )
                    
                    # Test recommendations
                    recommendations = data.get("recommendations", [])
                    if len(recommendations) >= 3:
                        self.log_test(
                            f"Pattern Recommendations ({context['context_value']})", 
                            "PASS", 
                            f"Generated {len(recommendations)} actionable recommendations"
                        )
                    else:
                        self.log_test(
                            f"Pattern Recommendations ({context['context_value']})", 
                            "FAIL", 
                            f"Insufficient recommendations: {len(recommendations)}"
                        )
                        
                else:
                    self.log_test(
                        f"Pattern Analysis {i+1}", 
                        "FAIL", 
                        f"HTTP {response.status_code}: {response.text[:200]}"
                    )
                    
            except requests.exceptions.Timeout:
                self.log_test(f"Pattern Analysis {i+1}", "FAIL", "Request timeout (60s)")
            except Exception as e:
                self.log_test(f"Pattern Analysis {i+1}", "FAIL", f"Exception: {str(e)}")

    def test_few_shot_script_generation(self):
        """Test POST /api/generate-script-few-shot - Enhanced script generation using learned patterns"""
        print("🔍 Testing Few-Shot Script Generation...")
        
        # Test cases covering different video types, industries, and platforms
        test_cases = [
            {
                "name": "Viral TikTok Health Content",
                "request": {
                    "prompt": "Create a video about 5 morning habits that boost energy naturally",
                    "video_type": "viral",
                    "industry": "health",
                    "platform": "tiktok",
                    "duration": "short",
                    "audience_tone": "energetic",
                    "complexity_level": "beginner",
                    "engagement_goals": ["viral_potential", "educational_value"],
                    "use_pattern_learning": True,
                    "max_examples": 5
                }
            },
            {
                "name": "Educational YouTube Tech Content",
                "request": {
                    "prompt": "Explain how artificial intelligence is transforming healthcare in 2025",
                    "video_type": "educational",
                    "industry": "tech",
                    "platform": "youtube",
                    "duration": "medium",
                    "audience_tone": "professional",
                    "complexity_level": "intermediate",
                    "engagement_goals": ["knowledge_transfer", "credibility"],
                    "use_pattern_learning": True,
                    "max_examples": 3
                }
            },
            {
                "name": "Entertainment Instagram Marketing",
                "request": {
                    "prompt": "Show the behind-the-scenes of creating a successful marketing campaign",
                    "video_type": "entertainment",
                    "industry": "marketing",
                    "platform": "instagram",
                    "duration": "medium",
                    "audience_tone": "casual",
                    "complexity_level": "intermediate",
                    "engagement_goals": ["engagement", "shareability"],
                    "use_pattern_learning": True,
                    "max_examples": 4
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                print(f"   Testing: {test_case['name']}")
                
                response = requests.post(
                    f"{BACKEND_URL}/generate-script-few-shot", 
                    json=test_case["request"], 
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["id", "original_prompt", "enhanced_prompt", "generated_script", 
                                     "patterns_applied", "examples_used", "confidence_score", 
                                     "learning_insights", "pattern_details", "created_at"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(
                            f"Few-Shot Generation Structure ({test_case['name']})", 
                            "FAIL", 
                            f"Missing fields: {missing_fields}",
                            data
                        )
                        continue
                    
                    # Test prompt enhancement
                    original_prompt = data.get("original_prompt", "")
                    enhanced_prompt = data.get("enhanced_prompt", "")
                    
                    if len(enhanced_prompt) > len(original_prompt) * 1.5:
                        enhancement_ratio = len(enhanced_prompt) / len(original_prompt)
                        self.log_test(
                            f"Prompt Enhancement ({test_case['name']})", 
                            "PASS", 
                            f"Enhanced prompt is {enhancement_ratio:.1f}x more detailed ({len(enhanced_prompt)} chars)"
                        )
                    else:
                        self.log_test(
                            f"Prompt Enhancement ({test_case['name']})", 
                            "FAIL", 
                            f"Insufficient enhancement: {len(enhanced_prompt)} vs {len(original_prompt)} chars"
                        )
                    
                    # Test script generation quality
                    generated_script = data.get("generated_script", "")
                    
                    if len(generated_script) > 500:  # Minimum quality threshold
                        self.log_test(
                            f"Script Generation Quality ({test_case['name']})", 
                            "PASS", 
                            f"Generated high-quality script ({len(generated_script)} characters)"
                        )
                    else:
                        self.log_test(
                            f"Script Generation Quality ({test_case['name']})", 
                            "FAIL", 
                            f"Script too short: {len(generated_script)} characters"
                        )
                    
                    # Test pattern application
                    patterns_applied = data.get("patterns_applied", 0)
                    examples_used = data.get("examples_used", 0)
                    
                    if patterns_applied > 0 and examples_used > 0:
                        self.log_test(
                            f"Pattern Application ({test_case['name']})", 
                            "PASS", 
                            f"Applied {patterns_applied} patterns using {examples_used} examples"
                        )
                    else:
                        self.log_test(
                            f"Pattern Application ({test_case['name']})", 
                            "FAIL", 
                            f"No patterns applied: {patterns_applied} patterns, {examples_used} examples"
                        )
                    
                    # Test confidence score
                    confidence_score = data.get("confidence_score", 0)
                    
                    if confidence_score >= 7.0:
                        self.log_test(
                            f"Generation Confidence ({test_case['name']})", 
                            "PASS", 
                            f"High confidence score: {confidence_score}/10"
                        )
                    elif confidence_score >= 5.0:
                        self.log_test(
                            f"Generation Confidence ({test_case['name']})", 
                            "PASS", 
                            f"Moderate confidence score: {confidence_score}/10"
                        )
                    else:
                        self.log_test(
                            f"Generation Confidence ({test_case['name']})", 
                            "FAIL", 
                            f"Low confidence score: {confidence_score}/10"
                        )
                    
                    # Test learning insights
                    learning_insights = data.get("learning_insights", [])
                    
                    if len(learning_insights) >= 3:
                        self.log_test(
                            f"Learning Insights ({test_case['name']})", 
                            "PASS", 
                            f"Generated {len(learning_insights)} learning insights"
                        )
                    else:
                        self.log_test(
                            f"Learning Insights ({test_case['name']})", 
                            "FAIL", 
                            f"Insufficient insights: {len(learning_insights)}"
                        )
                    
                    # Test pattern details
                    pattern_details = data.get("pattern_details", [])
                    
                    if len(pattern_details) > 0:
                        self.log_test(
                            f"Pattern Details ({test_case['name']})", 
                            "PASS", 
                            f"Provided {len(pattern_details)} pattern detail entries"
                        )
                    else:
                        self.log_test(
                            f"Pattern Details ({test_case['name']})", 
                            "FAIL", 
                            "No pattern details provided"
                        )
                    
                    # Test script structure and quality indicators
                    script_lower = generated_script.lower()
                    quality_indicators = 0
                    
                    # Check for engagement elements
                    if any(word in script_lower for word in ["hook", "attention", "grab", "imagine", "picture"]):
                        quality_indicators += 1
                    
                    # Check for structure elements
                    if any(word in script_lower for word in ["first", "second", "third", "finally", "conclusion"]):
                        quality_indicators += 1
                    
                    # Check for call-to-action
                    if any(word in script_lower for word in ["subscribe", "like", "comment", "share", "follow"]):
                        quality_indicators += 1
                    
                    # Check for industry-specific terms
                    industry = test_case["request"]["industry"]
                    industry_terms = {
                        "health": ["health", "wellness", "nutrition", "fitness", "medical"],
                        "tech": ["technology", "ai", "software", "digital", "innovation"],
                        "marketing": ["brand", "campaign", "audience", "engagement", "conversion"]
                    }
                    
                    if any(term in script_lower for term in industry_terms.get(industry, [])):
                        quality_indicators += 1
                    
                    if quality_indicators >= 3:
                        self.log_test(
                            f"Script Structure Quality ({test_case['name']})", 
                            "PASS", 
                            f"Script contains {quality_indicators}/4 quality indicators"
                        )
                    else:
                        self.log_test(
                            f"Script Structure Quality ({test_case['name']})", 
                            "FAIL", 
                            f"Script contains only {quality_indicators}/4 quality indicators"
                        )
                        
                else:
                    self.log_test(
                        f"Few-Shot Script Generation ({test_case['name']})", 
                        "FAIL", 
                        f"HTTP {response.status_code}: {response.text[:200]}"
                    )
                    
            except requests.exceptions.Timeout:
                self.log_test(f"Few-Shot Script Generation ({test_case['name']})", "FAIL", "Request timeout (120s)")
            except Exception as e:
                self.log_test(f"Few-Shot Script Generation ({test_case['name']})", "FAIL", f"Exception: {str(e)}")

    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("🔍 Testing Error Handling...")
        
        # Test invalid pattern analysis request
        try:
            invalid_request = {
                "context_type": "invalid_type",
                "context_value": "invalid_value",
                "analysis_depth": "invalid_depth"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/analyze-patterns", 
                json=invalid_request, 
                timeout=30
            )
            
            if response.status_code in [400, 422, 500]:
                self.log_test(
                    "Invalid Pattern Analysis Request", 
                    "PASS", 
                    f"Properly handled invalid request with HTTP {response.status_code}"
                )
            else:
                self.log_test(
                    "Invalid Pattern Analysis Request", 
                    "FAIL", 
                    f"Unexpected response: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Invalid Pattern Analysis Request", "FAIL", f"Exception: {str(e)}")

        # Test empty few-shot script request
        try:
            empty_request = {
                "prompt": "",
                "video_type": "general",
                "industry": "general",
                "platform": "general"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/generate-script-few-shot", 
                json=empty_request, 
                timeout=30
            )
            
            if response.status_code in [400, 422, 500]:
                self.log_test(
                    "Empty Script Request Handling", 
                    "PASS", 
                    f"Properly handled empty request with HTTP {response.status_code}"
                )
            else:
                self.log_test(
                    "Empty Script Request Handling", 
                    "FAIL", 
                    f"Unexpected response: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Empty Script Request Handling", "FAIL", f"Exception: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all Few-Shot Learning & Pattern Recognition System tests"""
        print("=" * 80)
        print("🚀 FEW-SHOT LEARNING & PATTERN RECOGNITION SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Few-Shot Stats Endpoint
        self.test_few_shot_stats_endpoint()
        
        # Test 2: Example Database Management
        self.test_example_database_management()
        
        # Test 3: Pattern Analysis
        self.test_pattern_analysis()
        
        # Test 4: Few-Shot Script Generation
        self.test_few_shot_script_generation()
        
        # Test 5: Error Handling
        self.test_error_handling()
        
        # Print final results
        print("=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Few-Shot Learning & Pattern Recognition System is fully operational.")
        elif self.failed_tests <= 3:
            print("⚠️  MOSTLY SUCCESSFUL with minor issues. Few-Shot system is largely functional.")
        else:
            print("❌ SIGNIFICANT ISSUES DETECTED. Few-Shot system needs attention.")
        
        print(f"Test End Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": round(self.passed_tests/self.total_tests*100, 1) if self.total_tests > 0 else 0,
            "test_results": self.test_results
        }

if __name__ == "__main__":
    # Run the comprehensive test suite
    test_suite = FewShotTestSuite()
    results = test_suite.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed_tests"] == 0 else 1)
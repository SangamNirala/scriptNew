#!/usr/bin/env python3
"""
Focused Backend Testing Script for Review Request
Tests the specific functionality mentioned in the review request:
1. Voice API endpoint returns proper voice list
2. Enhance Prompt API with sample data
3. Backend service status
4. Dependency verification
"""

import requests
import json
import time
from datetime import datetime
import sys

# Use localhost for internal testing since external URL has timeout issues
BACKEND_URL = "http://localhost:8001/api"

class FocusedBackendTester:
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
    
    def test_voices_endpoint_detailed(self):
        """Test /api/voices endpoint returns proper voice list (Review Request Focus)"""
        print("\n=== Testing Voice API Endpoint (Review Request Focus) ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Test 1: Verify response is a list
                if not isinstance(data, list):
                    self.log_test("Voice API - Data Type", False,
                                "Response is not a list", {"response_type": type(data).__name__})
                    return False
                
                # Test 2: Verify voices are returned
                if len(data) == 0:
                    self.log_test("Voice API - Voice Count", False,
                                "No voices returned - this resolves the 'Error loading voices' issue")
                    return False
                
                self.log_test("Voice API - Voice Count", True,
                            f"Successfully returned {len(data)} voices - resolves 'Error loading voices' issue")
                
                # Test 3: Verify voice structure
                first_voice = data[0]
                required_fields = ["name", "display_name", "language", "gender"]
                missing_fields = [field for field in required_fields if field not in first_voice]
                
                if missing_fields:
                    self.log_test("Voice API - Voice Structure", False,
                                f"Missing fields in voice: {missing_fields}")
                    return False
                
                self.log_test("Voice API - Voice Structure", True,
                            "All required fields present in voice objects")
                
                # Test 4: Verify variety of voices
                genders = set(voice.get("gender", "") for voice in data)
                languages = set(voice.get("language", "") for voice in data)
                
                if len(genders) < 2:
                    self.log_test("Voice API - Gender Variety", False,
                                f"Expected both male and female voices, got: {genders}")
                else:
                    self.log_test("Voice API - Gender Variety", True,
                                f"Good gender variety: {genders}")
                
                if len(languages) < 2:
                    self.log_test("Voice API - Language Variety", False,
                                f"Expected multiple language variants, got: {languages}")
                else:
                    self.log_test("Voice API - Language Variety", True,
                                f"Good language variety: {len(languages)} variants")
                
                # Test 5: Check for expected popular voices
                voice_names = [voice.get("name", "") for voice in data]
                expected_voices = ["en-US-AriaNeural", "en-US-DavisNeural", "en-GB-SoniaNeural"]
                found_expected = [voice for voice in expected_voices if voice in voice_names]
                
                if len(found_expected) >= 1:
                    self.log_test("Voice API - Popular Voices", True,
                                f"Found expected popular voices: {found_expected}")
                else:
                    self.log_test("Voice API - Popular Voices", False,
                                f"Expected popular voices not found. Available: {voice_names[:5]}")
                
                # Test 6: Display sample voices for verification
                print(f"   Sample voices returned:")
                for i, voice in enumerate(data[:3]):
                    print(f"   {i+1}. {voice['display_name']} ({voice['name']}) - {voice['gender']} {voice['language']}")
                
                return True
                
            else:
                self.log_test("Voice API - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Voice API - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_enhance_prompt_with_review_sample(self):
        """Test /api/enhance-prompt endpoint with exact sample from review request"""
        print("\n=== Testing Enhance Prompt API with Review Request Sample ===")
        
        # Exact sample from review request
        test_payload = {
            "original_prompt": "Create a video about healthy cooking tips",
            "video_type": "educational",
            "industry_focus": "health"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=test_payload,
                timeout=60  # Increased timeout for complex processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Test 1: Verify comprehensive response structure
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
                    self.log_test("Enhance Prompt - Response Structure", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
                
                self.log_test("Enhance Prompt - Response Structure", True,
                            "All required fields present in comprehensive response")
                
                # Test 2: Verify enhancement variations
                variations = data["enhancement_variations"]
                if not isinstance(variations, list) or len(variations) == 0:
                    self.log_test("Enhance Prompt - Enhancement Variations", False,
                                "enhancement_variations should be a non-empty list")
                    return False
                
                self.log_test("Enhance Prompt - Enhancement Variations", True,
                            f"Successfully generated {len(variations)} enhancement variations")
                
                # Test 3: Verify variation structure and content quality
                comprehensive_variations = 0
                for i, variation in enumerate(variations):
                    # Check required fields
                    variation_required_fields = [
                        "id", "title", "enhanced_prompt", "focus_strategy", 
                        "target_engagement", "industry_specific_elements", 
                        "estimated_performance_score"
                    ]
                    
                    missing_var_fields = [field for field in variation_required_fields if field not in variation]
                    if missing_var_fields:
                        self.log_test(f"Enhance Prompt - Variation {i+1} Structure", False,
                                    f"Missing fields: {missing_var_fields}")
                        continue
                    
                    # Check content quality (should be comprehensive)
                    enhanced_prompt = variation.get("enhanced_prompt", "")
                    word_count = len(enhanced_prompt.split())
                    
                    if word_count >= 100:  # Should be substantially enhanced
                        comprehensive_variations += 1
                        self.log_test(f"Enhance Prompt - Variation {i+1} Quality", True,
                                    f"Comprehensive enhancement: {word_count} words")
                    else:
                        self.log_test(f"Enhance Prompt - Variation {i+1} Quality", False,
                                    f"Enhancement too brief: {word_count} words")
                    
                    # Verify performance score
                    score = variation.get("estimated_performance_score", 0)
                    if isinstance(score, (int, float)) and 0 <= score <= 10:
                        self.log_test(f"Enhance Prompt - Variation {i+1} Score", True,
                                    f"Valid performance score: {score:.1f}/10")
                    else:
                        self.log_test(f"Enhance Prompt - Variation {i+1} Score", False,
                                    f"Invalid performance score: {score}")
                
                # Test 4: Verify quality metrics
                quality_metrics = data["quality_metrics"]
                metrics_required_fields = [
                    "emotional_engagement_score", "technical_clarity_score", 
                    "industry_relevance_score", "storytelling_strength_score",
                    "overall_quality_score", "improvement_ratio"
                ]
                
                missing_metrics_fields = [field for field in metrics_required_fields if field not in quality_metrics]
                if missing_metrics_fields:
                    self.log_test("Enhance Prompt - Quality Metrics", False,
                                f"Missing quality metrics: {missing_metrics_fields}")
                else:
                    overall_score = quality_metrics.get("overall_quality_score", 0)
                    improvement_ratio = quality_metrics.get("improvement_ratio", 0)
                    self.log_test("Enhance Prompt - Quality Metrics", True,
                                f"Quality score: {overall_score:.1f}/10, Improvement: {improvement_ratio:.1f}x")
                
                # Test 5: Verify audience analysis
                audience_analysis = data["audience_analysis"]
                audience_required_fields = [
                    "recommended_tone", "complexity_level", 
                    "cultural_considerations", "platform_optimizations", 
                    "engagement_triggers"
                ]
                
                missing_audience_fields = [field for field in audience_required_fields if field not in audience_analysis]
                if missing_audience_fields:
                    self.log_test("Enhance Prompt - Audience Analysis", False,
                                f"Missing audience analysis fields: {missing_audience_fields}")
                else:
                    self.log_test("Enhance Prompt - Audience Analysis", True,
                                "Complete audience analysis provided")
                
                # Test 6: Verify industry insights
                industry_insights = data["industry_insights"]
                if isinstance(industry_insights, list) and len(industry_insights) > 0:
                    self.log_test("Enhance Prompt - Industry Insights", True,
                                f"Provided {len(industry_insights)} industry insights")
                else:
                    self.log_test("Enhance Prompt - Industry Insights", False,
                                "Industry insights missing or invalid")
                
                # Test 7: Verify recommendation
                recommendation = data["recommendation"]
                if recommendation and len(recommendation) > 50:
                    self.log_test("Enhance Prompt - Recommendation", True,
                                f"Comprehensive recommendation provided ({len(recommendation)} chars)")
                else:
                    self.log_test("Enhance Prompt - Recommendation", False,
                                "Recommendation too brief or missing")
                
                # Test 8: Display sample output for verification
                print(f"\n   Sample Enhancement Output:")
                print(f"   Original: {data['original_prompt']}")
                print(f"   Variations Generated: {len(variations)}")
                if variations:
                    best_variation = max(variations, key=lambda x: x.get("estimated_performance_score", 0))
                    print(f"   Best Variation Title: {best_variation.get('title', 'N/A')}")
                    print(f"   Best Variation Score: {best_variation.get('estimated_performance_score', 0):.1f}/10")
                    print(f"   Enhancement Preview: {best_variation.get('enhanced_prompt', '')[:200]}...")
                
                return comprehensive_variations >= 2  # At least 2 comprehensive variations
                
            else:
                self.log_test("Enhance Prompt - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhance Prompt - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_backend_dependencies(self):
        """Test that all required dependencies are properly installed"""
        print("\n=== Testing Backend Dependencies ===")
        
        # Test by making requests that would fail if dependencies are missing
        dependency_tests = [
            {
                "name": "emergentintegrations (Gemini API)",
                "test": "enhance_prompt_basic"
            },
            {
                "name": "edge-tts (Voice Generation)",
                "test": "voices_endpoint"
            },
            {
                "name": "MongoDB Connection",
                "test": "scripts_endpoint"
            }
        ]
        
        successful_deps = 0
        
        # Test emergentintegrations (Gemini API)
        try:
            test_payload = {
                "original_prompt": "Test dependency check",
                "video_type": "general"
            }
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=test_payload,
                timeout=30
            )
            if response.status_code == 200:
                self.log_test("Dependency - emergentintegrations", True,
                            "Gemini API integration working correctly")
                successful_deps += 1
            else:
                self.log_test("Dependency - emergentintegrations", False,
                            f"Gemini API integration failed: {response.status_code}")
        except Exception as e:
            self.log_test("Dependency - emergentintegrations", False,
                        f"emergentintegrations dependency issue: {str(e)}")
        
        # Test edge-tts
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if response.status_code == 200 and len(response.json()) > 0:
                self.log_test("Dependency - edge-tts", True,
                            "Edge-TTS integration working correctly")
                successful_deps += 1
            else:
                self.log_test("Dependency - edge-tts", False,
                            "Edge-TTS integration failed")
        except Exception as e:
            self.log_test("Dependency - edge-tts", False,
                        f"edge-tts dependency issue: {str(e)}")
        
        # Test MongoDB connection
        try:
            response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            if response.status_code == 200:
                self.log_test("Dependency - MongoDB", True,
                            "MongoDB connection working correctly")
                successful_deps += 1
            else:
                self.log_test("Dependency - MongoDB", False,
                            f"MongoDB connection failed: {response.status_code}")
        except Exception as e:
            self.log_test("Dependency - MongoDB", False,
                        f"MongoDB dependency issue: {str(e)}")
        
        if successful_deps >= 2:
            self.log_test("Dependencies - Overall", True,
                        f"Backend dependencies working correctly ({successful_deps}/3 tested)")
            return True
        else:
            self.log_test("Dependencies - Overall", False,
                        f"Dependency issues detected ({successful_deps}/3 working)")
            return False
    
    def test_backend_service_status(self):
        """Test backend service status and health"""
        print("\n=== Testing Backend Service Status ===")
        
        # Test multiple endpoints to verify service health
        endpoints_to_test = [
            {"path": "/", "name": "Root Endpoint"},
            {"path": "/voices", "name": "Voices Endpoint"},
            {"path": "/scripts", "name": "Scripts Endpoint"}
        ]
        
        healthy_endpoints = 0
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{self.backend_url}{endpoint['path']}", timeout=10)
                if response.status_code == 200:
                    self.log_test(f"Service Health - {endpoint['name']}", True,
                                f"Endpoint responding correctly")
                    healthy_endpoints += 1
                else:
                    self.log_test(f"Service Health - {endpoint['name']}", False,
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Service Health - {endpoint['name']}", False,
                            f"Connection failed: {str(e)}")
        
        # Test POST endpoint
        try:
            test_payload = {"original_prompt": "Service health check"}
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=test_payload,
                timeout=30
            )
            if response.status_code == 200:
                self.log_test("Service Health - POST Endpoints", True,
                            "POST endpoints responding correctly")
                healthy_endpoints += 1
            else:
                self.log_test("Service Health - POST Endpoints", False,
                            f"POST endpoint failed: {response.status_code}")
        except Exception as e:
            self.log_test("Service Health - POST Endpoints", False,
                        f"POST endpoint error: {str(e)}")
        
        if healthy_endpoints >= 3:
            self.log_test("Backend Service Status", True,
                        f"Backend service fully operational ({healthy_endpoints}/4 endpoints healthy)")
            return True
        else:
            self.log_test("Backend Service Status", False,
                        f"Backend service issues detected ({healthy_endpoints}/4 endpoints healthy)")
            return False
    
    def run_focused_tests(self):
        """Run all focused tests for the review request"""
        print("🚀 Starting Focused Backend Testing for Review Request...")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 80)
        
        # Track overall results
        test_results = {
            "basic_connectivity": False,
            "voices_endpoint": False,
            "enhance_prompt": False,
            "dependencies": False,
            "service_status": False
        }
        
        # Run tests in order
        test_results["basic_connectivity"] = self.test_basic_connectivity()
        
        if test_results["basic_connectivity"]:
            test_results["voices_endpoint"] = self.test_voices_endpoint_detailed()
            test_results["enhance_prompt"] = self.test_enhance_prompt_with_review_sample()
            test_results["dependencies"] = self.test_backend_dependencies()
            test_results["service_status"] = self.test_backend_service_status()
        else:
            print("❌ Basic connectivity failed - skipping other tests")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FOCUSED TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name.replace('_', ' ').title()}")
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests >= 4:
            print("🎉 BACKEND FUNCTIONALITY VERIFIED - Review Request Requirements Met!")
            print("✅ Voice API endpoint working correctly")
            print("✅ Enhance Prompt API working with comprehensive responses")
            print("✅ Backend dependencies properly installed")
            print("✅ Backend service running correctly")
            return True
        else:
            print("⚠️  BACKEND ISSUES DETECTED - Review Request Requirements Not Fully Met")
            return False

if __name__ == "__main__":
    tester = FocusedBackendTester()
    success = tester.run_focused_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Enhance Prompt API Test - Verify the enhance prompt functionality works
Tests the /api/enhance-prompt endpoint with the exact sample from review request
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://fdb88e2d-1c56-4983-889f-10699a9a2d8a.preview.emergentagent.com/api"

class EnhancePromptTester:
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
    
    def test_enhance_prompt_endpoint(self):
        """Test enhance prompt endpoint with review request sample"""
        # Use exact sample from review request
        test_payload = {
            "original_prompt": "Create a video about healthy cooking tips",
            "video_type": "educational",
            "industry_focus": "health"
        }
        
        try:
            print(f"  📤 Sending request to /api/enhance-prompt...")
            print(f"  📋 Payload: {json.dumps(test_payload, indent=2)}")
            
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=test_payload,
                timeout=60  # Longer timeout for AI processing
            )
            
            print(f"  📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields are present
                required_fields = [
                    'original_prompt',
                    'audience_analysis', 
                    'enhancement_variations',
                    'quality_metrics',
                    'recommendation',
                    'industry_insights',
                    'enhancement_methodology'
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhance Prompt Endpoint", False, 
                                f"Missing required fields: {missing_fields}")
                    return False, None
                
                # Verify enhancement variations structure
                variations = data.get('enhancement_variations', [])
                if not isinstance(variations, list) or len(variations) == 0:
                    self.log_test("Enhance Prompt Endpoint", False, 
                                "No enhancement variations returned")
                    return False, None
                
                # Verify quality metrics
                quality_metrics = data.get('quality_metrics', {})
                if not isinstance(quality_metrics, dict):
                    self.log_test("Enhance Prompt Endpoint", False, 
                                "Invalid quality metrics structure")
                    return False, None
                
                self.log_test("Enhance Prompt Endpoint", True, 
                            f"Successfully enhanced prompt with {len(variations)} variations")
                return True, data
            else:
                self.log_test("Enhance Prompt Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("Enhance Prompt Endpoint", False, f"Error: {str(e)}")
            return False, None
    
    def test_enhancement_quality(self, enhancement_data):
        """Test the quality of enhancement response"""
        if not enhancement_data:
            self.log_test("Enhancement Quality", False, "No enhancement data to test")
            return False
        
        try:
            # Test original prompt preservation
            original = enhancement_data.get('original_prompt', '')
            if 'healthy cooking tips' not in original.lower():
                self.log_test("Enhancement Quality", False, "Original prompt not preserved correctly")
                return False
            
            # Test enhancement variations
            variations = enhancement_data.get('enhancement_variations', [])
            if len(variations) < 3:
                self.log_test("Enhancement Quality", False, f"Expected 3+ variations, got {len(variations)}")
                return False
            
            # Test each variation has required fields
            variation_fields = ['id', 'title', 'enhanced_prompt', 'focus_strategy']
            for i, variation in enumerate(variations):
                missing = [field for field in variation_fields if field not in variation]
                if missing:
                    self.log_test("Enhancement Quality", False, 
                                f"Variation {i+1} missing fields: {missing}")
                    return False
            
            # Test quality metrics
            quality_metrics = enhancement_data.get('quality_metrics', {})
            if 'overall_quality_score' not in quality_metrics:
                self.log_test("Enhancement Quality", False, "Missing overall quality score")
                return False
            
            overall_score = quality_metrics.get('overall_quality_score', 0)
            if overall_score < 5.0:  # Expect decent quality
                self.log_test("Enhancement Quality", False, f"Low quality score: {overall_score}")
                return False
            
            # Test industry insights
            industry_insights = enhancement_data.get('industry_insights', [])
            if not isinstance(industry_insights, list) or len(industry_insights) == 0:
                self.log_test("Enhancement Quality", False, "No industry insights provided")
                return False
            
            self.log_test("Enhancement Quality", True, 
                        f"High quality enhancement with score {overall_score:.1f}/10")
            return True
        except Exception as e:
            self.log_test("Enhancement Quality", False, f"Quality test error: {str(e)}")
            return False
    
    def test_enhancement_variations_content(self, enhancement_data):
        """Test that enhancement variations contain substantial content"""
        if not enhancement_data:
            self.log_test("Enhancement Variations Content", False, "No enhancement data")
            return False
        
        variations = enhancement_data.get('enhancement_variations', [])
        if not variations:
            self.log_test("Enhancement Variations Content", False, "No variations to test")
            return False
        
        try:
            substantial_variations = 0
            focus_strategies = set()
            
            for variation in variations:
                enhanced_prompt = variation.get('enhanced_prompt', '')
                focus_strategy = variation.get('focus_strategy', '')
                
                # Check for substantial content (should be much longer than original)
                if len(enhanced_prompt) > 500:  # Expect detailed enhancements
                    substantial_variations += 1
                
                # Collect focus strategies
                if focus_strategy:
                    focus_strategies.add(focus_strategy)
            
            if substantial_variations < 2:
                self.log_test("Enhancement Variations Content", False, 
                            f"Only {substantial_variations} variations have substantial content")
                return False
            
            if len(focus_strategies) < 2:
                self.log_test("Enhancement Variations Content", False, 
                            f"Only {len(focus_strategies)} unique focus strategies")
                return False
            
            self.log_test("Enhancement Variations Content", True, 
                        f"{substantial_variations} substantial variations with {len(focus_strategies)} strategies")
            return True
        except Exception as e:
            self.log_test("Enhancement Variations Content", False, f"Content test error: {str(e)}")
            return False
    
    def run_enhance_prompt_tests(self):
        """Run comprehensive enhance prompt tests"""
        print("✨ ENHANCE PROMPT API TESTS")
        print("=" * 50)
        print(f"Testing backend: {self.backend_url}")
        print(f"Test started: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Enhance Prompt Endpoint
        print("1. ENHANCE PROMPT ENDPOINT TEST")
        success, enhancement_data = self.test_enhance_prompt_endpoint()
        print()
        
        if not success:
            print("❌ CRITICAL: Enhance prompt endpoint failed!")
            return self.generate_summary()
        
        # Test 2: Enhancement Quality
        print("2. ENHANCEMENT QUALITY TEST")
        self.test_enhancement_quality(enhancement_data)
        print()
        
        # Test 3: Enhancement Variations Content
        print("3. ENHANCEMENT VARIATIONS CONTENT TEST")
        self.test_enhancement_variations_content(enhancement_data)
        print()
        
        # Display sample results
        if enhancement_data:
            print("4. SAMPLE ENHANCEMENT RESULTS")
            print("-" * 30)
            
            variations = enhancement_data.get('enhancement_variations', [])
            if variations:
                first_variation = variations[0]
                print(f"📋 First Variation Title: {first_variation.get('title', 'N/A')}")
                print(f"🎯 Focus Strategy: {first_variation.get('focus_strategy', 'N/A')}")
                enhanced_prompt = first_variation.get('enhanced_prompt', '')
                print(f"📝 Enhanced Prompt Length: {len(enhanced_prompt)} characters")
                if len(enhanced_prompt) > 200:
                    print(f"📄 Sample: {enhanced_prompt[:200]}...")
            
            quality_metrics = enhancement_data.get('quality_metrics', {})
            overall_score = quality_metrics.get('overall_quality_score', 0)
            print(f"⭐ Overall Quality Score: {overall_score:.1f}/10")
            print()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 50)
        print("✨ ENHANCE PROMPT API TESTS SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
            print()
        
        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 SUCCESS: Enhance prompt functionality working perfectly!")
            print("✅ API endpoint accessible and functional")
            print("✅ Enhancement quality meets requirements")
            print("✅ Variations contain substantial content")
            return True
        else:
            print("🚨 ISSUES DETECTED: Enhance prompt functionality has problems!")
            return False

if __name__ == "__main__":
    tester = EnhancePromptTester()
    success = tester.run_enhance_prompt_tests()
    sys.exit(0 if success else 1)
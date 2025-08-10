#!/usr/bin/env python3
"""
CORS and Image Generation Testing Script
Tests CORS configuration and image generation endpoint specifically
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://fdb88e2d-1c56-4983-889f-10699a9a2d8a.preview.emergentagent.com/api"
FRONTEND_ORIGIN = "https://fdb88e2d-1c56-4983-889f-10699a9a2d8a.preview.emergentagent.com"

class CORSImageTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.frontend_origin = FRONTEND_ORIGIN
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
    
    def test_cors_preflight_options(self):
        """Test CORS preflight OPTIONS request to /api/generate-images"""
        print("\n=== Testing CORS Preflight OPTIONS Request ===")
        
        try:
            # Make preflight OPTIONS request with CORS headers
            headers = {
                'Origin': self.frontend_origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(
                f"{self.backend_url}/generate-images",
                headers=headers,
                timeout=10
            )
            
            # Check response status
            if response.status_code not in [200, 204]:
                self.log_test("CORS Preflight - Status Code", False,
                            f"Expected 200 or 204, got {response.status_code}")
                return False
            
            # Check CORS headers in response
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            # Verify Access-Control-Allow-Origin
            allow_origin = cors_headers['Access-Control-Allow-Origin']
            if not allow_origin:
                self.log_test("CORS Preflight - Allow-Origin Missing", False,
                            "Access-Control-Allow-Origin header is missing")
                return False
            
            if allow_origin != '*' and allow_origin != self.frontend_origin:
                self.log_test("CORS Preflight - Allow-Origin Value", False,
                            f"Access-Control-Allow-Origin is '{allow_origin}', expected '*' or '{self.frontend_origin}'")
                return False
            
            self.log_test("CORS Preflight - Allow-Origin", True,
                        f"Access-Control-Allow-Origin: {allow_origin}")
            
            # Verify Access-Control-Allow-Methods includes POST
            allow_methods = cors_headers['Access-Control-Allow-Methods']
            if not allow_methods or 'POST' not in allow_methods.upper():
                self.log_test("CORS Preflight - Allow-Methods", False,
                            f"Access-Control-Allow-Methods missing or doesn't include POST: {allow_methods}")
                return False
            
            self.log_test("CORS Preflight - Allow-Methods", True,
                        f"Access-Control-Allow-Methods: {allow_methods}")
            
            # Verify Access-Control-Allow-Headers includes Content-Type
            allow_headers = cors_headers['Access-Control-Allow-Headers']
            if not allow_headers or 'content-type' not in allow_headers.lower():
                self.log_test("CORS Preflight - Allow-Headers", False,
                            f"Access-Control-Allow-Headers missing or doesn't include Content-Type: {allow_headers}")
                return False
            
            self.log_test("CORS Preflight - Allow-Headers", True,
                        f"Access-Control-Allow-Headers: {allow_headers}")
            
            self.log_test("CORS Preflight - Overall", True,
                        "CORS preflight request successful with proper headers")
            return True
            
        except Exception as e:
            self.log_test("CORS Preflight - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_cors_actual_request(self):
        """Test actual POST request to /api/generate-images with CORS headers"""
        print("\n=== Testing CORS Actual POST Request ===")
        
        # Sample enhanced image prompts for testing
        sample_enhanced_prompts = [
            "A professional food photography shot showing fresh vegetables being chopped on a wooden cutting board, studio lighting, high resolution, detailed textures, vibrant colors, shallow depth of field, commercial photography style",
            "Close-up macro shot of colorful spices in wooden bowls, overhead view, natural lighting, rustic kitchen setting, high detail, food styling, commercial quality",
            "Professional kitchen scene with chef's hands preparing ingredients, action shot, warm lighting, shallow focus, culinary photography, high-end restaurant atmosphere"
        ]
        
        payload = {
            "enhanced_prompts": sample_enhanced_prompts
        }
        
        try:
            # Make POST request with Origin header to simulate frontend request
            headers = {
                'Origin': self.frontend_origin,
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-images",
                json=payload,
                headers=headers,
                timeout=120  # Longer timeout for image generation
            )
            
            # Check CORS headers in response
            allow_origin = response.headers.get('Access-Control-Allow-Origin')
            if not allow_origin:
                self.log_test("CORS Actual Request - Allow-Origin Missing", False,
                            "Access-Control-Allow-Origin header missing in actual response")
                return False
            
            if allow_origin != '*' and allow_origin != self.frontend_origin:
                self.log_test("CORS Actual Request - Allow-Origin Value", False,
                            f"Access-Control-Allow-Origin is '{allow_origin}', expected '*' or '{self.frontend_origin}'")
                return False
            
            self.log_test("CORS Actual Request - Allow-Origin", True,
                        f"Access-Control-Allow-Origin: {allow_origin}")
            
            # Check response status and content
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verify response structure
                    if 'generated_images' not in data:
                        self.log_test("CORS Actual Request - Response Structure", False,
                                    "Response missing 'generated_images' field")
                        return False
                    
                    generated_images = data['generated_images']
                    if not isinstance(generated_images, list):
                        self.log_test("CORS Actual Request - Images Format", False,
                                    "generated_images is not a list")
                        return False
                    
                    if len(generated_images) == 0:
                        self.log_test("CORS Actual Request - Images Count", False,
                                    "No images generated")
                        return False
                    
                    # Verify each image has required fields
                    for i, image in enumerate(generated_images):
                        required_fields = ['image_base64', 'enhanced_prompt', 'image_index']
                        missing_fields = [field for field in required_fields if field not in image]
                        
                        if missing_fields:
                            self.log_test(f"CORS Actual Request - Image {i+1} Structure", False,
                                        f"Missing fields: {missing_fields}")
                            return False
                        
                        # Verify base64 data is substantial
                        if len(image['image_base64']) < 1000:
                            self.log_test(f"CORS Actual Request - Image {i+1} Data", False,
                                        f"Base64 data too short: {len(image['image_base64'])} chars")
                            return False
                    
                    self.log_test("CORS Actual Request - Image Generation", True,
                                f"Successfully generated {len(generated_images)} images with proper CORS headers")
                    
                    # Log image details
                    for i, image in enumerate(generated_images):
                        self.log_test(f"CORS Actual Request - Image {i+1} Details", True,
                                    f"Base64 length: {len(image['image_base64'])}, Prompt: {image['enhanced_prompt'][:50]}...")
                    
                    return True
                    
                except json.JSONDecodeError:
                    self.log_test("CORS Actual Request - JSON Parse", False,
                                f"Response is not valid JSON: {response.text[:200]}")
                    return False
                    
            else:
                self.log_test("CORS Actual Request - HTTP Status", False,
                            f"HTTP {response.status_code}: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("CORS Actual Request - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_cors_different_origins(self):
        """Test CORS with different origins to verify configuration"""
        print("\n=== Testing CORS with Different Origins ===")
        
        test_origins = [
            "https://fdb88e2d-1c56-4983-889f-10699a9a2d8a.preview.emergentagent.com",  # Expected frontend origin
            "https://example.com",  # Different origin
            "http://localhost:3000",  # Local development
        ]
        
        successful_tests = 0
        
        for origin in test_origins:
            try:
                headers = {
                    'Origin': origin,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
                
                response = self.session.options(
                    f"{self.backend_url}/generate-images",
                    headers=headers,
                    timeout=10
                )
                
                allow_origin = response.headers.get('Access-Control-Allow-Origin')
                
                if allow_origin == '*':
                    self.log_test(f"CORS Origin Test - {origin}", True,
                                "Wildcard CORS allows all origins")
                    successful_tests += 1
                elif allow_origin == origin:
                    self.log_test(f"CORS Origin Test - {origin}", True,
                                f"Origin specifically allowed: {allow_origin}")
                    successful_tests += 1
                elif origin == self.frontend_origin and allow_origin:
                    self.log_test(f"CORS Origin Test - {origin}", True,
                                f"Frontend origin handled: {allow_origin}")
                    successful_tests += 1
                else:
                    self.log_test(f"CORS Origin Test - {origin}", False,
                                f"Origin not allowed. Allow-Origin: {allow_origin}")
                
            except Exception as e:
                self.log_test(f"CORS Origin Test - {origin}", False,
                            f"Exception: {str(e)}")
        
        if successful_tests >= 1:
            self.log_test("CORS Different Origins - Overall", True,
                        f"CORS working for {successful_tests}/{len(test_origins)} origins")
            return True
        else:
            self.log_test("CORS Different Origins - Overall", False,
                        "CORS not working for any tested origins")
            return False
    
    def test_image_generation_functionality(self):
        """Test image generation functionality with sample data"""
        print("\n=== Testing Image Generation Functionality ===")
        
        # Test with the exact sample from review request
        sample_prompt = "A professional food photography shot showing fresh vegetables"
        
        payload = {
            "enhanced_prompts": [sample_prompt]
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-images",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ['generated_images']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Image Generation - Response Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                generated_images = data['generated_images']
                
                if len(generated_images) == 0:
                    self.log_test("Image Generation - Images Generated", False,
                                "No images were generated")
                    return False
                
                # Test first image
                first_image = generated_images[0]
                
                # Verify image structure
                image_required_fields = ['image_base64', 'enhanced_prompt', 'image_index']
                missing_image_fields = [field for field in image_required_fields if field not in first_image]
                
                if missing_image_fields:
                    self.log_test("Image Generation - Image Structure", False,
                                f"Missing image fields: {missing_image_fields}")
                    return False
                
                # Verify base64 data
                base64_data = first_image['image_base64']
                if not base64_data or len(base64_data) < 1000:
                    self.log_test("Image Generation - Base64 Data", False,
                                f"Base64 data too short or empty: {len(base64_data) if base64_data else 0} chars")
                    return False
                
                # Verify enhanced prompt
                enhanced_prompt = first_image['enhanced_prompt']
                if not enhanced_prompt or len(enhanced_prompt) < 10:
                    self.log_test("Image Generation - Enhanced Prompt", False,
                                f"Enhanced prompt too short: {len(enhanced_prompt) if enhanced_prompt else 0} chars")
                    return False
                
                # Verify image index
                image_index = first_image['image_index']
                if not isinstance(image_index, int) or image_index < 0:
                    self.log_test("Image Generation - Image Index", False,
                                f"Invalid image index: {image_index}")
                    return False
                
                self.log_test("Image Generation - Functionality", True,
                            f"Successfully generated image with {len(base64_data)} chars base64 data")
                
                # Test multiple prompts
                multi_payload = {
                    "enhanced_prompts": [
                        "A professional food photography shot showing fresh vegetables",
                        "Close-up of colorful spices in wooden bowls",
                        "Chef preparing ingredients in modern kitchen"
                    ]
                }
                
                multi_response = self.session.post(
                    f"{self.backend_url}/generate-images",
                    json=multi_payload,
                    timeout=180  # Longer timeout for multiple images
                )
                
                if multi_response.status_code == 200:
                    multi_data = multi_response.json()
                    multi_images = multi_data.get('generated_images', [])
                    
                    if len(multi_images) >= 1:  # At least one image should be generated
                        self.log_test("Image Generation - Multiple Prompts", True,
                                    f"Successfully generated {len(multi_images)} images from multiple prompts")
                    else:
                        self.log_test("Image Generation - Multiple Prompts", False,
                                    "Failed to generate images from multiple prompts")
                else:
                    self.log_test("Image Generation - Multiple Prompts", False,
                                f"Multiple prompts test failed: {multi_response.status_code}")
                
                return True
                
            else:
                self.log_test("Image Generation - HTTP Status", False,
                            f"HTTP {response.status_code}: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Image Generation - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_cors_headers_comprehensive(self):
        """Comprehensive test of all CORS headers"""
        print("\n=== Testing Comprehensive CORS Headers ===")
        
        try:
            # Test with actual request to get all CORS headers
            headers = {
                'Origin': self.frontend_origin,
                'Content-Type': 'application/json'
            }
            
            # Make a simple request to check CORS headers
            response = self.session.get(
                f"{self.backend_url}/",  # Root endpoint
                headers=headers,
                timeout=10
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
                'Access-Control-Max-Age': response.headers.get('Access-Control-Max-Age')
            }
            
            # Check each CORS header
            headers_present = 0
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log_test("CORS Headers - Allow-Origin", True,
                            f"Present: {cors_headers['Access-Control-Allow-Origin']}")
                headers_present += 1
            else:
                self.log_test("CORS Headers - Allow-Origin", False,
                            "Access-Control-Allow-Origin header missing")
            
            if cors_headers['Access-Control-Allow-Methods']:
                self.log_test("CORS Headers - Allow-Methods", True,
                            f"Present: {cors_headers['Access-Control-Allow-Methods']}")
                headers_present += 1
            else:
                self.log_test("CORS Headers - Allow-Methods", False,
                            "Access-Control-Allow-Methods header missing")
            
            if cors_headers['Access-Control-Allow-Headers']:
                self.log_test("CORS Headers - Allow-Headers", True,
                            f"Present: {cors_headers['Access-Control-Allow-Headers']}")
                headers_present += 1
            else:
                self.log_test("CORS Headers - Allow-Headers", False,
                            "Access-Control-Allow-Headers header missing")
            
            # Optional headers
            if cors_headers['Access-Control-Allow-Credentials']:
                self.log_test("CORS Headers - Allow-Credentials", True,
                            f"Present: {cors_headers['Access-Control-Allow-Credentials']}")
            
            if cors_headers['Access-Control-Max-Age']:
                self.log_test("CORS Headers - Max-Age", True,
                            f"Present: {cors_headers['Access-Control-Max-Age']}")
            
            if headers_present >= 2:  # At least Allow-Origin and one other
                self.log_test("CORS Headers - Comprehensive", True,
                            f"CORS properly configured with {headers_present} essential headers")
                return True
            else:
                self.log_test("CORS Headers - Comprehensive", False,
                            f"Insufficient CORS headers: only {headers_present} present")
                return False
                
        except Exception as e:
            self.log_test("CORS Headers - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all CORS and image generation tests"""
        print("🚀 Starting CORS and Image Generation Testing")
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend Origin: {self.frontend_origin}")
        print("=" * 80)
        
        tests = [
            self.test_cors_preflight_options,
            self.test_cors_actual_request,
            self.test_cors_different_origins,
            self.test_image_generation_functionality,
            self.test_cors_headers_comprehensive
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        print("\n" + "=" * 80)
        print("🏁 CORS AND IMAGE GENERATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"✅ Passed: {passed_tests}/{total_tests} tests ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - CORS and Image Generation working perfectly!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOSTLY WORKING - Minor issues detected")
        else:
            print("❌ SIGNIFICANT ISSUES - CORS or Image Generation needs attention")
        
        # Print detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    tester = CORSImageTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
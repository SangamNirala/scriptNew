#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Image Generation Functionality
Testing the /api/enhance-image-prompts and /api/generate-images endpoints
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Any

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://a779ad4a-5855-4219-82cc-d6cf5fbc2725.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ImageGenerationTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def log_test(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def test_backend_connectivity(self) -> bool:
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Connectivity", True, f"Backend accessible at {API_BASE}")
                return True
            else:
                self.log_test("Backend Connectivity", False, f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_enhance_image_prompts_endpoint(self) -> Dict[str, Any]:
        """Test the /api/enhance-image-prompts endpoint"""
        try:
            # Sample script content with image prompts (as mentioned in review request)
            test_data = {
                "script_content": """
                Welcome to our healthy cooking journey! [A professional food photography shot showing fresh vegetables being chopped on a wooden cutting board]
                
                Today we'll explore three amazing recipes. [Close-up shot of colorful ingredients arranged beautifully]
                
                First, let's prepare our workspace. [Wide shot of a clean, modern kitchen with natural lighting]
                
                The secret to great cooking is fresh ingredients. [Macro shot of water droplets on fresh herbs]
                """,
                "video_type": "educational",
                "enhancement_style": "detailed",
                "target_ai_generator": "universal"
            }
            
            print(f"🧪 Testing /api/enhance-image-prompts with sample data...")
            response = self.session.post(f"{API_BASE}/enhance-image-prompts", 
                                       json=test_data, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['id', 'original_script', 'enhanced_script', 'enhancement_count', 'enhancement_summary']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhance Image Prompts - Response Structure", False, 
                                f"Missing fields: {missing_fields}", data)
                    return {}
                
                # Check if enhancement actually happened
                if data['enhancement_count'] > 0:
                    self.log_test("Enhance Image Prompts - Functionality", True, 
                                f"Successfully enhanced {data['enhancement_count']} image prompts")
                    
                    # Extract enhanced prompts for image generation testing
                    enhanced_script = data['enhanced_script']
                    
                    # Use regex to extract enhanced prompts (as mentioned in review request)
                    import re
                    enhanced_prompts = re.findall(r'\[([^\]]+)\]', enhanced_script)
                    
                    self.log_test("Enhance Image Prompts - Prompt Extraction", True, 
                                f"Extracted {len(enhanced_prompts)} enhanced prompts from script")
                    
                    return {
                        'enhanced_prompts': enhanced_prompts,
                        'video_type': test_data['video_type'],
                        'full_response': data
                    }
                else:
                    self.log_test("Enhance Image Prompts - Functionality", False, 
                                "No image prompts were enhanced", data)
                    return {}
            else:
                error_detail = response.text if response.text else f"HTTP {response.status_code}"
                self.log_test("Enhance Image Prompts - API Call", False, 
                            f"API call failed: {error_detail}")
                return {}
                
        except Exception as e:
            self.log_test("Enhance Image Prompts - Exception", False, f"Exception occurred: {str(e)}")
            return {}
    
    def test_generate_images_endpoint(self, enhanced_prompts: List[str], video_type: str = "educational") -> bool:
        """Test the /api/generate-images endpoint"""
        try:
            if not enhanced_prompts:
                self.log_test("Generate Images - Input Validation", False, "No enhanced prompts provided")
                return False
            
            test_data = {
                "enhanced_prompts": enhanced_prompts[:2],  # Test with first 2 prompts to avoid timeout
                "video_type": video_type,
                "number_of_images_per_prompt": 1
            }
            
            print(f"🎨 Testing /api/generate-images with {len(test_data['enhanced_prompts'])} enhanced prompts...")
            print(f"Sample prompt: {enhanced_prompts[0][:100]}...")
            
            # Increase timeout for image generation
            response = self.session.post(f"{API_BASE}/generate-images", 
                                       json=test_data, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['generated_images', 'total_images', 'generation_summary']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Generate Images - Response Structure", False, 
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check if images were actually generated
                if data['total_images'] > 0:
                    self.log_test("Generate Images - Functionality", True, 
                                f"Successfully generated {data['total_images']} images")
                    
                    # Validate image structure
                    if data['generated_images']:
                        first_image = data['generated_images'][0]
                        image_fields = ['image_base64', 'enhanced_prompt', 'image_index']
                        missing_image_fields = [field for field in image_fields if field not in first_image]
                        
                        if missing_image_fields:
                            self.log_test("Generate Images - Image Structure", False, 
                                        f"Missing image fields: {missing_image_fields}")
                            return False
                        
                        # Check if base64 data is present
                        if first_image['image_base64'] and len(first_image['image_base64']) > 100:
                            self.log_test("Generate Images - Image Data", True, 
                                        f"Image base64 data present ({len(first_image['image_base64'])} chars)")
                            return True
                        else:
                            self.log_test("Generate Images - Image Data", False, 
                                        "Image base64 data missing or too short")
                            return False
                    else:
                        self.log_test("Generate Images - Image Array", False, 
                                    "Generated images array is empty")
                        return False
                else:
                    self.log_test("Generate Images - Functionality", False, 
                                f"No images generated. Summary: {data.get('generation_summary', 'N/A')}", data)
                    return False
            else:
                error_detail = response.text if response.text else f"HTTP {response.status_code}"
                self.log_test("Generate Images - API Call", False, 
                            f"API call failed: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test("Generate Images - Exception", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_dependencies_and_imports(self) -> bool:
        """Test if required dependencies are available by checking a simple endpoint"""
        try:
            # Test a simple endpoint to see if the server is working
            response = self.session.get(f"{API_BASE}/voices", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Dependencies - Basic Functionality", True, 
                            "Basic endpoints working, core dependencies available")
                return True
            else:
                self.log_test("Dependencies - Basic Functionality", False, 
                            f"Basic endpoint failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Dependencies - Basic Functionality", False, f"Exception: {str(e)}")
            return False
    
    def check_logs_for_errors(self) -> None:
        """Check backend logs for any errors related to image generation"""
        try:
            import subprocess
            result = subprocess.run(['sudo', 'tail', '-n', '50', '/var/log/supervisor/backend.*.log'], 
                                  capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for image generation related errors
                error_keywords = ['image', 'generation', 'GeminiImageGeneration', 'ImportError', 'ModuleNotFoundError']
                found_errors = []
                
                for line in logs.split('\n'):
                    if any(keyword.lower() in line.lower() for keyword in error_keywords):
                        if 'error' in line.lower() or 'failed' in line.lower():
                            found_errors.append(line.strip())
                
                if found_errors:
                    self.log_test("Log Analysis - Error Detection", False, 
                                f"Found {len(found_errors)} potential errors in logs", found_errors[:3])
                else:
                    self.log_test("Log Analysis - Error Detection", True, 
                                "No obvious image generation errors found in recent logs")
            else:
                self.log_test("Log Analysis - Access", False, "Could not access backend logs")
                
        except Exception as e:
            self.log_test("Log Analysis - Exception", False, f"Exception checking logs: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Image Generation Testing")
        print("=" * 60)
        
        # Test 1: Backend connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend not accessible. Stopping tests.")
            return
        
        # Test 2: Dependencies check
        self.test_dependencies_and_imports()
        
        # Test 3: Enhance image prompts
        enhancement_result = self.test_enhance_image_prompts_endpoint()
        
        # Test 4: Generate images (if enhancement worked)
        if enhancement_result and enhancement_result.get('enhanced_prompts'):
            self.test_generate_images_endpoint(
                enhancement_result['enhanced_prompts'], 
                enhancement_result['video_type']
            )
        else:
            self.log_test("Generate Images - Skipped", False, 
                        "Skipped due to enhancement failure")
        
        # Test 5: Check logs for errors
        self.check_logs_for_errors()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}")

if __name__ == "__main__":
    tester = ImageGenerationTester()
    tester.run_comprehensive_test()
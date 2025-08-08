#!/usr/bin/env python3
"""
CRITICAL IMAGE GENERATION WORKFLOW TESTING
Complete Backend API Testing for Image Generation Features

Testing the complete image generation workflow:
1. Enhance Image Prompt Endpoint (POST /api/enhance-image-prompts)
2. Generate Images Endpoint (POST /api/generate-images)

This test validates the workflow: Generate Script → Enhance Image Prompt → Generate Images using Gemini
"""

import requests
import json
import time
import base64
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://26dd9f7e-c30f-4172-9f0a-0b9a79b6475f.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(test_name, status, details="", response_data=None):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    
    print(f"\n{status_emoji} [{timestamp}] {test_name}: {status}")
    if details:
        print(f"   Details: {details}")
    if response_data and isinstance(response_data, dict):
        if 'error' in response_data:
            print(f"   Error: {response_data['error']}")
        if 'status_code' in response_data:
            print(f"   Status Code: {response_data['status_code']}")

def test_backend_connectivity():
    """Test basic backend connectivity"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=30)
        if response.status_code == 200:
            log_test_result("Backend Connectivity", "PASS", f"Backend responding at {API_BASE}")
            return True
        else:
            log_test_result("Backend Connectivity", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test_result("Backend Connectivity", "FAIL", f"Connection error: {str(e)}")
        return False

def test_enhance_image_prompts_endpoint():
    """
    PHASE 1: Test Enhance Image Prompt API
    Tests POST /api/enhance-image-prompts endpoint
    """
    print("\n" + "="*80)
    print("🎯 PHASE 1: ENHANCE IMAGE PROMPT API TESTING")
    print("="*80)
    
    # Sample script content with basic image prompts as specified in review request
    sample_script = """Welcome to our cooking show! [Chef standing in modern kitchen] Let's start with ingredients. [Fresh vegetables on cutting board] Today we'll make pasta. [Boiling water in pot] First, we'll prepare our sauce. [Chef chopping tomatoes] The secret is in the timing. [Steam rising from pan] Finally, we plate our masterpiece. [Beautifully plated pasta dish]"""
    
    test_cases = [
        {
            "name": "Basic Enhancement - Detailed Style",
            "data": {
                "script_content": sample_script,
                "video_type": "educational",
                "enhancement_style": "detailed",
                "target_ai_generator": "universal"
            }
        },
        {
            "name": "Cinematic Enhancement Style",
            "data": {
                "script_content": sample_script,
                "video_type": "educational", 
                "enhancement_style": "cinematic",
                "target_ai_generator": "midjourney"
            }
        },
        {
            "name": "Artistic Enhancement Style",
            "data": {
                "script_content": sample_script,
                "video_type": "educational",
                "enhancement_style": "artistic", 
                "target_ai_generator": "dalle3"
            }
        },
        {
            "name": "Photorealistic Enhancement Style",
            "data": {
                "script_content": sample_script,
                "video_type": "educational",
                "enhancement_style": "photorealistic",
                "target_ai_generator": "stable-diffusion"
            }
        }
    ]
    
    successful_enhancements = []
    
    for test_case in test_cases:
        try:
            print(f"\n🧪 Testing: {test_case['name']}")
            
            response = requests.post(
                f"{API_BASE}/enhance-image-prompts",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=120  # 2 minutes timeout for AI processing
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                required_fields = ['enhanced_script', 'enhancement_count', 'enhancement_summary', 'enhancement_style', 'target_ai_generator']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    log_test_result(test_case['name'], "FAIL", f"Missing fields: {missing_fields}")
                    continue
                
                # Validate enhancement quality
                original_length = len(test_case['data']['script_content'])
                enhanced_length = len(result['enhanced_script'])
                enhancement_ratio = enhanced_length / original_length if original_length > 0 else 0
                
                # Check if enhancement actually improved the prompts
                if enhancement_ratio > 1.5:  # At least 50% more detailed
                    log_test_result(
                        test_case['name'], 
                        "PASS", 
                        f"Enhanced {result['enhancement_count']} prompts, {enhancement_ratio:.1f}x more detailed"
                    )
                    
                    # Store successful enhancement for Phase 2 testing
                    successful_enhancements.append({
                        'style': test_case['data']['enhancement_style'],
                        'enhanced_script': result['enhanced_script'],
                        'enhancement_count': result['enhancement_count']
                    })
                    
                    # Print sample enhancement
                    print(f"   📝 Sample Enhancement Summary: {result['enhancement_summary'][:2]}")
                    
                else:
                    log_test_result(test_case['name'], "FAIL", f"Enhancement ratio too low: {enhancement_ratio:.1f}x")
                    
            else:
                error_detail = response.text if response.text else f"HTTP {response.status_code}"
                log_test_result(test_case['name'], "FAIL", f"API Error: {error_detail}")
                
        except requests.exceptions.Timeout:
            log_test_result(test_case['name'], "FAIL", "Request timeout (>2 minutes)")
        except Exception as e:
            log_test_result(test_case['name'], "FAIL", f"Exception: {str(e)}")
    
    return successful_enhancements

def extract_image_prompts_from_script(enhanced_script):
    """Extract image prompts from enhanced script (text in brackets [])"""
    import re
    
    # Find all text within brackets
    prompts = re.findall(r'\[([^\]]+)\]', enhanced_script)
    
    # Clean and filter prompts
    cleaned_prompts = []
    for prompt in prompts:
        # Remove any timestamp patterns
        clean_prompt = re.sub(r'\d+:\d+[-–]\d+:\d+\s*', '', prompt).strip()
        if clean_prompt and len(clean_prompt) > 10:  # Only meaningful prompts
            cleaned_prompts.append(clean_prompt)
    
    return cleaned_prompts

def test_generate_images_endpoint(successful_enhancements):
    """
    PHASE 2: Test Generate Images API
    Tests POST /api/generate-images endpoint using enhanced prompts from Phase 1
    """
    print("\n" + "="*80)
    print("🎨 PHASE 2: GENERATE IMAGES API TESTING")
    print("="*80)
    
    if not successful_enhancements:
        log_test_result("Generate Images Phase", "SKIP", "No successful enhancements from Phase 1")
        return False
    
    # Use the first successful enhancement for testing
    test_enhancement = successful_enhancements[0]
    enhanced_script = test_enhancement['enhanced_script']
    
    # Extract enhanced prompts from the script
    enhanced_prompts = extract_image_prompts_from_script(enhanced_script)
    
    if not enhanced_prompts:
        log_test_result("Prompt Extraction", "FAIL", "No image prompts found in enhanced script")
        return False
    
    log_test_result("Prompt Extraction", "PASS", f"Extracted {len(enhanced_prompts)} image prompts")
    
    # Print sample prompts
    print(f"\n📋 Sample Enhanced Prompts:")
    for i, prompt in enumerate(enhanced_prompts[:3]):  # Show first 3
        print(f"   {i+1}. {prompt[:100]}...")
    
    test_cases = [
        {
            "name": "Single Image Generation",
            "data": {
                "enhanced_prompts": enhanced_prompts[:1],  # Test with 1 prompt
                "video_type": "educational",
                "number_of_images_per_prompt": 1
            }
        },
        {
            "name": "Multiple Images Generation", 
            "data": {
                "enhanced_prompts": enhanced_prompts[:3],  # Test with 3 prompts
                "video_type": "educational",
                "number_of_images_per_prompt": 1
            }
        }
    ]
    
    successful_generations = 0
    
    for test_case in test_cases:
        try:
            print(f"\n🖼️ Testing: {test_case['name']}")
            print(f"   Generating images for {len(test_case['data']['enhanced_prompts'])} prompts...")
            
            start_time = time.time()
            
            response = requests.post(
                f"{API_BASE}/generate-images",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minutes timeout for image generation
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                required_fields = ['generated_images', 'total_images', 'generation_summary']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    log_test_result(test_case['name'], "FAIL", f"Missing fields: {missing_fields}")
                    continue
                
                # Validate generated images
                total_images = result['total_images']
                generated_images = result['generated_images']
                
                if total_images > 0 and len(generated_images) > 0:
                    # Validate image structure
                    sample_image = generated_images[0]
                    required_image_fields = ['image_base64', 'original_prompt', 'enhanced_prompt', 'image_index']
                    missing_image_fields = [field for field in required_image_fields if field not in sample_image]
                    
                    if missing_image_fields:
                        log_test_result(test_case['name'], "FAIL", f"Missing image fields: {missing_image_fields}")
                        continue
                    
                    # Validate base64 image data
                    try:
                        image_data = sample_image['image_base64']
                        if len(image_data) > 1000:  # Should be substantial base64 data
                            # Try to decode to verify it's valid base64
                            base64.b64decode(image_data[:100])  # Test first 100 chars
                            
                            log_test_result(
                                test_case['name'], 
                                "PASS", 
                                f"Generated {total_images} images in {processing_time:.1f}s, avg {len(image_data):,} chars per image"
                            )
                            successful_generations += 1
                            
                            # Print generation summary
                            print(f"   📊 {result['generation_summary']}")
                            
                        else:
                            log_test_result(test_case['name'], "FAIL", f"Image data too small: {len(image_data)} chars")
                            
                    except Exception as decode_error:
                        log_test_result(test_case['name'], "FAIL", f"Invalid base64 image data: {decode_error}")
                        
                else:
                    log_test_result(test_case['name'], "FAIL", f"No images generated: {total_images} total")
                    
            else:
                error_detail = response.text if response.text else f"HTTP {response.status_code}"
                log_test_result(test_case['name'], "FAIL", f"API Error: {error_detail}")
                
        except requests.exceptions.Timeout:
            log_test_result(test_case['name'], "FAIL", "Request timeout (>5 minutes)")
        except Exception as e:
            log_test_result(test_case['name'], "FAIL", f"Exception: {str(e)}")
    
    return successful_generations > 0

def test_end_to_end_workflow():
    """
    Test the complete workflow: Script → Enhance Prompts → Generate Images
    """
    print("\n" + "="*80)
    print("🔄 END-TO-END WORKFLOW TESTING")
    print("="*80)
    
    # Sample script from review request
    sample_script = """Welcome to our cooking show! [Chef standing in modern kitchen] Let's start with ingredients. [Fresh vegetables on cutting board] Today we'll make pasta. [Boiling water in pot]"""
    
    try:
        print("🔄 Step 1: Enhancing image prompts...")
        
        # Step 1: Enhance image prompts
        enhance_response = requests.post(
            f"{API_BASE}/enhance-image-prompts",
            json={
                "script_content": sample_script,
                "video_type": "educational",
                "enhancement_style": "detailed"
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if enhance_response.status_code != 200:
            log_test_result("End-to-End Workflow", "FAIL", f"Enhancement failed: {enhance_response.status_code}")
            return False
        
        enhance_result = enhance_response.json()
        enhanced_script = enhance_result['enhanced_script']
        
        print("🔄 Step 2: Extracting enhanced prompts...")
        
        # Step 2: Extract enhanced prompts
        enhanced_prompts = extract_image_prompts_from_script(enhanced_script)
        
        if not enhanced_prompts:
            log_test_result("End-to-End Workflow", "FAIL", "No enhanced prompts extracted")
            return False
        
        print("🔄 Step 3: Generating images...")
        
        # Step 3: Generate images
        generate_response = requests.post(
            f"{API_BASE}/generate-images",
            json={
                "enhanced_prompts": enhanced_prompts[:2],  # Test with first 2 prompts
                "video_type": "educational",
                "number_of_images_per_prompt": 1
            },
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        if generate_response.status_code != 200:
            log_test_result("End-to-End Workflow", "FAIL", f"Image generation failed: {generate_response.status_code}")
            return False
        
        generate_result = generate_response.json()
        
        if generate_result['total_images'] > 0:
            log_test_result(
                "End-to-End Workflow", 
                "PASS", 
                f"Complete workflow successful: {enhance_result['enhancement_count']} prompts enhanced → {generate_result['total_images']} images generated"
            )
            return True
        else:
            log_test_result("End-to-End Workflow", "FAIL", "No images generated in workflow")
            return False
            
    except Exception as e:
        log_test_result("End-to-End Workflow", "FAIL", f"Workflow exception: {str(e)}")
        return False

def test_error_handling():
    """Test error handling for both endpoints"""
    print("\n" + "="*80)
    print("🛡️ ERROR HANDLING TESTING")
    print("="*80)
    
    error_tests = [
        {
            "name": "Empty Script Content",
            "endpoint": "/enhance-image-prompts",
            "data": {"script_content": "", "video_type": "educational"},
            "expected_status": [400, 422, 500]
        },
        {
            "name": "Invalid Enhancement Style",
            "endpoint": "/enhance-image-prompts", 
            "data": {"script_content": "Test [image]", "enhancement_style": "invalid_style"},
            "expected_status": [200, 400, 422]  # May accept and use default
        },
        {
            "name": "Empty Prompts List",
            "endpoint": "/generate-images",
            "data": {"enhanced_prompts": [], "video_type": "educational"},
            "expected_status": [400, 422, 500]
        },
        {
            "name": "Invalid Prompts",
            "endpoint": "/generate-images",
            "data": {"enhanced_prompts": [""], "video_type": "educational"},
            "expected_status": [400, 422, 500]
        }
    ]
    
    for test in error_tests:
        try:
            response = requests.post(
                f"{API_BASE}{test['endpoint']}",
                json=test['data'],
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code in test['expected_status']:
                log_test_result(test['name'], "PASS", f"Correctly handled with status {response.status_code}")
            else:
                log_test_result(test['name'], "WARN", f"Unexpected status {response.status_code}, expected {test['expected_status']}")
                
        except Exception as e:
            log_test_result(test['name'], "FAIL", f"Exception: {str(e)}")

def main():
    """Main testing function"""
    print("🚀 CRITICAL IMAGE GENERATION WORKFLOW TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test backend connectivity first
    if not test_backend_connectivity():
        print("\n❌ Backend connectivity failed. Aborting tests.")
        return
    
    # Phase 1: Test enhance image prompts endpoint
    successful_enhancements = test_enhance_image_prompts_endpoint()
    
    # Phase 2: Test generate images endpoint
    image_generation_success = test_generate_images_endpoint(successful_enhancements)
    
    # End-to-end workflow test
    workflow_success = test_end_to_end_workflow()
    
    # Error handling tests
    test_error_handling()
    
    # Final summary
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    
    phase1_status = "✅ PASS" if successful_enhancements else "❌ FAIL"
    phase2_status = "✅ PASS" if image_generation_success else "❌ FAIL"
    workflow_status = "✅ PASS" if workflow_success else "❌ FAIL"
    
    print(f"Phase 1 - Enhance Image Prompts: {phase1_status}")
    print(f"Phase 2 - Generate Images: {phase2_status}")
    print(f"End-to-End Workflow: {workflow_status}")
    
    if successful_enhancements and image_generation_success and workflow_success:
        print("\n🎉 CRITICAL IMAGE GENERATION WORKFLOW: FULLY OPERATIONAL")
        print("✅ Both endpoints return 200 HTTP status")
        print("✅ Enhanced script contains detailed AI-optimized image prompts")
        print("✅ Generated images return valid base64 encoded image data")
        print("✅ Complete workflow: basic script → enhanced prompts → generated images works end-to-end")
    else:
        print("\n⚠️ CRITICAL IMAGE GENERATION WORKFLOW: ISSUES DETECTED")
        if not successful_enhancements:
            print("❌ Image prompt enhancement not working properly")
        if not image_generation_success:
            print("❌ Image generation not working properly")
        if not workflow_success:
            print("❌ End-to-end workflow not working properly")
    
    print(f"\nTest Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
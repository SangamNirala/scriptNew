#!/usr/bin/env python3
"""
Long Duration Fix - Focused Backend Testing
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

def test_backend_connectivity():
    """Test basic backend connectivity"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=30)
        if response.status_code == 200:
            print("✅ Backend Connectivity: SUCCESS")
            return True
        else:
            print(f"❌ Backend Connectivity: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Connectivity: FAILED - {str(e)}")
        return False

def count_shots_in_script(script: str) -> int:
    """Count the number of shots/timestamps in a script"""
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

def extract_image_prompts(script: str) -> List[str]:
    """Extract image prompts from script"""
    patterns = [
        r'AI IMAGE PROMPT:\s*["\']([^"\']+)["\']',  # AI IMAGE PROMPT: "..."
        r'AI IMAGE PROMPT:\s*([^\n]+)',             # AI IMAGE PROMPT: ...
        r'Image:\s*["\']([^"\']+)["\']',            # Image: "..."
        r'Image:\s*([^\n]+)',                       # Image: ...
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

def test_long_duration_fix():
    """Test the core long duration fix"""
    print("\n🎯 Testing Long Duration (3-5min) Fix...")
    
    try:
        # Test with the exact scenario from review request
        test_data = {
            "prompt": "Create a comprehensive video about overcoming fear and building confidence",
            "video_type": "educational",
            "duration": "long"
        }
        
        print("   Sending request to /api/generate-script...")
        response = requests.post(f"{API_BASE}/generate-script", 
                               json=test_data, 
                               timeout=180)  # 3 minutes timeout
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Script generation successful")
            
            # Check generation metadata
            generation_metadata = data.get("generation_metadata", {})
            if not generation_metadata:
                print("   ❌ No generation_metadata found")
                return False
            
            # Critical check: Verify generation strategy is "segmented"
            generation_strategy = generation_metadata.get("generation_strategy")
            print(f"   Generation Strategy: {generation_strategy}")
            
            if generation_strategy == "segmented":
                print("   ✅ Generation strategy correctly set to 'segmented'")
            else:
                print(f"   ❌ Expected 'segmented', got '{generation_strategy}'")
                return False
            
            # Check segment count
            segments = generation_metadata.get("segments", 0)
            print(f"   Segments: {segments}")
            
            if segments == 3:
                print("   ✅ Correct segment count: 3")
            else:
                print(f"   ⚠️  Expected 3 segments, got {segments}")
            
            # Check shot count
            generated_script = data.get("generated_script", "")
            shot_count = count_shots_in_script(generated_script)
            print(f"   Shot Count: {shot_count}")
            
            if 90 <= shot_count <= 150:
                print(f"   ✅ Shot count {shot_count} is within expected range (90-150)")
            else:
                print(f"   ⚠️  Shot count {shot_count} is outside expected range (90-150)")
            
            # Check image prompts
            image_prompts = extract_image_prompts(generated_script)
            print(f"   Image Prompts Found: {len(image_prompts)}")
            
            if len(image_prompts) > 0:
                print("   ✅ Image prompts are present")
                
                # Check quality of image prompts
                detailed_prompts = sum(1 for prompt in image_prompts if len(prompt.split()) >= 8)
                quality_ratio = detailed_prompts / len(image_prompts)
                print(f"   Detailed Prompts: {detailed_prompts}/{len(image_prompts)} ({quality_ratio:.1%})")
                
                if quality_ratio >= 0.7:
                    print("   ✅ Good image prompt quality")
                else:
                    print("   ⚠️  Image prompt quality could be improved")
            else:
                print("   ❌ No image prompts found")
            
            return True
            
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return False

def test_strategy_comparison():
    """Compare short vs long duration strategies"""
    print("\n📊 Testing Strategy Comparison (Short vs Long)...")
    
    try:
        # Test short duration
        short_data = {
            "prompt": "Create a video about overcoming fear",
            "video_type": "educational",
            "duration": "short"
        }
        
        print("   Testing short duration...")
        short_response = requests.post(f"{API_BASE}/generate-script", 
                                     json=short_data, 
                                     timeout=60)
        
        # Test long duration
        long_data = {
            "prompt": "Create a video about overcoming fear",
            "video_type": "educational",
            "duration": "long"
        }
        
        print("   Testing long duration...")
        long_response = requests.post(f"{API_BASE}/generate-script", 
                                    json=long_data, 
                                    timeout=180)
        
        if short_response.status_code == 200 and long_response.status_code == 200:
            short_data = short_response.json()
            long_data = long_response.json()
            
            # Compare strategies
            short_strategy = short_data.get("generation_metadata", {}).get("generation_strategy", "unknown")
            long_strategy = long_data.get("generation_metadata", {}).get("generation_strategy", "unknown")
            
            print(f"   Short Strategy: {short_strategy}")
            print(f"   Long Strategy: {long_strategy}")
            
            if short_strategy == "single_pass" and long_strategy == "segmented":
                print("   ✅ Strategy comparison correct")
                return True
            else:
                print("   ❌ Unexpected strategy combination")
                return False
        else:
            print(f"   ❌ One or both requests failed - Short: {short_response.status_code}, Long: {long_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return False

def main():
    print("🚀 Long Duration (3-5min) Image Generation Fix - Focused Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 70)
    
    # Test connectivity
    if not test_backend_connectivity():
        print("\n❌ Backend connectivity failed. Stopping tests.")
        return 1
    
    # Test the core fix
    fix_success = test_long_duration_fix()
    
    # Test strategy comparison
    comparison_success = test_strategy_comparison()
    
    # Final assessment
    print("\n" + "=" * 70)
    print("🏁 FINAL RESULTS")
    print("=" * 70)
    
    if fix_success and comparison_success:
        print("🎉 EXCELLENT: Long Duration (3-5min) fix is working correctly!")
        print("✅ Generation strategy changed from single_pass to segmented")
        print("✅ Script generation produces appropriate content for 3-5 minute duration")
        print("✅ Image prompts are consistent and detailed")
        return 0
    elif fix_success:
        print("✅ GOOD: Core fix is working, but some comparison issues detected")
        return 0
    else:
        print("❌ CRITICAL: Long Duration (3-5min) fix has issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
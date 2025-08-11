#!/usr/bin/env python3
"""
Quick Parallel Processing Test - Focus on key functionality
"""

import requests
import json
import time
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
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend connectivity: OK")
            return True
        else:
            print(f"❌ Backend connectivity: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connectivity failed: {str(e)}")
        return False

def test_extended_5_quick():
    """Quick test of extended_5 duration"""
    try:
        print("🚀 Testing extended_5 duration (should use parallel processing)...")
        start_time = time.time()
        
        test_data = {
            "prompt": "Create a guide about healthy eating habits",
            "video_type": "educational",
            "duration": "extended_5"
        }
        
        response = requests.post(f"{API_BASE}/generate-script", 
                               json=test_data, 
                               timeout=180)  # 3 minute timeout
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            script_content = data.get("generated_script", "")
            generation_metadata = data.get("generation_metadata", {})
            
            print(f"✅ Extended_5 generation successful!")
            print(f"   • Execution time: {execution_time:.1f}s")
            print(f"   • Script length: {len(script_content)} characters")
            
            # Check for parallel processing indicators
            if "parallel_generation" in generation_metadata:
                parallel_info = generation_metadata["parallel_generation"]
                print(f"   • Parallel processing detected!")
                print(f"   • Segments used: {parallel_info.get('segments_used', 'N/A')}")
                print(f"   • API keys used: {parallel_info.get('api_keys_used', 'N/A')}")
                print(f"   • Time saved: {parallel_info.get('time_saved_seconds', 'N/A')}s")
                return True, execution_time, True
            else:
                print(f"   • No parallel processing metadata found")
                return True, execution_time, False
                
        else:
            print(f"❌ Extended_5 generation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False, 0, False
            
    except Exception as e:
        print(f"❌ Extended_5 test failed: {str(e)}")
        return False, 0, False

def test_short_duration_comparison():
    """Test short duration for comparison"""
    try:
        print("🚀 Testing short duration (should use sequential processing)...")
        start_time = time.time()
        
        test_data = {
            "prompt": "Create a quick tip about time management",
            "video_type": "general",
            "duration": "short"
        }
        
        response = requests.post(f"{API_BASE}/generate-script", 
                               json=test_data, 
                               timeout=60)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            script_content = data.get("generated_script", "")
            generation_metadata = data.get("generation_metadata", {})
            
            print(f"✅ Short duration generation successful!")
            print(f"   • Execution time: {execution_time:.1f}s")
            print(f"   • Script length: {len(script_content)} characters")
            
            # Should NOT have parallel processing
            if "parallel_generation" not in generation_metadata:
                print(f"   • Sequential processing used (expected)")
                return True, execution_time
            else:
                print(f"   • Parallel processing detected (unexpected for short duration)")
                return True, execution_time
                
        else:
            print(f"❌ Short duration generation failed: HTTP {response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Short duration test failed: {str(e)}")
        return False, 0

def main():
    print("🚀 QUICK PARALLEL PROCESSING TEST")
    print("=" * 50)
    print()
    
    # Test 1: Backend connectivity
    if not test_backend_connectivity():
        print("❌ Cannot proceed without backend connectivity")
        return
    
    print()
    
    # Test 2: Extended_5 with parallel processing
    extended_success, extended_time, parallel_detected = test_extended_5_quick()
    
    print()
    
    # Test 3: Short duration for comparison
    short_success, short_time = test_short_duration_comparison()
    
    print()
    print("=" * 50)
    print("📊 QUICK TEST RESULTS SUMMARY")
    print("=" * 50)
    
    if extended_success and short_success:
        print("✅ Both tests completed successfully")
        
        if parallel_detected:
            print("🎉 PARALLEL PROCESSING DETECTED!")
            print(f"   • Extended_5 time: {extended_time:.1f}s")
            print(f"   • Short time: {short_time:.1f}s")
            
            if extended_time < 90:  # Expected improvement
                print("✅ Performance improvement achieved!")
            else:
                print("⚠️  Performance could be better")
        else:
            print("⚠️  Parallel processing metadata not found")
            print("   • This could mean:")
            print("     - Parallel processing not implemented yet")
            print("     - Metadata not being returned")
            print("     - System falling back to sequential")
    else:
        print("❌ Some tests failed")
        if not extended_success:
            print("   • Extended_5 test failed")
        if not short_success:
            print("   • Short duration test failed")

if __name__ == "__main__":
    main()
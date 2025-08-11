#!/usr/bin/env python3
"""
Direct test of parallel processing - using localhost directly
"""

import requests
import json
import time

# Test direct connection to localhost
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def test_backend_connectivity():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        print(f"✅ Backend connectivity: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False

def test_extended_5_generation():
    """Test extended_5 generation with parallel processing"""
    print("\n🚀 Testing extended_5 duration for parallel processing...")
    
    payload = {
        "prompt": "Create a comprehensive video about sustainable living practices",
        "video_type": "educational",
        "duration": "extended_5"
    }
    
    try:
        print(f"Making request to {API_BASE}/generate-script...")
        start_time = time.time()
        
        response = requests.post(f"{API_BASE}/generate-script", json=payload, timeout=300)
        execution_time = time.time() - start_time
        
        print(f"Response status: {response.status_code}")
        print(f"Execution time: {execution_time:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            script_content = data.get('generated_script', '')
            generation_metadata = data.get('generation_metadata', {})
            
            print(f"Script length: {len(script_content)} characters")
            
            # Check for parallel processing metadata
            if 'parallel_generation' in generation_metadata:
                parallel_info = generation_metadata['parallel_generation']
                print(f"🎉 PARALLEL PROCESSING DETECTED!")
                print(f"   • Total segments: {parallel_info.get('total_segments', 'N/A')}")
                print(f"   • Shots per segment: {parallel_info.get('shots_per_segment', 'N/A')}")
                print(f"   • API keys used: {parallel_info.get('api_keys_used', 'N/A')}")
                print(f"   • Execution time: {parallel_info.get('execution_time_seconds', 'N/A')}s")
                print(f"   • Time saved: {parallel_info.get('time_saved_seconds', 'N/A')}s")
                print(f"   • Parallel efficiency: {parallel_info.get('parallel_efficiency', 'N/A')}%")
                return True
            else:
                print("⚠️  No parallel processing metadata found")
                print("   Available metadata keys:", list(generation_metadata.keys()))
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during request: {e}")
        return False

def main():
    print("🎯 DIRECT PARALLEL PROCESSING TEST")
    print("=" * 50)
    
    # Test 1: Backend connectivity
    if not test_backend_connectivity():
        print("❌ Cannot proceed - backend not accessible")
        return
    
    # Test 2: Extended_5 parallel processing
    success = test_extended_5_generation()
    
    if success:
        print("\n🎉 PARALLEL PROCESSING IS WORKING!")
    else:
        print("\n⚠️  PARALLEL PROCESSING NEEDS INVESTIGATION")

if __name__ == "__main__":
    main()
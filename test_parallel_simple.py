#!/usr/bin/env python3
"""
Simple test to check parallel processing configuration
"""

import requests
import json
import time

# Test connection first
def test_basic_info():
    """Get basic backend information"""
    try:
        response = requests.get('http://127.0.0.1:8001/api/', timeout=30)
        print(f"✅ Backend is accessible: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False

def test_durations():
    """Check available durations"""
    try:
        response = requests.get('http://127.0.0.1:8001/api/durations', timeout=30)
        print(f"✅ Durations endpoint: {response.status_code}")
        if response.status_code == 200:
            durations = response.json()
            print(f"   Available durations: {durations}")
            return True
    except Exception as e:
        print(f"❌ Durations check failed: {e}")
        return False

def test_short_generation():
    """Test a simple short generation first"""
    print("\n🚀 Testing SHORT generation first...")
    
    payload = {
        "prompt": "Test video about cooking basics",
        "video_type": "educational",
        "duration": "short"
    }
    
    try:
        start_time = time.time()
        response = requests.post('http://127.0.0.1:8001/api/generate-script', 
                               json=payload, timeout=60)
        execution_time = time.time() - start_time
        
        print(f"Response status: {response.status_code}")
        print(f"Execution time: {execution_time:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            script_content = data.get('generated_script', '')
            generation_metadata = data.get('generation_metadata', {})
            
            print(f"Script length: {len(script_content)} characters")
            print(f"Generation metadata keys: {list(generation_metadata.keys())}")
            return True
        else:
            print(f"❌ Request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎯 SIMPLE PARALLEL PROCESSING CONFIGURATION TEST")
    print("=" * 60)
    
    if not test_basic_info():
        return
        
    if not test_durations():
        return
        
    if not test_short_generation():
        return
    
    print("\n✅ Basic functionality working! Ready for extended duration tests.")

if __name__ == "__main__":
    main()
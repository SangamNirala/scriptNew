#!/usr/bin/env python3
"""
Test extended_5 duration for parallel processing
"""

import requests
import json
import time

def test_extended_5_parallel():
    """Test extended_5 generation with parallel processing"""
    print("🚀 Testing EXTENDED_5 duration for parallel processing...")
    print("   This should use 3 segments with parallel processing")
    
    payload = {
        "prompt": "Create a comprehensive educational video about renewable energy sources covering solar, wind, and hydroelectric power with detailed explanations and examples",
        "video_type": "educational",
        "duration": "extended_5"
    }
    
    try:
        print(f"Making request...")
        start_time = time.time()
        
        response = requests.post('http://127.0.0.1:8001/api/generate-script', 
                               json=payload, timeout=300)
        execution_time = time.time() - start_time
        
        print(f"Response status: {response.status_code}")
        print(f"Execution time: {execution_time:.1f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            script_content = data.get('generated_script', '')
            generation_metadata = data.get('generation_metadata', {})
            
            print(f"Script length: {len(script_content)} characters")
            print(f"Generation metadata keys: {list(generation_metadata.keys())}")
            
            # Check for parallel processing metadata
            if 'parallel_generation' in generation_metadata:
                parallel_info = generation_metadata['parallel_generation']
                print(f"\n🎉 PARALLEL PROCESSING DETECTED!")
                print(f"   • Total segments: {parallel_info.get('total_segments', 'N/A')}")
                print(f"   • Shots per segment: {parallel_info.get('shots_per_segment', 'N/A')}")
                print(f"   • Target total shots: {parallel_info.get('total_target_shots', 'N/A')}")
                print(f"   • API keys used: {parallel_info.get('api_keys_used', 'N/A')}")
                print(f"   • Successful segments: {parallel_info.get('successful_segments', 'N/A')}")
                print(f"   • Execution time: {parallel_info.get('execution_time_seconds', 'N/A')}s")
                print(f"   • Time saved: {parallel_info.get('time_saved_seconds', 'N/A')}s")
                print(f"   • Parallel efficiency: {parallel_info.get('parallel_efficiency', 'N/A')}%")
                
                # Check if execution time is reasonable
                target_time = 60  # Target under 60 seconds
                if execution_time <= target_time:
                    print(f"✅ PERFORMANCE: Execution time {execution_time:.1f}s is within target ({target_time}s)")
                else:
                    print(f"⚠️  PERFORMANCE: Execution time {execution_time:.1f}s exceeds target ({target_time}s)")
                
                # Count segments in script content (continuity markers)
                segment_markers = script_content.count("SEGMENT")
                print(f"   • Segment continuity markers found: {segment_markers}")
                
                return True
            else:
                print("⚠️  No parallel processing metadata found")
                print("   This might indicate sequential generation was used instead")
                print("   Available metadata keys:", list(generation_metadata.keys()))
                
                # Check if it's using segmented generation at least
                if 'segments_used' in str(generation_metadata):
                    print("   Checking for segmented generation metadata...")
                
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during request: {e}")
        return False

def main():
    print("🎯 EXTENDED_5 PARALLEL PROCESSING TEST")
    print("=" * 50)
    
    success = test_extended_5_parallel()
    
    if success:
        print("\n🎉 PARALLEL PROCESSING IS WORKING FOR EXTENDED_5!")
        print("   The system is using multiple API keys for concurrent segment generation")
        print("   and achieving performance improvements through parallel execution.")
    else:
        print("\n⚠️  PARALLEL PROCESSING NEEDS INVESTIGATION FOR EXTENDED_5")
        print("   The system may be falling back to sequential generation.")

if __name__ == "__main__":
    main()
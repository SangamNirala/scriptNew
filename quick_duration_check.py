#!/usr/bin/env python3
"""
Quick Duration Check - Test basic functionality
"""

import requests
import json
import re

API_BASE = "http://localhost:8001/api"

def count_shots_and_words(script_content: str):
    """Quick count of shots and words"""
    if not script_content:
        return 0, 0
    
    # Count shots
    shot_patterns = [r'\[Shot \d+\]', r'Shot \d+:', r'\[\d+:\d+\-\d+:\d+\]', r'\d+:\d+\s*\-\s*\d+:\d+']
    shots = 0
    for pattern in shot_patterns:
        matches = re.findall(pattern, script_content, re.IGNORECASE)
        shots = max(shots, len(matches))
    
    if shots == 0:
        lines = [line.strip() for line in script_content.split('\n') if line.strip()]
        shots = max(1, len(lines) // 3)
    
    # Count words
    clean_content = re.sub(r'\[\d+:\d+\-\d+:\d+\]', '', script_content)
    clean_content = re.sub(r'\d+:\d+\s*\-\s*\d+:\d+', '', clean_content)
    words = len(clean_content.split())
    
    return shots, words

def test_basic_generation():
    """Test basic script generation"""
    print("Testing basic script generation...")
    
    try:
        # Test short duration first
        response = requests.post(f"{API_BASE}/generate-script", 
                               json={
                                   "prompt": "Create a video about healthy eating",
                                   "video_type": "educational",
                                   "duration": "short"
                               }, 
                               timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            script = data.get("generated_script", "")
            shots, words = count_shots_and_words(script)
            print(f"✅ SHORT generation: {shots} shots, {words} words")
            return True
        else:
            print(f"❌ SHORT generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("🔍 Quick Duration Check")
    print("=" * 40)
    
    # Test connectivity
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend: Connected")
        else:
            print(f"❌ Backend: Status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend: {str(e)}")
        return
    
    # Test basic generation
    success = test_basic_generation()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Basic functionality working")
    else:
        print("❌ Basic functionality issues detected")

if __name__ == "__main__":
    main()
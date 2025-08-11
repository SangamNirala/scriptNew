#!/usr/bin/env python3
"""
Simple Duration-Aware Script Generation Test
Focus on testing the key duration scaling functionality
"""

import requests
import json
import re
import time

API_BASE = "http://localhost:8001/api"

def count_shots_in_script(script_content: str) -> int:
    """Count the number of shots in a script"""
    if not script_content:
        return 0
        
    # Look for various shot indicators
    shot_patterns = [
        r'\[Shot \d+\]',  # [Shot 1], [Shot 2], etc.
        r'Shot \d+:',     # Shot 1:, Shot 2:, etc.
        r'\d+\.\s*\[',    # 1. [description], 2. [description], etc.
        r'\[\d+:\d+\-\d+:\d+\]',  # [0:00-0:03] timestamp format
        r'\d+:\d+\s*\-\s*\d+:\d+',  # 0:00-0:03 timestamp format
    ]
    
    total_shots = 0
    for pattern in shot_patterns:
        matches = re.findall(pattern, script_content, re.IGNORECASE)
        if matches:
            total_shots = max(total_shots, len(matches))
    
    # If no specific shot patterns found, estimate based on content structure
    if total_shots == 0:
        lines = script_content.split('\n')
        content_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        total_shots = max(1, len(content_lines) // 3)  # Rough estimate
        
    return total_shots

def count_words_in_script(script_content: str) -> int:
    """Count the total number of words in a script"""
    if not script_content:
        return 0
    
    # Remove timestamps and shot indicators for accurate word count
    clean_content = re.sub(r'\[\d+:\d+\-\d+:\d+\]', '', script_content)
    clean_content = re.sub(r'\d+:\d+\s*\-\s*\d+:\d+', '', clean_content)
    clean_content = re.sub(r'\[Shot \d+\]', '', clean_content, flags=re.IGNORECASE)
    clean_content = re.sub(r'Shot \d+:', '', clean_content, flags=re.IGNORECASE)
    
    words = clean_content.split()
    return len([word for word in words if word.strip()])

def test_duration_scaling():
    """Test duration scaling with short vs extended_10"""
    print("🔍 Testing Duration Scaling...")
    
    test_prompt = "Create a comprehensive educational video about sustainable energy solutions"
    
    # Test short duration
    print("   Testing SHORT duration...")
    short_data = {
        "prompt": test_prompt,
        "video_type": "educational",
        "duration": "short"
    }
    
    try:
        response = requests.post(f"{API_BASE}/generate-script", 
                               json=short_data, 
                               timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            short_script = data.get("generated_script", "")
            short_shots = count_shots_in_script(short_script)
            short_words = count_words_in_script(short_script)
            
            print(f"   ✅ SHORT: {short_shots} shots, {short_words} words")
        else:
            print(f"   ❌ SHORT failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ SHORT error: {str(e)}")
        return False
    
    # Test extended_10 duration
    print("   Testing EXTENDED_10 duration...")
    extended_data = {
        "prompt": test_prompt,
        "video_type": "educational", 
        "duration": "extended_10"
    }
    
    try:
        response = requests.post(f"{API_BASE}/generate-script", 
                               json=extended_data, 
                               timeout=300)  # Longer timeout for extended content
        
        if response.status_code == 200:
            data = response.json()
            extended_script = data.get("generated_script", "")
            extended_shots = count_shots_in_script(extended_script)
            extended_words = count_words_in_script(extended_script)
            
            print(f"   ✅ EXTENDED_10: {extended_shots} shots, {extended_words} words")
            
            # Check scaling
            shot_ratio = extended_shots / short_shots if short_shots > 0 else 0
            word_ratio = extended_words / short_words if short_words > 0 else 0
            
            print(f"   📊 SCALING RATIOS: {shot_ratio:.1f}x shots, {word_ratio:.1f}x words")
            
            # Check if extended_10 meets expected ranges
            expected_shots_min = 300
            expected_words_min = 12000
            
            shots_meets_target = extended_shots >= expected_shots_min
            words_meets_target = extended_words >= expected_words_min
            
            print(f"   🎯 EXTENDED_10 TARGETS:")
            print(f"      Shots: {'✅' if shots_meets_target else '❌'} {extended_shots} >= {expected_shots_min}")
            print(f"      Words: {'✅' if words_meets_target else '❌'} {extended_words} >= {expected_words_min}")
            
            # Check for dramatic scaling (at least 5x difference)
            dramatic_scaling = shot_ratio >= 5 and word_ratio >= 5
            print(f"   🚀 DRAMATIC SCALING: {'✅' if dramatic_scaling else '❌'} (5x+ required)")
            
            return shots_meets_target and words_meets_target and dramatic_scaling
            
        else:
            print(f"   ❌ EXTENDED_10 failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ EXTENDED_10 error: {str(e)}")
        return False

def main():
    print("🚀 Simple Duration-Aware Script Generation Test")
    print("=" * 60)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend connectivity: OK")
        else:
            print(f"❌ Backend connectivity failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend connectivity error: {str(e)}")
        return
    
    # Test duration scaling
    success = test_duration_scaling()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DURATION SCALING TEST: PASSED")
        print("   The system properly scales content based on duration selection.")
    else:
        print("❌ DURATION SCALING TEST: FAILED")
        print("   Duration selection may not be affecting content length properly.")

if __name__ == "__main__":
    main()
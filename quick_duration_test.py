#!/usr/bin/env python3
"""
Quick Duration-Aware Script Generation Test
Focus: Testing segment-based generation for extended_10 duration with timeout handling
"""

import asyncio
import aiohttp
import json
import time
import re
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://692556dc-9a80-418a-8d12-65b2cbc6f397.preview.emergentagent.com/api"

async def test_duration_scaling():
    """Quick test of duration scaling with timeout handling"""
    
    print("🚀 Quick Duration-Aware Script Generation Test")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    # Test connectivity
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    print("✅ Backend connectivity confirmed")
                else:
                    print(f"❌ Backend connectivity failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Backend connectivity error: {str(e)}")
            return
            
        # Test short duration (baseline)
        print("\n📊 Testing SHORT Duration (Baseline)")
        print("-" * 40)
        
        short_data = {
            "prompt": "Create a video about time management tips",
            "video_type": "educational",
            "duration": "short"
        }
        
        start_time = time.time()
        try:
            # Use shorter timeout for short duration
            timeout = aiohttp.ClientTimeout(total=60)
            async with session.post(f"{BACKEND_URL}/generate-script", json=short_data, timeout=timeout) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    script_content = data.get('generated_script', '')
                    
                    # Count shots and words
                    shot_patterns = [r'\[Shot \d+\]', r'Shot \d+:', r'\d+\.\s*\[', r'SHOT \d+']
                    shot_count = 0
                    for pattern in shot_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        shot_count = max(shot_count, len(matches))
                    
                    if shot_count == 0:
                        numbered_items = re.findall(r'^\d+\.', script_content, re.MULTILINE)
                        shot_count = len(numbered_items)
                    
                    word_count = len(script_content.split())
                    
                    print(f"✅ Short duration successful")
                    print(f"   📊 Shots: {shot_count}")
                    print(f"   📝 Words: {word_count}")
                    print(f"   ⏱️  Time: {response_time:.1f}s")
                    print(f"   📄 Length: {len(script_content)} chars")
                    
                    short_baseline = {
                        'shots': shot_count,
                        'words': word_count,
                        'time': response_time
                    }
                    
                else:
                    print(f"❌ Short duration failed: {response.status}")
                    return
                    
        except asyncio.TimeoutError:
            print("❌ Short duration test timed out")
            return
        except Exception as e:
            print(f"❌ Short duration error: {str(e)}")
            return
            
        # Test extended_10 duration with longer timeout
        print("\n🚀 Testing EXTENDED_10 Duration (10-15min)")
        print("-" * 40)
        
        extended_data = {
            "prompt": "Create a video about time management tips",
            "video_type": "educational", 
            "duration": "extended_10"
        }
        
        start_time = time.time()
        try:
            # Use much longer timeout for extended duration
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
            async with session.post(f"{BACKEND_URL}/generate-script", json=extended_data, timeout=timeout) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    script_content = data.get('generated_script', '')
                    metadata = data.get('generation_metadata', {})
                    
                    # Count shots and words
                    shot_patterns = [r'\[Shot \d+\]', r'Shot \d+:', r'\d+\.\s*\[', r'SHOT \d+']
                    shot_count = 0
                    for pattern in shot_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        shot_count = max(shot_count, len(matches))
                    
                    if shot_count == 0:
                        numbered_items = re.findall(r'^\d+\.', script_content, re.MULTILINE)
                        shot_count = len(numbered_items)
                    
                    word_count = len(script_content.split())
                    
                    print(f"✅ Extended_10 duration successful")
                    print(f"   📊 Shots: {shot_count}")
                    print(f"   📝 Words: {word_count}")
                    print(f"   ⏱️  Time: {response_time:.1f}s")
                    print(f"   📄 Length: {len(script_content)} chars")
                    
                    # Check for segmented generation metadata
                    segmented_gen = metadata.get('segmented_generation', {})
                    if segmented_gen:
                        print(f"   🧩 Segmented generation: YES")
                        print(f"   📈 Total segments: {segmented_gen.get('total_segments', 'N/A')}")
                        print(f"   🎯 Shots per segment: {segmented_gen.get('shots_per_segment', 'N/A')}")
                        print(f"   🎬 Total target shots: {segmented_gen.get('total_target_shots', 'N/A')}")
                    else:
                        print(f"   🧩 Segmented generation: NO")
                    
                    # Check for quality analysis
                    has_auto_regen = 'auto_regeneration' in metadata
                    has_quality_analysis = 'final_quality_analysis' in metadata
                    print(f"   🔄 Auto-regeneration: {'YES' if has_auto_regen else 'NO'}")
                    print(f"   📋 Quality analysis: {'YES' if has_quality_analysis else 'NO'}")
                    
                    # Compare with baseline
                    print(f"\n📈 SCALING COMPARISON:")
                    shot_ratio = shot_count / max(short_baseline['shots'], 1)
                    word_ratio = word_count / max(short_baseline['words'], 1)
                    print(f"   Shot scaling: {shot_ratio:.1f}x ({shot_count} vs {short_baseline['shots']})")
                    print(f"   Word scaling: {word_ratio:.1f}x ({word_count} vs {short_baseline['words']})")
                    
                    # Target validation
                    target_shots_min = 300
                    target_words_min = 12000
                    min_shots_threshold = int(target_shots_min * 0.7)  # 210
                    min_words_threshold = int(target_words_min * 0.7)  # 8400
                    
                    print(f"\n🎯 TARGET VALIDATION:")
                    print(f"   Target shots: 300-450 (min 210)")
                    print(f"   Actual shots: {shot_count} {'✅' if shot_count >= min_shots_threshold else '❌'}")
                    print(f"   Target words: 12,000-31,500 (min 8,400)")
                    print(f"   Actual words: {word_count:,} {'✅' if word_count >= min_words_threshold else '❌'}")
                    print(f"   10x scaling: {'✅' if shot_ratio >= 10.0 else '❌'}")
                    
                    # Overall assessment
                    checks_passed = 0
                    total_checks = 5
                    
                    if segmented_gen:
                        checks_passed += 1
                    if shot_count >= min_shots_threshold:
                        checks_passed += 1
                    if word_count >= min_words_threshold:
                        checks_passed += 1
                    if shot_ratio >= 10.0:
                        checks_passed += 1
                    if has_quality_analysis:
                        checks_passed += 1
                        
                    success_rate = (checks_passed / total_checks) * 100
                    print(f"\n🏁 OVERALL RESULT: {success_rate:.0f}% ({checks_passed}/{total_checks} checks passed)")
                    
                    if success_rate >= 80:
                        print("✅ Duration-aware scaling system working correctly!")
                    elif success_rate >= 60:
                        print("⚠️  Duration-aware scaling system partially working")
                    else:
                        print("❌ Duration-aware scaling system has significant issues")
                        
                else:
                    print(f"❌ Extended_10 duration failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text[:200]}...")
                    
        except asyncio.TimeoutError:
            print("❌ Extended_10 duration test timed out (>5 minutes)")
            print("   This suggests the segmented generation is taking too long")
        except Exception as e:
            print(f"❌ Extended_10 duration error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_duration_scaling())
#!/usr/bin/env python3
"""
Quick Backend Test for Critical Error Resolution Verification
Focus on the two reported errors from the review request
"""

import requests
import json
import time
from datetime import datetime

# Test with localhost since external URL is timing out
BACKEND_URL = "http://localhost:8001/api"

def test_critical_errors():
    """Test the two critical errors mentioned in review request"""
    print("🎯 CRITICAL ERROR RESOLUTION VERIFICATION")
    print("=" * 60)
    
    session = requests.Session()
    results = []
    
    # Test 1: "Error loading voices. Please refresh the page." - Test /api/voices endpoint
    print("\n1. Testing /api/voices endpoint (Critical Error #1)")
    try:
        response = session.get(f"{BACKEND_URL}/voices", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                # Verify voice structure
                first_voice = data[0]
                required_fields = ["name", "display_name", "language", "gender"]
                missing_fields = [field for field in required_fields if field not in first_voice]
                
                if not missing_fields:
                    print(f"✅ RESOLVED: /api/voices returns {len(data)} voices with proper structure")
                    print(f"   Sample voice: {first_voice}")
                    
                    # Check for variety
                    genders = set(voice.get("gender", "") for voice in data)
                    languages = set(voice.get("language", "") for voice in data)
                    print(f"   Gender variety: {genders}")
                    print(f"   Language variety: {len(languages)} variants")
                    results.append(("voices_endpoint", True, f"{len(data)} voices with proper structure"))
                else:
                    print(f"❌ PARTIAL: Voices returned but missing fields: {missing_fields}")
                    results.append(("voices_endpoint", False, f"Missing fields: {missing_fields}"))
            else:
                print("❌ FAILED: No voices returned or invalid format")
                results.append(("voices_endpoint", False, "No voices returned"))
        else:
            print(f"❌ FAILED: HTTP {response.status_code}: {response.text}")
            results.append(("voices_endpoint", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ FAILED: Exception - {str(e)}")
        results.append(("voices_endpoint", False, f"Exception: {str(e)}"))
    
    # Test 2: "Error enhancing prompt. Please try again." - Test /api/enhance-prompt endpoint
    print("\n2. Testing /api/enhance-prompt endpoint (Critical Error #2)")
    try:
        # Use exact sample from review request
        test_payload = {
            "original_prompt": "Create a video about healthy cooking tips",
            "video_type": "educational",
            "industry_focus": "health",
            "enhancement_count": 3
        }
        
        response = session.post(
            f"{BACKEND_URL}/enhance-prompt",
            json=test_payload,
            timeout=60  # Longer timeout for complex processing
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify comprehensive response structure
            required_fields = [
                "original_prompt", "audience_analysis", "enhancement_variations", 
                "quality_metrics", "recommendation", "industry_insights", "enhancement_methodology"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                variations = data["enhancement_variations"]
                quality_metrics = data["quality_metrics"]
                
                print(f"✅ RESOLVED: /api/enhance-prompt returns comprehensive response")
                print(f"   Enhancement variations: {len(variations)}")
                print(f"   Quality score: {quality_metrics.get('overall_quality_score', 'N/A')}/10")
                print(f"   Improvement ratio: {quality_metrics.get('improvement_ratio', 'N/A')}x")
                
                # Check variation quality
                if len(variations) >= 3:
                    best_variation = max(variations, key=lambda x: x.get("estimated_performance_score", 0))
                    print(f"   Best variation score: {best_variation.get('estimated_performance_score', 'N/A')}/10")
                    print(f"   Focus strategies: {[v.get('focus_strategy', 'N/A') for v in variations]}")
                
                results.append(("enhance_prompt_endpoint", True, f"Comprehensive response with {len(variations)} variations"))
            else:
                print(f"❌ PARTIAL: Response returned but missing fields: {missing_fields}")
                results.append(("enhance_prompt_endpoint", False, f"Missing fields: {missing_fields}"))
        else:
            print(f"❌ FAILED: HTTP {response.status_code}: {response.text[:200]}")
            results.append(("enhance_prompt_endpoint", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ FAILED: Exception - {str(e)}")
        results.append(("enhance_prompt_endpoint", False, f"Exception: {str(e)}"))
    
    # Test 3: Additional Core API Endpoints
    print("\n3. Testing Additional Core API Endpoints")
    
    # Test /api/generate-script
    try:
        script_payload = {
            "prompt": "Create a motivational video about achieving goals",
            "video_type": "general",
            "duration": "short"
        }
        
        response = session.post(f"{BACKEND_URL}/generate-script", json=script_payload, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            script = data.get("generated_script", "")
            print(f"✅ /api/generate-script: Generated {len(script)} character script")
            results.append(("generate_script", True, f"{len(script)} character script"))
        else:
            print(f"❌ /api/generate-script: HTTP {response.status_code}")
            results.append(("generate_script", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ /api/generate-script: Exception - {str(e)}")
        results.append(("generate_script", False, f"Exception: {str(e)}"))
    
    # Test /api/generate-audio (if voices are available)
    if any(result[0] == "voices_endpoint" and result[1] for result in results):
        try:
            # Get first available voice
            voices_response = session.get(f"{BACKEND_URL}/voices", timeout=15)
            if voices_response.status_code == 200:
                voices = voices_response.json()
                if voices:
                    test_voice = voices[0]["name"]
                    
                    audio_payload = {
                        "text": "Hello, this is a test of the text-to-speech functionality.",
                        "voice_name": test_voice
                    }
                    
                    response = session.post(f"{BACKEND_URL}/generate-audio", json=audio_payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data.get("audio_base64", "")
                        print(f"✅ /api/generate-audio: Generated {len(audio_base64)} chars of base64 audio")
                        results.append(("generate_audio", True, f"{len(audio_base64)} chars audio"))
                    else:
                        print(f"❌ /api/generate-audio: HTTP {response.status_code}")
                        results.append(("generate_audio", False, f"HTTP {response.status_code}"))
                        
        except Exception as e:
            print(f"❌ /api/generate-audio: Exception - {str(e)}")
            results.append(("generate_audio", False, f"Exception: {str(e)}"))
    
    # Test /api/scripts
    try:
        response = session.get(f"{BACKEND_URL}/scripts", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/scripts: Retrieved {len(data)} scripts")
            results.append(("scripts_endpoint", True, f"{len(data)} scripts retrieved"))
        else:
            print(f"❌ /api/scripts: HTTP {response.status_code}")
            results.append(("scripts_endpoint", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ /api/scripts: Exception - {str(e)}")
        results.append(("scripts_endpoint", False, f"Exception: {str(e)}"))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 CRITICAL ERROR RESOLUTION SUMMARY")
    print("=" * 60)
    
    critical_tests = [r for r in results if r[0] in ["voices_endpoint", "enhance_prompt_endpoint"]]
    other_tests = [r for r in results if r[0] not in ["voices_endpoint", "enhance_prompt_endpoint"]]
    
    critical_passed = sum(1 for r in critical_tests if r[1])
    other_passed = sum(1 for r in other_tests if r[1])
    
    print(f"Critical Error Resolution: {critical_passed}/{len(critical_tests)} RESOLVED")
    for test_name, success, message in critical_tests:
        status = "✅ RESOLVED" if success else "❌ FAILED"
        endpoint = test_name.replace("_endpoint", "").replace("_", "-")
        print(f"  {status}: /api/{endpoint} - {message}")
    
    print(f"\nAdditional API Endpoints: {other_passed}/{len(other_tests)} WORKING")
    for test_name, success, message in other_tests:
        status = "✅ WORKING" if success else "❌ FAILED"
        endpoint = test_name.replace("_endpoint", "").replace("_", "-")
        print(f"  {status}: /api/{endpoint} - {message}")
    
    # Overall assessment
    total_passed = critical_passed + other_passed
    total_tests = len(results)
    
    print(f"\nOVERALL BACKEND STATUS: {total_passed}/{total_tests} endpoints working")
    
    if critical_passed == len(critical_tests):
        print("🎉 SUCCESS: Both critical errors have been COMPLETELY RESOLVED!")
    else:
        print("⚠️  WARNING: Critical errors still present - requires immediate attention")
    
    return results

if __name__ == "__main__":
    test_critical_errors()
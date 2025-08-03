#!/usr/bin/env python3
"""
Comprehensive Backend Test for Review Request Verification
Tests all functionality mentioned in the review request
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://localhost:8001/api"

def comprehensive_backend_test():
    """Comprehensive test of all review request requirements"""
    print("🚀 COMPREHENSIVE BACKEND TESTING FOR REVIEW REQUEST")
    print("=" * 80)
    
    session = requests.Session()
    results = []
    
    # Test 1: Service Integration Testing
    print("\n📡 SERVICE INTEGRATION TESTING")
    print("-" * 40)
    
    # Test emergentintegrations library (Gemini AI integration)
    try:
        test_payload = {
            "original_prompt": "Test Gemini AI integration",
            "video_type": "general",
            "industry_focus": "general"
        }
        
        response = session.post(f"{BACKEND_URL}/enhance-prompt", json=test_payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if "enhancement_variations" in data and len(data["enhancement_variations"]) > 0:
                print("✅ Emergentintegrations library (Gemini AI) - WORKING")
                results.append(("gemini_integration", True, "Gemini AI responding correctly"))
            else:
                print("❌ Emergentintegrations library - FAILED (no variations)")
                results.append(("gemini_integration", False, "No enhancement variations"))
        else:
            print(f"❌ Emergentintegrations library - FAILED (HTTP {response.status_code})")
            results.append(("gemini_integration", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ Emergentintegrations library - FAILED ({str(e)})")
        results.append(("gemini_integration", False, f"Exception: {str(e)}"))
    
    # Test Edge-TTS voice generation functionality
    try:
        # First get voices
        voices_response = session.get(f"{BACKEND_URL}/voices", timeout=15)
        if voices_response.status_code == 200:
            voices = voices_response.json()
            if voices:
                test_voice = voices[0]["name"]
                
                # Test audio generation
                audio_payload = {
                    "text": "Testing Edge-TTS voice generation functionality for comprehensive review.",
                    "voice_name": test_voice
                }
                
                audio_response = session.post(f"{BACKEND_URL}/generate-audio", json=audio_payload, timeout=30)
                
                if audio_response.status_code == 200:
                    audio_data = audio_response.json()
                    audio_base64 = audio_data.get("audio_base64", "")
                    if len(audio_base64) > 1000:
                        print("✅ Edge-TTS voice generation - WORKING")
                        results.append(("edge_tts", True, f"{len(audio_base64)} chars audio generated"))
                    else:
                        print("❌ Edge-TTS voice generation - FAILED (insufficient audio)")
                        results.append(("edge_tts", False, "Insufficient audio generated"))
                else:
                    print(f"❌ Edge-TTS voice generation - FAILED (HTTP {audio_response.status_code})")
                    results.append(("edge_tts", False, f"HTTP {audio_response.status_code}"))
            else:
                print("❌ Edge-TTS voice generation - FAILED (no voices available)")
                results.append(("edge_tts", False, "No voices available"))
        else:
            print(f"❌ Edge-TTS voice generation - FAILED (voices endpoint HTTP {voices_response.status_code})")
            results.append(("edge_tts", False, f"Voices endpoint HTTP {voices_response.status_code}"))
            
    except Exception as e:
        print(f"❌ Edge-TTS voice generation - FAILED ({str(e)})")
        results.append(("edge_tts", False, f"Exception: {str(e)}"))
    
    # Test MongoDB connectivity for script storage
    try:
        # Generate a script to test database storage
        script_payload = {
            "prompt": "Test MongoDB connectivity and script storage",
            "video_type": "general",
            "duration": "short"
        }
        
        script_response = session.post(f"{BACKEND_URL}/generate-script", json=script_payload, timeout=45)
        
        if script_response.status_code == 200:
            script_data = script_response.json()
            script_id = script_data.get("id")
            
            # Wait a moment for database write
            time.sleep(2)
            
            # Try to retrieve scripts to verify storage
            retrieval_response = session.get(f"{BACKEND_URL}/scripts", timeout=15)
            
            if retrieval_response.status_code == 200:
                scripts = retrieval_response.json()
                script_found = any(script.get("id") == script_id for script in scripts)
                
                if script_found:
                    print("✅ MongoDB connectivity - WORKING")
                    results.append(("mongodb", True, "Script storage and retrieval working"))
                else:
                    print("❌ MongoDB connectivity - FAILED (script not found in database)")
                    results.append(("mongodb", False, "Script not persisted"))
            else:
                print(f"❌ MongoDB connectivity - FAILED (retrieval HTTP {retrieval_response.status_code})")
                results.append(("mongodb", False, f"Retrieval HTTP {retrieval_response.status_code}"))
        else:
            print(f"❌ MongoDB connectivity - FAILED (script generation HTTP {script_response.status_code})")
            results.append(("mongodb", False, f"Script generation HTTP {script_response.status_code}"))
            
    except Exception as e:
        print(f"❌ MongoDB connectivity - FAILED ({str(e)})")
        results.append(("mongodb", False, f"Exception: {str(e)}"))
    
    # Test 2: Core API Endpoints Testing (as specified in review request)
    print("\n🎯 CORE API ENDPOINTS TESTING")
    print("-" * 40)
    
    # /api/voices - Should return 8 curated voices with proper structure
    try:
        response = session.get(f"{BACKEND_URL}/voices", timeout=15)
        
        if response.status_code == 200:
            voices = response.json()
            
            if len(voices) == 8:
                # Verify structure
                required_fields = ["name", "display_name", "language", "gender"]
                all_valid = True
                
                for voice in voices:
                    missing_fields = [field for field in required_fields if field not in voice]
                    if missing_fields:
                        all_valid = False
                        break
                
                if all_valid:
                    genders = set(voice["gender"] for voice in voices)
                    languages = set(voice["language"] for voice in voices)
                    print(f"✅ /api/voices - PERFECT (8 voices, {len(genders)} genders, {len(languages)} languages)")
                    results.append(("voices_api", True, f"8 curated voices with proper structure"))
                else:
                    print(f"❌ /api/voices - FAILED (invalid structure)")
                    results.append(("voices_api", False, "Invalid voice structure"))
            else:
                print(f"❌ /api/voices - FAILED (expected 8 voices, got {len(voices)})")
                results.append(("voices_api", False, f"Got {len(voices)} voices instead of 8"))
        else:
            print(f"❌ /api/voices - FAILED (HTTP {response.status_code})")
            results.append(("voices_api", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ /api/voices - FAILED ({str(e)})")
        results.append(("voices_api", False, f"Exception: {str(e)}"))
    
    # /api/enhance-prompt - Should generate comprehensive enhanced prompts with quality metrics
    try:
        # Use exact sample from review request
        test_payload = {
            "original_prompt": "Create a video about healthy cooking tips",
            "video_type": "educational", 
            "industry_focus": "health"
        }
        
        response = session.post(f"{BACKEND_URL}/enhance-prompt", json=test_payload, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify comprehensive structure
            required_sections = [
                "original_prompt", "audience_analysis", "enhancement_variations",
                "quality_metrics", "recommendation", "industry_insights", "enhancement_methodology"
            ]
            
            missing_sections = [section for section in required_sections if section not in data]
            
            if not missing_sections:
                variations = data["enhancement_variations"]
                quality_metrics = data["quality_metrics"]
                
                # Verify quality metrics structure
                metrics_fields = [
                    "emotional_engagement_score", "technical_clarity_score",
                    "industry_relevance_score", "storytelling_strength_score", 
                    "overall_quality_score", "improvement_ratio"
                ]
                
                missing_metrics = [field for field in metrics_fields if field not in quality_metrics]
                
                if not missing_metrics and len(variations) >= 3:
                    overall_score = quality_metrics["overall_quality_score"]
                    improvement_ratio = quality_metrics["improvement_ratio"]
                    
                    print(f"✅ /api/enhance-prompt - EXCELLENT ({len(variations)} variations, {overall_score:.1f}/10 quality, {improvement_ratio:.1f}x improvement)")
                    results.append(("enhance_prompt_api", True, f"Comprehensive enhanced prompts with quality metrics"))
                else:
                    print(f"❌ /api/enhance-prompt - FAILED (missing metrics: {missing_metrics}, variations: {len(variations)})")
                    results.append(("enhance_prompt_api", False, f"Missing metrics or insufficient variations"))
            else:
                print(f"❌ /api/enhance-prompt - FAILED (missing sections: {missing_sections})")
                results.append(("enhance_prompt_api", False, f"Missing sections: {missing_sections}"))
        else:
            print(f"❌ /api/enhance-prompt - FAILED (HTTP {response.status_code})")
            results.append(("enhance_prompt_api", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ /api/enhance-prompt - FAILED ({str(e)})")
        results.append(("enhance_prompt_api", False, f"Exception: {str(e)}"))
    
    # /api/generate-script - Should generate video scripts with proper formatting
    try:
        script_payload = {
            "prompt": "Create an engaging video about productivity tips for remote workers",
            "video_type": "educational",
            "duration": "medium"
        }
        
        response = session.post(f"{BACKEND_URL}/generate-script", json=script_payload, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            script = data.get("generated_script", "")
            
            # Check for proper formatting elements
            has_scene_descriptions = "[" in script and "]" in script
            has_speaker_directions = "(" in script and ")" in script
            is_substantial = len(script) > 1000
            
            if has_scene_descriptions and has_speaker_directions and is_substantial:
                print(f"✅ /api/generate-script - EXCELLENT ({len(script)} chars with proper formatting)")
                results.append(("generate_script_api", True, f"Video script with proper formatting"))
            else:
                print(f"❌ /api/generate-script - FAILED (formatting issues: scenes={has_scene_descriptions}, directions={has_speaker_directions}, length={len(script)})")
                results.append(("generate_script_api", False, "Formatting or length issues"))
        else:
            print(f"❌ /api/generate-script - FAILED (HTTP {response.status_code})")
            results.append(("generate_script_api", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ /api/generate-script - FAILED ({str(e)})")
        results.append(("generate_script_api", False, f"Exception: {str(e)}"))
    
    # /api/generate-audio - Should generate base64 encoded audio using Edge-TTS
    try:
        # Get available voices first
        voices_response = session.get(f"{BACKEND_URL}/voices", timeout=15)
        if voices_response.status_code == 200:
            voices = voices_response.json()
            if voices:
                test_voice = voices[0]["name"]
                
                audio_payload = {
                    "text": "This is a comprehensive test of the audio generation functionality using Edge-TTS technology for the review request verification.",
                    "voice_name": test_voice
                }
                
                response = session.post(f"{BACKEND_URL}/generate-audio", json=audio_payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data.get("audio_base64", "")
                    voice_used = data.get("voice_used", "")
                    
                    if len(audio_base64) > 10000 and voice_used == test_voice:
                        print(f"✅ /api/generate-audio - EXCELLENT ({len(audio_base64)} chars base64 audio with {voice_used})")
                        results.append(("generate_audio_api", True, f"Base64 encoded audio using Edge-TTS"))
                    else:
                        print(f"❌ /api/generate-audio - FAILED (audio length: {len(audio_base64)}, voice: {voice_used})")
                        results.append(("generate_audio_api", False, "Insufficient audio or voice mismatch"))
                else:
                    print(f"❌ /api/generate-audio - FAILED (HTTP {response.status_code})")
                    results.append(("generate_audio_api", False, f"HTTP {response.status_code}"))
            else:
                print("❌ /api/generate-audio - FAILED (no voices available)")
                results.append(("generate_audio_api", False, "No voices available"))
        else:
            print(f"❌ /api/generate-audio - FAILED (voices endpoint issue)")
            results.append(("generate_audio_api", False, "Voices endpoint issue"))
            
    except Exception as e:
        print(f"❌ /api/generate-audio - FAILED ({str(e)})")
        results.append(("generate_audio_api", False, f"Exception: {str(e)}"))
    
    # /api/scripts - Should return script history
    try:
        response = session.get(f"{BACKEND_URL}/scripts", timeout=15)
        
        if response.status_code == 200:
            scripts = response.json()
            
            if isinstance(scripts, list):
                if len(scripts) > 0:
                    # Verify script structure
                    first_script = scripts[0]
                    required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                    missing_fields = [field for field in required_fields if field not in first_script]
                    
                    if not missing_fields:
                        print(f"✅ /api/scripts - EXCELLENT ({len(scripts)} scripts with proper structure)")
                        results.append(("scripts_api", True, f"Script history with proper structure"))
                    else:
                        print(f"❌ /api/scripts - FAILED (missing fields: {missing_fields})")
                        results.append(("scripts_api", False, f"Missing fields: {missing_fields}"))
                else:
                    print(f"✅ /api/scripts - OK (empty history, expected if no scripts generated)")
                    results.append(("scripts_api", True, "Empty script history"))
            else:
                print(f"❌ /api/scripts - FAILED (not a list)")
                results.append(("scripts_api", False, "Response not a list"))
        else:
            print(f"❌ /api/scripts - FAILED (HTTP {response.status_code})")
            results.append(("scripts_api", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ /api/scripts - FAILED ({str(e)})")
        results.append(("scripts_api", False, f"Exception: {str(e)}"))
    
    # Test 3: Performance and Reliability
    print("\n⚡ PERFORMANCE AND RELIABILITY TESTING")
    print("-" * 40)
    
    # Test response times
    start_time = time.time()
    try:
        response = session.get(f"{BACKEND_URL}/voices", timeout=15)
        voices_time = time.time() - start_time
        
        if response.status_code == 200 and voices_time < 5.0:
            print(f"✅ Response Time - Voices endpoint ({voices_time:.2f}s)")
            results.append(("response_time_voices", True, f"{voices_time:.2f}s response time"))
        else:
            print(f"❌ Response Time - Voices endpoint ({voices_time:.2f}s, status: {response.status_code})")
            results.append(("response_time_voices", False, f"{voices_time:.2f}s or HTTP error"))
            
    except Exception as e:
        print(f"❌ Response Time - Voices endpoint (Exception: {str(e)})")
        results.append(("response_time_voices", False, f"Exception: {str(e)}"))
    
    # Test error handling for invalid inputs
    try:
        # Test invalid voice name
        invalid_audio_payload = {
            "text": "Test invalid voice",
            "voice_name": "invalid-voice-name"
        }
        
        response = session.post(f"{BACKEND_URL}/generate-audio", json=invalid_audio_payload, timeout=30)
        
        # Should handle gracefully (either 400 error or fallback to default voice)
        if response.status_code in [400, 422] or (response.status_code == 200):
            print("✅ Error Handling - Invalid voice name handled gracefully")
            results.append(("error_handling", True, "Invalid inputs handled gracefully"))
        else:
            print(f"❌ Error Handling - Unexpected response to invalid voice: {response.status_code}")
            results.append(("error_handling", False, f"Unexpected response: {response.status_code}"))
            
    except Exception as e:
        print(f"❌ Error Handling - Exception with invalid inputs: {str(e)}")
        results.append(("error_handling", False, f"Exception: {str(e)}"))
    
    # Final Summary
    print("\n" + "=" * 80)
    print("🎉 COMPREHENSIVE BACKEND TEST RESULTS")
    print("=" * 80)
    
    # Categorize results
    critical_errors = [r for r in results if r[0] in ["voices_api", "enhance_prompt_api"]]
    core_apis = [r for r in results if r[0] in ["generate_script_api", "generate_audio_api", "scripts_api"]]
    integrations = [r for r in results if r[0] in ["gemini_integration", "edge_tts", "mongodb"]]
    performance = [r for r in results if r[0] in ["response_time_voices", "error_handling"]]
    
    def print_category(title, tests):
        passed = sum(1 for r in tests if r[1])
        print(f"\n{title}: {passed}/{len(tests)} PASSED")
        for test_name, success, message in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status}: {test_name.replace('_', ' ').title()} - {message}")
    
    print_category("🚨 CRITICAL ERROR RESOLUTION", critical_errors)
    print_category("🎯 CORE API ENDPOINTS", core_apis)
    print_category("📡 SERVICE INTEGRATIONS", integrations)
    print_category("⚡ PERFORMANCE & RELIABILITY", performance)
    
    # Overall assessment
    total_passed = sum(1 for r in results if r[1])
    total_tests = len(results)
    success_rate = (total_passed / total_tests) * 100
    
    print(f"\n🏆 OVERALL SUCCESS RATE: {total_passed}/{total_tests} ({success_rate:.1f}%)")
    
    # Critical assessment
    critical_passed = sum(1 for r in critical_errors if r[1])
    if critical_passed == len(critical_errors):
        print("🎉 SUCCESS: Both reported critical errors have been COMPLETELY RESOLVED!")
    else:
        print("⚠️  WARNING: Critical errors still present!")
    
    # Service integration assessment
    integration_passed = sum(1 for r in integrations if r[1])
    if integration_passed == len(integrations):
        print("🎉 SUCCESS: All service integrations are working perfectly!")
    else:
        print(f"⚠️  WARNING: {len(integrations) - integration_passed} service integration issues detected!")
    
    # Final verdict
    if success_rate >= 90 and critical_passed == len(critical_errors):
        print("\n🚀 VERDICT: Backend is PRODUCTION READY with all critical issues resolved!")
    elif success_rate >= 80:
        print("\n⚠️  VERDICT: Backend is mostly functional but needs minor fixes")
    else:
        print("\n❌ VERDICT: Backend has significant issues requiring immediate attention")
    
    return results

if __name__ == "__main__":
    comprehensive_backend_test()
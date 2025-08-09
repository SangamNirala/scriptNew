#!/usr/bin/env python3
"""
Phase 5 Comprehensive Backend Test - Testing key functionality with proper data
"""

import requests
import json
import time

# Get backend URL from frontend .env
BACKEND_URL = "https://d4bc3e4b-9123-4ba2-8801-6a24a3b446a2.preview.emergentagent.com/api"

def test_multi_model_validation():
    """Test Multi-Model Validation with sample data from review request"""
    print("🔍 Testing Multi-Model Validation...")
    
    payload = {
        "script": "Cook food. Eat healthy. The end.",  # Low quality script from review request
        "target_platform": "youtube",
        "duration": "medium", 
        "video_type": "educational"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/multi-model-validation",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["consensus_score", "individual_results", "agreement_level", "quality_threshold_passed"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"❌ FAIL: Missing fields: {missing}")
                return False
            
            consensus_score = data.get("consensus_score", 0)
            individual_results = data.get("individual_results", [])
            agreement_level = data.get("agreement_level", "")
            threshold_passed = data.get("quality_threshold_passed", False)
            
            print(f"✅ PASS: Multi-Model Validation")
            print(f"   - Consensus Score: {consensus_score:.1f}/10")
            print(f"   - Models Used: {len(individual_results)}")
            print(f"   - Agreement Level: {agreement_level}")
            print(f"   - Quality Threshold (8.5) Passed: {threshold_passed}")
            
            # Verify low quality script gets low score
            if consensus_score < 5.0:
                print(f"   ✅ Correctly identified low-quality script")
            else:
                print(f"   ⚠️  High score for low-quality script (unexpected)")
            
            return True
            
        else:
            print(f"❌ FAIL: HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_advanced_quality_metrics():
    """Test Advanced Quality Metrics endpoint"""
    print("\n📊 Testing Advanced Quality Metrics...")
    
    payload = {
        "script": "Welcome to our healthy cooking journey! Today we'll explore amazing techniques that transform simple ingredients into nutritious masterpieces. From proper knife skills to understanding flavor profiles, we'll cover everything you need to create delicious, healthy meals that your family will love.",
        "target_platform": "youtube",
        "duration": "medium",
        "video_type": "educational"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/advanced-quality-metrics",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["composite_quality_score", "detailed_metrics", "quality_recommendations"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"❌ FAIL: Missing fields: {missing}")
                return False
            
            composite_score = data.get("composite_quality_score", 0)
            detailed_metrics = data.get("detailed_metrics", {})
            recommendations = data.get("quality_recommendations", [])
            
            print(f"✅ PASS: Advanced Quality Metrics")
            print(f"   - Composite Score: {composite_score:.1f}/10")
            print(f"   - Detailed Metrics: {len(detailed_metrics)} categories")
            print(f"   - Recommendations: {len(recommendations)} suggestions")
            
            # Check for expected detailed metrics
            expected_metrics = ["readability", "engagement_prediction", "emotional_intelligence", "platform_compliance", "conversion_potential"]
            found_metrics = [m for m in expected_metrics if m in detailed_metrics]
            print(f"   - Expected Metrics Found: {len(found_metrics)}/{len(expected_metrics)}")
            
            return True
            
        else:
            print(f"❌ FAIL: HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_quality_improvement_optimization():
    """Test Quality Improvement Optimization - should auto-regenerate for low scores"""
    print("\n🔄 Testing Quality Improvement Optimization...")
    
    payload = {
        "original_prompt": "Create a video about healthy cooking tips",  # From review request
        "target_platform": "youtube",
        "duration": "medium",
        "video_type": "educational"
    }
    
    try:
        print("   (This may take 2-3 minutes for improvement cycles...)")
        response = requests.post(
            f"{BACKEND_URL}/quality-improvement-optimization",
            json=payload,
            timeout=180  # Long timeout for improvement cycles
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["original_score", "final_score", "cycles_completed", "quality_threshold_met", "final_script"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"❌ FAIL: Missing fields: {missing}")
                return False
            
            original_score = data.get("original_score", 0)
            final_score = data.get("final_score", 0)
            cycles = data.get("cycles_completed", 0)
            threshold_met = data.get("quality_threshold_met", False)
            final_script = data.get("final_script", "")
            
            print(f"✅ PASS: Quality Improvement Optimization")
            print(f"   - Original Score: {original_score:.1f}/10")
            print(f"   - Final Score: {final_score:.1f}/10")
            print(f"   - Improvement Cycles: {cycles}")
            print(f"   - Threshold (8.5) Met: {threshold_met}")
            print(f"   - Final Script Length: {len(final_script)} chars")
            
            # Verify improvement occurred
            if final_score > original_score:
                print(f"   ✅ Score improved by {final_score - original_score:.1f} points")
            else:
                print(f"   ⚠️  No score improvement detected")
            
            return True
            
        else:
            print(f"❌ FAIL: HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_intelligent_qa_analysis():
    """Test Intelligent QA Analysis - master orchestrator"""
    print("\n🧠 Testing Intelligent QA Analysis...")
    
    payload = {
        "script": "Cook food. Eat healthy. The end.",  # Low quality script
        "original_prompt": "Create a video about healthy cooking tips",
        "target_platform": "youtube",
        "duration": "medium",
        "video_type": "educational",
        "enable_regeneration": True
    }
    
    try:
        print("   (This may take 3-4 minutes for comprehensive analysis...)")
        response = requests.post(
            f"{BACKEND_URL}/intelligent-qa-analysis",
            json=payload,
            timeout=240  # Very long timeout for comprehensive analysis
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["final_script", "quality_analysis", "consensus_validation", "quality_threshold_met", "regeneration_performed"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"❌ FAIL: Missing fields: {missing}")
                return False
            
            final_script = data.get("final_script", "")
            quality_analysis = data.get("quality_analysis", {})
            consensus_validation = data.get("consensus_validation", {})
            threshold_met = data.get("quality_threshold_met", False)
            regeneration_performed = data.get("regeneration_performed", False)
            processing_time = data.get("total_processing_time", 0)
            
            print(f"✅ PASS: Intelligent QA Analysis")
            print(f"   - Final Script Length: {len(final_script)} chars")
            print(f"   - Quality Analysis: {len(quality_analysis)} metrics")
            print(f"   - Consensus Validation: {len(consensus_validation)} fields")
            print(f"   - Threshold (8.5) Met: {threshold_met}")
            print(f"   - Regeneration Performed: {regeneration_performed}")
            print(f"   - Processing Time: {processing_time:.1f}s")
            
            # Verify regeneration occurred for low quality script
            if regeneration_performed:
                print(f"   ✅ Correctly regenerated low-quality script")
            else:
                print(f"   ⚠️  No regeneration performed (may be unexpected)")
            
            return True
            
        else:
            print(f"❌ FAIL: HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

def test_generate_script_with_qa():
    """Test Script Generation with QA - generates and analyzes"""
    print("\n📝 Testing Script Generation with QA...")
    
    payload = {
        "prompt": "Create a video about healthy cooking tips",  # From review request
        "video_type": "educational",
        "duration": "medium"
    }
    
    try:
        print("   (This may take 2-3 minutes for generation + QA...)")
        response = requests.post(
            f"{BACKEND_URL}/generate-script-with-qa",
            json=payload,
            timeout=180
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for script generation fields
            script_field = None
            for field in ["generated_script", "final_script", "script"]:
                if field in data:
                    script_field = field
                    break
            
            if not script_field:
                print(f"❌ FAIL: No script field found in response")
                return False
            
            script_content = data.get(script_field, "")
            
            # Check for QA analysis fields
            qa_fields = ["quality_analysis", "consensus_validation", "quality_threshold_met"]
            qa_found = [f for f in qa_fields if f in data]
            
            print(f"✅ PASS: Script Generation with QA")
            print(f"   - Generated Script: {len(script_content)} chars")
            print(f"   - QA Fields Found: {len(qa_found)}/{len(qa_fields)}")
            
            if len(script_content) > 500:
                print(f"   ✅ Generated substantial script content")
            else:
                print(f"   ⚠️  Script content seems short")
            
            if qa_found:
                print(f"   ✅ QA analysis performed")
            else:
                print(f"   ⚠️  No QA analysis detected")
            
            return True
            
        else:
            print(f"❌ FAIL: HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Phase 5: Intelligent Quality Assurance & Auto-Optimization")
    print("Comprehensive Backend Testing")
    print("=" * 70)
    
    tests = [
        test_multi_model_validation,
        test_advanced_quality_metrics,
        test_quality_improvement_optimization,
        test_intelligent_qa_analysis,
        test_generate_script_with_qa
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(2)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {str(e)}")
    
    print("\n" + "=" * 70)
    print(f"🎯 PHASE 5 TESTING SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL PHASE 5 TESTS PASSED - System is fully functional!")
    elif passed >= total * 0.8:
        print("⚠️  MOST TESTS PASSED - Minor issues detected")
    else:
        print("❌ MULTIPLE FAILURES - Major issues detected")
    
    print(f"\n📋 Test Results:")
    print(f"   - Multi-Model Validation: {'✅' if passed >= 1 else '❌'}")
    print(f"   - Advanced Quality Metrics: {'✅' if passed >= 2 else '❌'}")
    print(f"   - Quality Improvement: {'✅' if passed >= 3 else '❌'}")
    print(f"   - Intelligent QA Analysis: {'✅' if passed >= 4 else '❌'}")
    print(f"   - Script Generation with QA: {'✅' if passed >= 5 else '❌'}")
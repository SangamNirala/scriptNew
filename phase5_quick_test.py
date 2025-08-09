#!/usr/bin/env python3
"""
Simple Phase 5 Backend Test - Quick connectivity and endpoint verification
"""

import requests
import json
import time

# Get backend URL from frontend .env
BACKEND_URL = "https://57ddad44-739c-4487-b1cc-36db80fa8192.preview.emergentagent.com/api"

def test_basic_connectivity():
    """Test basic API connectivity"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                print("✅ PASS: Basic Connectivity - API is accessible and responding")
                return True
            else:
                print(f"❌ FAIL: Basic Connectivity - Unexpected response: {data}")
                return False
        else:
            print(f"❌ FAIL: Basic Connectivity - HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Basic Connectivity - Connection failed: {str(e)}")
        return False

def test_phase5_endpoints_exist():
    """Test if Phase 5 endpoints exist (just check they don't return 404)"""
    endpoints = [
        "/multi-model-validation",
        "/advanced-quality-metrics", 
        "/quality-improvement-optimization",
        "/ab-test-optimization",
        "/intelligent-qa-analysis",
        "/generate-script-with-qa"
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            # Use POST with minimal payload to check if endpoint exists
            response = requests.post(
                f"{BACKEND_URL}{endpoint}",
                json={"script": "test"},
                timeout=30
            )
            
            if response.status_code == 404:
                print(f"❌ FAIL: {endpoint} - Endpoint not found (404)")
                results.append(False)
            elif response.status_code in [422, 500]:
                # 422 = validation error (expected with minimal payload)
                # 500 = server error (might be expected with test data)
                print(f"✅ PASS: {endpoint} - Endpoint exists (status: {response.status_code})")
                results.append(True)
            elif response.status_code == 200:
                print(f"✅ PASS: {endpoint} - Endpoint working (status: 200)")
                results.append(True)
            else:
                print(f"⚠️  UNKNOWN: {endpoint} - Unexpected status: {response.status_code}")
                results.append(True)  # Assume it exists
                
        except Exception as e:
            print(f"❌ FAIL: {endpoint} - Request failed: {str(e)}")
            results.append(False)
    
    return results

def test_multi_model_validation_basic():
    """Basic test of multi-model validation endpoint"""
    payload = {
        "script": "This is a simple test script for validation.",
        "target_platform": "youtube",
        "duration": "medium",
        "video_type": "educational"
    }
    
    try:
        print("Testing multi-model validation (this may take 60+ seconds)...")
        response = requests.post(
            f"{BACKEND_URL}/multi-model-validation",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if "consensus_score" in data and "individual_results" in data:
                consensus_score = data.get("consensus_score", 0)
                individual_count = len(data.get("individual_results", []))
                print(f"✅ PASS: Multi-Model Validation - Score: {consensus_score:.1f}/10, Models: {individual_count}")
                return True
            else:
                print(f"❌ FAIL: Multi-Model Validation - Missing required fields in response")
                return False
        else:
            print(f"❌ FAIL: Multi-Model Validation - HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Multi-Model Validation - Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Phase 5 Quick Backend Test")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    if not test_basic_connectivity():
        print("❌ Basic connectivity failed. Stopping tests.")
        exit(1)
    
    print()
    
    # Test 2: Check if Phase 5 endpoints exist
    print("Testing Phase 5 endpoint existence...")
    endpoint_results = test_phase5_endpoints_exist()
    endpoints_working = sum(endpoint_results)
    total_endpoints = len(endpoint_results)
    
    print(f"\n📊 Endpoint Availability: {endpoints_working}/{total_endpoints} endpoints available")
    
    if endpoints_working == 0:
        print("❌ No Phase 5 endpoints found. Phase 5 may not be implemented.")
        exit(1)
    
    print()
    
    # Test 3: Basic functionality test of one endpoint
    test_multi_model_validation_basic()
    
    print("\n🎯 Quick test completed!")
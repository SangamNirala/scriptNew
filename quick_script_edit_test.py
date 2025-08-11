#!/usr/bin/env python3
"""
Quick Script Editing Test
"""

import requests
import json

BACKEND_URL = "https://f40cef1f-02c2-45f9-8b54-67d355c080d1.preview.emergentagent.com/api"

def test_script_editing():
    session = requests.Session()
    
    print("🚀 Testing Script Editing Functionality")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    try:
        response = session.get(f"{BACKEND_URL}/", timeout=30)
        if response.status_code == 200:
            print("✅ Backend connectivity: OK")
        else:
            print(f"❌ Backend connectivity failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend connectivity failed: {str(e)}")
        return
    
    # Test 2: Get existing scripts to find one to edit
    try:
        scripts_response = session.get(f"{BACKEND_URL}/scripts", timeout=30)
        if scripts_response.status_code == 200:
            scripts = scripts_response.json()
            print(f"✅ Retrieved {len(scripts)} existing scripts")
            
            if len(scripts) == 0:
                print("⚠️ No existing scripts found. Generating one first...")
                
                # Generate a script first
                script_payload = {
                    "prompt": "Create a short video about time management",
                    "video_type": "educational",
                    "duration": "short"
                }
                
                script_response = session.post(
                    f"{BACKEND_URL}/generate-script",
                    json=script_payload,
                    timeout=60
                )
                
                if script_response.status_code == 200:
                    script_data = script_response.json()
                    script_id = script_data["id"]
                    print(f"✅ Generated new script with ID: {script_id}")
                else:
                    print(f"❌ Failed to generate script: {script_response.status_code}")
                    return
            else:
                # Use the first existing script
                script_id = scripts[0]["id"]
                print(f"✅ Using existing script ID: {script_id}")
                
        else:
            print(f"❌ Failed to retrieve scripts: {scripts_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error retrieving scripts: {str(e)}")
        return
    
    # Test 3: Update the script
    try:
        updated_content = """[SCENE: Modern office setting]

(Narrator - Professional tone)
Time management is crucial for success. Here are three essential tips:

First, prioritize your tasks using the Eisenhower Matrix. Focus on what's important and urgent.

Second, use time-blocking to schedule your day. Dedicate specific time slots for different activities.

Third, eliminate distractions. Turn off notifications and create a focused work environment.

(Narrator - Encouraging tone)
Remember, effective time management is a skill that improves with practice. Start implementing these strategies today!

What's your biggest time management challenge? Let us know in the comments!"""

        update_payload = {
            "script_id": script_id,
            "generated_script": updated_content
        }
        
        update_response = session.put(
            f"{BACKEND_URL}/scripts/{script_id}",
            json=update_payload,
            timeout=30
        )
        
        if update_response.status_code == 200:
            updated_data = update_response.json()
            print("✅ Script update successful!")
            print(f"   - Script ID: {updated_data['id']}")
            print(f"   - Content length: {len(updated_data['generated_script'])} chars")
            print(f"   - Original prompt preserved: {updated_data['original_prompt'][:50]}...")
            
            # Verify the content was actually updated
            if updated_data["generated_script"] == updated_content:
                print("✅ Script content correctly updated")
            else:
                print("❌ Script content not updated correctly")
                
        else:
            print(f"❌ Script update failed: {update_response.status_code}")
            print(f"   Response: {update_response.text[:200]}")
            return
            
    except Exception as e:
        print(f"❌ Error updating script: {str(e)}")
        return
    
    # Test 4: Verify database persistence
    try:
        verification_response = session.get(f"{BACKEND_URL}/scripts", timeout=30)
        if verification_response.status_code == 200:
            scripts = verification_response.json()
            updated_script = None
            
            for script in scripts:
                if script["id"] == script_id:
                    updated_script = script
                    break
            
            if updated_script and updated_script["generated_script"] == updated_content:
                print("✅ Database persistence verified")
            else:
                print("❌ Database persistence failed")
                
        else:
            print(f"❌ Failed to verify database persistence: {verification_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verifying database persistence: {str(e)}")
    
    # Test 5: Error handling - invalid script ID
    try:
        invalid_payload = {
            "script_id": "invalid-id-12345",
            "generated_script": "This should fail"
        }
        
        invalid_response = session.put(
            f"{BACKEND_URL}/scripts/invalid-id-12345",
            json=invalid_payload,
            timeout=30
        )
        
        if invalid_response.status_code == 404:
            print("✅ Invalid script ID error handling: OK")
        else:
            print(f"❌ Invalid script ID error handling failed: {invalid_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid script ID: {str(e)}")
    
    print("\n🎉 Script editing functionality test completed!")

if __name__ == "__main__":
    test_script_editing()
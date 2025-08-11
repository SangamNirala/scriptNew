#!/usr/bin/env python3
"""
Script Editing Functionality Test
Tests the new PUT /api/scripts/{script_id} endpoint
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://fb037db3-96a1-42dd-83e1-fc5d66dc6674.preview.emergentagent.com/api"

class ScriptEditingTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_script_editing_functionality(self):
        """Test the new script editing functionality (PUT /api/scripts/{script_id})"""
        print("\n=== Testing Script Editing Functionality ===")
        
        # Step 1: First generate a script to edit
        print("Step 1: Generating a script to edit...")
        script_payload = {
            "prompt": "Create a video about productivity tips for remote workers",
            "video_type": "educational",
            "duration": "medium"
        }
        
        try:
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Script Editing - Script Generation Setup", False,
                            f"Failed to generate script for editing test: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            script_id = script_data["id"]
            original_script = script_data["generated_script"]
            original_prompt = script_data["original_prompt"]
            original_video_type = script_data["video_type"]
            original_duration = script_data["duration"]
            original_created_at = script_data["created_at"]
            
            self.log_test("Script Editing - Script Generation Setup", True,
                        f"Successfully generated script with ID: {script_id}")
            
        except Exception as e:
            self.log_test("Script Editing - Script Generation Setup", False,
                        f"Exception during script generation: {str(e)}")
            return False
        
        # Step 2: Test valid script update
        print("Step 2: Testing valid script update...")
        updated_script_content = """[SCENE: Modern home office setup with natural lighting]

(Narrator - Professional, engaging tone)
Working from home has become the new normal, but staying productive can be challenging. Here are five game-changing tips that will transform your remote work experience.

[SCENE: Close-up of organized desk with productivity tools]

First, create a dedicated workspace. Your brain needs clear boundaries between work and personal life. Even a small corner can become your productivity zone.

[SCENE: Person following a morning routine]

Second, establish a morning routine. Start your day with intention - shower, dress professionally, and begin work at the same time every day.

[SCENE: Digital calendar and task management apps]

Third, use time-blocking techniques. Schedule specific times for deep work, meetings, and breaks. Your calendar becomes your productivity roadmap.

[SCENE: Person taking a walk outside]

Fourth, take regular breaks. The Pomodoro Technique works wonders - 25 minutes of focused work followed by a 5-minute break keeps your mind sharp.

[SCENE: Video call with team members]

Finally, over-communicate with your team. Remote work requires intentional communication. Share your progress, ask questions, and stay connected.

(Narrator - Encouraging tone)
Remember, productivity isn't about working more hours - it's about working smarter. Implement these strategies and watch your remote work efficiency soar!

[SCENE: Person successfully completing tasks with satisfaction]

What's your biggest remote work challenge? Share in the comments below!"""

        update_payload = {
            "script_id": script_id,
            "generated_script": updated_script_content
        }
        
        try:
            update_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=update_payload,
                timeout=30
            )
            
            if update_response.status_code == 200:
                updated_data = update_response.json()
                
                # Verify response structure
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in updated_data]
                
                if missing_fields:
                    self.log_test("Script Editing - Update Response Structure", False,
                                f"Missing fields in update response: {missing_fields}")
                    return False
                
                # Verify the script content was updated
                if updated_data["generated_script"] != updated_script_content:
                    self.log_test("Script Editing - Script Content Update", False,
                                "Script content was not updated correctly")
                    return False
                
                # Verify all original fields are preserved except generated_script
                if (updated_data["id"] != script_id or
                    updated_data["original_prompt"] != original_prompt or
                    updated_data["video_type"] != original_video_type or
                    updated_data["duration"] != original_duration or
                    updated_data["created_at"] != original_created_at):
                    self.log_test("Script Editing - Original Fields Preservation", False,
                                "Original script metadata was not preserved correctly")
                    return False
                
                self.log_test("Script Editing - Valid Update", True,
                            f"Successfully updated script content ({len(updated_script_content)} chars)")
                
            else:
                self.log_test("Script Editing - Valid Update", False,
                            f"HTTP {update_response.status_code}: {update_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Valid Update", False,
                        f"Exception during script update: {str(e)}")
            return False
        
        # Step 3: Verify the update was saved to database
        print("Step 3: Verifying database persistence...")
        try:
            # Retrieve the script again to verify it was saved
            retrieval_response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if retrieval_response.status_code == 200:
                scripts = retrieval_response.json()
                updated_script_found = None
                
                for script in scripts:
                    if script["id"] == script_id:
                        updated_script_found = script
                        break
                
                if not updated_script_found:
                    self.log_test("Script Editing - Database Persistence", False,
                                "Updated script not found in database")
                    return False
                
                if updated_script_found["generated_script"] != updated_script_content:
                    self.log_test("Script Editing - Database Persistence", False,
                                "Script content in database doesn't match update")
                    return False
                
                self.log_test("Script Editing - Database Persistence", True,
                            "Script update successfully persisted to database")
                
            else:
                self.log_test("Script Editing - Database Persistence", False,
                            f"Failed to retrieve scripts for verification: {retrieval_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Database Persistence", False,
                        f"Exception during database verification: {str(e)}")
            return False
        
        # Step 4: Test error handling for invalid script ID
        print("Step 4: Testing error handling for invalid script ID...")
        invalid_script_id = "invalid-script-id-12345"
        invalid_update_payload = {
            "script_id": invalid_script_id,
            "generated_script": "This should fail because the script ID doesn't exist"
        }
        
        try:
            invalid_response = self.session.put(
                f"{self.backend_url}/scripts/{invalid_script_id}",
                json=invalid_update_payload,
                timeout=30
            )
            
            if invalid_response.status_code == 404:
                self.log_test("Script Editing - Invalid ID Error Handling", True,
                            "Correctly returned 404 for invalid script ID")
            else:
                self.log_test("Script Editing - Invalid ID Error Handling", False,
                            f"Expected 404, got {invalid_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Invalid ID Error Handling", False,
                        f"Exception during invalid ID test: {str(e)}")
            return False
        
        # Step 5: Test error handling for missing required fields
        print("Step 5: Testing error handling for missing required fields...")
        try:
            # Test with missing generated_script field
            incomplete_payload = {
                "script_id": script_id
                # Missing generated_script field
            }
            
            incomplete_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=incomplete_payload,
                timeout=30
            )
            
            if incomplete_response.status_code == 422:  # Validation error
                self.log_test("Script Editing - Missing Fields Error Handling", True,
                            "Correctly returned 422 for missing required fields")
            else:
                self.log_test("Script Editing - Missing Fields Error Handling", False,
                            f"Expected 422, got {incomplete_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Missing Fields Error Handling", False,
                        f"Exception during missing fields test: {str(e)}")
            return False
        
        # Step 6: Test with empty script content
        print("Step 6: Testing with empty script content...")
        try:
            empty_payload = {
                "script_id": script_id,
                "generated_script": ""
            }
            
            empty_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=empty_payload,
                timeout=30
            )
            
            if empty_response.status_code == 200:
                empty_data = empty_response.json()
                if empty_data["generated_script"] == "":
                    self.log_test("Script Editing - Empty Content Handling", True,
                                "Successfully handled empty script content")
                else:
                    self.log_test("Script Editing - Empty Content Handling", False,
                                "Empty script content was not saved correctly")
                    return False
            else:
                self.log_test("Script Editing - Empty Content Handling", False,
                            f"Failed to handle empty content: {empty_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Empty Content Handling", False,
                        f"Exception during empty content test: {str(e)}")
            return False
        
        # Step 7: Test with very long script content
        print("Step 7: Testing with very long script content...")
        try:
            long_script = "This is a very long script content. " * 1000  # ~35,000 characters
            long_payload = {
                "script_id": script_id,
                "generated_script": long_script
            }
            
            long_response = self.session.put(
                f"{self.backend_url}/scripts/{script_id}",
                json=long_payload,
                timeout=30
            )
            
            if long_response.status_code == 200:
                long_data = long_response.json()
                if len(long_data["generated_script"]) == len(long_script):
                    self.log_test("Script Editing - Long Content Handling", True,
                                f"Successfully handled long script content ({len(long_script)} chars)")
                else:
                    self.log_test("Script Editing - Long Content Handling", False,
                                "Long script content was truncated or corrupted")
                    return False
            else:
                self.log_test("Script Editing - Long Content Handling", False,
                            f"Failed to handle long content: {long_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Script Editing - Long Content Handling", False,
                        f"Exception during long content test: {str(e)}")
            return False
        
        print("✅ Script editing functionality testing completed successfully!")
        return True

if __name__ == "__main__":
    print("🚀 Starting Script Editing Functionality Test...")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    tester = ScriptEditingTester()
    
    # Test basic connectivity first
    try:
        response = tester.session.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend connectivity confirmed")
        else:
            print(f"❌ Backend connectivity failed: {response.status_code}")
            exit(1)
    except Exception as e:
        print(f"❌ Backend connectivity failed: {str(e)}")
        exit(1)
    
    # Run the script editing test
    success = tester.test_script_editing_functionality()
    
    print("\n" + "="*80)
    print("🎯 SCRIPT EDITING TEST SUMMARY")
    print("="*80)
    
    if success:
        print("🎉 Script editing functionality test completed successfully!")
        print("✅ All test cases passed:")
        print("  - Script generation and setup")
        print("  - Valid script update")
        print("  - Database persistence verification")
        print("  - Invalid script ID error handling")
        print("  - Missing fields error handling")
        print("  - Empty content handling")
        print("  - Long content handling")
    else:
        print("❌ Script editing functionality test failed!")
        print("Some test cases did not pass as expected.")
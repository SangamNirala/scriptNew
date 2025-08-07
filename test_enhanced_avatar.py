#!/usr/bin/env python3
"""
Test script specifically for Enhanced Avatar Video Generation
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://12841f10-e126-423f-b7aa-bf740c34f127.preview.emergentagent.com/api"

class EnhancedAvatarTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_enhanced_avatar_video_generation_endpoint(self):
        """Test the new /api/generate-enhanced-avatar-video endpoint"""
        print("\n=== Testing Enhanced Avatar Video Generation Endpoint ===")
        
        # First, generate some audio to use for enhanced avatar video testing
        try:
            # Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Enhanced Avatar Video - Voice Retrieval", False,
                            "Could not retrieve voices for enhanced avatar video testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Enhanced Avatar Video - Voice Availability", False,
                            "No voices available for enhanced avatar video testing")
                return False
            
            test_voice = voices[0]["name"]
            
            # Generate sample audio for enhanced avatar video
            audio_text = "Welcome to our presentation. This is about technology and innovation in the modern world."
            audio_payload = {
                "text": audio_text,
                "voice_name": test_voice
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=30
            )
            
            if audio_response.status_code != 200:
                self.log_test("Enhanced Avatar Video - Audio Generation", False,
                            f"Failed to generate audio for enhanced avatar video: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Enhanced Avatar Video - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio for enhanced avatar video")
            
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Audio Setup", False, f"Failed to setup audio: {str(e)}")
            return False
        
        # Test Case 1: Default avatar option
        try:
            default_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "default",
                "script_text": "Welcome to our presentation. This is about technology and innovation in the modern world."
            }
            
            print("Sending request to enhanced avatar video endpoint...")
            default_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=default_payload,
                timeout=180  # Enhanced avatar video generation can take longer
            )
            
            if default_response.status_code == 200:
                default_data = default_response.json()
                
                # Verify response structure
                required_fields = ["video_base64", "duration_seconds", "request_id", "avatar_option", "script_segments", "sadtalker_used"]
                missing_fields = [field for field in required_fields if field not in default_data]
                
                if missing_fields:
                    self.log_test("Enhanced Avatar Video - Default Response Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify video data
                video_base64 = default_data["video_base64"]
                if not video_base64 or len(video_base64) < 1000:
                    self.log_test("Enhanced Avatar Video - Default Video Data", False,
                                "Video base64 data is too short or empty",
                                {"video_length": len(video_base64) if video_base64 else 0})
                    return False
                
                # Verify duration is reasonable
                duration = default_data["duration_seconds"]
                if duration <= 0 or duration > 120:  # Should be reasonable duration
                    self.log_test("Enhanced Avatar Video - Default Duration", False,
                                f"Unreasonable duration: {duration} seconds")
                    return False
                
                # Verify avatar option matches
                if default_data["avatar_option"] != "default":
                    self.log_test("Enhanced Avatar Video - Default Avatar Option", False,
                                f"Expected 'default', got '{default_data['avatar_option']}'")
                    return False
                
                # Verify script segments
                script_segments = default_data["script_segments"]
                if script_segments <= 0:
                    self.log_test("Enhanced Avatar Video - Default Script Segments", False,
                                f"Expected positive script segments, got {script_segments}")
                    return False
                
                # Verify sadtalker_used is boolean
                sadtalker_used = default_data["sadtalker_used"]
                if not isinstance(sadtalker_used, bool):
                    self.log_test("Enhanced Avatar Video - Default SadTalker Flag", False,
                                f"Expected boolean for sadtalker_used, got {type(sadtalker_used)}")
                    return False
                
                self.log_test("Enhanced Avatar Video - Default Avatar", True,
                            f"Successfully generated {len(video_base64)} chars of base64 video, duration: {duration:.2f}s, segments: {script_segments}, SadTalker: {sadtalker_used}")
                
            else:
                self.log_test("Enhanced Avatar Video - Default HTTP Response", False,
                            f"HTTP {default_response.status_code}: {default_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Default Generation Exception", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 2: AI Generated avatar option
        try:
            ai_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "ai_generated",
                "script_text": "This is a test of AI-generated avatar functionality."
            }
            
            print("Testing AI generated avatar option...")
            ai_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=ai_payload,
                timeout=180
            )
            
            if ai_response.status_code == 200:
                ai_data = ai_response.json()
                
                # Verify avatar option matches
                if ai_data["avatar_option"] != "ai_generated":
                    self.log_test("Enhanced Avatar Video - AI Generated Avatar Option", False,
                                f"Expected 'ai_generated', got '{ai_data['avatar_option']}'")
                    return False
                
                # Verify video was generated
                if not ai_data["video_base64"] or len(ai_data["video_base64"]) < 1000:
                    self.log_test("Enhanced Avatar Video - AI Generated Video Data", False,
                                "AI generated video data is too short or empty")
                    return False
                
                self.log_test("Enhanced Avatar Video - AI Generated Avatar", True,
                            f"Successfully generated AI avatar video: {len(ai_data['video_base64'])} chars, duration: {ai_data['duration_seconds']:.2f}s")
                
            else:
                self.log_test("Enhanced Avatar Video - AI Generated HTTP Response", False,
                            f"HTTP {ai_response.status_code}: {ai_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - AI Generated Exception", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 3: Upload avatar option (without actual image - should fail gracefully)
        try:
            upload_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "upload",
                "script_text": "This should fail without user image."
            }
            
            print("Testing upload validation...")
            upload_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=upload_payload,
                timeout=60
            )
            
            # This should fail with 400 because no user_image_base64 provided
            if upload_response.status_code == 400:
                self.log_test("Enhanced Avatar Video - Upload Validation", True,
                            "Properly validated missing user image for upload option")
            else:
                self.log_test("Enhanced Avatar Video - Upload Validation", False,
                            f"Expected 400 for missing user image, got {upload_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Upload Validation Exception", False, f"Request failed: {str(e)}")
        
        # Test Case 4: Invalid avatar option
        try:
            invalid_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "invalid_option",
                "script_text": "This should fail with invalid avatar option."
            }
            
            print("Testing invalid option validation...")
            invalid_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=invalid_payload,
                timeout=60
            )
            
            # This should fail with 400 because of invalid avatar option
            if invalid_response.status_code == 400:
                self.log_test("Enhanced Avatar Video - Invalid Option Validation", True,
                            "Properly validated invalid avatar option")
            else:
                self.log_test("Enhanced Avatar Video - Invalid Option Validation", False,
                            f"Expected 400 for invalid avatar option, got {invalid_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Invalid Option Exception", False, f"Request failed: {str(e)}")
        
        return True
    
    def run_tests(self):
        """Run enhanced avatar video tests"""
        print("🚀 Starting Enhanced Avatar Video Generation Testing")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 60)
        
        success = self.test_enhanced_avatar_video_generation_endpoint()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = EnhancedAvatarTester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)
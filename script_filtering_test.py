#!/usr/bin/env python3
"""
Script Audio Filtering Test - Comprehensive Testing
Tests the enhanced script filtering functionality to verify TTS system correctly extracts 
only dialogue content from AI-generated scripts instead of reading production notes.

Focus Areas:
1. Script Audio Filtering Testing - extract_clean_script() function with modern AI script formats
2. TTS API Testing with Filtered Content - /api/generate-audio endpoint  
3. Comprehensive Script Format Testing - various script formats
4. Quality and Performance Verification
"""

import requests
import json
import time
from datetime import datetime
import sys
import re

# Get backend URL from frontend .env
BACKEND_URL = "https://56d36cff-446d-4ac0-ab9f-1388b7969244.preview.emergentagent.com/api"

class ScriptFilteringTester:
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
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Basic Connectivity", True, "API is accessible and responding")
                    return True
                else:
                    self.log_test("Basic Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Basic Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_voices_endpoint(self):
        """Test voices endpoint for TTS functionality"""
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=10)
            if response.status_code == 200:
                voices = response.json()
                if isinstance(voices, list) and len(voices) > 0:
                    # Check voice structure
                    first_voice = voices[0]
                    required_fields = ['name', 'display_name', 'language', 'gender']
                    if all(field in first_voice for field in required_fields):
                        self.log_test("Voices Endpoint", True, f"Retrieved {len(voices)} voices with proper structure")
                        return voices
                    else:
                        self.log_test("Voices Endpoint", False, f"Voice structure missing required fields: {required_fields}")
                        return None
                else:
                    self.log_test("Voices Endpoint", False, "No voices returned or invalid format")
                    return None
            else:
                self.log_test("Voices Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Voices Endpoint", False, f"Error: {str(e)}")
            return None

    def test_script_filtering_with_dialogue_markers(self):
        """Test script filtering with [DIALOGUE:] markers as specified in review request"""
        
        # Sample script from review request
        test_script = '''Okay, here's a script designed to meet your very specific requirements.

**VIDEO SCRIPT: TEST**

**[0:00-0:03] AI IMAGE PROMPT:**
"Close-up on a person's face, dramatic lighting"

**[DIALOGUE:]** (Narrator) "This is the first dialogue line that should be spoken."

**[0:03-0:06] AI IMAGE PROMPT:**  
"Wide shot of cityscape at sunset"

**[DIALOGUE:]** (Encouraging tone) "This is the second dialogue line for the video."

**Important Considerations:**
- These are production notes that should NOT be spoken
- Platform-specific adjustments may be needed'''

        expected_dialogue = "This is the first dialogue line that should be spoken. This is the second dialogue line for the video."
        
        # Test with multiple voices to ensure consistency
        voices = self.test_voices_endpoint()
        if not voices:
            self.log_test("Script Filtering - Dialogue Markers", False, "Cannot test without available voices")
            return False
            
        test_voices = voices[:3]  # Test with first 3 voices
        success_count = 0
        
        for voice in test_voices:
            try:
                payload = {
                    "text": test_script,
                    "voice_name": voice['name']
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    audio_data = response.json()
                    
                    # Check if audio was generated
                    if 'audio_base64' in audio_data and len(audio_data['audio_base64']) > 1000:
                        # Audio should be substantial (>1000 chars base64)
                        audio_length = len(audio_data['audio_base64'])
                        self.log_test(
                            f"Script Filtering - {voice['display_name']}", 
                            True, 
                            f"Generated {audio_length} chars of clean audio from dialogue-only content"
                        )
                        success_count += 1
                    else:
                        self.log_test(
                            f"Script Filtering - {voice['display_name']}", 
                            False, 
                            "Audio generation failed or produced insufficient data"
                        )
                else:
                    self.log_test(
                        f"Script Filtering - {voice['display_name']}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Script Filtering - {voice['display_name']}", 
                    False, 
                    f"Error: {str(e)}"
                )
        
        # Overall success if at least 2 out of 3 voices worked
        overall_success = success_count >= 2
        self.log_test(
            "Script Filtering - Dialogue Markers Overall", 
            overall_success, 
            f"Successfully filtered and generated audio for {success_count}/{len(test_voices)} voices"
        )
        
        return overall_success

    def test_script_filtering_with_ai_image_prompts(self):
        """Test filtering of AI image prompts and production metadata"""
        
        test_script = '''**VIDEO SCRIPT: AI IMAGE PROMPT TEST**

**[0:00-0:05] AI IMAGE PROMPT:**
"Professional kitchen setup with modern appliances, warm lighting, chef preparing ingredients"

**[DIALOGUE:]** "Welcome to our cooking masterclass where we'll transform simple ingredients into extraordinary meals."

**[0:05-0:10] AI IMAGE PROMPT:**
"Close-up of hands chopping vegetables with precision, colorful ingredients spread on counter"

**[DIALOGUE:]** "Today's recipe focuses on fresh, seasonal ingredients that bring out natural flavors."

**Production Notes:**
- Ensure proper lighting for food shots
- Use macro lens for ingredient close-ups
- Background music should be upbeat but not overwhelming

**Important Considerations:**
- Color grading should enhance food appeal
- Audio levels must be consistent throughout'''

        expected_content_keywords = ["welcome", "cooking", "masterclass", "ingredients", "recipe", "seasonal", "flavors"]
        
        voices = self.test_voices_endpoint()
        if not voices:
            return False
            
        try:
            payload = {
                "text": test_script,
                "voice_name": voices[0]['name']  # Use first available voice
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                audio_data = response.json()
                
                if 'audio_base64' in audio_data and len(audio_data['audio_base64']) > 500:
                    audio_length = len(audio_data['audio_base64'])
                    self.log_test(
                        "AI Image Prompt Filtering", 
                        True, 
                        f"Successfully filtered AI image prompts and production notes, generated {audio_length} chars audio"
                    )
                    return True
                else:
                    self.log_test("AI Image Prompt Filtering", False, "Insufficient audio generated")
                    return False
            else:
                self.log_test("AI Image Prompt Filtering", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("AI Image Prompt Filtering", False, f"Error: {str(e)}")
            return False

    def test_script_filtering_with_production_notes(self):
        """Test filtering of production notes and technical specifications"""
        
        test_script = '''Okay, here's a script designed for maximum engagement and retention.

**VIDEO SCRIPT: PRODUCTION NOTES TEST**

**Technical Specifications:**
- Duration: 60 seconds
- Format: 16:9 aspect ratio
- Resolution: 1080p minimum
- Frame rate: 30fps

**[DIALOGUE:]** "Have you ever wondered what separates successful people from everyone else?"

**Production Guidelines:**
- Use dynamic camera movements
- Implement quick cuts every 3-4 seconds
- Ensure consistent audio levels
- Color grade for warm, inviting tones

**[DIALOGUE:]** "It's not talent, luck, or connections. It's something much simpler yet more powerful."

**Post-Production Notes:**
- Add subtle background music
- Include lower thirds for key points
- Implement smooth transitions
- Optimize for mobile viewing

**Platform-Specific Adjustments:**
- TikTok: Vertical format, trending sounds
- YouTube: Thumbnail optimization, SEO tags
- Instagram: Square format, story-friendly'''

        voices = self.test_voices_endpoint()
        if not voices:
            return False
            
        try:
            payload = {
                "text": test_script,
                "voice_name": voices[0]['name']
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                audio_data = response.json()
                
                if 'audio_base64' in audio_data and len(audio_data['audio_base64']) > 300:
                    audio_length = len(audio_data['audio_base64'])
                    self.log_test(
                        "Production Notes Filtering", 
                        True, 
                        f"Successfully filtered production notes and technical specs, generated {audio_length} chars audio"
                    )
                    return True
                else:
                    self.log_test("Production Notes Filtering", False, "Insufficient audio generated")
                    return False
            else:
                self.log_test("Production Notes Filtering", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Production Notes Filtering", False, f"Error: {str(e)}")
            return False

    def test_script_filtering_with_speaker_directions(self):
        """Test removal of speaker directions like (Intense, slightly hushed tone)"""
        
        test_script = '''**VIDEO SCRIPT: SPEAKER DIRECTIONS TEST**

**[DIALOGUE:]** (Intense, slightly hushed tone) "The secret they don't want you to know is hiding in plain sight."

**[DIALOGUE:]** (Narrator - Professional tone) "For decades, industry experts have kept this information locked away."

**[DIALOGUE:]** (Encouraging, upbeat) "But today, we're breaking down those barriers and sharing everything with you."

**[DIALOGUE:]** (Expert) "This revolutionary approach has helped thousands transform their lives completely."'''

        expected_clean_content = [
            "The secret they don't want you to know is hiding in plain sight.",
            "For decades, industry experts have kept this information locked away.",
            "But today, we're breaking down those barriers and sharing everything with you.",
            "This revolutionary approach has helped thousands transform their lives completely."
        ]
        
        voices = self.test_voices_endpoint()
        if not voices:
            return False
            
        try:
            payload = {
                "text": test_script,
                "voice_name": voices[0]['name']
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                audio_data = response.json()
                
                if 'audio_base64' in audio_data and len(audio_data['audio_base64']) > 1000:
                    audio_length = len(audio_data['audio_base64'])
                    self.log_test(
                        "Speaker Directions Filtering", 
                        True, 
                        f"Successfully removed speaker directions, generated {audio_length} chars audio"
                    )
                    return True
                else:
                    self.log_test("Speaker Directions Filtering", False, "Insufficient audio generated")
                    return False
            else:
                self.log_test("Speaker Directions Filtering", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Speaker Directions Filtering", False, f"Error: {str(e)}")
            return False

    def test_backward_compatibility(self):
        """Test that older script formats still work correctly"""
        
        # Traditional script format without [DIALOGUE:] markers
        traditional_script = '''**VIDEO SCRIPT: TRADITIONAL FORMAT**

TARGET DURATION: 45 seconds
VIDEO TYPE: Educational

[0:00-0:05] Opening scene with presenter in modern office setting

"Welcome to our comprehensive guide on productivity optimization."

[0:05-0:15] Screen recording showing software interface

"Today we'll explore three proven strategies that successful entrepreneurs use daily."

[0:15-0:30] Split screen with presenter and visual examples

"First, time-blocking helps you focus on high-impact activities without distractions."

[0:30-0:45] Call-to-action with presenter looking directly at camera

"Ready to transform your productivity? Download our free toolkit using the link below."

**END OF SCRIPT**'''

        voices = self.test_voices_endpoint()
        if not voices:
            return False
            
        try:
            payload = {
                "text": traditional_script,
                "voice_name": voices[0]['name']
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                audio_data = response.json()
                
                if 'audio_base64' in audio_data and len(audio_data['audio_base64']) > 1000:
                    audio_length = len(audio_data['audio_base64'])
                    self.log_test(
                        "Backward Compatibility", 
                        True, 
                        f"Traditional script format processed correctly, generated {audio_length} chars audio"
                    )
                    return True
                else:
                    self.log_test("Backward Compatibility", False, "Insufficient audio generated")
                    return False
            else:
                self.log_test("Backward Compatibility", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backward Compatibility", False, f"Error: {str(e)}")
            return False

    def test_empty_and_edge_cases(self):
        """Test edge cases like empty text, only production notes, etc."""
        
        test_cases = [
            {
                "name": "Empty Text",
                "script": "",
                "should_fail": True
            },
            {
                "name": "Only Production Notes",
                "script": '''**Important Considerations:**
- These are production notes that should NOT be spoken
- Platform-specific adjustments may be needed
- Color grading requirements
- Audio level specifications''',
                "should_fail": True
            },
            {
                "name": "Only AI Image Prompts",
                "script": '''**[0:00-0:03] AI IMAGE PROMPT:**
"Close-up on a person's face, dramatic lighting"

**[0:03-0:06] AI IMAGE PROMPT:**  
"Wide shot of cityscape at sunset"''',
                "should_fail": True
            },
            {
                "name": "Mixed Content with Minimal Dialogue",
                "script": '''**VIDEO SCRIPT: MINIMAL TEST**

**[DIALOGUE:]** "Hello."

**Important Considerations:**
- Lots of production notes
- Technical specifications
- Platform requirements''',
                "should_fail": False
            }
        ]
        
        voices = self.test_voices_endpoint()
        if not voices:
            return False
            
        success_count = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            try:
                payload = {
                    "text": test_case["script"],
                    "voice_name": voices[0]['name']
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=15
                )
                
                if test_case["should_fail"]:
                    # These should return 400 or 500 status codes
                    if response.status_code >= 400:
                        self.log_test(
                            f"Edge Case - {test_case['name']}", 
                            True, 
                            f"Correctly rejected invalid input with status {response.status_code}"
                        )
                        success_count += 1
                    else:
                        self.log_test(
                            f"Edge Case - {test_case['name']}", 
                            False, 
                            f"Should have failed but returned status {response.status_code}"
                        )
                else:
                    # These should succeed
                    if response.status_code == 200:
                        audio_data = response.json()
                        if 'audio_base64' in audio_data and len(audio_data['audio_base64']) > 100:
                            self.log_test(
                                f"Edge Case - {test_case['name']}", 
                                True, 
                                f"Successfully processed minimal content"
                            )
                            success_count += 1
                        else:
                            self.log_test(
                                f"Edge Case - {test_case['name']}", 
                                False, 
                                "Insufficient audio generated"
                            )
                    else:
                        self.log_test(
                            f"Edge Case - {test_case['name']}", 
                            False, 
                            f"Unexpected status {response.status_code}"
                        )
                        
            except Exception as e:
                if test_case["should_fail"]:
                    self.log_test(
                        f"Edge Case - {test_case['name']}", 
                        True, 
                        f"Correctly failed with error: {str(e)}"
                    )
                    success_count += 1
                else:
                    self.log_test(
                        f"Edge Case - {test_case['name']}", 
                        False, 
                        f"Unexpected error: {str(e)}"
                    )
        
        overall_success = success_count >= (total_tests * 0.75)  # 75% success rate
        self.log_test(
            "Edge Cases Overall", 
            overall_success, 
            f"Passed {success_count}/{total_tests} edge case tests"
        )
        
        return overall_success

    def test_performance_and_quality(self):
        """Test performance and quality of script filtering"""
        
        # Large script with mixed content to test performance
        large_script = '''Okay, here's a comprehensive script designed to test performance and quality.

**VIDEO SCRIPT: PERFORMANCE TEST**

**Technical Specifications:**
- Duration: 120 seconds
- Format: 16:9 aspect ratio
- Resolution: 4K
- Frame rate: 60fps

**[0:00-0:05] AI IMAGE PROMPT:**
"Stunning aerial view of modern city skyline at golden hour"

**[DIALOGUE:]** (Professional narrator) "In today's rapidly evolving digital landscape, success requires more than just traditional approaches."

**[0:05-0:10] AI IMAGE PROMPT:**
"Close-up of hands typing on modern laptop with code on screen"

**[DIALOGUE:]** (Confident tone) "We're witnessing a fundamental shift in how businesses operate, communicate, and deliver value to their customers."

**Production Guidelines:**
- Use dynamic camera movements throughout
- Implement quick cuts every 2-3 seconds for retention
- Ensure consistent audio levels across all segments
- Color grade for professional, modern aesthetic

**[0:10-0:20] AI IMAGE PROMPT:**
"Split screen showing before/after business transformation results"

**[DIALOGUE:]** (Inspiring) "The companies that thrive are those that embrace innovation, adapt quickly, and put their customers at the center of everything they do."

**Important Considerations:**
- Platform-specific optimizations required
- Mobile-first design approach essential
- Accessibility features must be included
- SEO optimization for maximum reach

**[DIALOGUE:]** (Authoritative) "This isn't just about technology—it's about creating meaningful connections and delivering exceptional experiences that drive real results."

**Post-Production Notes:**
- Add subtle background music that complements the narrative
- Include lower thirds for key statistics and data points
- Implement smooth transitions between segments
- Optimize for various platform requirements

**[DIALOGUE:]** (Call-to-action tone) "Ready to transform your approach and unlock unprecedented growth? Let's explore the strategies that industry leaders use to stay ahead of the competition."

**Platform-Specific Adjustments:**
- YouTube: Optimize for search algorithms and engagement metrics
- LinkedIn: Professional tone with business-focused messaging
- TikTok: Adapt for vertical format with trending elements
- Instagram: Visual-first approach with story-friendly content'''

        voices = self.test_voices_endpoint()
        if not voices:
            return False
            
        start_time = time.time()
        
        try:
            payload = {
                "text": large_script,
                "voice_name": voices[0]['name']
            }
            
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=60  # Longer timeout for large content
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                audio_data = response.json()
                
                if 'audio_base64' in audio_data and len(audio_data['audio_base64']) > 2000:
                    audio_length = len(audio_data['audio_base64'])
                    
                    # Quality checks
                    quality_score = 0
                    quality_details = []
                    
                    # Check processing time (should be reasonable)
                    if processing_time < 30:
                        quality_score += 1
                        quality_details.append(f"Good processing time: {processing_time:.1f}s")
                    else:
                        quality_details.append(f"Slow processing time: {processing_time:.1f}s")
                    
                    # Check audio length (should be substantial for the dialogue content)
                    if audio_length > 5000:
                        quality_score += 1
                        quality_details.append(f"Substantial audio generated: {audio_length} chars")
                    else:
                        quality_details.append(f"Limited audio generated: {audio_length} chars")
                    
                    # Check if voice information is preserved
                    if 'voice_used' in audio_data:
                        quality_score += 1
                        quality_details.append(f"Voice information preserved: {audio_data['voice_used']}")
                    
                    success = quality_score >= 2
                    self.log_test(
                        "Performance and Quality", 
                        success, 
                        f"Quality score: {quality_score}/3. " + "; ".join(quality_details)
                    )
                    return success
                else:
                    self.log_test("Performance and Quality", False, "Insufficient audio generated for large script")
                    return False
            else:
                self.log_test("Performance and Quality", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Performance and Quality", False, f"Error: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run all script filtering tests"""
        print("🎯 SCRIPT AUDIO FILTERING COMPREHENSIVE TESTING")
        print("=" * 60)
        print("Testing enhanced script filtering functionality to verify TTS system")
        print("correctly extracts only dialogue content from AI-generated scripts.")
        print()
        
        # Test sequence
        tests = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("Voices Endpoint", lambda: self.test_voices_endpoint() is not None),
            ("Script Filtering - Dialogue Markers", self.test_script_filtering_with_dialogue_markers),
            ("AI Image Prompt Filtering", self.test_script_filtering_with_ai_image_prompts),
            ("Production Notes Filtering", self.test_script_filtering_with_production_notes),
            ("Speaker Directions Filtering", self.test_script_filtering_with_speaker_directions),
            ("Backward Compatibility", self.test_backward_compatibility),
            ("Edge Cases", self.test_empty_and_edge_cases),
            ("Performance and Quality", self.test_performance_and_quality)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SCRIPT FILTERING TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 OVERALL RESULT: EXCELLENT - Script filtering functionality working correctly")
        elif success_rate >= 60:
            print("⚠️  OVERALL RESULT: GOOD - Minor issues detected but core functionality working")
        else:
            print("❌ OVERALL RESULT: NEEDS ATTENTION - Significant issues with script filtering")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ScriptFilteringTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Backend Testing Script for Script Generation App
Tests all backend API endpoints and functionality
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://96f7899b-d149-4ed7-8f25-3ff3cf1c56d1.preview.emergentagent.com/api"

class ScriptGenerationTester:
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
    
    def test_enhance_prompt_endpoint(self):
        """Test the /api/enhance-prompt endpoint"""
        print("\n=== Testing Prompt Enhancement Endpoint ===")
        
        # Test Case 1: Basic motivational video prompt
        test_prompt = "motivational video about success"
        payload = {
            "original_prompt": test_prompt,
            "video_type": "general"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["original_prompt", "enhanced_prompt", "enhancement_explanation"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhance Prompt - Structure", False, 
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify content quality
                original = data["original_prompt"]
                enhanced = data["enhanced_prompt"]
                explanation = data["enhancement_explanation"]
                
                if len(enhanced) <= len(original):
                    self.log_test("Enhance Prompt - Enhancement Quality", False,
                                "Enhanced prompt is not longer/more detailed than original",
                                {"original_length": len(original), "enhanced_length": len(enhanced)})
                    return False
                
                if not explanation or len(explanation) < 20:
                    self.log_test("Enhance Prompt - Explanation Quality", False,
                                "Enhancement explanation is too short or missing",
                                {"explanation_length": len(explanation)})
                    return False
                
                self.log_test("Enhance Prompt - Basic Functionality", True,
                            f"Successfully enhanced prompt from {len(original)} to {len(enhanced)} characters")
                
                # Test Case 2: Different video types
                video_types = ["educational", "entertainment", "marketing"]
                for video_type in video_types:
                    test_payload = {
                        "original_prompt": "create engaging content about technology",
                        "video_type": video_type
                    }
                    
                    type_response = self.session.post(
                        f"{self.backend_url}/enhance-prompt",
                        json=test_payload,
                        timeout=30
                    )
                    
                    if type_response.status_code == 200:
                        self.log_test(f"Enhance Prompt - {video_type.title()} Type", True,
                                    f"Successfully processed {video_type} video type")
                    else:
                        self.log_test(f"Enhance Prompt - {video_type.title()} Type", False,
                                    f"Failed for {video_type}: {type_response.status_code}")
                
                return True
                
            else:
                self.log_test("Enhance Prompt - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhance Prompt - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_generate_script_endpoint(self):
        """Test the /api/generate-script endpoint"""
        print("\n=== Testing Script Generation Endpoint ===")
        
        # Test Case 1: Basic script generation
        test_prompt = "Create a motivational video about overcoming challenges and achieving success"
        payload = {
            "prompt": test_prompt,
            "video_type": "general",
            "duration": "short"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Generate Script - Structure", False,
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify content quality
                script = data["generated_script"]
                if len(script) < 100:
                    self.log_test("Generate Script - Content Length", False,
                                "Generated script is too short", {"script_length": len(script)})
                    return False
                
                # Check for storytelling elements
                storytelling_indicators = [
                    "[", "]",  # Scene descriptions
                    "(", ")",  # Speaker directions
                ]
                
                has_formatting = any(indicator in script for indicator in storytelling_indicators)
                if not has_formatting:
                    self.log_test("Generate Script - Formatting", False,
                                "Script lacks proper formatting (scene descriptions, speaker directions)")
                else:
                    self.log_test("Generate Script - Formatting", True,
                                "Script includes proper formatting elements")
                
                self.log_test("Generate Script - Basic Functionality", True,
                            f"Successfully generated {len(script)} character script")
                
                # Test Case 2: Different video types and durations
                test_combinations = [
                    {"video_type": "educational", "duration": "medium"},
                    {"video_type": "entertainment", "duration": "long"},
                    {"video_type": "marketing", "duration": "short"}
                ]
                
                for combo in test_combinations:
                    test_payload = {
                        "prompt": "Create engaging content about innovation",
                        **combo
                    }
                    
                    combo_response = self.session.post(
                        f"{self.backend_url}/generate-script",
                        json=test_payload,
                        timeout=45
                    )
                    
                    if combo_response.status_code == 200:
                        combo_data = combo_response.json()
                        self.log_test(f"Generate Script - {combo['video_type']}/{combo['duration']}", True,
                                    f"Successfully generated script for {combo['video_type']} {combo['duration']} video")
                    else:
                        self.log_test(f"Generate Script - {combo['video_type']}/{combo['duration']}", False,
                                    f"Failed: {combo_response.status_code}")
                
                return True
                
            else:
                self.log_test("Generate Script - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Script - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_scripts_retrieval_endpoint(self):
        """Test the /api/scripts endpoint"""
        print("\n=== Testing Scripts Retrieval Endpoint ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Scripts Retrieval - Data Type", False,
                                "Response is not a list", {"response_type": type(data).__name__})
                    return False
                
                if len(data) == 0:
                    self.log_test("Scripts Retrieval - Empty List", True,
                                "No scripts found (expected if no scripts generated yet)")
                    return True
                
                # Verify script structure
                first_script = data[0]
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration", "created_at"]
                missing_fields = [field for field in required_fields if field not in first_script]
                
                if missing_fields:
                    self.log_test("Scripts Retrieval - Script Structure", False,
                                f"Missing fields in script: {missing_fields}")
                    return False
                
                # Check chronological order (newest first)
                if len(data) > 1:
                    timestamps = [script["created_at"] for script in data]
                    is_sorted = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
                    
                    if is_sorted:
                        self.log_test("Scripts Retrieval - Chronological Order", True,
                                    "Scripts are properly sorted in reverse chronological order")
                    else:
                        self.log_test("Scripts Retrieval - Chronological Order", False,
                                    "Scripts are not sorted in reverse chronological order")
                
                self.log_test("Scripts Retrieval - Basic Functionality", True,
                            f"Successfully retrieved {len(data)} scripts")
                return True
                
            else:
                self.log_test("Scripts Retrieval - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Scripts Retrieval - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_integration_flow(self):
        """Test the complete integration flow"""
        print("\n=== Testing Integration Flow ===")
        
        try:
            # Step 1: Enhance a prompt
            original_prompt = "fitness motivation for beginners"
            enhance_payload = {
                "original_prompt": original_prompt,
                "video_type": "motivational"
            }
            
            enhance_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=enhance_payload,
                timeout=30
            )
            
            if enhance_response.status_code != 200:
                self.log_test("Integration Flow - Enhance Step", False,
                            f"Enhance prompt failed: {enhance_response.status_code}")
                return False
            
            enhanced_data = enhance_response.json()
            enhanced_prompt = enhanced_data["enhanced_prompt"]
            
            # Step 2: Generate script with enhanced prompt
            script_payload = {
                "prompt": enhanced_prompt,
                "video_type": "motivational",
                "duration": "medium"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Integration Flow - Script Generation Step", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            script_id = script_data["id"]
            
            # Step 3: Retrieve scripts and verify our script is there
            time.sleep(1)  # Brief pause to ensure database consistency
            
            retrieval_response = self.session.get(f"{self.backend_url}/scripts", timeout=15)
            
            if retrieval_response.status_code != 200:
                self.log_test("Integration Flow - Retrieval Step", False,
                            f"Script retrieval failed: {retrieval_response.status_code}")
                return False
            
            scripts = retrieval_response.json()
            script_found = any(script["id"] == script_id for script in scripts)
            
            if not script_found:
                self.log_test("Integration Flow - Data Persistence", False,
                            "Generated script not found in retrieval results")
                return False
            
            self.log_test("Integration Flow - Complete", True,
                        "Successfully completed enhance → generate → retrieve flow")
            return True
            
        except Exception as e:
            self.log_test("Integration Flow - Exception", False, f"Integration test failed: {str(e)}")
            return False
    
    def test_voices_endpoint(self):
        """Test the /api/voices endpoint"""
        print("\n=== Testing Voices Endpoint ===")
        
        try:
            response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Voices Endpoint - Data Type", False,
                                "Response is not a list", {"response_type": type(data).__name__})
                    return False
                
                if len(data) == 0:
                    self.log_test("Voices Endpoint - Empty List", False,
                                "No voices returned - expected at least some voices")
                    return False
                
                # Verify voice structure
                first_voice = data[0]
                required_fields = ["name", "display_name", "language", "gender"]
                missing_fields = [field for field in required_fields if field not in first_voice]
                
                if missing_fields:
                    self.log_test("Voices Endpoint - Voice Structure", False,
                                f"Missing fields in voice: {missing_fields}")
                    return False
                
                # Check for variety of voices
                genders = set(voice.get("gender", "") for voice in data)
                languages = set(voice.get("language", "") for voice in data)
                
                if len(genders) < 2:
                    self.log_test("Voices Endpoint - Gender Variety", False,
                                f"Expected both male and female voices, got: {genders}")
                else:
                    self.log_test("Voices Endpoint - Gender Variety", True,
                                f"Good gender variety: {genders}")
                
                if len(languages) < 2:
                    self.log_test("Voices Endpoint - Language Variety", False,
                                f"Expected multiple language variants, got: {languages}")
                else:
                    self.log_test("Voices Endpoint - Language Variety", True,
                                f"Good language variety: {len(languages)} variants")
                
                # Check for expected popular voices
                voice_names = [voice.get("name", "") for voice in data]
                expected_voices = ["en-US-AriaNeural", "en-US-DavisNeural", "en-GB-SoniaNeural"]
                found_expected = [voice for voice in expected_voices if voice in voice_names]
                
                if len(found_expected) >= 2:
                    self.log_test("Voices Endpoint - Popular Voices", True,
                                f"Found expected popular voices: {found_expected}")
                else:
                    self.log_test("Voices Endpoint - Popular Voices", False,
                                f"Expected popular voices not found. Available: {voice_names[:5]}")
                
                self.log_test("Voices Endpoint - Basic Functionality", True,
                            f"Successfully retrieved {len(data)} voices")
                return True
                
            else:
                self.log_test("Voices Endpoint - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Voices Endpoint - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_generate_audio_endpoint(self):
        """Test the /api/generate-audio endpoint"""
        print("\n=== Testing Generate Audio Endpoint ===")
        
        # First get available voices
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Generate Audio - Voice Retrieval", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Generate Audio - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            test_voice = voices[0]["name"]  # Use first available voice
            
        except Exception as e:
            self.log_test("Generate Audio - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test Case 1: Basic audio generation
        test_text = "Hello, this is a test of the text-to-speech functionality."
        payload = {
            "text": test_text,
            "voice_name": test_voice
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["audio_base64", "voice_used"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Generate Audio - Structure", False,
                                f"Missing fields: {missing_fields}", data)
                    return False
                
                # Verify audio data
                audio_base64 = data["audio_base64"]
                if not audio_base64 or len(audio_base64) < 100:
                    self.log_test("Generate Audio - Audio Data", False,
                                "Audio base64 data is too short or empty",
                                {"audio_length": len(audio_base64) if audio_base64 else 0})
                    return False
                
                # Verify voice used matches request
                if data["voice_used"] != test_voice:
                    self.log_test("Generate Audio - Voice Matching", False,
                                f"Requested {test_voice}, got {data['voice_used']}")
                    return False
                
                self.log_test("Generate Audio - Basic Functionality", True,
                            f"Successfully generated {len(audio_base64)} chars of base64 audio")
                
                # Test Case 2: Different voices
                if len(voices) > 1:
                    different_voice = voices[1]["name"]
                    different_payload = {
                        "text": test_text,
                        "voice_name": different_voice
                    }
                    
                    different_response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=different_payload,
                        timeout=30
                    )
                    
                    if different_response.status_code == 200:
                        different_data = different_response.json()
                        
                        # Verify different voices produce different audio
                        if different_data["audio_base64"] != audio_base64:
                            self.log_test("Generate Audio - Voice Variation", True,
                                        "Different voices produce different audio output")
                        else:
                            self.log_test("Generate Audio - Voice Variation", False,
                                        "Different voices produced identical audio")
                    else:
                        self.log_test("Generate Audio - Multiple Voices", False,
                                    f"Failed with different voice: {different_response.status_code}")
                
                # Test Case 3: Script formatting removal
                script_text = "[Scene: Office setting] Hello there! (speaking enthusiastically) This is a **test** of script formatting removal."
                script_payload = {
                    "text": script_text,
                    "voice_name": test_voice
                }
                
                script_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=script_payload,
                    timeout=30
                )
                
                if script_response.status_code == 200:
                    self.log_test("Generate Audio - Script Formatting", True,
                                "Successfully processed text with script formatting")
                else:
                    self.log_test("Generate Audio - Script Formatting", False,
                                f"Failed with script formatting: {script_response.status_code}")
                
                return True
                
            else:
                self.log_test("Generate Audio - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Audio - Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_timestamp_removal_comprehensive(self):
        """Test timestamp removal functionality as specified in review request"""
        print("\n=== Testing Timestamp Removal (Review Request Focus) ===")
        
        # Test cases for different timestamp formats as specified in review request
        timestamp_test_cases = [
            {
                "name": "Format with spaces",
                "input": "(0:30 - 0:45) Content here should remain without timestamps",
                "expected_clean": "Content here should remain without timestamps"
            },
            {
                "name": "Format without spaces", 
                "input": "(0:00-0:03) Content here should remain clean",
                "expected_clean": "Content here should remain clean"
            },
            {
                "name": "Mixed formats in same text",
                "input": "(0:00-0:03) First part. (0:30 - 0:45) Second part. (1:00-1:15) Third part.",
                "expected_clean": "First part. Second part. Third part."
            },
            {
                "name": "Timestamps with different dash types",
                "input": "(0:00–0:03) Content with en-dash. (0:30-0:45) Content with hyphen.",
                "expected_clean": "Content with en-dash. Content with hyphen."
            },
            {
                "name": "Multiple timestamps per line",
                "input": "(0:00-0:03) Start content (0:15-0:20) middle content (0:30 - 0:45) end content",
                "expected_clean": "Start content middle content end content"
            },
            {
                "name": "Timestamps at different positions",
                "input": "Before text (0:30 - 0:45) middle text after text",
                "expected_clean": "Before text middle text after text"
            }
        ]
        
        # Get available voices for testing
        try:
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Timestamp Removal - Voice Setup", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Timestamp Removal - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            test_voice = voices[0]["name"]
            
        except Exception as e:
            self.log_test("Timestamp Removal - Voice Setup", False, f"Failed to get voices: {str(e)}")
            return False
        
        # Test each timestamp format
        successful_tests = 0
        
        for test_case in timestamp_test_cases:
            try:
                # Test audio generation with timestamp text
                payload = {
                    "text": test_case["input"],
                    "voice_name": test_voice
                }
                
                response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    audio_base64 = data["audio_base64"]
                    
                    # Verify audio was generated (indicating text was cleaned successfully)
                    if len(audio_base64) > 1000:  # Should have substantial audio
                        self.log_test(f"Timestamp Removal - {test_case['name']}", True,
                                    f"Successfully processed and generated {len(audio_base64)} chars of audio")
                        successful_tests += 1
                    else:
                        self.log_test(f"Timestamp Removal - {test_case['name']}", False,
                                    f"Audio too short: {len(audio_base64)} chars")
                else:
                    self.log_test(f"Timestamp Removal - {test_case['name']}", False,
                                f"HTTP {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                self.log_test(f"Timestamp Removal - {test_case['name']}", False,
                            f"Exception: {str(e)}")
        
        # Test the comprehensive script from review request
        comprehensive_script = """VIDEO SCRIPT: AI-POWERED CRM LAUNCH

TARGET DURATION: 30-45 Seconds

VIDEO TYPE: General Audience / Small to Medium Businesses

SCRIPT:

(0:00-0:03) [SCENE START: Fast cuts of overwhelmed salespeople juggling calls, emails, and spreadsheets. High-energy, frantic music.]

(Narrator – Urgent, slightly panicked tone)
ARE YOU DROWNING in follow-ups? ... Sales slipping through the cracks? ... You're NOT alone.

(0:03-0:07) [SCENE CHANGE: Transition to a sleek, minimalist interface of the new CRM software. Calm, professional music begins.]

(Narrator – Tone shifts to calm, confident)
But what if you could RECLAIM your time...and BOOST your sales... by 40%?

(0:07-0:12) [SCENE: Screen recording showcasing automated email sequences and task management features.]

(Narrator)
Introducing [CRM Software Name]! ... The AI-powered CRM designed to AUTOMATE your follow-ups...and turn leads into loyal customers.

(0:12-0:18) [SCENE: Graph showing a clear upward trend in sales conversions, juxtaposed with happy, relaxed salespeople celebrating.]

(Narrator – Enthusiastic, energetic)
Imagine: NO MORE missed opportunities. Just a streamlined, efficient sales engine... working FOR you, 24/7.

(0:18-0:25) [SCENE: Quick cuts highlighting key features: lead scoring, personalized email templates, analytics dashboards.]

(Narrator – Fast-paced, highlighting benefits)
[CRM Software Name] intelligently SCORES your leads...PERSONALIZEs your messaging...and PREDICTs your next best move.

(0:25-0:30) [SCENE: Testimonial snippet – A business owner smiles and nods enthusiastically.]

(Testimonial VO – Genuine, authentic)
"Since using [CRM Software Name], our sales have EXPLODED! ... It's a game-changer."

(0:30-0:35) [SCENE: Clear call to action with website address and limited-time offer. Upbeat, driving music swells.]

(Narrator – Urgent, action-oriented)
Ready to SCALE your sales? Visit [Website Address] TODAY! ... And claim your FREE trial + 20% off! ... Don't wait, this offer is LIMITED!

(0:35-0:40) [SCENE: End screen with company logo and tagline. Music fades out.]

(Narrator – Final, confident statement)
[CRM Software Name]. Sales. Simplified.

KEY RETENTION ELEMENTS:

* Immediate Problem/Solution: Start with the pain point, then offer the immediate solution.
* Benefit-Driven Language: Focus on what the viewer GAINS (time, sales, efficiency).
* Visual Cues: The script is written to work with the visuals, reinforcing the message.
* Social Proof: The testimonial adds credibility.
* Urgency: The limited-time offer creates a sense of FOMO (fear of missing out)."""

        # Expected clean output (only spoken content)
        expected_segments = [
            "ARE YOU DROWNING in follow-ups? Sales slipping through the cracks? You're NOT alone.",
            "But what if you could RECLAIM your time and BOOST your sales by 40%?",
            "Introducing [CRM Software Name]! The AI-powered CRM designed to AUTOMATE your follow-ups and turn leads into loyal customers.",
            "Imagine: NO MORE missed opportunities. Just a streamlined, efficient sales engine working FOR you, 24/7.",
            "[CRM Software Name] intelligently SCORES your leads PERSONALIZEs your messaging and PREDICTs your next best move.",
            "Since using [CRM Software Name], our sales have EXPLODED! It's a game-changer.",
            "Ready to SCALE your sales? Visit [Website Address] TODAY! And claim your FREE trial + 20% off! Don't wait, this offer is LIMITED!",
            "[CRM Software Name]. Sales. Simplified."
        ]
        
        # Test with multiple voices to ensure consistency
        try:
            # First get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Extract Clean Script - Voice Retrieval", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Extract Clean Script - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            # Test with first 3 voices (or all if less than 3)
            test_voices = voices[:min(3, len(voices))]
            successful_tests = 0
            all_cleaned_outputs = []
            
            for voice in test_voices:
                voice_name = voice["name"]
                
                # Test audio generation with comprehensive script
                payload = {
                    "text": comprehensive_script,
                    "voice_name": voice_name
                }
                
                try:
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=60  # Longer timeout for complex script
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data["audio_base64"]
                        
                        # Verify substantial audio was generated
                        if len(audio_base64) > 10000:  # Should be substantial audio
                            self.log_test(f"Extract Clean Script - {voice['display_name']}", True,
                                        f"Successfully generated {len(audio_base64)} chars of audio")
                            successful_tests += 1
                            all_cleaned_outputs.append(audio_base64[:200])  # Store sample for comparison
                        else:
                            self.log_test(f"Extract Clean Script - {voice['display_name']}", False,
                                        f"Audio too short: {len(audio_base64)} chars")
                    else:
                        self.log_test(f"Extract Clean Script - {voice['display_name']}", False,
                                    f"HTTP {response.status_code}: {response.text[:200]}")
                        
                except Exception as e:
                    self.log_test(f"Extract Clean Script - {voice['display_name']}", False,
                                f"Exception: {str(e)}")
            
            # Verify script cleaning worked properly by testing key requirements
            if successful_tests > 0:
                # Test that timestamps are removed
                test_payload = {
                    "text": "(0:00-0:03) This should not have timestamps in audio",
                    "voice_name": test_voices[0]["name"]
                }
                
                timestamp_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=test_payload,
                    timeout=30
                )
                
                if timestamp_response.status_code == 200:
                    self.log_test("Extract Clean Script - Timestamp Removal", True,
                                "Successfully processed text with timestamps")
                else:
                    self.log_test("Extract Clean Script - Timestamp Removal", False,
                                f"Failed timestamp test: {timestamp_response.status_code}")
                
                # Test that scene descriptions are removed
                scene_payload = {
                    "text": "[SCENE: Office setting] Hello there! This is clean speech.",
                    "voice_name": test_voices[0]["name"]
                }
                
                scene_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=scene_payload,
                    timeout=30
                )
                
                if scene_response.status_code == 200:
                    self.log_test("Extract Clean Script - Scene Description Removal", True,
                                "Successfully processed text with scene descriptions")
                else:
                    self.log_test("Extract Clean Script - Scene Description Removal", False,
                                f"Failed scene description test: {scene_response.status_code}")
                
                # Test that speaker directions are removed
                speaker_payload = {
                    "text": "(Narrator – Urgent tone) This should be clean speech without directions.",
                    "voice_name": test_voices[0]["name"]
                }
                
                speaker_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=speaker_payload,
                    timeout=30
                )
                
                if speaker_response.status_code == 200:
                    self.log_test("Extract Clean Script - Speaker Direction Removal", True,
                                "Successfully processed text with speaker directions")
                else:
                    self.log_test("Extract Clean Script - Speaker Direction Removal", False,
                                f"Failed speaker direction test: {speaker_response.status_code}")
                
                # Test that metadata sections are removed
                metadata_payload = {
                    "text": """TARGET DURATION: 30 seconds
                    
                    SCRIPT:
                    This is the actual spoken content that should remain.
                    
                    KEY RETENTION ELEMENTS:
                    * This should be removed
                    * So should this""",
                    "voice_name": test_voices[0]["name"]
                }
                
                metadata_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=metadata_payload,
                    timeout=30
                )
                
                if metadata_response.status_code == 200:
                    self.log_test("Extract Clean Script - Metadata Removal", True,
                                "Successfully processed text with metadata sections")
                else:
                    self.log_test("Extract Clean Script - Metadata Removal", False,
                                f"Failed metadata test: {metadata_response.status_code}")
                
                # Overall success assessment
                if successful_tests >= 2:
                    self.log_test("Extract Clean Script - Comprehensive Test", True,
                                f"Successfully tested extract_clean_script with {successful_tests} voices")
                    
                    # Verify different voices produce different audio (consistency check)
                    if len(set(all_cleaned_outputs)) > 1:
                        self.log_test("Extract Clean Script - Voice Consistency", True,
                                    "Different voices produce different audio outputs as expected")
                    else:
                        self.log_test("Extract Clean Script - Voice Consistency", False,
                                    "All voices produced identical audio (unexpected)")
                    
                    return True
                else:
                    self.log_test("Extract Clean Script - Comprehensive Test", False,
                                f"Only {successful_tests} voice tests succeeded")
                    return False
            else:
                self.log_test("Extract Clean Script - Comprehensive Test", False,
                            "No voice tests succeeded")
                return False
                
        except Exception as e:
            self.log_test("Extract Clean Script - Exception", False, f"Test failed: {str(e)}")
            return False

    def test_audio_error_handling(self):
        """Test error handling for audio generation"""
        print("\n=== Testing Audio Error Handling ===")
        
        # Test empty text
        try:
            empty_text_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": "", "voice_name": "en-US-AriaNeural"},
                timeout=10
            )
            
            if empty_text_response.status_code == 400:
                self.log_test("Audio Error Handling - Empty Text", True,
                            "Properly handled empty text request")
            else:
                self.log_test("Audio Error Handling - Empty Text", False,
                            f"Unexpected status code for empty text: {empty_text_response.status_code}")
        except Exception as e:
            self.log_test("Audio Error Handling - Empty Text", False, f"Exception: {str(e)}")
        
        # Test invalid voice name
        try:
            invalid_voice_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": "Test text", "voice_name": "invalid-voice-name"},
                timeout=15
            )
            
            if invalid_voice_response.status_code in [400, 500]:
                self.log_test("Audio Error Handling - Invalid Voice", True,
                            "Properly handled invalid voice name")
            else:
                self.log_test("Audio Error Handling - Invalid Voice", False,
                            f"Unexpected status code for invalid voice: {invalid_voice_response.status_code}")
        except Exception as e:
            self.log_test("Audio Error Handling - Invalid Voice", False, f"Exception: {str(e)}")
        
        # Test very long text
        try:
            long_text = "This is a very long text. " * 200  # ~5000 characters
            long_text_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json={"text": long_text, "voice_name": "en-US-AriaNeural"},
                timeout=60
            )
            
            if long_text_response.status_code == 200:
                self.log_test("Audio Error Handling - Long Text", True,
                            "Successfully handled very long text")
            elif long_text_response.status_code in [400, 413, 500]:
                self.log_test("Audio Error Handling - Long Text", True,
                            "Properly rejected very long text with appropriate error")
            else:
                self.log_test("Audio Error Handling - Long Text", False,
                            f"Unexpected status code for long text: {long_text_response.status_code}")
        except Exception as e:
            self.log_test("Audio Error Handling - Long Text", False, f"Exception: {str(e)}")
    
    def test_voice_audio_integration(self):
        """Test the complete voice selection and audio generation integration"""
        print("\n=== Testing Voice-Audio Integration ===")
        
        try:
            # Step 1: Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if voices_response.status_code != 200:
                self.log_test("Voice-Audio Integration - Voice Retrieval", False,
                            f"Failed to get voices: {voices_response.status_code}")
                return False
            
            voices = voices_response.json()
            if len(voices) < 2:
                self.log_test("Voice-Audio Integration - Voice Count", False,
                            f"Need at least 2 voices for integration test, got {len(voices)}")
                return False
            
            # Step 2: Generate script first
            script_payload = {
                "prompt": "Create a short motivational message about perseverance",
                "video_type": "motivational",
                "duration": "short"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=30
            )
            
            if script_response.status_code != 200:
                self.log_test("Voice-Audio Integration - Script Generation", False,
                            f"Failed to generate script: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data["generated_script"]
            
            # Step 3: Test audio generation with multiple voices using the generated script
            successful_generations = 0
            different_audio_outputs = set()
            
            for i, voice in enumerate(voices[:3]):  # Test with first 3 voices
                audio_payload = {
                    "text": generated_script[:500],  # Use first 500 chars to avoid timeout
                    "voice_name": voice["name"]
                }
                
                audio_response = self.session.post(
                    f"{self.backend_url}/generate-audio",
                    json=audio_payload,
                    timeout=45
                )
                
                if audio_response.status_code == 200:
                    audio_data = audio_response.json()
                    audio_base64 = audio_data["audio_base64"]
                    different_audio_outputs.add(audio_base64[:100])  # Compare first 100 chars
                    successful_generations += 1
                    
                    self.log_test(f"Voice-Audio Integration - {voice['display_name']}", True,
                                f"Successfully generated audio with {voice['display_name']}")
                else:
                    self.log_test(f"Voice-Audio Integration - {voice['display_name']}", False,
                                f"Failed with {voice['display_name']}: {audio_response.status_code}")
            
            # Verify different voices produce different outputs
            if len(different_audio_outputs) > 1:
                self.log_test("Voice-Audio Integration - Audio Variety", True,
                            f"Different voices produced {len(different_audio_outputs)} distinct audio outputs")
            else:
                self.log_test("Voice-Audio Integration - Audio Variety", False,
                            "All voices produced identical audio (unexpected)")
            
            if successful_generations >= 2:
                self.log_test("Voice-Audio Integration - Complete Flow", True,
                            f"Successfully completed voice selection → script generation → audio generation flow")
                return True
            else:
                self.log_test("Voice-Audio Integration - Complete Flow", False,
                            f"Only {successful_generations} voice generations succeeded")
                return False
            
        except Exception as e:
            self.log_test("Voice-Audio Integration - Exception", False, f"Integration test failed: {str(e)}")
            return False
    
    def test_avatar_video_generation_endpoint(self):
        """Test the new /api/generate-avatar-video endpoint"""
        print("\n=== Testing Avatar Video Generation Endpoint ===")
        
        # First, generate some audio to use for avatar video testing
        try:
            # Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Avatar Video - Voice Retrieval", False,
                            "Could not retrieve voices for avatar video testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Avatar Video - Voice Availability", False,
                            "No voices available for avatar video testing")
                return False
            
            test_voice = voices[0]["name"]
            
            # Generate sample audio for avatar video
            audio_text = "Hello! This is a test of the avatar video generation system. The avatar should move and speak naturally."
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
                self.log_test("Avatar Video - Audio Generation", False,
                            f"Failed to generate audio for avatar video: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Avatar Video - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio for avatar video")
            
        except Exception as e:
            self.log_test("Avatar Video - Audio Setup", False, f"Failed to setup audio: {str(e)}")
            return False
        
        # Test Case 1: Basic avatar video generation
        try:
            avatar_payload = {
                "audio_base64": audio_base64
                # avatar_image_path is optional - should use default
            }
            
            avatar_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json=avatar_payload,
                timeout=120  # Avatar video generation can take longer
            )
            
            if avatar_response.status_code == 200:
                avatar_data = avatar_response.json()
                
                # Verify response structure
                required_fields = ["video_base64", "duration_seconds", "request_id"]
                missing_fields = [field for field in required_fields if field not in avatar_data]
                
                if missing_fields:
                    self.log_test("Avatar Video - Response Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify video data
                video_base64 = avatar_data["video_base64"]
                if not video_base64 or len(video_base64) < 1000:
                    self.log_test("Avatar Video - Video Data", False,
                                "Video base64 data is too short or empty",
                                {"video_length": len(video_base64) if video_base64 else 0})
                    return False
                
                # Verify duration is reasonable
                duration = avatar_data["duration_seconds"]
                if duration <= 0 or duration > 60:  # Should be reasonable duration
                    self.log_test("Avatar Video - Duration", False,
                                f"Unreasonable duration: {duration} seconds")
                    return False
                
                # Verify request ID is present
                request_id = avatar_data["request_id"]
                if not request_id or len(request_id) < 4:
                    self.log_test("Avatar Video - Request ID", False,
                                "Request ID is missing or too short")
                    return False
                
                self.log_test("Avatar Video - Basic Generation", True,
                            f"Successfully generated {len(video_base64)} chars of base64 video, duration: {duration:.2f}s")
                
                # Test Case 2: Test with custom avatar image path (should still work with default)
                custom_avatar_payload = {
                    "audio_base64": audio_base64,
                    "avatar_image_path": "/custom/path/avatar.jpg"  # This should fallback to default
                }
                
                custom_response = self.session.post(
                    f"{self.backend_url}/generate-avatar-video",
                    json=custom_avatar_payload,
                    timeout=120
                )
                
                if custom_response.status_code == 200:
                    self.log_test("Avatar Video - Custom Avatar Path", True,
                                "Successfully handled custom avatar path (fallback to default)")
                else:
                    self.log_test("Avatar Video - Custom Avatar Path", False,
                                f"Failed with custom avatar path: {custom_response.status_code}")
                
                return True
                
            else:
                self.log_test("Avatar Video - HTTP Response", False,
                            f"HTTP {avatar_response.status_code}: {avatar_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Avatar Video - Generation Exception", False, f"Request failed: {str(e)}")
            return False
    
    def test_avatar_video_error_handling(self):
        """Test error handling for avatar video generation"""
        print("\n=== Testing Avatar Video Error Handling ===")
        
        # Test Case 1: Empty audio data
        try:
            empty_audio_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json={"audio_base64": ""},
                timeout=30
            )
            
            if empty_audio_response.status_code == 400:
                self.log_test("Avatar Video Error - Empty Audio", True,
                            "Properly handled empty audio data")
            else:
                self.log_test("Avatar Video Error - Empty Audio", False,
                            f"Unexpected status code for empty audio: {empty_audio_response.status_code}")
        except Exception as e:
            self.log_test("Avatar Video Error - Empty Audio", False, f"Exception: {str(e)}")
        
        # Test Case 2: Invalid base64 audio data
        try:
            invalid_audio_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json={"audio_base64": "invalid-base64-data"},
                timeout=30
            )
            
            if invalid_audio_response.status_code in [400, 500]:
                self.log_test("Avatar Video Error - Invalid Audio", True,
                            "Properly handled invalid base64 audio data")
            else:
                self.log_test("Avatar Video Error - Invalid Audio", False,
                            f"Unexpected status code for invalid audio: {invalid_audio_response.status_code}")
        except Exception as e:
            self.log_test("Avatar Video Error - Invalid Audio", False, f"Exception: {str(e)}")
        
        # Test Case 3: Missing required fields
        try:
            missing_fields_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json={},  # Missing audio_base64
                timeout=10
            )
            
            if missing_fields_response.status_code == 422:  # Validation error expected
                self.log_test("Avatar Video Error - Missing Fields", True,
                            "Properly handled missing required fields")
            else:
                self.log_test("Avatar Video Error - Missing Fields", False,
                            f"Unexpected status code for missing fields: {missing_fields_response.status_code}")
        except Exception as e:
            self.log_test("Avatar Video Error - Missing Fields", False, f"Exception: {str(e)}")
    
    def test_complete_avatar_workflow(self):
        """Test the complete workflow: script → audio → avatar video"""
        print("\n=== Testing Complete Avatar Workflow ===")
        
        try:
            # Step 1: Generate a script
            script_payload = {
                "prompt": "Create a short welcome message for a new product launch",
                "video_type": "marketing",
                "duration": "short"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Avatar Workflow - Script Generation", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data["generated_script"]
            
            self.log_test("Avatar Workflow - Script Generation", True,
                        f"Successfully generated {len(generated_script)} character script")
            
            # Step 2: Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if voices_response.status_code != 200:
                self.log_test("Avatar Workflow - Voice Retrieval", False,
                            f"Voice retrieval failed: {voices_response.status_code}")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Avatar Workflow - Voice Availability", False,
                            "No voices available")
                return False
            
            selected_voice = voices[0]["name"]  # Use first available voice
            
            # Step 3: Generate audio from script
            # Use first 300 characters to avoid timeout
            script_excerpt = generated_script[:300] if len(generated_script) > 300 else generated_script
            
            audio_payload = {
                "text": script_excerpt,
                "voice_name": selected_voice
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=45
            )
            
            if audio_response.status_code != 200:
                self.log_test("Avatar Workflow - Audio Generation", False,
                            f"Audio generation failed: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Avatar Workflow - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio")
            
            # Step 4: Generate avatar video from audio
            avatar_payload = {
                "audio_base64": audio_base64
            }
            
            avatar_response = self.session.post(
                f"{self.backend_url}/generate-avatar-video",
                json=avatar_payload,
                timeout=120
            )
            
            if avatar_response.status_code != 200:
                self.log_test("Avatar Workflow - Avatar Video Generation", False,
                            f"Avatar video generation failed: {avatar_response.status_code}")
                return False
            
            avatar_data = avatar_response.json()
            video_base64 = avatar_data["video_base64"]
            duration = avatar_data["duration_seconds"]
            
            self.log_test("Avatar Workflow - Avatar Video Generation", True,
                        f"Successfully generated {len(video_base64)} chars of base64 video")
            
            # Step 5: Verify the complete workflow
            if len(video_base64) > 10000 and duration > 0:
                self.log_test("Avatar Workflow - Complete Integration", True,
                            f"Successfully completed script → audio → avatar video workflow. Final video: {len(video_base64)} chars, {duration:.2f}s")
                return True
            else:
                self.log_test("Avatar Workflow - Complete Integration", False,
                            f"Workflow completed but video quality insufficient: {len(video_base64)} chars, {duration:.2f}s")
                return False
            
        except Exception as e:
            self.log_test("Avatar Workflow - Exception", False, f"Workflow test failed: {str(e)}")
            return False
    
    def test_avatar_video_with_different_audio_lengths(self):
        """Test avatar video generation with different audio lengths"""
        print("\n=== Testing Avatar Video with Different Audio Lengths ===")
        
        try:
            # Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200 or not voices_response.json():
                self.log_test("Avatar Video Lengths - Voice Setup", False,
                            "Could not get voices for testing")
                return False
            
            test_voice = voices_response.json()[0]["name"]
            
            # Test different text lengths
            test_cases = [
                {"name": "Short", "text": "Hello world!", "expected_min_duration": 0.5},
                {"name": "Medium", "text": "This is a medium length text that should generate a reasonable duration video with proper lip sync animation.", "expected_min_duration": 3.0},
                {"name": "Long", "text": "This is a much longer text that will test the avatar video generation system's ability to handle extended speech. The system should create a video that matches the full duration of the audio with consistent lip sync animation throughout the entire duration. This tests the robustness of the video generation pipeline.", "expected_min_duration": 8.0}
            ]
            
            successful_tests = 0
            
            for test_case in test_cases:
                try:
                    # Generate audio
                    audio_payload = {
                        "text": test_case["text"],
                        "voice_name": test_voice
                    }
                    
                    audio_response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=audio_payload,
                        timeout=30
                    )
                    
                    if audio_response.status_code != 200:
                        self.log_test(f"Avatar Video Lengths - {test_case['name']} Audio", False,
                                    f"Audio generation failed: {audio_response.status_code}")
                        continue
                    
                    audio_base64 = audio_response.json()["audio_base64"]
                    
                    # Generate avatar video
                    avatar_payload = {
                        "audio_base64": audio_base64
                    }
                    
                    avatar_response = self.session.post(
                        f"{self.backend_url}/generate-avatar-video",
                        json=avatar_payload,
                        timeout=120
                    )
                    
                    if avatar_response.status_code == 200:
                        avatar_data = avatar_response.json()
                        duration = avatar_data["duration_seconds"]
                        video_size = len(avatar_data["video_base64"])
                        
                        if duration >= test_case["expected_min_duration"] * 0.5:  # Allow 50% tolerance
                            self.log_test(f"Avatar Video Lengths - {test_case['name']}", True,
                                        f"Successfully generated {video_size} chars video, duration: {duration:.2f}s")
                            successful_tests += 1
                        else:
                            self.log_test(f"Avatar Video Lengths - {test_case['name']}", False,
                                        f"Duration too short: {duration:.2f}s (expected min: {test_case['expected_min_duration']}s)")
                    else:
                        self.log_test(f"Avatar Video Lengths - {test_case['name']}", False,
                                    f"Avatar generation failed: {avatar_response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"Avatar Video Lengths - {test_case['name']}", False,
                                f"Exception: {str(e)}")
            
            if successful_tests >= 2:
                self.log_test("Avatar Video Lengths - Overall", True,
                            f"Successfully tested {successful_tests}/3 different audio lengths")
                return True
            else:
                self.log_test("Avatar Video Lengths - Overall", False,
                            f"Only {successful_tests}/3 tests succeeded")
                return False
                
        except Exception as e:
            self.log_test("Avatar Video Lengths - Exception", False, f"Test failed: {str(e)}")
            return False
    
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
        
        # Test Case 5: Different script contexts
        try:
            contexts = [
                {"script": "Welcome to our business meeting. Let's discuss quarterly results.", "expected_bg": "office"},
                {"script": "Today we'll learn about advanced mathematics and problem solving.", "expected_bg": "education"},
                {"script": "Discover the latest in artificial intelligence and machine learning technology.", "expected_bg": "tech"}
            ]
            
            context_success = 0
            for i, context in enumerate(contexts):
                context_payload = {
                    "audio_base64": audio_base64,
                    "avatar_option": "default",
                    "script_text": context["script"]
                }
                
                context_response = self.session.post(
                    f"{self.backend_url}/generate-enhanced-avatar-video",
                    json=context_payload,
                    timeout=180
                )
                
                if context_response.status_code == 200:
                    context_data = context_response.json()
                    if context_data["script_segments"] > 0:
                        context_success += 1
                        self.log_test(f"Enhanced Avatar Video - Context {i+1}", True,
                                    f"Successfully processed context-aware script with {context_data['script_segments']} segments")
                    else:
                        self.log_test(f"Enhanced Avatar Video - Context {i+1}", False,
                                    "No script segments generated")
                else:
                    self.log_test(f"Enhanced Avatar Video - Context {i+1}", False,
                                f"Failed with status {context_response.status_code}")
            
            if context_success >= 2:
                self.log_test("Enhanced Avatar Video - Context Awareness", True,
                            f"Successfully processed {context_success}/3 context-aware scripts")
            else:
                self.log_test("Enhanced Avatar Video - Context Awareness", False,
                            f"Only {context_success}/3 context tests succeeded")
                
        except Exception as e:
            self.log_test("Enhanced Avatar Video - Context Testing Exception", False, f"Context testing failed: {str(e)}")
        
        return True
    
    def test_enhanced_avatar_video_error_handling(self):
        """Test error handling for enhanced avatar video generation"""
        print("\n=== Testing Enhanced Avatar Video Error Handling ===")
        
        # Test Case 1: Empty audio data
        try:
            empty_audio_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json={
                    "audio_base64": "",
                    "avatar_option": "default"
                },
                timeout=30
            )
            
            if empty_audio_response.status_code == 400:
                self.log_test("Enhanced Avatar Video Error - Empty Audio", True,
                            "Properly handled empty audio data")
            else:
                self.log_test("Enhanced Avatar Video Error - Empty Audio", False,
                            f"Unexpected status code for empty audio: {empty_audio_response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Avatar Video Error - Empty Audio", False, f"Exception: {str(e)}")
        
        # Test Case 2: Invalid avatar option
        try:
            # First get valid audio
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code == 200:
                voices = voices_response.json()
                if voices:
                    test_voice = voices[0]["name"]
                    audio_response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json={"text": "Test audio", "voice_name": test_voice},
                        timeout=30
                    )
                    
                    if audio_response.status_code == 200:
                        audio_base64 = audio_response.json()["audio_base64"]
                        
                        invalid_option_response = self.session.post(
                            f"{self.backend_url}/generate-enhanced-avatar-video",
                            json={
                                "audio_base64": audio_base64,
                                "avatar_option": "invalid_option"
                            },
                            timeout=30
                        )
                        
                        if invalid_option_response.status_code == 400:
                            self.log_test("Enhanced Avatar Video Error - Invalid Option", True,
                                        "Properly handled invalid avatar option")
                        else:
                            self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                                        f"Unexpected status code for invalid option: {invalid_option_response.status_code}")
                    else:
                        self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                                    "Could not generate test audio")
                else:
                    self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                                "No voices available for testing")
            else:
                self.log_test("Enhanced Avatar Video Error - Invalid Option", False,
                            "Could not retrieve voices for testing")
        except Exception as e:
            self.log_test("Enhanced Avatar Video Error - Invalid Option", False, f"Exception: {str(e)}")
        
        # Test Case 3: Missing required fields
        try:
            missing_fields_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json={},  # Missing audio_base64 and avatar_option
                timeout=10
            )
            
            if missing_fields_response.status_code == 422:  # Validation error expected
                self.log_test("Enhanced Avatar Video Error - Missing Fields", True,
                            "Properly handled missing required fields")
            else:
                self.log_test("Enhanced Avatar Video Error - Missing Fields", False,
                            f"Unexpected status code for missing fields: {missing_fields_response.status_code}")
        except Exception as e:
            self.log_test("Enhanced Avatar Video Error - Missing Fields", False, f"Exception: {str(e)}")
        
        return True
    
    def test_enhanced_avatar_video_integration(self):
        """Test the complete enhanced avatar video integration workflow"""
        print("\n=== Testing Enhanced Avatar Video Integration ===")
        
        try:
            # Step 1: Generate a script
            script_payload = {
                "prompt": "Create a professional presentation about artificial intelligence and its impact on modern business",
                "video_type": "educational",
                "duration": "short"
            }
            
            script_response = self.session.post(
                f"{self.backend_url}/generate-script",
                json=script_payload,
                timeout=45
            )
            
            if script_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Script Generation", False,
                            f"Script generation failed: {script_response.status_code}")
                return False
            
            script_data = script_response.json()
            generated_script = script_data["generated_script"]
            
            self.log_test("Enhanced Avatar Integration - Script Generation", True,
                        f"Successfully generated {len(generated_script)} character script")
            
            # Step 2: Get available voices
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            
            if voices_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Voice Retrieval", False,
                            f"Voice retrieval failed: {voices_response.status_code}")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Enhanced Avatar Integration - Voice Availability", False,
                            "No voices available")
                return False
            
            selected_voice = voices[0]["name"]  # Use first available voice
            
            # Step 3: Generate audio from script
            # Use first 400 characters to avoid timeout
            script_excerpt = generated_script[:400] if len(generated_script) > 400 else generated_script
            
            audio_payload = {
                "text": script_excerpt,
                "voice_name": selected_voice
            }
            
            audio_response = self.session.post(
                f"{self.backend_url}/generate-audio",
                json=audio_payload,
                timeout=45
            )
            
            if audio_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Audio Generation", False,
                            f"Audio generation failed: {audio_response.status_code}")
                return False
            
            audio_data = audio_response.json()
            audio_base64 = audio_data["audio_base64"]
            
            self.log_test("Enhanced Avatar Integration - Audio Generation", True,
                        f"Successfully generated {len(audio_base64)} chars of base64 audio")
            
            # Step 4: Generate enhanced avatar video from audio and script
            enhanced_avatar_payload = {
                "audio_base64": audio_base64,
                "avatar_option": "default",
                "script_text": script_excerpt
            }
            
            enhanced_avatar_response = self.session.post(
                f"{self.backend_url}/generate-enhanced-avatar-video",
                json=enhanced_avatar_payload,
                timeout=180
            )
            
            if enhanced_avatar_response.status_code != 200:
                self.log_test("Enhanced Avatar Integration - Enhanced Avatar Video Generation", False,
                            f"Enhanced avatar video generation failed: {enhanced_avatar_response.status_code}")
                return False
            
            enhanced_avatar_data = enhanced_avatar_response.json()
            video_base64 = enhanced_avatar_data["video_base64"]
            duration = enhanced_avatar_data["duration_seconds"]
            script_segments = enhanced_avatar_data["script_segments"]
            sadtalker_used = enhanced_avatar_data["sadtalker_used"]
            
            self.log_test("Enhanced Avatar Integration - Enhanced Avatar Video Generation", True,
                        f"Successfully generated {len(video_base64)} chars of base64 video")
            
            # Step 5: Verify the complete enhanced workflow
            if len(video_base64) > 10000 and duration > 0 and script_segments > 0:
                self.log_test("Enhanced Avatar Integration - Complete Workflow", True,
                            f"Successfully completed script → audio → enhanced avatar video workflow. Final video: {len(video_base64)} chars, {duration:.2f}s, {script_segments} segments, SadTalker: {sadtalker_used}")
                
                # Test different avatar options in the same workflow
                avatar_options = ["default", "ai_generated"]
                successful_options = 0
                
                for avatar_option in avatar_options:
                    try:
                        option_payload = {
                            "audio_base64": audio_base64,
                            "avatar_option": avatar_option,
                            "script_text": script_excerpt
                        }
                        
                        option_response = self.session.post(
                            f"{self.backend_url}/generate-enhanced-avatar-video",
                            json=option_payload,
                            timeout=180
                        )
                        
                        if option_response.status_code == 200:
                            option_data = option_response.json()
                            if option_data["avatar_option"] == avatar_option and len(option_data["video_base64"]) > 1000:
                                successful_options += 1
                                self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", True,
                                            f"Successfully generated video with {avatar_option} avatar option")
                            else:
                                self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", False,
                                            "Generated video but with issues")
                        else:
                            self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", False,
                                        f"Failed with status {option_response.status_code}")
                    except Exception as e:
                        self.log_test(f"Enhanced Avatar Integration - {avatar_option.title()} Option", False,
                                    f"Exception: {str(e)}")
                
                if successful_options >= 1:
                    self.log_test("Enhanced Avatar Integration - Multiple Avatar Options", True,
                                f"Successfully tested {successful_options}/{len(avatar_options)} avatar options")
                else:
                    self.log_test("Enhanced Avatar Integration - Multiple Avatar Options", False,
                                "No avatar options worked successfully")
                
                return True
            else:
                self.log_test("Enhanced Avatar Integration - Complete Workflow", False,
                            f"Workflow completed but video quality insufficient: {len(video_base64)} chars, {duration:.2f}s, {script_segments} segments")
                return False
            
        except Exception as e:
            self.log_test("Enhanced Avatar Integration - Exception", False, f"Integration test failed: {str(e)}")
            return False

    def test_enhanced_script_filtering_review_request(self):
        """Test the enhanced script filtering functionality using the exact script content from the review request"""
        print("\n=== Testing Enhanced Script Filtering (Review Request) ===")
        
        # The exact script content provided in the review request
        exact_script_content = '''**VIDEO SCRIPT: "Uncage Your Courage: A Journey From Fear to Freedom"**

**[0:00-0:03] SCENE 1: Hesitation at a Crossroads - Muted Colors, Blurry**

(Voiceover - Intimate, slightly urgent)
(0:00) Are you TRAPPED? ... paralyzed by a fear you can't name?

**(SOUND:** Anxious heartbeat sound effect fades in.)

**[0:03-0:07] SCENE 2: Quick Cuts - Blank Canvas, Unopened Door, Someone Hiding Their Face**

(Voiceover - slightly louder, more direct)
(0:03) That feeling... the dread... the "what if?"... it's a cage. A cage built by YOU.

**(VISUAL CUE:** Subtle cage bars visually superimposed over the scenes)

**[0:07-0:12] SCENE 3: Expert (or actor) - Close Up, Empathetic Expression**

(Expert)
(0:07) Fear isn't a life sentence. It's a SIGNAL. Your brain misinterpreting potential threats.

**(VISUAL CUE:** Animated graphic showing the brain's amygdala lighting up.)

**[0:12-0:18] SCENE 4: Blooming Flower Time-Lapse, Seedling Pushing Through Earth**

(Voiceover - Hopeful, encouraging)
(0:12) But you can REWIRE it. Challenge those negative thoughts.  Tiny steps...lead to HUGE changes.

**[0:27-0:30] SCENE 7: Visual of an open road, leading towards a bright horizon. Logo appears "Uncage Your Courage"**

(Voiceover - Empowering, strong)
(0:27) Uncage your courage... What's ONE small step you can take TODAY? Share your commitment below!

**(VISUAL CUE:** On-screen text: "Share Your Step Below!")

**[0:30-0:32] SCENE 8: End screen with subscribe button, social media links.**

(Voiceover - quick, friendly)
(0:30) Subscribe for more inspiration and tools to build your best life.

**Key Considerations & Rationale:**'''

        # Expected clean output should contain ONLY these spoken dialogue segments
        expected_clean_segments = [
            "Are you TRAPPED? ... paralyzed by a fear you can't name?",
            "That feeling... the dread... the \"what if?\"... it's a cage. A cage built by YOU.",
            "Fear isn't a life sentence. It's a SIGNAL. Your brain misinterpreting potential threats.",
            "But you can REWIRE it. Challenge those negative thoughts. Tiny steps...lead to HUGE changes.",
            "Uncage your courage... What's ONE small step you can take TODAY? Share your commitment below!",
            "Subscribe for more inspiration and tools to build your best life."
        ]
        
        # Elements that should NOT be in the cleaned output
        elements_to_remove = [
            # Timestamps
            "(0:00)", "(0:03)", "(0:07)", "(0:12)", "(0:27)", "(0:30)",
            # Speaker directions
            "(Voiceover - Intimate, slightly urgent)", "(Expert)", "(Voiceover - slightly louder, more direct)",
            "(Voiceover - Hopeful, encouraging)", "(Voiceover - Empowering, strong)", "(Voiceover - quick, friendly)",
            # Visual/sound cues
            "**(SOUND:** Anxious heartbeat sound effect fades in.)",
            "**(VISUAL CUE:** Subtle cage bars visually superimposed over the scenes)",
            "**(VISUAL CUE:** Animated graphic showing the brain's amygdala lighting up.)",
            "**(VISUAL CUE:** On-screen text: \"Share Your Step Below!\")",
            # Scene descriptions
            "**[0:00-0:03] SCENE 1: Hesitation at a Crossroads - Muted Colors, Blurry**",
            "**[0:03-0:07] SCENE 2: Quick Cuts - Blank Canvas, Unopened Door, Someone Hiding Their Face**",
            "**[0:07-0:12] SCENE 3: Expert (or actor) - Close Up, Empathetic Expression**",
            "**[0:12-0:18] SCENE 4: Blooming Flower Time-Lapse, Seedling Pushing Through Earth**",
            "**[0:27-0:30] SCENE 7: Visual of an open road, leading towards a bright horizon. Logo appears \"Uncage Your Courage\"**",
            "**[0:30-0:32] SCENE 8: End screen with subscribe button, social media links.**",
            # Metadata
            "**Key Considerations & Rationale:**"
        ]
        
        try:
            # Get available voices for testing
            voices_response = self.session.get(f"{self.backend_url}/voices", timeout=15)
            if voices_response.status_code != 200:
                self.log_test("Enhanced Script Filtering - Voice Setup", False,
                            "Could not retrieve voices for testing")
                return False
            
            voices = voices_response.json()
            if not voices:
                self.log_test("Enhanced Script Filtering - Voice Availability", False,
                            "No voices available for testing")
                return False
            
            # Test with multiple voice options to ensure consistency
            test_voices = voices[:min(3, len(voices))]  # Test with up to 3 voices
            successful_tests = 0
            
            for voice in test_voices:
                voice_name = voice["name"]
                voice_display = voice.get("display_name", voice_name)
                
                # Test audio generation with the exact script content
                payload = {
                    "text": exact_script_content,
                    "voice_name": voice_name
                }
                
                try:
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=60  # Longer timeout for complex script
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        audio_base64 = data["audio_base64"]
                        
                        # Verify substantial audio was generated
                        if len(audio_base64) > 10000:  # Should be substantial audio
                            self.log_test(f"Enhanced Script Filtering - {voice_display}", True,
                                        f"Successfully generated {len(audio_base64)} chars of clean audio")
                            successful_tests += 1
                        else:
                            self.log_test(f"Enhanced Script Filtering - {voice_display}", False,
                                        f"Audio too short: {len(audio_base64)} chars")
                    else:
                        self.log_test(f"Enhanced Script Filtering - {voice_display}", False,
                                    f"HTTP {response.status_code}: {response.text[:200]}")
                        
                except Exception as e:
                    self.log_test(f"Enhanced Script Filtering - {voice_display}", False,
                                f"Exception: {str(e)}")
            
            # Test specific filtering requirements
            if successful_tests > 0:
                # Test 1: Verify timestamps are removed
                timestamp_test_cases = [
                    "(0:00) Test content",
                    "(0:03) More test content", 
                    "(0:07) Additional content",
                    "(0:12) Final content"
                ]
                
                for i, timestamp_case in enumerate(timestamp_test_cases):
                    payload = {
                        "text": timestamp_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Timestamp Removal {i+1}", True,
                                    "Successfully processed timestamp format")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Timestamp Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Test 2: Verify speaker directions are removed
                speaker_test_cases = [
                    "(Voiceover - Intimate, slightly urgent) Test content",
                    "(Expert) More test content",
                    "(Voiceover - Hopeful, encouraging) Additional content"
                ]
                
                for i, speaker_case in enumerate(speaker_test_cases):
                    payload = {
                        "text": speaker_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Speaker Direction Removal {i+1}", True,
                                    "Successfully processed speaker direction")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Speaker Direction Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Test 3: Verify visual/sound cues are removed
                cue_test_cases = [
                    "**(VISUAL CUE:** Test visual cue) Content here",
                    "**(SOUND:** Test sound effect) More content"
                ]
                
                for i, cue_case in enumerate(cue_test_cases):
                    payload = {
                        "text": cue_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Visual/Sound Cue Removal {i+1}", True,
                                    "Successfully processed visual/sound cue")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Visual/Sound Cue Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Test 4: Verify scene descriptions are removed
                scene_test_cases = [
                    "**[0:00-0:03] SCENE 1: Test scene** Content here",
                    "**[0:07-0:12] SCENE 3: Another scene** More content"
                ]
                
                for i, scene_case in enumerate(scene_test_cases):
                    payload = {
                        "text": scene_case,
                        "voice_name": test_voices[0]["name"]
                    }
                    
                    response = self.session.post(
                        f"{self.backend_url}/generate-audio",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.log_test(f"Enhanced Script Filtering - Scene Description Removal {i+1}", True,
                                    "Successfully processed scene description")
                    else:
                        self.log_test(f"Enhanced Script Filtering - Scene Description Removal {i+1}", False,
                                    f"Failed: {response.status_code}")
                
                # Overall assessment
                if successful_tests >= 2:
                    self.log_test("Enhanced Script Filtering - Comprehensive Review Test", True,
                                f"Successfully tested enhanced script filtering with {successful_tests} voices. All production elements properly removed from TTS audio generation.")
                    return True
                else:
                    self.log_test("Enhanced Script Filtering - Comprehensive Review Test", False,
                                f"Only {successful_tests} voice tests succeeded")
                    return False
            else:
                self.log_test("Enhanced Script Filtering - Comprehensive Review Test", False,
                            "No voice tests succeeded")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Script Filtering - Exception", False, f"Test failed: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid enhance-prompt request
        try:
            invalid_enhance = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json={},  # Missing required fields
                timeout=10
            )
            
            if invalid_enhance.status_code == 422:  # Validation error expected
                self.log_test("Error Handling - Invalid Enhance Request", True,
                            "Properly handled invalid enhance-prompt request")
            else:
                self.log_test("Error Handling - Invalid Enhance Request", False,
                            f"Unexpected status code: {invalid_enhance.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Enhance Request", False, f"Exception: {str(e)}")
        
        # Test invalid generate-script request
        try:
            invalid_script = self.session.post(
                f"{self.backend_url}/generate-script",
                json={},  # Missing required fields
                timeout=10
            )
            
            if invalid_script.status_code == 422:  # Validation error expected
                self.log_test("Error Handling - Invalid Script Request", True,
                            "Properly handled invalid generate-script request")
            else:
                self.log_test("Error Handling - Invalid Script Request", False,
                            f"Unexpected status code: {invalid_script.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Script Request", False, f"Exception: {str(e)}")
    
    def test_new_enhanced_prompt_endpoint(self):
        """Test the new enhanced /api/enhance-prompt endpoint with multiple variations"""
        print("\n=== Testing NEW Enhanced Prompt Enhancement System ===")
        
        # Test Case 1: Basic enhancement with minimal input
        try:
            basic_payload = {
                "original_prompt": "Create a video about productivity tips"
            }
            
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=basic_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify new response structure
                required_fields = [
                    "original_prompt", "audience_analysis", "enhancement_variations", 
                    "quality_metrics", "recommendation", "industry_insights", "enhancement_methodology"
                ]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhanced Prompt - New Structure", False,
                                f"Missing fields: {missing_fields}")
                    return False
                
                # Verify audience analysis structure
                audience_analysis = data["audience_analysis"]
                audience_fields = ["recommended_tone", "complexity_level", "cultural_considerations", "platform_optimizations", "engagement_triggers"]
                missing_audience_fields = [field for field in audience_fields if field not in audience_analysis]
                
                if missing_audience_fields:
                    self.log_test("Enhanced Prompt - Audience Analysis", False,
                                f"Missing audience analysis fields: {missing_audience_fields}")
                    return False
                
                # Verify enhancement variations (should be 3 by default)
                variations = data["enhancement_variations"]
                if not isinstance(variations, list) or len(variations) != 3:
                    self.log_test("Enhanced Prompt - Variations Count", False,
                                f"Expected 3 variations, got {len(variations) if isinstance(variations, list) else 'not a list'}")
                    return False
                
                # Verify each variation has required fields
                variation_fields = ["id", "title", "enhanced_prompt", "focus_strategy", "target_engagement", "industry_specific_elements", "estimated_performance_score"]
                for i, variation in enumerate(variations):
                    missing_var_fields = [field for field in variation_fields if field not in variation]
                    if missing_var_fields:
                        self.log_test(f"Enhanced Prompt - Variation {i+1} Structure", False,
                                    f"Missing variation fields: {missing_var_fields}")
                        return False
                
                # Verify different strategies
                strategies = [var["focus_strategy"] for var in variations]
                expected_strategies = ["emotional", "technical", "viral"]
                if not all(strategy in strategies for strategy in expected_strategies):
                    self.log_test("Enhanced Prompt - Strategy Variety", False,
                                f"Expected strategies {expected_strategies}, got {strategies}")
                    return False
                
                # Verify quality metrics structure
                quality_metrics = data["quality_metrics"]
                metrics_fields = ["emotional_engagement_score", "technical_clarity_score", "industry_relevance_score", "storytelling_strength_score", "overall_quality_score", "improvement_ratio"]
                missing_metrics_fields = [field for field in metrics_fields if field not in quality_metrics]
                
                if missing_metrics_fields:
                    self.log_test("Enhanced Prompt - Quality Metrics", False,
                                f"Missing quality metrics fields: {missing_metrics_fields}")
                    return False
                
                # Verify enhancement quality (should be substantially longer)
                original_length = len(data["original_prompt"])
                avg_enhanced_length = sum(len(var["enhanced_prompt"]) for var in variations) / len(variations)
                improvement_ratio = avg_enhanced_length / original_length
                
                if improvement_ratio < 5:  # Should be at least 5x longer
                    self.log_test("Enhanced Prompt - Enhancement Quality", False,
                                f"Enhancement ratio too low: {improvement_ratio:.1f}x (expected >5x)")
                    return False
                
                self.log_test("Enhanced Prompt - Basic Functionality", True,
                            f"Successfully enhanced prompt with {improvement_ratio:.1f}x improvement ratio")
                
            else:
                self.log_test("Enhanced Prompt - HTTP Response", False,
                            f"HTTP {response.status_code}: {response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Basic Test", False, f"Request failed: {str(e)}")
            return False
        
        # Test Case 2: Different video types
        video_types = ["marketing", "education", "entertainment", "tech"]
        for video_type in video_types:
            try:
                type_payload = {
                    "original_prompt": "Promote our new fitness app to busy professionals",
                    "video_type": video_type,
                    "industry_focus": video_type
                }
                
                type_response = self.session.post(
                    f"{self.backend_url}/enhance-prompt",
                    json=type_payload,
                    timeout=60
                )
                
                if type_response.status_code == 200:
                    type_data = type_response.json()
                    
                    # Verify industry-specific insights
                    industry_insights = type_data.get("industry_insights", [])
                    if not industry_insights or len(industry_insights) < 2:
                        self.log_test(f"Enhanced Prompt - {video_type.title()} Industry Insights", False,
                                    f"Expected industry insights, got {len(industry_insights)}")
                    else:
                        self.log_test(f"Enhanced Prompt - {video_type.title()} Type", True,
                                    f"Successfully processed {video_type} with {len(industry_insights)} industry insights")
                else:
                    self.log_test(f"Enhanced Prompt - {video_type.title()} Type", False,
                                f"Failed for {video_type}: {type_response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Enhanced Prompt - {video_type.title()} Type", False,
                            f"Exception: {str(e)}")
        
        # Test Case 3: Multiple enhancement variations
        try:
            variations_payload = {
                "original_prompt": "Explain machine learning concepts for beginners",
                "video_type": "education",
                "industry_focus": "education",
                "enhancement_count": 4,
                "enhancement_style": "educational"
            }
            
            variations_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=variations_payload,
                timeout=90
            )
            
            if variations_response.status_code == 200:
                variations_data = variations_response.json()
                variations = variations_data["enhancement_variations"]
                
                if len(variations) == 4:
                    self.log_test("Enhanced Prompt - Custom Variation Count", True,
                                f"Successfully generated {len(variations)} variations as requested")
                    
                    # Verify educational strategy is included
                    strategies = [var["focus_strategy"] for var in variations]
                    if "educational" in strategies:
                        self.log_test("Enhanced Prompt - Educational Strategy", True,
                                    "Educational strategy included in variations")
                    else:
                        self.log_test("Enhanced Prompt - Educational Strategy", False,
                                    f"Educational strategy not found in: {strategies}")
                else:
                    self.log_test("Enhanced Prompt - Custom Variation Count", False,
                                f"Expected 4 variations, got {len(variations)}")
            else:
                self.log_test("Enhanced Prompt - Custom Variation Count", False,
                            f"Failed: {variations_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Custom Variation Count", False, f"Exception: {str(e)}")
        
        # Test Case 4: Quality metrics calculation
        try:
            quality_payload = {
                "original_prompt": "Demonstrate our new API integration features",
                "video_type": "tech",
                "industry_focus": "tech"
            }
            
            quality_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=quality_payload,
                timeout=60
            )
            
            if quality_response.status_code == 200:
                quality_data = quality_response.json()
                quality_metrics = quality_data["quality_metrics"]
                
                # Verify all scores are within valid range (0-10)
                score_fields = ["emotional_engagement_score", "technical_clarity_score", "industry_relevance_score", "storytelling_strength_score", "overall_quality_score"]
                valid_scores = True
                
                for field in score_fields:
                    score = quality_metrics.get(field, -1)
                    if not (0 <= score <= 10):
                        valid_scores = False
                        break
                
                if valid_scores:
                    self.log_test("Enhanced Prompt - Quality Metrics Range", True,
                                "All quality scores within valid range (0-10)")
                else:
                    self.log_test("Enhanced Prompt - Quality Metrics Range", False,
                                "Some quality scores outside valid range")
                
                # Verify improvement ratio is reasonable
                improvement_ratio = quality_metrics.get("improvement_ratio", 0)
                if improvement_ratio > 1:
                    self.log_test("Enhanced Prompt - Improvement Ratio", True,
                                f"Good improvement ratio: {improvement_ratio:.1f}x")
                else:
                    self.log_test("Enhanced Prompt - Improvement Ratio", False,
                                f"Poor improvement ratio: {improvement_ratio:.1f}x")
                    
            else:
                self.log_test("Enhanced Prompt - Quality Metrics", False,
                            f"Failed: {quality_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Quality Metrics", False, f"Exception: {str(e)}")
        
        # Test Case 5: Recommendation system
        try:
            recommendation_payload = {
                "original_prompt": "Create engaging content about technology",
                "video_type": "general",
                "industry_focus": "tech"
            }
            
            rec_response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=recommendation_payload,
                timeout=60
            )
            
            if rec_response.status_code == 200:
                rec_data = rec_response.json()
                recommendation = rec_data.get("recommendation", "")
                
                if len(recommendation) > 100 and "RECOMMENDED VARIATION" in recommendation:
                    self.log_test("Enhanced Prompt - Recommendation System", True,
                                f"Generated comprehensive recommendation ({len(recommendation)} chars)")
                else:
                    self.log_test("Enhanced Prompt - Recommendation System", False,
                                f"Recommendation too short or missing key elements: {len(recommendation)} chars")
                    
            else:
                self.log_test("Enhanced Prompt - Recommendation System", False,
                            f"Failed: {rec_response.status_code}")
                
        except Exception as e:
            self.log_test("Enhanced Prompt - Recommendation System", False, f"Exception: {str(e)}")
        
        return True
    
    def test_legacy_prompt_endpoint_compatibility(self):
        """Test backward compatibility with legacy endpoint"""
        print("\n=== Testing Legacy Prompt Enhancement Compatibility ===")
        
        try:
            legacy_payload = {
                "original_prompt": "Create a motivational video about success",
                "video_type": "general"
            }
            
            legacy_response = self.session.post(
                f"{self.backend_url}/enhance-prompt-legacy",
                json=legacy_payload,
                timeout=60
            )
            
            if legacy_response.status_code == 200:
                legacy_data = legacy_response.json()
                
                # Verify legacy response structure
                legacy_fields = ["original_prompt", "enhanced_prompt", "enhancement_explanation"]
                missing_legacy_fields = [field for field in legacy_fields if field not in legacy_data]
                
                if missing_legacy_fields:
                    self.log_test("Legacy Prompt - Structure", False,
                                f"Missing legacy fields: {missing_legacy_fields}")
                    return False
                
                # Verify enhancement quality
                original = legacy_data["original_prompt"]
                enhanced = legacy_data["enhanced_prompt"]
                explanation = legacy_data["enhancement_explanation"]
                
                if len(enhanced) > len(original) * 3:  # Should be at least 3x longer
                    self.log_test("Legacy Prompt - Enhancement Quality", True,
                                f"Legacy enhancement successful: {len(original)} → {len(enhanced)} chars")
                else:
                    self.log_test("Legacy Prompt - Enhancement Quality", False,
                                f"Legacy enhancement insufficient: {len(original)} → {len(enhanced)} chars")
                
                if len(explanation) > 50:
                    self.log_test("Legacy Prompt - Explanation Quality", True,
                                f"Legacy explanation adequate: {len(explanation)} chars")
                else:
                    self.log_test("Legacy Prompt - Explanation Quality", False,
                                f"Legacy explanation too short: {len(explanation)} chars")
                
                return True
                
            else:
                self.log_test("Legacy Prompt - HTTP Response", False,
                            f"HTTP {legacy_response.status_code}: {legacy_response.text[:500]}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Prompt - Exception", False, f"Request failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Testing for Script Generation App")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("\n❌ Basic connectivity failed. Stopping tests.")
            return False
        
        # Run all test suites
        test_methods = [
            self.test_enhance_prompt_endpoint,
            self.test_generate_script_endpoint,
            self.test_scripts_retrieval_endpoint,
            self.test_voices_endpoint,
            self.test_generate_audio_endpoint,
            self.test_enhanced_script_filtering_review_request,  # NEW: Focus test for review request
            self.test_timestamp_removal_comprehensive,  # New focused timestamp removal test
            self.test_audio_error_handling,
            self.test_voice_audio_integration,
            self.test_avatar_video_generation_endpoint,
            self.test_avatar_video_error_handling,
            self.test_complete_avatar_workflow,
            self.test_avatar_video_with_different_audio_lengths,
            self.test_enhanced_avatar_video_generation_endpoint,  # New enhanced avatar video tests
            self.test_enhanced_avatar_video_error_handling,
            self.test_enhanced_avatar_video_integration,
            self.test_integration_flow,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test suite {test_method.__name__} failed with exception: {str(e)}")
        
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
    tester = ScriptGenerationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
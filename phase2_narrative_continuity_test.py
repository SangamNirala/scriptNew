#!/usr/bin/env python3
"""
Phase 2 Narrative Continuity System Testing
Test the newly implemented Phase 2 Narrative Continuity System for Advanced Script Generation

This test suite validates:
1. New API Endpoint: /api/generate-script-advanced-continuity
2. Phase 2 Components: Story Arc Manager, Character Consistency Engine, Theme Continuity Tracker, Transition Generator
3. Response Structure verification
4. Context Endpoint: /api/advanced-script-continuity-context/{script_id}/segment/{segment_number}
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://2e8eb5fa-502b-46cf-a75e-9d0c7603ca91.preview.emergentagent.com/api"

class Phase2NarrativeContinuityTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.script_id = None
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_size": len(str(response_data)) if response_data else 0
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if response_data and isinstance(response_data, dict):
            print(f"    Response size: {len(str(response_data))} chars")
        print()

    def test_phase2_advanced_continuity_endpoint(self):
        """Test the main Phase 2 endpoint with medium duration (should trigger segmentation)"""
        print("🎭 Testing Phase 2 Advanced Script Generation with Narrative Continuity...")
        
        test_prompt = "Create a comprehensive video about healthy meal planning and nutrition for busy professionals. Include practical tips, meal prep strategies, and budget-friendly options."
        
        payload = {
            "prompt": test_prompt,
            "video_type": "educational",
            "duration": "extended_15"  # This should create multiple segments
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/generate-script-advanced-continuity", 
                                   json=payload, timeout=120)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.script_id = data.get('id')  # Store for context testing
                
                # Verify response structure
                required_fields = [
                    'id', 'original_prompt', 'video_type', 'duration',
                    'phase1_results', 'phase2_results', 'generation_context',
                    'ready_for_content_generation', 'phase_completed', 'next_steps'
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify Phase 1 results
                    phase1 = data.get('phase1_results', {})
                    phase1_components = ['segmentation_analysis', 'segment_plan', 'coordination_context']
                    phase1_missing = [comp for comp in phase1_components if comp not in phase1]
                    
                    # Verify Phase 2 results
                    phase2 = data.get('phase2_results', {})
                    phase2_components = ['analysis_components']
                    phase2_missing = [comp for comp in phase2_components if comp not in phase2]
                    
                    # Verify Phase 2 analysis components
                    analysis_components = phase2.get('analysis_components', {})
                    narrative_components = ['story_arc', 'character_consistency', 'theme_continuity', 'transitions']
                    narrative_missing = [comp for comp in narrative_components if comp not in analysis_components]
                    
                    if not phase1_missing and not phase2_missing and not narrative_missing:
                        # Verify specific Phase 2 component completions
                        story_arc_complete = analysis_components.get('story_arc', {}).get('narrative_analysis_complete', False)
                        character_complete = analysis_components.get('character_consistency', {}).get('character_analysis_complete', False)
                        theme_complete = analysis_components.get('theme_continuity', {}).get('theme_analysis_complete', False)
                        transitions_complete = analysis_components.get('transitions', {}).get('transition_analysis_complete', False)
                        
                        all_components_complete = all([story_arc_complete, character_complete, theme_complete, transitions_complete])
                        
                        if all_components_complete:
                            self.log_test(
                                "Phase 2 Advanced Continuity Endpoint - Complete Success",
                                True,
                                f"All Phase 2 components completed successfully. Processing time: {processing_time:.2f}s. "
                                f"Story Arc: {story_arc_complete}, Character: {character_complete}, "
                                f"Theme: {theme_complete}, Transitions: {transitions_complete}",
                                data
                            )
                        else:
                            self.log_test(
                                "Phase 2 Advanced Continuity Endpoint - Component Failure",
                                False,
                                f"Some Phase 2 components failed. Story Arc: {story_arc_complete}, "
                                f"Character: {character_complete}, Theme: {theme_complete}, Transitions: {transitions_complete}",
                                data
                            )
                    else:
                        self.log_test(
                            "Phase 2 Advanced Continuity Endpoint - Structure Missing",
                            False,
                            f"Missing components - Phase1: {phase1_missing}, Phase2: {phase2_missing}, Narrative: {narrative_missing}",
                            data
                        )
                else:
                    self.log_test(
                        "Phase 2 Advanced Continuity Endpoint - Response Structure",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
            else:
                self.log_test(
                    "Phase 2 Advanced Continuity Endpoint - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text[:500]}"
                )
                
        except requests.exceptions.Timeout:
            self.log_test(
                "Phase 2 Advanced Continuity Endpoint - Timeout",
                False,
                "Request timed out after 120 seconds"
            )
        except Exception as e:
            self.log_test(
                "Phase 2 Advanced Continuity Endpoint - Exception",
                False,
                f"Exception: {str(e)}"
            )

    def test_phase2_extended_duration(self):
        """Test with extended_20 duration to verify larger segmentation"""
        print("🎭 Testing Phase 2 with Extended Duration (extended_20)...")
        
        test_prompt = "Create a comprehensive video about healthy meal planning and nutrition for busy professionals. Include practical tips, meal prep strategies, and budget-friendly options."
        
        payload = {
            "prompt": test_prompt,
            "video_type": "educational", 
            "duration": "extended_20"  # Should create 4 segments
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/generate-script-advanced-continuity", 
                                   json=payload, timeout=120)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify segmentation for extended_20
                phase1 = data.get('phase1_results', {})
                segmentation = phase1.get('segmentation_analysis', {})
                total_segments = segmentation.get('total_segments', 1)
                
                # extended_20 (22.5 min) should create approximately 4 segments
                expected_segments = 4
                
                if total_segments == expected_segments:
                    # Verify Phase 2 components scale with segments
                    phase2 = data.get('phase2_results', {})
                    analysis_components = phase2.get('analysis_components', {})
                    
                    # Check story arc progression
                    story_arc = analysis_components.get('story_arc', {}).get('story_arc', {})
                    story_progression = story_arc.get('story_arc_progression', [])
                    
                    # Check transitions (should be 3 transitions for 4 segments)
                    transitions = analysis_components.get('transitions', {}).get('transitions', {})
                    segment_transitions = transitions.get('segment_transitions', [])
                    expected_transitions = expected_segments - 1
                    
                    if len(story_progression) == expected_segments and len(segment_transitions) == expected_transitions:
                        self.log_test(
                            "Phase 2 Extended Duration (extended_20) - Segmentation Success",
                            True,
                            f"Correct segmentation: {total_segments} segments, {len(segment_transitions)} transitions. "
                            f"Processing time: {processing_time:.2f}s",
                            data
                        )
                    else:
                        self.log_test(
                            "Phase 2 Extended Duration (extended_20) - Component Scaling",
                            False,
                            f"Component scaling issue. Story progression: {len(story_progression)}, "
                            f"Transitions: {len(segment_transitions)}, Expected: {expected_segments}/{expected_transitions}",
                            data
                        )
                else:
                    self.log_test(
                        "Phase 2 Extended Duration (extended_20) - Segmentation Count",
                        False,
                        f"Incorrect segment count: {total_segments}, expected: {expected_segments}",
                        data
                    )
            else:
                self.log_test(
                    "Phase 2 Extended Duration (extended_20) - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text[:500]}"
                )
                
        except Exception as e:
            self.log_test(
                "Phase 2 Extended Duration (extended_20) - Exception",
                False,
                f"Exception: {str(e)}"
            )

    def test_phase2_component_verification(self):
        """Test detailed verification of all Phase 2 components"""
        print("🎭 Testing Phase 2 Component Verification...")
        
        test_prompt = "Create a comprehensive video about healthy meal planning and nutrition for busy professionals. Include practical tips, meal prep strategies, and budget-friendly options."
        
        payload = {
            "prompt": test_prompt,
            "video_type": "educational",
            "duration": "extended_15"
        }
        
        try:
            response = requests.post(f"{self.backend_url}/generate-script-advanced-continuity", 
                                   json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                phase2 = data.get('phase2_results', {})
                analysis_components = phase2.get('analysis_components', {})
                
                # Test Story Arc Manager
                story_arc_data = analysis_components.get('story_arc', {})
                story_arc_complete = story_arc_data.get('narrative_analysis_complete', False)
                story_arc_content = story_arc_data.get('story_arc', {})
                
                story_arc_success = (
                    story_arc_complete and 
                    'overall_narrative_theme' in story_arc_content and
                    'story_arc_progression' in story_arc_content
                )
                
                self.log_test(
                    "Phase 2 Component - Story Arc Manager",
                    story_arc_success,
                    f"Complete: {story_arc_complete}, Theme: {'✓' if 'overall_narrative_theme' in story_arc_content else '✗'}, "
                    f"Progression: {'✓' if 'story_arc_progression' in story_arc_content else '✗'}",
                    story_arc_data
                )
                
                # Test Character Consistency Engine
                character_data = analysis_components.get('character_consistency', {})
                character_complete = character_data.get('character_analysis_complete', False)
                character_content = character_data.get('character_consistency', {})
                
                character_success = (
                    character_complete and
                    'primary_character_profile' in character_content and
                    'consistency_markers' in character_content
                )
                
                self.log_test(
                    "Phase 2 Component - Character Consistency Engine",
                    character_success,
                    f"Complete: {character_complete}, Profile: {'✓' if 'primary_character_profile' in character_content else '✗'}, "
                    f"Markers: {'✓' if 'consistency_markers' in character_content else '✗'}",
                    character_data
                )
                
                # Test Theme Continuity Tracker
                theme_data = analysis_components.get('theme_continuity', {})
                theme_complete = theme_data.get('theme_analysis_complete', False)
                theme_content = theme_data.get('theme_continuity', {})
                
                theme_success = (
                    theme_complete and
                    'core_theme_structure' in theme_content and
                    'segment_theme_mapping' in theme_content
                )
                
                self.log_test(
                    "Phase 2 Component - Theme Continuity Tracker",
                    theme_success,
                    f"Complete: {theme_complete}, Structure: {'✓' if 'core_theme_structure' in theme_content else '✗'}, "
                    f"Mapping: {'✓' if 'segment_theme_mapping' in theme_content else '✗'}",
                    theme_data
                )
                
                # Test Transition Generator
                transition_data = analysis_components.get('transitions', {})
                transition_complete = transition_data.get('transition_analysis_complete', False)
                transition_content = transition_data.get('transitions', {})
                
                transition_success = (
                    transition_complete and
                    'segment_transitions' in transition_content and
                    'transition_strategy' in transition_content
                )
                
                self.log_test(
                    "Phase 2 Component - Transition Generator",
                    transition_success,
                    f"Complete: {transition_complete}, Transitions: {'✓' if 'segment_transitions' in transition_content else '✗'}, "
                    f"Strategy: {'✓' if 'transition_strategy' in transition_content else '✗'}",
                    transition_data
                )
                
            else:
                self.log_test(
                    "Phase 2 Component Verification - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text[:500]}"
                )
                
        except Exception as e:
            self.log_test(
                "Phase 2 Component Verification - Exception",
                False,
                f"Exception: {str(e)}"
            )

    def test_context_endpoint(self):
        """Test the context endpoint for segment-specific narrative context"""
        print("🎭 Testing Phase 2 Context Endpoint...")
        
        if not self.script_id:
            # Generate a script first
            test_prompt = "Create a comprehensive video about healthy meal planning and nutrition for busy professionals. Include practical tips, meal prep strategies, and budget-friendly options."
            
            payload = {
                "prompt": test_prompt,
                "video_type": "educational",
                "duration": "extended_15"
            }
            
            try:
                response = requests.post(f"{self.backend_url}/generate-script-advanced-continuity", 
                                       json=payload, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    self.script_id = data.get('id')
                else:
                    self.log_test(
                        "Phase 2 Context Endpoint - Script Generation Failed",
                        False,
                        f"Could not generate script for context testing: HTTP {response.status_code}"
                    )
                    return
            except Exception as e:
                self.log_test(
                    "Phase 2 Context Endpoint - Script Generation Exception",
                    False,
                    f"Exception generating script: {str(e)}"
                )
                return
        
        # Test context retrieval for different segments
        segments_to_test = [1, 2, 3]
        
        for segment_num in segments_to_test:
            try:
                response = requests.get(
                    f"{self.backend_url}/advanced-script-continuity-context/{self.script_id}/segment/{segment_num}",
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify context structure
                    required_fields = [
                        'status', 'script_id', 'segment_context', 'original_script_data',
                        'phase1_ready', 'phase2_ready', 'ready_for_content_generation',
                        'narrative_continuity_ready'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Verify segment context contains narrative information
                        segment_context = data.get('segment_context', {})
                        narrative_context = segment_context.get('narrative_context', {})
                        
                        narrative_elements = [
                            'story_arc_context', 'character_context', 'theme_context', 'transitions'
                        ]
                        
                        narrative_present = [elem for elem in narrative_elements if elem in narrative_context]
                        
                        success = len(narrative_present) >= 3  # At least 3 of 4 narrative elements
                        
                        self.log_test(
                            f"Phase 2 Context Endpoint - Segment {segment_num}",
                            success,
                            f"Narrative elements present: {len(narrative_present)}/4 ({', '.join(narrative_present)}). "
                            f"Phase1 ready: {data.get('phase1_ready')}, Phase2 ready: {data.get('phase2_ready')}",
                            data
                        )
                    else:
                        self.log_test(
                            f"Phase 2 Context Endpoint - Segment {segment_num} Structure",
                            False,
                            f"Missing required fields: {missing_fields}",
                            data
                        )
                elif response.status_code == 404:
                    self.log_test(
                        f"Phase 2 Context Endpoint - Segment {segment_num} Not Found",
                        False,
                        f"Script ID {self.script_id} not found in database"
                    )
                else:
                    self.log_test(
                        f"Phase 2 Context Endpoint - Segment {segment_num} HTTP Error",
                        False,
                        f"HTTP {response.status_code}: {response.text[:500]}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Phase 2 Context Endpoint - Segment {segment_num} Exception",
                    False,
                    f"Exception: {str(e)}"
                )

    def test_database_storage(self):
        """Test that Phase 2 results are properly stored in database"""
        print("🎭 Testing Phase 2 Database Storage...")
        
        test_prompt = "Create a comprehensive video about healthy meal planning and nutrition for busy professionals. Include practical tips, meal prep strategies, and budget-friendly options."
        
        payload = {
            "prompt": test_prompt,
            "video_type": "educational",
            "duration": "extended_15"
        }
        
        try:
            response = requests.post(f"{self.backend_url}/generate-script-advanced-continuity", 
                                   json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                script_id = data.get('id')
                
                # Test that we can retrieve the stored data via context endpoint
                context_response = requests.get(
                    f"{self.backend_url}/advanced-script-continuity-context/{script_id}/segment/1",
                    timeout=30
                )
                
                if context_response.status_code == 200:
                    context_data = context_response.json()
                    
                    # Verify that the stored data contains Phase 2 information
                    original_script_data = context_data.get('original_script_data', {})
                    segment_context = context_data.get('segment_context', {})
                    
                    storage_success = (
                        'prompt' in original_script_data and
                        'video_type' in original_script_data and
                        'duration' in original_script_data and
                        'narrative_context' in segment_context
                    )
                    
                    self.log_test(
                        "Phase 2 Database Storage - Verification",
                        storage_success,
                        f"Script stored with ID: {script_id}. "
                        f"Original data: {'✓' if 'prompt' in original_script_data else '✗'}, "
                        f"Narrative context: {'✓' if 'narrative_context' in segment_context else '✗'}",
                        context_data
                    )
                else:
                    self.log_test(
                        "Phase 2 Database Storage - Retrieval Failed",
                        False,
                        f"Could not retrieve stored data: HTTP {context_response.status_code}"
                    )
            else:
                self.log_test(
                    "Phase 2 Database Storage - Generation Failed",
                    False,
                    f"Could not generate script for storage testing: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Phase 2 Database Storage - Exception",
                False,
                f"Exception: {str(e)}"
            )

    def test_generation_context_structure(self):
        """Test the generation_context structure for Phase 2"""
        print("🎭 Testing Phase 2 Generation Context Structure...")
        
        test_prompt = "Create a comprehensive video about healthy meal planning and nutrition for busy professionals. Include practical tips, meal prep strategies, and budget-friendly options."
        
        payload = {
            "prompt": test_prompt,
            "video_type": "educational",
            "duration": "extended_15"
        }
        
        try:
            response = requests.post(f"{self.backend_url}/generate-script-advanced-continuity", 
                                   json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                generation_context = data.get('generation_context', {})
                
                # Verify generation context contains both Phase 1 and Phase 2 elements
                phase1_elements = [
                    'segmentation_analysis', 'segment_plan', 'coordination_context'
                ]
                
                phase2_elements = [
                    'narrative_continuity', 'phase2_complete'
                ]
                
                phase1_present = [elem for elem in phase1_elements if elem in generation_context]
                phase2_present = [elem for elem in phase2_elements if elem in generation_context]
                
                # Verify narrative continuity structure
                narrative_continuity = generation_context.get('narrative_continuity', {})
                narrative_components = narrative_continuity.get('analysis_components', {})
                
                expected_components = ['story_arc', 'character_consistency', 'theme_continuity', 'transitions']
                components_present = [comp for comp in expected_components if comp in narrative_components]
                
                success = (
                    len(phase1_present) == len(phase1_elements) and
                    len(phase2_present) == len(phase2_elements) and
                    len(components_present) == len(expected_components) and
                    generation_context.get('phase2_complete', False)
                )
                
                self.log_test(
                    "Phase 2 Generation Context Structure",
                    success,
                    f"Phase1 elements: {len(phase1_present)}/{len(phase1_elements)}, "
                    f"Phase2 elements: {len(phase2_present)}/{len(phase2_elements)}, "
                    f"Narrative components: {len(components_present)}/{len(expected_components)}, "
                    f"Phase2 complete: {generation_context.get('phase2_complete', False)}",
                    generation_context
                )
            else:
                self.log_test(
                    "Phase 2 Generation Context Structure - HTTP Error",
                    False,
                    f"HTTP {response.status_code}: {response.text[:500]}"
                )
                
        except Exception as e:
            self.log_test(
                "Phase 2 Generation Context Structure - Exception",
                False,
                f"Exception: {str(e)}"
            )

    def run_all_tests(self):
        """Run all Phase 2 Narrative Continuity tests"""
        print("🎭 Starting Phase 2 Narrative Continuity System Testing")
        print("=" * 80)
        
        # Test main endpoint
        self.test_phase2_advanced_continuity_endpoint()
        
        # Test extended duration
        self.test_phase2_extended_duration()
        
        # Test component verification
        self.test_phase2_component_verification()
        
        # Test context endpoint
        self.test_context_endpoint()
        
        # Test database storage
        self.test_database_storage()
        
        # Test generation context structure
        self.test_generation_context_structure()
        
        # Print summary and return results
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("🎭 Phase 2 Narrative Continuity System Test Summary")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        print("✅ Passed Tests:")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}")
        
        print()
        print("🎭 Phase 2 Narrative Continuity System Testing Complete!")
        
        # Return success status
        return passed_tests, failed_tests, total_tests

if __name__ == "__main__":
    tester = Phase2NarrativeContinuityTester()
    passed, failed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)
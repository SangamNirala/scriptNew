"""
Narrative Continuity System - Phase 2: Advanced Script Generation Logic

This module implements the comprehensive narrative continuity management for segmented
script generation. It ensures consistent storytelling, character development, and 
thematic coherence across multiple script segments.

Components:
- Story Arc Manager: Tracks narrative progression across segments
- Character Consistency Engine: Maintains character development flow
- Theme Continuity Tracker: Keeps core messaging consistent
- Transition Generator: Creates smooth bridges between segments
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

logger = logging.getLogger(__name__)

class StoryArcManager:
    """
    Manages the overall narrative arc progression across multiple segments.
    Ensures each segment contributes meaningfully to the complete story structure.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.story_structure_templates = {
            "educational": ["hook", "problem_introduction", "core_concepts", "practical_application", "conclusion"],
            "marketing": ["attention", "interest", "desire", "social_proof", "action"],
            "entertainment": ["setup", "inciting_incident", "rising_action", "climax", "resolution"],
            "general": ["introduction", "context_building", "main_content", "insights", "conclusion"]
        }
    
    async def analyze_narrative_arc(self, 
                                  original_prompt: str, 
                                  video_type: str,
                                  total_segments: int,
                                  segment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and create the overall narrative arc structure for segmented content
        
        Args:
            original_prompt: Original user prompt
            video_type: Type of video content
            total_segments: Total number of segments planned
            segment_plan: Segment plan from Phase 1
            
        Returns:
            Comprehensive narrative arc analysis and structure
        """
        try:
            logger.info(f"🎭 Analyzing narrative arc for {total_segments} segments, type: {video_type}")
            
            # Create arc analysis chat instance
            arc_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"story-arc-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Narrative Architect specializing in multi-segment storytelling for video content. Your expertise lies in creating compelling story arcs that maintain engagement and coherence across multiple segments.

CORE EXPERTISE:
1. NARRATIVE STRUCTURE DESIGN: Creating compelling story arcs across segments
2. DRAMATIC TENSION MANAGEMENT: Building and maintaining tension throughout segments
3. EMOTIONAL JOURNEY MAPPING: Planning emotional peaks and valleys across content
4. THEMATIC INTEGRATION: Weaving central themes throughout all segments
5. AUDIENCE ENGAGEMENT ARCHITECTURE: Strategic placement of engagement elements

You excel at transforming linear content into dynamic, segmented narratives that feel cohesive and compelling."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Get template structure for video type
            template_structure = self.story_structure_templates.get(video_type, self.story_structure_templates["general"])
            
            arc_prompt = f"""Create a comprehensive narrative arc analysis for this segmented video content:

CONTENT DETAILS:
- Original Prompt: "{original_prompt}"
- Video Type: {video_type}
- Total Segments: {total_segments}
- Segment Duration: {segment_plan.get('segmentation_details', {}).get('segment_duration_minutes', 'N/A')} minutes each

SEGMENT STRUCTURE FROM PHASE 1:
{self._format_segment_outlines(segment_plan.get('segment_plan', {}).get('segment_outlines', []))}

Create a detailed narrative arc analysis following this EXACT format:

OVERALL_NARRATIVE_THEME:
[Define the central theme that will unify all segments]

STORY_ARC_PROGRESSION:
SEGMENT_1:
- ARC_POSITION: [Where this fits in overall story - opening, development, etc.]
- NARRATIVE_PURPOSE: [What this segment accomplishes for the story]
- EMOTIONAL_TARGET: [What emotion/feeling this segment should evoke]
- TENSION_LEVEL: [Low/Medium/High - building dramatic tension]
- KEY_STORY_ELEMENTS: [Main story components to include]
- SETUP_FOR_NEXT: [How this segment prepares for the next one]

[Continue for all {total_segments} segments...]

CHARACTER_ARC_OUTLINE:
- MAIN_PERSONA: [Primary character/narrator personality]
- DEVELOPMENT_STAGES: [How the character/presenter evolves across segments]
- CONSISTENCY_MARKERS: [Key traits to maintain throughout]

THEMATIC_THREADS:
- PRIMARY_THEME: [Main message/theme]
- SUPPORTING_THEMES: [Secondary themes that reinforce the primary]
- THEME_EVOLUTION: [How themes develop across segments]

ENGAGEMENT_STRATEGY:
- HOOK_DISTRIBUTION: [How to distribute engagement hooks across segments]
- CURIOSITY_GAPS: [Strategic information gaps to maintain interest]
- REVELATION_SEQUENCE: [Order of key revelations/insights]

QUALITY_BENCHMARKS:
[Standards for maintaining narrative quality across all segments]"""

            response = await arc_chat.send_message(UserMessage(text=arc_prompt))
            
            # Parse the narrative arc response
            parsed_arc = self._parse_narrative_arc(response, total_segments, video_type)
            
            return {
                "narrative_analysis_complete": True,
                "original_prompt": original_prompt,
                "video_type": video_type,
                "total_segments": total_segments,
                "story_arc": parsed_arc,
                "template_structure": template_structure,
                "arc_creation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in narrative arc analysis: {str(e)}")
            return {"error": str(e), "narrative_analysis_complete": False}
    
    def _format_segment_outlines(self, segment_outlines: List[Dict[str, Any]]) -> str:
        """Format segment outlines for prompt inclusion"""
        formatted = []
        for segment in segment_outlines:
            segment_num = segment.get('segment_number', 1)
            details = segment.get('details', {})
            formatted.append(f"Segment {segment_num}: {details.get('content_focus', 'Main content')} - {details.get('narrative_role', 'development')}")
        return "\n".join(formatted) if formatted else "No segment outlines available"
    
    def _parse_narrative_arc(self, arc_text: str, total_segments: int, video_type: str) -> Dict[str, Any]:
        """Parse the AI-generated narrative arc into structured format"""
        try:
            parsed_arc = {
                "overall_narrative_theme": "",
                "story_arc_progression": [],
                "character_arc_outline": {},
                "thematic_threads": {},
                "engagement_strategy": {},
                "quality_benchmarks": []
            }
            
            lines = arc_text.split('\n')
            current_section = None
            current_segment = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('OVERALL_NARRATIVE_THEME:'):
                    current_section = 'overall_narrative_theme'
                    parsed_arc['overall_narrative_theme'] = line.replace('OVERALL_NARRATIVE_THEME:', '').strip()
                elif line.startswith('STORY_ARC_PROGRESSION:'):
                    current_section = 'story_arc_progression'
                elif line.startswith('CHARACTER_ARC_OUTLINE:'):
                    current_section = 'character_arc_outline'
                elif line.startswith('THEMATIC_THREADS:'):
                    current_section = 'thematic_threads'
                elif line.startswith('ENGAGEMENT_STRATEGY:'):
                    current_section = 'engagement_strategy'
                elif line.startswith('QUALITY_BENCHMARKS:'):
                    current_section = 'quality_benchmarks'
                elif line.startswith('SEGMENT_'):
                    # New segment in story arc progression
                    if current_section == 'story_arc_progression':
                        current_segment = {
                            "segment_number": len(parsed_arc['story_arc_progression']) + 1,
                            "details": {}
                        }
                        parsed_arc['story_arc_progression'].append(current_segment)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'story_arc_progression' and current_segment:
                        self._parse_arc_segment_detail(line, current_segment)
                    elif current_section in ['character_arc_outline', 'thematic_threads', 'engagement_strategy']:
                        self._parse_section_detail(line, parsed_arc[current_section])
                    elif current_section == 'quality_benchmarks':
                        parsed_arc['quality_benchmarks'].append(line[1:].strip())
                elif current_section == 'overall_narrative_theme' and not line.startswith(('STORY_', 'CHARACTER_', 'THEMATIC_', 'ENGAGEMENT_', 'QUALITY_')):
                    parsed_arc['overall_narrative_theme'] += ' ' + line
            
            # Ensure we have segments even if parsing fails
            if not parsed_arc['story_arc_progression']:
                parsed_arc['story_arc_progression'] = [
                    {"segment_number": i+1, "details": {}} for i in range(total_segments)
                ]
            
            return parsed_arc
            
        except Exception as e:
            logger.error(f"Error parsing narrative arc: {str(e)}")
            return {
                "overall_narrative_theme": "Comprehensive exploration of the topic with engaging narrative flow",
                "story_arc_progression": [{"segment_number": i+1, "details": {}} for i in range(total_segments)],
                "character_arc_outline": {},
                "thematic_threads": {},
                "engagement_strategy": {},
                "quality_benchmarks": [],
                "parse_error": str(e)
            }
    
    def _parse_arc_segment_detail(self, line: str, segment: Dict[str, Any]):
        """Parse individual segment detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                segment['details'][key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass
    
    def _parse_section_detail(self, line: str, section_dict: Dict[str, Any]):
        """Parse section detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                section_dict[key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass


class CharacterConsistencyEngine:
    """
    Maintains character development and personality consistency across all segments.
    Ensures characters are introduced properly and developed naturally.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def analyze_character_consistency(self,
                                          narrative_arc: Dict[str, Any],
                                          original_prompt: str,
                                          video_type: str) -> Dict[str, Any]:
        """
        Analyze and create character consistency guidelines for segmented content
        
        Args:
            narrative_arc: Output from StoryArcManager
            original_prompt: Original user prompt
            video_type: Type of video content
            
        Returns:
            Character consistency analysis and guidelines
        """
        try:
            logger.info(f"👤 Analyzing character consistency for {video_type} content")
            
            # Create character analysis chat instance
            character_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"character-consistency-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Character Development Specialist for video content. Your expertise lies in creating and maintaining consistent character personas, narratives, and development arcs across multi-segment video content.

CORE EXPERTISE:
1. CHARACTER PERSONA DESIGN: Creating compelling, consistent character personalities
2. VOICE CONSISTENCY: Maintaining uniform tone, language patterns, and speaking style
3. CHARACTER ARC DEVELOPMENT: Planning character growth and evolution across segments
4. PERSONA AUTHENTICITY: Ensuring characters remain believable and relatable
5. NARRATIVE VOICE MANAGEMENT: Consistent narrator/presenter personality throughout

You excel at creating character guidelines that maintain authenticity while allowing for natural development across segments."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Extract character information from narrative arc
            character_arc = narrative_arc.get('story_arc', {}).get('character_arc_outline', {})
            overall_theme = narrative_arc.get('story_arc', {}).get('overall_narrative_theme', '')
            
            character_prompt = f"""Create comprehensive character consistency guidelines for this segmented video content:

CONTENT CONTEXT:
- Original Prompt: "{original_prompt}"
- Video Type: {video_type}
- Overall Theme: {overall_theme}
- Total Segments: {narrative_arc.get('total_segments', 1)}

EXISTING CHARACTER ANALYSIS:
{self._format_character_arc(character_arc)}

Create detailed character consistency guidelines following this EXACT format:

PRIMARY_CHARACTER_PROFILE:
- CHARACTER_TYPE: [Narrator/Presenter/Host personality type]
- CORE_PERSONALITY_TRAITS: [3-5 key personality characteristics]
- SPEAKING_STYLE: [How they communicate - formal, casual, energetic, etc.]
- EXPERTISE_LEVEL: [Beginner-friendly, intermediate, expert, etc.]
- EMOTIONAL_RANGE: [What emotions they express and how]
- VISUAL_PRESENCE: [How they should appear/be described visually]

CONSISTENCY_MARKERS:
- LANGUAGE_PATTERNS: [Specific words, phrases, or expressions they use]
- TRANSITION_PHRASES: [Signature phrases for connecting ideas]
- ENGAGEMENT_STYLE: [How they interact with audience - questions, commands, etc.]
- STORYTELLING_APPROACH: [Their unique way of presenting information]

SEGMENT_CHARACTER_EVOLUTION:
SEGMENT_1:
- CHARACTER_INTRODUCTION: [How character is introduced/established]
- PERSONALITY_FOCUS: [Which traits are most prominent]
- RELATIONSHIP_WITH_AUDIENCE: [How they connect with viewers]

[Continue for each segment...]

VOICE_CONSISTENCY_GUIDELINES:
- TONE_STANDARDS: [Consistent tone throughout all segments]
- ENERGY_LEVELS: [How energy varies but remains consistent to character]
- AUTHENTICITY_MARKERS: [What makes this character feel genuine]
- CONSISTENCY_CHECKPOINTS: [Key elements to verify in each segment]

DEVELOPMENT_TRAJECTORY:
[How the character grows/evolves across segments while maintaining core consistency]"""

            response = await character_chat.send_message(UserMessage(text=character_prompt))
            
            # Parse the character consistency response
            parsed_character = self._parse_character_consistency(response)
            
            return {
                "character_analysis_complete": True,
                "original_prompt": original_prompt,
                "video_type": video_type,
                "character_consistency": parsed_character,
                "character_creation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in character consistency analysis: {str(e)}")
            return {"error": str(e), "character_analysis_complete": False}
    
    def _format_character_arc(self, character_arc: Dict[str, Any]) -> str:
        """Format character arc information for prompt inclusion"""
        if not character_arc:
            return "No existing character analysis available"
        
        formatted_parts = []
        for key, value in character_arc.items():
            formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No character analysis available"
    
    def _parse_character_consistency(self, character_text: str) -> Dict[str, Any]:
        """Parse the AI-generated character consistency analysis"""
        try:
            parsed = {
                "primary_character_profile": {},
                "consistency_markers": {},
                "segment_character_evolution": [],
                "voice_consistency_guidelines": {},
                "development_trajectory": ""
            }
            
            lines = character_text.split('\n')
            current_section = None
            current_segment = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('PRIMARY_CHARACTER_PROFILE:'):
                    current_section = 'primary_character_profile'
                elif line.startswith('CONSISTENCY_MARKERS:'):
                    current_section = 'consistency_markers'
                elif line.startswith('SEGMENT_CHARACTER_EVOLUTION:'):
                    current_section = 'segment_character_evolution'
                elif line.startswith('VOICE_CONSISTENCY_GUIDELINES:'):
                    current_section = 'voice_consistency_guidelines'
                elif line.startswith('DEVELOPMENT_TRAJECTORY:'):
                    current_section = 'development_trajectory'
                    parsed['development_trajectory'] = line.replace('DEVELOPMENT_TRAJECTORY:', '').strip()
                elif line.startswith('SEGMENT_'):
                    # New segment in character evolution
                    if current_section == 'segment_character_evolution':
                        current_segment = {
                            "segment_number": len(parsed['segment_character_evolution']) + 1,
                            "details": {}
                        }
                        parsed['segment_character_evolution'].append(current_segment)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'segment_character_evolution' and current_segment:
                        self._parse_character_detail(line, current_segment)
                    elif current_section in ['primary_character_profile', 'consistency_markers', 'voice_consistency_guidelines']:
                        self._parse_section_detail(line, parsed[current_section])
                elif current_section == 'development_trajectory' and not line.startswith(('PRIMARY_', 'CONSISTENCY_', 'SEGMENT_', 'VOICE_')):
                    parsed['development_trajectory'] += ' ' + line
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing character consistency: {str(e)}")
            return {
                "primary_character_profile": {"character_type": "Professional presenter"},
                "consistency_markers": {"language_patterns": "Clear and engaging communication"},
                "segment_character_evolution": [],
                "voice_consistency_guidelines": {"tone_standards": "Professional and engaging"},
                "development_trajectory": "Consistent character development throughout content",
                "parse_error": str(e)
            }
    
    def _parse_character_detail(self, line: str, segment: Dict[str, Any]):
        """Parse individual character detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                segment['details'][key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass
    
    def _parse_section_detail(self, line: str, section_dict: Dict[str, Any]):
        """Parse section detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                section_dict[key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass


class ThemeContinuityTracker:
    """
    Maintains thematic consistency and core messaging across all segments.
    Ensures the central theme is reinforced throughout without repetition.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def analyze_theme_continuity(self,
                                     narrative_arc: Dict[str, Any],
                                     character_consistency: Dict[str, Any],
                                     original_prompt: str) -> Dict[str, Any]:
        """
        Analyze and create theme continuity guidelines for consistent messaging
        
        Args:
            narrative_arc: Output from StoryArcManager
            character_consistency: Output from CharacterConsistencyEngine
            original_prompt: Original user prompt
            
        Returns:
            Theme continuity analysis and guidelines
        """
        try:
            logger.info(f"🎯 Analyzing theme continuity across {narrative_arc.get('total_segments', 1)} segments")
            
            # Create theme analysis chat instance
            theme_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"theme-continuity-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Theme Strategist and Content Continuity Expert. Your expertise lies in maintaining consistent messaging, themes, and core values across multi-segment video content while avoiding redundancy.

CORE EXPERTISE:
1. THEMATIC ARCHITECTURE: Designing comprehensive theme structures across segments
2. MESSAGE CONSISTENCY: Ensuring core messages remain clear and unified
3. VARIATION WITHOUT REPETITION: Expressing themes in fresh ways across segments
4. SUBLIMINAL MESSAGING: Weaving themes naturally into content without being obvious
5. THEME REINFORCEMENT: Strategic placement of theme reinforcement throughout content

You excel at creating theme guidelines that maintain message consistency while keeping content fresh and engaging."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Extract thematic information
            thematic_threads = narrative_arc.get('story_arc', {}).get('thematic_threads', {})
            overall_theme = narrative_arc.get('story_arc', {}).get('overall_narrative_theme', '')
            character_traits = character_consistency.get('character_consistency', {}).get('primary_character_profile', {})
            
            theme_prompt = f"""Create comprehensive theme continuity guidelines for this segmented video content:

CONTENT FOUNDATION:
- Original Prompt: "{original_prompt}"
- Overall Narrative Theme: {overall_theme}
- Total Segments: {narrative_arc.get('total_segments', 1)}
- Video Type: {narrative_arc.get('video_type', 'general')}

EXISTING THEMATIC ANALYSIS:
{self._format_thematic_threads(thematic_threads)}

CHARACTER CONTEXT:
{self._format_character_traits(character_traits)}

Create detailed theme continuity guidelines following this EXACT format:

CORE_THEME_STRUCTURE:
- PRIMARY_THEME: [Main overarching theme/message]
- THEME_ESSENCE: [Core meaning in one sentence]
- KEY_VALUES: [3-4 fundamental values that support the theme]
- AUDIENCE_BENEFIT: [What the audience gains from this theme]

THEME_VARIATION_STRATEGY:
- SEGMENT_THEME_ANGLES: [How to approach the same theme differently in each segment]
- EXPRESSION_METHODS: [Different ways to express the theme - stories, data, examples, etc.]
- REINFORCEMENT_TECHNIQUES: [Subtle ways to reinforce without repetition]

SEGMENT_THEME_MAPPING:
SEGMENT_1:
- THEME_FOCUS: [Which aspect of the core theme this segment emphasizes]
- MESSAGE_ANGLE: [Unique angle/perspective for this segment]
- SUPPORTING_ELEMENTS: [How other elements support the theme]
- THEME_INTEGRATION: [How theme is woven into content naturally]

[Continue for all {narrative_arc.get('total_segments', 1)} segments...]

CONSISTENCY_FRAMEWORK:
- CORE_MESSAGE_PILLARS: [Key messages that must appear in every segment]
- VARIATION_GUIDELINES: [How to vary expression while maintaining consistency]
- SUBLIMINAL_INTEGRATION: [Ways to integrate themes without being preachy]
- AUTHENTICITY_MARKERS: [What ensures themes feel genuine to content]

CONTINUITY_CHECKPOINTS:
[Key elements to verify in each segment for theme consistency]"""

            response = await theme_chat.send_message(UserMessage(text=theme_prompt))
            
            # Parse the theme continuity response
            parsed_theme = self._parse_theme_continuity(response, narrative_arc.get('total_segments', 1))
            
            return {
                "theme_analysis_complete": True,
                "original_prompt": original_prompt,
                "total_segments": narrative_arc.get('total_segments', 1),
                "theme_continuity": parsed_theme,
                "theme_creation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in theme continuity analysis: {str(e)}")
            return {"error": str(e), "theme_analysis_complete": False}
    
    def _format_thematic_threads(self, thematic_threads: Dict[str, Any]) -> str:
        """Format thematic threads for prompt inclusion"""
        if not thematic_threads:
            return "No existing thematic analysis available"
        
        formatted_parts = []
        for key, value in thematic_threads.items():
            formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No thematic analysis available"
    
    def _format_character_traits(self, character_traits: Dict[str, Any]) -> str:
        """Format character traits for prompt inclusion"""
        if not character_traits:
            return "No character context available"
        
        formatted_parts = []
        for key, value in character_traits.items():
            formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No character context available"
    
    def _parse_theme_continuity(self, theme_text: str, total_segments: int) -> Dict[str, Any]:
        """Parse the AI-generated theme continuity analysis"""
        try:
            parsed = {
                "core_theme_structure": {},
                "theme_variation_strategy": {},
                "segment_theme_mapping": [],
                "consistency_framework": {},
                "continuity_checkpoints": []
            }
            
            lines = theme_text.split('\n')
            current_section = None
            current_segment = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('CORE_THEME_STRUCTURE:'):
                    current_section = 'core_theme_structure'
                elif line.startswith('THEME_VARIATION_STRATEGY:'):
                    current_section = 'theme_variation_strategy'
                elif line.startswith('SEGMENT_THEME_MAPPING:'):
                    current_section = 'segment_theme_mapping'
                elif line.startswith('CONSISTENCY_FRAMEWORK:'):
                    current_section = 'consistency_framework'
                elif line.startswith('CONTINUITY_CHECKPOINTS:'):
                    current_section = 'continuity_checkpoints'
                elif line.startswith('SEGMENT_'):
                    # New segment in theme mapping
                    if current_section == 'segment_theme_mapping':
                        current_segment = {
                            "segment_number": len(parsed['segment_theme_mapping']) + 1,
                            "details": {}
                        }
                        parsed['segment_theme_mapping'].append(current_segment)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'segment_theme_mapping' and current_segment:
                        self._parse_theme_detail(line, current_segment)
                    elif current_section in ['core_theme_structure', 'theme_variation_strategy', 'consistency_framework']:
                        self._parse_section_detail(line, parsed[current_section])
                    elif current_section == 'continuity_checkpoints':
                        parsed['continuity_checkpoints'].append(line[1:].strip())
            
            # Ensure we have segments even if parsing fails
            if not parsed['segment_theme_mapping']:
                parsed['segment_theme_mapping'] = [
                    {"segment_number": i+1, "details": {}} for i in range(total_segments)
                ]
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing theme continuity: {str(e)}")
            return {
                "core_theme_structure": {"primary_theme": "Comprehensive content delivery with engaging presentation"},
                "theme_variation_strategy": {"expression_methods": "Multiple approaches to maintain engagement"},
                "segment_theme_mapping": [{"segment_number": i+1, "details": {}} for i in range(total_segments)],
                "consistency_framework": {"core_message_pillars": "Consistent key messaging throughout"},
                "continuity_checkpoints": [],
                "parse_error": str(e)
            }
    
    def _parse_theme_detail(self, line: str, segment: Dict[str, Any]):
        """Parse individual theme detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                segment['details'][key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass
    
    def _parse_section_detail(self, line: str, section_dict: Dict[str, Any]):
        """Parse section detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                section_dict[key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass


class TransitionGenerator:
    """
    Creates smooth, natural transitions between segments that maintain narrative flow.
    Ensures each segment connects seamlessly to the next without abrupt breaks.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def generate_transitions(self,
                                 narrative_arc: Dict[str, Any],
                                 character_consistency: Dict[str, Any],
                                 theme_continuity: Dict[str, Any],
                                 total_segments: int) -> Dict[str, Any]:
        """
        Generate smooth transitions between all segments
        
        Args:
            narrative_arc: Output from StoryArcManager
            character_consistency: Output from CharacterConsistencyEngine
            theme_continuity: Output from ThemeContinuityTracker
            total_segments: Total number of segments
            
        Returns:
            Complete transition analysis and content for all segment boundaries
        """
        try:
            logger.info(f"🔗 Generating transitions for {total_segments} segments")
            
            # Create transition generation chat instance
            transition_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"transition-generator-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Transition Architect specializing in seamless content flow for video segments. Your expertise lies in creating natural, engaging bridges between content segments that maintain narrative momentum and audience engagement.

CORE EXPERTISE:
1. FLOW ARCHITECTURE: Creating seamless transitions that feel natural and unforced
2. MOMENTUM MANAGEMENT: Maintaining energy and interest across segment boundaries
3. NARRATIVE BRIDGING: Connecting story elements across segments smoothly
4. CURIOSITY ENGINEERING: Using transitions to build anticipation for next segments
5. THEMATIC WEAVING: Incorporating theme elements into transitions naturally

You excel at creating transitions that enhance rather than interrupt the viewing experience."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Extract relevant information for context
            story_progression = narrative_arc.get('story_arc', {}).get('story_arc_progression', [])
            character_traits = character_consistency.get('character_consistency', {}).get('primary_character_profile', {})
            theme_structure = theme_continuity.get('theme_continuity', {}).get('core_theme_structure', {})
            
            transition_prompt = f"""Create comprehensive transitions for this {total_segments}-segment video content:

NARRATIVE CONTEXT:
Total Segments: {total_segments}
Overall Theme: {theme_structure.get('primary_theme', 'Engaging content delivery')}
Character Style: {character_traits.get('speaking_style', 'Professional and engaging')}

STORY PROGRESSION:
{self._format_story_progression(story_progression)}

CHARACTER CONSISTENCY:
Language Patterns: {character_consistency.get('character_consistency', {}).get('consistency_markers', {}).get('language_patterns', 'Clear communication')}
Transition Phrases: {character_consistency.get('character_consistency', {}).get('consistency_markers', {}).get('transition_phrases', 'Natural connecting phrases')}

Create detailed transitions following this EXACT format:

TRANSITION_STRATEGY:
- OVERALL_APPROACH: [General strategy for all transitions]
- FLOW_METHODOLOGY: [How transitions maintain content flow]
- ENGAGEMENT_MAINTENANCE: [How transitions keep audience engaged]

SEGMENT_TRANSITIONS:
TRANSITION_1_TO_2:
- ENDING_BRIDGE: [How segment 1 should end to setup transition]
- TRANSITION_CONTENT: [Actual transition text/dialogue]
- OPENING_HOOK: [How segment 2 should begin after transition]
- NARRATIVE_CONNECTION: [How this connects the story elements]
- THEME_REINFORCEMENT: [How transition reinforces overall theme]

TRANSITION_2_TO_3:
[Continue for all transitions between segments...]

[Generate transitions for all {total_segments-1} segment boundaries]

TRANSITION_QUALITY_STANDARDS:
- NATURALNESS_CRITERIA: [What makes transitions feel natural]
- MOMENTUM_MAINTENANCE: [How to keep energy flowing]
- COHERENCE_MARKERS: [Elements that ensure logical flow]
- ENGAGEMENT_ELEMENTS: [What keeps audience interested during transitions]

TRANSITION_TEMPLATES:
[Reusable transition patterns that maintain consistency]"""

            response = await transition_chat.send_message(UserMessage(text=transition_prompt))
            
            # Parse the transition response
            parsed_transitions = self._parse_transitions(response, total_segments)
            
            return {
                "transition_analysis_complete": True,
                "total_segments": total_segments,
                "total_transitions": total_segments - 1,
                "transitions": parsed_transitions,
                "transition_creation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating transitions: {str(e)}")
            return {"error": str(e), "transition_analysis_complete": False}
    
    def _format_story_progression(self, story_progression: List[Dict[str, Any]]) -> str:
        """Format story progression for prompt inclusion"""
        if not story_progression:
            return "No story progression data available"
        
        formatted = []
        for segment in story_progression:
            seg_num = segment.get('segment_number', 1)
            details = segment.get('details', {})
            arc_position = details.get('arc_position', 'development')
            narrative_purpose = details.get('narrative_purpose', 'content delivery')
            formatted.append(f"Segment {seg_num}: {arc_position} - {narrative_purpose}")
        
        return "\n".join(formatted) if formatted else "No progression details available"
    
    def _parse_transitions(self, transition_text: str, total_segments: int) -> Dict[str, Any]:
        """Parse the AI-generated transition analysis"""
        try:
            parsed = {
                "transition_strategy": {},
                "segment_transitions": [],
                "transition_quality_standards": {},
                "transition_templates": []
            }
            
            lines = transition_text.split('\n')
            current_section = None
            current_transition = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('TRANSITION_STRATEGY:'):
                    current_section = 'transition_strategy'
                elif line.startswith('SEGMENT_TRANSITIONS:'):
                    current_section = 'segment_transitions'
                elif line.startswith('TRANSITION_QUALITY_STANDARDS:'):
                    current_section = 'transition_quality_standards'
                elif line.startswith('TRANSITION_TEMPLATES:'):
                    current_section = 'transition_templates'
                elif line.startswith('TRANSITION_') and '_TO_' in line:
                    # New transition
                    if current_section == 'segment_transitions':
                        transition_id = line.replace(':', '')
                        current_transition = {
                            "transition_id": transition_id,
                            "from_segment": self._extract_segment_number(transition_id, "from"),
                            "to_segment": self._extract_segment_number(transition_id, "to"),
                            "details": {}
                        }
                        parsed['segment_transitions'].append(current_transition)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'segment_transitions' and current_transition:
                        self._parse_transition_detail(line, current_transition)
                    elif current_section in ['transition_strategy', 'transition_quality_standards']:
                        self._parse_section_detail(line, parsed[current_section])
                    elif current_section == 'transition_templates':
                        parsed['transition_templates'].append(line[1:].strip())
            
            # Ensure we have transitions even if parsing fails
            if not parsed['segment_transitions']:
                for i in range(total_segments - 1):
                    parsed['segment_transitions'].append({
                        "transition_id": f"TRANSITION_{i+1}_TO_{i+2}",
                        "from_segment": i + 1,
                        "to_segment": i + 2,
                        "details": {}
                    })
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing transitions: {str(e)}")
            return {
                "transition_strategy": {"overall_approach": "Smooth and natural content flow"},
                "segment_transitions": [
                    {
                        "transition_id": f"TRANSITION_{i+1}_TO_{i+2}",
                        "from_segment": i + 1,
                        "to_segment": i + 2,
                        "details": {}
                    } for i in range(total_segments - 1)
                ],
                "transition_quality_standards": {"naturalness_criteria": "Natural flow maintenance"},
                "transition_templates": [],
                "parse_error": str(e)
            }
    
    def _extract_segment_number(self, transition_id: str, position: str) -> int:
        """Extract segment number from transition ID"""
        try:
            parts = transition_id.split('_')
            if position == "from":
                return int(parts[1]) if len(parts) > 1 else 1
            else:  # position == "to"
                return int(parts[3]) if len(parts) > 3 else 2
        except:
            return 1 if position == "from" else 2
    
    def _parse_transition_detail(self, line: str, transition: Dict[str, Any]):
        """Parse individual transition detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                transition['details'][key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass
    
    def _parse_section_detail(self, line: str, section_dict: Dict[str, Any]):
        """Parse section detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                section_dict[key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass


class NarrativeContinuitySystem:
    """
    Main orchestrator for the Narrative Continuity System.
    Combines all components to provide comprehensive narrative management.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.story_arc_manager = StoryArcManager(api_key)
        self.character_consistency_engine = CharacterConsistencyEngine(api_key)
        self.theme_continuity_tracker = ThemeContinuityTracker(api_key)
        self.transition_generator = TransitionGenerator(api_key)
    
    async def analyze_narrative_continuity(self,
                                         original_prompt: str,
                                         video_type: str,
                                         segment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete narrative continuity analysis combining all components
        
        Args:
            original_prompt: Original user prompt
            video_type: Type of video content
            segment_plan: Segment plan from Phase 1
            
        Returns:
            Comprehensive narrative continuity analysis
        """
        try:
            total_segments = segment_plan.get('segmentation_details', {}).get('total_segments', 1)
            logger.info(f"🎭 Starting comprehensive narrative continuity analysis for {total_segments} segments")
            
            # Phase 1: Analyze story arc
            logger.info("📖 Phase 1: Analyzing story arc...")
            narrative_arc = await self.story_arc_manager.analyze_narrative_arc(
                original_prompt, video_type, total_segments, segment_plan
            )
            
            if not narrative_arc.get('narrative_analysis_complete'):
                logger.error("Story arc analysis failed")
                return {"error": "Story arc analysis failed", "component": "story_arc_manager"}
            
            # Phase 2: Analyze character consistency
            logger.info("👤 Phase 2: Analyzing character consistency...")
            character_consistency = await self.character_consistency_engine.analyze_character_consistency(
                narrative_arc, original_prompt, video_type
            )
            
            if not character_consistency.get('character_analysis_complete'):
                logger.error("Character consistency analysis failed")
                return {"error": "Character consistency analysis failed", "component": "character_consistency_engine"}
            
            # Phase 3: Analyze theme continuity
            logger.info("🎯 Phase 3: Analyzing theme continuity...")
            theme_continuity = await self.theme_continuity_tracker.analyze_theme_continuity(
                narrative_arc, character_consistency, original_prompt
            )
            
            if not theme_continuity.get('theme_analysis_complete'):
                logger.error("Theme continuity analysis failed")
                return {"error": "Theme continuity analysis failed", "component": "theme_continuity_tracker"}
            
            # Phase 4: Generate transitions
            logger.info("🔗 Phase 4: Generating transitions...")
            transitions = await self.transition_generator.generate_transitions(
                narrative_arc, character_consistency, theme_continuity, total_segments
            )
            
            if not transitions.get('transition_analysis_complete'):
                logger.error("Transition generation failed")
                return {"error": "Transition generation failed", "component": "transition_generator"}
            
            # Combine all results
            logger.info("🎭 Narrative continuity analysis complete!")
            
            return {
                "narrative_continuity_complete": True,
                "original_prompt": original_prompt,
                "video_type": video_type,
                "total_segments": total_segments,
                "analysis_components": {
                    "story_arc": narrative_arc,
                    "character_consistency": character_consistency,
                    "theme_continuity": theme_continuity,
                    "transitions": transitions
                },
                "phase_completed": "Phase 2: Narrative Continuity System",
                "next_phase": "Ready for actual segment content generation",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in narrative continuity analysis: {str(e)}")
            return {"error": str(e), "narrative_continuity_complete": False}
    
    def get_segment_narrative_context(self, 
                                    narrative_continuity: Dict[str, Any], 
                                    segment_number: int) -> Dict[str, Any]:
        """
        Get narrative context for generating a specific segment
        
        Args:
            narrative_continuity: Output from analyze_narrative_continuity
            segment_number: Segment number (1-indexed)
            
        Returns:
            Narrative context for this specific segment
        """
        try:
            components = narrative_continuity.get('analysis_components', {})
            
            # Extract segment-specific information from each component
            story_arc = components.get('story_arc', {}).get('story_arc', {})
            character_consistency = components.get('character_consistency', {}).get('character_consistency', {})
            theme_continuity = components.get('theme_continuity', {}).get('theme_continuity', {})
            transitions = components.get('transitions', {}).get('transitions', {})
            
            # Get segment-specific story arc
            story_progression = story_arc.get('story_arc_progression', [])
            segment_story_arc = None
            if segment_number <= len(story_progression):
                segment_story_arc = story_progression[segment_number - 1]
            
            # Get segment-specific character evolution
            character_evolution = character_consistency.get('segment_character_evolution', [])
            segment_character = None
            if segment_number <= len(character_evolution):
                segment_character = character_evolution[segment_number - 1]
            
            # Get segment-specific theme mapping
            theme_mapping = theme_continuity.get('segment_theme_mapping', [])
            segment_theme = None
            if segment_number <= len(theme_mapping):
                segment_theme = theme_mapping[segment_number - 1]
            
            # Get relevant transitions
            segment_transitions = {
                "incoming": None,
                "outgoing": None
            }
            
            all_transitions = transitions.get('segment_transitions', [])
            for transition in all_transitions:
                if transition.get('to_segment') == segment_number:
                    segment_transitions["incoming"] = transition
                elif transition.get('from_segment') == segment_number:
                    segment_transitions["outgoing"] = transition
            
            return {
                "segment_number": segment_number,
                "total_segments": narrative_continuity.get('total_segments', 1),
                "story_arc_context": segment_story_arc,
                "character_context": segment_character,
                "theme_context": segment_theme,
                "transitions": segment_transitions,
                "global_context": {
                    "overall_theme": story_arc.get('overall_narrative_theme', ''),
                    "character_profile": character_consistency.get('primary_character_profile', {}),
                    "core_theme_structure": theme_continuity.get('core_theme_structure', {}),
                    "consistency_guidelines": {
                        "character_markers": character_consistency.get('consistency_markers', {}),
                        "theme_framework": theme_continuity.get('consistency_framework', {}),
                        "transition_standards": transitions.get('transition_quality_standards', {})
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting segment narrative context: {str(e)}")
            return {"error": str(e)}
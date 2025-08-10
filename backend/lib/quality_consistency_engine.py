"""
Quality Consistency Engine - Phase 2: Advanced Script Generation Logic

This module implements comprehensive quality consistency management for segmented 
script generation. It ensures uniform production value, tone consistency, and 
balanced engagement across all script segments.

Components:
- Cross-Segment Quality Validator: Ensures consistent production value across segments
- Tone Consistency Monitor: Maintains uniform voice and style throughout
- Engagement Balance Controller: Distributes engagement peaks evenly across segments
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

logger = logging.getLogger(__name__)

class CrossSegmentQualityValidator:
    """
    Validates and ensures consistent quality standards across all segments.
    Maintains uniform production value, writing quality, and content standards.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Quality dimensions and standards
        self.quality_dimensions = {
            "content_quality": {
                "accuracy": {"weight": 0.25, "min_score": 0.8},
                "depth": {"weight": 0.20, "min_score": 0.7},
                "relevance": {"weight": 0.25, "min_score": 0.8},
                "clarity": {"weight": 0.30, "min_score": 0.8}
            },
            "production_value": {
                "visual_descriptions": {"weight": 0.30, "min_score": 0.7},
                "audio_cues": {"weight": 0.25, "min_score": 0.7},
                "pacing": {"weight": 0.25, "min_score": 0.7},
                "polish": {"weight": 0.20, "min_score": 0.8}
            },
            "engagement_quality": {
                "hook_strength": {"weight": 0.30, "min_score": 0.7},
                "curiosity_maintenance": {"weight": 0.25, "min_score": 0.7},
                "emotional_connection": {"weight": 0.25, "min_score": 0.7},
                "retention_elements": {"weight": 0.20, "min_score": 0.7}
            }
        }
    
    async def establish_quality_standards(self,
                                        video_type: str,
                                        total_segments: int,
                                        overall_theme: str,
                                        target_audience: str = "general") -> Dict[str, Any]:
        """
        Establish comprehensive quality standards for all segments
        
        Args:
            video_type: Type of video content
            total_segments: Total number of segments
            overall_theme: Main theme of the content
            target_audience: Target audience description
            
        Returns:
            Comprehensive quality standards framework
        """
        try:
            logger.info(f"🎯 Establishing quality standards for {total_segments} segments")
            
            # Create quality standards chat instance
            standards_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"quality-standards-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Quality Assurance Strategist specializing in cross-segment content consistency for video productions. Your expertise lies in establishing and maintaining uniform quality standards across multi-segment content while ensuring each segment meets professional production benchmarks.

CORE EXPERTISE:
1. QUALITY FRAMEWORK DESIGN: Creating comprehensive quality measurement systems
2. CONSISTENCY BENCHMARKING: Establishing uniform standards across all segments
3. PRODUCTION VALUE ASSESSMENT: Evaluating professional production elements
4. CONTENT QUALITY METRICS: Measuring accuracy, depth, relevance, and clarity
5. AUDIENCE EXPERIENCE OPTIMIZATION: Ensuring consistent viewer experience quality

You excel at creating quality frameworks that maintain high standards while allowing for natural content variation across segments."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            standards_prompt = f"""Establish comprehensive quality standards for this segmented video content:

CONTENT PARAMETERS:
- Video Type: {video_type}
- Total Segments: {total_segments}
- Overall Theme: {overall_theme}
- Target Audience: {target_audience}

QUALITY DIMENSIONS TO ADDRESS:
{self._format_quality_dimensions()}

Create detailed quality standards following this EXACT format:

OVERALL_QUALITY_FRAMEWORK:
- QUALITY_PHILOSOPHY: [Core philosophy governing all quality decisions]
- CONSISTENCY_APPROACH: [How consistency will be maintained across segments]
- QUALITY_BASELINE: [Minimum acceptable quality level for all segments]
- EXCELLENCE_TARGETS: [What constitutes exceptional quality for this content]

CONTENT_QUALITY_STANDARDS:
- ACCURACY_REQUIREMENTS: [Standards for factual accuracy and correctness]
- DEPTH_EXPECTATIONS: [How deep content should go for this audience/type]
- RELEVANCE_CRITERIA: [What makes content relevant and valuable]
- CLARITY_BENCHMARKS: [Standards for clear, understandable content]

PRODUCTION_VALUE_STANDARDS:
- VISUAL_DESCRIPTION_QUALITY: [Standards for visual storytelling elements]
- AUDIO_CUE_INTEGRATION: [Requirements for audio elements and sound design]
- PACING_CONSISTENCY: [How pacing should be maintained across segments]
- POLISH_EXPECTATIONS: [Professional finish and refinement standards]

ENGAGEMENT_QUALITY_STANDARDS:
- HOOK_EFFECTIVENESS: [What constitutes strong opening hooks]
- CURIOSITY_MAINTENANCE: [How to sustain interest throughout each segment]
- EMOTIONAL_CONNECTION: [Standards for audience emotional engagement]
- RETENTION_OPTIMIZATION: [Elements that promote information retention]

CROSS_SEGMENT_CONSISTENCY:
- TONE_UNIFORMITY: [How tone should remain consistent across segments]
- STYLE_CONSISTENCY: [Writing and presentation style standards]
- ENERGY_LEVEL_MANAGEMENT: [How energy should be managed across segments]
- BRANDING_COHERENCE: [How brand/theme coherence is maintained]

QUALITY_VALIDATION_FRAMEWORK:
- ASSESSMENT_CRITERIA: [How quality will be measured for each segment]
- CONSISTENCY_CHECKPOINTS: [Key points where consistency is verified]
- IMPROVEMENT_PROTOCOLS: [How quality issues will be addressed]
- EXCELLENCE_INDICATORS: [What signals exceptional quality achievement]

SEGMENT_SPECIFIC_ADAPTATIONS:
[How quality standards adapt for different segment positions while maintaining consistency]"""

            response = await standards_chat.send_message(UserMessage(text=standards_prompt))
            
            # Parse the quality standards response
            parsed_standards = self._parse_quality_standards(response)
            
            return {
                "quality_standards_complete": True,
                "video_type": video_type,
                "total_segments": total_segments,
                "overall_theme": overall_theme,
                "target_audience": target_audience,
                "quality_standards": parsed_standards,
                "quality_dimensions": self.quality_dimensions,
                "standards_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error establishing quality standards: {str(e)}")
            return {"error": str(e), "quality_standards_complete": False}
    
    def _format_quality_dimensions(self) -> str:
        """Format quality dimensions for prompt inclusion"""
        formatted = []
        for dimension, criteria in self.quality_dimensions.items():
            formatted.append(f"\n{dimension.upper()}:")
            for criterion, details in criteria.items():
                formatted.append(f"  - {criterion}: Weight {details['weight']}, Min Score {details['min_score']}")
        return "\n".join(formatted)
    
    def _parse_quality_standards(self, standards_text: str) -> Dict[str, Any]:
        """Parse the AI-generated quality standards"""
        try:
            parsed = {
                "overall_quality_framework": {},
                "content_quality_standards": {},
                "production_value_standards": {},
                "engagement_quality_standards": {},
                "cross_segment_consistency": {},
                "quality_validation_framework": {},
                "segment_specific_adaptations": ""
            }
            
            lines = standards_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('OVERALL_QUALITY_FRAMEWORK:'):
                    current_section = 'overall_quality_framework'
                elif line.startswith('CONTENT_QUALITY_STANDARDS:'):
                    current_section = 'content_quality_standards'
                elif line.startswith('PRODUCTION_VALUE_STANDARDS:'):
                    current_section = 'production_value_standards'
                elif line.startswith('ENGAGEMENT_QUALITY_STANDARDS:'):
                    current_section = 'engagement_quality_standards'
                elif line.startswith('CROSS_SEGMENT_CONSISTENCY:'):
                    current_section = 'cross_segment_consistency'
                elif line.startswith('QUALITY_VALIDATION_FRAMEWORK:'):
                    current_section = 'quality_validation_framework'
                elif line.startswith('SEGMENT_SPECIFIC_ADAPTATIONS:'):
                    current_section = 'segment_specific_adaptations'
                    parsed['segment_specific_adaptations'] = line.replace('SEGMENT_SPECIFIC_ADAPTATIONS:', '').strip()
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section != 'segment_specific_adaptations':
                        self._parse_section_detail(line, parsed[current_section])
                elif current_section == 'segment_specific_adaptations' and not line.startswith(('OVERALL_', 'CONTENT_', 'PRODUCTION_', 'ENGAGEMENT_', 'CROSS_', 'QUALITY_')):
                    parsed['segment_specific_adaptations'] += ' ' + line
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing quality standards: {str(e)}")
            return {
                "overall_quality_framework": {"quality_philosophy": "Maintain professional standards across all segments"},
                "content_quality_standards": {"accuracy_requirements": "High accuracy and factual correctness"},
                "production_value_standards": {"visual_description_quality": "Professional visual storytelling"},
                "engagement_quality_standards": {"hook_effectiveness": "Strong, compelling openings"},
                "cross_segment_consistency": {"tone_uniformity": "Consistent tone throughout content"},
                "quality_validation_framework": {"assessment_criteria": "Comprehensive quality assessment"},
                "segment_specific_adaptations": "Appropriate adaptations while maintaining consistency",
                "parse_error": str(e)
            }
    
    def _parse_section_detail(self, line: str, section_dict: Dict[str, Any]):
        """Parse section detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                section_dict[key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass


class ToneConsistencyMonitor:
    """
    Monitors and maintains consistent tone, voice, and style across all segments.
    Ensures uniform personality and communication approach throughout content.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def analyze_tone_consistency(self,
                                     character_consistency: Dict[str, Any],
                                     quality_standards: Dict[str, Any],
                                     total_segments: int) -> Dict[str, Any]:
        """
        Analyze and create tone consistency framework for all segments
        
        Args:
            character_consistency: Character consistency from narrative continuity
            quality_standards: Quality standards from quality validator
            total_segments: Total number of segments
            
        Returns:
            Comprehensive tone consistency analysis and guidelines
        """
        try:
            logger.info(f"🎭 Analyzing tone consistency for {total_segments} segments")
            
            # Create tone consistency chat instance
            tone_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"tone-consistency-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Voice and Tone Specialist for multi-segment video content. Your expertise lies in maintaining consistent personality, communication style, and emotional resonance across extended content while allowing for natural variations that enhance rather than disrupt the viewing experience.

CORE EXPERTISE:
1. VOICE CONSISTENCY: Maintaining uniform narrator/presenter personality across segments
2. TONE MODULATION: Managing appropriate tone shifts while preserving core voice
3. STYLE UNIFORMITY: Ensuring consistent communication patterns and language use
4. EMOTIONAL COHERENCE: Managing emotional journey while maintaining consistent base tone
5. AUTHENTICITY PRESERVATION: Keeping genuine voice throughout extended content

You excel at creating tone frameworks that feel natural and engaging while maintaining professional consistency across all segments."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Extract character and quality information
            character_profile = character_consistency.get('character_consistency', {}).get('primary_character_profile', {})
            consistency_markers = character_consistency.get('character_consistency', {}).get('consistency_markers', {})
            cross_segment_consistency = quality_standards.get('quality_standards', {}).get('cross_segment_consistency', {})
            
            tone_prompt = f"""Create comprehensive tone consistency framework for this segmented video content:

CONTENT PARAMETERS:
- Total Segments: {total_segments}
- Video Type: {quality_standards.get('video_type', 'general')}
- Target Audience: {quality_standards.get('target_audience', 'general')}

CHARACTER FOUNDATION:
{self._format_character_profile(character_profile)}

CONSISTENCY MARKERS:
{self._format_consistency_markers(consistency_markers)}

QUALITY CONSISTENCY REQUIREMENTS:
{self._format_consistency_requirements(cross_segment_consistency)}

Create detailed tone consistency framework following this EXACT format:

CORE_TONE_IDENTITY:
- PRIMARY_VOICE_CHARACTERISTICS: [Key personality traits that define the voice]
- COMMUNICATION_STYLE: [How this voice communicates - formal, casual, energetic, etc.]
- EMOTIONAL_BASELINE: [Default emotional state and range]
- AUTHENTICITY_MARKERS: [What makes this voice feel genuine and consistent]

TONE_VARIATION_FRAMEWORK:
- ALLOWABLE_VARIATIONS: [How tone can naturally vary while staying consistent]
- SEGMENT_ADAPTATIONS: [How tone adapts to different segment purposes]
- EMOTIONAL_RANGE_MANAGEMENT: [How to manage emotional peaks without losing consistency]
- ENERGY_LEVEL_CONSISTENCY: [How energy varies appropriately across segments]

SEGMENT_TONE_MAPPING:
SEGMENT_1:
- TONE_FOCUS: [Primary tone characteristics for this segment]
- ENERGY_LEVEL: [Appropriate energy level for segment purpose]
- EMOTIONAL_TARGETS: [Key emotions to convey in this segment]
- CONSISTENCY_ANCHORS: [Elements that maintain voice consistency]

[Continue for all {total_segments} segments...]

LANGUAGE_CONSISTENCY_FRAMEWORK:
- VOCABULARY_STANDARDS: [Consistent vocabulary and language level]
- PHRASE_PATTERNS: [Signature phrases and communication patterns]
- TRANSITION_CONSISTENCY: [How transitions maintain voice consistency]
- ENGAGEMENT_LANGUAGE: [Consistent approach to audience engagement]

CONSISTENCY_VALIDATION_SYSTEM:
- TONE_CHECKPOINTS: [Key elements to verify in each segment]
- VOICE_AUTHENTICATION: [How to ensure voice authenticity]
- DEVIATION_CORRECTION: [How to address tone inconsistencies]
- NATURAL_VARIATION_GUIDELINES: [Distinguishing natural variation from inconsistency]

SEGMENT_TRANSITION_TONE_MANAGEMENT:
[How tone is managed during transitions between segments to maintain consistency]"""

            response = await tone_chat.send_message(UserMessage(text=tone_prompt))
            
            # Parse the tone consistency response
            parsed_tone = self._parse_tone_consistency(response, total_segments)
            
            return {
                "tone_consistency_complete": True,
                "total_segments": total_segments,
                "tone_consistency": parsed_tone,
                "tone_analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing tone consistency: {str(e)}")
            return {"error": str(e), "tone_consistency_complete": False}
    
    def _format_character_profile(self, character_profile: Dict[str, Any]) -> str:
        """Format character profile for prompt inclusion"""
        if not character_profile:
            return "No character profile available"
        
        formatted_parts = []
        for key, value in character_profile.items():
            formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No character details available"
    
    def _format_consistency_markers(self, consistency_markers: Dict[str, Any]) -> str:
        """Format consistency markers for prompt inclusion"""
        if not consistency_markers:
            return "No consistency markers available"
        
        formatted_parts = []
        for key, value in consistency_markers.items():
            formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No consistency markers available"
    
    def _format_consistency_requirements(self, cross_segment_consistency: Dict[str, Any]) -> str:
        """Format consistency requirements for prompt inclusion"""
        if not cross_segment_consistency:
            return "No specific consistency requirements"
        
        formatted_parts = []
        for key, value in cross_segment_consistency.items():
            formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "Standard consistency requirements"
    
    def _parse_tone_consistency(self, tone_text: str, total_segments: int) -> Dict[str, Any]:
        """Parse the AI-generated tone consistency analysis"""
        try:
            parsed = {
                "core_tone_identity": {},
                "tone_variation_framework": {},
                "segment_tone_mapping": [],
                "language_consistency_framework": {},
                "consistency_validation_system": {},
                "segment_transition_tone_management": ""
            }
            
            lines = tone_text.split('\n')
            current_section = None
            current_segment = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('CORE_TONE_IDENTITY:'):
                    current_section = 'core_tone_identity'
                elif line.startswith('TONE_VARIATION_FRAMEWORK:'):
                    current_section = 'tone_variation_framework'
                elif line.startswith('SEGMENT_TONE_MAPPING:'):
                    current_section = 'segment_tone_mapping'
                elif line.startswith('LANGUAGE_CONSISTENCY_FRAMEWORK:'):
                    current_section = 'language_consistency_framework'
                elif line.startswith('CONSISTENCY_VALIDATION_SYSTEM:'):
                    current_section = 'consistency_validation_system'
                elif line.startswith('SEGMENT_TRANSITION_TONE_MANAGEMENT:'):
                    current_section = 'segment_transition_tone_management'
                    parsed['segment_transition_tone_management'] = line.replace('SEGMENT_TRANSITION_TONE_MANAGEMENT:', '').strip()
                elif line.startswith('SEGMENT_'):
                    # New segment in tone mapping
                    if current_section == 'segment_tone_mapping':
                        current_segment = {
                            "segment_number": len(parsed['segment_tone_mapping']) + 1,
                            "tone_details": {}
                        }
                        parsed['segment_tone_mapping'].append(current_segment)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'segment_tone_mapping' and current_segment:
                        self._parse_tone_detail(line, current_segment)
                    elif current_section in ['core_tone_identity', 'tone_variation_framework', 'language_consistency_framework', 'consistency_validation_system']:
                        self._parse_section_detail(line, parsed[current_section])
                elif current_section == 'segment_transition_tone_management' and not line.startswith(('CORE_', 'TONE_', 'SEGMENT_', 'LANGUAGE_', 'CONSISTENCY_')):
                    parsed['segment_transition_tone_management'] += ' ' + line
            
            # Ensure we have segments even if parsing fails
            if not parsed['segment_tone_mapping']:
                parsed['segment_tone_mapping'] = [
                    {"segment_number": i+1, "tone_details": {}} for i in range(total_segments)
                ]
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing tone consistency: {str(e)}")
            return {
                "core_tone_identity": {"primary_voice_characteristics": "Professional and engaging presenter"},
                "tone_variation_framework": {"allowable_variations": "Natural variations maintaining core voice"},
                "segment_tone_mapping": [{"segment_number": i+1, "tone_details": {}} for i in range(total_segments)],
                "language_consistency_framework": {"vocabulary_standards": "Consistent professional vocabulary"},
                "consistency_validation_system": {"tone_checkpoints": "Regular tone consistency verification"},
                "segment_transition_tone_management": "Smooth tone transitions between segments",
                "parse_error": str(e)
            }
    
    def _parse_tone_detail(self, line: str, segment: Dict[str, Any]):
        """Parse individual tone detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                segment['tone_details'][key.strip().lower().replace(' ', '_')] = value.strip()
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


class EngagementBalanceController:
    """
    Manages engagement distribution across segments to maintain consistent audience interest.
    Prevents engagement fatigue while ensuring sustained attention throughout content.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Engagement distribution patterns
        self.engagement_patterns = {
            "linear": "Consistent engagement level across all segments",
            "wave": "Alternating high and moderate engagement levels",
            "crescendo": "Gradually building engagement toward climax",
            "plateau": "High engagement maintained throughout with peaks",
            "valley": "Strong opening and closing with moderate middle"
        }
    
    async def analyze_engagement_balance(self,
                                       story_arc: Dict[str, Any],
                                       tone_consistency: Dict[str, Any],
                                       total_segments: int,
                                       video_type: str) -> Dict[str, Any]:
        """
        Analyze and create engagement balance strategy across all segments
        
        Args:
            story_arc: Story arc from narrative continuity
            tone_consistency: Tone consistency analysis
            total_segments: Total number of segments
            video_type: Type of video content
            
        Returns:
            Comprehensive engagement balance analysis and distribution plan
        """
        try:
            logger.info(f"⚡ Analyzing engagement balance for {total_segments} segments")
            
            # Create engagement balance chat instance
            engagement_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"engagement-balance-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Engagement Strategist specializing in attention management across multi-segment video content. Your expertise lies in distributing engagement elements strategically to maintain consistent audience attention while preventing fatigue and optimizing retention throughout extended content.

CORE EXPERTISE:
1. ATTENTION SPAN MANAGEMENT: Understanding and working with natural attention patterns
2. ENGAGEMENT DISTRIBUTION: Strategic placement of high-engagement elements across segments
3. FATIGUE PREVENTION: Avoiding engagement overload while maintaining interest
4. RETENTION OPTIMIZATION: Maximizing audience retention across all segments
5. ENERGY ARCHITECTURE: Creating sustainable engagement energy across extended content

You excel at creating engagement strategies that feel natural and compelling while maintaining optimal audience attention throughout the complete viewing experience."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            # Extract story and tone information
            story_progression = story_arc.get('story_arc_progression', [])
            engagement_strategy = story_arc.get('engagement_strategy', {})
            tone_mapping = tone_consistency.get('tone_consistency', {}).get('segment_tone_mapping', [])
            
            engagement_prompt = f"""Create comprehensive engagement balance strategy for this segmented video content:

CONTENT PARAMETERS:
- Total Segments: {total_segments}
- Video Type: {video_type}

STORY ARC PROGRESSION:
{self._format_story_progression(story_progression)}

EXISTING ENGAGEMENT STRATEGY:
{self._format_engagement_strategy(engagement_strategy)}

TONE MAPPING ACROSS SEGMENTS:
{self._format_tone_mapping(tone_mapping)}

ENGAGEMENT PATTERNS AVAILABLE:
{self._format_engagement_patterns()}

Create detailed engagement balance strategy following this EXACT format:

ENGAGEMENT_DISTRIBUTION_PHILOSOPHY:
- OVERALL_ENGAGEMENT_APPROACH: [Core philosophy for maintaining audience attention]
- ATTENTION_SPAN_CONSIDERATIONS: [How natural attention patterns are accommodated]
- FATIGUE_PREVENTION_STRATEGY: [How engagement fatigue is avoided]
- RETENTION_OPTIMIZATION_METHOD: [Primary method for maximizing retention]

ENGAGEMENT_PATTERN_SELECTION:
- CHOSEN_PATTERN: [Selected engagement pattern from available options]
- PATTERN_JUSTIFICATION: [Why this pattern suits the content and audience]
- ADAPTATION_STRATEGY: [How the pattern is adapted for specific content needs]
- ENERGY_FLOW_DESIGN: [How engagement energy flows across segments]

SEGMENT_ENGAGEMENT_DISTRIBUTION:
SEGMENT_1:
- ENGAGEMENT_LEVEL: [Low/Medium/High/Peak engagement level]
- ENGAGEMENT_TECHNIQUES: [Specific techniques used to achieve engagement]
- ATTENTION_MANAGEMENT: [How attention is captured and maintained]
- ENERGY_CONTRIBUTION: [How this segment contributes to overall energy]
- TRANSITION_ENGAGEMENT: [How engagement transitions to next segment]

[Continue for all {total_segments} segments...]

ENGAGEMENT_BALANCE_FRAMEWORK:
- HIGH_ENGAGEMENT_DISTRIBUTION: [How peak engagement moments are distributed]
- RECOVERY_PERIODS: [Where and how audience gets engagement recovery]
- CURIOSITY_MAINTENANCE: [How curiosity is sustained across segments]
- EMOTIONAL_ENGAGEMENT_BALANCE: [How emotional engagement is balanced]

RETENTION_OPTIMIZATION_STRATEGY:
- HOOK_DISTRIBUTION: [How hooks are distributed across segments]
- PAYOFF_SCHEDULING: [When audience gets satisfaction/payoff]
- CLIFFHANGER_MANAGEMENT: [Strategic use of cliffhangers between segments]
- RESOLUTION_PACING: [How resolutions are paced for optimal retention]

ENGAGEMENT_QUALITY_CONTROLS:
- ENGAGEMENT_MONITORING: [How engagement levels are tracked/validated]
- BALANCE_VERIFICATION: [How to verify optimal engagement balance]
- ADJUSTMENT_PROTOCOLS: [How to adjust engagement if balance is off]
- SUCCESS_METRICS: [What indicates successful engagement balance]

AUDIENCE_EXPERIENCE_OPTIMIZATION:
[How the engagement strategy optimizes the complete audience viewing experience]"""

            response = await engagement_chat.send_message(UserMessage(text=engagement_prompt))
            
            # Parse the engagement balance response
            parsed_engagement = self._parse_engagement_balance(response, total_segments)
            
            return {
                "engagement_balance_complete": True,
                "total_segments": total_segments,
                "video_type": video_type,
                "engagement_balance": parsed_engagement,
                "engagement_analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement balance: {str(e)}")
            return {"error": str(e), "engagement_balance_complete": False}
    
    def _format_story_progression(self, story_progression: List[Dict[str, Any]]) -> str:
        """Format story progression for prompt inclusion"""
        if not story_progression:
            return "No story progression available"
        
        formatted = []
        for segment in story_progression:
            seg_num = segment.get('segment_number', 1)
            details = segment.get('details', {})
            arc_position = details.get('arc_position', 'development')
            tension_level = details.get('tension_level', 'Medium')
            formatted.append(f"Segment {seg_num}: {arc_position} (Tension: {tension_level})")
        
        return "\n".join(formatted) if formatted else "No story progression details available"
    
    def _format_engagement_strategy(self, engagement_strategy: Dict[str, Any]) -> str:
        """Format engagement strategy for prompt inclusion"""
        if not engagement_strategy:
            return "No existing engagement strategy"
        
        formatted_parts = []
        for key, value in engagement_strategy.items():
            formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts) if formatted_parts else "No engagement strategy details"
    
    def _format_tone_mapping(self, tone_mapping: List[Dict[str, Any]]) -> str:
        """Format tone mapping for prompt inclusion"""
        if not tone_mapping:
            return "No tone mapping available"
        
        formatted = []
        for segment in tone_mapping:
            seg_num = segment.get('segment_number', 1)
            tone_details = segment.get('tone_details', {})
            energy_level = tone_details.get('energy_level', 'Medium')
            formatted.append(f"Segment {seg_num}: Energy Level {energy_level}")
        
        return "\n".join(formatted) if formatted else "No tone mapping details available"
    
    def _format_engagement_patterns(self) -> str:
        """Format available engagement patterns for prompt inclusion"""
        formatted = []
        for pattern, description in self.engagement_patterns.items():
            formatted.append(f"- {pattern.upper()}: {description}")
        
        return "\n".join(formatted)
    
    def _parse_engagement_balance(self, engagement_text: str, total_segments: int) -> Dict[str, Any]:
        """Parse the AI-generated engagement balance analysis"""
        try:
            parsed = {
                "engagement_distribution_philosophy": {},
                "engagement_pattern_selection": {},
                "segment_engagement_distribution": [],
                "engagement_balance_framework": {},
                "retention_optimization_strategy": {},
                "engagement_quality_controls": {},
                "audience_experience_optimization": ""
            }
            
            lines = engagement_text.split('\n')
            current_section = None
            current_segment = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('ENGAGEMENT_DISTRIBUTION_PHILOSOPHY:'):
                    current_section = 'engagement_distribution_philosophy'
                elif line.startswith('ENGAGEMENT_PATTERN_SELECTION:'):
                    current_section = 'engagement_pattern_selection'
                elif line.startswith('SEGMENT_ENGAGEMENT_DISTRIBUTION:'):
                    current_section = 'segment_engagement_distribution'
                elif line.startswith('ENGAGEMENT_BALANCE_FRAMEWORK:'):
                    current_section = 'engagement_balance_framework'
                elif line.startswith('RETENTION_OPTIMIZATION_STRATEGY:'):
                    current_section = 'retention_optimization_strategy'
                elif line.startswith('ENGAGEMENT_QUALITY_CONTROLS:'):
                    current_section = 'engagement_quality_controls'
                elif line.startswith('AUDIENCE_EXPERIENCE_OPTIMIZATION:'):
                    current_section = 'audience_experience_optimization'
                    parsed['audience_experience_optimization'] = line.replace('AUDIENCE_EXPERIENCE_OPTIMIZATION:', '').strip()
                elif line.startswith('SEGMENT_'):
                    # New segment in engagement distribution
                    if current_section == 'segment_engagement_distribution':
                        current_segment = {
                            "segment_number": len(parsed['segment_engagement_distribution']) + 1,
                            "engagement_details": {}
                        }
                        parsed['segment_engagement_distribution'].append(current_segment)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'segment_engagement_distribution' and current_segment:
                        self._parse_engagement_detail(line, current_segment)
                    elif current_section in ['engagement_distribution_philosophy', 'engagement_pattern_selection', 'engagement_balance_framework', 'retention_optimization_strategy', 'engagement_quality_controls']:
                        self._parse_section_detail(line, parsed[current_section])
                elif current_section == 'audience_experience_optimization' and not line.startswith(('ENGAGEMENT_', 'SEGMENT_', 'RETENTION_')):
                    parsed['audience_experience_optimization'] += ' ' + line
            
            # Ensure we have segments even if parsing fails
            if not parsed['segment_engagement_distribution']:
                parsed['segment_engagement_distribution'] = [
                    {"segment_number": i+1, "engagement_details": {}} for i in range(total_segments)
                ]
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing engagement balance: {str(e)}")
            return {
                "engagement_distribution_philosophy": {"overall_engagement_approach": "Consistent audience attention maintenance"},
                "engagement_pattern_selection": {"chosen_pattern": "balanced", "pattern_justification": "Optimal for content type"},
                "segment_engagement_distribution": [{"segment_number": i+1, "engagement_details": {}} for i in range(total_segments)],
                "engagement_balance_framework": {"high_engagement_distribution": "Strategic peak engagement placement"},
                "retention_optimization_strategy": {"hook_distribution": "Even hook distribution across segments"},
                "engagement_quality_controls": {"engagement_monitoring": "Regular engagement level validation"},
                "audience_experience_optimization": "Optimized viewing experience across all segments",
                "parse_error": str(e)
            }
    
    def _parse_engagement_detail(self, line: str, segment: Dict[str, Any]):
        """Parse individual engagement detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                segment['engagement_details'][key.strip().lower().replace(' ', '_')] = value.strip()
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


class QualityConsistencyEngine:
    """
    Main orchestrator for the Quality Consistency Engine.
    Combines all components to provide comprehensive quality management across segments.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.quality_validator = CrossSegmentQualityValidator(api_key)
        self.tone_monitor = ToneConsistencyMonitor(api_key)
        self.engagement_controller = EngagementBalanceController(api_key)
    
    async def analyze_quality_consistency(self,
                                        narrative_continuity: Dict[str, Any],
                                        content_depth_scaling: Dict[str, Any],
                                        video_type: str,
                                        target_audience: str = "general") -> Dict[str, Any]:
        """
        Complete quality consistency analysis combining all components
        
        Args:
            narrative_continuity: Narrative continuity from Phase 2
            content_depth_scaling: Content depth scaling analysis
            video_type: Type of video content
            target_audience: Target audience description
            
        Returns:
            Comprehensive quality consistency analysis
        """
        try:
            total_segments = narrative_continuity.get('total_segments', 1)
            overall_theme = narrative_continuity.get('analysis_components', {}).get('story_arc', {}).get('story_arc', {}).get('overall_narrative_theme', '')
            
            logger.info(f"🎯 Starting comprehensive quality consistency analysis for {total_segments} segments")
            
            # Phase 1: Establish quality standards
            logger.info("📊 Phase 1: Establishing quality standards...")
            quality_standards = await self.quality_validator.establish_quality_standards(
                video_type, total_segments, overall_theme, target_audience
            )
            
            if not quality_standards.get('quality_standards_complete'):
                logger.error("Quality standards establishment failed")
                return {"error": "Quality standards establishment failed", "component": "quality_validator"}
            
            # Phase 2: Analyze tone consistency
            logger.info("🎭 Phase 2: Analyzing tone consistency...")
            character_consistency = narrative_continuity.get('analysis_components', {}).get('character_consistency', {})
            tone_consistency = await self.tone_monitor.analyze_tone_consistency(
                character_consistency, quality_standards, total_segments
            )
            
            if not tone_consistency.get('tone_consistency_complete'):
                logger.error("Tone consistency analysis failed")
                return {"error": "Tone consistency analysis failed", "component": "tone_monitor"}
            
            # Phase 3: Analyze engagement balance
            logger.info("⚡ Phase 3: Analyzing engagement balance...")
            story_arc = narrative_continuity.get('analysis_components', {}).get('story_arc', {}).get('story_arc', {})
            engagement_balance = await self.engagement_controller.analyze_engagement_balance(
                story_arc, tone_consistency, total_segments, video_type
            )
            
            if not engagement_balance.get('engagement_balance_complete'):
                logger.error("Engagement balance analysis failed")
                return {"error": "Engagement balance analysis failed", "component": "engagement_controller"}
            
            # Combine all results
            logger.info("🎯 Quality consistency analysis complete!")
            
            return {
                "quality_consistency_complete": True,
                "video_type": video_type,
                "target_audience": target_audience,
                "total_segments": total_segments,
                "overall_theme": overall_theme,
                "analysis_components": {
                    "quality_standards": quality_standards,
                    "tone_consistency": tone_consistency,
                    "engagement_balance": engagement_balance
                },
                "phase_completed": "Quality Consistency Engine",
                "next_phase": "Ready for Advanced Generation Workflow",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in quality consistency analysis: {str(e)}")
            return {"error": str(e), "quality_consistency_complete": False}
    
    def get_segment_quality_context(self, 
                                  quality_consistency: Dict[str, Any], 
                                  segment_number: int) -> Dict[str, Any]:
        """
        Get quality context for generating a specific segment
        
        Args:
            quality_consistency: Output from analyze_quality_consistency
            segment_number: Segment number (1-indexed)
            
        Returns:
            Quality context for this specific segment
        """
        try:
            components = quality_consistency.get('analysis_components', {})
            
            # Get quality standards
            quality_standards = components.get('quality_standards', {}).get('quality_standards', {})
            
            # Get segment-specific tone mapping
            tone_consistency = components.get('tone_consistency', {}).get('tone_consistency', {})
            segment_tone_mapping = tone_consistency.get('segment_tone_mapping', [])
            segment_tone = None
            if segment_number <= len(segment_tone_mapping):
                segment_tone = segment_tone_mapping[segment_number - 1]
            
            # Get segment-specific engagement distribution
            engagement_balance = components.get('engagement_balance', {}).get('engagement_balance', {})
            segment_engagement_distribution = engagement_balance.get('segment_engagement_distribution', [])
            segment_engagement = None
            if segment_number <= len(segment_engagement_distribution):
                segment_engagement = segment_engagement_distribution[segment_number - 1]
            
            return {
                "segment_number": segment_number,
                "total_segments": quality_consistency.get('total_segments', 1),
                "quality_standards": {
                    "content_quality": quality_standards.get('content_quality_standards', {}),
                    "production_value": quality_standards.get('production_value_standards', {}),
                    "engagement_quality": quality_standards.get('engagement_quality_standards', {}),
                    "validation_framework": quality_standards.get('quality_validation_framework', {})
                },
                "tone_requirements": segment_tone.get('tone_details', {}) if segment_tone else {},
                "engagement_requirements": segment_engagement.get('engagement_details', {}) if segment_engagement else {},
                "global_consistency": {
                    "cross_segment_consistency": quality_standards.get('cross_segment_consistency', {}),
                    "core_tone_identity": tone_consistency.get('core_tone_identity', {}),
                    "engagement_philosophy": engagement_balance.get('engagement_distribution_philosophy', {}),
                    "quality_framework": quality_standards.get('overall_quality_framework', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting segment quality context: {str(e)}")
            return {"error": str(e)}
"""
Advanced Segmented Script Generator - Phase 1: Core Segmentation System
Enhanced with Phase 2: Narrative Continuity System

This module implements intelligent script segmentation for long-form video content (15-30 minutes).
It breaks complex scripts into manageable segments while maintaining narrative coherence.

Phase 1 Features:
- Dynamic duration-based segment calculation
- Intelligent segment planning and coordination
- Content density optimization per segment
- Cross-segment narrative structure management

Phase 2 Features:
- Narrative Continuity System integration
- Story Arc Management across segments
- Character Consistency Engine
- Theme Continuity Tracking
- Transition Generation between segments
"""

import logging
import uuid
from typing import Dict, Any, List, Tuple
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

# Import Phase 2: Narrative Continuity System
from .narrative_continuity_system import NarrativeContinuitySystem

logger = logging.getLogger(__name__)

class SegmentationEngine:
    """
    Core engine for intelligent script segmentation based on duration and content type
    """
    
    def __init__(self):
        self.optimal_segment_duration = 6  # minutes per segment (target)
        self.min_segment_duration = 4      # minimum segment length
        self.max_segment_duration = 8      # maximum segment length
        
        # Duration mappings in minutes for calculation
        self.duration_minutes = {
            "short": 1,      # 30s-1min
            "medium": 2,     # 1-3min  
            "long": 4,       # 3-5min
            "extended_5": 7.5,    # 5-10min
            "extended_10": 12.5,  # 10-15min
            "extended_15": 17.5,  # 15-20min
            "extended_20": 22.5,  # 20-25min
            "extended_25": 27.5   # 25-30min
        }
    
    def calculate_segments(self, duration: str, video_type: str) -> Dict[str, Any]:
        """
        Calculate optimal segmentation strategy based on duration and video type
        
        Args:
            duration: Target duration key (e.g., "extended_15")
            video_type: Type of video content
            
        Returns:
            Segmentation plan with segment count, durations, and structure
        """
        try:
            total_minutes = self.duration_minutes.get(duration, 2)
            
            # For short content, no segmentation needed
            if total_minutes <= 5:
                return {
                    "requires_segmentation": False,
                    "total_segments": 1,
                    "segment_duration_minutes": total_minutes,
                    "segmentation_strategy": "single_pass",
                    "content_density": "standard"
                }
            
            # Calculate optimal segment count for longer content
            segment_count = max(2, round(total_minutes / self.optimal_segment_duration))
            segment_duration = total_minutes / segment_count
            
            # Adjust if segments are too short or too long
            if segment_duration < self.min_segment_duration:
                segment_count = max(1, int(total_minutes / self.min_segment_duration))
                segment_duration = total_minutes / segment_count
            elif segment_duration > self.max_segment_duration:
                segment_count = int(total_minutes / self.max_segment_duration) + 1
                segment_duration = total_minutes / segment_count
            
            # Determine content density based on total duration
            content_density = self._calculate_content_density(total_minutes, video_type)
            
            return {
                "requires_segmentation": True,
                "total_segments": segment_count,
                "segment_duration_minutes": round(segment_duration, 1),
                "total_duration_minutes": total_minutes,
                "segmentation_strategy": "multi_segment",
                "content_density": content_density,
                "estimated_words_per_segment": self._estimate_words_per_segment(segment_duration),
                "narrative_structure": self._plan_narrative_structure(segment_count, video_type)
            }
            
        except Exception as e:
            logger.error(f"Error calculating segments: {str(e)}")
            return {
                "requires_segmentation": False,
                "total_segments": 1,
                "error": str(e)
            }
    
    def _calculate_content_density(self, total_minutes: float, video_type: str) -> str:
        """Calculate appropriate content density based on duration and type"""
        
        # Base density on total duration
        if total_minutes <= 5:
            base_density = "standard"
        elif total_minutes <= 15:
            base_density = "detailed"
        else:
            base_density = "comprehensive"
        
        # Adjust based on video type
        density_modifiers = {
            "educational": +1,    # More detailed explanations needed
            "marketing": 0,       # Standard commercial pacing
            "entertainment": 0,   # Standard engagement pacing
            "general": 0          # Balanced approach
        }
        
        modifier = density_modifiers.get(video_type, 0)
        
        densities = ["light", "standard", "detailed", "comprehensive", "intensive"]
        base_index = densities.index(base_density)
        new_index = max(0, min(len(densities) - 1, base_index + modifier))
        
        return densities[new_index]
    
    def _estimate_words_per_segment(self, segment_duration: float) -> int:
        """Estimate optimal word count per segment based on duration"""
        # Average speaking rate: ~150-160 words per minute for video content
        words_per_minute = 155
        return int(segment_duration * words_per_minute)
    
    def _plan_narrative_structure(self, segment_count: int, video_type: str) -> List[Dict[str, Any]]:
        """Plan narrative arc structure across segments"""
        
        if segment_count == 1:
            return [{
                "segment_id": 1,
                "narrative_role": "complete_story",
                "content_focus": "full_arc",
                "engagement_level": "high"
            }]
        
        structure = []
        
        for i in range(segment_count):
            segment_role = self._determine_segment_role(i, segment_count, video_type)
            structure.append({
                "segment_id": i + 1,
                "narrative_role": segment_role["role"],
                "content_focus": segment_role["focus"],
                "engagement_level": segment_role["engagement"],
                "transition_to_next": segment_role.get("transition", "smooth") if i < segment_count - 1 else "conclusion"
            })
        
        return structure
    
    def _determine_segment_role(self, segment_index: int, total_segments: int, video_type: str) -> Dict[str, str]:
        """Determine the narrative role of each segment"""
        
        segment_position = segment_index / (total_segments - 1) if total_segments > 1 else 0
        
        if segment_position == 0:
            # First segment - Hook and Introduction
            return {
                "role": "introduction_hook",
                "focus": "capture_attention",
                "engagement": "very_high",
                "transition": "building_curiosity"
            }
        elif segment_position < 0.3:
            # Early segments - Problem/Context Setting
            return {
                "role": "context_building",
                "focus": "establish_foundation", 
                "engagement": "high",
                "transition": "deepening_understanding"
            }
        elif segment_position < 0.7:
            # Middle segments - Core Content/Development
            return {
                "role": "core_development",
                "focus": "main_content",
                "engagement": "sustained_high",
                "transition": "progressive_revelation"
            }
        elif segment_position < 0.9:
            # Later segments - Climax/Key Insights
            return {
                "role": "climax_insights",
                "focus": "key_revelations",
                "engagement": "peak",
                "transition": "building_to_resolution"
            }
        else:
            # Final segment - Resolution/Call to Action
            return {
                "role": "resolution_action",
                "focus": "conclusions_cta",
                "engagement": "very_high"
            }


class SegmentPlanner:
    """
    Plans individual segment content and coordinates between segments
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def create_segment_plan(self, 
                                original_prompt: str, 
                                segmentation_plan: Dict[str, Any], 
                                video_type: str) -> Dict[str, Any]:
        """
        Create detailed plan for each segment including content outline and coordination
        
        Args:
            original_prompt: Original user prompt
            segmentation_plan: Output from SegmentationEngine
            video_type: Type of video content
            
        Returns:
            Comprehensive segment plan with outlines and coordination strategy
        """
        try:
            if not segmentation_plan.get("requires_segmentation", False):
                return {
                    "segmentation_required": False,
                    "single_segment_plan": await self._create_single_segment_plan(original_prompt, video_type)
                }
            
            # Create planning chat instance
            planning_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"segment-planner-{str(uuid.uuid4())[:8]}",
                system_message="""You are an Expert Content Strategist and Script Architect specializing in long-form video content segmentation. Your expertise lies in breaking complex topics into engaging, coherent segments while maintaining narrative flow.

CORE EXPERTISE:
1. SEGMENT CONTENT PLANNING: Creating detailed outlines for each segment that build upon each other
2. NARRATIVE ARC MANAGEMENT: Ensuring smooth story progression across multiple segments  
3. ENGAGEMENT DISTRIBUTION: Balancing information density and engagement across segments
4. TRANSITION COORDINATION: Planning smooth bridges between segments
5. CONTENT DEPTH OPTIMIZATION: Scaling detail level appropriately for segment duration

You excel at creating segment plans that feel like a cohesive whole rather than disconnected pieces."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            planning_prompt = f"""Create a comprehensive segment plan for this video content:

ORIGINAL PROMPT: "{original_prompt}"
VIDEO TYPE: {video_type}
SEGMENTATION DETAILS:
- Total segments: {segmentation_plan['total_segments']}
- Segment duration: {segmentation_plan['segment_duration_minutes']} minutes each
- Content density: {segmentation_plan['content_density']}
- Total duration: {segmentation_plan['total_duration_minutes']} minutes

NARRATIVE STRUCTURE:
{self._format_narrative_structure(segmentation_plan.get('narrative_structure', []))}

Create a detailed plan following this EXACT format:

OVERALL_STRATEGY:
[Brief description of the overarching approach and how segments will work together]

SEGMENT_OUTLINES:
SEGMENT_1:
- NARRATIVE_ROLE: {segmentation_plan['narrative_structure'][0]['narrative_role'] if segmentation_plan.get('narrative_structure') else 'introduction'}
- CONTENT_FOCUS: [What this segment will cover]
- KEY_POINTS: [3-4 main points to address]
- ENGAGEMENT_HOOKS: [Specific elements to maintain engagement]
- VISUAL_THEMES: [Visual storytelling elements and AI image prompt themes]
- TRANSITION_SETUP: [How this segment sets up the next one]

[Continue for all {segmentation_plan['total_segments']} segments...]

COORDINATION_STRATEGY:
- CHARACTER_CONSISTENCY: [How to maintain consistent characters/personas]
- VISUAL_CONTINUITY: [Visual elements that will tie segments together]  
- THEMATIC_THREADS: [Core themes that will run through all segments]
- PACING_BALANCE: [How to balance information density across segments]
- ENGAGEMENT_DISTRIBUTION: [How to distribute high-engagement moments]

QUALITY_CHECKPOINTS:
[Key quality standards to maintain across all segments]"""

            response = await planning_chat.send_message(UserMessage(text=planning_prompt))
            
            # Parse the response into structured format
            parsed_plan = self._parse_segment_plan(response, segmentation_plan)
            
            return {
                "segmentation_required": True,
                "original_prompt": original_prompt,
                "video_type": video_type,
                "segmentation_details": segmentation_plan,
                "segment_plan": parsed_plan,
                "planning_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating segment plan: {str(e)}")
            return {"error": str(e)}
    
    def _format_narrative_structure(self, narrative_structure: List[Dict[str, Any]]) -> str:
        """Format narrative structure for prompt inclusion"""
        formatted = []
        for segment in narrative_structure:
            formatted.append(f"Segment {segment['segment_id']}: {segment['narrative_role']} - {segment['content_focus']}")
        return "\n".join(formatted)
    
    async def _create_single_segment_plan(self, original_prompt: str, video_type: str) -> Dict[str, Any]:
        """Create plan for single segment content (short duration)"""
        return {
            "approach": "single_pass_generation",
            "content_strategy": "complete_story_arc",
            "original_prompt": original_prompt,
            "video_type": video_type,
            "estimated_complexity": "standard"
        }
    
    def _parse_segment_plan(self, plan_text: str, segmentation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the AI-generated plan into structured format"""
        try:
            # Extract key sections using simple text parsing
            sections = {
                "overall_strategy": "",
                "segment_outlines": [],
                "coordination_strategy": {},
                "quality_checkpoints": []
            }
            
            lines = plan_text.split('\n')
            current_section = None
            current_segment = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify section headers
                if line.startswith('OVERALL_STRATEGY:'):
                    current_section = 'overall_strategy'
                    sections['overall_strategy'] = line.replace('OVERALL_STRATEGY:', '').strip()
                elif line.startswith('SEGMENT_OUTLINES:'):
                    current_section = 'segment_outlines'
                elif line.startswith('COORDINATION_STRATEGY:'):
                    current_section = 'coordination_strategy'
                elif line.startswith('QUALITY_CHECKPOINTS:'):
                    current_section = 'quality_checkpoints'
                elif line.startswith('SEGMENT_'):
                    # New segment outline
                    if current_section == 'segment_outlines':
                        current_segment = {
                            "segment_number": len(sections['segment_outlines']) + 1,
                            "details": {}
                        }
                        sections['segment_outlines'].append(current_segment)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'segment_outlines' and current_segment:
                        self._parse_segment_detail(line, current_segment)
                    elif current_section == 'coordination_strategy':
                        self._parse_coordination_detail(line, sections['coordination_strategy'])
                    elif current_section == 'quality_checkpoints':
                        sections['quality_checkpoints'].append(line[1:].strip())
                elif current_section == 'overall_strategy' and not line.startswith(('SEGMENT_', 'COORDINATION_', 'QUALITY_')):
                    sections['overall_strategy'] += ' ' + line
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing segment plan: {str(e)}")
            # Return basic structure on parse failure
            return {
                "overall_strategy": "Multi-segment approach with coordinated content progression",
                "segment_outlines": [{"segment_number": i+1, "details": {}} for i in range(segmentation_plan.get('total_segments', 1))],
                "coordination_strategy": {},
                "quality_checkpoints": [],
                "parse_error": str(e)
            }
    
    def _parse_segment_detail(self, line: str, segment: Dict[str, Any]):
        """Parse individual segment detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                segment['details'][key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass
    
    def _parse_coordination_detail(self, line: str, coordination: Dict[str, Any]):
        """Parse coordination strategy detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                coordination[key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass


class SegmentCoordinator:
    """
    Coordinates segment generation and ensures consistency across segments
    """
    
    def __init__(self):
        self.coordination_context = {}
    
    def initialize_coordination(self, segment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize coordination context for segment generation
        
        Args:
            segment_plan: Complete segment plan from SegmentPlanner
            
        Returns:
            Coordination context for consistent generation
        """
        try:
            coordination_strategy = segment_plan.get('segment_plan', {}).get('coordination_strategy', {})
            
            self.coordination_context = {
                "character_consistency": coordination_strategy.get('character_consistency', 'Maintain consistent character personas and visual descriptions'),
                "visual_continuity": coordination_strategy.get('visual_continuity', 'Consistent lighting, color palette, and visual style'),
                "thematic_threads": coordination_strategy.get('thematic_threads', 'Core message and themes throughout'),
                "pacing_balance": coordination_strategy.get('pacing_balance', 'Balanced information density and engagement'),
                "engagement_distribution": coordination_strategy.get('engagement_distribution', 'Even distribution of high-engagement moments'),
                
                # Generated coordination elements
                "overall_tone": self._determine_overall_tone(segment_plan),
                "visual_style_guide": self._create_visual_style_guide(segment_plan),
                "narrative_thread": self._extract_narrative_thread(segment_plan),
                "quality_standards": segment_plan.get('segment_plan', {}).get('quality_checkpoints', [])
            }
            
            return self.coordination_context
            
        except Exception as e:
            logger.error(f"Error initializing coordination: {str(e)}")
            return {}
    
    def get_segment_context(self, segment_number: int, total_segments: int) -> Dict[str, Any]:
        """
        Get context for generating a specific segment
        
        Args:
            segment_number: Current segment number (1-indexed)
            total_segments: Total number of segments
            
        Returns:
            Context dictionary for this specific segment
        """
        try:
            return {
                "segment_position": {
                    "current": segment_number,
                    "total": total_segments,
                    "is_first": segment_number == 1,
                    "is_last": segment_number == total_segments,
                    "progress_percentage": round((segment_number - 1) / (total_segments - 1) * 100) if total_segments > 1 else 100
                },
                
                "coordination_requirements": self.coordination_context,
                
                "previous_segment_context": self._get_previous_context(segment_number) if segment_number > 1 else None,
                
                "next_segment_preparation": self._get_next_preparation(segment_number, total_segments) if segment_number < total_segments else None
            }
            
        except Exception as e:
            logger.error(f"Error getting segment context: {str(e)}")
            return {}
    
    def _determine_overall_tone(self, segment_plan: Dict[str, Any]) -> str:
        """Determine overall tone from segment plan"""
        video_type = segment_plan.get('video_type', 'general')
        
        tone_mapping = {
            'educational': 'informative and engaging',
            'marketing': 'persuasive and energetic', 
            'entertainment': 'entertaining and dynamic',
            'general': 'professional and engaging'
        }
        
        return tone_mapping.get(video_type, 'professional and engaging')
    
    def _create_visual_style_guide(self, segment_plan: Dict[str, Any]) -> Dict[str, str]:
        """Create visual style guide for consistency"""
        return {
            "lighting_style": "consistent soft natural lighting with warm tones",
            "color_palette": "professional color scheme with brand consistency",
            "composition_style": "cinematic framing with dynamic angles",
            "quality_standard": "high-quality commercial photography style"
        }
    
    def _extract_narrative_thread(self, segment_plan: Dict[str, Any]) -> str:
        """Extract main narrative thread from segment plan"""
        overall_strategy = segment_plan.get('segment_plan', {}).get('overall_strategy', '')
        return overall_strategy or "Progressive development of core theme with engaging storytelling"
    
    def _get_previous_context(self, segment_number: int) -> Dict[str, Any]:
        """Get context from previous segments (placeholder for future implementation)"""
        return {
            "note": f"Context from segments 1-{segment_number-1}",
            "implementation": "To be implemented in Phase 2"
        }
    
    def _get_next_preparation(self, segment_number: int, total_segments: int) -> Dict[str, Any]:
        """Prepare context for next segment (placeholder for future implementation)"""
        return {
            "note": f"Preparation for segment {segment_number+1} of {total_segments}",
            "implementation": "To be implemented in Phase 2"
        }


class AdvancedScriptGenerator:
    """
    Main class for advanced segmented script generation
    Combines SegmentationEngine, SegmentPlanner, and SegmentCoordinator
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.segmentation_engine = SegmentationEngine()
        self.segment_planner = SegmentPlanner(api_key)
        self.segment_coordinator = SegmentCoordinator()
    
    async def generate_advanced_script(self,
                                     prompt: str,
                                     video_type: str = "general",
                                     duration: str = "medium") -> Dict[str, Any]:
        """
        Main entry point for advanced script generation with segmentation
        
        Args:
            prompt: Original user prompt
            video_type: Type of video content
            duration: Target duration
            
        Returns:
            Complete script generation result with segmentation data
        """
        try:
            logger.info(f"Starting advanced script generation for duration: {duration}, type: {video_type}")
            
            # Phase 1: Calculate segmentation strategy
            segmentation_plan = self.segmentation_engine.calculate_segments(duration, video_type)
            logger.info(f"Segmentation plan: {segmentation_plan}")
            
            # Phase 2: Create detailed segment plan
            segment_plan = await self.segment_planner.create_segment_plan(prompt, segmentation_plan, video_type)
            logger.info(f"Segment plan created with {len(segment_plan.get('segment_plan', {}).get('segment_outlines', []))} segments")
            
            # Phase 3: Initialize coordination
            coordination_context = self.segment_coordinator.initialize_coordination(segment_plan)
            logger.info(f"Coordination context initialized")
            
            # Phase 4: Prepare for script generation (actual generation will be in Phase 2 of overall plan)
            generation_ready_context = {
                "segmentation_analysis": segmentation_plan,
                "segment_plan": segment_plan,
                "coordination_context": coordination_context,
                "ready_for_generation": True,
                "generation_strategy": "segmented" if segmentation_plan.get("requires_segmentation") else "single_pass"
            }
            
            return {
                "status": "success",
                "phase": "segmentation_complete",
                "original_prompt": prompt,
                "video_type": video_type,
                "duration": duration,
                "generation_context": generation_ready_context,
                "next_steps": "Ready for Phase 2: Segment Content Generation",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in advanced script generation: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "phase": "segmentation_failed"
            }
    
    def get_segment_generation_context(self, generation_context: Dict[str, Any], segment_number: int) -> Dict[str, Any]:
        """
        Get context for generating a specific segment (for Phase 2 implementation)
        
        Args:
            generation_context: Context from generate_advanced_script
            segment_number: Segment to generate (1-indexed)
            
        Returns:
            Context for generating this specific segment
        """
        try:
            segmentation_plan = generation_context.get("segmentation_analysis", {})
            total_segments = segmentation_plan.get("total_segments", 1)
            
            # Get segment-specific context
            segment_context = self.segment_coordinator.get_segment_context(segment_number, total_segments)
            
            # Get segment outline from plan
            segment_outlines = generation_context.get("segment_plan", {}).get("segment_plan", {}).get("segment_outlines", [])
            current_segment_outline = None
            if segment_number <= len(segment_outlines):
                current_segment_outline = segment_outlines[segment_number - 1]
            
            return {
                "segment_number": segment_number,
                "total_segments": total_segments,
                "segment_context": segment_context,
                "segment_outline": current_segment_outline,
                "coordination_requirements": generation_context.get("coordination_context", {}),
                "ready_for_content_generation": True
            }
            
        except Exception as e:
            logger.error(f"Error getting segment generation context: {str(e)}")
            return {"error": str(e)}
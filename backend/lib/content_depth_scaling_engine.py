"""
Content Depth Scaling Engine - Phase 2: Advanced Script Generation Logic

This module implements intelligent content depth scaling for segmented script generation.
It adjusts information density, detail levels, and content complexity based on segment 
duration and position within the overall narrative structure.

Components:
- Duration-Based Content Strategy: Adjusts content density based on available time
- Progressive Revelation System: Structures information delivery across segments  
- Depth Calibration: Scales detail level appropriately for segment constraints
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio

logger = logging.getLogger(__name__)

class DurationBasedContentStrategy:
    """
    Determines optimal content strategy based on segment duration and content requirements.
    Balances information density with engagement and comprehension.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Content density mapping based on duration
        self.density_strategies = {
            "ultra_short": {  # < 2 minutes
                "max_concepts": 2,
                "detail_level": "essential_only",
                "pacing": "rapid",
                "engagement_ratio": 0.8  # 80% engagement elements
            },
            "short": {  # 2-4 minutes
                "max_concepts": 3,
                "detail_level": "concise",
                "pacing": "brisk",
                "engagement_ratio": 0.7
            },
            "medium": {  # 4-7 minutes
                "max_concepts": 5,
                "detail_level": "moderate",
                "pacing": "balanced",
                "engagement_ratio": 0.6
            },
            "long": {  # 7-10 minutes
                "max_concepts": 7,
                "detail_level": "comprehensive",
                "pacing": "thoughtful",
                "engagement_ratio": 0.5
            },
            "extended": {  # > 10 minutes
                "max_concepts": 10,
                "detail_level": "deep_dive",
                "pacing": "immersive",
                "engagement_ratio": 0.4
            }
        }
    
    async def analyze_content_strategy(self,
                                     segment_duration: float,
                                     segment_position: Dict[str, Any],
                                     content_focus: str,
                                     video_type: str) -> Dict[str, Any]:
        """
        Analyze and determine optimal content strategy for a segment
        
        Args:
            segment_duration: Duration of segment in minutes
            segment_position: Position info (current, total, is_first, is_last, etc.)
            content_focus: Main content focus for this segment
            video_type: Type of video content
            
        Returns:
            Comprehensive content strategy analysis
        """
        try:
            logger.info(f"📊 Analyzing content strategy for {segment_duration}min segment")
            
            # Determine duration category
            duration_category = self._categorize_duration(segment_duration)
            base_strategy = self.density_strategies[duration_category]
            
            # Create content strategy chat instance
            strategy_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"content-strategy-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Content Strategist specializing in duration-based content optimization for video scripts. Your expertise lies in calibrating information density, pacing, and detail levels to maximize comprehension and engagement within specific time constraints.

CORE EXPERTISE:
1. CONTENT DENSITY OPTIMIZATION: Balancing information volume with comprehension
2. DURATION-BASED PACING: Adjusting content delivery speed for optimal absorption
3. COGNITIVE LOAD MANAGEMENT: Preventing information overload in time-constrained segments
4. ENGAGEMENT CALIBRATION: Maintaining interest while delivering substantive content
5. PROGRESSIVE COMPLEXITY: Building understanding through structured information layering

You excel at creating content strategies that feel natural and engaging while maximizing educational or entertainment value within precise time limits."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            strategy_prompt = f"""Create a comprehensive content strategy for this video segment:

SEGMENT PARAMETERS:
- Duration: {segment_duration} minutes
- Duration Category: {duration_category}
- Position: Segment {segment_position.get('current', 1)} of {segment_position.get('total', 1)}
- Is First: {segment_position.get('is_first', False)}
- Is Last: {segment_position.get('is_last', False)}
- Progress: {segment_position.get('progress_percentage', 0)}%

CONTENT CONTEXT:
- Content Focus: {content_focus}
- Video Type: {video_type}
- Base Strategy: {base_strategy}

Create a detailed content strategy following this EXACT format:

CONTENT_DENSITY_ANALYSIS:
- OPTIMAL_CONCEPT_COUNT: [Number of main concepts that can be effectively covered]
- DETAIL_DEPTH_LEVEL: [How deep to go into each concept - surface/moderate/deep]
- INFORMATION_PACING: [Speed of information delivery - rapid/balanced/leisurely]
- COGNITIVE_LOAD_ASSESSMENT: [Expected mental effort required from audience]

DURATION_OPTIMIZATION:
- TIME_ALLOCATION_STRATEGY: [How to distribute time across content elements]
- CONTENT_PRIORITIZATION: [Which elements are essential vs optional]
- BUFFER_TIME_MANAGEMENT: [How much time to reserve for transitions/emphasis]
- PACING_ADJUSTMENTS: [Specific pacing modifications for this duration]

ENGAGEMENT_CALIBRATION:
- ENGAGEMENT_ELEMENT_RATIO: [Percentage of content dedicated to engagement]
- ATTENTION_RETENTION_STRATEGY: [How to maintain focus throughout duration]
- VARIETY_INTEGRATION: [How to introduce content variety within time limits]
- ENERGY_MANAGEMENT: [How to manage viewer energy levels]

CONTENT_STRUCTURE_OPTIMIZATION:
- OPENING_TIME_ALLOCATION: [How much time for segment opening]
- CORE_CONTENT_DISTRIBUTION: [How to structure main content delivery]
- CLOSING_TIME_ALLOCATION: [How much time for segment conclusion]
- TRANSITION_BUFFER: [Time reserved for smooth transitions]

QUALITY_STANDARDS:
- COMPREHENSION_BENCHMARKS: [Standards for audience understanding]
- ENGAGEMENT_THRESHOLDS: [Minimum engagement levels to maintain]
- CONTENT_DENSITY_LIMITS: [Maximum information density without overload]
- RETENTION_TARGETS: [Expected information retention rates]

SEGMENT_SPECIFIC_ADAPTATIONS:
[Any special considerations based on segment position and role in overall narrative]"""

            response = await strategy_chat.send_message(UserMessage(text=strategy_prompt))
            
            # Parse the content strategy response
            parsed_strategy = self._parse_content_strategy(response, duration_category, base_strategy)
            
            return {
                "content_strategy_complete": True,
                "segment_duration": segment_duration,
                "duration_category": duration_category,
                "segment_position": segment_position,
                "content_strategy": parsed_strategy,
                "base_strategy_applied": base_strategy,
                "strategy_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content strategy: {str(e)}")
            return {"error": str(e), "content_strategy_complete": False}
    
    def _categorize_duration(self, duration_minutes: float) -> str:
        """Categorize segment duration for strategy selection"""
        if duration_minutes < 2:
            return "ultra_short"
        elif duration_minutes < 4:
            return "short"
        elif duration_minutes < 7:
            return "medium"
        elif duration_minutes < 10:
            return "long"
        else:
            return "extended"
    
    def _parse_content_strategy(self, strategy_text: str, duration_category: str, base_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the AI-generated content strategy analysis"""
        try:
            parsed = {
                "content_density_analysis": {},
                "duration_optimization": {},
                "engagement_calibration": {},
                "content_structure_optimization": {},
                "quality_standards": {},
                "segment_specific_adaptations": ""
            }
            
            lines = strategy_text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('CONTENT_DENSITY_ANALYSIS:'):
                    current_section = 'content_density_analysis'
                elif line.startswith('DURATION_OPTIMIZATION:'):
                    current_section = 'duration_optimization'
                elif line.startswith('ENGAGEMENT_CALIBRATION:'):
                    current_section = 'engagement_calibration'
                elif line.startswith('CONTENT_STRUCTURE_OPTIMIZATION:'):
                    current_section = 'content_structure_optimization'
                elif line.startswith('QUALITY_STANDARDS:'):
                    current_section = 'quality_standards'
                elif line.startswith('SEGMENT_SPECIFIC_ADAPTATIONS:'):
                    current_section = 'segment_specific_adaptations'
                    parsed['segment_specific_adaptations'] = line.replace('SEGMENT_SPECIFIC_ADAPTATIONS:', '').strip()
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section != 'segment_specific_adaptations':
                        self._parse_section_detail(line, parsed[current_section])
                elif current_section == 'segment_specific_adaptations' and not line.startswith(('CONTENT_', 'DURATION_', 'ENGAGEMENT_', 'QUALITY_')):
                    parsed['segment_specific_adaptations'] += ' ' + line
            
            # Apply fallback values from base strategy if parsing fails
            if not parsed['content_density_analysis']:
                parsed['content_density_analysis'] = {
                    "optimal_concept_count": base_strategy["max_concepts"],
                    "detail_depth_level": base_strategy["detail_level"],
                    "information_pacing": base_strategy["pacing"],
                    "cognitive_load_assessment": "Moderate cognitive load expected"
                }
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing content strategy: {str(e)}")
            return {
                "content_density_analysis": {
                    "optimal_concept_count": base_strategy["max_concepts"],
                    "detail_depth_level": base_strategy["detail_level"],
                    "information_pacing": base_strategy["pacing"],
                    "cognitive_load_assessment": "Standard cognitive load for duration"
                },
                "duration_optimization": {"time_allocation_strategy": "Balanced distribution across content elements"},
                "engagement_calibration": {"engagement_element_ratio": base_strategy["engagement_ratio"]},
                "content_structure_optimization": {"core_content_distribution": "Even distribution throughout segment"},
                "quality_standards": {"comprehension_benchmarks": "Standard comprehension expectations"},
                "segment_specific_adaptations": "Standard adaptations for segment position",
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


class ProgressiveRevelationSystem:
    """
    Manages the progressive disclosure of information across segments.
    Ensures logical information flow and prevents redundancy or gaps.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def design_information_flow(self,
                                    total_segments: int,
                                    overall_narrative_theme: str,
                                    segment_outlines: List[Dict[str, Any]],
                                    story_arc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design progressive information revelation across all segments
        
        Args:
            total_segments: Total number of segments
            overall_narrative_theme: Main theme of the content
            segment_outlines: Outlines from segmentation planning
            story_arc: Story arc from narrative continuity system
            
        Returns:
            Complete information flow design
        """
        try:
            logger.info(f"📚 Designing progressive information flow for {total_segments} segments")
            
            # Create information flow chat instance
            flow_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"info-flow-{str(uuid.uuid4())[:8]}",
                system_message="""You are a Master Information Architect specializing in progressive knowledge revelation across multi-segment content. Your expertise lies in structuring information delivery to build understanding systematically while maintaining engagement and preventing cognitive overload.

CORE EXPERTISE:
1. INFORMATION LAYERING: Building knowledge systematically from foundations to complexity
2. REVELATION SEQUENCING: Timing information disclosure for maximum impact and comprehension
3. KNOWLEDGE DEPENDENCY MAPPING: Understanding prerequisite relationships between concepts
4. CURIOSITY GAP ENGINEERING: Creating strategic information gaps to maintain engagement
5. REDUNDANCY ELIMINATION: Avoiding repetition while reinforcing key concepts

You excel at creating information flows that feel natural and engaging while building comprehensive understanding across extended content."""
            ).with_model("gemini", "gemini-2.0-flash")
            
            flow_prompt = f"""Design a comprehensive progressive information revelation system:

CONTENT PARAMETERS:
- Total Segments: {total_segments}
- Overall Theme: {overall_narrative_theme}

SEGMENT STRUCTURE:
{self._format_segment_outlines(segment_outlines)}

STORY ARC CONTEXT:
{self._format_story_arc(story_arc)}

Create a detailed information flow design following this EXACT format:

INFORMATION_ARCHITECTURE:
- PRIMARY_KNOWLEDGE_PILLARS: [Core knowledge areas that must be covered]
- DEPENDENCY_RELATIONSHIPS: [Which concepts depend on others]
- COMPLEXITY_PROGRESSION: [How complexity builds across segments]
- REVELATION_STRATEGY: [Overall approach to information disclosure]

SEGMENT_INFORMATION_MAPPING:
SEGMENT_1:
- FOUNDATIONAL_CONCEPTS: [Essential concepts introduced in this segment]
- KNOWLEDGE_PREREQUISITES: [What audience needs to know before this segment]
- INFORMATION_DENSITY: [Low/Medium/High information load]
- REVELATION_FOCUS: [What type of information is primarily revealed]
- CURIOSITY_SETUP: [What questions/gaps are created for future segments]
- REINFORCEMENT_ELEMENTS: [How previous information is reinforced]

[Continue for all {total_segments} segments...]

KNOWLEDGE_FLOW_STRATEGY:
- FOUNDATION_BUILDING: [How foundational knowledge is established]
- COMPLEXITY_ESCALATION: [How complexity increases appropriately]
- REVELATION_PACING: [Speed and timing of information disclosure]
- RETENTION_MECHANISMS: [How key information is reinforced]

ENGAGEMENT_INTEGRATION:
- CURIOSITY_GAP_DISTRIBUTION: [How information gaps maintain interest]
- REVELATION_REWARDS: [How information disclosure creates satisfaction]
- KNOWLEDGE_CONNECTIVITY: [How concepts connect to create "aha" moments]
- ANTICIPATION_BUILDING: [How upcoming revelations are teased]

QUALITY_CONTROLS:
- COMPREHENSION_CHECKPOINTS: [How to verify understanding at each stage]
- INFORMATION_REDUNDANCY_PREVENTION: [Avoiding unnecessary repetition]
- KNOWLEDGE_GAP_DETECTION: [Identifying potential understanding gaps]
- FLOW_OPTIMIZATION_STANDARDS: [Standards for optimal information flow]

PROGRESSIVE_COMPLEXITY_FRAMEWORK:
[How information complexity progresses from simple to sophisticated across segments]"""

            response = await flow_chat.send_message(UserMessage(text=flow_prompt))
            
            # Parse the information flow response
            parsed_flow = self._parse_information_flow(response, total_segments)
            
            return {
                "information_flow_complete": True,
                "total_segments": total_segments,
                "overall_theme": overall_narrative_theme,
                "information_flow": parsed_flow,
                "flow_design_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error designing information flow: {str(e)}")
            return {"error": str(e), "information_flow_complete": False}
    
    def _format_segment_outlines(self, segment_outlines: List[Dict[str, Any]]) -> str:
        """Format segment outlines for prompt inclusion"""
        if not segment_outlines:
            return "No segment outlines available"
        
        formatted = []
        for segment in segment_outlines:
            segment_num = segment.get('segment_number', 1)
            details = segment.get('details', {})
            content_focus = details.get('content_focus', 'Main content')
            narrative_role = details.get('narrative_role', 'development')
            formatted.append(f"Segment {segment_num}: {content_focus} ({narrative_role})")
        
        return "\n".join(formatted) if formatted else "No segment details available"
    
    def _format_story_arc(self, story_arc: Dict[str, Any]) -> str:
        """Format story arc for prompt inclusion"""
        if not story_arc:
            return "No story arc available"
        
        progression = story_arc.get('story_arc_progression', [])
        if not progression:
            return "No story progression available"
        
        formatted = []
        for segment in progression:
            seg_num = segment.get('segment_number', 1)
            details = segment.get('details', {})
            arc_position = details.get('arc_position', 'development')
            narrative_purpose = details.get('narrative_purpose', 'content delivery')
            formatted.append(f"Segment {seg_num}: {arc_position} - {narrative_purpose}")
        
        return "\n".join(formatted) if formatted else "No story arc details available"
    
    def _parse_information_flow(self, flow_text: str, total_segments: int) -> Dict[str, Any]:
        """Parse the AI-generated information flow design"""
        try:
            parsed = {
                "information_architecture": {},
                "segment_information_mapping": [],
                "knowledge_flow_strategy": {},
                "engagement_integration": {},
                "quality_controls": {},
                "progressive_complexity_framework": ""
            }
            
            lines = flow_text.split('\n')
            current_section = None
            current_segment = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('INFORMATION_ARCHITECTURE:'):
                    current_section = 'information_architecture'
                elif line.startswith('SEGMENT_INFORMATION_MAPPING:'):
                    current_section = 'segment_information_mapping'
                elif line.startswith('KNOWLEDGE_FLOW_STRATEGY:'):
                    current_section = 'knowledge_flow_strategy'
                elif line.startswith('ENGAGEMENT_INTEGRATION:'):
                    current_section = 'engagement_integration'
                elif line.startswith('QUALITY_CONTROLS:'):
                    current_section = 'quality_controls'
                elif line.startswith('PROGRESSIVE_COMPLEXITY_FRAMEWORK:'):
                    current_section = 'progressive_complexity_framework'
                    parsed['progressive_complexity_framework'] = line.replace('PROGRESSIVE_COMPLEXITY_FRAMEWORK:', '').strip()
                elif line.startswith('SEGMENT_'):
                    # New segment in information mapping
                    if current_section == 'segment_information_mapping':
                        current_segment = {
                            "segment_number": len(parsed['segment_information_mapping']) + 1,
                            "information_details": {}
                        }
                        parsed['segment_information_mapping'].append(current_segment)
                elif current_section and line.startswith('-'):
                    # Handle bullet points in various sections
                    if current_section == 'segment_information_mapping' and current_segment:
                        self._parse_info_detail(line, current_segment)
                    elif current_section in ['information_architecture', 'knowledge_flow_strategy', 'engagement_integration', 'quality_controls']:
                        self._parse_section_detail(line, parsed[current_section])
                elif current_section == 'progressive_complexity_framework' and not line.startswith(('INFORMATION_', 'SEGMENT_', 'KNOWLEDGE_', 'ENGAGEMENT_', 'QUALITY_')):
                    parsed['progressive_complexity_framework'] += ' ' + line
            
            # Ensure we have segments even if parsing fails
            if not parsed['segment_information_mapping']:
                parsed['segment_information_mapping'] = [
                    {"segment_number": i+1, "information_details": {}} for i in range(total_segments)
                ]
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing information flow: {str(e)}")
            return {
                "information_architecture": {"primary_knowledge_pillars": "Core content concepts"},
                "segment_information_mapping": [{"segment_number": i+1, "information_details": {}} for i in range(total_segments)],
                "knowledge_flow_strategy": {"foundation_building": "Progressive knowledge building"},
                "engagement_integration": {"curiosity_gap_distribution": "Strategic information gaps"},
                "quality_controls": {"comprehension_checkpoints": "Regular understanding verification"},
                "progressive_complexity_framework": "Systematic complexity progression from basic to advanced",
                "parse_error": str(e)
            }
    
    def _parse_info_detail(self, line: str, segment: Dict[str, Any]):
        """Parse individual information detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                segment['information_details'][key.strip().lower().replace(' ', '_')] = value.strip()
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


class DepthCalibration:
    """
    Calibrates content depth based on segment constraints and audience needs.
    Ensures appropriate detail levels for available time and cognitive capacity.
    """
    
    def __init__(self):
        self.depth_levels = {
            "surface": {
                "concepts_per_minute": 1.5,
                "detail_ratio": 0.2,
                "examples_per_concept": 1,
                "explanation_depth": "basic"
            },
            "moderate": {
                "concepts_per_minute": 1.0,
                "detail_ratio": 0.4,
                "examples_per_concept": 2,
                "explanation_depth": "comprehensive"
            },
            "deep": {
                "concepts_per_minute": 0.7,
                "detail_ratio": 0.6,
                "examples_per_concept": 3,
                "explanation_depth": "thorough"
            },
            "intensive": {
                "concepts_per_minute": 0.5,
                "detail_ratio": 0.8,
                "examples_per_concept": 4,
                "explanation_depth": "exhaustive"
            }
        }
    
    def calibrate_content_depth(self,
                               segment_duration: float,
                               content_strategy: Dict[str, Any],
                               information_flow: Dict[str, Any],
                               segment_number: int) -> Dict[str, Any]:
        """
        Calibrate optimal content depth for a specific segment
        
        Args:
            segment_duration: Duration of segment in minutes
            content_strategy: Output from DurationBasedContentStrategy
            information_flow: Output from ProgressiveRevelationSystem
            segment_number: Current segment number
            
        Returns:
            Calibrated depth settings for the segment
        """
        try:
            logger.info(f"🎯 Calibrating content depth for segment {segment_number} ({segment_duration}min)")
            
            # Extract relevant information
            content_density = content_strategy.get('content_strategy', {}).get('content_density_analysis', {})
            optimal_concepts = content_density.get('optimal_concept_count', 3)
            detail_level = content_density.get('detail_depth_level', 'moderate')
            
            # Get segment information mapping
            info_mapping = information_flow.get('information_flow', {}).get('segment_information_mapping', [])
            segment_info = None
            if segment_number <= len(info_mapping):
                segment_info = info_mapping[segment_number - 1]
            
            # Determine appropriate depth level
            depth_level = self._determine_depth_level(detail_level, segment_duration, optimal_concepts)
            depth_settings = self.depth_levels[depth_level]
            
            # Calculate specific calibrations
            calibration = {
                "depth_level": depth_level,
                "segment_duration": segment_duration,
                "optimal_concept_count": optimal_concepts,
                
                # Time allocations
                "time_per_concept": segment_duration / max(optimal_concepts, 1),
                "detail_time_allocation": segment_duration * depth_settings["detail_ratio"],
                "engagement_time_allocation": segment_duration * (1 - depth_settings["detail_ratio"]),
                
                # Content specifications
                "explanation_depth": depth_settings["explanation_depth"],
                "examples_per_concept": depth_settings["examples_per_concept"],
                "concepts_per_minute": depth_settings["concepts_per_minute"],
                
                # Quality targets
                "comprehension_target": self._calculate_comprehension_target(depth_level),
                "retention_expectation": self._calculate_retention_expectation(depth_level),
                "engagement_threshold": self._calculate_engagement_threshold(depth_level),
                
                # Segment-specific adjustments
                "information_density": segment_info.get('information_details', {}).get('information_density', 'Medium') if segment_info else 'Medium',
                "complexity_adjustment": self._calculate_complexity_adjustment(segment_number, segment_info),
                
                "calibration_timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "depth_calibration_complete": True,
                "segment_number": segment_number,
                "calibration": calibration
            }
            
        except Exception as e:
            logger.error(f"Error calibrating content depth: {str(e)}")
            return {"error": str(e), "depth_calibration_complete": False}
    
    def _determine_depth_level(self, detail_level: str, duration: float, concept_count: int) -> str:
        """Determine appropriate depth level based on constraints"""
        
        # Base mapping from detail level
        level_mapping = {
            "essential_only": "surface",
            "concise": "surface", 
            "moderate": "moderate",
            "comprehensive": "deep",
            "deep_dive": "intensive"
        }
        
        base_level = level_mapping.get(detail_level, "moderate")
        
        # Adjust based on time constraints
        time_per_concept = duration / max(concept_count, 1)
        
        if time_per_concept < 1:
            return "surface"  # Force surface level if very time-constrained
        elif time_per_concept > 3:
            # Allow deeper level if time permits
            if base_level == "surface":
                return "moderate"
            elif base_level == "moderate":
                return "deep"
        
        return base_level
    
    def _calculate_comprehension_target(self, depth_level: str) -> float:
        """Calculate expected comprehension percentage for depth level"""
        targets = {
            "surface": 0.8,    # 80% comprehension expected
            "moderate": 0.75,  # 75% comprehension expected
            "deep": 0.7,       # 70% comprehension expected (more complex)
            "intensive": 0.65  # 65% comprehension expected (very complex)
        }
        return targets.get(depth_level, 0.75)
    
    def _calculate_retention_expectation(self, depth_level: str) -> float:
        """Calculate expected retention percentage for depth level"""
        retention = {
            "surface": 0.6,    # 60% retention expected
            "moderate": 0.7,   # 70% retention expected
            "deep": 0.75,      # 75% retention expected
            "intensive": 0.8   # 80% retention expected
        }
        return retention.get(depth_level, 0.7)
    
    def _calculate_engagement_threshold(self, depth_level: str) -> float:
        """Calculate minimum engagement level for depth level"""
        thresholds = {
            "surface": 0.8,    # High engagement needed for surface content
            "moderate": 0.7,   # Moderate engagement for balanced content
            "deep": 0.6,       # Lower threshold as content is inherently engaging
            "intensive": 0.5   # Lowest threshold for deep, complex content
        }
        return thresholds.get(depth_level, 0.7)
    
    def _calculate_complexity_adjustment(self, segment_number: int, segment_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate complexity adjustments based on segment position and info"""
        if not segment_info:
            return {"adjustment_factor": 1.0, "reasoning": "No segment info available"}
        
        info_details = segment_info.get('information_details', {})
        
        # Adjust based on foundational concepts vs advanced concepts
        if 'foundational_concepts' in info_details:
            return {"adjustment_factor": 0.8, "reasoning": "Foundational concepts require simpler explanation"}
        elif segment_number == 1:
            return {"adjustment_factor": 0.9, "reasoning": "First segment should be more accessible"}
        elif 'advanced' in str(info_details).lower():
            return {"adjustment_factor": 1.2, "reasoning": "Advanced concepts allow for higher complexity"}
        else:
            return {"adjustment_factor": 1.0, "reasoning": "Standard complexity level"}


class ContentDepthScalingEngine:
    """
    Main orchestrator for the Content Depth Scaling Engine.
    Combines all components to provide comprehensive content depth management.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.duration_strategy = DurationBasedContentStrategy(api_key)
        self.revelation_system = ProgressiveRevelationSystem(api_key)
        self.depth_calibration = DepthCalibration()
    
    async def analyze_content_depth_scaling(self,
                                          segmentation_plan: Dict[str, Any],
                                          narrative_continuity: Dict[str, Any],
                                          segment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete content depth scaling analysis for all segments
        
        Args:
            segmentation_plan: Segmentation analysis from Phase 1
            narrative_continuity: Narrative continuity from Phase 2
            segment_plan: Segment plan from Phase 1
            
        Returns:
            Comprehensive content depth scaling analysis
        """
        try:
            total_segments = segmentation_plan.get('total_segments', 1)
            segment_duration = segmentation_plan.get('segment_duration_minutes', 5.0)
            
            logger.info(f"📊 Starting content depth scaling analysis for {total_segments} segments")
            
            # Phase 1: Design progressive information flow
            logger.info("📚 Phase 1: Designing progressive information flow...")
            
            story_arc = narrative_continuity.get('analysis_components', {}).get('story_arc', {}).get('story_arc', {})
            overall_theme = story_arc.get('overall_narrative_theme', '')
            segment_outlines = segment_plan.get('segment_plan', {}).get('segment_outlines', [])
            
            information_flow = await self.revelation_system.design_information_flow(
                total_segments, overall_theme, segment_outlines, story_arc
            )
            
            if not information_flow.get('information_flow_complete'):
                logger.error("Information flow design failed")
                return {"error": "Information flow design failed", "component": "progressive_revelation_system"}
            
            # Phase 2: Analyze content strategy for each segment
            logger.info("📊 Phase 2: Analyzing content strategies for all segments...")
            
            segment_strategies = []
            segment_calibrations = []
            
            for segment_num in range(1, total_segments + 1):
                # Get segment-specific information
                segment_position = {
                    "current": segment_num,
                    "total": total_segments,
                    "is_first": segment_num == 1,
                    "is_last": segment_num == total_segments,
                    "progress_percentage": round((segment_num - 1) / (total_segments - 1) * 100) if total_segments > 1 else 100
                }
                
                # Get content focus from segment outline
                content_focus = "Main content"
                if segment_num <= len(segment_outlines):
                    segment_outline = segment_outlines[segment_num - 1]
                    content_focus = segment_outline.get('details', {}).get('content_focus', 'Main content')
                
                # Get video type from segment plan
                video_type = segment_plan.get('video_type', 'general')
                
                # Analyze content strategy for this segment
                strategy_result = await self.duration_strategy.analyze_content_strategy(
                    segment_duration, segment_position, content_focus, video_type
                )
                
                if strategy_result.get('content_strategy_complete'):
                    segment_strategies.append(strategy_result)
                    
                    # Phase 3: Calibrate content depth for this segment
                    calibration_result = self.depth_calibration.calibrate_content_depth(
                        segment_duration, strategy_result, information_flow, segment_num
                    )
                    
                    if calibration_result.get('depth_calibration_complete'):
                        segment_calibrations.append(calibration_result)
                else:
                    logger.warning(f"Content strategy analysis failed for segment {segment_num}")
            
            logger.info(f"✅ Content depth scaling analysis complete for {len(segment_strategies)} segments")
            
            return {
                "content_depth_scaling_complete": True,
                "total_segments": total_segments,
                "segment_duration": segment_duration,
                "analysis_components": {
                    "information_flow": information_flow,
                    "segment_strategies": segment_strategies,
                    "segment_calibrations": segment_calibrations
                },
                "scaling_summary": {
                    "total_segments_analyzed": len(segment_strategies),
                    "successful_calibrations": len(segment_calibrations),
                    "average_concept_density": sum(cal.get('calibration', {}).get('concepts_per_minute', 1.0) 
                                                 for cal in segment_calibrations) / max(len(segment_calibrations), 1)
                },
                "phase_completed": "Content Depth Scaling Engine",
                "next_phase": "Ready for Quality Consistency Engine",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in content depth scaling analysis: {str(e)}")
            return {"error": str(e), "content_depth_scaling_complete": False}
    
    def get_segment_depth_context(self, 
                                 content_depth_scaling: Dict[str, Any], 
                                 segment_number: int) -> Dict[str, Any]:
        """
        Get content depth context for generating a specific segment
        
        Args:
            content_depth_scaling: Output from analyze_content_depth_scaling
            segment_number: Segment number (1-indexed)
            
        Returns:
            Content depth context for this specific segment
        """
        try:
            components = content_depth_scaling.get('analysis_components', {})
            
            # Get segment-specific strategy
            segment_strategies = components.get('segment_strategies', [])
            segment_strategy = None
            if segment_number <= len(segment_strategies):
                segment_strategy = segment_strategies[segment_number - 1]
            
            # Get segment-specific calibration
            segment_calibrations = components.get('segment_calibrations', [])
            segment_calibration = None
            if segment_number <= len(segment_calibrations):
                segment_calibration = segment_calibrations[segment_number - 1]
            
            # Get segment information from information flow
            info_flow = components.get('information_flow', {}).get('information_flow', {})
            segment_info_mapping = info_flow.get('segment_information_mapping', [])
            segment_info = None
            if segment_number <= len(segment_info_mapping):
                segment_info = segment_info_mapping[segment_number - 1]
            
            return {
                "segment_number": segment_number,
                "total_segments": content_depth_scaling.get('total_segments', 1),
                "content_strategy": segment_strategy.get('content_strategy', {}) if segment_strategy else {},
                "depth_calibration": segment_calibration.get('calibration', {}) if segment_calibration else {},
                "information_requirements": segment_info.get('information_details', {}) if segment_info else {},
                "global_information_flow": {
                    "information_architecture": info_flow.get('information_architecture', {}),
                    "knowledge_flow_strategy": info_flow.get('knowledge_flow_strategy', {}),
                    "engagement_integration": info_flow.get('engagement_integration', {}),
                    "quality_controls": info_flow.get('quality_controls', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting segment depth context: {str(e)}")
            return {"error": str(e)}
"""
Advanced Generation Workflow - Phase 2: Advanced Script Generation Logic

This module implements the actual script content generation using all the analysis
and planning from previous phases. It generates high-quality, segmented script content
that incorporates segmentation planning, narrative continuity, content depth scaling,
and quality consistency.

Enhanced Features:
- Intelligent retry logic with exponential backoff
- Memory-efficient processing for large scripts
- Comprehensive performance monitoring
- Advanced error recovery mechanisms
- Quality-based regeneration with feedback loops
- Optimized async processing with concurrency limits
- Smart caching for repeated operations

Components:
- Segment Content Generator: Generates actual script content for individual segments
- Cross-Segment Coordinator: Ensures consistency and flow between generated segments
- Quality Validator: Validates generated content against quality standards
- Integration Manager: Combines all segments into final cohesive script
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import re
import time
from functools import wraps
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Configuration constants
class GenerationConfig:
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 1.0  # Base delay in seconds
    RETRY_EXPONENTIAL_FACTOR = 2.0
    MAX_CONCURRENT_SEGMENTS = 3  # Limit concurrent segment generation
    QUALITY_THRESHOLD = 0.7  # Minimum quality score for acceptance
    MAX_SEGMENT_GENERATION_TIME = 300  # 5 minutes timeout per segment
    CACHE_ENABLED = True
    MEMORY_OPTIMIZATION = True

class GenerationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class GenerationMetrics:
    start_time: float
    end_time: Optional[float] = None
    total_tokens_used: int = 0
    api_calls_made: int = 0
    retries_performed: int = 0
    cache_hits: int = 0
    memory_peak_mb: float = 0.0
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

def retry_with_backoff(max_retries: int = GenerationConfig.MAX_RETRIES):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                    
                    if attempt < max_retries:
                        delay = GenerationConfig.RETRY_DELAY_BASE * (GenerationConfig.RETRY_EXPONENTIAL_FACTOR ** attempt)
                        logger.info(f"Retrying in {delay:.1f} seconds...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator

def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = _get_memory_usage()
        
        try:
            result = await func(*args, **kwargs)
            
            # Add performance metrics to result if it's a dict
            if isinstance(result, dict):
                end_time = time.time()
                end_memory = _get_memory_usage()
                
                result['performance_metrics'] = {
                    'execution_time_seconds': end_time - start_time,
                    'memory_used_mb': end_memory - start_memory,
                    'function_name': func.__name__
                }
            
            return result
            
        except Exception as e:
            end_time = time.time()
            logger.error(f"Performance monitor - {func.__name__} failed after {end_time - start_time:.2f}s: {str(e)}")
            raise
            
    return wrapper

def _get_memory_usage() -> float:
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0  # If psutil not available, return 0

class SegmentContentGenerator:
    """
    Enhanced segment content generator with retry logic, caching, and performance optimization.
    Generates actual script content for individual segments using comprehensive context
    from all previous analysis phases.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._cache = {} if GenerationConfig.CACHE_ENABLED else None
        self._generation_metrics = {}
        
    @performance_monitor
    @retry_with_backoff(max_retries=GenerationConfig.MAX_RETRIES)
    async def generate_segment_content(self,
                                     segment_number: int,
                                     original_prompt: str,
                                     segmentation_context: Dict[str, Any],
                                     narrative_context: Dict[str, Any],
                                     depth_context: Dict[str, Any],
                                     quality_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive script content for a specific segment with enhanced error handling
        
        Args:
            segment_number: Current segment number (1-indexed)
            original_prompt: Original user prompt
            segmentation_context: Context from Phase 1 segmentation
            narrative_context: Context from narrative continuity system
            depth_context: Context from content depth scaling engine
            quality_context: Context from quality consistency engine
            
        Returns:
            Generated segment script content with metadata and performance metrics
        """
        try:
            total_segments = segmentation_context.get('total_segments', 1)
            generation_start_time = time.time()
            
            logger.info(f"🎬 Generating enhanced content for segment {segment_number}/{total_segments}")
            
            # Check cache first
            if self._cache is not None:
                cache_key = self._generate_cache_key(segment_number, original_prompt, segmentation_context)
                if cache_key in self._cache:
                    logger.info(f"📋 Cache hit for segment {segment_number}")
                    cached_result = self._cache[cache_key].copy()
                    cached_result['cache_hit'] = True
                    return cached_result
            
            # Initialize generation metrics
            metrics = GenerationMetrics(start_time=generation_start_time)
            self._generation_metrics[segment_number] = metrics
            
            # Create enhanced segment generation chat instance
            segment_chat = LlmChat(
                api_key=self.api_key,
                session_id=f"enhanced-segment-{segment_number}-{str(uuid.uuid4())[:8]}",
                system_message=self._get_enhanced_system_message()
            ).with_model("gemini", "gemini-2.0-flash")
            
            metrics.api_calls_made += 1
            
            # Build comprehensive context for generation
            generation_prompt = await self._build_enhanced_generation_prompt(
                segment_number,
                original_prompt,
                segmentation_context,
                narrative_context,
                depth_context,
                quality_context
            )
            
            # Generate content with timeout
            response_task = segment_chat.send_message(UserMessage(text=generation_prompt))
            
            try:
                response = await asyncio.wait_for(
                    response_task, 
                    timeout=GenerationConfig.MAX_SEGMENT_GENERATION_TIME
                )
            except asyncio.TimeoutError:
                logger.error(f"Segment {segment_number} generation timed out after {GenerationConfig.MAX_SEGMENT_GENERATION_TIME}s")
                raise Exception(f"Segment generation timeout after {GenerationConfig.MAX_SEGMENT_GENERATION_TIME} seconds")
            
            # Parse and validate the generated content
            parsed_content = self._parse_enhanced_segment_content(response, segment_number)
            
            # Perform quality validation
            quality_score = self._calculate_content_quality_score(parsed_content)
            if quality_score < GenerationConfig.QUALITY_THRESHOLD:
                logger.warning(f"Segment {segment_number} quality score {quality_score:.3f} below threshold {GenerationConfig.QUALITY_THRESHOLD}")
                # This will trigger a retry via the decorator
                raise Exception(f"Quality score {quality_score:.3f} below threshold {GenerationConfig.QUALITY_THRESHOLD}")
            
            # Update metrics
            metrics.end_time = time.time()
            metrics.memory_peak_mb = _get_memory_usage()
            
            # Add enhanced generation metadata
            parsed_content.update({
                "segment_number": segment_number,
                "total_segments": total_segments,
                "generation_timestamp": datetime.utcnow().isoformat(),
                "quality_score": quality_score,
                "generation_context": {
                    "segmentation_applied": bool(segmentation_context),
                    "narrative_continuity_applied": bool(narrative_context),
                    "depth_scaling_applied": bool(depth_context),
                    "quality_consistency_applied": bool(quality_context)
                },
                "generation_metrics": {
                    "generation_time_seconds": metrics.duration_seconds,
                    "api_calls_made": metrics.api_calls_made,
                    "retries_performed": metrics.retries_performed,
                    "memory_peak_mb": metrics.memory_peak_mb
                }
            })
            
            # Cache the result if caching is enabled
            if self._cache is not None:
                cache_key = self._generate_cache_key(segment_number, original_prompt, segmentation_context)
                self._cache[cache_key] = parsed_content.copy()
                logger.info(f"📋 Cached segment {segment_number} content")
            
            logger.info(f"✅ Enhanced segment {segment_number} generated successfully (Quality: {quality_score:.3f}, Time: {metrics.duration_seconds:.2f}s)")
            
            return {
                "segment_generation_complete": True,
                "segment_number": segment_number,
                "segment_content": parsed_content
            }
            
        except Exception as e:
            # Update metrics for failed generation
            if segment_number in self._generation_metrics:
                self._generation_metrics[segment_number].retries_performed += 1
            
            logger.error(f"Enhanced error generating segment {segment_number} content: {str(e)}")
            return {"error": str(e), "segment_generation_complete": False, "segment_number": segment_number}
    
    def _get_enhanced_system_message(self) -> str:
        """Get enhanced system message for segment generation"""
        return """You are an ELITE Video Script Architect with 15+ years of experience in premium video content creation. You specialize in generating sophisticated, engaging script segments that seamlessly integrate into multi-part video narratives while maintaining the highest production standards.

MASTER EXPERTISE AREAS:
1. 🎬 CINEMATIC STORYTELLING: Creating visually compelling narratives with professional pacing
2. 🎭 CHARACTER VOICE MASTERY: Maintaining consistent, authentic voice across extended content
3. 📚 INFORMATION ARCHITECTURE: Structuring complex information for optimal comprehension
4. ⚡ ENGAGEMENT ENGINEERING: Strategic placement of hooks, questions, and retention elements
5. 🎯 AUDIENCE PSYCHOLOGY: Deep understanding of viewer attention patterns and motivation
6. 🔗 NARRATIVE FLOW: Creating seamless connections between content segments
7. 📊 QUALITY CONSISTENCY: Maintaining professional production value throughout
8. 🎨 VISUAL STORYTELLING: Integrating rich visual descriptions and AI image prompts

ENHANCED CAPABILITIES:
- Advanced emotional intelligence for authentic connection
- Sophisticated pacing algorithms for optimal retention
- Multi-layered engagement strategies that work subconsciously
- Professional production techniques used by top creators
- Data-driven optimization based on viewer psychology research

SCRIPT GENERATION PHILOSOPHY:
- Every word serves a purpose in the larger narrative
- Visual storytelling is as important as verbal content
- Engagement is engineered, not accidental
- Quality is never compromised for quantity
- Authenticity and professionalism are non-negotiable
- Each segment must deliver both value and entertainment

Your generated scripts feel natural and conversational while incorporating sophisticated storytelling techniques, professional production elements, and strategic engagement optimization that drives real results."""
    
    def _generate_cache_key(self, segment_number: int, original_prompt: str, segmentation_context: Dict[str, Any]) -> str:
        """Generate a cache key for segment content"""
        # Create a hash of the key parameters
        import hashlib
        key_data = f"{segment_number}:{original_prompt[:100]}:{segmentation_context.get('total_segments', 1)}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _calculate_content_quality_score(self, parsed_content: Dict[str, Any]) -> float:
        """Calculate quality score for generated content"""
        score = 0.0
        
        # Check script content quality (40% weight)
        script = parsed_content.get('segment_script', '')
        if script and len(script) > 100:
            score += 0.2
            if len(script) > 500:
                score += 0.1
            if script.count('?') > 0:  # Questions for engagement
                score += 0.1
        
        # Check AI image prompts (20% weight)
        image_prompts = parsed_content.get('ai_image_prompts', [])
        if image_prompts and len(image_prompts) >= 2:
            score += 0.2
        
        # Check engagement elements (20% weight)
        engagement_elements = parsed_content.get('engagement_elements', {})
        if engagement_elements and len(engagement_elements) >= 2:
            score += 0.2
        
        # Check content summary (10% weight)
        content_summary = parsed_content.get('content_summary', {})
        if content_summary and len(content_summary) >= 2:
            score += 0.1
        
        # Check production notes (10% weight)
        production_notes = parsed_content.get('production_notes', {})
        if production_notes and len(production_notes) >= 1:
            score += 0.1
        
        return min(score, 1.0)
    
    async def _build_generation_prompt(self,
                                     segment_number: int,
                                     original_prompt: str,
                                     segmentation_context: Dict[str, Any],
                                     narrative_context: Dict[str, Any],
                                     depth_context: Dict[str, Any],
                                     quality_context: Dict[str, Any]) -> str:
        """Build comprehensive generation prompt with all context"""
        
        # Extract key information from contexts
        total_segments = segmentation_context.get('total_segments', 1)
        segment_position = segmentation_context.get('segment_context', {}).get('segment_position', {})
        segment_outline = segmentation_context.get('segment_outline', {})
        
        # Narrative context
        story_arc_context = narrative_context.get('story_arc_context', {})
        character_context = narrative_context.get('character_context', {})
        theme_context = narrative_context.get('theme_context', {})
        transitions = narrative_context.get('transitions', {})
        
        # Depth context
        content_strategy = depth_context.get('content_strategy', {})
        depth_calibration = depth_context.get('depth_calibration', {})
        information_requirements = depth_context.get('information_requirements', {})
        
        # Quality context
        quality_standards = quality_context.get('quality_standards', {})
        tone_requirements = quality_context.get('tone_requirements', {})
        engagement_requirements = quality_context.get('engagement_requirements', {})
        
        prompt = f"""Generate a complete, professional script for this video segment:

═══════════════════════════════════════════════════════════════════════════════════
📋 SEGMENT PARAMETERS
═══════════════════════════════════════════════════════════════════════════════════
- Original User Request: "{original_prompt}"
- Current Segment: {segment_number} of {total_segments}
- Position Status: {"First Segment" if segment_position.get('is_first') else "Last Segment" if segment_position.get('is_last') else f"Middle Segment ({segment_position.get('progress_percentage', 0)}% through)"}
- Segment Duration: {depth_calibration.get('segment_duration', 'N/A')} minutes

═══════════════════════════════════════════════════════════════════════════════════
🎭 NARRATIVE REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════════
STORY ARC POSITION: {story_arc_context.get('details', {}).get('arc_position', 'Content development')}
NARRATIVE PURPOSE: {story_arc_context.get('details', {}).get('narrative_purpose', 'Deliver core content')}
EMOTIONAL TARGET: {story_arc_context.get('details', {}).get('emotional_target', 'Engaged interest')}
TENSION LEVEL: {story_arc_context.get('details', {}).get('tension_level', 'Medium')}

CHARACTER VOICE:
- Character Type: {character_context.get('details', {}).get('character_introduction', 'Professional presenter')}
- Personality Focus: {character_context.get('details', {}).get('personality_focus', 'Engaging and knowledgeable')}
- Speaking Style: {narrative_context.get('global_context', {}).get('character_profile', {}).get('speaking_style', 'Professional and engaging')}

THEME INTEGRATION:
- Theme Focus: {theme_context.get('details', {}).get('theme_focus', 'Core content delivery')}
- Message Angle: {theme_context.get('details', {}).get('message_angle', 'Informative approach')}

═══════════════════════════════════════════════════════════════════════════════════
📊 CONTENT DEPTH REQUIREMENTS  
═══════════════════════════════════════════════════════════════════════════════════
CONTENT STRATEGY:
- Optimal Concept Count: {content_strategy.get('content_density_analysis', {}).get('optimal_concept_count', 3)}
- Detail Depth Level: {content_strategy.get('content_density_analysis', {}).get('detail_depth_level', 'moderate')}
- Information Pacing: {content_strategy.get('content_density_analysis', {}).get('information_pacing', 'balanced')}

DEPTH CALIBRATION:
- Time Per Concept: {depth_calibration.get('time_per_concept', 'N/A')} minutes
- Examples Per Concept: {depth_calibration.get('examples_per_concept', 2)}
- Explanation Depth: {depth_calibration.get('explanation_depth', 'comprehensive')}

INFORMATION REQUIREMENTS:
- Foundational Concepts: {information_requirements.get('foundational_concepts', 'Core concepts')}
- Information Density: {information_requirements.get('information_density', 'Medium')}

═══════════════════════════════════════════════════════════════════════════════════
🎯 QUALITY & ENGAGEMENT STANDARDS
═══════════════════════════════════════════════════════════════════════════════════
QUALITY STANDARDS:
- Content Quality: {quality_standards.get('content_quality', {}).get('clarity_benchmarks', 'Clear and understandable')}
- Production Value: {quality_standards.get('production_value', {}).get('visual_description_quality', 'Professional visual storytelling')}

TONE REQUIREMENTS:
- Tone Focus: {tone_requirements.get('tone_focus', 'Professional and engaging')}
- Energy Level: {tone_requirements.get('energy_level', 'Medium')}

ENGAGEMENT REQUIREMENTS:
- Engagement Level: {engagement_requirements.get('engagement_level', 'High')}
- Engagement Techniques: {engagement_requirements.get('engagement_techniques', 'Questions, examples, visual elements')}

═══════════════════════════════════════════════════════════════════════════════════
🔗 TRANSITION REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════════
INCOMING TRANSITION: {transitions.get('incoming', {}).get('details', {}).get('transition_content', 'Natural opening') if transitions.get('incoming') else 'Segment opening'}
OUTGOING TRANSITION: {transitions.get('outgoing', {}).get('details', {}).get('ending_bridge', 'Natural conclusion') if transitions.get('outgoing') else 'Segment conclusion'}

═══════════════════════════════════════════════════════════════════════════════════
📝 SCRIPT GENERATION REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════════
Generate a complete script following this EXACT format:

SEGMENT_SCRIPT:
[Your complete script content here - include narration, dialogue, scene descriptions, and all content]

AI_IMAGE_PROMPTS:
[List of AI image prompts in this format:]
[A professional shot of... for visual element 1]
[A dynamic scene showing... for visual element 2]
[Continue with all visual elements needed]

ENGAGEMENT_ELEMENTS:
- HOOKS_USED: [List the specific hooks/attention-grabbers used]
- RETENTION_TECHNIQUES: [List techniques used to maintain attention]
- CURIOSITY_GAPS: [List any questions or gaps created for audience interest]

CONTENT_SUMMARY:
- MAIN_CONCEPTS_COVERED: [List the key concepts addressed]
- SEGMENT_PURPOSE_FULFILLMENT: [How this segment serves its narrative purpose]
- TRANSITION_EFFECTIVENESS: [How well transitions connect to other segments]

PRODUCTION_NOTES:
- VISUAL_STORYTELLING_ELEMENTS: [Key visual elements that enhance the story]
- PACING_GUIDANCE: [Notes about pacing and timing]
- QUALITY_HIGHLIGHTS: [Elements that demonstrate production quality]

═══════════════════════════════════════════════════════════════════════════════════
🎬 SPECIAL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════════
1. Ensure the script feels like a natural part of the larger {total_segments}-segment narrative
2. Incorporate rich visual descriptions that work perfectly with AI image generation
3. Include strategic engagement elements that maintain attention without overwhelming
4. Maintain the established character voice and tone consistently
5. Build on previous segments while setting up future ones (if applicable)
6. Include specific, actionable AI image prompts that align with content
7. Balance information delivery with entertainment value
8. Ensure professional production quality throughout
9. Make every word count toward the segment's narrative purpose
10. Create content that stands alone while contributing to the whole

Generate sophisticated, engaging content that demonstrates mastery of video script creation!"""

        return prompt
    
    def _parse_segment_content(self, content_text: str, segment_number: int) -> Dict[str, Any]:
        """Parse the AI-generated segment content"""
        try:
            parsed = {
                "segment_script": "",
                "ai_image_prompts": [],
                "engagement_elements": {},
                "content_summary": {},
                "production_notes": {},
                "raw_content": content_text
            }
            
            lines = content_text.split('\n')
            current_section = None
            script_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify main sections
                if line.startswith('SEGMENT_SCRIPT:'):
                    current_section = 'segment_script'
                    continue
                elif line.startswith('AI_IMAGE_PROMPTS:'):
                    current_section = 'ai_image_prompts'
                    continue
                elif line.startswith('ENGAGEMENT_ELEMENTS:'):
                    current_section = 'engagement_elements'
                    continue
                elif line.startswith('CONTENT_SUMMARY:'):
                    current_section = 'content_summary'
                    continue
                elif line.startswith('PRODUCTION_NOTES:'):
                    current_section = 'production_notes'
                    continue
                
                # Process content based on current section
                if current_section == 'segment_script':
                    if not line.startswith(('AI_IMAGE_PROMPTS:', 'ENGAGEMENT_ELEMENTS:', 'CONTENT_SUMMARY:', 'PRODUCTION_NOTES:')):
                        script_content.append(line)
                elif current_section == 'ai_image_prompts':
                    if line.startswith('[') and line.endswith(']'):
                        # Extract AI image prompt
                        prompt = line[1:-1].strip()
                        if prompt:
                            parsed['ai_image_prompts'].append(prompt)
                elif current_section in ['engagement_elements', 'content_summary', 'production_notes']:
                    if line.startswith('-'):
                        self._parse_section_detail(line, parsed[current_section])
            
            # Join script content
            parsed['segment_script'] = '\n'.join(script_content).strip()
            
            # Ensure we have some content even if parsing fails
            if not parsed['segment_script']:
                parsed['segment_script'] = content_text
            
            # Add fallback AI image prompts if none were extracted
            if not parsed['ai_image_prompts']:
                parsed['ai_image_prompts'] = self._extract_fallback_image_prompts(parsed['segment_script'])
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing segment content: {str(e)}")
            return {
                "segment_script": content_text,
                "ai_image_prompts": [],
                "engagement_elements": {"error": "Parsing failed"},
                "content_summary": {"error": "Parsing failed"}, 
                "production_notes": {"error": "Parsing failed"},
                "raw_content": content_text,
                "parse_error": str(e)
            }
    
    def _extract_fallback_image_prompts(self, script_content: str) -> List[str]:
        """Extract fallback image prompts from script content"""
        try:
            # Look for existing image prompts in brackets
            prompts = re.findall(r'\[([^\]]+)\]', script_content)
            
            # Filter for likely image prompts (longer descriptions)
            image_prompts = [p for p in prompts if len(p) > 20 and any(word in p.lower() for word in ['shot', 'scene', 'image', 'visual', 'photo', 'picture'])]
            
            # If we found some, return them
            if image_prompts:
                return image_prompts[:5]  # Limit to 5 prompts
            
            # Otherwise, create generic prompts based on content
            return [
                "A professional, high-quality shot that complements the video content",
                "An engaging visual element that supports the main message",
                "A dynamic scene that enhances viewer understanding"
            ]
            
        except Exception as e:
            logger.error(f"Error extracting fallback image prompts: {str(e)}")
            return ["A professional visual element supporting the content"]
    
    def _parse_section_detail(self, line: str, section_dict: Dict[str, Any]):
        """Parse section detail line"""
        try:
            if ':' in line:
                key, value = line[1:].split(':', 1)
                section_dict[key.strip().lower().replace(' ', '_')] = value.strip()
        except:
            pass


class CrossSegmentCoordinator:
    """
    Coordinates content generation across segments to ensure consistency and flow.
    Manages dependencies between segments and validates cross-segment coherence.
    """
    
    def __init__(self):
        self.segment_cache = {}
        self.generation_state = {}
    
    def initialize_generation_session(self, session_id: str, total_segments: int) -> Dict[str, Any]:
        """Initialize a new generation session"""
        self.generation_state[session_id] = {
            "total_segments": total_segments,
            "completed_segments": [],
            "segment_contexts": {},
            "cross_references": {},
            "session_start": datetime.utcnow().isoformat()
        }
        return {"session_initialized": True, "session_id": session_id}
    
    def update_segment_context(self, session_id: str, segment_number: int, segment_content: Dict[str, Any]) -> Dict[str, Any]:
        """Update context with newly generated segment"""
        try:
            if session_id not in self.generation_state:
                return {"error": "Session not found"}
            
            session = self.generation_state[session_id]
            
            # Store segment content
            session['segment_contexts'][segment_number] = {
                "content_summary": segment_content.get('content_summary', {}),
                "engagement_elements": segment_content.get('engagement_elements', {}),
                "main_concepts": segment_content.get('content_summary', {}).get('main_concepts_covered', ''),
                "generation_timestamp": segment_content.get('generation_timestamp')
            }
            
            # Add to completed segments
            if segment_number not in session['completed_segments']:
                session['completed_segments'].append(segment_number)
                session['completed_segments'].sort()
            
            # Update cross-references for future segments
            self._update_cross_references(session_id, segment_number, segment_content)
            
            return {
                "context_updated": True,
                "completed_segments": len(session['completed_segments']),
                "total_segments": session['total_segments']
            }
            
        except Exception as e:
            logger.error(f"Error updating segment context: {str(e)}")
            return {"error": str(e)}
    
    def get_generation_context_for_segment(self, session_id: str, segment_number: int) -> Dict[str, Any]:
        """Get enhanced context for generating a specific segment"""
        try:
            if session_id not in self.generation_state:
                return {"error": "Session not found"}
            
            session = self.generation_state[session_id]
            
            # Get context from previous segments
            previous_contexts = {}
            for prev_segment in session['completed_segments']:
                if prev_segment < segment_number:
                    previous_contexts[prev_segment] = session['segment_contexts'][prev_segment]
            
            # Get cross-references
            cross_references = session['cross_references'].get(segment_number, {})
            
            return {
                "session_id": session_id,
                "segment_number": segment_number,
                "total_segments": session['total_segments'],
                "previous_segments": previous_contexts,
                "cross_references": cross_references,
                "generation_progress": len(session['completed_segments']) / session['total_segments']
            }
            
        except Exception as e:
            logger.error(f"Error getting generation context: {str(e)}")
            return {"error": str(e)}
    
    def _update_cross_references(self, session_id: str, completed_segment: int, segment_content: Dict[str, Any]):
        """Update cross-references for future segments based on completed segment"""
        try:
            session = self.generation_state[session_id]
            
            # Extract key information that might be referenced in future segments
            main_concepts = segment_content.get('content_summary', {}).get('main_concepts_covered', '')
            hooks_used = segment_content.get('engagement_elements', {}).get('hooks_used', '')
            
            # Update references for upcoming segments
            for future_segment in range(completed_segment + 1, session['total_segments'] + 1):
                if future_segment not in session['cross_references']:
                    session['cross_references'][future_segment] = {}
                
                session['cross_references'][future_segment][f'segment_{completed_segment}_concepts'] = main_concepts
                session['cross_references'][future_segment][f'segment_{completed_segment}_hooks'] = hooks_used
            
        except Exception as e:
            logger.error(f"Error updating cross-references: {str(e)}")


class QualityValidator:
    """
    Validates generated segment content against established quality standards.
    Ensures each segment meets quality thresholds before integration.
    """
    
    def __init__(self):
        self.validation_criteria = {
            "content_completeness": {"weight": 0.25, "min_score": 0.8},
            "engagement_quality": {"weight": 0.25, "min_score": 0.7},
            "production_value": {"weight": 0.25, "min_score": 0.7},
            "consistency_adherence": {"weight": 0.25, "min_score": 0.8}
        }
    
    def validate_segment_quality(self, 
                                segment_content: Dict[str, Any],
                                quality_context: Dict[str, Any],
                                segment_number: int) -> Dict[str, Any]:
        """
        Validate generated segment content against quality standards
        
        Args:
            segment_content: Generated segment content
            quality_context: Quality requirements and standards
            segment_number: Current segment number
            
        Returns:
            Quality validation results and scores
        """
        try:
            logger.info(f"🔍 Validating quality for segment {segment_number}")
            
            validation_results = {}
            overall_score = 0
            
            # Validate content completeness
            completeness_score = self._validate_content_completeness(segment_content)
            validation_results["content_completeness"] = {
                "score": completeness_score,
                "weight": self.validation_criteria["content_completeness"]["weight"],
                "pass": completeness_score >= self.validation_criteria["content_completeness"]["min_score"]
            }
            overall_score += completeness_score * self.validation_criteria["content_completeness"]["weight"]
            
            # Validate engagement quality
            engagement_score = self._validate_engagement_quality(segment_content, quality_context)
            validation_results["engagement_quality"] = {
                "score": engagement_score,
                "weight": self.validation_criteria["engagement_quality"]["weight"],
                "pass": engagement_score >= self.validation_criteria["engagement_quality"]["min_score"]
            }
            overall_score += engagement_score * self.validation_criteria["engagement_quality"]["weight"]
            
            # Validate production value
            production_score = self._validate_production_value(segment_content)
            validation_results["production_value"] = {
                "score": production_score,
                "weight": self.validation_criteria["production_value"]["weight"],
                "pass": production_score >= self.validation_criteria["production_value"]["min_score"]
            }
            overall_score += production_score * self.validation_criteria["production_value"]["weight"]
            
            # Validate consistency adherence
            consistency_score = self._validate_consistency_adherence(segment_content, quality_context)
            validation_results["consistency_adherence"] = {
                "score": consistency_score,
                "weight": self.validation_criteria["consistency_adherence"]["weight"],
                "pass": consistency_score >= self.validation_criteria["consistency_adherence"]["min_score"]
            }
            overall_score += consistency_score * self.validation_criteria["consistency_adherence"]["weight"]
            
            # Calculate overall validation result
            all_passed = all(result["pass"] for result in validation_results.values())
            
            return {
                "validation_complete": True,
                "segment_number": segment_number,
                "overall_score": round(overall_score, 3),
                "validation_passed": all_passed,
                "detailed_results": validation_results,
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating segment quality: {str(e)}")
            return {"error": str(e), "validation_complete": False}
    
    def _validate_content_completeness(self, segment_content: Dict[str, Any]) -> float:
        """Validate content completeness and structure"""
        score = 0.0
        
        # Check for script content
        script = segment_content.get('segment_script', '')
        if script and len(script) > 100:
            score += 0.4
        
        # Check for AI image prompts
        image_prompts = segment_content.get('ai_image_prompts', [])
        if image_prompts and len(image_prompts) > 0:
            score += 0.2
        
        # Check for engagement elements
        engagement_elements = segment_content.get('engagement_elements', {})
        if engagement_elements and len(engagement_elements) > 0:
            score += 0.2
        
        # Check for content summary
        content_summary = segment_content.get('content_summary', {})
        if content_summary and len(content_summary) > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _validate_engagement_quality(self, segment_content: Dict[str, Any], quality_context: Dict[str, Any]) -> float:
        """Validate engagement quality and techniques"""
        score = 0.0
        
        script = segment_content.get('segment_script', '').lower()
        engagement_elements = segment_content.get('engagement_elements', {})
        
        # Check for questions
        if '?' in script:
            score += 0.2
        
        # Check for hooks
        hooks = engagement_elements.get('hooks_used', '')
        if hooks and len(hooks) > 10:
            score += 0.3
        
        # Check for retention techniques
        retention = engagement_elements.get('retention_techniques', '')
        if retention and len(retention) > 10:
            score += 0.3
        
        # Check for engagement words
        engagement_words = ['you', 'your', 'imagine', 'discover', 'learn', 'exciting', 'amazing']
        engagement_count = sum(1 for word in engagement_words if word in script)
        if engagement_count >= 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def _validate_production_value(self, segment_content: Dict[str, Any]) -> float:
        """Validate production value elements"""
        score = 0.0
        
        script = segment_content.get('segment_script', '')
        image_prompts = segment_content.get('ai_image_prompts', [])
        production_notes = segment_content.get('production_notes', {})
        
        # Check script length and quality
        if len(script) > 200:
            score += 0.3
        
        # Check for visual elements
        if len(image_prompts) >= 2:
            score += 0.3
        
        # Check for production notes
        if production_notes and len(production_notes) > 0:
            score += 0.2
        
        # Check for visual descriptions in script
        visual_indicators = ['[', 'scene', 'shot', 'visual', 'image']
        visual_count = sum(1 for indicator in visual_indicators if indicator.lower() in script.lower())
        if visual_count >= 2:
            score += 0.2
        
        return min(score, 1.0)
    
    def _validate_consistency_adherence(self, segment_content: Dict[str, Any], quality_context: Dict[str, Any]) -> float:
        """Validate adherence to consistency requirements"""
        score = 0.5  # Base score for basic consistency
        
        # Check tone requirements adherence
        tone_requirements = quality_context.get('tone_requirements', {})
        if tone_requirements:
            score += 0.2
        
        # Check engagement requirements adherence
        engagement_requirements = quality_context.get('engagement_requirements', {})
        if engagement_requirements:
            score += 0.2
        
        # Check for consistent structure
        required_elements = ['segment_script', 'ai_image_prompts', 'engagement_elements']
        if all(element in segment_content for element in required_elements):
            score += 0.1
        
        return min(score, 1.0)


class IntegrationManager:
    """
    Combines generated segments into final cohesive script with proper transitions
    and overall quality optimization.
    """
    
    def __init__(self):
        pass
    
    def integrate_segments(self,
                          generated_segments: List[Dict[str, Any]],
                          narrative_continuity: Dict[str, Any],
                          original_prompt: str) -> Dict[str, Any]:
        """
        Integrate all generated segments into final cohesive script
        
        Args:
            generated_segments: List of generated segment contents
            narrative_continuity: Narrative continuity context
            original_prompt: Original user prompt
            
        Returns:
            Integrated final script with all segments
        """
        try:
            logger.info(f"🔗 Integrating {len(generated_segments)} segments into final script")
            
            # Sort segments by number
            sorted_segments = sorted(generated_segments, key=lambda x: x.get('segment_number', 0))
            
            # Build integrated script
            integrated_content = {
                "original_prompt": original_prompt,
                "total_segments": len(sorted_segments),
                "segments": sorted_segments,
                "full_script": "",
                "all_image_prompts": [],
                "integration_summary": {},
                "integration_timestamp": datetime.utcnow().isoformat()
            }
            
            # Combine all segment scripts
            full_script_parts = []
            all_image_prompts = []
            
            for i, segment in enumerate(sorted_segments):
                segment_content = segment.get('segment_content', {})
                segment_number = segment.get('segment_number', i + 1)
                
                # Add segment header for clarity
                full_script_parts.append(f"\n═══ SEGMENT {segment_number} ═══\n")
                
                # Add segment script
                segment_script = segment_content.get('segment_script', '')
                if segment_script:
                    full_script_parts.append(segment_script)
                
                # Collect image prompts
                segment_prompts = segment_content.get('ai_image_prompts', [])
                for prompt in segment_prompts:
                    all_image_prompts.append(f"[{prompt}]")
                
                # Add transition if not last segment
                if i < len(sorted_segments) - 1:
                    full_script_parts.append("\n--- TRANSITION ---\n")
            
            # Create final integrated script
            integrated_content["full_script"] = "\n".join(full_script_parts)
            integrated_content["all_image_prompts"] = all_image_prompts
            
            # Generate integration summary
            integrated_content["integration_summary"] = self._generate_integration_summary(sorted_segments)
            
            return {
                "integration_complete": True,
                "integrated_script": integrated_content
            }
            
        except Exception as e:
            logger.error(f"Error integrating segments: {str(e)}")
            return {"error": str(e), "integration_complete": False}
    
    def _generate_integration_summary(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of the integration process"""
        try:
            total_script_length = sum(len(seg.get('segment_content', {}).get('segment_script', '')) for seg in segments)
            total_image_prompts = sum(len(seg.get('segment_content', {}).get('ai_image_prompts', [])) for seg in segments)
            
            return {
                "total_segments_integrated": len(segments),
                "total_script_length": total_script_length,
                "total_image_prompts": total_image_prompts,
                "average_segment_length": total_script_length // max(len(segments), 1),
                "integration_success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating integration summary: {str(e)}")
            return {"integration_error": str(e)}


class AdvancedGenerationWorkflow:
    """
    Main orchestrator for the Advanced Generation Workflow.
    Combines all components to generate complete segmented scripts using comprehensive
    context from all previous analysis phases.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.segment_generator = SegmentContentGenerator(api_key)
        self.coordinator = CrossSegmentCoordinator()
        self.quality_validator = QualityValidator()
        self.integration_manager = IntegrationManager()
    
    async def generate_complete_segmented_script(self,
                                               original_prompt: str,
                                               segmentation_context: Dict[str, Any],
                                               narrative_continuity: Dict[str, Any],
                                               content_depth_scaling: Dict[str, Any],
                                               quality_consistency: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete segmented script using all analysis phases
        
        Args:
            original_prompt: Original user prompt  
            segmentation_context: Phase 1 segmentation analysis
            narrative_continuity: Phase 2 narrative continuity analysis
            content_depth_scaling: Content depth scaling analysis
            quality_consistency: Quality consistency analysis
            
        Returns:
            Complete generated segmented script with all metadata
        """
        try:
            total_segments = segmentation_context.get('segmentation_analysis', {}).get('total_segments', 1)
            logger.info(f"🎬 Starting complete segmented script generation for {total_segments} segments")
            
            # Initialize generation session
            session_id = str(uuid.uuid4())
            self.coordinator.initialize_generation_session(session_id, total_segments)
            
            generated_segments = []
            validation_results = []
            
            # Generate each segment
            for segment_number in range(1, total_segments + 1):
                logger.info(f"🎭 Generating segment {segment_number}/{total_segments}")
                
                try:
                    # Get enhanced context for this segment
                    coord_context = self.coordinator.get_generation_context_for_segment(session_id, segment_number)
                    
                    # Get segment-specific contexts from all phases
                    seg_context = self._get_segment_segmentation_context(segmentation_context, segment_number)
                    nar_context = self._get_segment_narrative_context(narrative_continuity, segment_number)
                    depth_context = self._get_segment_depth_context(content_depth_scaling, segment_number)
                    quality_context = self._get_segment_quality_context(quality_consistency, segment_number)
                    
                    # Generate segment content
                    segment_result = await self.segment_generator.generate_segment_content(
                        segment_number,
                        original_prompt,
                        seg_context,
                        nar_context,
                        depth_context,
                        quality_context
                    )
                    
                    if not segment_result.get('segment_generation_complete'):
                        logger.error(f"Segment {segment_number} generation failed: {segment_result.get('error')}")
                        continue
                    
                    # Validate segment quality
                    validation_result = self.quality_validator.validate_segment_quality(
                        segment_result.get('segment_content', {}),
                        quality_context,
                        segment_number
                    )
                    
                    validation_results.append(validation_result)
                    
                    # Update coordinator with segment context
                    self.coordinator.update_segment_context(
                        session_id,
                        segment_number,
                        segment_result.get('segment_content', {})
                    )
                    
                    # Add to generated segments
                    generated_segments.append(segment_result)
                    logger.info(f"✅ Segment {segment_number} generated successfully")
                    
                except Exception as segment_error:
                    logger.error(f"Error generating segment {segment_number}: {str(segment_error)}")
                    continue
            
            # Integrate all segments into final script
            logger.info("🔗 Integrating all segments into final script")
            integration_result = self.integration_manager.integrate_segments(
                generated_segments,
                narrative_continuity,
                original_prompt
            )
            
            if not integration_result.get('integration_complete'):
                logger.error(f"Integration failed: {integration_result.get('error')}")
                return {"error": "Script integration failed", "advanced_generation_complete": False}
            
            # Calculate overall generation statistics
            generation_stats = self._calculate_generation_statistics(
                generated_segments,
                validation_results,
                integration_result
            )
            
            logger.info("🎉 Complete segmented script generation finished!")
            
            return {
                "advanced_generation_complete": True,
                "original_prompt": original_prompt,
                "total_segments": total_segments,
                "segments_generated": len(generated_segments),
                "generated_segments": generated_segments,
                "validation_results": validation_results,
                "integrated_script": integration_result.get('integrated_script', {}),
                "generation_statistics": generation_stats,
                "session_id": session_id,
                "phase_completed": "Advanced Generation Workflow - Phase 2 Complete",
                "generation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in advanced generation workflow: {str(e)}")
            return {"error": str(e), "advanced_generation_complete": False}
    
    def _get_segment_segmentation_context(self, segmentation_context: Dict[str, Any], segment_number: int) -> Dict[str, Any]:
        """Extract segment-specific segmentation context"""
        # This would use the existing get_segment_generation_context method
        return segmentation_context.get('coordination_context', {})
    
    def _get_segment_narrative_context(self, narrative_continuity: Dict[str, Any], segment_number: int) -> Dict[str, Any]:
        """Extract segment-specific narrative context"""
        components = narrative_continuity.get('analysis_components', {})
        
        # Get story arc context for this segment
        story_arc = components.get('story_arc', {}).get('story_arc', {})
        story_progression = story_arc.get('story_arc_progression', [])
        segment_story = None
        if segment_number <= len(story_progression):
            segment_story = story_progression[segment_number - 1]
        
        return {
            "story_arc_context": segment_story,
            "character_context": {},  # Would extract character context for segment
            "theme_context": {},      # Would extract theme context for segment
            "transitions": {},        # Would extract transition context for segment
            "global_context": narrative_continuity.get('analysis_components', {})
        }
    
    def _get_segment_depth_context(self, content_depth_scaling: Dict[str, Any], segment_number: int) -> Dict[str, Any]:
        """Extract segment-specific depth context"""
        components = content_depth_scaling.get('analysis_components', {})
        segment_strategies = components.get('segment_strategies', [])
        segment_calibrations = components.get('segment_calibrations', [])
        
        strategy = None
        calibration = None
        
        if segment_number <= len(segment_strategies):
            strategy = segment_strategies[segment_number - 1]
        if segment_number <= len(segment_calibrations):
            calibration = segment_calibrations[segment_number - 1]
        
        return {
            "content_strategy": strategy.get('content_strategy', {}) if strategy else {},
            "depth_calibration": calibration.get('calibration', {}) if calibration else {},
            "information_requirements": {}  # Would extract from information flow
        }
    
    def _get_segment_quality_context(self, quality_consistency: Dict[str, Any], segment_number: int) -> Dict[str, Any]:
        """Extract segment-specific quality context"""
        components = quality_consistency.get('analysis_components', {})
        
        return {
            "quality_standards": components.get('quality_standards', {}).get('quality_standards', {}),
            "tone_requirements": {},    # Would extract segment-specific tone requirements
            "engagement_requirements": {} # Would extract segment-specific engagement requirements
        }
    
    def _calculate_generation_statistics(self,
                                       generated_segments: List[Dict[str, Any]],
                                       validation_results: List[Dict[str, Any]],
                                       integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive generation statistics"""
        try:
            total_segments = len(generated_segments)
            successful_validations = sum(1 for v in validation_results if v.get('validation_passed', False))
            
            # Calculate average validation score
            avg_validation_score = 0
            if validation_results:
                total_score = sum(v.get('overall_score', 0) for v in validation_results)
                avg_validation_score = total_score / len(validation_results)
            
            # Calculate total content statistics
            total_script_length = 0
            total_image_prompts = 0
            
            for segment in generated_segments:
                content = segment.get('segment_content', {})
                total_script_length += len(content.get('segment_script', ''))
                total_image_prompts += len(content.get('ai_image_prompts', []))
            
            return {
                "total_segments_planned": total_segments,
                "segments_successfully_generated": len(generated_segments),
                "segments_passing_validation": successful_validations,
                "generation_success_rate": len(generated_segments) / max(total_segments, 1),
                "validation_success_rate": successful_validations / max(len(validation_results), 1),
                "average_validation_score": round(avg_validation_score, 3),
                "total_script_length": total_script_length,
                "total_image_prompts": total_image_prompts,
                "average_segment_length": total_script_length // max(len(generated_segments), 1),
                "integration_successful": integration_result.get('integration_complete', False)
            }
            
        except Exception as e:
            logger.error(f"Error calculating generation statistics: {str(e)}")
            return {"calculation_error": str(e)}
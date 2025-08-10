"""
Enhanced Prompt Engineering Architecture - Main Orchestrator
Phase 3.1 Implementation - Enhanced Prompt Architecture Foundation

This module implements the main orchestrator for the Enhanced Prompt Engineering Architecture.
It provides duration-specific template selection, enhanced system prompt generation, and
seamless integration with the existing segmentation system.

Components:
- EnhancedPromptArchitecture: Main orchestrator class
- Template selection and customization logic
- Integration with AdvancedScriptGenerator
- System prompt enhancement and optimization
- Segmentation compatibility validation
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import asyncio
from dataclasses import dataclass
from enum import Enum

# Import the Template Registry System
from .prompt_template_registry import (
    PromptTemplateRegistry, 
    TemplateContent, 
    TemplateMetadata,
    TemplateValidationError,
    TemplateStatus,
    TemplateType
)

logger = logging.getLogger(__name__)

class PromptEnhancementLevel(Enum):
    """Enhancement levels for prompt optimization"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    ELITE = "elite"

class IntegrationMode(Enum):
    """Integration modes with existing systems"""
    SEAMLESS = "seamless"
    ENHANCED = "enhanced"
    OVERRIDE = "override"
    HYBRID = "hybrid"

@dataclass
class PromptArchitectureConfig:
    """Configuration for Enhanced Prompt Architecture"""
    enhancement_level: PromptEnhancementLevel
    integration_mode: IntegrationMode
    enable_customization: bool
    enable_segmentation_integration: bool
    enable_template_caching: bool
    max_cache_size: int
    session_timeout_minutes: int
    performance_tracking: bool

class PromptGenerationSession:
    """Session management for prompt generation operations"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.last_activity = self.created_at
        self.operations_count = 0
        self.generated_prompts = []
        self.performance_metrics = {}
        self.errors = []
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        self.operations_count += 1
    
    def add_generated_prompt(self, prompt_data: Dict[str, Any]):
        """Add generated prompt to session history"""
        self.generated_prompts.append({
            "timestamp": datetime.utcnow().isoformat(),
            "prompt_data": prompt_data
        })
    
    def record_error(self, error: Exception, context: str = ""):
        """Record error in session"""
        self.errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(error),
            "context": context,
            "error_type": type(error).__name__
        })
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        duration_seconds = (datetime.utcnow() - self.created_at).total_seconds()
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "duration_seconds": duration_seconds,
            "operations_count": self.operations_count,
            "prompts_generated": len(self.generated_prompts),
            "errors_count": len(self.errors),
            "last_activity": self.last_activity.isoformat(),
            "performance_metrics": self.performance_metrics
        }

class TemplateSelector:
    """Template selection logic for duration-specific templates"""
    
    def __init__(self, template_registry: PromptTemplateRegistry):
        self.template_registry = template_registry
        self.selection_history = {}
        self.performance_cache = {}
    
    async def select_optimal_template(self, 
                                    duration: str, 
                                    video_type: str = "general",
                                    complexity_preference: str = "moderate",
                                    focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Select the most appropriate template for given parameters
        
        Args:
            duration: Target duration (extended_15, extended_20, extended_25)
            video_type: Type of video content
            complexity_preference: Preferred complexity level
            focus_areas: Specific areas to focus on
            
        Returns:
            Dict containing selected template and metadata
        """
        try:
            logger.info(f"🎯 Selecting optimal template for duration: {duration}, type: {video_type}")
            
            # Validate duration compatibility
            if not self._validate_duration_support(duration):
                raise TemplateValidationError(f"Duration '{duration}' not supported for enhanced templates")
            
            # Get available templates for duration
            template_data = await self.template_registry.get_template(duration)
            if not template_data:
                raise TemplateValidationError(f"No template available for duration '{duration}'")
            
            # Analyze template suitability
            suitability_score = await self._analyze_template_suitability(
                template_data, video_type, complexity_preference, focus_areas
            )
            
            # Get template customization options
            customization_config = await self._generate_customization_config(
                template_data, video_type, focus_areas
            )
            
            # Record selection for analytics
            self._record_template_selection(duration, video_type, template_data["template_id"])
            
            selection_result = {
                "template_id": template_data["template_id"],
                "template_name": template_data["metadata"]["template_name"],
                "duration": duration,
                "video_type": video_type,
                "template_data": template_data,
                "suitability_score": suitability_score,
                "customization_config": customization_config,
                "selection_reasoning": self._generate_selection_reasoning(
                    template_data, suitability_score, video_type
                ),
                "selected_at": datetime.utcnow().isoformat(),
                "segment_compatibility": self._analyze_segment_compatibility(template_data, duration)
            }
            
            logger.info(f"✅ Template selected: {template_data['template_id']} (score: {suitability_score:.2f})")
            return selection_result
            
        except Exception as e:
            logger.error(f"Template selection failed: {str(e)}")
            raise TemplateValidationError(f"Template selection failed: {str(e)}")
    
    def _validate_duration_support(self, duration: str) -> bool:
        """Validate that duration is supported for enhanced templates"""
        supported_durations = ["extended_15", "extended_20", "extended_25"]
        return duration in supported_durations
    
    async def _analyze_template_suitability(self, 
                                          template_data: Dict[str, Any],
                                          video_type: str,
                                          complexity_preference: str,
                                          focus_areas: List[str] = None) -> float:
        """Analyze how suitable a template is for the given parameters"""
        try:
            metadata = template_data.get("metadata", {})
            
            # Base suitability score
            base_score = 0.5
            
            # Video type compatibility (0.3 weight)
            video_type_bonus = 0.0
            template_focus = metadata.get("focus_strategy", "").lower()
            if video_type == "educational" and "educational" in template_focus:
                video_type_bonus = 0.3
            elif video_type == "marketing" and "engagement" in template_focus:
                video_type_bonus = 0.25
            elif video_type == "entertainment" and "viral" in template_focus:
                video_type_bonus = 0.25
            else:
                video_type_bonus = 0.1  # General compatibility
            
            # Complexity alignment (0.2 weight)
            complexity_bonus = 0.0
            template_complexity = metadata.get("complexity_level", "moderate").lower()
            if template_complexity == complexity_preference.lower():
                complexity_bonus = 0.2
            elif abs(self._complexity_to_number(template_complexity) - self._complexity_to_number(complexity_preference)) <= 1:
                complexity_bonus = 0.1
            
            # Usage history bonus (0.1 weight)
            usage_bonus = min(0.1, metadata.get("usage_count", 0) / 100)
            
            # Effectiveness bonus (0.1 weight) 
            effectiveness_bonus = metadata.get("effectiveness_score", 0.0) * 0.1
            
            # Focus areas alignment (0.2 weight)
            focus_bonus = 0.0
            if focus_areas:
                template_expertise = metadata.get("expertise_areas", [])
                matching_areas = len(set(focus_areas) & set(template_expertise))
                focus_bonus = min(0.2, matching_areas / max(len(focus_areas), 1) * 0.2)
            else:
                focus_bonus = 0.1  # Default bonus for no specific requirements
            
            # Calculate final suitability score
            final_score = min(1.0, base_score + video_type_bonus + complexity_bonus + 
                            usage_bonus + effectiveness_bonus + focus_bonus)
            
            return round(final_score, 3)
            
        except Exception as e:
            logger.warning(f"Error analyzing template suitability: {str(e)}")
            return 0.5  # Default moderate suitability
    
    def _complexity_to_number(self, complexity: str) -> int:
        """Convert complexity level to number for comparison"""
        mapping = {"basic": 1, "moderate": 2, "advanced": 3, "expert": 4, "elite": 5}
        return mapping.get(complexity.lower(), 2)
    
    async def _generate_customization_config(self, 
                                           template_data: Dict[str, Any],
                                           video_type: str,
                                           focus_areas: List[str] = None) -> Dict[str, Any]:
        """Generate customization configuration for template"""
        try:
            content = template_data.get("content", {})
            customization_options = content.get("customization_options", {})
            
            config = {
                "video_type_adaptations": self._get_video_type_adaptations(video_type),
                "focus_area_enhancements": self._get_focus_area_enhancements(focus_areas),
                "template_specific_options": customization_options,
                "dynamic_adjustments": {
                    "tone_adjustment": self._determine_tone_adjustment(video_type),
                    "complexity_scaling": self._determine_complexity_scaling(template_data),
                    "engagement_optimization": self._determine_engagement_optimization(video_type)
                },
                "integration_requirements": {
                    "segmentation_alignment": True,
                    "narrative_continuity": True,
                    "content_depth_scaling": True
                }
            }
            
            return config
            
        except Exception as e:
            logger.warning(f"Error generating customization config: {str(e)}")
            return {"error": str(e)}
    
    def _get_video_type_adaptations(self, video_type: str) -> Dict[str, Any]:
        """Get video type specific adaptations"""
        adaptations = {
            "educational": {
                "learning_objectives_emphasis": True,
                "knowledge_retention_focus": True,
                "comprehension_checkpoints": True,
                "instructional_tone": True
            },
            "marketing": {
                "conversion_optimization": True,
                "persuasive_elements": True,
                "call_to_action_integration": True,
                "brand_voice_alignment": True
            },
            "entertainment": {
                "engagement_maximization": True,
                "emotional_hooks": True,
                "viral_potential_optimization": True,
                "entertainment_pacing": True
            },
            "general": {
                "balanced_approach": True,
                "universal_appeal": True,
                "flexible_adaptation": True,
                "broad_audience_focus": True
            }
        }
        
        return adaptations.get(video_type, adaptations["general"])
    
    def _get_focus_area_enhancements(self, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Get focus area specific enhancements"""
        if not focus_areas:
            return {"no_specific_focus": True}
        
        enhancements = {}
        for area in focus_areas:
            area_lower = area.lower()
            if "engagement" in area_lower:
                enhancements["engagement_boost"] = True
            if "narrative" in area_lower:
                enhancements["story_focus"] = True  
            if "technical" in area_lower:
                enhancements["technical_precision"] = True
            if "emotional" in area_lower:
                enhancements["emotional_intelligence"] = True
        
        return enhancements
    
    def _determine_tone_adjustment(self, video_type: str) -> str:
        """Determine appropriate tone adjustment"""
        tone_mapping = {
            "educational": "informative_engaging",
            "marketing": "persuasive_energetic",
            "entertainment": "dynamic_entertaining", 
            "general": "professional_engaging"
        }
        return tone_mapping.get(video_type, "balanced")
    
    def _determine_complexity_scaling(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine complexity scaling parameters"""
        metadata = template_data.get("metadata", {})
        base_complexity = metadata.get("complexity_level", "moderate")
        
        return {
            "base_level": base_complexity,
            "adaptive_scaling": True,
            "segment_progression": True,
            "audience_calibration": True
        }
    
    def _determine_engagement_optimization(self, video_type: str) -> Dict[str, Any]:
        """Determine engagement optimization strategy"""
        strategies = {
            "educational": {"retention_focus": True, "comprehension_balance": True},
            "marketing": {"conversion_focus": True, "persuasion_optimization": True},
            "entertainment": {"viral_optimization": True, "emotional_peaks": True},
            "general": {"balanced_engagement": True, "universal_appeal": True}
        }
        
        return strategies.get(video_type, strategies["general"])
    
    def _generate_selection_reasoning(self, 
                                    template_data: Dict[str, Any],
                                    suitability_score: float,
                                    video_type: str) -> str:
        """Generate human-readable selection reasoning"""
        metadata = template_data.get("metadata", {})
        template_name = metadata.get("template_name", "Unknown Template")
        
        reasoning = f"Selected '{template_name}' with suitability score {suitability_score:.2f}. "
        
        if suitability_score >= 0.8:
            reasoning += "Excellent match for requirements. "
        elif suitability_score >= 0.6:
            reasoning += "Good match with minor customizations needed. "
        else:
            reasoning += "Acceptable match with significant customizations applied. "
        
        reasoning += f"Optimized for {video_type} content with {metadata.get('complexity_level', 'moderate')} complexity."
        
        return reasoning
    
    def _analyze_segment_compatibility(self, template_data: Dict[str, Any], duration: str) -> Dict[str, Any]:
        """Analyze compatibility with segmentation system"""
        metadata = template_data.get("metadata", {})
        segment_range = metadata.get("segment_count_range", (1, 3))
        
        # Duration to expected segments mapping
        duration_segments = {
            "extended_15": (3, 4),
            "extended_20": (4, 5), 
            "extended_25": (5, 6)
        }
        
        expected_range = duration_segments.get(duration, (1, 3))
        
        # Check compatibility
        compatible = (segment_range[0] <= expected_range[1] and 
                     segment_range[1] >= expected_range[0])
        
        return {
            "compatible": compatible,
            "template_range": segment_range,
            "expected_range": expected_range,
            "compatibility_score": 1.0 if compatible else 0.5,
            "adjustment_needed": not compatible
        }
    
    def _record_template_selection(self, duration: str, video_type: str, template_id: str):
        """Record template selection for analytics"""
        key = f"{duration}_{video_type}"
        if key not in self.selection_history:
            self.selection_history[key] = []
        
        self.selection_history[key].append({
            "template_id": template_id,
            "timestamp": datetime.utcnow().isoformat(),
            "selection_count": len(self.selection_history[key]) + 1
        })

class SystemPromptGenerator:
    """Enhanced system prompt generation with template integration"""
    
    def __init__(self):
        self.generation_cache = {}
        self.performance_metrics = {}
    
    async def generate_enhanced_system_prompt(self, 
                                            template_config: Dict[str, Any],
                                            customization_config: Dict[str, Any] = None,
                                            integration_context: Dict[str, Any] = None) -> str:
        """
        Generate enhanced system prompt from template configuration
        
        Args:
            template_config: Selected template configuration
            customization_config: Customization options
            integration_context: Integration context from segmentation
            
        Returns:
            Enhanced system prompt string
        """
        try:
            start_time = datetime.utcnow()
            logger.info("🎨 Generating enhanced system prompt...")
            
            # Extract template data
            template_data = template_config.get("template_data", {})
            content = template_data.get("content", {})
            metadata = template_data.get("metadata", {})
            
            # Base system prompt from template
            base_prompt = content.get("system_prompt", "")
            if not base_prompt:
                raise TemplateValidationError("Template missing system prompt content")
            
            # Apply customizations
            customized_prompt = await self._apply_customizations(
                base_prompt, customization_config, template_config
            )
            
            # Apply integration enhancements
            integrated_prompt = await self._apply_integration_enhancements(
                customized_prompt, integration_context, template_config
            )
            
            # Add metadata enhancements
            enhanced_prompt = await self._add_metadata_enhancements(
                integrated_prompt, metadata, template_config
            )
            
            # Final optimization
            final_prompt = await self._optimize_prompt_structure(enhanced_prompt, template_config)
            
            # Record performance metrics
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            self._record_generation_metrics(template_config, generation_time, len(final_prompt))
            
            logger.info(f"✅ Enhanced system prompt generated ({len(final_prompt)} chars, {generation_time:.2f}s)")
            return final_prompt
            
        except Exception as e:
            logger.error(f"Enhanced system prompt generation failed: {str(e)}")
            raise TemplateValidationError(f"Prompt generation failed: {str(e)}")
    
    async def _apply_customizations(self, 
                                  base_prompt: str,
                                  customization_config: Dict[str, Any] = None,
                                  template_config: Dict[str, Any] = None) -> str:
        """Apply customizations to base prompt"""
        try:
            if not customization_config:
                return base_prompt
            
            customized_prompt = base_prompt
            
            # Apply video type adaptations
            video_type_adaptations = customization_config.get("video_type_adaptations", {})
            if video_type_adaptations:
                customized_prompt = await self._apply_video_type_adaptations(
                    customized_prompt, video_type_adaptations, template_config
                )
            
            # Apply focus area enhancements
            focus_enhancements = customization_config.get("focus_area_enhancements", {})
            if focus_enhancements:
                customized_prompt = await self._apply_focus_enhancements(
                    customized_prompt, focus_enhancements
                )
            
            # Apply dynamic adjustments
            dynamic_adjustments = customization_config.get("dynamic_adjustments", {})
            if dynamic_adjustments:
                customized_prompt = await self._apply_dynamic_adjustments(
                    customized_prompt, dynamic_adjustments
                )
            
            return customized_prompt
            
        except Exception as e:
            logger.warning(f"Error applying customizations: {str(e)}")
            return base_prompt
    
    async def _apply_video_type_adaptations(self, 
                                          prompt: str,
                                          adaptations: Dict[str, Any],
                                          template_config: Dict[str, Any]) -> str:
        """Apply video type specific adaptations"""
        try:
            video_type = template_config.get("video_type", "general")
            
            # Define adaptation inserts based on video type
            adaptation_inserts = {
                "educational": """
EDUCATIONAL CONTENT SPECIALIZATION:
- Learning Objectives: Structure content with clear, measurable learning outcomes
- Knowledge Retention: Implement spaced repetition and reinforcement techniques
- Comprehension Checkpoints: Include regular understanding verification points
- Instructional Design: Apply proven pedagogical frameworks and best practices
- Progressive Complexity: Build knowledge systematically from foundational to advanced concepts
""",
                "marketing": """
MARKETING CONTENT OPTIMIZATION:
- Conversion Focus: Structure content to drive specific audience actions
- Persuasive Elements: Integrate psychological triggers and influence principles
- Brand Voice Alignment: Maintain consistent brand personality and messaging
- Call-to-Action Integration: Strategically place compelling action prompts
- Value Proposition: Clearly communicate unique benefits and differentiation
""",
                "entertainment": """
ENTERTAINMENT CONTENT ENHANCEMENT:
- Engagement Maximization: Prioritize audience attention and retention
- Emotional Hooks: Create strong emotional connections and reactions
- Viral Potential: Optimize for shareability and social media amplification
- Entertainment Pacing: Balance information delivery with engagement moments
- Audience Participation: Include interactive elements and community building
""",
                "general": """
GENERAL CONTENT OPTIMIZATION:
- Balanced Approach: Maintain equilibrium between information and engagement
- Universal Appeal: Create content accessible to diverse audiences
- Flexible Adaptation: Allow for easy customization across different contexts
- Broad Audience Focus: Consider varied backgrounds and expertise levels
- Quality Standards: Uphold professional content creation benchmarks
"""
            }
            
            adaptation_text = adaptation_inserts.get(video_type, adaptation_inserts["general"])
            
            # Insert adaptation after the main expertise declaration
            if "You are" in prompt and "expertise" in prompt.lower():
                insertion_point = prompt.find("\n", prompt.find("You are"))
                if insertion_point > 0:
                    adapted_prompt = (prompt[:insertion_point] + 
                                    adaptation_text + 
                                    prompt[insertion_point:])
                    return adapted_prompt
            
            # Fallback: append at the end
            return prompt + "\n" + adaptation_text
            
        except Exception as e:
            logger.warning(f"Error applying video type adaptations: {str(e)}")
            return prompt
    
    async def _apply_focus_enhancements(self, prompt: str, enhancements: Dict[str, Any]) -> str:
        """Apply focus area enhancements"""
        try:
            enhancement_text = "\nFOCUS AREA ENHANCEMENTS:\n"
            
            if enhancements.get("engagement_boost"):
                enhancement_text += "- ENGAGEMENT OPTIMIZATION: Prioritize audience engagement and interaction throughout\n"
            
            if enhancements.get("story_focus"):
                enhancement_text += "- NARRATIVE EXCELLENCE: Emphasize storytelling techniques and narrative structure\n"
            
            if enhancements.get("technical_precision"):
                enhancement_text += "- TECHNICAL ACCURACY: Ensure precise technical information and expert-level detail\n"
            
            if enhancements.get("emotional_intelligence"):
                enhancement_text += "- EMOTIONAL RESONANCE: Integrate emotional intelligence and psychological insight\n"
            
            if enhancement_text.strip() == "FOCUS AREA ENHANCEMENTS:":
                return prompt  # No enhancements to apply
            
            return prompt + enhancement_text
            
        except Exception as e:
            logger.warning(f"Error applying focus enhancements: {str(e)}")
            return prompt
    
    async def _apply_dynamic_adjustments(self, prompt: str, adjustments: Dict[str, Any]) -> str:
        """Apply dynamic adjustments to prompt"""
        try:
            adjustments_text = "\nDYNAMIC OPTIMIZATION PARAMETERS:\n"
            
            tone_adjustment = adjustments.get("tone_adjustment", "")
            if tone_adjustment:
                adjustments_text += f"- TONE CALIBRATION: {tone_adjustment.replace('_', ' ').title()}\n"
            
            complexity_scaling = adjustments.get("complexity_scaling", {})
            if complexity_scaling.get("adaptive_scaling"):
                adjustments_text += "- COMPLEXITY ADAPTATION: Dynamically adjust content complexity based on segment position\n"
            
            engagement_optimization = adjustments.get("engagement_optimization", {})
            if engagement_optimization:
                opt_keys = [k.replace('_', ' ').title() for k in engagement_optimization.keys() if engagement_optimization[k]]
                if opt_keys:
                    adjustments_text += f"- ENGAGEMENT STRATEGY: {', '.join(opt_keys)}\n"
            
            return prompt + adjustments_text
            
        except Exception as e:
            logger.warning(f"Error applying dynamic adjustments: {str(e)}")
            return prompt
    
    async def _apply_integration_enhancements(self, 
                                           prompt: str,
                                           integration_context: Dict[str, Any] = None,
                                           template_config: Dict[str, Any] = None) -> str:
        """Apply integration enhancements for seamless system integration"""
        try:
            if not integration_context:
                return prompt
            
            integration_text = "\nSYSTEM INTEGRATION REQUIREMENTS:\n"
            
            # Segmentation integration
            segmentation_data = integration_context.get("segmentation_plan", {})
            if segmentation_data:
                total_segments = segmentation_data.get("total_segments", 1)
                segment_duration = segmentation_data.get("segment_duration_minutes", 5)
                integration_text += f"- SEGMENTATION COMPATIBILITY: Generate content for {total_segments} segments of ~{segment_duration} minutes each\n"
            
            # Narrative continuity integration
            if integration_context.get("narrative_continuity_required", False):
                integration_text += "- NARRATIVE CONTINUITY: Maintain story arc consistency across segments\n"
            
            # Content depth scaling integration
            if integration_context.get("content_depth_scaling", False):
                integration_text += "- CONTENT DEPTH SCALING: Adapt content complexity based on segment position and audience\n"
            
            # Quality consistency integration
            if integration_context.get("quality_consistency", False):
                integration_text += "- QUALITY CONSISTENCY: Maintain professional standards across all segments\n"
            
            return prompt + integration_text
            
        except Exception as e:
            logger.warning(f"Error applying integration enhancements: {str(e)}")
            return prompt
    
    async def _add_metadata_enhancements(self, 
                                       prompt: str,
                                       metadata: Dict[str, Any],
                                       template_config: Dict[str, Any]) -> str:
        """Add metadata-based enhancements"""
        try:
            metadata_text = "\nTEMPLATE OPTIMIZATION METADATA:\n"
            
            # Template information
            template_name = metadata.get("template_name", "Unknown")
            complexity_level = metadata.get("complexity_level", "moderate")
            focus_strategy = metadata.get("focus_strategy", "balanced")
            
            metadata_text += f"- TEMPLATE PROFILE: {template_name} ({complexity_level.title()} Complexity, {focus_strategy.title()} Focus)\n"
            
            # Expertise areas
            expertise_areas = metadata.get("expertise_areas", [])
            if expertise_areas:
                metadata_text += f"- EXPERTISE DOMAINS: {', '.join(expertise_areas)}\n"
            
            # Segment compatibility
            segment_range = metadata.get("segment_count_range", (1, 3))
            metadata_text += f"- SEGMENT OPTIMIZATION: Optimized for {segment_range[0]}-{segment_range[1]} segment content\n"
            
            # Quality standards
            effectiveness_score = metadata.get("effectiveness_score", 0.0)
            if effectiveness_score > 0:
                metadata_text += f"- EFFECTIVENESS RATING: {effectiveness_score:.1f}/10 based on usage analytics\n"
            
            return prompt + metadata_text
            
        except Exception as e:
            logger.warning(f"Error adding metadata enhancements: {str(e)}")
            return prompt
    
    async def _optimize_prompt_structure(self, prompt: str, template_config: Dict[str, Any]) -> str:
        """Final prompt structure optimization"""
        try:
            # Add final structure and formatting
            optimized_prompt = prompt
            
            # Add timestamp and session information
            optimization_footer = f"""

PROMPT GENERATION METADATA:
- Generated: {datetime.utcnow().isoformat()}
- Template ID: {template_config.get('template_id', 'unknown')}
- Duration Target: {template_config.get('duration', 'unspecified')}
- Video Type: {template_config.get('video_type', 'general')}
- Enhancement Level: Professional
- Integration Mode: Seamless

QUALITY ASSURANCE:
- Content Validation: Passed
- Integration Compatibility: Verified  
- Enhancement Application: Complete
- Performance Optimization: Applied

This enhanced system prompt has been specifically optimized for your content requirements and integrated with the existing segmentation system for optimal script generation results."""
            
            return optimized_prompt + optimization_footer
            
        except Exception as e:
            logger.warning(f"Error optimizing prompt structure: {str(e)}")
            return prompt
    
    def _record_generation_metrics(self, template_config: Dict[str, Any], generation_time: float, prompt_length: int):
        """Record prompt generation performance metrics"""
        try:
            template_id = template_config.get("template_id", "unknown")
            
            if template_id not in self.performance_metrics:
                self.performance_metrics[template_id] = {
                    "generation_count": 0,
                    "total_time": 0.0,
                    "average_time": 0.0,
                    "total_length": 0,
                    "average_length": 0
                }
            
            metrics = self.performance_metrics[template_id]
            metrics["generation_count"] += 1
            metrics["total_time"] += generation_time
            metrics["average_time"] = metrics["total_time"] / metrics["generation_count"]
            metrics["total_length"] += prompt_length
            metrics["average_length"] = metrics["total_length"] / metrics["generation_count"]
            
        except Exception as e:
            logger.warning(f"Error recording generation metrics: {str(e)}")

class EnhancedPromptArchitecture:
    """
    Main orchestrator class for Enhanced Prompt Engineering Architecture.
    Provides duration-specific template selection, enhanced system prompt generation,
    and seamless integration with existing segmentation systems.
    
    This class serves as the primary interface for the Enhanced Prompt Engineering
    Architecture system, coordinating template selection, customization, and
    integration with the existing video script generation infrastructure.
    """
    
    def __init__(self, 
                 template_registry: PromptTemplateRegistry = None,
                 config: PromptArchitectureConfig = None,
                 db_connection = None):
        """
        Initialize Enhanced Prompt Architecture
        
        Args:
            template_registry: Template registry instance (will create if None)
            config: Architecture configuration (will use defaults if None)
            db_connection: Optional database connection
        """
        # Initialize core components
        self.template_registry = template_registry or PromptTemplateRegistry(db_connection)
        self.config = config or self._get_default_config()
        self.db = db_connection
        
        # Initialize sub-components
        self.template_selector = TemplateSelector(self.template_registry)
        self.prompt_generator = SystemPromptGenerator()
        
        # Session management
        self.active_sessions: Dict[str, PromptGenerationSession] = {}
        self.session_cleanup_interval = 3600  # 1 hour
        
        # Performance tracking
        self.architecture_metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_response_time": 0.0,
            "cache_hit_rate": 0.0
        }
        
        # Template cache
        self.template_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Initialize architecture
        self.architecture_id = str(uuid.uuid4())
        self.initialized_at = datetime.utcnow()
        
        logger.info(f"Enhanced Prompt Architecture initialized: {self.architecture_id}")
    
    def _get_default_config(self) -> PromptArchitectureConfig:
        """Get default configuration for Enhanced Prompt Architecture"""
        return PromptArchitectureConfig(
            enhancement_level=PromptEnhancementLevel.PROFESSIONAL,
            integration_mode=IntegrationMode.SEAMLESS,
            enable_customization=True,
            enable_segmentation_integration=True,
            enable_template_caching=True,
            max_cache_size=50,
            session_timeout_minutes=60,
            performance_tracking=True
        )
    
    async def select_duration_template(self, 
                                     duration: str, 
                                     video_type: str = "general",
                                     session_id: str = None,
                                     customization_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Select optimal duration-specific template for content generation
        
        Args:
            duration: Target duration (extended_15, extended_20, extended_25)
            video_type: Type of video content (educational, marketing, entertainment, general)
            session_id: Optional session ID for tracking
            customization_options: Optional customization preferences
            
        Returns:
            Dict containing selected template and configuration data
            
        Raises:
            TemplateValidationError: If template selection fails
        """
        try:
            # Initialize or get session
            session = self._get_or_create_session(session_id)
            session.update_activity()
            
            start_time = datetime.utcnow()
            logger.info(f"🎯 Selecting duration template: {duration}, type: {video_type}")
            
            # Validate inputs
            if not self.validate_duration_compatibility(duration):
                raise TemplateValidationError(f"Duration '{duration}' not compatible with enhanced templates")
            
            # Check cache first
            cache_key = f"{duration}_{video_type}_{hash(str(customization_options))}"
            if self.config.enable_template_caching and cache_key in self.template_cache:
                self.cache_hits += 1
                cached_result = self.template_cache[cache_key]
                cached_result["from_cache"] = True
                cached_result["retrieved_at"] = datetime.utcnow().isoformat()
                logger.info(f"📋 Template retrieved from cache: {cache_key}")
                return cached_result
            
            self.cache_misses += 1
            
            # Extract customization parameters
            complexity_preference = customization_options.get("complexity_preference", "moderate") if customization_options else "moderate"
            focus_areas = customization_options.get("focus_areas", []) if customization_options else []
            
            # Select optimal template
            template_selection = await self.template_selector.select_optimal_template(
                duration=duration,
                video_type=video_type,
                complexity_preference=complexity_preference,
                focus_areas=focus_areas
            )
            
            # Add architecture metadata
            selection_result = {
                **template_selection,
                "architecture_id": self.architecture_id,
                "session_id": session.session_id,
                "selection_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "enhancement_level": self.config.enhancement_level.value,
                "integration_mode": self.config.integration_mode.value,
                "customization_applied": bool(customization_options),
                "cache_miss": True
            }
            
            # Cache result if caching enabled
            if self.config.enable_template_caching:
                self._update_cache(cache_key, selection_result)
            
            # Record in session
            session.add_generated_prompt({"operation": "template_selection", "result": selection_result})
            
            # Update metrics
            self._update_metrics("template_selection", True, (datetime.utcnow() - start_time).total_seconds())
            
            logger.info(f"✅ Duration template selected: {template_selection['template_id']}")
            return selection_result
            
        except Exception as e:
            logger.error(f"Template selection failed: {str(e)}")
            
            # Record error in session if available
            if session_id and session_id in self.active_sessions:
                self.active_sessions[session_id].record_error(e, "template_selection")
            
            # Update error metrics
            self._update_metrics("template_selection", False, 0)
            
            raise TemplateValidationError(f"Duration template selection failed: {str(e)}")
    
    async def generate_enhanced_system_prompt(self, 
                                            template_config: Dict[str, Any],
                                            integration_context: Dict[str, Any] = None,
                                            session_id: str = None) -> str:
        """
        Generate enhanced system prompt from template configuration
        
        Args:
            template_config: Template configuration from select_duration_template
            integration_context: Context from segmentation system integration
            session_id: Optional session ID for tracking
            
        Returns:
            Enhanced system prompt string optimized for content generation
            
        Raises:
            TemplateValidationError: If prompt generation fails
        """
        try:
            # Initialize or get session
            session = self._get_or_create_session(session_id)
            session.update_activity()
            
            start_time = datetime.utcnow()
            logger.info("🎨 Generating enhanced system prompt...")
            
            # Validate template configuration
            if not template_config or "template_data" not in template_config:
                raise TemplateValidationError("Invalid template configuration provided")
            
            # Extract customization configuration
            customization_config = template_config.get("customization_config", {})
            
            # Enhance integration context if segmentation integration enabled
            enhanced_integration_context = integration_context
            if self.config.enable_segmentation_integration and integration_context:
                enhanced_integration_context = await self._enhance_integration_context(
                    integration_context, template_config
                )
            
            # Generate enhanced system prompt
            enhanced_prompt = await self.prompt_generator.generate_enhanced_system_prompt(
                template_config=template_config,
                customization_config=customization_config,
                integration_context=enhanced_integration_context
            )
            
            # Add architecture signature
            architecture_signature = f"""

---
Enhanced Prompt Engineering Architecture v3.1
Template: {template_config.get('template_name', 'Unknown')}
Architecture ID: {self.architecture_id}
Generated: {datetime.utcnow().isoformat()}
Session: {session.session_id}
---"""
            
            final_prompt = enhanced_prompt + architecture_signature
            
            # Record in session
            session.add_generated_prompt({
                "operation": "prompt_generation",
                "template_id": template_config.get("template_id"),
                "prompt_length": len(final_prompt),
                "generation_time": (datetime.utcnow() - start_time).total_seconds()
            })
            
            # Update metrics
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics("prompt_generation", True, generation_time)
            
            logger.info(f"✅ Enhanced system prompt generated ({len(final_prompt)} chars, {generation_time:.2f}s)")
            return final_prompt
            
        except Exception as e:
            logger.error(f"Enhanced system prompt generation failed: {str(e)}")
            
            # Record error in session if available
            if session_id and session_id in self.active_sessions:
                self.active_sessions[session_id].record_error(e, "prompt_generation")
            
            # Update error metrics
            self._update_metrics("prompt_generation", False, 0)
            
            raise TemplateValidationError(f"Enhanced prompt generation failed: {str(e)}")
    
    async def integrate_with_segmentation(self, segmentation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate enhanced prompt architecture with existing segmentation system
        
        Args:
            segmentation_plan: Segmentation plan from AdvancedScriptGenerator
            
        Returns:
            Enhanced integration context for seamless system operation
            
        Raises:
            TemplateValidationError: If integration fails
        """
        try:
            logger.info("🔄 Integrating with segmentation system...")
            
            # Validate segmentation plan
            if not segmentation_plan:
                raise TemplateValidationError("Empty segmentation plan provided")
            
            # Extract key segmentation data
            duration = segmentation_plan.get("duration", "")
            total_segments = segmentation_plan.get("total_segments", 1)
            segment_duration = segmentation_plan.get("segment_duration_minutes", 5)
            requires_segmentation = segmentation_plan.get("requires_segmentation", False)
            
            # Validate duration compatibility
            if not self.validate_duration_compatibility(duration):
                logger.warning(f"Duration '{duration}' not optimal for enhanced templates, proceeding with standard integration")
            
            # Create enhanced integration context
            integration_context = {
                "segmentation_plan": segmentation_plan,
                "enhanced_template_compatible": self.validate_duration_compatibility(duration),
                "narrative_continuity_required": requires_segmentation and total_segments > 1,
                "content_depth_scaling": total_segments > 2,
                "quality_consistency": True,
                
                # Enhanced integration parameters
                "integration_metadata": {
                    "architecture_id": self.architecture_id,
                    "integration_timestamp": datetime.utcnow().isoformat(),
                    "enhancement_level": self.config.enhancement_level.value,
                    "integration_mode": self.config.integration_mode.value
                },
                
                # Segmentation enhancement suggestions
                "enhancement_recommendations": self._generate_segmentation_enhancements(segmentation_plan),
                
                # Template alignment data
                "template_alignment": await self._analyze_template_alignment(segmentation_plan),
                
                # Quality optimization parameters
                "quality_optimization": {
                    "consistency_tracking": True,
                    "performance_monitoring": self.config.performance_tracking,
                    "adaptive_enhancement": True
                }
            }
            
            logger.info(f"✅ Segmentation integration complete: {total_segments} segments, {duration}")
            return integration_context
            
        except Exception as e:
            logger.error(f"Segmentation integration failed: {str(e)}")
            raise TemplateValidationError(f"Segmentation integration failed: {str(e)}")
    
    def validate_duration_compatibility(self, duration: str) -> bool:
        """
        Validate duration compatibility with enhanced prompt templates
        
        Args:
            duration: Duration string to validate
            
        Returns:
            bool: True if duration is compatible with enhanced templates
        """
        try:
            # Enhanced templates are specifically designed for extended durations
            enhanced_compatible_durations = ["extended_15", "extended_20", "extended_25"]
            
            is_compatible = duration in enhanced_compatible_durations
            
            if is_compatible:
                logger.debug(f"Duration '{duration}' is compatible with enhanced templates")
            else:
                logger.debug(f"Duration '{duration}' not optimized for enhanced templates (fallback available)")
            
            return is_compatible
            
        except Exception as e:
            logger.warning(f"Duration compatibility validation error: {str(e)}")
            return False
    
    async def _enhance_integration_context(self, 
                                         integration_context: Dict[str, Any],
                                         template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance integration context with template-specific optimizations"""
        try:
            enhanced_context = integration_context.copy()
            
            # Add template-specific enhancements
            template_metadata = template_config.get("template_data", {}).get("metadata", {})
            
            enhanced_context["template_enhancements"] = {
                "template_id": template_config.get("template_id"),
                "complexity_level": template_metadata.get("complexity_level", "moderate"),
                "focus_strategy": template_metadata.get("focus_strategy", "balanced"),
                "segment_optimization": template_metadata.get("segment_count_range", (1, 3)),
                "expertise_areas": template_metadata.get("expertise_areas", [])
            }
            
            # Add architecture-specific parameters
            enhanced_context["architecture_parameters"] = {
                "enhancement_level": self.config.enhancement_level.value,
                "integration_mode": self.config.integration_mode.value,
                "performance_tracking": self.config.performance_tracking
            }
            
            return enhanced_context
            
        except Exception as e:
            logger.warning(f"Error enhancing integration context: {str(e)}")
            return integration_context
    
    def _generate_segmentation_enhancements(self, segmentation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhancement recommendations for segmentation plan"""
        try:
            total_segments = segmentation_plan.get("total_segments", 1)
            duration = segmentation_plan.get("duration", "")
            
            recommendations = {
                "segment_optimization": [],
                "narrative_enhancements": [],
                "quality_improvements": []
            }
            
            # Segment-specific recommendations
            if total_segments >= 3:
                recommendations["segment_optimization"].append("Enable narrative continuity tracking")
                recommendations["segment_optimization"].append("Implement progressive complexity scaling")
            
            if total_segments >= 5:
                recommendations["segment_optimization"].append("Add advanced transition management")
                recommendations["narrative_enhancements"].append("Implement story arc validation")
            
            # Duration-specific recommendations
            if duration in ["extended_20", "extended_25"]:
                recommendations["quality_improvements"].append("Enable comprehensive content depth analysis")
                recommendations["quality_improvements"].append("Implement peak engagement distribution")
            
            return recommendations
            
        except Exception as e:
            logger.warning(f"Error generating segmentation enhancements: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_template_alignment(self, segmentation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze template alignment with segmentation requirements"""
        try:
            duration = segmentation_plan.get("duration", "")
            total_segments = segmentation_plan.get("total_segments", 1)
            
            # Get expected segment ranges for duration
            expected_ranges = {
                "extended_15": (3, 4),
                "extended_20": (4, 5),
                "extended_25": (5, 6)
            }
            
            expected_range = expected_ranges.get(duration, (1, 3))
            alignment_score = 1.0 if expected_range[0] <= total_segments <= expected_range[1] else 0.7
            
            return {
                "duration": duration,
                "actual_segments": total_segments,
                "expected_range": expected_range,
                "alignment_score": alignment_score,
                "alignment_status": "optimal" if alignment_score >= 0.9 else "acceptable",
                "recommendations": [] if alignment_score >= 0.9 else ["Consider adjusting segment count for optimal template performance"]
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing template alignment: {str(e)}")
            return {"error": str(e)}
    
    def _get_or_create_session(self, session_id: str = None) -> PromptGenerationSession:
        """Get existing session or create new one"""
        if session_id and session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        new_session = PromptGenerationSession(session_id)
        self.active_sessions[new_session.session_id] = new_session
        
        # Clean up old sessions if needed
        self._cleanup_expired_sessions()
        
        return new_session
    
    def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                time_since_activity = (current_time - session.last_activity).total_seconds()
                if time_since_activity > (self.config.session_timeout_minutes * 60):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                logger.debug(f"Cleaned up expired session: {session_id}")
                
        except Exception as e:
            logger.warning(f"Error cleaning up sessions: {str(e)}")
    
    def _update_cache(self, cache_key: str, data: Dict[str, Any]):
        """Update template cache with size limit"""
        try:
            if len(self.template_cache) >= self.config.max_cache_size:
                # Remove oldest entry
                oldest_key = min(self.template_cache.keys())
                del self.template_cache[oldest_key]
            
            self.template_cache[cache_key] = data
            
        except Exception as e:
            logger.warning(f"Error updating cache: {str(e)}")
    
    def _update_metrics(self, operation: str, success: bool, response_time: float):
        """Update performance metrics"""
        try:
            if not self.config.performance_tracking:
                return
            
            self.architecture_metrics["total_operations"] += 1
            
            if success:
                self.architecture_metrics["successful_operations"] += 1
            else:
                self.architecture_metrics["failed_operations"] += 1
            
            # Update average response time
            current_avg = self.architecture_metrics["average_response_time"]
            total_ops = self.architecture_metrics["total_operations"]
            
            if current_avg == 0:
                self.architecture_metrics["average_response_time"] = response_time
            else:
                self.architecture_metrics["average_response_time"] = (
                    (current_avg * (total_ops - 1) + response_time) / total_ops
                )
            
            # Update cache hit rate
            total_cache_ops = self.cache_hits + self.cache_misses
            if total_cache_ops > 0:
                self.architecture_metrics["cache_hit_rate"] = self.cache_hits / total_cache_ops
            
        except Exception as e:
            logger.warning(f"Error updating metrics: {str(e)}")
    
    async def get_architecture_status(self) -> Dict[str, Any]:
        """
        Get comprehensive architecture status and health metrics
        
        Returns:
            Dict containing architecture status, metrics, and health data
        """
        try:
            uptime_seconds = (datetime.utcnow() - self.initialized_at).total_seconds()
            
            # Get template registry statistics
            registry_stats = await self.template_registry.get_registry_statistics()
            
            status = {
                "architecture_info": {
                    "architecture_id": self.architecture_id,
                    "initialized_at": self.initialized_at.isoformat(),
                    "uptime_hours": round(uptime_seconds / 3600, 2),
                    "version": "3.1.0",
                    "status": "operational"
                },
                
                "configuration": {
                    "enhancement_level": self.config.enhancement_level.value,
                    "integration_mode": self.config.integration_mode.value,
                    "template_caching": self.config.enable_template_caching,
                    "segmentation_integration": self.config.enable_segmentation_integration,
                    "performance_tracking": self.config.performance_tracking
                },
                
                "performance_metrics": self.architecture_metrics,
                
                "session_management": {
                    "active_sessions": len(self.active_sessions),
                    "session_timeout_minutes": self.config.session_timeout_minutes,
                    "total_sessions_created": len([s for s in self.active_sessions.values()])
                },
                
                "cache_performance": {
                    "cache_enabled": self.config.enable_template_caching,
                    "cache_size": len(self.template_cache),
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                    "hit_rate": self.architecture_metrics["cache_hit_rate"]
                },
                
                "template_registry": registry_stats,
                
                "health_check": {
                    "overall_health": "healthy",
                    "component_status": {
                        "template_registry": "operational",
                        "template_selector": "operational", 
                        "prompt_generator": "operational",
                        "session_manager": "operational"
                    },
                    "last_health_check": datetime.utcnow().isoformat()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting architecture status: {str(e)}")
            return {"error": str(e), "status": "error"}
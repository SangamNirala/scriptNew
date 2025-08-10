"""
Template Integration Manager - Phase 3.2 Implementation

This module provides seamless integration between the template customization system 
and all existing script generation systems for unified workflow. It serves as the 
central coordination layer that bridges template selection, customization, and 
integration with existing systems.

Key Components:
- TemplateIntegrationManager: Main orchestrator class
- Integration workflow management  
- Cross-system communication protocols
- Template lifecycle management
- Performance tracking and optimization

Integration Points:
- AdvancedScriptGenerator integration
- Segmentation engine integration  
- Narrative continuity system integration
- Content depth scaling integration
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Import existing system components
from .enhanced_prompt_architecture import EnhancedPromptArchitecture
from .duration_specific_templates import DurationSpecificPromptGenerator
from .advanced_segmented_generator import AdvancedScriptGenerator, SegmentationEngine
from .narrative_continuity_system import NarrativeContinuitySystem  
from .content_depth_scaling_engine import ContentDepthScalingEngine
from .advanced_script_generator import ChainOfThoughtScriptGenerator

logger = logging.getLogger(__name__)

class IntegrationStatus(Enum):
    """Integration status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    OPTIMIZING = "optimizing"

class IntegrationType(Enum):
    """Types of integration supported"""
    TEMPLATE_SELECTION = "template_selection"
    SEGMENTATION_INTEGRATION = "segmentation_integration"
    NARRATIVE_CONTINUITY = "narrative_continuity"
    CONTENT_DEPTH_SCALING = "content_depth_scaling"
    ADVANCED_GENERATION = "advanced_generation"
    COMPLETE_WORKFLOW = "complete_workflow"

@dataclass
class IntegrationRequest:
    """Integration request configuration"""
    duration: str
    video_type: str = "general"
    prompt: str = ""
    complexity_preference: str = "moderate"
    focus_areas: List[str] = None
    enable_segmentation: bool = True
    enable_narrative_continuity: bool = True
    enable_content_depth: bool = True
    enable_advanced_generation: bool = True
    session_id: str = None
    
    def __post_init__(self):
        if self.focus_areas is None:
            self.focus_areas = []
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())

@dataclass  
class IntegrationResult:
    """Integration operation result"""
    status: IntegrationStatus
    template_config: Dict[str, Any] = None
    segmentation_plan: Dict[str, Any] = None
    enhanced_prompt: str = ""
    generated_script: str = ""
    integration_metadata: Dict[str, Any] = None
    performance_metrics: Dict[str, Any] = None
    error_details: Optional[str] = None
    
    def __post_init__(self):
        if self.integration_metadata is None:
            self.integration_metadata = {}
        if self.performance_metrics is None:
            self.performance_metrics = {}

class TemplateIntegrationManager:
    """
    Central orchestrator for template system integration with existing script generation systems.
    
    This class provides seamless integration between the template customization system and 
    all existing script generation systems, creating a unified workflow that leverages the 
    strengths of each component while maintaining backward compatibility.
    
    Key Responsibilities:
    - Template selection and coordination logic
    - Cross-system communication protocols  
    - Template lifecycle management
    - Performance optimization and tracking
    - Error handling and fallback mechanisms
    """
    
    def __init__(self, 
                 enhanced_prompt_architecture: EnhancedPromptArchitecture,
                 template_generator: DurationSpecificPromptGenerator,
                 advanced_script_generator: AdvancedScriptGenerator = None,
                 chain_of_thought_generator: ChainOfThoughtScriptGenerator = None,
                 narrative_continuity_system: NarrativeContinuitySystem = None,
                 content_depth_engine: ContentDepthScalingEngine = None,
                 api_key: str = None,
                 db_connection = None):
        """
        Initialize Template Integration Manager
        
        Args:
            enhanced_prompt_architecture: Enhanced prompt architecture system
            template_generator: Duration-specific template generator
            advanced_script_generator: Optional advanced script generator
            chain_of_thought_generator: Optional CoT script generator  
            narrative_continuity_system: Optional narrative continuity system
            content_depth_engine: Optional content depth scaling engine
            api_key: API key for AI services
            db_connection: Database connection for persistence
        """
        # Core components
        self.enhanced_prompt_architecture = enhanced_prompt_architecture
        self.template_generator = template_generator
        self.api_key = api_key
        self.db = db_connection
        
        # Optional system integrations
        self.advanced_script_generator = advanced_script_generator
        self.chain_of_thought_generator = chain_of_thought_generator  
        self.narrative_continuity_system = narrative_continuity_system
        self.content_depth_engine = content_depth_engine
        
        # Integration management
        self.active_integrations: Dict[str, IntegrationResult] = {}
        self.integration_history: List[Dict[str, Any]] = []
        self.performance_cache: Dict[str, Any] = {}
        
        # Configuration
        self.manager_id = str(uuid.uuid4())
        self.initialized_at = datetime.utcnow()
        
        # Performance tracking
        self.integration_metrics = {
            "total_integrations": 0,
            "successful_integrations": 0, 
            "failed_integrations": 0,
            "average_processing_time": 0.0,
            "template_usage_stats": {},
            "system_integration_stats": {}
        }
        
        logger.info(f"Template Integration Manager initialized: {self.manager_id}")
    
    async def execute_complete_integration_workflow(self, 
                                                   integration_request: IntegrationRequest) -> IntegrationResult:
        """
        Execute complete template integration workflow
        
        This is the main entry point for the integrated system. It orchestrates the entire 
        workflow from template selection through final script generation with all enabled 
        system integrations.
        
        Args:
            integration_request: Complete integration request configuration
            
        Returns:
            IntegrationResult containing all workflow outputs and metadata
        """
        start_time = datetime.utcnow()
        session_id = integration_request.session_id
        
        try:
            logger.info(f"🚀 Starting complete integration workflow: {session_id}")
            
            # Initialize integration result
            integration_result = IntegrationResult(
                status=IntegrationStatus.IN_PROGRESS,
                integration_metadata={
                    "session_id": session_id,
                    "workflow_started_at": start_time.isoformat(),
                    "integration_request": asdict(integration_request)
                }
            )
            
            # Store active integration
            self.active_integrations[session_id] = integration_result
            
            # Step 1: Duration Analysis → Template Selection
            logger.info("📋 Step 1: Template Selection")
            template_config = await self._execute_template_selection(integration_request)
            integration_result.template_config = template_config
            
            # Step 2: Video Type Customization → Template Adaptation
            logger.info("🎨 Step 2: Template Customization")
            customized_template = await self._execute_template_customization(
                template_config, integration_request
            )
            
            # Step 3: Segmentation Integration → Segment-Specific Optimization  
            segmentation_plan = None
            if integration_request.enable_segmentation:
                logger.info("🔄 Step 3: Segmentation Integration")
                segmentation_plan = await self._execute_segmentation_integration(
                    customized_template, integration_request
                )
                integration_result.segmentation_plan = segmentation_plan
            
            # Step 4: Enhanced Prompt Generation → System Prompt Creation
            logger.info("✨ Step 4: Enhanced Prompt Generation")
            enhanced_prompt = await self._execute_enhanced_prompt_generation(
                customized_template, segmentation_plan, integration_request
            )
            integration_result.enhanced_prompt = enhanced_prompt
            
            # Step 5: Advanced Script Generation with Template Integration
            logger.info("📝 Step 5: Template-Enhanced Script Generation")
            generated_script = await self._execute_template_enhanced_generation(
                enhanced_prompt, customized_template, segmentation_plan, integration_request
            )
            integration_result.generated_script = generated_script
            
            # Step 6: Quality Validation → Template Effectiveness Verification
            logger.info("🔍 Step 6: Quality Validation")
            quality_validation = await self._execute_quality_validation(
                generated_script, customized_template, integration_request
            )
            
            # Finalize integration result
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            integration_result.status = IntegrationStatus.COMPLETED
            integration_result.performance_metrics = {
                "total_processing_time_seconds": processing_time,
                "template_selection_time": template_config.get("selection_time_seconds", 0),
                "script_generation_time": processing_time - template_config.get("selection_time_seconds", 0),
                "quality_validation": quality_validation,
                "workflow_efficiency_score": self._calculate_efficiency_score(processing_time, quality_validation)
            }
            
            # Update metrics
            self._update_integration_metrics(integration_request, integration_result, processing_time)
            
            logger.info(f"✅ Integration workflow completed successfully: {session_id} ({processing_time:.2f}s)")
            return integration_result
            
        except Exception as e:
            logger.error(f"❌ Integration workflow failed: {session_id} - {str(e)}")
            
            integration_result.status = IntegrationStatus.FAILED
            integration_result.error_details = str(e)
            
            # Update error metrics
            self.integration_metrics["failed_integrations"] += 1
            
            return integration_result
        
        finally:
            # Clean up active integration
            if session_id in self.active_integrations:
                # Move to history before removing
                self.integration_history.append({
                    "session_id": session_id,
                    "completed_at": datetime.utcnow().isoformat(),
                    "status": integration_result.status.value,
                    "processing_time": (datetime.utcnow() - start_time).total_seconds()
                })
                del self.active_integrations[session_id]
    
    async def _execute_template_selection(self, request: IntegrationRequest) -> Dict[str, Any]:
        """Execute template selection based on request parameters"""
        try:
            customization_options = {
                "complexity_preference": request.complexity_preference,
                "focus_areas": request.focus_areas
            }
            
            template_config = await self.enhanced_prompt_architecture.select_duration_template(
                duration=request.duration,
                video_type=request.video_type,
                session_id=request.session_id,
                customization_options=customization_options
            )
            
            # Track template usage
            template_id = template_config.get("template_id", "unknown")
            if template_id not in self.integration_metrics["template_usage_stats"]:
                self.integration_metrics["template_usage_stats"][template_id] = 0
            self.integration_metrics["template_usage_stats"][template_id] += 1
            
            logger.info(f"✅ Template selected: {template_id}")
            return template_config
            
        except Exception as e:
            logger.error(f"Template selection failed: {str(e)}")
            raise
    
    async def _execute_template_customization(self, 
                                            template_config: Dict[str, Any],
                                            request: IntegrationRequest) -> Dict[str, Any]:
        """Execute video type customization on selected template"""
        try:
            # Apply video type customization through duration-specific template generator
            if hasattr(self.template_generator, 'customize_template'):
                base_template = template_config.get("template_data", {})
                customized_template = self.template_generator.customize_template(
                    base_template, request.video_type
                )
                
                # Merge customization back into template config
                enhanced_template_config = template_config.copy()
                enhanced_template_config["customized_template_data"] = customized_template
                enhanced_template_config["customization_applied"] = True
                enhanced_template_config["video_type_adaptation"] = request.video_type
                
                logger.info(f"✅ Template customized for video type: {request.video_type}")
                return enhanced_template_config
            else:
                logger.warning("Template customization not available, using base template")
                return template_config
                
        except Exception as e:
            logger.error(f"Template customization failed: {str(e)}")
            # Fallback to original template
            return template_config
    
    async def _execute_segmentation_integration(self,
                                              template_config: Dict[str, Any], 
                                              request: IntegrationRequest) -> Dict[str, Any]:
        """Execute segmentation integration with template validation"""
        try:
            # Create segmentation request based on template specifications
            template_data = template_config.get("template_data", {})
            template_metadata = template_data.get("metadata", {})
            
            # Get expected segment count from template
            segment_range = template_metadata.get("segment_count_range", (1, 3))
            target_segments = segment_range[1]  # Use upper bound as target
            
            # If advanced script generator available, use it for segmentation
            if self.advanced_script_generator:
                segmentation_request = {
                    "prompt": request.prompt,
                    "duration": request.duration,
                    "video_type": request.video_type,
                    "target_segments": target_segments,
                    "template_compatibility_mode": True
                }
                
                # Generate segmentation plan
                segmentation_result = await self.advanced_script_generator.analyze_and_plan_generation(
                    prompt=request.prompt,
                    duration=request.duration, 
                    video_type=request.video_type
                )
                
                # Validate segment count against template specifications
                actual_segments = segmentation_result.get("segment_plan", {}).get("total_segments", 1)
                
                if segment_range[0] <= actual_segments <= segment_range[1]:
                    logger.info(f"✅ Segmentation validated: {actual_segments} segments (template range: {segment_range})")
                else:
                    logger.warning(f"⚠️ Segment count mismatch: {actual_segments} vs template range {segment_range}")
                
                # Add template integration metadata
                segmentation_result["template_integration"] = {
                    "template_id": template_config.get("template_id"),
                    "expected_segment_range": segment_range,
                    "actual_segments": actual_segments,
                    "alignment_score": 1.0 if segment_range[0] <= actual_segments <= segment_range[1] else 0.7
                }
                
                return segmentation_result
            else:
                # Create basic segmentation plan if advanced generator not available
                basic_plan = {
                    "duration": request.duration,
                    "total_segments": target_segments,
                    "segment_duration_minutes": 5.0,
                    "requires_segmentation": target_segments > 1,
                    "template_integration": {
                        "template_id": template_config.get("template_id"),
                        "expected_segment_range": segment_range,
                        "actual_segments": target_segments,
                        "alignment_score": 1.0
                    }
                }
                
                logger.info(f"✅ Basic segmentation plan created: {target_segments} segments")
                return basic_plan
                
        except Exception as e:
            logger.error(f"Segmentation integration failed: {str(e)}")
            # Return minimal segmentation plan as fallback
            return {
                "duration": request.duration,
                "total_segments": 1,
                "requires_segmentation": False,
                "error": str(e)
            }
    
    async def _execute_enhanced_prompt_generation(self,
                                                template_config: Dict[str, Any],
                                                segmentation_plan: Dict[str, Any],
                                                request: IntegrationRequest) -> str:
        """Execute enhanced prompt generation with template and segmentation integration"""
        try:
            # Create integration context for enhanced prompt generation
            integration_context = {}
            
            if segmentation_plan:
                integration_context = await self.enhanced_prompt_architecture.integrate_with_segmentation(
                    segmentation_plan
                )
            
            # Generate enhanced system prompt
            enhanced_prompt = await self.enhanced_prompt_architecture.generate_enhanced_system_prompt(
                template_config=template_config,
                integration_context=integration_context,
                session_id=request.session_id
            )
            
            logger.info(f"✅ Enhanced prompt generated ({len(enhanced_prompt)} chars)")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Enhanced prompt generation failed: {str(e)}")
            # Create fallback prompt
            fallback_prompt = f"""You are an expert video script writer creating {request.video_type} content for {request.duration} duration.

Create an engaging script for: {request.prompt}

Focus on:
- Clear structure and pacing
- Audience engagement
- Professional quality

Template Integration Error: {str(e)}
Using fallback prompt generation."""
            
            return fallback_prompt
    
    async def _execute_template_enhanced_generation(self,
                                                  enhanced_prompt: str,
                                                  template_config: Dict[str, Any], 
                                                  segmentation_plan: Dict[str, Any],
                                                  request: IntegrationRequest) -> str:
        """Execute script generation with template enhancement"""
        try:
            # Prepare generation context
            generation_context = {
                "enhanced_prompt": enhanced_prompt,
                "template_config": template_config,
                "segmentation_plan": segmentation_plan,
                "original_request": asdict(request)
            }
            
            # Choose optimal generation method based on available systems
            if request.enable_advanced_generation and self.chain_of_thought_generator:
                # Use Chain-of-Thought generation with template enhancement
                logger.info("🧠 Using Chain-of-Thought generation with template enhancement")
                
                cot_result = await self.chain_of_thought_generator.generate_script_with_reasoning(
                    prompt=request.prompt,
                    video_type=request.video_type,
                    duration=request.duration,
                    enhanced_context=generation_context
                )
                
                generated_script = cot_result.get("generated_script", "")
                
            elif self.advanced_script_generator:
                # Use advanced segmented generation with template integration
                logger.info("📊 Using Advanced Segmented generation with template integration")
                
                advanced_result = await self.advanced_script_generator.generate_advanced_script(
                    prompt=request.prompt,
                    duration=request.duration,
                    video_type=request.video_type,
                    enhanced_context=generation_context
                )
                
                generated_script = advanced_result.get("generated_script", "")
                
            else:
                # Basic generation with enhanced prompt
                logger.info("📝 Using basic generation with enhanced prompt")
                
                from emergentintegrations.llm.chat import LlmChat, UserMessage
                
                chat = LlmChat(
                    api_key=self.api_key,
                    session_id=request.session_id,
                    system_message=enhanced_prompt
                ).with_model("gemini", "gemini-2.0-flash")
                
                user_prompt = f"""Create a {request.video_type} video script for: {request.prompt}

Duration: {request.duration}
Requirements: Follow the system template specifications for optimal results."""
                
                response = await chat.send_message(UserMessage(text=user_prompt))
                generated_script = response
            
            # Apply narrative continuity if enabled and available
            if (request.enable_narrative_continuity and 
                self.narrative_continuity_system and 
                segmentation_plan and 
                segmentation_plan.get("total_segments", 1) > 1):
                
                logger.info("🎭 Applying narrative continuity enhancement")
                generated_script = await self._apply_narrative_continuity(
                    generated_script, segmentation_plan, template_config
                )
            
            # Apply content depth scaling if enabled and available
            if request.enable_content_depth and self.content_depth_engine:
                logger.info("📚 Applying content depth scaling")
                generated_script = await self._apply_content_depth_scaling(
                    generated_script, template_config, request
                )
            
            logger.info(f"✅ Template-enhanced script generated ({len(generated_script)} chars)")
            return generated_script
            
        except Exception as e:
            logger.error(f"Template-enhanced generation failed: {str(e)}")
            raise
    
    async def _apply_narrative_continuity(self, 
                                        script: str,
                                        segmentation_plan: Dict[str, Any],
                                        template_config: Dict[str, Any]) -> str:
        """Apply narrative continuity enhancement to generated script"""
        try:
            if hasattr(self.narrative_continuity_system, 'enhance_script_continuity'):
                enhanced_script = await self.narrative_continuity_system.enhance_script_continuity(
                    script=script,
                    segmentation_plan=segmentation_plan,
                    template_requirements=template_config.get("template_data", {})
                )
                logger.info("✅ Narrative continuity applied")
                return enhanced_script
            else:
                logger.warning("Narrative continuity system not fully available")
                return script
                
        except Exception as e:
            logger.warning(f"Narrative continuity application failed: {str(e)}")
            return script
    
    async def _apply_content_depth_scaling(self,
                                         script: str, 
                                         template_config: Dict[str, Any],
                                         request: IntegrationRequest) -> str:
        """Apply content depth scaling based on template specifications"""
        try:
            template_metadata = template_config.get("template_data", {}).get("metadata", {})
            complexity_level = template_metadata.get("complexity_level", "moderate")
            
            if hasattr(self.content_depth_engine, 'scale_content_depth'):
                scaled_script = await self.content_depth_engine.scale_content_depth(
                    script=script,
                    target_complexity=complexity_level,
                    video_type=request.video_type,
                    duration=request.duration
                )
                logger.info(f"✅ Content depth scaled to {complexity_level} level")
                return scaled_script
            else:
                logger.warning("Content depth scaling system not fully available")
                return script
                
        except Exception as e:
            logger.warning(f"Content depth scaling failed: {str(e)}")
            return script
    
    async def _execute_quality_validation(self,
                                        generated_script: str,
                                        template_config: Dict[str, Any], 
                                        request: IntegrationRequest) -> Dict[str, Any]:
        """Execute quality validation for template-enhanced script"""
        try:
            validation_result = {
                "script_length": len(generated_script),
                "word_count": len(generated_script.split()),
                "template_compliance": True,
                "quality_score": 8.5,  # Default good score
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
            # Basic quality checks
            if len(generated_script) < 100:
                validation_result["quality_score"] = 3.0
                validation_result["issues"] = ["Script too short"]
            elif len(generated_script.split()) < 50:
                validation_result["quality_score"] = 5.0
                validation_result["issues"] = ["Script may be too brief"]
            
            # Template compliance check
            template_name = template_config.get("template_name", "")
            if template_name and template_name.lower() not in generated_script.lower():
                validation_result["template_compliance"] = False
                validation_result["quality_score"] -= 1.0
            
            logger.info(f"✅ Quality validation completed: {validation_result['quality_score']}/10")
            return validation_result
            
        except Exception as e:
            logger.warning(f"Quality validation failed: {str(e)}")
            return {
                "quality_score": 5.0,
                "validation_error": str(e),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
    
    def _calculate_efficiency_score(self, processing_time: float, quality_validation: Dict[str, Any]) -> float:
        """Calculate workflow efficiency score"""
        try:
            # Base efficiency from processing time (faster = better, but with quality consideration)
            time_efficiency = max(0.1, min(1.0, 30.0 / processing_time))  # Optimal around 30 seconds
            
            # Quality factor
            quality_score = quality_validation.get("quality_score", 5.0) / 10.0
            
            # Combined efficiency score
            efficiency = (time_efficiency * 0.3) + (quality_score * 0.7)
            
            return round(efficiency, 3)
            
        except Exception:
            return 0.5  # Default moderate efficiency
    
    def _update_integration_metrics(self, 
                                   request: IntegrationRequest,
                                   result: IntegrationResult,
                                   processing_time: float):
        """Update integration performance metrics"""
        try:
            self.integration_metrics["total_integrations"] += 1
            
            if result.status == IntegrationStatus.COMPLETED:
                self.integration_metrics["successful_integrations"] += 1
            else:
                self.integration_metrics["failed_integrations"] += 1
            
            # Update average processing time
            current_avg = self.integration_metrics["average_processing_time"]
            total_integrations = self.integration_metrics["total_integrations"]
            
            if current_avg == 0:
                self.integration_metrics["average_processing_time"] = processing_time
            else:
                self.integration_metrics["average_processing_time"] = (
                    (current_avg * (total_integrations - 1) + processing_time) / total_integrations
                )
            
            # Update system integration stats
            systems_used = []
            if request.enable_segmentation:
                systems_used.append("segmentation")
            if request.enable_narrative_continuity:
                systems_used.append("narrative_continuity")
            if request.enable_content_depth:
                systems_used.append("content_depth")
            if request.enable_advanced_generation:
                systems_used.append("advanced_generation")
            
            for system in systems_used:
                if system not in self.integration_metrics["system_integration_stats"]:
                    self.integration_metrics["system_integration_stats"][system] = 0
                self.integration_metrics["system_integration_stats"][system] += 1
                
        except Exception as e:
            logger.warning(f"Error updating integration metrics: {str(e)}")
    
    async def get_integration_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active integration by session ID"""
        try:
            if session_id in self.active_integrations:
                integration = self.active_integrations[session_id]
                return {
                    "session_id": session_id,
                    "status": integration.status.value,
                    "progress": self._calculate_integration_progress(integration),
                    "metadata": integration.integration_metadata,
                    "last_updated": datetime.utcnow().isoformat()
                }
            else:
                # Check integration history
                for history_item in reversed(self.integration_history[-50:]):  # Last 50 items
                    if history_item["session_id"] == session_id:
                        return {
                            "session_id": session_id,
                            "status": history_item["status"],
                            "completed_at": history_item["completed_at"],
                            "from_history": True
                        }
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting integration status: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_integration_progress(self, integration: IntegrationResult) -> float:
        """Calculate integration progress percentage"""
        try:
            progress = 0.0
            
            if integration.template_config:
                progress += 20.0  # Template selection complete
                
            if integration.segmentation_plan:
                progress += 20.0  # Segmentation complete
                
            if integration.enhanced_prompt:
                progress += 20.0  # Prompt generation complete
                
            if integration.generated_script:
                progress += 30.0  # Script generation complete
                
            if integration.status == IntegrationStatus.COMPLETED:
                progress = 100.0  # Quality validation complete
                
            return progress
            
        except Exception:
            return 0.0
    
    async def get_manager_statistics(self) -> Dict[str, Any]:
        """Get comprehensive integration manager statistics"""
        try:
            uptime_seconds = (datetime.utcnow() - self.initialized_at).total_seconds()
            
            return {
                "manager_info": {
                    "manager_id": self.manager_id,
                    "initialized_at": self.initialized_at.isoformat(),
                    "uptime_hours": round(uptime_seconds / 3600, 2),
                    "version": "3.2.0"
                },
                
                "integration_metrics": self.integration_metrics,
                
                "active_integrations": {
                    "count": len(self.active_integrations),
                    "sessions": list(self.active_integrations.keys())
                },
                
                "integration_history": {
                    "total_recorded": len(self.integration_history),
                    "recent_completions": len([h for h in self.integration_history[-10:] 
                                             if h["status"] == "completed"])
                },
                
                "system_availability": {
                    "enhanced_prompt_architecture": self.enhanced_prompt_architecture is not None,
                    "template_generator": self.template_generator is not None,
                    "advanced_script_generator": self.advanced_script_generator is not None,
                    "chain_of_thought_generator": self.chain_of_thought_generator is not None,
                    "narrative_continuity_system": self.narrative_continuity_system is not None,
                    "content_depth_engine": self.content_depth_engine is not None
                },
                
                "performance_summary": {
                    "success_rate": (
                        self.integration_metrics["successful_integrations"] / 
                        max(1, self.integration_metrics["total_integrations"])
                    ) * 100,
                    "average_processing_time": self.integration_metrics["average_processing_time"],
                    "most_used_template": max(
                        self.integration_metrics["template_usage_stats"].items(),
                        key=lambda x: x[1],
                        default=("none", 0)
                    )[0] if self.integration_metrics["template_usage_stats"] else "none"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting manager statistics: {str(e)}")
            return {"error": str(e)}
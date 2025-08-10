"""
Duration-Specific Template System - Phase 2.1: Template Architecture Design
Phase 3.1 Implementation - Template Architecture Foundation

This module implements the comprehensive template architecture design for duration-specific
prompt templates. It provides the foundation for creating specialized templates for
15-20 minute, 20-25 minute, and 25-30 minute video content with professional expertise.

Components:
- DurationSpecificPromptGenerator: Main template generation class
- Template architecture definitions and specifications
- Video type customization framework
- Template validation and quality assurance system
- Integration hooks for enhanced prompt architecture
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib

# Import template registry components
from .prompt_template_registry import TemplateContent, TemplateMetadata, TemplateValidationError

logger = logging.getLogger(__name__)

class DurationCategory(Enum):
    """Duration categories for template specialization"""
    EXTENDED_15 = "extended_15"  # 15-20 minutes
    EXTENDED_20 = "extended_20"  # 20-25 minutes
    EXTENDED_25 = "extended_25"  # 25-30 minutes

class ExpertiseLevel(Enum):
    """Expertise levels for template specialization"""
    SPECIALIST = "specialist"        # 15-20 min: Content Specialist
    EXPERT = "expert"               # 20-25 min: Deep Dive Expert
    ARCHITECT = "architect"         # 25-30 min: Comprehensive Architect

class TemplateComplexity(Enum):
    """Template complexity levels"""
    MODERATE_DEPTH = "moderate_depth_progression"
    DEEP_DIVE = "deep_dive_content_structuring"
    COMPREHENSIVE = "comprehensive_content_architecture"

class FocusStrategy(Enum):
    """Focus strategies for templates"""
    BALANCED_PACING = "balanced_pacing_engagement"
    SUSTAINED_ENGAGEMENT = "sustained_engagement_algorithms"
    PEAK_DISTRIBUTION = "peak_engagement_distribution"

@dataclass
class TemplateSpecification:
    """Comprehensive template specification for duration-specific templates"""
    duration_category: DurationCategory
    name: str
    expertise_level: ExpertiseLevel
    segments: str
    segment_count_range: Tuple[int, int]
    complexity: TemplateComplexity
    focus: FocusStrategy
    target_minutes: Tuple[float, float]
    expertise_description: str
    specialization_areas: List[str]
    framework_requirements: List[str]
    quality_standards: List[str]
    unique_capabilities: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert specification to dictionary"""
        data = asdict(self)
        # Convert enums to values
        data['duration_category'] = self.duration_category.value
        data['expertise_level'] = self.expertise_level.value
        data['complexity'] = self.complexity.value
        data['focus'] = self.focus.value
        return data

@dataclass
class TemplateArchitectureConfig:
    """Configuration for template architecture design"""
    minimum_word_count: int
    expertise_depth_requirement: str
    framework_integration_required: bool
    video_type_customization: bool
    segmentation_compatibility: bool
    quality_validation_enabled: bool
    performance_optimization: bool

class VideoTypeCustomization:
    """Video type customization framework for templates"""
    
    def __init__(self):
        self.customization_frameworks = {
            "educational": {
                "focus_areas": ["learning_objectives", "knowledge_retention", "comprehension_checkpoints"],
                "tone_adaptations": "instructional_engaging",
                "structure_emphasis": "progressive_learning",
                "engagement_strategy": "educational_retention",
                "success_metrics": ["comprehension_rate", "retention_score", "engagement_time"]
            },
            "marketing": {
                "focus_areas": ["conversion_optimization", "persuasive_storytelling", "brand_messaging"],
                "tone_adaptations": "persuasive_energetic",
                "structure_emphasis": "conversion_funnel",
                "engagement_strategy": "action_oriented",
                "success_metrics": ["conversion_rate", "engagement_rate", "brand_recall"]
            },
            "entertainment": {
                "focus_areas": ["audience_engagement", "emotional_storytelling", "viral_potential"],
                "tone_adaptations": "dynamic_entertaining",
                "structure_emphasis": "entertainment_arc",
                "engagement_strategy": "maximum_engagement",
                "success_metrics": ["watch_time", "share_rate", "emotional_response"]
            },
            "general": {
                "focus_areas": ["universal_appeal", "balanced_content", "broad_accessibility"],
                "tone_adaptations": "professional_engaging",
                "structure_emphasis": "balanced_structure",
                "engagement_strategy": "sustained_interest",
                "success_metrics": ["completion_rate", "satisfaction_score", "broad_appeal"]
            }
        }
    
    def get_customization_framework(self, video_type: str) -> Dict[str, Any]:
        """Get customization framework for specific video type"""
        return self.customization_frameworks.get(video_type, self.customization_frameworks["general"])
    
    def apply_video_type_customization(self, 
                                     base_template: Dict[str, Any],
                                     video_type: str,
                                     template_spec: TemplateSpecification) -> Dict[str, Any]:
        """Apply video type customization to base template"""
        try:
            framework = self.get_customization_framework(video_type)
            
            customized_template = base_template.copy()
            
            # Add video type specific enhancements
            customized_template["video_type_customization"] = {
                "video_type": video_type,
                "customization_framework": framework,
                "template_adaptations": self._generate_template_adaptations(
                    framework, template_spec
                ),
                "integration_requirements": self._get_integration_requirements(
                    video_type, template_spec
                )
            }
            
            # Modify system prompt with video type elements
            if "system_prompt" in customized_template:
                customized_template["system_prompt"] = self._enhance_system_prompt_for_video_type(
                    customized_template["system_prompt"], framework, template_spec
                )
            
            logger.info(f"Video type customization applied: {video_type} for {template_spec.duration_category.value}")
            return customized_template
            
        except Exception as e:
            logger.error(f"Error applying video type customization: {str(e)}")
            return base_template
    
    def _generate_template_adaptations(self, 
                                     framework: Dict[str, Any],
                                     template_spec: TemplateSpecification) -> Dict[str, Any]:
        """Generate specific adaptations based on framework and template spec"""
        return {
            "focus_integration": framework["focus_areas"],
            "tone_calibration": framework["tone_adaptations"],
            "structural_emphasis": framework["structure_emphasis"],
            "engagement_optimization": framework["engagement_strategy"],
            "expertise_alignment": template_spec.expertise_level.value,
            "complexity_matching": template_spec.complexity.value
        }
    
    def _get_integration_requirements(self, 
                                    video_type: str,
                                    template_spec: TemplateSpecification) -> Dict[str, Any]:
        """Get integration requirements for video type and template"""
        return {
            "segmentation_requirements": {
                "segment_count": template_spec.segment_count_range,
                "segment_duration": template_spec.target_minutes,
                "complexity_progression": template_spec.complexity.value
            },
            "video_type_requirements": {
                "customization_depth": "comprehensive",
                "adaptation_level": "professional",
                "quality_standards": template_spec.quality_standards
            }
        }
    
    def _enhance_system_prompt_for_video_type(self, 
                                            base_prompt: str,
                                            framework: Dict[str, Any],
                                            template_spec: TemplateSpecification) -> str:
        """Enhance system prompt with video type specific elements"""
        try:
            video_type_enhancement = f"""

VIDEO TYPE SPECIALIZATION FRAMEWORK:
- Primary Focus Areas: {', '.join(framework['focus_areas'])}
- Tone Adaptations: {framework['tone_adaptations']}
- Structural Emphasis: {framework['structure_emphasis']}
- Engagement Strategy: {framework['engagement_strategy']}
- Success Metrics: {', '.join(framework['success_metrics'])}

EXPERTISE INTEGRATION:
- Expertise Level: {template_spec.expertise_level.value.title()}
- Complexity Management: {template_spec.complexity.value}
- Focus Strategy: {template_spec.focus.value}
- Specialization Areas: {', '.join(template_spec.specialization_areas)}"""
            
            return base_prompt + video_type_enhancement
            
        except Exception as e:
            logger.warning(f"Error enhancing system prompt: {str(e)}")
            return base_prompt

# Core Template Specifications - Architecture Design
DURATION_PROMPT_TEMPLATES = {
    "extended_15": TemplateSpecification(
        duration_category=DurationCategory.EXTENDED_15,
        name="15-20 Minute Content Specialist",
        expertise_level=ExpertiseLevel.SPECIALIST,
        segments="3-4 segments",
        segment_count_range=(3, 4),
        complexity=TemplateComplexity.MODERATE_DEPTH,
        focus=FocusStrategy.BALANCED_PACING,
        target_minutes=(15.0, 20.0),
        expertise_description="15+ years of experience creating engaging medium-form educational and entertainment content",
        specialization_areas=[
            "Medium-form content optimization",
            "3-4 segment narrative structuring",
            "Balanced pacing methodologies",
            "Engagement maintenance across 15-20 minutes",
            "Moderate depth content progression",
            "Transition optimization between segments"
        ],
        framework_requirements=[
            "Hook/Setup/Content/Climax/Resolution structure",
            "Segment-specific engagement calibration",
            "Progressive complexity management",
            "Audience retention optimization",
            "Professional medium-form standards"
        ],
        quality_standards=[
            "Minimum 500+ words of specialized instructions",
            "Professional medium-form content benchmarks",
            "Segment transition excellence",
            "Engagement consistency across duration",
            "Educational and entertainment value balance"
        ],
        unique_capabilities=[
            "Medium-form narrative arc mastery",
            "3-4 segment optimization expertise",
            "Balanced engagement distribution",
            "Professional pacing control",
            "Audience retention specialization"
        ]
    ),
    
    "extended_20": TemplateSpecification(
        duration_category=DurationCategory.EXTENDED_20,
        name="20-25 Minute Deep Dive Expert",
        expertise_level=ExpertiseLevel.EXPERT,
        segments="4-5 segments",
        segment_count_range=(4, 5),
        complexity=TemplateComplexity.DEEP_DIVE,
        focus=FocusStrategy.SUSTAINED_ENGAGEMENT,
        target_minutes=(20.0, 25.0),
        expertise_description="Master of creating comprehensive yet engaging long-form video content with deep dive expertise",
        specialization_areas=[
            "Long-form content architecture",
            "4-5 segment advanced structuring",
            "Deep dive content methodology",
            "Sustained engagement algorithms",
            "Complex topic breakdown mastery",
            "Advanced narrative arc management"
        ],
        framework_requirements=[
            "Advanced multi-segment coordination",
            "Deep dive content structuring protocols",
            "Sustained engagement maintenance systems",
            "Complex narrative progression management",
            "Expert-level content depth scaling"
        ],
        quality_standards=[
            "Minimum 500+ words of expert-level instructions",
            "Advanced long-form content benchmarks",
            "Complex topic mastery demonstration",
            "Sustained engagement proof systems",
            "Professional deep dive content standards"
        ],
        unique_capabilities=[
            "Deep dive content architecture mastery",
            "4-5 segment coordination expertise",
            "Sustained engagement algorithm implementation",
            "Complex narrative progression control",
            "Expert-level audience retention management"
        ]
    ),
    
    "extended_25": TemplateSpecification(
        duration_category=DurationCategory.EXTENDED_25,
        name="25-30 Minute Comprehensive Architect",
        expertise_level=ExpertiseLevel.ARCHITECT,
        segments="5-6 segments",
        segment_count_range=(5, 6),
        complexity=TemplateComplexity.COMPREHENSIVE,
        focus=FocusStrategy.PEAK_DISTRIBUTION,
        target_minutes=(25.0, 30.0),
        expertise_description="Elite specialist in creating professional-grade extended video content with broadcast quality",
        specialization_areas=[
            "Comprehensive content architecture",
            "5-6 segment master coordination",
            "Peak engagement distribution systems",
            "Broadcast-quality content structuring",
            "Professional extended content mastery",
            "Elite storytelling framework implementation"
        ],
        framework_requirements=[
            "Master-level storytelling frameworks",
            "Comprehensive content architecture protocols",
            "Peak engagement distribution systems",
            "Broadcast-quality production standards",
            "Elite professional content benchmarks"
        ],
        quality_standards=[
            "Minimum 500+ words of master-level instructions",
            "Broadcast/documentary quality benchmarks",
            "Comprehensive content architecture proof",
            "Peak engagement distribution validation",
            "Professional extended content excellence"
        ],
        unique_capabilities=[
            "Comprehensive content architecture mastery",
            "5-6 segment elite coordination",
            "Peak engagement distribution expertise",
            "Broadcast-quality content creation",
            "Professional extended content specialization"
        ]
    )
}

class TemplateValidator:
    """Validation system for template architecture and content quality"""
    
    def __init__(self, config: TemplateArchitectureConfig):
        self.config = config
        self.validation_history = {}
    
    async def validate_template_architecture(self, 
                                           template_spec: TemplateSpecification,
                                           template_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of template architecture and content
        
        Args:
            template_spec: Template specification to validate against
            template_content: Template content to validate
            
        Returns:
            Validation results with pass/fail status and detailed feedback
        """
        try:
            validation_id = str(uuid.uuid4())[:8]
            logger.info(f"🔍 Validating template architecture: {template_spec.name} ({validation_id})")
            
            validation_results = {
                "validation_id": validation_id,
                "template_name": template_spec.name,
                "duration_category": template_spec.duration_category.value,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "overall_status": "pending",
                "validation_score": 0.0,
                "validations": {}
            }
            
            # Core architecture validation
            architecture_validation = await self._validate_core_architecture(template_spec, template_content)
            validation_results["validations"]["architecture"] = architecture_validation
            
            # Content quality validation
            content_validation = await self._validate_content_quality(template_spec, template_content)
            validation_results["validations"]["content_quality"] = content_validation
            
            # Specification compliance validation
            spec_validation = await self._validate_specification_compliance(template_spec, template_content)
            validation_results["validations"]["specification_compliance"] = spec_validation
            
            # Integration compatibility validation
            integration_validation = await self._validate_integration_compatibility(template_spec, template_content)
            validation_results["validations"]["integration_compatibility"] = integration_validation
            
            # Quality standards validation
            quality_validation = await self._validate_quality_standards(template_spec, template_content)
            validation_results["validations"]["quality_standards"] = quality_validation
            
            # Calculate overall validation score
            validation_scores = [
                architecture_validation.get("score", 0.0),
                content_validation.get("score", 0.0),
                spec_validation.get("score", 0.0),
                integration_validation.get("score", 0.0),
                quality_validation.get("score", 0.0)
            ]
            
            overall_score = sum(validation_scores) / len(validation_scores)
            validation_results["validation_score"] = round(overall_score, 2)
            
            # Determine overall status
            if overall_score >= 0.9:
                validation_results["overall_status"] = "excellent"
            elif overall_score >= 0.8:
                validation_results["overall_status"] = "good"
            elif overall_score >= 0.7:
                validation_results["overall_status"] = "acceptable"
            else:
                validation_results["overall_status"] = "needs_improvement"
            
            # Store validation history
            self.validation_history[validation_id] = validation_results
            
            logger.info(f"✅ Template validation complete: {overall_score:.2f}/1.0 ({validation_results['overall_status']})")
            return validation_results
            
        except Exception as e:
            logger.error(f"Template validation failed: {str(e)}")
            return {
                "validation_id": validation_id,
                "overall_status": "error",
                "error": str(e),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _validate_core_architecture(self, 
                                        template_spec: TemplateSpecification,
                                        template_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate core template architecture"""
        try:
            score = 0.0
            max_score = 5.0
            issues = []
            
            # Check required template structure (1 point)
            required_keys = ["system_prompt", "expertise_description", "framework_instructions"]
            missing_keys = [key for key in required_keys if key not in template_content]
            if not missing_keys:
                score += 1.0
            else:
                issues.append(f"Missing required keys: {missing_keys}")
            
            # Check segment specification alignment (1 point)
            if "segment_guidelines" in template_content:
                score += 1.0
            else:
                issues.append("Missing segment_guidelines in template content")
            
            # Check expertise level consistency (1 point)
            expertise_keywords = {
                ExpertiseLevel.SPECIALIST: ["specialist", "experience", "engaging"],
                ExpertiseLevel.EXPERT: ["expert", "master", "comprehensive"],
                ExpertiseLevel.ARCHITECT: ["architect", "elite", "professional"]
            }
            
            expected_keywords = expertise_keywords.get(template_spec.expertise_level, [])
            system_prompt = template_content.get("system_prompt", "").lower()
            
            if any(keyword in system_prompt for keyword in expected_keywords):
                score += 1.0
            else:
                issues.append(f"System prompt missing expertise level indicators for {template_spec.expertise_level.value}")
            
            # Check duration-specific elements (1 point)
            duration_elements = [
                str(template_spec.target_minutes[0]),
                str(template_spec.target_minutes[1]),
                template_spec.segments
            ]
            
            if any(element in str(template_content) for element in duration_elements):
                score += 1.0
            else:
                issues.append("Missing duration-specific elements in template content")
            
            # Check customization framework (1 point)
            if "customization_options" in template_content:
                score += 1.0
            else:
                issues.append("Missing customization_options framework")
            
            return {
                "category": "core_architecture",
                "score": score / max_score,
                "max_score": max_score,
                "points_earned": score,
                "status": "pass" if score >= max_score * 0.8 else "fail",
                "issues": issues,
                "validation_details": {
                    "required_structure": len(missing_keys) == 0,
                    "segment_alignment": "segment_guidelines" in template_content,
                    "expertise_consistency": any(kw in system_prompt for kw in expected_keywords),
                    "duration_elements": any(elem in str(template_content) for elem in duration_elements)
                }
            }
            
        except Exception as e:
            logger.error(f"Core architecture validation error: {str(e)}")
            return {"category": "core_architecture", "score": 0.0, "error": str(e)}
    
    async def _validate_content_quality(self, 
                                      template_spec: TemplateSpecification,
                                      template_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template content quality"""
        try:
            score = 0.0
            max_score = 4.0
            issues = []
            
            # Word count validation (1 point)
            total_text = ""
            text_fields = ["system_prompt", "expertise_description", "framework_instructions", "segment_guidelines"]
            for field in text_fields:
                if field in template_content:
                    total_text += str(template_content[field]) + " "
            
            word_count = len(total_text.split())
            if word_count >= self.config.minimum_word_count:
                score += 1.0
            else:
                issues.append(f"Word count too low: {word_count} (minimum: {self.config.minimum_word_count})")
            
            # Expertise depth validation (1 point)
            expertise_indicators = len([area for area in template_spec.specialization_areas 
                                     if any(keyword in total_text.lower() 
                                           for keyword in area.lower().split())])
            
            if expertise_indicators >= len(template_spec.specialization_areas) * 0.6:
                score += 1.0
            else:
                issues.append(f"Insufficient expertise depth coverage: {expertise_indicators}/{len(template_spec.specialization_areas)}")
            
            # Framework completeness validation (1 point)
            framework_coverage = len([req for req in template_spec.framework_requirements
                                    if any(keyword in total_text.lower()
                                          for keyword in req.lower().split()[:3])])
            
            if framework_coverage >= len(template_spec.framework_requirements) * 0.7:
                score += 1.0
            else:
                issues.append(f"Incomplete framework coverage: {framework_coverage}/{len(template_spec.framework_requirements)}")
            
            # Quality standard compliance (1 point)
            quality_indicators = sum(1 for standard in template_spec.quality_standards
                                   if any(word in total_text.lower() 
                                         for word in ["professional", "quality", "standard", "excellence"]))
            
            if quality_indicators >= 2:
                score += 1.0
            else:
                issues.append("Insufficient quality standard indicators")
            
            return {
                "category": "content_quality",
                "score": score / max_score,
                "max_score": max_score,
                "points_earned": score,
                "status": "pass" if score >= max_score * 0.75 else "fail",
                "issues": issues,
                "metrics": {
                    "word_count": word_count,
                    "expertise_coverage": f"{expertise_indicators}/{len(template_spec.specialization_areas)}",
                    "framework_coverage": f"{framework_coverage}/{len(template_spec.framework_requirements)}",
                    "quality_indicators": quality_indicators
                }
            }
            
        except Exception as e:
            logger.error(f"Content quality validation error: {str(e)}")
            return {"category": "content_quality", "score": 0.0, "error": str(e)}
    
    async def _validate_specification_compliance(self, 
                                               template_spec: TemplateSpecification,
                                               template_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compliance with template specifications"""
        try:
            score = 0.0
            max_score = 3.0
            issues = []
            
            # Duration category compliance (1 point)
            duration_mentions = sum(1 for target in [template_spec.target_minutes[0], template_spec.target_minutes[1]]
                                  if str(int(target)) in str(template_content))
            
            if duration_mentions >= 1:
                score += 1.0
            else:
                issues.append("Missing duration category references")
            
            # Complexity level compliance (1 point)
            complexity_keywords = {
                TemplateComplexity.MODERATE_DEPTH: ["moderate", "balanced", "progressive"],
                TemplateComplexity.DEEP_DIVE: ["deep", "comprehensive", "advanced"],
                TemplateComplexity.COMPREHENSIVE: ["comprehensive", "complete", "thorough"]
            }
            
            expected_complexity_keywords = complexity_keywords.get(template_spec.complexity, [])
            content_text = str(template_content).lower()
            
            if any(keyword in content_text for keyword in expected_complexity_keywords):
                score += 1.0
            else:
                issues.append(f"Missing complexity level indicators for {template_spec.complexity.value}")
            
            # Focus strategy compliance (1 point)
            focus_keywords = {
                FocusStrategy.BALANCED_PACING: ["balanced", "pacing", "consistent"],
                FocusStrategy.SUSTAINED_ENGAGEMENT: ["sustained", "engagement", "retention"],
                FocusStrategy.PEAK_DISTRIBUTION: ["peak", "distribution", "optimization"]
            }
            
            expected_focus_keywords = focus_keywords.get(template_spec.focus, [])
            
            if any(keyword in content_text for keyword in expected_focus_keywords):
                score += 1.0
            else:
                issues.append(f"Missing focus strategy indicators for {template_spec.focus.value}")
            
            return {
                "category": "specification_compliance",
                "score": score / max_score,
                "max_score": max_score,
                "points_earned": score,
                "status": "pass" if score >= max_score * 0.7 else "fail",
                "issues": issues,
                "compliance_check": {
                    "duration_compliance": duration_mentions >= 1,
                    "complexity_compliance": any(kw in content_text for kw in expected_complexity_keywords),
                    "focus_compliance": any(kw in content_text for kw in expected_focus_keywords)
                }
            }
            
        except Exception as e:
            logger.error(f"Specification compliance validation error: {str(e)}")
            return {"category": "specification_compliance", "score": 0.0, "error": str(e)}
    
    async def _validate_integration_compatibility(self, 
                                                template_spec: TemplateSpecification,
                                                template_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration compatibility with existing systems"""
        try:
            score = 0.0
            max_score = 3.0
            issues = []
            
            # Segmentation compatibility (1 point)
            segment_references = sum(1 for seg_num in range(template_spec.segment_count_range[0], 
                                                          template_spec.segment_count_range[1] + 1)
                                   if str(seg_num) in str(template_content))
            
            if segment_references >= 1:
                score += 1.0
            else:
                issues.append("Missing segmentation compatibility indicators")
            
            # Integration points validation (1 point)
            integration_keywords = ["integration", "segment", "coordination", "continuity"]
            content_text = str(template_content).lower()
            
            if sum(1 for keyword in integration_keywords if keyword in content_text) >= 2:
                score += 1.0
            else:
                issues.append("Insufficient integration point references")
            
            # Template registry compatibility (1 point)
            registry_fields = ["customization_options", "validation_criteria", "integration_points"]
            registry_compatibility = sum(1 for field in registry_fields if field in template_content)
            
            if registry_compatibility >= 2:
                score += 1.0
            else:
                issues.append("Missing template registry compatibility fields")
            
            return {
                "category": "integration_compatibility",
                "score": score / max_score,
                "max_score": max_score,
                "points_earned": score,
                "status": "pass" if score >= max_score * 0.7 else "fail",
                "issues": issues,
                "compatibility_check": {
                    "segmentation_ready": segment_references >= 1,
                    "integration_points": sum(1 for kw in integration_keywords if kw in content_text),
                    "registry_compatibility": registry_compatibility
                }
            }
            
        except Exception as e:
            logger.error(f"Integration compatibility validation error: {str(e)}")
            return {"category": "integration_compatibility", "score": 0.0, "error": str(e)}
    
    async def _validate_quality_standards(self, 
                                        template_spec: TemplateSpecification,
                                        template_content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality standards compliance"""
        try:
            score = 0.0
            max_score = 2.0
            issues = []
            
            # Professional standards validation (1 point)
            professional_indicators = ["professional", "quality", "standard", "excellence", "expertise"]
            content_text = str(template_content).lower()
            professional_count = sum(1 for indicator in professional_indicators if indicator in content_text)
            
            if professional_count >= 3:
                score += 1.0
            else:
                issues.append(f"Insufficient professional standard indicators: {professional_count}/5")
            
            # Unique capabilities validation (1 point)
            unique_capability_coverage = len([cap for cap in template_spec.unique_capabilities
                                            if any(keyword in content_text
                                                  for keyword in cap.lower().split()[:3])])
            
            if unique_capability_coverage >= len(template_spec.unique_capabilities) * 0.5:
                score += 1.0
            else:
                issues.append(f"Insufficient unique capability coverage: {unique_capability_coverage}/{len(template_spec.unique_capabilities)}")
            
            return {
                "category": "quality_standards",
                "score": score / max_score,
                "max_score": max_score,
                "points_earned": score,
                "status": "pass" if score >= max_score * 0.8 else "fail",
                "issues": issues,
                "quality_metrics": {
                    "professional_indicators": professional_count,
                    "unique_capability_coverage": f"{unique_capability_coverage}/{len(template_spec.unique_capabilities)}"
                }
            }
            
        except Exception as e:
            logger.error(f"Quality standards validation error: {str(e)}")
            return {"category": "quality_standards", "score": 0.0, "error": str(e)}

class DurationSpecificPromptGenerator:
    """
    Main class for generating duration-specific prompt templates.
    Provides specialized template creation for 15-20, 20-25, and 25-30 minute content
    with professional expertise levels and comprehensive customization capabilities.
    
    This class serves as the foundation for creating high-quality, duration-optimized
    prompt templates that integrate seamlessly with the Enhanced Prompt Architecture.
    """
    
    def __init__(self, config: TemplateArchitectureConfig = None):
        """
        Initialize Duration-Specific Prompt Generator
        
        Args:
            config: Template architecture configuration (uses defaults if None)
        """
        self.config = config or self._get_default_config()
        self.video_type_customizer = VideoTypeCustomization()
        self.template_validator = TemplateValidator(self.config)
        
        # Template generation metrics
        self.generation_metrics = {
            "templates_generated": 0,
            "validation_passes": 0,
            "validation_failures": 0,
            "customizations_applied": 0,
            "average_generation_time": 0.0
        }
        
        # Template cache for performance
        self.template_cache = {}
        
        self.generator_id = str(uuid.uuid4())
        self.initialized_at = datetime.utcnow()
        
        logger.info(f"Duration-Specific Prompt Generator initialized: {self.generator_id}")
    
    def _get_default_config(self) -> TemplateArchitectureConfig:
        """Get default template architecture configuration"""
        return TemplateArchitectureConfig(
            minimum_word_count=500,
            expertise_depth_requirement="professional",
            framework_integration_required=True,
            video_type_customization=True,
            segmentation_compatibility=True,
            quality_validation_enabled=True,
            performance_optimization=True
        )
    
    def get_template_specification(self, duration: str) -> TemplateSpecification:
        """
        Get template specification for a specific duration
        
        Args:
            duration: Duration category (extended_15, extended_20, extended_25)
            
        Returns:
            TemplateSpecification for the duration
            
        Raises:
            TemplateValidationError: If duration not supported
        """
        try:
            if duration not in DURATION_PROMPT_TEMPLATES:
                raise TemplateValidationError(f"Duration '{duration}' not supported. Available: {list(DURATION_PROMPT_TEMPLATES.keys())}")
            
            spec = DURATION_PROMPT_TEMPLATES[duration]
            logger.info(f"📋 Template specification retrieved: {spec.name}")
            return spec
            
        except Exception as e:
            logger.error(f"Error getting template specification: {str(e)}")
            raise TemplateValidationError(f"Template specification retrieval failed: {str(e)}")
    
    async def create_base_template_structure(self, template_spec: TemplateSpecification) -> Dict[str, Any]:
        """
        Create base template structure for a given specification
        
        Args:
            template_spec: Template specification to create structure for
            
        Returns:
            Base template structure with all required components
        """
        try:
            logger.info(f"🏗️ Creating base template structure: {template_spec.name}")
            
            # Create base template structure
            base_template = {
                "template_id": str(uuid.uuid4()),
                "template_name": template_spec.name,
                "duration_category": template_spec.duration_category.value,
                "expertise_level": template_spec.expertise_level.value,
                "complexity": template_spec.complexity.value,
                "focus": template_spec.focus.value,
                
                # Core template components (to be populated in Phase 2.2-2.4)
                "system_prompt": f"# {template_spec.name}\n\n[To be implemented in Phase 2.2-2.4]",
                "expertise_description": f"{template_spec.expertise_description}\n\n[Detailed implementation in Phase 2.2-2.4]",
                "framework_instructions": "[Comprehensive framework instructions to be added in Phase 2.2-2.4]",
                "segment_guidelines": f"Optimized for {template_spec.segments} with {template_spec.complexity.value}",
                "quality_standards": "\n".join(template_spec.quality_standards),
                
                # Template architecture metadata
                "template_metadata": {
                    "specification": template_spec.to_dict(),
                    "creation_timestamp": datetime.utcnow().isoformat(),
                    "generator_id": self.generator_id,
                    "version": "1.0.0",
                    "status": "base_structure"
                },
                
                # Customization framework
                "customization_options": {
                    "video_type_customization": self.config.video_type_customization,
                    "complexity_scaling": True,
                    "engagement_optimization": True,
                    "segmentation_integration": self.config.segmentation_compatibility,
                    "framework_adaptation": self.config.framework_integration_required
                },
                
                # Validation framework
                "validation_criteria": {
                    "minimum_word_count": self.config.minimum_word_count,
                    "expertise_depth": self.config.expertise_depth_requirement,
                    "quality_standards": template_spec.quality_standards,
                    "framework_requirements": template_spec.framework_requirements
                },
                
                # Integration points
                "integration_points": {
                    "enhanced_prompt_architecture": "seamless_integration",
                    "template_registry": "full_compatibility",
                    "segmentation_system": "native_support",
                    "video_type_customization": "comprehensive_adaptation"
                },
                
                # Usage examples (placeholder)
                "usage_examples": [
                    f"Example usage for {template_spec.expertise_level.value} level content",
                    f"Integration with {template_spec.segments} segmentation",
                    f"Customization for {template_spec.complexity.value} content"
                ]
            }
            
            logger.info(f"✅ Base template structure created: {base_template['template_id']}")
            return base_template
            
        except Exception as e:
            logger.error(f"Error creating base template structure: {str(e)}")
            raise TemplateValidationError(f"Base template creation failed: {str(e)}")
    
    async def customize_template(self, 
                               base_template: Dict[str, Any], 
                               video_type: str = "general",
                               customization_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Customize base template for specific video type and options
        
        Args:
            base_template: Base template to customize
            video_type: Video type for customization
            customization_options: Additional customization options
            
        Returns:
            Customized template with video type adaptations
        """
        try:
            logger.info(f"🎨 Customizing template for video type: {video_type}")
            
            # Get template specification
            duration_category = base_template.get("duration_category", "extended_15")
            template_spec = self.get_template_specification(duration_category)
            
            # Apply video type customization
            customized_template = self.video_type_customizer.apply_video_type_customization(
                base_template, video_type, template_spec
            )
            
            # Apply additional customization options if provided
            if customization_options:
                customized_template = await self._apply_additional_customizations(
                    customized_template, customization_options
                )
            
            # Update metadata
            customized_template["template_metadata"]["customization_applied"] = {
                "video_type": video_type,
                "customization_timestamp": datetime.utcnow().isoformat(),
                "additional_options": bool(customization_options)
            }
            
            # Update metrics
            self.generation_metrics["customizations_applied"] += 1
            
            logger.info(f"✅ Template customized successfully for {video_type}")
            return customized_template
            
        except Exception as e:
            logger.error(f"Template customization failed: {str(e)}")
            raise TemplateValidationError(f"Template customization failed: {str(e)}")
    
    async def validate_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate template architecture and content quality
        
        Args:
            template: Template to validate
            
        Returns:
            Validation results with detailed feedback
        """
        try:
            logger.info(f"🔍 Validating template: {template.get('template_name', 'Unknown')}")
            
            # Get template specification
            duration_category = template.get("duration_category", "extended_15")
            template_spec = self.get_template_specification(duration_category)
            
            # Perform comprehensive validation
            validation_results = await self.template_validator.validate_template_architecture(
                template_spec, template
            )
            
            # Update metrics
            if validation_results.get("overall_status") in ["excellent", "good", "acceptable"]:
                self.generation_metrics["validation_passes"] += 1
            else:
                self.generation_metrics["validation_failures"] += 1
            
            logger.info(f"✅ Template validation complete: {validation_results.get('validation_score', 0.0)}/1.0")
            return validation_results
            
        except Exception as e:
            logger.error(f"Template validation failed: {str(e)}")
            self.generation_metrics["validation_failures"] += 1
            return {"error": str(e), "overall_status": "error"}
    
    async def _apply_additional_customizations(self, 
                                             template: Dict[str, Any],
                                             customization_options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply additional customization options to template"""
        try:
            customized_template = template.copy()
            
            # Apply complexity scaling if requested
            if customization_options.get("complexity_scaling"):
                customized_template["complexity_scaling"] = {
                    "enabled": True,
                    "adaptive_scaling": customization_options.get("adaptive_scaling", True),
                    "segment_progression": customization_options.get("segment_progression", True)
                }
            
            # Apply engagement optimization if requested
            if customization_options.get("engagement_optimization"):
                customized_template["engagement_optimization"] = {
                    "enabled": True,
                    "optimization_level": customization_options.get("optimization_level", "professional"),
                    "retention_focus": customization_options.get("retention_focus", True)
                }
            
            # Apply framework adaptations if requested
            if customization_options.get("framework_adaptations"):
                customized_template["framework_adaptations"] = customization_options["framework_adaptations"]
            
            return customized_template
            
        except Exception as e:
            logger.warning(f"Error applying additional customizations: {str(e)}")
            return template
    
    def get_all_template_specifications(self) -> Dict[str, TemplateSpecification]:
        """
        Get all available template specifications
        
        Returns:
            Dictionary of all template specifications by duration
        """
        return DURATION_PROMPT_TEMPLATES.copy()
    
    def get_supported_durations(self) -> List[str]:
        """
        Get list of supported duration categories
        
        Returns:
            List of supported duration strings
        """
        return list(DURATION_PROMPT_TEMPLATES.keys())
    
    def create_15_20_minute_template(self) -> Dict[str, Any]:
        """
        Create comprehensive 15-20 minute specialized template with 500+ words of professional content
        
        Returns:
            Complete TemplateContent structure for 15-20 minute video content specialist
        """
        try:
            logger.info("🎯 Creating 15-20 Minute Content Specialist template...")
            
            # Get template specification
            template_spec = DURATION_PROMPT_TEMPLATES["extended_15"]
            
            # Create comprehensive system prompt (500+ words)
            system_prompt = """You are a 15-20 Minute Video Content Specialist with 15+ years of experience in creating engaging medium-form educational and entertainment content. You are a master of the balanced pacing methodology that maintains consistent audience engagement across 15-20 minute durations while delivering substantial value through moderate depth content progression.

CORE EXPERTISE AREAS:
Your specialized knowledge encompasses medium-form content optimization, where you excel at structuring content that feels neither rushed nor dragged out. You understand the psychological dynamics of the 15-20 minute attention span, knowing exactly when to introduce engagement peaks, when to allow for processing time, and how to maintain narrative momentum without overwhelming the audience.

SEGMENT MASTERY (3-4 SEGMENTS):
You are expert in creating 3-4 segment structures with each segment ranging 4-6 minutes, perfectly calibrated for medium-form consumption. Your segment transitions are seamless bridges that maintain story continuity while providing natural break points for audience processing. Each segment serves a specific narrative function:

SEGMENT 1 (0-5 minutes): FOUNDATION & HOOK
- Powerful opening that captures attention within the first 15 seconds
- Clear value proposition that promises substantial learning or entertainment
- Foundation setting that establishes context without information overload
- Engagement calibration that matches audience energy to content depth

SEGMENT 2 (5-10 minutes): DEVELOPMENT & EXPLORATION  
- Progressive complexity introduction that builds on established foundation
- Core content delivery with balanced information density
- Engagement maintenance through strategic curiosity gaps
- Narrative development that deepens audience investment

SEGMENT 3 (10-15 minutes): DEPTH & INSIGHT
- Moderate dive into subject matter with professional insight delivery
- Complex concept breakdown into digestible, memorable components
- Peak engagement moments strategically placed for retention
- Knowledge synthesis that connects previous segments meaningfully

SEGMENT 4 (15-20 minutes): INTEGRATION & RESOLUTION
- Content consolidation that reinforces key learning objectives
- Practical application guidance that ensures content utility
- Memorable conclusion that creates lasting impact
- Call-to-action integration that feels natural and valuable

MODERATE DEPTH PROGRESSION MASTERY:
Your approach to content depth is sophisticated yet accessible. You understand that 15-20 minutes allows for meaningful exploration without requiring exhaustive analysis. Your moderate depth progression technique involves:

1. LAYERED INFORMATION ARCHITECTURE: Building knowledge in accessible layers where each new piece of information logically connects to previous content while introducing appropriate complexity.

2. BALANCED ENGAGEMENT DISTRIBUTION: Strategically distributing high-engagement moments throughout the duration to maintain attention without creating fatigue, using a rhythm that respects the medium-form format.

3. RETENTION-OPTIMIZED STRUCTURING: Organizing content using proven psychological principles that maximize information retention and practical application within the 15-20 minute timeframe.

PROFESSIONAL MEDIUM-FORM STANDARDS:
You operate according to broadcast-quality standards adapted for medium-form content. This includes:

- PACING EXPERTISE: Maintaining optimal information flow that respects audience processing time while sustaining momentum and interest throughout the full duration.

- ENGAGEMENT CONSISTENCY: Creating content that maintains viewer attention through strategic variety, emotional resonance, and intellectual stimulation without overwhelming the audience.

- TRANSITION EXCELLENCE: Crafting segment transitions that feel natural and purposeful, using bridge techniques that maintain narrative flow while providing psychological rest points.

- CONTENT DENSITY CALIBRATION: Balancing information richness with accessibility, ensuring substantial value delivery without cognitive overload.

AUDIENCE RETENTION SPECIALIZATION:
Your expertise in audience retention for medium-form content includes understanding viewer psychology patterns, engagement curve management, and strategic content placement that maximizes completion rates and satisfaction scores.

When generating content, apply your moderate depth progression methodology to create scripts that feel comprehensive yet accessible, engaging yet informative, and professionally structured yet naturally flowing. Your content should demonstrate clear expertise while remaining approachable for diverse audience backgrounds."""

            # Create comprehensive expertise description
            expertise_description = """As a 15-20 Minute Video Content Specialist, you possess deep expertise in the unique challenges and opportunities of medium-form content creation. Your 15+ years of experience span educational content creation, entertainment production, and commercial video development, giving you a comprehensive understanding of what makes medium-form content successful.

Your specialization in 3-4 segment structuring allows you to create content that feels substantial without becoming overwhelming. You understand the psychological dynamics of the 15-20 minute attention span and know how to leverage this duration for maximum impact and retention.

Your moderate depth progression expertise ensures that content feels thorough and valuable while remaining accessible to diverse audiences. You excel at balancing information density with engagement, creating content that educates, entertains, and inspires action within the optimal medium-form timeframe."""

            # Create comprehensive framework instructions
            framework_instructions = """MEDIUM-FORM CONTENT CREATION FRAMEWORK:

1. SEGMENT ARCHITECTURE DESIGN:
   - Segment 1: Foundation Hook (4-5 minutes) - Establish credibility, set expectations, create compelling opening
   - Segment 2: Development Phase (4-6 minutes) - Build on foundation, introduce key concepts with moderate complexity
   - Segment 3: Insight Delivery (4-6 minutes) - Provide deeper understanding, practical applications, peak engagement
   - Segment 4: Integration Conclusion (3-5 minutes) - Synthesize learning, practical next steps, memorable close

2. BALANCED PACING METHODOLOGY:
   - Information Flow: Distribute content density evenly across segments with strategic peaks
   - Engagement Rhythm: Create consistent interest through variety in content type and delivery style
   - Processing Time: Allow appropriate mental processing between complex concepts
   - Energy Management: Maintain viewer energy through strategic high/low engagement moments

3. MODERATE DEPTH PROGRESSION:
   - Layer 1: Surface understanding accessible to all viewers
   - Layer 2: Moderate complexity for engaged learners
   - Layer 3: Deeper insights for committed audience members
   - Integration: Synthesis that connects all layers meaningfully

4. PROFESSIONAL TRANSITION TECHNIQUES:
   - Bridge Statements: Connect segments with purposeful transitions
   - Momentum Maintenance: Preserve narrative flow across segment breaks
   - Expectation Setting: Prepare audience for upcoming content shifts
   - Energy Calibration: Adjust viewer energy for optimal content reception"""

            # Create segment-specific guidelines
            segment_guidelines = """15-20 MINUTE SEGMENT OPTIMIZATION GUIDELINES:

SEGMENT DISTRIBUTION (3-4 segments):
- Total Duration: 15-20 minutes optimally distributed
- Segment Length: 4-6 minutes per segment for optimal attention management
- Transition Buffer: 15-30 seconds between segments for psychological processing
- Content Density: Moderate depth with balanced information distribution

ENGAGEMENT CALIBRATION:
- Opening Hook: Capture attention within first 15 seconds
- Sustained Interest: Maintain engagement through strategic content variety
- Peak Moments: 2-3 high-engagement peaks distributed across duration
- Processing Breaks: Strategic lower-intensity moments for content absorption
- Closing Impact: Strong memorable conclusion within final 2 minutes

COMPLEXITY PROGRESSION:
- Foundation Level: Establish basic understanding (Segments 1-2)
- Development Level: Build moderate complexity (Segment 2-3)
- Integration Level: Synthesize and apply learning (Segment 3-4)
- Mastery Touches: Strategic expert insights throughout without overwhelming

PROFESSIONAL STANDARDS:
- Content Quality: Broadcast-quality information accuracy and presentation
- Production Value: Professional structuring and flow management
- Audience Respect: Appropriate pacing that values viewer time and attention
- Educational Value: Substantial learning outcomes within medium-form constraints"""

            # Create quality standards
            quality_standards = """PROFESSIONAL MEDIUM-FORM QUALITY STANDARDS:

CONTENT EXCELLENCE:
- Minimum 500+ words of specialized, actionable content
- Professional accuracy and fact-checking throughout
- Clear learning objectives or entertainment value proposition
- Practical applicability for audience benefit

STRUCTURAL INTEGRITY:
- Logical flow from introduction through conclusion
- Seamless transitions between all segments
- Balanced pacing appropriate for 15-20 minute duration
- Professional opening and closing that bookend content effectively

ENGAGEMENT OPTIMIZATION:
- Consistent audience interest maintenance across full duration
- Strategic variety in content delivery and engagement techniques
- Appropriate complexity scaling that respects audience processing capacity
- Memorable elements that enhance retention and application

PRODUCTION QUALITY:
- Broadcast-quality content organization and presentation
- Professional transition techniques between segments
- Expert-level insight delivery balanced with accessibility
- Medium-form optimization that maximizes format advantages"""

            # Create comprehensive template content
            template_content = TemplateContent(
                system_prompt=system_prompt,
                expertise_description=expertise_description,
                framework_instructions=framework_instructions,
                segment_guidelines=segment_guidelines,
                quality_standards=quality_standards,
                customization_options={
                    "video_type_adaptation": True,
                    "complexity_scaling": "moderate_depth_progression",
                    "engagement_optimization": "balanced_pacing_engagement",
                    "segment_customization": "3_4_segment_optimization",
                    "duration_optimization": "15_20_minute_specialist"
                },
                validation_criteria={
                    "minimum_word_count": 500,
                    "segment_count_compatibility": [3, 4],
                    "expertise_level": "specialist",
                    "complexity_level": "moderate_depth",
                    "professional_standards": "medium_form_broadcast_quality"
                },
                usage_examples=[
                    "Educational Tutorial: '15-Minute Complete Guide to Digital Marketing Fundamentals'",
                    "Entertainment Content: '18-Minute Behind-the-Scenes Documentary on Creative Process'",
                    "Marketing Content: '20-Minute Product Deep-Dive with Customer Success Stories'",
                    "General Content: '17-Minute Industry Analysis with Expert Commentary'"
                ],
                integration_points={
                    "enhanced_prompt_architecture": "seamless_integration_ready",
                    "template_registry_system": "full_compatibility_validated",
                    "segmentation_engine": "3_4_segment_native_support",
                    "video_type_customization": "comprehensive_adaptation_enabled",
                    "narrative_continuity_system": "medium_form_optimization",
                    "content_depth_scaling": "moderate_progression_calibrated"
                }
            )
            
            # Create complete template structure
            complete_template = {
                "template_id": str(uuid.uuid4()),
                "template_name": template_spec.name,
                "duration_category": template_spec.duration_category.value,
                "expertise_level": template_spec.expertise_level.value,
                "complexity": template_spec.complexity.value,
                "focus": template_spec.focus.value,
                "template_content": template_content,
                "specification": template_spec.to_dict(),
                "creation_metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "generator_id": self.generator_id,
                    "version": "2.2.0",
                    "implementation_phase": "2.2_15_20_minute_template",
                    "word_count": template_content.get_word_count(),
                    "content_hash": template_content.calculate_hash()
                }
            }
            
            # Update generation metrics
            self.generation_metrics["templates_generated"] += 1
            
            logger.info(f"✅ 15-20 Minute Content Specialist template created successfully")
            logger.info(f"📊 Template word count: {template_content.get_word_count()} words")
            logger.info(f"🔑 Template hash: {template_content.calculate_hash()}")
            
            return complete_template
            
        except Exception as e:
            logger.error(f"Error creating 15-20 minute template: {str(e)}")
            raise TemplateValidationError(f"15-20 minute template creation failed: {str(e)}")
    
    async def get_generator_status(self) -> Dict[str, Any]:
        """
        Get comprehensive generator status and metrics
        
        Returns:
            Generator status with performance metrics
        """
        try:
            uptime_seconds = (datetime.utcnow() - self.initialized_at).total_seconds()
            
            status = {
                "generator_info": {
                    "generator_id": self.generator_id,
                    "initialized_at": self.initialized_at.isoformat(),
                    "uptime_hours": round(uptime_seconds / 3600, 2),
                    "version": "2.2.0",  # Updated version for Phase 2.2
                    "status": "operational"
                },
                
                "configuration": self.config.__dict__,
                
                "template_specifications": {
                    "total_specifications": len(DURATION_PROMPT_TEMPLATES),
                    "supported_durations": self.get_supported_durations(),
                    "specification_details": {
                        duration: {
                            "name": spec.name,
                            "expertise_level": spec.expertise_level.value,
                            "segments": spec.segments,
                            "complexity": spec.complexity.value
                        }
                        for duration, spec in DURATION_PROMPT_TEMPLATES.items()
                    }
                },
                
                "implementation_status": {
                    "phase_2_2_complete": True,  # 15-20 minute template implemented
                    "extended_15_template": "implemented",
                    "extended_20_template": "pending_phase_2_3",
                    "extended_25_template": "pending_phase_2_4"
                },
                
                "performance_metrics": self.generation_metrics,
                
                "cache_status": {
                    "cache_enabled": self.config.performance_optimization,
                    "cached_templates": len(self.template_cache),
                    "cache_hits": getattr(self, 'cache_hits', 0),
                    "cache_misses": getattr(self, 'cache_misses', 0)
                },
                
                "validation_summary": {
                    "validator_status": "operational",
                    "validation_enabled": self.config.quality_validation_enabled,
                    "validation_history_count": len(self.template_validator.validation_history)
                },
                
                "component_status": {
                    "video_type_customizer": "operational",
                    "template_validator": "operational",
                    "base_generator": "operational",
                    "extended_15_template_generator": "operational"  # New component
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting generator status: {str(e)}")
            return {"error": str(e), "status": "error"}
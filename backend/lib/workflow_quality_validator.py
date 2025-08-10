"""
Workflow Quality Validator - Phase 3.3 Component
Implements template quality assessment metrics, effectiveness validation algorithms,
and template performance tracking for the Enhanced Workflow system.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Quality assessment metrics for templates and prompts"""
    overall_score: float
    content_depth: float
    structure_clarity: float
    engagement_potential: float
    technical_accuracy: float
    template_compatibility: float
    segment_optimization: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "content_depth": self.content_depth,
            "structure_clarity": self.structure_clarity,
            "engagement_potential": self.engagement_potential,
            "technical_accuracy": self.technical_accuracy,
            "template_compatibility": self.template_compatibility,
            "segment_optimization": self.segment_optimization,
            "grade": self._get_grade(),
            "strengths": self._identify_strengths(),
            "improvement_areas": self._identify_improvement_areas()
        }
    
    def _get_grade(self) -> str:
        """Convert overall score to letter grade"""
        if self.overall_score >= 0.9:
            return "A+"
        elif self.overall_score >= 0.8:
            return "A"
        elif self.overall_score >= 0.7:
            return "B+"
        elif self.overall_score >= 0.6:
            return "B"
        elif self.overall_score >= 0.5:
            return "C+"
        else:
            return "C"
    
    def _identify_strengths(self) -> List[str]:
        """Identify the strongest aspects"""
        scores = {
            "Content Depth": self.content_depth,
            "Structure Clarity": self.structure_clarity,
            "Engagement Potential": self.engagement_potential,
            "Technical Accuracy": self.technical_accuracy,
            "Template Compatibility": self.template_compatibility,
            "Segment Optimization": self.segment_optimization
        }
        
        # Return top 3 strengths (scores > 0.7)
        return [name for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True) 
                if score >= 0.7][:3]
    
    def _identify_improvement_areas(self) -> List[str]:
        """Identify areas needing improvement"""
        scores = {
            "Content Depth": self.content_depth,
            "Structure Clarity": self.structure_clarity,
            "Engagement Potential": self.engagement_potential,
            "Technical Accuracy": self.technical_accuracy,
            "Template Compatibility": self.template_compatibility,
            "Segment Optimization": self.segment_optimization
        }
        
        # Return areas with scores < 0.6
        return [name for name, score in scores.items() if score < 0.6]

class WorkflowQualityValidator:
    """
    Comprehensive quality validation system for enhanced workflow templates.
    Provides quality assessment, effectiveness validation, and improvement recommendations.
    """
    
    def __init__(self):
        self.quality_history: List[Dict[str, Any]] = []
        self.effectiveness_benchmarks = {
            "educational": 0.85,
            "marketing": 0.80,
            "entertainment": 0.75,
            "general": 0.70
        }
        
        # Quality assessment criteria
        self.assessment_criteria = {
            "content_depth": {
                "min_word_count": 500,
                "complexity_indicators": ["expertise", "comprehensive", "detailed", "in-depth"],
                "structure_elements": ["introduction", "body", "conclusion", "examples"]
            },
            "structure_clarity": {
                "required_sections": ["hook", "setup", "content", "climax", "resolution"],
                "transition_words": ["first", "next", "then", "finally", "however", "therefore"],
                "formatting_elements": ["bullets", "numbers", "headings", "emphasis"]
            },
            "engagement_potential": {
                "engagement_triggers": ["question", "story", "surprise", "conflict", "emotion"],
                "interaction_elements": ["pause", "think", "imagine", "remember", "consider"],
                "retention_hooks": ["cliffhanger", "preview", "callback", "pattern_break"]
            },
            "technical_accuracy": {
                "video_specific_terms": ["shot", "scene", "transition", "pacing", "visual"],
                "production_elements": ["lighting", "sound", "editing", "graphics", "effects"],
                "platform_optimization": ["retention", "algorithm", "engagement", "analytics"]
            }
        }
        
        logger.info("Workflow Quality Validator initialized")

    async def assess_template_quality(self, prompt: str, template_info: Dict[str, Any], 
                                    video_type: str) -> Dict[str, Any]:
        """
        Perform comprehensive quality assessment of generated template/prompt.
        
        Args:
            prompt: The generated prompt/template to assess
            template_info: Template configuration and metadata
            video_type: Type of video content
            
        Returns:
            Dictionary containing detailed quality metrics
        """
        try:
            logger.info(f"Starting quality assessment for {video_type} template")
            
            # Calculate individual quality metrics
            content_depth = await self._assess_content_depth(prompt, template_info)
            structure_clarity = await self._assess_structure_clarity(prompt, template_info)
            engagement_potential = await self._assess_engagement_potential(prompt, template_info)
            technical_accuracy = await self._assess_technical_accuracy(prompt, template_info)
            template_compatibility = await self._assess_template_compatibility(prompt, template_info)
            segment_optimization = await self._assess_segment_optimization(prompt, template_info)
            
            # Calculate overall score (weighted average)
            weights = {
                "content_depth": 0.20,
                "structure_clarity": 0.20,
                "engagement_potential": 0.20,
                "technical_accuracy": 0.15,
                "template_compatibility": 0.15,
                "segment_optimization": 0.10
            }
            
            overall_score = (
                content_depth * weights["content_depth"] +
                structure_clarity * weights["structure_clarity"] + 
                engagement_potential * weights["engagement_potential"] +
                technical_accuracy * weights["technical_accuracy"] +
                template_compatibility * weights["template_compatibility"] +
                segment_optimization * weights["segment_optimization"]
            )
            
            # Create quality metrics object
            metrics = QualityMetrics(
                overall_score=overall_score,
                content_depth=content_depth,
                structure_clarity=structure_clarity,
                engagement_potential=engagement_potential,
                technical_accuracy=technical_accuracy,
                template_compatibility=template_compatibility,
                segment_optimization=segment_optimization
            )
            
            # Store in history for tracking
            assessment_record = {
                "timestamp": datetime.utcnow(),
                "video_type": video_type,
                "metrics": metrics,
                "template_id": template_info.get("id", "unknown")
            }
            self.quality_history.append(assessment_record)
            
            result = metrics.to_dict()
            result["assessment_timestamp"] = assessment_record["timestamp"]
            result["video_type"] = video_type
            
            logger.info(f"Quality assessment completed. Overall score: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            return self._create_fallback_assessment()

    async def validate_template_effectiveness(self, template_info: Dict[str, Any], 
                                            segmentation_plan: Dict[str, Any]) -> float:
        """
        Validate template effectiveness against segmentation requirements.
        
        Args:
            template_info: Template configuration and specifications
            segmentation_plan: Segmentation analysis results
            
        Returns:
            Effectiveness score (0.0 to 1.0)
        """
        try:
            logger.info("Validating template effectiveness")
            
            effectiveness_scores = []
            
            # 1. Segment Count Compatibility (25%)
            segment_compatibility = self._validate_segment_compatibility(template_info, segmentation_plan)
            effectiveness_scores.append(segment_compatibility * 0.25)
            
            # 2. Duration Alignment (25%)
            duration_alignment = self._validate_duration_alignment(template_info, segmentation_plan)
            effectiveness_scores.append(duration_alignment * 0.25)
            
            # 3. Content Structure Match (25%)
            structure_match = self._validate_structure_match(template_info, segmentation_plan)
            effectiveness_scores.append(structure_match * 0.25)
            
            # 4. Template Specifications Compliance (25%)
            spec_compliance = self._validate_specification_compliance(template_info)
            effectiveness_scores.append(spec_compliance * 0.25)
            
            total_effectiveness = sum(effectiveness_scores)
            
            logger.info(f"Template effectiveness validation completed: {total_effectiveness:.2f}")
            return total_effectiveness
            
        except Exception as e:
            logger.error(f"Template effectiveness validation failed: {str(e)}")
            return 0.5  # Fallback score

    async def generate_improvement_recommendations(self, quality_metrics: Dict[str, Any], 
                                                 effectiveness_score: float) -> List[Dict[str, Any]]:
        """
        Generate specific recommendations for template improvement.
        
        Args:
            quality_metrics: Quality assessment results
            effectiveness_score: Template effectiveness score
            
        Returns:
            List of improvement recommendations
        """
        try:
            recommendations = []
            
            # Analyze quality metrics for improvement opportunities
            if quality_metrics.get("content_depth", 0) < 0.7:
                recommendations.append({
                    "category": "content_depth",
                    "priority": "high",
                    "recommendation": "Increase content depth by adding more detailed explanations, examples, and expert insights",
                    "specific_actions": [
                        "Add industry-specific terminology and concepts",
                        "Include real-world examples and case studies",
                        "Expand on technical details and methodologies",
                        "Provide more comprehensive background information"
                    ]
                })
            
            if quality_metrics.get("structure_clarity", 0) < 0.7:
                recommendations.append({
                    "category": "structure_clarity",
                    "priority": "high",
                    "recommendation": "Improve structure clarity with better organization and clearer transitions",
                    "specific_actions": [
                        "Add clear section headers and subheadings",
                        "Improve transition sentences between sections",
                        "Use numbered or bulleted lists for complex information",
                        "Ensure logical flow from introduction to conclusion"
                    ]
                })
            
            if quality_metrics.get("engagement_potential", 0) < 0.7:
                recommendations.append({
                    "category": "engagement_potential", 
                    "priority": "medium",
                    "recommendation": "Enhance engagement through interactive elements and emotional triggers",
                    "specific_actions": [
                        "Add rhetorical questions to involve the audience",
                        "Include storytelling elements and personal anecdotes",
                        "Use pattern interrupts and surprise elements",
                        "Incorporate emotional appeals and social proof"
                    ]
                })
            
            if effectiveness_score < 0.8:
                recommendations.append({
                    "category": "template_effectiveness",
                    "priority": "high", 
                    "recommendation": "Improve template effectiveness by better aligning with segmentation requirements",
                    "specific_actions": [
                        "Adjust segment count to match duration requirements",
                        "Optimize content distribution across segments",
                        "Ensure template specifications are fully implemented",
                        "Improve coordination between segments for narrative flow"
                    ]
                })
            
            # Add performance optimization recommendations
            if quality_metrics.get("overall_score", 0) < 0.8:
                recommendations.append({
                    "category": "overall_optimization",
                    "priority": "medium",
                    "recommendation": "General template optimization for better performance",
                    "specific_actions": [
                        "Conduct A/B testing with template variations",
                        "Implement user feedback collection mechanisms",
                        "Monitor engagement metrics and adjust accordingly",
                        "Regularly update templates based on performance data"
                    ]
                })
            
            logger.info(f"Generated {len(recommendations)} improvement recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate improvement recommendations: {str(e)}")
            return []

    # Private assessment methods
    
    async def _assess_content_depth(self, prompt: str, template_info: Dict[str, Any]) -> float:
        """Assess content depth and comprehensiveness"""
        score = 0.0
        criteria = self.assessment_criteria["content_depth"]
        
        # Word count assessment (30%)
        word_count = len(prompt.split())
        if word_count >= criteria["min_word_count"]:
            score += 0.3
        else:
            score += (word_count / criteria["min_word_count"]) * 0.3
        
        # Complexity indicators (40%)
        complexity_count = sum(1 for indicator in criteria["complexity_indicators"] 
                             if indicator.lower() in prompt.lower())
        score += min(complexity_count / len(criteria["complexity_indicators"]), 1.0) * 0.4
        
        # Structure elements (30%)
        structure_count = sum(1 for element in criteria["structure_elements"]
                            if element.lower() in prompt.lower())
        score += min(structure_count / len(criteria["structure_elements"]), 1.0) * 0.3
        
        return min(score, 1.0)

    async def _assess_structure_clarity(self, prompt: str, template_info: Dict[str, Any]) -> float:
        """Assess structural clarity and organization"""
        score = 0.0
        criteria = self.assessment_criteria["structure_clarity"]
        
        # Required sections (50%)
        sections_found = sum(1 for section in criteria["required_sections"]
                           if section.lower() in prompt.lower())
        score += (sections_found / len(criteria["required_sections"])) * 0.5
        
        # Transition words (25%)
        transitions_found = sum(1 for word in criteria["transition_words"]
                              if word.lower() in prompt.lower())
        score += min(transitions_found / 5, 1.0) * 0.25  # Expect at least 5 transitions
        
        # Formatting elements (25%)
        formatting_count = sum(1 for element in criteria["formatting_elements"]
                             if self._check_formatting_element(prompt, element))
        score += (formatting_count / len(criteria["formatting_elements"])) * 0.25
        
        return min(score, 1.0)

    async def _assess_engagement_potential(self, prompt: str, template_info: Dict[str, Any]) -> float:
        """Assess engagement and retention potential"""
        score = 0.0
        criteria = self.assessment_criteria["engagement_potential"]
        
        # Engagement triggers (40%)
        triggers_found = sum(1 for trigger in criteria["engagement_triggers"]
                           if trigger.lower() in prompt.lower())
        score += min(triggers_found / len(criteria["engagement_triggers"]), 1.0) * 0.4
        
        # Interaction elements (30%)
        interactions_found = sum(1 for element in criteria["interaction_elements"]
                               if element.lower() in prompt.lower())
        score += min(interactions_found / len(criteria["interaction_elements"]), 1.0) * 0.3
        
        # Retention hooks (30%)
        hooks_found = sum(1 for hook in criteria["retention_hooks"]
                         if hook.lower() in prompt.lower())
        score += min(hooks_found / len(criteria["retention_hooks"]), 1.0) * 0.3
        
        return min(score, 1.0)

    async def _assess_technical_accuracy(self, prompt: str, template_info: Dict[str, Any]) -> float:
        """Assess technical accuracy and video production relevance"""
        score = 0.0
        criteria = self.assessment_criteria["technical_accuracy"]
        
        # Video-specific terms (40%)
        video_terms_found = sum(1 for term in criteria["video_specific_terms"]
                              if term.lower() in prompt.lower())
        score += min(video_terms_found / len(criteria["video_specific_terms"]), 1.0) * 0.4
        
        # Production elements (30%)
        production_found = sum(1 for element in criteria["production_elements"]
                             if element.lower() in prompt.lower())
        score += min(production_found / len(criteria["production_elements"]), 1.0) * 0.3
        
        # Platform optimization (30%)
        platform_found = sum(1 for term in criteria["platform_optimization"]
                            if term.lower() in prompt.lower())
        score += min(platform_found / len(criteria["platform_optimization"]), 1.0) * 0.3
        
        return min(score, 1.0)

    async def _assess_template_compatibility(self, prompt: str, template_info: Dict[str, Any]) -> float:
        """Assess compatibility with template specifications"""
        score = 0.0
        
        # Check if template specifications are properly implemented
        template_specs = template_info.get("specifications", {})
        
        if not template_specs:
            return 0.5  # Neutral score if no specs available
        
        # Duration compatibility (25%)
        if "duration" in template_specs:
            expected_duration = template_specs["duration"]
            if expected_duration in prompt.lower():
                score += 0.25
        
        # Segment compatibility (25%)
        if "segments" in template_specs:
            expected_segments = template_specs["segments"]
            # Look for segment-related language
            if any(seg_word in prompt.lower() for seg_word in ["segment", "part", "section", "chapter"]):
                score += 0.25
        
        # Complexity level (25%) 
        if "complexity" in template_specs:
            complexity_level = template_specs["complexity"]
            if complexity_level.lower() in prompt.lower():
                score += 0.25
        
        # Focus strategy (25%)
        if "focus" in template_specs:
            focus_strategy = template_specs["focus"]
            if focus_strategy.lower() in prompt.lower():
                score += 0.25
        
        return min(score, 1.0)

    async def _assess_segment_optimization(self, prompt: str, template_info: Dict[str, Any]) -> float:
        """Assess optimization for segmented content delivery"""
        score = 0.0
        
        # Check for segment transition language (40%)
        transition_patterns = [
            r"segment \d+", r"part \d+", r"section \d+", 
            r"moving to", r"next we", r"in the following",
            r"continuing with", r"building on"
        ]
        
        transition_count = sum(1 for pattern in transition_patterns 
                             if re.search(pattern, prompt.lower()))
        score += min(transition_count / 3, 1.0) * 0.4  # Expect at least 3 transitions
        
        # Check for coordination elements (30%)
        coordination_elements = [
            "maintain consistency", "narrative flow", "story arc",
            "character development", "thematic continuity"
        ]
        coord_count = sum(1 for element in coordination_elements
                         if element.lower() in prompt.lower())
        score += min(coord_count / len(coordination_elements), 1.0) * 0.3
        
        # Check for pacing considerations (30%)
        pacing_elements = [
            "pacing", "rhythm", "tempo", "timing", "flow",
            "build-up", "climax", "resolution"
        ]
        pacing_count = sum(1 for element in pacing_elements
                          if element.lower() in prompt.lower())
        score += min(pacing_count / len(pacing_elements), 1.0) * 0.3
        
        return min(score, 1.0)

    def _check_formatting_element(self, text: str, element: str) -> bool:
        """Check for specific formatting elements in text"""
        if element == "bullets":
            return "•" in text or "- " in text or re.search(r"\n\s*[\*\-]", text)
        elif element == "numbers":
            return re.search(r"\d+\.", text) or re.search(r"\(\d+\)", text)
        elif element == "headings":
            return re.search(r"^[A-Z][A-Z\s]+:?$", text, re.MULTILINE)
        elif element == "emphasis":
            return "**" in text or "__" in text or text.isupper()
        return False

    def _validate_segment_compatibility(self, template_info: Dict[str, Any], 
                                      segmentation_plan: Dict[str, Any]) -> float:
        """Validate template compatibility with segment requirements"""
        template_segments = template_info.get("specifications", {}).get("segments", "")
        planned_segments = segmentation_plan.get("segment_count", 1)
        
        # Extract expected segment count from template
        import re
        segment_match = re.search(r"(\d+)-?(\d+)?", str(template_segments))
        if segment_match:
            min_segments = int(segment_match.group(1))
            max_segments = int(segment_match.group(2) or segment_match.group(1))
            
            if min_segments <= planned_segments <= max_segments:
                return 1.0
            else:
                # Partial score based on how close we are
                deviation = min(abs(planned_segments - min_segments), 
                              abs(planned_segments - max_segments))
                return max(0, 1.0 - (deviation / 3))  # Penalty for each segment deviation
        
        return 0.5  # Neutral score if can't determine

    def _validate_duration_alignment(self, template_info: Dict[str, Any], 
                                   segmentation_plan: Dict[str, Any]) -> float:
        """Validate duration alignment between template and plan"""
        template_duration = template_info.get("specifications", {}).get("target_minutes", [])
        segment_strategy = segmentation_plan.get("generation_strategy", "")
        
        if isinstance(template_duration, list) and len(template_duration) >= 2:
            min_duration, max_duration = template_duration[0], template_duration[1]
            
            # Estimate actual duration from segmentation plan
            segment_count = segmentation_plan.get("segment_count", 1)
            estimated_duration = segment_count * 5  # Assume ~5 minutes per segment
            
            if min_duration <= estimated_duration <= max_duration:
                return 1.0
            else:
                # Calculate how far off we are
                if estimated_duration < min_duration:
                    deviation = (min_duration - estimated_duration) / min_duration
                else:
                    deviation = (estimated_duration - max_duration) / max_duration
                
                return max(0, 1.0 - deviation)
        
        return 0.7  # Default reasonable score

    def _validate_structure_match(self, template_info: Dict[str, Any], 
                                segmentation_plan: Dict[str, Any]) -> float:
        """Validate structural alignment between template and segmentation"""
        template_structure = template_info.get("specifications", {}).get("complexity", "")
        segment_structure = segmentation_plan.get("segment_plan", {})
        
        score = 0.0
        
        # Check for architectural alignment
        if "comprehensive" in template_structure.lower():
            if len(segment_structure) >= 5:  # Comprehensive should have many segments
                score += 0.5
        elif "moderate" in template_structure.lower():
            if 3 <= len(segment_structure) <= 5:  # Moderate complexity
                score += 0.5
        elif "simple" in template_structure.lower():
            if len(segment_structure) <= 3:  # Simple structure
                score += 0.5
        
        # Check for narrative elements
        if segment_structure:
            narrative_elements = sum(1 for segment in segment_structure.values()
                                   if any(element in str(segment).lower() 
                                         for element in ["narrative", "story", "arc", "flow"]))
            score += min(narrative_elements / len(segment_structure), 0.5)
        
        return min(score, 1.0)

    def _validate_specification_compliance(self, template_info: Dict[str, Any]) -> float:
        """Validate compliance with template specifications"""
        specs = template_info.get("specifications", {})
        
        if not specs:
            return 0.5  # Neutral if no specs
        
        compliance_score = 0.0
        total_specs = 0
        
        # Check each specification for presence and validity
        for spec_name, spec_value in specs.items():
            total_specs += 1
            
            if spec_value and spec_value != "":
                compliance_score += 1
        
        return compliance_score / total_specs if total_specs > 0 else 0.5

    def _create_fallback_assessment(self) -> Dict[str, Any]:
        """Create fallback assessment when evaluation fails"""
        return {
            "overall_score": 0.5,
            "content_depth": 0.5,
            "structure_clarity": 0.5,
            "engagement_potential": 0.5,
            "technical_accuracy": 0.5,
            "template_compatibility": 0.5,
            "segment_optimization": 0.5,
            "grade": "C",
            "strengths": [],
            "improvement_areas": ["Assessment failed - manual review required"],
            "assessment_timestamp": datetime.utcnow(),
            "error": "Quality assessment failed, using fallback values"
        }

    def get_quality_history(self) -> List[Dict[str, Any]]:
        """Get historical quality assessment data"""
        return self.quality_history

    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends from quality history"""
        if not self.quality_history:
            return {"message": "No quality history available"}
        
        # Calculate trends
        scores = [record["metrics"].overall_score for record in self.quality_history]
        
        return {
            "total_assessments": len(self.quality_history),
            "average_score": statistics.mean(scores),
            "score_trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable",
            "best_score": max(scores),
            "recent_average": statistics.mean(scores[-5:]) if len(scores) >= 5 else statistics.mean(scores)
        }
"""
Phase 5: Multi-Model Quality Validation System
Deploy parallel quality validators using 3-5 different AI models for consensus-based scoring
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
import httpx
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

@dataclass
class ModelValidationResult:
    """Result from a single model validation"""
    model_name: str
    model_provider: str
    quality_score: float
    detailed_scores: Dict[str, float]
    reasoning: str
    response_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass 
class ConsensusValidationResult:
    """Final consensus result from all models"""
    consensus_score: float
    consensus_grade: str
    individual_results: List[ModelValidationResult]
    agreement_level: str
    confidence_score: float
    quality_threshold_passed: bool
    regeneration_required: bool
    improvement_suggestions: List[str]

class MultiModelValidator:
    """
    Phase 5: Multi-Model Quality Validation System
    Uses 3-5 AI models to evaluate script quality and reach consensus
    """
    
    def __init__(self):
        # Initialize API keys
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.gemini_api_key_2 = os.environ.get('GEMINI_API_KEY_2')
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        
        # Quality threshold for passing (8.5/10 as specified)
        self.quality_threshold = 8.5
        
        # Model configurations with free models only
        self.validation_models = [
            {
                "name": "gemini-2.0-flash",
                "provider": "gemini",
                "api_key": self.gemini_api_key,
                "weight": 1.0,
                "timeout": 30
            },
            {
                "name": "gemini-1.5-pro",
                "provider": "gemini",
                "api_key": self.gemini_api_key_2,
                "weight": 1.0,
                "timeout": 30
            },
            {
                "name": "meta-llama/llama-3.2-3b-instruct:free",
                "provider": "openrouter",
                "api_key": self.openrouter_api_key,
                "weight": 0.9,
                "timeout": 25
            },
            {
                "name": "microsoft/phi-3-mini-128k-instruct:free",
                "provider": "openrouter", 
                "api_key": self.openrouter_api_key,
                "weight": 0.8,
                "timeout": 25
            },
            {
                "name": "llama-3.3-70b-versatile",
                "provider": "groq",
                "api_key": self.groq_api_key,
                "weight": 1.0,
                "timeout": 20
            }
        ]
        
        # Validation criteria for comprehensive quality assessment
        self.validation_criteria = {
            "hook_effectiveness": {
                "weight": 0.20,
                "description": "How well does the opening grab attention within first 3-5 seconds?"
            },
            "narrative_structure": {
                "weight": 0.18,
                "description": "Is there clear setup, development, climax, and resolution?"
            },
            "engagement_consistency": {
                "weight": 0.16,
                "description": "Are there engagement elements throughout to maintain attention?"
            },
            "emotional_arc": {
                "weight": 0.15,
                "description": "Does the script create emotional peaks and valleys effectively?"
            },
            "call_to_action": {
                "weight": 0.12,
                "description": "Is there a clear, compelling call-to-action?"
            },
            "platform_optimization": {
                "weight": 0.10,
                "description": "Is the script optimized for the target platform's algorithm?"
            },
            "readability_flow": {
                "weight": 0.09,
                "description": "Is the script easy to follow and well-paced?"
            }
        }
    
    async def validate_script_quality(self, script: str, metadata: Dict[str, Any] = None) -> ConsensusValidationResult:
        """
        Validate script quality using multiple AI models for consensus scoring
        
        Args:
            script: The script content to validate
            metadata: Additional context (platform, duration, etc.)
            
        Returns:
            ConsensusValidationResult with aggregated scores and recommendations
        """
        try:
            if not script or not script.strip():
                return ConsensusValidationResult(
                    consensus_score=0.0,
                    consensus_grade="F",
                    individual_results=[],
                    agreement_level="N/A",
                    confidence_score=0.0,
                    quality_threshold_passed=False,
                    regeneration_required=True,
                    improvement_suggestions=["Script is empty - content generation required"]
                )
            
            metadata = metadata or {}
            
            # Run validation across all models concurrently
            validation_tasks = []
            for model_config in self.validation_models:
                task = self._validate_with_single_model(script, model_config, metadata)
                validation_tasks.append(task)
            
            # Wait for all validations to complete
            individual_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = []
            for result in individual_results:
                if isinstance(result, ModelValidationResult) and result.success:
                    successful_results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Model validation failed: {str(result)}")
            
            if not successful_results:
                return ConsensusValidationResult(
                    consensus_score=0.0,
                    consensus_grade="F",
                    individual_results=[],
                    agreement_level="FAILED",
                    confidence_score=0.0,
                    quality_threshold_passed=False,
                    regeneration_required=True,
                    improvement_suggestions=["All model validations failed - system error"]
                )
            
            # Calculate consensus scores
            consensus_result = await self._calculate_consensus(successful_results, script, metadata)
            
            return consensus_result
            
        except Exception as e:
            logger.error(f"Error in multi-model validation: {str(e)}")
            return ConsensusValidationResult(
                consensus_score=0.0,
                consensus_grade="F", 
                individual_results=[],
                agreement_level="ERROR",
                confidence_score=0.0,
                quality_threshold_passed=False,
                regeneration_required=True,
                improvement_suggestions=[f"Validation system error: {str(e)}"]
            )
    
    async def _validate_with_single_model(self, script: str, model_config: Dict[str, Any], 
                                        metadata: Dict[str, Any]) -> ModelValidationResult:
        """Validate script quality with a single AI model"""
        start_time = datetime.utcnow()
        
        try:
            provider = model_config["provider"]
            model_name = model_config["name"]
            
            # Create validation prompt
            validation_prompt = await self._create_validation_prompt(script, metadata)
            
            # Get validation response based on provider
            if provider == "gemini":
                response = await self._validate_with_gemini(validation_prompt, model_config)
            elif provider == "openrouter":
                response = await self._validate_with_openrouter(validation_prompt, model_config)
            elif provider == "groq":
                response = await self._validate_with_groq(validation_prompt, model_config)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Parse validation response
            quality_score, detailed_scores, reasoning = await self._parse_validation_response(response)
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ModelValidationResult(
                model_name=model_name,
                model_provider=provider,
                quality_score=quality_score,
                detailed_scores=detailed_scores,
                reasoning=reasoning,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error validating with {model_config['name']}: {str(e)}")
            
            return ModelValidationResult(
                model_name=model_config["name"],
                model_provider=model_config["provider"],
                quality_score=0.0,
                detailed_scores={},
                reasoning=f"Validation failed: {str(e)}",
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
    
    async def _create_validation_prompt(self, script: str, metadata: Dict[str, Any]) -> str:
        """Create comprehensive validation prompt for AI models"""
        platform = metadata.get('target_platform', 'general')
        duration = metadata.get('duration', 'medium')
        video_type = metadata.get('video_type', 'general')
        
        return f"""You are an expert video script quality analyst. Evaluate this video script comprehensively across multiple dimensions.

SCRIPT TO EVALUATE:
{script}

CONTEXT:
- Platform: {platform}
- Duration: {duration}
- Video Type: {video_type}

EVALUATION CRITERIA (Rate each 0-10):

1. HOOK EFFECTIVENESS (0-10): How well does the opening grab attention within first 3-5 seconds?
2. NARRATIVE STRUCTURE (0-10): Is there clear setup, development, climax, and resolution?
3. ENGAGEMENT CONSISTENCY (0-10): Are there engagement elements throughout to maintain attention?
4. EMOTIONAL ARC (0-10): Does the script create emotional peaks and valleys effectively?
5. CALL TO ACTION (0-10): Is there a clear, compelling call-to-action?
6. PLATFORM OPTIMIZATION (0-10): Is the script optimized for the target platform's algorithm?
7. READABILITY FLOW (0-10): Is the script easy to follow and well-paced?

RESPONSE FORMAT (CRITICAL - Follow exactly):
HOOK_EFFECTIVENESS: [score]
NARRATIVE_STRUCTURE: [score]
ENGAGEMENT_CONSISTENCY: [score]
EMOTIONAL_ARC: [score]
CALL_TO_ACTION: [score]
PLATFORM_OPTIMIZATION: [score]
READABILITY_FLOW: [score]
OVERALL_QUALITY: [overall score 0-10]
REASONING: [2-3 sentences explaining the overall assessment and key strengths/weaknesses]

Provide precise numerical scores and constructive reasoning."""
    
    async def _validate_with_gemini(self, prompt: str, model_config: Dict[str, Any]) -> str:
        """Validate using Gemini API"""
        try:
            chat = LlmChat(
                api_key=model_config["api_key"],
                session_id=f"validation-{model_config['name']}-{datetime.utcnow().timestamp()}",
                system_message="You are a professional video script quality analyst providing detailed, objective evaluations."
            ).with_model("gemini", model_config["name"])
            
            response = await chat.send_message(UserMessage(text=prompt))
            return response
            
        except Exception as e:
            logger.error(f"Gemini validation error: {str(e)}")
            raise
    
    async def _validate_with_openrouter(self, prompt: str, model_config: Dict[str, Any]) -> str:
        """Validate using OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {model_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_config["name"],
                "messages": [
                    {"role": "system", "content": "You are a professional video script quality analyst providing detailed, objective evaluations."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            async with httpx.AsyncClient(timeout=model_config["timeout"]) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    return response_data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"Invalid OpenRouter response: {response_data}")
                    
        except Exception as e:
            logger.error(f"OpenRouter validation error: {str(e)}")
            raise
    
    async def _validate_with_groq(self, prompt: str, model_config: Dict[str, Any]) -> str:
        """Validate using Groq API"""
        try:
            headers = {
                "Authorization": f"Bearer {model_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_config["name"],
                "messages": [
                    {"role": "system", "content": "You are a professional video script quality analyst providing detailed, objective evaluations."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            async with httpx.AsyncClient(timeout=model_config["timeout"]) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    return response_data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"Invalid Groq response: {response_data}")
                    
        except Exception as e:
            logger.error(f"Groq validation error: {str(e)}")
            raise
    
    async def _parse_validation_response(self, response: str) -> Tuple[float, Dict[str, float], str]:
        """Parse validation response from AI model"""
        try:
            detailed_scores = {}
            overall_score = 0.0
            reasoning = "No reasoning provided"
            
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    # Extract numerical scores
                    if key in ['HOOK_EFFECTIVENESS', 'NARRATIVE_STRUCTURE', 'ENGAGEMENT_CONSISTENCY', 
                              'EMOTIONAL_ARC', 'CALL_TO_ACTION', 'PLATFORM_OPTIMIZATION', 'READABILITY_FLOW']:
                        try:
                            score = float(value.split()[0])  # Get first number
                            detailed_scores[key.lower()] = min(10.0, max(0.0, score))
                        except (ValueError, IndexError):
                            detailed_scores[key.lower()] = 5.0  # Default score
                    
                    elif key == 'OVERALL_QUALITY':
                        try:
                            overall_score = float(value.split()[0])  # Get first number
                            overall_score = min(10.0, max(0.0, overall_score))
                        except (ValueError, IndexError):
                            overall_score = 5.0
                    
                    elif key == 'REASONING':
                        reasoning = value
            
            # Calculate overall score if not provided
            if overall_score == 0.0 and detailed_scores:
                overall_score = sum(detailed_scores.values()) / len(detailed_scores)
            
            return overall_score, detailed_scores, reasoning
            
        except Exception as e:
            logger.error(f"Error parsing validation response: {str(e)}")
            return 5.0, {}, f"Parsing error: {str(e)}"
    
    async def _calculate_consensus(self, results: List[ModelValidationResult], 
                                 script: str, metadata: Dict[str, Any]) -> ConsensusValidationResult:
        """Calculate consensus from multiple model validations"""
        try:
            if not results:
                raise ValueError("No successful validation results")
            
            # Calculate weighted consensus score
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for result in results:
                model_weight = next(
                    (m["weight"] for m in self.validation_models if m["name"] == result.model_name),
                    1.0
                )
                total_weighted_score += result.quality_score * model_weight
                total_weight += model_weight
            
            consensus_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Calculate agreement level
            scores = [r.quality_score for r in results]
            score_std = statistics.stdev(scores) if len(scores) > 1 else 0.0
            
            if score_std <= 0.5:
                agreement_level = "HIGH"
            elif score_std <= 1.0:
                agreement_level = "MEDIUM"
            elif score_std <= 1.5:
                agreement_level = "LOW"
            else:
                agreement_level = "VERY_LOW"
            
            # Calculate confidence score (based on agreement and number of models)
            confidence_base = len(results) / len(self.validation_models)  # Model coverage
            agreement_bonus = {"HIGH": 1.0, "MEDIUM": 0.8, "LOW": 0.6, "VERY_LOW": 0.4}[agreement_level]
            confidence_score = min(1.0, confidence_base * agreement_bonus)
            
            # Determine quality grade
            consensus_grade = self._score_to_grade(consensus_score)
            
            # Check quality threshold
            quality_threshold_passed = consensus_score >= self.quality_threshold
            regeneration_required = not quality_threshold_passed
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(
                results, consensus_score, script, metadata
            )
            
            return ConsensusValidationResult(
                consensus_score=round(consensus_score, 2),
                consensus_grade=consensus_grade,
                individual_results=results,
                agreement_level=agreement_level,
                confidence_score=round(confidence_score, 2),
                quality_threshold_passed=quality_threshold_passed,
                regeneration_required=regeneration_required,
                improvement_suggestions=improvement_suggestions
            )
            
        except Exception as e:
            logger.error(f"Error calculating consensus: {str(e)}")
            raise
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 9.5:
            return "A+"
        elif score >= 9.0:
            return "A"
        elif score >= 8.5:
            return "A-"
        elif score >= 8.0:
            return "B+"
        elif score >= 7.0:
            return "B"
        elif score >= 6.5:
            return "B-"
        elif score >= 6.0:
            return "C+"
        elif score >= 5.0:
            return "C"
        elif score >= 4.0:
            return "C-"
        elif score >= 3.0:
            return "D"
        else:
            return "F"
    
    async def _generate_improvement_suggestions(self, results: List[ModelValidationResult],
                                              consensus_score: float, script: str, 
                                              metadata: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on validation results"""
        suggestions = []
        
        try:
            # Analyze weak areas across all models
            weak_areas = {}
            for result in results:
                for criteria, score in result.detailed_scores.items():
                    if score < 7.0:  # Below good threshold
                        if criteria not in weak_areas:
                            weak_areas[criteria] = []
                        weak_areas[criteria].append(score)
            
            # Generate specific suggestions for weak areas
            for criteria, scores in weak_areas.items():
                avg_score = sum(scores) / len(scores)
                if avg_score < 6.0:  # Consistently weak area
                    if criteria == "hook_effectiveness":
                        suggestions.append("Strengthen opening hook - add curiosity gap or surprising element in first 3 seconds")
                    elif criteria == "narrative_structure":
                        suggestions.append("Improve story structure - ensure clear setup, conflict, and resolution")
                    elif criteria == "engagement_consistency":
                        suggestions.append("Add more engagement elements throughout - questions, callbacks, pattern interrupts")
                    elif criteria == "emotional_arc":
                        suggestions.append("Create stronger emotional journey - add emotional peaks and valleys")
                    elif criteria == "call_to_action":
                        suggestions.append("Strengthen call-to-action - make it more specific and compelling")
                    elif criteria == "platform_optimization":
                        suggestions.append(f"Optimize for {metadata.get('target_platform', 'platform')} - adjust pacing and format")
                    elif criteria == "readability_flow":
                        suggestions.append("Improve flow and readability - vary sentence length and add transitions")
            
            # Overall score-based suggestions
            if consensus_score < 6.0:
                suggestions.append("Consider complete script restructure - multiple fundamental issues identified")
            elif consensus_score < 8.0:
                suggestions.append("Focus on top 2-3 improvement areas for maximum impact")
            
            # Add regeneration notice if below threshold
            if consensus_score < self.quality_threshold:
                suggestions.insert(0, f"REGENERATION REQUIRED - Score {consensus_score:.1f} below threshold {self.quality_threshold}")
            
            return suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {str(e)}")
            return ["Unable to generate specific suggestions due to analysis error"]
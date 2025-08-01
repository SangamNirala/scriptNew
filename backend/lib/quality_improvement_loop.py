"""
Phase 5: Real-Time Quality Improvement Loop
Feedback-based prompt adjustment, dynamic system prompt evolution, and automatic optimization
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
from collections import defaultdict, deque
import numpy as np

from .multi_model_validator import MultiModelValidator, ConsensusValidationResult
from .advanced_quality_metrics import AdvancedQualityMetrics
from .prompt_optimization_engine import PromptOptimizationEngine
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

@dataclass
class ImprovementCycle:
    """Data class for improvement cycle tracking"""
    cycle_id: str
    original_prompt: str
    original_script: str
    original_score: float
    improvements_attempted: List[Dict[str, Any]]
    best_improvement: Optional[Dict[str, Any]]
    final_score: float
    cycles_completed: int
    success: bool
    timestamp: datetime

@dataclass
class PerformancePattern:
    """Data class for performance pattern analysis"""
    pattern_type: str
    success_indicators: List[str]
    failure_indicators: List[str]
    improvement_strategies: List[str]
    confidence_score: float

class QualityImprovementLoop:
    """
    Phase 5: Real-Time Quality Improvement Loop
    Automatic feedback-based improvement with dynamic system prompt evolution
    """
    
    def __init__(self, db, gemini_api_key: str):
        self.db = db
        self.gemini_api_key = gemini_api_key
        
        # Initialize components
        self.multi_model_validator = MultiModelValidator()
        self.advanced_metrics = AdvancedQualityMetrics()
        self.prompt_optimizer = PromptOptimizationEngine(db, gemini_api_key)
        
        # Collections for learning data
        self.improvement_cycles_collection = db.improvement_cycles
        self.performance_patterns_collection = db.performance_patterns
        self.system_prompt_evolution_collection = db.system_prompt_evolution
        
        # Quality threshold and improvement parameters
        self.quality_threshold = 8.5
        self.max_improvement_cycles = 3
        self.improvement_threshold = 0.5  # Minimum improvement to continue
        
        # Learning parameters for dynamic optimization
        self.learning_rate = 0.1
        self.pattern_confidence_threshold = 0.7
        
        # Performance history for pattern recognition
        self.performance_history = deque(maxlen=1000)
        self.success_patterns = {}
        self.failure_patterns = {}
        
        # Dynamic system prompts that evolve based on performance
        self.base_system_prompts = {
            "emotional_focus": """You are an elite emotional storytelling architect. Create video scripts that forge deep psychological connections through advanced emotional engineering techniques.""",
            "technical_focus": """You are a technical excellence specialist. Create video scripts with systematic frameworks, clear structure, and professional production standards.""",
            "viral_focus": """You are a viral content strategist. Create video scripts optimized for maximum shareability using 2025 algorithm preferences and psychological viral triggers.""",
            "retention_focus": """You are a retention optimization expert. Create video scripts engineered for maximum watch-through rates with strategic engagement hooks.""",
            "conversion_focus": """You are a conversion optimization specialist. Create video scripts designed to drive specific actions with compelling calls-to-action."""
        }
        
        # Evolved system prompts (updated based on performance data)
        self.evolved_system_prompts = self.base_system_prompts.copy()
        
        # A/B testing configurations
        self.ab_test_strategies = [
            "emotional_focus", "technical_focus", "viral_focus", 
            "retention_focus", "conversion_focus"
        ]
        
        self.ab_test_models = [
            "gemini-2.0-flash", "gemini-1.5-pro", 
            "meta-llama/llama-3.2-3b-instruct:free",
            "llama-3.3-70b-versatile"
        ]
    
    async def optimize_script_with_feedback_loop(self, original_prompt: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main optimization loop with automatic regeneration for low-quality scripts
        
        Args:
            original_prompt: The original user prompt
            metadata: Context information (platform, duration, etc.)
            
        Returns:
            Optimized script with improvement cycle data
        """
        try:
            metadata = metadata or {}
            cycle_id = str(uuid.uuid4())
            
            logger.info(f"Starting quality improvement loop for cycle {cycle_id}")
            
            # Initialize improvement cycle
            improvement_cycle = ImprovementCycle(
                cycle_id=cycle_id,
                original_prompt=original_prompt,
                original_script="",
                original_score=0.0,
                improvements_attempted=[],
                best_improvement=None,
                final_score=0.0,
                cycles_completed=0,
                success=False,
                timestamp=datetime.utcnow()
            )
            
            # Phase 1: Generate initial script with best known strategy
            best_strategy = await self._identify_best_strategy_for_prompt(original_prompt, metadata)
            initial_script = await self._generate_script_with_strategy(original_prompt, best_strategy, metadata)
            
            # Phase 2: Validate initial script quality
            initial_validation = await self.multi_model_validator.validate_script_quality(initial_script, metadata)
            
            improvement_cycle.original_script = initial_script
            improvement_cycle.original_score = initial_validation.consensus_score
            
            logger.info(f"Initial script score: {initial_validation.consensus_score}")
            
            # Phase 3: Check if regeneration is required
            if not initial_validation.quality_threshold_passed:
                logger.info(f"Quality threshold not met ({initial_validation.consensus_score} < {self.quality_threshold}). Starting improvement loop.")
                
                # Run improvement cycles
                improved_result = await self._run_improvement_cycles(
                    improvement_cycle, initial_script, initial_validation, metadata
                )
                
                if improved_result:
                    improvement_cycle.best_improvement = improved_result
                    improvement_cycle.final_score = improved_result["validation_result"].consensus_score
                    improvement_cycle.success = improved_result["validation_result"].quality_threshold_passed
                else:
                    improvement_cycle.final_score = initial_validation.consensus_score
                    improvement_cycle.success = False
            else:
                # Quality threshold already met
                improvement_cycle.final_score = initial_validation.consensus_score
                improvement_cycle.success = True
                logger.info(f"Initial script already meets quality threshold: {initial_validation.consensus_score}")
            
            # Phase 4: Learn from this cycle
            await self._learn_from_improvement_cycle(improvement_cycle)
            
            # Phase 5: Store improvement cycle data
            await self.improvement_cycles_collection.insert_one(improvement_cycle.__dict__)
            
            # Phase 6: Return optimized result
            final_script = improvement_cycle.best_improvement["script"] if improvement_cycle.best_improvement else initial_script
            final_validation = improvement_cycle.best_improvement["validation_result"] if improvement_cycle.best_improvement else initial_validation
            
            return {
                "cycle_id": cycle_id,
                "original_score": improvement_cycle.original_score,
                "final_score": improvement_cycle.final_score,
                "improvement_achieved": improvement_cycle.final_score - improvement_cycle.original_score,
                "quality_threshold_met": improvement_cycle.success,
                "cycles_completed": improvement_cycle.cycles_completed,
                "final_script": final_script,
                "validation_result": final_validation,
                "strategy_used": best_strategy,
                "improvements_attempted": len(improvement_cycle.improvements_attempted),
                "learning_insights": await self._generate_learning_insights(improvement_cycle)
            }
            
        except Exception as e:
            logger.error(f"Error in quality improvement loop: {str(e)}")
            return {
                "error": str(e),
                "cycle_id": cycle_id if 'cycle_id' in locals() else "unknown",
                "final_script": initial_script if 'initial_script' in locals() else "",
                "quality_threshold_met": False
            }
    
    async def run_ab_test_optimization(self, original_prompt: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run A/B testing for both prompt strategies AND AI models
        
        Args:
            original_prompt: The original user prompt
            metadata: Context information
            
        Returns:
            A/B test results with best performing combination
        """
        try:
            metadata = metadata or {}
            test_id = str(uuid.uuid4())
            
            logger.info(f"Starting A/B test optimization {test_id}")
            
            # Generate test variations combining strategies and models
            test_variations = []
            
            for strategy in self.ab_test_strategies[:3]:  # Test top 3 strategies
                for model in self.ab_test_models[:2]:     # Test top 2 models
                    test_variations.append({
                        "strategy": strategy,
                        "model": model,
                        "variation_id": f"{strategy}_{model}_{test_id[:8]}"
                    })
            
            # Run parallel A/B tests
            test_results = []
            test_tasks = []
            
            for variation in test_variations:
                task = self._run_single_ab_test(original_prompt, variation, metadata)
                test_tasks.append(task)
            
            results = await asyncio.gather(*test_tasks, return_exceptions=True)
            
            # Process results
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, dict) and "error" not in result:
                    result["variation"] = test_variations[i]
                    successful_results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"A/B test variation failed: {str(result)}")
            
            if not successful_results:
                return {"error": "All A/B test variations failed", "test_id": test_id}
            
            # Identify best performing combination
            best_result = max(successful_results, key=lambda x: x["validation_score"])
            
            # Calculate statistical significance
            statistical_analysis = await self._calculate_ab_test_significance(successful_results)
            
            # Update dynamic system prompts based on results
            await self._update_system_prompts_from_ab_test(successful_results)
            
            return {
                "test_id": test_id,
                "best_performing_combination": {
                    "strategy": best_result["variation"]["strategy"],
                    "model": best_result["variation"]["model"],
                    "score": best_result["validation_score"],
                    "script": best_result["script"]
                },
                "all_results": successful_results,
                "statistical_analysis": statistical_analysis,
                "performance_improvement": best_result["validation_score"] - min(r["validation_score"] for r in successful_results),
                "recommendations": await self._generate_ab_test_recommendations(successful_results)
            }
            
        except Exception as e:
            logger.error(f"Error in A/B test optimization: {str(e)}")
            return {"error": str(e), "test_id": test_id if 'test_id' in locals() else "unknown"}
    
    async def evolve_system_prompts(self) -> Dict[str, Any]:
        """
        Evolve system prompts based on accumulated performance data
        """
        try:
            logger.info("Starting system prompt evolution based on performance data")
            
            # Analyze recent performance patterns
            performance_patterns = await self._analyze_performance_patterns()
            
            # Identify successful prompt characteristics
            successful_characteristics = await self._identify_successful_prompt_characteristics()
            
            # Generate evolved system prompts
            evolved_prompts = {}
            evolution_improvements = {}
            
            for strategy, base_prompt in self.base_system_prompts.items():
                evolved_prompt = await self._evolve_single_system_prompt(
                    strategy, base_prompt, performance_patterns, successful_characteristics
                )
                evolved_prompts[strategy] = evolved_prompt
                
                # Test improvement
                improvement_score = await self._test_prompt_evolution_effectiveness(
                    strategy, base_prompt, evolved_prompt
                )
                evolution_improvements[strategy] = improvement_score
            
            # Update evolved prompts if improvements are significant
            significant_improvements = {}
            for strategy, improvement in evolution_improvements.items():
                if improvement > 0.3:  # 0.3 point improvement threshold
                    self.evolved_system_prompts[strategy] = evolved_prompts[strategy]
                    significant_improvements[strategy] = improvement
                    logger.info(f"Evolved system prompt for {strategy}: +{improvement:.2f} improvement")
            
            # Store evolution data
            evolution_record = {
                "evolution_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow(),
                "performance_patterns": performance_patterns,
                "successful_characteristics": successful_characteristics,
                "evolution_improvements": evolution_improvements,
                "significant_improvements": significant_improvements,
                "evolved_prompts": {k: v for k, v in evolved_prompts.items() if k in significant_improvements}
            }
            
            await self.system_prompt_evolution_collection.insert_one(evolution_record)
            
            return {
                "evolution_success": len(significant_improvements) > 0,
                "strategies_improved": list(significant_improvements.keys()),
                "average_improvement": statistics.mean(significant_improvements.values()) if significant_improvements else 0.0,
                "total_strategies_tested": len(evolved_prompts),
                "performance_patterns_analyzed": len(performance_patterns),
                "evolution_insights": await self._generate_evolution_insights(evolution_record)
            }
            
        except Exception as e:
            logger.error(f"Error in system prompt evolution: {str(e)}")
            return {"error": str(e), "evolution_success": False}
    
    # Core improvement cycle methods
    
    async def _run_improvement_cycles(self, improvement_cycle: ImprovementCycle, 
                                    current_script: str, current_validation: ConsensusValidationResult,
                                    metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run multiple improvement cycles until quality threshold is met or max cycles reached"""
        best_result = None
        current_best_score = current_validation.consensus_score
        
        for cycle_num in range(self.max_improvement_cycles):
            logger.info(f"Running improvement cycle {cycle_num + 1}/{self.max_improvement_cycles}")
            
            # Generate improvement based on validation feedback
            improvement_attempt = await self._generate_targeted_improvement(
                improvement_cycle.original_prompt, current_script, current_validation, metadata
            )
            
            if not improvement_attempt:
                logger.warning(f"Failed to generate improvement for cycle {cycle_num + 1}")
                continue
            
            # Validate improved script
            improved_validation = await self.multi_model_validator.validate_script_quality(
                improvement_attempt["script"], metadata
            )
            
            improvement_data = {
                "cycle_number": cycle_num + 1,
                "strategy_used": improvement_attempt["strategy"],
                "script": improvement_attempt["script"],
                "validation_result": improved_validation,
                "score_improvement": improved_validation.consensus_score - current_best_score,
                "timestamp": datetime.utcnow()
            }
            
            improvement_cycle.improvements_attempted.append(improvement_data)
            improvement_cycle.cycles_completed = cycle_num + 1
            
            # Check if this is the best result so far
            if improved_validation.consensus_score > current_best_score:
                best_result = improvement_data
                current_best_score = improved_validation.consensus_score
                logger.info(f"Improvement achieved: {improved_validation.consensus_score:.2f} (+{improvement_data['score_improvement']:.2f})")
                
                # Check if we've met the quality threshold
                if improved_validation.quality_threshold_passed:
                    logger.info("Quality threshold met, stopping improvement cycles")
                    break
            else:
                logger.info(f"No improvement in cycle {cycle_num + 1}: {improved_validation.consensus_score:.2f}")
            
            # Update current script for next cycle
            if best_result:
                current_script = best_result["script"]
                current_validation = best_result["validation_result"]
        
        return best_result
    
    async def _generate_targeted_improvement(self, original_prompt: str, current_script: str,
                                           validation_result: ConsensusValidationResult,
                                           metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate targeted improvement based on specific validation feedback"""
        try:
            # Analyze weakness areas from validation results
            weak_areas = []
            improvement_suggestions = validation_result.improvement_suggestions
            
            # Identify specific improvement strategy
            if any("hook" in suggestion.lower() for suggestion in improvement_suggestions):
                strategy = "hook_improvement"
            elif any("structure" in suggestion.lower() for suggestion in improvement_suggestions):
                strategy = "structure_improvement"
            elif any("engagement" in suggestion.lower() for suggestion in improvement_suggestions):
                strategy = "engagement_improvement"
            elif any("emotional" in suggestion.lower() for suggestion in improvement_suggestions):
                strategy = "emotional_improvement"
            elif any("cta" in suggestion.lower() or "call-to-action" in suggestion.lower() for suggestion in improvement_suggestions):
                strategy = "cta_improvement"
            else:
                strategy = "general_improvement"
            
            # Create targeted improvement prompt
            improvement_prompt = await self._create_targeted_improvement_prompt(
                original_prompt, current_script, validation_result, strategy, metadata
            )
            
            # Generate improved script
            improved_script = await self._generate_script_with_evolved_prompt(improvement_prompt, strategy, metadata)
            
            return {
                "strategy": strategy,
                "script": improved_script,
                "improvement_prompt": improvement_prompt,
                "target_areas": improvement_suggestions
            }
            
        except Exception as e:
            logger.error(f"Error generating targeted improvement: {str(e)}")
            return None
    
    async def _create_targeted_improvement_prompt(self, original_prompt: str, current_script: str,
                                                validation_result: ConsensusValidationResult,
                                                strategy: str, metadata: Dict[str, Any]) -> str:
        """Create targeted improvement prompt based on validation feedback"""
        platform = metadata.get('target_platform', 'general')
        duration = metadata.get('duration', 'medium')
        
        improvement_strategies = {
            "hook_improvement": f"""
TARGETED IMPROVEMENT: HOOK ENHANCEMENT

Original Prompt: {original_prompt}
Current Script Score: {validation_result.consensus_score}/10

SPECIFIC FEEDBACK TO ADDRESS:
{chr(10).join(validation_result.improvement_suggestions)}

HOOK IMPROVEMENT REQUIREMENTS:
1. Create a more compelling opening that grabs attention within 3 seconds
2. Add curiosity gap, surprising statistic, or bold statement
3. Include direct audience address ("you", "your")
4. Create immediate emotional connection
5. Promise clear value or revelation

CURRENT SCRIPT TO IMPROVE:
{current_script}

Create an improved version focusing specifically on a stronger hook while maintaining the core message.
""",
            "structure_improvement": f"""
TARGETED IMPROVEMENT: NARRATIVE STRUCTURE ENHANCEMENT

Original Prompt: {original_prompt}
Current Script Score: {validation_result.consensus_score}/10

STRUCTURAL IMPROVEMENTS NEEDED:
{chr(10).join(validation_result.improvement_suggestions)}

STRUCTURE ENHANCEMENT REQUIREMENTS:
1. Clear setup-conflict-resolution arc
2. Logical flow with smooth transitions
3. Strategic information reveal timing
4. Balanced pacing throughout
5. Strong conclusion that ties back to opening

CURRENT SCRIPT TO IMPROVE:
{current_script}

Restructure the script to create a more compelling narrative flow while keeping the core content.
""",
            "engagement_improvement": f"""
TARGETED IMPROVEMENT: ENGAGEMENT CONSISTENCY ENHANCEMENT

Original Prompt: {original_prompt}
Current Script Score: {validation_result.consensus_score}/10

ENGAGEMENT ISSUES TO FIX:
{chr(10).join(validation_result.improvement_suggestions)}

ENGAGEMENT ENHANCEMENT REQUIREMENTS:
1. Add engagement hooks every 15-20 seconds
2. Include more rhetorical questions
3. Add pattern interrupts and attention resets
4. Increase personal pronouns ("you", "your")
5. Create mini-cliffhangers between sections

CURRENT SCRIPT TO IMPROVE:
{current_script}

Enhance the script with consistent engagement elements throughout while maintaining the message.
"""
        }
        
        return improvement_strategies.get(strategy, f"""
GENERAL IMPROVEMENT REQUIRED

Original Prompt: {original_prompt}
Current Script Score: {validation_result.consensus_score}/10

AREAS NEEDING IMPROVEMENT:
{chr(10).join(validation_result.improvement_suggestions)}

CURRENT SCRIPT:
{current_script}

Create an improved version addressing the specific feedback while maintaining the core message and optimizing for {platform} platform.
""")
    
    async def _generate_script_with_strategy(self, prompt: str, strategy: str, metadata: Dict[str, Any]) -> str:
        """Generate script using specific strategy and evolved system prompt"""
        try:
            system_prompt = self.evolved_system_prompts.get(strategy, self.base_system_prompts.get(strategy, ""))
            
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=f"strategy-{strategy}-{datetime.utcnow().timestamp()}",
                system_message=system_prompt
            ).with_model("gemini", "gemini-2.0-flash")
            
            platform = metadata.get('target_platform', 'general')
            duration = metadata.get('duration', 'medium')
            video_type = metadata.get('video_type', 'general')
            
            generation_prompt = f"""Create a high-quality video script based on this prompt:

{prompt}

Requirements:
- Platform: {platform}
- Duration: {duration}  
- Video Type: {video_type}
- Strategy Focus: {strategy.replace('_', ' ').title()}

Create a complete script optimized for the specified strategy with:
1. Compelling hook within first 3 seconds
2. Clear structure and logical flow
3. Consistent engagement throughout
4. Strong emotional arc
5. Effective call-to-action

Format professionally with [scene directions] and (speaker notes)."""
            
            response = await chat.send_message(UserMessage(text=generation_prompt))
            return response
            
        except Exception as e:
            logger.error(f"Error generating script with strategy {strategy}: {str(e)}")
            return f"Error generating script: {str(e)}"
    
    async def _generate_script_with_evolved_prompt(self, improvement_prompt: str, strategy: str, metadata: Dict[str, Any]) -> str:
        """Generate improved script using evolved system prompt"""
        try:
            system_prompt = self.evolved_system_prompts.get(strategy, self.base_system_prompts.get("general", ""))
            
            chat = LlmChat(
                api_key=self.gemini_api_key,
                session_id=f"improvement-{strategy}-{datetime.utcnow().timestamp()}",
                system_message=f"{system_prompt}\n\nYou are specifically focused on targeted improvements based on quality validation feedback."
            ).with_model("gemini", "gemini-2.0-flash")
            
            response = await chat.send_message(UserMessage(text=improvement_prompt))
            return response
            
        except Exception as e:
            logger.error(f"Error generating improved script: {str(e)}")
            return improvement_prompt  # Fallback to original if generation fails
    
    # A/B Testing methods
    
    async def _run_single_ab_test(self, original_prompt: str, variation: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single A/B test variation"""
        try:
            strategy = variation["strategy"]
            model = variation["model"]
            
            # Generate script with specific strategy/model combination
            script = await self._generate_script_with_model(original_prompt, strategy, model, metadata)
            
            # Validate script quality
            validation_result = await self.multi_model_validator.validate_script_quality(script, metadata)
            
            return {
                "script": script,
                "validation_score": validation_result.consensus_score,
                "validation_result": validation_result,
                "strategy": strategy,
                "model": model
            }
            
        except Exception as e:
            logger.error(f"Error in single A/B test: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_script_with_model(self, prompt: str, strategy: str, model: str, metadata: Dict[str, Any]) -> str:
        """Generate script using specific model"""
        # This would implement model-specific generation
        # For now, using the main strategy-based generation
        return await self._generate_script_with_strategy(prompt, strategy, metadata)
    
    # Learning and Pattern Recognition methods
    
    async def _learn_from_improvement_cycle(self, improvement_cycle: ImprovementCycle):
        """Learn patterns from completed improvement cycle"""
        try:
            # Add to performance history
            self.performance_history.append({
                "original_score": improvement_cycle.original_score,
                "final_score": improvement_cycle.final_score,
                "improvement": improvement_cycle.final_score - improvement_cycle.original_score,
                "success": improvement_cycle.success,
                "cycles_needed": improvement_cycle.cycles_completed,
                "timestamp": improvement_cycle.timestamp
            })
            
            # Analyze success/failure patterns
            if improvement_cycle.success:
                await self._update_success_patterns(improvement_cycle)
            else:
                await self._update_failure_patterns(improvement_cycle)
                
        except Exception as e:
            logger.error(f"Error learning from improvement cycle: {str(e)}")
    
    async def _identify_best_strategy_for_prompt(self, prompt: str, metadata: Dict[str, Any]) -> str:
        """Identify best strategy based on prompt characteristics and historical performance"""
        try:
            prompt_lower = prompt.lower()
            
            # Analyze prompt characteristics
            if any(word in prompt_lower for word in ["feel", "emotion", "story", "heart", "inspire"]):
                return "emotional_focus"
            elif any(word in prompt_lower for word in ["how", "step", "guide", "tutorial", "explain"]):
                return "technical_focus"
            elif any(word in prompt_lower for word in ["viral", "trending", "share", "popular", "buzz"]):
                return "viral_focus"
            elif any(word in prompt_lower for word in ["subscribe", "buy", "click", "visit", "action"]):
                return "conversion_focus"
            else:
                return "retention_focus"  # Default to retention optimization
                
        except Exception as e:
            logger.error(f"Error identifying best strategy: {str(e)}")
            return "retention_focus"
    
    # Additional helper methods would continue here...
    # (Showing core structure due to length constraints)
    
    async def _generate_learning_insights(self, improvement_cycle: ImprovementCycle) -> List[str]:
        """Generate learning insights from improvement cycle"""
        insights = []
        
        if improvement_cycle.success:
            insights.append(f"Successfully improved script from {improvement_cycle.original_score:.1f} to {improvement_cycle.final_score:.1f}")
            insights.append(f"Required {improvement_cycle.cycles_completed} improvement cycles")
        else:
            insights.append(f"Could not achieve quality threshold despite {improvement_cycle.cycles_completed} improvement attempts")
            insights.append("Consider alternative strategy or manual review")
        
        return insights
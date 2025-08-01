"""
Phase 5: Intelligent Quality Assurance System
Master orchestrator for multi-model validation, advanced metrics, and quality improvement
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from .multi_model_validator import MultiModelValidator, ConsensusValidationResult
from .advanced_quality_metrics import AdvancedQualityMetrics
from .quality_improvement_loop import QualityImprovementLoop

logger = logging.getLogger(__name__)

@dataclass
class IntelligentQAResult:
    """Complete intelligent QA result"""
    qa_id: str
    original_prompt: str
    final_script: str
    quality_analysis: Dict[str, Any]
    consensus_validation: ConsensusValidationResult
    improvement_cycle_data: Optional[Dict[str, Any]]
    ab_test_data: Optional[Dict[str, Any]]
    quality_threshold_met: bool
    regeneration_performed: bool
    total_processing_time: float
    recommendations: List[str]
    confidence_score: float
    timestamp: datetime

class IntelligentQASystem:
    """
    Phase 5: Intelligent Quality Assurance System
    Master orchestrator combining all Phase 5 components for comprehensive quality assurance
    """
    
    def __init__(self, db, gemini_api_key: str):
        self.db = db
        self.gemini_api_key = gemini_api_key
        
        # Initialize all Phase 5 components
        self.multi_model_validator = MultiModelValidator()
        self.advanced_metrics = AdvancedQualityMetrics()
        self.quality_improvement_loop = QualityImprovementLoop(db, gemini_api_key)
        
        # System configuration
        self.quality_threshold = 8.5
        self.enable_auto_regeneration = True
        self.enable_ab_testing = True
        self.max_regeneration_attempts = 3
        
        # Collections for tracking
        self.qa_results_collection = db.intelligent_qa_results
        self.system_performance_collection = db.qa_system_performance
    
    async def comprehensive_qa_analysis(self, script: str, original_prompt: str = "", 
                                      metadata: Dict[str, Any] = None, 
                                      enable_regeneration: bool = True) -> IntelligentQAResult:
        """
        Run comprehensive intelligent QA analysis with all Phase 5 components
        
        Args:
            script: The script to analyze
            original_prompt: Original user prompt (for regeneration if needed)
            metadata: Context information
            enable_regeneration: Whether to enable automatic regeneration
            
        Returns:
            Complete intelligent QA result with all analysis data
        """
        start_time = datetime.utcnow()
        qa_id = f"qa_{int(start_time.timestamp())}"
        
        try:
            logger.info(f"Starting comprehensive QA analysis {qa_id}")
            
            metadata = metadata or {}
            
            # Phase 1: Multi-Model Consensus Validation
            logger.info("Phase 1: Multi-model consensus validation")
            consensus_validation = await self.multi_model_validator.validate_script_quality(script, metadata)
            
            # Phase 2: Advanced Quality Metrics Analysis
            logger.info("Phase 2: Advanced quality metrics analysis")
            quality_analysis = await self.advanced_metrics.analyze_comprehensive_quality(script, metadata)
            
            # Phase 3: Check Quality Threshold and Regeneration
            quality_threshold_met = consensus_validation.quality_threshold_passed
            regeneration_performed = False
            improvement_cycle_data = None
            final_script = script
            
            if not quality_threshold_met and enable_regeneration and original_prompt:
                logger.info(f"Quality threshold not met ({consensus_validation.consensus_score:.2f} < {self.quality_threshold}). Starting regeneration.")
                
                # Run quality improvement loop
                improvement_result = await self.quality_improvement_loop.optimize_script_with_feedback_loop(
                    original_prompt, metadata
                )
                
                if improvement_result.get("quality_threshold_met", False):
                    final_script = improvement_result["final_script"]
                    improvement_cycle_data = improvement_result
                    regeneration_performed = True
                    quality_threshold_met = True
                    
                    # Re-validate the improved script
                    consensus_validation = improvement_result["validation_result"]
                    quality_analysis = await self.advanced_metrics.analyze_comprehensive_quality(final_script, metadata)
                    
                    logger.info(f"Regeneration successful: {improvement_result['final_score']:.2f}")
                else:
                    logger.warning(f"Regeneration failed to meet quality threshold: {improvement_result.get('final_score', 0):.2f}")
            
            # Phase 4: Generate Comprehensive Recommendations
            recommendations = await self._generate_comprehensive_recommendations(
                consensus_validation, quality_analysis, improvement_cycle_data
            )
            
            # Phase 5: Calculate Overall Confidence Score
            confidence_score = await self._calculate_confidence_score(
                consensus_validation, quality_analysis, quality_threshold_met
            )
            
            # Phase 6: Create Final Result
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            qa_result = IntelligentQAResult(
                qa_id=qa_id,
                original_prompt=original_prompt,
                final_script=final_script,
                quality_analysis=quality_analysis,
                consensus_validation=consensus_validation,
                improvement_cycle_data=improvement_cycle_data,
                ab_test_data=None,  # Can be added later
                quality_threshold_met=quality_threshold_met,
                regeneration_performed=regeneration_performed,
                total_processing_time=processing_time,
                recommendations=recommendations,
                confidence_score=confidence_score,
                timestamp=datetime.utcnow()
            )
            
            # Store result
            await self.qa_results_collection.insert_one(qa_result.__dict__)
            
            # Update system performance metrics
            await self._update_system_performance_metrics(qa_result)
            
            logger.info(f"QA analysis completed in {processing_time:.2f}s. Final score: {consensus_validation.consensus_score:.2f}")
            
            return qa_result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error in comprehensive QA analysis: {str(e)}")
            
            # Return error result
            return IntelligentQAResult(
                qa_id=qa_id,
                original_prompt=original_prompt,
                final_script=script,
                quality_analysis={"error": str(e), "composite_quality_score": 0.0},
                consensus_validation=ConsensusValidationResult(
                    consensus_score=0.0,
                    consensus_grade="F",
                    individual_results=[],
                    agreement_level="ERROR",
                    confidence_score=0.0,
                    quality_threshold_passed=False,
                    regeneration_required=True,
                    improvement_suggestions=[f"System error: {str(e)}"]
                ),
                improvement_cycle_data=None,
                ab_test_data=None,
                quality_threshold_met=False,
                regeneration_performed=False,
                total_processing_time=processing_time,
                recommendations=["System error occurred - manual review required"],
                confidence_score=0.0,
                timestamp=datetime.utcnow()
            )
    
    async def run_ab_test_optimization(self, original_prompt: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run A/B testing optimization for both prompt strategies AND AI models
        
        Args:
            original_prompt: The original user prompt
            metadata: Context information
            
        Returns:
            A/B test optimization results
        """
        try:
            logger.info("Starting A/B test optimization")
            
            # Run A/B test through improvement loop
            ab_test_result = await self.quality_improvement_loop.run_ab_test_optimization(
                original_prompt, metadata
            )
            
            # If A/B test was successful, run full QA on the best result
            if "error" not in ab_test_result and "best_performing_combination" in ab_test_result:
                best_script = ab_test_result["best_performing_combination"]["script"]
                
                # Run comprehensive QA on the best result
                qa_result = await self.comprehensive_qa_analysis(
                    best_script, original_prompt, metadata, enable_regeneration=False
                )
                
                ab_test_result["comprehensive_qa"] = qa_result
            
            return ab_test_result
            
        except Exception as e:
            logger.error(f"Error in A/B test optimization: {str(e)}")
            return {"error": str(e)}
    
    async def evolve_system_prompts(self) -> Dict[str, Any]:
        """
        Evolve system prompts based on performance data
        """
        try:
            logger.info("Starting system prompt evolution")
            
            evolution_result = await self.quality_improvement_loop.evolve_system_prompts()
            
            # Update system performance tracking
            await self._track_prompt_evolution(evolution_result)
            
            return evolution_result
            
        except Exception as e:
            logger.error(f"Error in system prompt evolution: {str(e)}")
            return {"error": str(e), "evolution_success": False}
    
    async def get_qa_system_performance(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive QA system performance metrics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            System performance metrics and insights
        """
        try:
            # Fetch recent QA results
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            cursor = self.qa_results_collection.find({
                "timestamp": {"$gte": cutoff_date}
            }).sort("timestamp", -1)
            
            results = await cursor.to_list(1000)
            
            if not results:
                return {
                    "total_analyses": 0,
                    "message": "No QA results found in the specified period"
                }
            
            # Calculate performance metrics
            total_analyses = len(results)
            threshold_passed = sum(1 for r in results if r.get("quality_threshold_met", False))
            regenerations_performed = sum(1 for r in results if r.get("regeneration_performed", False))
            
            avg_processing_time = sum(r.get("total_processing_time", 0) for r in results) / total_analyses
            avg_confidence_score = sum(r.get("confidence_score", 0) for r in results) / total_analyses
            
            # Quality score distribution
            quality_scores = [r.get("consensus_validation", {}).get("consensus_score", 0) for r in results]
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Success rate trends
            success_rate = (threshold_passed / total_analyses) * 100 if total_analyses > 0 else 0
            regeneration_rate = (regenerations_performed / total_analyses) * 100 if total_analyses > 0 else 0
            
            return {
                "period_days": days,
                "total_analyses": total_analyses,
                "quality_metrics": {
                    "avg_quality_score": round(avg_quality_score, 2),
                    "threshold_pass_rate": round(success_rate, 1),
                    "regeneration_rate": round(regeneration_rate, 1),
                    "avg_confidence_score": round(avg_confidence_score, 2)
                },
                "performance_metrics": {
                    "avg_processing_time": round(avg_processing_time, 2),
                    "analyses_per_day": round(total_analyses / days, 1)
                },
                "quality_distribution": {
                    "excellent": sum(1 for s in quality_scores if s >= 9.0),
                    "good": sum(1 for s in quality_scores if 8.0 <= s < 9.0),
                    "acceptable": sum(1 for s in quality_scores if 7.0 <= s < 8.0),
                    "needs_improvement": sum(1 for s in quality_scores if s < 7.0)
                },
                "system_insights": await self._generate_system_insights(results)
            }
            
        except Exception as e:
            logger.error(f"Error getting QA system performance: {str(e)}")
            return {"error": str(e)}
    
    # Helper methods
    
    async def _generate_comprehensive_recommendations(self, consensus_validation: ConsensusValidationResult,
                                                   quality_analysis: Dict[str, Any],
                                                   improvement_data: Optional[Dict[str, Any]]) -> List[str]:
        """Generate comprehensive recommendations from all analyses"""
        recommendations = []
        
        # From consensus validation
        if consensus_validation.improvement_suggestions:
            recommendations.extend(consensus_validation.improvement_suggestions[:3])
        
        # From quality analysis
        quality_recs = quality_analysis.get("quality_recommendations", [])
        recommendations.extend(quality_recs[:2])
        
        # From improvement cycle
        if improvement_data and improvement_data.get("learning_insights"):
            recommendations.extend(improvement_data["learning_insights"][:2])
        
        # Add system-level recommendations
        if consensus_validation.consensus_score < 7.0:
            recommendations.append("Consider fundamental restructuring - multiple quality issues detected")
        elif consensus_validation.agreement_level == "LOW":
            recommendations.append("Mixed model feedback - consider alternative approaches")
        
        return recommendations[:5]  # Limit to top 5
    
    async def _calculate_confidence_score(self, consensus_validation: ConsensusValidationResult,
                                        quality_analysis: Dict[str, Any],
                                        threshold_met: bool) -> float:
        """Calculate overall confidence score"""
        confidence_factors = []
        
        # Consensus confidence
        confidence_factors.append(consensus_validation.confidence_score)
        
        # Quality analysis confidence (based on composite score)
        quality_score = quality_analysis.get("composite_quality_score", 0.0)
        quality_confidence = min(1.0, quality_score / 10.0)
        confidence_factors.append(quality_confidence)
        
        # Agreement level confidence
        agreement_bonuses = {"HIGH": 1.0, "MEDIUM": 0.8, "LOW": 0.6, "VERY_LOW": 0.4}
        agreement_confidence = agreement_bonuses.get(consensus_validation.agreement_level, 0.4)
        confidence_factors.append(agreement_confidence)
        
        # Threshold achievement bonus
        if threshold_met:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.5)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    async def _update_system_performance_metrics(self, qa_result: IntelligentQAResult):
        """Update system performance tracking"""
        try:
            performance_record = {
                "qa_id": qa_result.qa_id,
                "timestamp": qa_result.timestamp,
                "quality_score": qa_result.consensus_validation.consensus_score,
                "threshold_met": qa_result.quality_threshold_met,
                "regeneration_performed": qa_result.regeneration_performed,
                "processing_time": qa_result.total_processing_time,
                "confidence_score": qa_result.confidence_score,
                "agreement_level": qa_result.consensus_validation.agreement_level
            }
            
            await self.system_performance_collection.insert_one(performance_record)
            
        except Exception as e:
            logger.error(f"Error updating system performance metrics: {str(e)}")
    
    async def _track_prompt_evolution(self, evolution_result: Dict[str, Any]):
        """Track prompt evolution performance"""
        try:
            if evolution_result.get("evolution_success", False):
                logger.info(f"Prompt evolution successful: {evolution_result.get('strategies_improved', [])}")
            
        except Exception as e:
            logger.error(f"Error tracking prompt evolution: {str(e)}")
    
    async def _generate_system_insights(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate system-level insights from QA results"""
        insights = []
        
        if not results:
            return ["No data available for insights"]
        
        # Quality trends
        avg_score = sum(r.get("consensus_validation", {}).get("consensus_score", 0) for r in results) / len(results)
        insights.append(f"Average quality score: {avg_score:.1f}/10")
        
        # Regeneration patterns
        regen_rate = sum(1 for r in results if r.get("regeneration_performed", False)) / len(results) * 100
        if regen_rate > 30:
            insights.append(f"High regeneration rate ({regen_rate:.1f}%) - consider prompt optimization")
        
        # Performance trends
        avg_time = sum(r.get("total_processing_time", 0) for r in results) / len(results)
        insights.append(f"Average processing time: {avg_time:.1f} seconds")
        
        return insights
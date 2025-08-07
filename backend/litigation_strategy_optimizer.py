"""
Litigation Strategy Optimizer Module

AI-powered strategic litigation recommendations including optimal filing jurisdiction,
timing recommendations, evidence assessment, and comprehensive litigation planning
based on case analysis and predictive modeling.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import numpy as np
import google.generativeai as genai
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

# Import other litigation analytics modules
from litigation_analytics_engine import LitigationAnalyticsEngine, CaseData, PredictionResult
from case_outcome_predictor import EnsembleCasePredictor, CaseFeatures
from judicial_behavior_analyzer import JudicialBehaviorAnalyzer, JudicialProfile
from settlement_probability_calculator import SettlementProbabilityCalculator, SettlementAnalysis

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    COLLABORATIVE = "collaborative"
    PROCEDURAL = "procedural"
    SETTLEMENT_FOCUSED = "settlement_focused"
    TRIAL_FOCUSED = "trial_focused"

class ActionPriority(Enum):
    CRITICAL = "critical"    # Must do immediately
    HIGH = "high"           # Should do within 30 days
    MEDIUM = "medium"       # Should do within 90 days
    LOW = "low"            # Can defer beyond 90 days

@dataclass
class StrategicRecommendation:
    """Individual strategic recommendation with priority and timing"""
    recommendation_id: str
    title: str
    description: str
    priority: ActionPriority
    category: str  # e.g., "Discovery", "Motion Practice", "Settlement"
    estimated_cost: Optional[float] = None
    estimated_timeframe: Optional[str] = None
    success_probability: Optional[float] = None
    risk_level: str = "medium"  # low, medium, high
    dependencies: List[str] = field(default_factory=list)  # Other recommendation IDs
    supporting_evidence: List[str] = field(default_factory=list)

@dataclass
class JurisdictionAnalysis:
    """Analysis of optimal filing jurisdiction"""
    jurisdiction: str
    suitability_score: float  # 0.0 - 1.0
    advantages: List[str] = field(default_factory=list)
    disadvantages: List[str] = field(default_factory=list)
    average_case_duration: Optional[float] = None
    success_rate_for_case_type: Optional[float] = None
    settlement_rate: Optional[float] = None
    estimated_costs: Optional[float] = None

@dataclass 
class TimingAnalysis:
    """Optimal timing analysis for various litigation actions"""
    action_type: str  # e.g., "Filing", "Discovery Completion", "Motion Filing"
    optimal_window: Tuple[datetime, datetime]
    urgency_level: str  # "low", "medium", "high", "critical"
    rationale: str
    dependencies: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)

@dataclass
class EvidenceAssessment:
    """Comprehensive evidence strength assessment"""
    overall_strength: float  # 0.0 - 1.0
    key_strengths: List[str] = field(default_factory=list)
    critical_weaknesses: List[str] = field(default_factory=list)
    evidence_gaps: List[str] = field(default_factory=list)
    discovery_priorities: List[str] = field(default_factory=list)
    witness_reliability: Dict[str, float] = field(default_factory=dict)
    document_quality: float = 0.5
    expert_witness_needs: List[str] = field(default_factory=list)

@dataclass
class LitigationStrategy:
    """Comprehensive litigation strategy analysis"""
    case_id: str
    strategy_date: datetime
    recommended_strategy_type: StrategyType
    confidence_score: float
    
    # Core analyses
    case_outcome_prediction: Optional[PredictionResult] = None
    settlement_analysis: Optional[SettlementAnalysis] = None
    judicial_insights: Optional[Dict[str, Any]] = None
    
    # Strategic recommendations
    strategic_recommendations: List[StrategicRecommendation] = field(default_factory=list)
    jurisdiction_analysis: List[JurisdictionAnalysis] = field(default_factory=list)
    timing_analysis: List[TimingAnalysis] = field(default_factory=list)
    evidence_assessment: Optional[EvidenceAssessment] = None
    
    # Cost-benefit analysis
    estimated_total_cost: Optional[float] = None
    expected_value: Optional[float] = None
    roi_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Risk assessment
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    
    # AI insights
    ai_strategic_summary: str = ""
    alternative_strategies: List[Dict[str, Any]] = field(default_factory=list)

class LitigationStrategyOptimizer:
    """Main strategy optimization engine"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        
        # Initialize component analyzers
        self.analytics_engine = LitigationAnalyticsEngine(db_connection)
        self.outcome_predictor = EnsembleCasePredictor(db_connection)
        self.judicial_analyzer = JudicialBehaviorAnalyzer(db_connection)
        self.settlement_calculator = SettlementProbabilityCalculator(db_connection)
        
        logger.info("🎯 Litigation Strategy Optimizer initialized")

    async def optimize_litigation_strategy(self, case_data: Dict[str, Any]) -> LitigationStrategy:
        """Generate comprehensive litigation strategy optimization"""
        try:
            case_id = case_data.get('case_id', str(uuid.uuid4()))
            logger.info(f"🎯 Optimizing litigation strategy for case {case_id}")
            
            # Run parallel analyses
            analyses = await self._run_parallel_analyses(case_data)
            
            # Determine optimal strategy type
            strategy_type = self._determine_strategy_type(case_data, analyses)
            
            # Generate strategic recommendations
            recommendations = await self._generate_strategic_recommendations(case_data, analyses, strategy_type)
            
            # Analyze jurisdiction options
            jurisdiction_analysis = await self._analyze_jurisdictions(case_data)
            
            # Optimize timing
            timing_analysis = self._optimize_timing(case_data, analyses)
            
            # Assess evidence strength
            evidence_assessment = self._assess_evidence_strength(case_data, analyses)
            
            # Calculate costs and ROI
            cost_analysis = self._calculate_cost_benefit_analysis(case_data, analyses)
            
            # Generate AI strategic summary
            ai_summary = await self._generate_ai_strategic_summary(case_data, analyses, strategy_type)
            
            # Create comprehensive strategy
            strategy = LitigationStrategy(
                case_id=case_id,
                strategy_date=datetime.utcnow(),
                recommended_strategy_type=strategy_type,
                confidence_score=self._calculate_strategy_confidence(analyses),
                case_outcome_prediction=analyses.get('outcome_prediction'),
                settlement_analysis=analyses.get('settlement_analysis'),
                judicial_insights=analyses.get('judicial_insights'),
                strategic_recommendations=recommendations,
                jurisdiction_analysis=jurisdiction_analysis,
                timing_analysis=timing_analysis,
                evidence_assessment=evidence_assessment,
                estimated_total_cost=cost_analysis.get('total_cost'),
                expected_value=cost_analysis.get('expected_value'),
                roi_analysis=cost_analysis.get('roi_analysis', {}),
                risk_factors=self._identify_risk_factors(case_data, analyses),
                mitigation_strategies=self._develop_mitigation_strategies(case_data, analyses),
                ai_strategic_summary=ai_summary,
                alternative_strategies=self._generate_alternative_strategies(case_data, analyses)
            )
            
            # Cache strategy for future reference
            await self._cache_litigation_strategy(strategy)
            
            logger.info(f"✅ Strategy optimization completed for case {case_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"❌ Strategy optimization failed: {e}")
            return self._create_default_strategy(case_data.get('case_id', 'unknown'))

    async def _run_parallel_analyses(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all component analyses in parallel for efficiency"""
        try:
            # Prepare case data for different analyzers
            litigation_case_data = CaseData(
                case_id=case_data.get('case_id', str(uuid.uuid4())),
                case_type=case_data.get('case_type', 'civil'),
                jurisdiction=case_data.get('jurisdiction', 'federal'),
                court_level=case_data.get('court_level', 'district'),
                judge_name=case_data.get('judge_name'),
                case_facts=case_data.get('case_facts'),
                legal_issues=case_data.get('legal_issues', []),
                case_complexity=case_data.get('case_complexity'),
                case_value=case_data.get('case_value'),
                filing_date=case_data.get('filing_date'),
                evidence_strength=case_data.get('evidence_strength')
            )
            
            # Run analyses in parallel
            results = await asyncio.gather(
                self.analytics_engine.analyze_case_outcome(litigation_case_data),
                self.settlement_calculator.calculate_settlement_probability(case_data),
                self._get_judicial_insights(case_data),
                return_exceptions=True
            )
            
            # Process results
            analyses = {}
            
            if not isinstance(results[0], Exception):
                analyses['outcome_prediction'] = results[0]
            else:
                logger.warning(f"⚠️ Outcome prediction failed: {results[0]}")
            
            if not isinstance(results[1], Exception):
                analyses['settlement_analysis'] = results[1]
            else:
                logger.warning(f"⚠️ Settlement analysis failed: {results[1]}")
            
            if not isinstance(results[2], Exception):
                analyses['judicial_insights'] = results[2]
            else:
                logger.warning(f"⚠️ Judicial insights failed: {results[2]}")
            
            return analyses
            
        except Exception as e:
            logger.error(f"❌ Parallel analyses failed: {e}")
            return {}

    async def _get_judicial_insights(self, case_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get judicial insights if judge is specified"""
        judge_name = case_data.get('judge_name')
        if not judge_name:
            return None
        
        try:
            return await self.judicial_analyzer.get_judge_insights_for_case(
                judge_name=judge_name,
                case_type=case_data.get('case_type', 'civil'),
                case_value=case_data.get('case_value')
            )
        except Exception as e:
            logger.warning(f"⚠️ Judicial insights retrieval failed: {e}")
            return None

    def _determine_strategy_type(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> StrategyType:
        """Determine optimal strategy type based on case analysis"""
        # Analyze case characteristics
        evidence_strength = case_data.get('evidence_strength', 0.5)
        case_value = case_data.get('case_value', 0)
        
        # Get settlement probability if available
        settlement_analysis = analyses.get('settlement_analysis')
        settlement_probability = settlement_analysis.metrics.settlement_probability if settlement_analysis else 0.4
        
        # Get outcome prediction confidence
        outcome_prediction = analyses.get('outcome_prediction')
        outcome_confidence = outcome_prediction.confidence_score if outcome_prediction else 0.5
        
        # Decision logic
        if settlement_probability > 0.7:
            return StrategyType.SETTLEMENT_FOCUSED
        elif evidence_strength > 0.8 and outcome_confidence > 0.7:
            return StrategyType.AGGRESSIVE
        elif evidence_strength < 0.3 or outcome_confidence < 0.4:
            return StrategyType.CONSERVATIVE
        elif case_value > 1000000:
            return StrategyType.PROCEDURAL  # High-value cases need careful procedure
        else:
            return StrategyType.COLLABORATIVE

    async def _generate_strategic_recommendations(self, case_data: Dict[str, Any], analyses: Dict[str, Any], 
                                                strategy_type: StrategyType) -> List[StrategicRecommendation]:
        """Generate comprehensive strategic recommendations"""
        recommendations = []
        
        # Discovery recommendations
        recommendations.extend(self._generate_discovery_recommendations(case_data, analyses))
        
        # Motion practice recommendations
        recommendations.extend(self._generate_motion_recommendations(case_data, analyses, strategy_type))
        
        # Settlement recommendations
        recommendations.extend(self._generate_settlement_recommendations(case_data, analyses))
        
        # Trial preparation recommendations
        recommendations.extend(self._generate_trial_recommendations(case_data, analyses, strategy_type))
        
        # Case management recommendations
        recommendations.extend(self._generate_case_management_recommendations(case_data, analyses))
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: (x.priority.value, -x.success_probability if x.success_probability else 0))
        
        return recommendations[:15]  # Top 15 recommendations

    def _generate_discovery_recommendations(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> List[StrategicRecommendation]:
        """Generate discovery-specific recommendations"""
        recommendations = []
        evidence_strength = case_data.get('evidence_strength', 0.5)
        
        if evidence_strength < 0.6:
            recommendations.append(StrategicRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Comprehensive Document Discovery",
                description="Conduct thorough document discovery to strengthen evidence base and identify key supporting materials.",
                priority=ActionPriority.HIGH,
                category="Discovery",
                estimated_cost=15000.0,
                estimated_timeframe="90-120 days",
                success_probability=0.8,
                risk_level="medium",
                supporting_evidence=["Evidence strength below optimal threshold", "Document discovery often reveals crucial evidence"]
            ))
        
        recommendations.append(StrategicRecommendation(
            recommendation_id=str(uuid.uuid4()),
            title="Key Witness Depositions",
            description="Identify and depose key witnesses early in the discovery process to lock in testimony and assess case strength.",
            priority=ActionPriority.HIGH,
            category="Discovery",
            estimated_cost=8000.0,
            estimated_timeframe="60-90 days",
            success_probability=0.75,
            risk_level="medium"
        ))
        
        return recommendations

    def _generate_motion_recommendations(self, case_data: Dict[str, Any], analyses: Dict[str, Any], 
                                       strategy_type: StrategyType) -> List[StrategicRecommendation]:
        """Generate motion practice recommendations"""
        recommendations = []
        evidence_strength = case_data.get('evidence_strength', 0.5)
        
        # Summary judgment recommendations
        if evidence_strength > 0.7 and strategy_type in [StrategyType.AGGRESSIVE, StrategyType.PROCEDURAL]:
            recommendations.append(StrategicRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Motion for Summary Judgment",
                description="File motion for summary judgment based on strong evidence and clear legal standards.",
                priority=ActionPriority.MEDIUM,
                category="Motion Practice",
                estimated_cost=12000.0,
                estimated_timeframe="30-45 days to prepare",
                success_probability=evidence_strength * 0.8,  # Success correlates with evidence strength
                risk_level="medium"
            ))
        
        # Procedural motions
        if strategy_type == StrategyType.PROCEDURAL:
            recommendations.append(StrategicRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Strategic Motion to Dismiss",
                description="File targeted motion to dismiss to narrow issues and reduce case complexity.",
                priority=ActionPriority.HIGH,
                category="Motion Practice",
                estimated_cost=5000.0,
                estimated_timeframe="21 days",
                success_probability=0.6,
                risk_level="low"
            ))
        
        return recommendations

    def _generate_settlement_recommendations(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> List[StrategicRecommendation]:
        """Generate settlement-focused recommendations"""
        recommendations = []
        settlement_analysis = analyses.get('settlement_analysis')
        
        if settlement_analysis and settlement_analysis.metrics.settlement_probability > 0.5:
            recommendations.append(StrategicRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Early Settlement Negotiations",
                description=f"Initiate settlement discussions with {settlement_analysis.metrics.settlement_probability:.1%} probability of success.",
                priority=ActionPriority.HIGH if settlement_analysis.metrics.settlement_probability > 0.7 else ActionPriority.MEDIUM,
                category="Settlement",
                estimated_cost=3000.0,
                estimated_timeframe="30-60 days",
                success_probability=settlement_analysis.metrics.settlement_probability,
                risk_level="low"
            ))
        
        if settlement_analysis and settlement_analysis.metrics.optimal_timing.value == 'mediation':
            recommendations.append(StrategicRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Professional Mediation",
                description="Engage professional mediator for structured settlement negotiations.",
                priority=ActionPriority.MEDIUM,
                category="Settlement",
                estimated_cost=5000.0,
                estimated_timeframe="1-2 mediation sessions",
                success_probability=0.65,
                risk_level="low"
            ))
        
        return recommendations

    def _generate_trial_recommendations(self, case_data: Dict[str, Any], analyses: Dict[str, Any], 
                                      strategy_type: StrategyType) -> List[StrategicRecommendation]:
        """Generate trial preparation recommendations"""
        recommendations = []
        
        if strategy_type in [StrategyType.AGGRESSIVE, StrategyType.TRIAL_FOCUSED]:
            recommendations.append(StrategicRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Expert Witness Retention",
                description="Retain qualified expert witnesses to support key technical or industry-specific arguments.",
                priority=ActionPriority.MEDIUM,
                category="Trial Preparation",
                estimated_cost=25000.0,
                estimated_timeframe="120 days before trial",
                success_probability=0.7,
                risk_level="medium"
            ))
        
        recommendations.append(StrategicRecommendation(
            recommendation_id=str(uuid.uuid4()),
            title="Trial Graphics and Technology",
            description="Prepare compelling visual presentations and leverage courtroom technology for effective advocacy.",
            priority=ActionPriority.LOW,
            category="Trial Preparation",
            estimated_cost=8000.0,
            estimated_timeframe="60 days before trial",
            success_probability=0.6,
            risk_level="low"
        ))
        
        return recommendations

    def _generate_case_management_recommendations(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> List[StrategicRecommendation]:
        """Generate case management and administrative recommendations"""
        recommendations = []
        
        recommendations.append(StrategicRecommendation(
            recommendation_id=str(uuid.uuid4()),
            title="Case Management Conference Strategy",
            description="Prepare comprehensive case management plan to control scheduling and discovery timeline.",
            priority=ActionPriority.HIGH,
            category="Case Management",
            estimated_cost=2000.0,
            estimated_timeframe="Within 30 days",
            success_probability=0.9,
            risk_level="low"
        ))
        
        # Budget and resource planning
        case_value = case_data.get('case_value', 0)
        if case_value > 500000:
            recommendations.append(StrategicRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Litigation Budget and Resource Planning",
                description="Develop comprehensive litigation budget and resource allocation plan for high-value case.",
                priority=ActionPriority.HIGH,
                category="Case Management",
                estimated_cost=1500.0,
                estimated_timeframe="Within 14 days",
                success_probability=0.95,
                risk_level="low"
            ))
        
        return recommendations

    async def _analyze_jurisdictions(self, case_data: Dict[str, Any]) -> List[JurisdictionAnalysis]:
        """Analyze optimal filing jurisdictions"""
        try:
            jurisdictions = ['federal', 'california', 'new_york', 'texas', 'delaware']
            analyses = []
            
            current_jurisdiction = case_data.get('jurisdiction', '').lower()
            
            for jurisdiction in jurisdictions:
                # Calculate suitability score based on various factors
                score = await self._calculate_jurisdiction_suitability(case_data, jurisdiction)
                
                analysis = JurisdictionAnalysis(
                    jurisdiction=jurisdiction,
                    suitability_score=score,
                    advantages=self._get_jurisdiction_advantages(jurisdiction, case_data),
                    disadvantages=self._get_jurisdiction_disadvantages(jurisdiction, case_data),
                    average_case_duration=self._estimate_jurisdiction_duration(jurisdiction),
                    success_rate_for_case_type=self._estimate_jurisdiction_success_rate(jurisdiction, case_data.get('case_type')),
                    settlement_rate=self._estimate_jurisdiction_settlement_rate(jurisdiction)
                )
                
                analyses.append(analysis)
            
            # Sort by suitability score
            analyses.sort(key=lambda x: x.suitability_score, reverse=True)
            
            return analyses[:5]  # Top 5 jurisdictions
            
        except Exception as e:
            logger.warning(f"⚠️ Jurisdiction analysis failed: {e}")
            return []

    async def _calculate_jurisdiction_suitability(self, case_data: Dict[str, Any], jurisdiction: str) -> float:
        """Calculate suitability score for a jurisdiction"""
        score = 0.5  # Base score
        
        case_type = case_data.get('case_type', '')
        case_value = case_data.get('case_value', 0)
        
        # Jurisdiction-specific adjustments
        if jurisdiction == 'federal':
            if case_value > 75000:  # Federal diversity threshold
                score += 0.2
            if case_type in ['intellectual_property', 'securities']:
                score += 0.3
        
        elif jurisdiction == 'delaware':
            if case_type == 'corporate':
                score += 0.4
            if case_value > 1000000:
                score += 0.2
        
        elif jurisdiction == 'california':
            if case_type in ['employment', 'consumer']:
                score += 0.3
            if case_data.get('parties_in_ca'):
                score += 0.2
        
        return min(1.0, max(0.0, score))

    def _get_jurisdiction_advantages(self, jurisdiction: str, case_data: Dict[str, Any]) -> List[str]:
        """Get advantages of filing in specific jurisdiction"""
        advantages = {
            'federal': [
                "Experienced federal judges",
                "Streamlined procedures",
                "Nationwide enforcement",
                "Limited local bias"
            ],
            'california': [
                "Pro-plaintiff employment laws",
                "Large jury awards potential",
                "Strong consumer protections",
                "Technology-savvy courts"
            ],
            'delaware': [
                "Corporate law expertise",
                "Business-friendly procedures",
                "Expedited case scheduling",
                "Sophisticated commercial courts"
            ],
            'new_york': [
                "Commercial law expertise",
                "Efficient case management",
                "Strong discovery rules",
                "Financial services expertise"
            ],
            'texas': [
                "Business-friendly environment",
                "Reasonable damage awards",
                "Efficient court system",
                "Strong contract enforcement"
            ]
        }
        
        return advantages.get(jurisdiction, ["General litigation advantages"])

    def _get_jurisdiction_disadvantages(self, jurisdiction: str, case_data: Dict[str, Any]) -> List[str]:
        """Get disadvantages of filing in specific jurisdiction"""
        disadvantages = {
            'federal': [
                "Higher filing fees",
                "More complex procedures",
                "Limited local law expertise",
                "Potential for removal"
            ],
            'california': [
                "Pro-defendant recent trends",
                "High litigation costs",
                "Crowded court dockets",
                "Complex state procedures"
            ],
            'delaware': [
                "Limited jury trial options",
                "High attorney fees",
                "Corporate-defendant friendly",
                "Limited discovery timeline"
            ]
        }
        
        return disadvantages.get(jurisdiction, ["Standard litigation challenges"])

    def _estimate_jurisdiction_duration(self, jurisdiction: str) -> float:
        """Estimate average case duration in jurisdiction (days)"""
        durations = {
            'federal': 545,
            'california': 680,
            'delaware': 420,
            'new_york': 510,
            'texas': 475
        }
        
        return durations.get(jurisdiction, 500)

    def _estimate_jurisdiction_success_rate(self, jurisdiction: str, case_type: Optional[str]) -> float:
        """Estimate success rate for case type in jurisdiction"""
        # This would ideally use historical data
        base_rates = {
            'federal': 0.48,
            'california': 0.52,
            'delaware': 0.45,
            'new_york': 0.50,
            'texas': 0.46
        }
        
        return base_rates.get(jurisdiction, 0.48)

    def _estimate_jurisdiction_settlement_rate(self, jurisdiction: str) -> float:
        """Estimate settlement rate in jurisdiction"""
        settlement_rates = {
            'federal': 0.68,
            'california': 0.71,
            'delaware': 0.62,
            'new_york': 0.65,
            'texas': 0.64
        }
        
        return settlement_rates.get(jurisdiction, 0.65)

    def _optimize_timing(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> List[TimingAnalysis]:
        """Optimize timing for various litigation actions"""
        timing_analyses = []
        
        # Filing timing
        timing_analyses.append(TimingAnalysis(
            action_type="Case Filing",
            optimal_window=(datetime.utcnow(), datetime.utcnow() + timedelta(days=30)),
            urgency_level="high",
            rationale="Early filing preserves claims and initiates discovery timeline"
        ))
        
        # Discovery completion timing
        settlement_analysis = analyses.get('settlement_analysis')
        if settlement_analysis and settlement_analysis.metrics.optimal_timing.value == 'mid':
            timing_analyses.append(TimingAnalysis(
                action_type="Discovery Completion",
                optimal_window=(datetime.utcnow() + timedelta(days=90), datetime.utcnow() + timedelta(days=180)),
                urgency_level="medium",
                rationale="Mid-case discovery completion aligns with optimal settlement timing"
            ))
        
        # Settlement initiation timing
        if settlement_analysis and settlement_analysis.metrics.settlement_probability > 0.5:
            urgency = "high" if settlement_analysis.metrics.settlement_urgency_score > 0.7 else "medium"
            timing_analyses.append(TimingAnalysis(
                action_type="Settlement Negotiations",
                optimal_window=(datetime.utcnow() + timedelta(days=60), datetime.utcnow() + timedelta(days=120)),
                urgency_level=urgency,
                rationale=f"Settlement probability is {settlement_analysis.metrics.settlement_probability:.1%}"
            ))
        
        return timing_analyses

    def _assess_evidence_strength(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> EvidenceAssessment:
        """Comprehensive evidence strength assessment"""
        overall_strength = case_data.get('evidence_strength', 0.5)
        
        # Determine strengths and weaknesses based on evidence strength
        key_strengths = []
        critical_weaknesses = []
        evidence_gaps = []
        
        if overall_strength > 0.7:
            key_strengths.extend([
                "Strong documentary evidence",
                "Reliable witness testimony",
                "Clear liability indicators"
            ])
        elif overall_strength > 0.4:
            key_strengths.extend([
                "Adequate evidentiary support",
                "Some witness corroboration"
            ])
            evidence_gaps.append("Additional supporting evidence needed")
        else:
            critical_weaknesses.extend([
                "Insufficient documentary evidence",
                "Witness credibility concerns",
                "Gaps in liability chain"
            ])
            evidence_gaps.extend([
                "Core liability evidence",
                "Damages documentation",
                "Expert witness support"
            ])
        
        # Discovery priorities based on weaknesses
        discovery_priorities = []
        if overall_strength < 0.6:
            discovery_priorities.extend([
                "Document preservation and collection",
                "Key witness identification and interviews",
                "Expert witness consultation"
            ])
        
        return EvidenceAssessment(
            overall_strength=overall_strength,
            key_strengths=key_strengths,
            critical_weaknesses=critical_weaknesses,
            evidence_gaps=evidence_gaps,
            discovery_priorities=discovery_priorities,
            document_quality=overall_strength * 0.9,  # Assume documents are primary evidence
            expert_witness_needs=["Industry expert", "Damages expert"] if case_data.get('case_value', 0) > 500000 else []
        )

    def _calculate_cost_benefit_analysis(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive cost-benefit analysis"""
        case_value = case_data.get('case_value', 100000)
        
        # Estimate litigation costs
        base_cost = 50000  # Base litigation cost
        complexity_multiplier = 1 + (case_data.get('case_complexity', 0.5) * 1.5)
        duration_multiplier = 1.2 if case_value > 1000000 else 1.0
        
        estimated_total_cost = base_cost * complexity_multiplier * duration_multiplier
        
        # Calculate expected value
        outcome_prediction = analyses.get('outcome_prediction')
        if outcome_prediction:
            win_probability = outcome_prediction.probability_breakdown.get('plaintiff_win', 0.3)
            expected_value = (case_value * win_probability) - estimated_total_cost
        else:
            expected_value = (case_value * 0.4) - estimated_total_cost  # Default 40% win rate
        
        # ROI analysis
        roi_scenarios = {
            'best_case': (case_value * 0.8 - estimated_total_cost) / estimated_total_cost if estimated_total_cost > 0 else 0,
            'expected_case': expected_value / estimated_total_cost if estimated_total_cost > 0 else 0,
            'worst_case': (0 - estimated_total_cost) / estimated_total_cost if estimated_total_cost > 0 else -1
        }
        
        return {
            'total_cost': estimated_total_cost,
            'expected_value': expected_value,
            'roi_analysis': roi_scenarios
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_ai_strategic_summary(self, case_data: Dict[str, Any], analyses: Dict[str, Any], strategy_type: StrategyType) -> str:
        """Generate AI-powered strategic summary"""
        try:
            summary_prompt = f"""
            LITIGATION STRATEGY OPTIMIZATION - COMPREHENSIVE ANALYSIS
            
            CASE OVERVIEW:
            - Case Type: {case_data.get('case_type', 'Unknown')}
            - Case Value: ${case_data.get('case_value', 0):,.2f}
            - Evidence Strength: {case_data.get('evidence_strength', 0.5):.1%}
            - Case Complexity: {case_data.get('case_complexity', 0.5):.1%}
            - Jurisdiction: {case_data.get('jurisdiction', 'Unknown')}
            - Judge: {case_data.get('judge_name', 'Not assigned')}
            
            PREDICTIVE ANALYSIS RESULTS:
            """
            
            # Add outcome prediction results
            outcome_prediction = analyses.get('outcome_prediction')
            if outcome_prediction:
                summary_prompt += f"""
            OUTCOME PREDICTION:
            - Most Likely Outcome: {outcome_prediction.predicted_outcome.value.replace('_', ' ').title()}
            - Confidence Score: {outcome_prediction.confidence_score:.1%}
            - Estimated Duration: {outcome_prediction.estimated_duration or 365} days
            - Estimated Cost: ${outcome_prediction.estimated_cost or 50000:,.2f}
            """
            
            # Add settlement analysis
            settlement_analysis = analyses.get('settlement_analysis')
            if settlement_analysis:
                summary_prompt += f"""
            SETTLEMENT ANALYSIS:
            - Settlement Probability: {settlement_analysis.metrics.settlement_probability:.1%}
            - Expected Settlement Value: ${settlement_analysis.metrics.expected_settlement_value:,.2f}
            - Optimal Settlement Timing: {settlement_analysis.metrics.optimal_timing.value.replace('_', ' ').title()}
            - Settlement Urgency: {settlement_analysis.metrics.settlement_urgency_score:.1%}
            """
            
            # Add judicial insights
            judicial_insights = analyses.get('judicial_insights')
            if judicial_insights:
                summary_prompt += f"""
            JUDICIAL INSIGHTS:
            - Judge Experience: {judicial_insights.get('experience_years', 'Unknown')} years
            - Settlement Rate: {judicial_insights.get('overall_metrics', {}).get('settlement_rate', 0):.1%}
            - Plaintiff Success Rate: {judicial_insights.get('overall_metrics', {}).get('plaintiff_success_rate', 0):.1%}
            """
            
            summary_prompt += f"""
            
            RECOMMENDED STRATEGY TYPE: {strategy_type.value.replace('_', ' ').title()}
            
            Please provide a comprehensive strategic analysis covering:
            1. Overall case assessment and strategic positioning
            2. Key opportunities and potential challenges
            3. Recommended approach and tactical priorities
            4. Risk mitigation strategies
            5. Alternative strategies to consider
            6. Timeline and resource allocation recommendations
            
            Focus on actionable strategic insights for litigation counsel.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                summary_prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.warning(f"⚠️ AI strategic summary generation failed: {e}")
            return self._generate_fallback_summary(case_data, strategy_type)

    def _generate_fallback_summary(self, case_data: Dict[str, Any], strategy_type: StrategyType) -> str:
        """Generate fallback summary when AI fails"""
        return f"""
        LITIGATION STRATEGY SUMMARY
        
        Recommended Strategy: {strategy_type.value.replace('_', ' ').title()}
        
        Based on case analysis, this {case_data.get('case_type', 'litigation')} matter with 
        ${case_data.get('case_value', 0):,.2f} at stake requires a {strategy_type.value.replace('_', ' ')} approach.
        
        Key considerations include case complexity at {case_data.get('case_complexity', 0.5):.1%} 
        and evidence strength at {case_data.get('evidence_strength', 0.5):.1%}.
        
        Recommend proceeding with comprehensive discovery, strategic motion practice, 
        and parallel settlement discussions as appropriate.
        """

    def _calculate_strategy_confidence(self, analyses: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the strategy"""
        confidence_scores = []
        
        # Outcome prediction confidence
        outcome_prediction = analyses.get('outcome_prediction')
        if outcome_prediction:
            confidence_scores.append(outcome_prediction.confidence_score)
        
        # Settlement analysis confidence
        settlement_analysis = analyses.get('settlement_analysis')
        if settlement_analysis:
            confidence_scores.append(settlement_analysis.metrics.confidence_score)
        
        # Judicial insights confidence
        judicial_insights = analyses.get('judicial_insights')
        if judicial_insights:
            confidence_scores.append(judicial_insights.get('confidence_score', 0.5))
        
        # Base confidence if no analyses available
        if not confidence_scores:
            return 0.6
        
        return sum(confidence_scores) / len(confidence_scores)

    def _identify_risk_factors(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> List[str]:
        """Identify key risk factors for the litigation"""
        risk_factors = []
        
        # Evidence-based risks
        evidence_strength = case_data.get('evidence_strength', 0.5)
        if evidence_strength < 0.4:
            risk_factors.append("Weak evidence may undermine case viability")
        
        # Complexity risks
        complexity = case_data.get('case_complexity', 0.5)
        if complexity > 0.7:
            risk_factors.append("High case complexity increases cost and duration risks")
        
        # Value-based risks
        case_value = case_data.get('case_value', 0)
        if case_value > 1000000:
            risk_factors.append("High case value increases stakes and opponent resistance")
        
        # Settlement analysis risks
        settlement_analysis = analyses.get('settlement_analysis')
        if settlement_analysis and hasattr(settlement_analysis, 'risk_assessment'):
            risk_factors.extend(settlement_analysis.risk_assessment.get('high_risks', [])[:2])
        
        # Judicial risks
        judicial_insights = analyses.get('judicial_insights')
        if judicial_insights and judicial_insights.get('confidence_score', 1.0) < 0.5:
            risk_factors.append("Limited judicial insights increase uncertainty")
        
        return risk_factors[:5]  # Top 5 risk factors

    def _develop_mitigation_strategies(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> List[str]:
        """Develop strategies to mitigate identified risks"""
        strategies = []
        
        # Evidence mitigation
        evidence_strength = case_data.get('evidence_strength', 0.5)
        if evidence_strength < 0.4:
            strategies.append("Aggressive discovery to strengthen evidence base")
            strategies.append("Early expert witness retention to support weak areas")
        
        # Complexity mitigation
        complexity = case_data.get('case_complexity', 0.5)
        if complexity > 0.7:
            strategies.append("Phased litigation approach to manage complexity")
            strategies.append("Specialized counsel consultation for complex issues")
        
        # Cost mitigation
        case_value = case_data.get('case_value', 0)
        if case_value > 1000000:
            strategies.append("Structured fee arrangements to manage cost risk")
            strategies.append("Insurance coverage evaluation and notification")
        
        # Settlement-focused mitigation
        settlement_analysis = analyses.get('settlement_analysis')
        if settlement_analysis and settlement_analysis.metrics.settlement_probability > 0.5:
            strategies.append("Early settlement discussions to avoid litigation risks")
        
        return strategies[:5]  # Top 5 mitigation strategies

    def _generate_alternative_strategies(self, case_data: Dict[str, Any], analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative strategy options"""
        alternatives = []
        
        # Alternative 1: Settlement-focused approach
        settlement_analysis = analyses.get('settlement_analysis')
        if settlement_analysis:
            alternatives.append({
                'strategy_name': 'Settlement-Focused Strategy',
                'description': 'Prioritize early resolution through negotiation and mediation',
                'pros': ['Lower costs', 'Faster resolution', 'Controlled outcome'],
                'cons': ['May leave money on table', 'No precedent value'],
                'estimated_cost': 25000,
                'estimated_duration': 90,
                'success_probability': settlement_analysis.metrics.settlement_probability
            })
        
        # Alternative 2: Aggressive litigation
        outcome_prediction = analyses.get('outcome_prediction')
        if outcome_prediction and outcome_prediction.confidence_score > 0.6:
            alternatives.append({
                'strategy_name': 'Aggressive Trial Strategy',
                'description': 'Pursue maximum recovery through aggressive litigation and trial',
                'pros': ['Maximum potential recovery', 'Precedent setting', 'Deterrent effect'],
                'cons': ['Higher costs', 'Longer timeline', 'Uncertain outcome'],
                'estimated_cost': 150000,
                'estimated_duration': 730,
                'success_probability': outcome_prediction.probability_breakdown.get('plaintiff_win', 0.4)
            })
        
        # Alternative 3: Hybrid approach
        alternatives.append({
            'strategy_name': 'Hybrid Approach',
            'description': 'Balanced strategy combining litigation pressure with settlement readiness',
            'pros': ['Flexibility', 'Maintains leverage', 'Multiple resolution paths'],
            'cons': ['Complex coordination', 'Resource intensive'],
            'estimated_cost': 75000,
            'estimated_duration': 365,
            'success_probability': 0.6
        })
        
        return alternatives

    async def _cache_litigation_strategy(self, strategy: LitigationStrategy):
        """Cache litigation strategy for future reference"""
        try:
            strategy_dict = {
                'case_id': strategy.case_id,
                'strategy_date': strategy.strategy_date,
                'recommended_strategy_type': strategy.recommended_strategy_type.value,
                'confidence_score': strategy.confidence_score,
                'estimated_total_cost': strategy.estimated_total_cost,
                'expected_value': strategy.expected_value,
                'strategic_recommendations': [
                    {
                        'title': rec.title,
                        'description': rec.description,
                        'priority': rec.priority.value,
                        'category': rec.category,
                        'estimated_cost': rec.estimated_cost,
                        'success_probability': rec.success_probability
                    }
                    for rec in strategy.strategic_recommendations
                ],
                'risk_factors': strategy.risk_factors,
                'mitigation_strategies': strategy.mitigation_strategies,
                'ai_strategic_summary': strategy.ai_strategic_summary,
                'alternative_strategies': strategy.alternative_strategies
            }
            
            await self.db.litigation_strategies.update_one(
                {'case_id': strategy.case_id},
                {'$set': strategy_dict},
                upsert=True
            )
            
            logger.info(f"💾 Cached litigation strategy for case {strategy.case_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Strategy caching failed: {e}")

    def _create_default_strategy(self, case_id: str) -> LitigationStrategy:
        """Create default strategy when optimization fails"""
        return LitigationStrategy(
            case_id=case_id,
            strategy_date=datetime.utcnow(),
            recommended_strategy_type=StrategyType.COLLABORATIVE,
            confidence_score=0.5,
            strategic_recommendations=[
                StrategicRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    title="Initial Case Assessment",
                    description="Conduct comprehensive case assessment and evidence review",
                    priority=ActionPriority.HIGH,
                    category="Case Management",
                    estimated_cost=5000.0,
                    success_probability=0.9
                )
            ],
            ai_strategic_summary="Strategy optimization pending additional case information and analysis."
        )

# Global optimizer instance
_strategy_optimizer = None

async def get_litigation_strategy_optimizer(db_connection) -> LitigationStrategyOptimizer:
    """Get or create litigation strategy optimizer instance"""
    global _strategy_optimizer
    
    if _strategy_optimizer is None:
        _strategy_optimizer = LitigationStrategyOptimizer(db_connection)
        logger.info("🎯 Litigation Strategy Optimizer instance created")
    
    return _strategy_optimizer

async def initialize_litigation_strategy_optimizer(db_connection):
    """Initialize the litigation strategy optimizer"""
    await get_litigation_strategy_optimizer(db_connection)
    logger.info("✅ Litigation Strategy Optimizer initialized successfully")
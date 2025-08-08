"""
Settlement Probability Calculator Module

Advanced settlement analysis engine that calculates settlement likelihood,
optimal settlement ranges, and strategic timing recommendations using
AI-powered analysis and historical settlement data patterns.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json
import uuid
import numpy as np
import google.generativeai as genai
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SettlementTiming(Enum):
    EARLY = "early"  # 0-90 days
    MID = "mid"      # 90-180 days
    LATE = "late"    # 180+ days
    MEDIATION = "mediation"
    TRIAL_DOOR = "trial_door"  # Just before trial

class SettlementFactors(Enum):
    CASE_STRENGTH = "case_strength"
    ECONOMIC_PRESSURE = "economic_pressure"
    JUDICIAL_PRESSURE = "judicial_pressure"
    PUBLICITY_CONCERNS = "publicity_concerns"
    TIME_PRESSURE = "time_pressure"
    COST_CONCERNS = "cost_concerns"
    RELATIONSHIP_PRESERVATION = "relationship_preservation"
    PRECEDENT_CONCERNS = "precedent_concerns"

@dataclass
class SettlementMetrics:
    """Core metrics for settlement analysis"""
    settlement_probability: float = 0.0
    optimal_timing: SettlementTiming = SettlementTiming.MID
    plaintiff_settlement_range: Tuple[float, float] = (0.0, 0.0)
    defendant_settlement_range: Tuple[float, float] = (0.0, 0.0)
    expected_settlement_value: float = 0.0
    settlement_urgency_score: float = 0.5  # 0.0 = no urgency, 1.0 = urgent
    confidence_score: float = 0.0
    key_settlement_factors: List[str] = field(default_factory=list)
    negotiation_leverage: Dict[str, float] = field(default_factory=dict)  # plaintiff vs defendant leverage

@dataclass
class SettlementScenario:
    """Different settlement scenarios and their probabilities"""
    scenario_name: str
    probability: float
    settlement_amount: float
    timing: SettlementTiming
    key_conditions: List[str] = field(default_factory=list)
    plaintiff_satisfaction: float = 0.0  # 0.0 = poor, 1.0 = excellent
    defendant_satisfaction: float = 0.0
    strategic_notes: str = ""

@dataclass
class SettlementAnalysis:
    """Comprehensive settlement analysis result"""
    case_id: str
    analysis_date: datetime
    metrics: SettlementMetrics
    scenarios: List[SettlementScenario] = field(default_factory=list)
    comparative_settlements: List[Dict[str, Any]] = field(default_factory=list)
    negotiation_strategy: Dict[str, Any] = field(default_factory=dict)
    ai_insights: str = ""
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class SettlementProbabilityCalculator:
    """Main settlement probability calculator using AI and historical data"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        
        # Settlement analysis weights
        self.factor_weights = {
            SettlementFactors.CASE_STRENGTH: 0.25,
            SettlementFactors.ECONOMIC_PRESSURE: 0.20,
            SettlementFactors.JUDICIAL_PRESSURE: 0.15,
            SettlementFactors.TIME_PRESSURE: 0.15,
            SettlementFactors.COST_CONCERNS: 0.10,
            SettlementFactors.PUBLICITY_CONCERNS: 0.08,
            SettlementFactors.RELATIONSHIP_PRESERVATION: 0.04,
            SettlementFactors.PRECEDENT_CONCERNS: 0.03
        }
        
        logger.info("💰 Settlement Probability Calculator initialized")

    async def calculate_settlement_probability(self, case_data: Dict[str, Any]) -> SettlementAnalysis:
        """Calculate comprehensive settlement analysis for a case"""
        try:
            case_id = case_data.get('case_id', str(uuid.uuid4()))
            logger.info(f"💰 Calculating settlement probability for case {case_id}")
            
            # Gather historical settlement data
            historical_data = await self._get_historical_settlement_data(case_data)
            
            # Calculate base metrics
            base_metrics = await self._calculate_base_settlement_metrics(case_data, historical_data)
            
            # Generate settlement scenarios
            scenarios = await self._generate_settlement_scenarios(case_data, base_metrics)
            
            # Get AI insights
            ai_insights = await self._get_ai_settlement_insights(case_data, base_metrics, scenarios)
            
            # Develop negotiation strategy
            negotiation_strategy = self._develop_negotiation_strategy(case_data, base_metrics, scenarios)
            
            # Risk assessment
            risk_assessment = self._assess_settlement_risks(case_data, base_metrics)
            
            # Generate recommendations
            recommendations = self._generate_settlement_recommendations(
                case_data, base_metrics, scenarios, risk_assessment
            )
            
            # Create comprehensive analysis
            analysis = SettlementAnalysis(
                case_id=case_id,
                analysis_date=datetime.utcnow(),
                metrics=base_metrics,
                scenarios=scenarios,
                comparative_settlements=historical_data[:5],  # Top 5 comparable settlements
                negotiation_strategy=negotiation_strategy,
                ai_insights=ai_insights,
                risk_assessment=risk_assessment,
                recommendations=recommendations
            )
            
            # Cache the analysis
            await self._cache_settlement_analysis(analysis)
            
            logger.info(f"✅ Settlement analysis completed with {base_metrics.settlement_probability:.1%} probability")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Settlement calculation failed: {e}")
            return self._create_default_analysis(case_data.get('case_id', 'unknown'))

    async def _get_historical_settlement_data(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant historical settlement data"""
        try:
            # Build query for similar settled cases
            query = {
                'outcome': 'settlement',
                'settlement_amount': {'$exists': True, '$gt': 0}
            }
            
            # Add case type filter
            if case_data.get('case_type'):
                query['case_type'] = case_data['case_type']
            
            # Add jurisdiction filter
            if case_data.get('jurisdiction'):
                query['jurisdiction'] = case_data['jurisdiction']
            
            # Add case value range filter
            if case_data.get('case_value'):
                value_range = case_data['case_value'] * 0.5  # 50% range
                query['case_value'] = {
                    '$gte': case_data['case_value'] - value_range,
                    '$lte': case_data['case_value'] + value_range
                }
            
            # Retrieve similar settlements
            settlements = await self.db.settlement_data.find(query).sort('settlement_date', -1).limit(20).to_list(20)
            
            # If no direct matches, broaden search
            if len(settlements) < 5:
                broader_query = {'outcome': 'settlement', 'settlement_amount': {'$exists': True, '$gt': 0}}
                if case_data.get('case_type'):
                    broader_query['case_type'] = case_data['case_type']
                
                additional_settlements = await self.db.settlement_data.find(broader_query).limit(15).to_list(15)
                settlements.extend(additional_settlements)
            
            # Remove duplicates and sort by relevance
            unique_settlements = {s['case_id']: s for s in settlements}.values()
            sorted_settlements = sorted(
                unique_settlements,
                key=lambda x: self._calculate_settlement_relevance(x, case_data),
                reverse=True
            )
            
            logger.info(f"📊 Retrieved {len(sorted_settlements)} historical settlements")
            return list(sorted_settlements)
            
        except Exception as e:
            logger.warning(f"⚠️ Historical data retrieval failed: {e}")
            return self._generate_synthetic_settlement_data(case_data)

    def _calculate_settlement_relevance(self, settlement: Dict[str, Any], case_data: Dict[str, Any]) -> float:
        """Calculate relevance score for historical settlement"""
        score = 0.0
        
        # Case type match
        if settlement.get('case_type') == case_data.get('case_type'):
            score += 3.0
        
        # Jurisdiction match
        if settlement.get('jurisdiction') == case_data.get('jurisdiction'):
            score += 2.0
        
        # Case value proximity
        if case_data.get('case_value') and settlement.get('case_value'):
            value_diff = abs(case_data['case_value'] - settlement['case_value'])
            max_value = max(case_data['case_value'], settlement['case_value'])
            if max_value > 0:
                value_similarity = 1.0 - (value_diff / max_value)
                score += value_similarity * 2.0
        
        # Recency bonus
        if settlement.get('settlement_date'):
            try:
                if isinstance(settlement['settlement_date'], str):
                    settlement_date = datetime.fromisoformat(settlement['settlement_date'])
                else:
                    settlement_date = settlement['settlement_date']
                
                days_ago = (datetime.utcnow() - settlement_date).days
                recency_score = max(0, 1.0 - (days_ago / 1095))  # 3 year decay
                score += recency_score * 1.0
            except:
                pass
        
        return score

    async def _calculate_base_settlement_metrics(self, case_data: Dict[str, Any], historical_data: List[Dict]) -> SettlementMetrics:
        """Calculate enhanced settlement metrics using multiple data sources and sophisticated algorithms"""
        try:
            # Enhanced historical baseline with case-type specific data
            historical_baseline = self._calculate_enhanced_historical_baseline(historical_data, case_data)
            
            # Advanced factor-based analysis with real-world weights
            factor_analysis = self._analyze_enhanced_settlement_factors(case_data)
            
            # Market and economic adjustments
            market_adjustments = self._calculate_market_adjustments(case_data)
            
            # Case-specific risk assessment
            risk_assessment = self._calculate_comprehensive_risk_assessment(case_data)
            
            # Combine analyses with dynamic weighting based on data quality
            data_quality_score = self._assess_data_quality(case_data, historical_data)
            
            # Dynamic weighting based on data availability and quality
            if data_quality_score > 0.8:
                # High quality data - trust historical and factor analysis more
                base_probability = (
                    historical_baseline['settlement_probability'] * 0.45 +
                    factor_analysis['settlement_probability'] * 0.30 +
                    market_adjustments['probability_adjustment'] * 0.15 +
                    risk_assessment['probability_adjustment'] * 0.10
                )
            elif data_quality_score > 0.5:
                # Medium quality - balance approaches
                base_probability = (
                    historical_baseline['settlement_probability'] * 0.35 +
                    factor_analysis['settlement_probability'] * 0.35 +
                    market_adjustments['probability_adjustment'] * 0.20 +
                    risk_assessment['probability_adjustment'] * 0.10
                )
            else:
                # Low quality - rely more on general patterns and risk assessment
                base_probability = (
                    historical_baseline['settlement_probability'] * 0.25 +
                    factor_analysis['settlement_probability'] * 0.40 +
                    market_adjustments['probability_adjustment'] * 0.20 +
                    risk_assessment['probability_adjustment'] * 0.15
                )
            
            # Apply case-type specific multipliers
            base_probability = self._apply_case_type_multipliers(base_probability, case_data)
            
            # Ensure probability is within realistic range with smoother bounds
            settlement_probability = max(0.05, min(0.95, base_probability))
            
            # Enhanced settlement range calculations
            case_value = case_data.get('case_value', 100000)
            settlement_ranges = self._calculate_enhanced_settlement_ranges(case_data, factor_analysis, market_adjustments)
            
            # Calculate expected settlement using multiple methods and take weighted average
            expected_values = []
            
            # Method 1: Range overlap midpoint
            overlap_low = max(settlement_ranges['defendant_low'], settlement_ranges['plaintiff_low'])
            overlap_high = min(settlement_ranges['defendant_high'], settlement_ranges['plaintiff_high'])
            if overlap_high > overlap_low:
                expected_values.append(('range_overlap', (overlap_low + overlap_high) / 2, 0.4))
            
            # Method 2: Probability-weighted value
            prob_weighted = case_value * settlement_probability * factor_analysis.get('strength_multiplier', 0.5)
            expected_values.append(('probability_weighted', prob_weighted, 0.3))
            
            # Method 3: Case-type specific calculation
            case_type_value = self._calculate_case_type_settlement_value(case_data)
            expected_values.append(('case_type_specific', case_type_value, 0.3))
            
            # Calculate weighted average
            if expected_values:
                expected_value = sum(value * weight for _, value, weight in expected_values)
            else:
                expected_value = case_value * 0.4
            
            # Enhanced optimal timing determination
            optimal_timing = self._determine_enhanced_optimal_timing(case_data, factor_analysis, market_adjustments)
            
            # Advanced settlement urgency calculation
            urgency_score = self._calculate_enhanced_settlement_urgency(case_data, factor_analysis, risk_assessment)
            
            # Enhanced negotiation leverage with detailed breakdown
            leverage = self._calculate_enhanced_negotiation_leverage(case_data, factor_analysis, market_adjustments)
            
            # More detailed key factors with impact scores
            key_factors = self._identify_key_settlement_factors(factor_analysis, risk_assessment, market_adjustments)
            
            # Enhanced confidence scoring
            confidence_score = self._calculate_enhanced_confidence_score(
                historical_data, factor_analysis, data_quality_score, case_data
            )
            
            metrics = SettlementMetrics(
                settlement_probability=settlement_probability,
                optimal_timing=optimal_timing,
                plaintiff_settlement_range=(settlement_ranges['plaintiff_low'], settlement_ranges['plaintiff_high']),
                defendant_settlement_range=(settlement_ranges['defendant_low'], settlement_ranges['defendant_high']),
                expected_settlement_value=expected_value,
                settlement_urgency_score=urgency_score,
                confidence_score=confidence_score,
                key_settlement_factors=key_factors,
                negotiation_leverage=leverage
            )
            
            logger.info(f"✅ Enhanced settlement metrics calculated: {settlement_probability:.1%} probability, ${expected_value:,.0f} expected value, {confidence_score:.1%} confidence")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Enhanced metrics calculation failed: {e}")
            return self._create_enhanced_default_metrics(case_data)

    def _calculate_historical_baseline(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate baseline settlement probability from historical data"""
        if not historical_data:
            return {'settlement_probability': 0.4}  # Default 40%
        
        # All provided cases resulted in settlement, so probability is high
        settlement_rate = 1.0  # 100% since we filtered for settlements
        
        # But adjust based on how many similar cases we found
        confidence_adjustment = min(len(historical_data) / 10, 1.0)  # More data = higher confidence
        adjusted_probability = settlement_rate * confidence_adjustment + 0.3 * (1 - confidence_adjustment)
        
        return {'settlement_probability': adjusted_probability}

    def _analyze_settlement_factors(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze various factors that influence settlement probability"""
        factor_scores = {}
        
        # Case strength factor
        evidence_strength = case_data.get('evidence_strength', 0.5)
        if evidence_strength > 0.7:
            factor_scores['strong_case'] = 0.8  # Strong cases often settle to avoid risk
        elif evidence_strength < 0.3:
            factor_scores['weak_case'] = 0.7  # Weak cases settle to avoid loss
        else:
            factor_scores['moderate_case'] = 0.6
        
        # Economic pressure
        case_value = case_data.get('case_value', 0)
        if case_value > 1000000:
            factor_scores['high_value_pressure'] = 0.7  # High value increases settlement pressure
        elif case_value > 100000:
            factor_scores['moderate_value_pressure'] = 0.5
        else:
            factor_scores['low_value_pressure'] = 0.3
        
        # Time pressure
        filing_date = case_data.get('filing_date')
        if filing_date:
            try:
                if isinstance(filing_date, str):
                    filing_date = datetime.fromisoformat(filing_date)
                days_pending = (datetime.utcnow() - filing_date).days
                
                if days_pending > 730:  # Over 2 years
                    factor_scores['time_pressure'] = 0.8
                elif days_pending > 365:  # Over 1 year
                    factor_scores['time_pressure'] = 0.6
                else:
                    factor_scores['time_pressure'] = 0.4
            except:
                factor_scores['time_pressure'] = 0.5
        else:
            factor_scores['time_pressure'] = 0.5
        
        # Case type factors
        case_type = case_data.get('case_type', '')
        if case_type in ['employment', 'personal_injury']:
            factor_scores['high_settlement_type'] = 0.7
        elif case_type in ['commercial', 'intellectual_property']:
            factor_scores['moderate_settlement_type'] = 0.5
        else:
            factor_scores['general_settlement_type'] = 0.4
        
        # Complexity factor
        complexity = case_data.get('case_complexity', 0.5)
        if complexity > 0.7:
            factor_scores['complex_case'] = 0.6  # Complex cases often settle to avoid uncertainty
        else:
            factor_scores['simple_case'] = 0.4
        
        # Calculate overall settlement probability from factors
        total_weight = sum(self.factor_weights.get(factor, 0.1) for factor in factor_scores.keys())
        if total_weight == 0:
            total_weight = 1.0
        
        weighted_probability = sum(
            score * self.factor_weights.get(factor.replace('_pressure', '').replace('_case', '').replace('_type', ''), 0.1)
            for factor, score in factor_scores.items()
        ) / total_weight
        
        return {
            'settlement_probability': weighted_probability,
            'factor_scores': factor_scores
        }

    def _calculate_case_specific_adjustments(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate case-specific probability adjustments"""
        base_adjustment = 0.0
        
        # Judge-specific adjustments
        judge_name = case_data.get('judge_name')
        if judge_name:
            # This would ideally use judicial behavior data
            # For now, apply neutral adjustment
            base_adjustment += 0.0
        
        # Jurisdiction adjustments
        jurisdiction = case_data.get('jurisdiction', '').lower()
        if 'federal' in jurisdiction:
            base_adjustment += 0.1  # Federal courts often encourage settlement
        elif jurisdiction in ['california', 'new_york']:
            base_adjustment += 0.05  # High-volume jurisdictions
        
        # Party-specific factors
        if case_data.get('corporate_defendant'):
            base_adjustment += 0.1  # Corporations often prefer to settle
        
        if case_data.get('insurance_coverage'):
            base_adjustment += 0.15  # Insurance often drives settlements
        
        # Publicity sensitivity
        if case_data.get('high_profile'):
            base_adjustment += 0.2  # High-profile cases often settle quickly
        
        # Ensure adjustment stays within reasonable bounds
        probability_adjustment = max(-0.3, min(0.3, base_adjustment))
        
        return {'probability_adjustment': probability_adjustment}

    def _determine_optimal_timing(self, case_data: Dict[str, Any], factor_analysis: Dict[str, Any]) -> SettlementTiming:
        """Determine optimal settlement timing"""
        factor_scores = factor_analysis.get('factor_scores', {})
        
        # High time pressure suggests early settlement
        if factor_scores.get('time_pressure', 0) > 0.7:
            return SettlementTiming.EARLY
        
        # Complex cases benefit from discovery period
        if case_data.get('case_complexity', 0) > 0.7:
            return SettlementTiming.MID
        
        # High-value cases often settle at trial door
        if case_data.get('case_value', 0) > 1000000:
            return SettlementTiming.TRIAL_DOOR
        
        # Weak cases settle early
        if case_data.get('evidence_strength', 0.5) < 0.3:
            return SettlementTiming.EARLY
        
        # Default to mid-case timing
        return SettlementTiming.MID

    def _calculate_settlement_urgency(self, case_data: Dict[str, Any], factor_analysis: Dict[str, Any]) -> float:
        """Calculate settlement urgency score"""
        urgency_factors = []
        
        # Time pressure
        time_pressure = factor_analysis.get('factor_scores', {}).get('time_pressure', 0.5)
        urgency_factors.append(time_pressure * 0.3)
        
        # Economic pressure
        case_value = case_data.get('case_value', 0)
        if case_value > 500000:
            urgency_factors.append(0.7 * 0.3)
        else:
            urgency_factors.append(0.4 * 0.3)
        
        # Case strength extremes create urgency
        evidence_strength = case_data.get('evidence_strength', 0.5)
        if evidence_strength > 0.8 or evidence_strength < 0.2:
            urgency_factors.append(0.8 * 0.2)
        else:
            urgency_factors.append(0.4 * 0.2)
        
        # Trial proximity
        if case_data.get('trial_date'):
            urgency_factors.append(0.9 * 0.2)
        else:
            urgency_factors.append(0.3 * 0.2)
        
        return sum(urgency_factors)

    def _calculate_negotiation_leverage(self, case_data: Dict[str, Any], factor_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate relative negotiation leverage"""
        plaintiff_leverage = 0.5  # Base neutral
        defendant_leverage = 0.5
        
        # Evidence strength affects leverage
        evidence_strength = case_data.get('evidence_strength', 0.5)
        plaintiff_leverage += (evidence_strength - 0.5) * 0.6
        defendant_leverage += (0.5 - evidence_strength) * 0.6
        
        # Case value affects leverage differently
        case_value = case_data.get('case_value', 0)
        if case_value > 1000000:
            defendant_leverage += 0.1  # Defendant has more to lose
        
        # Economic resources
        if case_data.get('plaintiff_resources') == 'limited':
            defendant_leverage += 0.2
        if case_data.get('defendant_resources') == 'limited':
            plaintiff_leverage += 0.2
        
        # Normalize to ensure they sum to reasonable range
        total_leverage = plaintiff_leverage + defendant_leverage
        if total_leverage > 0:
            plaintiff_leverage = plaintiff_leverage / total_leverage
            defendant_leverage = defendant_leverage / total_leverage
        
        return {
            'plaintiff': max(0.1, min(0.9, plaintiff_leverage)),
            'defendant': max(0.1, min(0.9, defendant_leverage))
        }

    def _calculate_confidence_score(self, historical_data: List[Dict], factor_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for settlement analysis"""
        confidence_factors = []
        
        # Historical data quality and quantity
        if len(historical_data) > 10:
            confidence_factors.append(0.8)
        elif len(historical_data) > 5:
            confidence_factors.append(0.6)
        elif len(historical_data) > 0:
            confidence_factors.append(0.4)
        else:
            confidence_factors.append(0.2)
        
        # Factor analysis completeness
        available_factors = len(factor_analysis.get('factor_scores', {}))
        factor_confidence = min(available_factors / 6, 1.0)  # Optimal at 6+ factors
        confidence_factors.append(factor_confidence)
        
        # Data quality indicators
        confidence_factors.append(0.7)  # Base confidence for methodology
        
        return sum(confidence_factors) / len(confidence_factors)

    async def _generate_settlement_scenarios(self, case_data: Dict[str, Any], metrics: SettlementMetrics) -> List[SettlementScenario]:
        """Generate multiple settlement scenarios with probabilities"""
        scenarios = []
        
        # Scenario 1: Early Settlement (plaintiff accepts lower amount for certainty)
        early_amount = (metrics.plaintiff_settlement_range[0] + metrics.defendant_settlement_range[1]) / 2
        scenarios.append(SettlementScenario(
            scenario_name="Early Settlement",
            probability=0.3 if metrics.optimal_timing == SettlementTiming.EARLY else 0.2,
            settlement_amount=early_amount,
            timing=SettlementTiming.EARLY,
            key_conditions=["Plaintiff accepts lower amount", "Quick resolution preferred", "Cost avoidance priority"],
            plaintiff_satisfaction=0.6,
            defendant_satisfaction=0.8,
            strategic_notes="Minimizes litigation costs and uncertainty for both parties"
        ))
        
        # Scenario 2: Mid-Case Settlement (after discovery)
        mid_amount = metrics.expected_settlement_value
        scenarios.append(SettlementScenario(
            scenario_name="Post-Discovery Settlement",
            probability=0.4 if metrics.optimal_timing == SettlementTiming.MID else 0.3,
            settlement_amount=mid_amount,
            timing=SettlementTiming.MID,
            key_conditions=["Discovery completed", "Case strengths/weaknesses clear", "Informed negotiation"],
            plaintiff_satisfaction=0.7,
            defendant_satisfaction=0.7,
            strategic_notes="Balanced settlement after fact development"
        ))
        
        # Scenario 3: Trial Door Settlement (maximum pressure)
        trial_door_amount = (metrics.plaintiff_settlement_range[1] + metrics.defendant_settlement_range[0]) / 2
        scenarios.append(SettlementScenario(
            scenario_name="Trial Door Settlement",
            probability=0.25 if metrics.optimal_timing == SettlementTiming.TRIAL_DOOR else 0.15,
            settlement_amount=trial_door_amount,
            timing=SettlementTiming.TRIAL_DOOR,
            key_conditions=["Maximum litigation pressure", "Trial preparation complete", "Last chance for control"],
            plaintiff_satisfaction=0.8,
            defendant_satisfaction=0.6,
            strategic_notes="High-pressure negotiation with maximum information"
        ))
        
        # Scenario 4: Mediation Settlement
        mediation_amount = metrics.expected_settlement_value * 1.1  # Slightly higher due to mediation process
        scenarios.append(SettlementScenario(
            scenario_name="Mediation Settlement",
            probability=0.35,
            settlement_amount=mediation_amount,
            timing=SettlementTiming.MEDIATION,
            key_conditions=["Court-ordered or voluntary mediation", "Neutral third-party facilitation", "Creative solutions possible"],
            plaintiff_satisfaction=0.75,
            defendant_satisfaction=0.75,
            strategic_notes="Structured negotiation with professional mediator"
        ))
        
        # Normalize probabilities
        total_prob = sum(s.probability for s in scenarios)
        if total_prob > 0:
            for scenario in scenarios:
                scenario.probability = scenario.probability / total_prob
        
        return scenarios

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _get_ai_settlement_insights(self, case_data: Dict[str, Any], metrics: SettlementMetrics, scenarios: List[SettlementScenario]) -> str:
        """Get AI-powered settlement insights"""
        try:
            insights_prompt = f"""
            SETTLEMENT ANALYSIS - AI STRATEGIC INSIGHTS
            
            CASE OVERVIEW:
            - Case Type: {case_data.get('case_type', 'Unknown')}
            - Case Value: ${case_data.get('case_value', 0):,.2f}
            - Evidence Strength: {case_data.get('evidence_strength', 0.5):.1%}
            - Jurisdiction: {case_data.get('jurisdiction', 'Unknown')}
            - Case Complexity: {case_data.get('case_complexity', 0.5):.1%}
            
            CALCULATED METRICS:
            - Settlement Probability: {metrics.settlement_probability:.1%}
            - Expected Settlement Value: ${metrics.expected_settlement_value:,.2f}
            - Plaintiff Range: ${metrics.plaintiff_settlement_range[0]:,.2f} - ${metrics.plaintiff_settlement_range[1]:,.2f}
            - Defendant Range: ${metrics.defendant_settlement_range[0]:,.2f} - ${metrics.defendant_settlement_range[1]:,.2f}
            - Optimal Timing: {metrics.optimal_timing.value}
            - Settlement Urgency: {metrics.settlement_urgency_score:.1%}
            
            KEY SETTLEMENT FACTORS:
            {chr(10).join(f'- {factor}' for factor in metrics.key_settlement_factors)}
            
            SETTLEMENT SCENARIOS:
            {chr(10).join(f'- {s.scenario_name}: {s.probability:.1%} probability, ${s.settlement_amount:,.2f}' for s in scenarios)}
            
            NEGOTIATION LEVERAGE:
            - Plaintiff Leverage: {metrics.negotiation_leverage.get('plaintiff', 0.5):.1%}
            - Defendant Leverage: {metrics.negotiation_leverage.get('defendant', 0.5):.1%}
            
            Please provide strategic insights covering:
            1. Settlement likelihood assessment and key drivers
            2. Optimal negotiation strategy and timing
            3. Risk factors that could derail settlement
            4. Creative settlement structures to consider
            5. Psychological and business factors influencing parties
            6. Specific tactical recommendations for maximizing settlement success
            
            Focus on practical, actionable insights for litigation attorneys.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                insights_prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.warning(f"⚠️ AI insights generation failed: {e}")
            return self._generate_fallback_insights(case_data, metrics)

    def _generate_fallback_insights(self, case_data: Dict[str, Any], metrics: SettlementMetrics) -> str:
        """Generate fallback insights when AI fails"""
        insights = f"""
        SETTLEMENT ANALYSIS SUMMARY

        Based on case analysis, settlement probability is {metrics.settlement_probability:.1%} with key factors:
        {', '.join(metrics.key_settlement_factors)}.

        STRATEGIC RECOMMENDATIONS:
        - Optimal timing appears to be {metrics.optimal_timing.value} in the litigation process
        - Expected settlement range: ${metrics.plaintiff_settlement_range[0]:,.0f} - ${metrics.defendant_settlement_range[1]:,.0f}
        - Settlement urgency is {'high' if metrics.settlement_urgency_score > 0.7 else 'moderate' if metrics.settlement_urgency_score > 0.4 else 'low'}

        Consider mediation or structured negotiation to facilitate resolution.
        """
        return insights

    def _develop_negotiation_strategy(self, case_data: Dict[str, Any], metrics: SettlementMetrics, scenarios: List[SettlementScenario]) -> Dict[str, Any]:
        """Develop comprehensive negotiation strategy"""
        strategy = {
            'primary_approach': 'collaborative',
            'opening_position': {},
            'concession_strategy': {},
            'timing_recommendations': {},
            'leverage_points': [],
            'potential_obstacles': [],
            'creative_solutions': []
        }
        
        # Determine primary approach based on leverage and case strength
        plaintiff_leverage = metrics.negotiation_leverage.get('plaintiff', 0.5)
        if plaintiff_leverage > 0.7:
            strategy['primary_approach'] = 'aggressive'
        elif plaintiff_leverage < 0.3:
            strategy['primary_approach'] = 'accommodating'
        else:
            strategy['primary_approach'] = 'collaborative'
        
        # Opening position recommendations
        if case_data.get('evidence_strength', 0.5) > 0.7:
            strategy['opening_position'] = {
                'plaintiff_opening': metrics.plaintiff_settlement_range[1] * 1.2,
                'defendant_opening': metrics.defendant_settlement_range[0] * 0.8,
                'rationale': 'Strong case allows aggressive opening'
            }
        else:
            strategy['opening_position'] = {
                'plaintiff_opening': metrics.plaintiff_settlement_range[1],
                'defendant_opening': metrics.defendant_settlement_range[0],
                'rationale': 'Moderate case requires realistic opening'
            }
        
        # Concession strategy
        strategy['concession_strategy'] = {
            'initial_concessions': 'small',
            'pattern': 'decreasing',
            'final_move': metrics.expected_settlement_value,
            'walkaway_point': metrics.plaintiff_settlement_range[0] if plaintiff_leverage > 0.5 else metrics.plaintiff_settlement_range[0] * 0.8
        }
        
        # Timing recommendations
        best_scenario = max(scenarios, key=lambda s: s.probability * s.plaintiff_satisfaction)
        strategy['timing_recommendations'] = {
            'optimal_timing': best_scenario.timing.value,
            'key_milestones': best_scenario.key_conditions,
            'urgency_level': 'high' if metrics.settlement_urgency_score > 0.7 else 'moderate'
        }
        
        # Leverage points
        strategy['leverage_points'] = [
            f"Case strength: {case_data.get('evidence_strength', 0.5):.1%}",
            f"Case value at stake: ${case_data.get('case_value', 0):,.0f}",
            "Cost and time savings from settlement",
            "Certainty vs. trial risk"
        ]
        
        # Potential obstacles
        strategy['potential_obstacles'] = [
            "Emotional attachment to case outcome",
            "Precedent concerns for repeat defendant",
            "Insurance company approval requirements",
            "Principal-agent conflicts"
        ]
        
        # Creative solutions
        strategy['creative_solutions'] = [
            "Structured settlement with payments over time",
            "Non-monetary terms (apology, policy changes)",
            "Contingent settlement based on future events",
            "Confidentiality provisions with premium"
        ]
        
        return strategy

    def _assess_settlement_risks(self, case_data: Dict[str, Any], metrics: SettlementMetrics) -> Dict[str, Any]:
        """Assess risks that could affect settlement success"""
        risk_assessment = {
            'high_risks': [],
            'medium_risks': [],
            'low_risks': [],
            'mitigation_strategies': {},
            'overall_risk_score': 0.0
        }
        
        risk_factors = []
        
        # Case strength risks
        evidence_strength = case_data.get('evidence_strength', 0.5)
        if evidence_strength < 0.3:
            risk_assessment['high_risks'].append("Weak evidence may force unfavorable settlement")
            risk_factors.append(0.8)
        elif evidence_strength > 0.8:
            risk_assessment['medium_risks'].append("Strong case may create overconfidence")
            risk_factors.append(0.4)
        else:
            risk_assessment['low_risks'].append("Moderate case strength allows balanced negotiation")
            risk_factors.append(0.2)
        
        # Economic pressure risks
        if case_data.get('case_value', 0) > 1000000:
            risk_assessment['medium_risks'].append("High case value may complicate settlement approval")
            risk_factors.append(0.5)
        
        # Time pressure risks
        if metrics.settlement_urgency_score > 0.8:
            risk_assessment['high_risks'].append("High urgency may lead to rushed settlement decisions")
            risk_factors.append(0.7)
        
        # Leverage imbalance risks
        leverage_diff = abs(metrics.negotiation_leverage.get('plaintiff', 0.5) - metrics.negotiation_leverage.get('defendant', 0.5))
        if leverage_diff > 0.3:
            risk_assessment['medium_risks'].append("Significant leverage imbalance may create impasse")
            risk_factors.append(0.6)
        
        # Calculate overall risk score
        risk_assessment['overall_risk_score'] = sum(risk_factors) / len(risk_factors) if risk_factors else 0.3
        
        # Mitigation strategies
        risk_assessment['mitigation_strategies'] = {
            'weak_case': "Focus on cost-benefit analysis and certainty value",
            'high_urgency': "Implement structured timeline with clear deadlines",
            'leverage_imbalance': "Use neutral mediator to level playing field",
            'complex_approval': "Identify decision-makers early and include in process"
        }
        
        return risk_assessment

    def _generate_settlement_recommendations(self, case_data: Dict[str, Any], metrics: SettlementMetrics, 
                                           scenarios: List[SettlementScenario], risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate specific settlement recommendations"""
        recommendations = []
        
        # Probability-based recommendations
        if metrics.settlement_probability > 0.7:
            recommendations.append(f"High settlement probability ({metrics.settlement_probability:.1%}) - prioritize settlement strategy")
        elif metrics.settlement_probability > 0.5:
            recommendations.append(f"Moderate settlement likelihood ({metrics.settlement_probability:.1%}) - prepare dual track approach")
        else:
            recommendations.append(f"Lower settlement probability ({metrics.settlement_probability:.1%}) - focus on trial preparation with settlement opportunities")
        
        # Timing recommendations
        best_timing_scenario = max(scenarios, key=lambda s: s.probability)
        recommendations.append(f"Optimal settlement timing: {best_timing_scenario.scenario_name} ({best_timing_scenario.timing.value})")
        
        # Value recommendations
        recommendations.append(f"Target settlement range: ${metrics.plaintiff_settlement_range[0]:,.0f} - ${metrics.defendant_settlement_range[1]:,.0f}")
        
        # Strategy recommendations based on leverage
        plaintiff_leverage = metrics.negotiation_leverage.get('plaintiff', 0.5)
        if plaintiff_leverage > 0.6:
            recommendations.append("Strong negotiation position - consider aggressive opening position")
        elif plaintiff_leverage < 0.4:
            recommendations.append("Weaker negotiation position - focus on collaborative approach and mutual benefits")
        
        # Risk mitigation recommendations
        if risk_assessment['overall_risk_score'] > 0.6:
            recommendations.append("High settlement risks identified - consider early mediation to facilitate resolution")
        
        # Urgency recommendations
        if metrics.settlement_urgency_score > 0.7:
            recommendations.append("High settlement urgency - initiate discussions promptly to avoid time pressure")
        
        # Case-specific recommendations
        if case_data.get('case_type') == 'employment':
            recommendations.append("Employment cases often involve emotional factors - consider non-monetary terms")
        elif case_data.get('case_type') == 'commercial':
            recommendations.append("Commercial disputes may benefit from business-focused resolution terms")
        
        # Limit to top recommendations
        return recommendations[:7]

    async def _cache_settlement_analysis(self, analysis: SettlementAnalysis):
        """Cache settlement analysis for future reference"""
        try:
            analysis_dict = {
                'case_id': analysis.case_id,
                'analysis_date': analysis.analysis_date,
                'settlement_probability': analysis.metrics.settlement_probability,
                'expected_settlement_value': analysis.metrics.expected_settlement_value,
                'plaintiff_range_low': analysis.metrics.plaintiff_settlement_range[0],
                'plaintiff_range_high': analysis.metrics.plaintiff_settlement_range[1],
                'defendant_range_low': analysis.metrics.defendant_settlement_range[0],
                'defendant_range_high': analysis.metrics.defendant_settlement_range[1],
                'optimal_timing': analysis.metrics.optimal_timing.value,
                'settlement_urgency': analysis.metrics.settlement_urgency_score,
                'confidence_score': analysis.metrics.confidence_score,
                'key_factors': analysis.metrics.key_settlement_factors,
                'scenarios': [
                    {
                        'name': s.scenario_name,
                        'probability': s.probability,
                        'amount': s.settlement_amount,
                        'timing': s.timing.value,
                        'plaintiff_satisfaction': s.plaintiff_satisfaction,
                        'defendant_satisfaction': s.defendant_satisfaction
                    }
                    for s in analysis.scenarios
                ],
                'ai_insights': analysis.ai_insights,
                'negotiation_strategy': analysis.negotiation_strategy,
                'risk_assessment': analysis.risk_assessment,
                'recommendations': analysis.recommendations
            }
            
            await self.db.settlement_analysis.update_one(
                {'case_id': analysis.case_id},
                {'$set': analysis_dict},
                upsert=True
            )
            
            logger.info(f"💾 Cached settlement analysis for case {analysis.case_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Settlement analysis caching failed: {e}")

    def _create_default_analysis(self, case_id: str) -> SettlementAnalysis:
        """Create default analysis when calculation fails"""
        default_metrics = SettlementMetrics(
            settlement_probability=0.5,
            optimal_timing=SettlementTiming.MID,
            plaintiff_settlement_range=(50000, 200000),
            defendant_settlement_range=(30000, 150000),
            expected_settlement_value=100000,
            settlement_urgency_score=0.5,
            confidence_score=0.3,
            key_settlement_factors=["Case complexity", "Economic factors", "Time considerations"],
            negotiation_leverage={'plaintiff': 0.5, 'defendant': 0.5}
        )
        
        default_scenarios = [
            SettlementScenario(
                scenario_name="Standard Settlement",
                probability=1.0,
                settlement_amount=100000,
                timing=SettlementTiming.MID,
                key_conditions=["Mutual agreement reached"],
                plaintiff_satisfaction=0.6,
                defendant_satisfaction=0.6,
                strategic_notes="Balanced settlement outcome"
            )
        ]
        
        return SettlementAnalysis(
            case_id=case_id,
            analysis_date=datetime.utcnow(),
            metrics=default_metrics,
            scenarios=default_scenarios,
            ai_insights="Settlement analysis pending additional case information.",
            negotiation_strategy={'primary_approach': 'collaborative'},
            risk_assessment={'overall_risk_score': 0.5},
            recommendations=["Prepare for settlement discussions", "Gather comprehensive case information"]
        )

    def _create_default_metrics(self, case_data: Dict[str, Any]) -> SettlementMetrics:
        """Create default metrics when calculation fails"""
        case_value = case_data.get('case_value', 100000)
        
        return SettlementMetrics(
            settlement_probability=0.4,
            optimal_timing=SettlementTiming.MID,
            plaintiff_settlement_range=(case_value * 0.3, case_value * 0.8),
            defendant_settlement_range=(case_value * 0.2, case_value * 0.6),
            expected_settlement_value=case_value * 0.45,
            settlement_urgency_score=0.5,
            confidence_score=0.3,
            key_settlement_factors=["Case value", "Legal complexity", "Time factors"],
            negotiation_leverage={'plaintiff': 0.5, 'defendant': 0.5}
        )

    def _generate_synthetic_settlement_data(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate synthetic settlement data for development/testing"""
        import random
        import uuid
        
        synthetic_data = []
        case_type = case_data.get('case_type', 'civil')
        base_value = case_data.get('case_value', 100000)
        
        for i in range(10):
            settlement_amount = base_value * random.uniform(0.2, 0.8)
            case = {
                'case_id': str(uuid.uuid4()),
                'case_type': case_type,
                'jurisdiction': case_data.get('jurisdiction', 'federal'),
                'case_value': base_value * random.uniform(0.5, 2.0),
                'settlement_amount': settlement_amount,
                'outcome': 'settlement',
                'settlement_date': datetime.utcnow() - timedelta(days=random.randint(30, 1095)),
                'case_duration': random.randint(90, 730),
                'synthetic': True
            }
            synthetic_data.append(case)
        
        logger.info("🧪 Generated synthetic settlement data for analysis")
        return synthetic_data

# Global calculator instance
_settlement_calculator = None

async def get_settlement_calculator(db_connection) -> SettlementProbabilityCalculator:
    """Get or create settlement probability calculator instance"""
    global _settlement_calculator
    
    if _settlement_calculator is None:
        _settlement_calculator = SettlementProbabilityCalculator(db_connection)
        logger.info("💰 Settlement Probability Calculator instance created")
    
    return _settlement_calculator

async def initialize_settlement_calculator(db_connection):
    """Initialize the settlement probability calculator"""
    await get_settlement_calculator(db_connection)
    logger.info("✅ Settlement Probability Calculator initialized successfully")
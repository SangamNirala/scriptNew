"""
Advanced Settlement Probability Calculator - Next Generation
Enhanced with Multiple AI Models, Monte Carlo Simulation, and Real-time Analysis
"""

import os
import logging
import asyncio
import uuid
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, Counter
import scipy.stats as stats
from concurrent.futures import ThreadPoolExecutor
import time

# Import the new emergentintegrations library
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import existing components
from settlement_probability_calculator import (
    SettlementTiming, SettlementFactors, SettlementMetrics, 
    SettlementScenario, SettlementAnalysis, SettlementProbabilityCalculator
)

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    OPENROUTER = "openrouter"
    GEMINI = "gemini"
    GROK = "grok"
    HUGGINGFACE = "huggingface"

class AnalysisMode(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    MONTE_CARLO = "monte_carlo"
    COMPARATIVE = "comparative"
    REAL_TIME = "real_time"

@dataclass
class MonteCarloResults:
    """Results from Monte Carlo simulation"""
    mean_settlement_probability: float
    std_settlement_probability: float
    percentiles: Dict[str, float]  # 10th, 25th, 50th, 75th, 90th
    confidence_intervals: Dict[str, Tuple[float, float]]  # 90%, 95%, 99%
    scenario_probabilities: Dict[str, float]
    risk_metrics: Dict[str, float]
    simulation_count: int
    convergence_analysis: Dict[str, Any]

@dataclass
class ComparativeCaseData:
    """Similar case data for comparative analysis"""
    case_id: str
    case_type: str
    settlement_amount: float
    settlement_probability: float
    similarity_score: float
    key_factors: List[str]
    jurisdiction: str
    case_date: datetime
    outcome_details: Dict[str, Any]

@dataclass
class AdvancedSettlementMetrics(SettlementMetrics):
    """Enhanced metrics with advanced analytics"""
    monte_carlo_results: Optional[MonteCarloResults] = None
    comparative_cases: List[ComparativeCaseData] = field(default_factory=list)
    ai_consensus_score: float = 0.0
    market_trend_adjustment: float = 0.0
    volatility_index: float = 0.0
    strategic_advantage_score: float = 0.0
    negotiation_timeline: Dict[str, Any] = field(default_factory=dict)
    dynamic_factors: Dict[str, float] = field(default_factory=dict)

class AdvancedSettlementCalculator(SettlementProbabilityCalculator):
    """Advanced settlement calculator with next-generation features"""
    
    def __init__(self, db_connection):
        super().__init__(db_connection)
        
        # Initialize AI providers
        self.ai_providers = {}
        self._initialize_ai_providers()
        
        # Advanced analytics configuration
        self.monte_carlo_iterations = 10000
        self.confidence_levels = [0.90, 0.95, 0.99]
        self.max_parallel_analyses = 4
        
        # Market data cache
        self.market_data_cache = {}
        self.cache_expiry = 3600  # 1 hour
        
        logger.info("🚀 Advanced Settlement Probability Calculator initialized with multi-AI analysis")

    def _initialize_ai_providers(self):
        """Initialize multiple AI providers for enhanced analysis with latest models"""
        try:
            # OpenRouter (Latest GPT-4 and Claude models)
            openrouter_key = os.environ.get('OPENROUTER_API_KEY')
            if openrouter_key:
                self.ai_providers[AIProvider.OPENROUTER] = {
                    'api_key': openrouter_key,
                    'models': [
                        'openai/gpt-4o-2024-08-06',  # Latest GPT-4o
                        'anthropic/claude-3.5-sonnet',  # Latest Claude
                        'meta-llama/llama-3.3-70b-instruct',  # Latest Llama
                        'qwen/qwen-2.5-72b-instruct'  # Powerful reasoning model
                    ],
                    'weight': 0.35,
                    'capabilities': ['advanced_reasoning', 'legal_analysis', 'quantitative_modeling']
                }
            
            # Gemini (Latest model with enhanced capabilities)
            gemini_key = os.environ.get('GEMINI_API_KEY')
            if gemini_key:
                self.ai_providers[AIProvider.GEMINI] = {
                    'api_key': gemini_key,
                    'models': ['gemini-2.0-flash-exp'],  # Latest experimental model
                    'weight': 0.30,
                    'capabilities': ['multimodal_analysis', 'deep_reasoning', 'probabilistic_modeling']
                }
            
            # Groq (High-speed inference models)
            grok_key = os.environ.get('GROQ_API_KEY')
            if grok_key:
                self.ai_providers[AIProvider.GROK] = {
                    'api_key': grok_key,
                    'models': [
                        'llama-3.3-70b-versatile',  # Latest Llama on Groq
                        'mixtral-8x7b-32768',  # High-context model
                        'gemma2-9b-it'  # Efficient reasoning model
                    ],
                    'weight': 0.25,
                    'capabilities': ['fast_inference', 'batch_processing', 'real_time_analysis']
                }
            
            # HuggingFace (Open-source models)
            hf_key = os.environ.get('HUGGINGFACE_API_KEY')
            if hf_key:
                self.ai_providers[AIProvider.HUGGINGFACE] = {
                    'api_key': hf_key,
                    'models': [
                        'microsoft/DialoGPT-large',
                        'microsoft/DialoGPT-medium',
                        'meta-llama/Llama-2-13b-chat-hf'
                    ],
                    'weight': 0.10,
                    'capabilities': ['specialized_models', 'custom_fine_tuning', 'domain_adaptation']
                }
            
            logger.info(f"✅ Enhanced AI providers initialized: {len(self.ai_providers)} providers with latest models (GPT-4o, Claude-3.5, Llama-3.3, Gemini-2.0)")
            
        except Exception as e:
            logger.error(f"❌ AI provider initialization failed: {e}")
            # Fallback to existing providers
            self.ai_providers = {}

    async def calculate_advanced_settlement_analysis(
        self, 
        case_data: Dict[str, Any], 
        analysis_mode: AnalysisMode = AnalysisMode.ADVANCED
    ) -> SettlementAnalysis:
        """
        Calculate comprehensive settlement analysis with advanced features
        """
        try:
            case_id = case_data.get('case_id', str(uuid.uuid4()))
            logger.info(f"🚀 Starting advanced settlement analysis for case {case_id} (mode: {analysis_mode.value})")
            
            start_time = time.time()
            
            # Run multiple analysis tracks in parallel
            analysis_tasks = []
            
            # 1. Enhanced base analysis
            analysis_tasks.append(self._enhanced_base_analysis(case_data))
            
            # 2. Multi-AI consensus analysis
            if len(self.ai_providers) > 0:
                analysis_tasks.append(self._multi_ai_consensus_analysis(case_data))
            
            # 3. Monte Carlo simulation (if requested)
            if analysis_mode in [AnalysisMode.MONTE_CARLO, AnalysisMode.ADVANCED]:
                analysis_tasks.append(self._monte_carlo_simulation(case_data))
            
            # 4. Comparative case analysis
            if analysis_mode in [AnalysisMode.COMPARATIVE, AnalysisMode.ADVANCED]:
                analysis_tasks.append(self._comparative_case_analysis(case_data))
            
            # 5. Market trend analysis
            analysis_tasks.append(self._market_trend_analysis(case_data))
            
            # Execute all analyses in parallel
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process results
            base_metrics = analysis_results[0] if not isinstance(analysis_results[0], Exception) else None
            ai_consensus = analysis_results[1] if len(analysis_results) > 1 and not isinstance(analysis_results[1], Exception) else None
            monte_carlo = analysis_results[2] if len(analysis_results) > 2 and not isinstance(analysis_results[2], Exception) else None
            comparative = analysis_results[3] if len(analysis_results) > 3 and not isinstance(analysis_results[3], Exception) else None
            market_trends = analysis_results[4] if len(analysis_results) > 4 and not isinstance(analysis_results[4], Exception) else None
            
            # Combine and enhance metrics
            enhanced_metrics = self._combine_advanced_metrics(
                base_metrics, ai_consensus, monte_carlo, comparative, market_trends
            )
            
            # Generate advanced scenarios
            advanced_scenarios = await self._generate_advanced_scenarios(case_data, enhanced_metrics)
            
            # Get multi-AI insights
            multi_ai_insights = await self._get_multi_ai_insights(case_data, enhanced_metrics, advanced_scenarios)
            
            # Advanced strategy development
            advanced_strategy = self._develop_advanced_strategy(case_data, enhanced_metrics, advanced_scenarios)
            
            # Enhanced risk assessment
            advanced_risks = self._assess_advanced_risks(case_data, enhanced_metrics, monte_carlo)
            
            # Generate intelligent recommendations
            intelligent_recommendations = self._generate_intelligent_recommendations(
                case_data, enhanced_metrics, advanced_scenarios, advanced_risks
            )
            
            # Create comprehensive analysis
            analysis = SettlementAnalysis(
                case_id=case_id,
                analysis_date=datetime.utcnow(),
                metrics=enhanced_metrics,
                scenarios=advanced_scenarios,
                comparative_settlements=comparative.get('cases', [])[:5] if comparative else [],
                negotiation_strategy=advanced_strategy,
                ai_insights=multi_ai_insights,
                risk_assessment=advanced_risks,
                recommendations=intelligent_recommendations
            )
            
            # Add advanced metadata
            analysis.metadata = {
                'analysis_mode': analysis_mode.value,
                'processing_time': time.time() - start_time,
                'ai_providers_used': len(self.ai_providers),
                'monte_carlo_enabled': monte_carlo is not None,
                'comparative_cases_found': len(comparative.get('cases', [])) if comparative else 0,
                'confidence_level': enhanced_metrics.confidence_score,
                'version': '2.0-advanced'
            }
            
            # Cache the analysis
            await self._cache_advanced_analysis(analysis)
            
            logger.info(f"✅ Advanced settlement analysis completed in {time.time() - start_time:.2f}s with {enhanced_metrics.settlement_probability:.1%} probability")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Advanced settlement calculation failed: {e}")
            # Fallback to standard analysis
            return await super().calculate_settlement_probability(case_data)

    async def _enhanced_base_analysis(self, case_data: Dict[str, Any]) -> AdvancedSettlementMetrics:
        """Enhanced base analysis with improved algorithms"""
        try:
            # Get historical data with enhanced matching
            historical_data = await self._get_enhanced_historical_data(case_data)
            
            # Calculate base metrics using improved algorithms
            base_metrics = await self._calculate_enhanced_base_metrics(case_data, historical_data)
            
            # Convert to advanced metrics
            advanced_metrics = AdvancedSettlementMetrics(
                settlement_probability=base_metrics.settlement_probability,
                optimal_timing=base_metrics.optimal_timing,
                plaintiff_settlement_range=base_metrics.plaintiff_settlement_range,
                defendant_settlement_range=base_metrics.defendant_settlement_range,
                expected_settlement_value=base_metrics.expected_settlement_value,
                settlement_urgency_score=base_metrics.settlement_urgency_score,
                confidence_score=base_metrics.confidence_score,
                key_settlement_factors=base_metrics.key_settlement_factors,
                negotiation_leverage=base_metrics.negotiation_leverage
            )
            
            # Add volatility analysis
            advanced_metrics.volatility_index = self._calculate_volatility_index(case_data, historical_data)
            
            # Add dynamic factors
            advanced_metrics.dynamic_factors = self._analyze_dynamic_factors(case_data)
            
            return advanced_metrics
            
        except Exception as e:
            logger.error(f"Enhanced base analysis failed: {e}")
            # Fallback to standard base analysis
            standard_metrics = await super()._calculate_base_settlement_metrics(case_data, [])
            return AdvancedSettlementMetrics(
                settlement_probability=standard_metrics.settlement_probability,
                optimal_timing=standard_metrics.optimal_timing,
                plaintiff_settlement_range=standard_metrics.plaintiff_settlement_range,
                defendant_settlement_range=standard_metrics.defendant_settlement_range,
                expected_settlement_value=standard_metrics.expected_settlement_value,
                settlement_urgency_score=standard_metrics.settlement_urgency_score,
                confidence_score=standard_metrics.confidence_score,
                key_settlement_factors=standard_metrics.key_settlement_factors,
                negotiation_leverage=standard_metrics.negotiation_leverage
            )

    async def _multi_ai_consensus_analysis(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get consensus analysis from multiple AI providers"""
        try:
            if not self.ai_providers:
                return {'consensus_score': 0.5, 'ai_insights': {}}
            
            ai_analyses = []
            tasks = []
            
            for provider, config in self.ai_providers.items():
                task = self._get_single_ai_analysis(provider, config, case_data)
                tasks.append(task)
            
            # Execute AI analyses in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process valid results
            valid_results = [r for r in results if not isinstance(r, Exception)]
            
            if not valid_results:
                return {'consensus_score': 0.5, 'ai_insights': {}}
            
            # Calculate consensus
            probabilities = [r.get('settlement_probability', 0.5) for r in valid_results]
            consensus_probability = np.mean(probabilities)
            consensus_std = np.std(probabilities)
            
            # Weight by provider reliability
            weighted_consensus = 0.0
            total_weight = 0.0
            
            for i, result in enumerate(valid_results):
                provider_weight = list(self.ai_providers.values())[i].get('weight', 0.25)
                weighted_consensus += result.get('settlement_probability', 0.5) * provider_weight
                total_weight += provider_weight
            
            if total_weight > 0:
                weighted_consensus /= total_weight
            else:
                weighted_consensus = consensus_probability
            
            # Calculate consensus score (agreement measure)
            consensus_score = max(0.0, 1.0 - (consensus_std / 0.5))  # Normalize standard deviation
            
            return {
                'consensus_probability': weighted_consensus,
                'consensus_score': consensus_score,
                'ai_analyses': valid_results,
                'provider_count': len(valid_results),
                'probability_range': (min(probabilities), max(probabilities)),
                'agreement_level': 'high' if consensus_score > 0.8 else 'medium' if consensus_score > 0.6 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Multi-AI consensus analysis failed: {e}")
            return {'consensus_score': 0.5, 'ai_insights': {}}

    async def _get_single_ai_analysis(self, provider: AIProvider, config: Dict, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get analysis from a single AI provider using latest models"""
        try:
            # Create enhanced analysis prompt
            prompt = self._create_enhanced_ai_analysis_prompt(case_data)
            
            # Initialize chat based on provider
            session_id = f"settlement-analysis-{uuid.uuid4()}"
            system_message = """You are an expert legal settlement analyst with advanced quantitative modeling capabilities. 
            Provide detailed probabilistic analysis with numerical precision, risk assessments, and strategic insights.
            Return structured JSON with settlement_probability (0.0-1.0), confidence_score, risk_factors, and strategic_recommendations."""
            
            if provider == AIProvider.GEMINI:
                chat = LlmChat(
                    api_key=config['api_key'],
                    session_id=session_id,
                    system_message=system_message
                ).with_model("gemini", "gemini-2.0-flash-exp").with_max_tokens(4000)
                
            elif provider == AIProvider.OPENROUTER:
                # Use latest GPT-4o model
                model = config['models'][0] if config['models'] else 'openai/gpt-4o-2024-08-06'
                chat = LlmChat(
                    api_key=config['api_key'],
                    session_id=session_id,
                    system_message=system_message
                ).with_model("openrouter", model).with_max_tokens(4000)
                
            elif provider == AIProvider.GROK:
                # Use latest Llama model on Groq
                model = config['models'][0] if config['models'] else 'llama-3.3-70b-versatile'
                chat = LlmChat(
                    api_key=config['api_key'],
                    session_id=session_id,
                    system_message=system_message
                ).with_model("groq", model).with_max_tokens(4000)
                
            else:
                # Fallback
                return {
                    'settlement_probability': 0.5, 
                    'provider': provider.value, 
                    'error': 'unsupported provider',
                    'confidence_score': 0.3
                }
            
            # Send message
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse enhanced response
            analysis = self._parse_enhanced_ai_response(response, provider)
            analysis['provider'] = provider.value
            analysis['model_capabilities'] = config.get('capabilities', [])
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Single AI analysis failed for {provider.value}: {e}")
            return {
                'settlement_probability': 0.5, 
                'provider': provider.value, 
                'error': str(e),
                'confidence_score': 0.2
            }

    async def _get_enhanced_historical_data(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get enhanced historical settlement data with better matching"""
        try:
            # Use parent method as base
            base_data = await super()._get_historical_settlement_data(case_data)
            
            # Add enhanced filtering and weighting
            enhanced_data = []
            for settlement in base_data:
                # Calculate enhanced similarity score
                similarity = self._calculate_enhanced_similarity(settlement, case_data)
                settlement['enhanced_similarity'] = similarity
                if similarity > 0.3:  # Threshold for relevance
                    enhanced_data.append(settlement)
            
            # Sort by enhanced similarity
            enhanced_data.sort(key=lambda x: x['enhanced_similarity'], reverse=True)
            
            return enhanced_data[:15]  # Top 15 most similar cases
            
        except Exception as e:
            logger.warning(f"Enhanced historical data retrieval failed: {e}")
            return await super()._get_historical_settlement_data(case_data)

    def _calculate_enhanced_similarity(self, settlement: Dict[str, Any], case_data: Dict[str, Any]) -> float:
        """Calculate enhanced similarity score between cases"""
        score = 0.0
        max_score = 0.0
        
        # Case type similarity (weight: 0.3)
        if settlement.get('case_type') == case_data.get('case_type'):
            score += 0.3
        max_score += 0.3
        
        # Jurisdiction similarity (weight: 0.2)
        if settlement.get('jurisdiction') == case_data.get('jurisdiction'):
            score += 0.2
        max_score += 0.2
        
        # Case value similarity (weight: 0.25)
        if case_data.get('case_value') and settlement.get('case_value'):
            case_value = case_data['case_value']
            settlement_value = settlement['case_value']
            
            if case_value > 0 and settlement_value > 0:
                ratio = min(case_value, settlement_value) / max(case_value, settlement_value)
                score += ratio * 0.25
            
        max_score += 0.25
        
        # Complexity similarity (weight: 0.15)
        if case_data.get('case_complexity') is not None and settlement.get('case_complexity') is not None:
            complexity_diff = abs(case_data['case_complexity'] - settlement['case_complexity'])
            complexity_similarity = 1 - complexity_diff
            score += complexity_similarity * 0.15
        max_score += 0.15
        
        # Evidence strength similarity (weight: 0.1)
        if case_data.get('evidence_strength') is not None and settlement.get('evidence_strength') is not None:
            evidence_diff = abs(case_data['evidence_strength'] - settlement['evidence_strength'])
            evidence_similarity = 1 - (evidence_diff / 10)  # Normalize to 0-1
            score += max(0, evidence_similarity) * 0.1
        max_score += 0.1
        
        return score / max_score if max_score > 0 else 0.0

    async def _calculate_enhanced_base_metrics(self, case_data: Dict[str, Any], historical_data: List[Dict]) -> AdvancedSettlementMetrics:
        """Calculate enhanced base metrics with improved algorithms"""
        try:
            # Use parent method as starting point
            standard_metrics = await super()._calculate_base_settlement_metrics(case_data, historical_data)
            
            # Convert to advanced metrics
            enhanced_metrics = AdvancedSettlementMetrics(
                settlement_probability=standard_metrics.settlement_probability,
                optimal_timing=standard_metrics.optimal_timing,
                plaintiff_settlement_range=standard_metrics.plaintiff_settlement_range,
                defendant_settlement_range=standard_metrics.defendant_settlement_range,
                expected_settlement_value=standard_metrics.expected_settlement_value,
                settlement_urgency_score=standard_metrics.settlement_urgency_score,
                confidence_score=standard_metrics.confidence_score,
                key_settlement_factors=standard_metrics.key_settlement_factors,
                negotiation_leverage=standard_metrics.negotiation_leverage
            )
            
            # Add enhanced calculations
            enhanced_metrics.volatility_index = self._calculate_volatility_index(case_data, historical_data)
            enhanced_metrics.dynamic_factors = self._analyze_dynamic_factors(case_data)
            enhanced_metrics.strategic_advantage_score = self._calculate_strategic_advantage(enhanced_metrics)
            
            return enhanced_metrics
            
        except Exception as e:
            logger.error(f"Enhanced base metrics calculation failed: {e}")
            # Fallback to creating default advanced metrics
            return self._create_default_advanced_metrics(case_data)

    def _calculate_volatility_index(self, case_data: Dict[str, Any], historical_data: List[Dict]) -> float:
        """Calculate settlement outcome volatility"""
        try:
            if not historical_data:
                return 0.5  # Default moderate volatility
            
            # Calculate standard deviation of historical settlement probabilities
            probabilities = []
            for case in historical_data:
                if case.get('settlement_probability'):
                    probabilities.append(case['settlement_probability'])
                elif case.get('outcome') == 'settlement':
                    probabilities.append(0.8)  # Assume 80% for settled cases
                else:
                    probabilities.append(0.2)  # 20% for non-settled
            
            if len(probabilities) < 2:
                return 0.3  # Low volatility for insufficient data
            
            volatility = np.std(probabilities)
            
            # Adjust for case complexity and other factors
            complexity = case_data.get('case_complexity', 0.5)
            evidence_strength = case_data.get('evidence_strength', 5) / 10
            
            # Higher complexity increases volatility
            volatility += complexity * 0.1
            
            # Weaker evidence increases volatility
            if evidence_strength < 0.5:
                volatility += (0.5 - evidence_strength) * 0.2
            
            return min(1.0, max(0.0, volatility))
            
        except Exception as e:
            logger.warning(f"Volatility calculation failed: {e}")
            return 0.4

    def _analyze_dynamic_factors(self, case_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze dynamic factors affecting settlement"""
        factors = {}
        
        # Time pressure factor
        if case_data.get('filing_date'):
            try:
                if isinstance(case_data['filing_date'], str):
                    filing_date = datetime.fromisoformat(case_data['filing_date'])
                else:
                    filing_date = case_data['filing_date']
                
                days_since_filing = (datetime.utcnow() - filing_date).days
                
                if days_since_filing > 730:  # 2+ years
                    factors['time_pressure'] = 0.8
                elif days_since_filing > 365:  # 1+ year
                    factors['time_pressure'] = 0.6
                else:
                    factors['time_pressure'] = 0.3
            except:
                factors['time_pressure'] = 0.5
        else:
            factors['time_pressure'] = 0.5
        
        # Economic pressure
        case_value = case_data.get('case_value', 0)
        if case_value > 1000000:
            factors['economic_pressure'] = 0.7
        elif case_value > 100000:
            factors['economic_pressure'] = 0.5
        else:
            factors['economic_pressure'] = 0.3
        
        # Evidence dynamics
        evidence_strength = case_data.get('evidence_strength', 5) / 10
        if evidence_strength > 0.8:
            factors['evidence_confidence'] = 0.9
        elif evidence_strength < 0.3:
            factors['evidence_risk'] = 0.8
        else:
            factors['evidence_balance'] = 0.6
        
        # Complexity factor
        complexity = case_data.get('case_complexity', 0.5)
        factors['complexity_risk'] = complexity
        
        # Resource disparity
        opposing_resources = case_data.get('opposing_party_resources', 'medium')
        resource_map = {
            'very_high': 0.8,
            'high': 0.6,
            'medium': 0.5,
            'low': 0.3
        }
        factors['resource_pressure'] = resource_map.get(opposing_resources, 0.5)
        
        return factors

    async def _find_similar_cases_enhanced(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar cases with enhanced matching"""
        try:
            # Build enhanced query with multiple criteria
            base_query = {
                'outcome': 'settlement',
                'settlement_amount': {'$exists': True, '$gt': 0}
            }
            
            # Case type filter
            if case_data.get('case_type'):
                base_query['case_type'] = case_data['case_type']
            
            # Jurisdiction filter
            if case_data.get('jurisdiction'):
                base_query['jurisdiction'] = case_data['jurisdiction']
            
            # Execute query
            similar_cases = await self.db.settlement_data.find(base_query).limit(50).to_list(50)
            
            # Calculate similarity scores and sort
            scored_cases = []
            for case in similar_cases:
                similarity = self._calculate_enhanced_similarity(case, case_data)
                if similarity > 0.2:  # Minimum similarity threshold
                    case['similarity_score'] = similarity
                    scored_cases.append(case)
            
            # Sort by similarity and return top matches
            scored_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return scored_cases[:10]  # Top 10 similar cases
            
        except Exception as e:
            logger.error(f"Enhanced similar cases search failed: {e}")
            return []

    def _analyze_case_patterns(self, similar_cases: List[Dict[str, Any]], case_data: Dict[str, Any]) -> str:
        """Analyze patterns in similar cases"""
        if not similar_cases:
            return "No comparable cases available for pattern analysis"
        
        # Calculate averages
        avg_settlement_amount = np.mean([c.get('settlement_amount', 0) for c in similar_cases if c.get('settlement_amount')])
        avg_case_value = np.mean([c.get('case_value', 0) for c in similar_cases if c.get('case_value')])
        
        settlement_ratio = avg_settlement_amount / avg_case_value if avg_case_value > 0 else 0.5
        
        # Analyze timing patterns
        timing_counts = Counter([c.get('settlement_timing', 'mid') for c in similar_cases])
        most_common_timing = timing_counts.most_common(1)[0][0] if timing_counts else 'mid'
        
        analysis = f"""
Based on analysis of {len(similar_cases)} similar {case_data.get('case_type', 'civil')} cases:

• Average settlement rate: {settlement_ratio:.1%} of claim value
• Most common settlement timing: {most_common_timing.replace('_', ' ')}
• Pattern confidence: {'High' if len(similar_cases) > 5 else 'Medium' if len(similar_cases) > 2 else 'Low'}

This suggests {case_data.get('case_type', 'civil')} cases in {case_data.get('jurisdiction', 'this jurisdiction')} typically settle for {settlement_ratio:.1%} of the claimed amount.
"""
        
        return analysis

    def _extract_pattern_insights(self, similar_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from case patterns"""
        if not similar_cases:
            return {}
        
        insights = {
            'total_cases': len(similar_cases),
            'avg_similarity': np.mean([c.get('similarity_score', 0) for c in similar_cases]),
            'settlement_range': {
                'min': min([c.get('settlement_amount', 0) for c in similar_cases if c.get('settlement_amount', 0) > 0], default=0),
                'max': max([c.get('settlement_amount', 0) for c in similar_cases], default=0),
                'median': np.median([c.get('settlement_amount', 0) for c in similar_cases if c.get('settlement_amount', 0) > 0])
            },
            'common_factors': self._identify_common_factors(similar_cases),
            'success_indicators': self._identify_success_indicators(similar_cases)
        }
        
        return insights

    def _identify_common_factors(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Identify common factors across similar cases"""
        factors = []
        
        # Case type consistency
        case_types = [c.get('case_type') for c in cases]
        if len(set(case_types)) == 1:
            factors.append(f"Consistent case type: {case_types[0]}")
        
        # Jurisdiction patterns
        jurisdictions = [c.get('jurisdiction') for c in cases]
        jurisdiction_counts = Counter(jurisdictions)
        if jurisdiction_counts:
            top_jurisdiction = jurisdiction_counts.most_common(1)[0]
            if top_jurisdiction[1] > len(cases) * 0.5:
                factors.append(f"Common jurisdiction: {top_jurisdiction[0]}")
        
        # Settlement timing patterns
        timings = [c.get('settlement_timing') for c in cases if c.get('settlement_timing')]
        if timings:
            timing_counts = Counter(timings)
            top_timing = timing_counts.most_common(1)[0]
            if top_timing[1] > len(timings) * 0.4:
                factors.append(f"Typical timing: {top_timing[0].replace('_', ' ')}")
        
        return factors

    def _identify_success_indicators(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Identify factors that indicate successful settlements"""
        indicators = []
        
        # High settlement ratios
        high_settlements = [c for c in cases if c.get('settlement_amount', 0) > c.get('case_value', 1) * 0.7]
        if len(high_settlements) > len(cases) * 0.3:
            indicators.append("Strong evidence often leads to favorable settlements")
        
        # Quick settlements
        early_settlements = [c for c in cases if c.get('settlement_timing') in ['early', 'mediation']]
        if len(early_settlements) > len(cases) * 0.4:
            indicators.append("Early settlement discussions typically successful")
        
        # Complex case outcomes
        complex_cases = [c for c in cases if c.get('case_complexity', 0) > 0.7]
        if complex_cases:
            avg_complex_ratio = np.mean([c.get('settlement_amount', 0) / max(c.get('case_value', 1), 1) for c in complex_cases])
            if avg_complex_ratio > 0.6:
                indicators.append("Complex cases often drive higher settlement values")
        
        return indicators

    def _create_default_advanced_metrics(self, case_data: Dict[str, Any]) -> AdvancedSettlementMetrics:
        """Create default advanced metrics when calculation fails"""
        case_value = case_data.get('case_value', 100000)
        
        return AdvancedSettlementMetrics(
            settlement_probability=0.6,
            optimal_timing=SettlementTiming.MID,
            plaintiff_settlement_range=(case_value * 0.4, case_value * 0.8),
            defendant_settlement_range=(case_value * 0.3, case_value * 0.7),
            expected_settlement_value=case_value * 0.55,
            settlement_urgency_score=0.5,
            confidence_score=0.4,
            key_settlement_factors=["Case complexity", "Economic factors", "Time considerations"],
            negotiation_leverage={'plaintiff': 0.5, 'defendant': 0.5},
            volatility_index=0.3,
            strategic_advantage_score=0.5,
            dynamic_factors={'complexity_risk': 0.5, 'economic_pressure': 0.5}
        )

    def _develop_advanced_strategy(
        self, 
        case_data: Dict[str, Any], 
        metrics: AdvancedSettlementMetrics, 
        scenarios: List[SettlementScenario]
    ) -> Dict[str, Any]:
        """Develop advanced negotiation strategy"""
        
        # Use base strategy as foundation
        base_strategy = super()._develop_negotiation_strategy(case_data, metrics, scenarios)
        
        # Enhance with advanced analytics
        advanced_strategy = base_strategy.copy()
        
        # Add AI-driven insights
        if hasattr(metrics, 'ai_consensus_score') and metrics.ai_consensus_score > 0.7:
            advanced_strategy['ai_confidence'] = 'high'
            advanced_strategy['ai_recommendations'] = [
                "Multiple AI models show high agreement on settlement probability",
                "Consider accelerated negotiation timeline",
                "Focus on data-driven value justification"
            ]
        
        # Add Monte Carlo insights
        if hasattr(metrics, 'monte_carlo_results') and metrics.monte_carlo_results:
            mc = metrics.monte_carlo_results
            advanced_strategy['risk_profile'] = {
                'volatility': mc.std_settlement_probability,
                'confidence_90': mc.confidence_intervals.get('90%', (0, 0)),
                'downside_risk': mc.risk_metrics.get('value_at_risk_5%', 0),
                'upside_potential': mc.percentiles.get('90th', 0)
            }
        
        # Add market timing insights
        if metrics.market_trend_adjustment != 0:
            if metrics.market_trend_adjustment > 0.02:
                advanced_strategy['market_timing'] = "favorable"
                advanced_strategy['timing_advice'] = "Accelerate negotiations to capitalize on favorable market conditions"
            elif metrics.market_trend_adjustment < -0.02:
                advanced_strategy['market_timing'] = "challenging"
                advanced_strategy['timing_advice'] = "Consider delaying or restructuring settlement approach"
            else:
                advanced_strategy['market_timing'] = "neutral"
        
        return advanced_strategy

    def _assess_advanced_risks(
        self, 
        case_data: Dict[str, Any], 
        metrics: AdvancedSettlementMetrics, 
        monte_carlo: Optional[Any]
    ) -> Dict[str, Any]:
        """Assess advanced risks with enhanced analytics"""
        
        # Base risk assessment
        base_risks = super()._assess_settlement_risks(case_data, metrics)
        
        # Enhanced risk analysis
        advanced_risks = base_risks.copy()
        
        # Add volatility-based risks
        if metrics.volatility_index > 0.2:
            advanced_risks['high_risks'].append("High outcome volatility increases settlement uncertainty")
            advanced_risks['mitigation_strategies']['volatility'] = "Use structured settlement with milestone payments"
        
        # Add Monte Carlo risk insights
        if monte_carlo and hasattr(monte_carlo, 'risk_metrics'):
            risk_metrics = monte_carlo.risk_metrics
            
            if risk_metrics.get('value_at_risk_5%', 0) < 0.3:
                advanced_risks['high_risks'].append("Significant downside risk in worst-case scenarios")
            
            if risk_metrics.get('volatility', 0) > 0.15:
                advanced_risks['medium_risks'].append("Moderate outcome volatility requires scenario planning")
        
        # Add AI consensus risks
        if hasattr(metrics, 'ai_consensus_score') and metrics.ai_consensus_score < 0.5:
            advanced_risks['medium_risks'].append("Low AI consensus suggests uncertain outcome")
            advanced_risks['mitigation_strategies']['ai_uncertainty'] = "Gather additional case data for better prediction"
        
        # Calculate enhanced risk score
        total_risks = len(advanced_risks.get('high_risks', [])) * 0.8 + len(advanced_risks.get('medium_risks', [])) * 0.5
        advanced_risks['enhanced_risk_score'] = min(1.0, total_risks / 10)
        
        return advanced_risks

    def _generate_intelligent_recommendations(
        self, 
        case_data: Dict[str, Any], 
        metrics: AdvancedSettlementMetrics, 
        scenarios: List[SettlementScenario], 
        risks: Dict[str, Any]
    ) -> List[str]:
        """Generate intelligent recommendations based on advanced analytics"""
        
        recommendations = []
        
        # Probability-based recommendations
        if metrics.settlement_probability > 0.8:
            recommendations.append(f"Exceptional settlement probability ({metrics.settlement_probability:.0%}) - pursue aggressive settlement strategy")
        elif metrics.settlement_probability > 0.6:
            recommendations.append(f"Strong settlement prospects ({metrics.settlement_probability:.0%}) - prioritize negotiation preparation")
        elif metrics.settlement_probability < 0.4:
            recommendations.append(f"Lower settlement likelihood ({metrics.settlement_probability:.0%}) - prepare robust trial strategy alongside settlement efforts")
        
        # AI consensus recommendations
        if hasattr(metrics, 'ai_consensus_score'):
            if metrics.ai_consensus_score > 0.8:
                recommendations.append("High AI consensus provides strong analytical foundation for settlement decisions")
            elif metrics.ai_consensus_score < 0.5:
                recommendations.append("Mixed AI analysis suggests gathering additional case intelligence before major settlement decisions")
        
        # Monte Carlo recommendations
        if hasattr(metrics, 'monte_carlo_results') and metrics.monte_carlo_results:
            mc = metrics.monte_carlo_results
            if mc.std_settlement_probability > 0.15:
                recommendations.append(f"High outcome variability ({mc.std_settlement_probability:.0%}) - consider structured settlement to manage uncertainty")
            
            confidence_90 = mc.confidence_intervals.get('90%', (0, 0))
            if confidence_90[1] - confidence_90[0] > 0.3:
                recommendations.append("Wide confidence intervals suggest comprehensive scenario planning essential")
        
        # Market timing recommendations
        if abs(metrics.market_trend_adjustment) > 0.02:
            if metrics.market_trend_adjustment > 0:
                recommendations.append(f"Favorable market trends (+{metrics.market_trend_adjustment:.1%}) - accelerate settlement discussions")
            else:
                recommendations.append(f"Challenging market conditions ({metrics.market_trend_adjustment:+.1%}) - consider timeline adjustments")
        
        # Strategic advantage recommendations
        if metrics.strategic_advantage_score > 0.7:
            recommendations.append("Strong strategic position supports assertive negotiation approach")
        elif metrics.strategic_advantage_score < 0.4:
            recommendations.append("Weaker position suggests collaborative settlement approach with creative structuring")
        
        # Risk-based recommendations
        if risks.get('enhanced_risk_score', 0.5) > 0.7:
            recommendations.append("High risk profile requires comprehensive mitigation strategy and conservative settlement planning")
        
        # Timing optimization
        best_scenario = max(scenarios, key=lambda s: s.probability * s.plaintiff_satisfaction) if scenarios else None
        if best_scenario:
            recommendations.append(f"Optimal settlement window: {best_scenario.scenario_name} approach with {best_scenario.timing.value.replace('_', ' ')} timing")
        
        # Value optimization
        if metrics.expected_settlement_value > case_data.get('case_value', 0) * 0.7:
            recommendations.append(f"Strong expected value (${metrics.expected_settlement_value:,.0f}) supports premium settlement targeting")
        
        return recommendations[:8]  # Limit to top 8 recommendations

    def _create_enhanced_ai_analysis_prompt(self, case_data: Dict[str, Any]) -> str:
        """Create enhanced structured prompt for latest AI models"""
        case_type = case_data.get('case_type', 'civil')
        case_value = case_data.get('case_value', 100000)
        evidence_strength = case_data.get('evidence_strength', 0.5)
        complexity = case_data.get('case_complexity', 0.5)
        witness_count = case_data.get('witness_count', 0)
        case_facts = case_data.get('case_facts', 'Standard civil case')
        
        prompt = f"""
ADVANCED LEGAL SETTLEMENT PROBABILITY ANALYSIS

CASE PROFILE:
- Type: {case_type.title()} Law Case
- Claim Value: ${case_value:,.2f}
- Evidence Strength: {evidence_strength * 10:.1f}/10
- Case Complexity: {complexity:.1%}
- Jurisdiction: {case_data.get('jurisdiction', 'Federal')}
- Witness Count: {witness_count}
- Filing Date: {case_data.get('filing_date', 'Recent')}
- Judge: {case_data.get('judge_name', 'Standard')}

CASE FACTS:
{case_facts[:500]}

ADVANCED ANALYSIS REQUIRED:
Please provide a comprehensive JSON-formatted analysis with the following structure:

{{
  "settlement_probability": <decimal 0.0-1.0>,
  "confidence_score": <decimal 0.0-1.0>,
  "key_risk_factors": [
    {{"factor": "factor name", "impact": <decimal -1.0 to 1.0>, "likelihood": <decimal 0.0-1.0>}},
    // ... top 5 factors
  ],
  "optimal_timing": "<early|mid|late|mediation|pre_trial|trial_door>",
  "settlement_range": {{
    "minimum": <amount>,
    "likely": <amount>,
    "maximum": <amount>
  }},
  "strategic_factors": {{
    "plaintiff_leverage": <decimal 0.0-1.0>,
    "defendant_leverage": <decimal 0.0-1.0>,
    "time_pressure": <decimal 0.0-1.0>,
    "economic_factors": <decimal 0.0-1.0>
  }},
  "negotiation_recommendations": [
    // ... top 3 strategic recommendations
  ],
  "market_considerations": "<analysis of current legal market trends>",
  "precedent_analysis": "<relevant case law and precedent factors>",
  "volatility_assessment": <decimal 0.0-1.0>
}}

Base your analysis on:
1. Current legal precedents and market trends
2. Statistical analysis of similar cases
3. Economic factors and jurisdictional considerations
4. Case-specific risk and opportunity factors
5. Negotiation dynamics and timing optimization

Provide realistic, data-driven probabilities with professional legal insights.
"""
        return prompt

    def _parse_enhanced_ai_response(self, response: str, provider: AIProvider) -> Dict[str, Any]:
        """Parse enhanced AI response with JSON structure support"""
        try:
            # Try to parse as JSON first
            import re
            import json
            
            # Extract JSON block if present
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    return {
                        'settlement_probability': json_data.get('settlement_probability', 0.5),
                        'confidence_score': json_data.get('confidence_score', 0.6),
                        'key_factors': [f.get('factor', 'Unknown') for f in json_data.get('key_risk_factors', [])[:3]],
                        'risk_factors': json_data.get('key_risk_factors', []),
                        'optimal_timing': json_data.get('optimal_timing', 'mid'),
                        'settlement_range': json_data.get('settlement_range', {}),
                        'strategic_factors': json_data.get('strategic_factors', {}),
                        'recommendations': json_data.get('negotiation_recommendations', []),
                        'market_analysis': json_data.get('market_considerations', ''),
                        'precedent_analysis': json_data.get('precedent_analysis', ''),
                        'volatility': json_data.get('volatility_assessment', 0.3),
                        'raw_response': response[:1000]
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback to text parsing
            analysis = {
                'settlement_probability': 0.5,
                'confidence_score': 0.6,
                'key_factors': [],
                'optimal_timing': 'mid',
                'risk_level': 'medium',
                'expected_range': (0, 0),
                'insights': response[:500],
                'volatility': 0.3
            }
            
            lines = response.split('\n')
            
            for line in lines:
                line_lower = line.strip().lower()
                
                if 'settlement_probability' in line_lower or 'probability' in line_lower:
                    try:
                        prob_match = re.search(r'(\d*\.?\d+)', line)
                        if prob_match:
                            prob = float(prob_match.group(1))
                            if prob > 1.0:
                                prob = prob / 100  # Convert percentage
                            analysis['settlement_probability'] = max(0.0, min(1.0, prob))
                    except:
                        pass
                
                elif 'confidence' in line_lower:
                    try:
                        conf_match = re.search(r'(\d*\.?\d+)', line)
                        if conf_match:
                            conf = float(conf_match.group(1))
                            if conf > 1.0:
                                conf = conf / 100
                            analysis['confidence_score'] = max(0.0, min(1.0, conf))
                    except:
                        pass
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Enhanced AI response parsing failed for {provider.value}: {e}")
            return {
                'settlement_probability': 0.5,
                'confidence_score': 0.4,
                'key_factors': ['case complexity', 'evidence strength', 'market conditions'],
                'optimal_timing': 'mid',
                'risk_level': 'medium',
                'insights': response[:200] if response else 'Analysis unavailable',
                'volatility': 0.3
            }

    def _create_ai_analysis_prompt(self, case_data: Dict[str, Any]) -> str:
        case_type = case_data.get('case_type', 'civil')
        case_value = case_data.get('case_value', 100000)
        evidence_strength = case_data.get('evidence_strength', 0.5)
        complexity = case_data.get('case_complexity', 0.5)
        
        prompt = f"""
Analyze this legal case for settlement probability. Provide a structured analysis with specific numeric values.

CASE DETAILS:
- Type: {case_type.title()} Law
- Claim Value: ${case_value:,.2f}
- Evidence Strength: {evidence_strength:.1f}/10
- Case Complexity: {complexity:.1%}
- Jurisdiction: {case_data.get('jurisdiction', 'General')}

REQUIRED ANALYSIS FORMAT:
1. Settlement Probability: [0.00-1.00]
2. Key Factors: [List 3 most important factors]
3. Optimal Timing: [early/mid/late/mediation/trial_door]
4. Risk Level: [low/medium/high]
5. Expected Range: [min-max settlement amounts]

Provide quantitative analysis based on legal precedent and case characteristics.
Focus on realistic probabilities and actionable insights.

RESPONSE FORMAT:
Settlement Probability: 0.XX
Key Factors: factor1, factor2, factor3
Optimal Timing: timing_phase
Risk Level: risk_level
Expected Range: $X - $Y
Analysis: Brief explanation (2-3 sentences)
"""
        return prompt

    def _parse_ai_response(self, response: str, provider: AIProvider) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            analysis = {
                'settlement_probability': 0.5,
                'key_factors': [],
                'optimal_timing': 'mid',
                'risk_level': 'medium',
                'expected_range': (0, 0),
                'insights': response[:500]  # First 500 chars
            }
            
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip().lower()
                
                if 'settlement probability:' in line:
                    try:
                        prob_str = line.split(':')[1].strip()
                        # Extract decimal value
                        import re
                        prob_match = re.search(r'(\d*\.?\d+)', prob_str)
                        if prob_match:
                            prob = float(prob_match.group(1))
                            if prob > 1.0:
                                prob = prob / 100  # Convert percentage
                            analysis['settlement_probability'] = max(0.0, min(1.0, prob))
                    except:
                        pass
                
                elif 'key factors:' in line:
                    try:
                        factors_str = line.split(':', 1)[1].strip()
                        factors = [f.strip() for f in factors_str.split(',')]
                        analysis['key_factors'] = factors[:3]
                    except:
                        pass
                
                elif 'optimal timing:' in line:
                    try:
                        timing = line.split(':')[1].strip()
                        if timing in ['early', 'mid', 'late', 'mediation', 'trial_door']:
                            analysis['optimal_timing'] = timing
                    except:
                        pass
            
            return analysis
            
        except Exception as e:
            logger.warning(f"AI response parsing failed for {provider.value}: {e}")
            return {
                'settlement_probability': 0.5,
                'key_factors': ['case complexity', 'evidence strength', 'economic factors'],
                'optimal_timing': 'mid',
                'risk_level': 'medium',
                'insights': response[:200] if response else 'Analysis unavailable'
            }

    async def _monte_carlo_simulation(self, case_data: Dict[str, Any]) -> MonteCarloResults:
        """Run enhanced Monte Carlo simulation with sophisticated probabilistic modeling"""
        try:
            logger.info(f"🎲 Starting enhanced Monte Carlo simulation with {self.monte_carlo_iterations} iterations")
            
            # Enhanced parameter distributions based on legal research
            base_prob = case_data.get('evidence_strength', 5) / 10
            complexity_factor = case_data.get('case_complexity', 0.5)
            case_value = case_data.get('case_value', 100000)
            witness_count = case_data.get('witness_count', 3)
            
            # Legal case factors with realistic distributions
            jurisdiction_multipliers = {
                'federal': 1.1, 'state': 1.0, 'commercial': 1.15, 'employment': 0.9, 
                'personal_injury': 1.05, 'contract': 1.0, 'intellectual_property': 1.2
            }
            
            jurisdiction = case_data.get('jurisdiction', 'state').lower()
            jurisdiction_mult = jurisdiction_multipliers.get(jurisdiction, 1.0)
            
            # Advanced Monte Carlo parameters
            iterations = min(self.monte_carlo_iterations, 50000)  # Cap for performance
            results = []
            
            # Economic cycle modeling
            economic_cycles = np.random.choice(['recession', 'expansion', 'stability'], 
                                             iterations, p=[0.15, 0.25, 0.60])
            
            # Seasonal effects
            months = np.random.randint(1, 13, iterations)
            seasonal_factors = np.where(
                np.isin(months, [6, 7, 8]), 0.95,  # Summer slowdown
                np.where(np.isin(months, [11, 12]), 1.05, 1.0)  # Year-end push
            )
            
            # Judge variability (some judges favor settlements more)
            judge_settlement_bias = np.random.normal(1.0, 0.15, iterations)
            
            # Run enhanced simulation
            for i in range(iterations):
                # Dynamic evidence strength (can change during discovery)
                evidence_trajectory = np.random.choice(['improving', 'stable', 'declining'], 
                                                    p=[0.3, 0.5, 0.2])
                if evidence_trajectory == 'improving':
                    evidence_multiplier = np.random.uniform(1.0, 1.3)
                elif evidence_trajectory == 'declining':
                    evidence_multiplier = np.random.uniform(0.7, 1.0)
                else:
                    evidence_multiplier = np.random.uniform(0.9, 1.1)
                
                adjusted_evidence = np.clip(base_prob * evidence_multiplier, 0, 1)
                
                # Complexity with learning curve (cases get clearer over time)
                complexity_clarity = np.random.beta(2, 3)  # Tends toward clarification
                adjusted_complexity = complexity_factor * complexity_clarity
                
                # Witness reliability and availability
                witness_reliability = np.random.beta(witness_count + 1, 3)  # More witnesses = higher reliability
                
                # Economic impact modeling
                economic_impact = 1.0
                if economic_cycles[i] == 'recession':
                    economic_impact = np.random.uniform(0.85, 0.95)  # Lower settlements in recession
                elif economic_cycles[i] == 'expansion':
                    economic_impact = np.random.uniform(1.05, 1.15)  # Higher settlements in good times
                
                # Case value impact (higher value cases have different dynamics)
                value_factor = 1.0
                if case_value > 1000000:  # High-value cases
                    value_factor = np.random.normal(1.1, 0.1)  # Slightly higher settlement probability
                elif case_value < 50000:  # Small claims
                    value_factor = np.random.normal(0.9, 0.1)  # Might go to trial more often
                
                # Multi-factor settlement probability
                base_settlement_prob = (
                    adjusted_evidence * 0.35 +  # Evidence is key
                    (1 - adjusted_complexity) * 0.20 +  # Simpler cases settle more
                    witness_reliability * 0.15 +  # Good witnesses help
                    np.random.beta(3, 2) * 0.30  # General settlement tendency
                )
                
                # Apply all modifiers
                final_prob = (base_settlement_prob * 
                             jurisdiction_mult * 
                             economic_impact * 
                             seasonal_factors[i] * 
                             np.clip(judge_settlement_bias[i], 0.7, 1.3) *
                             value_factor)
                
                # Realistic bounds with legal constraints
                final_prob = np.clip(final_prob, 0.05, 0.95)
                
                # Add rare extreme events (5% chance)
                if np.random.random() < 0.05:
                    extreme_factor = np.random.choice([0.3, 1.7], p=[0.5, 0.5])  # Major setback or breakthrough
                    final_prob *= extreme_factor
                    final_prob = np.clip(final_prob, 0.02, 0.98)
                
                results.append(final_prob)
            
            # Enhanced statistical analysis
            results = np.array(results)
            
            # Multi-dimensional percentiles
            percentiles = {
                '5th': np.percentile(results, 5),
                '10th': np.percentile(results, 10),
                '25th': np.percentile(results, 25),
                '50th': np.percentile(results, 50),
                '75th': np.percentile(results, 75),
                '90th': np.percentile(results, 90),
                '95th': np.percentile(results, 95)
            }
            
            # Multiple confidence intervals
            confidence_intervals = {}
            for level in [0.80, 0.90, 0.95, 0.99]:
                alpha = 1 - level
                lower = np.percentile(results, (alpha/2) * 100)
                upper = np.percentile(results, (1 - alpha/2) * 100)
                confidence_intervals[f'{int(level*100)}%'] = (lower, upper)
            
            # Advanced risk metrics
            risk_metrics = {
                'value_at_risk_5%': np.percentile(results, 5),
                'value_at_risk_10%': np.percentile(results, 10),
                'expected_shortfall_5%': np.mean(results[results <= np.percentile(results, 5)]),
                'expected_shortfall_10%': np.mean(results[results <= np.percentile(results, 10)]),
                'volatility': np.std(results),
                'downside_volatility': np.std(results[results < np.median(results)]),
                'skewness': stats.skew(results),
                'kurtosis': stats.kurtosis(results),
                'sharpe_ratio': (np.mean(results) - 0.3) / np.std(results) if np.std(results) > 0 else 0,
                'maximum_drawdown': self._calculate_max_drawdown(results)
            }
            
            # Enhanced scenario probabilities with business implications
            scenario_probabilities = {
                'almost_certain_settlement': np.mean(results > 0.9),
                'very_high_settlement': np.mean((results > 0.8) & (results <= 0.9)),
                'high_settlement': np.mean((results > 0.6) & (results <= 0.8)),
                'moderate_settlement': np.mean((results > 0.4) & (results <= 0.6)),
                'low_settlement': np.mean((results > 0.2) & (results <= 0.4)),
                'very_low_settlement': np.mean((results > 0.05) & (results <= 0.2)),
                'likely_trial': np.mean(results <= 0.05),
                'optimal_range': np.mean((results >= 0.4) & (results <= 0.8))
            }
            
            # Advanced convergence analysis
            convergence_analysis = self._analyze_advanced_convergence(results)
            
            monte_carlo_results = MonteCarloResults(
                mean_settlement_probability=np.mean(results),
                std_settlement_probability=np.std(results),
                percentiles=percentiles,
                confidence_intervals=confidence_intervals,
                scenario_probabilities=scenario_probabilities,
                risk_metrics=risk_metrics,
                simulation_count=iterations,
                convergence_analysis=convergence_analysis
            )
            
            logger.info(f"✅ Enhanced Monte Carlo completed: μ={np.mean(results):.1%}, σ={np.std(results):.1%}, 95% CI=[{confidence_intervals['95%'][0]:.1%}, {confidence_intervals['95%'][1]:.1%}]")
            return monte_carlo_results
            
        except Exception as e:
            logger.error(f"❌ Enhanced Monte Carlo simulation failed: {e}")
            # Return improved fallback results
            return MonteCarloResults(
                mean_settlement_probability=0.55,
                std_settlement_probability=0.15,
                percentiles={'25th': 0.4, '50th': 0.55, '75th': 0.7},
                confidence_intervals={'95%': (0.3, 0.8)},
                scenario_probabilities={'moderate_settlement': 0.6},
                risk_metrics={'volatility': 0.15},
                simulation_count=1000,
                convergence_analysis={'converged': False}
            )

    def _calculate_max_drawdown(self, results: np.ndarray) -> float:
        """Calculate maximum drawdown for risk assessment"""
        try:
            cumulative = np.cumsum(results) / np.arange(1, len(results) + 1)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            return float(np.min(drawdown))
        except:
            return 0.0

    def _analyze_advanced_convergence(self, results: np.ndarray) -> Dict[str, Any]:
        """Advanced convergence analysis with multiple metrics"""

    def _analyze_convergence(self, results: np.ndarray) -> Dict[str, Any]:
        """Analyze Monte Carlo convergence"""
        try:
            # Running average
            running_mean = np.cumsum(results) / np.arange(1, len(results) + 1)
            
            # Convergence check (last 10% vs final value)
            final_mean = running_mean[-1]
            last_10_percent = int(len(results) * 0.1)
            recent_mean = np.mean(running_mean[-last_10_percent:])
            
            convergence_error = abs(recent_mean - final_mean) / final_mean
            
            return {
                'converged': convergence_error < 0.01,  # 1% error threshold
                'convergence_error': convergence_error,
                'final_mean': final_mean,
                'running_means': running_mean[-100:].tolist(),  # Last 100 iterations
                'stability_score': 1 - min(1, convergence_error * 10)
            }
            
        except Exception as e:
            logger.warning(f"Convergence analysis failed: {e}")
            return {'converged': False, 'convergence_error': 0.05}

    async def _comparative_case_analysis(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find and analyze comparable cases"""
        try:
            # Enhanced similarity search
            similar_cases = await self._find_similar_cases_enhanced(case_data)
            
            if not similar_cases:
                return {'cases': [], 'analysis': 'No comparable cases found'}
            
            # Analyze patterns
            case_analysis = self._analyze_case_patterns(similar_cases, case_data)
            
            return {
                'cases': similar_cases,
                'analysis': case_analysis,
                'pattern_insights': self._extract_pattern_insights(similar_cases)
            }
            
        except Exception as e:
            logger.error(f"Comparative case analysis failed: {e}")
            return {'cases': [], 'analysis': 'Analysis unavailable'}

    async def _market_trend_analysis(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market trends affecting settlement"""
        try:
            case_type = case_data.get('case_type', 'civil')
            jurisdiction = case_data.get('jurisdiction', 'general')
            
            # Check cache first
            cache_key = f"{case_type}_{jurisdiction}"
            if cache_key in self.market_data_cache:
                cached_data = self.market_data_cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_expiry:
                    return cached_data['data']
            
            # Analyze recent trends (simplified for now)
            trend_analysis = {
                'settlement_rate_trend': self._calculate_settlement_trend(case_type),
                'value_trend': self._calculate_value_trend(case_type),
                'timing_trends': self._calculate_timing_trends(case_type),
                'market_volatility': np.random.normal(0.1, 0.02),  # Placeholder
                'economic_indicators': {
                    'legal_market_index': np.random.normal(1.0, 0.1),
                    'litigation_volume': np.random.normal(1.0, 0.15),
                    'settlement_pressure_index': np.random.normal(0.6, 0.1)
                }
            }
            
            # Cache results
            self.market_data_cache[cache_key] = {
                'data': trend_analysis,
                'timestamp': time.time()
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Market trend analysis failed: {e}")
            return {'settlement_rate_trend': 0.0, 'value_trend': 0.0}

    def _calculate_settlement_trend(self, case_type: str) -> float:
        """Calculate settlement rate trend for case type"""
        # Simplified trend calculation
        case_type_trends = {
            'employment': 0.05,  # 5% increase
            'personal_injury': 0.03,
            'commercial': -0.02,
            'intellectual_property': 0.01,
            'civil': 0.0
        }
        return case_type_trends.get(case_type, 0.0)

    def _calculate_value_trend(self, case_type: str) -> float:
        """Calculate settlement value trend"""
        # Economic factors affecting settlement values
        base_trend = np.random.normal(0.02, 0.01)  # General 2% inflation
        
        case_multipliers = {
            'employment': 1.05,  # Higher due to policy changes
            'personal_injury': 1.03,
            'commercial': 0.98,
            'civil': 1.0
        }
        
        return base_trend * case_multipliers.get(case_type, 1.0)

    def _calculate_timing_trends(self, case_type: str) -> Dict[str, float]:
        """Calculate optimal timing trends"""
        return {
            'early_trend': np.random.normal(0.0, 0.02),
            'mediation_trend': np.random.normal(0.05, 0.02),
            'trial_door_trend': np.random.normal(-0.02, 0.02)
        }

    def _combine_advanced_metrics(
        self, 
        base_metrics: AdvancedSettlementMetrics,
        ai_consensus: Optional[Dict[str, Any]],
        monte_carlo: Optional[MonteCarloResults],
        comparative: Optional[Dict[str, Any]],
        market_trends: Optional[Dict[str, Any]]
    ) -> AdvancedSettlementMetrics:
        """Combine all analysis components into enhanced metrics"""
        
        if not base_metrics:
            # Create default metrics if base analysis failed
            base_metrics = AdvancedSettlementMetrics()
        
        # Integrate AI consensus
        if ai_consensus and 'consensus_probability' in ai_consensus:
            ai_weight = 0.3 if ai_consensus.get('consensus_score', 0) > 0.7 else 0.2
            base_weight = 0.7 if ai_consensus.get('consensus_score', 0) > 0.7 else 0.8
            
            base_metrics.settlement_probability = (
                base_metrics.settlement_probability * base_weight +
                ai_consensus['consensus_probability'] * ai_weight
            )
            base_metrics.ai_consensus_score = ai_consensus.get('consensus_score', 0)
        
        # Integrate Monte Carlo results
        if monte_carlo:
            # Use Monte Carlo mean but adjust for confidence
            mc_weight = 0.4 if monte_carlo.convergence_analysis.get('converged', False) else 0.2
            base_weight = 1 - mc_weight
            
            base_metrics.settlement_probability = (
                base_metrics.settlement_probability * base_weight +
                monte_carlo.mean_settlement_probability * mc_weight
            )
            base_metrics.monte_carlo_results = monte_carlo
            base_metrics.volatility_index = monte_carlo.std_settlement_probability
        
        # Integrate market trends
        if market_trends:
            settlement_trend = market_trends.get('settlement_rate_trend', 0)
            base_metrics.settlement_probability += settlement_trend
            base_metrics.market_trend_adjustment = settlement_trend
            
            # Update expected value with value trend
            value_trend = market_trends.get('value_trend', 0)
            base_metrics.expected_settlement_value *= (1 + value_trend)
        
        # Calculate strategic advantage
        base_metrics.strategic_advantage_score = self._calculate_strategic_advantage(base_metrics)
        
        # Ensure probability bounds
        base_metrics.settlement_probability = max(0.05, min(0.95, base_metrics.settlement_probability))
        
        # Update confidence score based on data quality
        confidence_factors = []
        if ai_consensus:
            confidence_factors.append(ai_consensus.get('consensus_score', 0.5))
        if monte_carlo and monte_carlo.convergence_analysis.get('converged', False):
            confidence_factors.append(0.9)
        if comparative and len(comparative.get('cases', [])) > 3:
            confidence_factors.append(0.8)
        
        if confidence_factors:
            base_metrics.confidence_score = (base_metrics.confidence_score + np.mean(confidence_factors)) / 2
        
        return base_metrics

    def _calculate_strategic_advantage(self, metrics: AdvancedSettlementMetrics) -> float:
        """Calculate overall strategic advantage score"""
        factors = [
            metrics.settlement_probability,
            metrics.negotiation_leverage.get('plaintiff', 0.5),
            1 - metrics.settlement_urgency_score,  # Lower urgency = higher advantage
            metrics.confidence_score
        ]
        
        return np.mean(factors)

    async def _generate_advanced_scenarios(
        self, 
        case_data: Dict[str, Any], 
        metrics: AdvancedSettlementMetrics
    ) -> List[SettlementScenario]:
        """Generate advanced settlement scenarios"""
        
        scenarios = []
        
        # Base scenarios from parent class
        base_scenarios = await super()._generate_settlement_scenarios(case_data, metrics)
        scenarios.extend(base_scenarios)
        
        # Add Monte Carlo informed scenarios
        if metrics.monte_carlo_results:
            mc_scenarios = self._generate_monte_carlo_scenarios(metrics)
            scenarios.extend(mc_scenarios)
        
        # Add market-driven scenarios
        if metrics.market_trend_adjustment != 0:
            market_scenarios = self._generate_market_scenarios(case_data, metrics)
            scenarios.extend(market_scenarios)
        
        # Normalize scenario probabilities
        total_prob = sum(s.probability for s in scenarios)
        if total_prob > 0:
            for scenario in scenarios:
                scenario.probability /= total_prob
        
        return scenarios[:6]  # Return top 6 scenarios

    def _generate_monte_carlo_scenarios(self, metrics: AdvancedSettlementMetrics) -> List[SettlementScenario]:
        """Generate scenarios based on Monte Carlo results"""
        scenarios = []
        
        if not metrics.monte_carlo_results:
            return scenarios
        
        mc = metrics.monte_carlo_results
        
        # High confidence scenario (75th percentile)
        scenarios.append(SettlementScenario(
            scenario_name="High Confidence Settlement",
            probability=mc.scenario_probabilities.get('high_settlement', 0.3),
            settlement_amount=metrics.expected_settlement_value * 1.2,
            timing=SettlementTiming.MID,
            key_conditions=["Monte Carlo high probability outcome", "Strong case fundamentals"],
            plaintiff_satisfaction=0.85,
            defendant_satisfaction=0.65,
            strategic_notes=f"Based on {mc.percentiles['75th']:.1%} Monte Carlo probability"
        ))
        
        # Conservative scenario (25th percentile)
        scenarios.append(SettlementScenario(
            scenario_name="Conservative Settlement",
            probability=mc.scenario_probabilities.get('low_settlement', 0.2),
            settlement_amount=metrics.expected_settlement_value * 0.8,
            timing=SettlementTiming.EARLY,
            key_conditions=["Risk mitigation priority", "Quick resolution preferred"],
            plaintiff_satisfaction=0.6,
            defendant_satisfaction=0.8,
            strategic_notes=f"Based on {mc.percentiles['25th']:.1%} Monte Carlo probability"
        ))
        
        return scenarios

    def _generate_market_scenarios(self, case_data: Dict[str, Any], metrics: AdvancedSettlementMetrics) -> List[SettlementScenario]:
        """Generate market-influenced scenarios"""
        scenarios = []
        
        if metrics.market_trend_adjustment == 0:
            return scenarios
        
        trend_factor = 1 + metrics.market_trend_adjustment
        
        scenarios.append(SettlementScenario(
            scenario_name="Market-Adjusted Settlement",
            probability=0.25,
            settlement_amount=metrics.expected_settlement_value * trend_factor,
            timing=SettlementTiming.MID,
            key_conditions=["Market trends favorable", "Economic conditions supportive"],
            plaintiff_satisfaction=0.75,
            defendant_satisfaction=0.7,
            strategic_notes=f"Adjusted for {metrics.market_trend_adjustment:+.1%} market trend"
        ))
        
        return scenarios

    async def _get_multi_ai_insights(
        self, 
        case_data: Dict[str, Any], 
        metrics: AdvancedSettlementMetrics, 
        scenarios: List[SettlementScenario]
    ) -> str:
        """Get enhanced insights from multiple AI providers"""
        
        try:
            # If we have AI consensus data, use it
            if hasattr(metrics, 'ai_consensus_score') and len(self.ai_providers) > 0:
                # Get one comprehensive insight from the best performing provider
                best_provider = max(self.ai_providers.keys(), key=lambda p: self.ai_providers[p]['weight'])
                config = self.ai_providers[best_provider]
                
                comprehensive_prompt = self._create_comprehensive_insights_prompt(case_data, metrics, scenarios)
                
                session_id = f"comprehensive-insights-{uuid.uuid4()}"
                
                if best_provider == AIProvider.GEMINI:
                    chat = LlmChat(
                        api_key=config['api_key'],
                        session_id=session_id,
                        system_message="You are a senior legal settlement strategist providing comprehensive analysis."
                    ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(3000)
                else:
                    # Use first available model for other providers
                    model = config['models'][0] if config['models'] else 'gpt-4o'
                    chat = LlmChat(
                        api_key=config['api_key'],
                        session_id=session_id,
                        system_message="You are a senior legal settlement strategist providing comprehensive analysis."
                    ).with_model("openai", model).with_max_tokens(3000)
                
                user_message = UserMessage(text=comprehensive_prompt)
                response = await chat.send_message(user_message)
                
                return response if response else self._generate_fallback_insights(case_data, metrics, scenarios)
            
            else:
                # Fallback to parent method
                return await super()._get_ai_settlement_insights(case_data, metrics, scenarios)
                
        except Exception as e:
            logger.error(f"Multi-AI insights failed: {e}")
            return self._generate_fallback_insights(case_data, metrics, scenarios)

    def _create_comprehensive_insights_prompt(
        self, 
        case_data: Dict[str, Any], 
        metrics: AdvancedSettlementMetrics, 
        scenarios: List[SettlementScenario]
    ) -> str:
        """Create comprehensive insights prompt"""
        
        mc_info = ""
        if metrics.monte_carlo_results:
            mc = metrics.monte_carlo_results
            mc_info = f"""
Monte Carlo Analysis Results:
- Mean Probability: {mc.mean_settlement_probability:.1%}
- Volatility: {mc.std_settlement_probability:.1%}
- 95% Confidence Interval: {mc.confidence_intervals.get('95%', (0, 0))[0]:.1%} - {mc.confidence_intervals.get('95%', (0, 0))[1]:.1%}
- Risk Metrics: VaR 5% = {mc.risk_metrics.get('value_at_risk_5%', 0):.1%}
"""
        
        prompt = f"""
COMPREHENSIVE SETTLEMENT ANALYSIS REPORT

CASE OVERVIEW:
- Type: {case_data.get('case_type', 'Civil').title()}
- Value: ${case_data.get('case_value', 0):,.2f}
- Evidence Strength: {case_data.get('evidence_strength', 5)}/10
- Complexity: {case_data.get('case_complexity', 0.5):.0%}
- Jurisdiction: {case_data.get('jurisdiction', 'General')}

ADVANCED METRICS:
- Settlement Probability: {metrics.settlement_probability:.1%}
- Expected Value: ${metrics.expected_settlement_value:,.2f}
- Volatility Index: {metrics.volatility_index:.1%}
- Strategic Advantage: {metrics.strategic_advantage_score:.1%}
- AI Consensus Score: {getattr(metrics, 'ai_consensus_score', 0):.1%}
- Market Adjustment: {metrics.market_trend_adjustment:+.1%}
{mc_info}

TOP SCENARIOS:
{chr(10).join(f'• {s.scenario_name}: {s.probability:.0%} probability (${s.settlement_amount:,.2f})' for s in scenarios[:3])}

PROVIDE COMPREHENSIVE STRATEGIC ANALYSIS:
1. Executive Summary (2-3 sentences)
2. Key Strategic Recommendations (4-5 actionable points)
3. Risk Assessment and Mitigation (3-4 specific strategies)
4. Negotiation Positioning (timing, leverage, tactics)
5. Value Optimization Strategies
6. Timeline and Milestone Recommendations

Focus on actionable, data-driven insights that integrate all analytical components.
"""
        
        return prompt

    def _generate_fallback_insights(
        self, 
        case_data: Dict[str, Any], 
        metrics: AdvancedSettlementMetrics, 
        scenarios: List[SettlementScenario]
    ) -> str:
        """Generate comprehensive fallback insights"""
        
        case_type = case_data.get('case_type', 'civil').title()
        case_value = case_data.get('case_value', 100000)
        
        mc_analysis = ""
        if metrics.monte_carlo_results:
            mc = metrics.monte_carlo_results
            mc_analysis = f"""

**Monte Carlo Risk Analysis:**
Our simulation of {mc.simulation_count:,} scenarios shows a {mc.mean_settlement_probability:.1%} average settlement probability with ±{mc.std_settlement_probability:.1%} volatility. The 95% confidence interval ranges from {mc.confidence_intervals.get('95%', (0, 0))[0]:.1%} to {mc.confidence_intervals.get('95%', (0, 0))[1]:.1%}, indicating {'high' if mc.std_settlement_probability < 0.1 else 'moderate' if mc.std_settlement_probability < 0.2 else 'significant'} outcome uncertainty."""
        
        ai_consensus = ""
        if hasattr(metrics, 'ai_consensus_score') and metrics.ai_consensus_score > 0:
            agreement_level = 'high' if metrics.ai_consensus_score > 0.8 else 'moderate' if metrics.ai_consensus_score > 0.6 else 'mixed'
            ai_consensus = f" Multiple AI models show {agreement_level} agreement on this assessment (consensus score: {metrics.ai_consensus_score:.0%})."
        
        insights = f"""
**ADVANCED SETTLEMENT ANALYSIS REPORT**

**Executive Summary:**
This {case_type} case presents a {metrics.settlement_probability:.0%} settlement probability with an expected value of ${metrics.expected_settlement_value:,.2f} ({(metrics.expected_settlement_value/case_value*100):.0f}% of claim value). The strategic advantage score of {metrics.strategic_advantage_score:.0%} indicates {'strong' if metrics.strategic_advantage_score > 0.7 else 'moderate' if metrics.strategic_advantage_score > 0.5 else 'challenging'} negotiation positioning.{ai_consensus}{mc_analysis}

**Key Strategic Recommendations:**

1. **Optimal Settlement Strategy:** Target the ${metrics.expected_settlement_value:,.2f} range during {metrics.optimal_timing.value.replace('_', ' ').lower()} phase negotiations, leveraging the {metrics.settlement_probability:.0%} probability assessment.

2. **Risk Mitigation:** With {metrics.volatility_index:.0%} volatility, {'implement conservative settlement floors' if metrics.volatility_index > 0.15 else 'pursue aggressive positioning given low outcome variance'}.

3. **Market Timing:** Current market trends show {'+' if metrics.market_trend_adjustment >= 0 else ''}{metrics.market_trend_adjustment:.1%} adjustment factor - {'accelerate discussions to capitalize on favorable conditions' if metrics.market_trend_adjustment > 0 else 'consider delaying for better market conditions' if metrics.market_trend_adjustment < -0.02 else 'proceed with standard timing'}.

4. **Negotiation Leverage:** Plaintiff holds {metrics.negotiation_leverage.get('plaintiff', 0.5):.0%} leverage vs defendant's {metrics.negotiation_leverage.get('defendant', 0.5):.0%} - {'press advantage for maximum settlement' if metrics.negotiation_leverage.get('plaintiff', 0.5) > 0.6 else 'focus on collaborative resolution' if metrics.negotiation_leverage.get('defendant', 0.5) > 0.6 else 'expect balanced negotiations'}.

5. **Value Optimization:** Settlement urgency at {metrics.settlement_urgency_score:.0%} suggests {'immediate action required' if metrics.settlement_urgency_score > 0.75 else 'measured approach with deadline management' if metrics.settlement_urgency_score > 0.5 else 'patience for optimal timing'}.

**Risk Assessment & Mitigation:**

• **Outcome Volatility:** {'High uncertainty requires comprehensive scenario planning and flexible settlement structure' if metrics.volatility_index > 0.2 else 'Moderate volatility allows standard negotiation approach' if metrics.volatility_index > 0.1 else 'Low volatility supports confident settlement positioning'}

• **Strategic Positioning:** Focus on {', '.join(metrics.key_settlement_factors[:3])} as primary negotiation levers

• **Timeline Management:** {metrics.optimal_timing.value.replace('_', ' ').title()} timing optimization balances case development with settlement pressure

**Expected Outcomes:**

Based on advanced analytics, anticipate settlement probability of {metrics.settlement_probability:.0%} with expected value ${metrics.expected_settlement_value:,.2f}. The analysis indicates {metrics.confidence_score:.0%} confidence in these projections, supported by {'multiple AI models and statistical simulation' if metrics.monte_carlo_results else 'comprehensive case factor analysis'}.

**Next Steps:**
1. Prepare settlement presentation emphasizing key success factors
2. {'Initiate immediate discussions due to high urgency' if metrics.settlement_urgency_score > 0.7 else 'Plan strategic timing for optimal market conditions'}
3. Structure negotiation approach around {metrics.settlement_probability:.0%} success probability
4. {'Consider mediation given moderate leverage balance' if abs(metrics.negotiation_leverage.get('plaintiff', 0.5) - 0.5) < 0.2 else 'Prepare for direct negotiation leveraging positional advantage'}

*Analysis powered by advanced AI models, Monte Carlo simulation, and market trend integration for comprehensive settlement strategy optimization.*
"""
        
        return insights

    async def _cache_advanced_analysis(self, analysis: SettlementAnalysis):
        """Cache advanced analysis with additional metadata"""
        try:
            # Use parent caching method but add advanced metadata
            await super()._cache_settlement_analysis(analysis)
            
            # Cache additional advanced data
            if hasattr(analysis.metrics, 'monte_carlo_results') and analysis.metrics.monte_carlo_results:
                mc_data = asdict(analysis.metrics.monte_carlo_results)
                
                await self.db.monte_carlo_cache.update_one(
                    {'case_id': analysis.case_id},
                    {'$set': {
                        'case_id': analysis.case_id,
                        'analysis_date': analysis.analysis_date,
                        'monte_carlo_results': mc_data,
                        'cached_at': datetime.utcnow()
                    }},
                    upsert=True
                )
            
            logger.info(f"💾 Advanced analysis cached for case {analysis.case_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Advanced analysis caching failed: {e}")

# Helper functions for enhanced analysis
async def get_advanced_settlement_calculator(db_connection):
    """Factory function to get enhanced settlement calculator"""
    return AdvancedSettlementCalculator(db_connection)

def create_enhanced_settlement_request():
    """Create enhanced request model for API"""
    from pydantic import BaseModel
    from typing import Optional
    
    class AdvancedSettlementRequest(BaseModel):
        case_type: str
        case_value: float
        evidence_strength: float
        case_complexity: float
        jurisdiction: Optional[str] = None
        judge_name: Optional[str] = None
        case_facts: Optional[str] = None
        analysis_mode: str = "advanced"  # basic, advanced, monte_carlo, comparative, real_time
        monte_carlo_iterations: Optional[int] = 10000
        ai_providers: Optional[List[str]] = None
        include_comparative: bool = True
        include_market_analysis: bool = True
        
    return AdvancedSettlementRequest
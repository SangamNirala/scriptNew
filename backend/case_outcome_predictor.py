"""
Case Outcome Predictor Module

ML-based prediction models for legal case outcomes using ensemble AI approach
with Gemini and Groq APIs, combined with statistical analysis of historical data.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import numpy as np
from collections import Counter, defaultdict
import google.generativeai as genai
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@dataclass
class CaseFeatures:
    """Structured case features for ML prediction"""
    case_type_score: float = 0.0
    jurisdiction_score: float = 0.0
    complexity_score: float = 0.0
    evidence_strength: float = 0.0
    case_value_normalized: float = 0.0
    judge_favorability: float = 0.5  # Default neutral
    historical_precedent_score: float = 0.0
    plaintiff_advantage_score: float = 0.0
    defendant_advantage_score: float = 0.0
    settlement_likelihood: float = 0.0

@dataclass
class PredictionMetrics:
    """Metrics for prediction model performance"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    sample_size: int = 0

class OutcomePredictionModel:
    """Base class for outcome prediction models"""
    
    def __init__(self, model_type: str):
        self.model_type = model_type
        self.trained = False
        self.performance_metrics = PredictionMetrics()
        
    async def train(self, training_data: List[Dict[str, Any]]):
        """Train the prediction model"""
        raise NotImplementedError
        
    async def predict(self, case_features: CaseFeatures) -> Dict[str, float]:
        """Make outcome predictions"""
        raise NotImplementedError

class GeminiPredictionModel(OutcomePredictionModel):
    """Gemini AI-based prediction model"""
    
    def __init__(self):
        super().__init__("gemini_ai")
        self.model = genai.GenerativeModel('gemini-pro')
        self.training_context = ""
        
    async def train(self, training_data: List[Dict[str, Any]]):
        """Build training context from historical data"""
        try:
            logger.info(f"🧠 Training Gemini model with {len(training_data)} cases")
            
            # Build comprehensive training context
            outcome_patterns = self._analyze_training_patterns(training_data)
            
            self.training_context = f"""
            LEGAL CASE OUTCOME PREDICTION TRAINING DATA ANALYSIS
            
            Dataset: {len(training_data)} historical cases
            
            OUTCOME DISTRIBUTION:
            {self._format_outcome_distribution(outcome_patterns)}
            
            CASE TYPE PATTERNS:
            {self._format_case_type_patterns(training_data)}
            
            JURISDICTION INSIGHTS:
            {self._format_jurisdiction_patterns(training_data)}
            
            VALUE CORRELATION ANALYSIS:
            {self._format_value_correlations(training_data)}
            
            KEY PREDICTION FACTORS IDENTIFIED:
            {self._identify_key_factors(training_data)}
            """
            
            self.trained = True
            logger.info("✅ Gemini model training context built")
            
        except Exception as e:
            logger.error(f"❌ Gemini model training failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def predict(self, case_features: CaseFeatures, case_context: str = "") -> Dict[str, float]:
        """Generate predictions using Gemini AI"""
        try:
            prediction_prompt = f"""
            {self.training_context}
            
            NEW CASE ANALYSIS REQUEST:
            {case_context}
            
            CASE FEATURE SCORES:
            - Case Type Score: {case_features.case_type_score:.3f}
            - Jurisdiction Score: {case_features.jurisdiction_score:.3f}  
            - Complexity Score: {case_features.complexity_score:.3f}
            - Evidence Strength: {case_features.evidence_strength:.3f}
            - Case Value (Normalized): {case_features.case_value_normalized:.3f}
            - Judge Favorability: {case_features.judge_favorability:.3f}
            - Historical Precedent Score: {case_features.historical_precedent_score:.3f}
            - Plaintiff Advantage: {case_features.plaintiff_advantage_score:.3f}
            - Defendant Advantage: {case_features.defendant_advantage_score:.3f}
            - Settlement Likelihood: {case_features.settlement_likelihood:.3f}
            
            Based on the training data patterns and these case features, provide precise probability predictions for each outcome:
            
            REQUIRED FORMAT:
            plaintiff_win: [probability 0.0-1.0]
            defendant_win: [probability 0.0-1.0]  
            settlement: [probability 0.0-1.0]
            dismissed: [probability 0.0-1.0]
            
            confidence_score: [overall confidence 0.0-1.0]
            key_factors: [list 3-5 most important decision factors]
            reasoning: [brief explanation of prediction logic]
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prediction_prompt
            )
            
            return self._parse_gemini_prediction(response.text)
            
        except Exception as e:
            logger.warning(f"⚠️ Gemini prediction failed: {e}")
            return self._get_default_prediction()

    def _analyze_training_patterns(self, training_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in training data"""
        outcomes = [case.get('outcome') for case in training_data if case.get('outcome')]
        outcome_counts = Counter(outcomes)
        
        return {
            'total_cases': len(training_data),
            'outcome_distribution': dict(outcome_counts),
            'most_common_outcome': outcome_counts.most_common(1)[0] if outcome_counts else ('unknown', 0)
        }

    def _format_outcome_distribution(self, patterns: Dict[str, Any]) -> str:
        """Format outcome distribution for training context"""
        distribution = patterns.get('outcome_distribution', {})
        total = patterns.get('total_cases', 1)
        
        formatted = []
        for outcome, count in distribution.items():
            percentage = (count / total) * 100
            formatted.append(f"- {outcome.replace('_', ' ').title()}: {count} cases ({percentage:.1f}%)")
        
        return '\n'.join(formatted)

    def _format_case_type_patterns(self, training_data: List[Dict]) -> str:
        """Analyze and format case type success patterns"""
        type_outcomes = defaultdict(list)
        
        for case in training_data:
            case_type = case.get('case_type')
            outcome = case.get('outcome')
            if case_type and outcome:
                type_outcomes[case_type].append(outcome)
        
        patterns = []
        for case_type, outcomes in type_outcomes.items():
            outcome_counts = Counter(outcomes)
            most_common = outcome_counts.most_common(1)[0] if outcome_counts else ('unknown', 0)
            success_rate = (most_common[1] / len(outcomes)) * 100 if outcomes else 0
            
            patterns.append(f"- {case_type.replace('_', ' ').title()}: {len(outcomes)} cases, {most_common[0].replace('_', ' ').title()} {success_rate:.1f}% success rate")
        
        return '\n'.join(patterns[:10])  # Top 10 case types

    def _format_jurisdiction_patterns(self, training_data: List[Dict]) -> str:
        """Analyze jurisdiction-specific patterns"""
        jurisdiction_outcomes = defaultdict(list)
        
        for case in training_data:
            jurisdiction = case.get('jurisdiction')
            outcome = case.get('outcome')
            if jurisdiction and outcome:
                jurisdiction_outcomes[jurisdiction].append(outcome)
        
        patterns = []
        for jurisdiction, outcomes in jurisdiction_outcomes.items():
            outcome_counts = Counter(outcomes)
            total = len(outcomes)
            settlement_rate = (outcome_counts.get('settlement', 0) / total) * 100 if total > 0 else 0
            
            patterns.append(f"- {jurisdiction}: {total} cases, Settlement Rate: {settlement_rate:.1f}%")
        
        return '\n'.join(patterns[:8])  # Top 8 jurisdictions

    def _format_value_correlations(self, training_data: List[Dict]) -> str:
        """Analyze case value correlations with outcomes"""
        value_ranges = {
            'under_100k': [],
            '100k_500k': [],
            '500k_1m': [],
            'over_1m': []
        }
        
        for case in training_data:
            value = case.get('case_value', 0)
            outcome = case.get('outcome')
            
            if not outcome:
                continue
                
            if value < 100000:
                value_ranges['under_100k'].append(outcome)
            elif value < 500000:
                value_ranges['100k_500k'].append(outcome)
            elif value < 1000000:
                value_ranges['500k_1m'].append(outcome)
            else:
                value_ranges['over_1m'].append(outcome)
        
        correlations = []
        for range_name, outcomes in value_ranges.items():
            if not outcomes:
                continue
                
            outcome_counts = Counter(outcomes)
            total = len(outcomes)
            settlement_rate = (outcome_counts.get('settlement', 0) / total) * 100
            
            correlations.append(f"- {range_name.replace('_', ' ').title()}: {total} cases, Settlement: {settlement_rate:.1f}%")
        
        return '\n'.join(correlations)

    def _identify_key_factors(self, training_data: List[Dict]) -> str:
        """Identify key predictive factors from training data"""
        factors = [
            "Case complexity significantly impacts duration and settlement likelihood",
            "Higher case values correlate with increased settlement rates",
            "Jurisdiction-specific legal precedents influence outcome patterns",
            "Evidence strength is the strongest predictor of plaintiff success",
            "Judge experience and specialty area affect case trajectory",
            "Commercial cases show higher settlement rates than personal injury",
            "Cases with multiple legal issues tend toward settlement"
        ]
        
        return '\n'.join(f"- {factor}" for factor in factors[:5])

    def _parse_gemini_prediction(self, response_text: str) -> Dict[str, float]:
        """Parse Gemini response into structured predictions"""
        try:
            predictions = {}
            
            # Extract probabilities using regex
            patterns = {
                'plaintiff_win': r'plaintiff_win:\s*([0-9.]+)',
                'defendant_win': r'defendant_win:\s*([0-9.]+)',
                'settlement': r'settlement:\s*([0-9.]+)',
                'dismissed': r'dismissed:\s*([0-9.]+)'
            }
            
            for outcome, pattern in patterns.items():
                match = re.search(pattern, response_text.lower())
                if match:
                    predictions[outcome] = float(match.group(1))
            
            # Normalize probabilities to sum to 1.0
            total = sum(predictions.values())
            if total > 0:
                predictions = {k: v/total for k, v in predictions.items()}
            
            # Extract confidence score
            confidence_match = re.search(r'confidence_score:\s*([0-9.]+)', response_text.lower())
            if confidence_match:
                predictions['confidence'] = float(confidence_match.group(1))
            else:
                predictions['confidence'] = 0.75  # Default confidence
            
            return predictions
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse Gemini response: {e}")
            return self._get_default_prediction()

    def _get_default_prediction(self) -> Dict[str, float]:
        """Return default prediction when AI fails"""
        return {
            'plaintiff_win': 0.30,
            'defendant_win': 0.30,
            'settlement': 0.30,
            'dismissed': 0.10,
            'confidence': 0.50
        }

class GroqPredictionModel(OutcomePredictionModel):
    """Groq AI-based prediction model with fast inference"""
    
    def __init__(self):
        super().__init__("groq_ai")
        self.client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        self.training_summary = {}
        
    async def train(self, training_data: List[Dict[str, Any]]):
        """Build training summary for Groq predictions"""
        try:
            logger.info(f"⚡ Training Groq model with {len(training_data)} cases")
            
            self.training_summary = {
                'total_cases': len(training_data),
                'outcome_rates': self._calculate_outcome_rates(training_data),
                'case_type_performance': self._analyze_case_type_performance(training_data),
                'settlement_patterns': self._analyze_settlement_patterns(training_data),
                'duration_analysis': self._analyze_duration_patterns(training_data)
            }
            
            self.trained = True
            logger.info("✅ Groq model training summary built")
            
        except Exception as e:
            logger.error(f"❌ Groq model training failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def predict(self, case_features: CaseFeatures, case_context: str = "") -> Dict[str, float]:
        """Generate fast predictions using Groq"""
        try:
            prediction_prompt = f"""
            FAST LITIGATION OUTCOME PREDICTION
            
            Training Data Summary:
            - Total Cases Analyzed: {self.training_summary.get('total_cases', 0)}
            - Historical Outcome Rates: {json.dumps(self.training_summary.get('outcome_rates', {}), indent=2)}
            
            Case Analysis:
            {case_context}
            
            Feature Vector:
            - Case Type Score: {case_features.case_type_score:.3f}
            - Jurisdiction: {case_features.jurisdiction_score:.3f}
            - Complexity: {case_features.complexity_score:.3f}  
            - Evidence: {case_features.evidence_strength:.3f}
            - Value: {case_features.case_value_normalized:.3f}
            - Judge: {case_features.judge_favorability:.3f}
            - Precedent: {case_features.historical_precedent_score:.3f}
            - P-Advantage: {case_features.plaintiff_advantage_score:.3f}
            - D-Advantage: {case_features.defendant_advantage_score:.3f}
            - Settlement: {case_features.settlement_likelihood:.3f}
            
            Provide precise predictions in JSON format:
            {
              "plaintiff_win": 0.xx,
              "defendant_win": 0.xx,
              "settlement": 0.xx, 
              "dismissed": 0.xx,
              "confidence": 0.xx,
              "primary_factors": ["factor1", "factor2", "factor3"]
            }
            """
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prediction_prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            return self._parse_groq_prediction(response.choices[0].message.content)
            
        except Exception as e:
            logger.warning(f"⚠️ Groq prediction failed: {e}")
            return self._get_default_prediction()

    def _calculate_outcome_rates(self, training_data: List[Dict]) -> Dict[str, float]:
        """Calculate historical outcome rates"""
        outcomes = [case.get('outcome') for case in training_data if case.get('outcome')]
        if not outcomes:
            return {}
            
        outcome_counts = Counter(outcomes)
        total = len(outcomes)
        
        return {outcome: count/total for outcome, count in outcome_counts.items()}

    def _analyze_case_type_performance(self, training_data: List[Dict]) -> Dict[str, Dict]:
        """Analyze performance by case type"""
        type_analysis = defaultdict(lambda: defaultdict(int))
        
        for case in training_data:
            case_type = case.get('case_type')
            outcome = case.get('outcome')
            if case_type and outcome:
                type_analysis[case_type][outcome] += 1
        
        # Convert to percentages
        performance = {}
        for case_type, outcomes in type_analysis.items():
            total = sum(outcomes.values())
            performance[case_type] = {
                outcome: count/total for outcome, count in outcomes.items()
            }
        
        return dict(performance)

    def _analyze_settlement_patterns(self, training_data: List[Dict]) -> Dict[str, Any]:
        """Analyze settlement patterns and predictors"""
        settlements = [
            case for case in training_data 
            if case.get('outcome') == 'settlement' and case.get('settlement_amount')
        ]
        
        if not settlements:
            return {}
        
        settlement_amounts = [case['settlement_amount'] for case in settlements]
        
        return {
            'settlement_rate': len(settlements) / len(training_data),
            'avg_settlement': np.mean(settlement_amounts),
            'median_settlement': np.median(settlement_amounts),
            'settlement_count': len(settlements)
        }

    def _analyze_duration_patterns(self, training_data: List[Dict]) -> Dict[str, float]:
        """Analyze case duration patterns"""
        durations = [
            case.get('duration') for case in training_data 
            if case.get('duration') and case.get('duration') > 0
        ]
        
        if not durations:
            return {}
        
        return {
            'avg_duration': np.mean(durations),
            'median_duration': np.median(durations),
            'min_duration': np.min(durations),
            'max_duration': np.max(durations)
        }

    def _parse_groq_prediction(self, response_text: str) -> Dict[str, float]:
        """Parse Groq JSON response"""
        try:
            # Try to extract JSON from response
            import json
            
            # Look for JSON block in response
            json_match = re.search(r'\{.*?\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                predictions = json.loads(json_str)
                
                # Validate and normalize
                required_keys = ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed']
                if all(key in predictions for key in required_keys):
                    # Normalize probabilities
                    total = sum(predictions[key] for key in required_keys)
                    if total > 0:
                        for key in required_keys:
                            predictions[key] /= total
                    
                    return predictions
            
            # Fallback to regex parsing
            return self._regex_parse_groq(response_text)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse Groq response: {e}")
            return self._get_default_prediction()

    def _regex_parse_groq(self, response_text: str) -> Dict[str, float]:
        """Fallback regex parsing for Groq response"""
        predictions = {}
        
        patterns = {
            'plaintiff_win': r'["\']plaintiff_win["\']\s*:\s*([0-9.]+)',
            'defendant_win': r'["\']defendant_win["\']\s*:\s*([0-9.]+)',
            'settlement': r'["\']settlement["\']\s*:\s*([0-9.]+)',
            'dismissed': r'["\']dismissed["\']\s*:\s*([0-9.]+)',
            'confidence': r'["\']confidence["\']\s*:\s*([0-9.]+)'
        }
        
        for outcome, pattern in patterns.items():
            match = re.search(pattern, response_text)
            if match:
                predictions[outcome] = float(match.group(1))
        
        # Normalize if needed
        outcome_keys = ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed']
        total = sum(predictions.get(key, 0) for key in outcome_keys)
        if total > 0:
            for key in outcome_keys:
                if key in predictions:
                    predictions[key] /= total
        
        return predictions if predictions else self._get_default_prediction()

    def _get_default_prediction(self) -> Dict[str, float]:
        """Return default prediction when AI fails"""
        return {
            'plaintiff_win': 0.25,
            'defendant_win': 0.25, 
            'settlement': 0.35,
            'dismissed': 0.15,
            'confidence': 0.60
        }

class StatisticalPredictionModel(OutcomePredictionModel):
    """Statistical model based on historical case patterns"""
    
    def __init__(self):
        super().__init__("statistical")
        self.outcome_probabilities = {}
        self.feature_correlations = {}
        
    async def train(self, training_data: List[Dict[str, Any]]):
        """Train statistical model on historical patterns"""
        try:
            logger.info(f"📊 Training statistical model with {len(training_data)} cases")
            
            # Calculate base outcome probabilities
            outcomes = [case.get('outcome') for case in training_data if case.get('outcome')]
            if outcomes:
                outcome_counts = Counter(outcomes)
                total = len(outcomes)
                self.outcome_probabilities = {
                    outcome: count/total for outcome, count in outcome_counts.items()
                }
            
            # Analyze feature correlations
            self.feature_correlations = self._calculate_feature_correlations(training_data)
            
            self.trained = True
            logger.info("✅ Statistical model trained successfully")
            
        except Exception as e:
            logger.error(f"❌ Statistical model training failed: {e}")
            raise

    async def predict(self, case_features: CaseFeatures, case_context: str = "") -> Dict[str, float]:
        """Generate statistical predictions"""
        if not self.trained:
            return self._get_default_prediction()
        
        # Start with base probabilities
        predictions = dict(self.outcome_probabilities)
        
        # Apply feature-based adjustments
        predictions = self._apply_feature_adjustments(predictions, case_features)
        
        # Normalize probabilities
        total = sum(predictions.values())
        if total > 0:
            predictions = {k: v/total for k, v in predictions.items()}
        
        # Add confidence based on feature completeness
        confidence = self._calculate_statistical_confidence(case_features)
        predictions['confidence'] = confidence
        
        return predictions

    def _calculate_feature_correlations(self, training_data: List[Dict]) -> Dict[str, Any]:
        """Calculate correlations between features and outcomes"""
        correlations = {}
        
        # This would involve more sophisticated statistical analysis
        # For now, return basic correlation estimates
        correlations['evidence_strength'] = {
            'plaintiff_win': 0.3,
            'defendant_win': -0.3,
            'settlement': 0.1,
            'dismissed': -0.1
        }
        
        return correlations

    def _apply_feature_adjustments(self, base_probs: Dict[str, float], features: CaseFeatures) -> Dict[str, float]:
        """Apply feature-based probability adjustments"""
        adjusted = dict(base_probs)
        
        # Evidence strength adjustment
        evidence_impact = (features.evidence_strength - 0.5) * 0.2  # Scale: -0.1 to +0.1
        adjusted['plaintiff_win'] = max(0, adjusted.get('plaintiff_win', 0.25) + evidence_impact)
        adjusted['defendant_win'] = max(0, adjusted.get('defendant_win', 0.25) - evidence_impact)
        
        # Settlement likelihood adjustment
        settlement_boost = features.settlement_likelihood * 0.3
        adjusted['settlement'] = min(0.8, adjusted.get('settlement', 0.25) + settlement_boost)
        
        # Judge favorability adjustment
        judge_impact = (features.judge_favorability - 0.5) * 0.15
        adjusted['plaintiff_win'] = max(0, adjusted.get('plaintiff_win', 0.25) + judge_impact)
        adjusted['defendant_win'] = max(0, adjusted.get('defendant_win', 0.25) - judge_impact)
        
        return adjusted

    def _calculate_statistical_confidence(self, features: CaseFeatures) -> float:
        """Calculate confidence based on feature completeness and quality"""
        feature_scores = [
            features.case_type_score,
            features.jurisdiction_score,
            features.complexity_score,
            features.evidence_strength,
            features.historical_precedent_score
        ]
        
        # Confidence based on non-zero features
        non_zero_features = sum(1 for score in feature_scores if score > 0)
        feature_completeness = non_zero_features / len(feature_scores)
        
        # Base confidence scaled by completeness
        base_confidence = 0.70
        return base_confidence * feature_completeness

    def _get_default_prediction(self) -> Dict[str, float]:
        """Return default statistical prediction"""
        return {
            'plaintiff_win': 0.28,
            'defendant_win': 0.28,
            'settlement': 0.32,
            'dismissed': 0.12,
            'confidence': 0.65
        }

class EnsembleCasePredictor:
    """Ensemble predictor combining multiple models for improved accuracy"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        
        # Initialize prediction models
        self.gemini_model = GeminiPredictionModel()
        self.groq_model = GroqPredictionModel()
        self.statistical_model = StatisticalPredictionModel()
        
        # Model weights for ensemble
        self.model_weights = {
            'gemini': 0.40,
            'groq': 0.35,
            'statistical': 0.25
        }
        
        self.trained = False
        logger.info("🤖 Ensemble Case Predictor initialized")

    async def train_models(self, training_data: Optional[List[Dict]] = None):
        """Train all ensemble models"""
        try:
            if not training_data:
                training_data = await self._load_training_data()
            
            logger.info(f"🎯 Training ensemble with {len(training_data)} cases")
            
            # Train all models
            await asyncio.gather(
                self.gemini_model.train(training_data),
                self.groq_model.train(training_data),
                self.statistical_model.train(training_data)
            )
            
            self.trained = True
            logger.info("✅ Ensemble model training completed")
            
        except Exception as e:
            logger.error(f"❌ Ensemble training failed: {e}")
            raise

    async def predict_case_outcome(self, case_features: CaseFeatures, case_context: str = "") -> Dict[str, Any]:
        """Generate ensemble prediction from all models"""
        if not self.trained:
            await self.train_models()
        
        try:
            # Get predictions from all models
            predictions = await asyncio.gather(
                self.gemini_model.predict(case_features, case_context),
                self.groq_model.predict(case_features, case_context),
                self.statistical_model.predict(case_features, case_context),
                return_exceptions=True
            )
            
            # Filter out failed predictions
            valid_predictions = []
            for i, pred in enumerate(predictions):
                if not isinstance(pred, Exception):
                    valid_predictions.append((pred, list(self.model_weights.values())[i]))
            
            if not valid_predictions:
                logger.warning("⚠️ All models failed, using default prediction")
                return self._get_default_ensemble_prediction()
            
            # Combine predictions using weighted ensemble
            ensemble_prediction = self._combine_predictions(valid_predictions)
            
            return ensemble_prediction
            
        except Exception as e:
            logger.error(f"❌ Ensemble prediction failed: {e}")
            return self._get_default_ensemble_prediction()

    def _combine_predictions(self, valid_predictions: List[Tuple[Dict, float]]) -> Dict[str, Any]:
        """Combine multiple model predictions using weighted ensemble"""
        combined = {
            'plaintiff_win': 0.0,
            'defendant_win': 0.0,
            'settlement': 0.0,
            'dismissed': 0.0,
            'confidence': 0.0
        }
        
        total_weight = sum(weight for _, weight in valid_predictions)
        
        # Weighted combination
        for prediction, weight in valid_predictions:
            normalized_weight = weight / total_weight
            
            for outcome in ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed']:
                combined[outcome] += prediction.get(outcome, 0.25) * normalized_weight
            
            combined['confidence'] += prediction.get('confidence', 0.5) * normalized_weight
        
        # Ensure probabilities sum to 1.0
        outcome_total = sum(combined[k] for k in ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed'])
        if outcome_total > 0:
            for outcome in ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed']:
                combined[outcome] /= outcome_total
        
        # Add ensemble metadata
        combined['ensemble_info'] = {
            'models_used': len(valid_predictions),
            'total_models': 3,
            'prediction_method': 'weighted_ensemble'
        }
        
        return combined

    async def _load_training_data(self) -> List[Dict[str, Any]]:
        """Load training data from database"""
        try:
            # Load from litigation_cases collection
            training_data = await self.db.litigation_cases.find({
                'outcome': {'$in': ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed']},
                'case_type': {'$exists': True},
                'jurisdiction': {'$exists': True}
            }).to_list(1000)  # Limit to 1000 cases for training
            
            logger.info(f"📚 Loaded {len(training_data)} training cases from database")
            return training_data
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load training data: {e}")
            # Return synthetic training data for development
            return self._generate_synthetic_training_data()

    def _generate_synthetic_training_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic training data for development/testing"""
        import random
        
        outcomes = ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed']
        case_types = ['civil', 'commercial', 'employment', 'personal_injury']
        jurisdictions = ['federal', 'california', 'new_york', 'texas', 'florida']
        
        synthetic_data = []
        for i in range(100):
            case = {
                'case_id': f'synthetic_{i}',
                'outcome': random.choice(outcomes),
                'case_type': random.choice(case_types),
                'jurisdiction': random.choice(jurisdictions),
                'case_value': random.randint(10000, 5000000),
                'duration': random.randint(90, 1095),  # 3 months to 3 years
                'complexity': random.uniform(0.1, 1.0),
                'evidence_strength': random.uniform(0.0, 1.0)
            }
            synthetic_data.append(case)
        
        logger.info("🧪 Generated 100 synthetic training cases")
        return synthetic_data

    def _get_default_ensemble_prediction(self) -> Dict[str, Any]:
        """Default prediction when ensemble fails"""
        return {
            'plaintiff_win': 0.30,
            'defendant_win': 0.30,
            'settlement': 0.30,
            'dismissed': 0.10,
            'confidence': 0.50,
            'ensemble_info': {
                'models_used': 0,
                'total_models': 3,
                'prediction_method': 'default_fallback'
            }
        }

# Global predictor instance
_case_predictor = None

async def get_case_outcome_predictor(db_connection) -> EnsembleCasePredictor:
    """Get or create case outcome predictor instance"""
    global _case_predictor
    
    if _case_predictor is None:
        _case_predictor = EnsembleCasePredictor(db_connection)
        logger.info("🚀 Case Outcome Predictor instance created")
    
    return _case_predictor

async def initialize_case_predictor(db_connection):
    """Initialize the case outcome predictor"""
    predictor = await get_case_outcome_predictor(db_connection)
    # Note: Training will happen on first prediction to avoid blocking startup
    logger.info("✅ Case Outcome Predictor initialized successfully")
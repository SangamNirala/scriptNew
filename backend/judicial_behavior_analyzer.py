"""
Judicial Behavior Analyzer Module

Analyzes judicial decision patterns, behavior tendencies, and provides insights
for litigation strategy using AI-powered analysis of historical judicial decisions.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json
import re
import numpy as np
import google.generativeai as genai
from groq import Groq
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class JudgeSpecialty(Enum):
    COMMERCIAL_LAW = "commercial_law"
    INTELLECTUAL_PROPERTY = "intellectual_property" 
    EMPLOYMENT_LAW = "employment_law"
    PERSONAL_INJURY = "personal_injury"
    CRIMINAL_LAW = "criminal_law"
    FAMILY_LAW = "family_law"
    BANKRUPTCY = "bankruptcy"
    TAX_LAW = "tax_law"
    ENVIRONMENTAL = "environmental"
    CONSTITUTIONAL = "constitutional"
    GENERAL = "general"

class DecisionTendency(Enum):
    PLAINTIFF_FAVORABLE = "plaintiff_favorable"
    DEFENDANT_FAVORABLE = "defendant_favorable"
    SETTLEMENT_ENCOURAGING = "settlement_encouraging"
    PROCEDURE_STRICT = "procedure_strict"
    EVIDENCE_FOCUSED = "evidence_focused"
    NEUTRAL = "neutral"

@dataclass
class JudicialMetrics:
    """Comprehensive metrics for judicial behavior analysis"""
    total_cases: int = 0
    cases_last_year: int = 0
    average_case_duration: float = 0.0
    median_case_duration: float = 0.0
    settlement_rate: float = 0.0
    appeal_rate: float = 0.0
    reversal_rate: float = 0.0
    plaintiff_success_rate: float = 0.0
    defendant_success_rate: float = 0.0
    motion_grant_rate: float = 0.0
    summary_judgment_rate: float = 0.0
    continuance_grant_rate: float = 0.0
    
@dataclass
class JudicialPattern:
    """Pattern analysis for specific case types or legal issues"""
    pattern_type: str
    case_count: int
    success_rate: float
    average_duration: float
    settlement_preference: float
    confidence_score: float
    notable_tendencies: List[str] = field(default_factory=list)

@dataclass
class JudicialProfile:
    """Comprehensive judicial profile"""
    judge_name: str
    court: str
    appointment_date: Optional[datetime] = None
    judicial_experience: float = 0.0  # years
    primary_specialties: List[JudgeSpecialty] = field(default_factory=list)
    decision_tendencies: List[DecisionTendency] = field(default_factory=list)
    metrics: JudicialMetrics = field(default_factory=JudicialMetrics)
    case_type_patterns: Dict[str, JudicialPattern] = field(default_factory=dict)
    recent_trends: Dict[str, Any] = field(default_factory=dict)
    notable_decisions: List[Dict[str, Any]] = field(default_factory=list)
    ai_analysis_summary: str = ""
    last_updated: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0

class JudicialBehaviorAnalyzer:
    """Main analyzer for judicial behavior and decision patterns"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        
        # CourtListener client for judicial data
        self.courtlistener_client = httpx.AsyncClient(
            base_url="https://www.courtlistener.com/api/rest/v3",
            headers={"Authorization": f"Token {os.environ.get('COURTLISTENER_API_KEY')}"}
        )
        
        logger.info("⚖️ Judicial Behavior Analyzer initialized")

    async def analyze_judge(self, judge_name: str, force_refresh: bool = False) -> JudicialProfile:
        """Comprehensive analysis of a specific judge's behavior patterns"""
        try:
            logger.info(f"⚖️ Analyzing judicial behavior for Judge {judge_name}")
            
            # Check for cached analysis
            if not force_refresh:
                cached_profile = await self._get_cached_profile(judge_name)
                if cached_profile:
                    logger.info(f"📄 Using cached profile for Judge {judge_name}")
                    return cached_profile
            
            # Collect judicial data
            judicial_data = await self._collect_judicial_data(judge_name)
            
            if not judicial_data:
                logger.warning(f"⚠️ No judicial data found for Judge {judge_name}")
                return self._create_default_profile(judge_name)
            
            # Analyze patterns and generate profile
            profile = await self._generate_judicial_profile(judge_name, judicial_data)
            
            # Cache the analysis
            await self._cache_judicial_profile(profile)
            
            logger.info(f"✅ Judicial analysis completed for Judge {judge_name}")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Judicial analysis failed for {judge_name}: {e}")
            return self._create_default_profile(judge_name)

    async def get_judge_insights_for_case(self, judge_name: str, case_type: str, case_value: Optional[float] = None) -> Dict[str, Any]:
        """Get specific insights for a judge in context of a particular case type"""
        try:
            profile = await self.analyze_judge(judge_name)
            
            # Get case-specific insights
            case_pattern = profile.case_type_patterns.get(case_type)
            
            insights = {
                'judge_name': judge_name,
                'court': profile.court,
                'experience_years': profile.judicial_experience,
                'overall_metrics': {
                    'total_cases': profile.metrics.total_cases,
                    'settlement_rate': profile.metrics.settlement_rate,
                    'plaintiff_success_rate': profile.metrics.plaintiff_success_rate,
                    'average_case_duration': profile.metrics.average_case_duration
                },
                'case_specific_insights': {},
                'strategic_recommendations': [],
                'confidence_score': profile.confidence_score
            }
            
            # Add case-specific patterns if available
            if case_pattern:
                insights['case_specific_insights'] = {
                    'case_type': case_type,
                    'case_count': case_pattern.case_count,
                    'success_rate': case_pattern.success_rate,
                    'average_duration': case_pattern.average_duration,
                    'settlement_preference': case_pattern.settlement_preference,
                    'notable_tendencies': case_pattern.notable_tendencies
                }
            
            # Generate strategic recommendations
            insights['strategic_recommendations'] = self._generate_strategic_recommendations(
                profile, case_type, case_value
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to get judge insights: {e}")
            return self._get_default_insights(judge_name)

    async def compare_judges(self, judge_names: List[str], case_type: Optional[str] = None) -> Dict[str, Any]:
        """Compare multiple judges for litigation strategy"""
        try:
            logger.info(f"⚖️ Comparing {len(judge_names)} judges")
            
            # Analyze all judges
            profiles = await asyncio.gather(
                *[self.analyze_judge(judge) for judge in judge_names],
                return_exceptions=True
            )
            
            # Filter out failed analyses
            valid_profiles = []
            for i, profile in enumerate(profiles):
                if not isinstance(profile, Exception):
                    valid_profiles.append(profile)
                else:
                    logger.warning(f"⚠️ Failed to analyze Judge {judge_names[i]}")
            
            if not valid_profiles:
                return {'error': 'No valid judge profiles found'}
            
            # Generate comparison analysis
            comparison = self._generate_judge_comparison(valid_profiles, case_type)
            
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Judge comparison failed: {e}")
            return {'error': str(e)}

    async def _collect_judicial_data(self, judge_name: str) -> List[Dict[str, Any]]:
        """Collect comprehensive judicial data from multiple sources"""
        try:
            # Try database first
            db_data = await self._get_judge_data_from_db(judge_name)
            
            if db_data and len(db_data) > 10:  # Sufficient data in DB
                return db_data
            
            # Fetch from CourtListener if needed
            courtlistener_data = await self._fetch_courtlistener_data(judge_name)
            
            # Combine data sources
            combined_data = db_data + courtlistener_data
            
            # Store new data in database for future use
            if courtlistener_data:
                await self._store_judicial_data(judge_name, courtlistener_data)
            
            return combined_data
            
        except Exception as e:
            logger.warning(f"⚠️ Data collection failed for {judge_name}: {e}")
            return []

    async def _get_judge_data_from_db(self, judge_name: str) -> List[Dict[str, Any]]:
        """Get existing judge data from database"""
        try:
            cases = await self.db.litigation_cases.find({
                'judge_name': {'$regex': judge_name, '$options': 'i'}
            }).to_list(500)  # Limit to 500 cases
            
            return cases
            
        except Exception as e:
            logger.warning(f"⚠️ DB query failed for {judge_name}: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch_courtlistener_data(self, judge_name: str) -> List[Dict[str, Any]]:
        """Fetch judge data from CourtListener API"""
        try:
            logger.info(f"🌐 Fetching CourtListener data for Judge {judge_name}")
            
            # Search for opinions by this judge
            response = await self.courtlistener_client.get(
                "/opinions/",
                params={
                    'judge': judge_name,
                    'per_page': 100,
                    'order_by': '-date_created'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                opinions = data.get('results', [])
                
                # Convert to standardized format
                judicial_data = []
                for opinion in opinions[:50]:  # Limit to 50 most recent
                    case_data = self._convert_courtlistener_opinion(opinion)
                    if case_data:
                        judicial_data.append(case_data)
                
                logger.info(f"📊 Retrieved {len(judicial_data)} cases for Judge {judge_name}")
                return judicial_data
            
            return []
            
        except Exception as e:
            logger.warning(f"⚠️ CourtListener fetch failed: {e}")
            return []

    def _convert_courtlistener_opinion(self, opinion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Convert CourtListener opinion to standardized case data"""
        try:
            case_data = {
                'case_id': f"cl_{opinion.get('id', 'unknown')}",
                'source': 'courtlistener',
                'judge_name': opinion.get('author_str', ''),
                'court': opinion.get('cluster', {}).get('docket', {}).get('court', ''),
                'case_type': self._infer_case_type(opinion.get('html', '')),
                'decision_date': opinion.get('date_created'),
                'citation': opinion.get('cluster', {}).get('citation_id'),
                'case_name': opinion.get('cluster', {}).get('case_name', ''),
                'disposition': self._extract_disposition(opinion.get('html', '')),
                'opinion_text': opinion.get('plain_text', ''),
                'case_nature': opinion.get('cluster', {}).get('nature_of_suit', '')
            }
            
            return case_data
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to convert opinion data: {e}")
            return None

    def _infer_case_type(self, opinion_text: str) -> str:
        """Infer case type from opinion text"""
        text_lower = opinion_text.lower()
        
        if any(term in text_lower for term in ['contract', 'breach', 'agreement', 'commercial']):
            return 'commercial'
        elif any(term in text_lower for term in ['employment', 'discrimination', 'wrongful termination']):
            return 'employment'
        elif any(term in text_lower for term in ['patent', 'trademark', 'copyright', 'intellectual property']):
            return 'intellectual_property'
        elif any(term in text_lower for term in ['personal injury', 'negligence', 'tort']):
            return 'personal_injury'
        elif any(term in text_lower for term in ['criminal', 'prosecution', 'defendant']):
            return 'criminal'
        else:
            return 'civil'

    def _extract_disposition(self, opinion_text: str) -> str:
        """Extract case disposition from opinion text"""
        text_lower = opinion_text.lower()
        
        if any(term in text_lower for term in ['affirmed', 'affirm']):
            return 'affirmed'
        elif any(term in text_lower for term in ['reversed', 'reverse']):
            return 'reversed'
        elif any(term in text_lower for term in ['remanded', 'remand']):
            return 'remanded'
        elif any(term in text_lower for term in ['granted', 'motion granted']):
            return 'granted'
        elif any(term in text_lower for term in ['denied', 'motion denied']):
            return 'denied'
        else:
            return 'unknown'

    async def _generate_judicial_profile(self, judge_name: str, judicial_data: List[Dict]) -> JudicialProfile:
        """Generate comprehensive judicial profile from collected data"""
        try:
            # Calculate basic metrics
            metrics = self._calculate_judicial_metrics(judicial_data)
            
            # Analyze case type patterns
            case_patterns = self._analyze_case_type_patterns(judicial_data)
            
            # Determine specialties and tendencies
            specialties = self._determine_specialties(judicial_data, case_patterns)
            tendencies = self._analyze_decision_tendencies(judicial_data)
            
            # Get AI analysis
            ai_summary = await self._get_ai_judicial_analysis(judge_name, judicial_data, metrics)
            
            # Calculate experience (estimate from case dates)
            experience_years = self._estimate_judicial_experience(judicial_data)
            
            # Determine court
            court = self._determine_primary_court(judicial_data)
            
            profile = JudicialProfile(
                judge_name=judge_name,
                court=court,
                judicial_experience=experience_years,
                primary_specialties=specialties,
                decision_tendencies=tendencies,
                metrics=metrics,
                case_type_patterns=case_patterns,
                ai_analysis_summary=ai_summary,
                confidence_score=self._calculate_profile_confidence(judicial_data),
                last_updated=datetime.utcnow()
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Profile generation failed: {e}")
            return self._create_default_profile(judge_name)

    def _calculate_judicial_metrics(self, judicial_data: List[Dict]) -> JudicialMetrics:
        """Calculate comprehensive judicial metrics"""
        if not judicial_data:
            return JudicialMetrics()
        
        total_cases = len(judicial_data)
        
        # Filter recent cases (last year)
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        recent_cases = [
            case for case in judicial_data
            if case.get('decision_date') and 
            (isinstance(case['decision_date'], datetime) and case['decision_date'] > one_year_ago or
             isinstance(case['decision_date'], str) and datetime.fromisoformat(case['decision_date'].replace('Z', '+00:00')) > one_year_ago)
        ]
        
        # Calculate dispositions
        dispositions = [case.get('disposition', 'unknown') for case in judicial_data]
        disposition_counts = Counter(dispositions)
        
        # Calculate settlement rate (cases that settled)
        settlements = sum(1 for case in judicial_data if case.get('outcome') == 'settlement')
        settlement_rate = settlements / total_cases if total_cases > 0 else 0.0
        
        # Calculate plaintiff success rate
        plaintiff_wins = sum(1 for case in judicial_data if case.get('outcome') == 'plaintiff_win')
        plaintiff_success_rate = plaintiff_wins / total_cases if total_cases > 0 else 0.0
        
        # Calculate defendant success rate
        defendant_wins = sum(1 for case in judicial_data if case.get('outcome') == 'defendant_win')
        defendant_success_rate = defendant_wins / total_cases if total_cases > 0 else 0.0
        
        # Calculate appeal and reversal rates (simplified)
        appeals = sum(1 for case in judicial_data if 'appeal' in case.get('disposition', '').lower())
        appeal_rate = appeals / total_cases if total_cases > 0 else 0.0
        
        reversals = disposition_counts.get('reversed', 0)
        reversal_rate = reversals / total_cases if total_cases > 0 else 0.0
        
        # Calculate motion grant rates
        granted_motions = disposition_counts.get('granted', 0)
        motion_grant_rate = granted_motions / total_cases if total_cases > 0 else 0.0
        
        return JudicialMetrics(
            total_cases=total_cases,
            cases_last_year=len(recent_cases),
            settlement_rate=settlement_rate,
            appeal_rate=appeal_rate,
            reversal_rate=reversal_rate,
            plaintiff_success_rate=plaintiff_success_rate,
            defendant_success_rate=defendant_success_rate,
            motion_grant_rate=motion_grant_rate
        )

    def _analyze_case_type_patterns(self, judicial_data: List[Dict]) -> Dict[str, JudicialPattern]:
        """Analyze patterns by case type"""
        patterns = {}
        
        # Group cases by type
        cases_by_type = defaultdict(list)
        for case in judicial_data:
            case_type = case.get('case_type', 'unknown')
            cases_by_type[case_type].append(case)
        
        # Analyze each case type
        for case_type, cases in cases_by_type.items():
            if len(cases) < 3:  # Need minimum cases for pattern analysis
                continue
            
            # Calculate success rate for this case type
            wins = sum(1 for case in cases if case.get('outcome') in ['plaintiff_win', 'granted'])
            success_rate = wins / len(cases) if cases else 0.0
            
            # Calculate average duration if available
            durations = [case.get('duration', 365) for case in cases if case.get('duration')]
            avg_duration = np.mean(durations) if durations else 365.0
            
            # Calculate settlement preference
            settlements = sum(1 for case in cases if case.get('outcome') == 'settlement')
            settlement_preference = settlements / len(cases) if cases else 0.0
            
            # Identify notable tendencies
            tendencies = []
            if success_rate > 0.7:
                tendencies.append("High success rate for this case type")
            if settlement_preference > 0.4:
                tendencies.append("Strong preference for settlement")
            if avg_duration < 180:
                tendencies.append("Tends to resolve cases quickly")
            
            patterns[case_type] = JudicialPattern(
                pattern_type=case_type,
                case_count=len(cases),
                success_rate=success_rate,
                average_duration=avg_duration,
                settlement_preference=settlement_preference,
                confidence_score=min(len(cases) / 10, 1.0),  # Confidence based on sample size
                notable_tendencies=tendencies
            )
        
        return patterns

    def _determine_specialties(self, judicial_data: List[Dict], case_patterns: Dict[str, JudicialPattern]) -> List[JudgeSpecialty]:
        """Determine judge's primary specialties"""
        specialties = []
        
        # Count cases by type
        type_counts = Counter(case.get('case_type', 'unknown') for case in judicial_data)
        
        # Determine specialties based on case volume and expertise indicators
        for case_type, count in type_counts.most_common(3):  # Top 3 case types
            if count >= 5:  # Minimum threshold
                try:
                    specialty = JudgeSpecialty(case_type)
                    specialties.append(specialty)
                except ValueError:
                    # Case type doesn't map to a specialty enum
                    continue
        
        # Default to general if no specific specialties identified
        if not specialties:
            specialties.append(JudgeSpecialty.GENERAL)
        
        return specialties

    def _analyze_decision_tendencies(self, judicial_data: List[Dict]) -> List[DecisionTendency]:
        """Analyze judge's decision-making tendencies"""
        tendencies = []
        
        if not judicial_data:
            return [DecisionTendency.NEUTRAL]
        
        # Analyze outcome patterns
        outcomes = [case.get('outcome') for case in judicial_data if case.get('outcome')]
        outcome_counts = Counter(outcomes)
        total_outcomes = len(outcomes)
        
        if total_outcomes > 0:
            plaintiff_rate = outcome_counts.get('plaintiff_win', 0) / total_outcomes
            defendant_rate = outcome_counts.get('defendant_win', 0) / total_outcomes
            settlement_rate = outcome_counts.get('settlement', 0) / total_outcomes
            
            # Determine tendencies based on rates
            if plaintiff_rate > 0.6:
                tendencies.append(DecisionTendency.PLAINTIFF_FAVORABLE)
            elif defendant_rate > 0.6:
                tendencies.append(DecisionTendency.DEFENDANT_FAVORABLE)
            
            if settlement_rate > 0.4:
                tendencies.append(DecisionTendency.SETTLEMENT_ENCOURAGING)
        
        # Default to neutral if no clear tendencies
        if not tendencies:
            tendencies.append(DecisionTendency.NEUTRAL)
        
        return tendencies

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _get_ai_judicial_analysis(self, judge_name: str, judicial_data: List[Dict], metrics: JudicialMetrics) -> str:
        """Get AI-powered analysis of judicial behavior"""
        try:
            analysis_prompt = f"""
            JUDICIAL BEHAVIOR ANALYSIS FOR JUDGE {judge_name}
            
            CASE DATA SUMMARY:
            - Total Cases Analyzed: {len(judicial_data)}
            - Settlement Rate: {metrics.settlement_rate:.1%}
            - Plaintiff Success Rate: {metrics.plaintiff_success_rate:.1%}
            - Defendant Success Rate: {metrics.defendant_success_rate:.1%}
            - Appeal Rate: {metrics.appeal_rate:.1%}
            - Motion Grant Rate: {metrics.motion_grant_rate:.1%}
            
            RECENT CASE TYPES:
            {self._format_case_types_for_ai(judicial_data)}
            
            DISPOSITION PATTERNS:
            {self._format_dispositions_for_ai(judicial_data)}
            
            Please provide a comprehensive analysis of this judge's:
            1. Decision-making patterns and tendencies
            2. Strengths and preferences in different case types
            3. Notable characteristics for litigation strategy
            4. Recommendations for attorneys appearing before this judge
            5. Overall judicial philosophy and approach
            
            Focus on practical insights that would be valuable for litigation planning.
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                analysis_prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.warning(f"⚠️ AI analysis failed: {e}")
            return f"Judge {judge_name} has presided over {len(judicial_data)} cases with a {metrics.settlement_rate:.1%} settlement rate. Further analysis pending."

    def _format_case_types_for_ai(self, judicial_data: List[Dict]) -> str:
        """Format case type data for AI analysis"""
        type_counts = Counter(case.get('case_type', 'unknown') for case in judicial_data)
        
        formatted = []
        for case_type, count in type_counts.most_common(5):
            formatted.append(f"- {case_type.replace('_', ' ').title()}: {count} cases")
        
        return '\n'.join(formatted)

    def _format_dispositions_for_ai(self, judicial_data: List[Dict]) -> str:
        """Format disposition data for AI analysis"""
        dispositions = Counter(case.get('disposition', 'unknown') for case in judicial_data)
        
        formatted = []
        for disposition, count in dispositions.most_common(5):
            formatted.append(f"- {disposition.replace('_', ' ').title()}: {count}")
        
        return '\n'.join(formatted)

    def _estimate_judicial_experience(self, judicial_data: List[Dict]) -> float:
        """Estimate years of judicial experience from case data"""
        try:
            dates = []
            for case in judicial_data:
                date_str = case.get('decision_date')
                if date_str:
                    if isinstance(date_str, str):
                        try:
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            dates.append(date_obj)
                        except:
                            continue
                    elif isinstance(date_str, datetime):
                        dates.append(date_str)
            
            if dates:
                earliest = min(dates)
                years = (datetime.utcnow() - earliest).days / 365.25
                return max(0, years)
            
            return 5.0  # Default estimate
            
        except Exception as e:
            logger.warning(f"⚠️ Experience estimation failed: {e}")
            return 5.0

    def _determine_primary_court(self, judicial_data: List[Dict]) -> str:
        """Determine judge's primary court"""
        courts = [case.get('court', '') for case in judicial_data if case.get('court')]
        if courts:
            court_counts = Counter(courts)
            return court_counts.most_common(1)[0][0]
        return "Unknown Court"

    def _calculate_profile_confidence(self, judicial_data: List[Dict]) -> float:
        """Calculate confidence score for the judicial profile"""
        if not judicial_data:
            return 0.0
        
        # Base confidence on data quantity and quality
        data_quantity_score = min(len(judicial_data) / 50, 1.0)  # Optimal at 50+ cases
        
        # Quality indicators
        quality_indicators = 0
        total_indicators = 4
        
        if any(case.get('outcome') for case in judicial_data):
            quality_indicators += 1
        if any(case.get('case_type') for case in judicial_data):
            quality_indicators += 1
        if any(case.get('decision_date') for case in judicial_data):
            quality_indicators += 1
        if any(case.get('disposition') for case in judicial_data):
            quality_indicators += 1
        
        quality_score = quality_indicators / total_indicators
        
        # Combined confidence score
        confidence = (data_quantity_score * 0.6) + (quality_score * 0.4)
        
        return confidence

    def _generate_strategic_recommendations(self, profile: JudicialProfile, case_type: str, case_value: Optional[float]) -> List[str]:
        """Generate strategic recommendations based on judicial profile"""
        recommendations = []
        
        # Experience-based recommendations
        if profile.judicial_experience > 15:
            recommendations.append("Judge has extensive experience - prepare for thorough case examination")
        elif profile.judicial_experience < 5:
            recommendations.append("Relatively new judge - consider providing clear legal precedent citations")
        
        # Settlement tendency recommendations
        if profile.metrics.settlement_rate > 0.4:
            recommendations.append("Judge shows strong settlement preference - prepare compelling settlement terms")
        
        # Case type specific recommendations
        if case_type in profile.case_type_patterns:
            pattern = profile.case_type_patterns[case_type]
            if pattern.success_rate > 0.7:
                recommendations.append(f"Judge has high success rate ({pattern.success_rate:.1%}) in {case_type} cases")
            if pattern.settlement_preference > 0.5:
                recommendations.append("Judge typically encourages settlement in this case type")
        
        # Motion practice recommendations
        if profile.metrics.motion_grant_rate > 0.6:
            recommendations.append("Judge tends to grant motions - file strategically important motions")
        elif profile.metrics.motion_grant_rate < 0.3:
            recommendations.append("Judge is conservative with motion grants - ensure motions are well-supported")
        
        # Default recommendations if none generated
        if not recommendations:
            recommendations = [
                "Prepare thoroughly documented legal arguments",
                "Consider settlement discussions early in the process",
                "Ensure all procedural requirements are met"
            ]
        
        return recommendations[:5]  # Return top 5 recommendations

    def _generate_judge_comparison(self, profiles: List[JudicialProfile], case_type: Optional[str]) -> Dict[str, Any]:
        """Generate comparative analysis of multiple judges"""
        comparison = {
            'judges_compared': len(profiles),
            'case_type_focus': case_type,
            'comparative_metrics': {},
            'recommendations': {}
        }
        
        # Compare key metrics
        metrics_comparison = {
            'settlement_rates': {},
            'plaintiff_success_rates': {},
            'average_case_durations': {},
            'motion_grant_rates': {}
        }
        
        for profile in profiles:
            judge_name = profile.judge_name
            metrics_comparison['settlement_rates'][judge_name] = profile.metrics.settlement_rate
            metrics_comparison['plaintiff_success_rates'][judge_name] = profile.metrics.plaintiff_success_rate
            metrics_comparison['motion_grant_rates'][judge_name] = profile.metrics.motion_grant_rate
            
            # Case-specific metrics if available
            if case_type and case_type in profile.case_type_patterns:
                pattern = profile.case_type_patterns[case_type]
                metrics_comparison[f'{case_type}_success_rates'] = metrics_comparison.get(f'{case_type}_success_rates', {})
                metrics_comparison[f'{case_type}_success_rates'][judge_name] = pattern.success_rate
        
        comparison['comparative_metrics'] = metrics_comparison
        
        # Generate recommendations for judge selection
        best_settlement = max(profiles, key=lambda p: p.metrics.settlement_rate)
        best_plaintiff = max(profiles, key=lambda p: p.metrics.plaintiff_success_rate)
        fastest_resolution = min(profiles, key=lambda p: p.metrics.average_case_duration or 365)
        
        comparison['recommendations'] = {
            'best_for_settlement': best_settlement.judge_name,
            'best_for_plaintiff': best_plaintiff.judge_name,
            'fastest_resolution': fastest_resolution.judge_name
        }
        
        return comparison

    async def _get_cached_profile(self, judge_name: str) -> Optional[JudicialProfile]:
        """Get cached judicial profile if recent enough"""
        try:
            cached = await self.db.judicial_decisions.find_one({
                'judge_name': judge_name,
                'last_updated': {'$gt': datetime.utcnow() - timedelta(days=30)}  # 30 day cache
            })
            
            if cached:
                # Convert to JudicialProfile object
                return self._dict_to_profile(cached)
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Cache retrieval failed: {e}")
            return None

    async def _cache_judicial_profile(self, profile: JudicialProfile):
        """Cache judicial profile for future use"""
        try:
            profile_dict = self._profile_to_dict(profile)
            
            await self.db.judicial_decisions.update_one(
                {'judge_name': profile.judge_name},
                {'$set': profile_dict},
                upsert=True
            )
            
            logger.info(f"📄 Cached profile for Judge {profile.judge_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Profile caching failed: {e}")

    def _create_default_profile(self, judge_name: str) -> JudicialProfile:
        """Create default profile when analysis fails"""
        return JudicialProfile(
            judge_name=judge_name,
            court="Unknown Court",
            judicial_experience=5.0,
            primary_specialties=[JudgeSpecialty.GENERAL],
            decision_tendencies=[DecisionTendency.NEUTRAL],
            metrics=JudicialMetrics(
                settlement_rate=0.35,
                plaintiff_success_rate=0.45,
                defendant_success_rate=0.45
            ),
            ai_analysis_summary=f"Limited data available for Judge {judge_name}. General litigation strategies recommended.",
            confidence_score=0.3
        )

    def _get_default_insights(self, judge_name: str) -> Dict[str, Any]:
        """Default insights when analysis fails"""
        return {
            'judge_name': judge_name,
            'court': 'Unknown',
            'experience_years': 5.0,
            'overall_metrics': {
                'total_cases': 0,
                'settlement_rate': 0.35,
                'plaintiff_success_rate': 0.45,
                'average_case_duration': 365
            },
            'strategic_recommendations': [
                'Prepare comprehensive legal documentation',
                'Consider early settlement discussions',
                'Follow standard litigation procedures'
            ],
            'confidence_score': 0.3
        }

    async def _store_judicial_data(self, judge_name: str, data: List[Dict]):
        """Store new judicial data in database"""
        try:
            if data:
                # Add metadata
                for case in data:
                    case['judge_name'] = judge_name
                    case['data_source'] = 'courtlistener'
                    case['imported_at'] = datetime.utcnow()
                
                await self.db.litigation_cases.insert_many(data)
                logger.info(f"📚 Stored {len(data)} cases for Judge {judge_name}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to store judicial data: {e}")

    def _profile_to_dict(self, profile: JudicialProfile) -> Dict[str, Any]:
        """Convert JudicialProfile to dictionary for storage"""
        return {
            'judge_name': profile.judge_name,
            'court': profile.court,
            'appointment_date': profile.appointment_date,
            'judicial_experience': profile.judicial_experience,
            'primary_specialties': [s.value for s in profile.primary_specialties],
            'decision_tendencies': [t.value for t in profile.decision_tendencies],
            'metrics': {
                'total_cases': profile.metrics.total_cases,
                'cases_last_year': profile.metrics.cases_last_year,
                'average_case_duration': profile.metrics.average_case_duration,
                'settlement_rate': profile.metrics.settlement_rate,
                'appeal_rate': profile.metrics.appeal_rate,
                'reversal_rate': profile.metrics.reversal_rate,
                'plaintiff_success_rate': profile.metrics.plaintiff_success_rate,
                'defendant_success_rate': profile.metrics.defendant_success_rate,
                'motion_grant_rate': profile.metrics.motion_grant_rate
            },
            'case_type_patterns': {
                k: {
                    'pattern_type': v.pattern_type,
                    'case_count': v.case_count,
                    'success_rate': v.success_rate,
                    'average_duration': v.average_duration,
                    'settlement_preference': v.settlement_preference,
                    'confidence_score': v.confidence_score,
                    'notable_tendencies': v.notable_tendencies
                }
                for k, v in profile.case_type_patterns.items()
            },
            'ai_analysis_summary': profile.ai_analysis_summary,
            'confidence_score': profile.confidence_score,
            'last_updated': profile.last_updated
        }

    def _dict_to_profile(self, data: Dict[str, Any]) -> JudicialProfile:
        """Convert dictionary to JudicialProfile object"""
        metrics = JudicialMetrics(
            total_cases=data.get('metrics', {}).get('total_cases', 0),
            cases_last_year=data.get('metrics', {}).get('cases_last_year', 0),
            average_case_duration=data.get('metrics', {}).get('average_case_duration', 0.0),
            settlement_rate=data.get('metrics', {}).get('settlement_rate', 0.0),
            appeal_rate=data.get('metrics', {}).get('appeal_rate', 0.0),
            reversal_rate=data.get('metrics', {}).get('reversal_rate', 0.0),
            plaintiff_success_rate=data.get('metrics', {}).get('plaintiff_success_rate', 0.0),
            defendant_success_rate=data.get('metrics', {}).get('defendant_success_rate', 0.0),
            motion_grant_rate=data.get('metrics', {}).get('motion_grant_rate', 0.0)
        )
        
        case_patterns = {}
        for k, v in data.get('case_type_patterns', {}).items():
            case_patterns[k] = JudicialPattern(
                pattern_type=v.get('pattern_type', ''),
                case_count=v.get('case_count', 0),
                success_rate=v.get('success_rate', 0.0),
                average_duration=v.get('average_duration', 0.0),
                settlement_preference=v.get('settlement_preference', 0.0),
                confidence_score=v.get('confidence_score', 0.0),
                notable_tendencies=v.get('notable_tendencies', [])
            )
        
        specialties = []
        for spec in data.get('primary_specialties', []):
            try:
                specialties.append(JudgeSpecialty(spec))
            except ValueError:
                continue
        
        tendencies = []
        for tend in data.get('decision_tendencies', []):
            try:
                tendencies.append(DecisionTendency(tend))
            except ValueError:
                continue
        
        return JudicialProfile(
            judge_name=data.get('judge_name', ''),
            court=data.get('court', ''),
            appointment_date=data.get('appointment_date'),
            judicial_experience=data.get('judicial_experience', 0.0),
            primary_specialties=specialties,
            decision_tendencies=tendencies,
            metrics=metrics,
            case_type_patterns=case_patterns,
            ai_analysis_summary=data.get('ai_analysis_summary', ''),
            confidence_score=data.get('confidence_score', 0.0),
            last_updated=data.get('last_updated', datetime.utcnow())
        )

# Global analyzer instance
_judicial_analyzer = None

async def get_judicial_analyzer(db_connection) -> JudicialBehaviorAnalyzer:
    """Get or create judicial behavior analyzer instance"""
    global _judicial_analyzer
    
    if _judicial_analyzer is None:
        _judicial_analyzer = JudicialBehaviorAnalyzer(db_connection)
        logger.info("⚖️ Judicial Behavior Analyzer instance created")
    
    return _judicial_analyzer

async def initialize_judicial_analyzer(db_connection):
    """Initialize the judicial behavior analyzer"""
    await get_judicial_analyzer(db_connection)
    logger.info("✅ Judicial Behavior Analyzer initialized successfully")
"""
Legal Update Validation and Impact Analysis System
Validates and analyzes the impact of legal updates on the knowledge base
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
from urllib.parse import urlparse
import hashlib
import google.generativeai as genai
from groq import Groq
import os

# Configure logging
logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    VALID = "valid"
    INVALID = "invalid"
    REQUIRES_REVIEW = "requires_review"
    DUPLICATE = "duplicate"

class ImpactLevel(Enum):
    HIGH = "high"          # Affects multiple legal domains or precedents
    MEDIUM = "medium"      # Affects specific legal area
    LOW = "low"           # Minor or procedural impact
    MINIMAL = "minimal"    # Administrative or clerical

@dataclass
class SourceValidation:
    """Results of source verification"""
    is_official: bool
    domain_verified: bool
    ssl_verified: bool
    reputation_score: float  # 0.0-1.0
    validation_notes: List[str]

@dataclass
class ContentValidation:
    """Results of content validation"""
    is_legal_content: bool
    contains_citations: bool
    has_legal_authority: bool
    content_quality_score: float  # 0.0-1.0
    validation_notes: List[str]

@dataclass
class ImpactAnalysis:
    """Results of impact analysis on knowledge base"""
    impact_level: ImpactLevel
    affected_documents: List[str]
    outdated_information: List[Dict[str, Any]]
    new_concepts: List[str]
    superseded_authorities: List[str]
    knowledge_base_changes: List[Dict[str, Any]]
    confidence_score: float  # 0.0-1.0
    analysis_notes: List[str]

@dataclass
class UpdateValidationResult:
    """Complete validation result for a legal update"""
    update_id: str
    validation_result: ValidationResult
    source_validation: SourceValidation
    content_validation: ContentValidation
    impact_analysis: Optional[ImpactAnalysis]
    integration_recommendation: str
    validation_timestamp: datetime
    reviewer_notes: List[str]

class LegalUpdateValidator:
    """Validates legal updates for authenticity and quality"""
    
    def __init__(self, gemini_api_key: str, groq_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.groq_client = Groq(api_key=groq_api_key)
        
        # Trusted domains for legal sources
        self.trusted_domains = {
            'supremecourt.gov': 1.0,
            'courtlistener.com': 0.95,
            'federalregister.gov': 1.0,
            'uscourts.gov': 1.0,
            'justice.gov': 1.0,
            'congress.gov': 1.0,
            'gpo.gov': 0.9,
            'law.justia.com': 0.8,
            'caselaw.findlaw.com': 0.75
        }
    
    async def validate_update(self, legal_update) -> UpdateValidationResult:
        """Perform comprehensive validation of a legal update"""
        try:
            logger.info(f"Validating legal update: {legal_update.update_id}")
            
            # Source validation
            source_validation = await self._validate_source(legal_update.url)
            
            # Content validation  
            content_validation = await self._validate_content(legal_update)
            
            # Determine overall validation result
            validation_result = self._determine_validation_result(
                source_validation, content_validation
            )
            
            # Impact analysis (only for valid updates)
            impact_analysis = None
            if validation_result in [ValidationResult.VALID, ValidationResult.REQUIRES_REVIEW]:
                impact_analysis = await self._analyze_impact(legal_update)
            
            # Integration recommendation
            integration_recommendation = self._generate_integration_recommendation(
                validation_result, source_validation, content_validation, impact_analysis
            )
            
            return UpdateValidationResult(
                update_id=legal_update.update_id,
                validation_result=validation_result,
                source_validation=source_validation,
                content_validation=content_validation,
                impact_analysis=impact_analysis,
                integration_recommendation=integration_recommendation,
                validation_timestamp=datetime.now(),
                reviewer_notes=[]
            )
            
        except Exception as e:
            logger.error(f"Error validating update {legal_update.update_id}: {e}")
            return self._create_error_validation_result(legal_update.update_id, str(e))
    
    async def _validate_source(self, url: str) -> SourceValidation:
        """Validate the source URL and domain"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check if domain is in trusted list
            reputation_score = 0.0
            domain_verified = False
            
            for trusted_domain, score in self.trusted_domains.items():
                if domain.endswith(trusted_domain):
                    reputation_score = score
                    domain_verified = True
                    break
            
            # Check for government domains
            is_official = domain.endswith('.gov') or domain in self.trusted_domains
            
            # SSL verification (assume HTTPS is SSL verified)
            ssl_verified = parsed_url.scheme == 'https'
            
            validation_notes = []
            if not is_official:
                validation_notes.append("Source is not an official government domain")
            if not ssl_verified:
                validation_notes.append("URL does not use HTTPS")
            if reputation_score < 0.7:
                validation_notes.append("Domain has lower reputation score")
            
            return SourceValidation(
                is_official=is_official,
                domain_verified=domain_verified,
                ssl_verified=ssl_verified,
                reputation_score=reputation_score,
                validation_notes=validation_notes
            )
            
        except Exception as e:
            logger.error(f"Error validating source {url}: {e}")
            return SourceValidation(
                is_official=False,
                domain_verified=False,
                ssl_verified=False,
                reputation_score=0.0,
                validation_notes=[f"Source validation error: {str(e)}"]
            )
    
    async def _validate_content(self, legal_update) -> ContentValidation:
        """Validate the content quality and legal authenticity"""
        try:
            content = f"{legal_update.title}\n{legal_update.summary}\n{legal_update.full_content[:2000]}"
            
            # AI-powered content validation
            validation_prompt = f"""
            As a legal content validator, analyze this legal document excerpt for authenticity and quality:
            
            Title: {legal_update.title}
            Source: {legal_update.source.value}
            Type: {legal_update.update_type.value}
            
            Content: {content}
            
            Evaluate and return JSON with:
            {{
                "is_legal_content": true/false,
                "contains_citations": true/false,
                "has_legal_authority": true/false,
                "content_quality_score": 0.0-1.0,
                "legal_indicators": ["list of legal language indicators found"],
                "quality_issues": ["list of any quality concerns"],
                "authenticity_score": 0.0-1.0
            }}
            
            Consider:
            - Legal terminology and structure
            - Presence of citations and references
            - Professional legal writing style
            - Consistency with expected document type
            - Absence of obvious errors or fabrication
            """
            
            try:
                # Use Gemini for content analysis
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(
                    validation_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1000,
                        temperature=0.1,
                    )
                )
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    
                    return ContentValidation(
                        is_legal_content=analysis_data.get('is_legal_content', True),
                        contains_citations=len(legal_update.citations) > 0 or analysis_data.get('contains_citations', False),
                        has_legal_authority=analysis_data.get('has_legal_authority', True),
                        content_quality_score=analysis_data.get('content_quality_score', 0.7),
                        validation_notes=analysis_data.get('quality_issues', [])
                    )
                    
            except Exception as ai_error:
                logger.warning(f"AI content validation failed, using fallback: {ai_error}")
            
            # Fallback validation using rule-based approach
            return self._fallback_content_validation(legal_update)
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            return ContentValidation(
                is_legal_content=True,  # Assume valid for official sources
                contains_citations=len(legal_update.citations) > 0,
                has_legal_authority=True,
                content_quality_score=0.5,
                validation_notes=[f"Content validation error: {str(e)}"]
            )
    
    def _fallback_content_validation(self, legal_update) -> ContentValidation:
        """Rule-based fallback content validation"""
        content = f"{legal_update.title} {legal_update.summary} {legal_update.full_content}".lower()
        
        # Legal terminology indicators
        legal_terms = [
            'court', 'judge', 'opinion', 'ruling', 'decision', 'statute', 'regulation',
            'plaintiff', 'defendant', 'petition', 'motion', 'order', 'judgment',
            'constitutional', 'federal', 'jurisdiction', 'precedent', 'appeal'
        ]
        
        legal_term_count = sum(1 for term in legal_terms if term in content)
        is_legal_content = legal_term_count >= 3
        
        # Check for citations
        contains_citations = len(legal_update.citations) > 0
        
        # Legal authority indicators
        authority_indicators = [
            'supreme court', 'circuit court', 'district court', 'federal register',
            'united states', 'constitution', 'code', 'statute'
        ]
        
        has_legal_authority = any(indicator in content for indicator in authority_indicators)
        
        # Quality score based on various factors
        quality_score = 0.6  # Base score
        if contains_citations:
            quality_score += 0.2
        if has_legal_authority:
            quality_score += 0.1
        if legal_term_count >= 5:
            quality_score += 0.1
        
        quality_score = min(quality_score, 1.0)
        
        validation_notes = []
        if not is_legal_content:
            validation_notes.append("Content may not be legal in nature")
        if not contains_citations:
            validation_notes.append("No legal citations found")
        if quality_score < 0.7:
            validation_notes.append("Lower content quality score")
        
        return ContentValidation(
            is_legal_content=is_legal_content,
            contains_citations=contains_citations,
            has_legal_authority=has_legal_authority,
            content_quality_score=quality_score,
            validation_notes=validation_notes
        )
    
    async def _analyze_impact(self, legal_update) -> ImpactAnalysis:
        """Analyze the potential impact of the update on the knowledge base"""
        try:
            # AI-powered impact analysis
            impact_prompt = f"""
            As a legal expert, analyze the potential impact of this legal update on an existing legal knowledge base:
            
            Update Details:
            - Title: {legal_update.title}
            - Source: {legal_update.source.value}
            - Type: {legal_update.update_type.value}
            - Priority: {legal_update.priority_level.value}
            - Legal Domains: {legal_update.legal_domains_affected}
            - Summary: {legal_update.summary}
            
            Analyze and return JSON with:
            {{
                "impact_level": "high|medium|low|minimal",
                "affected_domains": ["list of legal domains affected"],
                "new_legal_concepts": ["new concepts introduced"],
                "superseded_authorities": ["authorities that may be outdated"],
                "precedent_changes": ["changes in legal precedent"],
                "knowledge_updates_needed": ["types of knowledge base updates required"],
                "confidence_score": 0.0-1.0,
                "analysis_summary": "brief summary of impact"
            }}
            
            Consider:
            - Whether this creates new precedent or changes existing law
            - If it supersedes or modifies previous decisions/regulations
            - The scope of legal domains affected
            - The significance for legal practitioners
            """
            
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(
                    impact_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1500,
                        temperature=0.1,
                    )
                )
                
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    
                    # Map impact level
                    impact_level_map = {
                        'high': ImpactLevel.HIGH,
                        'medium': ImpactLevel.MEDIUM,
                        'low': ImpactLevel.LOW,
                        'minimal': ImpactLevel.MINIMAL
                    }
                    
                    impact_level = impact_level_map.get(
                        analysis_data.get('impact_level', 'medium'), 
                        ImpactLevel.MEDIUM
                    )
                    
                    return ImpactAnalysis(
                        impact_level=impact_level,
                        affected_documents=[],  # Would be populated by database search
                        outdated_information=[],  # Would be identified by content comparison
                        new_concepts=analysis_data.get('new_legal_concepts', []),
                        superseded_authorities=analysis_data.get('superseded_authorities', []),
                        knowledge_base_changes=analysis_data.get('knowledge_updates_needed', []),
                        confidence_score=analysis_data.get('confidence_score', 0.7),
                        analysis_notes=[analysis_data.get('analysis_summary', 'Impact analysis completed')]
                    )
                    
            except Exception as ai_error:
                logger.warning(f"AI impact analysis failed, using fallback: {ai_error}")
            
            # Fallback analysis
            return self._fallback_impact_analysis(legal_update)
            
        except Exception as e:
            logger.error(f"Error analyzing impact: {e}")
            return ImpactAnalysis(
                impact_level=ImpactLevel.MEDIUM,
                affected_documents=[],
                outdated_information=[],
                new_concepts=[],
                superseded_authorities=[],
                knowledge_base_changes=[],
                confidence_score=0.5,
                analysis_notes=[f"Impact analysis error: {str(e)}"]
            )
    
    def _fallback_impact_analysis(self, legal_update) -> ImpactAnalysis:
        """Rule-based fallback impact analysis"""
        # Determine impact level based on source and priority
        impact_level = ImpactLevel.MEDIUM
        
        if legal_update.source.value == 'supreme_court':
            impact_level = ImpactLevel.HIGH
        elif legal_update.priority_level.value == 'critical':
            impact_level = ImpactLevel.HIGH
        elif legal_update.priority_level.value == 'low':
            impact_level = ImpactLevel.LOW
        
        # Check for high-impact indicators
        high_impact_terms = ['overrule', 'overturn', 'unconstitutional', 'landmark', 'precedent']
        content_lower = f"{legal_update.title} {legal_update.summary}".lower()
        
        if any(term in content_lower for term in high_impact_terms):
            impact_level = ImpactLevel.HIGH
        
        return ImpactAnalysis(
            impact_level=impact_level,
            affected_documents=[],
            outdated_information=[],
            new_concepts=legal_update.legal_domains_affected,
            superseded_authorities=[],
            knowledge_base_changes=[],
            confidence_score=0.6,
            analysis_notes=[f"Fallback analysis based on source ({legal_update.source.value}) and priority ({legal_update.priority_level.value})"]
        )
    
    def _determine_validation_result(
        self, 
        source_validation: SourceValidation, 
        content_validation: ContentValidation
    ) -> ValidationResult:
        """Determine overall validation result based on source and content validation"""
        
        # Invalid if source is not trusted and content quality is low
        if (not source_validation.is_official and 
            source_validation.reputation_score < 0.5 and 
            content_validation.content_quality_score < 0.5):
            return ValidationResult.INVALID
        
        # Requires review if there are significant concerns
        if (not source_validation.is_official or 
            content_validation.content_quality_score < 0.7 or
            not content_validation.is_legal_content):
            return ValidationResult.REQUIRES_REVIEW
        
        # Valid if source is trusted and content quality is good
        if (source_validation.is_official and 
            content_validation.is_legal_content and 
            content_validation.content_quality_score >= 0.7):
            return ValidationResult.VALID
        
        # Default to requires review
        return ValidationResult.REQUIRES_REVIEW
    
    def _generate_integration_recommendation(
        self,
        validation_result: ValidationResult,
        source_validation: SourceValidation,
        content_validation: ContentValidation,
        impact_analysis: Optional[ImpactAnalysis]
    ) -> str:
        """Generate recommendation for integration"""
        
        if validation_result == ValidationResult.INVALID:
            return "DO NOT INTEGRATE - Update failed validation checks"
        
        if validation_result == ValidationResult.REQUIRES_REVIEW:
            reasons = []
            if not source_validation.is_official:
                reasons.append("unofficial source")
            if content_validation.content_quality_score < 0.7:
                reasons.append("content quality concerns")
            if not content_validation.is_legal_content:
                reasons.append("content may not be legal")
            
            return f"MANUAL REVIEW REQUIRED - Issues: {', '.join(reasons)}"
        
        if validation_result == ValidationResult.VALID:
            if impact_analysis and impact_analysis.impact_level == ImpactLevel.HIGH:
                return "AUTO-INTEGRATE WITH PRIORITY - High impact legal update"
            elif impact_analysis and impact_analysis.impact_level in [ImpactLevel.MEDIUM, ImpactLevel.LOW]:
                return "AUTO-INTEGRATE - Standard legal update"
            else:
                return "AUTO-INTEGRATE - Validated legal update"
        
        return "HOLD FOR REVIEW - Unable to determine integration approach"
    
    def _create_error_validation_result(self, update_id: str, error_message: str) -> UpdateValidationResult:
        """Create validation result for errors"""
        return UpdateValidationResult(
            update_id=update_id,
            validation_result=ValidationResult.REQUIRES_REVIEW,
            source_validation=SourceValidation(
                is_official=False,
                domain_verified=False,
                ssl_verified=False,
                reputation_score=0.0,
                validation_notes=[f"Validation error: {error_message}"]
            ),
            content_validation=ContentValidation(
                is_legal_content=False,
                contains_citations=False,
                has_legal_authority=False,
                content_quality_score=0.0,
                validation_notes=[f"Content validation error: {error_message}"]
            ),
            impact_analysis=None,
            integration_recommendation="MANUAL REVIEW REQUIRED - Validation errors occurred",
            validation_timestamp=datetime.now(),
            reviewer_notes=[f"Validation system error: {error_message}"]
        )

class KnowledgeBaseFreshnessTracker:
    """Tracks the freshness and currency of the knowledge base"""
    
    def __init__(self):
        self.domain_freshness = {}
        self.last_updates = {}
        self.outdated_documents = []
    
    def update_domain_freshness(self, domain: str, update_date: datetime):
        """Update freshness timestamp for a legal domain"""
        self.domain_freshness[domain] = update_date
        self.last_updates[domain] = datetime.now()
    
    def check_knowledge_base_currency(self) -> Dict[str, Any]:
        """Check overall currency of knowledge base"""
        current_time = datetime.now()
        freshness_report = {}
        
        for domain, last_update in self.domain_freshness.items():
            days_since_update = (current_time - last_update).days
            
            # Determine freshness status
            if days_since_update <= 7:
                status = "current"
            elif days_since_update <= 30:
                status = "recent"
            elif days_since_update <= 90:
                status = "aging"
            else:
                status = "stale"
            
            freshness_report[domain] = {
                "last_update": last_update.isoformat(),
                "days_since_update": days_since_update,
                "status": status
            }
        
        return {
            "overall_freshness": "current" if all(r["days_since_update"] <= 30 for r in freshness_report.values()) else "needs_updates",
            "domain_freshness": freshness_report,
            "check_timestamp": current_time.isoformat()
        }

# Global instances
legal_update_validator = None
knowledge_freshness_tracker = KnowledgeBaseFreshnessTracker()

def initialize_legal_update_validator(gemini_api_key: str, groq_api_key: str):
    """Initialize the global legal update validator"""
    global legal_update_validator
    legal_update_validator = LegalUpdateValidator(gemini_api_key, groq_api_key)
    return legal_update_validator
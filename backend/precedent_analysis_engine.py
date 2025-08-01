"""
Precedent Analysis Engine - Advanced Legal Precedent Analysis System

This module implements sophisticated legal precedent analysis that can:
1. Identify controlling vs. persuasive precedents
2. Handle precedent conflicts across jurisdictions  
3. Track precedent evolution over time
4. Provide legal reasoning chains from precedents to conclusions
5. Integrate with Legal Concept Understanding System

Key Features:
- Precedent hierarchy analysis with authority scoring
- Multi-jurisdiction precedent conflict resolution
- Legal reasoning chain construction
- Precedent influence and citation strength analysis
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re

from citation_extraction_engine import (
    CitationExtractionEngine, LegalCitation, CitationType, CitationContext, 
    CourtLevel, CitationNetwork, citation_engine
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrecedentType(Enum):
    """Types of precedent authority"""
    CONTROLLING = "controlling"      # Binding precedent from higher court in same jurisdiction
    PERSUASIVE = "persuasive"       # Non-binding but influential precedent  
    DISTINGUISHABLE = "distinguishable"  # Factually or legally distinguishable
    SUPERSEDED = "superseded"       # Overruled or no longer good law
    CONFLICTING = "conflicting"     # Conflicts with other precedents
    
class PrecedentStrength(Enum):
    """Strength of precedent authority"""
    VERY_STRONG = "very_strong"     # Supreme Court controlling precedent
    STRONG = "strong"               # Circuit controlling or highly cited
    MODERATE = "moderate"           # District court or state court
    WEAK = "weak"                   # Old or rarely cited
    VERY_WEAK = "very_weak"        # Superseded or heavily criticized

@dataclass
class PrecedentAnalysisResult:
    """Result of precedent analysis for a legal issue"""
    legal_issue: str
    controlling_precedents: List[Dict[str, Any]] = field(default_factory=list)
    persuasive_precedents: List[Dict[str, Any]] = field(default_factory=list) 
    conflicting_precedents: List[Dict[str, Any]] = field(default_factory=list)
    legal_reasoning_chain: List[str] = field(default_factory=list)
    precedent_summary: str = ""
    confidence_score: float = 0.0
    jurisdiction_analysis: Dict[str, Any] = field(default_factory=dict)
    temporal_analysis: Dict[str, Any] = field(default_factory=dict)
    concept_integration: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalPrecedent:
    """Enhanced precedent information with analysis"""
    case_id: str
    case_name: str
    court: str
    jurisdiction: str
    decision_date: Optional[datetime]
    legal_issues: List[str] = field(default_factory=list)
    holding: str = ""
    legal_principles: List[str] = field(default_factory=list)
    precedent_authority: float = 0.0  # 0.0-1.0 authority score
    citations_received: int = 0
    citing_cases: List[str] = field(default_factory=list)
    cited_cases: List[str] = field(default_factory=list)
    precedent_type: PrecedentType = PrecedentType.PERSUASIVE
    precedent_strength: PrecedentStrength = PrecedentStrength.MODERATE
    distinguishing_factors: List[str] = field(default_factory=list)
    overruling_cases: List[str] = field(default_factory=list)
    content: str = ""
    legal_concepts: List[str] = field(default_factory=list)  # Integration with concept system

@dataclass  
class LegalReasoningChain:
    """Multi-step legal reasoning from precedents to conclusions"""
    issue_identification: str
    applicable_precedents: List[str]
    rule_extraction: List[str]
    rule_application: List[str]
    conclusion: str
    confidence_score: float
    alternative_reasoning: List[str] = field(default_factory=list)

class PrecedentAnalysisEngine:
    """Advanced legal precedent analysis engine"""
    
    def __init__(self):
        self.citation_engine = citation_engine
        self.precedent_database: Dict[str, LegalPrecedent] = {}
        self.citation_networks: Dict[str, CitationNetwork] = {}
        
        # Court hierarchy for precedent authority
        self.court_hierarchy = {
            "U.S. Supreme Court": 1.0,
            "Federal Circuit": 0.95,
            "Circuit Courts": 0.85,
            "District Courts": 0.65,
            "State Supreme Courts": 0.80,
            "State Appellate Courts": 0.60,
            "State Trial Courts": 0.45
        }
        
        # Jurisdiction relationships for precedent authority
        self.jurisdiction_hierarchy = {
            "US_Federal": ["US_1st_Circuit", "US_2nd_Circuit", "US_3rd_Circuit", "US_4th_Circuit",
                          "US_5th_Circuit", "US_6th_Circuit", "US_7th_Circuit", "US_8th_Circuit", 
                          "US_9th_Circuit", "US_10th_Circuit", "US_11th_Circuit", "US_DC_Circuit"],
            "US_1st_Circuit": ["US_D.Mass_District", "US_D.Me_District", "US_D.N.H_District"],
            "US_2nd_Circuit": ["US_S.D.N.Y_District", "US_E.D.N.Y_District", "US_D.Conn_District"],
            # Add more jurisdictional relationships as needed
        }
        
        # Analysis statistics
        self.analysis_stats = {
            "precedents_analyzed": 0,
            "controlling_precedents_found": 0,
            "precedent_conflicts_resolved": 0,
            "legal_reasoning_chains_generated": 0
        }
        
        # Integration with Legal Concept Understanding System
        self.legal_concepts_integration = None
        
    def _initialize_legal_concepts_integration(self):
        """Initialize integration with Legal Concept Understanding System"""
        try:
            from legal_concept_extractor import legal_concept_extractor
            from legal_concept_ontology import legal_ontology
            from contextual_legal_analyzer import contextual_legal_analyzer
            
            self.legal_concepts_integration = {
                "extractor": legal_concept_extractor,
                "ontology": legal_ontology,
                "analyzer": contextual_legal_analyzer
            }
            logger.info("✅ Legal Concept Understanding System integration initialized")
        except ImportError as e:
            logger.warning(f"Legal Concept Understanding System not fully available: {e}")
            self.legal_concepts_integration = None
    
    async def initialize_precedent_database(self, knowledge_base_path: str = "/app/legal_knowledge_base.json"):
        """Initialize precedent database from legal knowledge base"""
        logger.info("🏗️ Initializing precedent database...")
        
        try:
            # Load knowledge base
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Build citation networks
            self.citation_networks = await self.citation_engine.build_citation_network(documents)
            
            # Create precedent entries
            for doc in documents:
                if self._is_case_document(doc):
                    precedent = await self._create_precedent_from_document(doc)
                    if precedent:
                        self.precedent_database[precedent.case_id] = precedent
            
            # Enhance precedents with citation analysis
            await self._enhance_precedents_with_citations()
            
            # Initialize legal concepts integration
            self._initialize_legal_concepts_integration()
            
            logger.info(f"✅ Precedent database initialized with {len(self.precedent_database)} precedents")
            
        except Exception as e:
            logger.error(f"Error initializing precedent database: {e}")
            raise
    
    def _is_case_document(self, document: Dict[str, Any]) -> bool:
        """Determine if a document is a case opinion vs statute/regulation"""
        content = document.get('content', '').lower()
        title = document.get('title', '').lower()
        doc_type = document.get('document_type', '').lower()
        
        # Check for case indicators
        case_indicators = [
            'v.', 'versus', 'opinion', 'court held', 'judgment', 'decided', 
            'appeal', 'petition', 'plaintiff', 'defendant', 'holding'
        ]
        
        # Check for non-case indicators  
        non_case_indicators = ['u.s.c.', 'c.f.r.', 'statute', 'regulation', 'code']
        
        case_score = sum(1 for indicator in case_indicators if indicator in content or indicator in title)
        non_case_score = sum(1 for indicator in non_case_indicators if indicator in content or indicator in title)
        
        return case_score > non_case_score or doc_type in ['case', 'opinion']
    
    async def _create_precedent_from_document(self, document: Dict[str, Any]) -> Optional[LegalPrecedent]:
        """Create a LegalPrecedent object from a document"""
        try:
            doc_id = document.get('id', '')
            title = document.get('title', 'Unknown Case')
            content = document.get('content', '')
            jurisdiction = document.get('jurisdiction', 'Unknown')
            
            # Extract decision date
            decision_date = self._extract_decision_date(content, title)
            
            # Identify court
            court = self._identify_court_from_document(document)
            
            # Extract legal issues and holding
            legal_issues = await self._extract_legal_issues(content)
            holding = self._extract_holding(content)
            legal_principles = await self._extract_legal_principles(content)
            
            # Calculate initial precedent authority based on court level
            precedent_authority = self._calculate_initial_authority(court, jurisdiction)
            
            # Determine precedent strength
            precedent_strength = self._determine_precedent_strength(court, decision_date, precedent_authority)
            
            # Extract legal concepts if integration available
            legal_concepts = []
            if self.legal_concepts_integration:
                legal_concepts = await self._extract_legal_concepts_from_precedent(content)
            
            precedent = LegalPrecedent(
                case_id=doc_id,
                case_name=title,
                court=court,
                jurisdiction=jurisdiction,
                decision_date=decision_date,
                legal_issues=legal_issues,
                holding=holding,
                legal_principles=legal_principles,
                precedent_authority=precedent_authority,
                precedent_strength=precedent_strength,
                content=content,
                legal_concepts=legal_concepts
            )
            
            return precedent
            
        except Exception as e:
            logger.error(f"Error creating precedent from document {document.get('id', '')}: {e}")
            return None
    
    def _extract_decision_date(self, content: str, title: str) -> Optional[datetime]:
        """Extract decision date from case content"""
        # Look for date patterns
        date_patterns = [
            r'(?:decided|filed|issued)\s+(?:on\s+)?([A-Z][a-z]+\s+\d{1,2},\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'([A-Z][a-z]+\s+\d{1,2},\s+\d{4})',
            r'\b(19|20)\d{2}\b'  # Year only as fallback
        ]
        
        combined_text = f"{title} {content[:1000]}"  # Check first 1000 chars
        
        for pattern in date_patterns:
            matches = re.findall(pattern, combined_text)
            if matches:
                try:
                    # Try to parse the first match
                    date_str = matches[0]
                    if '/' in date_str:
                        return datetime.strptime(date_str, '%m/%d/%Y')
                    elif ',' in date_str:
                        return datetime.strptime(date_str, '%B %d, %Y')
                    elif len(date_str) == 4:  # Year only
                        return datetime(int(date_str), 1, 1)
                except ValueError:
                    continue
        
        return None
    
    def _identify_court_from_document(self, document: Dict[str, Any]) -> str:
        """Identify the court from document metadata and content"""
        content = document.get('content', '')
        title = document.get('title', '')
        source_url = document.get('source_url', '')
        
        # Check for court identifiers
        if 'U.S.' in content or 'Supreme Court' in content:
            return "U.S. Supreme Court"
        elif any(circuit in content for circuit in ['Circuit', 'Cir.']):
            circuit_match = re.search(r'(\d+(?:st|nd|rd|th)|D\.C\.)\s+(?:Circuit|Cir)', content)
            if circuit_match:
                return f"{circuit_match.group(1)} Circuit Court of Appeals"
            return "Circuit Court of Appeals"
        elif any(district in content for district in ['District', 'D.', 'F. Supp']):
            return "U.S. District Court"
        elif any(state in content for state in ['Supreme Court', 'Sup. Ct.']):
            return "State Supreme Court"
        elif 'Court of Appeals' in content:
            return "State Court of Appeals"
        else:
            return "Unknown Court"
    
    async def _extract_legal_issues(self, content: str) -> List[str]:
        """Extract key legal issues from case content"""
        issues = []
        
        # Look for common legal issue patterns
        issue_patterns = [
            r'(?:issue|question|matter)\s+(?:before|for)\s+(?:the\s+court|us)\s+is\s+([^.]+)',
            r'the\s+(?:primary|main|central)\s+(?:issue|question)\s+is\s+([^.]+)',
            r'we\s+(?:must\s+)?(?:decide|determine)\s+(?:whether|if)\s+([^.]+)',
            r'the\s+court\s+(?:must\s+)?(?:decide|determine|consider)\s+([^.]+)'
        ]
        
        for pattern in issue_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            issues.extend([match.strip() for match in matches[:3]])  # Limit to 3 issues
        
        return issues[:5]  # Maximum 5 issues
    
    def _extract_holding(self, content: str) -> str:
        """Extract the holding from case content"""
        # Look for holding patterns
        holding_patterns = [
            r'(?:we\s+hold|held|holding)\s+that\s+([^.]+\.)',
            r'the\s+court\s+(?:holds|held)\s+that\s+([^.]+\.)',
            r'(?:accordingly|therefore),?\s+we\s+(?:hold|find|conclude)\s+([^.]+\.)',
            r'our\s+holding\s+is\s+([^.]+\.)'
        ]
        
        for pattern in holding_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    async def _extract_legal_principles(self, content: str) -> List[str]:
        """Extract legal principles from case content"""
        principles = []
        
        # Look for principle indicators
        principle_patterns = [
            r'the\s+(?:rule|principle|law)\s+(?:is|requires|states)\s+that\s+([^.]+)',
            r'it\s+is\s+(?:well\s+)?(?:established|settled)\s+(?:law\s+)?that\s+([^.]+)',
            r'(?:under|pursuant to)\s+(?:this|the)\s+(?:rule|principle|standard),?\s+([^.]+)',
            r'the\s+(?:legal\s+)?(?:standard|test|framework)\s+(?:is|requires)\s+([^.]+)'
        ]
        
        for pattern in principle_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            principles.extend([match.strip() for match in matches[:2]])
        
        return principles[:3]  # Maximum 3 principles
    
    def _calculate_initial_authority(self, court: str, jurisdiction: str) -> float:
        """Calculate initial precedent authority based on court and jurisdiction"""
        # Base authority from court level
        authority = 0.5  # Default
        
        for court_type, score in self.court_hierarchy.items():
            if court_type.lower() in court.lower():
                authority = score
                break
        
        # Adjust for jurisdiction (federal vs state)
        if 'federal' in jurisdiction.lower() or 'u.s.' in court.lower():
            authority += 0.1
        
        return min(1.0, authority)
    
    def _determine_precedent_strength(self, court: str, decision_date: Optional[datetime], 
                                   authority: float) -> PrecedentStrength:
        """Determine precedent strength based on multiple factors"""
        if authority >= 0.95:
            return PrecedentStrength.VERY_STRONG
        elif authority >= 0.8:
            return PrecedentStrength.STRONG
        elif authority >= 0.6:
            return PrecedentStrength.MODERATE
        elif authority >= 0.4:
            return PrecedentStrength.WEAK
        else:
            return PrecedentStrength.VERY_WEAK
    
    async def _extract_legal_concepts_from_precedent(self, content: str) -> List[str]:
        """Extract legal concepts using the Legal Concept Understanding System"""
        if not self.legal_concepts_integration:
            return []
        
        try:
            extractor = self.legal_concepts_integration["extractor"]
            result = await extractor.extract_legal_concepts(content)
            return [concept.get("concept_name", "") for concept in result.get("identified_concepts", [])]
        except Exception as e:
            logger.warning(f"Error extracting legal concepts: {e}")
            return []
    
    async def _enhance_precedents_with_citations(self):
        """Enhance precedents with citation analysis from citation networks"""
        logger.info("🔗 Enhancing precedents with citation analysis...")
        
        for case_id, precedent in self.precedent_database.items():
            if case_id in self.citation_networks:
                network = self.citation_networks[case_id]
                
                # Update citation information
                precedent.citations_received = len(network.inbound_citations)
                precedent.citing_cases = network.inbound_citations.copy()
                precedent.cited_cases = [cite.citation_string for cite in network.outbound_citations]
                
                # Update precedent authority based on citation analysis
                precedent.precedent_authority = min(1.0, precedent.precedent_authority + (network.authority_score * 0.3))
                
                # Analyze citing context to identify potential overruling
                for citation in network.outbound_citations:
                    if citation.citation_context == CitationContext.OVERRULING:
                        precedent.overruling_cases.append(citation.citation_string)
                        precedent.precedent_type = PrecedentType.SUPERSEDED
    
    async def analyze_precedents_for_issue(self, legal_issue: str, jurisdiction: str = "US_Federal",
                                         user_facts: Optional[str] = None) -> PrecedentAnalysisResult:
        """Analyze precedents for a specific legal issue"""
        logger.info(f"⚖️ Analyzing precedents for issue: {legal_issue[:100]}...")
        
        try:
            self.analysis_stats["precedents_analyzed"] += 1
            
            # Find relevant precedents
            relevant_precedents = await self._find_relevant_precedents(legal_issue, jurisdiction)
            
            # Classify precedents by type
            controlling = []
            persuasive = []
            conflicting = []
            
            for precedent in relevant_precedents:
                precedent_data = self._format_precedent_for_response(precedent)
                
                if await self._is_controlling_precedent(precedent, jurisdiction):
                    controlling.append(precedent_data)
                    self.analysis_stats["controlling_precedents_found"] += 1
                elif precedent.precedent_type == PrecedentType.CONFLICTING:
                    conflicting.append(precedent_data)
                else:
                    persuasive.append(precedent_data)
            
            # Generate legal reasoning chain
            reasoning_chain = await self._generate_legal_reasoning_chain(
                legal_issue, controlling + persuasive, user_facts
            )
            
            # Create precedent summary
            precedent_summary = self._create_precedent_summary(controlling, persuasive, conflicting)
            
            # Calculate confidence score
            confidence = self._calculate_analysis_confidence(controlling, persuasive, conflicting)
            
            # Perform jurisdiction analysis
            jurisdiction_analysis = self._analyze_jurisdictional_coverage(
                controlling + persuasive, jurisdiction
            )
            
            # Perform temporal analysis
            temporal_analysis = self._analyze_temporal_trends(controlling + persuasive)
            
            # Integrate with legal concepts if available
            concept_integration = {}
            if self.legal_concepts_integration:
                concept_integration = await self._integrate_with_legal_concepts(
                    legal_issue, controlling + persuasive
                )
            
            result = PrecedentAnalysisResult(
                legal_issue=legal_issue,
                controlling_precedents=controlling,
                persuasive_precedents=persuasive,
                conflicting_precedents=conflicting,
                legal_reasoning_chain=reasoning_chain.rule_application if reasoning_chain else [],
                precedent_summary=precedent_summary,
                confidence_score=confidence,
                jurisdiction_analysis=jurisdiction_analysis,
                temporal_analysis=temporal_analysis,
                concept_integration=concept_integration
            )
            
            logger.info(f"✅ Precedent analysis complete: {len(controlling)} controlling, {len(persuasive)} persuasive, {len(conflicting)} conflicting")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing precedents for issue: {e}")
            return PrecedentAnalysisResult(legal_issue=legal_issue)
    
    async def _find_relevant_precedents(self, legal_issue: str, jurisdiction: str) -> List[LegalPrecedent]:
        """Find precedents relevant to a legal issue"""
        relevant = []
        
        # Create search terms from legal issue
        issue_terms = set(legal_issue.lower().split())
        legal_keywords = {'contract', 'constitutional', 'tort', 'criminal', 'employment', 'property', 'family'}
        issue_terms.update(legal_keywords)
        
        for precedent in self.precedent_database.values():
            relevance_score = 0.0
            
            # Check legal issues
            for issue in precedent.legal_issues:
                issue_words = set(issue.lower().split())
                overlap = len(issue_terms.intersection(issue_words))
                relevance_score += overlap * 0.3
            
            # Check holding and principles
            content_text = f"{precedent.holding} {' '.join(precedent.legal_principles)}".lower()
            content_words = set(content_text.split())
            overlap = len(issue_terms.intersection(content_words))
            relevance_score += overlap * 0.2
            
            # Check legal concepts
            for concept in precedent.legal_concepts:
                if any(term in concept.lower() for term in issue_terms):
                    relevance_score += 0.4
            
            # Boost for same jurisdiction
            if precedent.jurisdiction == jurisdiction:
                relevance_score += 1.0
            elif jurisdiction in precedent.jurisdiction or precedent.jurisdiction in jurisdiction:
                relevance_score += 0.5
            
            # Minimum relevance threshold
            if relevance_score >= 1.0:
                relevant.append(precedent)
        
        # Sort by relevance and authority
        relevant.sort(key=lambda p: (p.precedent_authority, len(p.citing_cases)), reverse=True)
        return relevant[:20]  # Limit to top 20 most relevant
    
    async def _is_controlling_precedent(self, precedent: LegalPrecedent, jurisdiction: str) -> bool:
        """Determine if a precedent is controlling for the given jurisdiction"""
        # Same jurisdiction and higher or equal court level
        if precedent.jurisdiction == jurisdiction:
            return precedent.precedent_authority >= 0.8
        
        # Federal precedent controlling over state issues in some cases
        if jurisdiction.startswith("US_") and "Supreme Court" in precedent.court:
            return True
        
        # Circuit precedent controlling within circuit
        if jurisdiction.startswith("US_") and "Circuit" in precedent.court:
            precedent_circuit = self._extract_circuit_from_jurisdiction(precedent.jurisdiction)
            query_circuit = self._extract_circuit_from_jurisdiction(jurisdiction)
            return precedent_circuit == query_circuit and precedent.precedent_authority >= 0.8
        
        return False
    
    def _extract_circuit_from_jurisdiction(self, jurisdiction: str) -> Optional[str]:
        """Extract circuit identifier from jurisdiction string"""
        match = re.search(r'(\d+(?:st|nd|rd|th)|DC)_Circuit', jurisdiction)
        return match.group(1) if match else None
    
    async def _generate_legal_reasoning_chain(self, legal_issue: str, precedents: List[Dict], 
                                           user_facts: Optional[str] = None) -> Optional[LegalReasoningChain]:
        """Generate a legal reasoning chain from precedents to conclusion"""
        try:
            self.analysis_stats["legal_reasoning_chains_generated"] += 1
            
            # Extract rules from precedents
            extracted_rules = []
            applicable_precedents = []
            
            for precedent_data in precedents[:5]:  # Use top 5 precedents
                precedent_id = precedent_data.get("case_id", "")
                if precedent_id in self.precedent_database:
                    precedent = self.precedent_database[precedent_id]
                    applicable_precedents.append(precedent.case_name)
                    
                    # Extract legal rules from holding and principles
                    if precedent.holding:
                        extracted_rules.append(f"Rule from {precedent.case_name}: {precedent.holding}")
                    
                    for principle in precedent.legal_principles:
                        extracted_rules.append(f"Principle from {precedent.case_name}: {principle}")
            
            # Apply rules to user facts if provided
            rule_applications = []
            if user_facts and extracted_rules:
                for rule in extracted_rules[:3]:  # Apply top 3 rules
                    application = f"Applying {rule[:50]}... to the facts: {user_facts[:100]}..."
                    rule_applications.append(application)
            else:
                rule_applications = extracted_rules[:3]
            
            # Generate conclusion
            conclusion = f"Based on the analysis of {len(applicable_precedents)} relevant precedents for the issue '{legal_issue}', "
            if user_facts:
                conclusion += f"and applying the established legal rules to the given facts, "
            conclusion += "the legal analysis suggests following the precedential guidance established by the controlling authorities."
            
            # Calculate confidence
            confidence = min(0.9, len(precedents) * 0.1 + 0.3)
            
            return LegalReasoningChain(
                issue_identification=legal_issue,
                applicable_precedents=applicable_precedents,
                rule_extraction=extracted_rules,
                rule_application=rule_applications,
                conclusion=conclusion,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Error generating legal reasoning chain: {e}")
            return None
    
    def _format_precedent_for_response(self, precedent: LegalPrecedent) -> Dict[str, Any]:
        """Format precedent data for API response"""
        return {
            "case_id": precedent.case_id,
            "case_name": precedent.case_name,
            "court": precedent.court,
            "jurisdiction": precedent.jurisdiction,
            "decision_date": precedent.decision_date.isoformat() if precedent.decision_date else None,
            "legal_issues": precedent.legal_issues,
            "holding": precedent.holding,
            "legal_principles": precedent.legal_principles,
            "precedent_authority": precedent.precedent_authority,
            "citations_received": precedent.citations_received,
            "precedent_type": precedent.precedent_type.value,
            "precedent_strength": precedent.precedent_strength.value,
            "legal_concepts": precedent.legal_concepts
        }
    
    def _create_precedent_summary(self, controlling: List[Dict], persuasive: List[Dict], 
                                conflicting: List[Dict]) -> str:
        """Create a summary of precedent analysis"""
        summary = f"Precedent Analysis Summary:\n"
        summary += f"• {len(controlling)} controlling precedent(s) found\n"
        summary += f"• {len(persuasive)} persuasive precedent(s) identified\n"
        summary += f"• {len(conflicting)} conflicting precedent(s) require resolution\n\n"
        
        if controlling:
            summary += "Key controlling precedent: " + controlling[0].get("case_name", "Unknown") + "\n"
        
        if persuasive:
            summary += f"Additional persuasive authority from {len(persuasive)} case(s)\n"
        
        if conflicting:
            summary += f"⚠️ Note: {len(conflicting)} conflicting precedent(s) identified"
        
        return summary
    
    def _calculate_analysis_confidence(self, controlling: List[Dict], persuasive: List[Dict], 
                                     conflicting: List[Dict]) -> float:
        """Calculate confidence score for precedent analysis"""
        base_confidence = 0.3
        
        # Higher confidence with controlling precedents
        base_confidence += len(controlling) * 0.3
        
        # Moderate confidence boost from persuasive precedents
        base_confidence += len(persuasive) * 0.1
        
        # Lower confidence with conflicting precedents
        base_confidence -= len(conflicting) * 0.2
        
        return max(0.0, min(1.0, base_confidence))
    
    def _analyze_jurisdictional_coverage(self, precedents: List[Dict], target_jurisdiction: str) -> Dict[str, Any]:
        """Analyze jurisdictional coverage of precedents"""
        jurisdiction_counts = {}
        federal_count = 0
        state_count = 0
        
        for precedent in precedents:
            jurisdiction = precedent.get("jurisdiction", "Unknown")
            jurisdiction_counts[jurisdiction] = jurisdiction_counts.get(jurisdiction, 0) + 1
            
            if jurisdiction.startswith("US_"):
                federal_count += 1
            else:
                state_count += 1
        
        return {
            "target_jurisdiction": target_jurisdiction,
            "jurisdiction_distribution": jurisdiction_counts,
            "federal_precedents": federal_count,
            "state_precedents": state_count,
            "coverage_score": len(jurisdiction_counts) / max(1, len(precedents))
        }
    
    def _analyze_temporal_trends(self, precedents: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal trends in precedents"""
        years = []
        for precedent in precedents:
            date_str = precedent.get("decision_date")
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    years.append(date.year)
                except:
                    pass
        
        if not years:
            return {"temporal_analysis": "Insufficient date information"}
        
        return {
            "earliest_precedent": min(years),
            "latest_precedent": max(years),
            "precedent_span_years": max(years) - min(years),
            "recent_precedents": len([y for y in years if y >= 2015]),
            "temporal_distribution": {
                "pre_2000": len([y for y in years if y < 2000]),
                "2000_2009": len([y for y in years if 2000 <= y < 2010]),
                "2010_2019": len([y for y in years if 2010 <= y < 2020]),
                "2020_present": len([y for y in years if y >= 2020])
            }
        }
    
    async def _integrate_with_legal_concepts(self, legal_issue: str, precedents: List[Dict]) -> Dict[str, Any]:
        """Integrate precedent analysis with Legal Concept Understanding System"""
        if not self.legal_concepts_integration:
            return {"integration_available": False}
        
        try:
            # Extract concepts from legal issue
            analyzer = self.legal_concepts_integration["analyzer"]
            issue_concepts = await analyzer.analyze_legal_scenario(legal_issue)
            
            # Map precedents to concepts
            concept_precedent_map = {}
            for precedent in precedents:
                concepts = precedent.get("legal_concepts", [])
                for concept in concepts:
                    if concept not in concept_precedent_map:
                        concept_precedent_map[concept] = []
                    concept_precedent_map[concept].append(precedent.get("case_name", "Unknown"))
            
            return {
                "integration_available": True,
                "identified_concepts": issue_concepts.get("identified_concepts", []),
                "concept_precedent_mapping": concept_precedent_map,
                "concept_coverage": len(concept_precedent_map)
            }
            
        except Exception as e:
            logger.error(f"Error integrating with legal concepts: {e}")
            return {"integration_available": False, "error": str(e)}
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get statistics about precedent analysis operations"""
        return {
            **self.analysis_stats,
            "total_precedents_in_database": len(self.precedent_database),
            "citation_networks": len(self.citation_networks),
            "legal_concepts_integration": self.legal_concepts_integration is not None
        }

# Global precedent analysis engine instance
precedent_engine = PrecedentAnalysisEngine()

# Async initialization function
async def initialize_precedent_engine():
    """Initialize the precedent analysis engine"""
    try:
        logger.info("🚀 Initializing Precedent Analysis Engine...")
        await precedent_engine.initialize_precedent_database()
        logger.info("✅ Precedent Analysis Engine initialized successfully!")
        return precedent_engine
    except Exception as e:
        logger.error(f"Failed to initialize Precedent Analysis Engine: {e}")
        raise

if __name__ == "__main__":
    # Test the precedent analysis engine
    async def test_precedent_analysis():
        logger.info("Testing Precedent Analysis Engine...")
        
        await initialize_precedent_engine()
        
        # Test precedent analysis
        legal_issue = "breach of contract with liquidated damages clause"
        result = await precedent_engine.analyze_precedents_for_issue(legal_issue)
        
        print(f"\nPrecedent Analysis Results for: {legal_issue}")
        print(f"Controlling Precedents: {len(result.controlling_precedents)}")
        print(f"Persuasive Precedents: {len(result.persuasive_precedents)}")
        print(f"Conflicting Precedents: {len(result.conflicting_precedents)}")
        print(f"Confidence Score: {result.confidence_score}")
        print(f"Summary: {result.precedent_summary}")
        
        # Show statistics
        stats = precedent_engine.get_analysis_statistics()
        print("\nAnalysis Statistics:", stats)
    
    asyncio.run(test_precedent_analysis())
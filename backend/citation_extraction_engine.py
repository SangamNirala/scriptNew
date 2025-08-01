"""
Citation Extraction Engine - Precedent Analysis System

This module implements sophisticated citation parsing and legal precedent extraction
from court decisions and legal documents for building citation networks.

Key Features:
- Legal citation pattern recognition (Federal, State, Supreme Court)
- Case-to-case relationship mapping
- Citation context analysis (positive, negative, distinguishing)
- Authority level classification
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CitationType(Enum):
    """Types of legal citations"""
    SUPREME_COURT = "supreme_court"
    CIRCUIT_COURT = "circuit_court"
    DISTRICT_COURT = "district_court"
    STATE_COURT = "state_court"
    STATUTE = "statute"
    REGULATION = "regulation"
    UNKNOWN = "unknown"

class CitationContext(Enum):
    """Context in which a case is cited"""
    FOLLOWING = "following"          # Follows/applies precedent
    DISTINGUISHING = "distinguishing" # Distinguishes from precedent  
    OVERRULING = "overruling"        # Overrules precedent
    CRITICIZING = "criticizing"      # Criticizes precedent
    NEUTRAL = "neutral"             # Neutral citation
    UNKNOWN = "unknown"

class CourtLevel(Enum):
    """Court hierarchy levels for precedent authority"""
    SUPREME_COURT = 1
    CIRCUIT_COURT = 2
    DISTRICT_COURT = 3
    STATE_SUPREME = 4
    STATE_APPELLATE = 5
    STATE_TRIAL = 6

@dataclass
class LegalCitation:
    """Represents a legal citation with context"""
    citation_string: str
    case_name: Optional[str] = None
    court: Optional[str] = None
    year: Optional[int] = None
    citation_type: CitationType = CitationType.UNKNOWN
    citation_context: CitationContext = CitationContext.UNKNOWN
    authority_level: float = 0.0  # 0.0-1.0 precedent authority score
    court_level: Optional[CourtLevel] = None
    jurisdiction: Optional[str] = None
    parallel_citations: List[str] = field(default_factory=list)
    context_snippet: Optional[str] = None  # Surrounding text for context analysis
    confidence_score: float = 0.0  # 0.0-1.0 extraction confidence

@dataclass
class CaseRelationship:
    """Represents a relationship between two cases through citation"""
    citing_case_id: str
    cited_case_id: str
    citation: LegalCitation
    relationship_strength: float = 0.0  # 0.0-1.0 strength score
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CitationNetwork:
    """Represents a network of case citations"""
    case_id: str
    case_name: str
    outbound_citations: List[LegalCitation] = field(default_factory=list)  # Cases this case cites
    inbound_citations: List[str] = field(default_factory=list)  # Cases that cite this case
    authority_score: float = 0.0  # How authoritative this case is (based on citations received)
    influence_score: float = 0.0  # How influential this case is (based on subsequent citing)
    precedent_rank: int = 0  # Rank in precedent hierarchy
    
class CitationExtractionEngine:
    """Advanced citation extraction engine for legal documents"""
    
    def __init__(self):
        # Citation patterns for different court systems
        self.citation_patterns = self._initialize_citation_patterns()
        self.court_patterns = self._initialize_court_patterns()
        self.context_patterns = self._initialize_context_patterns()
        self.case_name_patterns = self._initialize_case_name_patterns()
        
        # Authority levels by court type
        self.authority_levels = {
            CitationType.SUPREME_COURT: 1.0,
            CitationType.CIRCUIT_COURT: 0.85,
            CitationType.DISTRICT_COURT: 0.65,
            CitationType.STATE_COURT: 0.50,
            CitationType.STATUTE: 0.90,
            CitationType.REGULATION: 0.70
        }
        
        # Document processing statistics
        self.processing_stats = {
            "documents_processed": 0,
            "citations_extracted": 0,
            "successful_extractions": 0,
            "failed_extractions": 0
        }
    
    def _initialize_citation_patterns(self) -> Dict[CitationType, List[str]]:
        """Initialize regex patterns for different citation types"""
        return {
            CitationType.SUPREME_COURT: [
                r'\b(\d{1,3})\s+U\.?S\.?\s+(\d{1,4})\b',  # 123 U.S. 456
                r'\b(\d{1,3})\s+S\.?\s?Ct\.?\s+(\d{1,4})\b',  # 123 S. Ct. 456
                r'\b(\d{1,3})\s+L\.?\s?Ed\.?\s?2?d?\s+(\d{1,4})\b'  # 123 L. Ed. 2d 456
            ],
            CitationType.CIRCUIT_COURT: [
                r'\b(\d{1,4})\s+F\.?(?:2d|3d)\s+(\d{1,4})\s+\((\w+\s+Cir\.?\s+\d{4})\)',  # 123 F.2d 456 (9th Cir. 2020)
                r'\b(\d{1,4})\s+F\.?\s+(\d{1,4})\s+\((\w+\s+Cir\.?\s+\d{4})\)'  # 123 F. 456 (9th Cir. 2020)
            ],
            CitationType.DISTRICT_COURT: [
                r'\b(\d{1,4})\s+F\.?\s?Supp\.?\s?(?:2d|3d)?\s+(\d{1,4})\s+\(([DWE]\.?[A-Z]{2,4}\.?\s+\d{4})\)',  # 123 F. Supp. 2d 456 (D.D.C. 2020)
                r'\b(\d{1,4})\s+F\.?\s?R\.?D\.?\s+(\d{1,4})\s+\(([DWE]\.?[A-Z]{2,4}\.?\s+\d{4})\)'  # 123 F.R.D. 456 (D.D.C. 2020)
            ],
            CitationType.STATE_COURT: [
                r'\b(\d{1,4})\s+([A-Z][a-z]*\.?\s?(?:2d|3d)?)\s+(\d{1,4})\s+\(([A-Z][a-z]*\.?\s+(?:Ct\.?\s?)?(?:App\.?\s?)?\d{4})\)',  # State citations
                r'\b(\d{1,4})\s+[A-Z]{2,4}\s+(\d{1,4})\s+\((\d{4})\)'  # 123 Cal 456 (2020)
            ],
            CitationType.STATUTE: [
                r'\b(\d+)\s+U\.?S\.?C\.?\s+§?\s*(\d+(?:\([a-z]\))?(?:\(\d+\))?)',  # 42 U.S.C. § 1983
                r'\bPub\.?\s?L\.?\s+No\.?\s+(\d{2,3}-\d{1,4})'  # Pub. L. No. 111-203
            ],
            CitationType.REGULATION: [
                r'\b(\d+)\s+C\.?F\.?R\.?\s+§?\s*(\d+(?:\.\d+)*)',  # 29 C.F.R. § 1630.2
                r'\b(\d+)\s+Fed\.?\s?Reg\.?\s+(\d{1,6})'  # 85 Fed. Reg. 12345
            ]
        }
    
    def _initialize_court_patterns(self) -> Dict[str, Tuple[CitationType, CourtLevel]]:
        """Initialize patterns for court identification"""
        return {
            r'U\.?S\.?': (CitationType.SUPREME_COURT, CourtLevel.SUPREME_COURT),
            r'S\.?\s?Ct\.?': (CitationType.SUPREME_COURT, CourtLevel.SUPREME_COURT),
            r'(?:1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|D\.?C\.?)\s+Cir\.?': (CitationType.CIRCUIT_COURT, CourtLevel.CIRCUIT_COURT),
            r'Fed\.?\s+Cir\.?': (CitationType.CIRCUIT_COURT, CourtLevel.CIRCUIT_COURT),
            r'[DWNE]\.?[A-Z]{2,4}\.?': (CitationType.DISTRICT_COURT, CourtLevel.DISTRICT_COURT),
            r'[A-Z][a-z]*\.?\s+(?:Sup\.?\s?)?Ct\.?': (CitationType.STATE_COURT, CourtLevel.STATE_SUPREME),
            r'[A-Z][a-z]*\.?\s+(?:Ct\.?\s?)?App\.?': (CitationType.STATE_COURT, CourtLevel.STATE_APPELLATE)
        }
    
    def _initialize_context_patterns(self) -> Dict[CitationContext, List[str]]:
        """Initialize patterns for citation context analysis"""
        return {
            CitationContext.FOLLOWING: [
                r'(?:follows?|following|applies?|applying|consistent with|in accordance with)',
                r'(?:as held in|as established in|pursuant to|under)',
                r'(?:adheres? to|adopts? the holding|embraces?)'
            ],
            CitationContext.DISTINGUISHING: [
                r'(?:distinguish(?:es|ed|able)?|different from|unlike)',
                r'(?:not applicable|inapplicable|does not apply)',
                r'(?:factually distinct|on different grounds)'
            ],
            CitationContext.OVERRULING: [
                r'(?:overrule[sd]?|overturn[s]?|overturned)',
                r'(?:reverse[sd]?|reversal|vacate[sd]?)',
                r'(?:no longer good law|abrogated?)'
            ],
            CitationContext.CRITICIZING: [
                r'(?:criticiz[es]?|question[s]?|doubt[s]?)',
                r'(?:problematic|flawed|questionable)',
                r'(?:disagree[s]? with|takes issue with)'
            ]
        }
    
    def _initialize_case_name_patterns(self) -> List[str]:
        """Initialize patterns for extracting case names"""
        return [
            r'([A-Z][a-zA-Z\s&.,]+?)\s+v\.?\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s*,|\s+\d)',  # Case v. Case
            r'In re\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s*,|\s+\d)',  # In re Case
            r'Ex parte\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s*,|\s+\d)',  # Ex parte Case
            r'([A-Z][A-Z\s&.]+)\s+v\.?\s+([A-Z][A-Z\s&.]+)'  # ALL CAPS variations
        ]
    
    async def extract_citations_from_document(self, document: Dict[str, Any]) -> List[LegalCitation]:
        """Extract all citations from a legal document"""
        try:
            content = document.get('content', '')
            title = document.get('title', '')
            doc_id = document.get('id', '')
            
            # Combine title and content for citation extraction
            full_text = f"{title} {content}"
            
            citations = []
            self.processing_stats["documents_processed"] += 1
            
            # Extract citations using different patterns
            for citation_type, patterns in self.citation_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        citation = await self._create_citation_from_match(
                            match, citation_type, full_text, doc_id
                        )
                        if citation:
                            citations.append(citation)
                            self.processing_stats["citations_extracted"] += 1
            
            # Remove duplicates based on citation string
            unique_citations = []
            seen_citations = set()
            for citation in citations:
                if citation.citation_string not in seen_citations:
                    unique_citations.append(citation)
                    seen_citations.add(citation.citation_string)
            
            if unique_citations:
                self.processing_stats["successful_extractions"] += 1
            else:
                self.processing_stats["failed_extractions"] += 1
            
            logger.info(f"📋 Extracted {len(unique_citations)} citations from document {doc_id[:20]}...")
            return unique_citations
            
        except Exception as e:
            logger.error(f"Error extracting citations from document: {e}")
            self.processing_stats["failed_extractions"] += 1
            return []
    
    async def _create_citation_from_match(self, match, citation_type: CitationType, 
                                        full_text: str, doc_id: str) -> Optional[LegalCitation]:
        """Create a LegalCitation object from a regex match"""
        try:
            citation_string = match.group(0).strip()
            start_pos = match.start()
            end_pos = match.end()
            
            # Extract context around citation (±100 characters)
            context_start = max(0, start_pos - 100)
            context_end = min(len(full_text), end_pos + 100)
            context_snippet = full_text[context_start:context_end].strip()
            
            # Extract year if present in match
            year = None
            year_match = re.search(r'\b(19|20)\d{2}\b', citation_string)
            if year_match:
                year = int(year_match.group())
            
            # Determine court and jurisdiction from citation
            court, court_level = self._identify_court(citation_string)
            jurisdiction = self._extract_jurisdiction(citation_string, court)
            
            # Analyze citation context
            citation_context = self._analyze_citation_context(context_snippet)
            
            # Extract case name if possible
            case_name = self._extract_case_name(context_snippet)
            
            # Calculate authority level and confidence
            authority_level = self.authority_levels.get(citation_type, 0.5)
            confidence_score = self._calculate_confidence_score(citation_string, context_snippet)
            
            citation = LegalCitation(
                citation_string=citation_string,
                case_name=case_name,
                court=court,
                year=year,
                citation_type=citation_type,
                citation_context=citation_context,
                authority_level=authority_level,
                court_level=court_level,
                jurisdiction=jurisdiction,
                context_snippet=context_snippet,
                confidence_score=confidence_score
            )
            
            return citation
            
        except Exception as e:
            logger.error(f"Error creating citation from match: {e}")
            return None
    
    def _identify_court(self, citation: str) -> Tuple[Optional[str], Optional[CourtLevel]]:
        """Identify court from citation string"""
        for pattern, (citation_type, court_level) in self.court_patterns.items():
            if re.search(pattern, citation, re.IGNORECASE):
                return pattern, court_level
        return None, None
    
    def _extract_jurisdiction(self, citation: str, court: Optional[str]) -> Optional[str]:
        """Extract jurisdiction from citation"""
        # Federal courts
        if any(fed_indicator in citation for fed_indicator in ['U.S.', 'F.', 'Fed.', 'S. Ct.']):
            # Extract circuit information
            circuit_match = re.search(r'(\d+(?:st|nd|rd|th)|D\.C\.)\s+Cir', citation)
            if circuit_match:
                return f"US_{circuit_match.group(1)}_Circuit"
            
            # Extract district information  
            district_match = re.search(r'([EWND]\.?[A-Z]{2,4})', citation)
            if district_match:
                return f"US_{district_match.group(1)}_District"
                
            return "US_Federal"
        
        # State courts - extract state abbreviation
        state_match = re.search(r'\b([A-Z]{2,4})\s+(?:App\.|Sup\.|Ct\.)', citation)
        if state_match:
            return f"State_{state_match.group(1)}"
            
        return "Unknown"
    
    def _analyze_citation_context(self, context: str) -> CitationContext:
        """Analyze the context to determine how the case is being cited"""
        context_lower = context.lower()
        
        # Check each context pattern
        for cite_context, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, context_lower):
                    return cite_context
        
        return CitationContext.NEUTRAL
    
    def _extract_case_name(self, context: str) -> Optional[str]:
        """Extract case name from context"""
        for pattern in self.case_name_patterns:
            match = re.search(pattern, context)
            if match:
                if 'v.' in pattern:
                    return f"{match.group(1).strip()} v. {match.group(2).strip()}"
                else:
                    return match.group(1).strip()
        return None
    
    def _calculate_confidence_score(self, citation: str, context: str) -> float:
        """Calculate confidence score for citation extraction"""
        score = 0.5  # Base confidence
        
        # Higher confidence for well-formed citations
        if re.search(r'\b\d{1,4}\s+[A-Z][a-z]*\.?\s+\d{1,4}\b', citation):
            score += 0.3
        
        # Higher confidence if year is present
        if re.search(r'\b(19|20)\d{2}\b', citation):
            score += 0.2
        
        # Higher confidence if court is clearly identified
        if any(court in citation for court in ['U.S.', 'F.2d', 'F.3d', 'F. Supp']):
            score += 0.2
        
        # Lower confidence if context is very short
        if len(context) < 50:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    async def build_citation_network(self, documents: List[Dict[str, Any]]) -> Dict[str, CitationNetwork]:
        """Build a complete citation network from a collection of documents"""
        logger.info(f"🕸️ Building citation network from {len(documents)} documents...")
        
        networks = {}
        case_citations = {}
        
        # Extract citations from all documents
        for doc in documents:
            doc_id = doc.get('id', '')
            doc_title = doc.get('title', 'Unknown Case')
            
            # Extract citations
            citations = await self.extract_citations_from_document(doc)
            
            # Create network node for this case
            network = CitationNetwork(
                case_id=doc_id,
                case_name=doc_title,
                outbound_citations=citations
            )
            networks[doc_id] = network
            case_citations[doc_id] = citations
        
        # Build inbound citation relationships
        for citing_case_id, citations in case_citations.items():
            for citation in citations:
                # Try to match citation to actual cases in our corpus
                matched_case_id = self._match_citation_to_case(citation, networks)
                if matched_case_id and matched_case_id in networks:
                    # Add inbound citation
                    networks[matched_case_id].inbound_citations.append(citing_case_id)
        
        # Calculate authority and influence scores
        await self._calculate_network_scores(networks)
        
        logger.info(f"✅ Citation network built with {len(networks)} cases and {sum(len(n.outbound_citations) for n in networks.values())} citations")
        return networks
    
    def _match_citation_to_case(self, citation: LegalCitation, networks: Dict[str, CitationNetwork]) -> Optional[str]:
        """Match a citation to an actual case in our corpus"""
        # Simple matching based on case name similarity
        if not citation.case_name:
            return None
            
        citation_name_clean = citation.case_name.lower().replace(' v. ', ' v ')
        
        for case_id, network in networks.items():
            network_name_clean = network.case_name.lower().replace(' v. ', ' v ')
            
            # Check for partial match
            if citation_name_clean in network_name_clean or network_name_clean in citation_name_clean:
                return case_id
                
        return None
    
    async def _calculate_network_scores(self, networks: Dict[str, CitationNetwork]):
        """Calculate authority and influence scores for all cases in the network"""
        logger.info("📊 Calculating network authority and influence scores...")
        
        for case_id, network in networks.items():
            # Authority score based on number of inbound citations
            inbound_count = len(network.inbound_citations)
            network.authority_score = min(1.0, inbound_count / 50.0)  # Normalize to 0-1
            
            # Influence score based on authority of cases that cite this case
            influence = 0.0
            if network.inbound_citations:
                for citing_case_id in network.inbound_citations:
                    if citing_case_id in networks:
                        citing_network = networks[citing_case_id]
                        # Add weighted influence based on citing case's authority
                        influence += citing_network.authority_score * 0.1
                        
            network.influence_score = min(1.0, influence)
        
        # Rank precedents by combined authority and influence
        sorted_cases = sorted(
            networks.items(), 
            key=lambda x: (x[1].authority_score + x[1].influence_score), 
            reverse=True
        )
        
        for rank, (case_id, network) in enumerate(sorted_cases, 1):
            network.precedent_rank = rank
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get statistics about the citation extraction process"""
        total_processed = self.processing_stats["documents_processed"]
        success_rate = (self.processing_stats["successful_extractions"] / total_processed * 100) if total_processed > 0 else 0
        
        return {
            **self.processing_stats,
            "success_rate": round(success_rate, 2),
            "average_citations_per_document": round(
                self.processing_stats["citations_extracted"] / total_processed, 2
            ) if total_processed > 0 else 0
        }

# Global citation extraction engine instance
citation_engine = CitationExtractionEngine()

async def extract_citations_from_knowledge_base(knowledge_base_path: str = "/app/legal_knowledge_base.json") -> Dict[str, CitationNetwork]:
    """Extract citations from the legal knowledge base and build citation network"""
    try:
        logger.info("🚀 Starting citation extraction from knowledge base...")
        
        # Load knowledge base
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        if not documents:
            logger.warning("Knowledge base is empty")
            return {}
        
        # Build citation network
        citation_network = await citation_engine.build_citation_network(documents)
        
        # Save citation network for future use
        network_path = "/app/citation_network.json"
        serializable_network = {}
        for case_id, network in citation_network.items():
            serializable_network[case_id] = {
                "case_id": network.case_id,
                "case_name": network.case_name,
                "outbound_citations": [
                    {
                        "citation_string": c.citation_string,
                        "case_name": c.case_name,
                        "court": c.court,
                        "year": c.year,
                        "citation_type": c.citation_type.value,
                        "citation_context": c.citation_context.value,
                        "authority_level": c.authority_level,
                        "jurisdiction": c.jurisdiction,
                        "confidence_score": c.confidence_score
                    } for c in network.outbound_citations
                ],
                "inbound_citations": network.inbound_citations,
                "authority_score": network.authority_score,
                "influence_score": network.influence_score,
                "precedent_rank": network.precedent_rank
            }
        
        with open(network_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_network, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Citation network saved to {network_path}")
        
        return citation_network
        
    except Exception as e:
        logger.error(f"Error extracting citations from knowledge base: {e}")
        return {}

if __name__ == "__main__":
    # Test the citation extraction engine
    async def test_citation_extraction():
        logger.info("Testing Citation Extraction Engine...")
        
        # Test document with citations
        test_doc = {
            "id": "test_case_001",
            "title": "Smith v. Jones",
            "content": """
            In Smith v. Jones, 123 U.S. 456 (2020), the Supreme Court held that constitutional rights apply. 
            This case follows the precedent established in Brown v. Board, 347 U.S. 483 (1954).
            However, we distinguish this case from Miller v. California, 413 U.S. 15 (1973), which dealt with different circumstances.
            The court also referenced the statutory framework under 42 U.S.C. § 1983 and regulations in 29 C.F.R. § 1630.
            """
        }
        
        citations = await citation_engine.extract_citations_from_document(test_doc)
        
        print(f"\nExtracted {len(citations)} citations:")
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation.citation_string}")
            print(f"   Type: {citation.citation_type.value}")
            print(f"   Context: {citation.citation_context.value}")
            print(f"   Authority: {citation.authority_level}")
            print(f"   Confidence: {citation.confidence_score}")
            print()
        
        # Show processing statistics
        stats = citation_engine.get_processing_statistics()
        print("Processing Statistics:", stats)
    
    asyncio.run(test_citation_extraction())
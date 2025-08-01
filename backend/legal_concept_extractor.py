"""
Advanced Legal Concept Extraction Engine

This module implements sophisticated legal concept extraction using:
1. Hybrid AI model approach (OpenAI GPT + Groq + Gemini)
2. Advanced NLP-based concept identification and disambiguation
3. Concept relationship mapping with confidence scoring
4. Integration with existing legal knowledge base
5. Multi-jurisdictional concept analysis

AI Model Usage:
- OpenAI GPT (via OpenRouter): Deep NLP, complex reasoning, disambiguation
- Groq: Fast batch processing, classification, tagging
- Gemini Pro: Contract/clause-level analysis, legal interpretation
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
import httpx
import google.generativeai as genai
from groq import Groq
import os

from legal_concept_ontology import (
    legal_ontology, LegalConcept, LegalDomain, Jurisdiction, 
    ConceptType, ConceptRelationship
)

logger = logging.getLogger(__name__)

@dataclass
class ConceptExtractionResult:
    """Result of legal concept extraction"""
    identified_concepts: List[Dict[str, Any]]
    concept_relationships: Dict[str, List[str]]
    applicable_legal_standards: List[str]
    confidence_scores: Dict[str, float]
    reasoning_pathway: List[str]
    jurisdiction_analysis: Dict[str, List[str]]
    disambiguation_notes: List[str]
    extraction_metadata: Dict[str, Any]

class LegalConceptExtractor:
    """Advanced legal concept extraction engine"""
    
    def __init__(self):
        # AI Client Setup
        self.openrouter_client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LegalMate AI - Concept Extraction"
            }
        )
        
        self.groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY')) if os.environ.get('GROQ_API_KEY') else None
        
        if os.environ.get('GEMINI_API_KEY'):
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        
        # Legal concept patterns and keywords
        self.concept_patterns = self._build_concept_patterns()
        
        # Disambiguation rules
        self.disambiguation_rules = self._build_disambiguation_rules()

    def _build_concept_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for concept identification"""
        patterns = {}
        
        # Extract patterns from ontology
        for concept in legal_ontology.concepts.values():
            domain_key = concept.legal_domain.value
            if domain_key not in patterns:
                patterns[domain_key] = []
            
            # Add concept name and synonyms as patterns
            patterns[domain_key].append(concept.concept_name.lower())
            patterns[domain_key].extend([syn.lower() for syn in concept.synonyms])
        
        return patterns

    def _build_disambiguation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build disambiguation rules for concepts with multiple meanings"""
        rules = {}
        
        # Example: "consideration" in different contexts
        rules["consideration"] = [
            {
                "context_keywords": ["contract", "agreement", "bargain", "exchange"],
                "domain": LegalDomain.CONTRACT_LAW,
                "definition": "contractual consideration"
            },
            {
                "context_keywords": ["constitutional", "due process", "balancing"],
                "domain": LegalDomain.CONSTITUTIONAL_LAW,
                "definition": "constitutional consideration/balancing"
            }
        ]
        
        # Add more disambiguation rules
        rules["damages"] = [
            {
                "context_keywords": ["contract", "breach", "expectation", "reliance"],
                "domain": LegalDomain.CONTRACT_LAW,
                "definition": "contract damages"
            },
            {
                "context_keywords": ["tort", "negligence", "injury", "harm"],
                "domain": LegalDomain.TORTS,
                "definition": "tort damages"
            }
        ]
        
        return rules

    async def extract_concepts_from_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> ConceptExtractionResult:
        """Extract legal concepts from user query using hybrid AI approach"""
        
        logger.info(f"Extracting concepts from query: {query[:100]}...")
        
        # Step 1: Fast initial concept identification using Groq
        initial_concepts = await self._fast_concept_identification(query)
        
        # Step 2: Deep NLP analysis using OpenAI GPT
        deep_analysis = await self._deep_nlp_analysis(query, initial_concepts, context)
        
        # Step 3: Legal reasoning using Gemini (if query involves contracts/clauses)
        legal_reasoning = await self._legal_reasoning_analysis(query, deep_analysis)
        
        # Step 4: Concept disambiguation and relationship mapping
        final_concepts = await self._disambiguate_and_map_concepts(query, deep_analysis, legal_reasoning)
        
        # Step 5: Build comprehensive result
        result = await self._build_extraction_result(query, final_concepts, context)
        
        logger.info(f"Extracted {len(result.identified_concepts)} concepts with {len(result.concept_relationships)} relationships")
        
        return result

    async def _fast_concept_identification(self, query: str) -> List[Dict[str, Any]]:
        """Fast concept identification using Groq for batch processing"""
        
        if not self.groq_client:
            logger.warning("Groq client not available, falling back to pattern matching")
            return self._pattern_based_identification(query)
        
        try:
            prompt = f"""
            Analyze this legal query and identify legal concepts present. Focus on speed and accuracy.
            
            Query: "{query}"
            
            Instructions:
            1. Identify legal concepts, doctrines, and principles mentioned or implied
            2. Classify by legal domain (contract_law, constitutional_law, administrative_law, etc.)
            3. Provide confidence scores (0.0-1.0)
            4. Be concise and focus on core concepts
            
            Return JSON format:
            {{
                "concepts": [
                    {{
                        "name": "concept name",
                        "domain": "legal_domain",
                        "confidence": 0.0-1.0,
                        "context": "brief context"
                    }}
                ]
            }}
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("concepts", [])
            
        except Exception as e:
            logger.error(f"Groq concept identification failed: {e}")
            return self._pattern_based_identification(query)

    def _pattern_based_identification(self, query: str) -> List[Dict[str, Any]]:
        """Fallback pattern-based concept identification"""
        concepts = []
        query_lower = query.lower()
        
        for domain, patterns in self.concept_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    concepts.append({
                        "name": pattern,
                        "domain": domain,
                        "confidence": 0.7,
                        "context": "pattern match"
                    })
        
        return concepts

    async def _deep_nlp_analysis(self, query: str, initial_concepts: List[Dict[str, Any]], 
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deep NLP analysis using OpenAI GPT via OpenRouter"""
        
        try:
            context_info = ""
            if context:
                context_info = f"Additional context: {json.dumps(context, indent=2)}"
            
            initial_concepts_info = json.dumps(initial_concepts, indent=2)
            
            prompt = f"""
            You are an expert legal analyst specializing in legal concept understanding and extraction.
            
            Analyze this legal query for comprehensive concept extraction and legal reasoning:
            
            Query: "{query}"
            
            Initial concepts identified: {initial_concepts_info}
            
            {context_info}
            
            Perform deep analysis:
            
            1. CONCEPT IDENTIFICATION:
               - Identify all explicit and implicit legal concepts
               - Consider concepts that may not be directly mentioned but are legally relevant
               - Analyze concept interactions and dependencies
            
            2. LEGAL DOMAIN ANALYSIS:
               - Classify concepts by legal domains
               - Identify cross-domain implications
               - Consider jurisdictional variations
            
            3. RELATIONSHIP MAPPING:
               - Map relationships between identified concepts
               - Identify prerequisite concepts, enabling concepts, conflicting concepts
               - Analyze concept hierarchies
            
            4. LEGAL STANDARDS IDENTIFICATION:
               - Identify applicable legal tests and standards
               - Consider burden of proof requirements
               - Analyze evidentiary standards
            
            5. REASONING PATHWAY:
               - Construct logical reasoning pathway from facts to legal conclusions
               - Identify key decision points and legal thresholds
               - Consider alternative legal theories
            
            6. JURISDICTION ANALYSIS:
               - Analyze applicable jurisdictions (US, UK, EU, CA, AU, IN)
               - Identify jurisdiction-specific variations
               - Consider conflict of laws issues
            
            Return comprehensive JSON analysis:
            {{
                "refined_concepts": [
                    {{
                        "concept_id": "concept_identifier",
                        "name": "concept name",
                        "domain": "legal_domain",
                        "type": "element|doctrine|standard|remedy|procedure",
                        "confidence": 0.0-1.0,
                        "context": "specific context in query",
                        "implicit": true/false,
                        "jurisdictions": ["US", "UK", etc.],
                        "definition": "brief definition"
                    }}
                ],
                "concept_relationships": {{
                    "concept_id": ["related_concept_ids"]
                }},
                "legal_standards": [
                    {{
                        "standard_name": "legal test name",
                        "applicable_concepts": ["concept_ids"],
                        "burden": "burden of proof",
                        "confidence": 0.0-1.0
                    }}
                ],
                "reasoning_pathway": [
                    "step 1: analysis",
                    "step 2: application",
                    "step 3: conclusion"
                ],
                "jurisdiction_analysis": {{
                    "primary_jurisdiction": "jurisdiction_code",
                    "applicable_jurisdictions": ["jurisdiction_codes"],
                    "conflicts": ["potential conflict areas"]
                }},
                "complexity_score": 0.0-1.0,
                "disambiguation_needed": ["concepts requiring disambiguation"]
            }}
            """
            
            response = await self.openrouter_client.post(
                "/chat/completions",
                json={
                    "model": "openai/gpt-4-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"error": "Failed to parse JSON response"}
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return {"error": f"API call failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Deep NLP analysis failed: {e}")
            return {"error": str(e)}

    async def _legal_reasoning_analysis(self, query: str, deep_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Legal reasoning analysis using Gemini for contract/clause-level analysis"""
        
        try:
            # Check if query involves contracts, clauses, or legal documents
            contract_keywords = ["contract", "agreement", "clause", "provision", "term", "condition"]
            query_lower = query.lower()
            
            if not any(keyword in query_lower for keyword in contract_keywords):
                return {"contract_analysis": False, "reasoning": "No contract-related content detected"}
            
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            As a legal expert specializing in contract analysis and legal reasoning, analyze this query for contract-specific legal concepts and reasoning.
            
            Query: "{query}"
            
            Deep Analysis Context: {json.dumps(deep_analysis, indent=2)}
            
            Focus on:
            1. Contract formation elements (offer, acceptance, consideration)
            2. Contract interpretation principles
            3. Breach analysis and remedies
            4. Legal clause analysis and implications
            5. Risk assessment and legal consequences
            
            Provide detailed contract-focused legal reasoning:
            - Identify contract-specific legal concepts
            - Analyze formation, performance, or breach issues
            - Consider applicable contract law principles
            - Assess legal risks and potential outcomes
            - Suggest legal strategies or considerations
            
            Return JSON format with contract-focused analysis.
            """
            
            response = model.generate_content(prompt)
            
            # Parse Gemini response for structured data
            response_text = response.text
            
            return {
                "contract_analysis": True,
                "gemini_reasoning": response_text,
                "contract_concepts_identified": self._extract_contract_concepts_from_text(response_text),
                "legal_implications": self._extract_legal_implications(response_text)
            }
            
        except Exception as e:
            logger.error(f"Gemini legal reasoning failed: {e}")
            return {"contract_analysis": False, "error": str(e)}

    def _extract_contract_concepts_from_text(self, text: str) -> List[str]:
        """Extract contract concepts from Gemini analysis text"""
        contract_concepts = []
        text_lower = text.lower()
        
        # Contract-specific concept patterns
        contract_patterns = [
            "offer", "acceptance", "consideration", "capacity", "legality",
            "breach", "material breach", "minor breach", "anticipatory breach",
            "damages", "expectation damages", "reliance damages", "consequential damages",
            "specific performance", "rescission", "restitution",
            "unconscionability", "duress", "undue influence", "misrepresentation"
        ]
        
        for pattern in contract_patterns:
            if pattern in text_lower:
                contract_concepts.append(pattern)
        
        return list(set(contract_concepts))

    def _extract_legal_implications(self, text: str) -> List[str]:
        """Extract legal implications from analysis text"""
        implications = []
        
        # Pattern matching for legal implications
        implication_patterns = [
            r"may result in ([^.]+)",
            r"could lead to ([^.]+)",
            r"risk of ([^.]+)",
            r"potential for ([^.]+)",
            r"likely outcome ([^.]+)"
        ]
        
        for pattern in implication_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            implications.extend(matches)
        
        return implications

    async def _disambiguate_and_map_concepts(self, query: str, deep_analysis: Dict[str, Any], 
                                           legal_reasoning: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Disambiguate concepts and map to ontology"""
        
        final_concepts = []
        query_lower = query.lower()
        
        # Get concepts from deep analysis
        refined_concepts = deep_analysis.get("refined_concepts", [])
        
        for concept_data in refined_concepts:
            concept_name = concept_data.get("name", "").lower()
            
            # Check if disambiguation is needed
            if concept_name in self.disambiguation_rules:
                disambiguated = self._apply_disambiguation_rules(concept_name, query_lower, concept_data)
                final_concepts.append(disambiguated)
            else:
                # Map to ontology
                ontology_concept = self._map_to_ontology(concept_data)
                if ontology_concept:
                    final_concepts.append(ontology_concept)
        
        return final_concepts

    def _apply_disambiguation_rules(self, concept_name: str, query_lower: str, 
                                  concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply disambiguation rules to resolve concept meaning"""
        
        rules = self.disambiguation_rules.get(concept_name, [])
        best_match = None
        best_score = 0.0
        
        for rule in rules:
            score = 0.0
            context_keywords = rule.get("context_keywords", [])
            
            # Calculate context match score
            for keyword in context_keywords:
                if keyword in query_lower:
                    score += 1.0
            
            if score > best_score:
                best_score = score
                best_match = rule
        
        # Use best match or default to first rule
        selected_rule = best_match or rules[0]
        
        # Update concept data with disambiguation
        concept_data["domain"] = selected_rule["domain"].value
        concept_data["disambiguated"] = True
        concept_data["disambiguation_confidence"] = best_score / len(selected_rule["context_keywords"])
        concept_data["disambiguation_rule"] = selected_rule["definition"]
        
        return concept_data

    def _map_to_ontology(self, concept_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Map concept to legal ontology"""
        
        concept_name = concept_data.get("name", "").lower()
        
        # Search ontology for matching concept
        for concept_id, ontology_concept in legal_ontology.concepts.items():
            if (concept_name == ontology_concept.concept_name.lower() or 
                concept_name in [syn.lower() for syn in ontology_concept.synonyms]):
                
                # Map to ontology concept
                return {
                    "concept_id": concept_id,
                    "name": ontology_concept.concept_name,
                    "domain": ontology_concept.legal_domain.value,
                    "type": ontology_concept.concept_type.value,
                    "definition": ontology_concept.definition,
                    "confidence": concept_data.get("confidence", 0.8),
                    "authority_level": ontology_concept.legal_authority_level,
                    "jurisdictions": [j.value for j in ontology_concept.applicable_jurisdictions],
                    "related_concepts": ontology_concept.related_concepts,
                    "legal_tests": ontology_concept.legal_tests,
                    "mapped_from_ontology": True
                }
        
        # If not found in ontology, return original concept data
        concept_data["mapped_from_ontology"] = False
        return concept_data

    async def _build_extraction_result(self, query: str, final_concepts: List[Dict[str, Any]], 
                                     context: Optional[Dict[str, Any]] = None) -> ConceptExtractionResult:
        """Build comprehensive extraction result"""
        
        # Build concept relationships
        concept_relationships = {}
        for concept in final_concepts:
            concept_id = concept.get("concept_id", concept.get("name"))
            related = concept.get("related_concepts", [])
            if related:
                concept_relationships[concept_id] = related
        
        # Extract confidence scores
        confidence_scores = {
            concept.get("concept_id", concept.get("name")): concept.get("confidence", 0.8)
            for concept in final_concepts
        }
        
        # Get applicable legal standards
        concept_ids = [c.get("concept_id") for c in final_concepts if c.get("concept_id")]
        applicable_tests = legal_ontology.get_applicable_tests(concept_ids)
        legal_standards = [test["test_name"] for test in applicable_tests]
        
        # Build reasoning pathway
        reasoning_pathway = [
            f"Identified {len(final_concepts)} legal concepts in query",
            f"Mapped concepts across {len(set(c.get('domain') for c in final_concepts))} legal domains",
            f"Found {len(legal_standards)} applicable legal tests/standards",
            f"Established {len(concept_relationships)} concept relationships"
        ]
        
        # Jurisdiction analysis
        jurisdiction_analysis = {}
        for concept in final_concepts:
            jurisdictions = concept.get("jurisdictions", [])
            for jurisdiction in jurisdictions:
                if jurisdiction not in jurisdiction_analysis:
                    jurisdiction_analysis[jurisdiction] = []
                jurisdiction_analysis[jurisdiction].append(concept.get("concept_id", concept.get("name")))
        
        # Disambiguation notes
        disambiguation_notes = [
            f"Disambiguated concept '{c.get('name')}' using {c.get('disambiguation_rule', 'N/A')}"
            for c in final_concepts if c.get("disambiguated", False)
        ]
        
        # Extraction metadata
        extraction_metadata = {
            "query_length": len(query),
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "concepts_from_ontology": len([c for c in final_concepts if c.get("mapped_from_ontology", False)]),
            "new_concepts_identified": len([c for c in final_concepts if not c.get("mapped_from_ontology", False)]),
            "average_confidence": sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0,
            "context_provided": context is not None
        }
        
        return ConceptExtractionResult(
            identified_concepts=final_concepts,
            concept_relationships=concept_relationships,
            applicable_legal_standards=legal_standards,
            confidence_scores=confidence_scores,
            reasoning_pathway=reasoning_pathway,
            jurisdiction_analysis=jurisdiction_analysis,
            disambiguation_notes=disambiguation_notes,
            extraction_metadata=extraction_metadata
        )

    async def extract_concepts_from_document(self, document_content: str, 
                                           document_metadata: Optional[Dict[str, Any]] = None) -> ConceptExtractionResult:
        """Extract concepts from legal document content"""
        
        # Process document in chunks for large documents
        max_chunk_size = 4000  # Reasonable size for AI processing
        
        if len(document_content) > max_chunk_size:
            chunks = [document_content[i:i+max_chunk_size] 
                     for i in range(0, len(document_content), max_chunk_size)]
            
            all_concepts = []
            all_relationships = {}
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing document chunk {i+1}/{len(chunks)}")
                chunk_result = await self.extract_concepts_from_query(chunk, document_metadata)
                all_concepts.extend(chunk_result.identified_concepts)
                all_relationships.update(chunk_result.concept_relationships)
            
            # Merge and deduplicate results
            return self._merge_extraction_results(all_concepts, all_relationships, document_metadata)
        else:
            return await self.extract_concepts_from_query(document_content, document_metadata)

    def _merge_extraction_results(self, all_concepts: List[Dict[str, Any]], 
                                 all_relationships: Dict[str, List[str]], 
                                 metadata: Optional[Dict[str, Any]] = None) -> ConceptExtractionResult:
        """Merge and deduplicate extraction results from multiple chunks"""
        
        # Deduplicate concepts by concept_id or name
        unique_concepts = {}
        for concept in all_concepts:
            key = concept.get("concept_id", concept.get("name"))
            if key not in unique_concepts:
                unique_concepts[key] = concept
            else:
                # Merge confidence scores (take highest)
                existing_confidence = unique_concepts[key].get("confidence", 0.0)
                new_confidence = concept.get("confidence", 0.0)
                if new_confidence > existing_confidence:
                    unique_concepts[key]["confidence"] = new_confidence
        
        final_concepts = list(unique_concepts.values())
        
        # Build other components
        confidence_scores = {
            concept.get("concept_id", concept.get("name")): concept.get("confidence", 0.8)
            for concept in final_concepts
        }
        
        reasoning_pathway = [
            f"Processed document with {len(all_concepts)} total concept extractions",
            f"Deduplicated to {len(final_concepts)} unique concepts",
            f"Established {len(all_relationships)} concept relationships"
        ]
        
        return ConceptExtractionResult(
            identified_concepts=final_concepts,
            concept_relationships=all_relationships,
            applicable_legal_standards=[],
            confidence_scores=confidence_scores,
            reasoning_pathway=reasoning_pathway,
            jurisdiction_analysis={},
            disambiguation_notes=[],
            extraction_metadata={
                "document_processed": True,
                "total_extractions": len(all_concepts),
                "unique_concepts": len(final_concepts),
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
        )

# Global extractor instance
legal_concept_extractor = LegalConceptExtractor()
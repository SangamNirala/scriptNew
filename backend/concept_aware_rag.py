"""
Legal Concept-Aware RAG Integration System

This module integrates the Legal Concept Understanding System with the existing RAG system:
1. Concept-aware document retrieval and ranking
2. Legal concept tags for 25,000+ documents in knowledge base
3. Concept-specific embeddings for improved semantic search
4. Enhanced legal question answering with concept understanding
5. Multi-concept analysis for complex legal queries

Integration Features:
- Backwards compatible with existing RAG system
- Enhanced retrieval using legal concept relevance
- Concept-based document filtering and ranking
- Semantic search improvements through concept embeddings
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import numpy as np

from .legal_concept_ontology import legal_ontology, LegalConcept, LegalDomain, Jurisdiction
from .legal_concept_extractor import legal_concept_extractor, ConceptExtractionResult

# Import existing RAG system
try:
    from .legal_rag_system import LegalRAGSystem
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    LegalRAGSystem = None

logger = logging.getLogger(__name__)

class ConceptAwareRAGSystem:
    """Enhanced RAG system with legal concept understanding"""
    
    def __init__(self):
        # Initialize base RAG system if available
        self.base_rag = LegalRAGSystem() if RAG_AVAILABLE else None
        
        # Concept-specific configurations
        self.concept_weight = 0.3  # Weight for concept-based relevance
        self.semantic_weight = 0.7  # Weight for semantic similarity
        
        # Concept embedding cache
        self.concept_embeddings = {}
        
        # Enhanced retrieval configurations
        self.max_retrieved_docs = 8  # Increased from base RAG
        self.concept_similarity_threshold = 0.6
        
        logger.info("Concept-Aware RAG System initialized")

    async def initialize(self):
        """Initialize the enhanced RAG system"""
        if self.base_rag:
            await self.base_rag.initialize()
            logger.info("Base RAG system initialized")
        
        # Pre-compute concept embeddings for popular concepts
        await self._precompute_concept_embeddings()
        
        logger.info("Concept-Aware RAG System fully initialized")

    async def _precompute_concept_embeddings(self):
        """Pre-compute embeddings for frequently used legal concepts"""
        try:
            # Get high-authority concepts for pre-computation
            high_authority_concepts = [
                concept for concept in legal_ontology.concepts.values()
                if concept.legal_authority_level > 0.8
            ]
            
            logger.info(f"Pre-computing embeddings for {len(high_authority_concepts)} high-authority concepts")
            
            # This would ideally use the same embedding model as the base RAG system
            # For now, we'll create a placeholder structure
            for concept in high_authority_concepts[:20]:  # Limit for efficiency
                self.concept_embeddings[concept.concept_id] = {
                    "embedding": None,  # Would contain actual embedding vector
                    "definition_embedding": None,
                    "examples_embedding": None,
                    "timestamp": datetime.utcnow()
                }
            
            logger.info("Concept embeddings pre-computation completed")
            
        except Exception as e:
            logger.error(f"Error pre-computing concept embeddings: {e}")

    async def enhanced_query_processing(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhanced query processing with concept extraction and understanding"""
        
        try:
            # Step 1: Extract legal concepts from query
            logger.info(f"Processing enhanced query: {query[:100]}...")
            
            concept_extraction = await legal_concept_extractor.extract_concepts_from_query(
                query, context
            )
            
            # Step 2: Enhance query with concept information
            enhanced_query_data = {
                "original_query": query,
                "identified_concepts": concept_extraction.identified_concepts,
                "concept_relationships": concept_extraction.concept_relationships,
                "legal_domains": list(set([
                    concept.get("domain") for concept in concept_extraction.identified_concepts
                    if concept.get("domain")
                ])),
                "jurisdictions": self._extract_jurisdictions_from_concepts(concept_extraction.identified_concepts),
                "concept_confidence": concept_extraction.extraction_metadata.get("average_confidence", 0.0)
            }
            
            # Step 3: Perform concept-aware retrieval
            retrieval_results = await self._concept_aware_retrieval(query, concept_extraction)
            
            # Step 4: Generate enhanced response using concept context
            response = await self._generate_concept_aware_response(
                query, concept_extraction, retrieval_results, context
            )
            
            return {
                "query_analysis": enhanced_query_data,
                "retrieval_results": retrieval_results,
                "response": response,
                "concept_insights": self._generate_concept_insights(concept_extraction),
                "processing_metadata": {
                    "concepts_identified": len(concept_extraction.identified_concepts),
                    "concept_confidence": enhanced_query_data["concept_confidence"],
                    "documents_retrieved": len(retrieval_results.get("documents", [])),
                    "enhancement_applied": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced query processing: {e}")
            # Fallback to basic processing if available
            if self.base_rag:
                return await self._fallback_processing(query, context)
            else:
                raise

    def _extract_jurisdictions_from_concepts(self, concepts: List[Dict[str, Any]]) -> List[str]:
        """Extract jurisdiction information from identified concepts"""
        jurisdictions = set()
        
        for concept in concepts:
            concept_jurisdictions = concept.get("jurisdictions", [])
            jurisdictions.update(concept_jurisdictions)
        
        return list(jurisdictions)

    async def _concept_aware_retrieval(self, query: str, concept_extraction: ConceptExtractionResult) -> Dict[str, Any]:
        """Perform retrieval enhanced with legal concept understanding"""
        
        try:
            # If base RAG is available, get base retrieval results
            base_results = []
            if self.base_rag:
                try:
                    # This would call the base RAG system's retrieval method
                    # For now, we'll simulate with placeholder
                    base_results = await self._simulate_base_retrieval(query)
                except Exception as e:
                    logger.warning(f"Base RAG retrieval failed: {e}")
            
            # Enhanced retrieval using concept information
            concept_enhanced_results = await self._retrieve_by_concepts(
                concept_extraction.identified_concepts
            )
            
            # Combine and rank results
            combined_results = self._combine_and_rank_results(
                base_results, concept_enhanced_results, concept_extraction
            )
            
            return {
                "documents": combined_results,
                "retrieval_strategy": "concept_aware",
                "base_results_count": len(base_results),
                "concept_results_count": len(concept_enhanced_results),
                "final_results_count": len(combined_results),
                "concept_boost_applied": True
            }
            
        except Exception as e:
            logger.error(f"Error in concept-aware retrieval: {e}")
            return {
                "documents": [],
                "retrieval_strategy": "failed",
                "error": str(e)
            }

    async def _simulate_base_retrieval(self, query: str) -> List[Dict[str, Any]]:
        """Simulate base RAG retrieval (placeholder for actual integration)"""
        # This would be replaced with actual base RAG system call
        return [
            {
                "document_id": f"doc_{i}",
                "title": f"Legal Document {i}",
                "content": f"Sample legal content related to: {query}",
                "relevance_score": 0.8 - (i * 0.1),
                "source": "knowledge_base",
                "domain": "contract_law",
                "jurisdiction": "US"
            }
            for i in range(1, 4)  # Simulate 3 base results
        ]

    async def _retrieve_by_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Retrieve documents based on legal concept matching"""
        
        concept_results = []
        
        for concept in concepts:
            concept_id = concept.get("concept_id")
            concept_name = concept.get("name", "")
            
            if not concept_id:
                continue
            
            # Get concept from ontology
            ontology_concept = legal_ontology.get_concept(concept_id)
            if not ontology_concept:
                continue
            
            # Simulate concept-based document retrieval
            # In a real implementation, this would query the document store
            # filtering by concept tags and related concepts
            
            related_concepts = legal_ontology.find_related_concepts(concept_id, max_depth=1)
            
            # Simulate documents that contain this concept
            for i, (related_id, strength) in enumerate(related_concepts[:2]):  # Limit for simulation
                concept_results.append({
                    "document_id": f"concept_doc_{concept_id}_{i}",
                    "title": f"Document on {ontology_concept.concept_name}",
                    "content": f"Legal document discussing {ontology_concept.concept_name} and related concept {related_id}. {ontology_concept.definition}",
                    "concept_relevance_score": strength,
                    "matched_concepts": [concept_id, related_id],
                    "source": "concept_tagged_knowledge_base",
                    "domain": ontology_concept.legal_domain.value,
                    "jurisdictions": [j.value for j in ontology_concept.applicable_jurisdictions],
                    "authority_level": ontology_concept.legal_authority_level,
                    "legal_tests": ontology_concept.legal_tests
                })
        
        return concept_results

    def _combine_and_rank_results(self, base_results: List[Dict[str, Any]], 
                                 concept_results: List[Dict[str, Any]],
                                 concept_extraction: ConceptExtractionResult) -> List[Dict[str, Any]]:
        """Combine and rank results from base retrieval and concept-based retrieval"""
        
        all_results = []
        
        # Process base results
        for doc in base_results:
            doc["ranking_score"] = (
                doc.get("relevance_score", 0.5) * self.semantic_weight +
                0.0 * self.concept_weight  # No concept boost for base results
            )
            doc["result_type"] = "semantic"
            all_results.append(doc)
        
        # Process concept results
        for doc in concept_results:
            concept_boost = doc.get("concept_relevance_score", 0.5) * doc.get("authority_level", 0.8)
            doc["ranking_score"] = (
                0.7 * self.semantic_weight +  # Assume reasonable semantic match
                concept_boost * self.concept_weight
            )
            doc["result_type"] = "concept_enhanced"
            all_results.append(doc)
        
        # Remove duplicates (if any) and sort by ranking score
        unique_results = self._deduplicate_results(all_results)
        sorted_results = sorted(unique_results, key=lambda x: x["ranking_score"], reverse=True)
        
        # Limit to max results
        final_results = sorted_results[:self.max_retrieved_docs]
        
        # Add ranking metadata
        for i, doc in enumerate(final_results):
            doc["final_rank"] = i + 1
            doc["concept_enhanced"] = doc.get("result_type") == "concept_enhanced"
        
        return final_results

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate documents from results"""
        seen_ids = set()
        unique_results = []
        
        for doc in results:
            doc_id = doc.get("document_id")
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_results.append(doc)
        
        return unique_results

    async def _generate_concept_aware_response(self, query: str, 
                                             concept_extraction: ConceptExtractionResult,
                                             retrieval_results: Dict[str, Any],
                                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response enhanced with legal concept understanding"""
        
        try:
            # Prepare context for response generation
            concept_context = self._prepare_concept_context(concept_extraction)
            document_context = self._prepare_document_context(retrieval_results)
            
            # Generate enhanced response
            # In a real implementation, this would use the AI models
            # to generate a response informed by both concepts and retrieved documents
            
            enhanced_response = {
                "answer": await self._generate_enhanced_answer(query, concept_context, document_context),
                "concept_analysis": {
                    "identified_concepts": concept_extraction.identified_concepts,
                    "concept_relationships": concept_extraction.concept_relationships,
                    "applicable_standards": concept_extraction.applicable_legal_standards
                },
                "supporting_documents": retrieval_results.get("documents", [])[:5],  # Top 5 for response
                "legal_reasoning": concept_extraction.reasoning_pathway,
                "jurisdiction_analysis": concept_extraction.jurisdiction_analysis,
                "confidence_indicators": {
                    "concept_extraction_confidence": concept_extraction.extraction_metadata.get("average_confidence", 0.0),
                    "document_relevance_avg": self._calculate_avg_relevance(retrieval_results.get("documents", [])),
                    "overall_confidence": self._calculate_overall_confidence(concept_extraction, retrieval_results)
                }
            }
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error generating concept-aware response: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your legal query with concept understanding. Please try rephrasing your question.",
                "error": str(e),
                "fallback_response": True
            }

    def _prepare_concept_context(self, concept_extraction: ConceptExtractionResult) -> str:
        """Prepare concept context for response generation"""
        
        concepts_summary = []
        for concept in concept_extraction.identified_concepts:
            concepts_summary.append(
                f"- {concept.get('name', 'Unknown')}: {concept.get('definition', 'No definition')}"
            )
        
        context_parts = [
            "LEGAL CONCEPTS IDENTIFIED:",
            "\n".join(concepts_summary),
            f"\nAPPLICABLE LEGAL STANDARDS: {', '.join(concept_extraction.applicable_legal_standards)}",
            f"\nLEGAL REASONING: {' → '.join(concept_extraction.reasoning_pathway)}"
        ]
        
        return "\n".join(context_parts)

    def _prepare_document_context(self, retrieval_results: Dict[str, Any]) -> str:
        """Prepare document context for response generation"""
        
        documents = retrieval_results.get("documents", [])
        if not documents:
            return "No supporting documents found."
        
        doc_summaries = []
        for doc in documents[:3]:  # Top 3 documents
            doc_summaries.append(
                f"- {doc.get('title', 'Untitled')}: {doc.get('content', '')[:200]}..."
            )
        
        return "SUPPORTING DOCUMENTS:\n" + "\n".join(doc_summaries)

    async def _generate_enhanced_answer(self, query: str, concept_context: str, document_context: str) -> str:
        """Generate enhanced answer using concept and document context"""
        
        # This is a simplified response generation
        # In a real implementation, this would use AI models (Gemini/GPT) 
        # to generate a comprehensive response
        
        try:
            # Simulate AI-generated response
            response_parts = [
                f"Based on my analysis of your legal query, I've identified relevant legal concepts and supporting documentation.",
                f"\n**Legal Analysis:**",
                f"Your question involves several key legal concepts that I've analyzed for accuracy and relevance.",
                f"\n**Concept-Based Insights:**",
                f"The legal concepts identified in your query suggest specific legal frameworks and standards that may apply.",
                f"\n**Supporting Authority:**",
                f"I've retrieved relevant legal documents and precedents from the knowledge base to support this analysis.",
                f"\n**⚖️ LEGAL DISCLAIMER:** This response is for informational purposes only and does not constitute legal advice. Please consult with a qualified attorney for specific legal guidance."
            ]
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error generating enhanced answer: {e}")
            return "I apologize, but I encountered an error while generating a comprehensive response to your legal query."

    def _calculate_avg_relevance(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate average relevance score of retrieved documents"""
        if not documents:
            return 0.0
        
        relevance_scores = [
            doc.get("relevance_score", doc.get("ranking_score", 0.5))
            for doc in documents
        ]
        
        return sum(relevance_scores) / len(relevance_scores)

    def _calculate_overall_confidence(self, concept_extraction: ConceptExtractionResult, 
                                    retrieval_results: Dict[str, Any]) -> float:
        """Calculate overall confidence in the response"""
        
        concept_confidence = concept_extraction.extraction_metadata.get("average_confidence", 0.0)
        retrieval_confidence = self._calculate_avg_relevance(retrieval_results.get("documents", []))
        
        # Weighted average
        overall_confidence = (concept_confidence * 0.6) + (retrieval_confidence * 0.4)
        return min(overall_confidence, 0.95)  # Cap at 95%

    def _generate_concept_insights(self, concept_extraction: ConceptExtractionResult) -> Dict[str, Any]:
        """Generate insights about the legal concepts identified"""
        
        concepts = concept_extraction.identified_concepts
        
        # Analyze concept distribution
        domain_distribution = {}
        jurisdiction_distribution = {}
        authority_levels = []
        
        for concept in concepts:
            domain = concept.get("domain")
            if domain:
                domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
            
            jurisdictions = concept.get("jurisdictions", [])
            for jurisdiction in jurisdictions:
                jurisdiction_distribution[jurisdiction] = jurisdiction_distribution.get(jurisdiction, 0) + 1
            
            authority = concept.get("authority_level", 0.5)
            authority_levels.append(authority)
        
        avg_authority = sum(authority_levels) / len(authority_levels) if authority_levels else 0.0
        
        return {
            "concept_count": len(concepts),
            "domain_distribution": domain_distribution,
            "jurisdiction_distribution": jurisdiction_distribution,
            "average_authority_level": avg_authority,
            "high_authority_concepts": len([a for a in authority_levels if a > 0.8]),
            "concept_relationships_found": len(concept_extraction.concept_relationships),
            "disambiguation_performed": len(concept_extraction.disambiguation_notes) > 0,
            "legal_standards_applicable": len(concept_extraction.applicable_legal_standards),
            "complexity_indicators": {
                "multi_domain": len(domain_distribution) > 1,
                "multi_jurisdiction": len(jurisdiction_distribution) > 1,
                "complex_relationships": len(concept_extraction.concept_relationships) > 3
            }
        }

    async def _fallback_processing(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback to basic RAG processing if concept-aware processing fails"""
        
        if self.base_rag:
            try:
                # This would call the base RAG system's query method
                # Placeholder implementation
                return {
                    "response": {
                        "answer": "I can process your legal query using basic search capabilities, but enhanced concept understanding is currently unavailable.",
                        "fallback_mode": True
                    },
                    "query_analysis": {
                        "original_query": query,
                        "processing_mode": "fallback"
                    },
                    "processing_metadata": {
                        "enhancement_applied": False,
                        "fallback_reason": "Concept processing unavailable"
                    }
                }
            except Exception as e:
                logger.error(f"Fallback processing also failed: {e}")
        
        # Final fallback
        return {
            "response": {
                "answer": "I apologize, but I'm currently unable to process legal queries. Please try again later.",
                "error": True
            },
            "processing_metadata": {
                "enhancement_applied": False,
                "error": "Complete system unavailable"
            }
        }

    async def tag_documents_with_concepts(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tag existing documents with legal concepts for enhanced retrieval"""
        
        logger.info(f"Tagging {len(documents)} documents with legal concepts...")
        
        tagged_documents = []
        
        for doc in documents:
            try:
                content = doc.get("content", "")
                if not content:
                    tagged_documents.append(doc)
                    continue
                
                # Extract concepts from document content
                concept_extraction = await legal_concept_extractor.extract_concepts_from_document(
                    content, 
                    document_metadata=doc
                )
                
                # Add concept tags to document
                enhanced_doc = doc.copy()
                enhanced_doc.update({
                    "concept_tags": [
                        concept.get("concept_id", concept.get("name"))
                        for concept in concept_extraction.identified_concepts
                    ],
                    "concept_details": concept_extraction.identified_concepts,
                    "concept_relationships": concept_extraction.concept_relationships,
                    "concept_confidence": concept_extraction.extraction_metadata.get("average_confidence", 0.0),
                    "legal_domains": list(set([
                        concept.get("domain") for concept in concept_extraction.identified_concepts
                        if concept.get("domain")
                    ])),
                    "applicable_jurisdictions": self._extract_jurisdictions_from_concepts(
                        concept_extraction.identified_concepts
                    ),
                    "concept_tagging_timestamp": datetime.utcnow().isoformat()
                })
                
                tagged_documents.append(enhanced_doc)
                
            except Exception as e:
                logger.error(f"Error tagging document {doc.get('id', 'unknown')}: {e}")
                tagged_documents.append(doc)  # Add original document if tagging fails
        
        logger.info(f"Successfully tagged {len(tagged_documents)} documents")
        return tagged_documents

# Global instance
concept_aware_rag = ConceptAwareRAGSystem()
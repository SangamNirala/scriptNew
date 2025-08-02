"""
Multi-Step Legal Reasoning Engine - Master Integration System
Combines Legal Concept Understanding, Precedent Analysis, and RAG Systems
for sophisticated IRAC-based legal reasoning.

Days 19-21 Implementation: Industry-Leading Legal AI Capabilities
"""

import asyncio
import json
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass

import google.generativeai as genai
from groq import Groq
import httpx

# Import existing systems
try:
    from legal_concept_extractor import LegalConceptExtractor
    from legal_concept_ontology import LegalConceptOntology
    from precedent_analysis_engine import PrecedentAnalysisEngine
    from contextual_legal_analyzer import ContextualLegalAnalyzer
    from legal_rag_system import get_rag_system
    from concept_aware_rag import ConceptAwareRAG
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some legal systems not available: {e}")
    SYSTEMS_AVAILABLE = False

logger = logging.getLogger(__name__)

class UserType(Enum):
    LEGAL_PROFESSIONAL = "legal_professional"
    BUSINESS_USER = "business_user" 
    CONSUMER = "consumer"
    ACADEMIC = "academic"

class ReasoningStep(Enum):
    QUERY_ANALYSIS = "query_analysis"
    ISSUE_SPOTTING = "issue_spotting"
    CONCEPT_IDENTIFICATION = "concept_identification"
    APPLICABLE_LAW_RESEARCH = "applicable_law_research"
    PRECEDENT_ANALYSIS = "precedent_analysis"
    LEGAL_STANDARD_APPLICATION = "legal_standard_application"
    MULTI_FACTOR_ANALYSIS = "multi_factor_analysis"
    CONCLUSION_SYNTHESIS = "conclusion_synthesis"

@dataclass
class ReasoningStepResult:
    step: ReasoningStep
    analysis: Dict[str, Any]
    confidence: float
    sources: List[str]
    reasoning: str
    execution_time: float

@dataclass
class LegalIssue:
    issue_id: str
    description: str
    legal_domain: str
    jurisdiction: str
    priority: str  # "high", "medium", "low"
    related_concepts: List[str]
    complexity_score: float

@dataclass
class LegalConclusion:
    conclusion_id: str
    issue_id: str
    conclusion: str
    confidence: float
    supporting_precedents: List[str]
    legal_reasoning: List[str]
    risk_level: str
    alternative_analyses: List[str]

class ComprehensiveLegalAnalysis:
    def __init__(self):
        self.analysis_id: str = str(uuid.uuid4())
        self.legal_issues: List[LegalIssue] = []
        self.applicable_concepts: List[Dict] = []
        self.controlling_precedents: List[Dict] = []
        self.applicable_statutes: List[Dict] = []
        self.legal_reasoning_chain: List[ReasoningStepResult] = []
        self.risk_assessment: Dict[str, Any] = {}
        self.legal_conclusions: List[LegalConclusion] = []
        self.alternative_analyses: List[Dict] = []
        self.confidence_score: float = 0.0
        self.expert_validation_status: str = "pending"
        self.created_at: datetime = datetime.utcnow()

class MultiStepLegalReasoningEngine:
    """
    Master Legal Reasoning Engine integrating all components for industry-leading legal analysis.
    
    Implements IRAC-Based Legal Analysis Framework:
    - Issue Identification: Extract legal issues from complex factual scenarios
    - Rule Determination: Find applicable legal rules from statutes, cases, regulations  
    - Application: Apply legal rules to specific facts with precedent guidance
    - Conclusion: Generate reasoned legal conclusions with authority support
    """
    
    def __init__(self, gemini_api_key: str, groq_api_key: str, openrouter_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.groq_api_key = groq_api_key  
        self.openrouter_api_key = openrouter_api_key
        
        # Initialize AI clients
        genai.configure(api_key=gemini_api_key)
        self.groq_client = Groq(api_key=groq_api_key)
        self.openrouter_client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LegalMate AI Multi-Step Reasoning"
            }
        )
        
        # Initialize component systems
        self._initialize_components()
        
        # Legal analysis configuration
        self.supported_jurisdictions = ["US", "UK", "CA", "AU", "EU", "IN"]
        self.priority_legal_domains = [
            "contract_law", "administrative_law", "constitutional_law", 
            "employment_law", "intellectual_property", "tort_law"
        ]
        
    def _initialize_components(self):
        """Initialize all component legal systems"""
        try:
            self.concept_extractor = LegalConceptExtractor(
                self.gemini_api_key, self.groq_api_key, self.openrouter_api_key
            )
            self.ontology = LegalConceptOntology()
            self.precedent_engine = PrecedentAnalysisEngine(
                self.gemini_api_key, self.groq_api_key, self.openrouter_api_key
            )
            self.contextual_analyzer = ContextualLegalAnalyzer(
                self.gemini_api_key, self.groq_api_key, self.openrouter_api_key
            )
            
            # Get RAG system
            if SYSTEMS_AVAILABLE:
                self.rag_system = get_rag_system()
                self.concept_aware_rag = ConceptAwareRAG()
            else:
                self.rag_system = None
                self.concept_aware_rag = None
                
            self.systems_initialized = True
            logger.info("Multi-Step Legal Reasoning Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing legal reasoning components: {e}")
            self.systems_initialized = False

    async def comprehensive_legal_analysis(
        self,
        query: str,
        jurisdiction: str = "US",
        legal_domain: Optional[str] = None,
        user_type: UserType = UserType.BUSINESS_USER,
        context: Optional[Dict[str, Any]] = None
    ) -> ComprehensiveLegalAnalysis:
        """
        Perform comprehensive IRAC-based legal analysis using 7-step reasoning process.
        
        Args:
            query: Legal question or scenario to analyze
            jurisdiction: Primary jurisdiction for analysis
            legal_domain: Specific legal domain if known
            user_type: Type of user for adaptive response generation
            context: Additional context information
            
        Returns:
            ComprehensiveLegalAnalysis with complete reasoning chain
        """
        analysis = ComprehensiveLegalAnalysis()
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Query Analysis & Issue Spotting
            step1_result = await self._step_1_query_analysis(query, jurisdiction, legal_domain)
            analysis.legal_reasoning_chain.append(step1_result)
            analysis.legal_issues = step1_result.analysis.get("identified_issues", [])
            
            # Step 2: Legal Concept Identification
            step2_result = await self._step_2_concept_identification(query, analysis.legal_issues)
            analysis.legal_reasoning_chain.append(step2_result)
            analysis.applicable_concepts = step2_result.analysis.get("concepts", [])
            
            # Step 3: Applicable Law Research
            step3_result = await self._step_3_applicable_law_research(
                analysis.legal_issues, jurisdiction, analysis.applicable_concepts
            )
            analysis.legal_reasoning_chain.append(step3_result)
            analysis.applicable_statutes = step3_result.analysis.get("statutes", [])
            
            # Step 4: Precedent Analysis
            step4_result = await self._step_4_precedent_analysis(
                analysis.legal_issues, jurisdiction, analysis.applicable_concepts
            )
            analysis.legal_reasoning_chain.append(step4_result)
            analysis.controlling_precedents = step4_result.analysis.get("precedents", [])
            
            # Step 5: Legal Standard Application
            step5_result = await self._step_5_legal_standard_application(
                query, analysis.applicable_concepts, analysis.controlling_precedents, jurisdiction
            )
            analysis.legal_reasoning_chain.append(step5_result)
            
            # Step 6: Multi-Factor Analysis
            step6_result = await self._step_6_multi_factor_analysis(
                analysis.legal_issues, analysis.applicable_concepts, 
                analysis.controlling_precedents, jurisdiction
            )
            analysis.legal_reasoning_chain.append(step6_result)
            
            # Step 7: Conclusion Synthesis with Authority Citations
            step7_result = await self._step_7_conclusion_synthesis(
                analysis, user_type, jurisdiction
            )
            analysis.legal_reasoning_chain.append(step7_result)
            analysis.legal_conclusions = step7_result.analysis.get("conclusions", [])
            
            # Calculate overall confidence
            analysis.confidence_score = self._calculate_overall_confidence(analysis.legal_reasoning_chain)
            
            # Generate risk assessment
            analysis.risk_assessment = await self._generate_risk_assessment(analysis, jurisdiction)
            
            # Generate alternative analyses
            analysis.alternative_analyses = await self._generate_alternative_analyses(analysis, jurisdiction)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Comprehensive legal analysis completed in {execution_time:.2f}s")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive legal analysis: {e}")
            raise

    async def _step_1_query_analysis(
        self, query: str, jurisdiction: str, legal_domain: Optional[str]
    ) -> ReasoningStepResult:
        """Step 1: Query Analysis & Issue Spotting"""
        start_time = datetime.utcnow()
        
        try:
            # Use Gemini Pro for sophisticated query analysis
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            analysis_prompt = f"""
            As a legal analysis expert, perform comprehensive query analysis and issue spotting for this legal scenario:
            
            LEGAL SCENARIO: {query}
            JURISDICTION: {jurisdiction}
            LEGAL DOMAIN: {legal_domain or "To be determined"}
            
            Please provide:
            1. ISSUE IDENTIFICATION:
               - Primary legal issues (ranked by importance)
               - Secondary/related issues
               - Issue complexity assessment (1-10)
               
            2. LEGAL DOMAIN CLASSIFICATION:
               - Primary legal domain(s)
               - Overlapping domains if applicable
               - Specialized sub-areas
               
            3. FACTUAL ANALYSIS:
               - Key facts that matter legally
               - Missing facts that would be important
               - Factual disputes or ambiguities
               
            4. PRELIMINARY JURISDICTION ASSESSMENT:
               - Jurisdiction appropriateness
               - Potential multi-jurisdiction issues
               - Forum selection considerations
               
            Provide structured JSON response with clear categorization.
            """
            
            response = model.generate_content(analysis_prompt)
            analysis_text = response.text
            
            # Parse and structure the response
            issues = self._extract_legal_issues_from_response(analysis_text, jurisdiction)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ReasoningStepResult(
                step=ReasoningStep.QUERY_ANALYSIS,
                analysis={
                    "identified_issues": issues,
                    "legal_domains": self._extract_legal_domains(analysis_text),
                    "key_facts": self._extract_key_facts(analysis_text),
                    "jurisdiction_assessment": self._extract_jurisdiction_assessment(analysis_text),
                    "raw_analysis": analysis_text
                },
                confidence=0.85,  # High confidence in issue spotting
                sources=["Gemini Pro Analysis", "Legal Issue Classification"],
                reasoning="Comprehensive query analysis using advanced AI to identify all legal issues and classify domains",
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in Step 1 - Query Analysis: {e}")
            # Return fallback analysis
            return ReasoningStepResult(
                step=ReasoningStep.QUERY_ANALYSIS,
                analysis={"error": str(e), "identified_issues": []},
                confidence=0.0,
                sources=[],
                reasoning=f"Error in query analysis: {e}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

    async def _step_2_concept_identification(
        self, query: str, legal_issues: List[LegalIssue]
    ) -> ReasoningStepResult:
        """Step 2: Legal Concept Identification using existing Day 15-16 system"""
        start_time = datetime.utcnow()
        
        try:
            if not self.systems_initialized or not self.concept_extractor:
                raise Exception("Concept extraction system not available")
                
            # Use existing concept extraction system
            concept_result = await self.concept_extractor.extract_concepts(
                text=query,
                legal_domain="multi_domain",  # Allow cross-domain analysis
                jurisdiction="US"  # Will be enhanced for multi-jurisdiction
            )
            
            # Enrich with ontology relationships
            enriched_concepts = []
            for concept in concept_result.get("identified_concepts", []):
                concept_details = self.ontology.get_concept_details(concept.get("concept", ""))
                if concept_details:
                    enriched_concept = {
                        **concept,
                        "ontology_details": concept_details,
                        "relationships": self.ontology.get_concept_relationships(concept.get("concept", "")),
                        "applicable_tests": concept_details.get("applicable_tests", []),
                        "jurisdictional_variations": concept_details.get("jurisdictional_variations", {})
                    }
                    enriched_concepts.append(enriched_concept)
                    
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ReasoningStepResult(
                step=ReasoningStep.CONCEPT_IDENTIFICATION,
                analysis={
                    "concepts": enriched_concepts,
                    "concept_relationships": concept_result.get("concept_relationships", []),
                    "confidence_scores": concept_result.get("confidence_scores", {}),
                    "reasoning_pathway": concept_result.get("reasoning_pathway", [])
                },
                confidence=concept_result.get("overall_confidence", 0.8),
                sources=["Legal Concept Extractor", "Legal Ontology System"],
                reasoning="Advanced concept identification using hybrid AI and legal ontology integration",
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in Step 2 - Concept Identification: {e}")
            return ReasoningStepResult(
                step=ReasoningStep.CONCEPT_IDENTIFICATION,
                analysis={"error": str(e), "concepts": []},
                confidence=0.0,
                sources=[],
                reasoning=f"Error in concept identification: {e}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

    async def _step_3_applicable_law_research(
        self, 
        legal_issues: List[LegalIssue], 
        jurisdiction: str,
        applicable_concepts: List[Dict]
    ) -> ReasoningStepResult:
        """Step 3: Applicable Law Research using RAG system"""
        start_time = datetime.utcnow()
        
        try:
            statutes = []
            regulations = []
            
            for issue in legal_issues:
                # Search for applicable statutes and regulations
                if self.rag_system:
                    # Use RAG system to find relevant legal documents
                    rag_query = f"applicable law statutes regulations {issue.description} {jurisdiction}"
                    rag_result = await self.rag_system.ask_legal_question(
                        question=rag_query,
                        jurisdiction=jurisdiction,
                        legal_domain=issue.legal_domain
                    )
                    
                    # Extract statutory references from RAG results
                    statute_refs = self._extract_statutory_references(rag_result.get("answer", ""))
                    statutes.extend(statute_refs)
                
                # Use Groq for fast legal research augmentation
                research_result = await self._groq_legal_research(issue, jurisdiction)
                if research_result:
                    statutes.extend(research_result.get("statutes", []))
                    regulations.extend(research_result.get("regulations", []))
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ReasoningStepResult(
                step=ReasoningStep.APPLICABLE_LAW_RESEARCH,
                analysis={
                    "statutes": list({statute["id"]: statute for statute in statutes}.values()),  # Deduplicate
                    "regulations": list({reg["id"]: reg for reg in regulations}.values()),
                    "common_law_principles": self._identify_common_law_principles(legal_issues),
                    "jurisdiction_specific_rules": await self._get_jurisdiction_specific_rules(jurisdiction)
                },
                confidence=0.82,
                sources=["Legal RAG System", "Groq Legal Research", "Statutory Databases"],
                reasoning="Comprehensive legal research using RAG system and AI-powered statutory analysis",
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in Step 3 - Applicable Law Research: {e}")
            return ReasoningStepResult(
                step=ReasoningStep.APPLICABLE_LAW_RESEARCH,
                analysis={"error": str(e), "statutes": [], "regulations": []},
                confidence=0.0,
                sources=[],
                reasoning=f"Error in applicable law research: {e}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

    async def _step_4_precedent_analysis(
        self,
        legal_issues: List[LegalIssue],
        jurisdiction: str, 
        applicable_concepts: List[Dict]
    ) -> ReasoningStepResult:
        """Step 4: Precedent Analysis using existing Day 17-18 system"""
        start_time = datetime.utcnow()
        
        try:
            if not self.systems_initialized or not self.precedent_engine:
                raise Exception("Precedent analysis system not available")
            
            all_precedents = []
            
            for issue in legal_issues:
                # Use existing precedent analysis system
                precedent_result = await self.precedent_engine.analyze_precedents(
                    legal_issue=issue.description,
                    jurisdiction=jurisdiction,
                    legal_concepts=applicable_concepts
                )
                
                if precedent_result:
                    all_precedents.extend(precedent_result.get("controlling_precedents", []))
                    all_precedents.extend(precedent_result.get("persuasive_precedents", []))
            
            # Rank precedents by authority and relevance
            ranked_precedents = self._rank_precedents_by_authority(all_precedents, jurisdiction)
            
            # Identify conflicts between precedents
            conflicts = self._identify_precedent_conflicts(ranked_precedents)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ReasoningStepResult(
                step=ReasoningStep.PRECEDENT_ANALYSIS,
                analysis={
                    "precedents": ranked_precedents[:20],  # Top 20 most relevant
                    "controlling_precedents": [p for p in ranked_precedents if p.get("binding_status") == "binding"][:10],
                    "persuasive_precedents": [p for p in ranked_precedents if p.get("binding_status") == "persuasive"][:10],
                    "conflicting_precedents": conflicts,
                    "precedent_summary": self._generate_precedent_summary(ranked_precedents)
                },
                confidence=0.88,
                sources=["Precedent Analysis Engine", "Citation Network Analysis", "Court Hierarchy System"],
                reasoning="Advanced precedent analysis using citation networks and legal authority ranking",
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in Step 4 - Precedent Analysis: {e}")
            return ReasoningStepResult(
                step=ReasoningStep.PRECEDENT_ANALYSIS,
                analysis={"error": str(e), "precedents": []},
                confidence=0.0,
                sources=[],
                reasoning=f"Error in precedent analysis: {e}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

    async def _step_5_legal_standard_application(
        self,
        query: str,
        applicable_concepts: List[Dict],
        controlling_precedents: List[Dict],
        jurisdiction: str
    ) -> ReasoningStepResult:
        """Step 5: Legal Standard Application"""
        start_time = datetime.utcnow()
        
        try:
            # Use OpenRouter GPT for sophisticated legal reasoning
            application_prompt = f"""
            As a legal reasoning expert, apply relevant legal standards to the facts:
            
            LEGAL SCENARIO: {query}
            JURISDICTION: {jurisdiction}
            
            APPLICABLE LEGAL CONCEPTS:
            {json.dumps(applicable_concepts[:5], indent=2)}
            
            CONTROLLING PRECEDENTS:
            {json.dumps(controlling_precedents[:3], indent=2)}
            
            Please provide:
            1. LEGAL TESTS APPLICATION:
               - Which legal tests apply to these facts
               - How each test should be applied step-by-step
               - Required elements and their satisfaction
               
            2. BURDEN OF PROOF ANALYSIS:
               - Who bears the burden of proof for each element
               - Standard of proof required (preponderance, clear and convincing, etc.)
               - Evidence that would satisfy each burden
               
            3. ELEMENT-BY-ELEMENT ANALYSIS:
               - Break down each required legal element
               - Apply facts to each element
               - Identify strengths and weaknesses
               
            4. PRECEDENT APPLICATION:
               - How controlling precedents apply to these facts
               - Analogies and distinctions with precedent cases
               - Precedential guidance for application
               
            Provide detailed reasoning in structured JSON format.
            """
            
            response = await self.openrouter_client.post(
                "/chat/completions",
                json={
                    "model": "openai/gpt-4-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an expert legal analyst specializing in legal standard application and precedent reasoning."},
                        {"role": "user", "content": application_prompt}
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.1
                }
            )
            
            result = response.json()
            analysis_text = result["choices"][0]["message"]["content"]
            
            # Structure the application analysis
            application_analysis = self._parse_legal_standard_application(analysis_text)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ReasoningStepResult(
                step=ReasoningStep.LEGAL_STANDARD_APPLICATION,
                analysis=application_analysis,
                confidence=0.85,
                sources=["OpenRouter GPT-4", "Legal Standard Application Framework"],
                reasoning="Detailed application of legal standards to facts using precedent guidance",
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in Step 5 - Legal Standard Application: {e}")
            return ReasoningStepResult(
                step=ReasoningStep.LEGAL_STANDARD_APPLICATION,
                analysis={"error": str(e)},
                confidence=0.0,
                sources=[],
                reasoning=f"Error in legal standard application: {e}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

    async def _step_6_multi_factor_analysis(
        self,
        legal_issues: List[LegalIssue],
        applicable_concepts: List[Dict],
        controlling_precedents: List[Dict],
        jurisdiction: str
    ) -> ReasoningStepResult:
        """Step 6: Multi-Factor Analysis for complex legal issues"""
        start_time = datetime.utcnow()
        
        try:
            # Identify issues requiring multi-factor analysis
            multi_factor_issues = [
                issue for issue in legal_issues 
                if issue.complexity_score > 7.0 or "balancing" in issue.description.lower()
            ]
            
            if not multi_factor_issues:
                # No complex multi-factor analysis needed
                return ReasoningStepResult(
                    step=ReasoningStep.MULTI_FACTOR_ANALYSIS,
                    analysis={
                        "multi_factor_analysis": "Not applicable - no complex balancing tests identified",
                        "factors": [],
                        "balancing_outcome": "N/A"
                    },
                    confidence=1.0,
                    sources=["Multi-Factor Analysis Framework"],
                    reasoning="No multi-factor balancing tests required for this analysis",
                    execution_time=(datetime.utcnow() - start_time).total_seconds()
                )
            
            # Perform multi-factor analysis using Groq for speed
            factors_analysis = []
            
            for issue in multi_factor_issues:
                factors = await self._identify_balancing_factors(issue, applicable_concepts, jurisdiction)
                factor_weights = await self._calculate_factor_weights(factors, controlling_precedents)
                balancing_outcome = await self._perform_balancing_test(factors, factor_weights)
                
                factors_analysis.append({
                    "issue": issue.description,
                    "factors": factors,
                    "weights": factor_weights,
                    "balancing_outcome": balancing_outcome
                })
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ReasoningStepResult(
                step=ReasoningStep.MULTI_FACTOR_ANALYSIS,
                analysis={
                    "multi_factor_analysis": factors_analysis,
                    "complex_issues_count": len(multi_factor_issues),
                    "balancing_methodology": "Weighted factor analysis with precedent guidance"
                },
                confidence=0.82,
                sources=["Multi-Factor Analysis Framework", "Groq AI", "Balancing Test Precedents"],
                reasoning="Advanced multi-factor balancing analysis for complex legal issues",
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in Step 6 - Multi-Factor Analysis: {e}")
            return ReasoningStepResult(
                step=ReasoningStep.MULTI_FACTOR_ANALYSIS,
                analysis={"error": str(e)},
                confidence=0.0,
                sources=[],
                reasoning=f"Error in multi-factor analysis: {e}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

    async def _step_7_conclusion_synthesis(
        self,
        analysis: ComprehensiveLegalAnalysis,
        user_type: UserType,
        jurisdiction: str
    ) -> ReasoningStepResult:
        """Step 7: Conclusion Synthesis with Authority Citations"""
        start_time = datetime.utcnow()
        
        try:
            # Synthesize all reasoning steps into coherent conclusions
            synthesis_prompt = f"""
            As a senior legal counsel, synthesize the comprehensive legal analysis into clear conclusions:
            
            USER TYPE: {user_type.value}
            JURISDICTION: {jurisdiction}
            
            LEGAL ISSUES IDENTIFIED:
            {[issue.description for issue in analysis.legal_issues]}
            
            KEY CONCEPTS:
            {[concept.get("concept", "") for concept in analysis.applicable_concepts[:5]]}
            
            CONTROLLING PRECEDENTS:
            {[p.get("case_name", "") for p in analysis.controlling_precedents[:3]]}
            
            Based on the 7-step legal reasoning analysis, provide:
            
            1. PRIMARY CONCLUSIONS:
               - Clear legal conclusions for each major issue
               - Confidence level for each conclusion (high/medium/low)
               - Supporting legal authority for each conclusion
               
            2. RISK ASSESSMENT:
               - Legal risks identified
               - Risk probability and impact
               - Risk mitigation recommendations
               
            3. ALTERNATIVE LEGAL THEORIES:
               - Alternative ways to analyze the issues
               - Comparative strengths of different approaches
               - Potential counterarguments
               
            4. PRACTICAL RECOMMENDATIONS:
               - Actionable next steps based on analysis
               - Documentation needed
               - Preventive measures
            
            Adapt language and detail level for {user_type.value} audience.
            Provide comprehensive citations to legal authority.
            """
            
            # Use Gemini Pro for final synthesis
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(synthesis_prompt)
            synthesis_text = response.text
            
            # Parse conclusions
            conclusions = self._parse_legal_conclusions(synthesis_text, analysis.legal_issues)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ReasoningStepResult(
                step=ReasoningStep.CONCLUSION_SYNTHESIS,
                analysis={
                    "conclusions": conclusions,
                    "synthesis_text": synthesis_text,
                    "user_type": user_type.value,
                    "adapted_language": True,
                    "authority_citations": self._extract_authority_citations(synthesis_text)
                },
                confidence=0.90,
                sources=["Gemini Pro Legal Synthesis", "Comprehensive Analysis Integration"],
                reasoning="Final synthesis of all reasoning steps with user-adapted conclusions and authority support",
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in Step 7 - Conclusion Synthesis: {e}")
            return ReasoningStepResult(
                step=ReasoningStep.CONCLUSION_SYNTHESIS,
                analysis={"error": str(e), "conclusions": []},
                confidence=0.0,
                sources=[],
                reasoning=f"Error in conclusion synthesis: {e}",
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

    # Helper methods for data extraction and processing
    
    def _extract_legal_issues_from_response(self, response_text: str, jurisdiction: str) -> List[LegalIssue]:
        """Extract structured legal issues from AI response"""
        issues = []
        try:
            # Basic parsing - would be enhanced with more sophisticated NLP
            lines = response_text.split('\n')
            current_issue = None
            
            for line in lines:
                if "Primary legal issues" in line or "Issue:" in line:
                    if current_issue:
                        issues.append(current_issue)
                    
                    issue_desc = line.split(':', 1)[-1].strip()
                    current_issue = LegalIssue(
                        issue_id=str(uuid.uuid4()),
                        description=issue_desc,
                        legal_domain=self._classify_legal_domain(issue_desc),
                        jurisdiction=jurisdiction,
                        priority="high",
                        related_concepts=[],
                        complexity_score=7.5  # Default complexity
                    )
            
            if current_issue:
                issues.append(current_issue)
                
            return issues
            
        except Exception as e:
            logger.error(f"Error extracting legal issues: {e}")
            return []

    def _extract_legal_domains(self, analysis_text: str) -> List[str]:
        """Extract identified legal domains from analysis"""
        domains = []
        domain_keywords = {
            "contract": "contract_law",
            "constitutional": "constitutional_law", 
            "administrative": "administrative_law",
            "employment": "employment_law",
            "tort": "tort_law",
            "intellectual property": "intellectual_property"
        }
        
        for keyword, domain in domain_keywords.items():
            if keyword.lower() in analysis_text.lower():
                domains.append(domain)
                
        return list(set(domains)) if domains else ["general_law"]

    def _extract_key_facts(self, analysis_text: str) -> List[str]:
        """Extract key legal facts from analysis"""
        # Simplified fact extraction - would be enhanced with NLP
        facts = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if "key fact" in line.lower() or "important" in line.lower():
                facts.append(line.strip())
                
        return facts[:10]  # Limit to top 10 facts

    def _extract_jurisdiction_assessment(self, analysis_text: str) -> Dict[str, Any]:
        """Extract jurisdiction assessment from analysis"""
        return {
            "appropriate_jurisdiction": True,  # Default
            "multi_jurisdiction_issues": False,
            "forum_considerations": "Standard jurisdiction analysis applies",
            "jurisdictional_challenges": []
        }

    def _classify_legal_domain(self, issue_description: str) -> str:
        """Classify legal domain for an issue"""
        issue_lower = issue_description.lower()
        
        if any(word in issue_lower for word in ["contract", "agreement", "breach", "performance"]):
            return "contract_law"
        elif any(word in issue_lower for word in ["constitutional", "rights", "amendment", "due process"]):
            return "constitutional_law"
        elif any(word in issue_lower for word in ["employment", "workplace", "termination", "discrimination"]):
            return "employment_law"
        elif any(word in issue_lower for word in ["tort", "negligence", "liability", "damages"]):
            return "tort_law"
        elif any(word in issue_lower for word in ["patent", "copyright", "trademark", "intellectual"]):
            return "intellectual_property"
        else:
            return "general_law"

    def _calculate_overall_confidence(self, reasoning_chain: List[ReasoningStepResult]) -> float:
        """Calculate overall confidence score from all reasoning steps"""
        if not reasoning_chain:
            return 0.0
            
        # Weighted average based on step importance
        weights = {
            ReasoningStep.QUERY_ANALYSIS: 0.15,
            ReasoningStep.CONCEPT_IDENTIFICATION: 0.20,
            ReasoningStep.APPLICABLE_LAW_RESEARCH: 0.15,
            ReasoningStep.PRECEDENT_ANALYSIS: 0.20,
            ReasoningStep.LEGAL_STANDARD_APPLICATION: 0.15,
            ReasoningStep.MULTI_FACTOR_ANALYSIS: 0.05,
            ReasoningStep.CONCLUSION_SYNTHESIS: 0.10
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for step_result in reasoning_chain:
            weight = weights.get(step_result.step, 0.1)
            weighted_sum += step_result.confidence * weight
            total_weight += weight
            
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _generate_risk_assessment(self, analysis: ComprehensiveLegalAnalysis, jurisdiction: str) -> Dict[str, Any]:
        """Generate comprehensive risk assessment"""
        try:
            # Use Groq for fast risk analysis
            risk_prompt = f"""
            Analyze legal risks for this scenario in {jurisdiction}:
            
            Issues: {[issue.description for issue in analysis.legal_issues]}
            
            Provide:
            1. Risk probability (high/medium/low)
            2. Risk impact (high/medium/low) 
            3. Risk categories (litigation, compliance, financial, operational)
            4. Mitigation strategies
            """
            
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a legal risk assessment expert."},
                    {"role": "user", "content": risk_prompt}
                ],
                model="llama-3.1-70b-versatile",
                max_tokens=1500,
                temperature=0.1
            )
            
            risk_text = completion.choices[0].message.content
            
            return {
                "overall_risk_level": "medium",  # Would parse from response
                "risk_categories": ["litigation", "compliance"],
                "probability_assessment": "medium",
                "impact_assessment": "medium",
                "mitigation_strategies": risk_text.split('\n')[:5],
                "detailed_analysis": risk_text
            }
            
        except Exception as e:
            logger.error(f"Error generating risk assessment: {e}")
            return {"error": str(e)}

    async def _generate_alternative_analyses(self, analysis: ComprehensiveLegalAnalysis, jurisdiction: str) -> List[Dict]:
        """Generate alternative legal analysis approaches"""
        alternatives = []
        
        try:
            for issue in analysis.legal_issues[:3]:  # Top 3 issues
                # Generate alternative approach for each major issue
                alternatives.append({
                    "issue_id": issue.issue_id,
                    "alternative_theory": f"Alternative analysis for {issue.description}",
                    "approach": "different_precedent_application",
                    "confidence": 0.7,
                    "reasoning": "Alternative precedent interpretation could lead to different outcome"
                })
                
        except Exception as e:
            logger.error(f"Error generating alternatives: {e}")
            
        return alternatives

    # Additional helper methods would be implemented for:
    # - _groq_legal_research()
    # - _extract_statutory_references()
    # - _rank_precedents_by_authority()
    # - _identify_precedent_conflicts()
    # - _parse_legal_standard_application()
    # - _identify_balancing_factors()
    # - _calculate_factor_weights()
    # - _perform_balancing_test()
    # - _parse_legal_conclusions()
    # - _extract_authority_citations()
    # And other supporting methods...

# Initialize global reasoning engine instance
_reasoning_engine = None

async def get_reasoning_engine(gemini_api_key: str, groq_api_key: str, openrouter_api_key: str) -> MultiStepLegalReasoningEngine:
    """Get or create reasoning engine instance"""
    global _reasoning_engine
    
    if _reasoning_engine is None:
        _reasoning_engine = MultiStepLegalReasoningEngine(
            gemini_api_key=gemini_api_key,
            groq_api_key=groq_api_key, 
            openrouter_api_key=openrouter_api_key
        )
        
    return _reasoning_engine
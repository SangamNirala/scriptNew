"""
Legal Knowledge Base Builder - Comprehensive Legal Data Collection System

This module implements a comprehensive legal data collection system that:
1. Fetches legal documents from multiple authoritative sources
2. Organizes content by jurisdiction (US Federal/State, India Central/State)
3. Categorizes by legal domains (Contract Law, Employment, IP, etc.)
4. Formats data for RAG system integration
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import httpx
import os
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# SerpAPI - handle import gracefully
try:
    from serpapi import Client as GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    GoogleSearch = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollectionMode(Enum):
    """Collection modes for backward compatibility"""
    STANDARD = "standard"  # Original 35 document collection
    BULK = "bulk"         # New 15,000+ document collection

@dataclass
class RateLimitState:
    """Track rate limiting state for each API key"""
    requests_made: int = 0
    last_request_time: float = 0
    backoff_until: float = 0
    consecutive_failures: int = 0

@dataclass 
class CollectionProgress:
    """Track collection progress for resumability"""
    total_queries: int = 0
    completed_queries: int = 0
    successful_queries: int = 0
    total_documents: int = 0
    failed_queries: List[str] = field(default_factory=list)
    last_checkpoint: Dict[str, Any] = field(default_factory=dict)
    # Enhanced progress tracking
    start_time: float = field(default_factory=time.time)
    documents_by_court: Dict[str, int] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    eta_seconds: float = 0.0
    average_doc_time: float = 0.0

@dataclass
class CourtPriority:
    """Court priority configuration for hierarchical collection"""
    code: str
    name: str
    priority: int  # 1=highest, 2=medium, 3=lowest
    target_documents: int
    collected_documents: int = 0
    
@dataclass
class QualityMetrics:
    """Track quality metrics for collection"""  
    total_processed: int = 0
    passed_length_filter: int = 0
    passed_status_filter: int = 0
    passed_date_filter: int = 0
    passed_content_filter: int = 0
    duplicates_filtered: int = 0
    average_word_count: float = 0.0
    quality_score_average: float = 0.0

class LegalKnowledgeBuilder:
    """Comprehensive legal knowledge base builder for RAG system"""
    
    def __init__(self, collection_mode: CollectionMode = CollectionMode.STANDARD):
        # Multiple CourtListener API keys for rotation
        self.courtlistener_api_keys = [
            os.environ.get('COURTLISTENER_API_KEY'),  # Original key from env
            'e7a714db2df7fb77b6065a9d69158dcb85fa1acd',  # Key 1
            '7ec22683a2adf0f192e3219df2a9bdbe6c5aaa4a',  # Key 2
            'cd364ff091a9aaef6a1989e054e2f8e215923f46',  # Key 3
            '9c48f847b58da0ee5a42d52d7cbcf022d07c5d96'   # Key 4
        ]
        # Filter out None values and ensure we have valid keys
        self.courtlistener_api_keys = [key for key in self.courtlistener_api_keys if key]
        self.current_api_key_index = 0
        self.serp_api_key = os.environ.get('SERP_API_KEY')
        
        # Collection mode configuration
        self.collection_mode = collection_mode
        self.config = self._get_collection_config()
        
        # Rate limiting state for each API key
        self.rate_limits = {i: RateLimitState() for i in range(len(self.courtlistener_api_keys))}
        
        # Collection progress tracking with enhancements
        self.progress = CollectionProgress()
        self.quality_metrics = QualityMetrics()
        
        # Court hierarchy prioritization
        self.court_priorities = self._initialize_court_priorities()
        
        # Legal domain categories
        self.legal_domains = [
            "contract_law", "employment_labor_law", "intellectual_property",
            "corporate_regulatory", "civil_criminal_procedure", "constitutional_law",
            "taxation_financial", "real_estate_law", "family_law", "immigration_law"
        ]
        
        # Jurisdictions to cover
        self.jurisdictions = {
            "us_federal": {"name": "United States Federal", "priority": "high"},
            "us_california": {"name": "California State", "priority": "high"},
            "us_new_york": {"name": "New York State", "priority": "high"},
            "us_texas": {"name": "Texas State", "priority": "medium"},
            "india_central": {"name": "India Central/Union", "priority": "high"},
            "india_maharashtra": {"name": "Maharashtra State", "priority": "medium"},
            "india_tamil_nadu": {"name": "Tamil Nadu State", "priority": "medium"}
        }
        
        # Knowledge base storage
        self.knowledge_base = []
        self.collected_sources = set()
        
        # Enhanced tracking for bulk collection
        self.seen_case_ids = set()  # Deduplication tracking
        self.seen_citations = set()  # Citation-based deduplication
        self.checkpoint_interval = 1000  # Save checkpoint every 1000 docs
        
    def _get_collection_config(self) -> Dict[str, Any]:
        """Get configuration based on collection mode"""
        if self.collection_mode == CollectionMode.BULK:
            return {
                "results_per_query": 500,  # Target 200-500 results per query
                "max_pages_per_query": 25,  # Max pages to fetch per query (500/20 per page)
                "batch_size": 200,  # Process in batches of 200
                "min_content_length": 1000,  # Enhanced: minimum 1000 words
                "enable_pagination": True,
                "enable_quality_filters": True,
                "date_range": {
                    "primary_min": "2020-01-01",  # Primary: 2020-2025
                    "primary_max": "2025-12-31",
                    "secondary_min": "2015-01-01",  # Secondary: 2015-2019
                    "secondary_max": "2019-12-31"
                },
                "precedential_status": ["Precedential", "Published"],  # Only precedential/published
                "excluded_keywords": ["procedural", "administrative", "order", "motion"],  # Exclude procedural orders
                "rate_limit_requests_per_minute": 50,  # Conservative rate limiting
                "max_retries": 5,
                "base_backoff_seconds": 2,
                "enable_parallel_processing": True,
                "max_concurrent_requests": 3,  # Parallel requests per court
                "checkpoint_enabled": True,
                "quality_threshold": 0.7,  # Quality score threshold
                "enable_enhanced_metadata": True
            }
        else:  # STANDARD mode for backward compatibility
            return {
                "results_per_query": 10,  # Original behavior
                "max_pages_per_query": 1,  # No pagination
                "batch_size": 35,  # Original batch size
                "min_content_length": 50,  # Original minimum
                "enable_pagination": False,
                "enable_quality_filters": False,
                "date_range": None,
                "rate_limit_requests_per_minute": 20,  # Original rate limit
                "max_retries": 3,
                "base_backoff_seconds": 3,
                "enable_parallel_processing": False,
                "max_concurrent_requests": 1,
                "checkpoint_enabled": False,
                "quality_threshold": 0.3,
                "enable_enhanced_metadata": False
            }
        
    def _initialize_court_priorities(self) -> List[CourtPriority]:
        """Initialize court hierarchy with prioritization for bulk collection"""
        if self.collection_mode == CollectionMode.BULK:
            # Court hierarchy prioritization for 15,000 documents
            return [
                # Priority 1: Supreme Court decisions (5,000 docs target)
                CourtPriority("scotus", "Supreme Court of the United States", 1, 5000),
                
                # Priority 2: Circuit Court decisions (8,000 docs target)
                CourtPriority("ca1", "1st Circuit Court of Appeals", 2, 615),
                CourtPriority("ca2", "2nd Circuit Court of Appeals", 2, 615),  
                CourtPriority("ca3", "3rd Circuit Court of Appeals", 2, 615),
                CourtPriority("ca4", "4th Circuit Court of Appeals", 2, 615),
                CourtPriority("ca5", "5th Circuit Court of Appeals", 2, 615),
                CourtPriority("ca6", "6th Circuit Court of Appeals", 2, 615),
                CourtPriority("ca7", "7th Circuit Court of Appeals", 2, 615),
                CourtPriority("ca8", "8th Circuit Court of Appeals", 2, 615),
                CourtPriority("ca9", "9th Circuit Court of Appeals", 2, 615),
                CourtPriority("ca10", "10th Circuit Court of Appeals", 2, 615),
                CourtPriority("ca11", "11th Circuit Court of Appeals", 2, 615),
                CourtPriority("cadc", "DC Circuit Court of Appeals", 2, 615),
                CourtPriority("cafc", "Federal Circuit Court of Appeals", 2, 615),
                
                # Priority 3: District Court landmark cases (2,000 docs target)
                CourtPriority("dcd", "D.C. District Court", 3, 400),
                CourtPriority("nysd", "S.D. New York District Court", 3, 400),
                CourtPriority("cand", "N.D. California District Court", 3, 400),
                CourtPriority("nynd", "N.D. New York District Court", 3, 400),
                CourtPriority("txsd", "S.D. Texas District Court", 3, 400),
            ]
        else:
            # Standard mode - simplified court list
            return [
                CourtPriority("scotus", "Supreme Court", 1, 35),
                CourtPriority("ca1", "1st Circuit", 2, 10),
                CourtPriority("ca2", "2nd Circuit", 2, 10),
                CourtPriority("ca9", "9th Circuit", 2, 10),
            ]
        
    async def build_comprehensive_knowledge_base(self) -> List[Dict[str, Any]]:
        """Main method to build comprehensive legal knowledge base"""
        logger.info("🚀 Starting comprehensive legal knowledge base creation...")
        
        # Phase 1: Collect US Legal Content
        logger.info("📚 Phase 1: Collecting US Legal Content...")
        us_content = await self._collect_us_legal_content()
        
        # Phase 2: Collect Indian Legal Content  
        logger.info("🇮🇳 Phase 2: Collecting Indian Legal Content...")
        indian_content = await self._collect_indian_legal_content()
        
        # Phase 3: Collect General Legal Resources
        logger.info("⚖️ Phase 3: Collecting General Legal Resources...")
        general_content = await self._collect_general_legal_resources()
        
        # Combine and deduplicate
        self.knowledge_base.extend(us_content)
        self.knowledge_base.extend(indian_content)
        self.knowledge_base.extend(general_content)
        
        # Remove duplicates based on content hash
        self.knowledge_base = self._deduplicate_content(self.knowledge_base)
        
        logger.info(f"✅ Legal knowledge base created with {len(self.knowledge_base)} documents")
        return self.knowledge_base
    
    async def _collect_us_legal_content(self) -> List[Dict[str, Any]]:
        """Collect comprehensive US legal content"""
        us_content = []
        
        # 1. Federal statutes and regulations
        federal_content = await self._fetch_federal_legal_content()
        us_content.extend(federal_content)
        
        # 2. Supreme Court and Circuit Court decisions
        court_decisions = await self._fetch_court_decisions()
        us_content.extend(court_decisions)
        
        # 3. State-specific laws (CA, NY, TX)
        state_content = await self._fetch_state_legal_content()
        us_content.extend(state_content)
        
        # 4. Federal agency guidelines (SEC, FTC, DOL, etc.)
        agency_content = await self._fetch_federal_agency_content()
        us_content.extend(agency_content)
        
        return us_content
    
    async def _collect_indian_legal_content(self) -> List[Dict[str, Any]]:
        """Collect comprehensive Indian legal content"""
        indian_content = []
        
        # 1. Central/Union legislation
        central_laws = await self._fetch_indian_central_laws()
        indian_content.extend(central_laws)
        
        # 2. Supreme Court of India decisions
        sc_decisions = await self._fetch_indian_supreme_court_decisions()
        indian_content.extend(sc_decisions)
        
        # 3. Regulatory body guidelines (SEBI, RBI, MCA)
        regulatory_content = await self._fetch_indian_regulatory_content()
        indian_content.extend(regulatory_content)
        
        # 4. State-specific laws (Maharashtra, Tamil Nadu)
        state_laws = await self._fetch_indian_state_laws()
        indian_content.extend(state_laws)
        
        return indian_content
    
    async def _collect_general_legal_resources(self) -> List[Dict[str, Any]]:
        """Collect general legal resources and international standards"""
        general_content = []
        
        # 1. Legal definitions and concepts
        definitions = await self._fetch_legal_definitions()
        general_content.extend(definitions)
        
        # 2. Legal procedures and practices
        procedures = await self._fetch_legal_procedures()
        general_content.extend(procedures)
        
        # 3. International legal standards (GDPR, WIPO, etc.)
        international_content = await self._fetch_international_legal_standards()
        general_content.extend(international_content)
        
        return general_content
    
    async def _fetch_federal_legal_content(self) -> List[Dict[str, Any]]:
        """Fetch US Federal legal content using multiple sources"""
        content = []
        
        # Search queries for different legal domains
        federal_queries = [
            "site:law.cornell.edu federal contract law statutes",
            "site:law.cornell.edu federal employment law regulations",
            "site:uscode.house.gov intellectual property laws",
            "site:law.cornell.edu federal corporate regulations SEC",
            "site:law.cornell.edu federal civil procedure rules",
            "site:law.cornell.edu constitutional amendments",
            "site:law.cornell.edu federal tax code regulations",
            "site:law.cornell.edu federal real estate laws",
            "site:law.cornell.edu federal immigration statutes"
        ]
        
        for query in federal_queries:
            try:
                results = await self._search_legal_content(query, jurisdiction="us_federal")
                content.extend(results)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching federal content for query '{query}': {e}")
                
        return content
    
    def _get_next_api_key(self) -> Optional[str]:
        """Get next available CourtListener API key with intelligent selection"""
        if not self.courtlistener_api_keys:
            return None
        
        current_time = time.time()
        
        # Find the key with least recent usage and no active backoff
        best_key_index = None
        best_score = float('inf')
        
        for i, key in enumerate(self.courtlistener_api_keys):
            rate_state = self.rate_limits[i]
            
            # Skip if key is in backoff period
            if current_time < rate_state.backoff_until:
                continue
                
            # Calculate score based on usage and time since last request
            time_since_last = current_time - rate_state.last_request_time
            usage_penalty = rate_state.requests_made * 0.1
            failure_penalty = rate_state.consecutive_failures * 2
            
            score = usage_penalty + failure_penalty - time_since_last
            
            if score < best_score:
                best_score = score
                best_key_index = i
        
        # If no key available (all in backoff), wait for shortest backoff
        if best_key_index is None:
            min_backoff = min(state.backoff_until for state in self.rate_limits.values())
            wait_time = max(0, min_backoff - current_time)
            logger.warning(f"All API keys in backoff. Waiting {wait_time:.1f}s")
            return None
            
        # Update state for selected key
        self.rate_limits[best_key_index].last_request_time = current_time
        self.rate_limits[best_key_index].requests_made += 1
        
        return self.courtlistener_api_keys[best_key_index]
    
    async def _wait_for_rate_limit(self, key_index: int):
        """Wait for rate limiting based on requests per minute limit"""
        if key_index not in self.rate_limits:
            return
            
        rate_state = self.rate_limits[key_index]
        current_time = time.time()
        
        # Calculate required wait time based on rate limit
        requests_per_minute = self.config["rate_limit_requests_per_minute"]
        min_interval = 60.0 / requests_per_minute  # seconds between requests
        
        time_since_last = current_time - rate_state.last_request_time
        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            # Add small jitter to avoid thundering herd
            jitter = random.uniform(0, 0.5)
            await asyncio.sleep(wait_time + jitter)
    
    async def _handle_api_error(self, key_index: int, status_code: int, response_text: str = "") -> bool:
        """Handle API errors with exponential backoff. Returns True if should retry."""
        if key_index not in self.rate_limits:
            return False
            
        rate_state = self.rate_limits[key_index]
        current_time = time.time()
        
        if status_code == 429:  # Rate limit exceeded
            rate_state.consecutive_failures += 1
            # Exponential backoff with jitter
            backoff_time = self.config["base_backoff_seconds"] * (2 ** rate_state.consecutive_failures)
            jitter = random.uniform(0.5, 1.5)
            rate_state.backoff_until = current_time + (backoff_time * jitter)
            
            logger.warning(f"Rate limit hit for key #{key_index}. Backing off for {backoff_time:.1f}s")
            return rate_state.consecutive_failures <= self.config["max_retries"]
            
        elif status_code in [500, 502, 503, 504]:  # Server errors
            rate_state.consecutive_failures += 1
            backoff_time = self.config["base_backoff_seconds"] * rate_state.consecutive_failures
            rate_state.backoff_until = current_time + backoff_time
            
            logger.warning(f"Server error {status_code} for key #{key_index}. Backing off for {backoff_time:.1f}s")
            return rate_state.consecutive_failures <= self.config["max_retries"]
            
        elif status_code == 401:  # Unauthorized
            logger.error(f"API key #{key_index} unauthorized. Removing from rotation.")
            # Don't retry with this key
            rate_state.backoff_until = current_time + 86400  # 24 hour backoff
            return False
            
        else:
            # Reset consecutive failures on success or other errors
            rate_state.consecutive_failures = 0
            return False
    
    async def _fetch_paginated_results(self, client: httpx.AsyncClient, base_url: str, 
                                     params: Dict[str, Any], headers: Dict[str, str],
                                     query: str, legal_domain: str, court_info: tuple) -> List[Dict[str, Any]]:
        """Fetch paginated results from CourtListener API"""
        all_results = []
        page_count = 0
        next_url = base_url
        
        court_code, court_name = court_info
        max_pages = self.config["max_pages_per_query"]
        target_results = self.config["results_per_query"]
        
        while next_url and page_count < max_pages and len(all_results) < target_results:
            try:
                page_count += 1
                
                # Get API key for this request
                api_key = self._get_next_api_key()
                if not api_key:
                    logger.warning("No API keys available, stopping pagination")
                    break
                    
                # Find key index for rate limiting
                key_index = next((i for i, k in enumerate(self.courtlistener_api_keys) if k == api_key), 0)
                
                # Wait for rate limiting
                await self._wait_for_rate_limit(key_index)
                
                # Update headers with current API key
                current_headers = {**headers, "Authorization": f"Token {api_key}"}
                
                # Make request
                if page_count == 1:
                    # First page uses base URL with params
                    response = await client.get(next_url, headers=current_headers, params=params)
                else:
                    # Subsequent pages use the next URL directly
                    response = await client.get(next_url, headers=current_headers)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if not results:
                        logger.info(f"No more results for query '{query}' in {court_name} (page {page_count})")
                        break
                    
                    # Process and filter results
                    page_results = []
                    for result in results:
                        if len(all_results) >= target_results:
                            break
                            
                        processed_result = await self._process_court_result(
                            result, query, legal_domain, court_code, court_name
                        )
                        
                        if processed_result and self._meets_quality_filters(processed_result):
                            page_results.append(processed_result)
                    
                    all_results.extend(page_results)
                    
                    # Get next page URL
                    next_url = data.get('next')
                    
                    logger.info(f"📄 Page {page_count}: Found {len(page_results)} quality results from {len(results)} total (Query: {query[:50]}...)")
                    
                    # Reset consecutive failures on success
                    self.rate_limits[key_index].consecutive_failures = 0
                    
                elif response.status_code in [429, 500, 502, 503, 504]:
                    # Handle retryable errors
                    should_retry = await self._handle_api_error(key_index, response.status_code, response.text)
                    if should_retry:
                        logger.info(f"Retrying page {page_count} for query '{query}' in {court_name}")
                        page_count -= 1  # Don't count this as a completed page
                        continue
                    else:
                        logger.error(f"Max retries exceeded for query '{query}' in {court_name}")
                        break
                else:
                    logger.warning(f"API request failed with status {response.status_code} for page {page_count}")
                    await self._handle_api_error(key_index, response.status_code, response.text)
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching page {page_count} for query '{query}' in {court_name}: {e}")
                break
        
        logger.info(f"🎯 Pagination complete for '{query}' in {court_name}: {len(all_results)} results from {page_count} pages")
        return all_results
    
    async def _process_court_result(self, result: Dict[str, Any], query: str, 
                                  legal_domain: str, court_code: str, court_name: str) -> Optional[Dict[str, Any]]:
        """Process a single court result with enhanced metadata extraction"""
        try:
            # Extract basic content
            content = result.get('text', '') or result.get('snippet', '')
            title = result.get('caseName', 'Unknown Case')
            
            # Enhanced metadata extraction
            enhanced_metadata = await self._extract_enhanced_metadata(result, content) if self.config.get("enable_enhanced_metadata", False) else {}
            
            # Legal concept tagging
            legal_concepts = self._extract_legal_concepts(content, legal_domain)
            
            # Court level classification
            court_level = self._classify_court_level(court_code)
            
            legal_doc = {
                "id": f"court_{result.get('id')}_{court_code}",
                "title": title,
                "content": content,
                "source": "CourtListener",
                "source_url": result.get('absolute_url', ''),
                "jurisdiction": "us_federal",
                "legal_domain": legal_domain,
                "document_type": "court_decision",
                "court": f"{court_name} ({court_code})",
                "court_code": court_code,
                "court_level": court_level,
                "date_filed": result.get('dateFiled', ''),
                "precedential_status": result.get('status', ''),
                "word_count": len(content.split()) if content else 0,
                "legal_concepts": legal_concepts,
                "metadata": {
                    "citation": result.get('citation', ''),
                    "judges": result.get('judges', []),
                    "docket_number": result.get('docketNumber', ''),
                    "search_query": query,
                    "target_domain": legal_domain,
                    "author": result.get('author', ''),
                    "cluster_id": result.get('cluster', ''),
                    "opinion_type": result.get('type', ''),
                    "panel": result.get('panel', []),
                    "attorneys": result.get('attorneys', []),
                    **enhanced_metadata
                },
                "created_at": datetime.utcnow().isoformat(),
                "content_hash": self._generate_content_hash(content)
            }
            
            return legal_doc
            
        except Exception as e:
            logger.error(f"Error processing court result: {e}")
            return None
    
    async def _extract_enhanced_metadata(self, result: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract enhanced metadata for better legal document understanding"""
        enhanced_metadata = {}
        
        try:
            # Extract citation network
            citations = self._extract_citations(content)
            enhanced_metadata["cited_cases"] = citations
            enhanced_metadata["citation_count"] = len(citations)
            
            # Extract legal authority references
            authorities = self._extract_legal_authorities(content)
            enhanced_metadata["legal_authorities"] = authorities
            
            # Extract procedural posture
            posture = self._extract_procedural_posture(content)
            if posture:
                enhanced_metadata["procedural_posture"] = posture
            
            # Extract key legal issues
            issues = self._extract_legal_issues(content)
            enhanced_metadata["legal_issues"] = issues
            
            # Extract outcome/holding
            outcome = self._extract_case_outcome(content)
            if outcome:
                enhanced_metadata["case_outcome"] = outcome
            
            # Court composition analysis
            judges = result.get('judges', [])
            if judges:
                enhanced_metadata["judge_count"] = len(judges)
                enhanced_metadata["unanimous"] = self._detect_unanimous_decision(content)
            
        except Exception as e:
            logger.error(f"Error extracting enhanced metadata: {e}")
            
        return enhanced_metadata
    
    def _extract_legal_concepts(self, content: str, legal_domain: str) -> List[str]:
        """Extract and tag legal concepts from document content"""
        concepts = []
        content_lower = content.lower()
        
        # Legal concept dictionaries by domain
        concept_mapping = {
            "contract_law": [
                "breach of contract", "consideration", "offer and acceptance", "specific performance",
                "damages", "rescission", "unconscionability", "statute of frauds", "parol evidence",
                "third party beneficiary", "assignment", "delegation", "conditions", "warranties"
            ],
            "employment_labor_law": [
                "wrongful termination", "discrimination", "harassment", "retaliation", "wage and hour",
                "overtime", "FLSA", "Title VII", "ADA", "FMLA", "workers compensation",
                "collective bargaining", "union organizing", "at-will employment"
            ],
            "constitutional_law": [
                "due process", "equal protection", "first amendment", "fourth amendment", "commerce clause",
                "supremacy clause", "establishment clause", "free speech", "search and seizure",
                "takings clause", "substantive due process", "procedural due process"
            ],
            "intellectual_property": [
                "patent infringement", "trademark dilution", "copyright fair use", "trade secret",
                "obviousness", "claim construction", "likelihood of confusion", "transformative use",
                "genericness", "abandonment", "misappropriation"
            ],
            "corporate_regulatory": [
                "fiduciary duty", "business judgment rule", "securities fraud", "insider trading",
                "merger and acquisition", "shareholder rights", "derivative suit", "piercing corporate veil",
                "disclosure requirements", "proxy solicitation"
            ],
            "civil_criminal_procedure": [
                "personal jurisdiction", "subject matter jurisdiction", "class action", "summary judgment",
                "discovery", "privilege", "forum non conveniens", "venue", "service of process",
                "pleading standards", "motions to dismiss"
            ]
        }
        
        # Extract concepts for the specific domain
        domain_concepts = concept_mapping.get(legal_domain, [])
        for concept in domain_concepts:
            if concept in content_lower:
                concepts.append(concept)
        
        # Extract general legal concepts regardless of domain
        general_concepts = [
            "injunctive relief", "damages", "attorney fees", "settlement", "judgment",
            "appeal", "remand", "affirm", "reverse", "cert denied", "writ of certiorari"
        ]
        
        for concept in general_concepts:
            if concept in content_lower and concept not in concepts:
                concepts.append(concept)
        
        return concepts[:10]  # Limit to top 10 concepts
    
    def _classify_court_level(self, court_code: str) -> str:
        """Classify court level for hierarchy understanding"""
        if court_code == "scotus":
            return "supreme_court"
        elif court_code.startswith("ca"):
            return "circuit_court"
        elif court_code.endswith("d"):
            return "district_court"
        else:
            return "other"
    
    def _extract_citations(self, content: str) -> List[str]:
        """Extract legal citations from content"""
        import re
        citations = []
        
        # Common citation patterns
        patterns = [
            r'\d+\s+U\.S\.\s+\d+',  # Supreme Court
            r'\d+\s+F\.\d+d\s+\d+',  # Federal cases
            r'\d+\s+S\.Ct\.\s+\d+',  # Supreme Court Reporter
            r'\d+\s+L\.Ed\.\d+d\s+\d+'  # Lawyers' Edition
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            citations.extend(matches)
        
        return list(set(citations))[:20]  # Limit and deduplicate
    
    def _extract_legal_authorities(self, content: str) -> List[str]:
        """Extract legal authorities (statutes, regulations, etc.)"""
        import re
        authorities = []
        
        # Authority patterns
        patterns = [
            r'\d+\s+U\.S\.C\.\s+§\s+\d+',  # U.S. Code
            r'\d+\s+C\.F\.R\.\s+§\s+\d+',  # Code of Federal Regulations
            r'Rule\s+\d+',  # Federal Rules
            r'Fed\.\s*R\.\s*Civ\.\s*P\.\s*\d+',  # Federal Rules of Civil Procedure
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            authorities.extend(matches)
        
        return list(set(authorities))[:10]
    
    def _extract_procedural_posture(self, content: str) -> Optional[str]:
        """Extract procedural posture of the case"""
        content_lower = content.lower()
        
        postures = {
            "motion to dismiss": "motion_to_dismiss",
            "summary judgment": "summary_judgment", 
            "appeal": "appeal",
            "petition for certiorari": "certiorari",
            "preliminary injunction": "preliminary_injunction",
            "class certification": "class_certification",
            "trial": "trial"
        }
        
        for phrase, posture in postures.items():
            if phrase in content_lower:
                return posture
        
        return None
    
    def _extract_legal_issues(self, content: str) -> List[str]:
        """Extract key legal issues from content"""
        issues = []
        content_lower = content.lower()
        
        # Common legal issue indicators
        issue_indicators = [
            "whether", "the issue is", "the question presented", "the court must decide",
            "at issue", "the legal question", "the matter before us"
        ]
        
        import re
        for indicator in issue_indicators:
            pattern = rf"{indicator}[^.]*\."
            matches = re.findall(pattern, content_lower)
            issues.extend(matches[:2])  # Limit per indicator
        
        return issues[:5]  # Limit total issues
    
    def _extract_case_outcome(self, content: str) -> Optional[str]:
        """Extract case outcome/disposition"""
        content_lower = content.lower()
        
        outcomes = {
            "affirmed": "affirmed",
            "reversed": "reversed", 
            "remanded": "remanded",
            "dismissed": "dismissed",
            "granted": "granted",
            "denied": "denied",
            "vacated": "vacated"
        }
        
        for outcome, key in outcomes.items():
            if outcome in content_lower:
                return key
        
        return None
    
    def _detect_unanimous_decision(self, content: str) -> bool:
        """Detect if decision was unanimous"""
        content_lower = content.lower()
        unanimous_indicators = ["unanimous", "unanimously", "per curiam"]
        dissent_indicators = ["dissent", "dissenting", "concur"]
        
        has_unanimous = any(indicator in content_lower for indicator in unanimous_indicators)
        has_dissent = any(indicator in content_lower for indicator in dissent_indicators)
        
        return has_unanimous and not has_dissent
    
    def _meets_quality_filters(self, document: Dict[str, Any]) -> bool:
        """Enhanced quality filters with comprehensive checks"""
        if not self.config["enable_quality_filters"]:
            return len(document["content"].strip()) > 50  # Original minimum
        
        self.quality_metrics.total_processed += 1
        
        # 1. Minimum content length filter (1000 words for bulk mode)
        if document["word_count"] < self.config["min_content_length"]:
            return False
        self.quality_metrics.passed_length_filter += 1
        
        # 2. Precedential status filter - only published/precedential opinions
        precedential_status = document.get("precedential_status", "").strip()
        if precedential_status not in self.config["precedential_status"]:
            return False
        self.quality_metrics.passed_status_filter += 1
        
        # 3. Content type filter - exclude procedural/administrative orders
        title = document.get("title", "").lower()
        content = document.get("content", "").lower()
        
        # Check for excluded keywords that indicate procedural orders
        for keyword in self.config["excluded_keywords"]:
            if keyword in title or keyword in content[:500]:  # Check first 500 chars
                return False
        self.quality_metrics.passed_content_filter += 1
        
        # 4. Date range filter with primary/secondary prioritization
        if self.config["date_range"]:
            date_filed = document.get("date_filed", "")
            if date_filed:
                try:
                    doc_date = datetime.strptime(date_filed.split('T')[0], '%Y-%m-%d')
                    
                    # Primary date range (2020-2025) - higher priority
                    primary_min = datetime.strptime(self.config["date_range"]["primary_min"], '%Y-%m-%d')
                    primary_max = datetime.strptime(self.config["date_range"]["primary_max"], '%Y-%m-%d')
                    
                    # Secondary date range (2015-2019) - lower priority  
                    secondary_min = datetime.strptime(self.config["date_range"]["secondary_min"], '%Y-%m-%d')
                    secondary_max = datetime.strptime(self.config["date_range"]["secondary_max"], '%Y-%m-%d')
                    
                    # Must be in either primary or secondary range
                    in_primary = primary_min <= doc_date <= primary_max
                    in_secondary = secondary_min <= doc_date <= secondary_max
                    
                    if not (in_primary or in_secondary):
                        return False
                        
                    # Mark priority level for later processing
                    document["date_priority"] = "primary" if in_primary else "secondary"
                    
                except:
                    # If date parsing fails, don't filter based on date
                    pass
        self.quality_metrics.passed_date_filter += 1
        
        # 5. Deduplication checks
        case_id = document.get("metadata", {}).get("cluster_id") or document.get("id", "")
        citation = document.get("metadata", {}).get("citation", "")
        
        # Check for duplicate case ID
        if case_id and case_id in self.seen_case_ids:
            self.quality_metrics.duplicates_filtered += 1
            return False
            
        # Check for duplicate citation
        if citation and citation in self.seen_citations:
            self.quality_metrics.duplicates_filtered += 1
            return False
        
        # Add to seen sets
        if case_id:
            self.seen_case_ids.add(case_id)
        if citation:
            self.seen_citations.add(citation)
        
        # 6. Calculate quality score
        quality_score = self._calculate_quality_score(document)
        document["quality_score"] = quality_score
        
        if quality_score < self.config["quality_threshold"]:
            return False
        
        # Update quality metrics
        self.quality_metrics.average_word_count = (
            (self.quality_metrics.average_word_count * (self.quality_metrics.passed_date_filter - 1) + document["word_count"]) 
            / self.quality_metrics.passed_date_filter
        )
        
        return True
    
    def _calculate_quality_score(self, document: Dict[str, Any]) -> float:
        """Calculate quality score for document (0.0 to 1.0)"""
        score = 0.0
        
        # Word count score (30% weight)
        word_count = document.get("word_count", 0)
        if word_count >= 2000:
            score += 0.3
        elif word_count >= 1500:
            score += 0.25
        elif word_count >= 1000:
            score += 0.2
        elif word_count >= 500:
            score += 0.1
        
        # Precedential status score (25% weight)
        status = document.get("precedential_status", "").lower()
        if status == "precedential":
            score += 0.25
        elif status == "published":
            score += 0.2
        
        # Court level score (20% weight)
        court = document.get("court", "").lower()
        if "supreme court" in court:
            score += 0.2
        elif "circuit" in court:
            score += 0.15
        elif "district" in court:
            score += 0.1
        
        # Date recency score (15% weight)
        date_priority = document.get("date_priority", "")
        if date_priority == "primary":  # 2020-2025
            score += 0.15
        elif date_priority == "secondary":  # 2015-2019
            score += 0.1
        
        # Content richness score (10% weight)
        content = document.get("content", "")
        if content:
            # Check for legal citations, structured content
            citation_markers = ["U.S.", "F.2d", "F.3d", "S.Ct.", "§"]
            citation_count = sum(1 for marker in citation_markers if marker in content)
            if citation_count >= 3:
                score += 0.1
            elif citation_count >= 1:
                score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0

    async def bulk_collect_court_decisions(self) -> List[Dict[str, Any]]:
        """
        Comprehensive bulk collection process for 15,000 CourtListener legal documents
        with court hierarchy prioritization, quality control, and intelligent processing
        """
        logger.info("🚀 Starting COMPREHENSIVE BULK COLLECTION PROCESS")
        logger.info("=" * 80)
        logger.info(f"🎯 Target: 15,000 high-quality court decisions")
        logger.info(f"⚖️ Court Hierarchy: Supreme Court → Circuit Courts → District Courts")
        logger.info(f"📊 Quality Filters: {self.config['min_content_length']}+ words, Precedential/Published only")
        logger.info(f"📅 Date Priority: 2020-2025 (primary), 2015-2019 (secondary)")
        logger.info("=" * 80)
        
        content = []
        self.progress.start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                
                # Sort courts by priority for hierarchical collection
                sorted_courts = sorted(self.court_priorities, key=lambda x: (x.priority, x.code))
                
                # PHASE 1: Priority-based Collection by Court Hierarchy
                for court_priority in sorted_courts:
                    court_code = court_priority.code
                    court_name = court_priority.name
                    target_docs = court_priority.target_documents
                    priority_level = court_priority.priority
                    
                    logger.info(f"\n🏛️ COURT PRIORITY {priority_level}: {court_name}")
                    logger.info(f"🎯 Target Documents: {target_docs}")
                    logger.info("-" * 60)
                    
                    court_results = await self._collect_from_single_court(
                        client, court_code, court_name, target_docs
                    )
                    
                    content.extend(court_results)
                    court_priority.collected_documents = len(court_results)
                    self.progress.documents_by_court[court_code] = len(court_results)
                    
                    # Update progress and ETA
                    self._update_progress_metrics()
                    
                    logger.info(f"✅ {court_name}: Collected {len(court_results)}/{target_docs} documents")
                    logger.info(f"📊 Total Progress: {len(content)}/15,000 ({(len(content)/15000)*100:.1f}%)")
                    
                    # Checkpoint save every 1000 documents
                    if len(content) >= self.checkpoint_interval and len(content) % self.checkpoint_interval == 0:
                        await self._save_checkpoint(content)
                        
                    # Stop if we've reached our overall target
                    if len(content) >= 15000:
                        logger.info("🎉 Target of 15,000 documents reached!")
                        break
                
                # PHASE 2: Gap Filling for Underperforming Courts
                if len(content) < 15000:
                    logger.info(f"\n🔄 PHASE 2: Gap Filling ({len(content)}/15,000 collected)")
                    remaining_needed = 15000 - len(content)
                    
                    # Redistribute remaining documents among courts that underperformed
                    underperforming_courts = [
                        court for court in self.court_priorities 
                        if court.collected_documents < court.target_documents * 0.8
                    ]
                    
                    if underperforming_courts:
                        additional_per_court = remaining_needed // len(underperforming_courts)
                        
                        for court_priority in underperforming_courts:
                            if len(content) >= 15000:
                                break
                                
                            logger.info(f"🔄 Gap filling for {court_priority.name}: +{additional_per_court} documents")
                            
                            additional_results = await self._collect_from_single_court(
                                client, court_priority.code, court_priority.name, 
                                additional_per_court, gap_filling=True
                            )
                            
                            content.extend(additional_results)
                            court_priority.collected_documents += len(additional_results)
                            self.progress.documents_by_court[court_priority.code] += len(additional_results)
                
                # PHASE 3: Final Quality Assessment and Reporting
                await self._generate_final_report(content)
                
        except Exception as e:
            logger.error(f"Critical error in bulk collection: {e}", exc_info=True)
            
        return content
    
    async def _collect_from_single_court(self, client: httpx.AsyncClient, court_code: str, 
                                       court_name: str, target_documents: int, 
                                       gap_filling: bool = False) -> List[Dict[str, Any]]:
        """Collect documents from a single court with intelligent query distribution"""
        court_results = []
        
        # Distribute target documents across legal domains
        queries_per_domain = self._distribute_queries_by_court_priority(court_code, target_documents)
        
        for legal_domain, domain_queries in queries_per_domain.items():
            for query, target_per_query in domain_queries:
                try:
                    # Parallel processing for efficiency (respecting rate limits)
                    if self.config["enable_parallel_processing"]:
                        query_results = await self._fetch_paginated_results_parallel(
                            client, query, legal_domain, court_code, court_name, target_per_query
                        )
                    else:
                        query_results = await self._fetch_paginated_results_enhanced(
                            client, query, legal_domain, court_code, court_name, target_per_query
                        )
                    
                    court_results.extend(query_results)
                    
                    # Real-time progress logging
                    if len(query_results) > 0:
                        logger.info(f"  ✅ '{query[:40]}...': {len(query_results)} quality documents")
                    else:
                        logger.info(f"  ❌ '{query[:40]}...': No qualifying documents")
                    
                    # Stop if we've reached the target for this court
                    if len(court_results) >= target_documents:
                        break
                        
                except Exception as e:
                    logger.error(f"Error with query '{query}' in {court_name}: {e}")
                    continue
            
            # Break outer loop if target reached
            if len(court_results) >= target_documents:
                break
        
        return court_results[:target_documents]  # Ensure we don't exceed target
    
    def _distribute_queries_by_court_priority(self, court_code: str, target_documents: int) -> Dict[str, List[tuple]]:
        """Distribute queries intelligently based on court type and target"""
        
        # Get appropriate queries based on court level
        if court_code == "scotus":
            # Supreme Court: Focus on landmark constitutional and high-impact cases
            query_distribution = {
                "constitutional_law": [
                    ("First Amendment free speech restrictions", target_documents // 8),
                    ("Due process substantive procedural", target_documents // 8),
                    ("Equal protection strict scrutiny", target_documents // 8),
                    ("Commerce Clause federal regulatory power", target_documents // 8)
                ],
                "contract_law": [
                    ("breach of contract damages Supreme Court", target_documents // 10),
                    ("contract interpretation parol evidence", target_documents // 10)
                ],
                "intellectual_property": [
                    ("patent infringement claim construction", target_documents // 10),
                    ("copyright fair use transformation", target_documents // 10)
                ],
                "employment_labor_law": [
                    ("employment discrimination Title VII", target_documents // 10),
                    ("Americans with Disabilities Act reasonable accommodation", target_documents // 10)
                ]
            }
        elif court_code.startswith("ca"):
            # Circuit Courts: Broader range of appellate decisions
            query_distribution = {
                "contract_law": [
                    ("breach of contract damages", target_documents // 6),
                    ("contract formation elements", target_documents // 8)
                ],
                "employment_labor_law": [
                    ("employment discrimination Title VII", target_documents // 6),
                    ("wrongful termination at-will employment", target_documents // 8)
                ],
                "intellectual_property": [
                    ("patent infringement claim construction", target_documents // 8),
                    ("trademark dilution likelihood confusion", target_documents // 8)
                ],
                "constitutional_law": [
                    ("First Amendment free speech restrictions", target_documents // 8),
                    ("Fourth Amendment search seizure warrant", target_documents // 8)
                ],
                "corporate_regulatory": [
                    ("securities fraud disclosure requirements", target_documents // 8),
                    ("fiduciary duty business judgment rule", target_documents // 8)
                ]
            }
        else:
            # District Courts: Focus on landmark trial court decisions
            query_distribution = {
                "contract_law": [
                    ("breach of contract damages district court", target_documents // 4),
                    ("contract interpretation landmark", target_documents // 6)
                ],
                "employment_labor_law": [
                    ("employment discrimination class action", target_documents // 4),
                    ("wage hour violations FLSA", target_documents // 6)
                ],
                "intellectual_property": [
                    ("patent infringement jury verdict", target_documents // 5),
                    ("trademark infringement injunction", target_documents // 6)
                ],
                "civil_criminal_procedure": [
                    ("class action certification requirements", target_documents // 5),
                    ("summary judgment material facts", target_documents // 6)
                ]
            }
        
        return query_distribution
    
    async def _fetch_paginated_results_enhanced(self, client: httpx.AsyncClient, query: str,
                                              legal_domain: str, court_code: str, court_name: str,
                                              target_results: int) -> List[Dict[str, Any]]:
        """Enhanced paginated results fetching with intelligent quality filtering"""
        all_results = []
        page_count = 0
        next_url = "https://www.courtlistener.com/api/rest/v3/search/"
        
        # Enhanced parameters for quality
        params = {
            "q": query,
            "type": "o",  # Opinions only
            "order_by": "score desc",
            "court": court_code,
            "format": "json"
        }
        
        # Add quality filters
        if self.config["enable_quality_filters"]:
            params.update({
                "stat_Precedential": "on",  # Only precedential opinions
                "stat_Published": "on",     # Only published opinions
            })
            
            # Prioritize recent cases (2020-2025) but include 2015-2019
            params["filed_after"] = self.config["date_range"]["primary_min"]
            params["filed_before"] = self.config["date_range"]["primary_max"]
        
        while next_url and page_count < self.config["max_pages_per_query"] and len(all_results) < target_results:
            try:
                page_count += 1
                
                # Get API key with intelligent rotation
                api_key = self._get_next_api_key()
                if not api_key:
                    logger.warning("No API keys available, waiting...")
                    await asyncio.sleep(5)
                    continue
                
                key_index = next((i for i, k in enumerate(self.courtlistener_api_keys) if k == api_key), 0)
                await self._wait_for_rate_limit(key_index)
                
                headers = {"Authorization": f"Token {api_key}", "Accept": "application/json"}
                
                # Make request
                if page_count == 1:
                    response = await client.get(next_url, headers=headers, params=params)
                else:
                    response = await client.get(next_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if not results:
                        break
                    
                    # Process and filter results with enhanced quality checks
                    quality_results = []
                    for result in results:
                        if len(all_results) >= target_results:
                            break
                        
                        processed_result = await self._process_court_result(
                            result, query, legal_domain, court_code, court_name
                        )
                        
                        if processed_result and self._meets_quality_filters(processed_result):
                            quality_results.append(processed_result)
                    
                    all_results.extend(quality_results)
                    next_url = data.get('next')
                    
                    # Reset consecutive failures on success
                    self.rate_limits[key_index].consecutive_failures = 0
                    
                elif response.status_code in [429, 500, 502, 503, 504]:
                    should_retry = await self._handle_api_error(key_index, response.status_code, response.text)
                    if should_retry:
                        page_count -= 1  # Don't count failed attempts
                        continue
                    else:
                        break
                else:
                    logger.warning(f"API request failed with status {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching page {page_count}: {e}")
                break
        
        return all_results
    
    async def _fetch_paginated_results_parallel(self, client: httpx.AsyncClient, query: str,
                                              legal_domain: str, court_code: str, court_name: str,
                                              target_results: int) -> List[Dict[str, Any]]:
        """Parallel processing of paginated results (respecting rate limits)"""
        # For now, use sequential processing to ensure rate limit compliance
        # TODO: Implement true parallel processing with semaphore and rate limit coordination
        return await self._fetch_paginated_results_enhanced(
            client, query, legal_domain, court_code, court_name, target_results
        )
    
    def _update_progress_metrics(self):
        """Update progress metrics and ETA calculations"""
        current_time = time.time()
        elapsed_time = current_time - self.progress.start_time
        total_collected = sum(self.progress.documents_by_court.values())
        
        if total_collected > 0:
            self.progress.average_doc_time = elapsed_time / total_collected
            remaining_docs = 15000 - total_collected
            self.progress.eta_seconds = remaining_docs * self.progress.average_doc_time
        
        # Update quality metrics
        if self.quality_metrics.total_processed > 0:
            success_rate = (
                self.quality_metrics.passed_date_filter / self.quality_metrics.total_processed
            ) * 100
            
            logger.info(f"📊 Quality Metrics: {success_rate:.1f}% pass rate, "
                       f"avg {self.quality_metrics.average_word_count:.0f} words")
    
    async def _save_checkpoint(self, content: List[Dict[str, Any]]):
        """Save collection checkpoint for resumability"""
        checkpoint_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "documents_collected": len(content),
            "court_progress": {court.code: court.collected_documents for court in self.court_priorities},
            "quality_metrics": {
                "total_processed": self.quality_metrics.total_processed,
                "average_word_count": self.quality_metrics.average_word_count,
                "duplicates_filtered": self.quality_metrics.duplicates_filtered
            }
        }
        
        checkpoint_file = f"/app/bulk_collection_checkpoint_{int(time.time())}.json"
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            logger.info(f"📋 Checkpoint saved: {checkpoint_file}")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
    
    async def _generate_final_report(self, content: List[Dict[str, Any]]):
        """Generate comprehensive final collection report"""
        total_time = time.time() - self.progress.start_time
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 BULK COLLECTION COMPLETED - FINAL REPORT")
        logger.info("=" * 80)
        
        # Overall statistics
        logger.info(f"📊 COLLECTION SUMMARY:")
        logger.info(f"  Total Documents Collected: {len(content):,}")
        logger.info(f"  Target Achievement: {(len(content)/15000)*100:.1f}%")
        logger.info(f"  Total Collection Time: {total_time/3600:.1f} hours")
        logger.info(f"  Average Documents/Hour: {len(content)/(total_time/3600):.1f}")
        
        # Court hierarchy breakdown
        logger.info(f"\n🏛️ COURT HIERARCHY BREAKDOWN:")
        total_priority_1 = sum(court.collected_documents for court in self.court_priorities if court.priority == 1)
        total_priority_2 = sum(court.collected_documents for court in self.court_priorities if court.priority == 2)  
        total_priority_3 = sum(court.collected_documents for court in self.court_priorities if court.priority == 3)
        
        logger.info(f"  Supreme Court (Priority 1): {total_priority_1:,} documents")
        logger.info(f"  Circuit Courts (Priority 2): {total_priority_2:,} documents") 
        logger.info(f"  District Courts (Priority 3): {total_priority_3:,} documents")
        
        # Quality metrics
        logger.info(f"\n📈 QUALITY METRICS:")
        logger.info(f"  Documents Processed: {self.quality_metrics.total_processed:,}")
        logger.info(f"  Quality Pass Rate: {(len(content)/max(self.quality_metrics.total_processed, 1))*100:.1f}%")
        logger.info(f"  Average Word Count: {self.quality_metrics.average_word_count:.0f}")
        logger.info(f"  Duplicates Filtered: {self.quality_metrics.duplicates_filtered:,}")
        
        # Legal domain distribution
        domain_counts = {}
        for doc in content:
            domain = doc.get("legal_domain", "unknown")
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        logger.info(f"\n⚖️ LEGAL DOMAIN DISTRIBUTION:")
        for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {domain}: {count:,} documents")
        
        # Date distribution
        primary_date_count = sum(1 for doc in content if doc.get("date_priority") == "primary")
        secondary_date_count = sum(1 for doc in content if doc.get("date_priority") == "secondary")
        
        logger.info(f"\n📅 DATE DISTRIBUTION:")
        logger.info(f"  Primary Period (2020-2025): {primary_date_count:,} documents")
        logger.info(f"  Secondary Period (2015-2019): {secondary_date_count:,} documents")
        
        logger.info("=" * 80)
    async def _fetch_court_decisions(self) -> List[Dict[str, Any]]:
        """Fetch comprehensive court decisions using CourtListener API with enhanced pagination and bulk collection"""
        
        # Use the new comprehensive bulk collection system for BULK mode
        if self.collection_mode == CollectionMode.BULK:
            logger.info("🚀 Using COMPREHENSIVE BULK COLLECTION SYSTEM")
            return await self.bulk_collect_court_decisions()
        
        # Original implementation for STANDARD mode (backward compatibility)
        content = []
        
        if not self.courtlistener_api_keys:
            logger.warning("No CourtListener API keys available, skipping court decisions")
            return content
        
        logger.info(f"🚀 Starting CourtListener collection in {self.collection_mode.value.upper()} mode")
        logger.info(f"🔑 Using {len(self.courtlistener_api_keys)} API keys with intelligent rotation")
        logger.info(f"📊 Target: {self.config['results_per_query']} results per query, {self.config['max_pages_per_query']} max pages")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # STANDARD MODE: Original search strategy
                
                # CONTRACT LAW - 15 queries (target 3,000 docs in bulk mode)
                contract_law_queries = [
                    "breach of contract damages",
                    "contract formation elements", 
                    "specific performance remedy",
                    "contract interpretation parol evidence",
                    "unconscionable contract terms",
                    "contract consideration adequacy",
                    "contract modification statute frauds",
                    "contract third party beneficiary",
                    "contract assignment delegation",
                    "contract discharge impossibility",
                    "contract warranties express implied",
                    "contract liquidated damages penalty",
                    "contract rescission restitution",
                    "contract capacity minors incapacity",
                    "contract duress undue influence"
                ]
                
                # EMPLOYMENT LAW - 12 queries (target 2,500 docs in bulk mode)
                employment_law_queries = [
                    "employment discrimination Title VII",
                    "wrongful termination at-will employment",
                    "wage hour violations FLSA overtime",
                    "workplace harassment hostile environment",
                    "employment retaliation whistleblower protection",
                    "Americans with Disabilities Act reasonable accommodation",
                    "Family Medical Leave Act FMLA interference",
                    "employment non-compete agreements enforceability",
                    "workplace safety OSHA violations",
                    "employment classification independent contractor",
                    "union organizing collective bargaining NLRA",
                    "employment arbitration agreements enforceability"
                ]
                
                # CONSTITUTIONAL LAW - 10 queries (target 2,000 docs in bulk mode)
                constitutional_law_queries = [
                    "First Amendment free speech restrictions",
                    "Fourth Amendment search seizure warrant",
                    "Due process substantive procedural",
                    "Equal protection strict scrutiny",
                    "Commerce Clause federal regulatory power",
                    "Establishment Clause religious freedom",
                    "Second Amendment right bear arms",
                    "Fourteenth Amendment civil rights",
                    "Takings Clause eminent domain compensation",
                    "Supremacy Clause federal preemption"
                ]
                
                # INTELLECTUAL PROPERTY - 8 queries (target 1,500 docs in bulk mode)
                intellectual_property_queries = [
                    "patent infringement claim construction",
                    "trademark dilution likelihood confusion",
                    "copyright fair use transformation",
                    "trade secret misappropriation protection",
                    "patent obviousness prior art",
                    "trademark generic descriptive marks",
                    "copyright derivative works authorization",
                    "design patent infringement ordinary observer"
                ]
                
                # CORPORATE LAW - 6 queries (target 1,200 docs in bulk mode)
                corporate_law_queries = [
                    "fiduciary duty business judgment rule",
                    "securities fraud disclosure requirements",
                    "merger acquisition shareholder rights",
                    "corporate governance derivative suits",
                    "insider trading material information",
                    "corporate veil piercing alter ego"
                ]
                
                # CIVIL PROCEDURE - 5 queries (target 1,000 docs in bulk mode)
                civil_procedure_queries = [
                    "personal jurisdiction minimum contacts",
                    "class action certification requirements",
                    "summary judgment material facts",
                    "discovery privilege attorney-client",
                    "forum non conveniens venue transfer"
                ]
                
                # CRIMINAL LAW - 4 queries (target 800 docs in bulk mode)
                criminal_law_queries = [
                    "criminal intent mens rea elements",
                    "criminal conspiracy agreement overt act",
                    "criminal sentencing guidelines departures",
                    "criminal evidence exclusionary rule"
                ]
                
                # Combine all queries with domain labels
                all_queries = [
                    (query, "contract_law") for query in contract_law_queries
                ] + [
                    (query, "employment_labor_law") for query in employment_law_queries
                ] + [
                    (query, "constitutional_law") for query in constitutional_law_queries
                ] + [
                    (query, "intellectual_property") for query in intellectual_property_queries
                ] + [
                    (query, "corporate_regulatory") for query in corporate_law_queries
                ] + [
                    (query, "civil_criminal_procedure") for query in civil_procedure_queries
                ] + [
                    (query, "civil_criminal_procedure") for query in criminal_law_queries
                ]
                
                # Update progress tracking
                self.progress.total_queries = len(all_queries)
                
                logger.info(f"📚 Executing {len(all_queries)} targeted search queries for comprehensive legal document collection")
                
                # Simplified court coverage for standard mode
                courts = [
                    ("scotus", "Supreme Court"),           # Supreme Court
                    ("ca1", "1st Circuit Court"),         # 1st Circuit  
                    ("ca2", "2nd Circuit Court"),         # 2nd Circuit
                    ("ca9", "9th Circuit Court"),         # 9th Circuit
                ]
                
                query_count = 0
                batch_results = []
                
                # Execute searches - simplified for standard mode
                for query, legal_domain in all_queries[:10]:  # Limit queries in standard mode
                    for court_code, court_name in courts:
                        try:
                            query_count += 1
                            self.progress.completed_queries = query_count
                            
                            # Base URL and parameters for CourtListener API
                            base_url = "https://www.courtlistener.com/api/rest/v3/search/"
                            params = {
                                "q": query,
                                "type": "o",  # Opinions
                                "order_by": "score desc",
                                "court": court_code,
                                "format": "json"
                            }
                            
                            logger.info(f"🔍 Query {query_count}: '{query}' in {court_name}")
                            
                            headers = {"Accept": "application/json"}
                            
                            # Standard mode: single page, limited results
                            api_key = self._get_next_api_key()
                            if api_key:
                                headers["Authorization"] = f"Token {api_key}"
                                response = await client.get(base_url, headers=headers, params=params)
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    raw_results = data.get('results', [])[:self.config["results_per_query"]]
                                    
                                    results = []
                                    for result in raw_results:
                                        processed = await self._process_court_result(
                                            result, query, legal_domain, court_code, court_name
                                        )
                                        if processed and self._meets_quality_filters(processed):
                                            results.append(processed)
                                else:
                                    results = []
                            else:
                                results = []
                            
                            # Add results to batch
                            batch_results.extend(results)
                            self.progress.total_documents += len(results)
                            
                            if results:
                                self.progress.successful_queries += 1
                                logger.info(f"✅ Query {query_count} successful: Added {len(results)} quality documents")
                            else:
                                logger.info(f"❌ Query {query_count} failed or no results")
                                self.progress.failed_queries.append(f"{query} in {court_name}")
                            
                        except Exception as e:
                            logger.error(f"Error processing query '{query}' in {court_name}: {e}")
                            self.progress.failed_queries.append(f"{query} in {court_name} - Error: {str(e)}")
                            continue
                
                # Process final batch
                content.extend(batch_results)
                
                # Final statistics
                success_rate = (self.progress.successful_queries / query_count) * 100 if query_count > 0 else 0
                
                logger.info(f"🎉 Court decisions collection completed!")
                logger.info(f"📈 Final Statistics:")
                logger.info(f"   - Collection Mode: {self.collection_mode.value.upper()}")
                logger.info(f"   - Total Queries: {query_count}")
                logger.info(f"   - Successful Queries: {self.progress.successful_queries}")
                logger.info(f"   - Success Rate: {success_rate:.1f}%")
                logger.info(f"   - Documents Collected: {len(content)}")
                        
        except Exception as e:
            logger.error(f"Critical error in CourtListener API collection: {e}")
            
        return content
    
    async def _fetch_state_legal_content(self) -> List[Dict[str, Any]]:
        """Fetch state-specific legal content"""
        content = []
        
        state_queries = [
            # California
            "site:leginfo.legislature.ca.gov California contract law",
            "site:leginfo.legislature.ca.gov California employment law",
            "site:leginfo.legislature.ca.gov California corporate code",
            
            # New York
            "site:nysenate.gov New York contract law statutes",
            "site:nysenate.gov New York employment law",
            "site:nysenate.gov New York business corporation law",
            
            # Texas
            "site:statutes.capitol.texas.gov Texas contract law",
            "site:statutes.capitol.texas.gov Texas employment law",
            "site:statutes.capitol.texas.gov Texas business organizations code"
        ]
        
        for query in state_queries:
            try:
                jurisdiction = "us_california" if "California" in query else "us_new_york" if "New York" in query else "us_texas"
                results = await self._search_legal_content(query, jurisdiction=jurisdiction)
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching state content for query '{query}': {e}")
                
        return content
    
    async def _fetch_federal_agency_content(self) -> List[Dict[str, Any]]:
        """Fetch federal agency guidelines and regulations"""
        content = []
        
        agency_queries = [
            "site:sec.gov SEC securities regulations compliance",
            "site:ftc.gov FTC consumer protection guidelines",
            "site:dol.gov DOL employment regulations FLSA",
            "site:irs.gov IRS tax regulations business",
            "site:uspto.gov USPTO patent trademark regulations",
            "site:nlrb.gov NLRB labor relations regulations",
            "site:eeoc.gov EEOC employment discrimination guidelines"
        ]
        
        for query in agency_queries:
            try:
                results = await self._search_legal_content(query, jurisdiction="us_federal", document_type="regulation")
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching agency content for query '{query}': {e}")
                
        return content
    
    async def _fetch_indian_central_laws(self) -> List[Dict[str, Any]]:
        """Fetch Indian Central/Union legislation"""
        content = []
        
        indian_queries = [
            "site:indiacode.nic.in Indian Contract Act",
            "site:indiacode.nic.in Indian Companies Act 2013",
            "site:indiacode.nic.in Indian Employment laws Labour Code",
            "site:indiacode.nic.in Indian Copyright Act",
            "site:indiacode.nic.in Indian Patent Act",
            "site:indiacode.nic.in Indian Constitution fundamental rights",
            "site:indiacode.nic.in Indian Income Tax Act",
            "site:indiacode.nic.in Indian Criminal Procedure Code",
            "site:indiacode.nic.in Indian Civil Procedure Code"
        ]
        
        for query in indian_queries:
            try:
                results = await self._search_legal_content(query, jurisdiction="india_central")
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching Indian central laws for query '{query}': {e}")
                
        return content
    
    async def _fetch_indian_supreme_court_decisions(self) -> List[Dict[str, Any]]:
        """Fetch Indian Supreme Court decisions"""
        content = []
        
        # Search for landmark Indian Supreme Court cases
        sc_queries = [
            "site:sci.gov.in Supreme Court India contract law judgments",
            "site:sci.gov.in Supreme Court India employment law decisions", 
            "site:sci.gov.in Supreme Court India constitutional law judgments",
            "site:sci.gov.in Supreme Court India corporate law decisions",
            "site:sci.gov.in Supreme Court India intellectual property judgments"
        ]
        
        for query in sc_queries:
            try:
                results = await self._search_legal_content(query, jurisdiction="india_central", document_type="court_decision")
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching Indian SC decisions for query '{query}': {e}")
                
        return content
    
    async def _fetch_indian_regulatory_content(self) -> List[Dict[str, Any]]:
        """Fetch Indian regulatory body content"""
        content = []
        
        regulatory_queries = [
            "site:sebi.gov.in SEBI securities regulations guidelines",
            "site:rbi.org.in RBI banking regulations guidelines",
            "site:mca.gov.in MCA company law regulations",
            "site:cbdt.gov.in CBDT income tax regulations",
            "site:cbec.gov.in customs excise regulations GST",
            "site:dipp.gov.in DIPP industrial policy regulations"
        ]
        
        for query in regulatory_queries:
            try:
                results = await self._search_legal_content(query, jurisdiction="india_central", document_type="regulation")
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching Indian regulatory content for query '{query}': {e}")
                
        return content
    
    async def _fetch_indian_state_laws(self) -> List[Dict[str, Any]]:
        """Fetch Indian state-specific laws"""
        content = []
        
        state_queries = [
            # Maharashtra
            "Maharashtra state laws employment contract",
            "Maharashtra state commercial laws",
            "Maharashtra state real estate laws",
            
            # Tamil Nadu  
            "Tamil Nadu state laws employment",
            "Tamil Nadu state commercial regulations",
            "Tamil Nadu state real estate laws"
        ]
        
        for query in state_queries:
            try:
                jurisdiction = "india_maharashtra" if "Maharashtra" in query else "india_tamil_nadu"
                results = await self._search_legal_content(query, jurisdiction=jurisdiction)
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching Indian state laws for query '{query}': {e}")
                
        return content
    
    async def _fetch_legal_definitions(self) -> List[Dict[str, Any]]:
        """Fetch legal definitions and concepts"""
        content = []
        
        definition_queries = [
            "legal definitions contract law terms",
            "legal definitions employment law terms",
            "legal definitions intellectual property terms",
            "legal definitions corporate law terms",
            "legal definitions civil procedure terms",
            "legal definitions criminal law terms"
        ]
        
        for query in definition_queries:
            try:
                results = await self._search_legal_content(query, document_type="definition")
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching legal definitions for query '{query}': {e}")
                
        return content
    
    async def _fetch_legal_procedures(self) -> List[Dict[str, Any]]:
        """Fetch legal procedures and practices"""
        content = []
        
        procedure_queries = [
            "legal procedures contract negotiation",
            "legal procedures employment termination",
            "legal procedures patent application",
            "legal procedures corporate formation",
            "legal procedures court filing civil",
            "legal procedures criminal defense"
        ]
        
        for query in procedure_queries:
            try:
                results = await self._search_legal_content(query, document_type="procedure")
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching legal procedures for query '{query}': {e}")
                
        return content
    
    async def _fetch_international_legal_standards(self) -> List[Dict[str, Any]]:
        """Fetch international legal standards"""
        content = []
        
        international_queries = [
            "GDPR data protection regulations EU",
            "WIPO intellectual property international standards",
            "UN trade law international commercial",
            "ISO legal compliance standards",
            "WTO trade regulations international"
        ]
        
        for query in international_queries:
            try:
                results = await self._search_legal_content(query, jurisdiction="international")
                content.extend(results)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error fetching international standards for query '{query}': {e}")
                
        return content
    
    async def _search_legal_content(self, query: str, jurisdiction: str = "general", 
                                  document_type: str = "statute") -> List[Dict[str, Any]]:
        """Search for legal content using SerpAPI"""
        content = []
        
        if not self.serp_api_key or not SERPAPI_AVAILABLE:
            logger.warning("SerpAPI not available or key missing, skipping search")
            return content
            
        try:
            client = GoogleSearch(api_key=self.serp_api_key)
            results = client.search({
                "q": query,
                "num": 10,  # Get top 10 results
                "hl": "en",
                "gl": "us"
            })
            
            for i, result in enumerate(results.get("organic_results", [])[:5]):  # Limit to top 5
                try:
                    # Extract and clean content
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    url = result.get("link", "")
                    
                    if not title or not snippet:
                        continue
                        
                    # Try to fetch full content
                    full_content = await self._fetch_full_content(url)
                    content_text = full_content if full_content else snippet
                    
                    # Skip if content too short
                    if len(content_text.strip()) < 100:
                        continue
                        
                    legal_doc = {
                        "id": f"search_{jurisdiction}_{document_type}_{i}_{int(time.time())}",
                        "title": title,
                        "content": content_text,
                        "source": "Web Search",
                        "source_url": url,
                        "jurisdiction": jurisdiction,
                        "legal_domain": self._categorize_content(query + " " + title + " " + snippet),
                        "document_type": document_type,
                        "metadata": {
                            "search_query": query,
                            "search_rank": i + 1,
                            "snippet": snippet
                        },
                        "created_at": datetime.utcnow().isoformat(),
                        "content_hash": self._generate_content_hash(content_text)
                    }
                    
                    content.append(legal_doc)
                    
                except Exception as e:
                    logger.error(f"Error processing search result: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error with SerpAPI search for '{query}': {e}")
            
        return content
    
    async def _fetch_full_content(self, url: str) -> Optional[str]:
        """Fetch full content from URL"""
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            ) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    # Parse HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Limit content length
                    if len(text) > 5000:
                        text = text[:5000] + "..."
                        
                    return text
                    
        except Exception as e:
            logger.debug(f"Could not fetch full content from {url}: {e}")
            
        return None
    
    def _categorize_content(self, text: str) -> str:
        """Categorize content into legal domains"""
        text_lower = text.lower()
        
        domain_keywords = {
            "contract_law": ["contract", "agreement", "breach", "consideration", "offer", "acceptance"],
            "employment_labor_law": ["employment", "labor", "worker", "employee", "workplace", "wage", "overtime", "discrimination"],
            "intellectual_property": ["patent", "trademark", "copyright", "trade secret", "intellectual property", "IP"],
            "corporate_regulatory": ["corporation", "corporate", "company", "business", "securities", "compliance", "regulation"],
            "civil_criminal_procedure": ["civil procedure", "criminal procedure", "court", "litigation", "trial", "evidence"],
            "constitutional_law": ["constitution", "constitutional", "rights", "amendment", "due process", "equal protection"],
            "taxation_financial": ["tax", "taxation", "financial", "IRS", "income", "deduction", "audit"],
            "real_estate_law": ["real estate", "property", "lease", "landlord", "tenant", "mortgage", "deed"],
            "family_law": ["family", "divorce", "custody", "marriage", "adoption", "domestic"],
            "immigration_law": ["immigration", "visa", "citizenship", "deportation", "asylum", "green card"]
        }
        
        # Count keyword matches for each domain
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        # Return domain with highest score, or general if no matches
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        else:
            return "general_law"
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    def _deduplicate_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate content based on content hash"""
        seen_hashes = set()
        deduplicated = []
        
        for item in content_list:
            content_hash = item.get("content_hash")
            if content_hash and content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                deduplicated.append(item)
        
        logger.info(f"Deduplicated {len(content_list) - len(deduplicated)} duplicate documents")
        return deduplicated
    
    def save_knowledge_base(self, filepath: str = "/app/legal_knowledge_base.json"):
        """Save knowledge base to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Knowledge base saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        if not self.knowledge_base:
            return {"total_documents": 0}
            
        stats = {
            "total_documents": len(self.knowledge_base),
            "by_jurisdiction": {},
            "by_legal_domain": {},
            "by_document_type": {},
            "by_source": {}
        }
        
        for doc in self.knowledge_base:
            # Count by jurisdiction
            jurisdiction = doc.get("jurisdiction", "unknown")
            stats["by_jurisdiction"][jurisdiction] = stats["by_jurisdiction"].get(jurisdiction, 0) + 1
            
            # Count by legal domain
            domain = doc.get("legal_domain", "unknown")
            stats["by_legal_domain"][domain] = stats["by_legal_domain"].get(domain, 0) + 1
            
            # Count by document type
            doc_type = doc.get("document_type", "unknown")
            stats["by_document_type"][doc_type] = stats["by_document_type"].get(doc_type, 0) + 1
            
            # Count by source
            source = doc.get("source", "unknown")
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
        
        return stats


# Main execution function
async def build_legal_knowledge_base(collection_mode: CollectionMode = CollectionMode.STANDARD):
    """Main function to build comprehensive legal knowledge base with configurable collection mode"""
    builder = LegalKnowledgeBuilder(collection_mode=collection_mode)
    
    try:
        logger.info(f"🚀 Starting legal knowledge base building in {collection_mode.value.upper()} mode")
        
        # Build the knowledge base
        knowledge_base = await builder.build_comprehensive_knowledge_base()
        
        # Save to file with mode-specific filename
        filename_suffix = "_bulk" if collection_mode == CollectionMode.BULK else "_standard"
        filepath = f"/app/legal_knowledge_base{filename_suffix}.json"
        builder.save_knowledge_base(filepath)
        
        # Print statistics
        stats = builder.get_knowledge_base_stats()
        print("\n" + "="*60)
        print(f"📊 LEGAL KNOWLEDGE BASE STATISTICS ({collection_mode.value.upper()} MODE)")
        print("="*60)
        print(f"Total Documents: {stats['total_documents']}")
        
        if collection_mode == CollectionMode.BULK:
            target_achievement = (stats['total_documents'] / 15000) * 100
            print(f"Target Achievement: {target_achievement:.1f}% of 15,000 documents")
        
        print(f"\n🎯 Collection Progress:")
        print(f"  Total Queries: {builder.progress.total_queries}")
        print(f"  Completed Queries: {builder.progress.completed_queries}")
        print(f"  Successful Queries: {builder.progress.successful_queries}")
        print(f"  Failed Queries: {len(builder.progress.failed_queries)}")
        
        print("\n📍 By Jurisdiction:")
        for jurisdiction, count in sorted(stats['by_jurisdiction'].items()):
            print(f"  {jurisdiction}: {count}")
        
        print("\n⚖️ By Legal Domain:")
        for domain, count in sorted(stats['by_legal_domain'].items()):
            print(f"  {domain}: {count}")
        
        print("\n📄 By Document Type:")
        for doc_type, count in sorted(stats['by_document_type'].items()):
            print(f"  {doc_type}: {count}")
            
        print("\n🔍 By Source:")
        for source, count in sorted(stats['by_source'].items()):
            print(f"  {source}: {count}")
        
        if builder.progress.failed_queries:
            print(f"\n⚠️ Failed Queries ({len(builder.progress.failed_queries)}):")
            for failed_query in builder.progress.failed_queries[:10]:  # Show first 10
                print(f"  - {failed_query}")
            if len(builder.progress.failed_queries) > 10:
                print(f"  ... and {len(builder.progress.failed_queries) - 10} more")
        
        print(f"\n✅ Legal knowledge base created successfully in {collection_mode.value.upper()} mode!")
        print(f"📁 Saved to: {filepath}")
        return knowledge_base
        
    except Exception as e:
        logger.error(f"Error building knowledge base: {e}")
        return []


# Convenience functions for different collection modes
async def build_standard_knowledge_base():
    """Build knowledge base in standard mode (backward compatible)"""
    return await build_legal_knowledge_base(CollectionMode.STANDARD)

async def build_bulk_knowledge_base():
    """Build knowledge base in bulk mode (15,000+ documents target)"""
    return await build_legal_knowledge_base(CollectionMode.BULK)


if __name__ == "__main__":
    import sys
    
    # Check command line arguments for collection mode
    collection_mode = CollectionMode.STANDARD
    if len(sys.argv) > 1:
        mode_arg = sys.argv[1].lower()
        if mode_arg in ['bulk', 'b']:
            collection_mode = CollectionMode.BULK
        elif mode_arg in ['standard', 's']:
            collection_mode = CollectionMode.STANDARD
        else:
            print("Usage: python legal_knowledge_builder.py [standard|s|bulk|b]")
            print("Default: standard mode (backward compatible)")
            sys.exit(1)
    
    print(f"🚀 Running Legal Knowledge Builder in {collection_mode.value.upper()} mode")
    
    # Run the knowledge base builder
    asyncio.run(build_legal_knowledge_base(collection_mode))
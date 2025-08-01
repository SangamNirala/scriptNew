"""
Knowledge Base Integration and Quality Assurance System
Days 12-14: Comprehensive Integration, Processing & Quality Assurance

This module implements a comprehensive system for:
1. Integration & consolidation of all existing legal documents
2. Quality assurance and validation systems  
3. Performance optimization for 25,000+ documents
4. Monitoring and analytics implementation
"""

import asyncio
import json
import logging
import os
import time
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from pathlib import Path

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SourceMetadata:
    """Metadata for different legal document sources"""
    name: str
    authority_weight: float  # 0.0-1.0, higher = more authoritative
    document_types: List[str]
    quality_threshold: float
    deduplication_fields: List[str]

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for document validation"""
    total_documents: int = 0
    passed_content_validation: int = 0
    passed_citation_validation: int = 0
    passed_jurisdiction_validation: int = 0
    passed_date_validation: int = 0
    duplicates_removed: int = 0
    authority_conflicts_resolved: int = 0
    metadata_enhanced: int = 0
    
    # Quality scores
    average_content_score: float = 0.0
    average_authority_score: float = 0.0
    average_completeness_score: float = 0.0

@dataclass
class IntegrationProgress:
    """Track integration progress across all phases"""
    phase: str
    start_time: datetime
    documents_processed: int = 0
    documents_validated: int = 0
    documents_integrated: int = 0
    errors_encountered: int = 0
    estimated_completion: Optional[datetime] = None

class KnowledgeIntegrationSystem:
    """Comprehensive knowledge base integration and quality assurance system"""
    
    def __init__(self):
        # MongoDB connection
        self.mongo_client = None
        self.db = None
        
        # Source authority hierarchy (Court decisions > Statutes > Regulations > Academic)
        self.source_hierarchy = {
            "supreme_court": SourceMetadata("Supreme Court", 1.0, ["court_decision"], 0.9, ["case_name", "citation"]),
            "circuit_court": SourceMetadata("Circuit Court", 0.9, ["court_decision"], 0.85, ["case_name", "citation"]),
            "district_court": SourceMetadata("District Court", 0.8, ["court_decision"], 0.8, ["case_name", "citation"]),
            "federal_statute": SourceMetadata("Federal Statute", 0.9, ["statute"], 0.85, ["title", "usc_section"]),
            "federal_regulation": SourceMetadata("Federal Regulation", 0.7, ["regulation"], 0.75, ["title", "cfr_section"]),
            "state_statute": SourceMetadata("State Statute", 0.75, ["statute"], 0.8, ["title", "state_code_section"]),
            "state_regulation": SourceMetadata("State Regulation", 0.65, ["regulation"], 0.7, ["title", "state_reg_section"]),
            "academic_paper": SourceMetadata("Academic Paper", 0.6, ["academic"], 0.8, ["title", "author", "doi"]),
            "law_review": SourceMetadata("Law Review", 0.55, ["academic"], 0.75, ["title", "journal", "volume"]),
            "government_report": SourceMetadata("Government Report", 0.7, ["report"], 0.75, ["title", "agency", "report_number"]),
            "legal_encyclopedia": SourceMetadata("Legal Encyclopedia", 0.5, ["reference"], 0.7, ["title", "topic"])
        }
        
        # Enhanced legal categorization (50+ subcategories)
        self.enhanced_categories = {
            "contract_law": [
                "breach_of_contract", "contract_formation", "consideration", "contract_interpretation",
                "remedies_damages", "specific_performance", "unconscionability", "statute_of_frauds",
                "third_party_beneficiaries", "assignment_delegation", "conditions_warranties",
                "discharge_frustration", "government_contracts", "international_contracts"
            ],
            "employment_labor_law": [
                "wrongful_termination", "employment_discrimination", "wage_hour_law", "workplace_safety",
                "workers_compensation", "unemployment_benefits", "collective_bargaining", "union_organizing",
                "employment_contracts", "non_compete_agreements", "whistleblower_protection",
                "family_medical_leave", "disability_accommodation", "retirement_benefits"
            ],
            "intellectual_property": [
                "patent_law", "trademark_law", "copyright_law", "trade_secrets", "patent_prosecution",
                "patent_litigation", "trademark_prosecution", "trademark_disputes", "copyright_infringement",
                "fair_use_doctrine", "dmca_provisions", "ip_licensing", "international_ip", "trade_dress"
            ],
            "constitutional_law": [
                "first_amendment", "fourth_amendment", "fifth_amendment", "fourteenth_amendment",
                "due_process_clause", "equal_protection", "commerce_clause", "supremacy_clause",
                "establishment_clause", "free_exercise_clause", "takings_clause", "privileges_immunities",
                "separation_powers", "federalism"
            ],
            "corporate_regulatory": [
                "securities_law", "corporate_governance", "merger_acquisition", "shareholder_rights",
                "fiduciary_duties", "business_judgment_rule", "proxy_regulations", "insider_trading",
                "public_offerings", "private_placements", "investment_advisors", "broker_dealers",
                "corporate_disclosure", "anti_fraud_provisions"
            ],
            "civil_criminal_procedure": [
                "personal_jurisdiction", "subject_matter_jurisdiction", "venue", "service_process",
                "pleading_standards", "discovery_rules", "summary_judgment", "class_actions",
                "appeals_procedure", "evidence_rules", "criminal_procedure", "search_seizure",
                "miranda_rights", "jury_selection"
            ],
            "taxation_financial": [
                "income_tax", "corporate_tax", "estate_gift_tax", "employment_tax", "tax_procedure",
                "tax_controversies", "international_tax", "state_local_tax", "tax_exempt_organizations",
                "retirement_plans", "employee_benefits_tax", "partnership_tax", "s_corporation_tax"
            ],
            "real_estate_law": [
                "real_estate_transactions", "landlord_tenant", "property_rights", "zoning_law",
                "construction_law", "real_estate_finance", "title_insurance", "eminent_domain",
                "environmental_law", "land_use_planning", "commercial_leasing", "residential_sales"
            ],
            "family_law": [
                "divorce_separation", "child_custody", "child_support", "spousal_support",
                "adoption_law", "domestic_violence", "prenuptial_agreements", "property_division",
                "paternity_issues", "guardianship", "domestic_relations", "juvenile_law"
            ],
            "immigration_law": [
                "visa_applications", "green_card_process", "citizenship_naturalization", "deportation_removal",
                "asylum_refugee", "immigration_enforcement", "family_immigration", "employment_immigration",
                "student_visas", "temporary_visas", "immigration_courts", "administrative_appeals"
            ]
        }
        
        # Quality validation rules
        self.validation_rules = {
            "min_content_length": 500,  # Minimum 500 characters
            "min_word_count": 100,      # Minimum 100 words
            "max_content_length": 50000, # Maximum 50,000 characters
            "required_fields": ["title", "content", "source", "jurisdiction", "legal_domain"],
            "valid_jurisdictions": [
                "us_federal", "us_california", "us_new_york", "us_texas", "us_florida",
                "us_illinois", "us_pennsylvania", "us_ohio", "us_michigan", "us_georgia",
                "india_central", "india_maharashtra", "india_tamil_nadu", "india_karnataka"
            ],
            "citation_patterns": [
                r'\d+\s+U\.S\.\s+\d+',  # Supreme Court
                r'\d+\s+F\.\d+d\s+\d+',  # Federal cases  
                r'\d+\s+S\.Ct\.\s+\d+',  # Supreme Court Reporter
                r'\d+\s+U\.S\.C\.\s+§\s+\d+',  # U.S. Code
                r'\d+\s+C\.F\.R\.\s+§\s+\d+',  # Code of Federal Regulations
            ]
        }
        
        # Performance tracking
        self.integration_progress = None
        self.quality_metrics = QualityMetrics()
        
        # Deduplication tracking
        self.content_hashes = set()
        self.citation_index = defaultdict(set)
        self.title_similarity_index = defaultdict(list)
        
    async def initialize(self):
        """Initialize the integration system"""
        logger.info("🚀 Initializing Knowledge Base Integration System...")
        
        # Initialize MongoDB connection
        try:
            mongo_url = os.environ.get('MONGO_URL')
            if not mongo_url:
                raise ValueError("MONGO_URL not found in environment variables")
                
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            self.db = self.mongo_client[os.environ.get('DB_NAME', 'legalmate')]
            
            # Test connection
            await self.mongo_client.admin.command('ping')
            logger.info("✅ MongoDB connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MongoDB: {e}")
            raise
        
        # Create indexes for performance
        await self._create_performance_indexes()
        
        logger.info("✅ Knowledge Base Integration System initialized successfully!")
    
    async def _create_performance_indexes(self):
        """Create MongoDB indexes for optimal performance with 25K+ documents"""
        try:
            # Documents collection indexes
            documents_collection = self.db.legal_documents
            
            # Compound indexes for common queries
            await documents_collection.create_index([
                ("legal_domain", 1),
                ("jurisdiction", 1),
                ("document_type", 1)
            ], name="domain_jurisdiction_type_idx")
            
            await documents_collection.create_index([
                ("source", 1),
                ("authority_weight", -1),
                ("created_at", -1)
            ], name="source_authority_date_idx")
            
            # Text search index for content
            await documents_collection.create_index([
                ("title", "text"),
                ("content", "text"),
                ("legal_concepts", "text")
            ], name="content_search_idx")
            
            # Deduplication indexes
            await documents_collection.create_index("content_hash", unique=True, name="content_hash_idx")
            await documents_collection.create_index("citation", name="citation_idx")
            
            # Quality metrics index
            await documents_collection.create_index([
                ("quality_score", -1),
                ("authority_weight", -1)
            ], name="quality_authority_idx")
            
            logger.info("✅ Performance indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {e}")
    
    async def execute_comprehensive_integration(self) -> Dict[str, Any]:
        """
        Execute comprehensive integration process for Days 12-14
        Phase 1: Integration & Consolidation
        Phase 2: Quality Assurance & Validation  
        Phase 3: Performance Optimization
        Phase 4: Monitoring & Analytics
        """
        logger.info("🎯 Starting Comprehensive Integration Process (Days 12-14)")
        
        integration_results = {
            "phases_completed": [],
            "total_documents_processed": 0,
            "final_document_count": 0,
            "quality_improvement": {},
            "performance_metrics": {},
            "monitoring_dashboard": {}
        }
        
        try:
            # Phase 1: Integration & Consolidation
            logger.info("📋 Phase 1: Integration & Consolidation")
            self.integration_progress = IntegrationProgress("Phase 1", datetime.utcnow())
            
            phase1_results = await self._execute_phase1_integration()
            integration_results["phases_completed"].append("Phase 1")
            integration_results["total_documents_processed"] += phase1_results["documents_processed"]
            
            # Phase 2: Quality Assurance & Validation
            logger.info("🔍 Phase 2: Quality Assurance & Validation")
            self.integration_progress = IntegrationProgress("Phase 2", datetime.utcnow())
            
            phase2_results = await self._execute_phase2_quality_assurance()
            integration_results["phases_completed"].append("Phase 2")
            integration_results["quality_improvement"] = phase2_results
            
            # Phase 3: Performance Optimization
            logger.info("⚡ Phase 3: Performance Optimization")
            self.integration_progress = IntegrationProgress("Phase 3", datetime.utcnow())
            
            phase3_results = await self._execute_phase3_performance_optimization()
            integration_results["phases_completed"].append("Phase 3")
            integration_results["performance_metrics"] = phase3_results
            
            # Phase 4: Monitoring & Analytics
            logger.info("📊 Phase 4: Monitoring & Analytics Implementation")
            self.integration_progress = IntegrationProgress("Phase 4", datetime.utcnow())
            
            phase4_results = await self._execute_phase4_monitoring_analytics()
            integration_results["phases_completed"].append("Phase 4")
            integration_results["monitoring_dashboard"] = phase4_results
            
            # Final statistics
            final_count = await self._get_final_document_count()
            integration_results["final_document_count"] = final_count
            
            logger.info("🎉 Comprehensive Integration Process Completed Successfully!")
            logger.info(f"📊 Final Document Count: {final_count:,}")
            
            return integration_results
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive integration: {e}")
            raise
    
    async def _execute_phase1_integration(self) -> Dict[str, Any]:
        """Phase 1: Integration & Consolidation of all existing legal documents"""
        logger.info("🔧 Executing Phase 1: Integration & Consolidation")
        
        phase1_results = {
            "documents_processed": 0,
            "sources_consolidated": 0,
            "schema_standardized": 0,
            "authority_hierarchy_applied": 0,
            "cross_source_deduplication": 0
        }
        
        try:
            # Step 1: Load and consolidate all existing sources
            existing_sources = await self._discover_existing_sources()
            logger.info(f"📚 Discovered {len(existing_sources)} existing document sources")
            
            # Step 2: Create unified schema and metadata structure
            unified_schema = await self._create_unified_schema()
            logger.info("📋 Unified document schema created")
            
            # Step 3: Process each source with standardization
            total_processed = 0
            for source_info in existing_sources:
                source_results = await self._process_source_integration(source_info, unified_schema)
                total_processed += source_results["documents_processed"]
                phase1_results["sources_consolidated"] += 1
                
                logger.info(f"✅ Source '{source_info['name']}': {source_results['documents_processed']} documents processed")
            
            # Step 4: Apply source authority hierarchy
            authority_results = await self._apply_authority_hierarchy()
            phase1_results["authority_hierarchy_applied"] = authority_results["documents_weighted"]
            
            # Step 5: Cross-source deduplication and conflict resolution
            dedup_results = await self._execute_cross_source_deduplication()
            phase1_results["cross_source_deduplication"] = dedup_results["duplicates_removed"]
            
            phase1_results["documents_processed"] = total_processed
            phase1_results["schema_standardized"] = total_processed
            
            logger.info(f"✅ Phase 1 completed: {total_processed:,} documents integrated")
            return phase1_results
            
        except Exception as e:
            logger.error(f"❌ Error in Phase 1: {e}")
            raise
    
    async def _discover_existing_sources(self) -> List[Dict[str, Any]]:
        """Discover all existing document sources in the system"""
        sources = []
        
        try:
            # 1. JSON knowledge base file
            if os.path.exists("/app/legal_knowledge_base.json"):
                with open("/app/legal_knowledge_base.json", 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                sources.append({
                    "name": "JSON Knowledge Base",
                    "type": "json_file",
                    "path": "/app/legal_knowledge_base.json",
                    "document_count": len(json_data),
                    "data": json_data
                })
            
            # 2. MongoDB collections
            collections = await self.db.list_collection_names()
            for collection_name in collections:
                if 'legal' in collection_name.lower() or 'document' in collection_name.lower():
                    collection = self.db[collection_name]
                    count = await collection.count_documents({})
                    if count > 0:
                        sources.append({
                            "name": f"MongoDB {collection_name}",
                            "type": "mongodb_collection",
                            "collection_name": collection_name,
                            "document_count": count
                        })
            
            # 3. Check for bulk collection results (if they exist in different locations)
            bulk_sources = await self._discover_bulk_collection_sources()
            sources.extend(bulk_sources)
            
            return sources
            
        except Exception as e:
            logger.error(f"Error discovering sources: {e}")
            return sources
    
    async def _discover_bulk_collection_sources(self) -> List[Dict[str, Any]]:
        """Discover bulk collection sources (court decisions, federal docs, academic papers)"""
        bulk_sources = []
        
        try:
            # Check for CourtListener bulk collection
            courtlistener_collection = self.db.courtlistener_documents
            court_count = await courtlistener_collection.count_documents({})
            if court_count > 0:
                bulk_sources.append({
                    "name": "CourtListener Bulk Collection",
                    "type": "mongodb_collection",
                    "collection_name": "courtlistener_documents",
                    "document_count": court_count,
                    "source_authority": "court_decisions"
                })
            
            # Check for federal resources collection
            federal_collection = self.db.federal_documents
            federal_count = await federal_collection.count_documents({})
            if federal_count > 0:
                bulk_sources.append({
                    "name": "Federal Resources Collection",
                    "type": "mongodb_collection", 
                    "collection_name": "federal_documents",
                    "document_count": federal_count,
                    "source_authority": "government_documents"
                })
            
            # Check for academic collection
            academic_collection = self.db.academic_documents
            academic_count = await academic_collection.count_documents({})
            if academic_count > 0:
                bulk_sources.append({
                    "name": "Academic Legal Collection",
                    "type": "mongodb_collection",
                    "collection_name": "academic_documents", 
                    "document_count": academic_count,
                    "source_authority": "academic_papers"
                })
                
            return bulk_sources
            
        except Exception as e:
            logger.error(f"Error discovering bulk sources: {e}")
            return []
    
    async def _create_unified_schema(self) -> Dict[str, Any]:
        """Create unified document schema for all sources"""
        unified_schema = {
            # Core identification
            "id": {"type": "string", "required": True, "unique": True},
            "title": {"type": "string", "required": True, "max_length": 1000},
            "content": {"type": "string", "required": True, "min_length": 500},
            
            # Source information with authority hierarchy
            "source": {"type": "string", "required": True},
            "source_url": {"type": "string", "required": False},
            "source_authority": {"type": "string", "enum": list(self.source_hierarchy.keys())},
            "authority_weight": {"type": "float", "min": 0.0, "max": 1.0},
            
            # Legal classification
            "jurisdiction": {"type": "string", "required": True, "enum": self.validation_rules["valid_jurisdictions"]},
            "legal_domain": {"type": "string", "required": True},
            "legal_subdomain": {"type": "string", "required": False},
            "document_type": {"type": "string", "required": True},
            
            # Enhanced metadata
            "court": {"type": "string", "required": False},
            "court_level": {"type": "string", "enum": ["supreme_court", "circuit_court", "district_court", "state_court", "other"]},
            "citation": {"type": "string", "required": False},
            "date_filed": {"type": "datetime", "required": False},
            "precedential_status": {"type": "string", "enum": ["Precedential", "Published", "Unpublished", "Other"]},
            
            # Content analysis
            "word_count": {"type": "integer", "min": 100},
            "legal_concepts": {"type": "array", "items": {"type": "string"}},
            "citations_referenced": {"type": "array", "items": {"type": "string"}},
            "legal_authorities": {"type": "array", "items": {"type": "string"}},
            
            # Quality metrics
            "quality_score": {"type": "float", "min": 0.0, "max": 1.0},
            "completeness_score": {"type": "float", "min": 0.0, "max": 1.0},
            "content_hash": {"type": "string", "required": True, "unique": True},
            
            # Processing metadata
            "created_at": {"type": "datetime", "required": True},
            "updated_at": {"type": "datetime", "required": True},
            "integration_phase": {"type": "string", "default": "phase1"},
            "validation_status": {"type": "string", "enum": ["pending", "validated", "rejected", "needs_review"]},
            
            # Flexible metadata container
            "metadata": {"type": "object", "required": False}
        }
        
        return unified_schema
    
    async def _process_source_integration(self, source_info: Dict[str, Any], unified_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Process and integrate documents from a specific source"""
        results = {"documents_processed": 0, "documents_integrated": 0, "errors": 0}
        
        try:
            if source_info["type"] == "json_file":
                # Process JSON file documents
                documents = source_info["data"]
                for doc in documents:
                    try:
                        integrated_doc = await self._standardize_document(doc, unified_schema, source_info)
                        await self._store_integrated_document(integrated_doc)
                        results["documents_integrated"] += 1
                    except Exception as e:
                        logger.error(f"Error processing document {doc.get('id', 'unknown')}: {e}")
                        results["errors"] += 1
                    results["documents_processed"] += 1
                        
            elif source_info["type"] == "mongodb_collection":
                # Process MongoDB collection documents
                collection = self.db[source_info["collection_name"]]
                async for doc in collection.find():
                    try:
                        # Convert ObjectId to string for processing
                        if "_id" in doc:
                            doc["_id"] = str(doc["_id"])
                        
                        integrated_doc = await self._standardize_document(doc, unified_schema, source_info)
                        await self._store_integrated_document(integrated_doc)
                        results["documents_integrated"] += 1
                    except Exception as e:
                        logger.error(f"Error processing MongoDB document {doc.get('_id', 'unknown')}: {e}")
                        results["errors"] += 1
                    results["documents_processed"] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing source {source_info['name']}: {e}")
            raise
    
    async def _standardize_document(self, original_doc: Dict[str, Any], schema: Dict[str, Any], source_info: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize document to unified schema"""
        standardized = {}
        
        try:
            # Core identification
            standardized["id"] = original_doc.get("id", f"integrated_{int(time.time())}_{original_doc.get('_id', 'unknown')}")
            standardized["title"] = original_doc.get("title", "Untitled Document")[:1000]
            standardized["content"] = original_doc.get("content", "")
            
            # Source information
            standardized["source"] = original_doc.get("source", source_info["name"])
            standardized["source_url"] = original_doc.get("source_url", "")
            
            # Determine source authority based on source type and content
            source_authority = self._determine_source_authority(original_doc, source_info)
            standardized["source_authority"] = source_authority
            standardized["authority_weight"] = self.source_hierarchy[source_authority].authority_weight
            
            # Legal classification
            standardized["jurisdiction"] = original_doc.get("jurisdiction", "us_federal")
            standardized["legal_domain"] = original_doc.get("legal_domain", "general_law")
            
            # Enhanced legal subdomain classification  
            subdomain = self._classify_legal_subdomain(standardized["content"], standardized["legal_domain"])
            standardized["legal_subdomain"] = subdomain
            
            standardized["document_type"] = original_doc.get("document_type", "unknown")
            
            # Court and legal metadata
            standardized["court"] = original_doc.get("court", "")
            standardized["court_level"] = self._classify_court_level(standardized["court"])
            standardized["citation"] = original_doc.get("citation", "")
            
            # Date handling
            date_filed = original_doc.get("date_filed") or original_doc.get("created_at")
            if date_filed:
                if isinstance(date_filed, str):
                    try:
                        standardized["date_filed"] = datetime.fromisoformat(date_filed.replace('Z', '+00:00'))
                    except:
                        standardized["date_filed"] = None
                else:
                    standardized["date_filed"] = date_filed
            else:
                standardized["date_filed"] = None
            
            standardized["precedential_status"] = original_doc.get("precedential_status", "Other")
            
            # Content analysis
            content = standardized["content"]
            standardized["word_count"] = len(content.split()) if content else 0
            standardized["legal_concepts"] = self._extract_legal_concepts(content, standardized["legal_domain"])
            standardized["citations_referenced"] = self._extract_citations(content)
            standardized["legal_authorities"] = self._extract_legal_authorities(content)
            
            # Quality metrics
            quality_score = self._calculate_quality_score(standardized)
            completeness_score = self._calculate_completeness_score(standardized)
            
            standardized["quality_score"] = quality_score
            standardized["completeness_score"] = completeness_score
            standardized["content_hash"] = self._generate_content_hash(content)
            
            # Processing metadata
            standardized["created_at"] = datetime.utcnow()
            standardized["updated_at"] = datetime.utcnow()
            standardized["integration_phase"] = "phase1"
            standardized["validation_status"] = "pending"
            
            # Preserve original metadata
            original_metadata = original_doc.get("metadata", {})
            standardized["metadata"] = {
                **original_metadata,
                "original_source": source_info["name"],
                "integration_timestamp": datetime.utcnow().isoformat()
            }
            
            return standardized
            
        except Exception as e:
            logger.error(f"Error standardizing document: {e}")
            raise
    
    def _determine_source_authority(self, doc: Dict[str, Any], source_info: Dict[str, Any]) -> str:
        """Determine source authority based on document content and source"""
        # Check document type and source patterns
        doc_type = doc.get("document_type", "").lower()
        source_name = source_info.get("name", "").lower()
        court = doc.get("court", "").lower()
        
        # Court decisions hierarchy
        if "supreme court" in court or "scotus" in source_name:
            return "supreme_court"
        elif "circuit" in court or "circuit" in source_name:
            return "circuit_court"
        elif "district" in court or "district" in source_name:
            return "district_court"
        elif doc_type == "court_decision":
            return "district_court"  # Default for court decisions
        
        # Statutory authority
        elif doc_type == "statute" or "usc" in doc.get("source_url", "").lower():
            if "state" in source_name:
                return "state_statute"
            return "federal_statute"
        
        # Regulatory authority
        elif doc_type == "regulation" or "cfr" in doc.get("source_url", "").lower():
            if "state" in source_name:
                return "state_regulation"
            return "federal_regulation"
        
        # Academic sources
        elif "academic" in source_name or "scholar" in source_name:
            if "law review" in doc.get("title", "").lower():
                return "law_review"
            return "academic_paper"
        
        # Government reports
        elif "government" in source_name or any(agency in source_name for agency in ["sec", "dol", "uspto", "irs"]):
            return "government_report"
        
        # Legal reference materials
        elif "wex" in doc.get("source_url", "").lower() or "encyclopedia" in source_name:
            return "legal_encyclopedia"
        
        # Default fallback
        return "legal_encyclopedia"
    
    def _classify_legal_subdomain(self, content: str, legal_domain: str) -> str:
        """Classify document into specific legal subdomain (50+ categories)"""
        if legal_domain not in self.enhanced_categories:
            return "general"
        
        content_lower = content.lower()
        subdomains = self.enhanced_categories[legal_domain]
        
        # Score each subdomain based on keyword presence
        subdomain_scores = defaultdict(int)
        
        for subdomain in subdomains:
            # Convert subdomain to search terms
            search_terms = subdomain.replace('_', ' ').split()
            
            for term in search_terms:
                if term in content_lower:
                    subdomain_scores[subdomain] += 1
            
            # Check for exact phrase match (higher score)
            phrase = subdomain.replace('_', ' ')
            if phrase in content_lower:
                subdomain_scores[subdomain] += 3
        
        # Return highest scoring subdomain
        if subdomain_scores:
            return max(subdomain_scores.items(), key=lambda x: x[1])[0]
        
        return "general"
    
    def _classify_court_level(self, court: str) -> str:
        """Classify court level for authority hierarchy"""
        if not court:
            return "other"
            
        court_lower = court.lower()
        
        if "supreme court" in court_lower or "scotus" in court_lower:
            return "supreme_court"
        elif "circuit" in court_lower or "appellate" in court_lower:
            return "circuit_court"
        elif "district" in court_lower:
            return "district_court"
        elif any(term in court_lower for term in ["state", "county", "municipal"]):
            return "state_court"
        else:
            return "other"
    
    def _extract_legal_concepts(self, content: str, legal_domain: str) -> List[str]:
        """Extract legal concepts from document content"""
        if not content:
            return []
        
        content_lower = content.lower()
        concepts = []
        
        # General legal concepts
        general_concepts = [
            "jurisdiction", "due process", "equal protection", "constitutional rights",
            "statutory interpretation", "precedent", "stare decisis", "burden of proof",
            "standard of review", "injunctive relief", "damages", "attorney fees",
            "settlement", "judgment", "appeal", "motion", "pleading", "discovery"
        ]
        
        # Domain-specific concepts
        domain_concepts = []
        if legal_domain in self.enhanced_categories:
            for subdomain in self.enhanced_categories[legal_domain]:
                domain_concepts.append(subdomain.replace('_', ' '))
        
        # Check for concept presence
        all_concepts = general_concepts + domain_concepts
        for concept in all_concepts:
            if concept in content_lower:
                concepts.append(concept)
        
        return concepts[:15]  # Limit to top 15 concepts
    
    def _extract_citations(self, content: str) -> List[str]:
        """Extract legal citations from content"""
        if not content:
            return []
            
        citations = []
        for pattern in self.validation_rules["citation_patterns"]:
            matches = re.findall(pattern, content)
            citations.extend(matches)
        
        return list(set(citations))[:20]  # Deduplicate and limit
    
    def _extract_legal_authorities(self, content: str) -> List[str]:
        """Extract legal authorities (statutes, regulations, rules)"""
        if not content:
            return []
            
        authorities = []
        
        # Authority patterns
        authority_patterns = [
            r'Rule\s+\d+',  # Federal Rules
            r'Fed\.\s*R\.\s*Civ\.\s*P\.\s*\d+',  # FRCP
            r'Fed\.\s*R\.\s*Crim\.\s*P\.\s*\d+',  # FRCrP
            r'Fed\.\s*R\.\s*Evid\.\s*\d+',  # FRE
        ]
        
        for pattern in authority_patterns:
            matches = re.findall(pattern, content)
            authorities.extend(matches)
        
        return list(set(authorities))[:10]  # Deduplicate and limit
    
    def _calculate_quality_score(self, doc: Dict[str, Any]) -> float:
        """Calculate quality score for document (0.0-1.0)"""
        score = 0.0
        
        # Content quality (40% of score)
        content = doc.get("content", "")
        word_count = doc.get("word_count", 0)
        
        if word_count >= 1000:
            score += 0.4
        elif word_count >= 500:
            score += 0.3
        elif word_count >= 200:
            score += 0.2
        elif word_count >= 100:
            score += 0.1
        
        # Citation quality (20% of score)
        citations = doc.get("citations_referenced", [])
        if len(citations) >= 5:
            score += 0.2
        elif len(citations) >= 3:
            score += 0.15
        elif len(citations) >= 1:
            score += 0.1
        
        # Metadata completeness (20% of score)
        required_fields = ["title", "jurisdiction", "legal_domain", "source"]
        optional_fields = ["court", "citation", "date_filed", "precedential_status"]
        
        required_complete = sum(1 for field in required_fields if doc.get(field))
        optional_complete = sum(1 for field in optional_fields if doc.get(field))
        
        completeness = (required_complete / len(required_fields)) * 0.15
        completeness += (optional_complete / len(optional_fields)) * 0.05
        score += completeness
        
        # Legal concept richness (10% of score)
        concepts = doc.get("legal_concepts", [])
        if len(concepts) >= 5:
            score += 0.1
        elif len(concepts) >= 3:
            score += 0.07
        elif len(concepts) >= 1:
            score += 0.05
        
        # Authority weight bonus (10% of score)
        authority_weight = doc.get("authority_weight", 0.0)
        score += authority_weight * 0.1
        
        return min(1.0, score)  # Cap at 1.0
    
    def _calculate_completeness_score(self, doc: Dict[str, Any]) -> float:
        """Calculate completeness score for document metadata"""
        total_fields = 0
        complete_fields = 0
        
        # Core fields (required)
        core_fields = ["title", "content", "source", "jurisdiction", "legal_domain", "document_type"]
        for field in core_fields:
            total_fields += 1
            if doc.get(field) and str(doc[field]).strip():
                complete_fields += 1
        
        # Enhanced fields (optional but valuable)
        enhanced_fields = ["court", "citation", "date_filed", "precedential_status", "legal_concepts", "citations_referenced"]
        for field in enhanced_fields:
            total_fields += 1
            if doc.get(field):
                if isinstance(doc[field], list) and len(doc[field]) > 0:
                    complete_fields += 1
                elif isinstance(doc[field], str) and doc[field].strip():
                    complete_fields += 1
                elif doc[field] is not None:
                    complete_fields += 1
        
        return complete_fields / total_fields if total_fields > 0 else 0.0
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate content hash for deduplication"""
        if not content:
            return ""
        
        # Normalize content for hashing
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    async def _store_integrated_document(self, document: Dict[str, Any]):
        """Store integrated document in unified collection"""
        try:
            collection = self.db.legal_documents_integrated
            
            # Handle potential duplicates by content hash
            existing = await collection.find_one({"content_hash": document["content_hash"]})
            if existing:
                # Update if new document has higher authority weight
                if document["authority_weight"] > existing.get("authority_weight", 0):
                    await collection.replace_one(
                        {"content_hash": document["content_hash"]},
                        document
                    )
                    logger.debug(f"Updated document with higher authority: {document['id']}")
                else:
                    logger.debug(f"Skipped duplicate document: {document['id']}")
                return
            
            # Insert new document
            await collection.insert_one(document)
            
        except Exception as e:
            logger.error(f"Error storing integrated document {document.get('id')}: {e}")
            raise
    
    async def _apply_authority_hierarchy(self) -> Dict[str, Any]:
        """Apply source authority hierarchy and resolve conflicts"""
        logger.info("🏛️ Applying source authority hierarchy...")
        
        results = {"documents_weighted": 0, "conflicts_resolved": 0}
        
        try:
            collection = self.db.legal_documents_integrated
            
            # Update authority weights for all documents
            async for doc in collection.find():
                source_authority = doc.get("source_authority", "legal_encyclopedia")
                if source_authority in self.source_hierarchy:
                    new_weight = self.source_hierarchy[source_authority].authority_weight
                    
                    await collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"authority_weight": new_weight}}
                    )
                    results["documents_weighted"] += 1
            
            # Resolve conflicts between documents with similar content
            conflicts_resolved = await self._resolve_authority_conflicts()
            results["conflicts_resolved"] = conflicts_resolved
            
            logger.info(f"✅ Authority hierarchy applied to {results['documents_weighted']} documents")
            return results
            
        except Exception as e:
            logger.error(f"Error applying authority hierarchy: {e}")
            raise
    
    async def _resolve_authority_conflicts(self) -> int:
        """Resolve conflicts between documents with similar content but different authorities"""
        conflicts_resolved = 0
        
        try:
            collection = self.db.legal_documents_integrated
            
            # Find documents with similar titles (potential conflicts)
            pipeline = [
                {"$group": {
                    "_id": "$title",
                    "docs": {"$push": {"id": "$id", "authority_weight": "$authority_weight", "_id": "$_id"}},
                    "count": {"$sum": 1}
                }},
                {"$match": {"count": {"$gt": 1}}}
            ]
            
            async for group in collection.aggregate(pipeline):
                docs = group["docs"]
                if len(docs) > 1:
                    # Keep document with highest authority weight
                    docs.sort(key=lambda x: x["authority_weight"], reverse=True)
                    highest_authority = docs[0]
                    
                    # Mark lower authority documents for review or removal
                    for doc in docs[1:]:
                        await collection.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {
                                "validation_status": "needs_review",
                                "conflict_resolved_by": highest_authority["id"],
                                "resolution_reason": "lower_authority_duplicate"
                            }}
                        )
                        conflicts_resolved += 1
            
            return conflicts_resolved
            
        except Exception as e:
            logger.error(f"Error resolving authority conflicts: {e}")
            return 0
    
    async def _execute_cross_source_deduplication(self) -> Dict[str, Any]:
        """Execute comprehensive cross-source deduplication"""
        logger.info("🔍 Executing cross-source deduplication...")
        
        results = {"duplicates_removed": 0, "near_duplicates_flagged": 0}
        
        try:
            collection = self.db.legal_documents_integrated
            
            # Content hash deduplication (exact duplicates)
            exact_duplicates = await self._find_exact_duplicates(collection)
            results["duplicates_removed"] += await self._remove_exact_duplicates(collection, exact_duplicates)
            
            # Citation-based deduplication
            citation_duplicates = await self._find_citation_duplicates(collection)
            results["duplicates_removed"] += await self._resolve_citation_duplicates(collection, citation_duplicates)
            
            # Title similarity deduplication
            title_near_duplicates = await self._find_title_near_duplicates(collection)
            results["near_duplicates_flagged"] += await self._flag_title_near_duplicates(collection, title_near_duplicates)
            
            logger.info(f"✅ Deduplication completed: {results['duplicates_removed']} exact duplicates removed")
            return results
            
        except Exception as e:
            logger.error(f"Error in cross-source deduplication: {e}")
            raise
    
    async def _find_exact_duplicates(self, collection) -> List[List[Dict[str, Any]]]:
        """Find documents with identical content hashes"""
        duplicates = []
        
        pipeline = [
            {"$group": {
                "_id": "$content_hash",
                "docs": {"$push": {"id": "$id", "authority_weight": "$authority_weight", "_id": "$_id"}},
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gt": 1}}}
        ]
        
        async for group in collection.aggregate(pipeline):
            if len(group["docs"]) > 1:
                duplicates.append(group["docs"])
        
        return duplicates
    
    async def _remove_exact_duplicates(self, collection, duplicates: List[List[Dict[str, Any]]]) -> int:
        """Remove exact duplicates, keeping highest authority version"""
        removed_count = 0
        
        for duplicate_group in duplicates:
            # Sort by authority weight (highest first)
            duplicate_group.sort(key=lambda x: x["authority_weight"], reverse=True)
            
            # Keep first (highest authority), remove others
            for doc in duplicate_group[1:]:
                await collection.delete_one({"_id": doc["_id"]})
                removed_count += 1
                logger.debug(f"Removed exact duplicate: {doc['id']}")
        
        return removed_count
    
    async def _find_citation_duplicates(self, collection) -> List[List[Dict[str, Any]]]:
        """Find documents with identical citations"""
        duplicates = []
        
        # Find documents with non-empty citations
        async for doc in collection.find({"citation": {"$ne": "", "$exists": True}}):
            citation = doc.get("citation", "").strip()
            if citation:
                # Find other documents with same citation
                same_citation_docs = []
                async for other_doc in collection.find({"citation": citation, "_id": {"$ne": doc["_id"]}}):
                    same_citation_docs.append({
                        "id": other_doc["id"],
                        "authority_weight": other_doc.get("authority_weight", 0),
                        "_id": other_doc["_id"]
                    })
                
                if same_citation_docs:
                    same_citation_docs.append({
                        "id": doc["id"],
                        "authority_weight": doc.get("authority_weight", 0),
                        "_id": doc["_id"]
                    })
                    duplicates.append(same_citation_docs)
        
        return duplicates
    
    async def _resolve_citation_duplicates(self, collection, duplicates: List[List[Dict[str, Any]]]) -> int:
        """Resolve citation duplicates by keeping highest authority version"""
        resolved_count = 0
        
        for duplicate_group in duplicates:
            duplicate_group.sort(key=lambda x: x["authority_weight"], reverse=True)
            
            # Mark lower authority versions for review
            for doc in duplicate_group[1:]:
                await collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {
                        "validation_status": "needs_review",
                        "duplicate_reason": "citation_duplicate",
                        "preferred_version": duplicate_group[0]["id"]
                    }}
                )
                resolved_count += 1
        
        return resolved_count
    
    async def _find_title_near_duplicates(self, collection) -> List[List[Dict[str, Any]]]:
        """Find documents with very similar titles"""
        near_duplicates = []
        
        # This is a simplified implementation - in production you might use
        # more sophisticated similarity algorithms like Levenshtein distance
        title_groups = defaultdict(list)
        
        async for doc in collection.find():
            title = doc.get("title", "").lower().strip()
            if title:
                # Simple normalization - remove common words and create key
                words = title.split()
                key_words = [w for w in words if len(w) > 3 and w not in ['the', 'and', 'for', 'case', 'law']]
                if key_words:
                    key = " ".join(sorted(key_words[:5]))  # Use first 5 significant words
                    title_groups[key].append({
                        "id": doc["id"],
                        "title": doc["title"],
                        "authority_weight": doc.get("authority_weight", 0),
                        "_id": doc["_id"]
                    })
        
        # Find groups with multiple documents
        for key, docs in title_groups.items():
            if len(docs) > 1:
                near_duplicates.append(docs)
        
        return near_duplicates
    
    async def _flag_title_near_duplicates(self, collection, near_duplicates: List[List[Dict[str, Any]]]) -> int:
        """Flag title near-duplicates for manual review"""
        flagged_count = 0
        
        for duplicate_group in near_duplicates:
            duplicate_group.sort(key=lambda x: x["authority_weight"], reverse=True)
            
            # Flag lower authority versions for review
            for doc in duplicate_group[1:]:
                await collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {
                        "validation_status": "needs_review",
                        "duplicate_reason": "title_similarity",
                        "similar_to": duplicate_group[0]["id"]
                    }}
                )
                flagged_count += 1
        
        return flagged_count
    
    async def _get_final_document_count(self) -> int:
        """Get final count of integrated documents"""
        try:
            collection = self.db.legal_documents_integrated
            return await collection.count_documents({})
        except Exception as e:
            logger.error(f"Error getting final document count: {e}")
            return 0
    
    async def close(self):
        """Close system connections"""
        if self.mongo_client:
            self.mongo_client.close()

# Main execution function for Phase 1
async def execute_phase1_integration():
    """Execute Phase 1: Integration & Consolidation"""
    system = KnowledgeIntegrationSystem()
    
    try:
        await system.initialize()
        
        logger.info("🚀 Starting Phase 1: Knowledge Base Integration & Consolidation")
        results = await system._execute_phase1_integration()
        
        logger.info("🎉 Phase 1 Integration completed successfully!")
        logger.info(f"📊 Results: {json.dumps(results, indent=2)}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Phase 1 Integration failed: {e}")
        raise
    finally:
        await system.close()

if __name__ == "__main__":
    # Test Phase 1 integration
    asyncio.run(execute_phase1_integration())
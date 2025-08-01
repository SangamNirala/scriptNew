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
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import httpx
import os
from pathlib import Path

# SerpAPI - handle import gracefully
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    GoogleSearch = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalKnowledgeBuilder:
    """Comprehensive legal knowledge base builder for RAG system"""
    
    def __init__(self):
        self.courtlistener_api_key = os.environ.get('COURTLISTENER_API_KEY')
        self.serp_api_key = os.environ.get('SERP_API_KEY')
        
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
    
    async def _fetch_court_decisions(self) -> List[Dict[str, Any]]:
        """Fetch court decisions using CourtListener API"""
        content = []
        
        if not self.courtlistener_api_key:
            logger.warning("CourtListener API key not available, skipping court decisions")
            return content
            
        try:
            async with httpx.AsyncClient() as client:
                # Fetch recent Supreme Court decisions
                headers = {"Authorization": f"Token {self.courtlistener_api_key}"}
                
                # Search for various legal domains
                search_queries = [
                    "contract law",
                    "employment law", 
                    "intellectual property",
                    "corporate law",
                    "constitutional law",
                    "civil procedure",
                    "criminal procedure"
                ]
                
                for query in search_queries:
                    try:
                        url = f"https://www.courtlistener.com/api/rest/v3/search/"
                        params = {
                            "q": query,
                            "type": "o",  # Opinions
                            "order_by": "score desc",
                            "stat_Precedential": "on",
                            "court": "scotus",  # Supreme Court
                            "format": "json"
                        }
                        
                        response = await client.get(url, headers=headers, params=params)
                        if response.status_code == 200:
                            data = response.json()
                            
                            for result in data.get('results', [])[:5]:  # Limit to top 5 per query
                                legal_doc = {
                                    "id": f"court_{result.get('id')}",
                                    "title": result.get('caseName', 'Unknown Case'),
                                    "content": result.get('text', '') or result.get('snippet', ''),
                                    "source": "CourtListener",
                                    "source_url": result.get('absolute_url', ''),
                                    "jurisdiction": "us_federal",
                                    "legal_domain": self._categorize_content(query),
                                    "document_type": "court_decision",
                                    "court": result.get('court', 'Unknown Court'),
                                    "date_filed": result.get('dateFiled', ''),
                                    "precedential_status": result.get('status', ''),
                                    "metadata": {
                                        "citation": result.get('citation', ''),
                                        "judges": result.get('judges', []),
                                        "docket_number": result.get('docketNumber', '')
                                    },
                                    "created_at": datetime.utcnow().isoformat(),
                                    "content_hash": self._generate_content_hash(result.get('text', '') or result.get('snippet', ''))
                                }
                                content.append(legal_doc)
                        
                        await asyncio.sleep(2)  # Rate limiting for API
                        
                    except Exception as e:
                        logger.error(f"Error fetching court decisions for '{query}': {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error with CourtListener API: {e}")
            
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
            search = GoogleSearch({
                "q": query,
                "api_key": self.serp_api_key,
                "num": 10,  # Get top 10 results
                "hl": "en",
                "gl": "us"
            })
            
            results = search.get_dict()
            
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
async def build_legal_knowledge_base():
    """Main function to build comprehensive legal knowledge base"""
    builder = LegalKnowledgeBuilder()
    
    try:
        # Build the knowledge base
        knowledge_base = await builder.build_comprehensive_knowledge_base()
        
        # Save to file
        builder.save_knowledge_base()
        
        # Print statistics
        stats = builder.get_knowledge_base_stats()
        print("\n" + "="*50)
        print("📊 LEGAL KNOWLEDGE BASE STATISTICS")
        print("="*50)
        print(f"Total Documents: {stats['total_documents']}")
        
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
        
        print("\n✅ Legal knowledge base created successfully!")
        return knowledge_base
        
    except Exception as e:
        logger.error(f"Error building knowledge base: {e}")
        return []


if __name__ == "__main__":
    # Run the knowledge base builder
    asyncio.run(build_legal_knowledge_base())
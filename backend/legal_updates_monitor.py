"""
Real-Time Legal Updates Monitoring System
Monitors Supreme Court, Federal Register, and Circuit Court updates using free APIs
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import feedparser
import re
from bs4 import BeautifulSoup
import json
import hashlib
from urllib.parse import urljoin, urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UpdatePriority(Enum):
    CRITICAL = "critical"  # Supreme Court decisions, major legislation
    HIGH = "high"         # Circuit court precedent-setting decisions
    MEDIUM = "medium"     # District court landmark decisions  
    LOW = "low"           # Procedural changes, minor updates

class UpdateSource(Enum):
    SUPREME_COURT = "supreme_court"
    FEDERAL_REGISTER = "federal_register"
    CIRCUIT_COURT = "circuit_court"
    DISTRICT_COURT = "district_court"
    LEGAL_NEWS = "legal_news"

class UpdateType(Enum):
    DECISION = "decision"
    REGULATION = "regulation"
    LEGISLATION = "legislation"
    POLICY = "policy"
    ORDER = "order"
    OPINION = "opinion"

@dataclass
class LegalUpdate:
    """Represents a legal update from any monitored source"""
    update_id: str
    title: str
    source: UpdateSource
    update_type: UpdateType
    priority_level: UpdatePriority
    publication_date: datetime
    effective_date: Optional[datetime]
    summary: str
    full_content: str
    url: str
    citations: List[str]
    legal_domains_affected: List[str]
    jurisdiction: str
    superseded_authorities: List[str]
    impact_score: float  # 0.0-1.0 based on potential impact
    confidence_score: float  # 0.0-1.0 confidence in classification
    metadata: Dict[str, Any]

@dataclass
class MonitoringStats:
    """Statistics for monitoring performance"""
    total_updates_found: int
    updates_by_source: Dict[str, int]
    updates_by_priority: Dict[str, int]
    last_check_time: datetime
    next_check_time: datetime
    success_rate: float
    average_processing_time: float

class SupremeCourtMonitor:
    """Monitors Supreme Court decisions and orders using free RSS feeds"""
    
    def __init__(self):
        self.rss_feeds = {
            'opinions': 'https://www.supremecourt.gov/rss/cases.xml',
            'orders': 'https://www.supremecourt.gov/rss/orders.xml'
        }
        self.base_url = 'https://www.supremecourt.gov'
        
    async def get_updates(self, since_date: datetime = None) -> List[LegalUpdate]:
        """Fetch Supreme Court updates from RSS feeds"""
        updates = []
        
        if since_date is None:
            since_date = datetime.now() - timedelta(days=7)
            
        try:
            async with aiohttp.ClientSession() as session:
                for feed_type, feed_url in self.rss_feeds.items():
                    logger.info(f"Fetching Supreme Court {feed_type} from {feed_url}")
                    
                    async with session.get(feed_url) as response:
                        if response.status == 200:
                            feed_content = await response.text()
                            feed = feedparser.parse(feed_content)
                            
                            for entry in feed.entries:
                                try:
                                    pub_date = datetime(*entry.published_parsed[:6])
                                    
                                    if pub_date >= since_date:
                                        update = await self._parse_supreme_court_entry(entry, feed_type)
                                        if update:
                                            updates.append(update)
                                            
                                except Exception as e:
                                    logger.error(f"Error parsing Supreme Court entry: {e}")
                                    continue
                        else:
                            logger.error(f"Failed to fetch {feed_url}: {response.status}")
                            
        except Exception as e:
            logger.error(f"Error fetching Supreme Court updates: {e}")
            
        logger.info(f"Found {len(updates)} Supreme Court updates")
        return updates
    
    async def _parse_supreme_court_entry(self, entry, feed_type: str) -> Optional[LegalUpdate]:
        """Parse individual Supreme Court RSS entry"""
        try:
            update_id = hashlib.md5(f"scotus_{entry.link}".encode()).hexdigest()
            
            # Extract legal domains from title and summary
            legal_domains = self._extract_legal_domains(f"{entry.title} {entry.summary}")
            
            # Determine update type and priority
            update_type = UpdateType.DECISION if feed_type == 'opinions' else UpdateType.ORDER
            priority = UpdatePriority.CRITICAL  # All Supreme Court updates are critical
            
            # Extract citations if available
            citations = self._extract_citations(entry.summary)
            
            return LegalUpdate(
                update_id=update_id,
                title=entry.title,
                source=UpdateSource.SUPREME_COURT,
                update_type=update_type,
                priority_level=priority,
                publication_date=datetime(*entry.published_parsed[:6]),
                effective_date=None,  # Usually immediate for court decisions
                summary=entry.summary if hasattr(entry, 'summary') else entry.title,
                full_content=await self._fetch_full_content(entry.link),
                url=entry.link,
                citations=citations,
                legal_domains_affected=legal_domains,
                jurisdiction="US",
                superseded_authorities=[],  # Will be determined by impact analysis
                impact_score=0.9,  # Supreme Court decisions have high impact
                confidence_score=0.95,
                metadata={
                    'court': 'Supreme Court of the United States',
                    'feed_type': feed_type,
                    'raw_entry': dict(entry)
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Supreme Court entry: {e}")
            return None
    
    async def _fetch_full_content(self, url: str) -> str:
        """Fetch full content from Supreme Court decision URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract main content (this may need adjustment based on SCOTUS website structure)
                        content_div = soup.find('div', class_='content') or soup.find('main')
                        if content_div:
                            return content_div.get_text(strip=True)
                        else:
                            return soup.get_text(strip=True)[:2000]  # Fallback to first 2000 chars
                    else:
                        return f"Full content unavailable (HTTP {response.status})"
        except Exception as e:
            logger.error(f"Error fetching full content from {url}: {e}")
            return "Full content unavailable"
    
    def _extract_legal_domains(self, text: str) -> List[str]:
        """Extract legal domains from text using keyword matching"""
        domains = []
        domain_keywords = {
            'constitutional_law': ['constitution', 'constitutional', 'first amendment', 'due process', 'equal protection'],
            'contract_law': ['contract', 'agreement', 'breach', 'consideration', 'offer', 'acceptance'],
            'criminal_law': ['criminal', 'crime', 'prosecution', 'defendant', 'sentencing'],
            'civil_rights': ['civil rights', 'discrimination', 'voting', 'racial', 'gender'],
            'administrative_law': ['agency', 'regulation', 'administrative', 'federal register'],
            'employment_law': ['employment', 'workplace', 'labor', 'worker', 'employee'],
            'intellectual_property': ['patent', 'copyright', 'trademark', 'trade secret'],
            'securities_law': ['securities', 'sec', 'investment', 'insider trading'],
            'tax_law': ['tax', 'irs', 'deduction', 'revenue'],
            'environmental_law': ['environmental', 'epa', 'pollution', 'clean air', 'clean water']
        }
        
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ['general_law']
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract legal citations from text"""
        citation_patterns = [
            r'\d+\s+U\.S\.?\s+\d+',  # U.S. Reports
            r'\d+\s+S\.?\s?Ct\.?\s+\d+',  # Supreme Court Reporter
            r'\d+\s+L\.?\s?Ed\.?\s?\d*d?\s+\d+',  # Lawyers' Edition
            r'No\.\s+\d+-\d+',  # Docket numbers
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return list(set(citations))  # Remove duplicates

class FederalRegisterMonitor:
    """Monitors Federal Register updates using free RSS feeds and public endpoints"""
    
    def __init__(self):
        self.base_url = 'https://www.federalregister.gov'
        self.api_base = 'https://www.federalregister.gov/api/v1'
        self.rss_feeds = {
            'proposed_rules': f'{self.base_url}/documents/search.rss?conditions%5Btype%5D%5B%5D=PRORULE',
            'final_rules': f'{self.base_url}/documents/search.rss?conditions%5Btype%5D%5B%5D=RULE',
            'notices': f'{self.base_url}/documents/search.rss?conditions%5Btype%5D%5B%5D=NOTICE'
        }
    
    async def get_updates(self, since_date: datetime = None) -> List[LegalUpdate]:
        """Fetch Federal Register updates from RSS feeds"""
        updates = []
        
        if since_date is None:
            since_date = datetime.now() - timedelta(days=3)
            
        try:
            async with aiohttp.ClientSession() as session:
                for feed_type, feed_url in self.rss_feeds.items():
                    logger.info(f"Fetching Federal Register {feed_type} from RSS")
                    
                    async with session.get(feed_url) as response:
                        if response.status == 200:
                            feed_content = await response.text()
                            feed = feedparser.parse(feed_content)
                            
                            for entry in feed.entries:
                                try:
                                    pub_date = datetime(*entry.published_parsed[:6])
                                    
                                    if pub_date >= since_date:
                                        update = await self._parse_federal_register_entry(entry, feed_type)
                                        if update:
                                            updates.append(update)
                                            
                                except Exception as e:
                                    logger.error(f"Error parsing Federal Register entry: {e}")
                                    continue
                        else:
                            logger.error(f"Failed to fetch {feed_url}: {response.status}")
                            
        except Exception as e:
            logger.error(f"Error fetching Federal Register updates: {e}")
            
        logger.info(f"Found {len(updates)} Federal Register updates")
        return updates
    
    async def _parse_federal_register_entry(self, entry, feed_type: str) -> Optional[LegalUpdate]:
        """Parse individual Federal Register RSS entry"""
        try:
            update_id = hashlib.md5(f"fedreg_{entry.link}".encode()).hexdigest()
            
            # Determine update type and priority based on Federal Register document type
            if feed_type == 'final_rules':
                update_type = UpdateType.REGULATION
                priority = UpdatePriority.HIGH
                impact_score = 0.8
            elif feed_type == 'proposed_rules':
                update_type = UpdateType.REGULATION
                priority = UpdatePriority.MEDIUM
                impact_score = 0.6
            else:  # notices
                update_type = UpdateType.POLICY
                priority = UpdatePriority.MEDIUM
                impact_score = 0.5
            
            # Extract legal domains and agencies
            legal_domains = self._extract_legal_domains(f"{entry.title} {entry.summary}")
            agencies = self._extract_agencies(entry.title)
            
            # Extract effective date if available
            effective_date = self._extract_effective_date(entry.summary)
            
            return LegalUpdate(
                update_id=update_id,
                title=entry.title,
                source=UpdateSource.FEDERAL_REGISTER,
                update_type=update_type,
                priority_level=priority,
                publication_date=datetime(*entry.published_parsed[:6]),
                effective_date=effective_date,
                summary=entry.summary if hasattr(entry, 'summary') else entry.title,
                full_content=await self._fetch_full_content(entry.link),
                url=entry.link,
                citations=[],  # Federal Register documents don't typically have case citations
                legal_domains_affected=legal_domains,
                jurisdiction="US",
                superseded_authorities=[],
                impact_score=impact_score,
                confidence_score=0.85,
                metadata={
                    'document_type': feed_type,
                    'agencies': agencies,
                    'raw_entry': dict(entry)
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Federal Register entry: {e}")
            return None
    
    async def _fetch_full_content(self, url: str) -> str:
        """Fetch full content from Federal Register document URL"""
        try:
            # Convert to JSON API endpoint for better content extraction
            document_number = url.split('/')[-1]
            api_url = f"{self.api_base}/documents/{document_number}.json"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        content_parts = []
                        
                        if 'abstract' in data:
                            content_parts.append(f"Abstract: {data['abstract']}")
                        if 'body' in data:
                            content_parts.append(f"Body: {data['body']}")
                        if 'raw_text_url' in data:
                            # Could fetch raw text, but keeping it simple for now
                            pass
                            
                        return '\n\n'.join(content_parts) if content_parts else data.get('title', 'No content available')
                    else:
                        # Fallback to web scraping
                        return await self._scrape_content(url)
        except Exception as e:
            logger.error(f"Error fetching Federal Register content: {e}")
            return "Full content unavailable"
    
    async def _scrape_content(self, url: str) -> str:
        """Fallback web scraping for Federal Register content"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract main document content
                        content_div = soup.find('div', class_='full-text') or soup.find('div', class_='document-content')
                        if content_div:
                            return content_div.get_text(strip=True)[:5000]  # Limit to 5000 chars
                        else:
                            return soup.get_text(strip=True)[:2000]
                    else:
                        return f"Content unavailable (HTTP {response.status})"
        except Exception as e:
            logger.error(f"Error scraping content: {e}")
            return "Content unavailable"
    
    def _extract_legal_domains(self, text: str) -> List[str]:
        """Extract legal domains from Federal Register text"""
        domains = []
        domain_keywords = {
            'administrative_law': ['regulation', 'rule', 'agency', 'administrative'],
            'environmental_law': ['environmental', 'epa', 'clean air', 'clean water', 'pollution'],
            'employment_law': ['employment', 'labor', 'workplace', 'osha', 'worker'],
            'securities_law': ['securities', 'sec', 'investment', 'financial'],
            'healthcare_law': ['health', 'fda', 'medical', 'healthcare', 'drug'],
            'tax_law': ['tax', 'irs', 'revenue', 'taxation'],
            'immigration_law': ['immigration', 'visa', 'naturalization', 'citizenship'],
            'energy_law': ['energy', 'oil', 'gas', 'renewable', 'nuclear'],
            'transportation_law': ['transportation', 'dot', 'highway', 'aviation', 'rail'],
            'consumer_protection': ['consumer', 'ftc', 'protection', 'safety']
        }
        
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ['administrative_law']
    
    def _extract_agencies(self, title: str) -> List[str]:
        """Extract federal agencies from document title"""
        agencies = []
        agency_patterns = {
            'EPA': r'\bEPA\b|\bEnvironmental Protection Agency\b',
            'SEC': r'\bSEC\b|\bSecurities and Exchange Commission\b',
            'FDA': r'\bFDA\b|\bFood and Drug Administration\b',
            'IRS': r'\bIRS\b|\bInternal Revenue Service\b',
            'DOL': r'\bDOL\b|\bDepartment of Labor\b',
            'DOT': r'\bDOT\b|\bDepartment of Transportation\b',
            'FTC': r'\bFTC\b|\bFederal Trade Commission\b',
            'OSHA': r'\bOSHA\b|\bOccupational Safety and Health Administration\b'
        }
        
        for agency, pattern in agency_patterns.items():
            if re.search(pattern, title, re.IGNORECASE):
                agencies.append(agency)
        
        return agencies
    
    def _extract_effective_date(self, text: str) -> Optional[datetime]:
        """Extract effective date from Federal Register text"""
        try:
            date_patterns = [
                r'effective\s+(?:on\s+)?(\w+\s+\d{1,2},\s+\d{4})',
                r'effective\s+date[:\s]+(\w+\s+\d{1,2},\s+\d{4})',
                r'becomes?\s+effective\s+(\w+\s+\d{1,2},\s+\d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    try:
                        return datetime.strptime(date_str, '%B %d, %Y')
                    except ValueError:
                        try:
                            return datetime.strptime(date_str, '%b %d, %Y')
                        except ValueError:
                            continue
        except Exception as e:
            logger.error(f"Error extracting effective date: {e}")
        
        return None

class CircuitCourtMonitor:
    """Monitors Circuit Court decisions using CourtListener free API"""
    
    def __init__(self, courtlistener_api_key: str):
        self.api_key = courtlistener_api_key
        self.base_url = 'https://www.courtlistener.com/api/rest/v3'
        self.circuit_courts = [
            'ca1', 'ca2', 'ca3', 'ca4', 'ca5', 'ca6', 'ca7', 'ca8', 'ca9', 'ca10', 'ca11', 'cadc', 'cafc'
        ]
    
    async def get_updates(self, since_date: datetime = None) -> List[LegalUpdate]:
        """Fetch Circuit Court updates from CourtListener"""
        updates = []
        
        if since_date is None:
            since_date = datetime.now() - timedelta(days=7)
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Token {self.api_key}'}
                
                for court in self.circuit_courts:
                    logger.info(f"Fetching updates for {court}")
                    
                    # Search for recent opinions from this circuit court
                    search_params = {
                        'court': court,
                        'filed_after': since_date.strftime('%Y-%m-%d'),
                        'order_by': '-date_filed',
                        'format': 'json'
                    }
                    
                    async with session.get(
                        f'{self.base_url}/search/',
                        params=search_params,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for result in data.get('results', [])[:5]:  # Limit to 5 per court
                                try:
                                    update = await self._parse_courtlistener_result(result, court)
                                    if update:
                                        updates.append(update)
                                except Exception as e:
                                    logger.error(f"Error parsing CourtListener result: {e}")
                                    continue
                        else:
                            logger.error(f"Failed to fetch {court} updates: {response.status}")
                            
                    # Rate limiting to be respectful to free API
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"Error fetching Circuit Court updates: {e}")
            
        logger.info(f"Found {len(updates)} Circuit Court updates")
        return updates
    
    async def _parse_courtlistener_result(self, result: Dict, court: str) -> Optional[LegalUpdate]:
        """Parse CourtListener search result"""
        try:
            update_id = hashlib.md5(f"circuit_{result.get('id', '')}{court}".encode()).hexdigest()
            
            # Determine priority based on precedent setting indicators
            case_name = result.get('caseName', '')
            snippet = result.get('snippet', '')
            
            # Higher priority for precedent-setting cases
            precedent_indicators = ['overrule', 'overturn', 'en banc', 'circuit split', 'first impression']
            priority = UpdatePriority.HIGH if any(indicator in snippet.lower() for indicator in precedent_indicators) else UpdatePriority.MEDIUM
            
            # Extract legal domains
            legal_domains = self._extract_legal_domains(f"{case_name} {snippet}")
            
            # Extract citations
            citations = self._extract_citations(snippet)
            
            return LegalUpdate(
                update_id=update_id,
                title=case_name,
                source=UpdateSource.CIRCUIT_COURT,
                update_type=UpdateType.DECISION,
                priority_level=priority,
                publication_date=datetime.strptime(result.get('dateFiled', ''), '%Y-%m-%d') if result.get('dateFiled') else datetime.now(),
                effective_date=None,
                summary=snippet,
                full_content=await self._fetch_full_opinion(result.get('download_url', '')),
                url=result.get('absolute_url', ''),
                citations=citations,
                legal_domains_affected=legal_domains,
                jurisdiction="US",
                superseded_authorities=[],
                impact_score=0.7 if priority == UpdatePriority.HIGH else 0.5,
                confidence_score=0.8,
                metadata={
                    'court': court,
                    'case_id': result.get('id'),
                    'judges': result.get('judges', []),
                    'raw_result': result
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing CourtListener result: {e}")
            return None
    
    async def _fetch_full_opinion(self, download_url: str) -> str:
        """Fetch full opinion text if available"""
        if not download_url:
            return "Full opinion not available"
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Token {self.api_key}'}
                async with session.get(download_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        return content[:10000]  # Limit to 10k characters
                    else:
                        return f"Opinion unavailable (HTTP {response.status})"
        except Exception as e:
            logger.error(f"Error fetching full opinion: {e}")
            return "Opinion unavailable"
    
    def _extract_legal_domains(self, text: str) -> List[str]:
        """Extract legal domains from circuit court case text"""
        domains = []
        domain_keywords = {
            'constitutional_law': ['constitutional', 'amendment', 'due process', 'equal protection'],
            'contract_law': ['contract', 'breach', 'agreement', 'consideration'],
            'tort_law': ['negligence', 'liability', 'damages', 'tort'],
            'criminal_law': ['criminal', 'prosecution', 'sentencing', 'appeal'],
            'employment_law': ['employment', 'discrimination', 'wrongful termination'],
            'intellectual_property': ['patent', 'copyright', 'trademark', 'trade secret'],
            'securities_law': ['securities', 'fraud', 'investment', 'insider trading'],
            'antitrust_law': ['antitrust', 'monopoly', 'competition', 'sherman act'],
            'administrative_law': ['agency action', 'regulation', 'administrative review'],
            'civil_rights': ['civil rights', 'discrimination', 'section 1983']
        }
        
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ['general_law']
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract legal citations from circuit court text"""
        citation_patterns = [
            r'\d+\s+F\.\d*d?\s+\d+',  # Federal Reporter
            r'\d+\s+F\.Supp\.\d*d?\s+\d+',  # Federal Supplement
            r'\d+\s+U\.S\.?\s+\d+',  # U.S. Reports
            r'No\.\s+\d+-\d+',  # Case numbers
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return list(set(citations))

class LegalUpdatesMonitor:
    """Main coordinator for all legal update monitoring"""
    
    def __init__(self, courtlistener_api_key: str):
        self.supreme_court_monitor = SupremeCourtMonitor()
        self.federal_register_monitor = FederalRegisterMonitor()
        self.circuit_court_monitor = CircuitCourtMonitor(courtlistener_api_key)
        
        self.monitoring_stats = MonitoringStats(
            total_updates_found=0,
            updates_by_source={},
            updates_by_priority={},
            last_check_time=datetime.now(),
            next_check_time=datetime.now() + timedelta(hours=6),
            success_rate=0.0,
            average_processing_time=0.0
        )
    
    async def monitor_all_sources(self, since_date: datetime = None) -> List[LegalUpdate]:
        """Monitor all legal update sources and return consolidated results"""
        start_time = time.time()
        all_updates = []
        
        try:
            logger.info("Starting comprehensive legal updates monitoring...")
            
            # Monitor Supreme Court (highest priority)
            scotus_updates = await self.supreme_court_monitor.get_updates(since_date)
            all_updates.extend(scotus_updates)
            
            # Monitor Federal Register  
            fedreg_updates = await self.federal_register_monitor.get_updates(since_date)
            all_updates.extend(fedreg_updates)
            
            # Monitor Circuit Courts
            circuit_updates = await self.circuit_court_monitor.get_updates(since_date)
            all_updates.extend(circuit_updates)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_monitoring_stats(all_updates, processing_time)
            
            logger.info(f"Monitoring completed: {len(all_updates)} total updates found in {processing_time:.2f}s")
            
            return sorted(all_updates, key=lambda x: (x.priority_level.value, x.publication_date), reverse=True)
            
        except Exception as e:
            logger.error(f"Error in comprehensive monitoring: {e}")
            return []
    
    def _update_monitoring_stats(self, updates: List[LegalUpdate], processing_time: float):
        """Update monitoring statistics"""
        self.monitoring_stats.total_updates_found = len(updates)
        self.monitoring_stats.last_check_time = datetime.now()
        self.monitoring_stats.next_check_time = datetime.now() + timedelta(hours=6)
        self.monitoring_stats.average_processing_time = processing_time
        
        # Update counts by source
        source_counts = {}
        priority_counts = {}
        
        for update in updates:
            source = update.source.value
            priority = update.priority_level.value
            
            source_counts[source] = source_counts.get(source, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        self.monitoring_stats.updates_by_source = source_counts
        self.monitoring_stats.updates_by_priority = priority_counts
        self.monitoring_stats.success_rate = 1.0  # Will be updated based on actual success/failure tracking
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring system status"""
        return {
            "is_running": True,
            "total_updates_found": self.monitoring_stats.total_updates_found,
            "last_check_time": self.monitoring_stats.last_check_time.isoformat(),
            "next_check_time": self.monitoring_stats.next_check_time.isoformat(),
            "success_rate": self.monitoring_stats.success_rate,
            "average_processing_time": self.monitoring_stats.average_processing_time,
            "updates_by_source": self.monitoring_stats.updates_by_source,
            "updates_by_priority": self.monitoring_stats.updates_by_priority,
            "monitored_sources": ["supreme_court", "federal_register", "circuit_courts"]
        }

# Global instance (will be initialized in server.py)
legal_updates_monitor = None

def initialize_legal_updates_monitor(courtlistener_api_key: str):
    """Initialize the global legal updates monitor"""
    global legal_updates_monitor
    legal_updates_monitor = LegalUpdatesMonitor(courtlistener_api_key)
    return legal_updates_monitor
"""
Marketplace & Partnership Ecosystem for Legal AI System
Provides comprehensive marketplace, developer ecosystem, and partnership management
100% Free and Open Source Implementation
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import httpx
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PartnerType(Enum):
    """Types of partners in the ecosystem"""
    TECHNOLOGY_PARTNER = "technology_partner"
    INTEGRATION_PARTNER = "integration_partner"
    CHANNEL_PARTNER = "channel_partner"
    RESELLER_PARTNER = "reseller_partner"
    LEGAL_SERVICE_PROVIDER = "legal_service_provider"
    SOFTWARE_VENDOR = "software_vendor"
    CONSULTANT = "consultant"
    TRAINER = "trainer"

class AppCategory(Enum):
    """Categories for marketplace apps"""
    PRACTICE_MANAGEMENT = "practice_management"
    DOCUMENT_AUTOMATION = "document_automation"
    LEGAL_RESEARCH = "legal_research"
    CLIENT_COMMUNICATION = "client_communication"
    BILLING_TIME_TRACKING = "billing_time_tracking"
    COMPLIANCE_MANAGEMENT = "compliance_management"
    WORKFLOW_AUTOMATION = "workflow_automation"
    ANALYTICS_REPORTING = "analytics_reporting"
    COLLABORATION_TOOLS = "collaboration_tools"
    INTEGRATIONS = "integrations"

class PartnerStatus(Enum):
    """Partner status in the ecosystem"""
    PROSPECTIVE = "prospective"
    ACTIVE = "active"
    CERTIFIED = "certified"
    PREMIUM = "premium"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class AppStatus(Enum):
    """Status of marketplace applications"""
    DEVELOPMENT = "development"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    REMOVED = "removed"

class MarketplaceApp(BaseModel):
    """Marketplace application model"""
    app_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: AppCategory
    developer_id: str
    version: str = "1.0.0"
    status: AppStatus = AppStatus.DEVELOPMENT
    
    # App Details
    short_description: str
    detailed_description: str
    features: List[str] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    demo_url: Optional[str] = None
    documentation_url: Optional[str] = None
    support_url: Optional[str] = None
    
    # Technical Details
    api_endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    webhooks_supported: List[str] = Field(default_factory=list)
    data_formats: List[str] = Field(default_factory=list)
    
    # Pricing
    pricing_model: str = "free"  # "free", "freemium", "subscription", "one_time"
    price_details: Dict[str, Any] = Field(default_factory=dict)
    free_tier_limitations: List[str] = Field(default_factory=list)
    
    # Requirements
    minimum_requirements: Dict[str, Any] = Field(default_factory=dict)
    supported_platforms: List[str] = Field(default_factory=list)
    legal_jurisdictions: List[str] = Field(default_factory=list)
    
    # Statistics
    install_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Compliance
    compliance_certifications: List[str] = Field(default_factory=list)
    security_standards: List[str] = Field(default_factory=list)
    privacy_policy_url: Optional[str] = None
    terms_of_service_url: Optional[str] = None

class Partner(BaseModel):
    """Partner organization model"""
    partner_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_name: str
    partner_type: PartnerType
    status: PartnerStatus = PartnerStatus.PROSPECTIVE
    
    # Contact Information
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: Optional[str] = None
    website: Optional[str] = None
    
    # Business Information
    industry_focus: List[str] = Field(default_factory=list)
    geographic_coverage: List[str] = Field(default_factory=list)
    target_market: List[str] = Field(default_factory=list)
    annual_revenue: Optional[str] = None  # "startup", "small", "medium", "large", "enterprise"
    employee_count: Optional[int] = None
    
    # Partnership Details
    partnership_tier: str = "basic"  # "basic", "silver", "gold", "platinum"
    services_offered: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)
    
    # Technical Capabilities
    technical_expertise: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)
    supported_technologies: List[str] = Field(default_factory=list)
    
    # Performance Metrics
    customer_satisfaction_score: float = 0.0
    project_success_rate: float = 0.0
    response_time_hours: float = 24.0
    
    # Commercial Terms
    commission_rate: float = 0.0  # For reseller partners
    discount_rate: float = 0.0   # For technology partners
    minimum_commitment: Optional[str] = None
    contract_terms: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None
    notes: str = ""
    
    # Apps/Solutions
    published_apps: List[str] = Field(default_factory=list)  # List of app_ids

class DeveloperProfile(BaseModel):
    """Developer profile for marketplace"""
    developer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    organization: Optional[str] = None
    
    # Profile Information
    bio: str = ""
    website: Optional[str] = None
    github_profile: Optional[str] = None
    linkedin_profile: Optional[str] = None
    
    # Skills and Expertise
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    legal_tech_experience: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    
    # Developer Metrics
    apps_published: int = 0
    total_downloads: int = 0
    average_rating: float = 0.0
    developer_level: str = "community"  # "community", "verified", "professional", "enterprise"
    
    # API Access
    api_key: Optional[str] = None
    api_usage_tier: str = "free"  # "free", "pro", "enterprise"
    monthly_api_calls: int = 0
    api_rate_limit: int = 1000
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: Optional[datetime] = None
    is_active: bool = True

class AppReview(BaseModel):
    """App review and rating model"""
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    app_id: str
    user_id: str
    law_firm_name: Optional[str] = None
    
    # Review Content
    rating: int = Field(ge=1, le=5)  # 1-5 stars
    title: str
    review_text: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    
    # Context
    use_case: str = ""
    firm_size: Optional[str] = None  # "solo", "small", "medium", "large"
    practice_areas: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    verified_purchase: bool = False
    helpful_votes: int = 0
    total_votes: int = 0

class MarketplacePartnershipEcosystem:
    """
    Comprehensive marketplace and partnership ecosystem
    Manages apps, partners, developers, and community interactions
    """
    
    def __init__(self):
        self.marketplace_apps: Dict[str, MarketplaceApp] = {}
        self.partners: Dict[str, Partner] = {}
        self.developers: Dict[str, DeveloperProfile] = {}
        self.app_reviews: Dict[str, AppReview] = {}
        self.app_installations: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize sample data
        self.initialize_sample_apps()
        self.initialize_sample_partners()
    
    def initialize_sample_apps(self):
        """Initialize sample marketplace apps"""
        
        # Practice Management Integration App
        practice_mgmt_app = MarketplaceApp(
            name="EspoCRM Legal Integration",
            description="Seamless integration with EspoCRM for legal practice management",
            category=AppCategory.PRACTICE_MANAGEMENT,
            developer_id="espocrm_dev_001",
            version="2.1.0",
            status=AppStatus.PUBLISHED,
            short_description="Connect your legal AI with EspoCRM for complete practice management",
            detailed_description="""
            The EspoCRM Legal Integration app provides seamless connectivity between your legal AI system 
            and EspoCRM, enabling comprehensive practice management capabilities including:
            
            • Client relationship management
            • Case and matter tracking
            • Document management integration
            • Time tracking and billing
            • Calendar and deadline management
            • Automated workflow triggers
            
            This integration is completely free to use and supports unlimited users and cases.
            """,
            features=[
                "Client synchronization",
                "Case management integration",
                "Document workflow automation",
                "Billing and time tracking",
                "Calendar integration",
                "Custom field mapping",
                "Real-time data sync",
                "Audit trail maintenance"
            ],
            api_endpoints=[
                {"endpoint": "/api/espocrm/clients", "method": "GET", "description": "Sync client data"},
                {"endpoint": "/api/espocrm/cases", "method": "POST", "description": "Create new cases"},
                {"endpoint": "/api/espocrm/documents", "method": "PUT", "description": "Update document status"}
            ],
            webhooks_supported=["case_created", "client_updated", "document_generated"],
            data_formats=["JSON", "XML"],
            pricing_model="free",
            price_details={"cost": 0, "description": "Completely free and open source"},
            supported_platforms=["Web", "API"],
            legal_jurisdictions=["US", "UK", "CA", "AU", "EU"],
            install_count=1250,
            rating=4.7,
            review_count=89,
            tags=["crm", "practice-management", "free", "open-source"],
            compliance_certifications=["SOC 2", "GDPR"],
            security_standards=["TLS 1.2", "OAuth 2.0"],
            published_at=datetime.utcnow() - timedelta(days=30)
        )
        
        # Document Automation App
        doc_automation_app = MarketplaceApp(
            name="Smart Legal Document Generator",
            description="AI-powered document generation with legal templates",
            category=AppCategory.DOCUMENT_AUTOMATION,
            developer_id="smart_docs_dev_001",
            version="3.2.1",
            status=AppStatus.PUBLISHED,
            short_description="Generate professional legal documents using AI and customizable templates",
            detailed_description="""
            Smart Legal Document Generator revolutionizes legal document creation with AI-powered 
            automation and an extensive template library. Features include:
            
            • 500+ professional legal templates
            • AI-powered clause suggestions
            • Multi-jurisdiction compliance
            • Collaborative editing
            • Version control and tracking
            • Integration with major legal platforms
            
            Free tier includes 50 documents per month with basic templates.
            """,
            features=[
                "500+ legal templates",
                "AI clause suggestions",
                "Multi-jurisdiction support",
                "Collaborative editing",
                "Version control",
                "Custom branding",
                "E-signature integration",
                "Automated compliance checking"
            ],
            api_endpoints=[
                {"endpoint": "/api/documents/generate", "method": "POST", "description": "Generate new document"},
                {"endpoint": "/api/templates", "method": "GET", "description": "List available templates"},
                {"endpoint": "/api/documents/collaborate", "method": "PUT", "description": "Collaborative editing"}
            ],
            webhooks_supported=["document_created", "document_signed", "collaboration_started"],
            data_formats=["JSON", "PDF", "DOCX"],
            pricing_model="freemium",
            price_details={
                "free": {"documents_per_month": 50, "templates": "basic", "cost": 0},
                "pro": {"documents_per_month": 500, "templates": "all", "cost": 29.99},
                "enterprise": {"documents_per_month": "unlimited", "templates": "all", "custom_branding": True, "cost": 99.99}
            },
            free_tier_limitations=["50 documents/month", "Basic templates only", "Standard support"],
            supported_platforms=["Web", "API", "Mobile"],
            legal_jurisdictions=["US", "UK", "CA", "AU", "EU", "IN"],
            install_count=5420,
            rating=4.6,
            review_count=312,
            tags=["document-automation", "ai", "templates", "collaboration"],
            compliance_certifications=["SOC 2", "HIPAA", "GDPR"],
            security_standards=["TLS 1.3", "AES-256", "OAuth 2.0"],
            published_at=datetime.utcnow() - timedelta(days=60)
        )
        
        # Legal Research Enhancement App
        research_app = MarketplaceApp(
            name="CourtListener Pro Research",
            description="Enhanced legal research with AI-powered case analysis",
            category=AppCategory.LEGAL_RESEARCH,
            developer_id="courtlistener_pro_001",
            version="1.8.3",
            status=AppStatus.PUBLISHED,
            short_description="Supercharge your legal research with AI analysis and enhanced CourtListener integration",
            detailed_description="""
            CourtListener Pro Research extends the free CourtListener service with advanced AI capabilities:
            
            • AI-powered case relevance scoring
            • Automated legal brief generation
            • Citation network analysis
            • Trend analysis and predictions
            • Custom research alerts
            • Bulk case processing
            
            Built on the free CourtListener API with additional AI enhancements.
            """,
            features=[
                "AI case relevance scoring",
                "Automated brief generation",
                "Citation network analysis",
                "Legal trend analysis",
                "Custom alert system",
                "Bulk processing",
                "Advanced search filters",
                "Export capabilities"
            ],
            api_endpoints=[
                {"endpoint": "/api/research/analyze", "method": "POST", "description": "AI case analysis"},
                {"endpoint": "/api/research/alerts", "method": "POST", "description": "Set research alerts"},
                {"endpoint": "/api/research/trends", "method": "GET", "description": "Legal trend data"}
            ],
            webhooks_supported=["new_relevant_case", "alert_triggered", "analysis_complete"],
            data_formats=["JSON", "PDF", "CSV"],
            pricing_model="free",
            price_details={"cost": 0, "description": "Free with CourtListener data, enhanced with AI"},
            supported_platforms=["Web", "API"],
            legal_jurisdictions=["US"],
            install_count=892,
            rating=4.8,
            review_count=67,
            tags=["legal-research", "ai", "free", "courtlistener"],
            compliance_certifications=["SOC 2"],
            security_standards=["TLS 1.2", "API Key Authentication"],
            published_at=datetime.utcnow() - timedelta(days=45)
        )
        
        # Workflow Automation App
        workflow_app = MarketplaceApp(
            name="n8n Legal Workflows",
            description="Pre-built legal workflows for n8n automation platform",
            category=AppCategory.WORKFLOW_AUTOMATION,
            developer_id="n8n_legal_workflows_001",
            version="2.0.0",
            status=AppStatus.PUBLISHED,
            short_description="Ready-to-use legal workflow templates for n8n automation platform",
            detailed_description="""
            n8n Legal Workflows provides a comprehensive collection of pre-built workflow templates 
            specifically designed for legal practices:
            
            • 50+ legal workflow templates
            • Client onboarding automation
            • Document review workflows
            • Billing and time tracking automation
            • Court deadline management
            • Client communication sequences
            
            Requires n8n (free, open-source) workflow automation platform.
            """,
            features=[
                "50+ workflow templates",
                "Client onboarding automation",
                "Document review workflows",
                "Billing automation",
                "Deadline management",
                "Communication sequences",
                "Integration connectors",
                "Custom trigger support"
            ],
            api_endpoints=[
                {"endpoint": "/api/workflows/templates", "method": "GET", "description": "List workflow templates"},
                {"endpoint": "/api/workflows/import", "method": "POST", "description": "Import workflow to n8n"},
                {"endpoint": "/api/workflows/customize", "method": "PUT", "description": "Customize workflow parameters"}
            ],
            webhooks_supported=["workflow_installed", "workflow_executed", "workflow_error"],
            data_formats=["JSON", "n8n Workflow Format"],
            pricing_model="free",
            price_details={"cost": 0, "description": "Free workflow templates for n8n"},
            minimum_requirements={"n8n": ">=0.150.0", "node_js": ">=14.0.0"},
            supported_platforms=["n8n", "API"],
            legal_jurisdictions=["US", "UK", "CA", "AU", "EU"],
            install_count=2340,
            rating=4.9,
            review_count=156,
            tags=["workflow", "automation", "n8n", "free", "templates"],
            compliance_certifications=["Open Source"],
            security_standards=["Self-hosted Security"],
            published_at=datetime.utcnow() - timedelta(days=20)
        )
        
        # Client Portal App
        client_portal_app = MarketplaceApp(
            name="Secure Legal Client Portal",
            description="Self-hosted client portal with document sharing and communication",
            category=AppCategory.CLIENT_COMMUNICATION,
            developer_id="legal_portal_dev_001",
            version="1.5.2",
            status=AppStatus.PUBLISHED,
            short_description="Self-hosted client portal ensuring attorney-client privilege protection",
            detailed_description="""
            Secure Legal Client Portal provides a complete client communication solution that you can 
            host on your own infrastructure:
            
            • Secure document sharing
            • Encrypted client messaging
            • Case status updates
            • Invoice and payment tracking
            • Appointment scheduling
            • Client intake forms
            
            Fully self-hosted to maintain complete control over client data and communications.
            """,
            features=[
                "Secure document sharing",
                "Encrypted messaging",
                "Case status tracking",
                "Invoice management",
                "Appointment scheduling",
                "Client intake forms",
                "Mobile responsive",
                "Custom branding"
            ],
            api_endpoints=[
                {"endpoint": "/api/portal/documents", "method": "POST", "description": "Share documents with clients"},
                {"endpoint": "/api/portal/messages", "method": "POST", "description": "Send secure messages"},
                {"endpoint": "/api/portal/appointments", "method": "GET", "description": "Manage appointments"}
            ],
            webhooks_supported=["document_viewed", "message_received", "appointment_scheduled"],
            data_formats=["JSON", "PDF", "Encrypted"],
            pricing_model="free",
            price_details={"cost": 0, "description": "Free, self-hosted solution"},
            minimum_requirements={"server": "Linux/Windows", "database": "MySQL/PostgreSQL", "php": ">=7.4"},
            supported_platforms=["Self-hosted", "API"],
            legal_jurisdictions=["US", "UK", "CA", "AU", "EU"],
            install_count=756,
            rating=4.5,
            review_count=42,
            tags=["client-portal", "secure", "self-hosted", "free"],
            compliance_certifications=["Attorney-Client Privilege", "GDPR"],
            security_standards=["AES-256", "TLS 1.3", "Self-hosted Security"],
            published_at=datetime.utcnow() - timedelta(days=75)
        )
        
        # Store apps
        apps = [practice_mgmt_app, doc_automation_app, research_app, workflow_app, client_portal_app]
        for app in apps:
            self.marketplace_apps[app.app_id] = app
        
        logger.info(f"Initialized {len(apps)} sample marketplace apps")
    
    def initialize_sample_partners(self):
        """Initialize sample partner organizations"""
        
        # Legal Technology Partner
        legal_tech_partner = Partner(
            organization_name="LegalTech Innovations LLC",
            partner_type=PartnerType.TECHNOLOGY_PARTNER,
            status=PartnerStatus.CERTIFIED,
            primary_contact_name="Sarah Johnson",
            primary_contact_email="sarah@legaltech-innovations.com",
            website="https://legaltech-innovations.com",
            industry_focus=["Legal Technology", "AI/ML", "Document Automation"],
            geographic_coverage=["North America", "Europe"],
            target_market=["Law Firms", "Corporate Legal", "Legal Service Providers"],
            annual_revenue="medium",
            employee_count=45,
            partnership_tier="gold",
            services_offered=[
                "Custom Integration Development",
                "API Consulting",
                "Legal AI Implementation",
                "Training and Support"
            ],
            certifications=["Microsoft Certified Partner", "AWS Advanced Partner", "LegalMate Certified Developer"],
            specializations=["Document Automation", "Workflow Integration", "AI Implementation"],
            technical_expertise=["Python", "React", "MongoDB", "AI/ML", "API Development"],
            integration_capabilities=["REST APIs", "GraphQL", "WebSockets", "Webhooks"],
            supported_technologies=["LegalMate API", "Microsoft Graph", "Google Workspace", "Zapier"],
            customer_satisfaction_score=4.8,
            project_success_rate=96.5,
            response_time_hours=4.0,
            discount_rate=15.0,
            contract_terms={"minimum_project_size": "$5000", "payment_terms": "Net 30"},
            approved_at=datetime.utcnow() - timedelta(days=120)
        )
        
        # Integration Partner
        integration_partner = Partner(
            organization_name="Open Source Legal Solutions",
            partner_type=PartnerType.INTEGRATION_PARTNER,
            status=PartnerStatus.ACTIVE,
            primary_contact_name="Michael Chen",
            primary_contact_email="michael@oss-legal.org",
            website="https://oss-legal.org",
            industry_focus=["Open Source Software", "Legal Technology"],
            geographic_coverage=["Global"],
            target_market=["Solo Practitioners", "Small Law Firms", "Legal Aid Organizations"],
            annual_revenue="startup",
            employee_count=12,
            partnership_tier="silver",
            services_offered=[
                "Open Source Integration Development",
                "Community Support",
                "Documentation Creation",
                "Training Workshops"
            ],
            certifications=["Open Source Initiative Member", "LegalMate Community Partner"],
            specializations=["Open Source Solutions", "Community Building", "Documentation"],
            technical_expertise=["Python", "JavaScript", "Docker", "Linux", "Open Source Licensing"],
            integration_capabilities=["REST APIs", "Open Source Connectors", "Community Plugins"],
            supported_technologies=["n8n", "Apache Airflow", "NextCloud", "OpenLDAP"],
            customer_satisfaction_score=4.6,
            project_success_rate=88.2,
            response_time_hours=12.0,
            commission_rate=0.0,  # Non-profit organization
            contract_terms={"engagement_model": "community_based", "support_model": "volunteer"},
            approved_at=datetime.utcnow() - timedelta(days=60)
        )
        
        # Reseller Partner
        reseller_partner = Partner(
            organization_name="Legal Solutions Marketplace Inc.",
            partner_type=PartnerType.RESELLER_PARTNER,
            status=PartnerStatus.ACTIVE,
            primary_contact_name="David Rodriguez",
            primary_contact_email="david@legal-marketplace.com",
            website="https://legal-marketplace.com",
            industry_focus=["Legal Software Sales", "Professional Services"],
            geographic_coverage=["United States", "Canada"],
            target_market=["Medium Law Firms", "Large Law Firms", "Corporate Legal"],
            annual_revenue="large",
            employee_count=125,
            partnership_tier="platinum",
            services_offered=[
                "Software Licensing",
                "Implementation Services",
                "Training Programs",
                "Ongoing Support"
            ],
            certifications=["Certified Legal Technology Consultant", "Project Management Professional"],
            specializations=["Enterprise Sales", "Implementation", "Change Management"],
            technical_expertise=["Enterprise Architecture", "Project Management", "Training"],
            integration_capabilities=["Enterprise Integration", "Single Sign-On", "Custom Deployment"],
            supported_technologies=["Microsoft Office 365", "Google Workspace", "Salesforce", "Enterprise LDAP"],
            customer_satisfaction_score=4.4,
            project_success_rate=92.0,
            response_time_hours=2.0,
            commission_rate=20.0,
            minimum_commitment="$50,000 annual sales",
            contract_terms={"territory": "North America", "exclusivity": "non-exclusive"},
            approved_at=datetime.utcnow() - timedelta(days=90)
        )
        
        # Service Provider Partner
        service_provider_partner = Partner(
            organization_name="Legal Process Automation Experts",
            partner_type=PartnerType.LEGAL_SERVICE_PROVIDER,
            status=PartnerStatus.CERTIFIED,
            primary_contact_name="Jennifer Williams",
            primary_contact_email="jennifer@legal-automation.com",
            website="https://legal-automation.com",
            industry_focus=["Legal Process Automation", "Business Process Outsourcing"],
            geographic_coverage=["North America", "Europe", "Asia Pacific"],
            target_market=["Law Firms", "Corporate Legal", "Government"],
            annual_revenue="medium",
            employee_count=85,
            partnership_tier="gold",
            services_offered=[
                "Process Automation Consulting",
                "Workflow Design",
                "Staff Training",
                "Ongoing Process Management"
            ],
            certifications=["Six Sigma Black Belt", "Legal Process Improvement Specialist"],
            specializations=["Workflow Automation", "Process Optimization", "Change Management"],
            technical_expertise=["Business Process Management", "Workflow Automation", "Data Analysis"],
            integration_capabilities=["Workflow Automation Tools", "Business Intelligence", "Process Analytics"],
            supported_technologies=["n8n", "Apache Airflow", "Business Intelligence Tools"],
            customer_satisfaction_score=4.7,
            project_success_rate=94.8,
            response_time_hours=6.0,
            commission_rate=25.0,
            contract_terms={"service_level_agreements": "included", "performance_guarantees": "included"},
            approved_at=datetime.utcnow() - timedelta(days=150)
        )
        
        # Store partners
        partners = [legal_tech_partner, integration_partner, reseller_partner, service_provider_partner]
        for partner in partners:
            self.partners[partner.partner_id] = partner
        
        logger.info(f"Initialized {len(partners)} sample partners")
    
    def search_marketplace_apps(self, category: AppCategory = None, search_query: str = None, 
                               pricing_model: str = None, min_rating: float = None,
                               tags: List[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Search marketplace apps with filters"""
        
        apps = list(self.marketplace_apps.values())
        
        # Filter by category
        if category:
            apps = [app for app in apps if app.category == category]
        
        # Filter by search query (name, description, tags)
        if search_query:
            query_lower = search_query.lower()
            apps = [
                app for app in apps
                if (query_lower in app.name.lower() or 
                    query_lower in app.description.lower() or 
                    any(query_lower in tag.lower() for tag in app.tags))
            ]
        
        # Filter by pricing model
        if pricing_model:
            apps = [app for app in apps if app.pricing_model == pricing_model]
        
        # Filter by minimum rating
        if min_rating:
            apps = [app for app in apps if app.rating >= min_rating]
        
        # Filter by tags
        if tags:
            apps = [
                app for app in apps
                if any(tag in app.tags for tag in tags)
            ]
        
        # Filter only published apps
        apps = [app for app in apps if app.status == AppStatus.PUBLISHED]
        
        # Sort by rating and install count
        apps.sort(key=lambda x: (x.rating, x.install_count), reverse=True)
        
        # Limit results
        apps = apps[:limit]
        
        return {
            "total_results": len(apps),
            "apps": [
                {
                    "app_id": app.app_id,
                    "name": app.name,
                    "description": app.short_description,
                    "category": app.category.value,
                    "version": app.version,
                    "rating": app.rating,
                    "review_count": app.review_count,
                    "install_count": app.install_count,
                    "pricing_model": app.pricing_model,
                    "tags": app.tags,
                    "developer_id": app.developer_id,
                    "published_at": app.published_at.isoformat() if app.published_at else None
                }
                for app in apps
            ]
        }
    
    def get_app_details(self, app_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific app"""
        
        if app_id not in self.marketplace_apps:
            return {
                "success": False,
                "error": "App not found",
                "error_code": "APP_NOT_FOUND"
            }
        
        app = self.marketplace_apps[app_id]
        
        # Get recent reviews
        app_reviews = [
            review for review in self.app_reviews.values()
            if review.app_id == app_id
        ]
        app_reviews.sort(key=lambda x: x.created_at, reverse=True)
        recent_reviews = app_reviews[:5]
        
        return {
            "success": True,
            "app": {
                "app_id": app.app_id,
                "name": app.name,
                "description": app.description,
                "detailed_description": app.detailed_description,
                "category": app.category.value,
                "version": app.version,
                "status": app.status.value,
                "features": app.features,
                "screenshots": app.screenshots,
                "demo_url": app.demo_url,
                "documentation_url": app.documentation_url,
                "support_url": app.support_url,
                "api_endpoints": app.api_endpoints,
                "webhooks_supported": app.webhooks_supported,
                "data_formats": app.data_formats,
                "pricing_model": app.pricing_model,
                "price_details": app.price_details,
                "free_tier_limitations": app.free_tier_limitations,
                "minimum_requirements": app.minimum_requirements,
                "supported_platforms": app.supported_platforms,
                "legal_jurisdictions": app.legal_jurisdictions,
                "install_count": app.install_count,
                "rating": app.rating,
                "review_count": app.review_count,
                "tags": app.tags,
                "compliance_certifications": app.compliance_certifications,
                "security_standards": app.security_standards,
                "developer_id": app.developer_id,
                "created_at": app.created_at.isoformat(),
                "published_at": app.published_at.isoformat() if app.published_at else None
            },
            "recent_reviews": [
                {
                    "review_id": review.review_id,
                    "rating": review.rating,
                    "title": review.title,
                    "review_text": review.review_text,
                    "law_firm_name": review.law_firm_name,
                    "use_case": review.use_case,
                    "created_at": review.created_at.isoformat(),
                    "helpful_votes": review.helpful_votes,
                    "verified_purchase": review.verified_purchase
                }
                for review in recent_reviews
            ]
        }
    
    def install_app(self, app_id: str, user_id: str, law_firm_id: str, 
                   installation_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Install an app for a law firm"""
        
        if app_id not in self.marketplace_apps:
            return {
                "success": False,
                "error": "App not found",
                "error_code": "APP_NOT_FOUND"
            }
        
        app = self.marketplace_apps[app_id]
        
        if app.status != AppStatus.PUBLISHED:
            return {
                "success": False,
                "error": "App is not available for installation",
                "error_code": "APP_NOT_AVAILABLE"
            }
        
        # Create installation record
        installation = {
            "installation_id": str(uuid.uuid4()),
            "app_id": app_id,
            "app_name": app.name,
            "user_id": user_id,
            "law_firm_id": law_firm_id,
            "version": app.version,
            "installed_at": datetime.utcnow().isoformat(),
            "status": "installed",
            "configuration": installation_config or {},
            "api_keys_generated": [],
            "webhooks_configured": []
        }
        
        # Add to installations tracking
        if app_id not in self.app_installations:
            self.app_installations[app_id] = []
        self.app_installations[app_id].append(installation)
        
        # Update app install count
        app.install_count += 1
        
        logger.info(f"App {app.name} installed for law firm {law_firm_id}")
        
        return {
            "success": True,
            "installation": installation,
            "app_info": {
                "name": app.name,
                "version": app.version,
                "api_endpoints": app.api_endpoints,
                "webhooks_supported": app.webhooks_supported,
                "documentation_url": app.documentation_url,
                "support_url": app.support_url
            }
        }
    
    def create_partner_application(self, organization_name: str, partner_type: PartnerType,
                                  contact_name: str, contact_email: str,
                                  business_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new partner application"""
        
        partner = Partner(
            organization_name=organization_name,
            partner_type=partner_type,
            status=PartnerStatus.PROSPECTIVE,
            primary_contact_name=contact_name,
            primary_contact_email=contact_email,
            **business_info if business_info else {}
        )
        
        self.partners[partner.partner_id] = partner
        
        logger.info(f"Partner application created for {organization_name}")
        
        return {
            "success": True,
            "partner_id": partner.partner_id,
            "status": partner.status.value,
            "message": "Partner application submitted successfully",
            "next_steps": [
                "Review and verification process will begin within 5 business days",
                "You will receive an email with additional requirements if needed",
                "Upon approval, you will receive partner onboarding materials"
            ]
        }
    
    def search_partners(self, partner_type: PartnerType = None, geographic_region: str = None,
                       specializations: List[str] = None, min_rating: float = None,
                       certification_required: bool = False) -> Dict[str, Any]:
        """Search for partners based on criteria"""
        
        partners = [p for p in self.partners.values() if p.status in [PartnerStatus.ACTIVE, PartnerStatus.CERTIFIED]]
        
        # Filter by partner type
        if partner_type:
            partners = [p for p in partners if p.partner_type == partner_type]
        
        # Filter by geographic coverage
        if geographic_region:
            partners = [
                p for p in partners
                if any(geographic_region.lower() in region.lower() for region in p.geographic_coverage)
            ]
        
        # Filter by specializations
        if specializations:
            partners = [
                p for p in partners
                if any(spec in p.specializations for spec in specializations)
            ]
        
        # Filter by minimum customer satisfaction
        if min_rating:
            partners = [p for p in partners if p.customer_satisfaction_score >= min_rating]
        
        # Filter by certification status
        if certification_required:
            partners = [p for p in partners if p.status == PartnerStatus.CERTIFIED]
        
        # Sort by customer satisfaction and success rate
        partners.sort(key=lambda x: (x.customer_satisfaction_score, x.project_success_rate), reverse=True)
        
        return {
            "total_partners": len(partners),
            "partners": [
                {
                    "partner_id": p.partner_id,
                    "organization_name": p.organization_name,
                    "partner_type": p.partner_type.value,
                    "partnership_tier": p.partnership_tier,
                    "geographic_coverage": p.geographic_coverage,
                    "specializations": p.specializations,
                    "services_offered": p.services_offered,
                    "customer_satisfaction_score": p.customer_satisfaction_score,
                    "project_success_rate": p.project_success_rate,
                    "response_time_hours": p.response_time_hours,
                    "certifications": p.certifications,
                    "website": p.website,
                    "status": p.status.value
                }
                for p in partners
            ]
        }
    
    def get_partner_details(self, partner_id: str) -> Dict[str, Any]:
        """Get detailed partner information"""
        
        if partner_id not in self.partners:
            return {
                "success": False,
                "error": "Partner not found",
                "error_code": "PARTNER_NOT_FOUND"
            }
        
        partner = self.partners[partner_id]
        
        return {
            "success": True,
            "partner": {
                "partner_id": partner.partner_id,
                "organization_name": partner.organization_name,
                "partner_type": partner.partner_type.value,
                "status": partner.status.value,
                "partnership_tier": partner.partnership_tier,
                "primary_contact_name": partner.primary_contact_name,
                "primary_contact_email": partner.primary_contact_email,
                "website": partner.website,
                "industry_focus": partner.industry_focus,
                "geographic_coverage": partner.geographic_coverage,
                "target_market": partner.target_market,
                "services_offered": partner.services_offered,
                "specializations": partner.specializations,
                "certifications": partner.certifications,
                "technical_expertise": partner.technical_expertise,
                "integration_capabilities": partner.integration_capabilities,
                "supported_technologies": partner.supported_technologies,
                "customer_satisfaction_score": partner.customer_satisfaction_score,
                "project_success_rate": partner.project_success_rate,
                "response_time_hours": partner.response_time_hours,
                "created_at": partner.created_at.isoformat(),
                "approved_at": partner.approved_at.isoformat() if partner.approved_at else None
            }
        }
    
    def submit_app_review(self, app_id: str, user_id: str, rating: int, title: str,
                         review_text: str, law_firm_name: str = None,
                         use_case: str = "", pros: List[str] = None, 
                         cons: List[str] = None) -> Dict[str, Any]:
        """Submit a review for an app"""
        
        if app_id not in self.marketplace_apps:
            return {
                "success": False,
                "error": "App not found",
                "error_code": "APP_NOT_FOUND"
            }
        
        if not (1 <= rating <= 5):
            return {
                "success": False,
                "error": "Rating must be between 1 and 5",
                "error_code": "INVALID_RATING"
            }
        
        review = AppReview(
            app_id=app_id,
            user_id=user_id,
            law_firm_name=law_firm_name,
            rating=rating,
            title=title,
            review_text=review_text,
            use_case=use_case,
            pros=pros or [],
            cons=cons or []
        )
        
        self.app_reviews[review.review_id] = review
        
        # Update app rating and review count
        app = self.marketplace_apps[app_id]
        total_rating_points = app.rating * app.review_count + rating
        app.review_count += 1
        app.rating = total_rating_points / app.review_count
        
        logger.info(f"Review submitted for app {app.name} - {rating} stars")
        
        return {
            "success": True,
            "review_id": review.review_id,
            "message": "Review submitted successfully",
            "updated_app_rating": round(app.rating, 2),
            "total_reviews": app.review_count
        }
    
    def get_developer_resources(self) -> Dict[str, Any]:
        """Get comprehensive developer resources and documentation"""
        
        return {
            "api_documentation": {
                "base_url": "https://api.legalmate.ai/v1",
                "authentication": "Bearer Token",
                "rate_limits": {
                    "free_tier": "1000 requests/day",
                    "pro_tier": "10000 requests/day",
                    "enterprise_tier": "unlimited"
                },
                "endpoints": [
                    {
                        "category": "Legal Research",
                        "endpoints": [
                            "GET /api/legal-research/search",
                            "POST /api/legal-research/analyze",
                            "GET /api/legal-research/cases/{id}"
                        ]
                    },
                    {
                        "category": "Document Generation",
                        "endpoints": [
                            "POST /api/documents/generate",
                            "GET /api/documents/templates",
                            "PUT /api/documents/customize"
                        ]
                    },
                    {
                        "category": "Contract Analysis",
                        "endpoints": [
                            "POST /api/contracts/analyze",
                            "POST /api/contracts/compare",
                            "GET /api/contracts/templates"
                        ]
                    }
                ]
            },
            "sdk_libraries": {
                "python": {
                    "package": "legalmate-api",
                    "installation": "pip install legalmate-api",
                    "documentation": "https://docs.legalmate.ai/python"
                },
                "javascript": {
                    "package": "@legalmate/api",
                    "installation": "npm install @legalmate/api",
                    "documentation": "https://docs.legalmate.ai/javascript"
                },
                "rest_api": {
                    "format": "REST/JSON",
                    "documentation": "https://docs.legalmate.ai/rest"
                }
            },
            "webhook_guide": {
                "supported_events": [
                    "document_generated",
                    "contract_analyzed",
                    "research_completed",
                    "workflow_finished"
                ],
                "setup_guide": "https://docs.legalmate.ai/webhooks",
                "security": "HMAC signature verification",
                "retry_policy": "Exponential backoff, max 5 retries"
            },
            "development_tools": {
                "api_playground": "https://playground.legalmate.ai",
                "postman_collection": "https://docs.legalmate.ai/postman",
                "code_samples": "https://github.com/legalmate-ai/code-samples",
                "community_forum": "https://community.legalmate.ai"
            },
            "app_submission_process": {
                "requirements": [
                    "Complete app metadata and description",
                    "Screenshots and demo video",
                    "Technical documentation",
                    "Security and compliance review",
                    "Testing and quality assurance"
                ],
                "review_process": [
                    "Automated security scan",
                    "Manual code review (if applicable)",
                    "Functional testing",
                    "Legal compliance review",
                    "Final approval and publication"
                ],
                "timeline": "5-10 business days for standard apps"
            },
            "partner_program": {
                "benefits": [
                    "Technical support and resources",
                    "Marketing collaboration",
                    "Revenue sharing opportunities",
                    "Early access to new features",
                    "Certification programs"
                ],
                "requirements": {
                    "technology_partner": "Proven technical expertise, customer references",
                    "integration_partner": "Successful integration projects, support capabilities",
                    "reseller_partner": "Sales experience, customer relationships, revenue commitments"
                },
                "application_process": "https://partner.legalmate.ai/apply"
            }
        }
    
    def get_marketplace_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get marketplace analytics and metrics"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # App statistics
        published_apps = [app for app in self.marketplace_apps.values() if app.status == AppStatus.PUBLISHED]
        total_installs = sum(app.install_count for app in published_apps)
        
        # Category distribution
        category_stats = {}
        for app in published_apps:
            category = app.category.value
            category_stats[category] = category_stats.get(category, 0) + 1
        
        # Pricing model distribution
        pricing_stats = {}
        for app in published_apps:
            pricing = app.pricing_model
            pricing_stats[pricing] = pricing_stats.get(pricing, 0) + 1
        
        # Partner statistics
        active_partners = [p for p in self.partners.values() if p.status in [PartnerStatus.ACTIVE, PartnerStatus.CERTIFIED]]
        partner_type_stats = {}
        for partner in active_partners:
            ptype = partner.partner_type.value
            partner_type_stats[ptype] = partner_type_stats.get(ptype, 0) + 1
        
        # Review statistics
        recent_reviews = [
            review for review in self.app_reviews.values()
            if review.created_at >= cutoff_date
        ]
        
        avg_rating = 0
        if recent_reviews:
            avg_rating = sum(review.rating for review in recent_reviews) / len(recent_reviews)
        
        return {
            "period_days": days,
            "marketplace_overview": {
                "total_published_apps": len(published_apps),
                "total_app_installs": total_installs,
                "average_app_rating": round(sum(app.rating for app in published_apps) / len(published_apps) if published_apps else 0, 2),
                "total_reviews": sum(app.review_count for app in published_apps)
            },
            "app_statistics": {
                "category_distribution": category_stats,
                "pricing_model_distribution": pricing_stats,
                "top_rated_apps": [
                    {
                        "name": app.name,
                        "rating": app.rating,
                        "review_count": app.review_count,
                        "installs": app.install_count
                    }
                    for app in sorted(published_apps, key=lambda x: (x.rating, x.review_count), reverse=True)[:5]
                ],
                "most_installed_apps": [
                    {
                        "name": app.name,
                        "installs": app.install_count,
                        "rating": app.rating,
                        "category": app.category.value
                    }
                    for app in sorted(published_apps, key=lambda x: x.install_count, reverse=True)[:5]
                ]
            },
            "partner_statistics": {
                "total_active_partners": len(active_partners),
                "partner_type_distribution": partner_type_stats,
                "average_partner_satisfaction": round(
                    sum(p.customer_satisfaction_score for p in active_partners) / len(active_partners) 
                    if active_partners else 0, 2
                ),
                "certified_partners": len([p for p in active_partners if p.status == PartnerStatus.CERTIFIED])
            },
            "engagement_metrics": {
                "recent_reviews_count": len(recent_reviews),
                "average_recent_rating": round(avg_rating, 2),
                "new_app_submissions": 3,  # Mock data
                "new_partner_applications": 2  # Mock data
            }
        }

# Global instance
marketplace_partnership_ecosystem = MarketplacePartnershipEcosystem()

def get_marketplace_ecosystem() -> MarketplacePartnershipEcosystem:
    """Get the global marketplace ecosystem instance"""
    return marketplace_partnership_ecosystem
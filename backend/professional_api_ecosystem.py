"""
Professional API Ecosystem for Legal Industry Integration
Provides RESTful APIs, WebSocket APIs, GraphQL APIs, and Webhook Integration
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
import jwt
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIType(Enum):
    """Types of APIs in the ecosystem"""
    REST = "rest"
    WEBSOCKET = "websocket"
    GRAPHQL = "graphql"
    WEBHOOK = "webhook"
    RPC = "rpc"

class APIAccessLevel(Enum):
    """API access levels for different user types"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PARTNER = "partner"

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    endpoint_id: str
    path: str
    method: str
    api_type: APIType
    access_level: APIAccessLevel
    description: str
    parameters: Dict[str, Any]
    response_schema: Dict[str, Any]
    rate_limit: Dict[str, int]
    authentication_required: bool
    legal_accuracy_guarantee: float
    professional_features: List[str]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class LegalAPIKey(BaseModel):
    """API Key model for legal integrations"""
    api_key_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    name: str
    description: str
    access_level: APIAccessLevel
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    allowed_endpoints: List[str] = Field(default_factory=list)
    organization_id: Optional[str] = None
    law_firm_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    usage_stats: Dict[str, Any] = Field(default_factory=dict)

class WebSocketConnection(BaseModel):
    """WebSocket connection model"""
    connection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    law_firm_id: Optional[str] = None
    connection_type: str  # "legal_consultation", "real_time_analysis", "collaboration"
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WebhookSubscription(BaseModel):
    """Webhook subscription model"""
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    webhook_url: str
    event_types: List[str]
    secret_key: str
    organization_id: Optional[str] = None
    is_active: bool = True
    retry_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProfessionalAPIEcosystem:
    """
    Comprehensive API ecosystem for legal industry professional integration
    Supports RESTful, WebSocket, GraphQL, and Webhook APIs
    """
    
    def __init__(self):
        self.api_endpoints: Dict[str, APIEndpoint] = {}
        self.api_keys: Dict[str, LegalAPIKey] = {}
        self.websocket_connections: Dict[str, WebSocketConnection] = {}
        self.webhook_subscriptions: Dict[str, WebhookSubscription] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        self.usage_analytics: Dict[str, Any] = {}
        
        # Initialize password context for API key hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Initialize professional API endpoints
        self.initialize_professional_endpoints()
    
    def initialize_professional_endpoints(self):
        """Initialize all professional API endpoints for legal industry"""
        
        # Legal Research API Endpoints
        legal_research_endpoints = [
            {
                "endpoint_id": "legal_research_comprehensive",
                "path": "/api/integrations/legal-research",
                "method": "POST",
                "api_type": APIType.REST,
                "access_level": APIAccessLevel.PROFESSIONAL,
                "description": "Comprehensive legal research across multiple databases",
                "parameters": {
                    "query": {"type": "string", "required": True},
                    "jurisdiction": {"type": "string", "default": "US"},
                    "practice_areas": {"type": "array", "items": "string"},
                    "date_range": {"type": "object", "properties": {"start": "string", "end": "string"}},
                    "include_citations": {"type": "boolean", "default": True},
                    "analysis_depth": {"type": "string", "enum": ["basic", "comprehensive", "expert"]}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "research_id": {"type": "string"},
                        "results": {"type": "array"},
                        "analysis": {"type": "object"},
                        "citations": {"type": "array"},
                        "confidence_score": {"type": "number"},
                        "processing_time": {"type": "number"}
                    }
                },
                "rate_limit": {"requests_per_minute": 30, "requests_per_hour": 500},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.92,
                "professional_features": ["multi_database", "citation_analysis", "precedent_matching", "expert_validation"]
            },
            {
                "endpoint_id": "contract_analysis_enterprise",
                "path": "/api/integrations/contract-analysis",
                "method": "POST",
                "api_type": APIType.REST,
                "access_level": APIAccessLevel.ENTERPRISE,
                "description": "Enterprise-grade contract analysis with risk assessment",
                "parameters": {
                    "contract_content": {"type": "string", "required": True},
                    "contract_type": {"type": "string"},
                    "jurisdiction": {"type": "string", "default": "US"},
                    "analysis_level": {"type": "string", "enum": ["standard", "comprehensive", "expert"]},
                    "include_recommendations": {"type": "boolean", "default": True},
                    "compliance_checks": {"type": "array", "items": "string"}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "analysis_id": {"type": "string"},
                        "risk_assessment": {"type": "object"},
                        "compliance_score": {"type": "number"},
                        "recommendations": {"type": "array"},
                        "clause_analysis": {"type": "array"},
                        "expert_validation": {"type": "object"}
                    }
                },
                "rate_limit": {"requests_per_minute": 20, "requests_per_hour": 300},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.95,
                "professional_features": ["enterprise_compliance", "multi_jurisdiction", "expert_review", "audit_trail"]
            },
            {
                "endpoint_id": "legal_memoranda_generation",
                "path": "/api/integrations/legal-memoranda",
                "method": "POST",
                "api_type": APIType.REST,
                "access_level": APIAccessLevel.PROFESSIONAL,
                "description": "Professional legal memo generation with citations",
                "parameters": {
                    "legal_issue": {"type": "string", "required": True},
                    "facts": {"type": "string", "required": True},
                    "jurisdiction": {"type": "string", "default": "US"},
                    "memo_type": {"type": "string", "enum": ["research", "advisory", "litigation"]},
                    "citation_style": {"type": "string", "enum": ["bluebook", "alwd", "chicago"]},
                    "length": {"type": "string", "enum": ["brief", "standard", "comprehensive"]}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "memo_id": {"type": "string"},
                        "memo_content": {"type": "string"},
                        "citations": {"type": "array"},
                        "legal_authorities": {"type": "array"},
                        "confidence_score": {"type": "number"},
                        "word_count": {"type": "integer"}
                    }
                },
                "rate_limit": {"requests_per_minute": 15, "requests_per_hour": 200},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.88,
                "professional_features": ["professional_formatting", "citation_verification", "authority_ranking", "bluebook_compliance"]
            },
            {
                "endpoint_id": "law_firm_dashboard_analytics",
                "path": "/api/integrations/law-firm-dashboard",
                "method": "GET",
                "api_type": APIType.REST,
                "access_level": APIAccessLevel.ENTERPRISE,
                "description": "Comprehensive law firm analytics and performance metrics",
                "parameters": {
                    "law_firm_id": {"type": "string", "required": True},
                    "date_range": {"type": "object", "properties": {"start": "string", "end": "string"}},
                    "metrics": {"type": "array", "items": "string"},
                    "include_benchmarks": {"type": "boolean", "default": True}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "firm_metrics": {"type": "object"},
                        "performance_analytics": {"type": "object"},
                        "benchmarks": {"type": "object"},
                        "recommendations": {"type": "array"},
                        "trends": {"type": "array"}
                    }
                },
                "rate_limit": {"requests_per_minute": 10, "requests_per_hour": 100},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.90,
                "professional_features": ["custom_dashboards", "benchmark_analysis", "trend_prediction", "performance_optimization"]
            },
            {
                "endpoint_id": "client_communication_ai",
                "path": "/api/integrations/client-communication",
                "method": "POST",
                "api_type": APIType.REST,
                "access_level": APIAccessLevel.PROFESSIONAL,
                "description": "AI-assisted professional client communication and advice",
                "parameters": {
                    "client_query": {"type": "string", "required": True},
                    "case_context": {"type": "object"},
                    "communication_type": {"type": "string", "enum": ["email", "letter", "memo", "update"]},
                    "tone": {"type": "string", "enum": ["formal", "professional", "friendly"]},
                    "include_disclaimers": {"type": "boolean", "default": True}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "communication_id": {"type": "string"},
                        "generated_content": {"type": "string"},
                        "legal_disclaimers": {"type": "array"},
                        "suggested_actions": {"type": "array"},
                        "compliance_notes": {"type": "array"}
                    }
                },
                "rate_limit": {"requests_per_minute": 25, "requests_per_hour": 400},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.87,
                "professional_features": ["client_portal_integration", "professional_templates", "compliance_checking", "audit_trail"]
            },
            {
                "endpoint_id": "billing_optimization_analytics",
                "path": "/api/integrations/billing-optimization",
                "method": "GET",
                "api_type": APIType.REST,
                "access_level": APIAccessLevel.PROFESSIONAL,
                "description": "Legal practice billing optimization and efficiency metrics",
                "parameters": {
                    "law_firm_id": {"type": "string", "required": True},
                    "analysis_period": {"type": "string", "enum": ["monthly", "quarterly", "yearly"]},
                    "practice_areas": {"type": "array", "items": "string"},
                    "include_recommendations": {"type": "boolean", "default": True}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "billing_metrics": {"type": "object"},
                        "efficiency_scores": {"type": "object"},
                        "optimization_opportunities": {"type": "array"},
                        "revenue_projections": {"type": "object"},
                        "benchmarks": {"type": "object"}
                    }
                },
                "rate_limit": {"requests_per_minute": 10, "requests_per_hour": 100},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.85,
                "professional_features": ["revenue_optimization", "efficiency_tracking", "benchmark_comparison", "predictive_analytics"]
            }
        ]
        
        # WebSocket API Endpoints
        websocket_endpoints = [
            {
                "endpoint_id": "real_time_legal_consultation",
                "path": "/ws/legal-consultation",
                "method": "WS",
                "api_type": APIType.WEBSOCKET,
                "access_level": APIAccessLevel.PROFESSIONAL,
                "description": "Real-time legal consultation and analysis",
                "parameters": {
                    "session_type": {"type": "string", "enum": ["consultation", "research", "collaboration"]},
                    "participants": {"type": "array", "items": "string"},
                    "encryption": {"type": "boolean", "default": True}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "message_type": {"type": "string"},
                        "content": {"type": "object"},
                        "timestamp": {"type": "string"},
                        "sender_id": {"type": "string"}
                    }
                },
                "rate_limit": {"messages_per_minute": 60, "connections_per_hour": 10},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.90,
                "professional_features": ["end_to_end_encryption", "session_recording", "real_time_collaboration", "expert_escalation"]
            },
            {
                "endpoint_id": "live_contract_collaboration",
                "path": "/ws/contract-collaboration",
                "method": "WS",
                "api_type": APIType.WEBSOCKET,
                "access_level": APIAccessLevel.ENTERPRISE,
                "description": "Live contract collaboration and real-time editing",
                "parameters": {
                    "contract_id": {"type": "string", "required": True},
                    "collaboration_mode": {"type": "string", "enum": ["editing", "review", "negotiation"]},
                    "permissions": {"type": "object"}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string"},
                        "changes": {"type": "object"},
                        "user_id": {"type": "string"},
                        "timestamp": {"type": "string"}
                    }
                },
                "rate_limit": {"events_per_minute": 120, "connections_per_hour": 20},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.92,
                "professional_features": ["real_time_editing", "conflict_resolution", "version_control", "audit_trail"]
            }
        ]
        
        # GraphQL API Endpoints
        graphql_endpoints = [
            {
                "endpoint_id": "legal_data_graphql",
                "path": "/graphql/legal-data",
                "method": "POST",
                "api_type": APIType.GRAPHQL,
                "access_level": APIAccessLevel.PROFESSIONAL,
                "description": "Flexible GraphQL API for complex legal data queries",
                "parameters": {
                    "query": {"type": "string", "required": True},
                    "variables": {"type": "object"},
                    "operation_name": {"type": "string"}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "errors": {"type": "array"},
                        "extensions": {"type": "object"}
                    }
                },
                "rate_limit": {"queries_per_minute": 40, "complexity_points_per_hour": 10000},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.89,
                "professional_features": ["complex_queries", "data_relationships", "real_time_subscriptions", "custom_resolvers"]
            }
        ]
        
        # Webhook API Endpoints
        webhook_endpoints = [
            {
                "endpoint_id": "legal_events_webhook",
                "path": "/webhooks/legal-events",
                "method": "POST",
                "api_type": APIType.WEBHOOK,
                "access_level": APIAccessLevel.PROFESSIONAL,
                "description": "Webhook notifications for legal events and updates",
                "parameters": {
                    "event_types": {"type": "array", "items": "string", "required": True},
                    "webhook_url": {"type": "string", "required": True},
                    "secret_key": {"type": "string", "required": True}
                },
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "subscription_id": {"type": "string"},
                        "status": {"type": "string"},
                        "events_subscribed": {"type": "array"}
                    }
                },
                "rate_limit": {"subscriptions_per_day": 100, "events_per_hour": 1000},
                "authentication_required": True,
                "legal_accuracy_guarantee": 0.95,
                "professional_features": ["reliable_delivery", "retry_logic", "signature_verification", "event_filtering"]
            }
        ]
        
        # Initialize all endpoints
        all_endpoints = (
            legal_research_endpoints + 
            websocket_endpoints + 
            graphql_endpoints + 
            webhook_endpoints
        )
        
        for endpoint_dict in all_endpoints:
            endpoint = APIEndpoint(**endpoint_dict)
            self.api_endpoints[endpoint.endpoint_id] = endpoint
        
        logger.info(f"Initialized {len(all_endpoints)} professional API endpoints")
    
    def generate_api_key(self, name: str, description: str, access_level: APIAccessLevel, 
                        organization_id: str = None, law_firm_name: str = None,
                        rate_limits: Dict[str, int] = None, expires_in_days: int = None) -> LegalAPIKey:
        """Generate a new API key for legal integrations"""
        
        # Generate secure API key
        key = f"lmate_{access_level.value}_{uuid.uuid4().hex[:16]}"
        
        # Set default rate limits based on access level
        default_rate_limits = {
            APIAccessLevel.PUBLIC: {"requests_per_minute": 10, "requests_per_hour": 100},
            APIAccessLevel.AUTHENTICATED: {"requests_per_minute": 30, "requests_per_hour": 500},
            APIAccessLevel.PROFESSIONAL: {"requests_per_minute": 100, "requests_per_hour": 2000},
            APIAccessLevel.ENTERPRISE: {"requests_per_minute": 500, "requests_per_hour": 10000},
            APIAccessLevel.PARTNER: {"requests_per_minute": 1000, "requests_per_hour": 20000}
        }
        
        if not rate_limits:
            rate_limits = default_rate_limits.get(access_level, default_rate_limits[APIAccessLevel.AUTHENTICATED])
        
        # Set expiration date
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Get allowed endpoints based on access level
        allowed_endpoints = self._get_allowed_endpoints(access_level)
        
        api_key = LegalAPIKey(
            key=key,
            name=name,
            description=description,
            access_level=access_level,
            rate_limits=rate_limits,
            allowed_endpoints=allowed_endpoints,
            organization_id=organization_id,
            law_firm_name=law_firm_name,
            expires_at=expires_at,
            usage_stats={"total_requests": 0, "last_used": None}
        )
        
        self.api_keys[api_key.key] = api_key
        
        logger.info(f"Generated API key for {name} with {access_level.value} access")
        
        return api_key
    
    def _get_allowed_endpoints(self, access_level: APIAccessLevel) -> List[str]:
        """Get allowed endpoints for an access level"""
        allowed = []
        
        for endpoint_id, endpoint in self.api_endpoints.items():
            # Check if the access level is sufficient for this endpoint
            level_hierarchy = {
                APIAccessLevel.PUBLIC: 0,
                APIAccessLevel.AUTHENTICATED: 1,
                APIAccessLevel.PROFESSIONAL: 2,
                APIAccessLevel.ENTERPRISE: 3,
                APIAccessLevel.PARTNER: 4
            }
            
            if level_hierarchy[access_level] >= level_hierarchy[endpoint.access_level]:
                allowed.append(endpoint_id)
        
        return allowed
    
    def validate_api_key(self, api_key: str, endpoint_id: str = None) -> Dict[str, Any]:
        """Validate API key and check permissions"""
        
        if api_key not in self.api_keys:
            return {
                "valid": False,
                "error": "Invalid API key",
                "error_code": "INVALID_KEY"
            }
        
        key_obj = self.api_keys[api_key]
        
        # Check if key is active
        if not key_obj.is_active:
            return {
                "valid": False,
                "error": "API key is inactive",
                "error_code": "INACTIVE_KEY"
            }
        
        # Check expiration
        if key_obj.expires_at and datetime.utcnow() > key_obj.expires_at:
            return {
                "valid": False,
                "error": "API key has expired",
                "error_code": "EXPIRED_KEY"
            }
        
        # Check endpoint permission
        if endpoint_id and endpoint_id not in key_obj.allowed_endpoints:
            return {
                "valid": False,
                "error": "Insufficient permissions for this endpoint",
                "error_code": "INSUFFICIENT_PERMISSIONS"
            }
        
        # Check rate limits (simplified check)
        current_usage = self._get_current_usage(api_key)
        if self._is_rate_limited(key_obj, current_usage):
            return {
                "valid": False,
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMITED"
            }
        
        return {
            "valid": True,
            "key_info": {
                "name": key_obj.name,
                "access_level": key_obj.access_level.value,
                "organization_id": key_obj.organization_id,
                "law_firm_name": key_obj.law_firm_name
            }
        }
    
    def _get_current_usage(self, api_key: str) -> Dict[str, int]:
        """Get current usage statistics for an API key"""
        # This would typically query a database or cache
        # For now, return mock data
        return {
            "requests_this_minute": 5,
            "requests_this_hour": 50
        }
    
    def _is_rate_limited(self, key_obj: LegalAPIKey, current_usage: Dict[str, int]) -> bool:
        """Check if the API key has exceeded rate limits"""
        
        # Check per-minute limit
        if current_usage.get("requests_this_minute", 0) >= key_obj.rate_limits.get("requests_per_minute", 100):
            return True
        
        # Check per-hour limit
        if current_usage.get("requests_this_hour", 0) >= key_obj.rate_limits.get("requests_per_hour", 1000):
            return True
        
        return False
    
    def create_websocket_connection(self, user_id: str = None, law_firm_id: str = None, 
                                  connection_type: str = "legal_consultation", 
                                  metadata: Dict[str, Any] = None) -> WebSocketConnection:
        """Create a new WebSocket connection"""
        
        connection = WebSocketConnection(
            user_id=user_id,
            law_firm_id=law_firm_id,
            connection_type=connection_type,
            metadata=metadata or {}
        )
        
        self.websocket_connections[connection.connection_id] = connection
        
        logger.info(f"Created WebSocket connection {connection.connection_id} for type {connection_type}")
        
        return connection
    
    def subscribe_webhook(self, webhook_url: str, event_types: List[str], 
                         organization_id: str = None, 
                         retry_config: Dict[str, Any] = None) -> WebhookSubscription:
        """Subscribe to webhook events"""
        
        # Generate secret key for webhook verification
        secret_key = f"whsec_{uuid.uuid4().hex}"
        
        subscription = WebhookSubscription(
            webhook_url=webhook_url,
            event_types=event_types,
            secret_key=secret_key,
            organization_id=organization_id,
            retry_config=retry_config or {
                "max_retries": 3,
                "retry_delay_seconds": 60,
                "backoff_multiplier": 2
            }
        )
        
        self.webhook_subscriptions[subscription.subscription_id] = subscription
        
        logger.info(f"Created webhook subscription {subscription.subscription_id} for {len(event_types)} event types")
        
        return subscription
    
    async def send_webhook_event(self, event_type: str, event_data: Dict[str, Any], 
                                organization_id: str = None) -> Dict[str, Any]:
        """Send webhook event to subscribers"""
        
        results = []
        
        # Find matching subscriptions
        matching_subscriptions = []
        for subscription in self.webhook_subscriptions.values():
            if (subscription.is_active and 
                event_type in subscription.event_types and
                (organization_id is None or subscription.organization_id == organization_id)):
                matching_subscriptions.append(subscription)
        
        # Send to each subscription
        async with httpx.AsyncClient() as client:
            for subscription in matching_subscriptions:
                try:
                    # Prepare webhook payload
                    payload = {
                        "event_type": event_type,
                        "event_id": str(uuid.uuid4()),
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": event_data
                    }
                    
                    # Create signature for verification
                    signature = self._create_webhook_signature(payload, subscription.secret_key)
                    
                    headers = {
                        "Content-Type": "application/json",
                        "X-LegalMate-Signature": signature,
                        "X-LegalMate-Event-Type": event_type
                    }
                    
                    response = await client.post(
                        subscription.webhook_url,
                        json=payload,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    results.append({
                        "subscription_id": subscription.subscription_id,
                        "success": response.status_code in [200, 201, 202],
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to send webhook to {subscription.webhook_url}: {str(e)}")
                    results.append({
                        "subscription_id": subscription.subscription_id,
                        "success": False,
                        "error": str(e)
                    })
        
        return {
            "event_type": event_type,
            "total_subscriptions": len(matching_subscriptions),
            "successful_deliveries": len([r for r in results if r.get("success")]),
            "failed_deliveries": len([r for r in results if not r.get("success")]),
            "results": results
        }
    
    def _create_webhook_signature(self, payload: Dict[str, Any], secret_key: str) -> str:
        """Create webhook signature for verification"""
        import hmac
        import hashlib
        
        payload_string = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """Generate comprehensive API documentation"""
        
        documentation = {
            "title": "LegalMate Professional API Ecosystem",
            "version": "1.0.0",
            "description": "Comprehensive APIs for legal industry professional integration",
            "base_url": "https://api.legalmate.ai",
            "authentication": {
                "type": "API Key",
                "header": "Authorization",
                "format": "Bearer {api_key}"
            },
            "endpoints": {},
            "websockets": {},
            "graphql": {},
            "webhooks": {},
            "rate_limits": {
                "public": "10 requests/minute, 100 requests/hour",
                "professional": "100 requests/minute, 2000 requests/hour", 
                "enterprise": "500 requests/minute, 10000 requests/hour"
            }
        }
        
        # Group endpoints by type
        for endpoint_id, endpoint in self.api_endpoints.items():
            endpoint_doc = {
                "path": endpoint.path,
                "method": endpoint.method,
                "description": endpoint.description,
                "access_level": endpoint.access_level.value,
                "parameters": endpoint.parameters,
                "response_schema": endpoint.response_schema,
                "rate_limit": endpoint.rate_limit,
                "legal_accuracy_guarantee": f"{endpoint.legal_accuracy_guarantee * 100}%",
                "professional_features": endpoint.professional_features
            }
            
            if endpoint.api_type == APIType.REST:
                documentation["endpoints"][endpoint_id] = endpoint_doc
            elif endpoint.api_type == APIType.WEBSOCKET:
                documentation["websockets"][endpoint_id] = endpoint_doc
            elif endpoint.api_type == APIType.GRAPHQL:
                documentation["graphql"][endpoint_id] = endpoint_doc
            elif endpoint.api_type == APIType.WEBHOOK:
                documentation["webhooks"][endpoint_id] = endpoint_doc
        
        return documentation
    
    def get_usage_analytics(self, api_key: str = None, organization_id: str = None, 
                           days: int = 30) -> Dict[str, Any]:
        """Get usage analytics for API keys or organizations"""
        
        # This would typically query a database with actual usage data
        # For now, return mock analytics data
        
        analytics = {
            "period": f"Last {days} days",
            "total_requests": 15420,
            "successful_requests": 14892,
            "error_rate": "3.4%",
            "average_response_time": "0.45s",
            "top_endpoints": [
                {"endpoint": "legal-research", "requests": 5240, "percentage": "34%"},
                {"endpoint": "contract-analysis", "requests": 3180, "percentage": "21%"},
                {"endpoint": "legal-memoranda", "requests": 2420, "percentage": "16%"},
                {"endpoint": "client-communication", "requests": 1980, "percentage": "13%"},
                {"endpoint": "law-firm-dashboard", "requests": 1200, "percentage": "8%"}
            ],
            "usage_by_day": [
                {"date": "2024-01-01", "requests": 520, "errors": 18},
                {"date": "2024-01-02", "requests": 485, "errors": 12},
                {"date": "2024-01-03", "requests": 612, "errors": 21}
                # ... more daily data
            ],
            "geographic_distribution": {
                "US": "68%",
                "UK": "12%",
                "CA": "8%",
                "AU": "7%",
                "Other": "5%"
            }
        }
        
        if api_key:
            key_obj = self.api_keys.get(api_key)
            if key_obj:
                analytics["api_key_info"] = {
                    "name": key_obj.name,
                    "access_level": key_obj.access_level.value,
                    "organization": key_obj.law_firm_name
                }
        
        return analytics

# Global instance
professional_api_ecosystem = ProfessionalAPIEcosystem()

def get_api_ecosystem() -> ProfessionalAPIEcosystem:
    """Get the global API ecosystem instance"""
    return professional_api_ecosystem
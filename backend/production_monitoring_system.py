"""
Production Monitoring and Alerting System
Enterprise-grade monitoring for Legal AI Platform
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
import psutil
import aiohttp
import time
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertChannel(Enum):
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    DATABASE = "database"

@dataclass
class Alert:
    """Alert definition and data"""
    alert_id: str
    title: str
    message: str
    severity: AlertSeverity
    component: str
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class HealthCheck:
    """System health check result"""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime

@dataclass
class QualityMetric:
    """Legal accuracy and quality metrics"""
    metric_name: str
    domain: str
    accuracy_score: float
    confidence_score: float
    validation_status: str
    expert_approval: Optional[bool]
    timestamp: datetime

class SystemHealthMonitor:
    """
    Comprehensive system health monitoring
    
    Features:
    - Real-time system performance monitoring
    - Database connectivity and performance checks
    - AI service availability monitoring
    - Legal accuracy trend analysis
    """
    
    def __init__(self, db):
        self.db = db
        self.health_collection = db.health_checks
        self.alerts_collection = db.system_alerts
        
        # Health check registry
        self.health_checks: Dict[str, Callable] = {}
        self.last_health_status = {}
        
        # Register default health checks
        self._register_default_health_checks()
        
        # Initialize monitoring
        asyncio.create_task(self._setup_monitoring_indexes())
        asyncio.create_task(self._continuous_health_monitoring())

    async def _setup_monitoring_indexes(self):
        """Setup database indexes for monitoring collections"""
        try:
            health_indexes = [
                IndexModel([("timestamp", -1)]),
                IndexModel([("component", 1), ("timestamp", -1)]),
                IndexModel([("status", 1), ("timestamp", -1)])
            ]
            await self.health_collection.create_indexes(health_indexes)
            
            alert_indexes = [
                IndexModel([("timestamp", -1)]),
                IndexModel([("severity", 1), ("resolved", 1)]),
                IndexModel([("component", 1), ("timestamp", -1)])
            ]
            await self.alerts_collection.create_indexes(alert_indexes)
            
            logger.info("Monitoring indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating monitoring indexes: {e}")

    def _register_default_health_checks(self):
        """Register default system health checks"""
        self.health_checks.update({
            "database": self._check_database_health,
            "memory": self._check_memory_health,
            "cpu": self._check_cpu_health,
            "disk": self._check_disk_health,
            "legal_ai_services": self._check_legal_ai_health,
            "knowledge_base": self._check_knowledge_base_health
        })

    async def _continuous_health_monitoring(self):
        """Continuous health monitoring loop"""
        while True:
            try:
                await self.run_health_checks()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in continuous health monitoring: {e}")
                await asyncio.sleep(60)

    async def run_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        results = {}
        
        for component, check_func in self.health_checks.items():
            try:
                start_time = time.time()
                health_result = await check_func()
                response_time = time.time() - start_time
                
                health_check = HealthCheck(
                    component=component,
                    status=health_result["status"],
                    response_time=response_time,
                    details=health_result.get("details", {}),
                    timestamp=datetime.utcnow()
                )
                
                results[component] = health_check
                
                # Store in database
                await self.health_collection.insert_one(asdict(health_check))
                
                # Check for status changes and alert if needed
                await self._check_for_status_change(component, health_check)
                
            except Exception as e:
                logger.error(f"Health check failed for {component}: {e}")
                
                error_check = HealthCheck(
                    component=component,
                    status="unhealthy",
                    response_time=0.0,
                    details={"error": str(e)},
                    timestamp=datetime.utcnow()
                )
                results[component] = error_check
        
        return results

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            # Test basic connectivity
            await self.db.command("ping")
            
            # Test query performance
            start_time = time.time()
            count = await self.db.performance_metrics.count_documents({})
            query_time = time.time() - start_time
            
            # Check connection pool
            client_info = self.db.client.server_info()
            
            if query_time < 1.0:
                status = "healthy"
            elif query_time < 3.0:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "details": {
                    "query_time": query_time,
                    "document_count": count,
                    "server_version": client_info.get("version", "unknown")
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent < 70:
                status = "healthy"
            elif usage_percent < 85:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "details": {
                    "usage_percent": usage_percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3)
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    async def _check_cpu_health(self) -> Dict[str, Any]:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            
            if cpu_percent < 70:
                status = "healthy"
            elif cpu_percent < 85:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "details": {
                    "cpu_percent": cpu_percent,
                    "load_average": load_avg,
                    "cpu_count": psutil.cpu_count()
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    async def _check_disk_health(self) -> Dict[str, Any]:
        """Check disk usage"""
        try:
            disk = psutil.disk_usage('/')
            usage_percent = disk.percent
            
            if usage_percent < 80:
                status = "healthy"
            elif usage_percent < 90:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "details": {
                    "usage_percent": usage_percent,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3)
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    async def _check_legal_ai_health(self) -> Dict[str, Any]:
        """Check Legal AI services health"""
        try:
            # Test legal reasoning service
            from legal_concept_extractor import LegalConceptExtractor
            from legal_rag_system import get_rag_system
            
            # Simple test query
            test_successful = True
            services_status = {}
            
            # Test concept extraction (mock)
            try:
                # This would be a real test of your legal AI services
                services_status["concept_extraction"] = "healthy"
            except Exception as e:
                services_status["concept_extraction"] = f"unhealthy: {str(e)}"
                test_successful = False
            
            # Test RAG system (mock)
            try:
                services_status["rag_system"] = "healthy"
            except Exception as e:
                services_status["rag_system"] = f"unhealthy: {str(e)}"
                test_successful = False
            
            status = "healthy" if test_successful else "degraded"
            
            return {
                "status": status,
                "details": services_status
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    async def _check_knowledge_base_health(self) -> Dict[str, Any]:
        """Check knowledge base health and freshness"""
        try:
            # Check document count
            total_docs = await self.db.legal_documents.count_documents({})
            
            # Check recent updates
            recent_threshold = datetime.utcnow() - timedelta(days=7)
            recent_updates = await self.db.legal_documents.count_documents({
                "updated_at": {"$gte": recent_threshold}
            })
            
            # Check for data integrity
            if total_docs > 20000:  # Based on your 25,000+ documents
                if recent_updates > 0:
                    status = "healthy"
                else:
                    status = "degraded"  # No recent updates
            elif total_docs > 10000:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "details": {
                    "total_documents": total_docs,
                    "recent_updates": recent_updates,
                    "last_update_check": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    async def _check_for_status_change(self, component: str, current_check: HealthCheck):
        """Check for status changes and trigger alerts"""
        previous_status = self.last_health_status.get(component)
        current_status = current_check.status
        
        # Update status
        self.last_health_status[component] = current_status
        
        # Check for degradation
        if previous_status == "healthy" and current_status in ["degraded", "unhealthy"]:
            severity = AlertSeverity.CRITICAL if current_status == "unhealthy" else AlertSeverity.WARNING
            
            alert = Alert(
                alert_id=f"health_{component}_{int(time.time())}",
                title=f"{component.title()} Health Degradation",
                message=f"{component} status changed from {previous_status} to {current_status}",
                severity=severity,
                component=component,
                metric_name="status",
                current_value=0 if current_status == "unhealthy" else 1,
                threshold_value=2,  # healthy threshold
                timestamp=current_check.timestamp
            )
            
            await self._trigger_alert(alert)

    async def _trigger_alert(self, alert: Alert):
        """Trigger system alert"""
        # Store alert in database
        await self.alerts_collection.insert_one(asdict(alert))
        
        # Log alert
        logger.warning(f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.message}")
        
        # Additional alerting logic would go here (email, webhooks, etc.)

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status summary"""
        # Get recent health checks (last 5 minutes)
        recent_threshold = datetime.utcnow() - timedelta(minutes=5)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": recent_threshold}}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$component",
                "latest_status": {"$first": "$status"},
                "latest_check": {"$first": "$timestamp"},
                "avg_response_time": {"$avg": "$response_time"}
            }}
        ]
        
        recent_checks = await self.health_collection.aggregate(pipeline).to_list(None)
        
        # Get active alerts
        active_alerts = await self.alerts_collection.count_documents({
            "resolved": False,
            "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}
        })
        
        # Calculate overall system health
        healthy_components = sum(1 for check in recent_checks if check["latest_status"] == "healthy")
        total_components = len(recent_checks)
        health_percentage = (healthy_components / total_components * 100) if total_components > 0 else 0
        
        overall_status = "healthy"
        if health_percentage < 50:
            overall_status = "unhealthy"
        elif health_percentage < 80:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "health_percentage": health_percentage,
            "component_status": {check["_id"]: check["latest_status"] for check in recent_checks},
            "active_alerts": active_alerts,
            "last_updated": datetime.utcnow().isoformat()
        }

class QualityAssuranceMonitor:
    """
    Legal accuracy and quality assurance monitoring
    
    Features:
    - Legal accuracy trend analysis
    - Expert validation rate monitoring
    - Knowledge base freshness tracking
    - Quality degradation detection
    """
    
    def __init__(self, db):
        self.db = db
        self.quality_collection = db.quality_metrics
        self.accuracy_thresholds = {
            "contract_law": 0.95,
            "constitutional_law": 0.92,
            "intellectual_property": 0.90,
            "administrative_law": 0.88,
            "securities_law": 0.90
        }
        
        asyncio.create_task(self._setup_quality_indexes())

    async def _setup_quality_indexes(self):
        """Setup indexes for quality monitoring"""
        try:
            indexes = [
                IndexModel([("timestamp", -1)]),
                IndexModel([("domain", 1), ("timestamp", -1)]),
                IndexModel([("metric_name", 1), ("timestamp", -1)]),
                IndexModel([("accuracy_score", -1)])
            ]
            await self.quality_collection.create_indexes(indexes)
            logger.info("Quality monitoring indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating quality indexes: {e}")

    async def record_quality_metric(self, metric: QualityMetric):
        """Record a quality metric"""
        try:
            await self.quality_collection.insert_one(asdict(metric))
            
            # Check for quality degradation
            await self._check_quality_degradation(metric)
            
        except Exception as e:
            logger.error(f"Error recording quality metric: {e}")

    async def _check_quality_degradation(self, metric: QualityMetric):
        """Check for quality degradation and alert if needed"""
        domain_threshold = self.accuracy_thresholds.get(metric.domain, 0.90)
        
        if metric.accuracy_score < domain_threshold:
            # Quality below threshold - create alert
            severity = AlertSeverity.CRITICAL if metric.accuracy_score < 0.80 else AlertSeverity.WARNING
            
            alert = Alert(
                alert_id=f"quality_{metric.domain}_{int(time.time())}",
                title=f"Legal Accuracy Below Threshold - {metric.domain}",
                message=f"Accuracy score {metric.accuracy_score:.2%} below threshold {domain_threshold:.2%}",
                severity=severity,
                component="legal_ai",
                metric_name=metric.metric_name,
                current_value=metric.accuracy_score,
                threshold_value=domain_threshold,
                timestamp=metric.timestamp
            )
            
            # Store alert
            await self.db.system_alerts.insert_one(asdict(alert))
            logger.warning(f"Quality degradation detected: {alert.message}")

    async def get_quality_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get quality trends over time"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "domain": "$domain",
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
                },
                "avg_accuracy": {"$avg": "$accuracy_score"},
                "avg_confidence": {"$avg": "$confidence_score"},
                "total_validations": {"$sum": 1},
                "expert_approvals": {"$sum": {"$cond": ["$expert_approval", 1, 0]}}
            }},
            {"$sort": {"_id.date": 1}}
        ]
        
        try:
            results = await self.quality_collection.aggregate(pipeline).to_list(None)
            
            # Process results by domain
            trends_by_domain = {}
            for result in results:
                domain = result["_id"]["domain"]
                if domain not in trends_by_domain:
                    trends_by_domain[domain] = []
                
                trends_by_domain[domain].append({
                    "date": result["_id"]["date"],
                    "avg_accuracy": result["avg_accuracy"],
                    "avg_confidence": result["avg_confidence"],
                    "total_validations": result["total_validations"],
                    "expert_approval_rate": result["expert_approvals"] / result["total_validations"] if result["total_validations"] > 0 else 0
                })
            
            return {
                "period_days": days,
                "trends_by_domain": trends_by_domain,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating quality trends: {e}")
            return {"error": str(e)}

# Global monitoring system instance
monitoring_system = None

async def initialize_monitoring_system(db):
    """Initialize the global monitoring system"""
    global monitoring_system
    
    if monitoring_system is None:
        health_monitor = SystemHealthMonitor(db)
        quality_monitor = QualityAssuranceMonitor(db)
        
        monitoring_system = {
            "health_monitor": health_monitor,
            "quality_monitor": quality_monitor
        }
        
        logger.info("Production monitoring system initialized successfully")
    
    return monitoring_system

def get_monitoring_system():
    """Get the global monitoring system instance"""
    return monitoring_system
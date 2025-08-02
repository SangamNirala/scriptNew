"""
Comprehensive Analytics System for Legal AI Platform
Enterprise-grade analytics with batch processing and performance monitoring
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
import logging
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LegalAIMetrics:
    """Legal AI performance metrics"""
    accuracy_by_domain: Dict[str, float]
    response_times: Dict[str, float]  
    user_satisfaction_scores: Dict[str, float]
    expert_validation_rates: Dict[str, float]
    knowledge_base_utilization: Dict[str, int]
    timestamp: datetime

@dataclass
class UsageAnalytics:
    """User behavior and usage patterns"""
    query_patterns: Dict[str, int]
    user_behavior: Dict[str, Any]
    session_analytics: Dict[str, Any]
    retention_metrics: Dict[str, float]
    feature_usage: Dict[str, int]
    timestamp: datetime

@dataclass
class SystemHealthMetrics:
    """System health and performance monitoring"""
    system_uptime: float
    query_throughput: int
    error_rates: Dict[str, float]
    resource_utilization: Dict[str, float]
    concurrent_users: int
    timestamp: datetime

class AnalyticsCollector:
    """
    Collects and processes analytics data for the Legal AI platform
    
    Features:
    - Legal AI performance tracking
    - Usage pattern analysis
    - System health monitoring
    - Batch processing with real-time upgrade capability
    """
    
    def __init__(self, db):
        self.db = db
        self.analytics_collection = db.analytics_data
        self.metrics_collection = db.performance_metrics
        self.user_sessions_collection = db.user_sessions
        
        # Analytics data storage
        self.current_metrics = defaultdict(dict)
        self.batch_data = defaultdict(list)
        
        # Initialize database indexes
        asyncio.create_task(self._setup_analytics_indexes())
        
    async def _setup_analytics_indexes(self):
        """Setup MongoDB indexes for analytics collections"""
        try:
            # Analytics data indexes
            analytics_indexes = [
                IndexModel([("timestamp", -1)]),
                IndexModel([("metric_type", 1), ("timestamp", -1)]),
                IndexModel([("date", 1), ("hour", 1)]),
                IndexModel([("user_id", 1), ("timestamp", -1)])
            ]
            await self.analytics_collection.create_indexes(analytics_indexes)
            
            # User sessions indexes
            session_indexes = [
                IndexModel([("session_id", 1), ("timestamp", -1)]),
                IndexModel([("user_id", 1), ("start_time", -1)]),
                IndexModel([("end_time", 1)], expireAfterSeconds=2592000)  # 30 days
            ]
            await self.user_sessions_collection.create_indexes(session_indexes)
            
            logger.info("Analytics indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating analytics indexes: {e}")

    async def track_legal_ai_performance(self, domain: str, query_type: str, 
                                       accuracy_score: float, response_time: float,
                                       user_satisfaction: Optional[float] = None,
                                       expert_validation: Optional[bool] = None):
        """Track Legal AI performance metrics"""
        metric_data = {
            "domain": domain,
            "query_type": query_type,
            "accuracy_score": accuracy_score,
            "response_time": response_time,
            "user_satisfaction": user_satisfaction,
            "expert_validation": expert_validation,
            "timestamp": datetime.utcnow()
        }
        
        # Add to batch for processing
        self.batch_data["legal_ai_performance"].append(metric_data)
        
        # Update current metrics for real-time access
        self.current_metrics["accuracy"][domain] = accuracy_score
        self.current_metrics["response_times"][query_type] = response_time
        
        if user_satisfaction:
            self.current_metrics["user_satisfaction"][domain] = user_satisfaction
        if expert_validation is not None:
            if "expert_validation" not in self.current_metrics:
                self.current_metrics["expert_validation"] = {}
            self.current_metrics["expert_validation"][domain] = expert_validation

    async def track_user_behavior(self, user_id: str, session_id: str, 
                                action: str, endpoint: str, 
                                duration: float = None,
                                additional_data: Dict = None):
        """Track user behavior and interaction patterns"""
        behavior_data = {
            "user_id": user_id,
            "session_id": session_id,
            "action": action,
            "endpoint": endpoint,
            "duration": duration,
            "additional_data": additional_data or {},
            "timestamp": datetime.utcnow()
        }
        
        # Add to batch for processing
        self.batch_data["user_behavior"].append(behavior_data)
        
        # Update session tracking
        await self._update_session_tracking(user_id, session_id, action, duration)

    async def track_knowledge_base_usage(self, document_id: str, query_type: str,
                                       user_id: str = None, relevance_score: float = None):
        """Track knowledge base utilization patterns"""
        usage_data = {
            "document_id": document_id,
            "query_type": query_type,
            "user_id": user_id,
            "relevance_score": relevance_score,
            "timestamp": datetime.utcnow()
        }
        
        # Add to batch for processing
        self.batch_data["knowledge_base_usage"].append(usage_data)
        
        # Update utilization metrics
        if "knowledge_base_utilization" not in self.current_metrics:
            self.current_metrics["knowledge_base_utilization"] = defaultdict(int)
        self.current_metrics["knowledge_base_utilization"][document_id] += 1

    async def track_system_health(self, query_throughput: int, error_count: int,
                                concurrent_users: int, resource_usage: Dict[str, float]):
        """Track system health and performance metrics"""
        health_data = {
            "query_throughput": query_throughput,
            "error_count": error_count,
            "concurrent_users": concurrent_users,
            "resource_usage": resource_usage,
            "timestamp": datetime.utcnow()
        }
        
        # Add to batch for processing
        self.batch_data["system_health"].append(health_data)
        
        # Update current health metrics
        self.current_metrics["system_health"] = {
            "query_throughput": query_throughput,
            "concurrent_users": concurrent_users,
            "resource_usage": resource_usage
        }

    async def _update_session_tracking(self, user_id: str, session_id: str, 
                                     action: str, duration: float = None):
        """Update user session tracking"""
        try:
            session_update = {
                "$set": {
                    "user_id": user_id,
                    "last_activity": datetime.utcnow()
                },
                "$inc": {"action_count": 1},
                "$push": {
                    "actions": {
                        "action": action,
                        "timestamp": datetime.utcnow(),
                        "duration": duration
                    }
                }
            }
            
            await self.user_sessions_collection.update_one(
                {"session_id": session_id},
                session_update,
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating session tracking: {e}")

    async def process_batch_analytics(self):
        """Process collected analytics data in batches"""
        logger.info("Starting batch analytics processing")
        
        try:
            # Process each type of analytics data
            for metric_type, data_list in self.batch_data.items():
                if data_list:
                    await self._process_metric_batch(metric_type, data_list)
                    
            # Clear batch data after processing
            self.batch_data.clear()
            
            logger.info("Batch analytics processing completed")
            
        except Exception as e:
            logger.error(f"Error in batch analytics processing: {e}")

    async def _process_metric_batch(self, metric_type: str, data_list: List[Dict]):
        """Process a specific batch of metrics"""
        try:
            # Add batch metadata
            processed_data = []
            for data in data_list:
                data["metric_type"] = metric_type
                data["batch_processed_at"] = datetime.utcnow()
                data["date"] = data["timestamp"].strftime("%Y-%m-%d")
                data["hour"] = data["timestamp"].hour
                processed_data.append(data)
            
            # Bulk insert for efficiency
            if processed_data:
                await self.analytics_collection.insert_many(processed_data)
                logger.info(f"Processed {len(processed_data)} {metric_type} metrics")
                
        except Exception as e:
            logger.error(f"Error processing {metric_type} batch: {e}")

    async def generate_performance_report(self, start_date: datetime, 
                                        end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive performance analytics report"""
        logger.info(f"Generating performance report from {start_date} to {end_date}")
        
        report = {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_days": (end_date - start_date).days
            },
            "legal_ai_performance": await self._analyze_legal_ai_performance(start_date, end_date),
            "usage_analytics": await self._analyze_usage_patterns(start_date, end_date),
            "system_performance": await self._analyze_system_performance(start_date, end_date),
            "user_engagement": await self._analyze_user_engagement(start_date, end_date),
            "knowledge_base_insights": await self._analyze_knowledge_base_usage(start_date, end_date),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report

    async def _analyze_legal_ai_performance(self, start_date: datetime, 
                                          end_date: datetime) -> Dict[str, Any]:
        """Analyze Legal AI performance metrics"""
        pipeline = [
            {"$match": {
                "metric_type": "legal_ai_performance",
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": "$domain",
                "avg_accuracy": {"$avg": "$accuracy_score"},
                "avg_response_time": {"$avg": "$response_time"},
                "total_queries": {"$sum": 1},
                "avg_user_satisfaction": {"$avg": "$user_satisfaction"},
                "expert_validation_rate": {
                    "$avg": {"$cond": ["$expert_validation", 1, 0]}
                }
            }},
            {"$sort": {"total_queries": -1}}
        ]
        
        try:
            results = await self.analytics_collection.aggregate(pipeline).to_list(None)
            
            # Calculate overall metrics
            if results:
                overall_accuracy = statistics.mean([r["avg_accuracy"] for r in results if r["avg_accuracy"]])
                overall_response_time = statistics.mean([r["avg_response_time"] for r in results if r["avg_response_time"]])
                total_queries = sum([r["total_queries"] for r in results])
            else:
                overall_accuracy = overall_response_time = total_queries = 0
            
            return {
                "by_domain": results,
                "overall_metrics": {
                    "average_accuracy": overall_accuracy,
                    "average_response_time": overall_response_time,
                    "total_queries": total_queries,
                    "performance_score": min(overall_accuracy * 100, 100) if overall_accuracy else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing legal AI performance: {e}")
            return {"error": str(e)}

    async def _analyze_usage_patterns(self, start_date: datetime, 
                                    end_date: datetime) -> Dict[str, Any]:
        """Analyze user usage patterns and behavior"""
        pipeline = [
            {"$match": {
                "metric_type": "user_behavior",
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": {
                    "action": "$action",
                    "endpoint": "$endpoint"
                },
                "total_actions": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"},
                "avg_duration": {"$avg": "$duration"}
            }},
            {"$addFields": {
                "unique_user_count": {"$size": "$unique_users"}
            }},
            {"$sort": {"total_actions": -1}}
        ]
        
        try:
            results = await self.analytics_collection.aggregate(pipeline).to_list(None)
            
            # Daily usage pattern
            daily_pipeline = [
                {"$match": {
                    "metric_type": "user_behavior",
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {
                    "_id": "$date",
                    "total_actions": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$addFields": {
                    "unique_user_count": {"$size": "$unique_users"}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            daily_results = await self.analytics_collection.aggregate(daily_pipeline).to_list(None)
            
            return {
                "action_patterns": results,
                "daily_usage": daily_results,
                "summary": {
                    "total_actions": sum([r["total_actions"] for r in results]),
                    "most_popular_action": results[0]["_id"]["action"] if results else "N/A",
                    "total_unique_users": len(set().union(*[r["unique_users"] for r in results])) if results else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
            return {"error": str(e)}

    async def _analyze_system_performance(self, start_date: datetime, 
                                        end_date: datetime) -> Dict[str, Any]:
        """Analyze system performance and health metrics"""
        pipeline = [
            {"$match": {
                "metric_type": "system_health",
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": "$date",
                "avg_throughput": {"$avg": "$query_throughput"},
                "avg_concurrent_users": {"$avg": "$concurrent_users"},
                "total_errors": {"$sum": "$error_count"},
                "avg_cpu_usage": {"$avg": "$resource_usage.cpu"},
                "avg_memory_usage": {"$avg": "$resource_usage.memory"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        try:
            results = await self.analytics_collection.aggregate(pipeline).to_list(None)
            
            if results:
                avg_throughput = statistics.mean([r["avg_throughput"] for r in results if r["avg_throughput"]])
                peak_concurrent_users = max([r["avg_concurrent_users"] for r in results if r["avg_concurrent_users"]])
                total_errors = sum([r["total_errors"] for r in results])
            else:
                avg_throughput = peak_concurrent_users = total_errors = 0
            
            return {
                "daily_performance": results,
                "summary": {
                    "average_throughput": avg_throughput,
                    "peak_concurrent_users": peak_concurrent_users,
                    "total_errors": total_errors,
                    "uptime_percentage": 99.5  # Placeholder - would be calculated from actual uptime data
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing system performance: {e}")
            return {"error": str(e)}

    async def _analyze_user_engagement(self, start_date: datetime, 
                                     end_date: datetime) -> Dict[str, Any]:
        """Analyze user engagement and retention metrics"""
        try:
            # Session analysis
            session_pipeline = [
                {"$match": {
                    "last_activity": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {
                    "_id": "$user_id",
                    "session_count": {"$sum": 1},
                    "total_actions": {"$sum": "$action_count"},
                    "last_session": {"$max": "$last_activity"}
                }}
            ]
            
            session_results = await self.user_sessions_collection.aggregate(session_pipeline).to_list(None)
            
            if session_results:
                avg_sessions_per_user = statistics.mean([r["session_count"] for r in session_results])
                avg_actions_per_user = statistics.mean([r["total_actions"] for r in session_results])
                total_active_users = len(session_results)
            else:
                avg_sessions_per_user = avg_actions_per_user = total_active_users = 0
            
            return {
                "user_engagement_summary": {
                    "total_active_users": total_active_users,
                    "avg_sessions_per_user": avg_sessions_per_user,
                    "avg_actions_per_user": avg_actions_per_user,
                    "engagement_score": min((avg_actions_per_user / 10) * 100, 100) if avg_actions_per_user else 0
                },
                "top_users": sorted(session_results, key=lambda x: x["total_actions"], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing user engagement: {e}")
            return {"error": str(e)}

    async def _analyze_knowledge_base_usage(self, start_date: datetime, 
                                          end_date: datetime) -> Dict[str, Any]:
        """Analyze knowledge base utilization patterns"""
        pipeline = [
            {"$match": {
                "metric_type": "knowledge_base_usage",
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": {
                    "document_id": "$document_id",
                    "query_type": "$query_type"
                },
                "access_count": {"$sum": 1},
                "avg_relevance": {"$avg": "$relevance_score"},
                "unique_users": {"$addToSet": "$user_id"}
            }},
            {"$addFields": {
                "unique_user_count": {"$size": "$unique_users"}
            }},
            {"$sort": {"access_count": -1}}
        ]
        
        try:
            results = await self.analytics_collection.aggregate(pipeline).to_list(None)
            
            # Query type distribution
            query_type_pipeline = [
                {"$match": {
                    "metric_type": "knowledge_base_usage",
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {
                    "_id": "$query_type",
                    "total_queries": {"$sum": 1},
                    "avg_relevance": {"$avg": "$relevance_score"}
                }},
                {"$sort": {"total_queries": -1}}
            ]
            
            query_type_results = await self.analytics_collection.aggregate(query_type_pipeline).to_list(None)
            
            return {
                "document_usage": results[:20],  # Top 20 documents
                "query_type_distribution": query_type_results,
                "summary": {
                    "total_document_accesses": sum([r["access_count"] for r in results]),
                    "most_accessed_document": results[0]["_id"]["document_id"] if results else "N/A",
                    "average_relevance_score": statistics.mean([r["avg_relevance"] for r in results if r["avg_relevance"]]) if results else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing knowledge base usage: {e}")
            return {"error": str(e)}

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": dict(self.current_metrics),
            "batch_queue_size": {k: len(v) for k, v in self.batch_data.items()}
        }

class AnalyticsScheduler:
    """
    Scheduler for batch analytics processing
    """
    
    def __init__(self, analytics_collector: AnalyticsCollector):
        self.collector = analytics_collector
        self.is_running = False
        
    async def start_scheduler(self, batch_interval_minutes: int = 60):
        """Start the analytics batch processing scheduler"""
        self.is_running = True
        logger.info(f"Starting analytics scheduler with {batch_interval_minutes} minute intervals")
        
        while self.is_running:
            try:
                await self.collector.process_batch_analytics()
                await asyncio.sleep(batch_interval_minutes * 60)  # Convert to seconds
            except Exception as e:
                logger.error(f"Error in analytics scheduler: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_scheduler(self):
        """Stop the analytics scheduler"""
        self.is_running = False
        logger.info("Analytics scheduler stopped")

# Global analytics system instance
analytics_system = None

async def initialize_analytics_system(db):
    """Initialize the global analytics system"""
    global analytics_system
    
    if analytics_system is None:
        collector = AnalyticsCollector(db)
        scheduler = AnalyticsScheduler(collector)
        
        analytics_system = {
            "collector": collector,
            "scheduler": scheduler
        }
        
        # Start the scheduler in the background
        asyncio.create_task(scheduler.start_scheduler(60))  # Process every hour
        
        logger.info("Analytics system initialized successfully")
    
    return analytics_system

def get_analytics_system():
    """Get the global analytics system instance"""
    return analytics_system
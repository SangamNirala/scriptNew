"""
Production Performance Optimization System
Enterprise-grade caching and optimization for Legal AI Platform
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel
import logging
from cachetools import TTLCache, LRUCache
import threading
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hit_count: int = 0
    miss_count: int = 0
    total_requests: int = 0
    total_response_time: float = 0.0
    cache_size: int = 0
    last_updated: datetime = None

    @property
    def hit_rate(self) -> float:
        return (self.hit_count / self.total_requests) if self.total_requests > 0 else 0.0

    @property
    def average_response_time(self) -> float:
        return (self.total_response_time / self.total_requests) if self.total_requests > 0 else 0.0

@dataclass
class QueryPerformanceMetrics:
    """Query performance tracking"""
    query_type: str
    execution_time: float
    cache_hit: bool
    complexity_score: float
    timestamp: datetime
    user_id: Optional[str] = None
    endpoint: Optional[str] = None

class HybridCacheSystem:
    """
    Hybrid caching system combining in-memory and MongoDB persistence
    
    Features:
    - In-memory cache for hot data (fast access)
    - MongoDB persistence for cache backup/recovery
    - Automatic cache warming and invalidation
    - Performance monitoring and metrics
    """
    
    def __init__(self, db, max_memory_cache_size: int = 1000, cache_ttl: int = 3600):
        self.db = db
        self.cache_collection = db.performance_cache
        
        # In-memory caches with different strategies
        self.memory_cache = TTLCache(maxsize=max_memory_cache_size, ttl=cache_ttl)
        self.lru_cache = LRUCache(maxsize=max_memory_cache_size // 2)
        
        # Cache metrics tracking
        self.metrics = CacheMetrics()
        self.query_metrics: List[QueryPerformanceMetrics] = []
        
        # Thread lock for thread safety
        self._lock = threading.RLock()
        
        # Initialize MongoDB indexes for cache performance
        asyncio.create_task(self._setup_cache_indexes())
        
    async def _setup_cache_indexes(self):
        """Setup MongoDB indexes for optimal cache performance"""
        try:
            indexes = [
                IndexModel([("cache_key", 1)], unique=True),
                IndexModel([("expires_at", 1)], expireAfterSeconds=0),
                IndexModel([("cache_type", 1), ("created_at", -1)]),
                IndexModel([("access_count", -1)]),
                IndexModel([("last_accessed", -1)])
            ]
            await self.cache_collection.create_indexes(indexes)
            logger.info("Cache indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating cache indexes: {e}")

    def _generate_cache_key(self, namespace: str, key: str, params: Dict = None) -> str:
        """Generate consistent cache key"""
        key_data = f"{namespace}:{key}"
        if params:
            # Sort params for consistent key generation
            sorted_params = json.dumps(params, sort_keys=True)
            key_data += f":{hashlib.md5(sorted_params.encode()).hexdigest()}"
        return key_data

    async def get(self, namespace: str, key: str, params: Dict = None) -> Optional[Dict]:
        """Get cached data with hybrid approach"""
        start_time = time.time()
        cache_key = self._generate_cache_key(namespace, key, params)
        
        with self._lock:
            # Try in-memory cache first (fastest)
            if cache_key in self.memory_cache:
                self.metrics.hit_count += 1
                self.metrics.total_requests += 1
                response_time = time.time() - start_time
                self.metrics.total_response_time += response_time
                
                logger.debug(f"Cache HIT (memory): {cache_key}")
                return self.memory_cache[cache_key]
            
            # Try LRU cache
            if cache_key in self.lru_cache:
                self.metrics.hit_count += 1
                self.metrics.total_requests += 1
                response_time = time.time() - start_time
                self.metrics.total_response_time += response_time
                
                # Promote to TTL cache
                self.memory_cache[cache_key] = self.lru_cache[cache_key]
                logger.debug(f"Cache HIT (LRU): {cache_key}")
                return self.lru_cache[cache_key]
        
        # Try MongoDB cache (persistent)
        try:
            cache_doc = await self.cache_collection.find_one({
                "cache_key": cache_key,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if cache_doc:
                cached_data = cache_doc["data"]
                
                # Update access metrics
                await self.cache_collection.update_one(
                    {"cache_key": cache_key},
                    {
                        "$inc": {"access_count": 1},
                        "$set": {"last_accessed": datetime.utcnow()}
                    }
                )
                
                # Promote to memory cache
                with self._lock:
                    self.memory_cache[cache_key] = cached_data
                    self.metrics.hit_count += 1
                    self.metrics.total_requests += 1
                    response_time = time.time() - start_time
                    self.metrics.total_response_time += response_time
                
                logger.debug(f"Cache HIT (MongoDB): {cache_key}")
                return cached_data
            
        except Exception as e:
            logger.error(f"Error retrieving from MongoDB cache: {e}")
        
        # Cache miss
        with self._lock:
            self.metrics.miss_count += 1
            self.metrics.total_requests += 1
            response_time = time.time() - start_time
            self.metrics.total_response_time += response_time
        
        logger.debug(f"Cache MISS: {cache_key}")
        return None

    async def set(self, namespace: str, key: str, data: Dict, ttl: int = 3600, params: Dict = None):
        """Set cached data with hybrid approach"""
        cache_key = self._generate_cache_key(namespace, key, params)
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        # Store in memory caches
        with self._lock:
            self.memory_cache[cache_key] = data
            self.lru_cache[cache_key] = data
            self.metrics.cache_size = len(self.memory_cache)
            self.metrics.last_updated = datetime.utcnow()
        
        # Store in MongoDB for persistence
        try:
            await self.cache_collection.update_one(
                {"cache_key": cache_key},
                {
                    "$set": {
                        "cache_key": cache_key,
                        "namespace": namespace,
                        "data": data,
                        "expires_at": expires_at,
                        "created_at": datetime.utcnow(),
                        "last_accessed": datetime.utcnow(),
                        "access_count": 0,
                        "cache_type": "hybrid"
                    }
                },
                upsert=True
            )
            logger.debug(f"Cache SET: {cache_key}")
        except Exception as e:
            logger.error(f"Error storing in MongoDB cache: {e}")

    async def invalidate(self, namespace: str, key: str = None, params: Dict = None):
        """Invalidate cache entries"""
        if key:
            cache_key = self._generate_cache_key(namespace, key, params)
            
            # Remove from memory caches
            with self._lock:
                self.memory_cache.pop(cache_key, None)
                self.lru_cache.pop(cache_key, None)
            
            # Remove from MongoDB
            try:
                await self.cache_collection.delete_one({"cache_key": cache_key})
                logger.info(f"Cache INVALIDATED: {cache_key}")
            except Exception as e:
                logger.error(f"Error invalidating cache: {e}")
        else:
            # Invalidate entire namespace
            with self._lock:
                # Remove from memory caches
                keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{namespace}:")]
                for k in keys_to_remove:
                    self.memory_cache.pop(k, None)
                    self.lru_cache.pop(k, None)
            
            # Remove from MongoDB
            try:
                result = await self.cache_collection.delete_many({"namespace": namespace})
                logger.info(f"Cache NAMESPACE INVALIDATED: {namespace}, {result.deleted_count} items removed")
            except Exception as e:
                logger.error(f"Error invalidating namespace cache: {e}")

    async def warm_cache(self, warmup_queries: List[Dict]):
        """Pre-populate cache with frequently accessed data"""
        logger.info(f"Starting cache warmup with {len(warmup_queries)} queries")
        
        for query in warmup_queries:
            try:
                # This would be implemented based on your specific query patterns
                # For now, we'll create a placeholder
                namespace = query.get("namespace", "warmup")
                key = query.get("key", "default")
                data = query.get("data", {})
                ttl = query.get("ttl", 7200)  # 2 hours for warmup data
                
                await self.set(namespace, key, data, ttl)
                
            except Exception as e:
                logger.error(f"Error in cache warmup: {e}")
        
        logger.info("Cache warmup completed")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current cache metrics"""
        with self._lock:
            metrics_dict = asdict(self.metrics)
            metrics_dict.update({
                "memory_cache_size": len(self.memory_cache),
                "lru_cache_size": len(self.lru_cache),
                "hit_rate_percentage": self.metrics.hit_rate * 100,
                "average_response_time_ms": self.metrics.average_response_time * 1000
            })
            return metrics_dict

class QueryOptimizer:
    """
    Advanced query optimization for legal AI operations
    
    Features:
    - Query complexity analysis
    - Intelligent batching
    - Resource allocation optimization
    - Performance monitoring
    """
    
    def __init__(self, cache_system: HybridCacheSystem, db):
        self.cache = cache_system
        self.db = db
        self.performance_metrics = []
        
    def analyze_query_complexity(self, query_type: str, params: Dict) -> float:
        """Analyze query complexity for resource allocation"""
        complexity_score = 1.0
        
        complexity_factors = {
            # Basic operations
            "user_profile": 0.5,
            "contract_template": 0.7,
            
            # Legal analysis operations  
            "contract_analysis": 2.0,
            "legal_reasoning": 3.0,
            "compliance_check": 2.5,
            "precedent_analysis": 4.0,
            
            # Complex AI operations
            "plain_english_conversion": 3.5,
            "concept_extraction": 4.5,
            "legal_research": 5.0,
            
            # Knowledge base operations
            "knowledge_base_query": 2.0,
            "bulk_document_processing": 8.0,
        }
        
        base_complexity = complexity_factors.get(query_type, 2.0)
        
        # Adjust based on parameters
        if params:
            # Text length factor
            if "content" in params or "text" in params:
                text_length = len(str(params.get("content", params.get("text", ""))))
                if text_length > 10000:
                    complexity_score *= 2.0
                elif text_length > 5000:
                    complexity_score *= 1.5
            
            # Jurisdiction complexity
            if params.get("jurisdiction") in ["EU", "MULTI"]:
                complexity_score *= 1.3
            
            # Analysis depth
            analysis_depth = params.get("analysis_depth", "standard")
            if analysis_depth == "comprehensive":
                complexity_score *= 2.0
            elif analysis_depth == "basic":
                complexity_score *= 0.7
        
        return base_complexity * complexity_score

    def cache_decorator(self, namespace: str, ttl: int = 3600):
        """Decorator for automatic caching of function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = f"{func.__name__}"
                cache_params = {
                    "args": str(args),
                    "kwargs": kwargs
                }
                
                # Check cache first
                cached_result = await self.cache.get(namespace, cache_key, cache_params)
                if cached_result:
                    return cached_result
                
                # Execute function and cache result
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Store in cache
                await self.cache.set(namespace, cache_key, result, ttl, cache_params)
                
                # Record metrics
                complexity = self.analyze_query_complexity(func.__name__, kwargs)
                metric = QueryPerformanceMetrics(
                    query_type=func.__name__,
                    execution_time=execution_time,
                    cache_hit=False,
                    complexity_score=complexity,
                    timestamp=datetime.utcnow(),
                    user_id=kwargs.get("user_id"),
                    endpoint=namespace
                )
                self.performance_metrics.append(metric)
                
                return result
            return wrapper
        return decorator

    async def optimize_batch_queries(self, queries: List[Dict]) -> List[Dict]:
        """Optimize batch queries for better performance"""
        # Group queries by type and complexity
        query_groups = {}
        for query in queries:
            query_type = query.get("type", "unknown")
            complexity = self.analyze_query_complexity(query_type, query.get("params", {}))
            
            group_key = f"{query_type}_{int(complexity)}"
            if group_key not in query_groups:
                query_groups[group_key] = []
            query_groups[group_key].append(query)
        
        # Execute queries in optimized order (simple first, then complex)
        results = []
        sorted_groups = sorted(query_groups.items(), key=lambda x: x[1][0].get("params", {}).get("complexity_score", 1.0))
        
        for group_key, group_queries in sorted_groups:
            # Process queries in parallel within the same complexity group
            group_results = await asyncio.gather(
                *[self._execute_single_query(query) for query in group_queries],
                return_exceptions=True
            )
            results.extend(group_results)
        
        return results

    async def _execute_single_query(self, query: Dict) -> Dict:
        """Execute a single optimized query"""
        # This would interface with your actual query execution system
        # Placeholder implementation
        start_time = time.time()
        
        # Simulate query execution
        await asyncio.sleep(0.1)  # Placeholder
        
        execution_time = time.time() - start_time
        
        return {
            "query_id": query.get("id", "unknown"),
            "result": {"status": "success", "data": {}},
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }

class PerformanceMonitor:
    """
    Real-time performance monitoring system
    """
    
    def __init__(self, db, cache_system: HybridCacheSystem):
        self.db = db
        self.cache = cache_system
        self.metrics_collection = db.performance_metrics
        
        # Initialize performance tracking
        asyncio.create_task(self._setup_metrics_indexes())
    
    async def _setup_metrics_indexes(self):
        """Setup indexes for performance metrics collection"""
        try:
            indexes = [
                IndexModel([("timestamp", -1)]),
                IndexModel([("query_type", 1), ("timestamp", -1)]),
                IndexModel([("endpoint", 1), ("timestamp", -1)]),
                IndexModel([("user_id", 1), ("timestamp", -1)]),
                IndexModel([("execution_time", -1)]),
                IndexModel([("complexity_score", -1)])
            ]
            await self.metrics_collection.create_indexes(indexes)
            logger.info("Performance metrics indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating metrics indexes: {e}")

    async def record_query_performance(self, metric: QueryPerformanceMetrics):
        """Record query performance metrics"""
        try:
            await self.metrics_collection.insert_one({
                "query_type": metric.query_type,
                "execution_time": metric.execution_time,
                "cache_hit": metric.cache_hit,
                "complexity_score": metric.complexity_score,
                "timestamp": metric.timestamp,
                "user_id": metric.user_id,
                "endpoint": metric.endpoint,
                "date": metric.timestamp.strftime("%Y-%m-%d"),
                "hour": metric.timestamp.hour
            })
        except Exception as e:
            logger.error(f"Error recording query performance: {e}")

    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": start_time}}},
            {"$group": {
                "_id": "$query_type",
                "avg_execution_time": {"$avg": "$execution_time"},
                "max_execution_time": {"$max": "$execution_time"},
                "min_execution_time": {"$min": "$execution_time"},
                "total_queries": {"$sum": 1},
                "cache_hits": {"$sum": {"$cond": ["$cache_hit", 1, 0]}},
                "avg_complexity": {"$avg": "$complexity_score"}
            }},
            {"$sort": {"total_queries": -1}}
        ]
        
        try:
            results = await self.metrics_collection.aggregate(pipeline).to_list(None)
            
            summary = {
                "time_period_hours": hours,
                "query_performance": results,
                "cache_metrics": self.cache.get_metrics(),
                "overall_stats": await self._get_overall_stats(start_time)
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {"error": str(e)}

    async def _get_overall_stats(self, start_time: datetime) -> Dict[str, Any]:
        """Get overall system performance statistics"""
        try:
            total_queries = await self.metrics_collection.count_documents({
                "timestamp": {"$gte": start_time}
            })
            
            avg_response_time = await self.metrics_collection.aggregate([
                {"$match": {"timestamp": {"$gte": start_time}}},
                {"$group": {"_id": None, "avg_time": {"$avg": "$execution_time"}}}
            ]).to_list(None)
            
            return {
                "total_queries": total_queries,
                "average_response_time": avg_response_time[0]["avg_time"] if avg_response_time else 0,
                "queries_per_hour": total_queries / 24 if total_queries > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating overall stats: {e}")
            return {}

# Global performance optimization system instance
performance_system = None

async def initialize_performance_system(db):
    """Initialize the global performance optimization system"""
    global performance_system
    
    if performance_system is None:
        cache_system = HybridCacheSystem(db)
        query_optimizer = QueryOptimizer(cache_system, db)
        performance_monitor = PerformanceMonitor(db, cache_system)
        
        performance_system = {
            "cache": cache_system,
            "optimizer": query_optimizer,
            "monitor": performance_monitor
        }
        
        logger.info("Performance optimization system initialized successfully")
    
    return performance_system

def get_performance_system():
    """Get the global performance system instance"""
    return performance_system
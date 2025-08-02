"""
Scalability and Concurrency Management System
Enterprise-grade scaling for 100+ concurrent users
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from collections import deque, defaultdict
import threading
import resource
import psutil
import weakref

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """User session management"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    active_requests: int = 0
    total_requests: int = 0
    session_data: Dict = None
    resource_usage: Dict[str, float] = None
    complexity_score: float = 1.0

@dataclass
class ResourceMetrics:
    """System resource utilization metrics"""
    cpu_percent: float
    memory_percent: float
    active_sessions: int
    concurrent_requests: int
    queue_length: int
    timestamp: datetime

@dataclass
class ScalingDecision:
    """Auto-scaling decision data"""
    action: str  # "scale_up", "scale_down", "maintain"
    reason: str
    current_load: float
    target_capacity: int
    timestamp: datetime

class ConcurrentUserManager:
    """
    Manages concurrent user sessions and resource allocation
    
    Features:
    - Session tracking and management
    - Resource allocation per user
    - Concurrent request limiting
    - Session persistence and recovery
    """
    
    def __init__(self, db, max_concurrent_users: int = 100, max_requests_per_user: int = 10):
        self.db = db
        self.max_concurrent_users = max_concurrent_users
        self.max_requests_per_user = max_requests_per_user
        
        # Session management
        self.active_sessions: Dict[str, UserSession] = {}
        self.session_queue = deque(maxlen=max_concurrent_users * 2)
        self.session_lock = threading.RLock()
        
        # Resource tracking
        self.resource_metrics = []
        self.sessions_collection = db.user_sessions
        
        # Request rate limiting
        self.user_request_counts = defaultdict(int)
        self.user_last_request = defaultdict(datetime)
        
        # Cleanup task
        asyncio.create_task(self._periodic_cleanup())

    async def create_session(self, user_id: str, session_data: Dict = None) -> Optional[UserSession]:
        """Create a new user session"""
        with self.session_lock:
            # Check if we're at capacity
            if len(self.active_sessions) >= self.max_concurrent_users:
                # Try to clean up inactive sessions first
                await self._cleanup_inactive_sessions()
                
                if len(self.active_sessions) >= self.max_concurrent_users:
                    logger.warning(f"Session creation denied - at capacity ({self.max_concurrent_users})")
                    return None
            
            session_id = f"{user_id}_{int(time.time() * 1000)}"
            
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                session_data=session_data or {},
                resource_usage={"cpu": 0.0, "memory": 0.0, "requests": 0}
            )
            
            self.active_sessions[session_id] = session
            self.session_queue.append(session_id)
            
            # Persist session to database
            await self._persist_session(session)
            
            logger.info(f"Session created: {session_id} for user {user_id}")
            return session

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get an active session"""
        with self.session_lock:
            session = self.active_sessions.get(session_id)
            if session:
                session.last_activity = datetime.utcnow()
                return session
            
            # Try to restore from database
            return await self._restore_session(session_id)

    async def update_session_activity(self, session_id: str, request_complexity: float = 1.0):
        """Update session activity and resource usage"""
        with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.last_activity = datetime.utcnow()
                session.active_requests += 1
                session.total_requests += 1
                session.complexity_score = (session.complexity_score + request_complexity) / 2
                
                # Update resource usage estimates
                session.resource_usage["requests"] = session.active_requests
                session.resource_usage["cpu"] = min(session.active_requests * 0.1, 1.0)
                session.resource_usage["memory"] = min(session.total_requests * 0.01, 0.5)
                
                return True
        return False

    async def complete_session_request(self, session_id: str):
        """Mark a session request as completed"""
        with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.active_requests = max(0, session.active_requests - 1)
                return True
        return False

    async def can_handle_request(self, session_id: str) -> bool:
        """Check if session can handle another request"""
        with self.session_lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            return session.active_requests < self.max_requests_per_user

    async def end_session(self, session_id: str):
        """End a user session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions.pop(session_id)
                
                # Update database
                await self.sessions_collection.update_one(
                    {"session_id": session_id},
                    {"$set": {
                        "ended_at": datetime.utcnow(),
                        "total_requests": session.total_requests,
                        "status": "ended"
                    }}
                )
                
                logger.info(f"Session ended: {session_id}")

    async def _cleanup_inactive_sessions(self, inactive_threshold_minutes: int = 30):
        """Clean up inactive sessions"""
        threshold = datetime.utcnow() - timedelta(minutes=inactive_threshold_minutes)
        inactive_sessions = []
        
        with self.session_lock:
            for session_id, session in list(self.active_sessions.items()):
                if session.last_activity < threshold and session.active_requests == 0:
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                await self.end_session(session_id)
        
        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")

    async def _periodic_cleanup(self):
        """Periodic cleanup task"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_inactive_sessions()
                await self._update_resource_metrics()
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")

    async def _persist_session(self, session: UserSession):
        """Persist session to database"""
        try:
            await self.sessions_collection.update_one(
                {"session_id": session.session_id},
                {"$set": {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "session_data": session.session_data,
                    "status": "active"
                }},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error persisting session: {e}")

    async def _restore_session(self, session_id: str) -> Optional[UserSession]:
        """Restore session from database"""
        try:
            session_doc = await self.sessions_collection.find_one({
                "session_id": session_id,
                "status": "active"
            })
            
            if session_doc:
                session = UserSession(
                    session_id=session_doc["session_id"],
                    user_id=session_doc["user_id"],
                    created_at=session_doc["created_at"],
                    last_activity=session_doc["last_activity"],
                    session_data=session_doc.get("session_data", {}),
                    resource_usage={"cpu": 0.0, "memory": 0.0, "requests": 0}
                )
                
                with self.session_lock:
                    self.active_sessions[session_id] = session
                
                return session
        except Exception as e:
            logger.error(f"Error restoring session: {e}")
        
        return None

    async def _update_resource_metrics(self):
        """Update system resource metrics"""
        try:
            # Get system resource usage
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Calculate session metrics
            with self.session_lock:
                active_sessions = len(self.active_sessions)
                concurrent_requests = sum(s.active_requests for s in self.active_sessions.values())
                queue_length = len(self.session_queue)
            
            metric = ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                active_sessions=active_sessions,
                concurrent_requests=concurrent_requests,
                queue_length=queue_length,
                timestamp=datetime.utcnow()
            )
            
            self.resource_metrics.append(metric)
            
            # Keep only last 100 metrics
            if len(self.resource_metrics) > 100:
                self.resource_metrics = self.resource_metrics[-100:]
                
        except Exception as e:
            logger.error(f"Error updating resource metrics: {e}")

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get current session statistics"""
        with self.session_lock:
            active_count = len(self.active_sessions)
            total_active_requests = sum(s.active_requests for s in self.active_sessions.values())
            avg_complexity = sum(s.complexity_score for s in self.active_sessions.values()) / active_count if active_count > 0 else 0
            
            return {
                "active_sessions": active_count,
                "max_concurrent_users": self.max_concurrent_users,
                "utilization_percentage": (active_count / self.max_concurrent_users) * 100,
                "total_active_requests": total_active_requests,
                "average_complexity_score": avg_complexity,
                "queue_length": len(self.session_queue)
            }

class LoadBalancer:
    """
    Intelligent load balancing for legal AI operations
    
    Features:
    - Request complexity-based routing
    - Dynamic resource allocation
    - Queue management for high-load periods
    - Auto-scaling triggers
    """
    
    def __init__(self, session_manager: ConcurrentUserManager):
        self.session_manager = session_manager
        self.request_queues = {
            "low_complexity": asyncio.Queue(maxsize=200),
            "medium_complexity": asyncio.Queue(maxsize=100),
            "high_complexity": asyncio.Queue(maxsize=50)
        }
        
        self.worker_pools = {
            "low_complexity": 10,
            "medium_complexity": 5,
            "high_complexity": 3
        }
        
        # Load balancing metrics
        self.request_counts = defaultdict(int)
        self.processing_times = defaultdict(list)
        
        # Start worker pools
        self._start_worker_pools()

    def _start_worker_pools(self):
        """Start worker pools for different complexity levels"""
        for complexity_level, worker_count in self.worker_pools.items():
            for i in range(worker_count):
                asyncio.create_task(self._worker(complexity_level, i))

    async def _worker(self, complexity_level: str, worker_id: int):
        """Worker for processing requests"""
        queue = self.request_queues[complexity_level]
        
        while True:
            try:
                # Get request from queue
                request_data = await queue.get()
                
                # Process request
                start_time = time.time()
                result = await self._process_request(request_data)
                processing_time = time.time() - start_time
                
                # Record metrics
                self.processing_times[complexity_level].append(processing_time)
                if len(self.processing_times[complexity_level]) > 100:
                    self.processing_times[complexity_level] = self.processing_times[complexity_level][-100:]
                
                # Complete request
                await self._complete_request(request_data, result)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker {worker_id} for {complexity_level}: {e}")
                await asyncio.sleep(1)

    async def submit_request(self, session_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a request for processing"""
        # Check if session can handle request
        if not await self.session_manager.can_handle_request(session_id):
            return {"error": "Session at maximum request capacity", "status": "rejected"}
        
        # Determine complexity level
        complexity = self._analyze_request_complexity(request_data)
        complexity_level = self._get_complexity_level(complexity)
        
        # Update session activity
        await self.session_manager.update_session_activity(session_id, complexity)
        
        # Add request metadata
        request_data.update({
            "session_id": session_id,
            "complexity": complexity,
            "complexity_level": complexity_level,
            "submitted_at": datetime.utcnow(),
            "request_id": f"{session_id}_{int(time.time() * 1000)}"
        })
        
        # Queue request
        try:
            queue = self.request_queues[complexity_level]
            await queue.put(request_data)
            
            self.request_counts[complexity_level] += 1
            
            return {
                "status": "queued",
                "request_id": request_data["request_id"],
                "complexity_level": complexity_level,
                "queue_position": queue.qsize()
            }
            
        except asyncio.QueueFull:
            await self.session_manager.complete_session_request(session_id)
            return {"error": f"Queue full for {complexity_level} requests", "status": "rejected"}

    def _analyze_request_complexity(self, request_data: Dict[str, Any]) -> float:
        """Analyze request complexity for load balancing"""
        base_complexity = 1.0
        
        # Request type complexity
        request_type = request_data.get("type", "unknown")
        type_complexity = {
            "contract_analysis": 3.0,
            "legal_reasoning": 4.0,
            "compliance_check": 2.5,
            "precedent_analysis": 5.0,
            "plain_english_conversion": 3.5,
            "concept_extraction": 4.0,
            "legal_research": 6.0,
            "knowledge_base_query": 2.0
        }.get(request_type, 2.0)
        
        # Content size factor
        content_length = len(str(request_data.get("content", "")))
        size_factor = 1.0
        if content_length > 10000:
            size_factor = 3.0
        elif content_length > 5000:
            size_factor = 2.0
        elif content_length > 1000:
            size_factor = 1.5
        
        # Jurisdiction complexity
        jurisdiction = request_data.get("jurisdiction", "US")
        jurisdiction_factor = 1.5 if jurisdiction in ["EU", "MULTI"] else 1.0
        
        return base_complexity * type_complexity * size_factor * jurisdiction_factor

    def _get_complexity_level(self, complexity_score: float) -> str:
        """Map complexity score to processing level"""
        if complexity_score < 3.0:
            return "low_complexity"
        elif complexity_score < 8.0:
            return "medium_complexity"
        else:
            return "high_complexity"

    async def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request (placeholder for actual processing logic)"""
        # This would interface with your actual legal AI processing system
        # For now, simulate processing time based on complexity
        complexity = request_data.get("complexity", 1.0)
        processing_time = min(complexity * 0.5, 5.0)  # Max 5 seconds
        
        await asyncio.sleep(processing_time)
        
        return {
            "request_id": request_data["request_id"],
            "status": "completed",
            "result": {"processed": True, "complexity": complexity},
            "processing_time": processing_time
        }

    async def _complete_request(self, request_data: Dict[str, Any], result: Dict[str, Any]):
        """Complete request processing"""
        session_id = request_data["session_id"]
        await self.session_manager.complete_session_request(session_id)
        
        # Store result or notify client
        logger.info(f"Completed request {request_data['request_id']} for session {session_id}")

    def get_load_statistics(self) -> Dict[str, Any]:
        """Get load balancing statistics"""
        stats = {}
        
        for complexity_level in self.request_queues:
            queue = self.request_queues[complexity_level]
            processing_times = self.processing_times[complexity_level]
            
            stats[complexity_level] = {
                "queue_size": queue.qsize(),
                "total_requests": self.request_counts[complexity_level],
                "worker_count": self.worker_pools[complexity_level],
                "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
                "max_processing_time": max(processing_times) if processing_times else 0
            }
        
        return stats

class AutoScaler:
    """
    Auto-scaling system for dynamic resource management
    
    Features:
    - CPU and memory-based scaling
    - Queue length monitoring
    - Predictive scaling based on usage patterns
    - Scaling decision logging
    """
    
    def __init__(self, session_manager: ConcurrentUserManager, load_balancer: LoadBalancer):
        self.session_manager = session_manager
        self.load_balancer = load_balancer
        self.scaling_decisions = []
        
        # Scaling thresholds
        self.cpu_scale_up_threshold = 75.0
        self.cpu_scale_down_threshold = 30.0
        self.memory_scale_up_threshold = 80.0
        self.queue_scale_up_threshold = 20
        
        # Start monitoring
        asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Main monitoring and scaling loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._evaluate_scaling()
            except Exception as e:
                logger.error(f"Error in auto-scaling monitoring: {e}")

    async def _evaluate_scaling(self):
        """Evaluate if scaling action is needed"""
        # Get current metrics
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        session_stats = self.session_manager.get_session_statistics()
        load_stats = self.load_balancer.get_load_statistics()
        
        # Calculate total queue length
        total_queue_length = sum(stats["queue_size"] for stats in load_stats.values())
        
        # Determine scaling action
        scaling_decision = self._make_scaling_decision(
            cpu_percent, memory_percent, session_stats, total_queue_length
        )
        
        if scaling_decision.action != "maintain":
            await self._execute_scaling_decision(scaling_decision)
            self.scaling_decisions.append(scaling_decision)
            
            # Keep only last 50 decisions
            if len(self.scaling_decisions) > 50:
                self.scaling_decisions = self.scaling_decisions[-50:]

    def _make_scaling_decision(self, cpu_percent: float, memory_percent: float, 
                             session_stats: Dict, queue_length: int) -> ScalingDecision:
        """Make scaling decision based on current metrics"""
        utilization = session_stats["utilization_percentage"]
        
        # Scale up conditions
        if (cpu_percent > self.cpu_scale_up_threshold or 
            memory_percent > self.memory_scale_up_threshold or 
            queue_length > self.queue_scale_up_threshold or
            utilization > 80):
            
            reason = f"CPU: {cpu_percent}%, Memory: {memory_percent}%, Queue: {queue_length}, Utilization: {utilization}%"
            return ScalingDecision(
                action="scale_up",
                reason=reason,
                current_load=max(cpu_percent, memory_percent, utilization),
                target_capacity=min(self.session_manager.max_concurrent_users + 20, 200),
                timestamp=datetime.utcnow()
            )
        
        # Scale down conditions
        elif (cpu_percent < self.cpu_scale_down_threshold and 
              memory_percent < 50 and 
              queue_length == 0 and 
              utilization < 40):
            
            reason = f"Low resource usage - CPU: {cpu_percent}%, Memory: {memory_percent}%, Utilization: {utilization}%"
            return ScalingDecision(
                action="scale_down",
                reason=reason,
                current_load=max(cpu_percent, memory_percent, utilization),
                target_capacity=max(self.session_manager.max_concurrent_users - 10, 50),
                timestamp=datetime.utcnow()
            )
        
        # Maintain current capacity
        else:
            return ScalingDecision(
                action="maintain",
                reason="Metrics within acceptable ranges",
                current_load=max(cpu_percent, memory_percent, utilization),
                target_capacity=self.session_manager.max_concurrent_users,
                timestamp=datetime.utcnow()
            )

    async def _execute_scaling_decision(self, decision: ScalingDecision):
        """Execute scaling decision"""
        logger.info(f"Scaling decision: {decision.action} - {decision.reason}")
        
        if decision.action == "scale_up":
            # Increase capacity
            self.session_manager.max_concurrent_users = decision.target_capacity
            
            # Add more workers to load balancer
            for complexity_level in self.load_balancer.worker_pools:
                additional_workers = 2
                for i in range(additional_workers):
                    asyncio.create_task(self.load_balancer._worker(
                        complexity_level, 
                        self.load_balancer.worker_pools[complexity_level] + i
                    ))
                self.load_balancer.worker_pools[complexity_level] += additional_workers
        
        elif decision.action == "scale_down":
            # Decrease capacity (gracefully)
            self.session_manager.max_concurrent_users = decision.target_capacity
            
            # Note: Worker reduction would require more complex implementation
            # For now, just log the decision
            logger.info(f"Scaling down to {decision.target_capacity} concurrent users")

    def get_scaling_history(self) -> List[Dict[str, Any]]:
        """Get scaling decision history"""
        return [asdict(decision) for decision in self.scaling_decisions[-20:]]

# Global scalability system instance
scalability_system = None

async def initialize_scalability_system(db, max_concurrent_users: int = 100):
    """Initialize the global scalability system"""
    global scalability_system
    
    if scalability_system is None:
        session_manager = ConcurrentUserManager(db, max_concurrent_users)
        load_balancer = LoadBalancer(session_manager)
        auto_scaler = AutoScaler(session_manager, load_balancer)
        
        scalability_system = {
            "session_manager": session_manager,
            "load_balancer": load_balancer,
            "auto_scaler": auto_scaler
        }
        
        logger.info(f"Scalability system initialized for {max_concurrent_users} concurrent users")
    
    return scalability_system

def get_scalability_system():
    """Get the global scalability system instance"""
    return scalability_system
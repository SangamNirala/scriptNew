"""
Workflow Metrics - Phase 3.3 Component
Performance analytics and reporting system for the Enhanced Workflow Manager.
Tracks workflow performance, template effectiveness, and system optimization metrics.
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

@dataclass
class WorkflowPerformanceMetrics:
    """Performance metrics for individual workflow execution"""
    workflow_id: str
    execution_time: float
    steps_completed: int
    success_rate: float
    template_effectiveness: float
    quality_score: float
    video_type: str
    duration: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass 
class SystemPerformanceMetrics:
    """System-wide performance metrics"""
    total_workflows: int
    success_rate: float
    average_execution_time: float
    template_selection_accuracy: float
    quality_improvement_ratio: float
    peak_performance_score: float
    system_load: float
    error_rate: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class WorkflowMetrics:
    """
    Comprehensive metrics collection and analysis system for Enhanced Workflow.
    Provides performance analytics, template effectiveness tracking, and optimization insights.
    """
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        # Performance tracking data structures
        self.workflow_history: deque = deque(maxlen=max_history_size)
        self.system_metrics_history: deque = deque(maxlen=100)  # Keep last 100 system snapshots
        
        # Real-time metrics
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.template_performance: defaultdict = defaultdict(list)
        self.video_type_performance: defaultdict = defaultdict(list)
        self.duration_performance: defaultdict = defaultdict(list)
        
        # Analytics cache
        self.cached_analytics: Dict[str, Any] = {}
        self.cache_expiry: datetime = datetime.utcnow()
        self.cache_duration = timedelta(minutes=15)  # Cache analytics for 15 minutes
        
        # Performance benchmarks
        self.benchmarks = {
            "execution_time": {
                "excellent": 60.0,    # < 1 minute
                "good": 120.0,        # < 2 minutes  
                "acceptable": 300.0,  # < 5 minutes
                "poor": 600.0         # < 10 minutes
            },
            "success_rate": {
                "excellent": 0.95,
                "good": 0.90,
                "acceptable": 0.80,
                "poor": 0.70
            },
            "quality_score": {
                "excellent": 0.90,
                "good": 0.80,
                "acceptable": 0.70,
                "poor": 0.60
            }
        }
        
        logger.info("Workflow Metrics system initialized")

    async def record_workflow_start(self, workflow_id: str, workflow_config: Dict[str, Any]) -> None:
        """Record the start of a workflow execution"""
        try:
            self.active_workflows[workflow_id] = {
                "start_time": datetime.utcnow(),
                "config": workflow_config,
                "steps_completed": [],
                "current_step": None,
                "step_times": {}
            }
            
            logger.info(f"Recorded workflow start: {workflow_id}")
        except Exception as e:
            logger.error(f"Failed to record workflow start: {str(e)}")

    async def record_workflow_step(self, workflow_id: str, step_name: str, 
                                 step_duration: float, success: bool) -> None:
        """Record completion of a workflow step"""
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow["steps_completed"].append(step_name)
                workflow["step_times"][step_name] = {
                    "duration": step_duration,
                    "success": success,
                    "timestamp": datetime.utcnow()
                }
                workflow["current_step"] = step_name
                
                logger.debug(f"Recorded step '{step_name}' for workflow {workflow_id}")
        except Exception as e:
            logger.error(f"Failed to record workflow step: {str(e)}")

    async def record_workflow_completion(self, workflow_id: str, result: Any) -> None:
        """Record completion of a workflow with final results"""
        try:
            if workflow_id not in self.active_workflows:
                logger.warning(f"Workflow {workflow_id} not found in active workflows")
                return
            
            workflow = self.active_workflows[workflow_id]
            end_time = datetime.utcnow()
            execution_time = (end_time - workflow["start_time"]).total_seconds()
            
            # Create performance metrics record
            metrics = WorkflowPerformanceMetrics(
                workflow_id=workflow_id,
                execution_time=execution_time,
                steps_completed=len(workflow["steps_completed"]),
                success_rate=1.0 if result.status.value == "completed" else 0.0,
                template_effectiveness=self._extract_template_effectiveness(result),
                quality_score=self._extract_quality_score(result), 
                video_type=workflow["config"].get("video_type", "unknown"),
                duration=workflow["config"].get("duration", "unknown"),
                timestamp=end_time
            )
            
            # Store in history
            self.workflow_history.append(metrics)
            
            # Update performance tracking by category
            self._update_category_performance(metrics)
            
            # Clean up active workflow
            del self.active_workflows[workflow_id]
            
            # Invalidate analytics cache
            self._invalidate_cache()
            
            logger.info(f"Recorded workflow completion: {workflow_id} "
                       f"(execution_time: {execution_time:.2f}s, "
                       f"success: {metrics.success_rate > 0})")
            
        except Exception as e:
            logger.error(f"Failed to record workflow completion: {str(e)}")

    async def get_performance_analytics(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        Get comprehensive performance analytics for specified time range.
        
        Args:
            time_range: Time range for analytics ("1h", "24h", "7d", "30d", "all")
            
        Returns:
            Dictionary containing detailed performance analytics
        """
        try:
            # Check cache first
            cache_key = f"analytics_{time_range}"
            if (self.cached_analytics.get(cache_key) and 
                datetime.utcnow() < self.cache_expiry):
                return self.cached_analytics[cache_key]
            
            # Filter workflows by time range
            filtered_workflows = self._filter_workflows_by_time(time_range)
            
            if not filtered_workflows:
                return {"message": "No workflow data available for specified time range"}
            
            # Calculate comprehensive analytics
            analytics = {
                "overview": await self._calculate_overview_metrics(filtered_workflows),
                "performance_trends": await self._calculate_performance_trends(filtered_workflows),
                "template_analytics": await self._calculate_template_analytics(filtered_workflows),
                "video_type_analytics": await self._calculate_video_type_analytics(filtered_workflows),
                "duration_analytics": await self._calculate_duration_analytics(filtered_workflows),
                "quality_metrics": await self._calculate_quality_metrics(filtered_workflows),
                "optimization_insights": await self._generate_optimization_insights(filtered_workflows),
                "system_health": await self._assess_system_health(filtered_workflows)
            }
            
            # Cache results
            self.cached_analytics[cache_key] = analytics
            self.cache_expiry = datetime.utcnow() + self.cache_duration
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate performance analytics: {str(e)}")
            return {"error": "Failed to generate analytics"}

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        try:
            current_time = datetime.utcnow()
            
            # Active workflows
            active_count = len(self.active_workflows)
            
            # Recent performance (last hour)
            recent_workflows = [w for w in self.workflow_history 
                              if (current_time - w.timestamp).total_seconds() < 3600]
            
            # Calculate real-time metrics
            metrics = {
                "active_workflows": active_count,
                "recent_completions": len(recent_workflows),
                "average_execution_time": statistics.mean([w.execution_time for w in recent_workflows]) if recent_workflows else 0,
                "success_rate": statistics.mean([w.success_rate for w in recent_workflows]) if recent_workflows else 0,
                "average_quality_score": statistics.mean([w.quality_score for w in recent_workflows]) if recent_workflows else 0,
                "system_load": self._calculate_system_load(),
                "performance_status": self._assess_performance_status(recent_workflows),
                "timestamp": current_time
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {str(e)}")
            return {"error": "Failed to get real-time metrics"}

    async def get_template_effectiveness_report(self) -> Dict[str, Any]:
        """Generate comprehensive template effectiveness report"""
        try:
            # Group workflows by template type
            template_groups = defaultdict(list)
            
            for workflow in self.workflow_history:
                template_key = f"{workflow.duration}_{workflow.video_type}"
                template_groups[template_key].append(workflow)
            
            # Calculate effectiveness for each template
            template_report = {}
            
            for template_key, workflows in template_groups.items():
                if len(workflows) < 2:  # Skip templates with insufficient data
                    continue
                
                effectiveness_scores = [w.template_effectiveness for w in workflows]
                quality_scores = [w.quality_score for w in workflows]
                execution_times = [w.execution_time for w in workflows]
                success_rates = [w.success_rate for w in workflows]
                
                template_report[template_key] = {
                    "sample_size": len(workflows),
                    "effectiveness": {
                        "average": statistics.mean(effectiveness_scores),
                        "median": statistics.median(effectiveness_scores),
                        "std_dev": statistics.stdev(effectiveness_scores) if len(effectiveness_scores) > 1 else 0,
                        "trend": self._calculate_trend(effectiveness_scores)
                    },
                    "quality": {
                        "average": statistics.mean(quality_scores),
                        "median": statistics.median(quality_scores),
                        "improvement_ratio": max(quality_scores) / min(quality_scores) if min(quality_scores) > 0 else 1
                    },
                    "performance": {
                        "average_time": statistics.mean(execution_times),
                        "success_rate": statistics.mean(success_rates),
                        "reliability_score": self._calculate_reliability_score(workflows)
                    },
                    "recommendation": self._generate_template_recommendation(workflows)
                }
            
            # Overall template system performance
            overall_metrics = {
                "total_templates_analyzed": len(template_report),
                "best_performing_template": max(template_report.keys(), 
                                              key=lambda k: template_report[k]["effectiveness"]["average"]) if template_report else None,
                "worst_performing_template": min(template_report.keys(),
                                               key=lambda k: template_report[k]["effectiveness"]["average"]) if template_report else None,
                "system_effectiveness": statistics.mean([t["effectiveness"]["average"] for t in template_report.values()]) if template_report else 0
            }
            
            return {
                "overall_metrics": overall_metrics,
                "template_analysis": template_report,
                "optimization_recommendations": self._generate_system_optimization_recommendations(template_report)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate template effectiveness report: {str(e)}")
            return {"error": "Failed to generate template effectiveness report"}

    # Private helper methods
    
    def _extract_template_effectiveness(self, result: Any) -> float:
        """Extract template effectiveness score from workflow result"""
        try:
            if hasattr(result, 'quality_metrics') and result.quality_metrics:
                return result.quality_metrics.get("effectiveness_score", 0.5)
            return 0.5  # Default neutral score
        except:
            return 0.5

    def _extract_quality_score(self, result: Any) -> float:
        """Extract quality score from workflow result"""
        try:
            if hasattr(result, 'quality_metrics') and result.quality_metrics:
                return result.quality_metrics.get("overall_score", 0.5)
            return 0.5  # Default neutral score
        except:
            return 0.5

    def _update_category_performance(self, metrics: WorkflowPerformanceMetrics) -> None:
        """Update performance tracking by category"""
        self.template_performance[f"{metrics.duration}_{metrics.video_type}"].append(metrics)
        self.video_type_performance[metrics.video_type].append(metrics)
        self.duration_performance[metrics.duration].append(metrics)

    def _filter_workflows_by_time(self, time_range: str) -> List[WorkflowPerformanceMetrics]:
        """Filter workflows by specified time range"""
        if time_range == "all":
            return list(self.workflow_history)
        
        # Parse time range
        time_mapping = {
            "1h": timedelta(hours=1),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        cutoff_time = datetime.utcnow() - time_mapping.get(time_range, timedelta(days=1))
        
        return [w for w in self.workflow_history if w.timestamp >= cutoff_time]

    async def _calculate_overview_metrics(self, workflows: List[WorkflowPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate overview performance metrics"""
        if not workflows:
            return {}
        
        execution_times = [w.execution_time for w in workflows]
        success_rates = [w.success_rate for w in workflows]
        quality_scores = [w.quality_score for w in workflows]
        
        return {
            "total_workflows": len(workflows),
            "success_rate": statistics.mean(success_rates),
            "average_execution_time": statistics.mean(execution_times),
            "median_execution_time": statistics.median(execution_times),
            "average_quality_score": statistics.mean(quality_scores),
            "quality_improvement_ratio": max(quality_scores) / min(quality_scores) if min(quality_scores) > 0 else 1,
            "performance_grade": self._calculate_performance_grade(workflows)
        }

    async def _calculate_performance_trends(self, workflows: List[WorkflowPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(workflows) < 3:
            return {"message": "Insufficient data for trend analysis"}
        
        # Sort by timestamp
        sorted_workflows = sorted(workflows, key=lambda w: w.timestamp)
        
        # Calculate trends
        execution_trend = self._calculate_trend([w.execution_time for w in sorted_workflows])
        quality_trend = self._calculate_trend([w.quality_score for w in sorted_workflows])
        success_trend = self._calculate_trend([w.success_rate for w in sorted_workflows])
        
        return {
            "execution_time_trend": execution_trend,
            "quality_score_trend": quality_trend,
            "success_rate_trend": success_trend,
            "overall_trend": "improving" if sum([execution_trend == "improving", 
                                               quality_trend == "improving", 
                                               success_trend == "improving"]) >= 2 else "stable"
        }

    async def _calculate_template_analytics(self, workflows: List[WorkflowPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate template-specific analytics"""
        template_groups = defaultdict(list)
        
        for workflow in workflows:
            template_key = f"{workflow.duration}_{workflow.video_type}"
            template_groups[template_key].append(workflow)
        
        analytics = {}
        for template_key, template_workflows in template_groups.items():
            if len(template_workflows) > 0:
                analytics[template_key] = {
                    "usage_count": len(template_workflows),
                    "success_rate": statistics.mean([w.success_rate for w in template_workflows]),
                    "average_quality": statistics.mean([w.quality_score for w in template_workflows]),
                    "average_execution_time": statistics.mean([w.execution_time for w in template_workflows])
                }
        
        # Find best and worst performing templates
        if analytics:
            best_template = max(analytics.keys(), key=lambda k: analytics[k]["average_quality"])
            worst_template = min(analytics.keys(), key=lambda k: analytics[k]["average_quality"])
            
            return {
                "template_performance": analytics,
                "best_performing": best_template,
                "worst_performing": worst_template,
                "template_selection_accuracy": self._calculate_template_accuracy(analytics)
            }
        
        return {"message": "No template data available"}

    async def _calculate_video_type_analytics(self, workflows: List[WorkflowPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate video type specific analytics"""
        type_groups = defaultdict(list)
        
        for workflow in workflows:
            type_groups[workflow.video_type].append(workflow)
        
        analytics = {}
        for video_type, type_workflows in type_groups.items():
            if len(type_workflows) > 0:
                analytics[video_type] = {
                    "usage_count": len(type_workflows),
                    "success_rate": statistics.mean([w.success_rate for w in type_workflows]),
                    "average_quality": statistics.mean([w.quality_score for w in type_workflows]),
                    "average_execution_time": statistics.mean([w.execution_time for w in type_workflows])
                }
        
        return analytics

    async def _calculate_duration_analytics(self, workflows: List[WorkflowPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate duration-specific analytics"""
        duration_groups = defaultdict(list)
        
        for workflow in workflows:
            duration_groups[workflow.duration].append(workflow)
        
        analytics = {}
        for duration, duration_workflows in duration_groups.items():
            if len(duration_workflows) > 0:
                analytics[duration] = {
                    "usage_count": len(duration_workflows),
                    "success_rate": statistics.mean([w.success_rate for w in duration_workflows]),
                    "average_quality": statistics.mean([w.quality_score for w in duration_workflows]),
                    "average_execution_time": statistics.mean([w.execution_time for w in duration_workflows])
                }
        
        return analytics

    async def _calculate_quality_metrics(self, workflows: List[WorkflowPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics"""
        if not workflows:
            return {}
        
        quality_scores = [w.quality_score for w in workflows]
        template_effectiveness = [w.template_effectiveness for w in workflows]
        
        return {
            "average_quality": statistics.mean(quality_scores),
            "quality_std_dev": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
            "quality_range": max(quality_scores) - min(quality_scores),
            "average_template_effectiveness": statistics.mean(template_effectiveness),
            "quality_distribution": self._calculate_quality_distribution(quality_scores),
            "improvement_potential": self._calculate_improvement_potential(quality_scores)
        }

    async def _generate_optimization_insights(self, workflows: List[WorkflowPerformanceMetrics]) -> List[Dict[str, Any]]:
        """Generate optimization insights and recommendations"""
        insights = []
        
        if not workflows:
            return insights
        
        # Execution time insights
        execution_times = [w.execution_time for w in workflows]
        avg_time = statistics.mean(execution_times)
        
        if avg_time > self.benchmarks["execution_time"]["acceptable"]:
            insights.append({
                "category": "performance",
                "priority": "high",
                "insight": f"Average execution time ({avg_time:.1f}s) exceeds acceptable threshold",
                "recommendation": "Consider optimizing template generation algorithms or implementing parallel processing"
            })
        
        # Quality insights
        quality_scores = [w.quality_score for w in workflows]
        avg_quality = statistics.mean(quality_scores)
        
        if avg_quality < self.benchmarks["quality_score"]["good"]:
            insights.append({
                "category": "quality",
                "priority": "medium",
                "insight": f"Average quality score ({avg_quality:.2f}) below good threshold",
                "recommendation": "Review template specifications and enhance quality validation algorithms"
            })
        
        # Success rate insights
        success_rates = [w.success_rate for w in workflows]
        avg_success = statistics.mean(success_rates)
        
        if avg_success < self.benchmarks["success_rate"]["good"]:
            insights.append({
                "category": "reliability",
                "priority": "high",
                "insight": f"Success rate ({avg_success:.2f}) below acceptable threshold",
                "recommendation": "Investigate failure patterns and improve error handling mechanisms"
            })
        
        return insights

    async def _assess_system_health(self, workflows: List[WorkflowPerformanceMetrics]) -> Dict[str, Any]:
        """Assess overall system health"""
        if not workflows:
            return {"status": "unknown", "message": "No data available"}
        
        # Calculate health score based on multiple factors
        execution_times = [w.execution_time for w in workflows]
        success_rates = [w.success_rate for w in workflows]
        quality_scores = [w.quality_score for w in workflows]
        
        avg_time = statistics.mean(execution_times)
        avg_success = statistics.mean(success_rates)
        avg_quality = statistics.mean(quality_scores)
        
        # Score each dimension (0-1 scale)
        time_score = min(1.0, self.benchmarks["execution_time"]["excellent"] / avg_time)
        success_score = avg_success
        quality_score = avg_quality
        
        overall_health = (time_score + success_score + quality_score) / 3
        
        # Determine health status
        if overall_health >= 0.9:
            status = "excellent"
        elif overall_health >= 0.8:
            status = "good"
        elif overall_health >= 0.7:
            status = "acceptable"
        else:
            status = "needs_attention"
        
        return {
            "status": status,
            "overall_health_score": overall_health,
            "performance_health": time_score,
            "reliability_health": success_score,
            "quality_health": quality_score,
            "active_workflows": len(self.active_workflows),
            "timestamp": datetime.utcnow()
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 3:
            return "stable"
        
        # Simple trend calculation using first and last third of values
        first_third = values[:len(values)//3]
        last_third = values[-len(values)//3:]
        
        first_avg = statistics.mean(first_third)
        last_avg = statistics.mean(last_third)
        
        change_percent = (last_avg - first_avg) / first_avg if first_avg != 0 else 0
        
        if change_percent > 0.05:  # 5% improvement threshold
            return "improving"
        elif change_percent < -0.05:  # 5% degradation threshold
            return "declining"
        else:
            return "stable"

    def _calculate_performance_grade(self, workflows: List[WorkflowPerformanceMetrics]) -> str:
        """Calculate overall performance grade"""
        if not workflows:
            return "N/A"
        
        success_rates = [w.success_rate for w in workflows]
        quality_scores = [w.quality_score for w in workflows]
        execution_times = [w.execution_time for w in workflows]
        
        avg_success = statistics.mean(success_rates)
        avg_quality = statistics.mean(quality_scores)
        avg_time = statistics.mean(execution_times)
        
        # Time score (inverted - lower is better)
        time_score = min(1.0, self.benchmarks["execution_time"]["excellent"] / avg_time)
        
        overall_score = (avg_success + avg_quality + time_score) / 3
        
        if overall_score >= 0.9:
            return "A+"
        elif overall_score >= 0.8:
            return "A"
        elif overall_score >= 0.7:
            return "B"
        elif overall_score >= 0.6:
            return "C"
        else:
            return "D"

    def _calculate_system_load(self) -> float:
        """Calculate current system load based on active workflows"""
        active_count = len(self.active_workflows)
        
        # Simple load calculation (can be enhanced based on system capacity)
        if active_count == 0:
            return 0.0
        elif active_count <= 2:
            return 0.25
        elif active_count <= 5:
            return 0.5
        elif active_count <= 10:
            return 0.75
        else:
            return 1.0

    def _assess_performance_status(self, recent_workflows: List[WorkflowPerformanceMetrics]) -> str:
        """Assess current performance status"""
        if not recent_workflows:
            return "idle"
        
        avg_time = statistics.mean([w.execution_time for w in recent_workflows])
        avg_success = statistics.mean([w.success_rate for w in recent_workflows])
        
        if avg_success >= 0.95 and avg_time <= self.benchmarks["execution_time"]["good"]:
            return "excellent"
        elif avg_success >= 0.85 and avg_time <= self.benchmarks["execution_time"]["acceptable"]:
            return "good"
        elif avg_success >= 0.70:
            return "acceptable"
        else:
            return "degraded"

    def _calculate_template_accuracy(self, template_analytics: Dict[str, Any]) -> float:
        """Calculate template selection accuracy"""
        if not template_analytics:
            return 0.0
        
        # Template selection is considered accurate if it achieves good performance
        accurate_templates = sum(1 for t in template_analytics.values() 
                               if t["success_rate"] >= 0.8 and t["average_quality"] >= 0.7)
        
        return accurate_templates / len(template_analytics)

    def _calculate_quality_distribution(self, quality_scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of quality scores"""
        distribution = {"excellent": 0, "good": 0, "acceptable": 0, "poor": 0}
        
        for score in quality_scores:
            if score >= 0.9:
                distribution["excellent"] += 1
            elif score >= 0.8:
                distribution["good"] += 1
            elif score >= 0.7:
                distribution["acceptable"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution

    def _calculate_improvement_potential(self, quality_scores: List[float]) -> float:
        """Calculate potential for quality improvement"""
        if not quality_scores:
            return 0.0
        
        current_avg = statistics.mean(quality_scores)
        theoretical_max = 1.0
        
        return (theoretical_max - current_avg) / theoretical_max

    def _calculate_reliability_score(self, workflows: List[WorkflowPerformanceMetrics]) -> float:
        """Calculate reliability score for a template"""
        if not workflows:
            return 0.0
        
        success_rates = [w.success_rate for w in workflows]
        quality_consistency = 1.0 - (statistics.stdev([w.quality_score for w in workflows]) if len(workflows) > 1 else 0)
        
        return (statistics.mean(success_rates) + quality_consistency) / 2

    def _generate_template_recommendation(self, workflows: List[WorkflowPerformanceMetrics]) -> str:
        """Generate recommendation for template improvement"""
        if not workflows:
            return "Insufficient data for recommendation"
        
        avg_quality = statistics.mean([w.quality_score for w in workflows])
        avg_success = statistics.mean([w.success_rate for w in workflows])
        avg_time = statistics.mean([w.execution_time for w in workflows])
        
        if avg_success < 0.8:
            return "Focus on improving template reliability and error handling"
        elif avg_quality < 0.7:
            return "Enhance template quality and content depth"
        elif avg_time > 300:  # 5 minutes
            return "Optimize template for faster execution"
        else:
            return "Template performing well, consider minor optimizations"

    def _generate_system_optimization_recommendations(self, template_report: Dict[str, Any]) -> List[str]:
        """Generate system-wide optimization recommendations"""
        recommendations = []
        
        if not template_report:
            return ["Insufficient data for system recommendations"]
        
        # Analyze overall system performance
        avg_effectiveness = statistics.mean([t["effectiveness"]["average"] for t in template_report.values()])
        
        if avg_effectiveness < 0.8:
            recommendations.append("Consider reviewing and updating template specifications")
        
        # Check for performance consistency
        effectiveness_values = [t["effectiveness"]["average"] for t in template_report.values()]
        if len(effectiveness_values) > 1 and statistics.stdev(effectiveness_values) > 0.2:
            recommendations.append("Address performance inconsistencies across templates")
        
        # Check template usage patterns
        usage_counts = [t["sample_size"] for t in template_report.values()]
        if max(usage_counts) / min(usage_counts) > 5:  # High usage imbalance
            recommendations.append("Consider load balancing or optimizing popular templates")
        
        return recommendations if recommendations else ["System performing optimally"]

    def _invalidate_cache(self) -> None:
        """Invalidate analytics cache to force recalculation"""
        self.cached_analytics.clear()
        self.cache_expiry = datetime.utcnow()

    def clear_history(self) -> None:
        """Clear all performance history (use with caution)"""
        self.workflow_history.clear()
        self.system_metrics_history.clear()
        self.template_performance.clear()
        self.video_type_performance.clear()
        self.duration_performance.clear()
        self._invalidate_cache()
        
        logger.info("Performance history cleared")
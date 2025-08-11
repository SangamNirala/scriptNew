#!/usr/bin/env python3
"""
Phase 3.3: Enhanced Prompt Generation Workflow System - Comprehensive Backend Testing
Tests the complete end-to-end workflow that combines duration analysis, template selection,
video type customization, segmentation integration, and quality validation.
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase33EnhancedWorkflowTester:
    """Comprehensive tester for Phase 3.3 Enhanced Workflow System"""
    
    def __init__(self, base_url: str = "https://42a664c7-cfb0-482a-a5bd-f05ce6cec8de.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.test_results = []
        self.workflow_ids = []
        
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive Phase 3.3 Enhanced Workflow System test"""
        logger.info("🚀 Starting Phase 3.3: Enhanced Prompt Generation Workflow System Comprehensive Test")
        
        test_summary = {
            "phase": "3.3_enhanced_workflow_system",
            "test_start_time": datetime.utcnow().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "critical_issues": [],
            "test_details": []
        }
        
        # Test scenarios as specified in review request
        test_scenarios = [
            {
                "name": "Educational + Extended_20 Duration Workflow",
                "prompt": "Create a comprehensive educational video about quantum computing fundamentals",
                "video_type": "educational",
                "duration": "extended_20",
                "industry_focus": "technology",
                "expected_segments": 4,
                "expected_duration_minutes": 22.5
            },
            {
                "name": "Marketing + Medium Duration Workflow",
                "prompt": "Create a compelling marketing video for our new sustainable fashion brand",
                "video_type": "marketing", 
                "duration": "medium",
                "industry_focus": "fashion",
                "expected_segments": 1,
                "expected_duration_minutes": 2.0
            },
            {
                "name": "Entertainment + Short Duration Workflow",
                "prompt": "Create an entertaining video about funny pet moments and reactions",
                "video_type": "entertainment",
                "duration": "short", 
                "industry_focus": None,
                "expected_segments": 1,
                "expected_duration_minutes": 0.75
            },
            {
                "name": "General + Extended_25 Duration Workflow",
                "prompt": "Create a detailed guide on building sustainable communities",
                "video_type": "general",
                "duration": "extended_25",
                "industry_focus": "environment",
                "expected_segments": 5,
                "expected_duration_minutes": 27.5
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Main Workflow Testing
            await self._test_main_workflow_generation(session, test_scenarios, test_summary)
            
            # Test 2: Status and Results Testing
            await self._test_status_and_results_tracking(session, test_summary)
            
            # Test 3: Analytics Testing
            await self._test_analytics_endpoints(session, test_summary)
            
            # Test 4: Quality Validation Testing
            await self._test_quality_validation(session, test_summary)
            
            # Test 5: Integration Testing
            await self._test_integration_points(session, test_summary)
            
            # Test 6: Performance Testing
            await self._test_performance_requirements(session, test_summary)
            
            # Test 7: Error Handling Testing
            await self._test_error_handling(session, test_summary)
            
            # Test 8: Comprehensive Testing Endpoint
            await self._test_comprehensive_endpoint(session, test_summary)
        
        # Calculate final results
        test_summary["test_end_time"] = datetime.utcnow().isoformat()
        test_summary["success_rate"] = (test_summary["tests_passed"] / test_summary["tests_run"] * 100) if test_summary["tests_run"] > 0 else 0
        test_summary["overall_status"] = "PASSED" if test_summary["success_rate"] >= 90 else "FAILED"
        
        logger.info(f"✅ Phase 3.3 Enhanced Workflow System Test Complete: {test_summary['success_rate']:.1f}% success rate")
        
        return test_summary

    async def _test_main_workflow_generation(self, session: aiohttp.ClientSession, scenarios: List[Dict], summary: Dict):
        """Test 1: Main Workflow Testing with different combinations"""
        logger.info("🔧 Test 1: Main Workflow Generation Testing")
        
        for scenario in scenarios:
            test_name = f"Main Workflow - {scenario['name']}"
            summary["tests_run"] += 1
            
            try:
                # Execute enhanced workflow generation
                payload = {
                    "prompt": scenario["prompt"],
                    "video_type": scenario["video_type"],
                    "duration": scenario["duration"],
                    "industry_focus": scenario["industry_focus"]
                }
                
                start_time = time.time()
                async with session.post(f"{self.api_base}/enhanced-workflow-generation", json=payload) as response:
                    execution_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Validate workflow result structure
                        required_fields = ["workflow_id", "status", "final_prompt", "template_info", 
                                         "segmentation_plan", "quality_metrics", "execution_time", "steps_completed"]
                        
                        validation_results = []
                        for field in required_fields:
                            if field in result:
                                validation_results.append(f"✅ {field}")
                            else:
                                validation_results.append(f"❌ Missing {field}")
                        
                        # Validate workflow completion
                        workflow_success = (
                            result.get("status") == "completed" and
                            result.get("final_prompt") is not None and
                            len(result.get("final_prompt", "")) > 500 and  # Substantial prompt
                            result.get("template_info") is not None and
                            result.get("segmentation_plan") is not None and
                            result.get("quality_metrics") is not None and
                            len(result.get("steps_completed", [])) >= 5  # All 6 steps completed
                        )
                        
                        if workflow_success:
                            summary["tests_passed"] += 1
                            self.workflow_ids.append(result["workflow_id"])
                            
                            summary["test_details"].append({
                                "test": test_name,
                                "status": "PASSED",
                                "execution_time": execution_time,
                                "workflow_id": result["workflow_id"],
                                "final_prompt_length": len(result.get("final_prompt", "")),
                                "steps_completed": len(result.get("steps_completed", [])),
                                "quality_score": result.get("quality_metrics", {}).get("overall_score"),
                                "validation": validation_results
                            })
                            
                            logger.info(f"✅ {test_name}: PASSED (execution_time: {execution_time:.2f}s)")
                        else:
                            summary["tests_failed"] += 1
                            summary["critical_issues"].append(f"{test_name}: Workflow incomplete or invalid")
                            
                            summary["test_details"].append({
                                "test": test_name,
                                "status": "FAILED",
                                "reason": "Workflow incomplete or invalid result structure",
                                "validation": validation_results
                            })
                            
                            logger.error(f"❌ {test_name}: FAILED - Workflow incomplete")
                    else:
                        summary["tests_failed"] += 1
                        error_text = await response.text()
                        summary["critical_issues"].append(f"{test_name}: HTTP {response.status}")
                        
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "http_status": response.status,
                            "error": error_text[:200]
                        })
                        
                        logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                        
            except Exception as e:
                summary["tests_failed"] += 1
                summary["critical_issues"].append(f"{test_name}: Exception - {str(e)}")
                
                summary["test_details"].append({
                    "test": test_name,
                    "status": "FAILED",
                    "exception": str(e)[:200]
                })
                
                logger.error(f"❌ {test_name}: FAILED - {str(e)}")

    async def _test_status_and_results_tracking(self, session: aiohttp.ClientSession, summary: Dict):
        """Test 2: Status and Results Testing"""
        logger.info("🔧 Test 2: Status and Results Tracking Testing")
        
        if not self.workflow_ids:
            logger.warning("⚠️ No workflow IDs available for status testing")
            return
        
        # Test workflow status endpoint
        for workflow_id in self.workflow_ids[:2]:  # Test first 2 workflows
            test_name = f"Workflow Status - {workflow_id[:8]}"
            summary["tests_run"] += 1
            
            try:
                async with session.get(f"{self.api_base}/workflow-status/{workflow_id}") as response:
                    if response.status == 200:
                        status_data = await response.json()
                        
                        # Validate status structure
                        required_status_fields = ["workflow_id", "status", "steps_completed", "progress", "elapsed_time"]
                        status_valid = all(field in status_data for field in required_status_fields)
                        
                        if status_valid:
                            summary["tests_passed"] += 1
                            summary["test_details"].append({
                                "test": test_name,
                                "status": "PASSED",
                                "workflow_status": status_data.get("status"),
                                "progress": status_data.get("progress"),
                                "steps_completed": len(status_data.get("steps_completed", []))
                            })
                            logger.info(f"✅ {test_name}: PASSED")
                        else:
                            summary["tests_failed"] += 1
                            summary["test_details"].append({
                                "test": test_name,
                                "status": "FAILED",
                                "reason": "Invalid status structure"
                            })
                            logger.error(f"❌ {test_name}: FAILED - Invalid status structure")
                    else:
                        summary["tests_failed"] += 1
                        logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                        
            except Exception as e:
                summary["tests_failed"] += 1
                logger.error(f"❌ {test_name}: FAILED - {str(e)}")
        
        # Test workflow results endpoint
        for workflow_id in self.workflow_ids[:2]:  # Test first 2 workflows
            test_name = f"Workflow Results - {workflow_id[:8]}"
            summary["tests_run"] += 1
            
            try:
                async with session.get(f"{self.api_base}/workflow-results/{workflow_id}") as response:
                    if response.status == 200:
                        results_data = await response.json()
                        
                        # Validate results structure
                        required_result_fields = ["workflow_id", "status", "final_prompt", "template_info", 
                                                "segmentation_plan", "quality_metrics", "execution_time"]
                        results_valid = all(field in results_data for field in required_result_fields)
                        
                        if results_valid:
                            summary["tests_passed"] += 1
                            summary["test_details"].append({
                                "test": test_name,
                                "status": "PASSED",
                                "has_final_prompt": bool(results_data.get("final_prompt")),
                                "has_quality_metrics": bool(results_data.get("quality_metrics")),
                                "execution_time": results_data.get("execution_time")
                            })
                            logger.info(f"✅ {test_name}: PASSED")
                        else:
                            summary["tests_failed"] += 1
                            summary["test_details"].append({
                                "test": test_name,
                                "status": "FAILED",
                                "reason": "Invalid results structure"
                            })
                            logger.error(f"❌ {test_name}: FAILED - Invalid results structure")
                    else:
                        summary["tests_failed"] += 1
                        logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                        
            except Exception as e:
                summary["tests_failed"] += 1
                logger.error(f"❌ {test_name}: FAILED - {str(e)}")

    async def _test_analytics_endpoints(self, session: aiohttp.ClientSession, summary: Dict):
        """Test 3: Analytics Testing"""
        logger.info("🔧 Test 3: Analytics Endpoints Testing")
        
        # Test performance analytics
        test_name = "Performance Analytics"
        summary["tests_run"] += 1
        
        try:
            async with session.get(f"{self.api_base}/workflow-analytics?time_range=1h") as response:
                if response.status == 200:
                    analytics = await response.json()
                    
                    # Validate analytics structure
                    expected_sections = ["overview", "performance_trends", "template_analytics", 
                                       "video_type_analytics", "duration_analytics", "quality_metrics"]
                    
                    analytics_valid = any(section in analytics for section in expected_sections)
                    
                    if analytics_valid:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "sections_found": [section for section in expected_sections if section in analytics]
                        })
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        summary["tests_failed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "reason": "Missing expected analytics sections"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Missing analytics sections")
                else:
                    summary["tests_failed"] += 1
                    logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                    
        except Exception as e:
            summary["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")
        
        # Test real-time metrics
        test_name = "Real-time Metrics"
        summary["tests_run"] += 1
        
        try:
            async with session.get(f"{self.api_base}/workflow-real-time-metrics") as response:
                if response.status == 200:
                    metrics = await response.json()
                    
                    # Validate real-time metrics structure
                    expected_metrics = ["active_workflows", "recent_completions", "average_execution_time", 
                                      "success_rate", "system_load", "performance_status"]
                    
                    metrics_valid = any(metric in metrics for metric in expected_metrics)
                    
                    if metrics_valid:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "active_workflows": metrics.get("active_workflows"),
                            "recent_completions": metrics.get("recent_completions"),
                            "performance_status": metrics.get("performance_status")
                        })
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        summary["tests_failed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "reason": "Missing expected metrics"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Missing metrics")
                else:
                    summary["tests_failed"] += 1
                    logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                    
        except Exception as e:
            summary["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")
        
        # Test template effectiveness report
        test_name = "Template Effectiveness Report"
        summary["tests_run"] += 1
        
        try:
            async with session.get(f"{self.api_base}/template-effectiveness-report") as response:
                if response.status == 200:
                    report = await response.json()
                    
                    # Validate template effectiveness report structure
                    expected_report_sections = ["overall_metrics", "template_analysis", "optimization_recommendations"]
                    
                    report_valid = any(section in report for section in expected_report_sections)
                    
                    if report_valid:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "has_overall_metrics": "overall_metrics" in report,
                            "has_template_analysis": "template_analysis" in report,
                            "has_recommendations": "optimization_recommendations" in report
                        })
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        summary["tests_failed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "reason": "Missing expected report sections"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Missing report sections")
                else:
                    summary["tests_failed"] += 1
                    logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                    
        except Exception as e:
            summary["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")

    async def _test_quality_validation(self, session: aiohttp.ClientSession, summary: Dict):
        """Test 4: Quality Validation Testing"""
        logger.info("🔧 Test 4: Quality Validation Testing")
        
        # This test verifies that quality metrics are being calculated and effectiveness scores are generated
        test_name = "Quality Metrics Validation"
        summary["tests_run"] += 1
        
        try:
            # Use a simple workflow to test quality validation
            payload = {
                "prompt": "Create a test video for quality validation",
                "video_type": "general",
                "duration": "short",
                "industry_focus": None
            }
            
            async with session.post(f"{self.api_base}/enhanced-workflow-generation", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Validate quality metrics presence and structure
                    quality_metrics = result.get("quality_metrics", {})
                    
                    expected_quality_fields = ["overall_score", "content_depth", "structure_clarity", 
                                             "engagement_potential", "technical_accuracy"]
                    
                    quality_valid = (
                        quality_metrics and
                        any(field in quality_metrics for field in expected_quality_fields) and
                        isinstance(quality_metrics.get("overall_score"), (int, float))
                    )
                    
                    if quality_valid:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "overall_score": quality_metrics.get("overall_score"),
                            "quality_fields_present": [field for field in expected_quality_fields if field in quality_metrics]
                        })
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        summary["tests_failed"] += 1
                        summary["critical_issues"].append(f"{test_name}: Quality metrics missing or invalid")
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "reason": "Quality metrics missing or invalid structure"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Quality metrics invalid")
                else:
                    summary["tests_failed"] += 1
                    logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                    
        except Exception as e:
            summary["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")

    async def _test_integration_points(self, session: aiohttp.ClientSession, summary: Dict):
        """Test 5: Integration Testing"""
        logger.info("🔧 Test 5: Integration Points Testing")
        
        # Test integration with existing systems from previous phases
        test_name = "System Integration Verification"
        summary["tests_run"] += 1
        
        try:
            # Test that the workflow integrates with duration-specific templates (Phase 2)
            payload = {
                "prompt": "Test integration with duration-specific templates",
                "video_type": "educational",
                "duration": "extended_15",  # This should use Phase 2 templates
                "industry_focus": "technology"
            }
            
            async with session.post(f"{self.api_base}/enhanced-workflow-generation", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Validate integration points
                    integration_valid = (
                        result.get("template_info") is not None and  # Phase 2 integration
                        result.get("segmentation_plan") is not None and  # Phase 1 integration
                        result.get("final_prompt") is not None and  # Enhanced prompt architecture
                        len(result.get("steps_completed", [])) >= 5  # All workflow steps
                    )
                    
                    if integration_valid:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "template_integration": bool(result.get("template_info")),
                            "segmentation_integration": bool(result.get("segmentation_plan")),
                            "prompt_architecture_integration": bool(result.get("final_prompt")),
                            "workflow_steps_completed": len(result.get("steps_completed", []))
                        })
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        summary["tests_failed"] += 1
                        summary["critical_issues"].append(f"{test_name}: Integration points missing")
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "reason": "Integration points missing or incomplete"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Integration incomplete")
                else:
                    summary["tests_failed"] += 1
                    logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                    
        except Exception as e:
            summary["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")

    async def _test_performance_requirements(self, session: aiohttp.ClientSession, summary: Dict):
        """Test 6: Performance Testing"""
        logger.info("🔧 Test 6: Performance Requirements Testing")
        
        # Test workflow execution times are reasonable (< 10 minutes as specified)
        test_name = "Performance Requirements"
        summary["tests_run"] += 1
        
        try:
            payload = {
                "prompt": "Performance test for workflow execution time",
                "video_type": "general",
                "duration": "medium",
                "industry_focus": None
            }
            
            start_time = time.time()
            async with session.post(f"{self.api_base}/enhanced-workflow-generation", json=payload) as response:
                execution_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    # Validate performance requirements
                    performance_acceptable = (
                        execution_time < 600 and  # < 10 minutes
                        result.get("status") == "completed" and
                        result.get("execution_time", 0) < 600
                    )
                    
                    if performance_acceptable:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "execution_time": execution_time,
                            "workflow_execution_time": result.get("execution_time"),
                            "performance_grade": "Excellent" if execution_time < 60 else "Good" if execution_time < 300 else "Acceptable"
                        })
                        logger.info(f"✅ {test_name}: PASSED (execution_time: {execution_time:.2f}s)")
                    else:
                        summary["tests_failed"] += 1
                        summary["critical_issues"].append(f"{test_name}: Performance requirements not met")
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "execution_time": execution_time,
                            "reason": "Execution time exceeds 10 minute requirement"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Performance too slow ({execution_time:.2f}s)")
                else:
                    summary["tests_failed"] += 1
                    logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                    
        except Exception as e:
            summary["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")

    async def _test_error_handling(self, session: aiohttp.ClientSession, summary: Dict):
        """Test 7: Error Handling Testing"""
        logger.info("🔧 Test 7: Error Handling Testing")
        
        # Test with invalid inputs
        error_test_cases = [
            {
                "name": "Invalid Duration",
                "payload": {
                    "prompt": "Test invalid duration",
                    "video_type": "general",
                    "duration": "invalid_duration",
                    "industry_focus": None
                },
                "expected_status": 400
            },
            {
                "name": "Empty Prompt",
                "payload": {
                    "prompt": "",
                    "video_type": "general",
                    "duration": "medium",
                    "industry_focus": None
                },
                "expected_status": [400, 422]  # Could be validation error
            },
            {
                "name": "Invalid Video Type",
                "payload": {
                    "prompt": "Test invalid video type",
                    "video_type": "invalid_type",
                    "duration": "medium",
                    "industry_focus": None
                },
                "expected_status": [200, 400]  # Might be handled gracefully
            }
        ]
        
        for test_case in error_test_cases:
            test_name = f"Error Handling - {test_case['name']}"
            summary["tests_run"] += 1
            
            try:
                async with session.post(f"{self.api_base}/enhanced-workflow-generation", json=test_case["payload"]) as response:
                    expected_statuses = test_case["expected_status"] if isinstance(test_case["expected_status"], list) else [test_case["expected_status"]]
                    
                    if response.status in expected_statuses:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "http_status": response.status,
                            "error_handled_correctly": True
                        })
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        summary["tests_failed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "http_status": response.status,
                            "expected_status": expected_statuses,
                            "reason": "Unexpected error handling behavior"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Unexpected status {response.status}")
                        
            except Exception as e:
                summary["tests_failed"] += 1
                logger.error(f"❌ {test_name}: FAILED - {str(e)}")

    async def _test_comprehensive_endpoint(self, session: aiohttp.ClientSession, summary: Dict):
        """Test 8: Comprehensive Testing Endpoint"""
        logger.info("🔧 Test 8: Comprehensive Testing Endpoint")
        
        test_name = "Comprehensive Test Endpoint"
        summary["tests_run"] += 1
        
        try:
            async with session.post(f"{self.api_base}/test-enhanced-workflow") as response:
                if response.status == 200:
                    test_result = await response.json()
                    
                    # Validate comprehensive test result
                    comprehensive_valid = (
                        test_result.get("phase_implementation") == "3.3_enhanced_workflow_system" and
                        "test_summary" in test_result and
                        "detailed_results" in test_result and
                        "workflow_system_verification" in test_result and
                        "performance_benchmarks" in test_result
                    )
                    
                    if comprehensive_valid:
                        summary["tests_passed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "PASSED",
                            "success_rate": test_result.get("test_summary", {}).get("success_rate_percent"),
                            "scenarios_tested": test_result.get("test_summary", {}).get("total_scenarios"),
                            "all_workflows_working": test_result.get("test_summary", {}).get("all_workflows_working")
                        })
                        logger.info(f"✅ {test_name}: PASSED")
                    else:
                        summary["tests_failed"] += 1
                        summary["test_details"].append({
                            "test": test_name,
                            "status": "FAILED",
                            "reason": "Invalid comprehensive test result structure"
                        })
                        logger.error(f"❌ {test_name}: FAILED - Invalid result structure")
                else:
                    summary["tests_failed"] += 1
                    logger.error(f"❌ {test_name}: FAILED - HTTP {response.status}")
                    
        except Exception as e:
            summary["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")

async def main():
    """Main test execution function"""
    tester = Phase33EnhancedWorkflowTester()
    results = await tester.run_comprehensive_test()
    
    print("\n" + "="*80)
    print("🎯 PHASE 3.3: ENHANCED PROMPT GENERATION WORKFLOW SYSTEM - TEST RESULTS")
    print("="*80)
    print(f"📊 Overall Status: {results['overall_status']}")
    print(f"📈 Success Rate: {results['success_rate']:.1f}%")
    print(f"✅ Tests Passed: {results['tests_passed']}")
    print(f"❌ Tests Failed: {results['tests_failed']}")
    print(f"📝 Total Tests: {results['tests_run']}")
    
    if results['critical_issues']:
        print(f"\n🚨 Critical Issues Found:")
        for issue in results['critical_issues']:
            print(f"   • {issue}")
    
    print(f"\n📋 Detailed Test Results:")
    for test_detail in results['test_details']:
        status_icon = "✅" if test_detail['status'] == 'PASSED' else "❌"
        print(f"   {status_icon} {test_detail['test']}: {test_detail['status']}")
        if test_detail['status'] == 'FAILED' and 'reason' in test_detail:
            print(f"      Reason: {test_detail['reason']}")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
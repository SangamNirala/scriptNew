#!/usr/bin/env python3
"""
Phase 5: Intelligent Quality Assurance & Auto-Optimization Backend Testing Script
Tests all new Phase 5 endpoints for multi-model validation, quality metrics, and optimization
"""

import requests
import json
import time
from datetime import datetime
import sys

# Get backend URL from frontend .env
BACKEND_URL = "https://dd694e3b-a30b-41f0-bc6e-bb4a5f83262e.preview.emergentagent.com/api"

class Phase5QATester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
        # Sample data for testing as specified in review request
        self.sample_prompt = "Create a video about healthy cooking tips"
        self.sample_low_quality_script = "Cook food. Eat healthy. The end."
        self.sample_platform = "youtube"
        self.sample_duration = "medium"
        self.sample_video_type = "educational"
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Hello World":
                    self.log_test("Basic Connectivity", True, "API is accessible and responding")
                    return True
                else:
                    self.log_test("Basic Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Basic Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_multi_model_validation(self):
        """Test Multi-Model Validation endpoint - Uses 3-5 AI models for consensus scoring"""
        print("\n=== Testing Multi-Model Validation Endpoint ===")
        
        payload = {
            "script": self.sample_low_quality_script,
            "target_platform": self.sample_platform,
            "duration": self.sample_duration,
            "video_type": self.sample_video_type
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/multi-model-validation",
                json=payload,
                timeout=120  # Longer timeout for multi-model processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required response fields
                required_fields = [
                    "consensus_score", "consensus_grade", "individual_results", 
                    "agreement_level", "confidence_score", "quality_threshold_passed",
                    "regeneration_required", "improvement_suggestions"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Multi-Model Validation - Structure", False, 
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify consensus score is valid (0-10)
                consensus_score = data.get("consensus_score", 0)
                if not isinstance(consensus_score, (int, float)) or consensus_score < 0 or consensus_score > 10:
                    self.log_test("Multi-Model Validation - Consensus Score", False,
                                f"Invalid consensus score: {consensus_score} (should be 0-10)")
                    return False
                
                # Verify individual results structure
                individual_results = data.get("individual_results", [])
                if not isinstance(individual_results, list) or len(individual_results) < 3:
                    self.log_test("Multi-Model Validation - Individual Results", False,
                                f"Should have at least 3 individual model results, got {len(individual_results)}")
                    return False
                
                # Check each individual result has required fields
                for i, result in enumerate(individual_results):
                    if not all(key in result for key in ["model_name", "score", "reasoning"]):
                        self.log_test("Multi-Model Validation - Individual Result Structure", False,
                                    f"Individual result {i+1} missing required fields")
                        return False
                
                # Verify agreement level is valid
                agreement_level = data.get("agreement_level", "")
                valid_agreement_levels = ["high", "medium", "low", "very_high", "very_low"]
                if agreement_level.lower() not in valid_agreement_levels:
                    self.log_test("Multi-Model Validation - Agreement Level", False,
                                f"Invalid agreement level: {agreement_level}")
                    return False
                
                self.log_test("Multi-Model Validation", True,
                            f"Successfully validated with {len(individual_results)} models, consensus score: {consensus_score:.1f}/10, agreement: {agreement_level}")
                return True
                
            else:
                self.log_test("Multi-Model Validation", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Multi-Model Validation", False, f"Request failed: {str(e)}")
            return False
    
    def test_advanced_quality_metrics(self):
        """Test Advanced Quality Metrics endpoint - Comprehensive analysis"""
        print("\n=== Testing Advanced Quality Metrics Endpoint ===")
        
        payload = {
            "script": self.sample_low_quality_script,
            "target_platform": self.sample_platform,
            "duration": self.sample_duration,
            "video_type": self.sample_video_type
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/advanced-quality-metrics",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required response fields
                required_fields = [
                    "composite_quality_score", "quality_grade", "detailed_metrics",
                    "quality_recommendations", "analysis_metadata"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Advanced Quality Metrics - Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify composite quality score
                composite_score = data.get("composite_quality_score", 0)
                if not isinstance(composite_score, (int, float)) or composite_score < 0 or composite_score > 10:
                    self.log_test("Advanced Quality Metrics - Composite Score", False,
                                f"Invalid composite score: {composite_score} (should be 0-10)")
                    return False
                
                # Verify detailed metrics structure
                detailed_metrics = data.get("detailed_metrics", {})
                expected_metrics = [
                    "readability", "engagement_prediction", "emotional_intelligence",
                    "platform_compliance", "conversion_potential"
                ]
                
                missing_metrics = [metric for metric in expected_metrics if metric not in detailed_metrics]
                if missing_metrics:
                    self.log_test("Advanced Quality Metrics - Detailed Metrics", False,
                                f"Missing detailed metrics: {missing_metrics}")
                    return False
                
                # Verify quality recommendations
                recommendations = data.get("quality_recommendations", [])
                if not isinstance(recommendations, list) or len(recommendations) == 0:
                    self.log_test("Advanced Quality Metrics - Recommendations", False,
                                "Should provide quality recommendations")
                    return False
                
                self.log_test("Advanced Quality Metrics", True,
                            f"Successfully analyzed with composite score: {composite_score:.1f}/10, {len(recommendations)} recommendations")
                return True
                
            else:
                self.log_test("Advanced Quality Metrics", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Advanced Quality Metrics", False, f"Request failed: {str(e)}")
            return False
    
    def test_quality_improvement_optimization(self):
        """Test Quality Improvement Optimization endpoint - Auto-regeneration for scripts below 8.5/10"""
        print("\n=== Testing Quality Improvement Optimization Endpoint ===")
        
        payload = {
            "original_prompt": self.sample_prompt,
            "target_platform": self.sample_platform,
            "duration": self.sample_duration,
            "video_type": self.sample_video_type
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/quality-improvement-optimization",
                json=payload,
                timeout=180  # Longer timeout for improvement cycles
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required response fields
                required_fields = [
                    "cycle_id", "original_score", "final_score", "improvement_achieved",
                    "quality_threshold_met", "cycles_completed", "final_script",
                    "validation_result", "strategy_used", "improvements_attempted",
                    "learning_insights"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Quality Improvement - Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify scores are valid
                original_score = data.get("original_score", 0)
                final_score = data.get("final_score", 0)
                
                if not isinstance(original_score, (int, float)) or original_score < 0 or original_score > 10:
                    self.log_test("Quality Improvement - Original Score", False,
                                f"Invalid original score: {original_score}")
                    return False
                
                if not isinstance(final_score, (int, float)) or final_score < 0 or final_score > 10:
                    self.log_test("Quality Improvement - Final Score", False,
                                f"Invalid final score: {final_score}")
                    return False
                
                # Verify improvement logic
                improvement_achieved = data.get("improvement_achieved", 0)
                expected_improvement = final_score - original_score
                if abs(improvement_achieved - expected_improvement) > 0.1:
                    self.log_test("Quality Improvement - Improvement Calculation", False,
                                f"Improvement calculation mismatch: {improvement_achieved} vs expected {expected_improvement}")
                    return False
                
                # Verify threshold logic (8.5/10)
                quality_threshold_met = data.get("quality_threshold_met", False)
                if final_score >= 8.5 and not quality_threshold_met:
                    self.log_test("Quality Improvement - Threshold Logic", False,
                                f"Final score {final_score} >= 8.5 but threshold not marked as met")
                    return False
                
                # Verify final script exists
                final_script = data.get("final_script", "")
                if not final_script or len(final_script) < 50:
                    self.log_test("Quality Improvement - Final Script", False,
                                "Final script should be substantial content")
                    return False
                
                cycles_completed = data.get("cycles_completed", 0)
                self.log_test("Quality Improvement", True,
                            f"Successfully improved from {original_score:.1f} to {final_score:.1f} in {cycles_completed} cycles, threshold met: {quality_threshold_met}")
                return True
                
            else:
                self.log_test("Quality Improvement", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Quality Improvement", False, f"Request failed: {str(e)}")
            return False
    
    def test_ab_test_optimization(self):
        """Test A/B Test Optimization endpoint - Tests both prompt strategies AND AI models"""
        print("\n=== Testing A/B Test Optimization Endpoint ===")
        
        payload = {
            "original_prompt": self.sample_prompt,
            "target_platform": self.sample_platform,
            "duration": self.sample_duration,
            "video_type": self.sample_video_type
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/ab-test-optimization",
                json=payload,
                timeout=240  # Very long timeout for A/B testing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required response fields
                required_fields = [
                    "test_id", "best_performing_combination", "all_results",
                    "statistical_analysis", "performance_improvement", "recommendations"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("A/B Test Optimization - Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify best performing combination structure
                best_combo = data.get("best_performing_combination", {})
                combo_required_fields = ["strategy", "model", "score", "script"]
                combo_missing = [field for field in combo_required_fields if field not in best_combo]
                if combo_missing:
                    self.log_test("A/B Test Optimization - Best Combo Structure", False,
                                f"Missing fields in best combination: {combo_missing}")
                    return False
                
                # Verify all results structure
                all_results = data.get("all_results", [])
                if not isinstance(all_results, list) or len(all_results) < 2:
                    self.log_test("A/B Test Optimization - All Results", False,
                                f"Should have at least 2 test results, got {len(all_results)}")
                    return False
                
                # Verify each result has required fields
                for i, result in enumerate(all_results):
                    result_required = ["strategy", "model", "score", "script"]
                    result_missing = [field for field in result_required if field not in result]
                    if result_missing:
                        self.log_test("A/B Test Optimization - Result Structure", False,
                                    f"Result {i+1} missing fields: {result_missing}")
                        return False
                
                # Verify statistical analysis
                stats = data.get("statistical_analysis", {})
                if not isinstance(stats, dict) or len(stats) == 0:
                    self.log_test("A/B Test Optimization - Statistical Analysis", False,
                                "Should provide statistical analysis")
                    return False
                
                # Verify performance improvement
                performance_improvement = data.get("performance_improvement", 0)
                if not isinstance(performance_improvement, (int, float)):
                    self.log_test("A/B Test Optimization - Performance Improvement", False,
                                f"Invalid performance improvement: {performance_improvement}")
                    return False
                
                best_score = best_combo.get("score", 0)
                self.log_test("A/B Test Optimization", True,
                            f"Successfully tested {len(all_results)} combinations, best: {best_combo.get('strategy', 'unknown')} + {best_combo.get('model', 'unknown')} (score: {best_score:.1f})")
                return True
                
            else:
                self.log_test("A/B Test Optimization", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("A/B Test Optimization", False, f"Request failed: {str(e)}")
            return False
    
    def test_intelligent_qa_analysis(self):
        """Test Intelligent QA Analysis endpoint - Master orchestrator combining all Phase 5 components"""
        print("\n=== Testing Intelligent QA Analysis Endpoint ===")
        
        payload = {
            "script": self.sample_low_quality_script,
            "original_prompt": self.sample_prompt,
            "target_platform": self.sample_platform,
            "duration": self.sample_duration,
            "video_type": self.sample_video_type,
            "enable_regeneration": True
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/intelligent-qa-analysis",
                json=payload,
                timeout=300  # Very long timeout for comprehensive analysis
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required response fields
                required_fields = [
                    "qa_id", "original_prompt", "final_script", "quality_analysis",
                    "consensus_validation", "quality_threshold_met", "regeneration_performed",
                    "total_processing_time", "recommendations", "confidence_score"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Intelligent QA Analysis - Structure", False,
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify quality analysis structure
                quality_analysis = data.get("quality_analysis", {})
                if not isinstance(quality_analysis, dict) or len(quality_analysis) == 0:
                    self.log_test("Intelligent QA Analysis - Quality Analysis", False,
                                "Should provide comprehensive quality analysis")
                    return False
                
                # Verify consensus validation structure
                consensus_validation = data.get("consensus_validation", {})
                if not isinstance(consensus_validation, dict) or len(consensus_validation) == 0:
                    self.log_test("Intelligent QA Analysis - Consensus Validation", False,
                                "Should provide consensus validation results")
                    return False
                
                # Verify final script exists and is substantial
                final_script = data.get("final_script", "")
                if not final_script or len(final_script) < 50:
                    self.log_test("Intelligent QA Analysis - Final Script", False,
                                "Final script should be substantial content")
                    return False
                
                # Verify confidence score
                confidence_score = data.get("confidence_score", 0)
                if not isinstance(confidence_score, (int, float)) or confidence_score < 0 or confidence_score > 1:
                    self.log_test("Intelligent QA Analysis - Confidence Score", False,
                                f"Invalid confidence score: {confidence_score} (should be 0-1)")
                    return False
                
                # Verify processing time
                processing_time = data.get("total_processing_time", 0)
                if not isinstance(processing_time, (int, float)) or processing_time < 0:
                    self.log_test("Intelligent QA Analysis - Processing Time", False,
                                f"Invalid processing time: {processing_time}")
                    return False
                
                regeneration_performed = data.get("regeneration_performed", False)
                threshold_met = data.get("quality_threshold_met", False)
                
                self.log_test("Intelligent QA Analysis", True,
                            f"Successfully analyzed in {processing_time:.1f}s, regeneration: {regeneration_performed}, threshold met: {threshold_met}, confidence: {confidence_score:.2f}")
                return True
                
            else:
                self.log_test("Intelligent QA Analysis", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Intelligent QA Analysis", False, f"Request failed: {str(e)}")
            return False
    
    def test_generate_script_with_qa(self):
        """Test Script Generation with QA endpoint - Generates script and automatically runs intelligent QA"""
        print("\n=== Testing Script Generation with QA Endpoint ===")
        
        payload = {
            "prompt": self.sample_prompt,
            "video_type": self.sample_video_type,
            "duration": self.sample_duration
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/generate-script-with-qa",
                json=payload,
                timeout=300  # Very long timeout for generation + QA
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # This endpoint should return both generation and QA results
                # Verify it has both script generation and QA analysis data
                
                # Check for script generation fields
                if "generated_script" not in data and "final_script" not in data:
                    self.log_test("Generate Script with QA - Script Generation", False,
                                "Should contain generated script")
                    return False
                
                # Check for QA analysis fields
                qa_fields = ["quality_analysis", "consensus_validation", "quality_threshold_met"]
                missing_qa_fields = [field for field in qa_fields if field not in data]
                if len(missing_qa_fields) == len(qa_fields):  # All QA fields missing
                    self.log_test("Generate Script with QA - QA Analysis", False,
                                "Should contain QA analysis results")
                    return False
                
                # Verify script content
                script_content = data.get("generated_script") or data.get("final_script", "")
                if not script_content or len(script_content) < 100:
                    self.log_test("Generate Script with QA - Script Content", False,
                                "Generated script should be substantial content")
                    return False
                
                # Check if QA was performed
                qa_performed = any(field in data for field in qa_fields)
                
                self.log_test("Generate Script with QA", True,
                            f"Successfully generated script ({len(script_content)} chars) with QA analysis: {qa_performed}")
                return True
                
            else:
                self.log_test("Generate Script with QA", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Generate Script with QA", False, f"Request failed: {str(e)}")
            return False
    
    def test_api_keys_functionality(self):
        """Test that all new API keys are working (Gemini #2, OpenRouter, Groq)"""
        print("\n=== Testing API Keys Functionality ===")
        
        # This is tested indirectly through the multi-model validation endpoint
        # which should use multiple API keys
        
        payload = {
            "script": "This is a test script to verify API keys are working properly.",
            "target_platform": "youtube",
            "duration": "short",
            "video_type": "general"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/multi-model-validation",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                individual_results = data.get("individual_results", [])
                
                # Check if we have results from multiple models (indicating multiple API keys work)
                if len(individual_results) >= 3:
                    model_names = [result.get("model_name", "") for result in individual_results]
                    unique_models = set(model_names)
                    
                    if len(unique_models) >= 3:
                        self.log_test("API Keys Functionality", True,
                                    f"Successfully used {len(unique_models)} different models: {', '.join(unique_models)}")
                        return True
                    else:
                        self.log_test("API Keys Functionality", False,
                                    f"Only {len(unique_models)} unique models used, expected at least 3")
                        return False
                else:
                    self.log_test("API Keys Functionality", False,
                                f"Only {len(individual_results)} model results, expected at least 3")
                    return False
            else:
                self.log_test("API Keys Functionality", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API Keys Functionality", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 5 tests"""
        print("🚀 Starting Phase 5: Intelligent Quality Assurance & Auto-Optimization Testing")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed. Stopping tests.")
            return False
        
        # Run all Phase 5 specific tests
        tests = [
            self.test_api_keys_functionality,
            self.test_multi_model_validation,
            self.test_advanced_quality_metrics,
            self.test_quality_improvement_optimization,
            self.test_ab_test_optimization,
            self.test_intelligent_qa_analysis,
            self.test_generate_script_with_qa
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                time.sleep(2)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 80)
        print(f"🎯 PHASE 5 TESTING SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ ALL PHASE 5 TESTS PASSED - System is fully functional!")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  MOST TESTS PASSED - Minor issues detected")
        else:
            print("❌ MULTIPLE FAILURES - Major issues detected")
        
        return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    tester = Phase5QATester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
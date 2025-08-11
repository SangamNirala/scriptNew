#!/usr/bin/env python3
"""
Phase 4.1 Enhanced Prompt Architecture Debug Test
=================================================

This test specifically focuses on debugging the critical error:
"'str' object has no attribute 'enable_template_caching'" 
occurring in enhanced_prompt_architecture.select_duration_template() method.

The test will:
1. Reproduce the exact error scenario
2. Debug the initialization and execution flow
3. Test all enhanced duration + video type combinations
4. Verify backward compatibility
5. Identify the root cause of the config attribute error
"""

import asyncio
import aiohttp
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List

# Configure logging for detailed debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase41EnhancedArchitectureDebugger:
    """Comprehensive debugger for Phase 4.1 Enhanced Prompt Architecture issues"""
    
    def __init__(self):
        self.base_url = "https://b03732ae-2f6a-4aa1-bcf3-86fe8377d488.preview.emergentagent.com/api"
        self.test_results = []
        self.error_details = []
        
    async def run_comprehensive_debug_tests(self):
        """Run comprehensive debugging tests for Phase 4.1"""
        logger.info("🔍 PHASE 4.1 ENHANCED PROMPT ARCHITECTURE DEBUG TEST STARTED")
        logger.info("=" * 80)
        
        try:
            # Test 1: Backend connectivity and basic health check
            await self.test_backend_connectivity()
            
            # Test 2: Enhanced duration error reproduction
            await self.test_enhanced_duration_error_reproduction()
            
            # Test 3: All enhanced duration + video type combinations
            await self.test_all_enhanced_combinations()
            
            # Test 4: Backward compatibility verification
            await self.test_backward_compatibility()
            
            # Test 5: Error handling for invalid durations
            await self.test_invalid_duration_handling()
            
            # Test 6: Enhanced metadata verification
            await self.test_enhanced_metadata()
            
            # Generate comprehensive debug report
            await self.generate_debug_report()
            
        except Exception as e:
            logger.error(f"❌ Critical test failure: {str(e)}")
            logger.error(traceback.format_exc())
            
    async def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        logger.info("🔗 Testing backend connectivity...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/") as response:
                    if response.status == 200:
                        logger.info("✅ Backend connectivity: PASSED")
                        self.test_results.append({
                            "test": "backend_connectivity",
                            "status": "PASSED",
                            "response_code": response.status
                        })
                    else:
                        logger.error(f"❌ Backend connectivity: FAILED (status: {response.status})")
                        self.test_results.append({
                            "test": "backend_connectivity", 
                            "status": "FAILED",
                            "response_code": response.status
                        })
        except Exception as e:
            logger.error(f"❌ Backend connectivity error: {str(e)}")
            self.test_results.append({
                "test": "backend_connectivity",
                "status": "ERROR", 
                "error": str(e)
            })
    
    async def test_enhanced_duration_error_reproduction(self):
        """Reproduce the specific 'enable_template_caching' attribute error"""
        logger.info("🐛 Testing enhanced duration error reproduction...")
        
        # Test cases that should trigger the error
        error_test_cases = [
            {"duration": "extended_15", "video_type": "educational"},
            {"duration": "extended_20", "video_type": "marketing"},
            {"duration": "extended_25", "video_type": "entertainment"}
        ]
        
        for test_case in error_test_cases:
            await self.test_single_enhanced_duration(
                test_case["duration"], 
                test_case["video_type"],
                f"error_reproduction_{test_case['duration']}_{test_case['video_type']}"
            )
    
    async def test_all_enhanced_combinations(self):
        """Test all enhanced duration + video type combinations"""
        logger.info("🎯 Testing all enhanced duration + video type combinations...")
        
        enhanced_durations = ["extended_15", "extended_20", "extended_25"]
        video_types = ["educational", "marketing", "entertainment", "general"]
        
        for duration in enhanced_durations:
            for video_type in video_types:
                await self.test_single_enhanced_duration(
                    duration, 
                    video_type,
                    f"enhanced_combination_{duration}_{video_type}"
                )
    
    async def test_single_enhanced_duration(self, duration: str, video_type: str, test_name: str):
        """Test a single enhanced duration + video type combination with detailed error tracking"""
        logger.info(f"🔍 Testing {test_name}: {duration} + {video_type}")
        
        test_payload = {
            "prompt": f"Create a comprehensive video about advanced {video_type} strategies and techniques",
            "video_type": video_type,
            "duration": duration
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate-script",
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            response_data = json.loads(response_text)
                            
                            # Check for enhanced metadata
                            metadata = response_data.get("generation_metadata", {})
                            has_enhanced_metadata = all(key in metadata for key in ["template_id", "template_name", "suitability_score"])
                            
                            logger.info(f"✅ {test_name}: SUCCESS")
                            logger.info(f"   - Script length: {len(response_data.get('generated_script', ''))}")
                            logger.info(f"   - Enhanced metadata: {'YES' if has_enhanced_metadata else 'NO'}")
                            if has_enhanced_metadata:
                                logger.info(f"   - Template ID: {metadata.get('template_id')}")
                                logger.info(f"   - Template Name: {metadata.get('template_name')}")
                                logger.info(f"   - Suitability Score: {metadata.get('suitability_score')}")
                            
                            self.test_results.append({
                                "test": test_name,
                                "status": "SUCCESS",
                                "duration": duration,
                                "video_type": video_type,
                                "script_length": len(response_data.get('generated_script', '')),
                                "enhanced_metadata": has_enhanced_metadata,
                                "metadata": metadata
                            })
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ {test_name}: JSON decode error")
                            logger.error(f"   Response text: {response_text[:500]}...")
                            self.test_results.append({
                                "test": test_name,
                                "status": "JSON_ERROR",
                                "error": str(e),
                                "response_preview": response_text[:500]
                            })
                    
                    elif response.status == 500:
                        # This is likely our target error
                        logger.error(f"❌ {test_name}: SERVER ERROR (500)")
                        logger.error(f"   Response: {response_text}")
                        
                        # Check if this is the specific error we're looking for
                        if "enable_template_caching" in response_text:
                            logger.error("🎯 FOUND TARGET ERROR: 'enable_template_caching' attribute error!")
                            self.error_details.append({
                                "test": test_name,
                                "error_type": "enable_template_caching_attribute_error",
                                "duration": duration,
                                "video_type": video_type,
                                "full_response": response_text,
                                "timestamp": datetime.utcnow().isoformat()
                            })
                        
                        self.test_results.append({
                            "test": test_name,
                            "status": "SERVER_ERROR",
                            "duration": duration,
                            "video_type": video_type,
                            "response_code": response.status,
                            "error_response": response_text
                        })
                    
                    elif response.status == 400:
                        logger.warning(f"⚠️ {test_name}: BAD REQUEST (400)")
                        logger.warning(f"   Response: {response_text}")
                        self.test_results.append({
                            "test": test_name,
                            "status": "BAD_REQUEST",
                            "duration": duration,
                            "video_type": video_type,
                            "response_code": response.status,
                            "error_response": response_text
                        })
                    
                    else:
                        logger.error(f"❌ {test_name}: UNEXPECTED STATUS ({response.status})")
                        logger.error(f"   Response: {response_text}")
                        self.test_results.append({
                            "test": test_name,
                            "status": "UNEXPECTED_STATUS",
                            "duration": duration,
                            "video_type": video_type,
                            "response_code": response.status,
                            "error_response": response_text
                        })
                        
        except asyncio.TimeoutError:
            logger.error(f"❌ {test_name}: TIMEOUT")
            self.test_results.append({
                "test": test_name,
                "status": "TIMEOUT",
                "duration": duration,
                "video_type": video_type
            })
            
        except Exception as e:
            logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
            logger.error(traceback.format_exc())
            self.test_results.append({
                "test": test_name,
                "status": "EXCEPTION",
                "duration": duration,
                "video_type": video_type,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
    
    async def test_backward_compatibility(self):
        """Test backward compatibility with short, medium, long durations"""
        logger.info("🔄 Testing backward compatibility...")
        
        standard_durations = ["short", "medium", "long"]
        video_types = ["educational", "marketing", "entertainment", "general"]
        
        for duration in standard_durations:
            for video_type in video_types:
                await self.test_single_standard_duration(duration, video_type)
    
    async def test_single_standard_duration(self, duration: str, video_type: str):
        """Test a single standard duration for backward compatibility"""
        test_name = f"backward_compatibility_{duration}_{video_type}"
        logger.info(f"🔄 Testing {test_name}")
        
        test_payload = {
            "prompt": f"Create a {duration} video about {video_type} content",
            "video_type": video_type,
            "duration": duration
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate-script",
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"✅ {test_name}: SUCCESS (backward compatibility maintained)")
                        self.test_results.append({
                            "test": test_name,
                            "status": "SUCCESS",
                            "duration": duration,
                            "video_type": video_type,
                            "script_length": len(response_data.get('generated_script', ''))
                        })
                    else:
                        response_text = await response.text()
                        logger.error(f"❌ {test_name}: FAILED (status: {response.status})")
                        self.test_results.append({
                            "test": test_name,
                            "status": "FAILED",
                            "duration": duration,
                            "video_type": video_type,
                            "response_code": response.status,
                            "error_response": response_text
                        })
                        
        except Exception as e:
            logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
            self.test_results.append({
                "test": test_name,
                "status": "EXCEPTION",
                "duration": duration,
                "video_type": video_type,
                "error": str(e)
            })
    
    async def test_invalid_duration_handling(self):
        """Test error handling for invalid durations"""
        logger.info("⚠️ Testing invalid duration handling...")
        
        invalid_durations = ["invalid_duration", "extended_30", "super_long", ""]
        
        for invalid_duration in invalid_durations:
            test_name = f"invalid_duration_{invalid_duration or 'empty'}"
            logger.info(f"⚠️ Testing {test_name}")
            
            test_payload = {
                "prompt": "Create a test video",
                "video_type": "general",
                "duration": invalid_duration
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/generate-script",
                        json=test_payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status == 400:
                            logger.info(f"✅ {test_name}: Correctly returned 400 Bad Request")
                            self.test_results.append({
                                "test": test_name,
                                "status": "CORRECT_ERROR_HANDLING",
                                "duration": invalid_duration,
                                "response_code": response.status
                            })
                        elif response.status == 500:
                            response_text = await response.text()
                            logger.error(f"❌ {test_name}: Should return 400, got 500")
                            logger.error(f"   Response: {response_text}")
                            self.test_results.append({
                                "test": test_name,
                                "status": "INCORRECT_ERROR_CODE",
                                "duration": invalid_duration,
                                "response_code": response.status,
                                "error_response": response_text
                            })
                        else:
                            response_text = await response.text()
                            logger.warning(f"⚠️ {test_name}: Unexpected status {response.status}")
                            self.test_results.append({
                                "test": test_name,
                                "status": "UNEXPECTED_RESPONSE",
                                "duration": invalid_duration,
                                "response_code": response.status,
                                "error_response": response_text
                            })
                            
            except Exception as e:
                logger.error(f"❌ {test_name}: EXCEPTION - {str(e)}")
                self.test_results.append({
                    "test": test_name,
                    "status": "EXCEPTION",
                    "duration": invalid_duration,
                    "error": str(e)
                })
    
    async def test_enhanced_metadata(self):
        """Test enhanced metadata fields in successful responses"""
        logger.info("📊 Testing enhanced metadata verification...")
        
        # Test one successful case to verify metadata structure
        test_payload = {
            "prompt": "Create a comprehensive educational video about machine learning fundamentals",
            "video_type": "educational",
            "duration": "medium"  # Use standard duration first to ensure success
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate-script",
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        metadata = response_data.get("generation_metadata", {})
                        
                        logger.info("✅ Enhanced metadata test: SUCCESS")
                        logger.info(f"   - Metadata keys: {list(metadata.keys())}")
                        
                        # Check for enhanced fields
                        enhanced_fields = ["template_id", "template_name", "suitability_score"]
                        has_enhanced_fields = all(field in metadata for field in enhanced_fields)
                        
                        self.test_results.append({
                            "test": "enhanced_metadata_verification",
                            "status": "SUCCESS",
                            "metadata_keys": list(metadata.keys()),
                            "has_enhanced_fields": has_enhanced_fields,
                            "metadata": metadata
                        })
                    else:
                        response_text = await response.text()
                        logger.error(f"❌ Enhanced metadata test: FAILED (status: {response.status})")
                        self.test_results.append({
                            "test": "enhanced_metadata_verification",
                            "status": "FAILED",
                            "response_code": response.status,
                            "error_response": response_text
                        })
                        
        except Exception as e:
            logger.error(f"❌ Enhanced metadata test: EXCEPTION - {str(e)}")
            self.test_results.append({
                "test": "enhanced_metadata_verification",
                "status": "EXCEPTION",
                "error": str(e)
            })
    
    async def generate_debug_report(self):
        """Generate comprehensive debug report"""
        logger.info("📋 Generating comprehensive debug report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] in ["SUCCESS", "CORRECT_ERROR_HANDLING"]])
        failed_tests = len([r for r in self.test_results if r["status"] not in ["SUCCESS", "CORRECT_ERROR_HANDLING"]])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Count specific error types
        enable_caching_errors = len([e for e in self.error_details if e["error_type"] == "enable_template_caching_attribute_error"])
        
        # Enhanced duration test results
        enhanced_tests = [r for r in self.test_results if r.get("test", "").startswith("enhanced_combination_")]
        enhanced_success = len([r for r in enhanced_tests if r["status"] == "SUCCESS"])
        enhanced_total = len(enhanced_tests)
        enhanced_success_rate = (enhanced_success / enhanced_total * 100) if enhanced_total > 0 else 0
        
        # Backward compatibility results
        backward_tests = [r for r in self.test_results if r.get("test", "").startswith("backward_compatibility_")]
        backward_success = len([r for r in backward_tests if r["status"] == "SUCCESS"])
        backward_total = len(backward_tests)
        backward_success_rate = (backward_success / backward_total * 100) if backward_total > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🔍 PHASE 4.1 ENHANCED PROMPT ARCHITECTURE DEBUG REPORT")
        logger.info("=" * 80)
        logger.info(f"📊 OVERALL STATISTICS:")
        logger.info(f"   - Total Tests: {total_tests}")
        logger.info(f"   - Successful Tests: {successful_tests}")
        logger.info(f"   - Failed Tests: {failed_tests}")
        logger.info(f"   - Success Rate: {success_rate:.1f}%")
        logger.info("")
        logger.info(f"🎯 ENHANCED FEATURES TESTING:")
        logger.info(f"   - Enhanced Duration Tests: {enhanced_total}")
        logger.info(f"   - Enhanced Success: {enhanced_success}")
        logger.info(f"   - Enhanced Success Rate: {enhanced_success_rate:.1f}%")
        logger.info("")
        logger.info(f"🔄 BACKWARD COMPATIBILITY:")
        logger.info(f"   - Backward Compatibility Tests: {backward_total}")
        logger.info(f"   - Backward Success: {backward_success}")
        logger.info(f"   - Backward Success Rate: {backward_success_rate:.1f}%")
        logger.info("")
        logger.info(f"🐛 CRITICAL ERROR ANALYSIS:")
        logger.info(f"   - 'enable_template_caching' Errors: {enable_caching_errors}")
        
        if enable_caching_errors > 0:
            logger.info("   - ERROR DETAILS:")
            for error in self.error_details:
                if error["error_type"] == "enable_template_caching_attribute_error":
                    logger.info(f"     * Test: {error['test']}")
                    logger.info(f"     * Duration: {error['duration']}")
                    logger.info(f"     * Video Type: {error['video_type']}")
                    logger.info(f"     * Timestamp: {error['timestamp']}")
                    # Show first 500 chars of error response
                    error_preview = error['full_response'][:500] + "..." if len(error['full_response']) > 500 else error['full_response']
                    logger.info(f"     * Error Preview: {error_preview}")
                    logger.info("")
        
        logger.info("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] in ["SUCCESS", "CORRECT_ERROR_HANDLING"] else "❌"
            logger.info(f"   {status_emoji} {result['test']}: {result['status']}")
            if result.get("duration") and result.get("video_type"):
                logger.info(f"      Duration: {result['duration']}, Video Type: {result['video_type']}")
            if result.get("script_length"):
                logger.info(f"      Script Length: {result['script_length']} chars")
            if result.get("enhanced_metadata"):
                logger.info(f"      Enhanced Metadata: {result['enhanced_metadata']}")
            if result.get("error"):
                logger.info(f"      Error: {result['error']}")
        
        logger.info("=" * 80)
        logger.info("🔍 DEBUG TEST COMPLETED")
        logger.info("=" * 80)

async def main():
    """Main test execution function"""
    debugger = Phase41EnhancedArchitectureDebugger()
    await debugger.run_comprehensive_debug_tests()

if __name__ == "__main__":
    asyncio.run(main())
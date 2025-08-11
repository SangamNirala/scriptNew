#!/usr/bin/env python3
"""
Phase 5.1: Template Initialization and Testing Fix
Initialize templates properly before running comprehensive tests
"""

import sys
import os
import asyncio
import json
import uuid
import time
from datetime import datetime
import logging

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def initialize_templates_for_testing():
    """Initialize templates in the registry for testing"""
    try:
        from server import (
            prompt_template_registry,
            duration_specific_prompt_generator
        )
        
        logger.info("🚀 Initializing templates for testing...")
        
        # Create and register 15-20 minute template
        template_15_20 = duration_specific_prompt_generator.create_15_20_minute_template()
        template_content_15_20 = template_15_20["template_content"]
        await prompt_template_registry.register_template(
            duration="extended_15",
            template_content=template_content_15_20,
            template_name="15-20 Minute Content Specialist",
            description="Professional template for 15-20 minute video content with specialized expertise",
            expertise_areas=["Medium-form content", "Segment coordination", "Engagement optimization"],
            complexity_level="moderate",
            focus_strategy="balanced_pacing_engagement",
            tags=["extended", "specialist", "medium-form"]
        )
        logger.info("✅ Registered 15-20 minute template")
        
        # Create and register 20-25 minute template  
        template_20_25 = duration_specific_prompt_generator.create_20_25_minute_template()
        template_content_20_25 = template_20_25["template_content"]
        await prompt_template_registry.register_template(
            duration="extended_20",
            template_content=template_content_20_25,
            template_name="20-25 Minute Deep Dive Expert",
            description="Expert template for 20-25 minute deep dive video content",
            expertise_areas=["Long-form content", "Deep dive methodology", "Complex structuring"],
            complexity_level="advanced",
            focus_strategy="sustained_engagement_algorithms",
            tags=["extended", "expert", "deep-dive"]
        )
        logger.info("✅ Registered 20-25 minute template")
        
        # Create and register 25-30 minute template
        template_25_30 = duration_specific_prompt_generator.create_25_30_minute_template()
        template_content_25_30 = template_25_30["template_content"]
        await prompt_template_registry.register_template(
            duration="extended_25",
            template_content=template_content_25_30,
            template_name="25-30 Minute Comprehensive Content Architect",
            description="Elite template for 25-30 minute comprehensive video content with broadcast quality",
            expertise_areas=["Comprehensive architecture", "Elite coordination", "Broadcast quality"],
            complexity_level="expert",
            focus_strategy="peak_engagement_distribution",
            tags=["extended", "architect", "comprehensive"]
        )
        logger.info("✅ Registered 25-30 minute template")
        
        # Verify templates are registered
        templates = await prompt_template_registry.list_available_templates()
        logger.info(f"🎉 Template initialization completed successfully. Total templates: {len(templates)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Template initialization failed: {str(e)}")
        raise e

async def main():
    """Initialize templates and run testing"""
    try:
        # Initialize templates first
        await initialize_templates_for_testing()
        
        # Now run the comprehensive testing suite
        from tests.phase_5_1_comprehensive_testing_suite import Phase51ComprehensiveTestingSuite
        
        test_suite = Phase51ComprehensiveTestingSuite()
        results = await test_suite.run_all_tests()
        
        # Save results to file
        results_file = "/app/backend/tests/phase_5_1_test_results.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n💾 Test results saved to: {results_file}")
        
        # Return appropriate exit code
        success_rate = results["summary"]["success_rate"]
        if success_rate >= 90:
            logger.info("🎉 EXCELLENT: All systems operational!")
            return 0
        elif success_rate >= 75:
            logger.info("✅ GOOD: Most systems operational with minor issues")
            return 0
        elif success_rate >= 50:
            logger.warning("⚠️  WARNING: Significant issues detected")
            return 1
        else:
            logger.error("🚨 CRITICAL: Major system failures detected")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Testing execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
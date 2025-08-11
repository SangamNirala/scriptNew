#!/usr/bin/env python3
"""
Phase 4.2: Enhanced Prompt Template API - Detailed Response Validation Test

This test validates the actual content and structure of API responses to ensure they meet
all the specific requirements mentioned in the review request.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Backend URL Configuration
BACKEND_URL = "https://692556dc-9a80-418a-8d12-65b2cbc6f397.preview.emergentagent.com/api"

class DetailedResponseValidator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        
    async def run_detailed_validation(self):
        """Run detailed response validation tests"""
        print("🔍 PHASE 4.2: DETAILED RESPONSE VALIDATION TESTING")
        print("=" * 80)
        
        await self.test_template_list_content()
        await self.test_template_generation_content()
        await self.test_duration_specific_content()
        await self.test_compatibility_analysis_content()
        
        print("\n✅ Detailed response validation completed")
    
    async def test_template_list_content(self):
        """Test the content of template list response"""
        print("\n📋 Testing Template List Response Content...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.backend_url}/enhanced-prompt-templates") as response:
                data = await response.json()
        
        print(f"✅ Status: {response.status}")
        print(f"✅ Total Templates: {data['total_templates']}")
        
        # Check available templates
        templates = data['available_templates']
        print(f"✅ Available Templates: {len(templates)}")
        
        for template in templates:
            print(f"   📄 {template['template_name']} ({template['duration']})")
            print(f"      - Complexity: {template['complexity_level']}")
            print(f"      - Focus: {template['focus_strategy']}")
            print(f"      - Word Count: {template['word_count']}")
            print(f"      - Expertise Areas: {', '.join(template['expertise_areas'])}")
        
        # Check registry info
        registry_info = data['registry_info']
        print(f"✅ Registry Info:")
        print(f"   - Registry ID: {registry_info.get('registry_id')}")
        print(f"   - Total Templates in Registry: {registry_info.get('total_templates_in_registry')}")
        print(f"   - Active Templates: {registry_info.get('active_templates')}")
        print(f"   - Total Usage: {registry_info.get('total_usage')}")
    
    async def test_template_generation_content(self):
        """Test template generation response content"""
        print("\n🧪 Testing Template Generation Response Content...")
        
        payload = {
            "duration": "extended_20",
            "video_type": "educational",
            "enable_customization": True,
            "customization_options": {
                "focus_area": "learning_objectives",
                "complexity_level": "advanced"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.backend_url}/enhanced-prompt-templates", json=payload) as response:
                data = await response.json()
        
        print(f"✅ Status: {response.status}")
        
        # Check template info
        template_info = data['template_info']
        print(f"✅ Template Info:")
        print(f"   - Template ID: {template_info['template_id']}")
        print(f"   - Template Name: {template_info['template_name']}")
        print(f"   - Duration: {template_info['duration']}")
        print(f"   - Video Type: {template_info['video_type']}")
        print(f"   - Suitability Score: {template_info['suitability_score']}")
        
        # Check enhanced system prompt
        prompt = data['enhanced_system_prompt']
        print(f"✅ Enhanced System Prompt: {len(prompt)} characters")
        print(f"   Preview: {prompt[:200]}...")
        
        # Check segmentation compatibility
        segmentation = data['segmentation_compatibility']
        print(f"✅ Segmentation Compatibility:")
        print(f"   - Compatible: {segmentation.get('compatible')}")
        print(f"   - Analysis: {len(str(segmentation))} chars")
        
        # Check customizations applied
        customizations = data['customizations_applied']
        print(f"✅ Customizations Applied: {len(customizations)}")
        for customization in customizations:
            print(f"   - {customization}")
        
        # Check generation metadata
        metadata = data['generation_metadata']
        print(f"✅ Generation Metadata:")
        print(f"   - Test Generation: {metadata.get('test_generation')}")
        print(f"   - Template Selected: {metadata.get('template_selected')}")
        print(f"   - Prompt Length: {metadata.get('prompt_length_chars')}")
        print(f"   - Customization Enabled: {metadata.get('customization_enabled')}")
    
    async def test_duration_specific_content(self):
        """Test duration-specific endpoint content"""
        print("\n⏱️ Testing Duration-Specific Response Content...")
        
        # Test GET endpoint
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.backend_url}/enhanced-prompt-templates/extended_25") as response:
                data = await response.json()
        
        print(f"✅ GET Status: {response.status}")
        
        # Check template details
        details = data['template_details']
        print(f"✅ Template Details:")
        print(f"   - Template ID: {details['template_id']}")
        print(f"   - Duration: {details['duration']}")
        print(f"   - Template Name: {details['template_name']}")
        print(f"   - Description: {details['description'][:100]}...")
        
        # Check specifications
        specs = data['template_specifications']
        print(f"✅ Template Specifications:")
        print(f"   - Complexity Level: {specs['complexity_level']}")
        print(f"   - Focus Strategy: {specs['focus_strategy']}")
        print(f"   - Word Count: {specs['word_count']}")
        print(f"   - Expertise Areas: {', '.join(specs['expertise_areas'])}")
        
        # Check integration compatibility
        integration = data['integration_compatibility']
        print(f"✅ Integration Compatibility:")
        for key, value in integration.items():
            print(f"   - {key.replace('_', ' ').title()}: {value}")
        
        # Test POST endpoint
        payload = {
            "duration": "extended_25",
            "video_type": "marketing",
            "enable_customization": True,
            "customization_options": {
                "tone": "persuasive",
                "focus_area": "conversion_optimization"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.backend_url}/enhanced-prompt-templates/extended_25", json=payload) as response:
                data = await response.json()
        
        print(f"✅ POST Status: {response.status}")
        print(f"✅ Enhanced Prompt Length: {len(data['enhanced_system_prompt'])} characters")
        print(f"✅ Customizations Applied: {len(data['customizations_applied'])}")
    
    async def test_compatibility_analysis_content(self):
        """Test compatibility validation response content"""
        print("\n🔍 Testing Compatibility Analysis Content...")
        
        payload = {
            "duration": "extended_20",
            "segmentation_plan": {
                "total_segments": 4,
                "segment_duration_minutes": 5.5,
                "total_duration_minutes": 22,
                "complexity_level": "advanced",
                "focus_strategy": "sustained_engagement_algorithms"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.backend_url}/validate-template-compatibility", json=payload) as response:
                data = await response.json()
        
        print(f"✅ Status: {response.status}")
        print(f"✅ Compatible: {data['compatible']}")
        print(f"✅ Compatibility Score: {data['compatibility_score']:.3f}")
        
        # Check analysis details
        analysis = data['analysis']
        print(f"✅ Analysis:")
        print(f"   - Overall Assessment: {analysis['overall_assessment']}")
        
        detailed_analysis = analysis['detailed_analysis']
        print(f"✅ Detailed Analysis:")
        for key, value in detailed_analysis.items():
            if isinstance(value, dict) and 'compatible' in value:
                print(f"   - {key.replace('_', ' ').title()}: {value['compatible']}")
        
        # Check recommendations
        recommendations = data['recommendations']
        print(f"✅ Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Check template info in analysis
        template_info = analysis['template_info']
        print(f"✅ Template Info in Analysis:")
        print(f"   - Template Name: {template_info['template_name']}")
        print(f"   - Complexity Level: {template_info['complexity_level']}")
        print(f"   - Focus Strategy: {template_info['focus_strategy']}")

async def main():
    """Main test execution"""
    validator = DetailedResponseValidator()
    await validator.run_detailed_validation()

if __name__ == "__main__":
    asyncio.run(main())
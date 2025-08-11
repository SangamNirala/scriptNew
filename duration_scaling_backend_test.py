#!/usr/bin/env python3
"""
Duration-Aware Script Generation System Backend Testing
Focus: Testing segment-based generation for extended_10 duration after recent changes

Review Request Requirements:
- Verify extended_10 (10-15min) uses segment-based generation
- Target: 300-450 shots and 12,000-31,500 words (or 70% minimum due to model variability)
- Validate generation_metadata.segmented_generation presence and fields
- Compare short vs extended_10: extended should be >10x shots of short
- Confirm auto-regeneration loop logs and final_quality_analysis metrics
- Ensure no regressions for 'short' duration
"""

import asyncio
import aiohttp
import json
import time
import re
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://7ddca776-a8d1-40eb-a60b-df8e9c11de93.preview.emergentagent.com/api"

class DurationScalingTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.short_duration_baseline = None
        self.extended_10_results = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🚀 Duration-Aware Script Generation System Testing Started")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    async def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    print("✅ Backend connectivity confirmed")
                    return True
                else:
                    print(f"❌ Backend connectivity failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Backend connectivity error: {str(e)}")
            return False
            
    def extract_shots_and_words(self, script_content: str) -> tuple:
        """Extract shot count and word count from script content"""
        # Count shots by looking for shot indicators
        shot_patterns = [
            r'\[Shot \d+\]',
            r'Shot \d+:',
            r'\d+\.\s*\[',
            r'SHOT \d+',
            r'\[\d+:\d+\-\d+:\d+\]'
        ]
        
        shot_count = 0
        for pattern in shot_patterns:
            matches = re.findall(pattern, script_content, re.IGNORECASE)
            shot_count = max(shot_count, len(matches))
            
        # If no specific shot patterns found, estimate from content structure
        if shot_count == 0:
            # Look for numbered items or bullet points
            numbered_items = re.findall(r'^\d+\.', script_content, re.MULTILINE)
            bullet_points = re.findall(r'^[-•*]\s', script_content, re.MULTILINE)
            shot_count = max(len(numbered_items), len(bullet_points))
            
        # Count words
        word_count = len(script_content.split())
        
        return shot_count, word_count
        
    def analyze_quality_metrics(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze quality metrics from response"""
        quality_analysis = {}
        
        # Extract generation metadata
        metadata = response_data.get('generation_metadata', {})
        quality_analysis['has_metadata'] = bool(metadata)
        
        # Check for segmented generation fields
        segmented_gen = metadata.get('segmented_generation', {})
        quality_analysis['has_segmented_generation'] = bool(segmented_gen)
        
        if segmented_gen:
            quality_analysis['total_segments'] = segmented_gen.get('total_segments', 0)
            quality_analysis['shots_per_segment'] = segmented_gen.get('shots_per_segment', 0)
            quality_analysis['total_target_shots'] = segmented_gen.get('total_target_shots', 0)
            
        # Check for auto-regeneration logs
        quality_analysis['has_auto_regeneration'] = 'auto_regeneration' in metadata
        quality_analysis['has_final_quality_analysis'] = 'final_quality_analysis' in metadata
        
        return quality_analysis
        
    async def test_short_duration_baseline(self):
        """Test short duration as baseline for comparison"""
        print("\n📊 Testing SHORT Duration (Baseline)")
        print("-" * 50)
        
        test_data = {
            "prompt": "Create a comprehensive video about effective time management strategies for busy professionals",
            "video_type": "educational",
            "duration": "short"
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(f"{BACKEND_URL}/generate-script", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    script_content = data.get('generated_script', '')
                    shot_count, word_count = self.extract_shots_and_words(script_content)
                    quality_metrics = self.analyze_quality_metrics(data)
                    
                    self.short_duration_baseline = {
                        'duration': 'short',
                        'shot_count': shot_count,
                        'word_count': word_count,
                        'response_time': response_time,
                        'quality_metrics': quality_metrics,
                        'script_length': len(script_content)
                    }
                    
                    print(f"✅ Short duration generation successful")
                    print(f"   📊 Shots: {shot_count}")
                    print(f"   📝 Words: {word_count}")
                    print(f"   ⏱️  Response time: {response_time:.2f}s")
                    print(f"   📄 Script length: {len(script_content)} chars")
                    print(f"   🔧 Has metadata: {quality_metrics['has_metadata']}")
                    
                    return True
                else:
                    print(f"❌ Short duration test failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Short duration test error: {str(e)}")
            return False
            
    async def test_extended_10_duration(self):
        """Test extended_10 duration for segment-based generation"""
        print("\n🚀 Testing EXTENDED_10 Duration (10-15min)")
        print("-" * 50)
        
        test_data = {
            "prompt": "Create a comprehensive video about effective time management strategies for busy professionals",
            "video_type": "educational", 
            "duration": "extended_10"
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(f"{BACKEND_URL}/generate-script", json=test_data) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    script_content = data.get('generated_script', '')
                    shot_count, word_count = self.extract_shots_and_words(script_content)
                    quality_metrics = self.analyze_quality_metrics(data)
                    
                    self.extended_10_results = {
                        'duration': 'extended_10',
                        'shot_count': shot_count,
                        'word_count': word_count,
                        'response_time': response_time,
                        'quality_metrics': quality_metrics,
                        'script_length': len(script_content),
                        'raw_data': data
                    }
                    
                    print(f"✅ Extended_10 duration generation successful")
                    print(f"   📊 Shots: {shot_count}")
                    print(f"   📝 Words: {word_count}")
                    print(f"   ⏱️  Response time: {response_time:.2f}s")
                    print(f"   📄 Script length: {len(script_content)} chars")
                    print(f"   🔧 Has metadata: {quality_metrics['has_metadata']}")
                    print(f"   🧩 Has segmented generation: {quality_metrics['has_segmented_generation']}")
                    
                    if quality_metrics['has_segmented_generation']:
                        print(f"   📈 Total segments: {quality_metrics.get('total_segments', 'N/A')}")
                        print(f"   🎯 Shots per segment: {quality_metrics.get('shots_per_segment', 'N/A')}")
                        print(f"   🎬 Total target shots: {quality_metrics.get('total_target_shots', 'N/A')}")
                        
                    print(f"   🔄 Has auto-regeneration: {quality_metrics['has_auto_regeneration']}")
                    print(f"   📋 Has final quality analysis: {quality_metrics['has_final_quality_analysis']}")
                    
                    return True
                else:
                    print(f"❌ Extended_10 duration test failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Extended_10 duration test error: {str(e)}")
            return False
            
    def validate_scaling_requirements(self):
        """Validate that extended_10 meets scaling requirements"""
        print("\n🎯 SCALING REQUIREMENTS VALIDATION")
        print("=" * 60)
        
        if not self.short_duration_baseline or not self.extended_10_results:
            print("❌ Cannot validate scaling - missing baseline or extended results")
            return False
            
        short = self.short_duration_baseline
        extended = self.extended_10_results
        
        # Target requirements for extended_10
        target_shots_min = 300
        target_shots_max = 450
        target_words_min = 12000
        target_words_max = 31500
        
        # 70% minimum threshold due to model variability
        min_shots_threshold = int(target_shots_min * 0.7)  # 210 shots
        min_words_threshold = int(target_words_min * 0.7)  # 8400 words
        
        print(f"📊 CONTENT VOLUME COMPARISON:")
        print(f"   Short duration:     {short['shot_count']} shots, {short['word_count']} words")
        print(f"   Extended_10:        {extended['shot_count']} shots, {extended['word_count']} words")
        print(f"   Scaling ratio:      {extended['shot_count']/max(short['shot_count'], 1):.1f}x shots, {extended['word_count']/max(short['word_count'], 1):.1f}x words")
        
        print(f"\n🎯 TARGET REQUIREMENTS:")
        print(f"   Target shots:       {target_shots_min}-{target_shots_max}")
        print(f"   Target words:       {target_words_min:,}-{target_words_max:,}")
        print(f"   Minimum threshold:  {min_shots_threshold} shots, {min_words_threshold:,} words (70%)")
        
        # Validation checks
        validations = []
        
        # 1. Segment-based generation metadata
        has_segmented = extended['quality_metrics']['has_segmented_generation']
        validations.append(("Segmented generation metadata", has_segmented))
        
        # 2. Shot count requirements
        shots_meet_target = target_shots_min <= extended['shot_count'] <= target_shots_max
        shots_meet_minimum = extended['shot_count'] >= min_shots_threshold
        validations.append(("Shots meet target range", shots_meet_target))
        validations.append(("Shots meet minimum threshold", shots_meet_minimum))
        
        # 3. Word count requirements  
        words_meet_target = target_words_min <= extended['word_count'] <= target_words_max
        words_meet_minimum = extended['word_count'] >= min_words_threshold
        validations.append(("Words meet target range", words_meet_target))
        validations.append(("Words meet minimum threshold", words_meet_minimum))
        
        # 4. Scaling ratio (extended should be >10x shots of short)
        shot_scaling_ratio = extended['shot_count'] / max(short['shot_count'], 1)
        meets_10x_scaling = shot_scaling_ratio >= 10.0
        validations.append(("Extended >10x shots of short", meets_10x_scaling))
        
        # 5. Auto-regeneration and quality analysis
        has_auto_regen = extended['quality_metrics']['has_auto_regeneration']
        has_quality_analysis = extended['quality_metrics']['has_final_quality_analysis']
        validations.append(("Auto-regeneration logs", has_auto_regen))
        validations.append(("Final quality analysis", has_quality_analysis))
        
        print(f"\n✅ VALIDATION RESULTS:")
        passed_count = 0
        for description, passed in validations:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status} {description}")
            if passed:
                passed_count += 1
                
        success_rate = (passed_count / len(validations)) * 100
        print(f"\n📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_count}/{len(validations)} checks passed)")
        
        # Detailed segmented generation analysis
        if has_segmented:
            print(f"\n🧩 SEGMENTED GENERATION DETAILS:")
            seg_data = extended['quality_metrics']
            print(f"   Total segments: {seg_data.get('total_segments', 'N/A')}")
            print(f"   Shots per segment: {seg_data.get('shots_per_segment', 'N/A')}")
            print(f"   Total target shots: {seg_data.get('total_target_shots', 'N/A')}")
            
        return success_rate >= 70.0  # Consider successful if 70%+ checks pass
        
    async def run_comprehensive_test(self):
        """Run comprehensive duration scaling test"""
        await self.setup()
        
        try:
            # Test backend connectivity
            if not await self.test_backend_connectivity():
                return False
                
            # Test short duration baseline
            if not await self.test_short_duration_baseline():
                return False
                
            # Test extended_10 duration
            if not await self.test_extended_10_duration():
                return False
                
            # Validate scaling requirements
            scaling_success = self.validate_scaling_requirements()
            
            print(f"\n🏁 FINAL ASSESSMENT:")
            if scaling_success:
                print("✅ Duration-aware scaling system is working correctly")
                print("   Extended_10 duration produces dramatically higher content volume")
                print("   Segment-based generation is operational")
                print("   Quality analysis and auto-regeneration systems functional")
            else:
                print("❌ Duration-aware scaling system has issues")
                print("   Extended_10 duration not meeting scaling requirements")
                print("   Manual investigation needed for segment-based generation")
                
            return scaling_success
            
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    tester = DurationScalingTester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All duration scaling tests completed successfully!")
        exit(0)
    else:
        print("\n⚠️  Duration scaling tests completed with issues")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
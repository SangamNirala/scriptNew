#!/usr/bin/env python3
"""
Phase 1 Enhanced Prompt Improvements Testing Script
Tests for exact section headers and requirements from Phase 1 review request
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "https://26eacdda-b626-4083-882f-12e26aea3e2a.preview.emergentagent.com/api"

class Phase1ComplianceTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
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
    
    def test_phase_1_enhanced_prompt_improvements(self):
        """Test Phase 1 enhanced prompt improvements with exact validation requirements"""
        print("\n🔍 === TESTING PHASE 1 ENHANCED PROMPT IMPROVEMENTS ===")
        
        # Exact payload from review request
        test_prompt = "Create a video about productivity tips for remote workers"
        payload = {
            "original_prompt": test_prompt,
            "video_type": "educational",
            "industry_focus": "general",
            "duration": "medium"
        }
        
        try:
            print("🚀 Sending request to /api/enhance-prompt...")
            response = self.session.post(
                f"{self.backend_url}/enhance-prompt",
                json=payload,
                timeout=120  # Extended timeout for complex processing
            )
            
            if response.status_code != 200:
                self.log_test("Phase 1 - HTTP Response", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return 0
            
            data = response.json()
            print("📄 Response received, analyzing structure...")
            
            # Initialize validation results
            validations_passed = 0
            total_validations = 6
            
            # Get emotional variation (first variation typically focuses on emotional engagement)
            emotional_variation = None
            if "enhancement_variations" in data:
                for variation in data["enhancement_variations"]:
                    if "emotional" in variation.get("focus_strategy", "").lower():
                        emotional_variation = variation
                        break
                # Fallback to first variation if no emotional strategy found
                if not emotional_variation and data["enhancement_variations"]:
                    emotional_variation = data["enhancement_variations"][0]
            
            if not emotional_variation:
                self.log_test("Phase 1 - Emotional Variation", False, 
                            "No emotional variation found in response")
                return 0
            
            enhanced_prompt = emotional_variation.get("enhanced_prompt", "")
            
            # ===============================
            # CRITICAL VALIDATION 1: Exact Section Headers
            # ===============================
            required_sections = [
                "🎣 HOOK SECTION (0-3 seconds) - WORD COUNT: 25",
                "🎬 SETUP SECTION (3-15 seconds) - WORD COUNT: 50", 
                "📚 CONTENT CORE (15-80% duration) - WORD COUNT: 250",
                "🏆 CLIMAX MOMENT (80-90% duration) - WORD COUNT: 35",
                "✨ RESOLUTION (90-100% duration) - WORD COUNT: 40"
            ]
            
            sections_found = 0
            for section in required_sections:
                if section in enhanced_prompt:
                    sections_found += 1
                    print(f"   ✅ Found: {section}")
                else:
                    print(f"   ❌ Missing: {section}")
            
            if sections_found == len(required_sections):
                self.log_test("VALIDATION 1 - Exact Section Headers", True,
                            f"All {len(required_sections)} required section headers found")
                validations_passed += 1
            else:
                self.log_test("VALIDATION 1 - Exact Section Headers", False,
                            f"Only {sections_found}/{len(required_sections)} section headers found")
            
            # ===============================
            # CRITICAL VALIDATION 2: Additional Required Sections
            # ===============================
            additional_sections = [
                "🧠 PSYCHOLOGICAL TRIGGERS INTEGRATED:",
                "📲 2025 TRENDS & PLATFORM OPTIMIZATION:",
                "⚡ RETENTION ENGINEERING ELEMENTS:"
            ]
            
            additional_found = 0
            for section in additional_sections:
                if section in enhanced_prompt:
                    additional_found += 1
                    print(f"   ✅ Found: {section}")
                else:
                    print(f"   ❌ Missing: {section}")
            
            if additional_found == len(additional_sections):
                self.log_test("VALIDATION 2 - Additional Required Sections", True,
                            f"All {len(additional_sections)} additional sections found")
                validations_passed += 1
            else:
                self.log_test("VALIDATION 2 - Additional Required Sections", False,
                            f"Only {additional_found}/{len(additional_sections)} additional sections found")
            
            # ===============================
            # CRITICAL VALIDATION 3: Word Count Specifications
            # ===============================
            word_count_specs = ["WORD COUNT: 25", "WORD COUNT: 50", "WORD COUNT: 250", 
                              "WORD COUNT: 35", "WORD COUNT: 40"]
            word_counts_found = 0
            for spec in word_count_specs:
                if spec in enhanced_prompt:
                    word_counts_found += 1
            
            if word_counts_found == len(word_count_specs):
                self.log_test("VALIDATION 3 - Word Count Specifications", True,
                            f"All {len(word_count_specs)} word count specifications found")
                validations_passed += 1
            else:
                self.log_test("VALIDATION 3 - Word Count Specifications", False,
                            f"Only {word_counts_found}/{len(word_count_specs)} word count specifications found")
            
            # ===============================
            # CRITICAL VALIDATION 4: Psychological Triggers
            # ===============================
            psychological_triggers = ["FOMO", "Social Proof", "Authority", "Reciprocity", "Commitment"]
            triggers_found = 0
            for trigger in psychological_triggers:
                if trigger.lower() in enhanced_prompt.lower():
                    triggers_found += 1
                    print(f"   ✅ Found psychological trigger: {trigger}")
            
            if triggers_found >= 3:  # At least 3 out of 5 triggers should be present
                self.log_test("VALIDATION 4 - Psychological Triggers", True,
                            f"{triggers_found}/{len(psychological_triggers)} psychological triggers found")
                validations_passed += 1
            else:
                self.log_test("VALIDATION 4 - Psychological Triggers", False,
                            f"Only {triggers_found}/{len(psychological_triggers)} psychological triggers found")
            
            # ===============================
            # CRITICAL VALIDATION 5: 2025 Trends and Seasonal Relevance
            # ===============================
            trends_keywords = ["2025", "trend", "seasonal", "current", "latest", "platform optimization"]
            trends_found = 0
            for keyword in trends_keywords:
                if keyword.lower() in enhanced_prompt.lower():
                    trends_found += 1
                    print(f"   ✅ Found 2025 trend keyword: {keyword}")
            
            if trends_found >= 2:  # At least 2 trend-related keywords
                self.log_test("VALIDATION 5 - 2025 Trends & Seasonal Relevance", True,
                            f"{trends_found}/{len(trends_keywords)} trend-related keywords found")
                validations_passed += 1
            else:
                self.log_test("VALIDATION 5 - 2025 Trends & Seasonal Relevance", False,
                            f"Only {trends_found}/{len(trends_keywords)} trend-related keywords found")
            
            # ===============================
            # CRITICAL VALIDATION 6: Retention Engineering Elements
            # ===============================
            retention_elements = [
                "engagement questions every 15-20 seconds",
                "emotional peaks",
                "pattern interrupts",
                "retention",
                "engagement"
            ]
            retention_found = 0
            for element in retention_elements:
                if element.lower() in enhanced_prompt.lower():
                    retention_found += 1
                    print(f"   ✅ Found retention element: {element}")
            
            if retention_found >= 3:  # At least 3 retention elements
                self.log_test("VALIDATION 6 - Retention Engineering Elements", True,
                            f"{retention_found}/{len(retention_elements)} retention engineering elements found")
                validations_passed += 1
            else:
                self.log_test("VALIDATION 6 - Retention Engineering Elements", False,
                            f"Only {retention_found}/{len(retention_elements)} retention engineering elements found")
            
            # ===============================
            # CALCULATE PHASE 1 COMPLIANCE
            # ===============================
            compliance_percentage = (validations_passed / total_validations) * 100
            
            print(f"\n📊 === PHASE 1 COMPLIANCE RESULTS ===")
            print(f"✅ Validations Passed: {validations_passed}/{total_validations}")
            print(f"📈 Phase 1 Compliance: {compliance_percentage:.1f}%")
            
            if compliance_percentage == 100:
                print("🎉 PHASE 1 FULLY COMPLIANT! All critical validations passed.")
            else:
                print("⚠️  PHASE 1 COMPLIANCE INCOMPLETE. Missing validations need to be addressed.")
            
            # Show sample of enhanced prompt for manual verification
            print(f"\n📋 === SAMPLE OF ENHANCED PROMPT OUTPUT ===")
            print(enhanced_prompt[:1000])
            if len(enhanced_prompt) > 1000:
                print("... [TRUNCATED] ...")
            
            return compliance_percentage
            
        except Exception as e:
            self.log_test("Phase 1 - Exception", False, f"Request failed: {str(e)}")
            return 0

def main():
    print("🚀 Starting Phase 1 Enhanced Prompt Improvements Testing...")
    tester = Phase1ComplianceTester()
    
    # Run Phase 1 compliance test
    compliance = tester.test_phase_1_enhanced_prompt_improvements()
    
    print(f"\n🏁 === PHASE 1 TESTING COMPLETE ===")
    print(f"Final Phase 1 Compliance Score: {compliance:.1f}%")
    
    if compliance < 100:
        print("\n⚠️  ACTION ITEMS:")
        print("1. Update the emotional variation generation to include missing section headers")
        print("2. Add missing psychological triggers, 2025 trends, and retention engineering elements")
        print("3. Ensure all word count specifications are present")
        print("4. Re-run this test to verify 100% Phase 1 compliance")
    else:
        print("\n✅ All Phase 1 requirements met! System is fully compliant.")
    
    return compliance >= 100

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
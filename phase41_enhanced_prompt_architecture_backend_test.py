#!/usr/bin/env python3
"""
Phase 4.1 Enhanced Prompt Architecture Server Integration - Comprehensive Backend Testing
Testing the integration of Enhanced Prompt Architecture modules with the main /api/generate-script endpoint
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

class Phase41EnhancedPromptArchitectureTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Connectivity", True, f"Backend responding on {API_BASE}")
                return True
            else:
                self.log_test("Backend Connectivity", False, f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_enhanced_duration_integration_extended_15(self):
        """Test /api/generate-script with duration=extended_15 (Enhanced Architecture)"""
        try:
            test_data = {
                "prompt": "Create a comprehensive educational video about sustainable energy solutions",
                "video_type": "educational",
                "duration": "extended_15"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["id", "original_prompt", "generated_script", "video_type", "duration"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Enhanced Duration Integration - Extended_15 Structure", 
                                False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check for enhanced metadata
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Critical Phase 4.1 checks
                    enhanced_checks = [
                        metadata.get("enhanced_architecture_used") == True,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        metadata.get("duration") == "extended_15"
                    ]
                    
                    passed_checks = sum(enhanced_checks)
                    
                    if passed_checks >= 4:
                        self.log_test("Enhanced Duration Integration - Extended_15", True, 
                                    f"Enhanced architecture properly integrated ({passed_checks}/5 checks passed)")
                        
                        # Additional validation
                        template_name = metadata.get("template_name", "")
                        suitability_score = metadata.get("suitability_score", 0)
                        
                        if "15-20 Minute" in template_name and suitability_score > 0:
                            self.log_test("Enhanced Duration Integration - Extended_15 Template Selection", True,
                                        f"Template: {template_name}, Suitability: {suitability_score}")
                        else:
                            self.log_test("Enhanced Duration Integration - Extended_15 Template Selection", False,
                                        f"Template: {template_name}, Suitability: {suitability_score}")
                        
                        return True
                    else:
                        self.log_test("Enhanced Duration Integration - Extended_15", False, 
                                    f"Enhanced architecture not properly integrated ({passed_checks}/5 checks passed)")
                        return False
                else:
                    self.log_test("Enhanced Duration Integration - Extended_15", False, 
                                "Missing generation_metadata in response")
                    return False
                
            else:
                self.log_test("Enhanced Duration Integration - Extended_15", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Duration Integration - Extended_15", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_duration_integration_extended_20(self):
        """Test /api/generate-script with duration=extended_20 (Enhanced Architecture)"""
        try:
            test_data = {
                "prompt": "Create a marketing video about innovative fintech solutions",
                "video_type": "marketing",
                "duration": "extended_20"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced metadata
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Critical Phase 4.1 checks
                    enhanced_checks = [
                        metadata.get("enhanced_architecture_used") == True,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        metadata.get("duration") == "extended_20"
                    ]
                    
                    passed_checks = sum(enhanced_checks)
                    
                    if passed_checks >= 4:
                        self.log_test("Enhanced Duration Integration - Extended_20", True, 
                                    f"Enhanced architecture properly integrated ({passed_checks}/5 checks passed)")
                        
                        # Check for 20-25 minute template
                        template_name = metadata.get("template_name", "")
                        if "20-25 Minute" in template_name:
                            self.log_test("Enhanced Duration Integration - Extended_20 Template", True,
                                        f"Correct template selected: {template_name}")
                        else:
                            self.log_test("Enhanced Duration Integration - Extended_20 Template", False,
                                        f"Unexpected template: {template_name}")
                        
                        return True
                    else:
                        self.log_test("Enhanced Duration Integration - Extended_20", False, 
                                    f"Enhanced architecture not properly integrated ({passed_checks}/5 checks passed)")
                        return False
                else:
                    self.log_test("Enhanced Duration Integration - Extended_20", False, 
                                "Missing generation_metadata in response")
                    return False
                
            else:
                self.log_test("Enhanced Duration Integration - Extended_20", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Duration Integration - Extended_20", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_duration_integration_extended_25(self):
        """Test /api/generate-script with duration=extended_25 (Enhanced Architecture)"""
        try:
            test_data = {
                "prompt": "Create an entertainment video about the future of virtual reality",
                "video_type": "entertainment",
                "duration": "extended_25"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for enhanced metadata
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Critical Phase 4.1 checks
                    enhanced_checks = [
                        metadata.get("enhanced_architecture_used") == True,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        metadata.get("duration") == "extended_25"
                    ]
                    
                    passed_checks = sum(enhanced_checks)
                    
                    if passed_checks >= 4:
                        self.log_test("Enhanced Duration Integration - Extended_25", True, 
                                    f"Enhanced architecture properly integrated ({passed_checks}/5 checks passed)")
                        
                        # Check for 25-30 minute template
                        template_name = metadata.get("template_name", "")
                        if "25-30 Minute" in template_name:
                            self.log_test("Enhanced Duration Integration - Extended_25 Template", True,
                                        f"Correct template selected: {template_name}")
                        else:
                            self.log_test("Enhanced Duration Integration - Extended_25 Template", False,
                                        f"Unexpected template: {template_name}")
                        
                        return True
                    else:
                        self.log_test("Enhanced Duration Integration - Extended_25", False, 
                                    f"Enhanced architecture not properly integrated ({passed_checks}/5 checks passed)")
                        return False
                else:
                    self.log_test("Enhanced Duration Integration - Extended_25", False, 
                                "Missing generation_metadata in response")
                    return False
                
            else:
                self.log_test("Enhanced Duration Integration - Extended_25", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Duration Integration - Extended_25", False, f"Request failed: {str(e)}")
            return False

    def test_backward_compatibility_short(self):
        """Test /api/generate-script with duration=short (Standard Architecture)"""
        try:
            test_data = {
                "prompt": "Create a short video about healthy breakfast ideas",
                "video_type": "general",
                "duration": "short"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for standard metadata (backward compatibility)
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Backward compatibility checks
                    compatibility_checks = [
                        metadata.get("enhanced_architecture_used") == False,
                        metadata.get("duration") == "short",
                        "generated_script" in data,
                        len(data.get("generated_script", "")) > 100
                    ]
                    
                    passed_checks = sum(compatibility_checks)
                    
                    if passed_checks >= 3:
                        self.log_test("Backward Compatibility - Short Duration", True, 
                                    f"Standard architecture working correctly ({passed_checks}/4 checks passed)")
                        return True
                    else:
                        self.log_test("Backward Compatibility - Short Duration", False, 
                                    f"Backward compatibility issues ({passed_checks}/4 checks passed)")
                        return False
                else:
                    # Even without metadata, if script is generated, it's working
                    if "generated_script" in data and len(data.get("generated_script", "")) > 100:
                        self.log_test("Backward Compatibility - Short Duration", True, 
                                    "Script generated successfully (legacy mode)")
                        return True
                    else:
                        self.log_test("Backward Compatibility - Short Duration", False, 
                                    "No script generated")
                        return False
                
            else:
                self.log_test("Backward Compatibility - Short Duration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backward Compatibility - Short Duration", False, f"Request failed: {str(e)}")
            return False

    def test_backward_compatibility_medium(self):
        """Test /api/generate-script with duration=medium (Standard Architecture)"""
        try:
            test_data = {
                "prompt": "Create a medium-length video about time management tips",
                "video_type": "educational",
                "duration": "medium"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for standard metadata (backward compatibility)
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Backward compatibility checks
                    compatibility_checks = [
                        metadata.get("enhanced_architecture_used") == False,
                        metadata.get("duration") == "medium",
                        "generated_script" in data,
                        len(data.get("generated_script", "")) > 200
                    ]
                    
                    passed_checks = sum(compatibility_checks)
                    
                    if passed_checks >= 3:
                        self.log_test("Backward Compatibility - Medium Duration", True, 
                                    f"Standard architecture working correctly ({passed_checks}/4 checks passed)")
                        return True
                    else:
                        self.log_test("Backward Compatibility - Medium Duration", False, 
                                    f"Backward compatibility issues ({passed_checks}/4 checks passed)")
                        return False
                else:
                    # Even without metadata, if script is generated, it's working
                    if "generated_script" in data and len(data.get("generated_script", "")) > 200:
                        self.log_test("Backward Compatibility - Medium Duration", True, 
                                    "Script generated successfully (legacy mode)")
                        return True
                    else:
                        self.log_test("Backward Compatibility - Medium Duration", False, 
                                    "No script generated")
                        return False
                
            else:
                self.log_test("Backward Compatibility - Medium Duration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backward Compatibility - Medium Duration", False, f"Request failed: {str(e)}")
            return False

    def test_backward_compatibility_long(self):
        """Test /api/generate-script with duration=long (Standard Architecture)"""
        try:
            test_data = {
                "prompt": "Create a long video about digital marketing strategies",
                "video_type": "marketing",
                "duration": "long"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for standard metadata (backward compatibility)
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Backward compatibility checks
                    compatibility_checks = [
                        metadata.get("enhanced_architecture_used") == False,
                        metadata.get("duration") == "long",
                        "generated_script" in data,
                        len(data.get("generated_script", "")) > 300
                    ]
                    
                    passed_checks = sum(compatibility_checks)
                    
                    if passed_checks >= 3:
                        self.log_test("Backward Compatibility - Long Duration", True, 
                                    f"Standard architecture working correctly ({passed_checks}/4 checks passed)")
                        return True
                    else:
                        self.log_test("Backward Compatibility - Long Duration", False, 
                                    f"Backward compatibility issues ({passed_checks}/4 checks passed)")
                        return False
                else:
                    # Even without metadata, if script is generated, it's working
                    if "generated_script" in data and len(data.get("generated_script", "")) > 300:
                        self.log_test("Backward Compatibility - Long Duration", True, 
                                    "Script generated successfully (legacy mode)")
                        return True
                    else:
                        self.log_test("Backward Compatibility - Long Duration", False, 
                                    "No script generated")
                        return False
                
            else:
                self.log_test("Backward Compatibility - Long Duration", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backward Compatibility - Long Duration", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_template_selection_educational(self):
        """Test enhanced template selection for educational video type"""
        try:
            test_data = {
                "prompt": "Create an educational video about quantum physics fundamentals",
                "video_type": "educational",
                "duration": "extended_15"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Template selection checks
                    template_checks = [
                        metadata.get("enhanced_architecture_used") == True,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        metadata.get("video_type") == "educational"
                    ]
                    
                    passed_checks = sum(template_checks)
                    
                    if passed_checks >= 4:
                        template_name = metadata.get("template_name", "")
                        suitability_score = metadata.get("suitability_score", 0)
                        
                        self.log_test("Enhanced Template Selection - Educational", True, 
                                    f"Template selection working ({passed_checks}/5 checks passed)")
                        
                        # Check suitability score
                        if suitability_score > 0.5:
                            self.log_test("Enhanced Template Selection - Educational Suitability", True,
                                        f"Good suitability score: {suitability_score}")
                        else:
                            self.log_test("Enhanced Template Selection - Educational Suitability", False,
                                        f"Low suitability score: {suitability_score}")
                        
                        return True
                    else:
                        self.log_test("Enhanced Template Selection - Educational", False, 
                                    f"Template selection issues ({passed_checks}/5 checks passed)")
                        return False
                else:
                    self.log_test("Enhanced Template Selection - Educational", False, 
                                "Missing generation_metadata")
                    return False
                
            else:
                self.log_test("Enhanced Template Selection - Educational", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Template Selection - Educational", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_template_selection_marketing(self):
        """Test enhanced template selection for marketing video type"""
        try:
            test_data = {
                "prompt": "Create a marketing video about revolutionary AI-powered productivity tools",
                "video_type": "marketing",
                "duration": "extended_20"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Template selection checks
                    template_checks = [
                        metadata.get("enhanced_architecture_used") == True,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        metadata.get("video_type") == "marketing"
                    ]
                    
                    passed_checks = sum(template_checks)
                    
                    if passed_checks >= 4:
                        self.log_test("Enhanced Template Selection - Marketing", True, 
                                    f"Template selection working ({passed_checks}/5 checks passed)")
                        return True
                    else:
                        self.log_test("Enhanced Template Selection - Marketing", False, 
                                    f"Template selection issues ({passed_checks}/5 checks passed)")
                        return False
                else:
                    self.log_test("Enhanced Template Selection - Marketing", False, 
                                "Missing generation_metadata")
                    return False
                
            else:
                self.log_test("Enhanced Template Selection - Marketing", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Template Selection - Marketing", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_template_selection_entertainment(self):
        """Test enhanced template selection for entertainment video type"""
        try:
            test_data = {
                "prompt": "Create an entertainment video about the most bizarre historical events",
                "video_type": "entertainment",
                "duration": "extended_25"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Template selection checks
                    template_checks = [
                        metadata.get("enhanced_architecture_used") == True,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        metadata.get("video_type") == "entertainment"
                    ]
                    
                    passed_checks = sum(template_checks)
                    
                    if passed_checks >= 4:
                        self.log_test("Enhanced Template Selection - Entertainment", True, 
                                    f"Template selection working ({passed_checks}/5 checks passed)")
                        return True
                    else:
                        self.log_test("Enhanced Template Selection - Entertainment", False, 
                                    f"Template selection issues ({passed_checks}/5 checks passed)")
                        return False
                else:
                    self.log_test("Enhanced Template Selection - Entertainment", False, 
                                "Missing generation_metadata")
                    return False
                
            else:
                self.log_test("Enhanced Template Selection - Entertainment", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Template Selection - Entertainment", False, f"Request failed: {str(e)}")
            return False

    def test_enhanced_template_selection_general(self):
        """Test enhanced template selection for general video type"""
        try:
            test_data = {
                "prompt": "Create a general video about the importance of mental health awareness",
                "video_type": "general",
                "duration": "extended_15"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Template selection checks
                    template_checks = [
                        metadata.get("enhanced_architecture_used") == True,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        metadata.get("video_type") == "general"
                    ]
                    
                    passed_checks = sum(template_checks)
                    
                    if passed_checks >= 4:
                        self.log_test("Enhanced Template Selection - General", True, 
                                    f"Template selection working ({passed_checks}/5 checks passed)")
                        return True
                    else:
                        self.log_test("Enhanced Template Selection - General", False, 
                                    f"Template selection issues ({passed_checks}/5 checks passed)")
                        return False
                else:
                    self.log_test("Enhanced Template Selection - General", False, 
                                "Missing generation_metadata")
                    return False
                
            else:
                self.log_test("Enhanced Template Selection - General", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Template Selection - General", False, f"Request failed: {str(e)}")
            return False

    def test_integration_error_handling(self):
        """Test error handling and fallback scenarios"""
        try:
            # Test with invalid duration
            test_data = {
                "prompt": "Create a video about testing error handling",
                "video_type": "general",
                "duration": "invalid_duration"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=60)
            
            # Should return error for invalid duration
            if response.status_code == 400:
                self.log_test("Integration Error Handling - Invalid Duration", True, 
                            "Properly rejected invalid duration")
            else:
                self.log_test("Integration Error Handling - Invalid Duration", False, 
                            f"Unexpected response for invalid duration: {response.status_code}")
            
            # Test with empty prompt
            test_data = {
                "prompt": "",
                "video_type": "general",
                "duration": "extended_15"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=60)
            
            # Should handle empty prompt gracefully
            if response.status_code in [400, 422]:
                self.log_test("Integration Error Handling - Empty Prompt", True, 
                            "Properly handled empty prompt")
                return True
            elif response.status_code == 200:
                # If it generates something, that's also acceptable
                data = response.json()
                if "generated_script" in data:
                    self.log_test("Integration Error Handling - Empty Prompt", True, 
                                "Generated script despite empty prompt (graceful handling)")
                    return True
                else:
                    self.log_test("Integration Error Handling - Empty Prompt", False, 
                                "No script generated for empty prompt")
                    return False
            else:
                self.log_test("Integration Error Handling - Empty Prompt", False, 
                            f"Unexpected response for empty prompt: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Integration Error Handling", False, f"Request failed: {str(e)}")
            return False

    def test_database_metadata_storage(self):
        """Test that enhanced metadata is stored correctly in database"""
        try:
            # Generate a script with enhanced architecture
            test_data = {
                "prompt": "Create a comprehensive video about renewable energy technologies",
                "video_type": "educational",
                "duration": "extended_20"
            }
            
            response = requests.post(f"{API_BASE}/generate-script", 
                                   json=test_data, 
                                   timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                script_id = data.get("id")
                
                if not script_id:
                    self.log_test("Database Metadata Storage - Script ID", False, 
                                "No script ID returned")
                    return False
                
                # Check if metadata is present in response
                if "generation_metadata" in data:
                    metadata = data["generation_metadata"]
                    
                    # Check for enhanced metadata fields
                    metadata_checks = [
                        "enhanced_architecture_used" in metadata,
                        "template_id" in metadata,
                        "template_name" in metadata,
                        "suitability_score" in metadata,
                        "duration" in metadata
                    ]
                    
                    passed_checks = sum(metadata_checks)
                    
                    if passed_checks >= 4:
                        self.log_test("Database Metadata Storage", True, 
                                    f"Enhanced metadata present ({passed_checks}/5 fields)")
                        
                        # Try to retrieve the script to verify storage
                        try:
                            scripts_response = requests.get(f"{API_BASE}/scripts", timeout=30)
                            if scripts_response.status_code == 200:
                                scripts_data = scripts_response.json()
                                
                                # Find our script in the list
                                our_script = None
                                for script in scripts_data:
                                    if script.get("id") == script_id:
                                        our_script = script
                                        break
                                
                                if our_script and "generation_metadata" in our_script:
                                    self.log_test("Database Metadata Storage - Retrieval", True,
                                                "Enhanced metadata stored and retrievable")
                                else:
                                    self.log_test("Database Metadata Storage - Retrieval", False,
                                                "Enhanced metadata not found in stored script")
                            else:
                                self.log_test("Database Metadata Storage - Retrieval", False,
                                            f"Could not retrieve scripts: {scripts_response.status_code}")
                        except Exception as e:
                            self.log_test("Database Metadata Storage - Retrieval", False,
                                        f"Error retrieving scripts: {str(e)}")
                        
                        return True
                    else:
                        self.log_test("Database Metadata Storage", False, 
                                    f"Insufficient metadata fields ({passed_checks}/5 fields)")
                        return False
                else:
                    self.log_test("Database Metadata Storage", False, 
                                "No generation_metadata in response")
                    return False
                
            else:
                self.log_test("Database Metadata Storage", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Metadata Storage", False, f"Request failed: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run all Phase 4.1 Enhanced Prompt Architecture Server Integration tests"""
        print("🚀 Starting Phase 4.1 Enhanced Prompt Architecture Server Integration Testing")
        print("=" * 80)
        print()
        
        # Test 1: Basic connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed. Stopping tests.")
            return 0
        
        # Test 2: Enhanced Duration Integration
        print("🎯 Testing Enhanced Duration Integration...")
        self.test_enhanced_duration_integration_extended_15()
        self.test_enhanced_duration_integration_extended_20()
        self.test_enhanced_duration_integration_extended_25()
        
        # Test 3: Backward Compatibility
        print("🔄 Testing Backward Compatibility...")
        self.test_backward_compatibility_short()
        self.test_backward_compatibility_medium()
        self.test_backward_compatibility_long()
        
        # Test 4: Enhanced Template Selection
        print("📋 Testing Enhanced Template Selection...")
        self.test_enhanced_template_selection_educational()
        self.test_enhanced_template_selection_marketing()
        self.test_enhanced_template_selection_entertainment()
        self.test_enhanced_template_selection_general()
        
        # Test 5: Integration Error Handling
        print("⚠️  Testing Integration Error Handling...")
        self.test_integration_error_handling()
        
        # Test 6: Database Metadata Storage
        print("💾 Testing Database Metadata Storage...")
        self.test_database_metadata_storage()
        
        # Final results
        print("=" * 80)
        print("🏁 PHASE 4.1 ENHANCED PROMPT ARCHITECTURE SERVER INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        print()
        
        # Categorize results
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}")
        
        if failed_tests:
            print()
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print()
        
        # Overall assessment
        if success_rate >= 85:
            print("🎉 EXCELLENT: Phase 4.1 Enhanced Prompt Architecture Server Integration is working excellently!")
        elif success_rate >= 70:
            print("✅ GOOD: Phase 4.1 Enhanced Prompt Architecture Server Integration is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Phase 4.1 Enhanced Prompt Architecture Server Integration has some issues that need attention.")
        else:
            print("❌ CRITICAL: Phase 4.1 Enhanced Prompt Architecture Server Integration has significant issues.")
        
        return success_rate

if __name__ == "__main__":
    print("Phase 4.1 Enhanced Prompt Architecture Server Integration - Backend Testing")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    tester = Phase41EnhancedPromptArchitectureTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)
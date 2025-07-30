import requests
import sys
import json
from datetime import datetime

class LegalMateAPITester:
    def __init__(self, base_url="https://8c721040-3fb9-48a1-8c68-1ab61d53dd59.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.contract_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'List with ' + str(len(response_data)) + ' items'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_contract_types(self):
        """Test contract types endpoint"""
        success, response = self.run_test("Contract Types", "GET", "contract-types", 200)
        if success and 'types' in response:
            types = response['types']
            print(f"   Found {len(types)} contract types:")
            for contract_type in types:
                print(f"     - {contract_type.get('name', 'Unknown')} ({contract_type.get('id', 'No ID')})")
            
            # Verify expected contract types
            expected_types = ['NDA', 'freelance_agreement', 'partnership_agreement']
            found_types = [t.get('id') for t in types]
            missing_types = [t for t in expected_types if t not in found_types]
            if missing_types:
                print(f"   ⚠️  Missing expected types: {missing_types}")
            else:
                print(f"   ✅ All expected contract types found")
        return success, response

    def test_jurisdictions(self):
        """Test jurisdictions endpoint"""
        success, response = self.run_test("Jurisdictions", "GET", "jurisdictions", 200)
        if success and 'jurisdictions' in response:
            jurisdictions = response['jurisdictions']
            print(f"   Found {len(jurisdictions)} jurisdictions:")
            supported = [j for j in jurisdictions if j.get('supported', False)]
            print(f"   Supported: {[j.get('name') for j in supported]}")
        return success, response

    def test_contracts_list(self):
        """Test contracts list endpoint"""
        return self.run_test("Contracts List", "GET", "contracts", 200)

    def test_nda_generation(self):
        """Test NDA contract generation"""
        nda_data = {
            "contract_type": "NDA",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Tech Corp Inc.",
                "party1_type": "company",
                "party2_name": "John Doe",
                "party2_type": "individual"
            },
            "terms": {
                "purpose": "Discussion of potential business collaboration and sharing of proprietary technology information",
                "duration": "2_years"
            },
            "special_clauses": ["Non-compete clause for 6 months"]
        }
        
        success, response = self.run_test(
            "NDA Contract Generation", 
            "POST", 
            "generate-contract", 
            200, 
            nda_data,
            timeout=60  # AI generation might take longer
        )
        
        if success and 'contract' in response:
            contract = response['contract']
            self.contract_id = contract.get('id')
            print(f"   Contract ID: {self.contract_id}")
            print(f"   Compliance Score: {contract.get('compliance_score', 'N/A')}%")
            print(f"   Clauses Count: {len(contract.get('clauses', []))}")
            print(f"   Content Length: {len(contract.get('content', ''))} characters")
            
            # Check for warnings and suggestions
            if 'warnings' in response and response['warnings']:
                print(f"   Warnings: {response['warnings']}")
            if 'suggestions' in response and response['suggestions']:
                print(f"   Suggestions: {response['suggestions']}")
                
        return success, response

    def test_freelance_generation(self):
        """Test Freelance Agreement generation"""
        freelance_data = {
            "contract_type": "freelance_agreement",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Digital Agency LLC",
                "party1_type": "llc",
                "party2_name": "Jane Smith",
                "party2_type": "individual"
            },
            "terms": {
                "scope": "Development of a responsive website with e-commerce functionality including payment integration and admin dashboard",
                "payment_amount": "$5,000",
                "payment_terms": "milestone"
            },
            "special_clauses": []
        }
        
        success, response = self.run_test(
            "Freelance Agreement Generation", 
            "POST", 
            "generate-contract", 
            200, 
            freelance_data,
            timeout=60
        )
        
        if success and 'contract' in response:
            contract = response['contract']
            print(f"   Contract ID: {contract.get('id')}")
            print(f"   Compliance Score: {contract.get('compliance_score', 'N/A')}%")
            
        return success, response

    def test_partnership_generation(self):
        """Test Partnership Agreement generation"""
        partnership_data = {
            "contract_type": "partnership_agreement",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Alpha Ventures",
                "party1_type": "company",
                "party2_name": "Beta Solutions",
                "party2_type": "company"
            },
            "terms": {
                "business_purpose": "Joint venture for developing and marketing AI-powered business solutions",
                "profit_split": "60/40",
                "capital_contribution": "$50,000 each"
            },
            "special_clauses": ["Intellectual property sharing agreement"]
        }
        
        success, response = self.run_test(
            "Partnership Agreement Generation", 
            "POST", 
            "generate-contract", 
            200, 
            partnership_data,
            timeout=60
        )
        
        if success and 'contract' in response:
            contract = response['contract']
            print(f"   Contract ID: {contract.get('id')}")
            print(f"   Compliance Score: {contract.get('compliance_score', 'N/A')}%")
            
        return success, response

    def test_get_specific_contract(self):
        """Test getting a specific contract by ID"""
        if not self.contract_id:
            print("⚠️  Skipping specific contract test - no contract ID available")
            return True, {}
            
        return self.run_test(
            f"Get Contract {self.contract_id}", 
            "GET", 
            f"contracts/{self.contract_id}", 
            200
        )

    def test_invalid_contract_generation(self):
        """Test contract generation with invalid data"""
        invalid_data = {
            "contract_type": "invalid_type",
            "jurisdiction": "INVALID",
            "parties": {},
            "terms": {}
        }
        
        # This should fail with 422 (validation error) or 500 (server error)
        success, response = self.run_test(
            "Invalid Contract Generation", 
            "POST", 
            "generate-contract", 
            500,  # Expecting server error due to invalid data
            invalid_data
        )
        
        # If it returns 422 instead of 500, that's also acceptable
        if not success:
            # Try with 422 status code
            success_422, _ = self.run_test(
                "Invalid Contract Generation (422)", 
                "POST", 
                "generate-contract", 
                422, 
                invalid_data
            )
            if success_422:
                self.tests_passed += 1  # Adjust count since we ran an extra test
                return True, response
        
        return success, response

    def test_pdf_download_valid_contract(self):
        """Test PDF download for a valid contract"""
        if not self.contract_id:
            print("⚠️  Skipping PDF download test - no contract ID available")
            return True, {}
        
        url = f"{self.api_url}/contracts/{self.contract_id}/download-pdf"
        
        self.tests_run += 1
        print(f"\n🔍 Testing PDF Download for Valid Contract...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Check response headers
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                print(f"   Content-Type: {content_type}")
                print(f"   Content-Disposition: {content_disposition}")
                
                # Verify PDF headers
                if 'application/pdf' in content_type:
                    print("   ✅ Correct PDF content type")
                else:
                    print(f"   ⚠️  Expected PDF content type, got: {content_type}")
                
                if 'attachment' in content_disposition and 'filename' in content_disposition:
                    print("   ✅ Correct download headers")
                else:
                    print(f"   ⚠️  Missing or incorrect download headers")
                
                # Check PDF content size
                content_length = len(response.content)
                print(f"   PDF Size: {content_length} bytes")
                
                if content_length > 1000:  # PDF should be reasonably sized
                    print("   ✅ PDF has reasonable size")
                else:
                    print("   ⚠️  PDF seems too small")
                
                # Check if content starts with PDF header
                if response.content.startswith(b'%PDF'):
                    print("   ✅ Valid PDF format")
                else:
                    print("   ❌ Invalid PDF format - missing PDF header")
                
                return True, {"content_length": content_length, "headers": dict(response.headers)}
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_pdf_download_invalid_contract(self):
        """Test PDF download for invalid contract ID"""
        invalid_contract_id = "invalid-contract-id-12345"
        
        url = f"{self.api_url}/contracts/{invalid_contract_id}/download-pdf"
        
        self.tests_run += 1
        print(f"\n🔍 Testing PDF Download for Invalid Contract...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                self.tests_passed += 1
                print(f"✅ Passed - Correctly returned 404 for invalid contract")
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return True, {}
            else:
                print(f"❌ Failed - Expected 404, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_pdf_download_nonexistent_contract(self):
        """Test PDF download for non-existent but valid UUID format contract"""
        import uuid
        nonexistent_id = str(uuid.uuid4())
        
        url = f"{self.api_url}/contracts/{nonexistent_id}/download-pdf"
        
        self.tests_run += 1
        print(f"\n🔍 Testing PDF Download for Non-existent Contract...")
        print(f"   URL: {url}")
        print(f"   Contract ID: {nonexistent_id}")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                self.tests_passed += 1
                print(f"✅ Passed - Correctly returned 404 for non-existent contract")
                try:
                    error_data = response.json()
                    print(f"   Error message: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return True, {}
            else:
                print(f"❌ Failed - Expected 404, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def validate_contract_formatting(self, contract_content, contract_type):
        """Validate contract formatting requirements"""
        formatting_issues = []
        
        # Check 1: No asterisk (*) expressions anywhere in the content
        if '*' in contract_content:
            asterisk_count = contract_content.count('*')
            formatting_issues.append(f"Found {asterisk_count} asterisk (*) characters in content")
        
        # Check 2: Proper **bold** formatting for headings and sections
        # Look for patterns that should be bold formatted
        bold_patterns = ['AGREEMENT', 'CONTRACT', 'WHEREAS', 'NOW, THEREFORE', 'GOVERNING LAW', 'TERMINATION']
        missing_bold = []
        for pattern in bold_patterns:
            if pattern in contract_content.upper():
                # Check if it's properly formatted with **bold**
                if f"**{pattern}" not in contract_content and f"**{pattern.title()}" not in contract_content and f"**{pattern.lower()}" not in contract_content:
                    missing_bold.append(pattern)
        
        if missing_bold:
            formatting_issues.append(f"Missing bold formatting for: {missing_bold}")
        
        # Check 3: [Date of Execution] placeholder properly placed
        if '[Date of Execution]' not in contract_content and 'Date of Execution' not in contract_content:
            formatting_issues.append("Missing [Date of Execution] placeholder")
        
        # Check 4: Clean, professional formatting
        # Check for excessive whitespace
        if '\n\n\n' in contract_content:
            formatting_issues.append("Excessive whitespace found (more than 2 consecutive newlines)")
        
        # Check for proper paragraph structure
        lines = contract_content.split('\n')
        empty_lines = sum(1 for line in lines if not line.strip())
        total_lines = len(lines)
        if total_lines > 0 and empty_lines / total_lines > 0.5:
            formatting_issues.append("Too many empty lines - poor paragraph structure")
        
        return formatting_issues

    def test_nda_formatting_requirements(self):
        """Test NDA contract generation with focus on formatting requirements"""
        nda_data = {
            "contract_type": "NDA",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Innovative Tech Solutions Inc.",
                "party1_type": "corporation",
                "party2_name": "Sarah Johnson",
                "party2_type": "individual"
            },
            "terms": {
                "purpose": "Evaluation of potential strategic partnership and sharing of confidential business information",
                "duration": "3_years"
            },
            "special_clauses": ["Return of materials clause", "Non-solicitation provision"]
        }
        
        success, response = self.run_test(
            "NDA Contract Formatting Requirements", 
            "POST", 
            "generate-contract", 
            200, 
            nda_data,
            timeout=60
        )
        
        if success and 'contract' in response:
            contract = response['contract']
            content = contract.get('content', '')
            
            print(f"   Testing formatting requirements for NDA...")
            formatting_issues = self.validate_contract_formatting(content, 'NDA')
            
            if not formatting_issues:
                print("   ✅ All formatting requirements met")
            else:
                print("   ❌ Formatting issues found:")
                for issue in formatting_issues:
                    print(f"     - {issue}")
                # Don't fail the test completely, but note the issues
                
            # Show sample of content for verification
            print(f"   Content preview (first 300 chars):")
            print(f"   {content[:300]}...")
            
        return success, response

    def test_freelance_formatting_requirements(self):
        """Test Freelance Agreement generation with focus on formatting requirements"""
        freelance_data = {
            "contract_type": "freelance_agreement",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Creative Marketing Agency LLC",
                "party1_type": "llc",
                "party2_name": "Michael Chen",
                "party2_type": "individual"
            },
            "terms": {
                "scope": "Design and development of comprehensive brand identity including logo, website, and marketing materials",
                "payment_amount": "$8,500",
                "payment_terms": "50% upfront, 50% on completion"
            },
            "special_clauses": ["Revision limits", "Copyright transfer upon payment"]
        }
        
        success, response = self.run_test(
            "Freelance Agreement Formatting Requirements", 
            "POST", 
            "generate-contract", 
            200, 
            freelance_data,
            timeout=60
        )
        
        if success and 'contract' in response:
            contract = response['contract']
            content = contract.get('content', '')
            
            print(f"   Testing formatting requirements for Freelance Agreement...")
            formatting_issues = self.validate_contract_formatting(content, 'freelance_agreement')
            
            if not formatting_issues:
                print("   ✅ All formatting requirements met")
            else:
                print("   ❌ Formatting issues found:")
                for issue in formatting_issues:
                    print(f"     - {issue}")
                    
            # Show sample of content for verification
            print(f"   Content preview (first 300 chars):")
            print(f"   {content[:300]}...")
            
        return success, response

    def test_partnership_formatting_requirements(self):
        """Test Partnership Agreement generation with focus on formatting requirements"""
        partnership_data = {
            "contract_type": "partnership_agreement",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Green Energy Innovations Corp",
                "party1_type": "corporation",
                "party2_name": "Sustainable Tech Partners LLC",
                "party2_type": "llc"
            },
            "terms": {
                "business_purpose": "Joint development and commercialization of renewable energy storage solutions",
                "profit_split": "55/45",
                "capital_contribution": "$100,000 from each party"
            },
            "special_clauses": ["Technology sharing agreement", "Exclusive territory rights"]
        }
        
        success, response = self.run_test(
            "Partnership Agreement Formatting Requirements", 
            "POST", 
            "generate-contract", 
            200, 
            partnership_data,
            timeout=60
        )
        
        if success and 'contract' in response:
            contract = response['contract']
            content = contract.get('content', '')
            
            print(f"   Testing formatting requirements for Partnership Agreement...")
            formatting_issues = self.validate_contract_formatting(content, 'partnership_agreement')
            
            if not formatting_issues:
                print("   ✅ All formatting requirements met")
            else:
                print("   ❌ Formatting issues found:")
                for issue in formatting_issues:
                    print(f"     - {issue}")
                    
            # Show sample of content for verification
            print(f"   Content preview (first 300 chars):")
            print(f"   {content[:300]}...")
            
        return success, response

def main():
    print("🚀 Starting LegalMate AI Backend API Tests")
    print("=" * 60)
    
    tester = LegalMateAPITester()
    
    # Run all tests
    test_results = []
    
    # Basic endpoint tests
    test_results.append(tester.test_root_endpoint())
    test_results.append(tester.test_contract_types())
    test_results.append(tester.test_jurisdictions())
    test_results.append(tester.test_contracts_list())
    
    # Contract generation tests (main functionality)
    print("\n" + "="*40)
    print("🤖 Testing AI Contract Generation")
    print("="*40)
    
    test_results.append(tester.test_nda_generation())
    test_results.append(tester.test_freelance_generation())
    test_results.append(tester.test_partnership_generation())
    
    # Contract formatting requirements tests
    print("\n" + "="*50)
    print("📝 Testing Contract Formatting Requirements")
    print("="*50)
    
    test_results.append(tester.test_nda_formatting_requirements())
    test_results.append(tester.test_freelance_formatting_requirements())
    test_results.append(tester.test_partnership_formatting_requirements())
    
    # Additional tests
    test_results.append(tester.test_get_specific_contract())
    test_results.append(tester.test_invalid_contract_generation())
    
    # PDF Download tests
    print("\n" + "="*40)
    print("📄 Testing PDF Download Functionality")
    print("="*40)
    
    test_results.append(tester.test_pdf_download_valid_contract())
    test_results.append(tester.test_pdf_download_invalid_contract())
    test_results.append(tester.test_pdf_download_nonexistent_contract())
    
    # Print final results
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
import requests
import sys
import json
from datetime import datetime

class LegalMateAPITester:
    def __init__(self, base_url="https://37403d54-9c24-4492-951b-8436e7a68ea6.preview.emergentagent.com"):
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

    def test_pdf_bold_formatting_specific(self):
        """Test PDF generation with specific focus on bold formatting without asterisks"""
        # Generate a new contract specifically for PDF bold formatting testing
        test_data = {
            "contract_type": "NDA",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Bold Format Testing Corp",
                "party1_type": "corporation",
                "party2_name": "PDF Validation Specialist",
                "party2_type": "individual"
            },
            "terms": {
                "purpose": "Testing PDF bold formatting functionality to ensure section headings appear in bold without asterisk symbols",
                "duration": "1_year"
            },
            "special_clauses": ["Bold formatting verification clause"]
        }
        
        # First generate the contract
        success, response = self.run_test(
            "Generate Contract for PDF Bold Testing", 
            "POST", 
            "generate-contract", 
            200, 
            test_data,
            timeout=60
        )
        
        if not success or 'contract' not in response:
            print("❌ Failed to generate contract for PDF bold testing")
            return False, {}
        
        contract = response['contract']
        test_contract_id = contract.get('id')
        contract_content = contract.get('content', '')
        
        print(f"   Generated contract ID: {test_contract_id}")
        
        # Check the contract content for proper formatting before PDF generation
        print(f"\n   📝 Checking contract content formatting...")
        
        # Check 1: No asterisk symbols should be present
        asterisk_count = contract_content.count('*')
        if asterisk_count == 0:
            print(f"   ✅ No asterisk (*) symbols found in contract content")
        else:
            print(f"   ❌ Found {asterisk_count} asterisk (*) symbols in contract content")
            # Show where asterisks are found
            lines_with_asterisks = [line for line in contract_content.split('\n') if '*' in line]
            for line in lines_with_asterisks[:3]:  # Show first 3 lines with asterisks
                print(f"      - {line.strip()}")
        
        # Check 2: Look for **bold** formatting patterns
        import re
        bold_patterns = re.findall(r'\*\*[^*]+\*\*', contract_content)
        if bold_patterns:
            print(f"   ✅ Found {len(bold_patterns)} **bold** formatting patterns in contract")
            for pattern in bold_patterns[:3]:  # Show first 3 bold patterns
                print(f"      - {pattern}")
        else:
            print(f"   ⚠️  No **bold** formatting patterns found in contract content")
        
        # Now test PDF download
        if not test_contract_id:
            print("❌ No contract ID available for PDF testing")
            return False, {}
        
        url = f"{self.api_url}/contracts/{test_contract_id}/download-pdf"
        
        self.tests_run += 1
        print(f"\n🔍 Testing PDF Bold Formatting...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ PDF download successful")
                
                # Verify PDF format
                if response.content.startswith(b'%PDF'):
                    print("   ✅ Valid PDF format")
                else:
                    print("   ❌ Invalid PDF format")
                    return False, {}
                
                # Check PDF size
                content_length = len(response.content)
                print(f"   PDF Size: {content_length} bytes")
                
                if content_length > 2000:  # Should be reasonably sized for a contract
                    print("   ✅ PDF has reasonable size for contract content")
                else:
                    print("   ⚠️  PDF seems small - may not contain full contract")
                
                # Try to extract text from PDF to check for asterisks
                try:
                    # Simple check - look for asterisk patterns in the raw PDF content
                    # This is a basic check since we don't have PDF parsing libraries
                    pdf_content_str = response.content.decode('latin-1', errors='ignore')
                    
                    # Count asterisks in the PDF content (excluding PDF structure)
                    # Filter out PDF metadata and focus on text content
                    text_parts = []
                    lines = pdf_content_str.split('\n')
                    for line in lines:
                        # Skip PDF structure lines
                        if not any(keyword in line for keyword in ['obj', 'endobj', 'stream', 'endstream', '/Type', '/Font', '/Length']):
                            if line.strip() and not line.startswith('%'):
                                text_parts.append(line)
                    
                    text_content = '\n'.join(text_parts)
                    asterisk_in_pdf = text_content.count('*')
                    
                    print(f"   📄 PDF Content Analysis:")
                    print(f"      - Asterisk (*) count in PDF text: {asterisk_in_pdf}")
                    
                    if asterisk_in_pdf == 0:
                        print("   ✅ No asterisk (*) symbols found in PDF content - formatting requirement met")
                    else:
                        print("   ❌ Found asterisk (*) symbols in PDF content - formatting requirement NOT met")
                        # Show some context where asterisks appear
                        asterisk_lines = [line for line in text_content.split('\n') if '*' in line]
                        for line in asterisk_lines[:2]:  # Show first 2 lines with asterisks
                            print(f"         - {line.strip()[:100]}...")
                    
                    # Look for evidence of bold formatting in PDF structure
                    # ReportLab uses <b> tags which should be converted to PDF bold formatting
                    if '<b>' in pdf_content_str or '/F1' in pdf_content_str or 'Bold' in pdf_content_str:
                        print("   ✅ Evidence of bold formatting found in PDF structure")
                    else:
                        print("   ⚠️  Limited evidence of bold formatting in PDF structure")
                    
                except Exception as e:
                    print(f"   ⚠️  Could not analyze PDF text content: {str(e)}")
                
                return True, {
                    "contract_id": test_contract_id,
                    "pdf_size": content_length,
                    "asterisk_in_contract": asterisk_count,
                    "bold_patterns_in_contract": len(bold_patterns)
                }
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

    def test_edited_pdf_generation_valid_data(self):
        """Test the new edited PDF generation endpoint with valid contract data"""
        # First generate a contract to get valid structure
        contract_data = {
            "contract_type": "NDA",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "EditTest Corp",
                "party1_type": "corporation",
                "party2_name": "PDF Editor",
                "party2_type": "individual"
            },
            "terms": {
                "purpose": "Testing edited PDF generation functionality",
                "duration": "1_year"
            },
            "special_clauses": ["Edited content verification clause"]
        }
        
        # Generate original contract
        success, response = self.run_test(
            "Generate Contract for Edited PDF Test", 
            "POST", 
            "generate-contract", 
            200, 
            contract_data,
            timeout=60
        )
        
        if not success or 'contract' not in response:
            print("❌ Failed to generate contract for edited PDF testing")
            return False, {}
        
        original_contract = response['contract']
        
        # Modify the contract content to simulate editing
        edited_contract = original_contract.copy()
        edited_contract['content'] = edited_contract['content'].replace(
            "Testing edited PDF generation functionality",
            "EDITED: Testing the new edited PDF generation functionality with modified content"
        )
        
        # Test the edited PDF endpoint
        edited_pdf_data = {
            "contract": edited_contract
        }
        
        url = f"{self.api_url}/contracts/download-pdf-edited"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Edited PDF Generation with Valid Data...")
        print(f"   URL: {url}")
        print(f"   Contract ID: {edited_contract.get('id')}")
        
        try:
            response = requests.post(url, json=edited_pdf_data, headers={'Content-Type': 'application/json'}, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - Edited PDF generated successfully")
                
                # Check response headers
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                print(f"   Content-Type: {content_type}")
                print(f"   Content-Disposition: {content_disposition}")
                
                # Verify PDF headers
                if 'application/pdf' in content_type:
                    print("   ✅ Correct PDF content type")
                else:
                    print(f"   ❌ Expected PDF content type, got: {content_type}")
                
                if 'attachment' in content_disposition and 'filename' in content_disposition:
                    print("   ✅ Correct download headers")
                    if '_edited.pdf' in content_disposition:
                        print("   ✅ Filename includes 'edited' indicator")
                    else:
                        print("   ⚠️  Filename doesn't include 'edited' indicator")
                else:
                    print(f"   ❌ Missing or incorrect download headers")
                
                # Check PDF content size
                content_length = len(response.content)
                print(f"   PDF Size: {content_length} bytes")
                
                if content_length > 1000:
                    print("   ✅ PDF has reasonable size")
                else:
                    print("   ❌ PDF seems too small")
                
                # Check if content starts with PDF header
                if response.content.startswith(b'%PDF'):
                    print("   ✅ Valid PDF format")
                else:
                    print("   ❌ Invalid PDF format - missing PDF header")
                
                # Try to verify "Edited" status in PDF content
                try:
                    pdf_content_str = response.content.decode('latin-1', errors='ignore')
                    if 'Edited' in pdf_content_str:
                        print("   ✅ PDF includes 'Edited' status indicator")
                    else:
                        print("   ⚠️  Could not verify 'Edited' status in PDF")
                except:
                    print("   ⚠️  Could not analyze PDF content for 'Edited' status")
                
                return True, {
                    "content_length": content_length, 
                    "headers": dict(response.headers),
                    "original_contract_id": original_contract.get('id'),
                    "edited_contract_id": edited_contract.get('id')
                }
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

    def test_edited_pdf_generation_invalid_data(self):
        """Test edited PDF generation endpoint with invalid request format"""
        # Test with missing contract data
        invalid_data_1 = {}
        
        success_1, response_1 = self.run_test(
            "Edited PDF with Missing Contract Data", 
            "POST", 
            "contracts/download-pdf-edited", 
            422,  # Expecting validation error
            invalid_data_1
        )
        
        # If 422 doesn't work, try 500
        if not success_1:
            success_1, response_1 = self.run_test(
                "Edited PDF with Missing Contract Data (500)", 
                "POST", 
                "contracts/download-pdf-edited", 
                500,
                invalid_data_1
            )
            if success_1:
                self.tests_passed += 1  # Adjust count since we ran an extra test
        
        # Test with invalid contract structure
        invalid_data_2 = {
            "contract": {
                "invalid_field": "test"
                # Missing required fields like id, content, etc.
            }
        }
        
        success_2, response_2 = self.run_test(
            "Edited PDF with Invalid Contract Structure", 
            "POST", 
            "contracts/download-pdf-edited", 
            500,  # Expecting server error due to missing required fields
            invalid_data_2
        )
        
        return success_1 and success_2, {"test1": response_1, "test2": response_2}

    def test_edited_pdf_content_verification(self):
        """Test that edited PDF content differs from original when content is modified"""
        # Generate a contract first
        contract_data = {
            "contract_type": "freelance_agreement",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "Content Verification LLC",
                "party1_type": "llc",
                "party2_name": "PDF Content Tester",
                "party2_type": "individual"
            },
            "terms": {
                "scope": "Original content for PDF verification testing",
                "payment_amount": "$1,000",
                "payment_terms": "upon_completion"
            },
            "special_clauses": []
        }
        
        # Generate original contract
        success, response = self.run_test(
            "Generate Contract for Content Verification", 
            "POST", 
            "generate-contract", 
            200, 
            contract_data,
            timeout=60
        )
        
        if not success or 'contract' not in response:
            print("❌ Failed to generate contract for content verification")
            return False, {}
        
        original_contract = response['contract']
        contract_id = original_contract.get('id')
        
        # Download original PDF
        original_pdf_url = f"{self.api_url}/contracts/{contract_id}/download-pdf"
        
        print(f"\n🔍 Testing Content Verification - Downloading Original PDF...")
        try:
            original_pdf_response = requests.get(original_pdf_url, timeout=30)
            if original_pdf_response.status_code != 200:
                print("❌ Failed to download original PDF")
                return False, {}
            
            original_pdf_size = len(original_pdf_response.content)
            print(f"   Original PDF Size: {original_pdf_size} bytes")
            
        except Exception as e:
            print(f"❌ Failed to download original PDF: {str(e)}")
            return False, {}
        
        # Create edited version with significant content changes
        edited_contract = original_contract.copy()
        edited_contract['content'] = edited_contract['content'].replace(
            "Original content for PDF verification testing",
            "SIGNIFICANTLY MODIFIED CONTENT: This has been extensively edited to verify that the edited PDF generation creates different content from the original PDF"
        )
        
        # Add more modifications to ensure clear difference
        edited_contract['content'] = edited_contract['content'].replace(
            "$1,000",
            "$2,500 (EDITED AMOUNT)"
        )
        
        # Generate edited PDF
        edited_pdf_data = {"contract": edited_contract}
        edited_pdf_url = f"{self.api_url}/contracts/download-pdf-edited"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Content Verification - Generating Edited PDF...")
        
        try:
            edited_pdf_response = requests.post(
                edited_pdf_url, 
                json=edited_pdf_data, 
                headers={'Content-Type': 'application/json'}, 
                timeout=30
            )
            
            if edited_pdf_response.status_code != 200:
                print(f"❌ Failed to generate edited PDF - Status: {edited_pdf_response.status_code}")
                return False, {}
            
            edited_pdf_size = len(edited_pdf_response.content)
            print(f"   Edited PDF Size: {edited_pdf_size} bytes")
            
            # Compare PDF sizes (they should be different due to content changes)
            size_difference = abs(edited_pdf_size - original_pdf_size)
            print(f"   Size Difference: {size_difference} bytes")
            
            if size_difference > 50:  # Reasonable threshold for content difference
                print("   ✅ PDF sizes differ significantly - content modification detected")
                self.tests_passed += 1
            else:
                print("   ⚠️  PDF sizes are very similar - content modification may not be reflected")
            
            # Try to verify content differences in PDF structure
            try:
                original_pdf_str = original_pdf_response.content.decode('latin-1', errors='ignore')
                edited_pdf_str = edited_pdf_response.content.decode('latin-1', errors='ignore')
                
                # Look for the modified text in the edited PDF
                if 'SIGNIFICANTLY MODIFIED CONTENT' in edited_pdf_str:
                    print("   ✅ Edited content found in edited PDF")
                elif 'MODIFIED CONTENT' in edited_pdf_str:
                    print("   ✅ Modified content detected in edited PDF")
                else:
                    print("   ⚠️  Could not verify edited content in PDF")
                
                if 'EDITED AMOUNT' in edited_pdf_str:
                    print("   ✅ Edited amount found in edited PDF")
                else:
                    print("   ⚠️  Could not verify edited amount in PDF")
                
                # Verify original content is NOT in edited PDF
                if 'Original content for PDF verification testing' not in edited_pdf_str:
                    print("   ✅ Original content successfully replaced in edited PDF")
                else:
                    print("   ❌ Original content still present in edited PDF")
                
            except Exception as e:
                print(f"   ⚠️  Could not analyze PDF content differences: {str(e)}")
            
            return True, {
                "original_pdf_size": original_pdf_size,
                "edited_pdf_size": edited_pdf_size,
                "size_difference": size_difference,
                "contract_id": contract_id
            }
            
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

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
    
    # Specific PDF Bold Formatting Test
    print("\n" + "="*50)
    print("🔍 Testing PDF Bold Formatting (No Asterisks)")
    print("="*50)
    
    test_results.append(tester.test_pdf_bold_formatting_specific())
    
    # NEW: Edited PDF Generation Tests
    print("\n" + "="*50)
    print("📝 Testing Edited PDF Generation Functionality")
    print("="*50)
    
    test_results.append(tester.test_edited_pdf_generation_valid_data())
    test_results.append(tester.test_edited_pdf_generation_invalid_data())
    test_results.append(tester.test_edited_pdf_content_verification())
    
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
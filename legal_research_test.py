#!/usr/bin/env python3
"""
Legal Research Integration Test
Tests the new legal research endpoints and functionality
"""

import asyncio
import aiohttp
import json
import time

BASE_URL = "http://localhost:8001/api"

async def test_legal_research_endpoints():
    """Test all legal research endpoints"""
    
    async with aiohttp.ClientSession() as session:
        
        print("🔍 TESTING LEGAL RESEARCH INTEGRATION")
        print("=" * 50)
        
        # Test 1: Legal Case Search
        print("\n1. Testing Legal Case Search...")
        search_payload = {
            "query": "contract breach enforcement",
            "jurisdiction": "US",
            "case_type": "contract_law",
            "max_results": 5
        }
        
        try:
            async with session.post(f"{BASE_URL}/legal-research/search", json=search_payload) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Found {data['total_found']} cases")
                    print(f"   ✅ Search time: {data['search_time']:.2f}s")
                    print(f"   ✅ AI analysis: {data['ai_analysis'][:100] if data['ai_analysis'] else 'None'}...")
                    if data['cases']:
                        print(f"   ✅ First case: {data['cases'][0]['title'][:50]}...")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test 2: Precedent Analysis
        print("\n2. Testing Precedent Analysis...")
        precedent_payload = {
            "contract_content": """
            THIS FREELANCE AGREEMENT is entered into between Company ABC ("Client") and John Doe ("Freelancer").
            
            1. SERVICES: Freelancer agrees to provide web development services.
            2. PAYMENT: Client agrees to pay $5000 upon completion.
            3. TERM: This agreement shall commence on January 1, 2024.
            4. CONFIDENTIALITY: Both parties agree to maintain confidentiality.
            """,
            "contract_type": "freelance_agreement",
            "jurisdiction": "US",
            "analysis_depth": "standard"
        }
        
        try:
            async with session.post(f"{BASE_URL}/legal-research/precedent-analysis", json=precedent_payload) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Found {len(data['similar_cases'])} similar cases")
                    print(f"   ✅ Confidence score: {data['confidence_score']}")
                    print(f"   ✅ Legal principles: {len(data['legal_principles'])}")
                    print(f"   ✅ Recommendations: {len(data['recommendations'])}")
                    if data['similar_cases']:
                        print(f"   ✅ Top case: {data['similar_cases'][0]['case']['title'][:50]}...")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test 3: Contract Legal Insights
        print("\n3. Testing Contract Legal Insights...")
        insights_payload = {
            "contract_content": """
            NON-DISCLOSURE AGREEMENT
            
            This Non-Disclosure Agreement is entered into between TechCorp Inc. and Employee.
            
            1. CONFIDENTIAL INFORMATION: Employee acknowledges access to proprietary information.
            2. NON-DISCLOSURE: Employee agrees not to disclose confidential information.
            3. RETURN OF MATERIALS: Upon termination, employee must return all materials.
            4. TERM: This agreement remains in effect for 2 years.
            """,
            "contract_type": "nda",
            "jurisdiction": "US"
        }
        
        try:
            async with session.post(f"{BASE_URL}/legal-research/contract-insight", json=insights_payload) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Risk level: {data['risk_level']}")
                    print(f"   ✅ Confidence score: {data['confidence_score']}")
                    print(f"   ✅ Key recommendations: {len(data['key_recommendations'])}")
                    print(f"   ✅ AI insights length: {len(data['ai_insights'])} chars")
                    if data['key_recommendations']:
                        print(f"   ✅ First recommendation: {data['key_recommendations'][0][:60]}...")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test 4: Get Legal Research Results
        print("\n4. Testing Get Legal Research Results...")
        try:
            async with session.get(f"{BASE_URL}/legal-research/results") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Found {data['count']} research results")
                    if data['results']:
                        print(f"   ✅ Latest result: {data['results'][0]['query']}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test 5: Get Precedent Analyses
        print("\n5. Testing Get Precedent Analyses...")
        try:
            async with session.get(f"{BASE_URL}/legal-research/precedent-analyses") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Found {data['count']} precedent analyses")
                    if data['analyses']:
                        print(f"   ✅ Latest analysis: {data['analyses'][0]['contract_type']}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 LEGAL RESEARCH INTEGRATION TESTING COMPLETED")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_legal_research_endpoints())
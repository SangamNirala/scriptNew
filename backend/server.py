from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import google.generativeai as genai
from groq import Groq
import json
import re
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
import httpx
import difflib

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI API Setup
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
groq_client = Groq(api_key=os.environ['GROQ_API_KEY'])

# OpenRouter client setup
openrouter_client = httpx.AsyncClient(
    base_url="https://openrouter.ai/api/v1",
    headers={
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "LegalMate AI"
    }
)

# Hugging Face client setup
huggingface_client = httpx.AsyncClient(
    base_url="https://api-inference.huggingface.co/models",
    headers={
        "Authorization": f"Bearer {os.environ['HUGGINGFACE_API_KEY']}"
    }
)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class ContractRequest(BaseModel):
    contract_type: str
    parties: Dict[str, Any]
    terms: Dict[str, Any] 
    jurisdiction: str = "US"
    special_clauses: Optional[List[str]] = []
    execution_date: Optional[str] = None

class GeneratedContract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_type: str
    jurisdiction: str
    content: str
    clauses: List[Dict[str, Any]]
    compliance_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    first_party_signature: Optional[str] = None  # Base64 encoded signature image
    second_party_signature: Optional[str] = None  # Base64 encoded signature image

class ContractResponse(BaseModel):
    contract: GeneratedContract
    warnings: List[str] = []
    suggestions: List[str] = []

# New models for Smart Contract Analysis
class ContractAnalysisRequest(BaseModel):
    contract_content: str
    contract_type: Optional[str] = None
    jurisdiction: str = "US"

class RiskAssessment(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]

class ClauseRecommendation(BaseModel):
    clause_type: str
    title: str
    content: str
    priority: str  # "HIGH", "MEDIUM", "LOW"
    reasoning: str
    industry_specific: bool = False

class ContractAnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract_content: str
    contract_type: Optional[str]
    jurisdiction: str
    risk_assessment: RiskAssessment
    clause_recommendations: List[ClauseRecommendation]
    compliance_issues: List[Dict[str, Any]]
    readability_score: float
    completeness_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContractComparisonRequest(BaseModel):
    contract1_content: str
    contract2_content: str
    contract1_label: str = "Contract A"
    contract2_label: str = "Contract B"

class ContractDifference(BaseModel):
    type: str  # "addition", "deletion", "modification"
    section: str
    contract1_text: Optional[str]
    contract2_text: Optional[str]
    significance: str  # "HIGH", "MEDIUM", "LOW"
    description: str

class ContractComparisonResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contract1_label: str
    contract2_label: str
    differences: List[ContractDifference]
    similarity_score: float
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Multi-Agent System
class LegalMateAgents:
    
    @staticmethod
    async def intake_agent(request: ContractRequest) -> Dict[str, Any]:
        """Parses and structures user input into legal requirements"""
        prompt = f"""
        You are a legal intake specialist. Parse this contract request and extract key legal requirements:
        
        Contract Type: {request.contract_type}
        Parties: {request.parties}
        Terms: {request.terms}
        Jurisdiction: {request.jurisdiction}
        Special Clauses: {request.special_clauses}
        
        Return a structured analysis in JSON format with:
        - contract_classification
        - key_parties (with roles)
        - essential_terms
        - risk_factors
        - required_clauses
        - jurisdiction_requirements
        
        Be precise and legally oriented.
        """
        
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1500
            )
            
            response_text = chat_completion.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback structure
                return {
                    "contract_classification": request.contract_type,
                    "key_parties": request.parties,
                    "essential_terms": request.terms,
                    "risk_factors": [],
                    "required_clauses": ["governing_law", "dispute_resolution"],
                    "jurisdiction_requirements": [request.jurisdiction]
                }
        except Exception as e:
            logging.error(f"Intake agent error: {e}")
            return {
                "contract_classification": request.contract_type,
                "key_parties": request.parties,
                "essential_terms": request.terms,
                "risk_factors": ["parsing_error"],
                "required_clauses": ["governing_law"],
                "jurisdiction_requirements": [request.jurisdiction]
            }

    @staticmethod
    async def contract_generator(structured_requirements: Dict[str, Any], contract_type: str) -> str:
        """Generates the actual contract content"""
        
        # Contract templates and prompts - Expanded to 50+ types
        contract_prompts = {
            # Business Contracts
            "NDA": """
            Generate a professional Non-Disclosure Agreement with these requirements:
            {requirements}
            
            FORMATTING REQUIREMENTS:
            - Remove all instances of asterisk (*) expressions 
            - Use proper bold formatting for headings and key sections using **text** format
            - Include a line for Date of Execution: [Date of Execution] before any special clauses section
            - Use proper paragraph spacing and professional formatting
            
            Include standard clauses:
            - Definition of Confidential Information
            - Permitted Uses and Restrictions
            - Duration of Agreement
            - Return of Materials
            - Remedies for Breach
            - Governing Law and Jurisdiction
            """,
            
            "employment_agreement": """
            Generate a comprehensive Employment Agreement including:
            {requirements}
            
            FORMATTING REQUIREMENTS:
            - Remove all instances of asterisk (*) expressions 
            - Use proper bold formatting for headings and key sections using **text** format
            - Include Date of Execution: [Date of Execution]
            
            Include essential clauses:
            - Job Title and Description
            - Compensation and Benefits
            - Working Hours and Location
            - Confidentiality and Non-Compete
            - Termination Conditions
            - Intellectual Property Rights
            """,
            
            "freelance_agreement": """
            Generate a comprehensive Freelance Service Agreement with:
            {requirements}
            
            FORMATTING REQUIREMENTS:
            - Remove all instances of asterisk (*) expressions 
            - Use proper bold formatting for headings and key sections using **text** format
            - Include Date of Execution: [Date of Execution]
            
            Include essential clauses:
            - Scope of Work
            - Payment Terms
            - Intellectual Property Rights
            - Termination Conditions
            - Liability Limitations
            - Governing Law
            """,
            
            "partnership_agreement": """
            Generate a Business Partnership Agreement including:
            {requirements}
            
            FORMATTING REQUIREMENTS:
            - Remove all instances of asterisk (*) expressions 
            - Use proper bold formatting for headings and key sections using **text** format
            - Include Date of Execution: [Date of Execution]
            
            Cover key areas:
            - Partnership Structure
            - Capital Contributions
            - Profit/Loss Distribution
            - Decision Making Process
            - Dissolution Procedures
            - Governing Law
            """,
            
            "consulting_agreement": """
            Generate a Professional Consulting Agreement with:
            {requirements}
            
            Include: Services Description, Payment Terms, Confidentiality, Deliverables, Timeline
            """,
            
            "software_license": """
            Generate a Software License Agreement with:
            {requirements}
            
            Include: License Grant, Restrictions, Support Terms, Liability Limitations, Updates
            """,
            
            "vendor_agreement": """
            Generate a Vendor/Supplier Agreement with:
            {requirements}
            
            Include: Supply Terms, Quality Standards, Payment Terms, Delivery, Warranties
            """,
            
            "distribution_agreement": """
            Generate a Distribution Agreement with:
            {requirements}
            
            Include: Territory Rights, Sales Targets, Marketing, Pricing, Termination
            """,
            
            "franchise_agreement": """
            Generate a Franchise Agreement with:
            {requirements}
            
            Include: Franchise Rights, Fees, Territory, Standards, Training, Support
            """,
            
            "joint_venture": """
            Generate a Joint Venture Agreement with:
            {requirements}
            
            Include: Venture Purpose, Contributions, Management, Profit Sharing, Exit Terms
            """,
            
            "merger_acquisition": """
            Generate a Merger & Acquisition Agreement with:
            {requirements}
            
            Include: Purchase Price, Due Diligence, Representations, Closing Conditions
            """,
            
            "shareholder_agreement": """
            Generate a Shareholder Agreement with:
            {requirements}
            
            Include: Share Rights, Transfer Restrictions, Board Composition, Dividends
            """,
            
            "loan_agreement": """
            Generate a Business Loan Agreement with:
            {requirements}
            
            Include: Loan Amount, Interest Rate, Repayment Terms, Security, Default Provisions
            """,
            
            "equipment_lease": """
            Generate an Equipment Lease Agreement with:
            {requirements}
            
            Include: Equipment Description, Lease Terms, Maintenance, Insurance, Return Conditions
            """,
            
            "service_agreement": """
            Generate a General Service Agreement with:
            {requirements}
            
            Include: Service Description, Performance Standards, Payment, Liability, Termination
            """,
            
            "licensing_agreement": """
            Generate an Intellectual Property Licensing Agreement with:
            {requirements}
            
            Include: Licensed Property, Royalties, Territory, Quality Control, Termination
            """,
            
            "manufacturing_agreement": """
            Generate a Manufacturing Agreement with:
            {requirements}
            
            Include: Product Specifications, Quality Standards, Delivery, Payment, IP Rights
            """,
            
            "marketing_agreement": """
            Generate a Marketing Services Agreement with:
            {requirements}
            
            Include: Marketing Services, Budget, Performance Metrics, IP Rights, Confidentiality
            """,
            
            "research_agreement": """
            Generate a Research & Development Agreement with:
            {requirements}
            
            Include: Research Scope, Funding, IP Ownership, Publication Rights, Commercialization
            """,
            
            "maintenance_agreement": """
            Generate a Maintenance Service Agreement with:
            {requirements}
            
            Include: Maintenance Scope, Response Times, Service Levels, Payment, Liability
            """,
            
            "supply_agreement": """
            Generate a Supply Agreement with:
            {requirements}
            
            Include: Product Specifications, Quantities, Delivery Terms, Quality Standards, Payment
            """,
            
            "technology_transfer": """
            Generate a Technology Transfer Agreement with:
            {requirements}
            
            Include: Technology Description, Transfer Terms, Royalties, Support, Restrictions
            """,
            
            "indemnification_agreement": """
            Generate an Indemnification Agreement with:
            {requirements}
            
            Include: Indemnification Scope, Conditions, Procedures, Limitations, Defense Obligations
            """,
            
            "non_compete": """
            Generate a Non-Compete Agreement with:
            {requirements}
            
            Include: Restricted Activities, Territory, Duration, Consideration, Remedies
            """,
            
            "settlement_agreement": """
            Generate a Settlement Agreement with:
            {requirements}
            
            Include: Dispute Description, Settlement Terms, Release, Confidentiality, Enforcement
            """,
            
            # Real Estate Contracts
            "purchase_agreement": """
            Generate a Real Estate Purchase Agreement with:
            {requirements}
            
            Include: Property Description, Purchase Price, Financing Terms, Inspections, Closing
            """,
            
            "lease_agreement": """
            Generate a Real Estate Lease Agreement with:
            {requirements}
            
            Include: Property Description, Rent Terms, Security Deposit, Maintenance, Utilities
            """,
            
            "property_management": """
            Generate a Property Management Agreement with:
            {requirements}
            
            Include: Management Services, Fees, Tenant Relations, Maintenance, Financial Reporting
            """,
            
            "construction_contract": """
            Generate a Construction Contract with:
            {requirements}
            
            Include: Work Description, Timeline, Payment Schedule, Materials, Change Orders
            """,
            
            "commercial_lease": """
            Generate a Commercial Lease Agreement with:
            {requirements}
            
            Include: Premises, Rent, Operating Expenses, Use Restrictions, Improvements
            """,
            
            "residential_lease": """
            Generate a Residential Lease Agreement with:
            {requirements}
            
            Include: Property Details, Rent, Security Deposit, Pet Policy, Maintenance
            """,
            
            "deed_of_trust": """
            Generate a Deed of Trust with:
            {requirements}
            
            Include: Property Description, Loan Terms, Trustee Powers, Default Provisions
            """,
            
            "easement_agreement": """
            Generate an Easement Agreement with:
            {requirements}
            
            Include: Easement Purpose, Location, Rights Granted, Maintenance, Compensation
            """,
            
            "option_to_purchase": """
            Generate an Option to Purchase Agreement with:
            {requirements}
            
            Include: Property Description, Option Price, Exercise Terms, Conditions
            """,
            
            "listing_agreement": """
            Generate a Real Estate Listing Agreement with:
            {requirements}
            
            Include: Property Details, Commission, Marketing, Exclusivity, Duration
            """,
            
            "land_contract": """
            Generate a Land Contract with:
            {requirements}
            
            Include: Property Description, Purchase Terms, Payments, Title Transfer, Default
            """,
            
            "development_agreement": """
            Generate a Real Estate Development Agreement with:
            {requirements}
            
            Include: Development Plan, Timeline, Approvals, Financing, Profit Sharing
            """,
            
            "tenant_improvement": """
            Generate a Tenant Improvement Agreement with:
            {requirements}
            
            Include: Improvement Scope, Cost Allocation, Timeline, Approval Process
            """,
            
            "property_sale": """
            Generate a Property Sale Agreement with:
            {requirements}
            
            Include: Sale Terms, Conditions, Warranties, Closing Requirements, Adjustments
            """,
            
            "sublease_agreement": """
            Generate a Sublease Agreement with:
            {requirements}
            
            Include: Sublease Terms, Consent Requirements, Responsibilities, Rent, Duration
            """,
            
            "ground_lease": """
            Generate a Ground Lease Agreement with:
            {requirements}
            
            Include: Land Description, Lease Term, Ground Rent, Improvements, Reversion
            """,
            
            "mortgage_agreement": """
            Generate a Mortgage Agreement with:
            {requirements}
            
            Include: Loan Amount, Interest Rate, Payment Terms, Property Description, Default
            """,
            
            "escrow_agreement": """
            Generate an Escrow Agreement with:
            {requirements}
            
            Include: Escrow Purpose, Conditions, Agent Duties, Release Terms, Fees
            """,
            
            "brokerage_agreement": """
            Generate a Real Estate Brokerage Agreement with:
            {requirements}
            
            Include: Services, Commission Structure, Obligations, Duration, Termination
            """,
            
            "right_of_first_refusal": """
            Generate a Right of First Refusal Agreement with:
            {requirements}
            
            Include: Property Description, Trigger Events, Exercise Terms, Valuation
            """,
            
            # Additional Business Contracts
            "confidentiality_agreement": """
            Generate a Confidentiality Agreement with:
            {requirements}
            
            Include: Confidential Information Definition, Use Restrictions, Duration, Remedies
            """,
            
            "agency_agreement": """
            Generate an Agency Agreement with:
            {requirements}
            
            Include: Agency Scope, Authority, Compensation, Duration, Termination
            """,
            
            "insurance_agreement": """
            Generate an Insurance Service Agreement with:
            {requirements}
            
            Include: Coverage Types, Premiums, Claims Process, Policy Terms, Renewal
            """,
            
            "catering_agreement": """
            Generate a Catering Services Agreement with:
            {requirements}
            
            Include: Event Details, Menu, Pricing, Setup, Cancellation, Liability
            """,
            
            "transportation_agreement": """
            Generate a Transportation Services Agreement with:
            {requirements}
            
            Include: Transport Services, Routes, Scheduling, Rates, Liability, Insurance
            """,
            
            "security_agreement": """
            Generate a Security Services Agreement with:
            {requirements}
            
            Include: Security Services, Coverage Hours, Personnel, Equipment, Reporting
            """,
            
            "cleaning_agreement": """
            Generate a Cleaning Services Agreement with:
            {requirements}
            
            Include: Cleaning Scope, Schedule, Supplies, Quality Standards, Pricing
            """,
            
            "photography_agreement": """
            Generate a Photography Services Agreement with:
            {requirements}
            
            Include: Event Coverage, Deliverables, Usage Rights, Payment, Cancellation
            """,
            
            "web_development": """
            Generate a Web Development Agreement with:
            {requirements}
            
            Include: Project Scope, Timeline, Deliverables, Hosting, Maintenance, IP Rights
            """,
            
            "advertising_agreement": """
            Generate an Advertising Services Agreement with:
            {requirements}
            
            Include: Campaign Details, Media Placement, Budget, Performance Metrics, Rights
            """
        }
        
        # Extract party names safely
        key_parties = structured_requirements.get('key_parties', {})
        if isinstance(key_parties, dict):
            party1_name = key_parties.get('party1_name', 'First Party')
            party2_name = key_parties.get('party2_name', 'Second Party')
        else:
            # Fallback if key_parties is not a dict (e.g., it's a list or other type)
            party1_name = 'First Party'
            party2_name = 'Second Party'
        
        # Add signature section template to all contracts
        signature_section = f"""
            
            **SIGNATURES**
            
            IN WITNESS WHEREOF, the parties have executed this agreement as of the Effective Date.
            
            **FIRST PARTY:**
            
            [First Party Signature Placeholder]
            _________________________________
            {party1_name}
            
            **SECOND PARTY:**
            
            [Second Party Signature Placeholder] 
            _________________________________
            {party2_name}
        """
        
        # Get the base prompt
        base_prompt = contract_prompts.get(contract_type, contract_prompts["NDA"])
        
        # Add signature section if not already present
        if "**SIGNATURES**" not in base_prompt:
            base_prompt += signature_section
        
        prompt = base_prompt.format(
            requirements=json.dumps(structured_requirements, indent=2),
            party1_name=party1_name,
            party2_name=party2_name
        )
        
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=4000,
                    temperature=0.1,
                )
            )
            
            # Post-process the generated content to ensure formatting requirements
            formatted_content = LegalMateAgents.format_contract_content(response.text)
            return formatted_content
            
        except Exception as e:
            logging.error(f"Contract generator error: {e}")
            # Fallback simple contract
            fallback_content = f"""
            **{contract_type.upper()} AGREEMENT**

            **Date of Execution:** [Date of Execution]

            This agreement is entered into between the parties as specified.

            **WHEREAS**, the parties wish to enter into this {contract_type} agreement;

            **NOW, THEREFORE**, the parties agree as follows:

            **1. SCOPE:** As defined in the attached terms.
            **2. TERMS:** {structured_requirements.get('essential_terms', {})}
            **3. GOVERNING LAW:** This agreement shall be governed by the laws of {structured_requirements.get('jurisdiction_requirements', ['US'])[0]}.

            [This is a simplified fallback contract. Please review with legal counsel.]
            """
            return LegalMateAgents.format_contract_content(fallback_content)

    @staticmethod
    def format_contract_content(content: str) -> str:
        """Post-process contract content to ensure formatting requirements are met"""
        
        # Remove single asterisks but preserve **bold** formatting
        # First, temporarily replace **bold** patterns with placeholders
        bold_patterns = re.findall(r'\*\*[^*]+\*\*', content)
        temp_replacements = {}
        for i, pattern in enumerate(bold_patterns):
            placeholder = f"__BOLD_PLACEHOLDER_{i}__"
            temp_replacements[placeholder] = pattern
            content = content.replace(pattern, placeholder, 1)
        
        # Now remove all remaining single asterisks and malformed asterisk expressions
        content = re.sub(r'\*+(?!\*)', '', content)  # Remove single or multiple asterisks but not **
        content = re.sub(r'(?<!\*)\*(?!\*)', '', content)  # Remove isolated single asterisks
        
        # Restore **bold** formatting
        for placeholder, original in temp_replacements.items():
            content = content.replace(placeholder, original)
        
        # Ensure Date of Execution line exists if not already present
        if '[Date of Execution]' not in content and 'Date of Execution' not in content:
            # Insert Date of Execution line after the title but before main content
            lines = content.split('\n')
            title_found = False
            for i, line in enumerate(lines):
                if ('AGREEMENT' in line.upper() or 'CONTRACT' in line.upper()) and not title_found:
                    title_found = True
                    continue
                elif title_found and line.strip() and not line.strip().startswith('**Date'):
                    lines.insert(i, '')
                    lines.insert(i+1, '**Date of Execution:** [Date of Execution]')
                    lines.insert(i+2, '')
                    break
            content = '\n'.join(lines)
        
        # Clean up excessive whitespace while preserving paragraph structure
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()
        
        return content

    @staticmethod
    def convert_markdown_to_html_bold(text: str) -> str:
        """Convert **markdown bold** to <b>HTML bold</b> for reportlab"""
        return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

    @staticmethod
    def process_signature_image_robust(signature_base64: str) -> io.BytesIO:
        """
        Robust signature image processing that converts image to standardized base64 format
        and creates reliable BytesIO buffer for reportlab PDF generation
        """
        try:
            # Remove data URL prefix if present
            if signature_base64.startswith('data:image'):
                signature_base64 = signature_base64.split(',')[1]
            
            # Decode the base64 data
            signature_data = base64.b64decode(signature_base64)
            
            # Open image with PIL for processing
            input_buffer = io.BytesIO(signature_data)
            
            with PILImage.open(input_buffer) as original_image:
                # Convert to RGB to ensure compatibility (removes alpha channel if present)
                if original_image.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    rgb_image = PILImage.new('RGB', original_image.size, (255, 255, 255))
                    if original_image.mode == 'P':
                        original_image = original_image.convert('RGBA')
                    rgb_image.paste(original_image, mask=original_image.split()[-1] if original_image.mode in ('RGBA', 'LA') else None)
                    processed_image = rgb_image
                elif original_image.mode != 'RGB':
                    processed_image = original_image.convert('RGB')
                else:
                    processed_image = original_image.copy()
                
                # Resize if the image is too large (max 400x200 for signatures)
                max_width, max_height = 400, 200
                if processed_image.size[0] > max_width or processed_image.size[1] > max_height:
                    processed_image.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
                
                # Save the processed image to a new buffer as PNG
                processed_buffer = io.BytesIO()
                processed_image.save(processed_buffer, format='PNG', optimize=True)
                
                # Convert processed image back to base64 for consistent handling
                processed_buffer.seek(0)
                processed_base64 = base64.b64encode(processed_buffer.getvalue()).decode('utf-8')
                
                # Create final BytesIO buffer from the processed base64
                final_signature_data = base64.b64decode(processed_base64)
                final_buffer = io.BytesIO(final_signature_data)
                final_buffer.seek(0)
                
                logging.info(f"Successfully processed signature image: {processed_image.size} pixels, {len(final_signature_data)} bytes")
                return final_buffer
                
        except Exception as e:
            logging.error(f"Error in robust signature processing: {str(e)}")
            # Try fallback method - direct processing
            try:
                logging.info("Attempting fallback signature processing...")
                if signature_base64.startswith('data:image'):
                    signature_base64 = signature_base64.split(',')[1]
                
                signature_data = base64.b64decode(signature_base64)
                fallback_buffer = io.BytesIO(signature_data)
                fallback_buffer.seek(0)
                return fallback_buffer
            except Exception as fallback_error:
                logging.error(f"Fallback signature processing also failed: {fallback_error}")
                raise Exception(f"Unable to process signature image: {str(e)}")
    
    @staticmethod
    def process_signature_image(signature_base64: str) -> io.BytesIO:
        """Legacy method - delegates to robust processing"""
        return LegalMateAgents.process_signature_image_robust(signature_base64)
    
    @staticmethod
    def process_signature_image_direct(signature_base64: str) -> io.BytesIO:
        """Legacy method - delegates to robust processing"""  
        return LegalMateAgents.process_signature_image_robust(signature_base64)

    @staticmethod
    def process_signature_content(content: str, first_party_signature: str = None, second_party_signature: str = None) -> tuple:
        """Process contract content and return content with signature elements separated"""
        
        # Split content into main content and signature section
        signature_section_start = content.find("**SIGNATURES**")
        
        if signature_section_start == -1:
            # No signature section found, return content as is
            return content, [], []
        
        main_content = content[:signature_section_start]
        signature_content = content[signature_section_start:]
        
        # Extract signature placeholders and party names
        first_party_info = {}
        second_party_info = {}
        
        # Look for First Party signature placeholder (both original and uploaded versions)
        first_match = re.search(r'\[First Party Signature (?:Placeholder|Uploaded)\]\s*\n_+\s*\n(.+)', signature_content)
        if first_match:
            first_party_info['name'] = first_match.group(1).strip()
            first_party_info['signature'] = first_party_signature
        
        # Look for Second Party signature placeholder (both original and uploaded versions)  
        second_match = re.search(r'\[Second Party Signature (?:Placeholder|Uploaded)\]\s*\n_+\s*\n(.+)', signature_content)
        if second_match:
            second_party_info['name'] = second_match.group(1).strip()
            second_party_info['signature'] = second_party_signature
        
        return main_content, first_party_info, second_party_info

    @staticmethod
    def replace_execution_date(content: str, execution_date: str = None) -> str:
        """Replace [Date of Execution] placeholder with actual date"""
        if execution_date:
            try:
                # Parse the ISO date string and format it nicely
                date_obj = datetime.fromisoformat(execution_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%B %d, %Y')
                content = content.replace('[Date of Execution]', formatted_date)
            except Exception as e:
                logging.warning(f"Error parsing execution date {execution_date}: {e}")
                # Fallback to current date if parsing fails
                current_date = datetime.now().strftime('%B %d, %Y')
                content = content.replace('[Date of Execution]', current_date)
        else:
            # If no date provided, use current date
            current_date = datetime.now().strftime('%B %d, %Y')
            content = content.replace('[Date of Execution]', current_date)
        
        return content

    @staticmethod
    async def compliance_validator(contract_content: str, jurisdiction: str) -> Dict[str, Any]:
        """Validates contract compliance and assigns score"""
        
        prompt = f"""
        As a legal compliance expert, analyze this contract for {jurisdiction} jurisdiction:
        
        {contract_content}
        
        Evaluate:
        1. Legal completeness (essential clauses present)
        2. Jurisdiction compliance
        3. Enforceability factors
        4. Risk areas
        
        Return JSON with:
        - compliance_score (0-100)
        - missing_clauses []
        - risk_warnings []
        - suggestions []
        """
        
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1000
            )
            
            response_text = chat_completion.choices[0].message.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "compliance_score": 75.0,
                    "missing_clauses": [],
                    "risk_warnings": ["Please review with legal counsel"],
                    "suggestions": ["Consider adding termination clause"]
                }
        except Exception as e:
            logging.error(f"Compliance validator error: {e}")
            return {
                "compliance_score": 70.0,
                "missing_clauses": ["unknown"],
                "risk_warnings": ["Validation error occurred"],
                "suggestions": ["Manual review required"]
            }

    @staticmethod
    def extract_clauses(contract_content: str) -> List[Dict[str, Any]]:
        """Extracts and structures contract clauses"""
        # Simple clause extraction logic
        clauses = []
        lines = contract_content.split('\n')
        current_clause = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('WHEREAS') or line.startswith('NOW')):
                if current_clause:
                    clauses.append({
                        "title": current_clause,
                        "content": ' '.join(current_content),
                        "type": "standard",
                        "editable": True
                    })
                current_clause = line
                current_content = []
            elif line:
                current_content.append(line)
        
        if current_clause:
            clauses.append({
                "title": current_clause,
                "content": ' '.join(current_content),
                "type": "standard", 
                "editable": True
            })
        
        return clauses


# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "LegalMate AI - Contract Generation API"}

@api_router.post("/generate-contract", response_model=ContractResponse)
async def generate_contract(request: ContractRequest):
    """Main contract generation endpoint"""
    try:
        # Step 1: Intake Analysis
        structured_requirements = await LegalMateAgents.intake_agent(request)
        logging.info(f"Structured requirements type: {type(structured_requirements)}")
        
        # Step 2: Generate Contract
        contract_content = await LegalMateAgents.contract_generator(
            structured_requirements, request.contract_type
        )
        
        # Step 3: Compliance Validation
        compliance_result = await LegalMateAgents.compliance_validator(
            contract_content, request.jurisdiction
        )
        logging.info(f"Compliance result type: {type(compliance_result)}")
        
        # Step 4: Extract Clauses
        clauses = LegalMateAgents.extract_clauses(contract_content)
        
        # Step 5: Replace execution date placeholder with actual date
        contract_content = LegalMateAgents.replace_execution_date(
            contract_content, request.execution_date
        )
        
        # Ensure compliance_result is a dictionary
        if not isinstance(compliance_result, dict):
            logging.warning(f"Compliance result is not a dict: {type(compliance_result)}, value: {compliance_result}")
            compliance_result = {
                "compliance_score": 75.0,
                "risk_warnings": ["Compliance validation returned unexpected format"],
                "suggestions": ["Manual review recommended"]
            }
        
        # Create contract object
        generated_contract = GeneratedContract(
            contract_type=request.contract_type,
            jurisdiction=request.jurisdiction,
            content=contract_content,
            clauses=clauses,
            compliance_score=compliance_result.get('compliance_score', 75.0)
        )
        
        # Save to database
        await db.contracts.insert_one(generated_contract.dict())
        
        # Prepare response
        response = ContractResponse(
            contract=generated_contract,
            warnings=compliance_result.get('risk_warnings', []),
            suggestions=compliance_result.get('suggestions', [])
        )
        
        return response
        
    except Exception as e:
        logging.error(f"Contract generation error: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating contract: {str(e)}")

@api_router.get("/contracts", response_model=List[GeneratedContract])
async def get_contracts():
    """Get all generated contracts"""
    try:
        contracts = await db.contracts.find().to_list(100)
        return [GeneratedContract(**contract) for contract in contracts]
    except Exception as e:
        logging.error(f"Error fetching contracts: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching contracts: {str(e)}")

@api_router.get("/contracts/{contract_id}", response_model=GeneratedContract)
async def get_contract(contract_id: str):
    """Get specific contract by ID"""
    try:
        contract = await db.contracts.find_one({"id": contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return GeneratedContract(**contract)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching contract: {str(e)}")

@api_router.get("/contract-types")
async def get_contract_types():
    """Get available contract types"""
    return {
        "types": [
            {
                "id": "NDA",
                "name": "Non-Disclosure Agreement",
                "description": "Protect confidential information",
                "complexity": "Simple"
            },
            {
                "id": "freelance_agreement", 
                "name": "Freelance Agreement",
                "description": "Service contracts for freelancers",
                "complexity": "Medium"
            },
            {
                "id": "partnership_agreement",
                "name": "Partnership Agreement", 
                "description": "Business partnership contracts",
                "complexity": "Complex"
            }
        ]
    }

@api_router.get("/jurisdictions")
async def get_jurisdictions():
    """Get supported jurisdictions"""
    return {
        "jurisdictions": [
            {"code": "US", "name": "United States", "supported": True},
            {"code": "UK", "name": "United Kingdom", "supported": True},
            {"code": "EU", "name": "European Union", "supported": True},
            {"code": "CA", "name": "Canada", "supported": False},
            {"code": "AU", "name": "Australia", "supported": False}
        ]
    }

@api_router.get("/contracts/{contract_id}/download-pdf")
async def download_contract_pdf(contract_id: str):
    """Generate and download PDF for a specific contract"""
    try:
        # Get the contract from database
        contract = await db.contracts.find_one({"id": contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Build PDF content
        content = []
        
        # Title
        title = f"{contract['contract_type'].upper()} CONTRACT"
        content.append(Paragraph(title, title_style))
        content.append(Spacer(1, 12))
        
        # Contract metadata
        metadata_style = styles['Normal']
        content.append(Paragraph(f"<b>Contract ID:</b> {contract['id']}", metadata_style))
        content.append(Paragraph(f"<b>Jurisdiction:</b> {contract['jurisdiction']}", metadata_style))
        content.append(Paragraph(f"<b>Generated:</b> {contract['created_at']}", metadata_style))
        content.append(Paragraph(f"<b>Compliance Score:</b> {contract['compliance_score']:.0f}%", metadata_style))
        content.append(Spacer(1, 20))
        
        # Contract content with signature processing
        contract_content = contract['content']
        first_party_signature = contract.get('first_party_signature')
        second_party_signature = contract.get('second_party_signature')
        
        # Process content and extract signature information
        main_content, first_party_info, second_party_info = LegalMateAgents.process_signature_content(
            contract_content, first_party_signature, second_party_signature
        )
        
        # Split main content into paragraphs and add to PDF with proper bold formatting
        paragraphs = main_content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                # Process bold formatting - convert **text** to <b>text</b> for reportlab
                formatted_paragraph = LegalMateAgents.convert_markdown_to_html_bold(paragraph.strip())
                content.append(Paragraph(formatted_paragraph, styles['Normal']))
                content.append(Spacer(1, 12))
        
        # Add signature section if present
        if first_party_info or second_party_info:
            content.append(Spacer(1, 20))
            content.append(Paragraph("<b>SIGNATURES</b>", styles['Heading2']))
            content.append(Spacer(1, 12))
            content.append(Paragraph("IN WITNESS WHEREOF, the parties have executed this agreement as of the Effective Date.", styles['Normal']))
            content.append(Spacer(1, 20))
            
            # First Party signature
            if first_party_info:
                content.append(Paragraph("<b>FIRST PARTY:</b>", styles['Normal']))
                content.append(Spacer(1, 12))
                
                if first_party_info.get('signature'):
                    try:
                        # Use robust base64 processing with PIL standardization
                        signature_buffer = LegalMateAgents.process_signature_image_robust(first_party_info['signature'])
                        # Create reportlab Image with better error handling
                        signature_image = Image(signature_buffer, width=2*inch, height=0.8*inch)
                        content.append(signature_image)
                        logging.info("Successfully added first party signature to PDF")
                    except Exception as e:
                        logging.error(f"Error processing first party signature for PDF: {e}")
                        content.append(Paragraph("[Signature Image Error]", styles['Normal']))
                else:
                    content.append(Spacer(1, 30))  # Space for manual signature
                
                content.append(Paragraph("_" * 50, styles['Normal']))
                content.append(Paragraph(first_party_info.get('name', 'First Party'), styles['Normal']))
                content.append(Spacer(1, 20))
            
            # Second Party signature
            if second_party_info:
                content.append(Paragraph("<b>SECOND PARTY:</b>", styles['Normal']))
                content.append(Spacer(1, 12))
                
                if second_party_info.get('signature'):
                    try:
                        # Use robust base64 processing with PIL standardization
                        signature_buffer = LegalMateAgents.process_signature_image_robust(second_party_info['signature'])
                        # Create reportlab Image with better error handling
                        signature_image = Image(signature_buffer, width=2*inch, height=0.8*inch)
                        content.append(signature_image)
                        logging.info("Successfully added second party signature to PDF")
                    except Exception as e:
                        logging.error(f"Error processing second party signature for PDF: {e}")
                        content.append(Paragraph("[Signature Image Error]", styles['Normal']))
                else:
                    content.append(Spacer(1, 30))  # Space for manual signature
                
                content.append(Paragraph("_" * 50, styles['Normal']))
                content.append(Paragraph(second_party_info.get('name', 'Second Party'), styles['Normal']))
                content.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(content)
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Create filename
        filename = f"contract_{contract_id}.pdf"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_data),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating PDF for contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

class EditedContractRequest(BaseModel):
    contract: Dict[str, Any]

@api_router.post("/contracts/download-pdf-edited")
async def download_edited_contract_pdf(request: EditedContractRequest):
    """Generate and download PDF for edited contract content"""
    try:
        contract = request.contract
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Build PDF content
        content = []
        
        # Title
        title = f"{contract['contract_type'].upper()} CONTRACT"
        content.append(Paragraph(title, title_style))
        content.append(Spacer(1, 12))
        
        # Contract metadata
        metadata_style = styles['Normal']
        content.append(Paragraph(f"<b>Contract ID:</b> {contract['id']}", metadata_style))
        content.append(Paragraph(f"<b>Jurisdiction:</b> {contract['jurisdiction']}", metadata_style))
        content.append(Paragraph(f"<b>Generated:</b> {contract['created_at']}", metadata_style))
        content.append(Paragraph(f"<b>Compliance Score:</b> {contract['compliance_score']:.0f}%", metadata_style))
        content.append(Paragraph("<b>Status:</b> Edited", metadata_style))
        content.append(Spacer(1, 20))
        
        # Contract content (edited) with signature processing
        contract_content = contract['content']
        first_party_signature = contract.get('first_party_signature')
        second_party_signature = contract.get('second_party_signature')
        
        # Process content and extract signature information
        main_content, first_party_info, second_party_info = LegalMateAgents.process_signature_content(
            contract_content, first_party_signature, second_party_signature
        )
        
        # Split main content into paragraphs and add to PDF with proper bold formatting
        paragraphs = main_content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                # Process bold formatting - convert **text** to <b>text</b> for reportlab
                formatted_paragraph = LegalMateAgents.convert_markdown_to_html_bold(paragraph.strip())
                content.append(Paragraph(formatted_paragraph, styles['Normal']))
                content.append(Spacer(1, 12))
        
        # Add signature section if present
        if first_party_info or second_party_info:
            content.append(Spacer(1, 20))
            content.append(Paragraph("<b>SIGNATURES</b>", styles['Heading2']))
            content.append(Spacer(1, 12))
            content.append(Paragraph("IN WITNESS WHEREOF, the parties have executed this agreement as of the Effective Date.", styles['Normal']))
            content.append(Spacer(1, 20))
            
            # First Party signature
            if first_party_info:
                content.append(Paragraph("<b>FIRST PARTY:</b>", styles['Normal']))
                content.append(Spacer(1, 12))
                
                if first_party_info.get('signature'):
                    try:
                        # Use robust base64 processing with PIL standardization
                        signature_buffer = LegalMateAgents.process_signature_image_robust(first_party_info['signature'])
                        # Create reportlab Image with better error handling
                        signature_image = Image(signature_buffer, width=2*inch, height=0.8*inch)
                        content.append(signature_image)
                        logging.info("Successfully added first party signature to PDF")
                    except Exception as e:
                        logging.error(f"Error processing first party signature for PDF: {e}")
                        content.append(Paragraph("[Signature Image Error]", styles['Normal']))
                else:
                    content.append(Spacer(1, 30))  # Space for manual signature
                
                content.append(Paragraph("_" * 50, styles['Normal']))
                content.append(Paragraph(first_party_info.get('name', 'First Party'), styles['Normal']))
                content.append(Spacer(1, 20))
            
            # Second Party signature
            if second_party_info:
                content.append(Paragraph("<b>SECOND PARTY:</b>", styles['Normal']))
                content.append(Spacer(1, 12))
                
                if second_party_info.get('signature'):
                    try:
                        # Use robust base64 processing with PIL standardization
                        signature_buffer = LegalMateAgents.process_signature_image_robust(second_party_info['signature'])
                        # Create reportlab Image with better error handling
                        signature_image = Image(signature_buffer, width=2*inch, height=0.8*inch)
                        content.append(signature_image)
                        logging.info("Successfully added second party signature to PDF")
                    except Exception as e:
                        logging.error(f"Error processing second party signature for PDF: {e}")
                        content.append(Paragraph("[Signature Image Error]", styles['Normal']))
                else:
                    content.append(Spacer(1, 30))  # Space for manual signature
                
                content.append(Paragraph("_" * 50, styles['Normal']))
                content.append(Paragraph(second_party_info.get('name', 'Second Party'), styles['Normal']))
                content.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(content)
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Create filename
        filename = f"contract_{contract['id']}_edited.pdf"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_data),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logging.error(f"Error generating edited PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# Signature upload models
class SignatureUploadRequest(BaseModel):
    contract_id: str
    party_type: str  # "first_party" or "second_party"
    signature_image: str  # Base64 encoded image

@api_router.post("/contracts/{contract_id}/upload-signature")
async def upload_signature(request: SignatureUploadRequest):
    """Upload a signature image for a contract"""
    try:
        # Validate party type
        if request.party_type not in ["first_party", "second_party"]:
            raise HTTPException(status_code=400, detail="Invalid party type. Must be 'first_party' or 'second_party'")
        
        # Validate base64 image
        if not request.signature_image:
            raise HTTPException(status_code=400, detail="Signature image is required")
        
        # Check if it's a valid base64 image
        try:
            import base64
            # Remove data URL prefix if present
            if request.signature_image.startswith('data:image'):
                request.signature_image = request.signature_image.split(',')[1]
            
            # Validate base64
            base64.b64decode(request.signature_image)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image format")
        
        # Update contract with signature
        update_field = f"{request.party_type}_signature"
        result = await db.contracts.update_one(
            {"id": request.contract_id},
            {"$set": {update_field: request.signature_image}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {"message": "Signature uploaded successfully", "party_type": request.party_type}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading signature: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading signature: {str(e)}")

@api_router.get("/contracts/{contract_id}/signatures")
async def get_contract_signatures(contract_id: str):
    """Get signatures for a contract"""
    try:
        contract = await db.contracts.find_one({"id": contract_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {
            "contract_id": contract_id,
            "first_party_signature": contract.get("first_party_signature"),
            "second_party_signature": contract.get("second_party_signature")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting signatures: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting signatures: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
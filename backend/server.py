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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI API Setup
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
groq_client = Groq(api_key=os.environ['GROQ_API_KEY'])

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
        
        # Contract templates and prompts
        contract_prompts = {
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
            
            Format the document professionally with:
            - **Bold headings** for major sections
            - Clear paragraph structure
            - [Date of Execution] placeholder for date entry
            - No asterisk (*) notations anywhere in the document
            
            End the document with a signature section:
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
            
            Make it legally sound and professionally formatted.
            """,
            "freelance_agreement": """
            Generate a comprehensive Freelance Service Agreement with:
            {requirements}
            
            FORMATTING REQUIREMENTS:
            - Remove all instances of asterisk (*) expressions 
            - Use proper bold formatting for headings and key sections using **text** format
            - Include a line for Date of Execution: [Date of Execution] before any special clauses section
            - Use proper paragraph spacing and professional formatting
            
            Include essential clauses:
            - Scope of Work
            - Payment Terms
            - Intellectual Property Rights
            - Termination Conditions
            - Liability Limitations
            - Governing Law
            
            Format the document professionally with:
            - **Bold headings** for major sections
            - Clear paragraph structure
            - [Date of Execution] placeholder for date entry
            - No asterisk (*) notations anywhere in the document
            
            End the document with a signature section:
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
            
            Ensure clarity and legal enforceability.
            """,
            "partnership_agreement": """
            Generate a Business Partnership Agreement including:
            {requirements}
            
            FORMATTING REQUIREMENTS:
            - Remove all instances of asterisk (*) expressions 
            - Use proper bold formatting for headings and key sections using **text** format
            - Include a line for Date of Execution: [Date of Execution] before any special clauses section
            - Use proper paragraph spacing and professional formatting
            
            Cover key areas:
            - Partnership Structure
            - Capital Contributions
            - Profit/Loss Distribution
            - Decision Making Process
            - Dissolution Procedures
            - Governing Law
            
            Format the document professionally with:
            - **Bold headings** for major sections
            - Clear paragraph structure
            - [Date of Execution] placeholder for date entry
            - No asterisk (*) notations anywhere in the document
            
            End the document with a signature section:
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
            
            Make it comprehensive and legally binding.
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
        
        prompt = contract_prompts.get(contract_type, contract_prompts["NDA"]).format(
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
    def process_signature_image(signature_base64: str) -> io.BytesIO:
        """Process base64 signature image and return a BytesIO object for reportlab"""
        try:
            # Remove data URL prefix if present
            if signature_base64.startswith('data:image'):
                signature_base64 = signature_base64.split(',')[1]
            
            # Decode base64 data
            signature_data = base64.b64decode(signature_base64)
            
            # Open image with PIL to validate and process
            original_image = PILImage.open(io.BytesIO(signature_data))
            
            # Convert to RGB if necessary (reportlab works better with RGB)
            if original_image.mode not in ('RGB', 'L'):
                # Create a new RGB image
                rgb_image = PILImage.new('RGB', original_image.size, (255, 255, 255))
                rgb_image.paste(original_image, mask=original_image.split()[-1] if original_image.mode == 'RGBA' else None)
                processed_image = rgb_image
                original_image.close()
            else:
                processed_image = original_image
            
            # Create a new BytesIO buffer for the processed image
            processed_buffer = io.BytesIO()
            
            # Save as PNG (reportlab handles PNG well)
            processed_image.save(processed_buffer, format='PNG')
            processed_buffer.seek(0)
            
            # Close the PIL image to free memory
            processed_image.close()
            
            return processed_buffer
                
        except Exception as e:
            logging.error(f"Error processing signature image: {e}")
            raise Exception(f"Invalid signature image: {str(e)}")

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
        
        # Look for First Party signature placeholder
        first_match = re.search(r'\[First Party Signature Placeholder\]\s*\n_+\s*\n(.+)', signature_content)
        if first_match:
            first_party_info['name'] = first_match.group(1).strip()
            first_party_info['signature'] = first_party_signature
        
        # Look for Second Party signature placeholder  
        second_match = re.search(r'\[Second Party Signature Placeholder\]\s*\n_+\s*\n(.+)', signature_content)
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
                        # Process signature image using new helper method
                        signature_buffer = LegalMateAgents.process_signature_image(first_party_info['signature'])
                        signature_image = Image(signature_buffer, width=200, height=50)
                        content.append(signature_image)
                    except Exception as e:
                        logging.warning(f"Error processing first party signature: {e}")
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
                        # Process signature image using new helper method
                        signature_buffer = LegalMateAgents.process_signature_image(second_party_info['signature'])
                        signature_image = Image(signature_buffer, width=200, height=50)
                        content.append(signature_image)
                    except Exception as e:
                        logging.warning(f"Error processing second party signature: {e}")
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
                        # Process signature image using new helper method
                        signature_buffer = LegalMateAgents.process_signature_image(first_party_info['signature'])
                        signature_image = Image(signature_buffer, width=200, height=50)
                        content.append(signature_image)
                    except Exception as e:
                        logging.warning(f"Error processing first party signature: {e}")
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
                        # Process signature image using new helper method
                        signature_buffer = LegalMateAgents.process_signature_image(second_party_info['signature'])
                        signature_image = Image(signature_buffer, width=200, height=50)
                        content.append(signature_image)
                    except Exception as e:
                        logging.warning(f"Error processing second party signature: {e}")
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
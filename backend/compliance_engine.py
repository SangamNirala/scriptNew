"""
Legal Compliance Engine - Day 1 UPL Violation Elimination System

This module implements the core compliance system to prevent Unauthorized Practice of Law (UPL) violations
by detecting and blocking legal advice patterns in generated content.
"""

import os
import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from enum import Enum
import json

# AI Integration imports
import google.generativeai as genai
from groq import Groq
import httpx

# Database imports
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Compliance enforcement levels"""
    STRICT = "strict"           # Block everything that could be legal advice
    MODERATE = "moderate"       # Block direct advice, allow informational content
    PERMISSIVE = "permissive"   # Only block explicit legal recommendations

class UPLViolationType(Enum):
    """Types of UPL violations detected"""
    DIRECT_LEGAL_ADVICE = "direct_legal_advice"
    LEGAL_RECOMMENDATION = "legal_recommendation"
    CASE_SPECIFIC_GUIDANCE = "case_specific_guidance"
    PROHIBITED_LANGUAGE = "prohibited_language"
    ATTORNEY_CLIENT_PRIVILEGE = "attorney_client_privilege"

class ComplianceResult:
    """Result of compliance checking"""
    def __init__(self):
        self.is_compliant: bool = True
        self.violations: List[Dict[str, Any]] = []
        self.confidence_score: float = 0.0
        self.sanitized_content: Optional[str] = None
        self.requires_attorney_review: bool = False
        self.blocked_phrases: List[str] = []
        self.recommendations: List[str] = []

class ComplianceEngine:
    def __init__(self, mongo_client: AsyncIOMotorClient, db_name: str):
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        
        # Load environment variables
        self.compliance_mode = os.getenv('COMPLIANCE_MODE', 'true').lower() == 'true'
        self.attorney_supervision_required = os.getenv('ATTORNEY_SUPERVISION_REQUIRED', 'true').lower() == 'true'
        self.maintenance_mode = os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'
        
        # Set compliance level
        self.compliance_level = ComplianceLevel.STRICT if self.compliance_mode else ComplianceLevel.PERMISSIVE
        
        # Initialize AI clients
        self.groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        
        self.openrouter_client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LegalMate AI Compliance"
            }
        )
        
        # Prohibited phrases that indicate legal advice
        self.prohibited_phrases = [
            # Direct advice patterns
            r'\byou should\b',
            r'\byou must\b', 
            r'\byou need to\b',
            r'\bI recommend\b',
            r'\bI suggest\b',
            r'\bI advise\b',
            r'\bmy advice is\b',
            r'\byou are required to\b',
            r'\byou have to\b',
            r'\blegally required\b',
            r'\bmandatory that you\b',
            
            # Legal conclusions
            r'\bthis is legal\b',
            r'\bthis is illegal\b',
            r'\byou have a case\b',
            r'\byou should sue\b',
            r'\byou can sue\b',
            r'\byou will win\b',
            r'\byou will lose\b',
            r'\bguaranteed to win\b',
            
            # Attorney-client privilege language
            r'\bas your attorney\b',
            r'\blegal counsel\b',
            r'\battorney-client\b',
            r'\bconfidential legal advice\b',
            
            # Specific legal actions
            r'\bfile a lawsuit\b',
            r'\bgo to court\b',
            r'\bhire a lawyer\b',
            r'\bcontact an attorney\b',
            r'\bseek legal counsel\b'
        ]
        
        # Compliance-safe alternatives
        self.safe_alternatives = {
            "you should": "typically one might consider",
            "you must": "it may be necessary to",
            "you need to": "it is common to",
            "I recommend": "it is often advisable to",
            "I suggest": "one approach might be to",
            "I advise": "it may be helpful to consider",
            "legally required": "often required by law",
            "you have to": "it may be necessary to",
            "this is legal": "this appears to comply with general legal principles",
            "this is illegal": "this may raise legal concerns",
            "you should sue": "legal action might be considered",
            "you can sue": "legal remedies may be available"
        }

    async def check_compliance(self, content: str, content_type: str = "general") -> ComplianceResult:
        """
        Main compliance checking function that detects UPL violations
        """
        result = ComplianceResult()
        
        if not self.compliance_mode:
            result.is_compliant = True
            return result
        
        if self.maintenance_mode:
            result.is_compliant = False
            result.violations.append({
                "type": "maintenance_mode",
                "message": "Legal advice generation is temporarily unavailable for compliance maintenance",
                "severity": "critical"
            })
            return result
        
        try:
            # Step 1: Pattern-based detection (fast)
            pattern_violations = await self._detect_prohibited_patterns(content)
            result.violations.extend(pattern_violations)
            result.blocked_phrases = [v["phrase"] for v in pattern_violations if "phrase" in v]
            
            # Step 2: AI-powered analysis (comprehensive)
            ai_analysis = await self._ai_content_analysis(content, content_type)
            result.violations.extend(ai_analysis["violations"])
            result.confidence_score = ai_analysis["confidence"]
            
            # Step 3: Context-specific analysis
            context_violations = await self._context_specific_analysis(content, content_type)
            result.violations.extend(context_violations)
            
            # Step 4: Determine overall compliance
            result.is_compliant = len(result.violations) == 0
            result.requires_attorney_review = (
                not result.is_compliant or 
                self.attorney_supervision_required or
                result.confidence_score < 0.8
            )
            
            # Step 5: Generate sanitized content if needed
            if not result.is_compliant:
                result.sanitized_content = await self._sanitize_content(content, result.violations)
            
            # Step 6: Generate compliance recommendations
            result.recommendations = await self._generate_recommendations(result.violations)
            
            # Log compliance check
            await self._log_compliance_check(content, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            # Fail safe - if compliance check fails, require attorney review
            result.is_compliant = False
            result.requires_attorney_review = True
            result.violations.append({
                "type": "system_error",
                "message": "Compliance checking system encountered an error. Attorney review required.",
                "severity": "critical"
            })
            return result

    async def _detect_prohibited_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect prohibited phrases using regex patterns"""
        violations = []
        content_lower = content.lower()
        
        for pattern in self.prohibited_phrases:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                violations.append({
                    "type": UPLViolationType.PROHIBITED_LANGUAGE.value,
                    "phrase": match.group(),
                    "position": match.start(),
                    "message": f"Prohibited phrase detected: '{match.group()}'",
                    "severity": "high"
                })
        
        return violations

    async def _ai_content_analysis(self, content: str, content_type: str) -> Dict[str, Any]:
        """Use AI to analyze content for legal advice patterns"""
        try:
            analysis_prompt = f"""
            Analyze the following {content_type} content for potential Unauthorized Practice of Law (UPL) violations.
            
            Content to analyze:
            {content}
            
            Look for:
            1. Direct legal advice or recommendations
            2. Specific case guidance
            3. Legal conclusions or predictions
            4. Attorney-client privilege assumptions
            5. Explicit legal action recommendations
            
            Respond with JSON in this format:
            {{
                "violations": [
                    {{
                        "type": "violation_type",
                        "message": "description of violation",
                        "severity": "low|medium|high|critical",
                        "text_excerpt": "relevant text"
                    }}
                ],
                "confidence": 0.95,
                "analysis_summary": "brief summary of findings"
            }}
            
            Be strict in compliance checking. If in doubt, flag as violation.
            """
            
            # Use Groq for fast analysis
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": analysis_prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1500
            )
            
            response_text = chat_completion.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group())
                return analysis_result
            else:
                # Fallback analysis
                return {
                    "violations": [],
                    "confidence": 0.5,
                    "analysis_summary": "AI analysis inconclusive"
                }
                
        except Exception as e:
            logger.error(f"AI content analysis failed: {e}")
            return {
                "violations": [{
                    "type": "analysis_error",
                    "message": "AI analysis failed, manual review required",
                    "severity": "medium"
                }],
                "confidence": 0.0,
                "analysis_summary": "Analysis error occurred"
            }

    async def _context_specific_analysis(self, content: str, content_type: str) -> List[Dict[str, Any]]:
        """Context-specific compliance analysis based on content type"""
        violations = []
        
        if content_type == "contract":
            # Contract-specific compliance checks
            if "as your attorney" in content.lower():
                violations.append({
                    "type": UPLViolationType.ATTORNEY_CLIENT_PRIVILEGE.value,
                    "message": "Contract contains attorney-client privilege language",
                    "severity": "critical"
                })
            
            if "legal advice" in content.lower() and "not legal advice" not in content.lower():
                violations.append({
                    "type": UPLViolationType.DIRECT_LEGAL_ADVICE.value,
                    "message": "Contract may contain direct legal advice",
                    "severity": "high"
                })
        
        elif content_type == "legal_qa":
            # Q&A specific checks
            if any(phrase in content.lower() for phrase in ["you should", "i recommend", "my advice"]):
                violations.append({
                    "type": UPLViolationType.DIRECT_LEGAL_ADVICE.value,
                    "message": "Q&A response contains direct legal advice language",
                    "severity": "high"
                })
        
        return violations

    async def _sanitize_content(self, content: str, violations: List[Dict[str, Any]]) -> str:
        """Sanitize content by replacing prohibited phrases with compliant alternatives"""
        sanitized = content
        
        # Replace prohibited phrases with safe alternatives
        for phrase, alternative in self.safe_alternatives.items():
            sanitized = re.sub(rf'\b{re.escape(phrase)}\b', alternative, sanitized, flags=re.IGNORECASE)
        
        # Add mandatory disclaimers
        disclaimer = """
        
        ⚠️ ATTORNEY SUPERVISION REQUIRED ⚠️
        
        This content requires attorney supervision and review before use. 
        This information is for educational purposes only and does not constitute legal advice.
        Consult with a qualified attorney for advice specific to your situation.
        
        Status: PENDING ATTORNEY REVIEW
        """
        
        sanitized = disclaimer + "\n\n" + sanitized + "\n\n" + disclaimer
        
        return sanitized

    async def _generate_recommendations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations based on violations"""
        recommendations = []
        
        if any(v["type"] == UPLViolationType.DIRECT_LEGAL_ADVICE.value for v in violations):
            recommendations.append("Remove direct legal advice language and replace with informational content")
            recommendations.append("Add disclaimers clarifying this is not legal advice")
        
        if any(v["type"] == UPLViolationType.PROHIBITED_LANGUAGE.value for v in violations):
            recommendations.append("Replace prohibited phrases with compliance-safe alternatives")
        
        if any(v["type"] == UPLViolationType.ATTORNEY_CLIENT_PRIVILEGE.value for v in violations):
            recommendations.append("Remove any language implying attorney-client relationship")
        
        recommendations.append("Submit content for attorney review before publication")
        recommendations.append("Ensure all legal content includes appropriate disclaimers")
        
        return recommendations

    async def _log_compliance_check(self, content: str, result: ComplianceResult):
        """Log compliance check for audit trail"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "content_hash": hash(content),
                "content_length": len(content),
                "is_compliant": result.is_compliant,
                "violation_count": len(result.violations),
                "violations": result.violations,
                "confidence_score": result.confidence_score,
                "requires_attorney_review": result.requires_attorney_review,
                "compliance_mode": self.compliance_mode,
                "compliance_level": self.compliance_level.value
            }
            
            await self.db.compliance_logs.insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log compliance check: {e}")

    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get current compliance system status"""
        try:
            # Get recent compliance statistics
            recent_checks = await self.db.compliance_logs.count_documents({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}
            })
            
            violations_today = await self.db.compliance_logs.count_documents({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)},
                "is_compliant": False
            })
            
            return {
                "compliance_mode": self.compliance_mode,
                "attorney_supervision_required": self.attorney_supervision_required,
                "maintenance_mode": self.maintenance_mode,
                "compliance_level": self.compliance_level.value,
                "system_status": "operational" if not self.maintenance_mode else "maintenance",
                "checks_today": recent_checks,
                "violations_today": violations_today,
                "compliance_rate": (recent_checks - violations_today) / recent_checks * 100 if recent_checks > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get compliance status: {e}")
            return {
                "compliance_mode": self.compliance_mode,
                "system_status": "error",
                "error": str(e)
            }

# Global compliance engine instance
compliance_engine = None

def get_compliance_engine(mongo_client: AsyncIOMotorClient, db_name: str) -> ComplianceEngine:
    """Get global compliance engine instance"""
    global compliance_engine
    if compliance_engine is None:
        compliance_engine = ComplianceEngine(mongo_client, db_name)
    return compliance_engine
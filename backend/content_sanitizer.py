"""
Legal Content Sanitization Engine

This module implements automatic content sanitization to convert direct legal advice
into compliant informational content with appropriate disclaimers.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from enum import Enum

# AI Integration imports
import google.generativeai as genai
from groq import Groq
import httpx

logger = logging.getLogger(__name__)

class SanitizationLevel(Enum):
    """Content sanitization levels"""
    MINIMAL = "minimal"         # Only add disclaimers
    MODERATE = "moderate"       # Replace direct advice + disclaimers
    COMPREHENSIVE = "comprehensive"  # Full content rewrite + disclaimers

class ContentType(Enum):
    """Types of content for sanitization"""
    CONTRACT = "contract"
    LEGAL_ADVICE = "legal_advice"
    TEMPLATE = "template"
    EMAIL = "email"
    GENERAL = "general"

class SanitizationResult:
    """Result of content sanitization"""
    def __init__(self):
        self.sanitized_content: str = ""
        self.changes_made: List[Dict[str, Any]] = []
        self.disclaimers_added: List[str] = []
        self.blocked_phrases: List[str] = []
        self.confidence_score: float = 0.0
        self.requires_review: bool = True

class ContentSanitizer:
    def __init__(self):
        # Initialize AI clients
        self.groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        
        self.openrouter_client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LegalMate AI Content Sanitizer"
            }
        )
        
        # Phrase replacement patterns for sanitization
        self.sanitization_patterns = {
            # Direct advice to informational
            r'\byou should\b': "it is generally advisable to",
            r'\byou must\b': "it is typically required to",
            r'\byou need to\b': "it is commonly necessary to",
            r'\bI recommend\b': "it is often recommended to",
            r'\bI suggest\b': "one approach might be to",
            r'\bI advise\b': "it may be beneficial to consider",
            r'\bmy advice is\b': "a common approach is",
            r'\byou are required to\b': "it is generally required to",
            r'\byou have to\b': "it is typically necessary to",
            r'\blegally required\b': "often required by applicable law",
            r'\bmandatory that you\b': "typically required to",
            
            # Legal conclusions to conditional statements
            r'\bthis is legal\b': "this may be permissible under applicable law",
            r'\bthis is illegal\b': "this may raise legal concerns",
            r'\byou have a case\b': "there may be legal remedies available",
            r'\byou should sue\b': "legal action might be considered",
            r'\byou can sue\b': "legal remedies may be available",
            r'\byou will win\b': "the outcome may be favorable",
            r'\byou will lose\b': "there may be challenges with this approach",
            r'\bguaranteed to win\b': "there may be a strong case",
            
            # Attorney relationship language
            r'\bas your attorney\b': "as a legal professional",
            r'\blegal counsel\b': "legal guidance",
            r'\battorney-client\b': "professional",
            r'\bconfidential legal advice\b': "confidential legal information",
            
            # Action-oriented to informational
            r'\bfile a lawsuit\b': "consider legal action",
            r'\bgo to court\b': "pursue litigation",
            r'\bhire a lawyer\b': "consult with legal counsel",
            r'\bcontact an attorney\b': "seek professional legal advice"
        }
        
        # Standard disclaimers by content type
        self.disclaimers = {
            ContentType.CONTRACT: """
⚠️ ATTORNEY SUPERVISION REQUIRED ⚠️

This contract template requires attorney supervision and review before use.
This document is for informational purposes only and does not constitute legal advice.
Laws vary by jurisdiction. Consult with a qualified attorney licensed in your 
jurisdiction before using this contract.

Status: PENDING ATTORNEY REVIEW
""",
            ContentType.LEGAL_ADVICE: """
⚠️ ATTORNEY SUPERVISION REQUIRED ⚠️

This information requires attorney supervision and review.
This content is for educational purposes only and does not constitute legal advice.
The information provided is general in nature and may not apply to your specific situation.
Always consult with a qualified attorney for advice tailored to your circumstances.

Status: PENDING ATTORNEY REVIEW
""",
            ContentType.TEMPLATE: """
⚠️ ATTORNEY SUPERVISION REQUIRED ⚠️

This template requires attorney supervision and customization before use.
Templates are for informational purposes only and do not constitute legal advice.
Legal requirements vary by jurisdiction and situation.
Consult with a qualified attorney before using this template.

Status: PENDING ATTORNEY REVIEW
""",
            ContentType.GENERAL: """
⚠️ ATTORNEY SUPERVISION REQUIRED ⚠️

This content requires attorney supervision and review.
This information is for educational purposes only and does not constitute legal advice.
Consult with a qualified attorney for advice specific to your situation.

Status: PENDING ATTORNEY REVIEW
"""
        }

    async def sanitize_content(self, content: str, content_type: ContentType = ContentType.GENERAL,
                             sanitization_level: SanitizationLevel = SanitizationLevel.COMPREHENSIVE) -> SanitizationResult:
        """
        Main content sanitization function
        """
        result = SanitizationResult()
        
        try:
            if sanitization_level == SanitizationLevel.MINIMAL:
                result.sanitized_content = await self._add_disclaimers(content, content_type)
                result.disclaimers_added.append(f"Added {content_type.value} disclaimer")
                
            elif sanitization_level == SanitizationLevel.MODERATE:
                # Pattern-based replacement + disclaimers
                sanitized = await self._pattern_based_sanitization(content)
                result.sanitized_content = await self._add_disclaimers(sanitized, content_type)
                result.changes_made = await self._track_changes(content, sanitized)
                result.disclaimers_added.append(f"Added {content_type.value} disclaimer")
                
            else:  # COMPREHENSIVE
                # AI-powered full content rewrite
                result = await self._ai_powered_sanitization(content, content_type)
                result.sanitized_content = await self._add_disclaimers(result.sanitized_content, content_type)
                result.disclaimers_added.append(f"Added {content_type.value} disclaimer")
            
            # Always requires review after sanitization
            result.requires_review = True
            result.confidence_score = await self._calculate_confidence_score(result.sanitized_content)
            
            return result
            
        except Exception as e:
            logger.error(f"Content sanitization failed: {e}")
            # Fallback - just add disclaimers
            result.sanitized_content = await self._add_disclaimers(content, content_type)
            result.requires_review = True
            result.confidence_score = 0.0
            return result

    async def _pattern_based_sanitization(self, content: str) -> str:
        """Apply pattern-based sanitization replacements"""
        sanitized = content
        
        for pattern, replacement in self.sanitization_patterns.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized

    async def _ai_powered_sanitization(self, content: str, content_type: ContentType) -> SanitizationResult:
        """Use AI to comprehensively sanitize content"""
        result = SanitizationResult()
        
        try:
            sanitization_prompt = f"""
            Rewrite the following {content_type.value} content to be legally compliant and remove all direct legal advice.
            
            Requirements:
            1. Remove all direct legal advice language (you should, I recommend, etc.)
            2. Convert legal conclusions to conditional/informational statements
            3. Remove any language implying attorney-client relationship
            4. Replace imperative statements with informational content
            5. Add qualifying language (may, might, could, generally, typically)
            6. Maintain the core informational value
            7. Keep the content useful but compliant
            
            Original content:
            {content}
            
            Return the sanitized content only, without explanations.
            """
            
            # Use Gemini for content rewriting
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(sanitization_prompt)
            
            sanitized_content = response.text.strip()
            
            # Track changes made
            result.changes_made = await self._track_changes(content, sanitized_content)
            result.sanitized_content = sanitized_content
            result.confidence_score = 0.85  # AI-powered sanitization gets higher confidence
            
            return result
            
        except Exception as e:
            logger.error(f"AI-powered sanitization failed: {e}")
            # Fallback to pattern-based
            result.sanitized_content = await self._pattern_based_sanitization(content)
            result.confidence_score = 0.6
            return result

    async def _add_disclaimers(self, content: str, content_type: ContentType) -> str:
        """Add appropriate disclaimers to content"""
        disclaimer = self.disclaimers.get(content_type, self.disclaimers[ContentType.GENERAL])
        
        # Add disclaimer at the beginning and end
        disclaimered_content = f"{disclaimer}\n\n{content}\n\n{disclaimer}"
        
        return disclaimered_content

    async def _track_changes(self, original: str, sanitized: str) -> List[Dict[str, Any]]:
        """Track what changes were made during sanitization"""
        changes = []
        
        # Simple change tracking - could be enhanced with diff algorithms
        for pattern, replacement in self.sanitization_patterns.items():
            matches = re.finditer(pattern, original, re.IGNORECASE)
            for match in matches:
                changes.append({
                    "type": "phrase_replacement",
                    "original": match.group(),
                    "replacement": replacement,
                    "position": match.start(),
                    "reason": "Legal advice language sanitization"
                })
        
        return changes

    async def _calculate_confidence_score(self, content: str) -> float:
        """Calculate confidence score for sanitized content"""
        try:
            # Check for remaining prohibited patterns
            prohibited_count = 0
            for pattern in self.sanitization_patterns.keys():
                if re.search(pattern, content, re.IGNORECASE):
                    prohibited_count += 1
            
            # Base confidence starts high for sanitized content
            base_confidence = 0.9
            
            # Reduce confidence for each remaining prohibited phrase
            confidence = base_confidence - (prohibited_count * 0.1)
            
            # Check for presence of disclaimers
            if "ATTORNEY SUPERVISION REQUIRED" in content:
                confidence += 0.05
            
            if "does not constitute legal advice" in content:
                confidence += 0.05
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.5

    async def sanitize_contract_template(self, template: str, contract_type: str) -> SanitizationResult:
        """Specialized contract template sanitization"""
        try:
            # Enhanced sanitization for contract templates
            sanitization_prompt = f"""
            Sanitize this {contract_type} contract template to ensure compliance with legal practice requirements.
            
            Requirements for contract template sanitization:
            1. Remove any language that provides specific legal advice
            2. Add placeholder fields where specific legal guidance would be needed
            3. Include attorney review requirements in clauses
            4. Remove any guarantees about legal effectiveness
            5. Add appropriate legal disclaimers
            6. Maintain structural integrity of the contract
            7. Replace definitive statements with conditional language
            
            Template to sanitize:
            {template}
            
            Return only the sanitized template.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(sanitization_prompt)
            
            sanitized_template = response.text.strip()
            
            # Add contract-specific disclaimers
            result = SanitizationResult()
            result.sanitized_content = await self._add_disclaimers(sanitized_template, ContentType.CONTRACT)
            result.changes_made = await self._track_changes(template, sanitized_template)
            result.confidence_score = 0.8
            result.requires_review = True
            
            # Add contract-specific attorney supervision clause
            supervision_clause = """

ATTORNEY SUPERVISION CLAUSE:
This contract template has been generated by an AI system and requires review and approval by a licensed attorney before execution. The parties acknowledge that:
(a) This template may require customization for specific circumstances
(b) Legal requirements vary by jurisdiction  
(c) An attorney licensed in the relevant jurisdiction should review this agreement
(d) This template does not constitute legal advice

"""
            
            result.sanitized_content = result.sanitized_content.replace(
                "[Date of Execution]", 
                "[Date of Execution - Attorney Review Required]" + supervision_clause
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Contract template sanitization failed: {e}")
            # Fallback sanitization
            return await self.sanitize_content(template, ContentType.CONTRACT, SanitizationLevel.MODERATE)

    async def validate_sanitized_content(self, content: str) -> Dict[str, Any]:
        """Validate that sanitized content is compliant"""
        try:
            validation_result = {
                "is_compliant": True,
                "issues_found": [],
                "confidence": 0.0,
                "recommendations": []
            }
            
            # Check for remaining prohibited phrases
            issues = []
            for pattern in self.sanitization_patterns.keys():
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"Prohibited phrase pattern found: {pattern}")
            
            # Check for required disclaimers
            if "ATTORNEY SUPERVISION REQUIRED" not in content:
                issues.append("Missing attorney supervision disclaimer")
            
            if "does not constitute legal advice" not in content:
                issues.append("Missing legal advice disclaimer")
            
            validation_result["issues_found"] = issues
            validation_result["is_compliant"] = len(issues) == 0
            validation_result["confidence"] = await self._calculate_confidence_score(content)
            
            if issues:
                validation_result["recommendations"] = [
                    "Re-sanitize content with higher sanitization level",
                    "Manual review required to remove remaining prohibited language",
                    "Add missing compliance disclaimers"
                ]
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return {
                "is_compliant": False,
                "issues_found": ["Validation system error"],
                "confidence": 0.0,
                "recommendations": ["Manual attorney review required"]
            }

# Global content sanitizer instance
content_sanitizer = None

def get_content_sanitizer() -> ContentSanitizer:
    """Get global content sanitizer instance"""
    global content_sanitizer
    if content_sanitizer is None:
        content_sanitizer = ContentSanitizer()
    return content_sanitizer
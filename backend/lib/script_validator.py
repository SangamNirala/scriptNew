"""
Phase 3: Script Validator
Comprehensive script structure validation and quality assurance
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import textstat
from collections import Counter
import math

logger = logging.getLogger(__name__)

class ScriptValidator:
    """Comprehensive script validation system for structure and quality assurance"""
    
    def __init__(self):
        # Define validation criteria weights
        self.validation_weights = {
            "hook_quality": 0.30,
            "pacing_optimization": 0.25,
            "retention_hooks": 0.25,
            "cta_placement": 0.20
        }
        
        # Platform-specific validation rules
        self.platform_rules = {
            "youtube": {
                "min_hook_duration": 10,  # seconds
                "max_hook_duration": 20,
                "optimal_segment_length": 30,  # seconds
                "required_retention_elements": 3,
                "cta_positions": ["end", "middle"],
                "max_silent_duration": 45  # seconds without engagement
            },
            "tiktok": {
                "min_hook_duration": 2,
                "max_hook_duration": 5,
                "optimal_segment_length": 10,
                "required_retention_elements": 2,
                "cta_positions": ["beginning", "end"],
                "max_silent_duration": 15
            },
            "instagram": {
                "min_hook_duration": 3,
                "max_hook_duration": 8,
                "optimal_segment_length": 15,
                "required_retention_elements": 2,
                "cta_positions": ["end"],
                "max_silent_duration": 25
            },
            "linkedin": {
                "min_hook_duration": 8,
                "max_hook_duration": 15,
                "optimal_segment_length": 45,
                "required_retention_elements": 2,
                "cta_positions": ["end"],
                "max_silent_duration": 60
            }
        }
        
        # Validation rule definitions
        self.validation_rules = {
            "hook_requirements": {
                "min_word_count": 10,
                "required_elements": ["curiosity", "value_proposition", "emotional_trigger"],
                "forbidden_elements": ["generic_greeting", "long_introduction"]
            },
            "pacing_requirements": {
                "max_sentence_length": 20,
                "min_sentence_variety": 0.3,
                "required_transitions": 2,
                "optimal_paragraph_length": 50
            },
            "retention_requirements": {
                "min_questions": 1,
                "min_engagement_elements": 3,
                "max_info_density": 0.8,
                "required_pattern_breaks": 2
            },
            "cta_requirements": {
                "min_cta_count": 1,
                "max_cta_count": 3,
                "required_clarity": 0.8,
                "optimal_placement_score": 0.7
            }
        }
    
    def validate_script_structure(self, script: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive script structure validation
        
        Args:
            script: The script content to validate
            requirements: Platform and content requirements
            
        Returns:
            Detailed validation results with scores and recommendations
        """
        if not script or not script.strip():
            return self._get_empty_script_validation()
        
        try:
            platform = requirements.get('platform', 'youtube').lower()
            duration = requirements.get('duration', 'medium')
            content_type = requirements.get('content_type', 'general')
            
            # Get platform-specific rules
            platform_rules = self.platform_rules.get(platform, self.platform_rules['youtube'])
            
            # Perform individual validation checks
            hook_validation = self.validate_hook_section(script, platform_rules, requirements)
            pacing_validation = self.check_pacing_intervals(script, platform_rules, requirements)
            retention_validation = self.validate_retention_elements(script, platform_rules, requirements)
            cta_validation = self.validate_call_to_action(script, platform_rules, requirements)
            
            # Calculate overall validation score
            overall_score = self._calculate_validation_score({
                "hook_quality": hook_validation["score"],
                "pacing_optimization": pacing_validation["score"],
                "retention_hooks": retention_validation["score"],
                "cta_placement": cta_validation["score"]
            })
            
            # Determine validation status
            validation_status = self._determine_validation_status(overall_score)
            
            # Generate comprehensive recommendations
            recommendations = self._generate_validation_recommendations(
                hook_validation, pacing_validation, retention_validation, cta_validation, platform
            )
            
            # Identify critical issues
            critical_issues = self._identify_critical_issues(
                hook_validation, pacing_validation, retention_validation, cta_validation
            )
            
            return {
                "validation_status": validation_status,
                "overall_score": round(overall_score, 2),
                "validation_grade": self._get_validation_grade(overall_score),
                "detailed_validation": {
                    "hook_quality": hook_validation,
                    "pacing_optimization": pacing_validation,
                    "retention_hooks": retention_validation,
                    "cta_placement": cta_validation
                },
                "critical_issues": critical_issues,
                "recommendations": recommendations,
                "compliance_summary": self._generate_compliance_summary(
                    hook_validation, pacing_validation, retention_validation, cta_validation
                ),
                "validation_metadata": {
                    "validated_at": datetime.utcnow().isoformat(),
                    "platform": platform,
                    "duration": duration,
                    "content_type": content_type,
                    "script_word_count": len(script.split()),
                    "validation_version": "3.0"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in script validation: {str(e)}")
            return self._get_error_validation(str(e))
    
    def validate_hook_section(self, script: str, platform_rules: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the effectiveness and structure of the script hook"""
        try:
            words = script.split()
            if not words:
                return {"score": 0.0, "issues": ["No content to validate"]}
            
            # Calculate hook section (first portion based on platform)
            hook_duration = platform_rules["min_hook_duration"]
            hook_word_count = min(len(words), hook_duration * 2)  # ~2 words per second
            hook_text = ' '.join(words[:hook_word_count])
            
            validation_results = {
                "score": 0.0,
                "issues": [],
                "strengths": [],
                "hook_elements": {},
                "recommendations": []
            }
            
            # Check hook length appropriateness
            hook_length_score = self._validate_hook_length(hook_text, platform_rules)
            validation_results["hook_elements"]["length_score"] = hook_length_score
            
            # Check for curiosity gap
            curiosity_score = self._validate_curiosity_gap(hook_text)
            validation_results["hook_elements"]["curiosity_score"] = curiosity_score
            
            # Check for value proposition
            value_score = self._validate_value_proposition(hook_text)
            validation_results["hook_elements"]["value_score"] = value_score
            
            # Check for emotional triggers
            emotional_score = self._validate_emotional_triggers(hook_text)
            validation_results["hook_elements"]["emotional_score"] = emotional_score
            
            # Check for immediate engagement
            engagement_score = self._validate_immediate_engagement(hook_text)
            validation_results["hook_elements"]["engagement_score"] = engagement_score
            
            # Check for forbidden elements
            forbidden_penalty = self._check_forbidden_hook_elements(hook_text)
            
            # Calculate overall hook score
            hook_score = (
                hook_length_score * 0.15 +
                curiosity_score * 0.25 +
                value_score * 0.20 +
                emotional_score * 0.25 +
                engagement_score * 0.15
            ) - forbidden_penalty
            
            validation_results["score"] = max(0.0, min(10.0, hook_score))
            
            # Generate hook-specific issues and strengths
            if curiosity_score < 5:
                validation_results["issues"].append("Hook lacks curiosity gap or intrigue")
            else:
                validation_results["strengths"].append("Strong curiosity gap in hook")
                
            if value_score < 5:
                validation_results["issues"].append("Value proposition not clear in opening")
            else:
                validation_results["strengths"].append("Clear value proposition established")
                
            if emotional_score < 4:
                validation_results["issues"].append("Hook needs stronger emotional triggers")
            else:
                validation_results["strengths"].append("Good emotional engagement in hook")
            
            # Generate hook recommendations
            validation_results["recommendations"] = self._generate_hook_recommendations(
                curiosity_score, value_score, emotional_score, engagement_score
            )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating hook section: {str(e)}")
            return {"score": 0.0, "error": str(e)}
    
    def check_pacing_intervals(self, script: str, platform_rules: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Check pacing optimization and rhythm throughout the script"""
        try:
            validation_results = {
                "score": 0.0,
                "issues": [],
                "strengths": [],
                "pacing_analysis": {},
                "recommendations": []
            }
            
            # Analyze sentence structure and variety
            sentence_analysis = self._analyze_sentence_pacing(script)
            validation_results["pacing_analysis"]["sentence_analysis"] = sentence_analysis
            
            # Check paragraph structure
            paragraph_analysis = self._analyze_paragraph_pacing(script)
            validation_results["pacing_analysis"]["paragraph_analysis"] = paragraph_analysis
            
            # Check transition quality
            transition_analysis = self._analyze_transitions(script)
            validation_results["pacing_analysis"]["transition_analysis"] = transition_analysis
            
            # Check rhythm and flow
            rhythm_analysis = self._analyze_rhythm_flow(script)
            validation_results["pacing_analysis"]["rhythm_analysis"] = rhythm_analysis
            
            # Check for pacing dead zones
            dead_zones = self._identify_pacing_dead_zones(script, platform_rules)
            validation_results["pacing_analysis"]["dead_zones"] = dead_zones
            
            # Calculate overall pacing score
            pacing_score = (
                sentence_analysis["score"] * 0.25 +
                paragraph_analysis["score"] * 0.20 +
                transition_analysis["score"] * 0.25 +
                rhythm_analysis["score"] * 0.20 +
                (10.0 - min(10.0, len(dead_zones) * 2)) * 0.10
            )
            
            validation_results["score"] = max(0.0, min(10.0, pacing_score))
            
            # Generate pacing issues and strengths
            if sentence_analysis["score"] < 6:
                validation_results["issues"].append("Sentence length variety needs improvement")
            else:
                validation_results["strengths"].append("Good sentence length variation")
                
            if transition_analysis["score"] < 5:
                validation_results["issues"].append("More transition words needed for flow")
            else:
                validation_results["strengths"].append("Strong transitions between ideas")
                
            if len(dead_zones) > 2:
                validation_results["issues"].append("Multiple pacing dead zones detected")
            elif len(dead_zones) == 0:
                validation_results["strengths"].append("Excellent pacing throughout")
            
            # Generate pacing recommendations
            validation_results["recommendations"] = self._generate_pacing_recommendations(
                sentence_analysis, paragraph_analysis, transition_analysis, dead_zones
            )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error checking pacing intervals: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    def validate_retention_elements(self, script: str, platform_rules: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate retention hooks and engagement elements throughout the script"""
        try:
            validation_results = {
                "score": 0.0,
                "issues": [],
                "strengths": [],
                "retention_analysis": {},
                "recommendations": []
            }
            
            # Check for engagement questions
            question_analysis = self._analyze_engagement_questions(script)
            validation_results["retention_analysis"]["questions"] = question_analysis
            
            # Check for pattern interrupts
            pattern_analysis = self._analyze_pattern_interrupts(script)
            validation_results["retention_analysis"]["pattern_interrupts"] = pattern_analysis
            
            # Check for curiosity loops
            curiosity_analysis = self._analyze_curiosity_loops(script)
            validation_results["retention_analysis"]["curiosity_loops"] = curiosity_analysis
            
            # Check for emotional peaks
            emotional_analysis = self._analyze_emotional_peaks(script)
            validation_results["retention_analysis"]["emotional_peaks"] = emotional_analysis
            
            # Check retention element distribution
            distribution_analysis = self._analyze_retention_distribution(script, platform_rules)
            validation_results["retention_analysis"]["distribution"] = distribution_analysis
            
            # Calculate overall retention score
            retention_score = (
                question_analysis["score"] * 0.25 +
                pattern_analysis["score"] * 0.20 +
                curiosity_analysis["score"] * 0.25 +
                emotional_analysis["score"] * 0.15 +
                distribution_analysis["score"] * 0.15
            )
            
            validation_results["score"] = max(0.0, min(10.0, retention_score))
            
            # Generate retention issues and strengths
            if question_analysis["count"] < platform_rules["required_retention_elements"]:
                validation_results["issues"].append("Insufficient engagement questions for platform")
            else:
                validation_results["strengths"].append("Good use of engagement questions")
                
            if pattern_analysis["score"] < 5:
                validation_results["issues"].append("More pattern interrupts needed to maintain attention")
            else:
                validation_results["strengths"].append("Effective pattern interruption techniques")
                
            if distribution_analysis["score"] < 6:
                validation_results["issues"].append("Uneven distribution of retention elements")
            else:
                validation_results["strengths"].append("Well-distributed retention elements")
            
            # Generate retention recommendations
            validation_results["recommendations"] = self._generate_retention_recommendations(
                question_analysis, pattern_analysis, curiosity_analysis, distribution_analysis
            )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating retention elements: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    def validate_call_to_action(self, script: str, platform_rules: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate call-to-action placement and effectiveness"""
        try:
            validation_results = {
                "score": 0.0,
                "issues": [],
                "strengths": [],
                "cta_analysis": {},
                "recommendations": []
            }
            
            # Find and analyze all CTAs
            cta_elements = self._find_all_ctas(script)
            validation_results["cta_analysis"]["elements"] = cta_elements
            
            # Check CTA placement
            placement_analysis = self._analyze_cta_placement(script, cta_elements, platform_rules)
            validation_results["cta_analysis"]["placement"] = placement_analysis
            
            # Check CTA clarity and strength
            clarity_analysis = self._analyze_cta_clarity(cta_elements)
            validation_results["cta_analysis"]["clarity"] = clarity_analysis
            
            # Check CTA frequency and spacing
            frequency_analysis = self._analyze_cta_frequency(script, cta_elements)
            validation_results["cta_analysis"]["frequency"] = frequency_analysis
            
            # Check platform-specific CTA requirements
            platform_compliance = self._check_platform_cta_compliance(cta_elements, platform_rules)
            validation_results["cta_analysis"]["platform_compliance"] = platform_compliance
            
            # Calculate overall CTA score
            cta_score = (
                placement_analysis["score"] * 0.30 +
                clarity_analysis["score"] * 0.30 +
                frequency_analysis["score"] * 0.25 +
                platform_compliance["score"] * 0.15
            )
            
            validation_results["score"] = max(0.0, min(10.0, cta_score))
            
            # Generate CTA issues and strengths
            if len(cta_elements) == 0:
                validation_results["issues"].append("No call-to-action elements found")
            elif len(cta_elements) > 4:
                validation_results["issues"].append("Too many CTAs may overwhelm audience")
            else:
                validation_results["strengths"].append("Appropriate number of CTAs")
                
            if placement_analysis["score"] < 6:
                validation_results["issues"].append("CTA placement not optimal for platform")
            else:
                validation_results["strengths"].append("Well-placed CTAs")
                
            if clarity_analysis["score"] < 6:
                validation_results["issues"].append("CTAs need clearer, more direct language")
            else:
                validation_results["strengths"].append("Clear and actionable CTAs")
            
            # Generate CTA recommendations
            validation_results["recommendations"] = self._generate_cta_recommendations(
                cta_elements, placement_analysis, clarity_analysis, frequency_analysis, platform_rules
            )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating call to action: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    # Hook validation helper methods
    
    def _validate_hook_length(self, hook_text: str, platform_rules: Dict[str, Any]) -> float:
        """Validate hook length appropriateness"""
        word_count = len(hook_text.split())
        optimal_min = platform_rules["min_hook_duration"] * 2  # ~2 words per second
        optimal_max = platform_rules["max_hook_duration"] * 2
        
        if optimal_min <= word_count <= optimal_max:
            return 10.0
        elif word_count < optimal_min:
            return max(0.0, 10.0 - (optimal_min - word_count) * 0.5)
        else:
            return max(0.0, 10.0 - (word_count - optimal_max) * 0.3)
    
    def _validate_curiosity_gap(self, hook_text: str) -> float:
        """Validate presence of curiosity gap elements"""
        curiosity_indicators = [
            'secret', 'hidden', 'revealed', 'truth', 'mystery', 'discovered',
            'what if', 'imagine', 'did you know', 'here\'s why', 'reason',
            'but first', 'before', 'until', 'however', 'surprise'
        ]
        
        hook_lower = hook_text.lower()
        curiosity_score = 0.0
        
        for indicator in curiosity_indicators:
            if indicator in hook_lower:
                curiosity_score += 2.0
        
        # Questions create curiosity
        if '?' in hook_text:
            curiosity_score += 3.0
        
        # Numbers and statistics create curiosity
        if re.search(r'\d+', hook_text):
            curiosity_score += 1.5
        
        return min(10.0, curiosity_score)
    
    def _validate_value_proposition(self, hook_text: str) -> float:
        """Validate clear value proposition in hook"""
        value_indicators = [
            'learn', 'discover', 'find out', 'show you', 'teach', 'reveal',
            'help', 'save', 'make', 'get', 'achieve', 'improve', 'increase',
            'tips', 'tricks', 'secrets', 'guide', 'tutorial', 'method'
        ]
        
        hook_lower = hook_text.lower()
        value_score = 0.0
        
        for indicator in value_indicators:
            if indicator in hook_lower:
                value_score += 1.5
        
        # Direct benefit statements
        benefit_patterns = [r'you will', r'you can', r'you\'ll', r'this will']
        for pattern in benefit_patterns:
            if re.search(pattern, hook_lower):
                value_score += 2.0
        
        return min(10.0, value_score)
    
    def _validate_emotional_triggers(self, hook_text: str) -> float:
        """Validate emotional trigger elements"""
        emotional_words = {
            'excitement': ['amazing', 'incredible', 'fantastic', 'extraordinary'],
            'urgency': ['now', 'today', 'immediately', 'urgent', 'quick'],
            'fear': ['mistake', 'wrong', 'avoid', 'danger', 'warning'],
            'curiosity': ['secret', 'hidden', 'mysterious', 'unknown'],
            'social': ['everyone', 'nobody', 'most people', 'experts']
        }
        
        hook_lower = hook_text.lower()
        emotional_score = 0.0
        
        for category, words in emotional_words.items():
            for word in words:
                if word in hook_lower:
                    emotional_score += 1.2
        
        # Exclamation points add emotional intensity
        emotional_score += hook_text.count('!') * 0.8
        
        return min(10.0, emotional_score)
    
    def _validate_immediate_engagement(self, hook_text: str) -> float:
        """Validate immediate audience engagement elements"""
        engagement_elements = [
            'you', 'your', 'imagine', 'picture', 'think', 'remember',
            'have you', 'do you', 'are you', 'can you', 'would you'
        ]
        
        hook_lower = hook_text.lower()
        engagement_score = 0.0
        
        for element in engagement_elements:
            if element in hook_lower:
                engagement_score += 1.0
        
        # Direct questions increase engagement
        engagement_score += hook_text.count('?') * 2.0
        
        return min(10.0, engagement_score)
    
    def _check_forbidden_hook_elements(self, hook_text: str) -> float:
        """Check for elements that weaken hooks"""
        forbidden_elements = [
            'hello', 'hi there', 'welcome', 'my name is', 'today i',
            'in this video', 'i want to', 'i will', 'let me',
            'before we start', 'first of all'
        ]
        
        hook_lower = hook_text.lower()
        penalty = 0.0
        
        for element in forbidden_elements:
            if element in hook_lower:
                penalty += 2.0
        
        return penalty
    
    # Pacing validation helper methods
    
    def _analyze_sentence_pacing(self, script: str) -> Dict[str, Any]:
        """Analyze sentence structure and pacing"""
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        if not sentences:
            return {"score": 0.0, "variety": 0.0}
        
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Calculate variety (standard deviation)
        variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        variety = math.sqrt(variance) / avg_length if avg_length > 0 else 0
        
        # Score based on optimal length (8-15 words) and good variety
        length_score = 10.0 - abs(avg_length - 11.5) * 0.5
        variety_score = min(10.0, variety * 20)  # Higher variety = better pacing
        
        overall_score = (length_score * 0.6 + variety_score * 0.4)
        
        return {
            "score": max(0.0, min(10.0, overall_score)),
            "avg_length": round(avg_length, 2),
            "variety": round(variety, 2),
            "sentence_count": len(sentences)
        }
    
    def _analyze_paragraph_pacing(self, script: str) -> Dict[str, Any]:
        """Analyze paragraph structure and flow"""
        paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [script]  # Single paragraph
        
        paragraph_lengths = [len(paragraph.split()) for paragraph in paragraphs]
        if not paragraph_lengths:
            return {"score": 5.0}
        
        avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
        
        # Optimal paragraph length: 30-70 words
        if 30 <= avg_length <= 70:
            length_score = 10.0
        else:
            length_score = max(0.0, 10.0 - abs(avg_length - 50) * 0.2)
        
        return {
            "score": length_score,
            "avg_length": round(avg_length, 2),
            "paragraph_count": len(paragraphs)
        }
    
    def _analyze_transitions(self, script: str) -> Dict[str, Any]:
        """Analyze transition words and flow"""
        transition_words = [
            'however', 'but', 'meanwhile', 'therefore', 'consequently',
            'furthermore', 'moreover', 'additionally', 'next', 'then',
            'finally', 'first', 'second', 'also', 'because', 'since'
        ]
        
        script_lower = script.lower()
        transition_count = sum(1 for word in transition_words if word in script_lower)
        
        word_count = len(script.split())
        transition_ratio = transition_count / max(1, word_count / 100)  # Per 100 words
        
        # Optimal: 2-5 transitions per 100 words
        if 2 <= transition_ratio <= 5:
            score = 10.0
        elif 1 <= transition_ratio <= 6:
            score = 8.0
        else:
            score = max(0.0, 8.0 - abs(transition_ratio - 3.5) * 1.5)
        
        return {
            "score": score,
            "count": transition_count,
            "ratio": round(transition_ratio, 2)
        }
    
    def _analyze_rhythm_flow(self, script: str) -> Dict[str, Any]:
        """Analyze overall rhythm and flow"""
        # Check for rhythm markers
        rhythm_elements = ['pause', 'wait', 'listen', 'stop', 'hold on']
        punctuation_rhythm = script.count(',') + script.count(';') + script.count(':')
        
        script_lower = script.lower()
        rhythm_markers = sum(1 for element in rhythm_elements if element in script_lower)
        
        word_count = len(script.split())
        rhythm_score = min(10.0, (rhythm_markers + punctuation_rhythm * 0.5) / max(1, word_count / 50))
        
        return {
            "score": rhythm_score * 2,  # Amplify for better scoring
            "rhythm_markers": rhythm_markers,
            "punctuation_rhythm": punctuation_rhythm
        }
    
    def _identify_pacing_dead_zones(self, script: str, platform_rules: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify sections with poor pacing"""
        words = script.split()
        dead_zones = []
        
        max_silent_words = platform_rules["max_silent_duration"] * 2  # ~2 words per second
        
        # Check for long segments without engagement elements
        engagement_indicators = ['?', '!', 'you', 'your', 'imagine', 'think']
        
        current_zone_start = 0
        last_engagement = 0
        
        for i, word in enumerate(words):
            if any(indicator in word.lower() or indicator in ' '.join(words[max(0, i-1):i+2]).lower() 
                   for indicator in engagement_indicators):
                if i - last_engagement > max_silent_words:
                    dead_zones.append({
                        "start_word": last_engagement,
                        "end_word": i,
                        "issue": f"No engagement for {i - last_engagement} words"
                    })
                last_engagement = i
        
        return dead_zones
    
    # Retention validation helper methods
    
    def _analyze_engagement_questions(self, script: str) -> Dict[str, Any]:
        """Analyze engagement questions throughout script"""
        questions = script.count('?')
        
        # Find question types
        rhetorical_patterns = [r'have you', r'do you', r'are you', r'can you', r'would you', r'what if']
        rhetorical_count = sum(len(re.findall(pattern, script, re.IGNORECASE)) for pattern in rhetorical_patterns)
        
        word_count = len(script.split())
        question_ratio = questions / max(1, word_count / 100)  # Per 100 words
        
        # Score based on appropriate question frequency
        if 1 <= question_ratio <= 4:
            score = 10.0
        elif 0.5 <= question_ratio <= 5:
            score = 8.0
        else:
            score = max(0.0, 8.0 - abs(question_ratio - 2.5) * 2)
        
        return {
            "score": score,
            "count": questions,
            "rhetorical_count": rhetorical_count,
            "ratio": round(question_ratio, 2)
        }
    
    def _analyze_pattern_interrupts(self, script: str) -> Dict[str, Any]:
        """Analyze pattern interrupt techniques"""
        interrupt_patterns = [
            'but', 'however', 'wait', 'stop', 'actually', 'surprisingly',
            'suddenly', 'plot twist', 'here\'s the thing', 'but here\'s',
            'now', 'listen', 'pay attention'
        ]
        
        script_lower = script.lower()
        interrupt_count = sum(1 for pattern in interrupt_patterns if pattern in script_lower)
        
        word_count = len(script.split())
        interrupt_ratio = interrupt_count / max(1, word_count / 100)
        
        # Optimal: 1-3 interrupts per 100 words
        if 1 <= interrupt_ratio <= 3:
            score = 10.0
        elif 0.5 <= interrupt_ratio <= 4:
            score = 8.0
        else:
            score = max(0.0, 8.0 - abs(interrupt_ratio - 2) * 2)
        
        return {
            "score": score,
            "count": interrupt_count,
            "ratio": round(interrupt_ratio, 2)
        }
    
    def _analyze_curiosity_loops(self, script: str) -> Dict[str, Any]:
        """Analyze curiosity loop creation and resolution"""
        loop_openers = ['secret', 'mystery', 'reveal', 'surprising', 'shocking', 'but first', 'later']
        loop_closers = ['because', 'here\'s why', 'the answer', 'turns out', 'revealed']
        
        script_lower = script.lower()
        openers = sum(1 for opener in loop_openers if opener in script_lower)
        closers = sum(1 for closer in loop_closers if closer in script_lower)
        
        # Good loops have both openers and closers
        if openers > 0 and closers > 0:
            balance_score = min(10.0, min(openers, closers) * 3)
        else:
            balance_score = max(openers, closers) * 2
        
        return {
            "score": balance_score,
            "openers": openers,
            "closers": closers
        }
    
    def _analyze_emotional_peaks(self, script: str) -> Dict[str, Any]:
        """Analyze emotional peak distribution"""
        emotional_words = [
            'amazing', 'incredible', 'shocking', 'fantastic', 'terrible',
            'devastating', 'thrilling', 'exciting', 'surprising', 'unbelievable'
        ]
        
        script_lower = script.lower()
        emotional_count = sum(1 for word in emotional_words if word in script_lower)
        
        # Add exclamation points as emotional indicators
        emotional_count += script.count('!')
        
        word_count = len(script.split())
        emotional_ratio = emotional_count / max(1, word_count / 100)
        
        # Optimal: 2-6 emotional peaks per 100 words
        if 2 <= emotional_ratio <= 6:
            score = 10.0
        elif 1 <= emotional_ratio <= 8:
            score = 8.0
        else:
            score = max(0.0, 8.0 - abs(emotional_ratio - 4) * 1.5)
        
        return {
            "score": score,
            "count": emotional_count,
            "ratio": round(emotional_ratio, 2)
        }
    
    def _analyze_retention_distribution(self, script: str, platform_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze distribution of retention elements throughout script"""
        words = script.split()
        if not words:
            return {"score": 0.0}
        
        segment_size = len(words) // 4  # Divide into 4 segments
        if segment_size == 0:
            return {"score": 5.0}
        
        segments = [
            ' '.join(words[i:i+segment_size]) 
            for i in range(0, len(words), segment_size)
        ]
        
        retention_elements = ['?', '!', 'you', 'your', 'but', 'however', 'secret']
        segment_scores = []
        
        for segment in segments:
            segment_lower = segment.lower()
            element_count = sum(1 for element in retention_elements if element in segment_lower)
            segment_scores.append(element_count)
        
        # Good distribution has elements in most segments
        segments_with_elements = sum(1 for score in segment_scores if score > 0)
        distribution_score = (segments_with_elements / len(segments)) * 10
        
        return {
            "score": distribution_score,
            "segment_scores": segment_scores,
            "segments_with_elements": segments_with_elements
        }
    
    # CTA validation helper methods
    
    def _find_all_ctas(self, script: str) -> List[Dict[str, Any]]:
        """Find all call-to-action elements in script"""
        cta_patterns = {
            'subscribe': r'\b(subscribe|sub)\b',
            'like': r'\b(like|thumbs up)\b',
            'comment': r'\b(comment|let me know|tell me)\b',
            'share': r'\b(share|spread|tell others)\b',
            'follow': r'\b(follow|connect)\b',
            'click': r'\b(click|tap|press)\b',
            'visit': r'\b(visit|check out|go to)\b',
            'download': r'\b(download|get|grab)\b'
        }
        
        ctas = []
        script_lower = script.lower()
        
        for cta_type, pattern in cta_patterns.items():
            matches = list(re.finditer(pattern, script_lower))
            for match in matches:
                ctas.append({
                    "type": cta_type,
                    "text": match.group(),
                    "position": match.start(),
                    "relative_position": match.start() / len(script)
                })
        
        return ctas
    
    def _analyze_cta_placement(self, script: str, cta_elements: List[Dict[str, Any]], platform_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CTA placement effectiveness"""
        if not cta_elements:
            return {"score": 0.0, "issues": ["No CTAs found"]}
        
        optimal_positions = set(platform_rules["cta_positions"])
        placement_score = 0.0
        placement_analysis = {"beginning": 0, "middle": 0, "end": 0}
        
        for cta in cta_elements:
            rel_pos = cta["relative_position"]
            if rel_pos < 0.25:
                placement_analysis["beginning"] += 1
                if "beginning" in optimal_positions:
                    placement_score += 3
            elif rel_pos > 0.75:
                placement_analysis["end"] += 1
                if "end" in optimal_positions:
                    placement_score += 3
            else:
                placement_analysis["middle"] += 1
                if "middle" in optimal_positions:
                    placement_score += 2
        
        final_score = min(10.0, placement_score)
        
        return {
            "score": final_score,
            "placement_distribution": placement_analysis,
            "optimal_positions": list(optimal_positions)
        }
    
    def _analyze_cta_clarity(self, cta_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze clarity and strength of CTAs"""
        if not cta_elements:
            return {"score": 0.0}
        
        strong_ctas = ['subscribe', 'click', 'download', 'visit']
        medium_ctas = ['like', 'share', 'follow']
        weak_ctas = ['comment', 'tell me']
        
        clarity_score = 0.0
        
        for cta in cta_elements:
            cta_type = cta["type"]
            if cta_type in strong_ctas:
                clarity_score += 3
            elif cta_type in medium_ctas:
                clarity_score += 2
            elif cta_type in weak_ctas:
                clarity_score += 1
        
        avg_clarity = clarity_score / len(cta_elements) if cta_elements else 0
        
        return {
            "score": min(10.0, avg_clarity * 3),
            "avg_strength": round(avg_clarity, 2)
        }
    
    def _analyze_cta_frequency(self, script: str, cta_elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CTA frequency appropriateness"""
        word_count = len(script.split())
        cta_count = len(cta_elements)
        
        if word_count == 0:
            return {"score": 0.0}
        
        cta_ratio = cta_count / (word_count / 100)  # CTAs per 100 words
        
        # Optimal: 1-2 CTAs per 100 words
        if 0.5 <= cta_ratio <= 2.0:
            score = 10.0
        elif 0.2 <= cta_ratio <= 3.0:
            score = 8.0
        elif cta_ratio == 0:
            score = 0.0
        else:
            score = max(0.0, 8.0 - abs(cta_ratio - 1.25) * 3)
        
        return {
            "score": score,
            "count": cta_count,
            "ratio": round(cta_ratio, 2)
        }
    
    def _check_platform_cta_compliance(self, cta_elements: List[Dict[str, Any]], platform_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Check platform-specific CTA compliance"""
        compliance_score = 5.0  # Base score
        
        # Platform-specific bonuses
        cta_types = [cta["type"] for cta in cta_elements]
        
        if "subscribe" in cta_types:
            compliance_score += 2.0  # Always good for most platforms
        
        if "like" in cta_types:
            compliance_score += 1.5
        
        if "share" in cta_types:
            compliance_score += 1.5
        
        return {
            "score": min(10.0, compliance_score),
            "cta_types": cta_types
        }
    
    # Scoring and recommendation methods
    
    def _calculate_validation_score(self, component_scores: Dict[str, float]) -> float:
        """Calculate weighted overall validation score"""
        total_score = 0.0
        for component, score in component_scores.items():
            weight = self.validation_weights.get(component, 0.25)
            total_score += score * weight
        return total_score
    
    def _determine_validation_status(self, score: float) -> str:
        """Determine validation status based on score"""
        if score >= 8.5:
            return "EXCELLENT"
        elif score >= 7.5:
            return "GOOD"
        elif score >= 6.5:
            return "ACCEPTABLE"
        elif score >= 5.0:
            return "NEEDS_IMPROVEMENT"
        else:
            return "REQUIRES_MAJOR_REVISION"
    
    def _get_validation_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 9.0:
            return "A+"
        elif score >= 8.5:
            return "A"
        elif score >= 8.0:
            return "A-"
        elif score >= 7.5:
            return "B+"
        elif score >= 7.0:
            return "B"
        elif score >= 6.5:
            return "B-"
        elif score >= 6.0:
            return "C+"
        elif score >= 5.5:
            return "C"
        elif score >= 5.0:
            return "C-"
        elif score >= 4.0:
            return "D"
        else:
            return "F"
    
    def _generate_validation_recommendations(self, hook_val, pacing_val, retention_val, cta_val, platform) -> List[str]:
        """Generate comprehensive validation recommendations"""
        recommendations = []
        
        # Hook recommendations
        if hook_val["score"] < 7:
            recommendations.extend(hook_val.get("recommendations", [])[:2])
        
        # Pacing recommendations
        if pacing_val["score"] < 7:
            recommendations.extend(pacing_val.get("recommendations", [])[:2])
        
        # Retention recommendations
        if retention_val["score"] < 7:
            recommendations.extend(retention_val.get("recommendations", [])[:2])
        
        # CTA recommendations
        if cta_val["score"] < 7:
            recommendations.extend(cta_val.get("recommendations", [])[:2])
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _identify_critical_issues(self, hook_val, pacing_val, retention_val, cta_val) -> List[Dict[str, str]]:
        """Identify critical issues requiring immediate attention"""
        critical_issues = []
        
        if hook_val["score"] < 5:
            critical_issues.append({
                "area": "Hook",
                "severity": "HIGH",
                "issue": "Hook fails to engage audience effectively",
                "impact": "High drop-off rate in first few seconds"
            })
        
        if retention_val["score"] < 4:
            critical_issues.append({
                "area": "Retention",
                "severity": "HIGH",
                "issue": "Insufficient retention elements throughout script",
                "impact": "Poor audience retention and engagement"
            })
        
        if cta_val["score"] < 3:
            critical_issues.append({
                "area": "Call-to-Action",
                "severity": "MEDIUM",
                "issue": "Weak or missing call-to-action elements",
                "impact": "Low conversion and audience action"
            })
        
        if pacing_val["score"] < 4:
            critical_issues.append({
                "area": "Pacing",
                "severity": "MEDIUM",
                "issue": "Poor pacing may lose audience attention",
                "impact": "Reduced engagement and retention"
            })
        
        return critical_issues
    
    def _generate_compliance_summary(self, hook_val, pacing_val, retention_val, cta_val) -> Dict[str, str]:
        """Generate compliance summary"""
        components = {
            "Hook Quality": hook_val["score"],
            "Pacing Optimization": pacing_val["score"],
            "Retention Elements": retention_val["score"],
            "CTA Effectiveness": cta_val["score"]
        }
        
        compliant = sum(1 for score in components.values() if score >= 7)
        total = len(components)
        
        return {
            "overall_compliance": f"{compliant}/{total} components meeting standards",
            "compliance_rate": f"{(compliant/total)*100:.1f}%",
            "status": "COMPLIANT" if compliant >= 3 else "NON_COMPLIANT"
        }
    
    # Recommendation generation helper methods
    
    def _generate_hook_recommendations(self, curiosity_score, value_score, emotional_score, engagement_score) -> List[str]:
        """Generate hook-specific recommendations"""
        recommendations = []
        
        if curiosity_score < 5:
            recommendations.append("Add curiosity gap with 'secret', 'surprising', or 'what if' elements")
        if value_score < 5:
            recommendations.append("Clearly state the value or benefit audience will receive")
        if emotional_score < 4:
            recommendations.append("Include emotional triggers like 'amazing', 'shocking', or urgency words")
        if engagement_score < 5:
            recommendations.append("Use direct audience address with 'you' and rhetorical questions")
        
        return recommendations
    
    def _generate_pacing_recommendations(self, sentence_analysis, paragraph_analysis, transition_analysis, dead_zones) -> List[str]:
        """Generate pacing-specific recommendations"""
        recommendations = []
        
        if sentence_analysis["score"] < 6:
            recommendations.append("Vary sentence lengths - mix short punchy sentences with longer explanations")
        if transition_analysis["score"] < 5:
            recommendations.append("Add more transition words like 'however', 'because', 'next' for better flow")
        if len(dead_zones) > 1:
            recommendations.append("Break up long segments with questions or engagement elements")
        if paragraph_analysis["score"] < 6:
            recommendations.append("Optimize paragraph length - aim for 30-70 words per paragraph")
        
        return recommendations
    
    def _generate_retention_recommendations(self, question_analysis, pattern_analysis, curiosity_analysis, distribution_analysis) -> List[str]:
        """Generate retention-specific recommendations"""
        recommendations = []
        
        if question_analysis["score"] < 6:
            recommendations.append("Add more rhetorical questions to maintain engagement")
        if pattern_analysis["score"] < 5:
            recommendations.append("Include pattern interrupts like 'but', 'however', 'surprisingly'")
        if curiosity_analysis["score"] < 6:
            recommendations.append("Create curiosity loops - open mysteries and resolve them later")
        if distribution_analysis["score"] < 6:
            recommendations.append("Distribute retention elements more evenly throughout the script")
        
        return recommendations
    
    def _generate_cta_recommendations(self, cta_elements, placement_analysis, clarity_analysis, frequency_analysis, platform_rules) -> List[str]:
        """Generate CTA-specific recommendations"""
        recommendations = []
        
        if len(cta_elements) == 0:
            recommendations.append("Add at least one clear call-to-action")
        elif len(cta_elements) > 4:
            recommendations.append("Reduce number of CTAs to avoid overwhelming audience")
        
        if placement_analysis["score"] < 6:
            optimal_positions = platform_rules["cta_positions"]
            recommendations.append(f"Place CTAs in optimal positions: {', '.join(optimal_positions)}")
        
        if clarity_analysis["score"] < 6:
            recommendations.append("Use stronger, more direct action words in CTAs")
        
        if frequency_analysis["score"] < 6:
            recommendations.append("Adjust CTA frequency - aim for 1-2 CTAs per 100 words")
        
        return recommendations
    
    def _get_empty_script_validation(self) -> Dict[str, Any]:
        """Return validation for empty script"""
        return {
            "validation_status": "INVALID",
            "overall_score": 0.0,
            "validation_grade": "F",
            "critical_issues": [{"area": "Content", "severity": "HIGH", "issue": "No script content provided"}],
            "recommendations": ["Provide script content for validation"],
            "validation_metadata": {
                "validated_at": datetime.utcnow().isoformat(),
                "error": "Empty script"
            }
        }
    
    def _get_error_validation(self, error_message: str) -> Dict[str, Any]:
        """Return validation for error case"""
        return {
            "validation_status": "ERROR",
            "overall_score": 0.0,
            "validation_grade": "Error",
            "error": error_message,
            "recommendations": ["Please try again with valid script content"],
            "validation_metadata": {
                "validated_at": datetime.utcnow().isoformat(),
                "error": error_message
            }
        }
"""
Phase 3: Script Quality Analyzer
Comprehensive script quality analysis with retention, engagement, and optimization scoring
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import textstat
from collections import Counter
import math

logger = logging.getLogger(__name__)

class ScriptQualityAnalyzer:
    """Comprehensive script quality analysis engine"""
    
    def __init__(self):
        # Define quality scoring weights (Phase 4: Updated with new metrics)
        self.scoring_weights = {
            "structural_compliance": 0.15,        # Phase 4: Adherence to template structure
            "engagement_density": 0.15,           # Phase 4: Hooks per minute ratio  
            "emotional_arc_strength": 0.15,       # Phase 4: Peak-to-valley emotional variance
            "platform_optimization": 0.15,       # Phase 4: Algorithm-friendly elements
            "retention_potential": 0.15,          # Phase 4: Predicted watch-through rate
            "viral_coefficient": 0.125,           # Phase 4: Shareability prediction
            "conversion_potential": 0.125         # Phase 4: CTA effectiveness score
        }
        
        # Phase 4: Quality Metrics Dictionary as specified
        self.QUALITY_METRICS = {
            "structural_compliance": 0.0,    # Adherence to template structure
            "engagement_density": 0.0,       # Hooks per minute ratio
            "emotional_arc_strength": 0.0,   # Peak-to-valley emotional variance
            "platform_optimization": 0.0,    # Algorithm-friendly elements
            "retention_potential": 0.0,      # Predicted watch-through rate
            "viral_coefficient": 0.0,        # Shareability prediction
            "conversion_potential": 0.0      # CTA effectiveness score
        }
        
        # Platform-specific optimization criteria
        self.platform_criteria = {
            "youtube": {
                "optimal_length": {"short": 30, "medium": 180, "long": 600},
                "hook_duration": 15,
                "retention_checkpoints": [15, 30, 60, 120],
                "engagement_frequency": 30,  # Every 30 seconds
                "cta_placement": ["beginning", "middle", "end"]
            },
            "tiktok": {
                "optimal_length": {"short": 15, "medium": 30, "long": 60},
                "hook_duration": 3,
                "retention_checkpoints": [3, 7, 15, 30],
                "engagement_frequency": 10,  # Every 10 seconds
                "cta_placement": ["beginning", "end"]
            },
            "instagram": {
                "optimal_length": {"short": 15, "medium": 60, "long": 90},
                "hook_duration": 5,
                "retention_checkpoints": [5, 15, 30, 60],
                "engagement_frequency": 20,  # Every 20 seconds
                "cta_placement": ["beginning", "end"]
            },
            "linkedin": {
                "optimal_length": {"short": 60, "medium": 120, "long": 300},
                "hook_duration": 10,
                "retention_checkpoints": [10, 30, 60, 120],
                "engagement_frequency": 45,  # Every 45 seconds
                "cta_placement": ["end"]
            }
        }
        
        # Emotional arc patterns
        self.emotional_patterns = {
            "hero_journey": ["challenge", "struggle", "breakthrough", "triumph"],
            "problem_solution": ["problem", "agitation", "solution", "resolution"],
            "curiosity_gap": ["mystery", "investigation", "revelation", "conclusion"],
            "transformation": ["before", "catalyst", "process", "after"]
        }
    
    def analyze_script_quality(self, script: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive script quality analysis
        
        Args:
            script: The script content to analyze
            metadata: Additional context (platform, duration, etc.)
        
        Returns:
            Dictionary with detailed quality scores and recommendations
        """
        if not script or not script.strip():
            return self._get_empty_script_analysis()
        
        try:
            metadata = metadata or {}
            platform = metadata.get('target_platform', 'youtube').lower()
            duration = metadata.get('duration', 'medium')
            
            # Phase 4: Enhanced quality analyses with new metrics
            structural_analysis = self.analyze_structural_compliance(script, metadata)
            engagement_density_analysis = self.calculate_engagement_density(script, platform, duration)
            emotional_analysis = self.analyze_emotional_journey(script)
            platform_analysis = self.check_platform_compliance(script, platform, duration)
            retention_analysis = self.calculate_retention_score(script, platform, duration)
            viral_analysis = self.calculate_viral_coefficient(script, platform, metadata)
            conversion_analysis = self.calculate_conversion_potential(script, platform, metadata)
            
            # Keep legacy analyses for backward compatibility
            engagement_analysis = self.count_engagement_hooks(script, platform)
            cta_analysis = self.evaluate_cta(script, platform)
            
            # Calculate weighted overall score with Phase 4 metrics
            overall_score = self._calculate_weighted_score({
                "structural_compliance": structural_analysis["score"],
                "engagement_density": engagement_density_analysis["score"], 
                "emotional_arc_strength": emotional_analysis["score"],
                "platform_optimization": platform_analysis["score"],
                "retention_potential": retention_analysis["score"],
                "viral_coefficient": viral_analysis["score"],
                "conversion_potential": conversion_analysis["score"]
            })
            
            # Generate comprehensive recommendations
            recommendations = self._generate_comprehensive_recommendations(
                retention_analysis, engagement_analysis, emotional_analysis,
                platform_analysis, cta_analysis, metadata
            )
            
            return {
                "overall_quality_score": round(overall_score, 2),
                "quality_grade": self._get_quality_grade(overall_score),
                "detailed_scores": {
                    "retention_potential": retention_analysis,
                    "engagement_triggers": engagement_analysis,
                    "emotional_arc_strength": emotional_analysis,
                    "platform_optimization": platform_analysis,
                    "call_to_action_effectiveness": cta_analysis
                },
                "recommendations": recommendations,
                "strengths": self._identify_strengths(retention_analysis, engagement_analysis, 
                                                   emotional_analysis, platform_analysis, cta_analysis),
                "improvement_areas": self._identify_improvement_areas(retention_analysis, engagement_analysis,
                                                                   emotional_analysis, platform_analysis, cta_analysis),
                "optimization_priority": self._get_optimization_priority(retention_analysis, engagement_analysis,
                                                                       emotional_analysis, platform_analysis, cta_analysis),
                "analysis_metadata": {
                    "analyzed_at": datetime.utcnow().isoformat(),
                    "script_length": len(script),
                    "word_count": len(script.split()),
                    "platform": platform,
                    "duration": duration
                }
            }
            
        except Exception as e:
            logger.error(f"Error in script quality analysis: {str(e)}")
            return self._get_error_analysis(str(e))
    
    def calculate_retention_score(self, script: str, platform: str = "youtube", duration: str = "medium") -> Dict[str, Any]:
        """Calculate script's retention potential score"""
        try:
            # Get platform-specific criteria
            platform_config = self.platform_criteria.get(platform, self.platform_criteria["youtube"])
            
            # Analyze hook strength (first portion of script)
            hook_strength = self._analyze_hook_section(script, platform_config["hook_duration"])
            
            # Analyze pacing and rhythm
            pacing_score = self._analyze_pacing(script)
            
            # Check for retention checkpoints
            checkpoint_score = self._analyze_retention_checkpoints(script, platform_config["retention_checkpoints"])
            
            # Analyze content structure
            structure_score = self._analyze_content_structure(script)
            
            # Calculate drop-off risk points
            drop_off_risks = self._identify_drop_off_risks(script)
            
            # Overall retention score (weighted combination)
            retention_score = (
                hook_strength * 0.35 +
                pacing_score * 0.25 +
                checkpoint_score * 0.20 +
                structure_score * 0.20
            )
            
            return {
                "score": round(min(10.0, retention_score), 2),
                "hook_strength": round(hook_strength, 2),
                "pacing_quality": round(pacing_score, 2),
                "checkpoint_effectiveness": round(checkpoint_score, 2),
                "structure_quality": round(structure_score, 2),
                "drop_off_risks": drop_off_risks,
                "retention_recommendations": self._generate_retention_recommendations(
                    hook_strength, pacing_score, checkpoint_score, structure_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating retention score: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    def _analyze_hook_section(self, script: str, hook_duration: int) -> float:
        """Analyze the effectiveness of the opening hook"""
        words = script.split()
        if not words:
            return 0.0
        
        # Estimate words for hook duration (assuming ~2 words per second)
        hook_word_count = min(len(words), hook_duration * 2)
        hook_text = ' '.join(words[:hook_word_count])
        
        hook_score = 0.0
        
        # Check for strong hook indicators
        strong_hooks = [
            'imagine', 'what if', 'did you know', 'here\'s why', 'secret',
            'mistake', 'truth', 'revealed', 'shocking', 'never', 'always',
            'everyone', 'nobody', 'first time', 'last time', 'only way'
        ]
        
        hook_lower = hook_text.lower()
        for hook_phrase in strong_hooks:
            if hook_phrase in hook_lower:
                hook_score += 1.5
        
        # Check for questions (curiosity gap)
        if '?' in hook_text:
            hook_score += 2.0
        
        # Check for numbers/statistics
        if re.search(r'\d+', hook_text):
            hook_score += 1.0
        
        # Check for personal pronouns (connection)
        personal_pronouns = len(re.findall(r'\b(you|your|we|us|our)\b', hook_lower))
        hook_score += min(2.0, personal_pronouns * 0.5)
        
        # Emotional language bonus
        emotional_words = ['amazing', 'incredible', 'shocking', 'unbelievable', 'fantastic']
        for word in emotional_words:
            if word in hook_lower:
                hook_score += 0.8
        
        return min(10.0, hook_score)
    
    def _analyze_pacing(self, script: str) -> float:
        """Analyze script pacing and rhythm"""
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        if not sentences:
            return 5.0
        
        # Calculate sentence length variations
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Good pacing has variety in sentence lengths
        length_variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        variance_score = min(10.0, math.sqrt(length_variance))
        
        # Check for pacing markers
        pacing_markers = ['but', 'however', 'meanwhile', 'suddenly', 'then', 'next', 'finally']
        pacing_count = sum(1 for marker in pacing_markers if marker.lower() in script.lower())
        pacing_score = min(5.0, pacing_count * 0.8)
        
        # Optimal sentence length (8-15 words average)
        length_score = 10.0 - abs(avg_length - 11.5) * 0.5
        length_score = max(0.0, length_score)
        
        return (variance_score * 0.3 + pacing_score * 0.3 + length_score * 0.4)
    
    def _analyze_retention_checkpoints(self, script: str, checkpoints: List[int]) -> float:
        """Analyze presence of retention elements at key checkpoints"""
        words = script.split()
        if not words:
            return 0.0
        
        total_words = len(words)
        checkpoint_score = 0.0
        
        retention_elements = ['question', 'reveal', 'tip', 'secret', 'but', 'however', 'surprise']
        
        for checkpoint in checkpoints:
            # Calculate word position for this checkpoint (assuming ~2 words per second)
            checkpoint_word_pos = min(total_words - 1, checkpoint * 2)
            
            # Check surrounding words (±10 words)
            start_pos = max(0, checkpoint_word_pos - 10)
            end_pos = min(total_words, checkpoint_word_pos + 10)
            
            checkpoint_text = ' '.join(words[start_pos:end_pos]).lower()
            
            # Check for retention elements
            element_found = any(element in checkpoint_text for element in retention_elements)
            if element_found:
                checkpoint_score += 2.5
            
            # Check for questions at checkpoints
            if '?' in checkpoint_text:
                checkpoint_score += 1.5
        
        return min(10.0, checkpoint_score)
    
    def _analyze_content_structure(self, script: str) -> float:
        """Analyze overall content structure quality"""
        structure_score = 0.0
        
        # Check for clear sections
        sections = ['introduction', 'main content', 'conclusion']
        script_lower = script.lower()
        
        # Introduction indicators
        intro_indicators = ['welcome', 'today', 'going to', 'will show', 'about to']
        if any(indicator in script_lower for indicator in intro_indicators):
            structure_score += 2.0
        
        # Main content indicators (lists, steps, points)
        content_indicators = ['first', 'second', 'next', 'then', 'finally', 'step', 'point']
        content_count = sum(1 for indicator in content_indicators if indicator in script_lower)
        structure_score += min(4.0, content_count * 0.8)
        
        # Conclusion indicators
        conclusion_indicators = ['conclusion', 'summary', 'remember', 'takeaway', 'key point']
        if any(indicator in script_lower for indicator in conclusion_indicators):
            structure_score += 2.0
        
        # Logical flow (transition words)
        transition_words = ['because', 'therefore', 'however', 'moreover', 'furthermore', 'consequently']
        transition_count = sum(1 for word in transition_words if word in script_lower)
        structure_score += min(2.0, transition_count * 0.5)
        
        return min(10.0, structure_score)
    
    def _identify_drop_off_risks(self, script: str) -> List[Dict[str, str]]:
        """Identify potential drop-off risk points"""
        risks = []
        words = script.split()
        
        if not words:
            return [{"risk": "Empty script", "severity": "high"}]
        
        # Check for overly long segments without engagement
        sentences = script.split('.')
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 25:  # Very long sentence
                risks.append({
                    "risk": f"Long sentence at position {i+1} may lose attention",
                    "severity": "medium",
                    "suggestion": "Break into shorter, punchier sentences"
                })
        
        # Check for lack of questions in middle section
        middle_start = len(words) // 3
        middle_end = 2 * len(words) // 3
        middle_text = ' '.join(words[middle_start:middle_end])
        
        if '?' not in middle_text and len(words) > 50:
            risks.append({
                "risk": "No engagement questions in middle section",
                "severity": "medium",
                "suggestion": "Add rhetorical questions to maintain interest"
            })
        
        return risks[:5]  # Top 5 risks
    
    def count_engagement_hooks(self, script: str, platform: str = "youtube") -> Dict[str, Any]:
        """Count and analyze engagement triggers in the script"""
        try:
            platform_config = self.platform_criteria.get(platform, self.platform_criteria["youtube"])
            
            # Count different types of engagement elements
            questions = script.count('?')
            exclamations = script.count('!')
            
            # Count direct address to audience
            personal_pronouns = len(re.findall(r'\b(you|your|we|us|our)\b', script, re.IGNORECASE))
            
            # Count call-to-action words
            cta_words = ['subscribe', 'like', 'comment', 'share', 'follow', 'click', 'watch', 'check']
            cta_count = sum(1 for word in cta_words if word.lower() in script.lower())
            
            # Count emotional triggers
            emotional_triggers = [
                'amazing', 'incredible', 'shocking', 'surprising', 'unbelievable',
                'secret', 'hidden', 'revealed', 'exclusive', 'limited',
                'urgent', 'important', 'crucial', 'essential', 'vital'
            ]
            emotional_count = sum(1 for trigger in emotional_triggers if trigger.lower() in script.lower())
            
            # Count interactive elements
            interactive_elements = ['imagine', 'picture', 'think about', 'consider', 'what if']
            interactive_count = sum(1 for element in interactive_elements if element.lower() in script.lower())
            
            # Count curiosity gaps
            curiosity_indicators = ['secret', 'reason', 'truth', 'why', 'how', 'what', 'mystery']
            curiosity_count = sum(1 for indicator in curiosity_indicators if indicator.lower() in script.lower())
            
            # Calculate engagement frequency score
            total_words = len(script.split())
            expected_frequency = platform_config["engagement_frequency"]
            actual_frequency = total_words / max(1, (questions + cta_count + interactive_count))
            frequency_score = 10.0 - abs(actual_frequency - expected_frequency) * 0.2
            frequency_score = max(0.0, min(10.0, frequency_score))
            
            # Overall engagement score
            engagement_score = (
                min(10.0, questions * 1.5) * 0.25 +
                min(10.0, emotional_count * 1.2) * 0.25 +
                min(10.0, interactive_count * 2.0) * 0.20 +
                min(10.0, cta_count * 1.8) * 0.15 +
                frequency_score * 0.15
            )
            
            return {
                "score": round(engagement_score, 2),
                "questions_count": questions,
                "emotional_triggers_count": emotional_count,
                "interactive_elements_count": interactive_count,
                "cta_elements_count": cta_count,
                "personal_connection_score": round(min(10.0, personal_pronouns * 0.3), 2),
                "curiosity_gaps_count": curiosity_count,
                "engagement_frequency_score": round(frequency_score, 2),
                "engagement_breakdown": {
                    "questions": questions,
                    "exclamations": exclamations,
                    "emotional_words": emotional_count,
                    "interactive_prompts": interactive_count,
                    "call_to_actions": cta_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error counting engagement hooks: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    def analyze_emotional_journey(self, script: str) -> Dict[str, Any]:
        """Analyze the emotional arc and journey of the script"""
        try:
            # Split script into segments for arc analysis
            words = script.split()
            if not words:
                return {"score": 0.0, "arc_type": "none"}
            
            segment_size = max(1, len(words) // 4)  # Divide into 4 segments
            segments = [
                ' '.join(words[i:i+segment_size]) 
                for i in range(0, len(words), segment_size)
            ]
            
            # Analyze emotional intensity in each segment
            emotional_progression = []
            for segment in segments:
                intensity = self._calculate_emotional_intensity(segment)
                emotional_progression.append(intensity)
            
            # Identify emotional arc pattern
            arc_pattern = self._identify_emotional_arc(emotional_progression)
            
            # Calculate emotional variety
            emotional_variety = self._calculate_emotional_variety(script)
            
            # Calculate emotional peaks and valleys
            peaks_valleys = self._identify_emotional_peaks_valleys(emotional_progression)
            
            # Overall emotional arc strength
            arc_strength = self._calculate_arc_strength(emotional_progression, arc_pattern)
            
            return {
                "score": round(arc_strength, 2),
                "arc_type": arc_pattern["type"],
                "arc_description": arc_pattern["description"],
                "emotional_progression": [round(p, 2) for p in emotional_progression],
                "emotional_variety_score": round(emotional_variety, 2),
                "emotional_peaks": peaks_valleys["peaks"],
                "emotional_valleys": peaks_valleys["valleys"],
                "arc_recommendations": self._generate_emotional_arc_recommendations(
                    emotional_progression, arc_pattern, emotional_variety
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotional journey: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate emotional intensity of a text segment"""
        # Define emotional word categories with weights
        high_intensity = {
            'positive': ['amazing', 'incredible', 'fantastic', 'extraordinary', 'phenomenal', 'brilliant'],
            'negative': ['terrible', 'horrible', 'devastating', 'shocking', 'catastrophic', 'tragic'],
            'excitement': ['exciting', 'thrilling', 'exhilarating', 'electrifying', 'stunning'],
            'urgency': ['urgent', 'critical', 'crucial', 'immediate', 'emergency', 'now']
        }
        
        medium_intensity = {
            'positive': ['good', 'great', 'nice', 'pleasant', 'enjoyable', 'satisfying'],
            'negative': ['bad', 'poor', 'disappointing', 'concerning', 'problematic'],
            'curiosity': ['interesting', 'curious', 'mysterious', 'intriguing', 'surprising'],
            'importance': ['important', 'significant', 'notable', 'valuable', 'useful']
        }
        
        text_lower = text.lower()
        intensity_score = 0.0
        
        # Count high intensity words
        for category, words in high_intensity.items():
            for word in words:
                if word in text_lower:
                    intensity_score += 3.0
        
        # Count medium intensity words
        for category, words in medium_intensity.items():
            for word in words:
                if word in text_lower:
                    intensity_score += 1.5
        
        # Factor in punctuation
        intensity_score += text.count('!') * 0.5
        intensity_score += text.count('?') * 0.3
        
        # Normalize by text length
        word_count = len(text.split())
        if word_count > 0:
            intensity_score = (intensity_score / word_count) * 100
        
        return min(10.0, intensity_score)
    
    def _identify_emotional_arc(self, progression: List[float]) -> Dict[str, str]:
        """Identify the type of emotional arc"""
        if len(progression) < 3:
            return {"type": "insufficient_data", "description": "Not enough content for arc analysis"}
        
        # Analyze progression pattern
        start = progression[0]
        middle = sum(progression[1:-1]) / max(1, len(progression[1:-1]))
        end = progression[-1]
        
        # Determine arc type based on pattern
        if start < middle > end and middle - start > 2 and middle - end > 2:
            return {"type": "peak_arc", "description": "Builds to emotional peak then resolves"}
        elif start > middle < end and start - middle > 2 and end - middle > 2:
            return {"type": "valley_arc", "description": "Starts high, dips, then recovers"}
        elif end > start + 2:
            return {"type": "ascending_arc", "description": "Gradually builds emotional intensity"}
        elif start > end + 2:
            return {"type": "descending_arc", "description": "Starts intense then calms down"}
        elif max(progression) - min(progression) < 2:
            return {"type": "flat_arc", "description": "Consistent emotional tone throughout"}
        else:
            return {"type": "mixed_arc", "description": "Complex emotional journey with multiple peaks"}
    
    def _calculate_emotional_variety(self, script: str) -> float:
        """Calculate variety of emotional elements"""
        emotional_categories = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'cheerful'],
            'surprise': ['surprising', 'shocking', 'unexpected', 'amazing', 'incredible'],
            'fear': ['scary', 'frightening', 'terrifying', 'alarming', 'worried'],
            'anger': ['angry', 'furious', 'outraged', 'frustrated', 'annoyed'],
            'sadness': ['sad', 'disappointed', 'heartbroken', 'tragic', 'unfortunate'],
            'curiosity': ['mysterious', 'intriguing', 'puzzling', 'curious', 'wondering']
        }
        
        script_lower = script.lower()
        categories_found = 0
        
        for category, words in emotional_categories.items():
            if any(word in script_lower for word in words):
                categories_found += 1
        
        variety_score = (categories_found / len(emotional_categories)) * 10
        return min(10.0, variety_score)
    
    def _identify_emotional_peaks_valleys(self, progression: List[float]) -> Dict[str, List[int]]:
        """Identify emotional peaks and valleys in the progression"""
        peaks = []
        valleys = []
        
        for i in range(1, len(progression) - 1):
            if progression[i] > progression[i-1] and progression[i] > progression[i+1]:
                peaks.append(i)
            elif progression[i] < progression[i-1] and progression[i] < progression[i+1]:
                valleys.append(i)
        
        return {"peaks": peaks, "valleys": valleys}
    
    def _calculate_arc_strength(self, progression: List[float], arc_pattern: Dict[str, str]) -> float:
        """Calculate overall strength of emotional arc"""
        if not progression:
            return 0.0
        
        # Base score from progression range
        progression_range = max(progression) - min(progression)
        range_score = min(8.0, progression_range)
        
        # Bonus for specific arc types
        arc_bonuses = {
            "peak_arc": 2.0,
            "valley_arc": 1.5,
            "ascending_arc": 1.8,
            "descending_arc": 1.2,
            "mixed_arc": 1.0,
            "flat_arc": 0.0
        }
        
        arc_bonus = arc_bonuses.get(arc_pattern["type"], 0.5)
        
        # Penalty for too flat progression
        if progression_range < 1:
            range_score *= 0.3
        
        return min(10.0, range_score + arc_bonus)
    
    def check_platform_compliance(self, script: str, platform: str = "youtube", duration: str = "medium") -> Dict[str, Any]:
        """Check script compliance with platform-specific best practices"""
        try:
            platform_config = self.platform_criteria.get(platform, self.platform_criteria["youtube"])
            
            # Calculate estimated duration (assuming ~2 words per second)
            word_count = len(script.split())
            estimated_duration = word_count / 2
            
            # Check length compliance
            optimal_length = platform_config["optimal_length"][duration]
            length_compliance = self._calculate_length_compliance(estimated_duration, optimal_length)
            
            # Check hook timing
            hook_compliance = self._check_hook_timing(script, platform_config["hook_duration"])
            
            # Check engagement frequency
            engagement_compliance = self._check_engagement_frequency(script, platform_config["engagement_frequency"])
            
            # Check platform-specific elements
            platform_elements = self._check_platform_elements(script, platform)
            
            # Overall platform optimization score
            optimization_score = (
                length_compliance * 0.3 +
                hook_compliance * 0.3 +
                engagement_compliance * 0.25 +
                platform_elements * 0.15
            )
            
            return {
                "score": round(optimization_score, 2),
                "platform": platform,
                "estimated_duration": round(estimated_duration, 1),
                "optimal_duration": optimal_length,
                "length_compliance": round(length_compliance, 2),
                "hook_compliance": round(hook_compliance, 2),
                "engagement_frequency_compliance": round(engagement_compliance, 2),
                "platform_specific_score": round(platform_elements, 2),
                "platform_recommendations": self._generate_platform_recommendations(
                    platform, length_compliance, hook_compliance, engagement_compliance
                )
            }
            
        except Exception as e:
            logger.error(f"Error checking platform compliance: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    def _calculate_length_compliance(self, actual_duration: float, optimal_duration: float) -> float:
        """Calculate how well the script length matches platform optimal length"""
        if optimal_duration == 0:
            return 5.0
        
        ratio = actual_duration / optimal_duration
        
        # Best compliance when ratio is between 0.8 and 1.2
        if 0.8 <= ratio <= 1.2:
            return 10.0
        elif 0.6 <= ratio <= 1.5:
            return 8.0
        elif 0.4 <= ratio <= 2.0:
            return 6.0
        elif 0.2 <= ratio <= 3.0:
            return 4.0
        else:
            return 2.0
    
    def _check_hook_timing(self, script: str, hook_duration: int) -> float:
        """Check if hook is appropriately timed for platform"""
        words = script.split()
        if not words:
            return 0.0
        
        hook_word_count = hook_duration * 2  # ~2 words per second
        hook_text = ' '.join(words[:min(len(words), hook_word_count)])
        
        # Check for strong hook elements
        hook_score = self._analyze_hook_section(script, hook_duration)
        
        # Normalize to 0-10 scale
        return min(10.0, hook_score)
    
    def _check_engagement_frequency(self, script: str, target_frequency: int) -> float:
        """Check if engagement elements are appropriately spaced"""
        words = script.split()
        if not words:
            return 0.0
        
        total_duration = len(words) / 2  # Estimated duration in seconds
        
        # Count engagement elements
        engagement_elements = (
            script.count('?') +
            len(re.findall(r'\b(you|your)\b', script, re.IGNORECASE)) +
            script.count('!')
        )
        
        if engagement_elements == 0:
            return 2.0
        
        actual_frequency = total_duration / engagement_elements
        
        # Score based on how close to target frequency
        frequency_diff = abs(actual_frequency - target_frequency)
        frequency_score = max(0.0, 10.0 - (frequency_diff * 0.3))
        
        return frequency_score
    
    def _check_platform_elements(self, script: str, platform: str) -> float:
        """Check for platform-specific optimization elements"""
        script_lower = script.lower()
        platform_score = 5.0  # Base score
        
        if platform == "tiktok":
            # TikTok-specific elements
            if any(word in script_lower for word in ['trending', 'viral', 'challenge', 'duet']):
                platform_score += 2.0
            if any(word in script_lower for word in ['quick', 'fast', 'instant', 'seconds']):
                platform_score += 1.5
                
        elif platform == "youtube":
            # YouTube-specific elements
            if any(word in script_lower for word in ['subscribe', 'notification', 'bell', 'channel']):
                platform_score += 2.0
            if any(word in script_lower for word in ['tutorial', 'guide', 'how to', 'learn']):
                platform_score += 1.5
                
        elif platform == "linkedin":
            # LinkedIn-specific elements
            if any(word in script_lower for word in ['professional', 'career', 'business', 'industry']):
                platform_score += 2.0
            if any(word in script_lower for word in ['insights', 'experience', 'expertise', 'strategy']):
                platform_score += 1.5
                
        elif platform == "instagram":
            # Instagram-specific elements
            if any(word in script_lower for word in ['story', 'behind', 'authentic', 'real']):
                platform_score += 2.0
            if any(word in script_lower for word in ['visual', 'beautiful', 'aesthetic', 'style']):
                platform_score += 1.5
        
        return min(10.0, platform_score)
    
    def evaluate_cta(self, script: str, platform: str = "youtube") -> Dict[str, Any]:
        """Evaluate call-to-action effectiveness"""
        try:
            platform_config = self.platform_criteria.get(platform, self.platform_criteria["youtube"])
            
            # Find all CTAs
            cta_analysis = self._find_cta_elements(script)
            
            # Check CTA placement
            placement_score = self._check_cta_placement(script, platform_config["cta_placement"])
            
            # Evaluate CTA strength
            strength_score = self._evaluate_cta_strength(cta_analysis["ctas"])
            
            # Check CTA frequency
            frequency_score = self._evaluate_cta_frequency(cta_analysis["ctas"], len(script.split()))
            
            # Overall CTA effectiveness
            cta_score = (
                placement_score * 0.35 +
                strength_score * 0.35 +
                frequency_score * 0.30
            )
            
            return {
                "score": round(cta_score, 2),
                "cta_count": cta_analysis["count"],
                "cta_types": cta_analysis["types"],
                "placement_score": round(placement_score, 2),
                "strength_score": round(strength_score, 2),
                "frequency_score": round(frequency_score, 2),
                "cta_recommendations": self._generate_cta_recommendations(
                    platform, cta_analysis, placement_score, strength_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error evaluating CTA: {str(e)}")
            return {"score": 5.0, "error": str(e)}
    
    def _find_cta_elements(self, script: str) -> Dict[str, Any]:
        """Find and categorize CTA elements in script"""
        cta_patterns = {
            'subscribe': r'\b(subscribe|sub|follow)\b',
            'like': r'\b(like|thumbs up|heart)\b',
            'comment': r'\b(comment|leave|tell|share thoughts)\b',
            'share': r'\b(share|spread|tell friends)\b',
            'click': r'\b(click|tap|press|visit)\b',
            'watch': r'\b(watch|check out|see|view)\b',
            'download': r'\b(download|get|grab)\b',
            'signup': r'\b(sign up|register|join)\b'
        }
        
        ctas = []
        cta_types = []
        
        script_lower = script.lower()
        
        for cta_type, pattern in cta_patterns.items():
            matches = re.findall(pattern, script_lower)
            if matches:
                ctas.extend(matches)
                cta_types.append(cta_type)
        
        return {
            "ctas": ctas,
            "count": len(ctas),
            "types": list(set(cta_types))
        }
    
    def _check_cta_placement(self, script: str, optimal_placements: List[str]) -> float:
        """Check if CTAs are placed in optimal positions"""
        words = script.split()
        if not words:
            return 0.0
        
        script_length = len(words)
        placement_score = 0.0
        
        # Define sections
        beginning = ' '.join(words[:script_length//4])
        middle = ' '.join(words[script_length//4:3*script_length//4])
        end = ' '.join(words[3*script_length//4:])
        
        cta_words = ['subscribe', 'like', 'comment', 'share', 'click', 'follow']
        
        for placement in optimal_placements:
            if placement == "beginning":
                if any(cta in beginning.lower() for cta in cta_words):
                    placement_score += 3.0
            elif placement == "middle":
                if any(cta in middle.lower() for cta in cta_words):
                    placement_score += 2.5
            elif placement == "end":
                if any(cta in end.lower() for cta in cta_words):
                    placement_score += 3.5
        
        return min(10.0, placement_score)
    
    def _evaluate_cta_strength(self, ctas: List[str]) -> float:
        """Evaluate the strength and clarity of CTAs"""
        if not ctas:
            return 0.0
        
        # Strong CTA indicators
        strong_ctas = ['subscribe', 'follow', 'click', 'download', 'join']
        weak_ctas = ['maybe', 'might', 'could']
        
        strength_score = 0.0
        
        for cta in ctas:
            cta_lower = cta.lower()
            if any(strong in cta_lower for strong in strong_ctas):
                strength_score += 2.0
            elif any(weak in cta_lower for weak in weak_ctas):
                strength_score -= 0.5
            else:
                strength_score += 1.0
        
        # Average strength per CTA
        avg_strength = strength_score / len(ctas) if ctas else 0
        return min(10.0, avg_strength * 2)
    
    def _evaluate_cta_frequency(self, ctas: List[str], word_count: int) -> float:
        """Evaluate if CTA frequency is appropriate"""
        if word_count == 0:
            return 0.0
        
        cta_ratio = len(ctas) / word_count * 100  # CTAs per 100 words
        
        # Optimal ratio: 1-3 CTAs per 100 words
        if 1.0 <= cta_ratio <= 3.0:
            return 10.0
        elif 0.5 <= cta_ratio <= 4.0:
            return 8.0
        elif 0.2 <= cta_ratio <= 5.0:
            return 6.0
        else:
            return 3.0
    
    # Helper methods for generating recommendations and analysis
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall quality score"""
        total_score = 0.0
        for component, score in scores.items():
            weight = self.scoring_weights.get(component, 0.2)
            total_score += score * weight
        return total_score
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
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
    
    def _generate_comprehensive_recommendations(self, retention, engagement, emotional, platform, cta, metadata) -> List[str]:
        """Generate comprehensive improvement recommendations"""
        recommendations = []
        
        # Retention recommendations
        if retention.get("score", 0) < 7:
            recommendations.extend(retention.get("retention_recommendations", [])[:2])
        
        # Engagement recommendations
        if engagement.get("score", 0) < 7:
            if engagement.get("questions_count", 0) < 2:
                recommendations.append("Add more rhetorical questions to increase engagement")
            if engagement.get("interactive_elements_count", 0) < 1:
                recommendations.append("Include interactive prompts like 'imagine' or 'picture this'")
        
        # Emotional arc recommendations
        if emotional.get("score", 0) < 6:
            recommendations.extend(emotional.get("arc_recommendations", [])[:2])
        
        # Platform recommendations
        if platform.get("score", 0) < 7:
            recommendations.extend(platform.get("platform_recommendations", [])[:2])
        
        # CTA recommendations
        if cta.get("score", 0) < 6:
            recommendations.extend(cta.get("cta_recommendations", [])[:2])
        
        return recommendations[:8]  # Top 8 recommendations
    
    def _identify_strengths(self, retention, engagement, emotional, platform, cta) -> List[str]:
        """Identify script strengths"""
        strengths = []
        
        if retention.get("score", 0) >= 8:
            strengths.append("Excellent retention potential with strong hook and pacing")
        if engagement.get("score", 0) >= 8:
            strengths.append("High engagement with effective audience interaction")
        if emotional.get("score", 0) >= 7:
            strengths.append("Strong emotional journey that connects with audience")
        if platform.get("score", 0) >= 8:
            strengths.append("Well-optimized for target platform requirements")
        if cta.get("score", 0) >= 7:
            strengths.append("Effective call-to-action strategy")
        
        if not strengths:
            strengths.append("Script shows potential with room for optimization")
        
        return strengths[:5]
    
    def _identify_improvement_areas(self, retention, engagement, emotional, platform, cta) -> List[str]:
        """Identify areas needing improvement"""
        improvements = []
        
        scores = {
            "Retention and Hook Strength": retention.get("score", 0),
            "Audience Engagement": engagement.get("score", 0),
            "Emotional Journey": emotional.get("score", 0),
            "Platform Optimization": platform.get("score", 0),
            "Call-to-Action Effectiveness": cta.get("score", 0)
        }
        
        # Sort by lowest scores first
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for area, score in sorted_scores:
            if score < 7:
                improvements.append(area)
        
        return improvements[:3]  # Top 3 improvement areas
    
    def _get_optimization_priority(self, retention, engagement, emotional, platform, cta) -> str:
        """Determine optimization priority based on lowest scores"""
        scores = {
            "retention": retention.get("score", 0),
            "engagement": engagement.get("score", 0),
            "emotional": emotional.get("score", 0),
            "platform": platform.get("score", 0),
            "cta": cta.get("score", 0)
        }
        
        lowest_area = min(scores.items(), key=lambda x: x[1])
        
        priority_map = {
            "retention": "Focus on improving hook strength and content pacing",
            "engagement": "Prioritize adding more audience interaction elements",
            "emotional": "Develop stronger emotional arc and variety",
            "platform": "Optimize for platform-specific requirements",
            "cta": "Strengthen call-to-action placement and effectiveness"
        }
        
        return priority_map.get(lowest_area[0], "Overall content structure improvement")
    
    # Additional helper methods for specific recommendations
    
    def _generate_retention_recommendations(self, hook_strength, pacing_score, checkpoint_score, structure_score) -> List[str]:
        """Generate retention-specific recommendations"""
        recommendations = []
        
        if hook_strength < 6:
            recommendations.append("Strengthen opening hook with curiosity gap or bold statement")
        if pacing_score < 6:
            recommendations.append("Improve pacing with varied sentence lengths and transition words")
        if checkpoint_score < 6:
            recommendations.append("Add retention elements at key checkpoints (questions, reveals)")
        if structure_score < 6:
            recommendations.append("Improve content structure with clear introduction, body, and conclusion")
        
        return recommendations
    
    def _generate_emotional_arc_recommendations(self, progression, arc_pattern, variety) -> List[str]:
        """Generate emotional arc recommendations"""
        recommendations = []
        
        if arc_pattern["type"] == "flat_arc":
            recommendations.append("Add emotional variety - include peaks and valleys")
        if variety < 5:
            recommendations.append("Incorporate different emotional elements (surprise, curiosity, excitement)")
        if max(progression) < 6:
            recommendations.append("Increase emotional intensity with stronger language and examples")
        
        return recommendations
    
    def _generate_platform_recommendations(self, platform, length_compliance, hook_compliance, engagement_compliance) -> List[str]:
        """Generate platform-specific recommendations"""
        recommendations = []
        
        if length_compliance < 7:
            recommendations.append(f"Adjust content length for optimal {platform} performance")
        if hook_compliance < 7:
            recommendations.append(f"Optimize opening hook for {platform} attention spans")
        if engagement_compliance < 7:
            recommendations.append(f"Increase engagement frequency suitable for {platform}")
        
        # Platform-specific advice
        if platform == "tiktok":
            recommendations.append("Add trending elements and quick pacing for TikTok")
        elif platform == "youtube":
            recommendations.append("Include clear subscribe prompts and educational value")
        elif platform == "linkedin":
            recommendations.append("Focus on professional insights and industry expertise")
        
        return recommendations
    
    def _generate_cta_recommendations(self, platform, cta_analysis, placement_score, strength_score) -> List[str]:
        """Generate CTA-specific recommendations"""
        recommendations = []
        
        if cta_analysis["count"] == 0:
            recommendations.append("Add clear call-to-action elements")
        elif cta_analysis["count"] > 5:
            recommendations.append("Reduce CTA frequency to avoid overwhelming audience")
        
        if placement_score < 6:
            recommendations.append("Improve CTA placement at beginning or end of content")
        if strength_score < 6:
            recommendations.append("Use stronger, more direct action words in CTAs")
        
        return recommendations
    
    def _get_empty_script_analysis(self) -> Dict[str, Any]:
        """Return analysis for empty script"""
        return {
            "overall_quality_score": 0.0,
            "quality_grade": "F",
            "detailed_scores": {},
            "recommendations": ["Add content to script"],
            "strengths": [],
            "improvement_areas": ["All areas need development"],
            "optimization_priority": "Create initial content",
            "analysis_metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "script_length": 0,
                "word_count": 0
            }
        }
    
    def _get_error_analysis(self, error_message: str) -> Dict[str, Any]:
        """Return analysis for error case"""
        return {
            "overall_quality_score": 5.0,
            "quality_grade": "Error",
            "error": error_message,
            "recommendations": ["Please try again with valid script content"],
            "analysis_metadata": {
                "analyzed_at": datetime.utcnow().isoformat(),
                "error": error_message
            }
        }
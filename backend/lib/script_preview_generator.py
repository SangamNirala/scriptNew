"""
Phase 3: Script Preview Generator  
Advanced script preview system with engagement predictions and optimization suggestions
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import textstat
from collections import Counter, defaultdict
import math

logger = logging.getLogger(__name__)

class ScriptPreviewGenerator:
    """
    Advanced script preview generator that creates engagement timelines,
    retention predictions, and optimization suggestions
    """
    
    def __init__(self):
        # Preview generation settings
        self.preview_settings = {
            "timeline_segments": 10,  # Number of timeline segments
            "prediction_confidence_threshold": 0.7,
            "optimization_priority_levels": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            "engagement_threshold": 6.0,
            "retention_threshold": 70.0
        }
        
        # Platform-specific preview configurations
        self.platform_configs = {
            "youtube": {
                "optimal_engagement_points": [5, 15, 30, 60, 120, 180],
                "critical_retention_points": [3, 7, 15, 30],
                "expected_drop_off_rate": 0.15,  # 15% per segment
                "engagement_frequency_target": 30  # seconds
            },
            "tiktok": {
                "optimal_engagement_points": [1, 3, 7, 15, 30],
                "critical_retention_points": [1, 3, 5, 10],
                "expected_drop_off_rate": 0.25,
                "engagement_frequency_target": 10
            },
            "instagram": {
                "optimal_engagement_points": [2, 5, 15, 30, 60],
                "critical_retention_points": [2, 5, 10, 20],
                "expected_drop_off_rate": 0.20,
                "engagement_frequency_target": 20
            },
            "linkedin": {
                "optimal_engagement_points": [10, 30, 60, 120],
                "critical_retention_points": [10, 20, 45, 90],
                "expected_drop_off_rate": 0.12,
                "engagement_frequency_target": 45
            }
        }
        
        # Engagement element weights for timeline generation
        self.engagement_weights = {
            "question": 3.0,
            "emotional_word": 2.5,
            "call_to_action": 2.0,
            "personal_address": 1.5,
            "curiosity_gap": 3.5,
            "pattern_interrupt": 2.8,
            "visual_cue": 1.8,
            "story_element": 2.2
        }
    
    def generate_script_preview(self, script: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive script preview with engagement predictions and optimization suggestions
        
        Args:
            script: The script content to preview
            metadata: Additional context (platform, duration, etc.)
            
        Returns:
            Comprehensive preview with timeline, predictions, and suggestions
        """
        if not script or not script.strip():
            return self._get_empty_preview()
        
        try:
            metadata = metadata or {}
            platform = metadata.get('target_platform', 'youtube').lower()
            duration = metadata.get('duration', 'medium')
            content_type = metadata.get('content_type', 'general')
            
            # Generate core preview components
            engagement_timeline = self.create_engagement_curve(script, platform)
            retention_predictions = self.predict_drop_off_points(script, platform)
            optimization_suggestions = self.suggest_improvements(script, metadata)
            
            # Calculate overall preview scores
            preview_scores = self._calculate_preview_scores(
                engagement_timeline, retention_predictions, optimization_suggestions
            )
            
            # Generate detailed analysis
            detailed_analysis = self._generate_detailed_analysis(script, platform)
            
            # Create performance predictions
            performance_forecast = self._generate_performance_forecast(
                engagement_timeline, retention_predictions, metadata
            )
            
            # Generate actionable recommendations
            actionable_recommendations = self._generate_actionable_recommendations(
                optimization_suggestions, preview_scores, platform
            )
            
            return {
                "preview_id": f"preview_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "script_metadata": {
                    "platform": platform,
                    "duration": duration,
                    "content_type": content_type,
                    "word_count": len(script.split()),
                    "estimated_duration": len(script.split()) / 2,  # ~2 words per second
                    "character_count": len(script)
                },
                "engagement_timeline": engagement_timeline,
                "retention_predictions": retention_predictions,
                "optimization_suggestions": optimization_suggestions,
                "preview_scores": preview_scores,
                "detailed_analysis": detailed_analysis,
                "performance_forecast": performance_forecast,
                "actionable_recommendations": actionable_recommendations,
                "confidence_metrics": self._calculate_confidence_metrics(script, metadata)
            }
            
        except Exception as e:
            logger.error(f"Error generating script preview: {str(e)}")
            return self._get_error_preview(str(e))
    
    def create_engagement_curve(self, script: str, platform: str = "youtube") -> Dict[str, Any]:
        """Create detailed engagement timeline curve for the script"""
        try:
            words = script.split()
            if not words:
                return {"error": "No content to analyze"}
            
            platform_config = self.platform_configs.get(platform, self.platform_configs["youtube"])
            
            # Divide script into timeline segments
            segment_size = max(1, len(words) // self.preview_settings["timeline_segments"])
            segments = []
            
            for i in range(0, len(words), segment_size):
                segment_words = words[i:i+segment_size]
                segment_text = ' '.join(segment_words)
                segments.append({
                    "segment_id": len(segments),
                    "start_word": i,
                    "end_word": min(i + segment_size, len(words)),
                    "text": segment_text,
                    "duration_start": i / 2,  # ~2 words per second
                    "duration_end": min(i + segment_size, len(words)) / 2
                })
            
            # Calculate engagement score for each segment
            engagement_scores = []
            timeline_events = []
            
            for segment in segments:
                segment_score = self._calculate_segment_engagement(segment["text"])
                engagement_scores.append(segment_score)
                
                # Identify key engagement events
                events = self._identify_engagement_events(segment, segment_score)
                timeline_events.extend(events)
            
            # Smooth the engagement curve
            smoothed_scores = self._smooth_engagement_curve(engagement_scores)
            
            # Identify peaks and valleys
            peaks_valleys = self._identify_engagement_peaks_valleys(smoothed_scores)
            
            # Generate timeline summary
            timeline_summary = self._generate_timeline_summary(
                segments, smoothed_scores, timeline_events, platform_config
            )
            
            return {
                "timeline_type": "ENGAGEMENT_CURVE",
                "total_segments": len(segments),
                "segments": [{
                    "segment_id": seg["segment_id"],
                    "time_start": round(seg["duration_start"], 1),
                    "time_end": round(seg["duration_end"], 1),
                    "engagement_score": round(smoothed_scores[seg["segment_id"]], 2),
                    "key_elements": self._identify_segment_elements(seg["text"])
                } for seg in segments],
                "engagement_curve": [round(score, 2) for score in smoothed_scores],
                "peak_moments": peaks_valleys["peaks"],
                "valley_moments": peaks_valleys["valleys"],
                "timeline_events": timeline_events,
                "timeline_summary": timeline_summary,
                "overall_engagement_score": round(sum(smoothed_scores) / len(smoothed_scores), 2),
                "engagement_consistency": self._calculate_engagement_consistency(smoothed_scores)
            }
            
        except Exception as e:
            logger.error(f"Error creating engagement curve: {str(e)}")
            return {"error": str(e)}
    
    def predict_drop_off_points(self, script: str, platform: str = "youtube") -> Dict[str, Any]:
        """Predict where audience is likely to drop off during the script"""
        try:
            words = script.split()
            if not words:
                return {"error": "No content to analyze"}
            
            platform_config = self.platform_configs.get(platform, self.platform_configs["youtube"])
            
            # Calculate baseline retention curve
            baseline_retention = self._calculate_baseline_retention(len(words), platform_config)
            
            # Identify specific drop-off risks
            drop_off_risks = self._identify_drop_off_risks(script, platform_config)
            
            # Calculate adjusted retention predictions
            adjusted_retention = self._adjust_retention_for_risks(baseline_retention, drop_off_risks)
            
            # Identify critical retention points
            critical_points = self._identify_critical_retention_points(
                adjusted_retention, platform_config
            )
            
            # Generate retention improvement opportunities
            improvement_opportunities = self._identify_retention_improvements(
                drop_off_risks, critical_points
            )
            
            # Calculate retention confidence
            retention_confidence = self._calculate_retention_confidence(script, drop_off_risks)
            
            return {
                "prediction_type": "RETENTION_ANALYSIS",
                "platform": platform,
                "baseline_retention": baseline_retention,
                "predicted_retention": adjusted_retention,
                "drop_off_risks": drop_off_risks,
                "critical_points": critical_points,
                "improvement_opportunities": improvement_opportunities,
                "retention_summary": {
                    "overall_retention_rate": round(adjusted_retention[-1], 1),
                    "major_drop_points": len([risk for risk in drop_off_risks if risk["severity"] == "HIGH"]),
                    "retention_grade": self._get_retention_grade(adjusted_retention[-1]),
                    "confidence_level": round(retention_confidence, 2)
                },
                "retention_recommendations": self._generate_retention_recommendations(
                    drop_off_risks, critical_points
                )
            }
            
        except Exception as e:
            logger.error(f"Error predicting drop-off points: {str(e)}")
            return {"error": str(e)}
    
    def suggest_improvements(self, script: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive optimization suggestions for the script"""
        try:
            metadata = metadata or {}
            platform = metadata.get('target_platform', 'youtube').lower()
            
            # Analyze different aspects of the script
            hook_analysis = self._analyze_hook_optimization(script)
            structure_analysis = self._analyze_structure_optimization(script)
            engagement_analysis = self._analyze_engagement_optimization(script, platform)
            content_analysis = self._analyze_content_optimization(script)
            platform_analysis = self._analyze_platform_optimization(script, platform)
            
            # Prioritize suggestions
            prioritized_suggestions = self._prioritize_suggestions([
                *hook_analysis["suggestions"],
                *structure_analysis["suggestions"],
                *engagement_analysis["suggestions"],
                *content_analysis["suggestions"],
                *platform_analysis["suggestions"]
            ])
            
            # Generate quick wins
            quick_wins = self._identify_quick_wins(prioritized_suggestions)
            
            # Generate long-term improvements
            strategic_improvements = self._identify_strategic_improvements(prioritized_suggestions)
            
            # Calculate improvement impact
            improvement_impact = self._calculate_improvement_impact(prioritized_suggestions)
            
            return {
                "optimization_type": "COMPREHENSIVE_ANALYSIS",
                "total_suggestions": len(prioritized_suggestions),
                "analysis_breakdown": {
                    "hook_optimization": hook_analysis,
                    "structure_optimization": structure_analysis,
                    "engagement_optimization": engagement_analysis,
                    "content_optimization": content_analysis,
                    "platform_optimization": platform_analysis
                },
                "prioritized_suggestions": prioritized_suggestions,
                "quick_wins": quick_wins,
                "strategic_improvements": strategic_improvements,
                "improvement_impact": improvement_impact,
                "optimization_summary": {
                    "critical_issues": len([s for s in prioritized_suggestions if s["priority"] == "CRITICAL"]),
                    "high_priority_items": len([s for s in prioritized_suggestions if s["priority"] == "HIGH"]),
                    "expected_improvement": improvement_impact["total_impact"],
                    "implementation_difficulty": self._calculate_implementation_difficulty(prioritized_suggestions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error suggesting improvements: {str(e)}")
            return {"error": str(e)}
    
    # Engagement curve helper methods
    
    def _calculate_segment_engagement(self, segment_text: str) -> float:
        """Calculate engagement score for a text segment"""
        if not segment_text:
            return 0.0
        
        engagement_score = 0.0
        text_lower = segment_text.lower()
        
        # Questions increase engagement
        questions = segment_text.count('?')
        engagement_score += questions * self.engagement_weights["question"]
        
        # Emotional words
        emotional_words = [
            'amazing', 'incredible', 'shocking', 'surprising', 'fantastic',
            'terrible', 'devastating', 'exciting', 'thrilling', 'wonderful'
        ]
        for word in emotional_words:
            if word in text_lower:
                engagement_score += self.engagement_weights["emotional_word"]
        
        # Call-to-action words
        cta_words = ['subscribe', 'like', 'comment', 'share', 'click', 'follow']
        for word in cta_words:
            if word in text_lower:
                engagement_score += self.engagement_weights["call_to_action"]
        
        # Personal address
        personal_words = ['you', 'your', 'we', 'us', 'our']
        personal_count = sum(1 for word in personal_words if word in text_lower)
        engagement_score += min(3.0, personal_count * self.engagement_weights["personal_address"])
        
        # Curiosity gaps
        curiosity_words = ['secret', 'hidden', 'revealed', 'mystery', 'surprising']
        for word in curiosity_words:
            if word in text_lower:
                engagement_score += self.engagement_weights["curiosity_gap"]
        
        # Pattern interrupts
        interrupt_words = ['but', 'however', 'wait', 'stop', 'actually', 'surprisingly']
        for word in interrupt_words:
            if word in text_lower:
                engagement_score += self.engagement_weights["pattern_interrupt"]
        
        # Normalize by segment length
        word_count = len(segment_text.split())
        if word_count > 0:
            engagement_score = (engagement_score / word_count) * 20  # Scale factor
        
        return min(10.0, engagement_score)
    
    def _identify_engagement_events(self, segment: Dict[str, Any], engagement_score: float) -> List[Dict[str, Any]]:
        """Identify key engagement events in a segment"""
        events = []
        
        if engagement_score > 8.0:
            events.append({
                "type": "HIGH_ENGAGEMENT",
                "time": segment["duration_start"],
                "description": "Peak engagement moment",
                "score": engagement_score
            })
        elif engagement_score < 3.0:
            events.append({
                "type": "LOW_ENGAGEMENT",
                "time": segment["duration_start"],
                "description": "Potential drop-off risk",
                "score": engagement_score
            })
        
        # Check for specific elements
        if '?' in segment["text"]:
            events.append({
                "type": "AUDIENCE_QUESTION",
                "time": segment["duration_start"],
                "description": "Audience engagement question",
                "score": engagement_score
            })
        
        return events
    
    def _smooth_engagement_curve(self, scores: List[float]) -> List[float]:
        """Apply smoothing to engagement curve for better visualization"""
        if len(scores) < 3:
            return scores
        
        smoothed = []
        for i in range(len(scores)):
            if i == 0:
                smoothed.append((scores[i] + scores[i+1]) / 2)
            elif i == len(scores) - 1:
                smoothed.append((scores[i-1] + scores[i]) / 2)
            else:
                smoothed.append((scores[i-1] + scores[i] + scores[i+1]) / 3)
        
        return smoothed
    
    def _identify_engagement_peaks_valleys(self, scores: List[float]) -> Dict[str, List[Dict[str, Any]]]:
        """Identify peaks and valleys in engagement curve"""
        peaks = []
        valleys = []
        
        for i in range(1, len(scores) - 1):
            if scores[i] > scores[i-1] and scores[i] > scores[i+1] and scores[i] > 6.0:
                peaks.append({
                    "segment": i,
                    "score": round(scores[i], 2),
                    "type": "ENGAGEMENT_PEAK"
                })
            elif scores[i] < scores[i-1] and scores[i] < scores[i+1] and scores[i] < 4.0:
                valleys.append({
                    "segment": i,
                    "score": round(scores[i], 2),
                    "type": "ENGAGEMENT_VALLEY"
                })
        
        return {"peaks": peaks, "valleys": valleys}
    
    def _identify_segment_elements(self, segment_text: str) -> List[str]:
        """Identify key elements in a segment"""
        elements = []
        text_lower = segment_text.lower()
        
        if '?' in segment_text:
            elements.append("Question")
        if any(word in text_lower for word in ['you', 'your']):
            elements.append("Direct Address")
        if any(word in text_lower for word in ['amazing', 'incredible', 'shocking']):
            elements.append("Emotional Language")
        if any(word in text_lower for word in ['subscribe', 'like', 'share']):
            elements.append("Call-to-Action")
        if any(word in text_lower for word in ['secret', 'hidden', 'revealed']):
            elements.append("Curiosity Gap")
        
        return elements
    
    def _generate_timeline_summary(self, segments: List[Dict[str, Any]], scores: List[float], 
                                 events: List[Dict[str, Any]], platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of the engagement timeline"""
        return {
            "peak_engagement_time": round(scores.index(max(scores)) * (len(segments) / 10), 1),
            "lowest_engagement_time": round(scores.index(min(scores)) * (len(segments) / 10), 1),
            "engagement_consistency": round(1 - (max(scores) - min(scores)) / max(scores, 1), 2),
            "total_engagement_events": len(events),
            "recommended_improvements": self._get_timeline_improvements(scores, events)
        }
    
    def _calculate_engagement_consistency(self, scores: List[float]) -> float:
        """Calculate how consistent engagement is throughout the script"""
        if not scores:
            return 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        consistency = 1 - (math.sqrt(variance) / max(mean_score, 1))
        
        return max(0.0, min(1.0, consistency))
    
    # Retention prediction helper methods
    
    def _calculate_baseline_retention(self, word_count: int, platform_config: Dict[str, Any]) -> List[float]:
        """Calculate baseline retention curve for the platform"""
        duration = word_count / 2  # ~2 words per second
        drop_rate = platform_config["expected_drop_off_rate"]
        
        # Create retention curve
        time_points = []
        retention_values = []
        
        for i in range(11):  # 0% to 100% of content
            time_point = (duration * i) / 10
            retention = 100 * (1 - drop_rate) ** i
            time_points.append(time_point)
            retention_values.append(max(20, retention))  # Minimum 20% retention
        
        return retention_values
    
    def _identify_drop_off_risks(self, script: str, platform_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific drop-off risks in the script"""
        risks = []
        words = script.split()
        
        # Check for weak hook
        hook_text = ' '.join(words[:20])  # First 20 words
        if not any(word in hook_text.lower() for word in ['you', 'secret', 'amazing', 'how', 'why']):
            risks.append({
                "type": "WEAK_HOOK",
                "location": "0-10 seconds",
                "severity": "HIGH",
                "description": "Hook lacks engaging elements",
                "impact": -15  # 15% retention loss
            })
        
        # Check for long segments without engagement
        segment_size = max(1, len(words) // 10)
        for i in range(0, len(words), segment_size):
            segment = ' '.join(words[i:i+segment_size])
            if '?' not in segment and not any(word in segment.lower() for word in ['you', 'your']):
                risks.append({
                    "type": "LOW_ENGAGEMENT_SEGMENT",
                    "location": f"{i/2}-{(i+segment_size)/2} seconds",
                    "severity": "MEDIUM",
                    "description": "Segment lacks audience engagement",
                    "impact": -8
                })
        
        # Check for missing pattern interrupts
        interrupt_words = ['but', 'however', 'wait', 'actually', 'surprisingly']
        if not any(word in script.lower() for word in interrupt_words):
            risks.append({
                "type": "NO_PATTERN_INTERRUPTS",
                "location": "Throughout",
                "severity": "MEDIUM",
                "description": "No pattern interrupts to maintain attention",
                "impact": -10
            })
        
        return risks
    
    def _adjust_retention_for_risks(self, baseline: List[float], risks: List[Dict[str, Any]]) -> List[float]:
        """Adjust baseline retention based on identified risks"""
        adjusted = baseline.copy()
        
        for risk in risks:
            impact = abs(risk["impact"])
            # Apply impact across relevant time periods
            for i in range(len(adjusted)):
                adjusted[i] = max(10, adjusted[i] - (impact * (i / len(adjusted))))
        
        return adjusted
    
    def _identify_critical_retention_points(self, retention_curve: List[float], 
                                          platform_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical points where retention drops significantly"""
        critical_points = []
        critical_thresholds = platform_config["critical_retention_points"]
        
        for i, retention in enumerate(retention_curve):
            time_point = (len(retention_curve) * i) / 10
            if time_point in critical_thresholds and retention < 60:
                critical_points.append({
                    "time": time_point,
                    "retention_rate": round(retention, 1),
                    "severity": "HIGH" if retention < 40 else "MEDIUM",
                    "recommendation": f"Add engagement element at {time_point}s"
                })
        
        return critical_points
    
    def _identify_retention_improvements(self, risks: List[Dict[str, Any]], 
                                       critical_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify specific opportunities to improve retention"""
        improvements = []
        
        # From risks
        for risk in risks:
            if risk["severity"] == "HIGH":
                improvements.append({
                    "type": "RISK_MITIGATION",
                    "area": risk["type"],
                    "improvement": f"Address {risk['description'].lower()}",
                    "expected_impact": f"+{abs(risk['impact'])}% retention",
                    "priority": "HIGH"
                })
        
        # From critical points
        for point in critical_points:
            improvements.append({
                "type": "CRITICAL_POINT_ENHANCEMENT",
                "area": f"Time: {point['time']}s",
                "improvement": point["recommendation"],
                "expected_impact": "+5-10% retention",
                "priority": point["severity"]
            })
        
        return improvements
    
    def _calculate_retention_confidence(self, script: str, risks: List[Dict[str, Any]]) -> float:
        """Calculate confidence in retention predictions"""
        base_confidence = 75.0
        
        # Reduce confidence for each high-severity risk
        high_risks = len([r for r in risks if r["severity"] == "HIGH"])
        confidence = base_confidence - (high_risks * 15)
        
        # Increase confidence for script length (more data points)
        word_count = len(script.split())
        if word_count > 200:
            confidence += 10
        elif word_count < 50:
            confidence -= 20
        
        return max(30.0, min(95.0, confidence))
    
    def _get_retention_grade(self, final_retention: float) -> str:
        """Convert retention rate to letter grade"""
        if final_retention >= 80:
            return "A"
        elif final_retention >= 70:
            return "B"
        elif final_retention >= 60:
            return "C"
        elif final_retention >= 50:
            return "D"
        else:
            return "F"
    
    def _generate_retention_recommendations(self, risks: List[Dict[str, Any]], 
                                          critical_points: List[Dict[str, Any]]) -> List[str]:
        """Generate specific retention recommendations"""
        recommendations = []
        
        if any(r["type"] == "WEAK_HOOK" for r in risks):
            recommendations.append("Strengthen opening hook with curiosity gap or bold statement")
        
        if any(r["type"] == "LOW_ENGAGEMENT_SEGMENT" for r in risks):
            recommendations.append("Add more audience engagement throughout the script")
        
        if any(r["type"] == "NO_PATTERN_INTERRUPTS" for r in risks):
            recommendations.append("Include pattern interrupts like 'but', 'however', 'surprisingly'")
        
        if len(critical_points) > 2:
            recommendations.append("Add retention hooks at critical time points")
        
        return recommendations
    
    # Optimization suggestion helper methods
    
    def _analyze_hook_optimization(self, script: str) -> Dict[str, Any]:
        """Analyze hook optimization opportunities"""
        words = script.split()
        hook_text = ' '.join(words[:25]) if len(words) >= 25 else script
        
        suggestions = []
        hook_score = 5.0  # Base score
        
        # Check for curiosity elements
        curiosity_words = ['secret', 'hidden', 'revealed', 'mystery', 'surprising']
        if not any(word in hook_text.lower() for word in curiosity_words):
            suggestions.append({
                "type": "HOOK_IMPROVEMENT",
                "priority": "HIGH",
                "suggestion": "Add curiosity gap with words like 'secret', 'hidden', or 'revealed'",
                "expected_impact": "+15% engagement",
                "implementation": "EASY"
            })
        else:
            hook_score += 2.0
        
        # Check for questions
        if '?' not in hook_text:
            suggestions.append({
                "type": "HOOK_IMPROVEMENT",
                "priority": "MEDIUM",
                "suggestion": "Start with an engaging question to create curiosity",
                "expected_impact": "+10% engagement",
                "implementation": "EASY"
            })
        else:
            hook_score += 1.5
        
        # Check for emotional elements
        emotional_words = ['amazing', 'incredible', 'shocking', 'unbelievable']
        if not any(word in hook_text.lower() for word in emotional_words):
            suggestions.append({
                "type": "HOOK_IMPROVEMENT",
                "priority": "MEDIUM",
                "suggestion": "Add emotional language to increase impact",
                "expected_impact": "+8% engagement",
                "implementation": "EASY"
            })
        else:
            hook_score += 1.0
        
        return {
            "area": "HOOK_OPTIMIZATION",
            "current_score": min(10.0, hook_score),
            "suggestions": suggestions,
            "analysis_summary": f"Hook analyzed for curiosity, questions, and emotional elements"
        }
    
    def _analyze_structure_optimization(self, script: str) -> Dict[str, Any]:
        """Analyze script structure optimization opportunities"""
        suggestions = []
        structure_score = 5.0
        
        # Check for clear sections
        sentences = script.split('.')
        if len(sentences) < 3:
            suggestions.append({
                "type": "STRUCTURE_IMPROVEMENT",
                "priority": "HIGH",
                "suggestion": "Develop clearer structure with introduction, main content, and conclusion",
                "expected_impact": "+12% retention",
                "implementation": "MEDIUM"
            })
        else:
            structure_score += 2.0
        
        # Check for transitions
        transition_words = ['however', 'therefore', 'next', 'then', 'finally']
        if not any(word in script.lower() for word in transition_words):
            suggestions.append({
                "type": "STRUCTURE_IMPROVEMENT",
                "priority": "MEDIUM",
                "suggestion": "Add transition words to improve flow between ideas",
                "expected_impact": "+8% retention",
                "implementation": "EASY"
            })
        else:
            structure_score += 1.5
        
        return {
            "area": "STRUCTURE_OPTIMIZATION",
            "current_score": min(10.0, structure_score),
            "suggestions": suggestions,
            "analysis_summary": "Structure analyzed for clarity, transitions, and logical flow"
        }
    
    def _analyze_engagement_optimization(self, script: str, platform: str) -> Dict[str, Any]:
        """Analyze engagement optimization opportunities"""
        suggestions = []
        engagement_score = 5.0
        
        # Check question frequency
        questions = script.count('?')
        word_count = len(script.split())
        question_ratio = questions / max(1, word_count / 100)  # Questions per 100 words
        
        if question_ratio < 2:
            suggestions.append({
                "type": "ENGAGEMENT_IMPROVEMENT",
                "priority": "HIGH",
                "suggestion": "Add more rhetorical questions to increase audience engagement",
                "expected_impact": "+15% engagement",
                "implementation": "EASY"
            })
        else:
            engagement_score += 2.0
        
        # Check for call-to-action
        cta_words = ['subscribe', 'like', 'comment', 'share', 'follow']
        if not any(word in script.lower() for word in cta_words):
            suggestions.append({
                "type": "ENGAGEMENT_IMPROVEMENT",
                "priority": "MEDIUM",
                "suggestion": "Add clear call-to-action elements",
                "expected_impact": "+10% conversion",
                "implementation": "EASY"
            })
        else:
            engagement_score += 1.5
        
        return {
            "area": "ENGAGEMENT_OPTIMIZATION",
            "current_score": min(10.0, engagement_score),
            "suggestions": suggestions,
            "analysis_summary": "Engagement analyzed for questions, CTAs, and interaction elements"
        }
    
    def _analyze_content_optimization(self, script: str) -> Dict[str, Any]:
        """Analyze content optimization opportunities"""
        suggestions = []
        content_score = 5.0
        
        # Check readability
        readability = textstat.flesch_reading_ease(script)
        if readability < 60:
            suggestions.append({
                "type": "CONTENT_IMPROVEMENT",
                "priority": "MEDIUM",
                "suggestion": "Simplify language for better readability",
                "expected_impact": "+8% comprehension",
                "implementation": "MEDIUM"
            })
        else:
            content_score += 1.5
        
        # Check for storytelling elements
        story_words = ['story', 'happened', 'experience', 'remember', 'once']
        if any(word in script.lower() for word in story_words):
            content_score += 1.5
        else:
            suggestions.append({
                "type": "CONTENT_IMPROVEMENT",
                "priority": "LOW",
                "suggestion": "Add storytelling elements or personal experiences",
                "expected_impact": "+6% engagement",
                "implementation": "MEDIUM"
            })
        
        return {
            "area": "CONTENT_OPTIMIZATION",
            "current_score": min(10.0, content_score),
            "suggestions": suggestions,
            "analysis_summary": "Content analyzed for readability, storytelling, and clarity"
        }
    
    def _analyze_platform_optimization(self, script: str, platform: str) -> Dict[str, Any]:
        """Analyze platform-specific optimization opportunities"""
        suggestions = []
        platform_score = 5.0
        
        word_count = len(script.split())
        estimated_duration = word_count / 2
        
        # Platform-specific recommendations
        if platform == "tiktok":
            if estimated_duration > 60:
                suggestions.append({
                    "type": "PLATFORM_OPTIMIZATION",
                    "priority": "HIGH",
                    "suggestion": "Shorten content for TikTok's optimal length (30-60 seconds)",
                    "expected_impact": "+20% completion rate",
                    "implementation": "HARD"
                })
            else:
                platform_score += 2.0
        
        elif platform == "youtube":
            if estimated_duration < 60:
                suggestions.append({
                    "type": "PLATFORM_OPTIMIZATION",
                    "priority": "MEDIUM",
                    "suggestion": "Consider expanding content for better YouTube performance",
                    "expected_impact": "+10% watch time",
                    "implementation": "MEDIUM"
                })
            else:
                platform_score += 1.5
        
        # Check for platform-specific elements
        if platform == "youtube" and 'subscribe' not in script.lower():
            suggestions.append({
                "type": "PLATFORM_OPTIMIZATION",
                "priority": "MEDIUM",
                "suggestion": "Add YouTube-specific CTAs like 'subscribe' and 'notification bell'",
                "expected_impact": "+12% subscriber conversion",
                "implementation": "EASY"
            })
        
        return {
            "area": "PLATFORM_OPTIMIZATION",
            "current_score": min(10.0, platform_score),
            "suggestions": suggestions,
            "analysis_summary": f"Content optimized for {platform} best practices"
        }
    
    def _prioritize_suggestions(self, all_suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize suggestions by impact and implementation difficulty"""
        priority_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        implementation_weights = {"EASY": 3, "MEDIUM": 2, "HARD": 1}
        
        for suggestion in all_suggestions:
            priority_score = priority_weights.get(suggestion["priority"], 1)
            implementation_score = implementation_weights.get(suggestion["implementation"], 1)
            suggestion["prioritization_score"] = priority_score * implementation_score
        
        return sorted(all_suggestions, key=lambda x: x["prioritization_score"], reverse=True)
    
    def _identify_quick_wins(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify quick wins (easy implementation, high impact)"""
        return [
            suggestion for suggestion in suggestions
            if suggestion["implementation"] == "EASY" and suggestion["priority"] in ["HIGH", "CRITICAL"]
        ][:5]
    
    def _identify_strategic_improvements(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify strategic improvements (harder to implement but high impact)"""
        return [
            suggestion for suggestion in suggestions
            if suggestion["implementation"] in ["MEDIUM", "HARD"] and suggestion["priority"] in ["HIGH", "CRITICAL"]
        ][:5]
    
    def _calculate_improvement_impact(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total improvement impact"""
        impact_values = []
        for suggestion in suggestions:
            impact_str = suggestion.get("expected_impact", "+0%")
            try:
                impact_value = float(re.search(r'\+(\d+(?:\.\d+)?)%', impact_str).group(1))
                impact_values.append(impact_value)
            except (AttributeError, ValueError):
                impact_values.append(0)
        
        total_impact = sum(impact_values)
        return {
            "total_impact": f"+{total_impact:.1f}%",
            "high_impact_count": len([v for v in impact_values if v >= 10]),
            "medium_impact_count": len([v for v in impact_values if 5 <= v < 10]),
            "low_impact_count": len([v for v in impact_values if v < 5])
        }
    
    def _calculate_implementation_difficulty(self, suggestions: List[Dict[str, Any]]) -> str:
        """Calculate overall implementation difficulty"""
        difficulty_counts = Counter(s["implementation"] for s in suggestions)
        
        if difficulty_counts["HARD"] > difficulty_counts["EASY"] + difficulty_counts["MEDIUM"]:
            return "HIGH"
        elif difficulty_counts["EASY"] > difficulty_counts["MEDIUM"] + difficulty_counts["HARD"]:
            return "LOW"
        else:
            return "MEDIUM"
    
    # Main helper methods
    
    def _calculate_preview_scores(self, engagement_timeline: Dict[str, Any], 
                                retention_predictions: Dict[str, Any], 
                                optimization_suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall preview scores"""
        engagement_score = engagement_timeline.get("overall_engagement_score", 5.0)
        retention_rate = retention_predictions.get("retention_summary", {}).get("overall_retention_rate", 60.0)
        
        # Convert retention rate to 0-10 scale
        retention_score = retention_rate / 10.0
        
        # Count critical suggestions
        suggestions = optimization_suggestions.get("prioritized_suggestions", [])
        critical_issues = len([s for s in suggestions if s["priority"] == "CRITICAL"])
        
        overall_score = (engagement_score * 0.4 + retention_score * 0.4 + max(0, 10 - critical_issues * 2) * 0.2)
        
        return {
            "overall_preview_score": round(overall_score, 2),
            "engagement_score": round(engagement_score, 2),
            "retention_score": round(retention_score, 2),
            "optimization_score": round(max(0, 10 - critical_issues), 2),
            "preview_grade": self._get_preview_grade(overall_score),
            "score_breakdown": {
                "engagement_weight": "40%",
                "retention_weight": "40%",
                "optimization_weight": "20%"
            }
        }
    
    def _generate_detailed_analysis(self, script: str, platform: str) -> Dict[str, Any]:
        """Generate detailed script analysis"""
        word_count = len(script.split())
        char_count = len(script)
        sentence_count = len([s for s in script.split('.') if s.strip()])
        
        return {
            "script_metrics": {
                "word_count": word_count,
                "character_count": char_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": round(word_count / max(1, sentence_count), 1),
                "estimated_duration": round(word_count / 2, 1),
                "readability_score": round(textstat.flesch_reading_ease(script), 1)
            },
            "content_analysis": {
                "question_count": script.count('?'),
                "exclamation_count": script.count('!'),
                "personal_pronoun_count": len(re.findall(r'\b(you|your|we|us|our)\b', script, re.IGNORECASE)),
                "emotional_word_count": self._count_emotional_words(script)
            },
            "platform_compatibility": self._analyze_platform_compatibility(script, platform)
        }
    
    def _generate_performance_forecast(self, engagement_timeline: Dict[str, Any], 
                                     retention_predictions: Dict[str, Any], 
                                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance forecast based on analysis"""
        engagement_score = engagement_timeline.get("overall_engagement_score", 5.0)
        retention_rate = retention_predictions.get("retention_summary", {}).get("overall_retention_rate", 60.0)
        
        # Simple forecast model
        performance_forecast = {
            "expected_engagement_rate": round(engagement_score * 0.8, 1),
            "expected_retention_rate": round(retention_rate, 1),
            "expected_completion_rate": round(retention_rate * 0.9, 1),
            "viral_potential": "High" if engagement_score > 8 and retention_rate > 75 else 
                             "Medium" if engagement_score > 6 and retention_rate > 60 else "Low",
            "performance_confidence": round((engagement_score + retention_rate) / 2, 1)
        }
        
        return performance_forecast
    
    def _generate_actionable_recommendations(self, optimization_suggestions: Dict[str, Any], 
                                          preview_scores: Dict[str, Any], 
                                          platform: str) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # From optimization suggestions
        quick_wins = optimization_suggestions.get("quick_wins", [])
        for win in quick_wins[:3]:  # Top 3 quick wins
            recommendations.append(win["suggestion"])
        
        # From scores
        if preview_scores["engagement_score"] < 6:
            recommendations.append("Focus on increasing audience engagement with more interactive elements")
        
        if preview_scores["retention_score"] < 6:
            recommendations.append("Improve content pacing and add retention hooks throughout")
        
        # Platform-specific
        if platform == "tiktok":
            recommendations.append("Optimize for TikTok's fast-paced format with quick hooks")
        elif platform == "youtube":
            recommendations.append("Include YouTube-specific engagement prompts and subscribe CTAs")
        
        return recommendations[:8]  # Top 8 actionable recommendations
    
    def _calculate_confidence_metrics(self, script: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence metrics for the preview"""
        word_count = len(script.split())
        
        # Base confidence on content length and completeness
        base_confidence = 70.0
        
        if word_count > 100:
            base_confidence += 15
        elif word_count < 30:
            base_confidence -= 20
        
        # Platform-specific confidence
        platform = metadata.get('target_platform', 'youtube')
        if platform in self.platform_configs:
            base_confidence += 10
        
        return {
            "overall_confidence": round(base_confidence, 1),
            "engagement_prediction_confidence": round(base_confidence * 0.9, 1),
            "retention_prediction_confidence": round(base_confidence * 0.85, 1),
            "optimization_confidence": round(base_confidence * 0.95, 1),
            "confidence_factors": [
                f"Script length: {word_count} words",
                f"Platform: {platform}",
                "Analysis completeness: High"
            ]
        }
    
    # Utility methods
    
    def _get_timeline_improvements(self, scores: List[float], events: List[Dict[str, Any]]) -> List[str]:
        """Get timeline-specific improvements"""
        improvements = []
        
        if min(scores) < 3:
            improvements.append("Add engagement elements in low-scoring segments")
        if max(scores) - min(scores) > 6:
            improvements.append("Balance engagement throughout the script")
        if len(events) < 3:
            improvements.append("Include more engagement events for better timeline")
        
        return improvements
    
    def _count_emotional_words(self, script: str) -> int:
        """Count emotional words in script"""
        emotional_words = [
            'amazing', 'incredible', 'fantastic', 'wonderful', 'brilliant',
            'shocking', 'surprising', 'unbelievable', 'devastating', 'terrible',
            'exciting', 'thrilling', 'inspiring', 'motivating', 'powerful'
        ]
        
        script_lower = script.lower()
        return sum(1 for word in emotional_words if word in script_lower)
    
    def _analyze_platform_compatibility(self, script: str, platform: str) -> Dict[str, str]:
        """Analyze compatibility with platform requirements"""
        word_count = len(script.split())
        duration = word_count / 2
        
        compatibility = {"overall": "GOOD"}  # Default
        
        if platform == "tiktok":
            if duration > 60:
                compatibility["length"] = "TOO_LONG"
                compatibility["overall"] = "NEEDS_IMPROVEMENT"
            else:
                compatibility["length"] = "OPTIMAL"
        
        elif platform == "youtube":
            if duration < 30:
                compatibility["length"] = "TOO_SHORT"
                compatibility["overall"] = "NEEDS_IMPROVEMENT"
            else:
                compatibility["length"] = "GOOD"
        
        return compatibility
    
    def _get_preview_grade(self, score: float) -> str:
        """Convert preview score to letter grade"""
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
    
    def _get_empty_preview(self) -> Dict[str, Any]:
        """Return preview for empty script"""
        return {
            "error": "EMPTY_SCRIPT",
            "message": "No script content provided for preview generation",
            "recommendations": ["Provide script content to generate preview"]
        }
    
    def _get_error_preview(self, error_message: str) -> Dict[str, Any]:
        """Return preview for error case"""
        return {
            "error": "PREVIEW_GENERATION_ERROR",
            "message": error_message,
            "recommendations": ["Please try again with valid script content"]
        }
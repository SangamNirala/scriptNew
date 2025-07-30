"""
Phase 3: Advanced Context Engine
Multi-layered context enrichment with trend analysis, competitor insights, and performance prediction
"""

import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
from serpapi import GoogleSearch
import textstat
import re
from collections import Counter
import math

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Analyzes current trends and viral patterns for content optimization"""
    
    def __init__(self, serp_api_key: str):
        self.serp_api_key = serp_api_key
        self.trend_cache = {}
        self.cache_duration = 1800  # 30 minutes cache for trends
    
    async def analyze_trending_topics(self, industry: str, platform: str = "youtube") -> Dict[str, Any]:
        """Analyze trending topics for given industry and platform"""
        cache_key = f"trends_{industry}_{platform}"
        
        if self._is_cached(cache_key):
            return self.trend_cache[cache_key]['data']
        
        try:
            # Get trending searches
            trending_data = await self._fetch_trending_searches(industry, platform)
            
            # Analyze viral patterns
            viral_patterns = await self._analyze_viral_patterns(trending_data)
            
            # Get seasonal relevance
            seasonal_context = await self._get_seasonal_context()
            
            result = {
                "trending_keywords": trending_data.get("keywords", []),
                "viral_patterns": viral_patterns,
                "seasonal_context": seasonal_context,
                "trend_score": self._calculate_trend_score(trending_data, viral_patterns),
                "recommended_angles": self._generate_trend_angles(trending_data, industry)
            }
            
            # Cache results
            self.trend_cache[cache_key] = {
                'data': result,
                'timestamp': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return self._get_fallback_trends(industry)
    
    async def _fetch_trending_searches(self, industry: str, platform: str) -> Dict[str, Any]:
        """Fetch trending searches using SERP API"""
        try:
            search_params = {
                "engine": "google_trends",
                "q": industry,
                "api_key": self.serp_api_key,
                "data_type": "TIMESERIES",
                "date": "today 7-d"  # Last 7 days
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            keywords = []
            if "interest_over_time" in results:
                for entry in results["interest_over_time"]["timeline_data"][:10]:
                    if entry.get("values"):
                        keywords.extend([kw.get("query", "") for kw in entry["values"][:5]])
            
            return {
                "keywords": list(set(keywords))[:15],  # Top 15 unique keywords
                "platform_data": results.get("related_queries", {})
            }
            
        except Exception as e:
            logger.error(f"Error fetching trending searches: {str(e)}")
            return {"keywords": [], "platform_data": {}}
    
    async def _analyze_viral_patterns(self, trending_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns that make content go viral"""
        keywords = trending_data.get("keywords", [])
        
        # Analyze keyword patterns
        word_frequency = Counter()
        emotional_words = []
        action_words = []
        
        emotional_indicators = ["amazing", "shocking", "incredible", "secret", "hidden", "revealed", "mind-blowing", "unbelievable"]
        action_indicators = ["how to", "tutorial", "guide", "tips", "tricks", "hacks", "steps", "ways"]
        
        for keyword in keywords:
            words = keyword.lower().split()
            word_frequency.update(words)
            
            for word in words:
                if any(emotion in word for emotion in emotional_indicators):
                    emotional_words.append(word)
                if any(action in keyword.lower() for action in action_indicators):
                    action_words.append(keyword)
        
        return {
            "common_patterns": dict(word_frequency.most_common(10)),
            "emotional_triggers": list(set(emotional_words)),
            "action_oriented": list(set(action_words)),
            "viral_score": len(emotional_words) * 2 + len(action_words) * 1.5
        }
    
    async def _get_seasonal_context(self) -> Dict[str, Any]:
        """Get current seasonal and cultural context"""
        now = datetime.utcnow()
        month = now.month
        
        seasonal_contexts = {
            1: {"season": "New Year", "themes": ["resolutions", "fresh start", "goals"], "mood": "optimistic"},
            2: {"season": "Winter", "themes": ["Valentine's", "love", "relationships"], "mood": "romantic"},
            3: {"season": "Spring", "themes": ["growth", "renewal", "motivation"], "mood": "energetic"},
            4: {"season": "Spring", "themes": ["Easter", "rebirth", "family"], "mood": "hopeful"},
            5: {"season": "Spring", "themes": ["Mother's Day", "graduation", "achievements"], "mood": "celebratory"},
            6: {"season": "Summer", "themes": ["Father's Day", "vacation", "freedom"], "mood": "relaxed"},
            7: {"season": "Summer", "themes": ["independence", "adventure", "outdoors"], "mood": "adventurous"},
            8: {"season": "Summer", "themes": ["back to school", "preparation", "learning"], "mood": "focused"},
            9: {"season": "Fall", "themes": ["harvest", "productivity", "organization"], "mood": "determined"},
            10: {"season": "Fall", "themes": ["Halloween", "transformation", "mystery"], "mood": "mysterious"},
            11: {"season": "Fall", "themes": ["Thanksgiving", "gratitude", "family"], "mood": "grateful"},
            12: {"season": "Winter", "themes": ["Christmas", "giving", "reflection"], "mood": "nostalgic"}
        }
        
        return seasonal_contexts.get(month, seasonal_contexts[1])
    
    def _calculate_trend_score(self, trending_data: Dict[str, Any], viral_patterns: Dict[str, Any]) -> float:
        """Calculate overall trend relevance score"""
        keyword_count = len(trending_data.get("keywords", []))
        viral_score = viral_patterns.get("viral_score", 0)
        
        return min(10.0, (keyword_count * 0.3) + (viral_score * 0.7))
    
    def _generate_trend_angles(self, trending_data: Dict[str, Any], industry: str) -> List[str]:
        """Generate trending angles for content"""
        keywords = trending_data.get("keywords", [])
        angles = []
        
        if keywords:
            angles.extend([
                f"Why {keywords[0]} is trending in {industry}",
                f"The secret behind {keywords[0]} success",
                f"How to use {keywords[0]} for {industry}",
                f"What {keywords[0]} means for {industry} in 2025"
            ])
        
        return angles[:5]
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.trend_cache:
            return False
        
        cache_time = self.trend_cache[cache_key]['timestamp']
        return (datetime.utcnow() - cache_time).seconds < self.cache_duration
    
    def _get_fallback_trends(self, industry: str) -> Dict[str, Any]:
        """Fallback trends when API fails"""
        return {
            "trending_keywords": [f"{industry} tips", f"{industry} 2025", f"best {industry}"],
            "viral_patterns": {"common_patterns": {}, "emotional_triggers": [], "action_oriented": [], "viral_score": 5.0},
            "seasonal_context": {"season": "Current", "themes": ["trending", "popular"], "mood": "engaging"},
            "trend_score": 5.0,
            "recommended_angles": [f"Latest {industry} trends", f"Why {industry} matters now"]
        }


class CompetitorAnalyzer:
    """Analyzes competitor content and identifies successful patterns"""
    
    def __init__(self, serp_api_key: str):
        self.serp_api_key = serp_api_key
        self.competitor_cache = {}
        self.cache_duration = 3600  # 1 hour cache
    
    async def analyze_competitor_landscape(self, topic: str, platform: str = "youtube") -> Dict[str, Any]:
        """Analyze competitor content for given topic and platform"""
        cache_key = f"competitors_{topic}_{platform}"
        
        if self._is_cached(cache_key):
            return self.competitor_cache[cache_key]['data']
        
        try:
            # Fetch top performing content
            competitor_content = await self._fetch_top_content(topic, platform)
            
            # Analyze content patterns
            content_patterns = await self._analyze_content_patterns(competitor_content)
            
            # Identify gaps and opportunities
            opportunities = await self._identify_opportunities(competitor_content, content_patterns)
            
            result = {
                "top_performers": competitor_content,
                "content_patterns": content_patterns,
                "opportunities": opportunities,
                "competitive_score": self._calculate_competitive_score(competitor_content),
                "differentiation_strategies": self._generate_differentiation_strategies(content_patterns)
            }
            
            # Cache results
            self.competitor_cache[cache_key] = {
                'data': result,
                'timestamp': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing competitors: {str(e)}")
            return self._get_fallback_analysis(topic)
    
    async def _fetch_top_content(self, topic: str, platform: str) -> List[Dict[str, Any]]:
        """Fetch top performing content using SERP API"""
        try:
            if platform == "youtube":
                search_params = {
                    "engine": "youtube",
                    "search_query": topic,
                    "api_key": self.serp_api_key
                }
            else:
                search_params = {
                    "engine": "google",
                    "q": f"{topic} {platform}",
                    "api_key": self.serp_api_key,
                    "num": 10
                }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            content = []
            if platform == "youtube" and "video_results" in results:
                for video in results["video_results"][:10]:
                    content.append({
                        "title": video.get("title", ""),
                        "views": video.get("views", 0),
                        "duration": video.get("length", ""),
                        "channel": video.get("channel", ""),
                        "url": video.get("link", "")
                    })
            elif "organic_results" in results:
                for result in results["organic_results"][:10]:
                    content.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "source": result.get("source", "")
                    })
            
            return content
            
        except Exception as e:
            logger.error(f"Error fetching top content: {str(e)}")
            return []
    
    async def _analyze_content_patterns(self, content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in competitor content"""
        if not content:
            return {}
        
        titles = [item.get("title", "") for item in content]
        
        # Analyze title patterns
        title_words = []
        title_lengths = []
        common_phrases = []
        
        for title in titles:
            if title:
                words = title.lower().split()
                title_words.extend(words)
                title_lengths.append(len(title))
                
                # Extract common phrases (2-3 words)
                for i in range(len(words) - 1):
                    if len(words[i]) > 2 and len(words[i+1]) > 2:
                        common_phrases.append(f"{words[i]} {words[i+1]}")
        
        word_frequency = Counter(title_words)
        phrase_frequency = Counter(common_phrases)
        
        return {
            "common_words": dict(word_frequency.most_common(10)),
            "common_phrases": dict(phrase_frequency.most_common(8)),
            "avg_title_length": sum(title_lengths) / len(title_lengths) if title_lengths else 0,
            "title_patterns": self._identify_title_patterns(titles),
            "engagement_indicators": self._find_engagement_indicators(titles)
        }
    
    def _identify_title_patterns(self, titles: List[str]) -> List[str]:
        """Identify common title patterns"""
        patterns = []
        
        pattern_indicators = {
            "how_to": ["how to", "how i", "tutorial"],
            "listicle": ["top", "best", "ways", "tips", "secrets"],
            "question": ["why", "what", "when", "where", "which"],
            "urgency": ["now", "today", "immediate", "quick"],
            "curiosity": ["secret", "hidden", "revealed", "truth", "exposed"]
        }
        
        for pattern_name, indicators in pattern_indicators.items():
            count = sum(1 for title in titles if any(indicator in title.lower() for indicator in indicators))
            if count > 0:
                patterns.append(f"{pattern_name}: {count}/{len(titles)} titles")
        
        return patterns
    
    def _find_engagement_indicators(self, titles: List[str]) -> List[str]:
        """Find elements that drive engagement"""
        engagement_words = ["amazing", "shocking", "incredible", "must", "should", "never", "always", "secret", "hack"]
        
        indicators = []
        for word in engagement_words:
            count = sum(1 for title in titles if word.lower() in title.lower())
            if count > 0:
                indicators.append(f"{word}: appears in {count} titles")
        
        return indicators
    
    async def _identify_opportunities(self, content: List[Dict[str, Any]], patterns: Dict[str, Any]) -> List[str]:
        """Identify content gaps and opportunities"""
        opportunities = []
        
        if not content:
            return ["Create foundational content in this niche", "Be the first to cover trending topics"]
        
        # Check for content gaps
        common_words = patterns.get("common_words", {})
        if len(common_words) < 5:
            opportunities.append("Low competition - opportunity to establish authority")
        
        # Check for trending angles not covered
        opportunities.extend([
            "Create contrarian viewpoint content",
            "Develop beginner-friendly versions of expert content",
            "Add personal stories to technical topics",
            "Create comparison/review content",
            "Develop series or multi-part content"
        ])
        
        return opportunities[:5]
    
    def _calculate_competitive_score(self, content: List[Dict[str, Any]]) -> float:
        """Calculate competitive landscape score"""
        if not content:
            return 1.0  # Low competition
        
        # Higher number of results = higher competition
        competition_factor = min(10.0, len(content) * 0.8)
        return competition_factor
    
    def _generate_differentiation_strategies(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate strategies to differentiate from competitors"""
        strategies = [
            "Use unique personal experiences and case studies",
            "Create interactive or participatory content",
            "Focus on underserved audience segments",
            "Combine multiple topics for unique angles",
            "Use different content formats (visual, audio, text)"
        ]
        
        common_phrases = patterns.get("common_phrases", {})
        if common_phrases:
            most_common = list(common_phrases.keys())[0]
            strategies.append(f"Avoid overused phrase '{most_common}' - find fresh alternatives")
        
        return strategies[:5]
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.competitor_cache:
            return False
        
        cache_time = self.competitor_cache[cache_key]['timestamp']
        return (datetime.utcnow() - cache_time).seconds < self.cache_duration
    
    def _get_fallback_analysis(self, topic: str) -> Dict[str, Any]:
        """Fallback analysis when API fails"""
        return {
            "top_performers": [],
            "content_patterns": {"common_words": {}, "common_phrases": {}},
            "opportunities": ["Create original content", "Focus on unique perspective"],
            "competitive_score": 5.0,
            "differentiation_strategies": ["Add personal touch", "Use storytelling", "Focus on audience needs"]
        }


class PerformancePredictor:
    """Predicts content performance based on historical data and current trends"""
    
    def __init__(self):
        self.prediction_cache = {}
        self.cache_duration = 1800  # 30 minutes
    
    async def predict_performance(self, script_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance metrics for given script content"""
        cache_key = f"prediction_{hash(script_content)}"
        
        if self._is_cached(cache_key):
            return self.prediction_cache[cache_key]['data']
        
        try:
            # Analyze content characteristics
            content_analysis = await self._analyze_content_characteristics(script_content)
            
            # Calculate engagement predictions
            engagement_prediction = await self._predict_engagement(content_analysis, metadata)
            
            # Predict retention metrics
            retention_prediction = await self._predict_retention(content_analysis, metadata)
            
            # Calculate viral potential
            viral_potential = await self._calculate_viral_potential(content_analysis, engagement_prediction)
            
            result = {
                "content_analysis": content_analysis,
                "engagement_prediction": engagement_prediction,
                "retention_prediction": retention_prediction,
                "viral_potential": viral_potential,
                "overall_score": self._calculate_overall_score(engagement_prediction, retention_prediction, viral_potential),
                "optimization_recommendations": self._generate_optimization_recommendations(content_analysis)
            }
            
            # Cache results
            self.prediction_cache[cache_key] = {
                'data': result,
                'timestamp': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting performance: {str(e)}")
            return self._get_fallback_prediction()
    
    async def _analyze_content_characteristics(self, script: str) -> Dict[str, Any]:
        """Analyze key characteristics of the script content"""
        if not script:
            return {}
        
        # Basic metrics
        word_count = len(script.split())
        sentence_count = len([s for s in script.split('.') if s.strip()])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability
        readability_score = textstat.flesch_reading_ease(script)
        
        # Emotional analysis
        emotional_score = self._calculate_emotional_score(script)
        
        # Engagement elements
        engagement_elements = self._count_engagement_elements(script)
        
        # Hook strength (first 50 words)
        hook_text = ' '.join(script.split()[:50])
        hook_strength = self._analyze_hook_strength(hook_text)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "readability_score": readability_score,
            "emotional_score": emotional_score,
            "engagement_elements": engagement_elements,
            "hook_strength": hook_strength,
            "content_density": word_count / max(1, sentence_count)
        }
    
    def _calculate_emotional_score(self, script: str) -> float:
        """Calculate emotional engagement score"""
        emotional_words = [
            'amazing', 'incredible', 'shocking', 'surprising', 'unbelievable',
            'exciting', 'thrilling', 'fantastic', 'wonderful', 'brilliant',
            'devastating', 'heartbreaking', 'inspiring', 'motivating', 'powerful'
        ]
        
        script_lower = script.lower()
        emotional_count = sum(1 for word in emotional_words if word in script_lower)
        total_words = len(script.split())
        
        return min(10.0, (emotional_count / max(1, total_words)) * 100)
    
    def _count_engagement_elements(self, script: str) -> Dict[str, int]:
        """Count various engagement elements in the script"""
        return {
            "questions": script.count('?'),
            "exclamations": script.count('!'),
            "calls_to_action": len(re.findall(r'\b(subscribe|like|comment|share|follow)\b', script, re.IGNORECASE)),
            "personal_pronouns": len(re.findall(r'\b(you|your|we|us|our)\b', script, re.IGNORECASE)),
            "action_verbs": len(re.findall(r'\b(discover|learn|find|get|create|build|achieve)\b', script, re.IGNORECASE))
        }
    
    def _analyze_hook_strength(self, hook_text: str) -> float:
        """Analyze the strength of the opening hook"""
        if not hook_text:
            return 0.0
        
        hook_indicators = [
            'imagine', 'what if', 'did you know', 'here\'s why', 'secret',
            'mistake', 'truth', 'revealed', 'shocking', 'never'
        ]
        
        hook_lower = hook_text.lower()
        hook_count = sum(1 for indicator in hook_indicators if indicator in hook_lower)
        
        # Factor in questions and emotional words
        question_bonus = 2.0 if '?' in hook_text else 0.0
        emotional_bonus = self._calculate_emotional_score(hook_text) * 0.5
        
        return min(10.0, hook_count * 2.0 + question_bonus + emotional_bonus)
    
    async def _predict_engagement(self, content_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Predict engagement metrics"""
        base_engagement = 5.0  # Base score
        
        # Factors that increase engagement
        hook_bonus = content_analysis.get("hook_strength", 0) * 0.3
        emotional_bonus = content_analysis.get("emotional_score", 0) * 0.2
        engagement_elements = content_analysis.get("engagement_elements", {})
        interaction_bonus = (engagement_elements.get("questions", 0) * 0.5 + 
                           engagement_elements.get("calls_to_action", 0) * 0.3)
        
        # Platform-specific adjustments
        platform = metadata.get("platform", "general").lower()
        platform_multiplier = {
            "tiktok": 1.2,
            "youtube": 1.0,
            "instagram": 1.1,
            "linkedin": 0.9
        }.get(platform, 1.0)
        
        predicted_engagement = (base_engagement + hook_bonus + emotional_bonus + interaction_bonus) * platform_multiplier
        
        return {
            "predicted_likes_rate": min(15.0, predicted_engagement * 0.8),
            "predicted_comments_rate": min(5.0, predicted_engagement * 0.3),
            "predicted_shares_rate": min(3.0, predicted_engagement * 0.2),
            "overall_engagement_score": min(10.0, predicted_engagement),
            "confidence_level": self._calculate_confidence(content_analysis)
        }
    
    async def _predict_retention(self, content_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Predict audience retention metrics"""
        word_count = content_analysis.get("word_count", 0)
        hook_strength = content_analysis.get("hook_strength", 0)
        content_density = content_analysis.get("content_density", 0)
        
        # Retention decreases with length but improves with hook strength
        length_penalty = max(0, (word_count - 200) * 0.01)
        hook_bonus = hook_strength * 0.05
        density_factor = min(1.0, content_density / 10.0) * 0.1
        
        base_retention = 70.0  # 70% base retention
        predicted_retention = max(30.0, base_retention - length_penalty + hook_bonus + density_factor)
        
        return {
            "predicted_retention_rate": min(95.0, predicted_retention),
            "estimated_drop_off_points": self._estimate_drop_off_points(word_count),
            "retention_optimization_score": min(10.0, predicted_retention / 10.0)
        }
    
    def _estimate_drop_off_points(self, word_count: int) -> List[Dict[str, Any]]:
        """Estimate where audience might drop off"""
        if word_count < 100:
            return []
        
        # Typical drop-off points based on content length
        drop_points = []
        if word_count > 150:
            drop_points.append({"position": "25%", "reason": "Initial interest waning"})
        if word_count > 300:
            drop_points.append({"position": "50%", "reason": "Mid-content attention dip"})
        if word_count > 500:
            drop_points.append({"position": "75%", "reason": "Content fatigue"})
        
        return drop_points
    
    async def _calculate_viral_potential(self, content_analysis: Dict[str, Any], engagement_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate viral potential score"""
        hook_strength = content_analysis.get("hook_strength", 0)
        emotional_score = content_analysis.get("emotional_score", 0)
        engagement_score = engagement_prediction.get("overall_engagement_score", 0)
        
        # Viral factors
        shareability = min(10.0, (emotional_score * 0.4) + (hook_strength * 0.3) + (engagement_score * 0.3))
        
        return {
            "viral_probability": min(25.0, shareability * 2.5),  # Max 25% viral probability
            "shareability_score": shareability,
            "viral_factors": self._identify_viral_factors(content_analysis),
            "viral_optimization_tips": self._generate_viral_tips(content_analysis)
        }
    
    def _identify_viral_factors(self, content_analysis: Dict[str, Any]) -> List[str]:
        """Identify factors that contribute to viral potential"""
        factors = []
        
        if content_analysis.get("hook_strength", 0) > 7:
            factors.append("Strong opening hook")
        if content_analysis.get("emotional_score", 0) > 6:
            factors.append("High emotional engagement")
        
        engagement_elements = content_analysis.get("engagement_elements", {})
        if engagement_elements.get("questions", 0) > 2:
            factors.append("Interactive questioning")
        if engagement_elements.get("calls_to_action", 0) > 1:
            factors.append("Clear calls to action")
        
        return factors
    
    def _generate_viral_tips(self, content_analysis: Dict[str, Any]) -> List[str]:
        """Generate tips to increase viral potential"""
        tips = []
        
        if content_analysis.get("hook_strength", 0) < 6:
            tips.append("Strengthen opening hook with curiosity gap or shocking statement")
        if content_analysis.get("emotional_score", 0) < 5:
            tips.append("Add more emotional language and personal stories")
        
        engagement_elements = content_analysis.get("engagement_elements", {})
        if engagement_elements.get("questions", 0) < 2:
            tips.append("Include more rhetorical questions to engage audience")
        if engagement_elements.get("calls_to_action", 0) < 1:
            tips.append("Add clear calls to action for sharing and engagement")
        
        return tips[:3]  # Top 3 tips
    
    def _calculate_overall_score(self, engagement: Dict[str, Any], retention: Dict[str, Any], viral: Dict[str, Any]) -> float:
        """Calculate overall performance prediction score"""
        engagement_score = engagement.get("overall_engagement_score", 0) * 0.4
        retention_score = retention.get("retention_optimization_score", 0) * 0.4
        viral_score = viral.get("shareability_score", 0) * 0.2
        
        return min(10.0, engagement_score + retention_score + viral_score)
    
    def _generate_optimization_recommendations(self, content_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific optimization recommendations"""
        recommendations = []
        
        word_count = content_analysis.get("word_count", 0)
        if word_count < 50:
            recommendations.append("Expand content - too short for meaningful engagement")
        elif word_count > 500:
            recommendations.append("Consider shortening - long content may lose audience")
        
        if content_analysis.get("hook_strength", 0) < 5:
            recommendations.append("Improve opening hook - start with question, statistic, or bold statement")
        
        if content_analysis.get("readability_score", 0) < 60:
            recommendations.append("Simplify language for better readability")
        
        return recommendations[:5]
    
    def _calculate_confidence(self, content_analysis: Dict[str, Any]) -> float:
        """Calculate confidence level in predictions"""
        # More data points = higher confidence
        data_completeness = len([v for v in content_analysis.values() if v is not None and v != 0]) / 8.0
        return min(100.0, data_completeness * 85.0 + 15.0)  # 15-100% confidence range
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.prediction_cache:
            return False
        
        cache_time = self.prediction_cache[cache_key]['timestamp']
        return (datetime.utcnow() - cache_time).seconds < self.cache_duration
    
    def _get_fallback_prediction(self) -> Dict[str, Any]:
        """Fallback prediction when analysis fails"""
        return {
            "content_analysis": {},
            "engagement_prediction": {"overall_engagement_score": 5.0, "confidence_level": 50.0},
            "retention_prediction": {"predicted_retention_rate": 60.0},
            "viral_potential": {"viral_probability": 5.0, "shareability_score": 5.0},
            "overall_score": 5.0,
            "optimization_recommendations": ["Optimize content structure", "Improve engagement elements"]
        }


class AdvancedContextEngine:
    """Main engine that orchestrates all context analysis components"""
    
    def __init__(self):
        serp_api_key = os.environ.get('SERP_API_KEY')
        
        self.trend_analyzer = TrendAnalyzer(serp_api_key) if serp_api_key else None
        self.competitor_analyzer = CompetitorAnalyzer(serp_api_key) if serp_api_key else None
        self.performance_predictor = PerformancePredictor()
    
    async def enrich_prompt_context(self, base_prompt: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Multi-layered context enrichment for prompt optimization"""
        try:
            industry = metadata.get('industry_focus', 'general')
            platform = metadata.get('target_platform', 'youtube')
            
            # Parallel execution of all analysis components
            tasks = []
            
            if self.trend_analyzer:
                tasks.append(self.trend_analyzer.analyze_trending_topics(industry, platform))
            else:
                tasks.append(asyncio.create_task(self._get_fallback_trends(industry)))
            
            if self.competitor_analyzer:
                tasks.append(self.competitor_analyzer.analyze_competitor_landscape(base_prompt, platform))
            else:
                tasks.append(asyncio.create_task(self._get_fallback_competitors(base_prompt)))
            
            tasks.append(self.performance_predictor.predict_performance(base_prompt, metadata))
            
            # Execute all tasks concurrently
            trend_analysis, competitor_analysis, performance_prediction = await asyncio.gather(*tasks)
            
            # Synthesize all insights
            enriched_context = {
                "trend_insights": trend_analysis,
                "competitive_landscape": competitor_analysis,
                "performance_prediction": performance_prediction,
                "context_synthesis": self._synthesize_insights(trend_analysis, competitor_analysis, performance_prediction),
                "enhancement_recommendations": self._generate_enhancement_recommendations(
                    trend_analysis, competitor_analysis, performance_prediction, metadata
                )
            }
            
            return enriched_context
            
        except Exception as e:
            logger.error(f"Error in context enrichment: {str(e)}")
            return self._get_fallback_context()
    
    def _synthesize_insights(self, trends: Dict[str, Any], competitors: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from all analysis components"""
        return {
            "key_opportunities": self._identify_key_opportunities(trends, competitors),
            "risk_factors": self._identify_risk_factors(competitors, predictions),
            "success_probability": self._calculate_success_probability(trends, competitors, predictions),
            "recommended_strategy": self._recommend_strategy(trends, competitors, predictions)
        }
    
    def _identify_key_opportunities(self, trends: Dict[str, Any], competitors: Dict[str, Any]) -> List[str]:
        """Identify key opportunities based on trends and competition"""
        opportunities = []
        
        # From trends
        if trends.get("trend_score", 0) > 7:
            opportunities.append("High trending topic - capitalize on current interest")
        
        trending_keywords = trends.get("trending_keywords", [])
        if trending_keywords:
            opportunities.append(f"Leverage trending keyword: {trending_keywords[0]}")
        
        # From competitor analysis
        competitor_score = competitors.get("competitive_score", 5)
        if competitor_score < 5:
            opportunities.append("Low competition - opportunity to establish authority")
        
        comp_opportunities = competitors.get("opportunities", [])
        opportunities.extend(comp_opportunities[:2])
        
        return opportunities[:5]
    
    def _identify_risk_factors(self, competitors: Dict[str, Any], predictions: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Competition risks
        competitive_score = competitors.get("competitive_score", 5)
        if competitive_score > 8:
            risks.append("High competition - need strong differentiation")
        
        # Performance risks
        predicted_retention = predictions.get("retention_prediction", {}).get("predicted_retention_rate", 60)
        if predicted_retention < 50:
            risks.append("Low predicted retention - strengthen hook and pacing")
        
        engagement_score = predictions.get("engagement_prediction", {}).get("overall_engagement_score", 5)
        if engagement_score < 4:
            risks.append("Low engagement prediction - add interactive elements")
        
        return risks[:3]
    
    def _calculate_success_probability(self, trends: Dict[str, Any], competitors: Dict[str, Any], predictions: Dict[str, Any]) -> float:
        """Calculate overall success probability"""
        trend_factor = min(10, trends.get("trend_score", 5)) * 0.3
        competition_factor = (10 - min(10, competitors.get("competitive_score", 5))) * 0.3
        prediction_factor = predictions.get("overall_score", 5) * 0.4
        
        return min(100.0, (trend_factor + competition_factor + prediction_factor) * 10)
    
    def _recommend_strategy(self, trends: Dict[str, Any], competitors: Dict[str, Any], predictions: Dict[str, Any]) -> str:
        """Recommend overall content strategy"""
        trend_score = trends.get("trend_score", 5)
        competitive_score = competitors.get("competitive_score", 5)
        performance_score = predictions.get("overall_score", 5)
        
        if trend_score > 7 and competitive_score < 6:
            return "Trend Surfing Strategy: Capitalize on high trending topics with low competition"
        elif competitive_score > 8:
            return "Differentiation Strategy: Focus on unique angles and underserved niches"
        elif performance_score > 7:
            return "Quality Focus Strategy: Leverage strong content fundamentals for organic growth"
        else:
            return "Foundation Building Strategy: Establish authority through consistent, valuable content"
    
    def _generate_enhancement_recommendations(self, trends: Dict[str, Any], competitors: Dict[str, Any], 
                                           predictions: Dict[str, Any], metadata: Dict[str, Any]) -> List[str]:
        """Generate specific enhancement recommendations"""
        recommendations = []
        
        # Trend-based recommendations
        trending_keywords = trends.get("trending_keywords", [])
        if trending_keywords:
            recommendations.append(f"Incorporate trending keyword: '{trending_keywords[0]}'")
        
        seasonal_context = trends.get("seasonal_context", {})
        if seasonal_context.get("themes"):
            theme = seasonal_context["themes"][0]
            recommendations.append(f"Align with seasonal theme: {theme}")
        
        # Competitor-based recommendations
        differentiation_strategies = competitors.get("differentiation_strategies", [])
        if differentiation_strategies:
            recommendations.append(differentiation_strategies[0])
        
        # Performance-based recommendations
        optimization_recs = predictions.get("optimization_recommendations", [])
        recommendations.extend(optimization_recs[:2])
        
        return recommendations[:5]
    
    async def _get_fallback_trends(self, industry: str) -> Dict[str, Any]:
        """Fallback trends when API is not available"""
        return {
            "trending_keywords": [f"{industry} tips", f"{industry} 2025"],
            "trend_score": 5.0,
            "seasonal_context": {"themes": ["trending"], "mood": "engaging"}
        }
    
    async def _get_fallback_competitors(self, topic: str) -> Dict[str, Any]:
        """Fallback competitor analysis when API is not available"""
        return {
            "competitive_score": 5.0,
            "opportunities": ["Create unique perspective", "Focus on storytelling"],
            "differentiation_strategies": ["Add personal touch", "Use case studies"]
        }
    
    def _get_fallback_context(self) -> Dict[str, Any]:
        """Fallback context when all analysis fails"""
        return {
            "trend_insights": {"trend_score": 5.0},
            "competitive_landscape": {"competitive_score": 5.0},
            "performance_prediction": {"overall_score": 5.0},
            "context_synthesis": {
                "success_probability": 50.0,
                "recommended_strategy": "Foundation Building Strategy"
            },
            "enhancement_recommendations": ["Focus on clear structure", "Add engaging elements"]
        }
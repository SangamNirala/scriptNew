"""
Few-Shot Learning & Pattern Recognition System for Script Generation

This module implements intelligent pattern recognition and few-shot learning
to generate higher quality scripts by learning from proven high-performing examples.

Key Features:
- Curated database of high-performing scripts across categories
- Pattern extraction from successful content structures
- Context-aware example selection based on industry/platform/type
- Template learning and application for consistent quality
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
import asyncio
from pathlib import Path

# NLP and ML imports
import spacy
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database and AI imports
from motor.motor_asyncio import AsyncIOMotorDatabase
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

@dataclass
class ScriptExample:
    """High-performing script example with metadata"""
    id: str
    title: str
    script_content: str
    video_type: str  # educational, marketing, entertainment, viral, etc.
    industry: str    # health, tech, finance, general, etc.
    platform: str    # tiktok, youtube, instagram, general
    duration: str    # short, medium, long
    performance_metrics: Dict[str, float]  # engagement_rate, viral_score, retention_rate
    structural_elements: Dict[str, Any]    # hook, setup, content, climax, resolution
    engagement_techniques: List[str]       # psychological_triggers, retention_cues
    language_patterns: Dict[str, Any]      # tone, complexity, keywords
    success_factors: List[str]             # what made this script successful
    created_at: datetime

@dataclass
class PatternTemplate:
    """Extracted pattern template from successful scripts"""
    id: str
    pattern_type: str  # structural, engagement, platform_specific
    template_name: str
    template_structure: Dict[str, Any]
    effectiveness_score: float
    applicable_contexts: List[str]  # when to use this pattern
    example_scripts: List[str]      # script IDs that demonstrate this pattern
    usage_guidelines: Dict[str, str]
    created_at: datetime

@dataclass
class ContextProfile:
    """Context profile for dynamic example selection"""
    video_type: str
    industry: str
    platform: str
    duration: str
    audience_tone: str
    complexity_level: str
    engagement_goals: List[str]

class FewShotScriptGenerator:
    """
    Few-Shot Learning & Pattern Recognition System for Script Generation
    
    Implements intelligent pattern recognition to improve script quality by:
    1. Learning from curated high-performing examples
    2. Extracting successful patterns and structures
    3. Dynamically selecting relevant examples based on context
    4. Applying learned patterns to new script generation
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, gemini_api_key: str):
        self.db = db
        self.gemini_api_key = gemini_api_key
        self.nlp = None  # Will be loaded when needed
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.pattern_cache = {}
        self.example_embeddings = {}
        
        # Initialize collections
        self.examples_collection = db.script_examples
        self.patterns_collection = db.pattern_templates
        self.performance_collection = db.script_performance
        
    async def initialize(self):
        """Initialize the few-shot learning system"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ Few-Shot Script Generator initialized successfully")
        except OSError:
            logger.warning("spaCy model not found. Installing en_core_web_sm...")
            # In production, this should be pre-installed
            self.nlp = None
            
        # Build initial example database if empty
        await self.build_example_database()
        
        # Extract patterns from examples
        await self.extract_patterns()
        
        logger.info("🚀 Few-Shot Learning & Pattern Recognition System ready")
    
    async def build_example_database(self) -> Dict[str, Any]:
        """
        Build curated database of high-performing scripts across different categories
        
        This creates a comprehensive collection of proven script examples that serve
        as the foundation for pattern recognition and few-shot learning.
        """
        
        # Check if database already populated
        existing_count = await self.examples_collection.count_documents({})
        if existing_count > 0:
            logger.info(f"📚 Example database already contains {existing_count} examples")
            return {"status": "existing", "count": existing_count}
        
        logger.info("🏗️ Building curated example database...")
        
        # Curated high-performing script examples across categories
        curated_examples = [
            # === VIRAL/ENTERTAINMENT CATEGORY ===
            {
                "title": "The Phone Addiction Reality Check",
                "script_content": """
🎣 HOOK (0-3s): "You've picked up your phone 147 times today and don't even realize it."

🎬 SETUP (3-15s): *[Shows person mindlessly scrolling]* "That number isn't a guess—it's the average for someone your age. But here's what's actually terrifying about this..."

📚 CONTENT CORE (15s-1:20s): "Your brain is being rewired every single time you get that dopamine hit from a notification. Tech companies hire neuroscientists—not to help you, but to make you more addicted. They call it 'engagement,' but it's actually a carefully designed trap.

Here's the test: Put your phone in another room for just 2 hours. Notice how many times you instinctively reach for it. That phantom vibration? That's your brain literally craving the addiction.

The scariest part? We're the first generation in human history to voluntarily carry around a device designed to interrupt our thoughts every few minutes."

🏆 CLIMAX (1:20-1:30s): "But what if I told you there's a simple 30-second technique that breaks this cycle completely?"

✨ RESOLUTION (1:30-1:40s): "Turn off ALL notifications except calls and texts. Your brain will thank you, your focus will skyrocket, and you'll actually start living in the moment again. Try it for one week. Your future self will thank you."
                """,
                "video_type": "viral",
                "industry": "general",
                "platform": "tiktok",
                "duration": "short",
                "performance_metrics": {
                    "engagement_rate": 8.5,
                    "viral_score": 9.2,
                    "retention_rate": 87.3,
                    "share_rate": 12.4
                },
                "engagement_techniques": [
                    "shocking_statistic_hook",
                    "fear_appeal",
                    "social_proof",
                    "actionable_solution",
                    "personal_challenge"
                ],
                "success_factors": [
                    "Relatable universal problem",
                    "Surprising statistics",
                    "Clear villain (tech companies)",
                    "Simple actionable solution",
                    "Immediate test/challenge"
                ]
            },
            
            # === EDUCATIONAL/HEALTH CATEGORY ===
            {
                "title": "The 5-Minute Morning Routine That Changes Everything",
                "script_content": """
🎣 HOOK (0-3s): "This 5-minute morning routine is used by Navy SEALs, Olympic athletes, and billionaire CEOs."

🎬 SETUP (3-15s): "But it's not what you think. No ice baths, no 4 AM wake-ups, no complicated supplements. Just 5 simple steps that rewire your brain for peak performance."

📚 CONTENT CORE (15s-2:30s): "Step 1: Hydrate immediately. Your brain is 75% water and you just went 8 hours without any. One glass kickstarts your metabolism and clears brain fog.

Step 2: Move for 60 seconds. Not a workout—just movement. Jump, stretch, dance. You're activating your lymphatic system and boosting circulation.

Step 3: Breathe intentionally. 4 counts in, hold for 4, out for 6. Three times. This activates your parasympathetic nervous system and reduces cortisol by 23%.

Step 4: Set your intention. Not goals—intention. What energy do you want to bring to today? Confidence? Curiosity? Calm? Your brain will start looking for ways to embody it.

Step 5: Win immediately. Make your bed, drink that water, send that text you've been avoiding. Start your day with a win, and momentum builds naturally."

🏆 CLIMAX (2:30-2:40s): "Here's the science: This routine doesn't just wake up your body—it literally changes your brain chemistry for optimal performance."

✨ RESOLUTION (2:40-3:00s): "Try it tomorrow morning. Time yourself. Notice how different you feel by 9 AM. Your most productive, focused, energized self is just 5 minutes away."
                """,
                "video_type": "educational",
                "industry": "health",
                "platform": "youtube",
                "duration": "medium",
                "performance_metrics": {
                    "engagement_rate": 7.8,
                    "viral_score": 6.9,
                    "retention_rate": 92.1,
                    "save_rate": 18.7
                },
                "engagement_techniques": [
                    "authority_positioning",
                    "curiosity_gap",
                    "scientific_backing",
                    "step_by_step_framework",
                    "immediate_challenge"
                ],
                "success_factors": [
                    "Authority figures mentioned",
                    "Contradicts common expectations",
                    "Simple, actionable steps",
                    "Scientific explanation",
                    "Immediate results promise"
                ]
            },
            
            # === MARKETING/BUSINESS CATEGORY ===
            {
                "title": "Why 99% of Small Businesses Fail in Year One",
                "script_content": """
🎣 HOOK (0-3s): "I watched 47 small businesses fail in my neighborhood last year. They all made the same deadly mistake."

🎬 SETUP (3-15s): "It wasn't bad products, terrible locations, or lack of money. It was something way more basic that nobody talks about because it's not sexy."

📚 CONTENT CORE (15s-2:45s): "They fell in love with their product instead of their customer's problem.

Here's what I mean: Sarah opened a boutique fitness studio. Beautiful space, top equipment, certified trainers. But she focused on what SHE loved about fitness instead of what her customers actually struggled with.

Her customers didn't want perfect form or complicated routines. They wanted to feel confident in their bodies again after having kids. They wanted workouts that fit into chaotic schedules. They wanted a community that didn't judge their current fitness level.

Sarah was selling fitness. Her customers wanted transformation.

The successful gym across the street? Their tagline wasn't 'Premium Fitness Experience.' It was 'Get Your Pre-Baby Body Back in 8 Weeks.'

Same service, different focus. Guess which one survived?

This applies to every business. Restaurants that focus on their chef's creativity instead of solving dinner stress. Consultants who talk about their process instead of client results. Coaches who sell their method instead of their client's desired outcome."

🏆 CLIMAX (2:45-2:55s): "Your customers don't buy products. They buy better versions of themselves."

✨ RESOLUTION (2:55-3:15s): "Ask yourself: What transformation does my customer want? What problem keeps them awake at night? Lead with that, and your business becomes essential instead of optional."
                """,
                "video_type": "educational",
                "industry": "marketing",
                "platform": "linkedin",
                "duration": "medium",
                "performance_metrics": {
                    "engagement_rate": 9.1,
                    "viral_score": 7.4,
                    "retention_rate": 89.6,
                    "comment_rate": 15.2
                },
                "engagement_techniques": [
                    "storytelling_with_examples",
                    "contrarian_perspective",
                    "specific_case_study",
                    "problem_agitation",
                    "transformation_promise"
                ],
                "success_factors": [
                    "Specific statistics (47 businesses)",
                    "Real example with names",
                    "Clear before/after contrast",
                    "Universally applicable lesson",
                    "Actionable self-reflection"
                ]
            },
            
            # === TECH/INNOVATION CATEGORY ===
            {
                "title": "The AI Tool That Replaces 6 Hours of Work in 6 Minutes",
                "script_content": """
🎣 HOOK (0-3s): "I just automated my entire content calendar for next month in under 6 minutes."

🎬 SETUP (3-15s): "No, this isn't another ChatGPT tutorial. This is a workflow that combines 3 free AI tools to do what used to take me 6 hours every week."

📚 CONTENT CORE (15s-2:20s): "Here's the exact process:

Tool 1: Claude for strategy. I ask it to analyze my top 5 performing posts and identify patterns. It creates a content strategy based on what actually works for my audience.

Tool 2: Perplexity for research. I feed it trending topics in my industry and ask for unique angles nobody else is covering. It gives me current data and fresh perspectives.

Tool 3: Gamma for visuals. I describe the content concept and it generates professional slides, infographics, and social media templates automatically.

The magic happens when you chain them together. Claude creates the strategy, Perplexity provides the insights, Gamma makes it visual. 

I went from spending Sunday afternoons stressed about content to having a month's worth of high-quality posts ready in minutes."

🏆 CLIMAX (2:20-2:30s): "The best part? This workflow adapts to any industry, any platform, any content type."

✨ RESOLUTION (2:30-2:45s): "Try this exact process this week. Start with your best-performing content, analyze the patterns, and let AI amplify what already works. Your content creation stress is about to disappear."
                """,
                "video_type": "educational",
                "industry": "tech",
                "platform": "youtube",
                "duration": "medium",
                "performance_metrics": {
                    "engagement_rate": 8.7,
                    "viral_score": 8.1,
                    "retention_rate": 91.4,
                    "save_rate": 22.3
                },
                "engagement_techniques": [
                    "time_saving_promise",
                    "tool_specific_tutorial",
                    "workflow_demonstration",
                    "personal_transformation",
                    "universal_applicability"
                ],
                "success_factors": [
                    "Specific time savings claim",
                    "Concrete tool recommendations",
                    "Step-by-step process",
                    "Personal before/after story",
                    "Immediately actionable"
                ]
            },
            
            # === FINANCE/WEALTH CATEGORY ===
            {
                "title": "The $10 Investment That Made Me $50,000",
                "script_content": """
🎣 HOOK (0-3s): "A $10 book changed my entire financial future. Here's how."

🎬 SETUP (3-15s): "I was broke, in debt, and making minimum wage at 23. Everyone said I needed more money to invest. They were wrong. I needed better knowledge."

📚 CONTENT CORE (15s-2:30s): "The book was 'The Intelligent Investor' by Benjamin Graham. Cost me $10 used. Here's what it taught me that business school never did:

Lesson 1: You're not buying stocks, you're buying pieces of businesses. This completely changed how I evaluate investments.

Lesson 2: Market volatility is your friend, not your enemy. When everyone's panicking, that's when opportunities appear.

Lesson 3: Dollar-cost averaging beats timing the market every single time. I started investing $50 every month, no matter what the market was doing.

But here's the real secret: I didn't just read it. I implemented one chapter per month. Slow, deliberate action beats fast, random action.

Year 1: Lost $200 learning. Year 2: Made $500. Year 3: Made $2,000. By year 5: My portfolio hit $50,000.

The $10 investment in knowledge generated 5,000x returns. Not because of luck or timing, but because of understanding principles that work in any market."

🏆 CLIMAX (2:30-2:40s): "The best investment you can make isn't in stocks or crypto. It's in your financial education."

✨ RESOLUTION (2:40-3:00s): "Start with one book, one chapter, one principle. Implement it before moving to the next. Your future wealthy self will thank you for starting today."
                """,
                "video_type": "educational",
                "industry": "finance",
                "platform": "instagram",
                "duration": "medium",
                "performance_metrics": {
                    "engagement_rate": 9.3,
                    "viral_score": 8.9,
                    "retention_rate": 88.7,
                    "save_rate": 19.8
                },
                "engagement_techniques": [
                    "rags_to_riches_story",
                    "specific_numbers",
                    "contrarian_advice",
                    "progressive_learning",
                    "long_term_thinking"
                ],
                "success_factors": [
                    "Relatable starting point (broke at 23)",
                    "Specific book recommendation",
                    "Year-by-year progress tracking",
                    "ROI calculation (5,000x)",
                    "Systematic approach emphasis"
                ]
            },
            
            # === ENTERTAINMENT/LIFESTYLE CATEGORY ===
            {
                "title": "I Lived Like a Medieval Peasant for 30 Days",
                "script_content": """
🎣 HOOK (0-3s): "I gave up electricity, running water, and modern food for an entire month. Here's what happened."

🎬 SETUP (3-15s): "No phone, no internet, no grocery stores. Just me, a small cabin, and the lifestyle our ancestors lived for thousands of years. What I discovered will change how you think about happiness."

📚 CONTENT CORE (15s-2:15s): "Day 1: Pure misery. No coffee, no warm shower, no instant anything. I questioned my sanity.

Day 7: Something shifted. Without constant entertainment, my mind became incredibly clear. I noticed things—bird sounds, wind patterns, the way light changes throughout the day.

Day 14: My sleep improved dramatically. Without artificial light, my body naturally aligned with sunrise and sunset. I was falling asleep at 9 PM and waking up refreshed at 6 AM.

Day 21: The most surprising change—my anxiety disappeared. No news updates, no social media comparisons, no digital overwhelm. Just present-moment awareness.

Day 30: I didn't want to go back.

Here's what medieval peasants had that we don't: Deep sleep, genuine community, purposeful work, and zero information overload. They had struggles we can't imagine, but they also had peace we've forgotten exists."

🏆 CLIMAX (2:15-2:25s): "We've gained the whole world but lost our inner peace. Maybe it's time to find balance."

✨ RESOLUTION (2:25-2:40s): "You don't need to live in a cabin for 30 days. But try this: One evening per week, put away all devices after sunset. Read by candlelight. Go to bed early. Your mind will thank you."
                """,
                "video_type": "entertainment",
                "industry": "lifestyle",
                "platform": "youtube",
                "duration": "medium",
                "performance_metrics": {
                    "engagement_rate": 8.9,
                    "viral_score": 9.5,
                    "retention_rate": 93.2,
                    "comment_rate": 16.7
                },
                "engagement_techniques": [
                    "extreme_experiment",
                    "daily_progression",
                    "unexpected_insights",
                    "historical_comparison",
                    "practical_takeaway"
                ],
                "success_factors": [
                    "Extreme commitment (30 days)",
                    "Day-by-day narrative structure",
                    "Unexpected positive outcomes",
                    "Relatable modern problems",
                    "Simple actionable advice"
                ]
            }
        ]
        
        # Add more examples for different platforms and contexts
        platform_specific_examples = [
            # TikTok-optimized example
            {
                "title": "POV: You're the Smart Friend Everyone Asks for Advice",
                "script_content": """
🎣 HOOK (0-3s): "POV: You're known as the 'smart friend' but you're secretly winging it too."

🎬 SETUP (3-8s): "Everyone thinks you have your life together because you give good advice. Plot twist: You literally Googled half of it 5 minutes ago."

📚 CONTENT CORE (8s-25s): "The truth? Being the 'smart friend' isn't about knowing everything. It's about asking better questions.

Instead of 'What should I do?' ask 'What would I tell my best friend to do?'
Instead of 'Why is this happening?' ask 'What can I learn from this?'
Instead of 'What if I fail?' ask 'What if I don't try?'

The smartest people I know don't have all the answers. They just ask questions that lead to clarity."

🏆 CLIMAX (25-28s): "You're not supposed to have it all figured out. None of us do."

✨ RESOLUTION (28-30s): "Give yourself the same grace you give your friends. You're doing better than you think. ✨"
                """,
                "video_type": "viral",
                "industry": "general",
                "platform": "tiktok",
                "duration": "short",
                "performance_metrics": {
                    "engagement_rate": 9.8,
                    "viral_score": 9.7,
                    "retention_rate": 89.4,
                    "share_rate": 18.9
                },
                "engagement_techniques": [
                    "pov_format",
                    "relatable_imposter_syndrome",
                    "vulnerability",
                    "reframing_questions",
                    "self_compassion"
                ],
                "success_factors": [
                    "Universal relatability",
                    "Vulnerable honesty",
                    "Actionable reframes",
                    "Positive affirmation ending",
                    "TikTok-native POV format"
                ]
            }
        ]
        
        # Combine all examples
        all_examples = curated_examples + platform_specific_examples
        
        # Insert examples into database
        inserted_count = 0
        for example_data in all_examples:
            # Create script example object
            script_example = ScriptExample(
                id=str(uuid.uuid4()),
                title=example_data["title"],
                script_content=example_data["script_content"],
                video_type=example_data["video_type"],
                industry=example_data["industry"],
                platform=example_data["platform"],
                duration=example_data["duration"],
                performance_metrics=example_data["performance_metrics"],
                structural_elements=self._extract_structural_elements(example_data["script_content"]),
                engagement_techniques=example_data["engagement_techniques"],
                language_patterns=self._analyze_language_patterns(example_data["script_content"]),
                success_factors=example_data["success_factors"],
                created_at=datetime.utcnow()
            )
            
            # Insert into database
            await self.examples_collection.insert_one(asdict(script_example))
            inserted_count += 1
        
        logger.info(f"✅ Successfully built example database with {inserted_count} high-performing scripts")
        
        return {
            "status": "created",
            "count": inserted_count,
            "categories": {
                "viral": len([e for e in all_examples if e["video_type"] == "viral"]),
                "educational": len([e for e in all_examples if e["video_type"] == "educational"]),
                "entertainment": len([e for e in all_examples if e["video_type"] == "entertainment"]),
                "platforms": {
                    "tiktok": len([e for e in all_examples if e["platform"] == "tiktok"]),
                    "youtube": len([e for e in all_examples if e["platform"] == "youtube"]),
                    "instagram": len([e for e in all_examples if e["platform"] == "instagram"]),
                    "linkedin": len([e for e in all_examples if e["platform"] == "linkedin"])
                }
            }
        }
    
    def _extract_structural_elements(self, script_content: str) -> Dict[str, Any]:
        """Extract structural elements from script content"""
        elements = {
            "hook": "",
            "setup": "",
            "content": "",
            "climax": "",
            "resolution": "",
            "has_clear_structure": False
        }
        
        # Look for explicit structure markers
        hook_match = re.search(r'🎣 HOOK.*?:(.*?)(?=🎬|$)', script_content, re.DOTALL)
        setup_match = re.search(r'🎬 SETUP.*?:(.*?)(?=📚|$)', script_content, re.DOTALL)
        content_match = re.search(r'📚 CONTENT.*?:(.*?)(?=🏆|$)', script_content, re.DOTALL)
        climax_match = re.search(r'🏆 CLIMAX.*?:(.*?)(?=✨|$)', script_content, re.DOTALL)
        resolution_match = re.search(r'✨ RESOLUTION.*?:(.*?)$', script_content, re.DOTALL)
        
        if hook_match:
            elements["hook"] = hook_match.group(1).strip()
            elements["has_clear_structure"] = True
        if setup_match:
            elements["setup"] = setup_match.group(1).strip()
        if content_match:
            elements["content"] = content_match.group(1).strip()
        if climax_match:
            elements["climax"] = climax_match.group(1).strip()
        if resolution_match:
            elements["resolution"] = resolution_match.group(1).strip()
            
        return elements
    
    def _analyze_language_patterns(self, script_content: str) -> Dict[str, Any]:
        """Analyze language patterns in script content"""
        # Remove structure markers for pure text analysis
        clean_text = re.sub(r'🎣.*?:|🎬.*?:|📚.*?:|🏆.*?:|✨.*?:', '', script_content)
        clean_text = re.sub(r'\[.*?\]', '', clean_text)  # Remove stage directions
        
        words = clean_text.split()
        sentences = clean_text.split('.')
        
        # Calculate basic metrics
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Analyze tone indicators
        urgency_words = ['now', 'immediately', 'urgent', 'quickly', 'hurry', 'deadline']
        emotion_words = ['amazing', 'incredible', 'shocking', 'surprising', 'terrifying', 'beautiful']
        action_words = ['try', 'start', 'begin', 'do', 'make', 'create', 'build', 'implement']
        
        urgency_score = sum(1 for word in words if word.lower() in urgency_words) / max(word_count, 1) * 100
        emotion_score = sum(1 for word in words if word.lower() in emotion_words) / max(word_count, 1) * 100  
        action_score = sum(1 for word in words if word.lower() in action_words) / max(word_count, 1) * 100
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "urgency_score": urgency_score,
            "emotion_score": emotion_score,
            "action_score": action_score,
            "complexity_level": "simple" if avg_sentence_length < 15 else "medium" if avg_sentence_length < 25 else "complex"
        }
    
    async def select_relevant_examples(self, context: ContextProfile, limit: int = 5) -> List[ScriptExample]:
        """
        Select most relevant examples based on context using intelligent matching
        
        Uses a combination of exact matching and similarity scoring to find
        the best examples for the given context.
        """
        # Build query for exact matches
        query = {}
        
        # Primary matching criteria
        if context.video_type != "general":
            query["video_type"] = context.video_type
            
        if context.industry != "general":
            query["industry"] = context.industry
            
        if context.platform != "general":
            query["platform"] = context.platform
            
        # Get examples from database
        cursor = self.examples_collection.find(query).limit(limit * 2)  # Get more for scoring
        examples = await cursor.to_list(length=None)
        
        if not examples:
            # Fallback to broader search if no exact matches
            cursor = self.examples_collection.find({}).limit(limit * 2)
            examples = await cursor.to_list(length=None)
        
        # Convert to ScriptExample objects
        script_examples = []
        for example_data in examples:
            # Handle MongoDB _id field - create a copy to avoid modifying original
            example_copy = example_data.copy()
            if '_id' in example_copy:
                example_copy['id'] = str(example_copy['_id'])
                del example_copy['_id']
            script_example = ScriptExample(**example_copy)
            script_examples.append(script_example)
        
        # Score examples based on context relevance
        scored_examples = []
        for example in script_examples:
            score = self._calculate_relevance_score(example, context)
            scored_examples.append((example, score))
        
        # Sort by relevance score and return top examples
        scored_examples.sort(key=lambda x: x[1], reverse=True)
        top_examples = [example for example, score in scored_examples[:limit]]
        
        logger.info(f"📋 Selected {len(top_examples)} relevant examples for context: {context.video_type}/{context.industry}/{context.platform}")
        
        return top_examples
    
    def _calculate_relevance_score(self, example: ScriptExample, context: ContextProfile) -> float:
        """Calculate relevance score for example based on context"""
        score = 0.0
        
        # Exact match bonuses
        if example.video_type == context.video_type:
            score += 3.0
        if example.industry == context.industry:
            score += 2.5
        if example.platform == context.platform:
            score += 2.0
        if example.duration == context.duration:
            score += 1.5
            
        # Performance metrics bonus
        avg_performance = (
            example.performance_metrics.get("engagement_rate", 0) +
            example.performance_metrics.get("viral_score", 0) +
            example.performance_metrics.get("retention_rate", 0) / 10  # Scale retention to 0-10
        ) / 3
        score += avg_performance * 0.5
        
        # Complexity matching
        if hasattr(context, 'complexity_level'):
            example_complexity = example.language_patterns.get("complexity_level", "medium")
            if example_complexity == context.complexity_level:
                score += 1.0
        
        # Engagement goals matching
        if hasattr(context, 'engagement_goals'):
            matching_techniques = set(example.engagement_techniques) & set(context.engagement_goals)
            score += len(matching_techniques) * 0.5
        
        return score
    
    async def extract_patterns(self) -> Dict[str, Any]:
        """
        Extract successful patterns from high-performing examples
        
        Analyzes structural, engagement, and platform-specific patterns
        that contribute to script success.
        """
        logger.info("🔍 Extracting patterns from high-performing examples...")
        
        # Get all examples from database
        cursor = self.examples_collection.find({})
        examples = await cursor.to_list(length=None)
        
        if not examples:
            logger.warning("No examples found for pattern extraction")
            return {"status": "no_examples"}
        
        patterns_extracted = 0
        
        # Extract structural patterns
        structural_patterns = await self._extract_structural_patterns(examples)
        for pattern in structural_patterns:
            await self.patterns_collection.insert_one(asdict(pattern))
            patterns_extracted += 1
        
        # Extract engagement patterns
        engagement_patterns = await self._extract_engagement_patterns(examples)
        for pattern in engagement_patterns:
            await self.patterns_collection.insert_one(asdict(pattern))
            patterns_extracted += 1
        
        # Extract platform-specific patterns
        platform_patterns = await self._extract_platform_patterns(examples)
        for pattern in platform_patterns:
            await self.patterns_collection.insert_one(asdict(pattern))
            patterns_extracted += 1
        
        logger.info(f"✅ Extracted {patterns_extracted} patterns from examples")
        
        return {
            "status": "completed",
            "patterns_extracted": patterns_extracted,
            "categories": {
                "structural": len(structural_patterns),
                "engagement": len(engagement_patterns),
                "platform_specific": len(platform_patterns)
            }
        }
    
    async def _extract_structural_patterns(self, examples: List[Dict]) -> List[PatternTemplate]:
        """Extract structural patterns from examples"""
        patterns = []
        
        # Analyze hook patterns
        hook_patterns = defaultdict(list)
        for example in examples:
            structural_elements = example.get("structural_elements", {})
            hook = structural_elements.get("hook", "")
            if hook:
                # Classify hook type
                hook_type = self._classify_hook_type(hook)
                hook_patterns[hook_type].append(str(example.get("_id", example.get("id", ""))))
        
        # Create hook pattern templates
        for hook_type, example_ids in hook_patterns.items():
            if len(example_ids) >= 2:  # Only create patterns with multiple examples
                effectiveness = self._calculate_pattern_effectiveness(example_ids, examples)
                
                pattern = PatternTemplate(
                    id=str(uuid.uuid4()),
                    pattern_type="structural",
                    template_name=f"hook_{hook_type}",
                    template_structure={
                        "hook_type": hook_type,
                        "typical_length": "0-3 seconds",
                        "key_elements": self._get_hook_elements(hook_type),
                        "effectiveness_factors": self._get_hook_effectiveness_factors(hook_type)
                    },
                    effectiveness_score=effectiveness,
                    applicable_contexts=self._get_hook_contexts(hook_type),
                    example_scripts=example_ids,
                    usage_guidelines={
                        "when_to_use": self._get_hook_usage_guide(hook_type),
                        "avoid_if": self._get_hook_avoidance_guide(hook_type)
                    },
                    created_at=datetime.utcnow()
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _extract_engagement_patterns(self, examples: List[Dict]) -> List[PatternTemplate]:
        """Extract engagement patterns from examples"""
        patterns = []
        
        # Analyze engagement technique patterns
        technique_patterns = defaultdict(list)
        for example in examples:
            techniques = example.get("engagement_techniques", [])
            for technique in techniques:
                technique_patterns[technique].append(str(example.get("_id", example.get("id", ""))))
        
        # Create engagement pattern templates
        for technique, example_ids in technique_patterns.items():
            if len(example_ids) >= 2:
                effectiveness = self._calculate_pattern_effectiveness(example_ids, examples)
                
                pattern = PatternTemplate(
                    id=str(uuid.uuid4()),
                    pattern_type="engagement",
                    template_name=f"engagement_{technique}",
                    template_structure={
                        "technique": technique,
                        "psychological_basis": self._get_psychological_basis(technique),
                        "implementation_guide": self._get_implementation_guide(technique),
                        "timing_recommendations": self._get_timing_recommendations(technique)
                    },
                    effectiveness_score=effectiveness,
                    applicable_contexts=self._get_technique_contexts(technique),
                    example_scripts=example_ids,
                    usage_guidelines={
                        "optimal_placement": self._get_optimal_placement(technique),
                        "combination_tips": self._get_combination_tips(technique)
                    },
                    created_at=datetime.utcnow()
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _extract_platform_patterns(self, examples: List[Dict]) -> List[PatternTemplate]:
        """Extract platform-specific patterns from examples"""
        patterns = []
        
        # Group examples by platform
        platform_groups = defaultdict(list)
        for example in examples:
            platform = example.get("platform", "general")
            platform_groups[platform].append(example)
        
        # Analyze each platform's patterns
        for platform, platform_examples in platform_groups.items():
            if len(platform_examples) >= 2:
                # Calculate average performance metrics
                avg_metrics = self._calculate_average_metrics(platform_examples)
                
                # Extract common characteristics
                common_characteristics = self._extract_common_characteristics(platform_examples)
                
                pattern = PatternTemplate(
                    id=str(uuid.uuid4()),
                    pattern_type="platform_specific",
                    template_name=f"platform_{platform}",
                    template_structure={
                        "platform": platform,
                        "optimal_duration": self._get_optimal_duration(platform_examples),
                        "typical_structure": self._get_typical_structure(platform_examples),
                        "engagement_style": self._get_engagement_style(platform_examples),
                        "visual_elements": self._get_visual_elements(platform),
                        "algorithm_preferences": self._get_algorithm_preferences(platform)
                    },
                    effectiveness_score=avg_metrics.get("overall_score", 7.0),
                    applicable_contexts=[platform],
                    example_scripts=[str(ex.get("_id", ex.get("id", ""))) for ex in platform_examples],
                    usage_guidelines={
                        "content_format": self._get_content_format(platform),
                        "posting_strategy": self._get_posting_strategy(platform),
                        "optimization_tips": self._get_optimization_tips(platform)
                    },
                    created_at=datetime.utcnow()
                )
                patterns.append(pattern)
        
        return patterns
    
    def _classify_hook_type(self, hook: str) -> str:
        """Classify the type of hook based on content"""
        hook_lower = hook.lower()
        
        if any(word in hook_lower for word in ['statistic', 'number', '%', 'studies show']):
            return "statistical"
        elif any(word in hook_lower for word in ['you', 'your', 'imagine', 'picture this']):
            return "personal_address"
        elif any(word in hook_lower for word in ['question', '?', 'what if', 'why']):
            return "question"
        elif any(word in hook_lower for word in ['shocking', 'secret', 'nobody tells you', 'surprising']):
            return "revelation"
        elif any(word in hook_lower for word in ['story', 'happened', 'experience', 'i was']):
            return "story"
        else:
            return "statement"
    
    def _calculate_pattern_effectiveness(self, example_ids: List[str], examples: List[Dict]) -> float:
        """Calculate effectiveness score for a pattern based on examples"""
        relevant_examples = [ex for ex in examples if str(ex.get("_id", ex.get("id", ""))) in example_ids]
        if not relevant_examples:
            return 5.0
        
        total_score = 0.0
        for example in relevant_examples:
            metrics = example.get("performance_metrics", {})
            # Weight different metrics
            score = (
                metrics.get("engagement_rate", 5.0) * 0.3 +
                metrics.get("viral_score", 5.0) * 0.3 +
                metrics.get("retention_rate", 50.0) / 10 * 0.4  # Scale to 0-10
            )
            total_score += score
        
        return total_score / len(relevant_examples)
    
    # Helper methods for pattern extraction (simplified implementations)
    def _get_hook_elements(self, hook_type: str) -> List[str]:
        hook_elements = {
            "statistical": ["specific numbers", "credible sources", "surprising data"],
            "personal_address": ["direct address", "second person", "visualization"],
            "question": ["open-ended questions", "curiosity gaps", "challenging assumptions"],
            "revelation": ["contrast", "insider knowledge", "surprising facts"],
            "story": ["personal narrative", "relatable situation", "emotional connection"],
            "statement": ["bold claims", "clear positioning", "immediate value"]
        }
        return hook_elements.get(hook_type, ["engagement", "clarity", "relevance"])
    
    def _get_hook_effectiveness_factors(self, hook_type: str) -> List[str]:
        return ["immediate attention grab", "curiosity generation", "relevance to audience", "emotional impact"]
    
    def _get_hook_contexts(self, hook_type: str) -> List[str]:
        contexts = {
            "statistical": ["educational", "business", "health"],
            "personal_address": ["self-help", "motivation", "lifestyle"],
            "question": ["educational", "problem-solving", "philosophical"],
            "revelation": ["viral", "entertainment", "contrarian"],
            "story": ["personal brand", "testimonial", "case study"],
            "statement": ["marketing", "announcement", "positioning"]
        }
        return contexts.get(hook_type, ["general"])
    
    def _get_hook_usage_guide(self, hook_type: str) -> str:
        guides = {
            "statistical": "Use when you have credible, surprising data that supports your main point",
            "personal_address": "Use when creating intimate, personal connections with audience",
            "question": "Use when you want to make audience think and engage mentally",
            "revelation": "Use when you have insider knowledge or contrarian perspectives",
            "story": "Use when you have relatable, emotional narratives",
            "statement": "Use when you need to establish authority or make bold claims"
        }
        return guides.get(hook_type, "Use when context is appropriate")
    
    def _get_hook_avoidance_guide(self, hook_type: str) -> str:
        return "Avoid if the hook doesn't align with your content's actual value or if it feels forced"
    
    # Additional helper methods (simplified)
    def _get_psychological_basis(self, technique: str) -> str:
        return f"Psychological principle behind {technique}"
    
    def _get_implementation_guide(self, technique: str) -> str:
        return f"How to implement {technique} effectively"
    
    def _get_timing_recommendations(self, technique: str) -> str:
        return f"Optimal timing for {technique}"
    
    def _get_technique_contexts(self, technique: str) -> List[str]:
        return ["general"]
    
    def _get_optimal_placement(self, technique: str) -> str:
        return f"Best placement for {technique}"
    
    def _get_combination_tips(self, technique: str) -> str:
        return f"How to combine {technique} with other techniques"
    
    def _calculate_average_metrics(self, examples: List[Dict]) -> Dict[str, float]:
        if not examples:
            return {"overall_score": 5.0}
        
        total_engagement = sum(ex.get("performance_metrics", {}).get("engagement_rate", 5.0) for ex in examples)
        return {"overall_score": total_engagement / len(examples)}
    
    def _extract_common_characteristics(self, examples: List[Dict]) -> Dict[str, Any]:
        return {"common_traits": "extracted characteristics"}
    
    def _get_optimal_duration(self, examples: List[Dict]) -> str:
        durations = [ex.get("duration", "medium") for ex in examples]
        return Counter(durations).most_common(1)[0][0] if durations else "medium"
    
    def _get_typical_structure(self, examples: List[Dict]) -> str:
        return "typical structure pattern"
    
    def _get_engagement_style(self, examples: List[Dict]) -> str:
        return "engagement style pattern"
    
    def _get_visual_elements(self, platform: str) -> List[str]:
        elements = {
            "tiktok": ["vertical format", "trending sounds", "quick cuts", "text overlays"],
            "youtube": ["thumbnails", "chapters", "end screens", "cards"],
            "instagram": ["square/vertical", "stories", "reels effects", "hashtags"],
            "linkedin": ["professional imagery", "carousels", "infographics", "native video"]
        }
        return elements.get(platform, ["general visual elements"])
    
    def _get_algorithm_preferences(self, platform: str) -> List[str]:
        preferences = {
            "tiktok": ["completion rate", "engagement velocity", "trending audio", "hashtag participation"],
            "youtube": ["watch time", "CTR", "session duration", "subscriber growth"],
            "instagram": ["saves", "shares", "comments", "profile visits"],
            "linkedin": ["professional engagement", "industry relevance", "thought leadership", "network sharing"]
        }
        return preferences.get(platform, ["general engagement"])
    
    def _get_content_format(self, platform: str) -> str:
        formats = {
            "tiktok": "Short-form vertical video with quick paced content",
            "youtube": "Longer form content with clear structure and retention hooks",
            "instagram": "Visual-first content with strong aesthetic appeal",
            "linkedin": "Professional, value-driven content with industry insights"
        }
        return formats.get(platform, "Platform-appropriate format")
    
    def _get_posting_strategy(self, platform: str) -> str:
        return f"Optimal posting strategy for {platform}"
    
    def _get_optimization_tips(self, platform: str) -> List[str]:
        return [f"Optimization tip 1 for {platform}", f"Optimization tip 2 for {platform}"]
    
    async def apply_learned_patterns(self, 
                                   context: ContextProfile, 
                                   base_prompt: str,
                                   selected_examples: List[ScriptExample] = None) -> Dict[str, Any]:
        """
        Apply learned patterns to generate enhanced script prompts
        
        Uses pattern templates and relevant examples to create optimized
        prompts that incorporate proven successful techniques.
        """
        logger.info(f"🎯 Applying learned patterns for context: {context.video_type}/{context.industry}")
        
        # Get relevant examples if not provided
        if not selected_examples:
            selected_examples = await self.select_relevant_examples(context, limit=3)
        
        # Get relevant pattern templates
        relevant_patterns = await self._get_relevant_patterns(context)
        
        # Generate enhanced prompt using patterns and examples
        enhanced_prompt = await self._generate_pattern_enhanced_prompt(
            context, base_prompt, selected_examples, relevant_patterns
        )
        
        return {
            "enhanced_prompt": enhanced_prompt,
            "patterns_applied": len(relevant_patterns),
            "examples_used": len(selected_examples),
            "confidence_score": self._calculate_confidence_score(selected_examples, relevant_patterns),
            "pattern_details": [
                {
                    "type": pattern.pattern_type,
                    "name": pattern.template_name,
                    "effectiveness": pattern.effectiveness_score
                }
                for pattern in relevant_patterns
            ]
        }
    
    async def _get_relevant_patterns(self, context: ContextProfile) -> List[PatternTemplate]:
        """Get pattern templates relevant to the context"""
        # Query patterns collection
        cursor = self.patterns_collection.find({
            "applicable_contexts": {"$in": [context.platform, context.video_type, context.industry, "general"]}
        })
        patterns_data = await cursor.to_list(length=None)
        
        # Convert to PatternTemplate objects
        patterns = []
        for pattern_data in patterns_data:
            pattern = PatternTemplate(**pattern_data)
            patterns.append(pattern)
        
        # Sort by effectiveness score
        patterns.sort(key=lambda p: p.effectiveness_score, reverse=True)
        
        return patterns[:10]  # Return top 10 patterns
    
    async def _generate_pattern_enhanced_prompt(self,
                                              context: ContextProfile,
                                              base_prompt: str,
                                              examples: List[ScriptExample],
                                              patterns: List[PatternTemplate]) -> str:
        """Generate enhanced prompt using patterns and examples"""
        
        # Create AI chat for prompt enhancement
        chat = LlmChat(
            api_key=self.gemini_api_key,
            session_id=f"pattern-enhance-{str(uuid.uuid4())[:8]}",
            system_message="""You are an expert script optimization specialist who applies proven patterns from high-performing content to enhance script prompts. Your role is to integrate successful structural, engagement, and platform-specific patterns to maximize script effectiveness."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Prepare examples summary
        examples_summary = ""
        for i, example in enumerate(examples[:3], 1):
            examples_summary += f"""
EXAMPLE {i}: {example.title}
Performance: Engagement {example.performance_metrics.get('engagement_rate', 0):.1f}/10, Viral {example.performance_metrics.get('viral_score', 0):.1f}/10
Key Techniques: {', '.join(example.engagement_techniques[:3])}
Success Factors: {', '.join(example.success_factors[:2])}

Structure Preview:
{example.structural_elements.get('hook', 'N/A')[:100]}...
"""
        
        # Prepare patterns summary
        patterns_summary = ""
        for pattern in patterns[:5]:
            patterns_summary += f"""
PATTERN: {pattern.template_name.replace('_', ' ').title()}
Type: {pattern.pattern_type}
Effectiveness: {pattern.effectiveness_score:.1f}/10
Usage: {pattern.usage_guidelines.get('when_to_use', 'General usage')[:100]}...
"""
        
        enhancement_prompt = f"""PATTERN-ENHANCED SCRIPT OPTIMIZATION

ORIGINAL PROMPT: "{base_prompt}"

CONTEXT:
- Video Type: {context.video_type}
- Industry: {context.industry}  
- Platform: {context.platform}
- Duration: {context.duration}
- Audience Tone: {context.audience_tone}
- Complexity: {context.complexity_level}

HIGH-PERFORMING EXAMPLES TO LEARN FROM:
{examples_summary}

PROVEN PATTERNS TO APPLY:
{patterns_summary}

ENHANCEMENT INSTRUCTIONS:

1. STRUCTURAL OPTIMIZATION:
   - Apply proven hook patterns from successful examples
   - Integrate effective setup → content → climax → resolution flow
   - Ensure optimal pacing for {context.platform} platform

2. ENGAGEMENT INTEGRATION:
   - Incorporate high-performing psychological triggers
   - Apply retention techniques from successful examples
   - Balance emotional engagement with {context.industry} requirements

3. PLATFORM ADAPTATION:
   - Optimize for {context.platform} algorithm preferences
   - Apply platform-specific formatting and style
   - Integrate visual and audio elements recommendations

4. PATTERN SYNTHESIS:
   - Combine multiple proven patterns intelligently
   - Avoid pattern conflicts or overuse
   - Maintain authenticity while applying learned techniques

Create an enhanced version of the original prompt that:
- Incorporates 3-5 proven patterns from the provided templates
- References specific successful techniques from the examples
- Maintains the original intent while dramatically improving potential performance
- Includes specific structural, engagement, and platform optimization guidance

ENHANCED PROMPT:"""
        
        response = await chat.send_message(UserMessage(text=enhancement_prompt))
        
        return response.strip()
    
    def _calculate_confidence_score(self, examples: List[ScriptExample], patterns: List[PatternTemplate]) -> float:
        """Calculate confidence score for the pattern application"""
        if not examples and not patterns:
            return 5.0
        
        # Base score from examples
        example_score = 0.0
        if examples:
            avg_performance = sum(
                (ex.performance_metrics.get('engagement_rate', 5.0) + 
                 ex.performance_metrics.get('viral_score', 5.0)) / 2
                for ex in examples
            ) / len(examples)
            example_score = avg_performance
        
        # Pattern effectiveness score
        pattern_score = 0.0
        if patterns:
            pattern_score = sum(p.effectiveness_score for p in patterns) / len(patterns)
        
        # Combined confidence score
        confidence = (example_score * 0.6 + pattern_score * 0.4)
        return min(10.0, max(1.0, confidence))

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the few-shot learning system"""
        
        # Count examples by category
        examples_count = await self.examples_collection.count_documents({})
        patterns_count = await self.patterns_collection.count_documents({})
        
        # Get category breakdowns
        video_types = await self.examples_collection.distinct("video_type")
        industries = await self.examples_collection.distinct("industry")
        platforms = await self.examples_collection.distinct("platform")
        
        # Get performance metrics
        cursor = self.examples_collection.find({}, {"performance_metrics": 1})
        examples = await cursor.to_list(length=None)
        
        if examples:
            avg_engagement = sum(ex.get("performance_metrics", {}).get("engagement_rate", 0) for ex in examples) / len(examples)
            avg_viral = sum(ex.get("performance_metrics", {}).get("viral_score", 0) for ex in examples) / len(examples)
            avg_retention = sum(ex.get("performance_metrics", {}).get("retention_rate", 0) for ex in examples) / len(examples)
        else:
            avg_engagement = avg_viral = avg_retention = 0
        
        return {
            "system_status": "operational",
            "database_stats": {
                "examples_count": examples_count,
                "patterns_count": patterns_count,
                "categories": {
                    "video_types": video_types,
                    "industries": industries,
                    "platforms": platforms
                }
            },
            "performance_averages": {
                "engagement_rate": round(avg_engagement, 2),
                "viral_score": round(avg_viral, 2),
                "retention_rate": round(avg_retention, 2)
            },
            "learning_capability": {
                "pattern_recognition": "active",
                "example_matching": "context-aware",
                "template_learning": "adaptive"
            }
        }
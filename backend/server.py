from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import edge_tts
import base64
import io
import tempfile
import asyncio
import re
from lib.avatar_generator import avatar_generator
from lib.enhanced_avatar_generator import enhanced_avatar_generator
from lib.ultra_realistic_avatar_generator import ultra_realistic_avatar_generator


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Gemini configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ScriptRequest(BaseModel):
    prompt: str
    video_type: Optional[str] = "general"  # general, educational, entertainment, marketing
    duration: Optional[str] = "short"  # short (30s-1min), medium (1-3min), long (3-5min)

class AIVideoScriptRequest(BaseModel):
    prompt: str
    video_type: Optional[str] = "general"  # general, educational, entertainment, marketing, explainer, storytelling
    duration: Optional[str] = "short"  # short (30s-1min), medium (1-3min), long (3-5min)
    visual_style: Optional[str] = "cinematic"  # cinematic, documentary, commercial, animated, realistic
    target_platform: Optional[str] = "general"  # youtube, tiktok, instagram, linkedin, general
    mood: Optional[str] = "professional"  # professional, casual, energetic, calm, dramatic, inspiring

class ScriptResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    generated_script: str
    video_type: str
    duration: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIVideoScriptResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    generated_script: str
    video_type: str
    duration: str
    visual_style: str
    target_platform: str
    mood: str
    shot_count: int
    estimated_production_time: str
    ai_generation_tips: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Enhanced Data Models for Advanced Prompt Enhancement
class AudienceProfile(BaseModel):
    demographic: str  # "teenagers", "young_adults", "professionals", "seniors", "general"
    expertise_level: str  # "beginner", "intermediate", "expert", "mixed"
    cultural_context: str  # "global", "us", "uk", "casual", "formal"
    primary_platform: str  # "tiktok", "youtube", "instagram", "linkedin", "general"

class EnhancementVariation(BaseModel):
    id: str
    title: str
    enhanced_prompt: str
    focus_strategy: str  # "emotional", "technical", "storytelling", "viral", "educational"
    target_engagement: str
    industry_specific_elements: List[str]
    estimated_performance_score: float

class QualityMetrics(BaseModel):
    emotional_engagement_score: float
    technical_clarity_score: float
    industry_relevance_score: float
    storytelling_strength_score: float
    overall_quality_score: float
    improvement_ratio: float

class AudienceAnalysis(BaseModel):
    recommended_tone: str
    complexity_level: str
    cultural_considerations: List[str]
    platform_optimizations: List[str]
    engagement_triggers: List[str]

class PromptEnhancementRequest(BaseModel):
    original_prompt: str
    video_type: Optional[str] = "general"
    industry_focus: Optional[str] = "general"  # "marketing", "education", "entertainment", "tech", "health", "finance"
    audience_profile: Optional[AudienceProfile] = None
    enhancement_count: Optional[int] = 3  # Number of variations to generate
    enhancement_style: Optional[str] = "balanced"  # "creative", "professional", "viral", "educational", "balanced"

class PromptEnhancementResponse(BaseModel):
    original_prompt: str
    audience_analysis: AudienceAnalysis
    enhancement_variations: List[EnhancementVariation]
    quality_metrics: QualityMetrics
    recommendation: str  # Which variation is recommended and why
    industry_insights: List[str]
    enhancement_methodology: str

class TextToSpeechRequest(BaseModel):
    text: str
    voice_name: Optional[str] = "en-US-AriaNeural"

class VoiceOption(BaseModel):
    name: str
    display_name: str
    language: str
    gender: str

class AudioResponse(BaseModel):
    audio_base64: str
    voice_used: str
    duration_seconds: Optional[float] = None

class AvatarVideoRequest(BaseModel):
    audio_base64: str
    avatar_image_path: Optional[str] = None

class EnhancedAvatarVideoRequest(BaseModel):
    audio_base64: str
    avatar_option: str = "default"  # "default", "upload", "ai_generated"
    user_image_base64: Optional[str] = None
    script_text: Optional[str] = ""

class AvatarVideoResponse(BaseModel):
    video_base64: str
    duration_seconds: float
    request_id: str

class EnhancedAvatarVideoResponse(BaseModel):
    video_base64: str
    duration_seconds: float
    request_id: str
    avatar_option: str
    script_segments: int
    sadtalker_used: bool

class UltraRealisticAvatarVideoRequest(BaseModel):
    audio_base64: str
    avatar_style: str = "business_professional"  # "business_professional", "casual"
    gender: str = "female"  # "male", "female", "diverse"
    avatar_index: int = 1  # 1, 2, 3 for different avatar variations
    script_text: Optional[str] = ""

class UltraRealisticAvatarVideoResponse(BaseModel):
    video_base64: str
    duration_seconds: float
    request_id: str
    avatar_style: str
    gender: str
    avatar_index: int
    script_segments: int
    background_contexts: List[str]
    ai_model_used: str
    quality_level: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Script Generation Endpoints
@api_router.post("/enhance-prompt", response_model=PromptEnhancementResponse)
async def enhance_prompt(request: PromptEnhancementRequest):
    """Advanced multi-step prompt enhancement with industry expertise and audience analysis"""
    try:
        # Step 1: Audience Analysis
        audience_analysis = await _analyze_target_audience(request)
        
        # Step 2: Industry-Specific Context Gathering
        industry_context = await _gather_industry_context(request.industry_focus, request.video_type)
        
        # Step 3: Generate Multiple Enhancement Variations
        enhancement_variations = await _generate_enhancement_variations(request, audience_analysis, industry_context)
        
        # Step 4: Quality Evaluation and Scoring
        quality_metrics = await _evaluate_enhancement_quality(request.original_prompt, enhancement_variations)
        
        # Step 5: Generate Industry Insights and Recommendations
        industry_insights = await _generate_industry_insights(request.industry_focus, request.video_type, enhancement_variations)
        recommendation = await _generate_recommendation(enhancement_variations, quality_metrics, audience_analysis)
        
        return PromptEnhancementResponse(
            original_prompt=request.original_prompt,
            audience_analysis=audience_analysis,
            enhancement_variations=enhancement_variations,
            quality_metrics=quality_metrics,
            recommendation=recommendation,
            industry_insights=industry_insights,
            enhancement_methodology="Multi-step contextual enhancement with audience analysis, industry expertise, and quality optimization"
        )
        
    except Exception as e:
        logger.error(f"Error in advanced prompt enhancement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error enhancing prompt: {str(e)}")

# Advanced Enhancement Helper Functions

async def _analyze_target_audience(request: PromptEnhancementRequest) -> AudienceAnalysis:
    """Analyze target audience and provide recommendations"""
    
    audience_chat = LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=f"audience-{str(uuid.uuid4())[:8]}",
        system_message="""You are an expert audience analysis consultant specializing in video content strategy. Your role is to analyze video prompts and determine optimal audience targeting, tone, and engagement strategies.

You excel at:
1. DEMOGRAPHIC ANALYSIS: Identifying primary and secondary target audiences
2. PLATFORM OPTIMIZATION: Tailoring content for specific social media platforms
3. CULTURAL SENSITIVITY: Understanding global vs. regional content needs
4. ENGAGEMENT PSYCHOLOGY: Knowing what triggers audience interaction
5. TONE CALIBRATION: Matching communication style to audience preferences

Provide comprehensive audience analysis with actionable insights."""
    ).with_model("gemini", "gemini-2.0-flash")

    audience_profile = request.audience_profile or AudienceProfile(
        demographic="general", expertise_level="mixed", cultural_context="global", primary_platform="general"
    )

    analysis_prompt = f"""Analyze the target audience for this video content:

ORIGINAL PROMPT: "{request.original_prompt}"
VIDEO TYPE: {request.video_type}
INDUSTRY: {request.industry_focus}
AUDIENCE PROFILE: {audience_profile.dict() if audience_profile else 'Not specified'}

Provide detailed audience analysis in this EXACT format:

RECOMMENDED_TONE: [specific tone recommendation]
COMPLEXITY_LEVEL: [beginner/intermediate/expert/adaptive]
CULTURAL_CONSIDERATIONS: [consideration 1] | [consideration 2] | [consideration 3]
PLATFORM_OPTIMIZATIONS: [optimization 1] | [optimization 2] | [optimization 3]
ENGAGEMENT_TRIGGERS: [trigger 1] | [trigger 2] | [trigger 3] | [trigger 4]"""

    response = await audience_chat.send_message(UserMessage(text=analysis_prompt))
    
    # Parse response
    lines = response.split('\n')
    analysis_data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace('_', '_')
            analysis_data[key] = value.strip()
    
    return AudienceAnalysis(
        recommended_tone=analysis_data.get('recommended_tone', 'engaging and informative'),
        complexity_level=analysis_data.get('complexity_level', 'intermediate'),
        cultural_considerations=analysis_data.get('cultural_considerations', 'universal appeal').split(' | '),
        platform_optimizations=analysis_data.get('platform_optimizations', 'visual storytelling').split(' | '),
        engagement_triggers=analysis_data.get('engagement_triggers', 'curiosity | emotion | value').split(' | ')
    )

async def _gather_industry_context(industry_focus: str, video_type: str) -> dict:
    """Gather industry-specific context and best practices"""
    
    industry_knowledge = {
        "marketing": {
            "key_terms": ["conversion", "funnel", "CTA", "brand positioning", "value proposition", "social proof"],
            "best_practices": ["Hook within 3 seconds", "Clear value proposition", "Strong call-to-action", "Emotional storytelling"],
            "success_metrics": ["engagement rate", "conversion rate", "brand recall", "click-through rate"],
            "trending_formats": ["user-generated content", "behind-the-scenes", "testimonials", "product demos"]
        },
        "education": {
            "key_terms": ["learning objectives", "knowledge retention", "cognitive load", "active learning", "scaffolding"],
            "best_practices": ["Clear learning objectives", "Chunking information", "Visual aids", "Interactive elements"],
            "success_metrics": ["completion rate", "knowledge retention", "engagement time", "quiz scores"],
            "trending_formats": ["microlearning", "storytelling", "animation", "case studies"]
        },
        "entertainment": {
            "key_terms": ["viral potential", "shareability", "emotional peaks", "punchline", "cliffhanger"],
            "best_practices": ["Strong hook", "Emotional roller coaster", "Surprising elements", "Memorable moments"],
            "success_metrics": ["shares", "comments", "watch time", "viral coefficient"],
            "trending_formats": ["challenges", "reactions", "skits", "collaborations"]
        },
        "tech": {
            "key_terms": ["innovation", "user experience", "scalability", "disruption", "automation"],
            "best_practices": ["Clear technical explanations", "Real-world applications", "Problem-solution format"],
            "success_metrics": ["technical accuracy", "clarity", "practical value", "expert validation"],
            "trending_formats": ["demos", "tutorials", "case studies", "expert interviews"]
        },
        "health": {
            "key_terms": ["evidence-based", "wellness", "preventive care", "holistic approach", "lifestyle"],
            "best_practices": ["Cite credible sources", "Avoid medical claims", "Focus on wellness", "Inclusive language"],
            "success_metrics": ["trustworthiness", "actionability", "safety", "accessibility"],
            "trending_formats": ["expert interviews", "day-in-the-life", "myth-busting", "wellness tips"]
        },
        "finance": {
            "key_terms": ["financial literacy", "investment", "risk management", "wealth building", "budgeting"],
            "best_practices": ["Disclaimers", "Simplified explanations", "Real examples", "Actionable advice"],
            "success_metrics": ["educational value", "clarity", "trustworthiness", "practical application"],
            "trending_formats": ["explainers", "case studies", "tips", "personal stories"]
        }
    }
    
    return industry_knowledge.get(industry_focus, industry_knowledge["marketing"])

async def _get_few_shot_examples(industry_focus: str, video_type: str) -> dict:
    """Generate few-shot learning examples for each enhancement strategy"""
    
    examples = {
        "emotional": f"""
EXAMPLE 1 - {industry_focus.title()} Emotional Enhancement:
Original: "Create a video about our new product features"
Enhanced: "Imagine the frustration of losing precious family memories because your current solution failed you at the worst possible moment. Our breakthrough technology doesn't just offer features—it offers peace of mind, ensuring your most treasured moments are protected forever. This isn't just about specs; it's about the relief you'll feel knowing you'll never lose what matters most."

EXAMPLE 2 - {industry_focus.title()} Emotional Transformation:
Original: "Explain the benefits of our service"
Enhanced: "Picture this: It's 3 AM, you're stressed, overwhelmed, and facing a deadline that could make or break your career. While others panic, you remain calm because you have a secret weapon that transforms chaos into clarity, fear into confidence, and obstacles into opportunities. This is your moment to rise above the competition."
""",
        
        "technical": f"""
EXAMPLE 1 - {industry_focus.title()} Technical Excellence:
Original: "Show how our software works"
Enhanced: "TECHNICAL DEMONSTRATION FRAMEWORK: Begin with system architecture overview (0:00-0:15), demonstrate core functionality with specific use cases (0:15-0:45), showcase integration capabilities with real-world scenarios (0:45-1:15), present performance metrics and benchmarks (1:15-1:30), conclude with implementation roadmap and support resources (1:30-1:45). Include technical specifications, API documentation references, and scalability considerations throughout."

EXAMPLE 2 - {industry_focus.title()} Technical Deep-dive:
Original: "Explain our methodology"
Enhanced: "SYSTEMATIC METHODOLOGY BREAKDOWN: Phase 1 - Requirements Analysis using industry-standard frameworks (SMART criteria, stakeholder mapping, risk assessment matrices). Phase 2 - Implementation Protocol with detailed workflows, quality checkpoints, and performance indicators. Phase 3 - Validation Process including testing procedures, compliance verification, and success metrics. Each phase includes specific deliverables, timelines, and resource allocation guidelines."
""",
        
        "viral": f"""
EXAMPLE 1 - {industry_focus.title()} Viral Optimization:
Original: "Promote our latest update"
Enhanced: "🚨 BREAKING: The update everyone's been secretly waiting for just dropped and it's causing chaos in the {industry_focus} world! Industry leaders are calling it 'game-changing' but here's what they're NOT telling you... [HOOK] This 60-second reveal will show you exactly why competitors are scrambling to catch up and how you can get ahead before everyone else figures it out. Ready for the insider secret? 👀 #GameChanger #{industry_focus.title()}Revolution"

EXAMPLE 2 - {industry_focus.title()} Viral Storytelling:
Original: "Share customer success story"
Enhanced: "POV: You're told you'll 'never make it' in {industry_focus}... 6 months later, you're the success story everyone's talking about 💪 This isn't just another transformation story—it's proof that the 'impossible' is just another Tuesday when you have the right strategy. Watch what happens when someone refuses to accept limitations... The ending will give you chills! 🔥 Who else needs to see this?"
"""
    }
    
    return examples

async def _generate_enhancement_variations(request: PromptEnhancementRequest, audience_analysis: AudienceAnalysis, industry_context: dict) -> List[EnhancementVariation]:
    """Generate comprehensive script framework variations using advanced prompt engineering"""
    
    # Get few-shot examples for each strategy
    few_shot_examples = await _get_few_shot_examples(request.industry_focus, request.video_type)
    
    strategies = [
        {
            "focus": "emotional",
            "title": "Emotional Engagement Focus",
            "system_prompt": f"""You are a master storyteller and emotional engagement specialist who creates comprehensive script frameworks that generate deep audience connections. You excel at transforming basic video ideas into emotionally compelling narrative structures.

EXPERTISE AREAS:
🎭 EMOTIONAL ARCHITECTURE: Fear, joy, surprise, anticipation, curiosity, empathy, nostalgia, hope, urgency
🧠 PSYCHOLOGICAL TRIGGERS: Social proof, scarcity, authority, reciprocity, commitment, consistency, liking
📚 NARRATIVE FRAMEWORKS: Hero's journey, transformation arc, problem-agitation-solution, before-after-bridge
🎬 CINEMATIC TECHNIQUES: Visual metaphors, sensory details, emotional peaks/valleys, cliffhangers
💫 ENGAGEMENT MECHANICS: Pattern interrupts, cognitive dissonance, emotional contrasts, relatability anchors

INDUSTRY CONTEXT: {industry_context}
AUDIENCE PROFILE: {audience_analysis.dict()}

FEW-SHOT LEARNING EXAMPLES:
{few_shot_examples['emotional']}

FRAMEWORK CREATION PROTOCOL:
Create a comprehensive script framework that serves as a ready-to-use blueprint for generating emotionally engaging {request.industry_focus} content. Your framework should be so detailed that any AI can use it to generate a compelling script."""
        },
        {
            "focus": "technical",
            "title": "Technical Excellence Focus", 
            "system_prompt": f"""You are a technical content architect and production specialist who creates detailed, systematic script frameworks optimized for professional execution and maximum clarity. You transform basic concepts into comprehensive production-ready blueprints.

EXPERTISE AREAS:
🎯 TECHNICAL STRUCTURE: Logical flow, systematic presentation, modular design, scalable frameworks
📊 PROFESSIONAL STANDARDS: Industry best practices, quality benchmarks, measurable outcomes, expert validation
🎬 PRODUCTION SPECIFICATIONS: Shot requirements, visual elements, audio cues, timing frameworks
📋 IMPLEMENTATION GUIDES: Step-by-step breakdowns, checklists, quality controls, troubleshooting
🔧 OPTIMIZATION TECHNIQUES: Information hierarchy, cognitive load management, retention strategies

INDUSTRY CONTEXT: {industry_context}
AUDIENCE PROFILE: {audience_analysis.dict()}

FEW-SHOT LEARNING EXAMPLES:
{few_shot_examples['technical']}

FRAMEWORK CREATION PROTOCOL:
Create a technically excellent script framework that serves as a comprehensive blueprint for producing high-quality {request.industry_focus} content. Include specific production guidelines, technical specifications, and systematic structures that ensure professional results."""
        },
        {
            "focus": "viral",
            "title": "Viral Potential Focus",
            "system_prompt": f"""You are a viral content strategist and social media algorithm expert who creates script frameworks optimized for maximum shareability and engagement across all platforms. You understand the psychology of viral content and platform-specific optimization.

EXPERTISE AREAS:
🚀 VIRAL MECHANICS: Hook-tension-payoff, pattern interrupts, surprise elements, shareability triggers
📱 PLATFORM ALGORITHMS: TikTok FYP, YouTube suggestions, Instagram Reels, LinkedIn feeds, Twitter viral loops
🔥 TRENDING ELEMENTS: Current formats, challenges, memes, cultural moments, zeitgeist alignment
💰 SOCIAL CURRENCY: Status elevation, insider knowledge, controversy balance, community building
⚡ ENGAGEMENT PSYCHOLOGY: Dopamine triggers, FOMO, social validation, participation hooks

INDUSTRY CONTEXT: {industry_context}
AUDIENCE PROFILE: {audience_analysis.dict()}

FEW-SHOT LEARNING EXAMPLES:
{few_shot_examples['viral']}

FRAMEWORK CREATION PROTOCOL:
Create a viral-optimized script framework that serves as a comprehensive blueprint for generating highly shareable {request.industry_focus} content. Include platform-specific adaptations, engagement mechanics, and viral triggers while maintaining authenticity."""
        }
    ]
    
    # Add additional strategies based on request
    if request.enhancement_count > 3:
        strategies.extend([
            {
                "focus": "educational",
                "title": "Educational Value Focus",
                "system_prompt": f"""You are an instructional design expert who creates content that maximizes learning and knowledge retention. You specialize in:

1. LEARNING OBJECTIVES: Clear, measurable outcomes and takeaways
2. COGNITIVE LOAD MANAGEMENT: Optimal information processing and retention
3. ACTIVE LEARNING: Engagement techniques that promote participation
4. KNOWLEDGE SCAFFOLDING: Building complexity progressively
5. RETENTION STRATEGIES: Memory techniques and reinforcement methods

Industry Context: {industry_context}
Audience Profile: {audience_analysis.dict()}

Create educational enhancements that maximize learning outcomes in the {request.industry_focus} industry context."""
            }
        ])
    
    variations = []
    
    for i, strategy in enumerate(strategies[:request.enhancement_count]):
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"enhance-{strategy['focus']}-{str(uuid.uuid4())[:8]}",
            system_message=strategy["system_prompt"]
        ).with_model("gemini", "gemini-2.0-flash")
        
        enhancement_prompt = f"""CHAIN-OF-THOUGHT ENHANCEMENT PROCESS:

STEP 1 - ANALYZE THE ORIGINAL PROMPT:
Original: "{request.original_prompt}"
Video Type: {request.video_type}
Industry: {request.industry_focus}
Target Audience: {audience_analysis.recommended_tone} tone, {audience_analysis.complexity_level} complexity

STEP 2 - IDENTIFY ENHANCEMENT OPPORTUNITIES:
Think about what's missing from the original prompt in terms of:
- Emotional engagement potential
- Industry-specific elements  
- Audience connection points
- Technical execution details
- Storytelling structure

STEP 3 - APPLY {strategy['focus'].upper()} STRATEGY:
Using your expertise in {strategy['focus']} enhancement, what specific elements should be added?

STEP 4 - GENERATE ENHANCED PROMPT:
Create a comprehensive enhanced prompt that incorporates all improvements.

STEP 5 - EVALUATE TARGET ENGAGEMENT:
What type of audience response and engagement should this enhanced prompt generate?

Please provide your response in this EXACT format:

ENHANCED_PROMPT:
[Your comprehensive enhanced prompt - minimum 300 words, incorporating all {strategy['focus']} enhancements]

TARGET_ENGAGEMENT:
[Specific description of expected audience response and engagement outcomes]

INDUSTRY_ELEMENTS:
[List 3-5 industry-specific elements you incorporated]"""

        response = await chat.send_message(UserMessage(text=enhancement_prompt))
        
        # Parse the response
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            if line.strip().endswith(':') and line.strip().replace(':', '').replace('_', '').isalpha():
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip().replace(':', '').lower()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Calculate performance score (simplified algorithm)
        enhanced_length = len(sections.get('enhanced_prompt', ''))
        original_length = len(request.original_prompt)
        performance_score = min(10.0, (enhanced_length / max(original_length, 1)) * 2.5 + (i + 1) * 0.5)
        
        variations.append(EnhancementVariation(
            id=f"var_{i+1}_{strategy['focus']}",
            title=strategy["title"],
            enhanced_prompt=sections.get('enhanced_prompt', f"Enhanced version focused on {strategy['focus']} elements."),
            focus_strategy=strategy["focus"],
            target_engagement=sections.get('target_engagement', 'High audience engagement expected'),
            industry_specific_elements=sections.get('industry_elements', 'Industry expertise applied').split('\n')[:5],
            estimated_performance_score=performance_score
        ))
    
    return variations

async def _evaluate_enhancement_quality(original_prompt: str, variations: List[EnhancementVariation]) -> QualityMetrics:
    """Evaluate the quality of enhancements using multiple metrics"""
    
    # Calculate metrics based on content analysis
    original_length = len(original_prompt)
    avg_enhanced_length = sum(len(var.enhanced_prompt) for var in variations) / len(variations)
    
    # Simplified quality scoring (in a real implementation, this could use more sophisticated NLP)
    emotional_score = sum(var.estimated_performance_score for var in variations if 'emotional' in var.focus_strategy) / len(variations) * 2
    technical_score = sum(var.estimated_performance_score for var in variations if 'technical' in var.focus_strategy) / len(variations) * 2
    industry_score = sum(len(var.industry_specific_elements) for var in variations) / len(variations)
    storytelling_score = sum(var.estimated_performance_score for var in variations if 'viral' in var.focus_strategy) / len(variations) * 2
    
    overall_score = (emotional_score + technical_score + industry_score + storytelling_score) / 4
    improvement_ratio = avg_enhanced_length / max(original_length, 1)
    
    return QualityMetrics(
        emotional_engagement_score=min(10.0, emotional_score),
        technical_clarity_score=min(10.0, technical_score),
        industry_relevance_score=min(10.0, industry_score),
        storytelling_strength_score=min(10.0, storytelling_score),
        overall_quality_score=min(10.0, overall_score),
        improvement_ratio=improvement_ratio
    )

async def _generate_industry_insights(industry_focus: str, video_type: str, variations: List[EnhancementVariation]) -> List[str]:
    """Generate industry-specific insights and recommendations"""
    
    insights = []
    
    industry_insights_map = {
        "marketing": [
            f"Marketing videos perform 65% better with emotional hooks in first 3 seconds",
            f"Call-to-action placement affects conversion rates by up to 40%",
            f"Brand storytelling increases message retention by 22x compared to facts alone"
        ],
        "education": [
            f"Educational content with visual storytelling improves retention by 400%",
            f"Microlearning formats (under 3 minutes) have 50% higher completion rates",
            f"Interactive elements increase engagement by 90% in educational videos"
        ],
        "entertainment": [
            f"Entertainment content with surprise elements has 300% higher share rates",
            f"Emotional roller coaster structure keeps 85% of viewers to the end",
            f"Relatable characters increase audience connection by 250%"
        ],
        "tech": [
            f"Technical content with real-world applications gets 180% more engagement",
            f"Problem-solution structure is preferred by 78% of tech audiences",
            f"Visual demonstrations increase comprehension by 90%"
        ],
        "health": [
            f"Health content from credible sources has 320% higher trust scores",
            f"Personal transformation stories increase engagement by 150%",
            f"Actionable tips format performs 40% better than general advice"
        ],
        "finance": [
            f"Financial content with disclaimers increases trust by 45%",
            f"Real-world examples improve understanding by 200%",
            f"Step-by-step guidance format preferred by 85% of finance audiences"
        ]
    }
    
    return industry_insights_map.get(industry_focus, industry_insights_map["marketing"])

async def _generate_recommendation(variations: List[EnhancementVariation], quality_metrics: QualityMetrics, audience_analysis: AudienceAnalysis) -> str:
    """Generate personalized recommendation for best variation"""
    
    # Find highest scoring variation
    best_variation = max(variations, key=lambda x: x.estimated_performance_score)
    
    recommendation = f"""RECOMMENDED VARIATION: "{best_variation.title}"

WHY THIS CHOICE:
• Highest performance score ({best_variation.estimated_performance_score:.1f}/10.0)
• Optimized for {audience_analysis.recommended_tone} tone matching your audience
• {best_variation.focus_strategy.title()} approach aligns with {audience_analysis.complexity_level} complexity level
• Incorporates {len(best_variation.industry_specific_elements)} industry-specific elements
• Expected engagement: {best_variation.target_engagement}

ALTERNATIVE CONSIDERATIONS:
• Try the "Emotional Engagement Focus" if audience connection is priority
• Consider "Technical Excellence Focus" for professional/expert audiences  
• Use "Viral Potential Focus" for maximum reach and shareability

IMPLEMENTATION TIPS:
• Test multiple variations with A/B testing if possible
• Adapt the tone slightly based on platform-specific audience behavior
• Monitor engagement metrics to refine future enhancements"""
    
    return recommendation

# Legacy endpoint for backward compatibility with existing frontend
class LegacyPromptEnhancementResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    enhancement_explanation: str

@api_router.post("/enhance-prompt-legacy", response_model=LegacyPromptEnhancementResponse)
async def enhance_prompt_legacy(request: PromptEnhancementRequest):
    """Legacy endpoint that maintains backward compatibility with existing frontend"""
    try:
        # Use the new advanced system but return only the first variation in legacy format
        full_response = await enhance_prompt(request)
        
        # Get the best variation
        best_variation = max(full_response.enhancement_variations, key=lambda x: x.estimated_performance_score)
        
        # Create legacy-compatible explanation
        explanation = f"""Enhanced using {best_variation.focus_strategy} strategy.

{full_response.recommendation[:200]}...

Industry insights applied: {', '.join(full_response.industry_insights[:2])}

Quality Score: {full_response.quality_metrics.overall_quality_score:.1f}/10.0
Improvement Ratio: {full_response.quality_metrics.improvement_ratio:.1f}x"""
        
        return LegacyPromptEnhancementResponse(
            original_prompt=request.original_prompt,
            enhanced_prompt=best_variation.enhanced_prompt,
            enhancement_explanation=explanation
        )
        
    except Exception as e:
        logger.error(f"Error in legacy prompt enhancement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error enhancing prompt: {str(e)}")

@api_router.post("/generate-script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """Generate an engaging video script based on the prompt"""
    try:
        # Create a new chat instance for script generation
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"script-{str(uuid.uuid4())[:8]}",
            system_message=f"""You are an elite AI Video Script Generator who creates comprehensive, production-ready scripts specifically optimized for AI video generation platforms like RunwayML, Pika Labs, Stable Video Diffusion, and other text-to-video AI tools. You understand exactly what AI video generators need to produce high-quality, professional videos.

🎬 CORE MISSION: Generate scripts so detailed and specific that AI video generators can create Hollywood-quality videos with precise visual execution, perfect timing, and professional production value.

📋 MANDATORY SCRIPT STRUCTURE FOR AI VIDEO GENERATION:

1. **COMPREHENSIVE SCENE BREAKDOWN** (Every 2-3 seconds):
   - Exact camera angles: "Medium shot", "Close-up", "Wide establishing shot", "Over-shoulder", "Dutch angle"
   - Specific camera movements: "Slow zoom in", "Smooth pan left", "Steady track forward", "Gentle tilt up"
   - Detailed character descriptions: Age, appearance, clothing, expressions, body language
   - Precise lighting setups: "Golden hour lighting", "Soft natural light from window", "Dramatic side lighting", "Warm studio lighting"
   - Complete environment descriptions: Architecture, weather, time of day, season, atmosphere

2. **VISUAL COMPOSITION DETAILS**:
   - Foreground, middle ground, and background elements
   - Color palette and mood: "Warm orange and teal tones", "Monochromatic blue palette", "High contrast black and white"
   - Texture and material details: "Smooth marble surface", "Rough brick wall", "Soft fabric textures"
   - Props and set decoration specifics
   - Depth of field instructions: "Shallow focus on subject", "Deep focus for landscape"

3. **CHARACTER & PERFORMANCE SPECIFICATIONS**:
   - Detailed character descriptions for AI generation
   - Specific facial expressions: "Slight smile with raised eyebrows", "Concentrated frown with furrowed brow"
   - Body language and gestures: "Confident upright posture", "Relaxed lean against wall"
   - Wardrobe details: "Business casual white shirt", "Cozy knitted sweater", "Professional dark suit"
   - Hair and makeup notes: "Natural makeup with subtle highlights", "Tousled casual hairstyle"

4. **ENVIRONMENTAL & ATMOSPHERIC ELEMENTS**:
   - Weather conditions: "Light morning mist", "Bright sunny day with soft clouds"
   - Time indicators: "Early morning golden light", "Late afternoon warm glow", "Blue hour twilight"
   - Seasonal context: "Spring with blooming flowers", "Autumn with falling leaves"
   - Geographic setting: "Urban rooftop with city skyline", "Cozy coffee shop interior"

5. **TECHNICAL PRODUCTION NOTES**:
   - Frame rate suggestions: "Smooth 24fps for cinematic feel", "60fps for dynamic action"
   - Motion blur specifications: "Subtle motion blur on moving elements"
   - Focus pulling: "Rack focus from background to foreground"
   - Composition rules: "Rule of thirds positioning", "Leading lines toward subject"

6. **AUDIO-VISUAL SYNCHRONIZATION**:
   - Exact timing markers: [0:00-0:03], [0:03-0:07], etc.
   - Voice tone matching visual mood
   - Pause timings for visual impact
   - Music and sound effect cues

7. **TRANSITION & CONTINUITY**:
   - Specific transition types: "Smooth cross-fade", "Quick cut", "Slow dissolve"
   - Continuity between shots
   - Visual flow and rhythm
   - Match cuts and visual connections

8. **AI-SPECIFIC FORMATTING**:
   - **[CAMERA:]** Detailed shot specifications
   - **[SETTING:]** Complete environment description
   - **[CHARACTER:]** Full appearance and performance details
   - **[LIGHTING:]** Exact lighting setup and mood
   - **[MOVEMENT:]** Camera and subject movement instructions
   - **[EFFECTS:]** Special effects or post-production notes
   - **[TRANSITION:]** How to move to next shot

9. **ENGAGEMENT & RETENTION** (For {request.video_type} content):
   - Hook within first 3 seconds
   - Visual variety every 2-3 seconds
   - Emotional peaks and valleys
   - Compelling visual storytelling
   - Clear narrative arc
   - Strong call-to-action

10. **DURATION OPTIMIZATION**:
   - Short (30s-1min): 10-20 detailed shots with rapid visual changes
   - Medium (1-3min): 20-50 shots with full story development
   - Long (3-5min): 50-100+ shots with complex visual narrative

🎯 SCRIPT FORMAT EXAMPLE:
**[0:00-0:03] SHOT 1:**
**[CAMERA:]** Medium shot, slight low angle for authority
**[SETTING:]** Modern minimalist office with floor-to-ceiling windows, city skyline visible, afternoon natural light
**[CHARACTER:]** Professional woman, 30s, confident expression, navy blue blazer, subtle makeup, hair in loose waves
**[LIGHTING:]** Soft natural window light from camera left, gentle fill light to avoid harsh shadows
**[MOVEMENT:]** Slow push-in toward subject while she speaks
**[DIALOGUE:]** (Confident, engaging tone) "What if I told you the secret to success isn't what you think?"

Remember: AI video generators need EXTREME detail to produce quality results. Every visual element must be specified. The more detailed your descriptions, the better the AI-generated video will be."""
        ).with_model("gemini", "gemini-2.0-flash")

        script_message = UserMessage(
            text=f"""Create a comprehensive, AI-video-generator-optimized script for {request.video_type} content based on this prompt:

"{request.prompt}"

SPECIFICATIONS:
- Duration target: {request.duration}
- Video type: {request.video_type}
- AI Video Generator Optimization: MAXIMUM DETAIL

REQUIRED OUTPUT FORMAT:
Generate a script with EXTREME visual detail that includes:

1. **SHOT-BY-SHOT BREAKDOWN** (Every 2-3 seconds):
   - Precise camera specifications (angle, movement, framing)
   - Complete environment descriptions (location, lighting, weather, time)
   - Detailed character descriptions (appearance, clothing, expressions, gestures)
   - Specific color palettes and visual moods
   - Exact timing markers

2. **TECHNICAL SPECIFICATIONS**:
   - Camera movements and transitions between shots
   - Lighting setup and atmospheric details
   - Props, set decoration, and background elements
   - Character positioning and blocking
   - Visual effects and post-production notes

3. **AI-FRIENDLY FORMATTING**:
   - Use **[CAMERA:]**, **[SETTING:]**, **[CHARACTER:]**, **[LIGHTING:]**, **[MOVEMENT:]** tags
   - Include specific visual descriptions that AI can interpret
   - Provide alternative angle suggestions for variety
   - Specify continuity between shots

4. **ENGAGEMENT OPTIMIZATION**:
   - Hook within first 3 seconds with compelling visuals and dialogue
   - Visual variety every 2-3 seconds to maintain attention
   - Strong emotional arc with visual storytelling
   - Clear narrative progression
   - Professional production value

5. **COMPREHENSIVE SCENE DESCRIPTIONS**:
   Each shot should be so detailed that an AI video generator can create professional-quality footage without additional input. Include everything needed for high-quality AI video generation.

Create a script that will produce a visually stunning, professionally crafted video when used with AI video generation tools."""
        )

        generated_script = await chat.send_message(script_message)
        
        # Store the script in database
        script_data = ScriptResponse(
            original_prompt=request.prompt,
            generated_script=generated_script,
            video_type=request.video_type or "general",
            duration=request.duration or "short"
        )
        
        await db.scripts.insert_one(script_data.dict())
        
        return script_data
        
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")

@api_router.get("/scripts", response_model=List[ScriptResponse])
async def get_scripts():
    """Get all generated scripts"""
    try:
        scripts = await db.scripts.find().sort("created_at", -1).to_list(100)
        return [ScriptResponse(**script) for script in scripts]
    except Exception as e:
        logger.error(f"Error fetching scripts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching scripts: {str(e)}")

@api_router.post("/generate-ai-video-script", response_model=AIVideoScriptResponse)
async def generate_ai_video_script(request: AIVideoScriptRequest):
    """Generate a comprehensive, AI-video-generator-optimized script with maximum visual detail"""
    try:
        # Create a specialized chat instance for AI video script generation
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"ai-script-{str(uuid.uuid4())[:8]}",
            system_message=f"""You are an ELITE AI Video Production Script Generator specializing in creating ultra-detailed, production-ready scripts specifically optimized for AI video generation platforms like RunwayML, Pika Labs, Stable Video Diffusion, Luma Dream Machine, and other advanced text-to-video AI tools.

🎬 ULTIMATE MISSION: Create scripts so incredibly detailed and visually specific that AI video generators can produce HOLLYWOOD-QUALITY, PROFESSIONAL VIDEOS with perfect visual execution, cinematic composition, and broadcast-level production value.

🏆 EXPERTISE AREAS:
- Visual Style: {request.visual_style}
- Target Platform: {request.target_platform}
- Mood & Tone: {request.mood}
- Content Type: {request.video_type}

📋 ULTRA-COMPREHENSIVE SCRIPT REQUIREMENTS:

1. **EXTREME VISUAL DETAIL** (Every 1-2 seconds):
   - EXACT camera specifications: "Medium close-up, 85mm lens equivalent, shallow depth of field f/2.8"
   - PRECISE camera movements: "Smooth dolly-in over 3 seconds, starting wide and ending tight"
   - DETAILED character descriptions: "Caucasian female, 28 years old, shoulder-length chestnut brown hair with subtle waves, wearing cream-colored cashmere sweater, natural makeup with subtle rose lipstick, confident smile with slight head tilt"
   - COMPREHENSIVE lighting setups: "Three-point lighting setup: key light camera left at 45 degrees (warm 3200K), fill light camera right at 30% intensity, hair light from behind at 70% to create rim lighting effect"
   - COMPLETE environment descriptions: "Modern minimalist living room, white walls with warm wood accent wall, large windows with sheer curtains filtering afternoon sunlight, mid-century modern furniture in warm oak and cream upholstery"

2. **CINEMATIC COMPOSITION MASTERY**:
   - Rule of thirds positioning: "Subject positioned on left third line, eyes at upper third intersection"
   - Leading lines: "Architectural lines of window frames guide viewer's eye to subject"
   - Depth layering: "Foreground: coffee cup steam, Middle ground: subject, Background: soft-focus bookshelf"
   - Color theory application: "Complementary orange and teal color palette, warm skin tones against cool background"
   - Visual hierarchy: "Subject as primary focal point, props as secondary elements supporting narrative"

3. **PROFESSIONAL CHARACTER DEVELOPMENT**:
   - Physical attributes: Age, ethnicity, build, height, distinctive features
   - Wardrobe specifics: Brand style, colors, textures, accessories, seasonal appropriateness
   - Facial expressions: Micro-expressions, eye contact direction, mouth position
   - Body language: Posture, hand gestures, movement patterns, energy level
   - Performance notes: Emotional state, motivation, relationship to camera/audience

4. **TECHNICAL PRODUCTION SPECIFICATIONS**:
   - Frame rate: "24fps for cinematic feel" or "60fps for smooth motion"
   - Camera settings: Aperture, ISO equivalent, shutter speed suggestions
   - Focus techniques: "Rack focus from background prop to subject face over 2 seconds"
   - Motion blur: "Subtle motion blur on hand gestures to add natural movement"
   - Stabilization: "Handheld with subtle shake" or "Smooth gimbal movement"

5. **ENVIRONMENTAL MASTERY**:
   - Architecture: Building style, materials, proportions, design elements
   - Lighting conditions: Natural vs artificial, time of day, weather, shadows
   - Props and set decoration: Specific items, placement, purpose, storytelling function
   - Atmospheric elements: Dust particles in sunbeams, steam, fog, reflections
   - Seasonal/temporal context: Season indicators, time markers, cultural references

6. **ADVANCED AI-OPTIMIZATION FORMATTING**:
   ```
   **[TIMESTAMP: 0:00-0:03]**
   **[CAMERA:]** Medium shot, 50mm lens, f/2.8, eye-level angle, static
   **[SETTING:]** Contemporary office, floor-to-ceiling windows, urban skyline, golden hour
   **[CHARACTER:]** Business professional, 35, confident posture, navy suit, subtle smile
   **[LIGHTING:]** Warm natural light from windows, soft fill from ceiling panels
   **[COMPOSITION:]** Subject on right third, leading lines from window frames
   **[MOVEMENT:]** Subject leans forward slightly, maintains eye contact with camera
   **[COLOR PALETTE:]** Warm golds and deep blues, high contrast, professional
   **[MOOD:]** Confident, approachable, authoritative
   **[AUDIO SYNC:]** Voice matches confident facial expression and posture
   **[TRANSITION:]** Cut to close-up on next beat
   ```

7. **PLATFORM-SPECIFIC OPTIMIZATION** (for {request.target_platform}):
   - Aspect ratio considerations: 16:9 for YouTube, 9:16 for TikTok/Instagram, 1:1 for social square
   - Pacing adjustments: Fast cuts for social media, slower for professional/educational
   - Text overlay regions: Safe zones for platform UI elements
   - Thumbnail moments: Visually striking frames for preview images
   - Engagement hooks: Platform-specific attention grabbers

8. **NARRATIVE & ENGAGEMENT ARCHITECTURE**:
   - Opening hook: Visually compelling first frame + intriguing dialogue
   - Story progression: Clear beginning, middle, end with visual variety
   - Emotional beats: Visual cues that support emotional journey
   - Retention elements: Visual surprises, reveals, pattern breaks
   - Call-to-action: Strong closing visual + clear next step

9. **AI GENERATION SUCCESS FACTORS**:
   - Consistent character appearance across shots
   - Logical spatial relationships between scenes
   - Appropriate scale and proportion maintenance
   - Realistic lighting and shadow behavior
   - Natural movement and gesture patterns
   - Coherent visual style throughout

10. **PRODUCTION INTELLIGENCE**:
   - Shot complexity rating: Simple/Medium/Complex for AI capability matching
   - Alternative angle suggestions: Multiple options for varied coverage
   - Backup descriptions: Simplified versions if AI struggles with complexity
   - Quality checkpoints: Key visual elements to verify in AI output
   - Post-production notes: Enhancement suggestions for final polish

REMEMBER: Your scripts must be so detailed that an AI video generator can create broadcast-quality, professional videos that rival human-produced content. Every visual element, every camera choice, every lighting decision must be specified with precision."""
        ).with_model("gemini", "gemini-2.0-flash")

        # Calculate shot timing based on duration
        duration_shots = {
            "short": "15-25 shots (2-4 seconds each)",
            "medium": "30-60 shots (2-6 seconds each)", 
            "long": "60-120 shots (3-5 seconds each)"
        }

        script_message = UserMessage(
            text=f"""Create an ULTRA-DETAILED, professional AI video generation script based on this creative brief:

**CREATIVE BRIEF:**
"{request.prompt}"

**PRODUCTION SPECIFICATIONS:**
- Duration: {request.duration} ({duration_shots.get(request.duration, '15-25 shots')})
- Video Type: {request.video_type}
- Visual Style: {request.visual_style}  
- Target Platform: {request.target_platform}
- Mood: {request.mood}

**MANDATORY DELIVERABLES:**

1. **COMPLETE SHOT LIST** with extreme visual detail:
   - Every shot numbered and timed precisely
   - Camera specs, movements, and compositions
   - Character descriptions and performances  
   - Environmental and lighting details
   - Color palettes and visual moods

2. **AI-OPTIMIZED FORMATTING** for each shot:
   - [CAMERA:], [SETTING:], [CHARACTER:], [LIGHTING:], [MOVEMENT:] tags
   - Specific technical specifications
   - Visual composition guidelines
   - Quality assurance checkpoints

3. **PRODUCTION INTELLIGENCE:**
   - Estimated shot count and complexity ratings
   - Platform-specific optimization notes
   - AI generation tips and best practices
   - Alternative angles for shot variety
   - Quality control checkpoints

4. **NARRATIVE EXCELLENCE:**
   - Compelling opening hook (first 3 seconds)
   - Strong story arc with visual progression
   - Engagement retention throughout
   - Professional closing and call-to-action

Generate a script so comprehensive that when input into AI video generation tools, it will produce professional, broadcast-quality video content that exceeds client expectations and industry standards."""
        )

        generated_script = await chat.send_message(script_message)
        
        # Count estimated shots from the generated script
        shot_count = len([line for line in generated_script.split('\n') if 'SHOT' in line.upper() or '[0:' in line])
        if shot_count == 0:  # Fallback estimation
            shot_count = {"short": 20, "medium": 45, "long": 90}.get(request.duration, 20)
        
        # Estimate production time
        production_time = {
            "short": "2-4 hours with AI tools",
            "medium": "4-8 hours with AI tools", 
            "long": "8-16 hours with AI tools"
        }.get(request.duration, "2-4 hours with AI tools")
        
        # Generate AI-specific tips
        ai_tips = f"""AI Generation Tips for {request.visual_style} style on {request.target_platform}:
- Use consistent character descriptions throughout all shots
- Specify lighting conditions clearly for each scene  
- Include backup simpler descriptions for complex shots
- Test key shots individually before full video generation
- Allow extra time for character consistency across shots
- Consider generating shots in batches for better consistency"""
        
        # Store the AI video script in database
        script_data = AIVideoScriptResponse(
            original_prompt=request.prompt,
            generated_script=generated_script,
            video_type=request.video_type or "general",
            duration=request.duration or "short",
            visual_style=request.visual_style or "cinematic",
            target_platform=request.target_platform or "general",
            mood=request.mood or "professional",
            shot_count=shot_count,
            estimated_production_time=production_time,
            ai_generation_tips=ai_tips
        )
        
        await db.ai_video_scripts.insert_one(script_data.dict())
        
        return script_data
        
    except Exception as e:
        logger.error(f"Error generating AI video script: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating AI video script: {str(e)}")

# Voice and TTS Endpoints

def extract_clean_script(raw_script):
    """
    Extract only the actual spoken content from a formatted video script.
    Removes ALL production elements and keeps ONLY what should be spoken in the final video.
    
    This includes removing:
    - Timestamps (0:00), (0:00-0:03)
    - Scene descriptions [SCENE START: ...]
    - Speaker/narrator directions (Expert), (Narrator), (Person Speaking)
    - Visual and sound cues **(VISUAL CUE:**, **(SOUND:**
    - Section headers (TARGET DURATION, VIDEO TYPE, etc.)
    - Production notes and metadata
    - Bullet points and formatting instructions
    """
    
    lines = raw_script.strip().split('\n')
    spoken_content = []
    
    # Section headers and metadata to completely skip
    skip_sections = [
        'TARGET DURATION', 'VIDEO TYPE', 'VIDEO SCRIPT', 'SCRIPT:', 'KEY RETENTION ELEMENTS',
        'NOTES:', 'RETENTION ELEMENTS:', 'ADJUSTMENTS:', 'OPTIMIZATION:', 'METRICS:',
        'NOTES', 'SCRIPT', 'DURATION', 'TYPE', 'KEY CONSIDERATIONS', 'RATIONALE:',
        'END.', '**KEY CONSIDERATIONS', '**END**'
    ]
    
    # Track if we're in a metadata section
    in_metadata_section = False
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip visual and sound cues completely
        if line.startswith('**(VISUAL CUE:') or line.startswith('**(SOUND:') or line.startswith('**(VISUAL'):
            continue
            
        # Skip lines that start with bold section markers
        if line.startswith('**[') and line.endswith(']**') or line.startswith('**SCENE'):
            continue
        
        # Check for section headers - skip entire sections
        line_upper = line.upper()
        if any(line_upper.startswith(section) or section in line_upper for section in skip_sections):
            in_metadata_section = True
            continue
        
        # Skip bullet points and lists (metadata sections)
        if line.startswith('*') or line.startswith('•') or line.startswith('-') or line.startswith('◦'):
            in_metadata_section = True
            continue
        
        # If we encounter what looks like actual content after metadata, reset flag
        if in_metadata_section and (line.startswith('(') or line.startswith('[') or line.count('.') > 1):
            in_metadata_section = False
        
        # Skip if still in metadata section
        if in_metadata_section:
            continue
        
        # Skip standalone timestamps - handle both single and range formats
        if re.match(r'^\(\d+:\d+\s*[-–]\s*\d+:\d+\)$', line):  # (0:00-0:03)
            continue
        if re.match(r'^\(\d+:\d+\)$', line):  # (0:00)
            continue
        
        # Skip pure scene descriptions in brackets
        if re.match(r'^\[.*\]$', line):
            continue
            
        # Skip standalone speaker directions - ENHANCED to catch more patterns
        speaker_patterns = [
            r'^\([^)]*(?:Narrator|Host|Speaker|VO|Voiceover|Testimonial|Expert|Person Speaking)[^)]*\)$',
            r'^\([^)]*(?:Intimate|urgent|louder|direct|Hopeful|encouraging|Empowering|strong|quick|friendly)[^)]*\)$',
            r'^\(Voiceover[^)]*\)$',
            r'^\([^)]*Speaking[^)]*\)$'
        ]
        skip_line = False
        for pattern in speaker_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                skip_line = True
                break
        if skip_line:
            continue
            
        # Now extract actual spoken content from mixed lines
        # Remove timestamps at the beginning or anywhere in the line - handle both formats
        line = re.sub(r'\(\d+:\d+\s*[-–]\s*\d+:\d+\)', '', line)  # (0:00-0:03)
        line = re.sub(r'\(\d+:\d+\)', '', line)  # (0:00)
        
        # Remove scene descriptions in brackets
        line = re.sub(r'\[.*?\]', '', line)
        
        # Remove visual and sound cues
        line = re.sub(r'\*\*\(VISUAL CUE:[^)]*\)\*\*', '', line)
        line = re.sub(r'\*\*\(SOUND:[^)]*\)\*\*', '', line)
        
        # Remove speaker directions - ENHANCED patterns
        line = re.sub(r'\([^)]*(?:Narrator|Host|Speaker|VO|Voiceover|Testimonial|Expert|Person Speaking)[^)]*\)', '', line, re.IGNORECASE)
        line = re.sub(r'\([^)]*(?:Intimate|urgent|louder|direct|Hopeful|encouraging|Empowering|strong|quick|friendly)[^)]*\)', '', line, re.IGNORECASE)
        line = re.sub(r'\([^)]*(?:tone|music|sound|audio|video|cut|scene|transition|relatable|Genuine)[^)]*\)', '', line, re.IGNORECASE)
        line = re.sub(r'\([^)]*(?:–|—)[^)]*\)', '', line)  # Remove parentheses with dashes (speaker directions)
        
        # Remove standalone speaker identifiers in parentheses
        line = re.sub(r'\(Expert\)', '', line, re.IGNORECASE)
        line = re.sub(r'\(Person Speaking[^)]*\)', '', line, re.IGNORECASE)
        line = re.sub(r'\(Voiceover[^)]*\)', '', line, re.IGNORECASE)
        
        # Clean up the line
        line = line.strip()
        
        # Only keep lines that have substantial spoken content
        if line and len(line) > 3:
            # Remove markdown formatting
            line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # Bold
            line = re.sub(r'\*([^*]+)\*', r'\1', line)      # Italic
            line = re.sub(r'__([^_]+)__', r'\1', line)      # Underline
            
            # Remove any remaining isolated parentheses or brackets
            line = re.sub(r'^\s*[\[\]()]+\s*$', '', line)
            
            # Clean up extra spaces and normalize punctuation
            line = re.sub(r'\s+', ' ', line).strip()
            
            # Only add if it's not just punctuation or whitespace
            if line and not re.match(r'^[\s\[\]().,!?-]*$', line):
                spoken_content.append(line)
    
    # Join all spoken content
    final_script = ' '.join(spoken_content)
    
    # Final cleanup
    final_script = re.sub(r'\s+', ' ', final_script)  # Multiple spaces
    final_script = re.sub(r'\s*\.\.\.\s*', '... ', final_script)  # Normalize ellipses
    final_script = re.sub(r'\s*!\s*', '! ', final_script)  # Normalize exclamation
    final_script = re.sub(r'\s*\?\s*', '? ', final_script)  # Normalize questions
    final_script = re.sub(r'\s*,\s*', ', ', final_script)  # Normalize commas
    
    # Remove any remaining stray brackets or parentheses
    final_script = re.sub(r'[\[\]()]+', '', final_script)
    
    # Final timestamp cleanup - catch any remaining timestamp patterns
    final_script = re.sub(r'\b\d+:\d+\s*[-–]\s*\d+:\d+\b', '', final_script)
    final_script = re.sub(r'\b\d+:\d+\b', '', final_script)  # Single timestamps
    
    final_script = re.sub(r'\s+', ' ', final_script).strip()
    
    # If result is too short, try extracting quoted content as fallback
    if len(final_script) < 20:
        quoted_content = re.findall(r'"([^"]+)"', raw_script)
        if quoted_content:
            final_script = ' '.join(quoted_content)
        else:
            # Last resort: very basic cleanup
            fallback = raw_script
            # Remove common patterns
            fallback = re.sub(r'\([^)]*\)', ' ', fallback)
            fallback = re.sub(r'\[[^]]*\]', ' ', fallback)
            fallback = re.sub(r'^\s*[A-Z\s:]+\s*$', '', fallback, flags=re.MULTILINE)
            fallback = re.sub(r'^\s*\*.*$', '', fallback, flags=re.MULTILINE)
            fallback = ' '.join(fallback.split())
            if len(fallback.strip()) > len(final_script):
                final_script = fallback
    
    return final_script.strip()

@api_router.get("/voices", response_model=List[VoiceOption])
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices = await edge_tts.list_voices()
        
        # Filter and format voices for better user experience
        voice_options = []
        
        # Select popular voices with good variety
        popular_voices = {
            "en-US-AriaNeural": {"display": "Aria (US Female - Natural)", "gender": "Female"},
            "en-US-DavisNeural": {"display": "Davis (US Male - Natural)", "gender": "Male"}, 
            "en-US-JennyNeural": {"display": "Jenny (US Female - Friendly)", "gender": "Female"},
            "en-US-GuyNeural": {"display": "Guy (US Male - Professional)", "gender": "Male"},
            "en-GB-SoniaNeural": {"display": "Sonia (UK Female)", "gender": "Female"},
            "en-GB-RyanNeural": {"display": "Ryan (UK Male)", "gender": "Male"},
            "en-AU-NatashaNeural": {"display": "Natasha (Australian Female)", "gender": "Female"},
            "en-AU-WilliamNeural": {"display": "William (Australian Male)", "gender": "Male"},
            "en-CA-ClaraNeural": {"display": "Clara (Canadian Female)", "gender": "Female"},
            "en-CA-LiamNeural": {"display": "Liam (Canadian Male)", "gender": "Male"}
        }
        
        for voice in voices:
            voice_name = voice.get('ShortName', '')  # Use ShortName instead of Name
            if voice_name in popular_voices:
                voice_info = popular_voices[voice_name]
                voice_options.append(VoiceOption(
                    name=voice_name,
                    display_name=voice_info["display"],
                    language=voice.get('Locale', 'en-US'),
                    gender=voice_info["gender"]
                ))
        
        # If no popular voices found, add first 10 English voices
        if not voice_options:
            count = 0
            for voice in voices:
                if voice.get('Locale', '').startswith('en-') and count < 10:
                    voice_name = voice.get('ShortName', '')
                    gender = voice.get('Gender', 'Unknown')
                    locale = voice.get('Locale', 'en-US')
                    
                    # Create display name from ShortName
                    name_part = voice_name.split('-')[-1].replace('Neural', '')
                    display_name = f"{name_part} ({locale} {gender})"
                    
                    voice_options.append(VoiceOption(
                        name=voice_name,
                        display_name=display_name,
                        language=locale,
                        gender=gender
                    ))
                    count += 1
        
        # Sort by gender and then by name for better UI organization
        voice_options.sort(key=lambda x: (x.gender, x.display_name))
        
        return voice_options
        
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")

@api_router.post("/generate-audio", response_model=AudioResponse)
async def generate_audio(request: TextToSpeechRequest):
    """Generate audio from text using selected voice"""
    try:
        # Clean the text for better TTS (remove formatting)
        original_text = request.text.strip()
        if not original_text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Debug logging
        logger.info(f"Received TTS request with voice: {request.voice_name}")
        logger.info(f"Original text (first 200 chars): {original_text[:200]}...")
        
        # Use sophisticated script cleaning
        clean_text = extract_clean_script(original_text)
        
        if not clean_text.strip():
            raise HTTPException(status_code=400, detail="After cleaning, no readable text remains")
        
        logger.info(f"Cleaned text (first 200 chars): {clean_text[:200]}...")
        logger.info(f"Text reduction: {len(original_text)} → {len(clean_text)} chars")
        
        # Create TTS communication
        communicate = edge_tts.Communicate(clean_text, request.voice_name)
        
        # Generate audio in memory
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="Failed to generate audio data")
        
        # Convert to base64 for frontend
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return AudioResponse(
            audio_base64=audio_base64,
            voice_used=request.voice_name,
            duration_seconds=len(audio_data) / 16000  # Rough estimation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

@api_router.post("/generate-avatar-video", response_model=AvatarVideoResponse)
async def generate_avatar_video(request: AvatarVideoRequest):
    """Generate an avatar video from audio using AI-powered lip sync"""
    try:
        logger.info("Starting avatar video generation")
        
        if not request.audio_base64 or request.audio_base64.strip() == "":
            raise HTTPException(status_code=400, detail="Audio data is required")
        
        # Generate avatar video in a separate thread to avoid blocking
        import concurrent.futures
        import asyncio
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                avatar_generator.generate_avatar_video,
                request.audio_base64,
                request.avatar_image_path
            )
        
        logger.info(f"Avatar video generation completed successfully. Video size: {len(result['video_base64'])} chars")
        
        return AvatarVideoResponse(
            video_base64=result["video_base64"],
            duration_seconds=result["duration_seconds"],
            request_id=result["request_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating avatar video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating avatar video: {str(e)}")

@api_router.post("/generate-enhanced-avatar-video", response_model=EnhancedAvatarVideoResponse)
async def generate_enhanced_avatar_video(request: EnhancedAvatarVideoRequest):
    """Generate an enhanced avatar video with realistic AI avatars and context-aware backgrounds"""
    try:
        logger.info("Starting enhanced avatar video generation")
        
        if not request.audio_base64 or request.audio_base64.strip() == "":
            raise HTTPException(status_code=400, detail="Audio data is required")
        
        # Validate avatar option
        if request.avatar_option not in ["default", "upload", "ai_generated"]:
            raise HTTPException(status_code=400, detail="Invalid avatar option")
        
        # Validate user image if upload option is selected
        if request.avatar_option == "upload" and not request.user_image_base64:
            raise HTTPException(status_code=400, detail="User image is required for upload option")
        
        # Generate enhanced avatar video in a separate thread to avoid blocking
        import concurrent.futures
        import asyncio
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                enhanced_avatar_generator.generate_enhanced_avatar_video,
                request.audio_base64,
                request.avatar_option,
                request.user_image_base64,
                request.script_text or ""
            )
        
        logger.info(f"Enhanced avatar video generation completed successfully. Video size: {len(result['video_base64'])} chars")
        
        return EnhancedAvatarVideoResponse(
            video_base64=result["video_base64"],
            duration_seconds=result["duration_seconds"],
            request_id=result["request_id"],
            avatar_option=result["avatar_option"],
            script_segments=result["script_segments"],
            sadtalker_used=result["sadtalker_used"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating enhanced avatar video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating enhanced avatar video: {str(e)}")

@api_router.post("/generate-ultra-realistic-avatar-video", response_model=UltraRealisticAvatarVideoResponse)
async def generate_ultra_realistic_avatar_video(request: UltraRealisticAvatarVideoRequest):
    """Generate ultra-realistic avatar video with AI-generated faces, perfect lip-sync, and dynamic backgrounds"""
    try:
        logger.info("Starting ultra-realistic avatar video generation")
        
        if not request.audio_base64 or request.audio_base64.strip() == "":
            raise HTTPException(status_code=400, detail="Audio data is required")
        
        # Validate avatar style
        if request.avatar_style not in ["business_professional", "casual"]:
            raise HTTPException(status_code=400, detail="Invalid avatar style")
        
        # Validate gender
        if request.gender not in ["male", "female", "diverse"]:
            raise HTTPException(status_code=400, detail="Invalid gender")
        
        # Validate avatar index
        if request.avatar_index not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Invalid avatar index")
        
        # Generate ultra-realistic avatar video in a separate thread to avoid blocking
        import concurrent.futures
        import asyncio
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                ultra_realistic_avatar_generator.generate_ultra_realistic_video,
                request.audio_base64,
                request.avatar_style,
                request.gender,
                request.avatar_index,
                request.script_text or ""
            )
        
        logger.info(f"Ultra-realistic avatar video generation completed successfully. Video size: {len(result['video_base64'])} chars")
        
        return UltraRealisticAvatarVideoResponse(
            video_base64=result["video_base64"],
            duration_seconds=result["duration_seconds"],
            request_id=result["request_id"],
            avatar_style=result["avatar_style"],
            gender=result["gender"],
            avatar_index=result["avatar_index"],
            script_segments=result["script_segments"],
            background_contexts=result["background_contexts"],
            ai_model_used=result["ai_model_used"],
            quality_level=result["quality_level"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ultra-realistic avatar video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating ultra-realistic avatar video: {str(e)}")

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

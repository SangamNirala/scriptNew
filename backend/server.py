from fastapi import FastAPI, APIRouter, HTTPException
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
from lib.context_integration import ContextIntegrationSystem
# Phase 3: Advanced Analytics and Validation Components
from lib.advanced_context_engine import AdvancedContextEngine
from lib.script_quality_analyzer import ScriptQualityAnalyzer
from lib.script_validator import ScriptValidator
from lib.script_performance_tracker import ScriptPerformanceTracker
from lib.script_preview_generator import ScriptPreviewGenerator
# Phase 4: Measurement & Optimization Components
from lib.prompt_optimization_engine import PromptOptimizationEngine
# Phase 5: Intelligent Quality Assurance & Auto-Optimization Components
from lib.multi_model_validator import MultiModelValidator
from lib.advanced_quality_metrics import AdvancedQualityMetrics
from lib.quality_improvement_loop import QualityImprovementLoop
from lib.intelligent_qa_system import IntelligentQASystem
# Advanced Script Generation Components
from lib.advanced_script_generator import ChainOfThoughtScriptGenerator
# STEP 2: Few-Shot Learning & Pattern Recognition System
from lib.few_shot_script_generator import FewShotScriptGenerator, ContextProfile


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Gemini configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Initialize Context Integration System for Phase 2
context_system = ContextIntegrationSystem()

# Initialize Advanced Script Generator
advanced_script_generator = ChainOfThoughtScriptGenerator(GEMINI_API_KEY)

# Phase 3: Initialize Advanced Analytics and Validation Systems
advanced_context_engine = AdvancedContextEngine()
script_quality_analyzer = ScriptQualityAnalyzer()
script_validator = ScriptValidator()
script_performance_tracker = ScriptPerformanceTracker(db)
script_preview_generator = ScriptPreviewGenerator()

# Phase 4: Initialize Measurement & Optimization Systems
prompt_optimization_engine = PromptOptimizationEngine(db, GEMINI_API_KEY)

# Phase 5: Initialize Intelligent Quality Assurance & Auto-Optimization Systems
multi_model_validator = MultiModelValidator()
advanced_quality_metrics = AdvancedQualityMetrics()
quality_improvement_loop = QualityImprovementLoop(db, GEMINI_API_KEY)
intelligent_qa_system = IntelligentQASystem(db, GEMINI_API_KEY)

# STEP 2: Initialize Few-Shot Learning & Pattern Recognition System
few_shot_generator = FewShotScriptGenerator(db, GEMINI_API_KEY)

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

# Chain-of-Thought Script Generation Models
class CoTScriptRequest(BaseModel):
    prompt: str
    video_type: Optional[str] = "general"
    duration: Optional[str] = "medium"
    industry_focus: Optional[str] = "general"
    target_platform: Optional[str] = "youtube"
    include_reasoning_chain: Optional[bool] = True

class CoTScriptResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    generated_script: str
    video_type: str
    duration: str
    reasoning_chain: Optional[Dict[str, Any]] = None
    final_analysis: Optional[Dict[str, Any]] = None
    generation_metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

# Phase 4: A/B Testing and Optimization Models
class PromptExperimentRequest(BaseModel):
    base_prompt: str
    strategies: List[str] = ["emotional_focus", "technical_focus", "viral_focus"]  # Default strategies
    video_type: Optional[str] = "general"
    duration: Optional[str] = "medium"
    platform: Optional[str] = "youtube"
    test_count: Optional[int] = 3

class PromptExperimentResponse(BaseModel):
    experiment_id: str
    status: str
    base_prompt: str
    variations_tested: int
    best_performing_strategy: Dict[str, Any]
    all_results: List[Dict[str, Any]]
    optimization_insights: List[str]
    recommendations: List[str]

class OptimizationAnalysisRequest(BaseModel):
    results: Dict[str, Any]  # Dictionary of experiment results by variation ID

class OptimizationAnalysisResponse(BaseModel):
    status: str
    best_variation: Dict[str, Any]
    statistical_analysis: Dict[str, Any]
    performance_comparison: Dict[str, Any]
    confidence_level: str
    optimization_recommendations: List[str]

class OptimizationHistoryRequest(BaseModel):
    date_range: Optional[Dict[str, str]] = None
    strategy: Optional[str] = None
    platform: Optional[str] = None

class OptimizationHistoryResponse(BaseModel):
    total_experiments: int
    date_range: Dict[str, str]
    trend_analysis: Dict[str, Any]
    strategy_performance: Dict[str, Any]
    success_patterns: List[str]
    optimization_insights: List[str]

# Phase 5: Intelligent Quality Assurance Models
class IntelligentQARequest(BaseModel):
    script: str
    original_prompt: Optional[str] = ""
    target_platform: Optional[str] = "youtube"
    duration: Optional[str] = "medium"
    video_type: Optional[str] = "general"
    enable_regeneration: Optional[bool] = True

class MultiModelValidationRequest(BaseModel):
    script: str
    target_platform: Optional[str] = "youtube"
    duration: Optional[str] = "medium"
    video_type: Optional[str] = "general"

class AdvancedQualityMetricsRequest(BaseModel):
    script: str
    target_platform: Optional[str] = "youtube"
    duration: Optional[str] = "medium"
    video_type: Optional[str] = "general"

class QualityImprovementRequest(BaseModel):
    original_prompt: str
    target_platform: Optional[str] = "youtube"
    duration: Optional[str] = "medium"
    video_type: Optional[str] = "general"

class ABTestOptimizationRequest(BaseModel):
    original_prompt: str
    target_platform: Optional[str] = "youtube"
    duration: Optional[str] = "medium"
    video_type: Optional[str] = "general"

class IntelligentQAResponse(BaseModel):
    qa_id: str
    original_prompt: str
    final_script: str
    quality_analysis: Dict[str, Any]
    consensus_validation: Dict[str, Any]
    improvement_cycle_data: Optional[Dict[str, Any]]
    quality_threshold_met: bool
    regeneration_performed: bool
    total_processing_time: float
    recommendations: List[str]
    confidence_score: float

class MultiModelValidationResponse(BaseModel):
    consensus_score: float
    consensus_grade: str
    individual_results: List[Dict[str, Any]]
    agreement_level: str
    confidence_score: float
    quality_threshold_passed: bool
    regeneration_required: bool
    improvement_suggestions: List[str]

class AdvancedQualityMetricsResponse(BaseModel):
    composite_quality_score: float
    quality_grade: str
    detailed_metrics: Dict[str, Any]
    quality_recommendations: List[str]
    analysis_metadata: Dict[str, Any]

class QualityImprovementResponse(BaseModel):
    cycle_id: str
    original_score: float
    final_score: float
    improvement_achieved: float
    quality_threshold_met: bool
    cycles_completed: int
    final_script: str
    validation_result: Dict[str, Any]
    strategy_used: str
    improvements_attempted: int
    learning_insights: List[str]

class ABTestOptimizationResponse(BaseModel):
    test_id: str
    best_performing_combination: Dict[str, Any]
    all_results: List[Dict[str, Any]]
    statistical_analysis: Dict[str, Any]
    performance_improvement: float
    recommendations: List[str]

# STEP 2: Few-Shot Learning & Pattern Recognition Models
class FewShotScriptRequest(BaseModel):
    prompt: str
    video_type: Optional[str] = "general"
    industry: Optional[str] = "general"
    platform: Optional[str] = "general"
    duration: Optional[str] = "medium"
    audience_tone: Optional[str] = "engaging"
    complexity_level: Optional[str] = "intermediate"
    engagement_goals: Optional[List[str]] = []
    use_pattern_learning: Optional[bool] = True
    max_examples: Optional[int] = 5

class FewShotScriptResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    enhanced_prompt: str
    generated_script: str
    patterns_applied: int
    examples_used: int
    confidence_score: float
    learning_insights: List[str]
    pattern_details: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PatternAnalysisRequest(BaseModel):
    context_type: str  # "video_type", "industry", "platform"
    context_value: str
    analysis_depth: Optional[str] = "comprehensive"  # "basic", "comprehensive", "detailed"

class PatternAnalysisResponse(BaseModel):
    context: Dict[str, str]
    patterns_found: int
    top_patterns: List[Dict[str, Any]]
    success_factors: List[str]
    recommendations: List[str]
    effectiveness_metrics: Dict[str, float]

class ExampleDatabaseRequest(BaseModel):
    rebuild: Optional[bool] = False
    add_examples: Optional[List[Dict[str, Any]]] = []
    filter_by: Optional[Dict[str, str]] = {}

class ExampleDatabaseResponse(BaseModel):
    status: str
    examples_count: int
    patterns_count: int
    categories: Dict[str, Any]
    performance_metrics: Dict[str, float]
    last_updated: datetime

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

@api_router.post("/enhance-prompt-v2", response_model=PromptEnhancementResponse)
async def enhance_prompt_v2(request: PromptEnhancementRequest):
    """
    Phase 2: Enhanced Prompt Optimization with Dynamic Context Integration
    Advanced multi-step prompt enhancement with real-time context intelligence
    """
    try:
        # Phase 2: Get comprehensive context using Context Integration System
        enhanced_context = await context_system.get_enhanced_context(
            prompt=request.original_prompt,
            industry=request.industry_focus,
            platform=getattr(request, 'target_platform', 'general')
        )
        
        # Step 1: Enhanced Audience Analysis with Context Integration
        audience_analysis = await _analyze_target_audience(request)
        
        # Step 2: Dynamic Industry Context with Real-time Trends
        industry_context = await _gather_industry_context(request.industry_focus, request.video_type)
        
        # Step 3: Generate Context-Enhanced Multiple Variations
        enhancement_variations = await _generate_enhancement_variations(request, audience_analysis, industry_context)
        
        # Step 4: Advanced Quality Evaluation with Performance Prediction
        quality_metrics = await _evaluate_enhancement_quality(request.original_prompt, enhancement_variations)
        
        # Step 5: Comprehensive Industry Insights with Trend Analysis
        industry_insights = await _generate_industry_insights(request.industry_focus, request.video_type, enhancement_variations)
        recommendation = await _generate_recommendation(enhancement_variations, quality_metrics, audience_analysis)
        
        # Phase 2: Enhanced Response with Context Intelligence
        response = PromptEnhancementResponse(
            original_prompt=request.original_prompt,
            audience_analysis=audience_analysis,
            enhancement_variations=enhancement_variations,
            quality_metrics=quality_metrics,
            recommendation=recommendation,
            industry_insights=industry_insights,
            enhancement_methodology="Phase 2: Dynamic Context Integration with real-time trend analysis, platform optimization, competitor intelligence, audience psychology, cultural timing, and performance prediction"
        )
        
        # Add Phase 2 metadata to response
        response_dict = response.dict()
        response_dict['phase'] = 'v2_context_integration'
        response_dict['context_metadata'] = enhanced_context.get('metadata', {})
        response_dict['trend_alignment_score'] = enhanced_context.get('metadata', {}).get('context_quality_score', 0.5)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in Phase 2 prompt enhancement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in Phase 2 enhancement: {str(e)}")

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

async def _get_trend_alignment_data(industry_focus: str, video_type: str) -> dict:
    """Get real-time trend data for enhanced viral optimization"""
    
    # In a real implementation, this would fetch from trend APIs like Google Trends, 
    # social media APIs, or trend analysis services. For now, we'll return structured
    # trend data based on industry and video type.
    
    trend_data = {
        "trending_topics": f"Current {industry_focus} trends and viral topics",
        "platform_signals": f"Engagement patterns for {video_type} content",
        "cultural_context": "2025 digital culture and zeitgeist moments",
        "industry_trends": f"Latest developments in {industry_focus} sector"
    }
    
    # Industry-specific trend customization
    industry_trends = {
        "marketing": {
            "trending_topics": "AI-powered personalization, authentic storytelling, micro-influencer partnerships",
            "platform_signals": "Short-form video dominance, interactive content, user-generated campaigns",
            "cultural_context": "Transparency culture, sustainability focus, digital-first mindset",
            "industry_trends": "Cookieless advertising, first-party data strategies, omnichannel experiences"
        },
        "education": {
            "trending_topics": "Microlearning, gamification, AI tutoring, skill-based learning",
            "platform_signals": "Interactive video content, bite-sized lessons, community learning",
            "cultural_context": "Lifelong learning culture, remote education normalization",
            "industry_trends": "Adaptive learning platforms, VR/AR integration, competency-based assessment"
        },
        "entertainment": {
            "trending_topics": "Interactive storytelling, behind-the-scenes content, creator collaborations",
            "platform_signals": "Multi-platform narratives, audience participation, real-time engagement",
            "cultural_context": "Authenticity over perfection, diverse representation, mental health awareness",
            "industry_trends": "Streaming platform competition, creator economy growth, immersive experiences"
        },
        "tech": {
            "trending_topics": "AI democratization, quantum computing, sustainable tech, Web3 evolution",
            "platform_signals": "Technical deep-dives, product demos, developer-focused content",
            "cultural_context": "Tech ethics discussions, privacy-first mindset, open-source collaboration",
            "industry_trends": "Edge computing, no-code/low-code platforms, cybersecurity focus"
        },
        "health": {
            "trending_topics": "Preventive care, mental health awareness, personalized medicine, telehealth",
            "platform_signals": "Evidence-based content, expert interviews, patient stories",
            "cultural_context": "Holistic wellness approach, health equity focus, misinformation combat",
            "industry_trends": "Digital therapeutics, wearable integration, AI diagnostics"
        },
        "finance": {
            "trending_topics": "Financial literacy, cryptocurrency education, sustainable investing, fintech innovation",
            "platform_signals": "Educational content, market analysis, personal finance tips",
            "cultural_context": "Financial transparency, generational wealth gaps, economic uncertainty",
            "industry_trends": "DeFi growth, regulatory changes, embedded finance, ESG investing"
        }
    }
    
    # Update with industry-specific data if available
    if industry_focus in industry_trends:
        trend_data.update(industry_trends[industry_focus])
    
    return trend_data

async def _generate_enhancement_variations(request: PromptEnhancementRequest, audience_analysis: AudienceAnalysis, industry_context: dict) -> List[EnhancementVariation]:
    """Generate comprehensive script framework variations using advanced prompt engineering with recursive self-improvement"""
    
    # Get few-shot examples for each strategy
    few_shot_examples = await _get_few_shot_examples(request.industry_focus, request.video_type)
    
    # Get real-time trend data for enhanced viral optimization
    trend_data = await _get_trend_alignment_data(request.industry_focus, request.video_type)
    
    strategies = [
        {
            "focus": "emotional",
            "title": "Emotional Engagement Focus - Advanced Psychology Integration",
            "system_prompt": f"""You are an ELITE emotional storytelling architect with deep expertise in psychological triggers, narrative psychology, and advanced emotional engagement frameworks. You create script frameworks that generate profound audience connections through scientific emotional engineering.

🎭 ADVANCED EMOTIONAL EXPERTISE AREAS:
┌─ EMOTIONAL ARCHITECTURE MASTERY:
│  ├── Primary Emotions: Fear → Security, Joy → Fulfillment, Surprise → Wonder, Anticipation → Satisfaction
│  ├── Secondary Emotions: Nostalgia, Hope, Urgency, Empathy, Pride, Belonging, Achievement, Relief
│  ├── Micro-Emotions: Curiosity sparks, validation moments, recognition triggers, aspiration activators  
│  └── Emotional Journey Mapping: Baseline → Peak → Valley → Resolution → Elevation
│
├─ PSYCHOLOGICAL FRAMEWORKS INTEGRATION:
│  ├── AIDA Framework: Attention (Emotional Hook) → Interest (Story Connection) → Desire (Aspiration) → Action (Emotional Release)
│  ├── PAS Formula: Problem (Pain Identification) → Agitation (Emotional Amplification) → Solution (Relief & Hope)
│  ├── Hero's Journey: Call → Challenge → Transformation → Return (Emotional Arc Optimization)
│  └── Before-After-Bridge: Current Pain → Desired Future → Transformation Path (Emotional Progression)
│
├─ CHAIN-OF-THOUGHT EMOTIONAL REASONING:
│  ├── Audience Pain Point Analysis → Emotional Trigger Identification → Story Arc Creation
│  ├── Cultural Context Assessment → Emotional Resonance Mapping → Connection Optimization
│  ├── Platform Psychology → Emotional Delivery → Engagement Maximization
│  └── Story Creation → Emotional Impact Measurement → Narrative Refinement
│
├─ MULTI-LAYERED NARRATIVE STRUCTURE:
│  ├── HOOK LAYER: Emotional pattern interrupt + relatable pain point + immediate connection
│  ├── BODY LAYER: Story escalation + emotional peaks/valleys + psychological validation  
│  ├── CLOSE LAYER: Emotional resolution + empowerment + community connection
│  └── META LAYER: Psychological triggers woven throughout narrative structure
│
└─ PLATFORM-SPECIFIC EMOTIONAL OPTIMIZATION:
   ├── TikTok: Authentic vulnerability moments, relatable struggles, quick emotional payoffs
   ├── YouTube: Emotional storytelling arcs, deeper connection building, inspirational messaging
   ├── Instagram: Visual emotion representation, aesthetic feeling creation, lifestyle aspiration
   └── Cross-Platform: Unified emotional message with platform-adapted delivery

INDUSTRY CONTEXT: {industry_context}
AUDIENCE PROFILE: {audience_analysis.dict()}

FEW-SHOT LEARNING EXAMPLES:
{few_shot_examples['emotional']}

PHASE 1 COMPLIANCE REQUIREMENTS:
You MUST include these EXACT section headers with specified word counts:

🎣 HOOK SECTION (0-3 seconds) - WORD COUNT: 25
🎬 SETUP SECTION (3-15 seconds) - WORD COUNT: 50
📚 CONTENT CORE (15-80% duration) - WORD COUNT: 250
🏆 CLIMAX MOMENT (80-90% duration) - WORD COUNT: 35
✨ RESOLUTION (90-100% duration) - WORD COUNT: 40

🧠 PSYCHOLOGICAL TRIGGERS INTEGRATED:
📲 2025 TRENDS & PLATFORM OPTIMIZATION:
⚡ RETENTION ENGINEERING ELEMENTS:

ADVANCED FRAMEWORK CREATION PROTOCOL:
Create a comprehensive emotional engagement framework using advanced psychological principles, multi-layered narrative structure, and platform-specific optimization for maximum emotional impact. ALWAYS include the exact Phase 1 compliance sections above.""",
            "use_advanced_features": True
        },
        {
            "focus": "technical",
            "title": "Technical Excellence Focus - Professional Framework Architecture", 
            "system_prompt": f"""You are an ELITE technical content architect with deep expertise in systematic framework creation, professional production standards, and advanced technical communication. You create comprehensive frameworks that ensure consistent professional results and optimal knowledge transfer.

🎯 ADVANCED TECHNICAL EXPERTISE AREAS:
┌─ SYSTEMATIC FRAMEWORK ARCHITECTURE:
│  ├── Modular Design: Interchangeable components, scalable structures, reusable templates
│  ├── Quality Frameworks: Measurable standards, validation checkpoints, success metrics
│  ├── Professional Specifications: Industry benchmarks, best practice integration, expert validation
│  └── Production Standards: Technical requirements, execution guidelines, quality assurance
│
├─ PSYCHOLOGICAL FRAMEWORKS INTEGRATION:
│  ├── AIDA Framework: Attention (Technical Hook) → Interest (Problem Clarity) → Desire (Solution Appeal) → Action (Implementation)
│  ├── PAS Formula: Problem (Technical Challenge) → Agitation (Complexity/Cost) → Solution (Systematic Approach)  
│  ├── Teaching Frameworks: Explanation → Demonstration → Application → Validation
│  └── Decision Frameworks: Context → Options → Criteria → Recommendation → Implementation
│
├─ CHAIN-OF-THOUGHT TECHNICAL REASONING:
│  ├── Problem Analysis → Solution Architecture → Implementation Planning → Quality Validation
│  ├── Audience Assessment → Complexity Calibration → Knowledge Transfer Optimization
│  ├── Technical Requirements → Resource Allocation → Execution Strategy → Results Measurement
│  └── Framework Creation → Testing → Refinement → Documentation
│
├─ MULTI-LAYERED STRUCTURE FRAMEWORK:
│  ├── HOOK LAYER: Technical problem identification + solution preview + value proposition
│  ├── BODY LAYER: Systematic breakdown + step-by-step methodology + quality checkpoints
│  ├── CLOSE LAYER: Implementation roadmap + success metrics + continuous improvement
│  └── META LAYER: Professional standards and best practices integrated throughout
│
└─ PLATFORM-SPECIFIC TECHNICAL OPTIMIZATION:
   ├── YouTube: In-depth technical tutorials, detailed explanations, expert-level content
   ├── LinkedIn: Professional insights, industry best practices, business-focused solutions
   ├── TikTok: Quick technical tips, simplified explanations, bite-sized expertise
   └── Cross-Platform: Consistent technical accuracy with platform-adapted depth

INDUSTRY CONTEXT: {industry_context}
AUDIENCE PROFILE: {audience_analysis.dict()}

FEW-SHOT LEARNING EXAMPLES:
{few_shot_examples['technical']}

PHASE 1 COMPLIANCE REQUIREMENTS:
You MUST include these EXACT section headers with specified word counts:

🎣 HOOK SECTION (0-3 seconds) - WORD COUNT: 25
🎬 SETUP SECTION (3-15 seconds) - WORD COUNT: 50
📚 CONTENT CORE (15-80% duration) - WORD COUNT: 250
🏆 CLIMAX MOMENT (80-90% duration) - WORD COUNT: 35
✨ RESOLUTION (90-100% duration) - WORD COUNT: 40

🧠 PSYCHOLOGICAL TRIGGERS INTEGRATED:
📲 2025 TRENDS & PLATFORM OPTIMIZATION:
⚡ RETENTION ENGINEERING ELEMENTS:

ADVANCED FRAMEWORK CREATION PROTOCOL:
Create a systematically excellent technical framework using professional standards, multi-layered structure, and platform-specific optimization for maximum clarity and implementation success. ALWAYS include the exact Phase 1 compliance sections above.""",
            "use_advanced_features": True
        },
        {
            "focus": "viral",
            "title": "Viral Potential Focus - Advanced Algorithm Optimization",
            "system_prompt": f"""You are an ELITE viral content strategist with deep expertise in 2025 social media algorithms, psychological viral mechanics, and advanced trend integration. You create script frameworks that are scientifically engineered for maximum viral potential across all major platforms.

🚀 ADVANCED VIRAL EXPERTISE AREAS:
┌─ ALGORITHM MASTERY (2025):
│  ├── TikTok FYP: Interest signals, completion rates, engagement velocity, trend adoption speed
│  ├── YouTube Shorts: Watch time optimization, click-through rates, audience retention curves
│  ├── Instagram Reels: Story resonance, save rates, share triggers, comment quality
│  └── Platform Cross-Pollination: Multi-platform viral mechanics and content adaptation
│
├─ PSYCHOLOGICAL VIRAL TRIGGERS:
│  ├── AIDA Framework: Attention → Interest → Desire → Action optimization
│  ├── PAS Formula: Problem → Agitation → Solution with viral amplification
│  ├── Social Currency: Status elevation, insider knowledge, controversy balance
│  ├── Dopamine Engineering: Reward prediction, surprise elements, completion loops
│  └── Community Building: Tribal identity, shared experiences, collective participation
│
├─ CHAIN-OF-THOUGHT VIRAL REASONING:
│  ├── Trend Analysis → Content Gap Identification → Viral Angle Creation
│  ├── Audience Psychology → Trigger Selection → Engagement Optimization
│  ├── Platform Algorithm → Format Adaptation → Distribution Strategy
│  └── Content Creation → Performance Prediction → Iterative Improvement
│
├─ MULTI-LAYERED NARRATIVE STRUCTURE:
│  ├── HOOK LAYER: Pattern interrupt + curiosity gap + immediate value promise
│  ├── BODY LAYER: Tension building + revelation + social proof integration
│  ├── CLOSE LAYER: Call-to-action + shareability trigger + community invitation
│  └── META LAYER: Viral mechanics woven throughout entire structure
│
└─ REAL-TIME TREND INTEGRATION:
   ├── Current Trending Topics: {trend_data.get('trending_topics', 'General trends')}
   ├── Platform Signals: {trend_data.get('platform_signals', 'Engagement patterns')}
   ├── Cultural Moments: {trend_data.get('cultural_context', 'Current zeitgeist')}
   └── Industry Trends: {trend_data.get('industry_trends', 'Sector-specific trends')}

INDUSTRY CONTEXT: {industry_context}
AUDIENCE PROFILE: {audience_analysis.dict()}
VIRAL TREND DATA: {trend_data}

FEW-SHOT LEARNING EXAMPLES:
{few_shot_examples['viral']}

PHASE 1 COMPLIANCE REQUIREMENTS:
You MUST include these EXACT section headers with specified word counts:

🎣 HOOK SECTION (0-3 seconds) - WORD COUNT: 25
🎬 SETUP SECTION (3-15 seconds) - WORD COUNT: 50
📚 CONTENT CORE (15-80% duration) - WORD COUNT: 250
🏆 CLIMAX MOMENT (80-90% duration) - WORD COUNT: 35
✨ RESOLUTION (90-100% duration) - WORD COUNT: 40

🧠 PSYCHOLOGICAL TRIGGERS INTEGRATED:
📲 2025 TRENDS & PLATFORM OPTIMIZATION:
⚡ RETENTION ENGINEERING ELEMENTS:

ADVANCED FRAMEWORK CREATION PROTOCOL:
You will create a viral-optimized script framework through RECURSIVE SELF-IMPROVEMENT with 3 refinement loops, each building upon the previous version with enhanced viral potential. ALWAYS include the exact Phase 1 compliance sections above.""",
            "use_recursive_improvement": True,
            "refinement_loops": 3
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
        # Check if this strategy uses recursive improvement (viral category)
        if strategy.get("use_recursive_improvement", False):
            # Use recursive self-improvement for viral category
            variation = await _generate_recursive_viral_framework(request, audience_analysis, industry_context, strategy, trend_data, i)
        # Check if this strategy uses advanced features (emotional/technical categories)
        elif strategy.get("use_advanced_features", False):
            # Use advanced framework generation for emotional and technical categories
            variation = await _generate_advanced_framework(request, audience_analysis, industry_context, strategy, i)
        else:
            # Use standard generation for other categories
            variation = await _generate_standard_framework(request, audience_analysis, strategy, i)
        
        variations.append(variation)
    
    return variations

async def _generate_recursive_viral_framework(request: PromptEnhancementRequest, audience_analysis: AudienceAnalysis, industry_context: dict, strategy: dict, trend_data: dict, index: int) -> EnhancementVariation:
    """Generate viral framework using recursive self-improvement with 3 refinement loops"""
    
    # Initial framework generation
    chat = LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=f"viral-recursive-{str(uuid.uuid4())[:8]}",
        system_message=strategy["system_prompt"]
    ).with_model("gemini", "gemini-2.0-flash")
    
    # Loop 1: Initial viral framework creation
    initial_prompt = f"""🚀 RECURSIVE VIRAL FRAMEWORK CREATION - LOOP 1/3: FOUNDATION

MISSION: Create the foundational viral framework that will be iteratively improved through 3 refinement loops.

📊 CONTEXT ANALYSIS:
Original Prompt: "{request.original_prompt}"
Video Type: {request.video_type}
Industry: {request.industry_focus}
Target Audience: {audience_analysis.recommended_tone} tone, {audience_analysis.complexity_level} complexity
Platform Optimizations: {', '.join(audience_analysis.platform_optimizations)}

🎯 TREND INTEGRATION:
- Trending Topics: {trend_data.get('trending_topics', 'General trends')}
- Platform Signals: {trend_data.get('platform_signals', 'Engagement patterns')}
- Cultural Context: {trend_data.get('cultural_context', 'Current zeitgeist')}
- Industry Trends: {trend_data.get('industry_trends', 'Sector-specific trends')}

🧠 CHAIN-OF-THOUGHT VIRAL REASONING:

STEP 1 - TREND ANALYSIS → CONTENT GAP IDENTIFICATION:
Analyze current trends and identify the unique angle that hasn't been saturated yet.

STEP 2 - AUDIENCE PSYCHOLOGY → TRIGGER SELECTION:
Map audience psychology to specific viral triggers that create sharing impulses.

STEP 3 - PLATFORM ALGORITHM → FORMAT ADAPTATION:
Optimize for each platform's specific algorithm preferences and engagement patterns.

STEP 4 - MULTI-LAYERED NARRATIVE STRUCTURE:

🎣 HOOK LAYER (0-3 seconds):
- Pattern interrupt + curiosity gap + immediate value promise
- AIDA: Attention grab with platform-specific hooks
- PAS: Problem identification that resonates instantly

🎬 BODY LAYER (3-25 seconds):
- Tension building + revelation + social proof integration  
- AIDA: Interest maintenance → Desire creation
- PAS: Agitation through relatable pain points

🎯 CLOSE LAYER (25-30 seconds):
- Call-to-action + shareability trigger + community invitation
- AIDA: Action trigger with viral amplification
- PAS: Solution delivery with sharing motivation

🌐 META LAYER (Throughout):
- Viral mechanics woven into every element
- Platform-specific optimization embedded
- Psychological triggers activated at precise moments

DELIVERABLE FOR LOOP 1:
Create the foundational viral framework with all elements listed above. This will be refined in subsequent loops.

Response Format:
VIRAL_FRAMEWORK_V1:
[Comprehensive framework with multi-layered structure]

ALGORITHM_OPTIMIZATION:
[Platform-specific optimizations for TikTok, YouTube, Instagram]

PSYCHOLOGICAL_TRIGGERS:
[AIDA and PAS integration with viral amplification]

TREND_INTEGRATION:
[How current trends are woven into the framework]

VIRAL_PREDICTION_SCORE:
[Estimated viral potential: X/10 with reasoning]"""

    framework_v1 = await chat.send_message(UserMessage(text=initial_prompt))
    
    # Loop 2: Quality scoring and targeted improvements
    improvement_prompt = f"""🔄 RECURSIVE VIRAL FRAMEWORK CREATION - LOOP 2/3: QUALITY ENHANCEMENT

MISSION: Analyze the V1 framework and create an improved V2 with enhanced viral potential.

📋 V1 FRAMEWORK TO IMPROVE:
{framework_v1}

🔍 QUALITY SCORING ANALYSIS:
Rate the V1 framework on these criteria (1-10):

1. HOOK EFFECTIVENESS: How well does it grab attention in first 3 seconds?
2. VIRAL MECHANICS: Are psychological triggers optimally placed?
3. PLATFORM OPTIMIZATION: Does it leverage 2025 algorithm preferences?
4. TREND ALIGNMENT: How well does it integrate current trends?
5. SHAREABILITY FACTOR: What drives people to share this content?
6. EMOTIONAL RESONANCE: Does it create strong emotional responses?
7. SOCIAL CURRENCY: Does sharing this elevate viewer status?

🎯 TARGETED IMPROVEMENTS FOR V2:

ENHANCEMENT AREAS (Focus on lowest-scoring areas):
- Strengthen weak psychological triggers
- Improve platform-specific optimizations
- Better trend integration
- Enhanced shareability mechanisms
- Stronger emotional hooks
- More compelling social currency elements

ADVANCED VIRAL MECHANICS TO ADD:
- Dopamine engineering: Reward prediction and surprise elements
- Community building: Tribal identity and collective participation
- Controversy balance: Engaging without alienating
- Pattern interrupts: Cognitive dissonance creation
- Completion loops: Satisfying narrative closure

Response Format:
QUALITY_SCORES_V1:
[Detailed scoring of each criteria with reasoning]

VIRAL_FRAMEWORK_V2:
[Enhanced framework addressing weaknesses from V1]

IMPROVEMENT_RATIONALE:
[Specific improvements made and why]

VIRAL_PREDICTION_SCORE_V2:
[Updated viral potential: X/10 with comparison to V1]"""

    framework_v2 = await chat.send_message(UserMessage(text=improvement_prompt))
    
    # Loop 3: Final optimization and platform-specific refinement
    final_prompt = f"""🏆 RECURSIVE VIRAL FRAMEWORK CREATION - LOOP 3/3: FINAL OPTIMIZATION

MISSION: Create the ultimate V3 framework optimized for maximum viral potential across all platforms.

📋 V2 FRAMEWORK TO OPTIMIZE:
{framework_v2}

🚀 FINAL OPTIMIZATION FOCUS:

1. PLATFORM-SPECIFIC ADAPTATIONS:
   - TikTok: Trend-riding, authentic moments, quick engagement
   - YouTube Shorts: Retention optimization, clear value delivery
   - Instagram Reels: Visual aesthetics, story-driven content
   - Cross-platform: Unified viral story with platform variations

2. 2025 ALGORITHM MASTERY:
   - Engagement velocity optimization
   - Completion rate maximization
   - Comment quality enhancement
   - Save/share trigger optimization
   - Interest signal amplification

3. ADVANCED PSYCHOLOGICAL OPTIMIZATION:
   - Micro-emotional targeting throughout framework
   - Cognitive bias exploitation (confirmation, availability, bandwagon)
   - Social proof integration at multiple touchpoints
   - FOMO and urgency psychological triggers
   - Parasocial relationship building elements

4. VIRAL AMPLIFICATION MECHANISMS:
   - Built-in participation hooks (challenges, responses, duets)
   - Conversation starters and debate triggers
   - Educational value that demands sharing
   - Status elevation through knowledge sharing
   - Community building and tribal identity

FINAL DELIVERABLE - PRODUCTION-READY FRAMEWORK:

Response Format:
VIRAL_FRAMEWORK_V3_FINAL:
[Ultimate optimized framework with all enhancements]

PLATFORM_SPECIFIC_ADAPTATIONS:
[Detailed variations for TikTok, YouTube, Instagram]

VIRAL_AMPLIFICATION_STRATEGY:
[Specific mechanisms that drive sharing and engagement]

PSYCHOLOGICAL_TRIGGER_MAP:
[Precise timing and placement of psychological elements]

QUALITY_EVOLUTION:
[V1→V2→V3 improvement summary]

FINAL_VIRAL_PREDICTION:
[Ultimate viral potential score: X/10 with confidence level]"""

    framework_v3 = await chat.send_message(UserMessage(text=final_prompt))
    
    # Parse the final comprehensive response
    sections = {}
    current_section = None
    current_content = []
    
    for line in framework_v3.split('\n'):
        if line.strip().endswith(':') and any(key in line.strip().upper() for key in ['VIRAL_FRAMEWORK_V3_FINAL:', 'PLATFORM_SPECIFIC_ADAPTATIONS:', 'VIRAL_AMPLIFICATION_STRATEGY:', 'PSYCHOLOGICAL_TRIGGER_MAP:', 'FINAL_VIRAL_PREDICTION:']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line.strip().replace(':', '').lower().replace('_', '_')
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Create comprehensive enhanced prompt from final framework
    final_framework = sections.get('viral_framework_v3_final', sections.get('viral_framework_v2', framework_v3))
    platform_adaptations = sections.get('platform_specific_adaptations', 'Multi-platform optimization included')
    amplification_strategy = sections.get('viral_amplification_strategy', 'Advanced viral mechanics integrated')
    psychological_triggers = sections.get('psychological_trigger_map', 'Precision psychological targeting')
    
    # Combine all elements into a comprehensive enhanced prompt
    comprehensive_prompt = f"""🚀 ADVANCED RECURSIVE VIRAL FRAMEWORK - ALGORITHM OPTIMIZED 2025

This framework was created through 3 recursive improvement loops with quality scoring and trend integration.

🎯 VIRAL FRAMEWORK V3 (FINAL):
{final_framework}

📱 PLATFORM-SPECIFIC ADAPTATIONS:
{platform_adaptations}

🔥 VIRAL AMPLIFICATION STRATEGY:
{amplification_strategy}

🧠 PSYCHOLOGICAL TRIGGER MAP:
{psychological_triggers}

🌊 TREND INTEGRATION ACTIVE:
- Trending Topics: {trend_data.get('trending_topics', 'Current trends')}
- Platform Signals: {trend_data.get('platform_signals', 'Algorithm preferences')}
- Cultural Context: {trend_data.get('cultural_context', 'Zeitgeist alignment')}

This is a scientifically engineered viral framework optimized through recursive self-improvement for maximum shareability and engagement across all major 2025 social media platforms."""
    
    # Calculate enhanced performance score based on recursive improvement
    framework_length = len(comprehensive_prompt)
    original_length = len(request.original_prompt)
    recursive_bonus = 3.0  # Bonus for recursive improvement process
    trend_bonus = 1.5     # Bonus for trend integration
    platform_bonus = 1.0  # Bonus for platform optimization
    
    performance_score = min(10.0, (framework_length / max(original_length, 100)) * 0.8 + recursive_bonus + trend_bonus + platform_bonus)
    
    # Extract industry elements from the comprehensive framework
    industry_elements = [
        f"Advanced {request.industry_focus} viral optimization",
        "2025 algorithm mastery integration", 
        "Recursive self-improvement methodology",
        "Real-time trend alignment",
        "Multi-platform viral mechanics",
        "AIDA/PAS psychological framework integration",
        "Chain-of-thought viral reasoning"
    ]
    
    return EnhancementVariation(
        id=f"var_{index+1}_viral_recursive_v3",
        title="🚀 Viral Potential Focus - Recursive AI Optimization V3",
        enhanced_prompt=comprehensive_prompt,
        focus_strategy="viral_recursive_optimization",
        target_engagement=f'Maximum viral potential through 3-loop recursive improvement with {performance_score:.1f}/10 viral prediction score',
        industry_specific_elements=industry_elements,
        estimated_performance_score=performance_score
    )


async def _generate_advanced_framework(request: PromptEnhancementRequest, audience_analysis: AudienceAnalysis, industry_context: dict, strategy: dict, index: int) -> EnhancementVariation:
    """Generate advanced framework for emotional and technical categories with enhanced features"""
    
    chat = LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=f"enhance-advanced-{strategy['focus']}-{str(uuid.uuid4())[:8]}",
        system_message=strategy["system_prompt"]
    ).with_model("gemini", "gemini-2.0-flash")
    
    enhancement_prompt = f"""ADVANCED FRAMEWORK CREATION WITH ENHANCED FEATURES:

STEP 1 - DEEP ANALYSIS AND UNDERSTANDING:
Original Prompt: "{request.original_prompt}"
Video Type: {request.video_type}
Industry: {request.industry_focus}
Target Audience: {audience_analysis.recommended_tone} tone, {audience_analysis.complexity_level} complexity
Cultural Context: {', '.join(audience_analysis.cultural_considerations)}
Platform Optimizations: {', '.join(audience_analysis.platform_optimizations)}

STEP 2 - ADVANCED STRATEGIC FRAMEWORK IDENTIFICATION:
Based on your expertise in {strategy['focus']} optimization with advanced features, identify:
- Advanced psychological triggers and emotional engineering techniques
- Multi-layered narrative structures with sophisticated frameworks
- Industry-specific best practices with cutting-edge methodologies
- Platform-specific optimization with algorithm mastery
- Advanced engagement mechanics and retention strategies

STEP 3 - PHASE 1 COMPREHENSIVE ADVANCED FRAMEWORK CREATION:
Create a detailed, production-ready advanced framework that MUST include these EXACT REQUIRED SECTIONS:

🎣 HOOK SECTION (0-3 seconds) - WORD COUNT: 25
[Provide exactly 25-word hook with psychological triggers]

🎬 SETUP SECTION (3-15 seconds) - WORD COUNT: 50  
[Provide exactly 50-word setup with audience engagement]

📚 CONTENT CORE (15-80% duration) - WORD COUNT: 250
[Provide exactly 250-word content core with detailed structure]

🏆 CLIMAX MOMENT (80-90% duration) - WORD COUNT: 35
[Provide exactly 35-word climax with maximum impact]

✨ RESOLUTION (90-100% duration) - WORD COUNT: 40
[Provide exactly 40-word resolution with clear call-to-action]

🧠 PSYCHOLOGICAL TRIGGERS INTEGRATED:
- FOMO (Fear of Missing Out): [specific implementation]
- Social Proof: [specific examples and placement]
- Authority: [expert positioning and credibility markers]
- Reciprocity: [value delivery and give-first approach]
- Commitment: [engagement and participation hooks]

📲 2025 TRENDS & PLATFORM OPTIMIZATION:
- Current seasonal trends and relevance
- Latest platform algorithm preferences
- 2025 social media optimization techniques
- Trending hashtags and format adaptation
- Current zeitgeist alignment

⚡ RETENTION ENGINEERING ELEMENTS:
- Engagement questions every 15-20 seconds
- Emotional peaks and valley management
- Pattern interrupts and attention resets
- Cognitive loops and completion triggers
- Retention hooks and cliffhangers
- Complex transition templates with emotional bridges
- Advanced placeholder templates with psychological triggers
- Sophisticated voice and tone guidelines with micro-adjustments

D) ADVANCED PRODUCTION GUIDELINES:
- Precise pacing instructions with psychological timing
- Advanced visual cue suggestions with emotional mapping
- Sophisticated music/sound effect recommendations
- Advanced technical specifications for optimal psychological impact

E) ADVANCED CALL-TO-ACTION FRAMEWORK:
- Multi-layered action-oriented language with psychological triggers
- Advanced urgency/scarcity elements with emotional amplification
- Sophisticated CTA options based on psychological readiness stages
- Advanced platform-specific optimization with algorithm mastery

STEP 4 - ADVANCED INDUSTRY-SPECIFIC CUSTOMIZATION:
Incorporate advanced {request.industry_focus} industry elements:
- Sophisticated terminology and advanced jargon usage
- Cutting-edge industry best practices and methodologies
- Advanced case studies and expert-level examples
- Complex compliance considerations and risk management

STEP 5 - ADVANCED PSYCHOLOGICAL ENGAGEMENT INTEGRATION:
Embed {strategy['focus']}-optimized advanced psychological elements:
- Sophisticated trigger points with precise timing
- Advanced engagement maintenance with psychological loops
- Complex retention and recall optimization techniques
- Advanced social sharing psychological motivators with viral mechanics

Please provide your response in this EXACT structured format:

ADVANCED_FRAMEWORK:
[Comprehensive, production-ready advanced framework with all templates, placeholders, and specific instructions - minimum 750 words with sophisticated structure]

ADVANCED_PRODUCTION_GUIDELINES:
[Sophisticated production instructions including precise psychological timing, advanced visual cues, complex technical requirements, and expert execution details]

ADVANCED_TARGET_ENGAGEMENT:
[Detailed description of expected advanced audience response, sophisticated engagement patterns, and complex success metrics]

ADVANCED_INDUSTRY_ELEMENTS:
[List of 7-10 specific advanced industry elements, cutting-edge best practices, and sophisticated customizations incorporated]

ADVANCED_PSYCHOLOGICAL_TRIGGERS:
[List of 7-10 specific advanced psychological triggers and sophisticated engagement mechanics integrated into the framework]

ADVANCED_PLATFORM_ADAPTATIONS:
[Sophisticated modifications for different social media platforms with algorithm mastery and advanced content distribution strategies]"""

    response = await chat.send_message(UserMessage(text=enhancement_prompt))
    
    # Parse the comprehensive response structure
    sections = {}
    current_section = None
    current_content = []
    
    for line in response.split('\n'):
        if line.strip().endswith(':') and any(key in line.strip().upper() for key in ['ADVANCED_FRAMEWORK:', 'ADVANCED_PRODUCTION_GUIDELINES:', 'ADVANCED_TARGET_ENGAGEMENT:', 'ADVANCED_INDUSTRY_ELEMENTS:', 'ADVANCED_PSYCHOLOGICAL_TRIGGERS:', 'ADVANCED_PLATFORM_ADAPTATIONS:']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line.strip().replace(':', '').lower().replace('_', '_')
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Create comprehensive enhanced prompt from advanced framework
    advanced_framework = sections.get('advanced_framework', sections.get('enhanced_prompt', f"Advanced {strategy['focus']} framework for {request.original_prompt}"))
    production_guidelines = sections.get('advanced_production_guidelines', 'Advanced production standards applied')
    psychological_triggers = sections.get('advanced_psychological_triggers', 'Sophisticated engagement techniques integrated')
    platform_adaptations = sections.get('advanced_platform_adaptations', 'Advanced multi-platform optimization included')
    
    # Combine all elements into a comprehensive enhanced prompt
    comprehensive_prompt = f"""🚀 ADVANCED FRAMEWORK - {strategy['title'].upper()} WITH ENHANCED FEATURES

📋 ADVANCED FRAMEWORK:
{advanced_framework}

🎯 ADVANCED PRODUCTION GUIDELINES:
{production_guidelines}

🧠 ADVANCED PSYCHOLOGICAL TRIGGERS INTEGRATED:
{psychological_triggers}

📱 ADVANCED PLATFORM ADAPTATIONS:
{platform_adaptations}

This advanced framework serves as a sophisticated blueprint for generating high-quality, {strategy['focus']}-optimized video content with enhanced features that maximizes engagement through advanced psychological techniques and achieves professional results with cutting-edge methodologies."""
    
    # Calculate enhanced performance score based on advanced framework comprehensiveness  
    framework_length = len(comprehensive_prompt)
    original_length = len(request.original_prompt)
    advanced_bonus = len(sections) * 0.8  # Higher bonus for advanced structure
    performance_score = min(10.0, (framework_length / max(original_length, 100)) * 2.0 + advanced_bonus + (index + 1) * 0.5)
    
    # Parse industry elements from response
    industry_elements_text = sections.get('advanced_industry_elements', 'Advanced industry best practices applied')
    industry_elements = [elem.strip() for elem in industry_elements_text.split('\n') if elem.strip() and not elem.strip().startswith('[')][:10]
    
    return EnhancementVariation(
        id=f"var_{index+1}_{strategy['focus']}_advanced_framework",
        title=f"{strategy['title']} - Advanced Enhanced Framework",
        enhanced_prompt=comprehensive_prompt,
        focus_strategy=f"{strategy['focus']}_advanced_framework",
        target_engagement=sections.get('advanced_target_engagement', f'High-impact advanced {strategy["focus"]} engagement with sophisticated framework structure and enhanced features'),
        industry_specific_elements=industry_elements or [f"Advanced {request.industry_focus} optimization", "Sophisticated framework structure", "Cutting-edge industry best practices integration"],
        estimated_performance_score=performance_score
    )


async def _generate_standard_framework(request: PromptEnhancementRequest, audience_analysis: AudienceAnalysis, strategy: dict, index: int) -> EnhancementVariation:
    """Generate standard framework for non-viral categories"""
    
    chat = LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=f"enhance-{strategy['focus']}-{str(uuid.uuid4())[:8]}",
        system_message=strategy["system_prompt"]
    ).with_model("gemini", "gemini-2.0-flash")
    
    enhancement_prompt = f"""COMPREHENSIVE SCRIPT FRAMEWORK CREATION:

STEP 1 - DEEP ANALYSIS AND UNDERSTANDING:
Original Prompt: "{request.original_prompt}"
Video Type: {request.video_type}
Industry: {request.industry_focus}
Target Audience: {audience_analysis.recommended_tone} tone, {audience_analysis.complexity_level} complexity
Cultural Context: {', '.join(audience_analysis.cultural_considerations)}
Platform Optimizations: {', '.join(audience_analysis.platform_optimizations)}

STEP 2 - STRATEGIC FRAMEWORK IDENTIFICATION:
Based on your expertise in {strategy['focus']} optimization, identify:
- Core psychological triggers to activate
- Narrative structure most suitable for this content type
- Industry-specific best practices to incorporate
- Platform-specific optimization opportunities
- Engagement mechanics to implement

STEP 3 - COMPREHENSIVE SCRIPT FRAMEWORK CREATION:
Create a detailed, ready-to-use script framework that includes:

A) OPENING HOOK FRAMEWORK:
- Attention-grabbing first 3 seconds
- Pattern interrupt or curiosity gap
- Audience identification statement
- Promise/value proposition setup

B) NARRATIVE STRUCTURE TEMPLATE:
- Act 1: Setup and problem identification [specific templates]
- Act 2: Development and tension building [specific templates]
- Act 3: Resolution and call-to-action [specific templates]

C) DIALOGUE TEMPLATES AND TRANSITIONS:
- Specific phrases optimized for {strategy['focus']} goals  
- Smooth transition templates between sections
- Placeholder templates: [PRODUCT_NAME], [PAIN_POINT], [BENEFIT], [SOCIAL_PROOF]
- Voice and tone guidelines

D) PRODUCTION GUIDELINES:
- Pacing instructions (fast/medium/slow for each section)
- Visual cue suggestions
- Music/sound effect recommendations
- Technical specifications for optimal delivery

E) CALL-TO-ACTION FRAMEWORK:
- Action-oriented language specific to content type
- Urgency/scarcity elements where appropriate
- Multiple CTA options based on audience readiness
- Platform-specific optimization

STEP 4 - INDUSTRY-SPECIFIC CUSTOMIZATION:
Incorporate {request.industry_focus} industry elements:
- Terminology and jargon appropriate for audience level
- Industry best practices and standards
- Relevant case studies or examples
- Compliance considerations if applicable

STEP 5 - PSYCHOLOGICAL ENGAGEMENT INTEGRATION:
Embed {strategy['focus']}-optimized psychological elements:
- Specific trigger points throughout the framework
- Engagement maintenance strategies
- Retention and recall optimization techniques
- Social sharing psychological motivators

Please provide your response in this EXACT structured format:

SCRIPT_FRAMEWORK:
[Comprehensive, ready-to-use script framework with all templates, placeholders, and specific instructions - minimum 500 words with detailed structure]

PRODUCTION_GUIDELINES:
[Specific production instructions including pacing, visual cues, technical requirements, and execution details]

TARGET_ENGAGEMENT:
[Detailed description of expected audience response, engagement patterns, and success metrics]

INDUSTRY_ELEMENTS:
[List of 5-7 specific industry elements, best practices, and customizations incorporated]

PSYCHOLOGICAL_TRIGGERS:
[List of 5-7 specific psychological triggers and engagement mechanics integrated into the framework]

PLATFORM_ADAPTATIONS:
[Specific modifications for different social media platforms and content distribution channels]"""

    response = await chat.send_message(UserMessage(text=enhancement_prompt))
    
    # Parse the comprehensive response structure
    sections = {}
    current_section = None
    current_content = []
    
    for line in response.split('\n'):
        if line.strip().endswith(':') and any(key in line.strip().upper() for key in ['SCRIPT_FRAMEWORK:', 'PRODUCTION_GUIDELINES:', 'TARGET_ENGAGEMENT:', 'INDUSTRY_ELEMENTS:', 'PSYCHOLOGICAL_TRIGGERS:', 'PLATFORM_ADAPTATIONS:']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line.strip().replace(':', '').lower().replace('_', '_')
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Create comprehensive enhanced prompt from script framework
    script_framework = sections.get('script_framework', sections.get('enhanced_prompt', f"Enhanced {strategy['focus']} framework for {request.original_prompt}"))
    production_guidelines = sections.get('production_guidelines', 'Professional production standards applied')
    psychological_triggers = sections.get('psychological_triggers', 'Advanced engagement techniques integrated')
    platform_adaptations = sections.get('platform_adaptations', 'Multi-platform optimization included')
    
    # Combine all elements into a comprehensive enhanced prompt
    comprehensive_prompt = f"""🎬 COMPREHENSIVE SCRIPT FRAMEWORK - {strategy['title'].upper()}

📋 SCRIPT FRAMEWORK:
{script_framework}

🎯 PRODUCTION GUIDELINES:
{production_guidelines}

🧠 PSYCHOLOGICAL TRIGGERS INTEGRATED:
{psychological_triggers}

📱 PLATFORM ADAPTATIONS:
{platform_adaptations}

This framework serves as a complete blueprint for generating high-quality, {strategy['focus']}-optimized video content that maximizes engagement and achieves professional results."""
    
    # Calculate enhanced performance score based on framework comprehensiveness  
    framework_length = len(comprehensive_prompt)
    original_length = len(request.original_prompt)
    complexity_bonus = len(sections) * 0.5  # Bonus for comprehensive structure
    performance_score = min(10.0, (framework_length / max(original_length, 100)) * 1.5 + complexity_bonus + (index + 1) * 0.3)
    
    # Parse industry elements from response
    industry_elements_text = sections.get('industry_elements', 'Industry best practices applied')
    industry_elements = [elem.strip() for elem in industry_elements_text.split('\n') if elem.strip() and not elem.strip().startswith('[')][:7]
    
    return EnhancementVariation(
        id=f"var_{index+1}_{strategy['focus']}_framework",
        title=f"{strategy['title']} - Advanced Framework",
        enhanced_prompt=comprehensive_prompt,
        focus_strategy=f"{strategy['focus']}_framework",
        target_engagement=sections.get('target_engagement', f'High-impact {strategy["focus"]} engagement with comprehensive framework structure'),
        industry_specific_elements=industry_elements or [f"Advanced {request.industry_focus} optimization", "Professional framework structure", "Industry best practices integration"],
        estimated_performance_score=performance_score
    )

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

@api_router.post("/generate-script-v2", response_model=ScriptResponse)
async def generate_script_v2(request: ScriptRequest):
    """
    Phase 2: Master Prompt Template V2.0 - ELITE Video Script Generation
    Advanced script generation with dynamic context integration and viral optimization
    """
    try:
        # Phase 2: Get enhanced context using Context Integration System
        enhanced_context = await context_system.get_enhanced_context(
            prompt=request.prompt,
            industry=getattr(request, 'industry_focus', 'general'),
            platform=getattr(request, 'target_platform', 'general')
        )
        
        # Phase 2: Master Prompt Template V2.0 - ELITE Video Script Architect
        SYSTEM_PROMPT_V2 = f"""
You are an ELITE video script architect with proven track record of creating viral content across all platforms. Your expertise combines:

🎬 STRUCTURAL MASTERY:
- 15+ years in video production and storytelling
- Deep understanding of viewer psychology and retention curves  
- Platform-specific algorithm optimization expertise

📊 DATA-DRIVEN APPROACH:
- Analysis of 10,000+ high-performing videos
- Real-time trend integration and cultural awareness
- Audience behavior prediction and engagement optimization

🧠 PSYCHOLOGICAL FRAMEWORKS:
- Advanced persuasion psychology (Cialdini's 6 principles)
- Emotional arc engineering for maximum impact
- Cognitive load optimization for information retention

MANDATORY SCRIPT ARCHITECTURE:
┌─ HOOK SECTION (0-3 seconds): 
│  ├── Pattern Interrupt: Unexpected statement/visual
│  ├── Relevance Bridge: Direct audience connection
│  └── Promise Setup: Clear value proposition preview
│
├─ SETUP SECTION (3-15 seconds):
│  ├── Context Establishment: Scene/problem setting
│  ├── Stakes Definition: Why this matters now
│  └── Journey Preview: What audience will discover
│
├─ CONTENT DELIVERY (Core 60-80%):
│  ├── Primary Message: Core value/information
│  ├── Supporting Evidence: Proof points/examples  
│  ├── Engagement Hooks: Questions/surprises every 15-20 seconds
│  └── Retention Anchors: Callbacks and progression markers
│
├─ CLIMAX MOMENT (80-90%):
│  ├── Peak Revelation: Most impactful information
│  ├── Emotional Crescendo: Maximum engagement point
│  └── Transformation Preview: Clear before/after vision
│
└─ RESOLUTION (90-100%):
   ├── Key Takeaway Summary: Memorable conclusion
   ├── Call-to-Action: Specific next step
   └── Community Engagement: Like/comment/share prompt

QUALITY VALIDATION CHECKLIST:
□ Retention hook every 15-20 seconds
□ Emotional arc with clear peaks and valleys  
□ Platform-optimized pacing and format
□ Clear value proposition maintained throughout
□ Compelling call-to-action with specific benefit
□ Cultural relevance and trend alignment
□ Algorithm-friendly engagement triggers

CURRENT CONTEXT INTEGRATION:
- Duration: {request.duration} 
- Video Type: {request.video_type}
- Platform Algorithm Insights: {enhanced_context.get('platform_algorithm', {}).get('priority_factors', [])}
- Trending Topics: {[trend.get('title', '') for trend in enhanced_context.get('trend_analysis', {}).get('trending_topics', [])[:3]]}
- Audience Psychology: {enhanced_context.get('audience_psychology', {}).get('psychological_profile', {}).get('cognitive_style', 'mixed')}
- Cultural Moment: {enhanced_context.get('seasonal_relevance', {}).get('digital_culture', {}).get('current_trends', [])}
- Performance Optimization: {enhanced_context.get('performance_history', {}).get('optimization_opportunities', [])}

ADVANCED PRODUCTION SPECIFICATIONS:
🎥 VISUAL STORYTELLING (Every 2-3 seconds):
   - Exact camera specifications: angles, movements, framing
   - Detailed environment descriptions: lighting, setting, atmosphere
   - Character positioning and expressions
   - Color psychology and mood enhancement
   - Transition techniques and flow

🎯 ENGAGEMENT ENGINEERING:
   - Dopamine triggers and reward loops
   - Social proof integration points
   - Curiosity gaps and pattern interrupts
   - Interactive elements and participation cues
   - Emotional peak orchestration

🚀 VIRAL MECHANICS INTEGRATION:
   - Shareability triggers and moments
   - Meme potential and cultural references
   - Controversy balance and discussion starters
   - Trend participation opportunities
   - Community building elements

📱 PLATFORM OPTIMIZATION ({getattr(request, 'target_platform', 'general')}):
   - Algorithm-friendly structure and pacing
   - Format-specific engagement patterns
   - Optimal length and retention strategies
   - Hashtag and discoverability integration
   - Cross-platform adaptation potential

Create a script that follows this ELITE architecture with integrated context insights for maximum viral potential and audience engagement.
"""
        
        # Create enhanced chat instance with Master Prompt Template V2.0
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"script-v2-{str(uuid.uuid4())[:8]}",
            system_message=SYSTEM_PROMPT_V2
        ).with_model("gemini", "gemini-2.0-flash")

        # Enhanced script generation message with context integration
        script_message = UserMessage(
            text=f"""Using the Master Prompt Template V2.0 architecture, create an ELITE viral-optimized script:

PROMPT: "{request.prompt}"

CONTEXT INTELLIGENCE INTEGRATION:
🔥 TRENDING INSIGHTS: {enhanced_context.get('trend_analysis', {}).get('trend_insights', [])}
🎯 PLATFORM STRATEGIES: {enhanced_context.get('platform_algorithm', {}).get('optimization_strategies', [])}
👥 AUDIENCE PSYCHOLOGY: {enhanced_context.get('audience_psychology', {}).get('content_optimization', [])}
📅 CULTURAL TIMING: {enhanced_context.get('seasonal_relevance', {}).get('content_calendar_suggestions', [])}
⚡ PERFORMANCE PREDICTORS: {enhanced_context.get('performance_history', {}).get('success_factors', [])}

SPECIFICATIONS:
- Duration: {request.duration}
- Video Type: {request.video_type}
- Context Quality Score: {enhanced_context.get('metadata', {}).get('context_quality_score', 0.5)}

MANDATORY ARCHITECTURE IMPLEMENTATION:
1. HOOK SECTION (0-3s): Pattern interrupt + Relevance bridge + Promise setup
2. SETUP SECTION (3-15s): Context establishment + Stakes definition + Journey preview  
3. CONTENT DELIVERY (60-80%): Primary message + Evidence + Engagement hooks + Retention anchors
4. CLIMAX MOMENT (80-90%): Peak revelation + Emotional crescendo + Transformation preview
5. RESOLUTION (90-100%): Key takeaway + Call-to-action + Community engagement

ENHANCED REQUIREMENTS:
✅ Include retention hooks every 15-20 seconds
✅ Implement emotional arc with clear peaks and valleys
✅ Integrate trending insights and cultural relevance
✅ Apply platform-specific optimization strategies
✅ Include viral mechanics and shareability triggers
✅ Add detailed visual storytelling specifications
✅ Ensure quality validation checklist compliance

Generate a professional, production-ready script that maximizes viral potential and audience engagement using advanced context intelligence."""
        )

        generated_script = await chat.send_message(script_message)
        
        # Store the enhanced script in database with context metadata
        script_data = ScriptResponse(
            original_prompt=request.prompt,
            generated_script=generated_script,
            video_type=request.video_type or "general",
            duration=request.duration or "short"
        )
        
        # Add Phase 2 metadata
        script_dict = script_data.dict()
        script_dict['phase'] = 'v2_master_template'
        script_dict['context_quality_score'] = enhanced_context.get('metadata', {}).get('context_quality_score', 0.5)
        script_dict['trend_alignment'] = len([t for t in enhanced_context.get('trend_analysis', {}).get('trending_topics', []) if t.get('relevance_score', 0) > 0.5])
        script_dict['platform_optimization'] = enhanced_context.get('platform_algorithm', {}).get('platform', 'general')
        
        await db.scripts.insert_one(script_dict)
        
        return script_data
        
    except Exception as e:
        logger.error(f"Error in Phase 2 script generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating Phase 2 script: {str(e)}")


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

@api_router.post("/generate-script-cot", response_model=CoTScriptResponse)
async def generate_script_with_chain_of_thought(request: CoTScriptRequest):
    """
    Advanced Script Generation with Chain-of-Thought Reasoning
    
    This endpoint uses advanced Chain-of-Thought reasoning to generate high-quality scripts
    through a systematic 6-step process:
    1. Analysis and Understanding
    2. Audience and Context Mapping  
    3. Narrative Architecture Design
    4. Engagement Strategy Planning
    5. Content Development
    6. Quality Validation and Refinement
    """
    try:
        # Get enhanced context if available
        enhanced_context = await context_system.get_enhanced_context(
            prompt=request.prompt,
            industry=request.industry_focus,
            platform=request.target_platform
        )
        
        # Generate script using Chain-of-Thought reasoning
        result = await advanced_script_generator.generate_script_with_reasoning(
            prompt=request.prompt,
            video_type=request.video_type,
            duration=request.duration,
            enhanced_context=enhanced_context
        )
        
        # Create response object
        script_response = CoTScriptResponse(
            original_prompt=request.prompt,
            generated_script=result["generated_script"],
            video_type=request.video_type or "general",
            duration=request.duration or "medium",
            reasoning_chain=result["reasoning_chain"] if request.include_reasoning_chain else None,
            final_analysis=result["final_analysis"],
            generation_metadata=result["generation_metadata"]
        )
        
        # Store in database with enhanced metadata
        script_dict = script_response.dict()
        script_dict['generation_method'] = 'chain_of_thought'
        script_dict['context_quality_score'] = enhanced_context.get('metadata', {}).get('context_quality_score', 0.5)
        script_dict['reasoning_steps_completed'] = len(result["reasoning_chain"])
        script_dict['validation_score'] = result["final_analysis"].get("validation_score", 5.0)
        
        await db.scripts.insert_one(script_dict)
        
        return script_response
        
    except Exception as e:
        logger.error(f"Error in Chain-of-Thought script generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating CoT script: {str(e)}")

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
    - Duplicate content (same text in CHARACTER and DIALOGUE fields)
    """
    
    lines = raw_script.strip().split('\n')
    spoken_content = []
    seen_content = set()  # Track unique content to avoid duplicates
    
    # Section headers and metadata to completely skip
    skip_sections = [
        'TARGET DURATION', 'VIDEO TYPE', 'VIDEO SCRIPT', 'SCRIPT:', 'KEY RETENTION ELEMENTS',
        'NOTES:', 'RETENTION ELEMENTS:', 'ADJUSTMENTS:', 'OPTIMIZATION:', 'METRICS:',
        'NOTES', 'SCRIPT', 'DURATION', 'TYPE', 'KEY CONSIDERATIONS', 'RATIONALE:',
        'END.', '**KEY CONSIDERATIONS', '**END**', 'VIDEO TITLE', 'TARGET DURATION'
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
        
        # Skip CHARACTER field descriptions (like "Text: 'some text'") 
        # These are visual overlays, not spoken content
        if line.startswith('**[CHARACTER:]**') or 'Text:' in line:
            # Extract quoted content but mark it as CHARACTER content to avoid duplicates
            character_quotes = re.findall(r'"([^"]+)"', line)
            for quote in character_quotes:
                seen_content.add(quote.strip().lower())  # Mark as seen (case insensitive)
            continue
        
        # Skip camera, setting, lighting, movement, effects, transition descriptions
        production_fields = ['CAMERA:', 'SETTING:', 'LIGHTING:', 'MOVEMENT:', 'EFFECTS:', 'TRANSITION:']
        if any(field in line for field in production_fields):
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
        
        # Extract quoted content (actual dialogue)
        quoted_content = re.findall(r'"([^"]+)"', line)
        for quote in quoted_content:
            quote_clean = quote.strip()
            quote_lower = quote_clean.lower()
            
            # Only add if we haven't seen this content before (avoid duplicates)
            if quote_lower not in seen_content and len(quote_clean) > 3:
                seen_content.add(quote_lower)
                spoken_content.append(quote_clean)
        
        # Also process non-quoted spoken content
        # Remove quotes and speaker directions to get remaining spoken content
        line_no_quotes = re.sub(r'"[^"]*"', '', line)
        line_no_quotes = line_no_quotes.strip()
        
        # Clean up the line
        if line_no_quotes and len(line_no_quotes) > 3:
            # Remove markdown formatting
            line_no_quotes = re.sub(r'\*\*([^*]+)\*\*', r'\1', line_no_quotes)  # Bold
            line_no_quotes = re.sub(r'\*([^*]+)\*', r'\1', line_no_quotes)      # Italic
            line_no_quotes = re.sub(r'__([^_]+)__', r'\1', line_no_quotes)      # Underline
            
            # Remove any remaining isolated parentheses or brackets
            line_no_quotes = re.sub(r'^\s*[\[\]()]+\s*$', '', line_no_quotes)
            
            # Clean up extra spaces and normalize punctuation
            line_no_quotes = re.sub(r'\s+', ' ', line_no_quotes).strip()
            
            # Only add if it's not just punctuation or whitespace and not a duplicate
            if (line_no_quotes and 
                not re.match(r'^[\s\[\]().,!?-]*$', line_no_quotes) and
                line_no_quotes.lower() not in seen_content):
                seen_content.add(line_no_quotes.lower())
                spoken_content.append(line_no_quotes)
    
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
            # Remove duplicates while preserving order
            unique_quotes = []
            seen_fallback = set()
            for quote in quoted_content:
                quote_lower = quote.strip().lower()
                if quote_lower not in seen_fallback:
                    seen_fallback.add(quote_lower)
                    unique_quotes.append(quote.strip())
            final_script = ' '.join(unique_quotes)
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

# =============================================================================
# PHASE 3: ADVANCED ANALYTICS AND VALIDATION ENDPOINTS
# =============================================================================

# Phase 3 Data Models
class AdvancedAnalysisRequest(BaseModel):
    script: str
    metadata: Optional[Dict[str, Any]] = {}

class QualityAnalysisRequest(BaseModel):
    script: str 
    metadata: Optional[Dict[str, Any]] = {}

class ValidationRequest(BaseModel):
    script: str
    requirements: Dict[str, Any]

class PerformanceTrackingRequest(BaseModel):
    script_id: str
    performance_metrics: Dict[str, Any]

class ScriptPreviewRequest(BaseModel):
    script: str
    metadata: Optional[Dict[str, Any]] = {}

class PerformanceInsightsRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = {}

class ScriptRecommendationsRequest(BaseModel):
    script_context: Dict[str, Any]

# Priority 1: Prompt Enhancement Pipeline

@api_router.post("/advanced-context-analysis")
async def advanced_context_analysis(request: AdvancedAnalysisRequest):
    """Advanced context enrichment with trend analysis, competitor insights, and performance prediction"""
    try:
        enriched_context = await advanced_context_engine.enrich_prompt_context(
            request.script, request.metadata
        )
        
        return {
            "status": "SUCCESS",
            "analysis_type": "ADVANCED_CONTEXT_ENRICHMENT",
            "enriched_context": enriched_context,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in advanced context analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Advanced context analysis failed: {str(e)}")

@api_router.post("/script-quality-analysis")
async def script_quality_analysis(request: QualityAnalysisRequest):
    """Comprehensive script quality analysis with retention, engagement, and optimization scoring"""
    try:
        quality_analysis = script_quality_analyzer.analyze_script_quality(
            request.script, request.metadata
        )
        
        return {
            "status": "SUCCESS",
            "analysis_type": "SCRIPT_QUALITY_ANALYSIS",
            "quality_analysis": quality_analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in script quality analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Script quality analysis failed: {str(e)}")

# Priority 2: Validation and Feedback Loop

@api_router.post("/script-validation")
async def script_validation(request: ValidationRequest):
    """Comprehensive script structure validation and quality assurance"""
    try:
        validation_results = script_validator.validate_script_structure(
            request.script, request.requirements
        )
        
        return {
            "status": "SUCCESS",
            "validation_type": "COMPREHENSIVE_VALIDATION",
            "validation_results": validation_results,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in script validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Script validation failed: {str(e)}")

@api_router.post("/track-performance")
async def track_script_performance(request: PerformanceTrackingRequest):
    """Track script performance for learning and improvement"""
    try:
        tracking_results = await script_performance_tracker.track_script_performance(
            request.script_id, request.performance_metrics
        )
        
        return {
            "status": "SUCCESS",
            "tracking_type": "PERFORMANCE_TRACKING",
            "tracking_results": tracking_results,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error tracking performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance tracking failed: {str(e)}")

@api_router.post("/performance-insights")
async def get_performance_insights(request: PerformanceInsightsRequest):
    """Get comprehensive performance insights and learning patterns"""
    try:
        insights = await script_performance_tracker.get_performance_insights(request.filters)
        
        return {
            "status": "SUCCESS",
            "insights_type": "PERFORMANCE_INSIGHTS",
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance insights failed: {str(e)}")

@api_router.post("/script-recommendations")
async def get_script_recommendations(request: ScriptRecommendationsRequest):
    """Get personalized script recommendations based on performance learning"""
    try:
        recommendations = await script_performance_tracker.get_script_recommendations(
            request.script_context
        )
        
        return {
            "status": "SUCCESS",
            "recommendation_type": "PERSONALIZED_RECOMMENDATIONS",
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting script recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Script recommendations failed: {str(e)}")

# Priority 3: User Experience Enhancements

@api_router.post("/script-preview")
async def generate_script_preview(request: ScriptPreviewRequest):
    """Generate comprehensive script preview with engagement predictions and optimization suggestions"""
    try:
        preview = script_preview_generator.generate_script_preview(
            request.script, request.metadata
        )
        
        return {
            "status": "SUCCESS",
            "preview_type": "COMPREHENSIVE_PREVIEW",
            "preview": preview,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating script preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Script preview generation failed: {str(e)}")

@api_router.post("/engagement-timeline")
async def create_engagement_timeline(request: ScriptPreviewRequest):
    """Create detailed engagement timeline curve for script analysis"""
    try:
        platform = request.metadata.get('target_platform', 'youtube') if request.metadata else 'youtube'
        engagement_timeline = script_preview_generator.create_engagement_curve(
            request.script, platform
        )
        
        return {
            "status": "SUCCESS",
            "timeline_type": "ENGAGEMENT_TIMELINE",
            "engagement_timeline": engagement_timeline,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating engagement timeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Engagement timeline creation failed: {str(e)}")

@api_router.post("/retention-predictions")
async def predict_retention_points(request: ScriptPreviewRequest):
    """Predict audience drop-off points and retention metrics"""
    try:
        platform = request.metadata.get('target_platform', 'youtube') if request.metadata else 'youtube'
        retention_predictions = script_preview_generator.predict_drop_off_points(
            request.script, platform
        )
        
        return {
            "status": "SUCCESS",
            "prediction_type": "RETENTION_PREDICTIONS",
            "retention_predictions": retention_predictions,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting retention: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retention prediction failed: {str(e)}")

@api_router.post("/optimization-suggestions")
async def get_optimization_suggestions(request: ScriptPreviewRequest):
    """Generate comprehensive optimization suggestions for script improvement"""
    try:
        optimization_suggestions = script_preview_generator.suggest_improvements(
            request.script, request.metadata
        )
        
        return {
            "status": "SUCCESS",
            "suggestion_type": "OPTIMIZATION_SUGGESTIONS",
            "optimization_suggestions": optimization_suggestions,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating optimization suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization suggestions failed: {str(e)}")

# Comprehensive Analysis Endpoint

@api_router.post("/comprehensive-script-analysis")
async def comprehensive_script_analysis(request: AdvancedAnalysisRequest):
    """
    Comprehensive script analysis combining all Phase 3 features:
    - Advanced context enrichment
    - Quality analysis
    - Structure validation
    - Preview generation
    """
    try:
        # Prepare metadata with defaults
        metadata = request.metadata or {}
        platform = metadata.get('target_platform', 'youtube')
        
        # Run all analyses in parallel for efficiency
        results = await asyncio.gather(
            # Context enrichment
            advanced_context_engine.enrich_prompt_context(request.script, metadata),
            
            # Quality analysis
            asyncio.create_task(asyncio.to_thread(
                script_quality_analyzer.analyze_script_quality, request.script, metadata
            )),
            
            # Structure validation
            asyncio.create_task(asyncio.to_thread(
                script_validator.validate_script_structure, 
                request.script, 
                {"platform": platform, **metadata}
            )),
            
            # Preview generation
            asyncio.create_task(asyncio.to_thread(
                script_preview_generator.generate_script_preview, request.script, metadata
            )),
            
            return_exceptions=True
        )
        
        context_analysis, quality_analysis, validation_results, preview_results = results
        
        # Handle any exceptions
        analyses = {}
        if not isinstance(context_analysis, Exception):
            analyses["context_analysis"] = context_analysis
        if not isinstance(quality_analysis, Exception):
            analyses["quality_analysis"] = quality_analysis
        if not isinstance(validation_results, Exception):
            analyses["validation_results"] = validation_results
        if not isinstance(preview_results, Exception):
            analyses["preview_results"] = preview_results
        
        # Generate comprehensive summary
        comprehensive_summary = _generate_comprehensive_summary(analyses)
        
        return {
            "status": "SUCCESS",
            "analysis_type": "COMPREHENSIVE_ANALYSIS",
            "comprehensive_summary": comprehensive_summary,
            "detailed_analyses": analyses,
            "generated_at": datetime.utcnow().isoformat(),
            "analysis_metadata": {
                "script_length": len(request.script),
                "word_count": len(request.script.split()),
                "platform": platform,
                "analyses_completed": len(analyses)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive script analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

def _generate_comprehensive_summary(analyses: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary from all completed analyses"""
    summary = {
        "overall_health": "UNKNOWN",
        "key_strengths": [],
        "critical_issues": [],
        "top_recommendations": [],
        "performance_forecast": "MODERATE"
    }
    
    try:
        # Extract key metrics from each analysis
        if "quality_analysis" in analyses:
            quality = analyses["quality_analysis"]
            summary["overall_health"] = quality.get("quality_grade", "UNKNOWN")
            summary["key_strengths"].extend(quality.get("strengths", [])[:3])
        
        if "validation_results" in analyses:
            validation = analyses["validation_results"]
            critical_issues = validation.get("critical_issues", [])
            summary["critical_issues"].extend([issue.get("issue", "") for issue in critical_issues][:3])
        
        if "preview_results" in analyses:
            preview = analyses["preview_results"]
            recommendations = preview.get("actionable_recommendations", [])
            summary["top_recommendations"].extend(recommendations[:5])
            
            forecast = preview.get("performance_forecast", {})
            viral_potential = forecast.get("viral_potential", "MODERATE")
            summary["performance_forecast"] = viral_potential
        
        if "context_analysis" in analyses:
            context = analyses["context_analysis"]
            synthesis = context.get("context_synthesis", {})
            success_prob = synthesis.get("success_probability", 50)
            
            if success_prob > 75:
                summary["performance_forecast"] = "HIGH"
            elif success_prob < 40:
                summary["performance_forecast"] = "LOW"
    
    except Exception as e:
        logger.error(f"Error generating comprehensive summary: {str(e)}")
        summary["error"] = str(e)
    
    return summary

# =============================================================================
# END PHASE 3 ENDPOINTS
# =============================================================================

# =============================================================================
# PHASE 4: MEASUREMENT & OPTIMIZATION ENDPOINTS
# =============================================================================

@api_router.post("/run-prompt-experiments", response_model=PromptExperimentResponse)
async def run_prompt_experiments(request: PromptExperimentRequest):
    """
    Phase 4: Run A/B testing experiments on different prompt strategies
    Tests multiple prompt variations and identifies the best performing strategy
    """
    try:
        # Convert strategies to variation configs
        variations = [
            {"strategy": strategy} 
            for strategy in request.strategies
        ]
        
        # Prepare metadata
        metadata = {
            "video_type": request.video_type,
            "duration": request.duration,
            "platform": request.platform
        }
        
        # Run the experiment using PromptOptimizationEngine
        results = await prompt_optimization_engine.run_prompt_experiments(
            base_prompt=request.base_prompt,
            variations=variations,
            metadata=metadata
        )
        
        return PromptExperimentResponse(**results)
        
    except Exception as e:
        logger.error(f"Error running prompt experiments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Experiment failed: {str(e)}")

@api_router.post("/analyze-best-strategy", response_model=OptimizationAnalysisResponse)
async def analyze_best_strategy(request: OptimizationAnalysisRequest):
    """
    Phase 4: Analyze experiment results and identify best performing strategy
    Uses statistical analysis to determine optimal prompt optimization approach
    """
    try:
        # Use PromptOptimizationEngine to identify best strategy
        analysis = await prompt_optimization_engine.identify_best_performing_strategy(
            results=request.results
        )
        
        return OptimizationAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing best strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.post("/optimization-history", response_model=OptimizationHistoryResponse)
async def get_optimization_history(request: OptimizationHistoryRequest):
    """
    Phase 4: Get historical optimization data and performance trends
    Provides insights into optimization patterns and strategy effectiveness over time
    """
    try:
        filters = {}
        
        if request.date_range:
            filters["date_range"] = request.date_range
        if request.strategy:
            filters["strategy"] = request.strategy
        if request.platform:
            filters["platform"] = request.platform
        
        # Get historical data from PromptOptimizationEngine
        history = await prompt_optimization_engine.get_optimization_history(filters)
        
        return OptimizationHistoryResponse(**history)
        
    except Exception as e:
        logger.error(f"Error getting optimization history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

@api_router.post("/quality-metrics-analysis")
async def analyze_quality_metrics(request: Dict[str, Any]):
    """
    Phase 4: Analyze script using enhanced quality metrics
    Uses the updated ScriptQualityAnalyzer with Phase 4 metrics integration
    """
    try:
        script = request.get("script", "")
        metadata = request.get("metadata", {})
        
        if not script:
            raise HTTPException(status_code=400, detail="Script content is required")
        
        # Use enhanced Phase 4 quality analyzer
        analysis = script_quality_analyzer.analyze_script_quality(script, metadata)
        
        # Extract Phase 4 specific metrics
        phase4_metrics = {
            "structural_compliance": analysis.get("detailed_scores", {}).get("structural_compliance", {}),
            "engagement_density": analysis.get("detailed_scores", {}).get("engagement_density", {}),
            "emotional_arc_strength": analysis.get("detailed_scores", {}).get("emotional_arc_strength", {}),
            "platform_optimization": analysis.get("detailed_scores", {}).get("platform_optimization", {}),
            "retention_potential": analysis.get("detailed_scores", {}).get("retention_potential", {}),
            "viral_coefficient": analysis.get("detailed_scores", {}).get("viral_coefficient", {}),
            "conversion_potential": analysis.get("detailed_scores", {}).get("conversion_potential", {})
        }
        
        return {
            "status": "SUCCESS",
            "phase": "PHASE_4_ENHANCED_METRICS",
            "overall_analysis": analysis,
            "phase4_metrics": phase4_metrics,
            "quality_summary": {
                "overall_score": analysis.get("overall_quality_score", 0.0),
                "quality_grade": analysis.get("quality_grade", "F"),
                "top_metrics": sorted(
                    [(k, v.get("score", 0) if isinstance(v, dict) else v) 
                     for k, v in phase4_metrics.items()],
                    key=lambda x: x[1], reverse=True
                )[:3]
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in Phase 4 quality metrics analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quality analysis failed: {str(e)}")

# =============================================================================
# END PHASE 4 ENDPOINTS  
# =============================================================================

# =============================================================================
# PHASE 5: INTELLIGENT QUALITY ASSURANCE & AUTO-OPTIMIZATION ENDPOINTS
# =============================================================================

@api_router.post("/intelligent-qa-analysis", response_model=IntelligentQAResponse)
async def intelligent_qa_analysis(request: IntelligentQARequest):
    """
    Phase 5: Comprehensive Intelligent QA Analysis
    Multi-model validation, advanced metrics, automatic regeneration for low-quality scripts
    """
    try:
        logger.info(f"Starting intelligent QA analysis for script length: {len(request.script)} characters")
        
        # Prepare metadata
        metadata = {
            "target_platform": request.target_platform,
            "duration": request.duration,
            "video_type": request.video_type
        }
        
        # Run comprehensive QA analysis
        qa_result = await intelligent_qa_system.comprehensive_qa_analysis(
            script=request.script,
            original_prompt=request.original_prompt,
            metadata=metadata,
            enable_regeneration=request.enable_regeneration
        )
        
        # Convert to response format
        return IntelligentQAResponse(
            qa_id=qa_result.qa_id,
            original_prompt=qa_result.original_prompt,
            final_script=qa_result.final_script,
            quality_analysis=qa_result.quality_analysis,
            consensus_validation=qa_result.consensus_validation.__dict__,  # Convert dataclass to dict
            improvement_cycle_data=qa_result.improvement_cycle_data,
            quality_threshold_met=qa_result.quality_threshold_met,
            regeneration_performed=qa_result.regeneration_performed,
            total_processing_time=qa_result.total_processing_time,
            recommendations=qa_result.recommendations,
            confidence_score=qa_result.confidence_score
        )
        
    except Exception as e:
        logger.error(f"Error in intelligent QA analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Intelligent QA analysis failed: {str(e)}")

@api_router.post("/multi-model-validation", response_model=MultiModelValidationResponse)
async def multi_model_validation(request: MultiModelValidationRequest):
    """
    Phase 5: Multi-Model Consensus Validation
    Uses 3-5 AI models for consensus-based quality scoring
    """
    try:
        logger.info(f"Starting multi-model validation for script length: {len(request.script)} characters")
        
        # Prepare metadata
        metadata = {
            "target_platform": request.target_platform,
            "duration": request.duration,
            "video_type": request.video_type
        }
        
        # Run multi-model validation
        validation_result = await multi_model_validator.validate_script_quality(request.script, metadata)
        
        # Convert individual results to dict format
        individual_results = []
        for result in validation_result.individual_results:
            individual_results.append({
                "model_name": result.model_name,
                "model_provider": result.model_provider,
                "quality_score": result.quality_score,
                "detailed_scores": result.detailed_scores,
                "reasoning": result.reasoning,
                "response_time": result.response_time,
                "success": result.success,
                "error_message": result.error_message
            })
        
        return MultiModelValidationResponse(
            consensus_score=validation_result.consensus_score,
            consensus_grade=validation_result.consensus_grade,
            individual_results=individual_results,
            agreement_level=validation_result.agreement_level,
            confidence_score=validation_result.confidence_score,
            quality_threshold_passed=validation_result.quality_threshold_passed,
            regeneration_required=validation_result.regeneration_required,
            improvement_suggestions=validation_result.improvement_suggestions
        )
        
    except Exception as e:
        logger.error(f"Error in multi-model validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Multi-model validation failed: {str(e)}")

@api_router.post("/advanced-quality-metrics", response_model=AdvancedQualityMetricsResponse)
async def advanced_quality_metrics_analysis(request: AdvancedQualityMetricsRequest):
    """
    Phase 5: Advanced Quality Metrics Framework
    Comprehensive analysis including readability, engagement prediction, emotional intelligence, 
    platform compliance, and conversion potential
    """
    try:
        logger.info(f"Starting advanced quality metrics analysis for script length: {len(request.script)} characters")
        
        # Prepare metadata
        metadata = {
            "target_platform": request.target_platform,
            "duration": request.duration,
            "video_type": request.video_type
        }
        
        # Run advanced quality metrics analysis
        metrics_result = await advanced_quality_metrics.analyze_comprehensive_quality(request.script, metadata)
        
        return AdvancedQualityMetricsResponse(
            composite_quality_score=metrics_result["composite_quality_score"],
            quality_grade=metrics_result["quality_grade"],
            detailed_metrics=metrics_result["detailed_metrics"],
            quality_recommendations=metrics_result["quality_recommendations"],
            analysis_metadata=metrics_result["analysis_metadata"]
        )
        
    except Exception as e:
        logger.error(f"Error in advanced quality metrics analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Advanced quality metrics analysis failed: {str(e)}")

@api_router.post("/quality-improvement-optimization", response_model=QualityImprovementResponse)
async def quality_improvement_optimization(request: QualityImprovementRequest):
    """
    Phase 5: Quality Improvement Loop with Automatic Regeneration
    Feedback-based script optimization with automatic regeneration for low-quality outputs
    """
    try:
        logger.info(f"Starting quality improvement optimization for prompt: {request.original_prompt[:100]}...")
        
        # Prepare metadata
        metadata = {
            "target_platform": request.target_platform,
            "duration": request.duration,
            "video_type": request.video_type
        }
        
        # Run quality improvement optimization
        improvement_result = await quality_improvement_loop.optimize_script_with_feedback_loop(
            request.original_prompt, metadata
        )
        
        return QualityImprovementResponse(
            cycle_id=improvement_result["cycle_id"],
            original_score=improvement_result["original_score"],
            final_score=improvement_result["final_score"],
            improvement_achieved=improvement_result["improvement_achieved"],
            quality_threshold_met=improvement_result["quality_threshold_met"],
            cycles_completed=improvement_result["cycles_completed"],
            final_script=improvement_result["final_script"],
            validation_result=improvement_result["validation_result"].__dict__ if hasattr(improvement_result["validation_result"], '__dict__') else improvement_result["validation_result"],
            strategy_used=improvement_result["strategy_used"],
            improvements_attempted=improvement_result["improvements_attempted"],
            learning_insights=improvement_result["learning_insights"]
        )
        
    except Exception as e:
        logger.error(f"Error in quality improvement optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quality improvement optimization failed: {str(e)}")

@api_router.post("/ab-test-optimization", response_model=ABTestOptimizationResponse)
async def ab_test_optimization(request: ABTestOptimizationRequest):
    """
    Phase 5: A/B Testing for Both Prompt Strategies AND AI Models
    Tests different prompt strategies and AI models to find optimal combination
    """
    try:
        logger.info(f"Starting A/B test optimization for prompt: {request.original_prompt[:100]}...")
        
        # Prepare metadata
        metadata = {
            "target_platform": request.target_platform,
            "duration": request.duration,
            "video_type": request.video_type
        }
        
        # Run A/B test optimization
        ab_test_result = await intelligent_qa_system.run_ab_test_optimization(
            request.original_prompt, metadata
        )
        
        if "error" in ab_test_result:
            raise HTTPException(status_code=500, detail=ab_test_result["error"])
        
        return ABTestOptimizationResponse(
            test_id=ab_test_result["test_id"],
            best_performing_combination=ab_test_result["best_performing_combination"],
            all_results=ab_test_result["all_results"],
            statistical_analysis=ab_test_result["statistical_analysis"],
            performance_improvement=ab_test_result["performance_improvement"],
            recommendations=ab_test_result["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Error in A/B test optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"A/B test optimization failed: {str(e)}")

@api_router.post("/evolve-system-prompts")
async def evolve_system_prompts():
    """
    Phase 5: Dynamic System Prompt Evolution
    Evolves system prompts based on accumulated performance data
    """
    try:
        logger.info("Starting system prompt evolution based on performance data")
        
        # Run system prompt evolution
        evolution_result = await intelligent_qa_system.evolve_system_prompts()
        
        return {
            "status": "SUCCESS",
            "phase": "PHASE_5_PROMPT_EVOLUTION",
            "evolution_result": evolution_result,
            "evolution_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in system prompt evolution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"System prompt evolution failed: {str(e)}")

@api_router.get("/qa-system-performance")
async def get_qa_system_performance(days: int = 30):
    """
    Phase 5: QA System Performance Metrics
    Get comprehensive performance metrics and system insights
    """
    try:
        logger.info(f"Getting QA system performance metrics for last {days} days")
        
        # Get system performance
        performance_result = await intelligent_qa_system.get_qa_system_performance(days)
        
        return {
            "status": "SUCCESS",
            "phase": "PHASE_5_SYSTEM_PERFORMANCE",
            "performance_metrics": performance_result,
            "query_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting QA system performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"QA system performance query failed: {str(e)}")

@api_router.post("/generate-script-with-qa")
async def generate_script_with_intelligent_qa(request: ScriptRequest):
    """
    Phase 5: Script Generation with Automatic Intelligent QA
    Generates script and automatically runs intelligent QA with regeneration if needed
    """
    try:
        logger.info(f"Generating script with intelligent QA for prompt: {request.prompt[:100]}...")
        
        # First generate the script using existing endpoint logic
        script_response = await generate_script(request)
        
        # Run intelligent QA on the generated script
        qa_request = IntelligentQARequest(
            script=script_response.generated_script,
            original_prompt=request.prompt,
            target_platform="youtube",  # Default platform
            duration=request.duration,
            video_type=request.video_type,
            enable_regeneration=True
        )
        
        qa_result = await intelligent_qa_analysis(qa_request)
        
        # Return combined result
        return {
            "status": "SUCCESS",
            "phase": "PHASE_5_SCRIPT_GENERATION_WITH_QA",
            "script_generation": {
                "id": script_response.id,
                "original_prompt": script_response.original_prompt,
                "generated_script": script_response.generated_script,
                "video_type": script_response.video_type,
                "duration": script_response.duration,
                "created_at": script_response.created_at
            },
            "intelligent_qa": {
                "qa_id": qa_result.qa_id,
                "final_script": qa_result.final_script,
                "quality_threshold_met": qa_result.quality_threshold_met,
                "regeneration_performed": qa_result.regeneration_performed,
                "consensus_score": qa_result.consensus_validation["consensus_score"],
                "consensus_grade": qa_result.consensus_validation["consensus_grade"],
                "confidence_score": qa_result.confidence_score,
                "recommendations": qa_result.recommendations,
                "processing_time": qa_result.total_processing_time
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in script generation with QA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Script generation with QA failed: {str(e)}")

# =============================================================================
# END PHASE 5 ENDPOINTS
# =============================================================================

# =============================================================================
# STEP 2: FEW-SHOT LEARNING & PATTERN RECOGNITION ENDPOINTS
# =============================================================================

@api_router.post("/generate-script-few-shot", response_model=FewShotScriptResponse)
async def generate_script_few_shot(request: FewShotScriptRequest):
    """
    Generate scripts using Few-Shot Learning & Pattern Recognition
    
    This endpoint leverages curated high-performing examples and pattern recognition
    to generate scripts with proven techniques and structures.
    """
    try:
        # Initialize few-shot generator if not already done
        if not hasattr(few_shot_generator, 'nlp') or few_shot_generator.nlp is None:
            await few_shot_generator.initialize()
        
        # Create context profile
        context = ContextProfile(
            video_type=request.video_type,
            industry=request.industry,
            platform=request.platform,
            duration=request.duration,
            audience_tone=request.audience_tone,
            complexity_level=request.complexity_level,
            engagement_goals=request.engagement_goals
        )
        
        # Apply learned patterns to enhance the prompt
        pattern_result = await few_shot_generator.apply_learned_patterns(
            context=context,
            base_prompt=request.prompt
        )
        
        # Generate script using the enhanced prompt
        script_chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"few-shot-script-{str(uuid.uuid4())[:8]}",
            system_message=f"""You are an expert video script writer enhanced with Few-Shot Learning capabilities. You generate scripts by applying proven patterns from high-performing content.

Your writing incorporates:
1. PROVEN STRUCTURAL PATTERNS: Hook → Setup → Content → Climax → Resolution
2. ENGAGEMENT TECHNIQUES: Psychological triggers, retention cues, platform optimization
3. INDUSTRY BEST PRACTICES: {request.industry}-specific terminology and approaches
4. PLATFORM OPTIMIZATION: {request.platform}-native formatting and style

Generate engaging, high-quality scripts that follow proven successful patterns while maintaining authenticity and value."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Create duration mapping
        duration_mapping = {
            'short': '30-60 seconds',
            'medium': '1-3 minutes', 
            'long': '3-5 minutes'
        }
        duration_text = duration_mapping.get(request.duration, request.duration)
        
        script_prompt = f"""Generate a {request.duration} {request.video_type} video script optimized for {request.platform}.

ENHANCED PROMPT WITH LEARNED PATTERNS:
{pattern_result['enhanced_prompt']}

REQUIREMENTS:
- Duration: {request.duration} ({duration_text})
- Platform: {request.platform}
- Industry: {request.industry}
- Tone: {request.audience_tone}
- Complexity: {request.complexity_level}

Apply the learned patterns while creating an original, engaging script that follows proven success structures."""
        
        generated_script = await script_chat.send_message(UserMessage(text=script_prompt))
        
        # Extract learning insights
        learning_insights = [
            f"Applied {pattern_result['patterns_applied']} proven patterns",
            f"Leveraged {pattern_result['examples_used']} high-performing examples",
            f"Confidence score: {pattern_result['confidence_score']:.1f}/10",
            f"Enhanced prompt was {len(pattern_result['enhanced_prompt']) / len(request.prompt):.1f}x more detailed"
        ]
        
        # Store the generated script
        script_response = FewShotScriptResponse(
            original_prompt=request.prompt,
            enhanced_prompt=pattern_result['enhanced_prompt'],
            generated_script=generated_script,
            patterns_applied=pattern_result['patterns_applied'],
            examples_used=pattern_result['examples_used'],
            confidence_score=pattern_result['confidence_score'],
            learning_insights=learning_insights,
            pattern_details=pattern_result['pattern_details']
        )
        
        # Save to database
        await db.few_shot_scripts.insert_one(script_response.dict())
        
        logger.info(f"✅ Generated few-shot script with {pattern_result['patterns_applied']} patterns applied")
        
        return script_response
        
    except Exception as e:
        logger.error(f"Error in few-shot script generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Few-shot script generation failed: {str(e)}")

@api_router.post("/analyze-patterns", response_model=PatternAnalysisResponse)
async def analyze_patterns(request: PatternAnalysisRequest):
    """
    Analyze patterns in the example database for specific contexts
    
    Provides insights into what makes scripts successful in different contexts.
    """
    try:
        # Initialize few-shot generator if needed
        if not hasattr(few_shot_generator, 'nlp') or few_shot_generator.nlp is None:
            await few_shot_generator.initialize()
        
        # Get patterns for the specified context
        query = {request.context_type: request.context_value}
        cursor = few_shot_generator.patterns_collection.find({
            "applicable_contexts": {"$in": [request.context_value, "general"]}
        })
        patterns_data = await cursor.to_list(length=None)
        
        # Get example scripts for this context
        examples_cursor = few_shot_generator.examples_collection.find(query)
        examples_data = await examples_cursor.to_list(length=None)
        
        # Analyze top patterns
        top_patterns = []
        for pattern_data in sorted(patterns_data, key=lambda x: x.get('effectiveness_score', 0), reverse=True)[:5]:
            top_patterns.append({
                "name": pattern_data.get('template_name', 'Unknown'),
                "type": pattern_data.get('pattern_type', 'general'),
                "effectiveness": pattern_data.get('effectiveness_score', 0),
                "usage_guide": pattern_data.get('usage_guidelines', {}).get('when_to_use', 'General usage'),
                "example_count": len(pattern_data.get('example_scripts', []))
            })
        
        # Extract success factors
        success_factors = []
        for example in examples_data:
            success_factors.extend(example.get('success_factors', []))
        
        # Get most common success factors
        from collections import Counter
        common_factors = Counter(success_factors).most_common(5)
        top_success_factors = [factor for factor, count in common_factors]
        
        # Calculate effectiveness metrics
        if examples_data:
            avg_engagement = sum(ex.get('performance_metrics', {}).get('engagement_rate', 0) for ex in examples_data) / len(examples_data)
            avg_viral = sum(ex.get('performance_metrics', {}).get('viral_score', 0) for ex in examples_data) / len(examples_data)
            avg_retention = sum(ex.get('performance_metrics', {}).get('retention_rate', 0) for ex in examples_data) / len(examples_data)
        else:
            avg_engagement = avg_viral = avg_retention = 0
        
        # Generate recommendations
        recommendations = [
            f"Focus on {top_patterns[0]['name'] if top_patterns else 'structural patterns'} for best results",
            f"Top success factor: {top_success_factors[0] if top_success_factors else 'clear value proposition'}",
            f"Average engagement rate: {avg_engagement:.1f}/10 - {'above' if avg_engagement > 7 else 'at' if avg_engagement > 5 else 'below'} average",
            f"Recommended improvement: {'Increase viral elements' if avg_viral < 7 else 'Maintain current viral strategy'}"
        ]
        
        return PatternAnalysisResponse(
            context={request.context_type: request.context_value},
            patterns_found=len(patterns_data),
            top_patterns=top_patterns,
            success_factors=top_success_factors,
            recommendations=recommendations,
            effectiveness_metrics={
                "average_engagement": round(avg_engagement, 2),
                "average_viral_score": round(avg_viral, 2),
                "average_retention": round(avg_retention, 2)
            }
        )
        
    except Exception as e:
        logger.error(f"Error in pattern analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@api_router.post("/manage-example-database", response_model=ExampleDatabaseResponse)
async def manage_example_database(request: ExampleDatabaseRequest):
    """
    Manage the curated example database
    
    Allows rebuilding, adding examples, or querying the database status.
    """
    try:
        # Initialize few-shot generator if needed
        if not hasattr(few_shot_generator, 'nlp') or few_shot_generator.nlp is None:
            await few_shot_generator.initialize()
        
        if request.rebuild:
            # Clear existing examples and rebuild
            await few_shot_generator.examples_collection.delete_many({})
            await few_shot_generator.patterns_collection.delete_many({})
            
            # Rebuild database
            result = await few_shot_generator.build_example_database()
            
            # Extract patterns
            await few_shot_generator.extract_patterns()
            
            status = "rebuilt"
        else:
            # Get current status
            result = await few_shot_generator.get_system_stats()
            status = "current_status"
        
        # Add new examples if provided
        if request.add_examples:
            for example_data in request.add_examples:
                # Validate and add example
                await few_shot_generator.examples_collection.insert_one(example_data)
            
        # Get final statistics
        stats = await few_shot_generator.get_system_stats()
        
        return ExampleDatabaseResponse(
            status=status,
            examples_count=stats["database_stats"]["examples_count"],
            patterns_count=stats["database_stats"]["patterns_count"],
            categories=stats["database_stats"]["categories"],
            performance_metrics=stats["performance_averages"],
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error managing example database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database management failed: {str(e)}")

@api_router.get("/few-shot-stats")
async def get_few_shot_stats():
    """Get comprehensive statistics about the Few-Shot Learning system"""
    try:
        # Initialize few-shot generator if needed
        if not hasattr(few_shot_generator, 'nlp') or few_shot_generator.nlp is None:
            await few_shot_generator.initialize()
        
        stats = await few_shot_generator.get_system_stats()
        
        return {
            "status": "operational",
            "system_stats": stats,
            "capabilities": {
                "pattern_recognition": "✅ Active",
                "example_matching": "✅ Context-aware",
                "template_learning": "✅ Adaptive",
                "dynamic_selection": "✅ Intelligent"
            },
            "learning_effectiveness": {
                "pattern_application": f"{stats['database_stats']['patterns_count']} patterns available",
                "example_quality": f"Average {stats['performance_averages']['engagement_rate']}/10 engagement",
                "context_coverage": f"{len(stats['database_stats']['categories']['video_types'])} video types"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting few-shot stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

# =============================================================================
# END STEP 2: FEW-SHOT LEARNING ENDPOINTS
# =============================================================================

# Add CORS middleware BEFORE including router
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router in the main app
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

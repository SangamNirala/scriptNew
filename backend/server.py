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

class ScriptResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_prompt: str
    generated_script: str
    video_type: str
    duration: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PromptEnhancementRequest(BaseModel):
    original_prompt: str
    video_type: Optional[str] = "general"

class PromptEnhancementResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    enhancement_explanation: str

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
    """Enhance user's prompt to make it more effective for script generation"""
    try:
        # Create a new chat instance for prompt enhancement
        chat = LlmChat(
            api_key=GEMINI_API_KEY,
            session_id=f"enhance-{str(uuid.uuid4())[:8]}",
            system_message="""You are an expert script writing consultant specializing in creating engaging video content. Your job is to take basic user prompts and transform them into detailed, emotionally compelling briefs that will result in high-quality, engaging video scripts.

Key areas to enhance:
1. EMOTIONAL HOOKS: Add elements that create immediate emotional connection
2. STORYTELLING STRUCTURE: Suggest narrative arcs, character development, conflict/resolution
3. AUDIENCE ENGAGEMENT: Include techniques to maintain viewer attention throughout
4. VISUAL STORYTELLING: Add suggestions for visual elements that enhance the script
5. PACING & RHYTHM: Recommend timing and flow for maximum impact
6. CALL-TO-ACTION: Include compelling endings that drive viewer response

Always provide:
- Enhanced prompt that's 3-5x more detailed than the original
- Brief explanation of what you enhanced and why
- Keep the core intent but make it much more actionable for script generation"""
        ).with_model("gemini", "gemini-2.0-flash")

        enhancement_message = UserMessage(
            text=f"""Original prompt: "{request.original_prompt}"
Video type: {request.video_type}

Please enhance this prompt to make it more effective for generating an engaging video script. 

IMPORTANT: Format your response with proper paragraph breaks and line spacing for readability. Use double line breaks between major sections.

Return your response in this exact format:

ENHANCED_PROMPT:
[Your enhanced prompt here - make it detailed, specific, and emotionally compelling. Use proper paragraph breaks and formatting for readability. Separate different aspects with line breaks.]

EXPLANATION:
[Brief explanation of what you enhanced and why it will make the script better. Use proper paragraph formatting.]"""
        )

        response = await chat.send_message(enhancement_message)
        
        # Parse the response
        response_parts = response.split("EXPLANATION:")
        if len(response_parts) != 2:
            raise HTTPException(status_code=500, detail="Invalid AI response format")
        
        enhanced_prompt = response_parts[0].replace("ENHANCED_PROMPT:", "").strip()
        explanation = response_parts[1].strip()

        return PromptEnhancementResponse(
            original_prompt=request.original_prompt,
            enhanced_prompt=enhanced_prompt,
            enhancement_explanation=explanation
        )
        
    except Exception as e:
        logger.error(f"Error enhancing prompt: {str(e)}")
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

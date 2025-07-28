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

class AvatarVideoResponse(BaseModel):
    video_base64: str
    duration_seconds: float
    request_id: str

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
            system_message=f"""You are a world-class video script writer who creates emotionally compelling, highly engaging content that keeps viewers hooked from start to finish. You specialize in {request.video_type} content and understand the psychology of viewer retention.

CRITICAL REQUIREMENTS FOR ENGAGING SCRIPTS:

1. HOOK (First 3-5 seconds):
   - Start with a compelling question, shocking statement, or immediate promise
   - Create curiosity gap that MUST be filled
   - Use pattern interrupts to grab attention

2. STORYTELLING STRUCTURE:
   - Use proven narrative frameworks (Hero's Journey, Problem-Solution, Before-After)
   - Include conflict, tension, and resolution
   - Build emotional investment in characters/outcomes

3. PACING & FLOW:
   - Vary sentence length and rhythm
   - Use strategic pauses and emphasis
   - Include transition phrases that maintain momentum
   - Build to emotional peaks and strategic breaks

4. ENGAGEMENT TECHNIQUES:
   - Ask rhetorical questions to involve viewers mentally
   - Use "you" language to make it personal
   - Include relatable scenarios and emotions
   - Create "aha moments" and revelations

5. VISUAL STORYTELLING:
   - Write for the medium - include visual cues and scene descriptions
   - Suggest compelling b-roll and graphics
   - Use cinematic language that translates to engaging visuals

6. EMOTIONAL TRIGGERS:
   - Tap into core human emotions: fear, hope, curiosity, belonging
   - Use power words and vivid imagery
   - Create emotional peaks and valleys

7. RETENTION OPTIMIZATION:
   - Plant "seeds" early that pay off later
   - Use cliffhangers and open loops
   - Include unexpected twists or insights
   - End each section with a reason to keep watching

8. DURATION-SPECIFIC OPTIMIZATION:
   - Short (30s-1min): Rapid-fire value, single focused message
   - Medium (1-3min): Full story arc with development
   - Long (3-5min): Deep dive with multiple value points

Your scripts should be formatted with:
- Scene descriptions in [brackets]
- Speaker directions in (parentheses)
- Clear timing indicators
- Emphasis on KEY WORDS
- Strategic pauses marked as ...

Remember: Every word should serve viewer retention. If it doesn't add value or engagement, cut it."""
        ).with_model("gemini", "gemini-2.0-flash")

        script_message = UserMessage(
            text=f"""Create an engaging {request.duration} duration video script for {request.video_type} content based on this prompt:

"{request.prompt}"

Duration target: {request.duration}
Video type: {request.video_type}

Please create a script that maximizes viewer engagement and retention. Include all formatting, visual cues, and timing suggestions."""
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
    - Timestamps (0:00-0:03)
    - Scene descriptions [SCENE START: ...]
    - Speaker/narrator directions (Narrator – tone description)
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
        'NOTES', 'SCRIPT', 'DURATION', 'TYPE'
    ]
    
    # Track if we're in a metadata section
    in_metadata_section = False
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        # Skip empty lines
        if not line:
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
        
        # Skip standalone timestamps
        if re.match(r'^\(\d+:\d+[-–]\d+:\d+\)', line):
            continue
        
        # Skip pure scene descriptions in brackets
        if re.match(r'^\[.*\]$', line):
            continue
            
        # Skip standalone speaker directions
        if re.match(r'^\([^)]*(?:Narrator|Host|Speaker|VO|Voiceover|Testimonial)[^)]*\)$', line, re.IGNORECASE):
            continue
            
        # Now extract actual spoken content from mixed lines
        # Remove timestamps at the beginning
        line = re.sub(r'^\(\d+:\d+[-–]\d+:\d+\)\s*', '', line)
        
        # Remove scene descriptions in brackets
        line = re.sub(r'\[.*?\]', '', line)
        
        # Remove speaker directions - more comprehensive patterns
        line = re.sub(r'\([^)]*(?:Narrator|Host|Speaker|VO|Voiceover|Testimonial)[^)]*\)', '', line, re.IGNORECASE)
        line = re.sub(r'\([^)]*(?:tone|music|sound|audio|video|cut|scene|transition)[^)]*\)', '', line, re.IGNORECASE)
        line = re.sub(r'\([^)]*(?:–|—)[^)]*\)', '', line)  # Remove parentheses with dashes (speaker directions)
        
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
        
        if not request.audio_base64:
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
        
    except Exception as e:
        logger.error(f"Error generating avatar video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating avatar video: {str(e)}")

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

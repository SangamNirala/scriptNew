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
    Extract only the spoken content from a formatted script, removing:
    - Timestamps [0:00-0:05]
    - Scene headers [SCENE START], [HOOK], [PROBLEM], etc.
    - Speaker labels (NARRATOR:, HOST:, VOICEOVER:)
    - Tone/delivery instructions (Fast-paced, energetic)
    - Stage directions and metadata
    """
    
    # Start with the raw script
    clean_text = raw_script.strip()
    
    # Remove timestamps [0:00-0:05], [00:15-00:30], etc.
    clean_text = re.sub(r'\[\d+:\d+\-\d+:\d+\]', '', clean_text)
    clean_text = re.sub(r'\[\d+:\d+\]', '', clean_text)
    
    # Remove scene headers and labels in brackets
    # [SCENE START], [HOOK], [THE PROBLEM], [SOLUTION], etc.
    clean_text = re.sub(r'\[(?:SCENE|HOOK|PROBLEM|SOLUTION|INTRO|OUTRO|TRANSITION|CTA|CALL.*ACTION).*?\]', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\[[A-Z\s]+:\]', '', clean_text)
    clean_text = re.sub(r'\[[A-Z\s]+\]', '', clean_text)
    
    # Remove speaker labels like NARRATOR:, HOST:, VOICEOVER:, etc.
    clean_text = re.sub(r'^[A-Z\s]+(\([^)]+\))?:\s*', '', clean_text, flags=re.MULTILINE)
    clean_text = re.sub(r'\b(NARRATOR|HOST|VOICEOVER|SPEAKER|ANNOUNCER|PRESENTER)(\s*\([^)]+\))?:\s*', '', clean_text, flags=re.IGNORECASE)
    
    # Remove tone and delivery instructions in parentheses
    # (Fast-paced, energetic), (Calm, reassuring), (Excited), etc.
    clean_text = re.sub(r'\([^)]*(?:paced|energetic|calm|excited|dramatic|slow|fast|tone|voice|delivery|style)[^)]*\)', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\([^)]*(?:whisper|shout|loud|quiet|emphasis|stress)[^)]*\)', '', clean_text, flags=re.IGNORECASE)
    
    # Remove remaining stage directions and notes in parentheses (but keep natural speech in parentheses)
    # Remove if contains common stage direction words
    clean_text = re.sub(r'\([^)]*(?:camera|shot|zoom|pan|cut|fade|scene|background|music|sound|sfx|effect)[^)]*\)', '', clean_text, flags=re.IGNORECASE)
    
    # Remove remaining empty brackets and parentheses
    clean_text = re.sub(r'\[\s*\]', '', clean_text)
    clean_text = re.sub(r'\(\s*\)', '', clean_text)
    
    # Remove video production terms that might appear
    production_terms = [
        'B-ROLL', 'CUTAWAY', 'MONTAGE', 'GRAPHICS', 'TITLE CARD', 'LOWER THIRD',
        'FADE IN', 'FADE OUT', 'CUT TO', 'DISSOLVE', 'TRANSITION', 'OVERLAY'
    ]
    for term in production_terms:
        clean_text = re.sub(f'\\b{term}\\b[^\\n]*', '', clean_text, flags=re.IGNORECASE)
    
    # Remove markdown formatting
    clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)  # Bold **text**
    clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)      # Italic *text*
    clean_text = re.sub(r'__([^_]+)__', r'\1', clean_text)      # Bold __text__
    clean_text = re.sub(r'_([^_]+)_', r'\1', clean_text)        # Italic _text_
    
    # Clean up whitespace and line breaks
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)  # Normalize double line breaks
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)   # Remove excessive line breaks
    clean_text = re.sub(r'[ \t]+', ' ', clean_text)       # Normalize spaces
    clean_text = clean_text.strip()
    
    # If the result is too short or seems empty, return a basic cleanup
    if len(clean_text.strip()) < 20:
        # Fallback to basic cleanup
        fallback_text = raw_script
        fallback_text = re.sub(r'\[.*?\]', '', fallback_text)
        fallback_text = re.sub(r'\(.*?\)', '', fallback_text)
        fallback_text = re.sub(r'[A-Z\s]+:', '', fallback_text)
        fallback_text = ' '.join(fallback_text.split())
        return fallback_text if len(fallback_text.strip()) > 10 else raw_script
    
    return clean_text

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
        clean_text = request.text.strip()
        if not clean_text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Debug logging
        logger.info(f"Received TTS request with voice: {request.voice_name}")
        logger.info(f"Original text (first 100 chars): {clean_text[:100]}...")
        
        # Remove script formatting for better speech
        clean_text = clean_text.replace('[', '').replace(']', '')  # Remove scene descriptions
        clean_text = clean_text.replace('(', '').replace(')', '')  # Remove speaker directions  
        clean_text = clean_text.replace('**', '')  # Remove bold formatting
        clean_text = ' '.join(clean_text.split())  # Normalize whitespace
        
        logger.info(f"Cleaned text (first 100 chars): {clean_text[:100]}...")
        
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

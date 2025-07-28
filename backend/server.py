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
    - Timestamps, scene descriptions, speaker notes, production metadata
    - Section headers like TARGET DURATION, VIDEO TYPE, KEY RETENTION ELEMENTS
    - All bracketed content and parenthetical directions
    """
    
    # Start with the raw script
    lines = raw_script.strip().split('\n')
    clean_lines = []
    
    # Skip common section headers and metadata
    skip_sections = [
        'TARGET DURATION', 'VIDEO TYPE', 'VIDEO SCRIPT', 'SCRIPT:', 'KEY RETENTION ELEMENTS',
        'NOTES:', 'RETENTION ELEMENTS:', 'ADJUSTMENTS:', 'OPTIMIZATION:', 'METRICS:'
    ]
    
    in_skip_section = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines in processing (we'll add them back selectively)
        if not line:
            continue
            
        # Check if we're entering a section to skip
        if any(line.upper().startswith(section) for section in skip_sections):
            in_skip_section = True
            continue
            
        # Check if we're in a bullet point section (skip until next main section)
        if line.startswith('*') or line.startswith('•') or line.startswith('-'):
            in_skip_section = True
            continue
            
        # Skip lines that are clearly metadata or headers
        if line.upper() in ['SCRIPT:', 'NOTES:', 'KEY RETENTION ELEMENTS:', 'ADJUSTMENTS:']:
            in_skip_section = True
            continue
            
        # If line starts with a new section that looks like content, stop skipping
        if line.startswith('(') and ':' in line and 'SCENE' in line.upper():
            in_skip_section = False
            # Continue processing this line
            
        if in_skip_section:
            continue
            
        # Remove timestamps (0:00-0:03), (0:03-0:07), etc.
        line = re.sub(r'^\(\d+:\d+\-\d+:\d+\)', '', line).strip()
        
        # Remove scene descriptions [SCENE START: ...], [SCENE CHANGE: ...], [SCENE: ...]
        line = re.sub(r'\[SCENE[^]]*\]', '', line)
        line = re.sub(r'\[[^]]*SCENE[^]]*\]', '', line)
        line = re.sub(r'\[[^]]*cut[^]]*\]', '', line, flags=re.IGNORECASE)
        
        # Remove all other bracketed content [anything]
        line = re.sub(r'\[[^]]+\]', '', line)
        
        # Remove speaker directions (Narrator – tone description)
        line = re.sub(r'\([^)]*(?:Narrator|Host|Speaker|VO|Voiceover)[^)]*\)', '', line, flags=re.IGNORECASE)
        
        # Remove testimonial indicators
        line = re.sub(r'\(Testimonial[^)]*\)', '', line, flags=re.IGNORECASE)
        
        # Remove all remaining parenthetical directions
        line = re.sub(r'\([^)]*(?:tone|music|sound|audio|video)[^)]*\)', '', line, flags=re.IGNORECASE)
        
        # Clean up the line
        line = line.strip()
        
        # If line has content after cleaning, add it
        if line and len(line) > 2:
            # Remove any remaining formatting
            line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # Bold
            line = re.sub(r'\*([^*]+)\*', r'\1', line)      # Italic
            line = re.sub(r'__([^_]+)__', r'\1', line)      # Underline
            
            # Clean up extra spaces
            line = re.sub(r'\s+', ' ', line).strip()
            
            # Add the cleaned line
            clean_lines.append(line)
    
    # Join the lines and do final cleanup
    clean_text = ' '.join(clean_lines)
    
    # Remove any remaining brackets or parentheses that might be left
    clean_text = re.sub(r'[\[\]()]+', '', clean_text)
    
    # Clean up multiple spaces and normalize punctuation
    clean_text = re.sub(r'\s+', ' ', clean_text)
    clean_text = re.sub(r'\s*\.\.\.\s*', '... ', clean_text)  # Normalize ellipses
    clean_text = re.sub(r'\s*!\s*', '! ', clean_text)         # Normalize exclamation
    clean_text = re.sub(r'\s*\?\s*', '? ', clean_text)        # Normalize questions
    
    clean_text = clean_text.strip()
    
    # If the result is too short, try a more basic approach
    if len(clean_text) < 50:
        # Fallback: extract anything that looks like speech
        speech_patterns = re.findall(r'"([^"]+)"', raw_script)  # Quoted speech
        if speech_patterns:
            clean_text = ' '.join(speech_patterns)
        else:
            # Last resort: basic cleanup
            fallback = raw_script
            fallback = re.sub(r'\([^)]*\)', '', fallback)
            fallback = re.sub(r'\[[^]]*\]', '', fallback)
            fallback = re.sub(r'^[A-Z\s:]+$', '', fallback, flags=re.MULTILINE)
            fallback = ' '.join(fallback.split())
            if len(fallback.strip()) > len(clean_text.strip()):
                clean_text = fallback
    
    return clean_text.strip()

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

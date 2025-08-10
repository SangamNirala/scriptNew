from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional
import re
import time
from deep_translator import GoogleTranslator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Translation Models
class ScriptTranslationRequest(BaseModel):
    script_content: str = Field(..., description="Script content to translate")
    source_language: str = Field(default="en", description="Source language code (default: en)")
    target_language: str = Field(..., description="Target language code (e.g., hi, es, fr)")

class ScriptTranslationResponse(BaseModel):
    original_script: str
    translated_script: str
    source_language: str
    target_language: str
    translation_service: str
    success: bool

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/translate-script", response_model=ScriptTranslationResponse)
async def translate_script(request: ScriptTranslationRequest):
    """
    Translate script content from one language to another.
    - Uses deep-translator with GoogleTranslator by default (free, no key)
    - Preserves any text inside square brackets [ ... ] exactly as-is (do NOT translate image prompts)
    - Preserves AI IMAGE PROMPT: "..." structures exactly as-is in English
    - Preserves overall formatting like brackets [] and parentheses ()
    - Chunks long texts (>4500 chars) to avoid provider limits
    """
    try:
        logger.info(f"Translation requested: {request.source_language} -> {request.target_language}")

        original_text = request.script_content or ""

        # 1) Mask all [ ... ] segments so they remain in English and keep positions
        # We use distinctive placeholders unlikely to be altered by translators
        bracket_pattern = re.compile(r"\[[^\]]+\]")
        bracket_segments = bracket_pattern.findall(original_text)
        masked_text = original_text
        
        # Replace bracketed segments with placeholders
        for i, seg in enumerate(bracket_segments):
            placeholder = f"§§BR_{i}§§"
            masked_text = masked_text.replace(seg, placeholder, 1)
        
        # Also mask AI IMAGE PROMPT quoted content (keep English)
        # Example line: AI IMAGE PROMPT: "..."
        ai_image_pattern = re.compile(r"(AI\s+IMAGE\s+PROMPT\s*:?\s*)([\"'])([^\"']+)([\"'])", re.IGNORECASE)
        ai_image_segments = []  # store full quoted substrings including quotes
        def _ai_masker(m):
            idx = len(ai_image_segments)
            # Preserve the entire AI IMAGE PROMPT structure including the prefix
            full_structure = m.group(1) + m.group(2) + m.group(3) + m.group(4)
            ai_image_segments.append(full_structure)
            return f"§§IP_{idx}§§"
        masked_text = ai_image_pattern.sub(_ai_masker, masked_text)

        # Helper to restore placeholders robustly after translation
        def _restore_placeholders(text, segments, prefix):
            restored = text
            for i, seg in enumerate(segments):
                canonical = f"§§{prefix}_{i}§§"
                # Build tolerant regex: allow 1-3 leading/trailing §, optional spaces, and optional missing trailing §
                pattern = re.compile(rf"[§]{{1,3}}\s*{prefix}_{i}\s*[§]{{0,3}}", re.IGNORECASE)
                # If not found, try more permissive variants including plain token
                if not pattern.search(restored):
                    alt_patterns = [
                        re.compile(rf"{prefix}_{i}", re.IGNORECASE),
                        re.compile(rf"[§]{{0,3}}\s*{prefix}\s*_\s*{i}\s*[§]{{0,3}}", re.IGNORECASE),
                    ]
                    found = False
                    for p in alt_patterns:
                        if p.search(restored):
                            restored = p.sub(seg, restored, count=1)
                            found = True
                            break
                    if not found:
                        # last attempt: direct string replace for common truncation like '§§BR_i§'
                        common_var_1 = f"§§{prefix}_{i}§"
                        common_var_2 = f"§{prefix}_{i}§§"
                        if common_var_1 in restored:
                            restored = restored.replace(common_var_1, seg)
                        elif common_var_2 in restored:
                            restored = restored.replace(common_var_2, seg)
                else:
                    restored = pattern.sub(seg, restored, count=1)
            return restored

        # 2) Prepare chunks for translation (on the masked text)
        try:
            if len(masked_text) > 4500:
                words = masked_text.split()
                chunks = []
                current_chunk = []
                current_length = 0
                for word in words:
                    # +1 for space
                    if current_length + len(word) + 1 < 4500:
                        current_chunk.append(word)
                        current_length += len(word) + 1
                    else:
                        if current_chunk:
                            chunks.append(" ".join(current_chunk))
                        current_chunk = [word]
                        current_length = len(word)
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
            else:
                chunks = [masked_text]

            # 3) Translate each chunk using deep-translator
            translator = GoogleTranslator(source=request.source_language or "auto", target=request.target_language)
            translated_chunks = []
            for idx, chunk in enumerate(chunks):
                if chunk.strip():
                    if len(chunks) > 1:
                        time.sleep(0.5)  # gentle rate limit between chunk calls
                    translated_chunk = translator.translate(chunk)
                    translated_chunks.append(translated_chunk)
            translated_masked_text = " ".join(translated_chunks)

            # 4) Unmask preserved segments (image prompts and bracketed) back to original English
            restored_text = translated_masked_text
            # First restore AI image prompt quoted content
            restored_text = _restore_placeholders(restored_text, ai_image_segments, "IP")
            # Then restore bracketed segments
            restored_text = _restore_placeholders(restored_text, bracket_segments, "BR")

            return ScriptTranslationResponse(
                original_script=original_text,
                translated_script=restored_text,
                source_language=request.source_language,
                target_language=request.target_language,
                translation_service="deep-translator (Google)",
                success=True,
            )
        except Exception as te:
            logger.error(f"Translation service failed: {str(te)}")
            raise HTTPException(
                status_code=503,
                detail="Translation service temporarily unavailable. Please try again later.",
            )

    except HTTPException:
        # Re-raise HTTPExceptions (like 503 from translation service) without modification
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

# Include the router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
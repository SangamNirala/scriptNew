#!/usr/bin/env python3
"""
Detailed debugging script to trace the Hindi audio processing pipeline.
"""

import requests
import json

# Test the exact same functions that are used in the backend
def test_extract_functions_directly():
    print("🔍 DIRECT FUNCTION TESTING - HINDI CONTENT PROCESSING")
    print("=" * 70)
    
    # Copy exact functions from backend to test locally
    import re
    
    def extract_dialogue_with_timestamps(raw_script):
        dialogue_content = []
        seen_content = set()
        
        lines = raw_script.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are just timestamps (both bracketed and bare formats)
            if re.match(r'^\[\d+:\d+\s*[-–]\s*\d+:\d+\]$', line):  # [0:00-0:03]
                continue
            if re.match(r'^\d+:\d+\s*[-–]\s*\d+:\d+$', line):  # 0:00-0:03 (bare format)
                continue
                
            # Extract content after timestamp markers (bracketed format)
            timestamp_match = re.match(r'^\[\d+:\d+\s*[-–]\s*\d+:\d+\]\s*(.+)$', line)
            if timestamp_match:
                dialogue = timestamp_match.group(1).strip()
                if dialogue and dialogue not in seen_content:
                    dialogue_content.append(dialogue)
                    seen_content.add(dialogue)
                continue
            
            # Remove timestamps from the beginning of lines (both formats)
            line = re.sub(r'^\[\d+:\d+\s*[-–]\s*\d+:\d+\]\s*', '', line)  # Remove [0:00-0:03]
            line = re.sub(r'^\d+:\d+\s*[-–]\s*\d+:\d+\s*', '', line)  # Remove 0:00-0:03
                
            # Skip common production elements
            skip_patterns = [
                r'^\*\*.*\*\*$',  # **Bold text**
                r'^AI IMAGE PROMPT',
                r'^VISUAL:',
                r'^AUDIO:',
                r'^SCENE:',
                r'^NARRATOR:',
                r'^VOICE OVER:',
                r'^PRODUCTION NOTE',
                r'^NOTE:',
                r'^IMPORTANT:',
                r'^\[.*\]$',  # [Any bracketed content without timestamps]
            ]
            
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
                    
            if should_skip:
                continue
                
            # If it's regular dialogue content (not a timestamp line), include it
            if line and line not in seen_content and len(line) > 3:
                dialogue_content.append(line)
                seen_content.add(line)
        
        # Join with spaces for natural speech flow
        result = ' '.join(dialogue_content).strip()
        
        # Final cleanup - remove any remaining timestamps (both bracketed and bare formats)
        result = re.sub(r'\[\d+:\d+\s*[-–]\s*\d+:\d+\]', '', result)  # Remove [0:00-0:03]
        result = re.sub(r'\b\d+:\d+\s*[-–]\s*\d+:\d+\b', '', result)  # Remove 0:00-0:03 (bare format)
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    # Test with Hindi dialogue content (exact format from frontend)
    hindi_content = """0:00-0:03
नमस्ते और हमारे वीडियो में आपका स्वागत है।

0:03-0:06
आज हम स्वस्थ खाना पकाने की युक्तियों पर चर्चा करेंगे।"""

    print("📝 Raw Hindi Input:")
    print(f"'{hindi_content}'")
    print()
    
    # Process the content
    cleaned = extract_dialogue_with_timestamps(hindi_content)
    
    print("📝 Cleaned Hindi Output:")
    print(f"'{cleaned}'")
    print(f"📊 Length: {len(cleaned)} characters")
    print(f"📊 Empty: {'YES' if not cleaned.strip() else 'NO'}")
    
    # Check for Unicode content
    unicode_count = sum(1 for char in cleaned if ord(char) > 127)
    print(f"📊 Unicode characters: {unicode_count}")
    
    if cleaned.strip():
        print("✅ Text processing successful - Hindi content preserved")
        return cleaned
    else:
        print("❌ CRITICAL: Text processing failed - no content extracted!")
        return None

def test_edge_tts_with_hindi():
    print("\n" + "=" * 70)
    print("🔍 TESTING EDGE-TTS DIRECTLY WITH HINDI CONTENT")
    print("=" * 70)
    
    # Test Edge-TTS directly with Hindi content to see if it's a voice issue
    try:
        import asyncio
        import edge_tts
        
        async def test_hindi_tts():
            # Test with Hindi content directly
            hindi_text = "नमस्ते और हमारे वीडियो में आपका स्वागत है। आज हम स्वस्थ खाना पकाने की युक्तियों पर चर्चा करेंगे।"
            voice = "en-US-AriaNeural"
            
            print(f"📝 Testing text: '{hindi_text}'")
            print(f"🎵 Using voice: {voice}")
            
            try:
                communicate = edge_tts.Communicate(hindi_text, voice)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                
                print(f"📊 Generated audio length: {len(audio_data)} bytes")
                
                if len(audio_data) > 0:
                    print("✅ Edge-TTS successfully generated audio for Hindi content!")
                    return True
                else:
                    print("❌ Edge-TTS failed to generate audio for Hindi content")
                    return False
            except Exception as e:
                print(f"❌ Edge-TTS error: {e}")
                return False
        
        result = asyncio.run(test_hindi_tts())
        return result
    except ImportError:
        print("❌ Edge-TTS not available for direct testing")
        return None

def test_backend_api_with_logging():
    print("\n" + "=" * 70)
    print("🔍 TESTING BACKEND API WITH DETAILED REQUEST")
    print("=" * 70)
    
    # Test just the cleaned Hindi content (no timestamps)
    clean_hindi = "नमस्ते और हमारे वीडियो में आपका स्वागत है। आज हम स्वस्थ खाना पकाने की युक्तियों पर चर्चा करेंगे।"
    
    print(f"📝 Sending clean Hindi text to backend:")
    print(f"'{clean_hindi}'")
    print()
    
    request_data = {
        "text": clean_hindi,
        "voice_name": "en-US-AriaNeural"
    }
    
    try:
        response = requests.post("http://localhost:8001/api/generate-audio", json=request_data)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            audio_length = len(result.get('audio_base64', ''))
            print(f"✅ Clean Hindi text successfully generated audio!")
            print(f"📊 Audio data length: {audio_length} characters")
            return True
        else:
            print(f"❌ Backend failed with clean Hindi text")
            print(f"📄 Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🚨 DETAILED HINDI AUDIO DEBUG ANALYSIS")
    print()
    
    # Test 1: Verify text processing works correctly
    cleaned_text = test_extract_functions_directly()
    
    # Test 2: Test Edge-TTS directly (if available)
    edge_tts_result = test_edge_tts_with_hindi()
    
    # Test 3: Test backend with cleaned text
    if cleaned_text:
        backend_result = test_backend_api_with_logging()
    else:
        backend_result = False
        print("⚠️ Skipping backend test - no cleaned text available")
    
    print("\n" + "=" * 70)
    print("🎯 DEBUG ANALYSIS SUMMARY")
    print("=" * 70)
    
    if cleaned_text:
        print("✅ Text Processing: Working - Hindi content properly extracted")
    else:
        print("❌ Text Processing: BROKEN - this is likely the bug source")
    
    if edge_tts_result:
        print("✅ Edge-TTS: Working - can handle Hindi content")
    elif edge_tts_result is False:
        print("❌ Edge-TTS: BROKEN - cannot handle Hindi content")
    else:
        print("⚠️ Edge-TTS: Not tested")
    
    if backend_result:
        print("✅ Backend API: Working - can generate Hindi audio")
    else:
        print("❌ Backend API: BROKEN - issue with Hindi audio generation")
    
    print("\n🔍 The issue is likely:")
    if not cleaned_text:
        print("   - Text processing regex patterns failing on Hindi content")
    elif edge_tts_result is False:
        print("   - Edge-TTS voice not compatible with Hindi content")  
    else:
        print("   - Backend pipeline issue when processing raw dialogue content")

if __name__ == "__main__":
    main()
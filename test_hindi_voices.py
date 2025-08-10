#!/usr/bin/env python3
"""
Test to find Hindi-compatible voices in Edge-TTS
"""

import asyncio
import edge_tts

async def list_all_voices():
    print("🔍 FINDING ALL AVAILABLE VOICES IN EDGE-TTS")
    print("=" * 60)
    
    voices = await edge_tts.list_voices()
    
    # Look for Hindi voices
    hindi_voices = []
    english_voices = []
    
    for voice in voices:
        locale = voice.get('Locale', '')
        name = voice.get('Name', '')
        display_name = voice.get('FriendlyName', name)
        gender = voice.get('Gender', 'Unknown')
        
        if 'hi-' in locale.lower() or 'hindi' in display_name.lower():
            hindi_voices.append({
                'name': name,
                'display_name': display_name,
                'locale': locale,
                'gender': gender
            })
        elif 'en-' in locale.lower():
            english_voices.append({
                'name': name,
                'display_name': display_name,
                'locale': locale,
                'gender': gender
            })
    
    print(f"📊 Found {len(hindi_voices)} Hindi voices:")
    for voice in hindi_voices[:10]:  # Show first 10
        print(f"   - {voice['name']} ({voice['display_name']}) - {voice['locale']} - {voice['gender']}")
    
    print(f"\n📊 Found {len(english_voices)} English voices (showing first 5):")
    for voice in english_voices[:5]:
        print(f"   - {voice['name']} ({voice['display_name']}) - {voice['locale']} - {voice['gender']}")
    
    return hindi_voices, english_voices

async def test_hindi_with_different_voices():
    print("\n" + "=" * 60)
    print("🔍 TESTING HINDI TEXT WITH DIFFERENT VOICE TYPES")
    print("=" * 60)
    
    hindi_text = "नमस्ते और हमारे वीडियो में आपका स्वागत है।"
    
    # Test voices to try
    test_voices = [
        "en-US-AriaNeural",    # English voice (should fail)
        "hi-IN-SwaraNeural",   # Hindi voice (if available)
        "en-IN-NeerjaNeural",  # Indian English (might work)
    ]
    
    for voice_name in test_voices:
        print(f"\n🎵 Testing voice: {voice_name}")
        print(f"📝 Text: '{hindi_text}'")
        
        try:
            communicate = edge_tts.Communicate(hindi_text, voice_name)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            if len(audio_data) > 0:
                print(f"✅ SUCCESS: {len(audio_data)} bytes of audio generated")
            else:
                print(f"❌ FAILED: No audio generated")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

async def main():
    print("🚨 TESTING HINDI VOICE COMPATIBILITY IN EDGE-TTS")
    print()
    
    # Find all available voices
    hindi_voices, english_voices = await list_all_voices()
    
    # Test with different voice types
    await test_hindi_with_different_voices()
    
    print("\n" + "=" * 60)
    print("🎯 SOLUTION FOR HINDI AUDIO BUG:")
    print("=" * 60)
    
    if hindi_voices:
        print("✅ Hindi voices found! We can fix the bug by:")
        print("   1. Auto-detecting Hindi content in the backend")
        print("   2. Using Hindi-compatible voices for Hindi text")
        print("   3. Falling back to Indian English voices if needed")
        print(f"   Recommended voice: {hindi_voices[0]['name'] if hindi_voices else 'None'}")
    else:
        print("⚠️ No native Hindi voices found. Alternative solutions:")
        print("   1. Use Indian English voices (en-IN-*) for Hindi content")
        print("   2. Add language detection and voice mapping")
        print("   3. Provide user option to select Hindi-compatible voices")

if __name__ == "__main__":
    asyncio.run(main())
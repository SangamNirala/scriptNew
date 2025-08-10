#!/usr/bin/env python3
"""
Test script to reproduce and verify the fix for Hindi audio generation bug.

BUG: When content is translated to Hindi in Dialogue Only section, 
     the "Listen" button only plays timestamps instead of Hindi dialogue content.
"""

import sys
import os
sys.path.append('/app/backend')

from server import extract_clean_script, extract_dialogue_with_timestamps
import re

def test_hindi_audio_generation_bug():
    print("🔍 TESTING HINDI AUDIO GENERATION BUG")
    print("=" * 60)
    
    # Simulate the exact content format created by frontend extractDialogueOnly function
    # after Hindi translation (bare timestamps + Hindi dialogue)
    hindi_dialogue_content = """0:00-0:03
नमस्ते और हमारे वीडियो में आपका स्वागत है।

0:03-0:06
आज हम स्वस्थ खाना पकाने की युक्तियों पर चर्चा करेंगे।

0:06-0:10
पहले, आइए ताज़ी सामग्री के बारे में बात करते हैं।

0:10-0:15
गुणवत्ता पूर्ण भोजन चुनना महत्वपूर्ण है।"""

    print("📝 INPUT (Hindi Dialogue Content from Frontend):")
    print("-" * 50)
    print(hindi_dialogue_content)
    print()
    
    # Test current extract_clean_script function behavior
    print("🔍 TESTING: extract_clean_script() with Hindi content")
    print("-" * 50)
    
    try:
        # This should detect it's dialogue with timestamps and call extract_dialogue_with_timestamps
        cleaned_result = extract_clean_script(hindi_dialogue_content)
        print(f"✅ Result length: {len(cleaned_result)} characters")
        print(f"📄 Cleaned text: '{cleaned_result}'")
        print()
        
        # Check what content is actually returned
        if "0:00" in cleaned_result or "0:03" in cleaned_result:
            print("❌ BUG CONFIRMED: Timestamps found in cleaned text!")
            print("   The audio will speak timestamps instead of Hindi dialogue")
        else:
            print("✅ GOOD: No timestamps in cleaned text")
            
        # Check if Hindi content is preserved
        hindi_chars_in_input = sum(1 for char in hindi_dialogue_content if ord(char) > 127)
        hindi_chars_in_output = sum(1 for char in cleaned_result if ord(char) > 127)
        
        print(f"📊 Unicode characters in input: {hindi_chars_in_input}")
        print(f"📊 Unicode characters in output: {hindi_chars_in_output}")
        
        if hindi_chars_in_output == 0 and hindi_chars_in_input > 0:
            print("❌ CRITICAL BUG: All Hindi characters were removed!")
        elif hindi_chars_in_output < hindi_chars_in_input * 0.8:
            print("⚠️  WARNING: Significant Hindi content loss detected")
        else:
            print("✅ GOOD: Hindi content preserved")
            
    except Exception as e:
        print(f"❌ ERROR in extract_clean_script: {str(e)}")
    
    print()
    print("🔍 TESTING: extract_dialogue_with_timestamps() directly")
    print("-" * 50)
    
    try:
        # Test the specific function that should handle dialogue with timestamps
        dialogue_result = extract_dialogue_with_timestamps(hindi_dialogue_content)
        print(f"✅ Result length: {len(dialogue_result)} characters")
        print(f"📄 Dialogue text: '{dialogue_result}'")
        print()
        
        # Detailed analysis
        if not dialogue_result.strip():
            print("❌ CRITICAL: No dialogue content extracted!")
        elif "0:00" in dialogue_result or "0:03" in dialogue_result:
            print("❌ BUG: Timestamps not properly removed from dialogue")
        else:
            print("✅ GOOD: Timestamps properly removed")
            
        # Check Hindi content preservation
        hindi_words_expected = ["नमस्ते", "आज", "हम", "स्वस्थ", "खाना", "पकाने"]
        hindi_words_found = sum(1 for word in hindi_words_expected if word in dialogue_result)
        
        print(f"📊 Hindi words found: {hindi_words_found}/{len(hindi_words_expected)}")
        
        if hindi_words_found == 0:
            print("❌ CRITICAL BUG: No Hindi words found in result!")
            print("   This confirms the audio generation bug")
        elif hindi_words_found < len(hindi_words_expected) * 0.5:
            print("⚠️  WARNING: Partial Hindi content loss")
        else:
            print("✅ GOOD: Hindi dialogue content properly preserved")
            
    except Exception as e:
        print(f"❌ ERROR in extract_dialogue_with_timestamps: {str(e)}")
    
    print()
    print("🔍 TESTING: English content (baseline - should work)")
    print("-" * 50)
    
    english_dialogue_content = """0:00-0:03
Hello and welcome to our video.

0:03-0:06
Today we will discuss healthy cooking tips.

0:06-0:10
First, let's talk about fresh ingredients.

0:10-0:15
Choosing quality food is important."""

    try:
        english_result = extract_clean_script(english_dialogue_content)
        print(f"✅ English result: '{english_result}'")
        
        if "Hello" in english_result and "0:00" not in english_result:
            print("✅ BASELINE CONFIRMED: English dialogue processing works correctly")
        else:
            print("❌ ISSUE: English baseline processing has problems")
    except Exception as e:
        print(f"❌ ERROR in English baseline test: {str(e)}")

def test_regex_patterns_with_hindi():
    """Test specific regex patterns used in the functions"""
    print("\n" + "=" * 60)
    print("🔍 TESTING REGEX PATTERNS WITH HINDI CONTENT")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        ("0:00-0:03", "Bare timestamp"),
        ("नमस्ते और हमारे वीडियो में आपका स्वागत है।", "Hindi sentence"),
        ("0:03-0:06\nआज हम स्वस्थ खाना पकाने की युक्तियों पर चर्चा करेंगे।", "Timestamp + Hindi"),
    ]
    
    # Current patterns from extract_dialogue_with_timestamps
    timestamp_patterns = [
        r'^\[\d+:\d+\s*[-–]\s*\d+:\d+\]$',  # [0:00-0:03]
        r'^\d+:\d+\s*[-–]\s*\d+:\d+$',      # 0:00-0:03 (bare format)
    ]
    
    for text, description in test_cases:
        print(f"\n📝 Testing: {description}")
        print(f"   Text: '{text}'")
        
        for i, pattern in enumerate(timestamp_patterns):
            match = re.match(pattern, text)
            pattern_name = "Bracketed" if i == 0 else "Bare"
            print(f"   {pattern_name} timestamp pattern: {'✅ MATCH' if match else '❌ NO MATCH'}")

def main():
    print("🚨 CRITICAL BUG REPRODUCTION TEST: Hindi Audio Generation")
    print("Testing the issue where Hindi dialogue audio only plays timestamps\n")
    
    test_hindi_audio_generation_bug()
    test_regex_patterns_with_hindi()
    
    print("\n" + "=" * 60)
    print("🎯 EXPECTED BEHAVIOR AFTER FIX:")
    print("=" * 60)
    print("✅ Hindi dialogue content should be extracted without timestamps")
    print("✅ Audio generation should speak Hindi text: 'नमस्ते और हमारे...'") 
    print("✅ No timestamps should be spoken in the audio")
    print("✅ Voice selection should work with Hindi content")

if __name__ == "__main__":
    main()
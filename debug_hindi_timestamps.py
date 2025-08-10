#!/usr/bin/env python3

import sys
import re
import os

# Add backend directory to path
sys.path.append('/app/backend')

# Import the functions from server
from server import extract_clean_script, extract_dialogue_with_timestamps, detect_content_language

def test_hindi_timestamp_removal():
    print("=== Testing Hindi Timestamp Removal Logic ===\n")
    
    # Test case 1: Pure English content with timestamps (SHOULD work correctly)
    english_content = """0:00-0:03
Hello and welcome to our video. Today we will discuss healthy cooking tips.

0:04-0:07
First, let's talk about fresh ingredients and their importance."""

    print("1. ENGLISH CONTENT TEST:")
    print(f"Original: {repr(english_content)}")
    english_cleaned = extract_clean_script(english_content)
    print(f"Cleaned: {repr(english_cleaned)}")
    english_lang = detect_content_language(english_cleaned)
    print(f"Detected Language: {english_lang}")
    print()

    # Test case 2: Pure Hindi content with timestamps (THE PROBLEM CASE)
    hindi_content = """0:00-0:03
नमस्ते और हमारे वीडियो में आपका स्वागत है। आज हम स्वस्थ खाना बनाने के टिप्स पर चर्चा करेंगे।

0:04-0:07
पहले, आइए ताजे अवयवों और उनके महत्व के बारे में बात करते हैं।"""

    print("2. HINDI CONTENT TEST:")
    print(f"Original: {repr(hindi_content)}")
    hindi_cleaned = extract_clean_script(hindi_content)
    print(f"Cleaned: {repr(hindi_cleaned)}")
    hindi_lang = detect_content_language(hindi_cleaned)
    print(f"Detected Language: {hindi_lang}")
    print()

    # Test case 3: Mixed content with timestamps
    mixed_content = """0:00-0:03
नमस्ते hello and welcome to our video.

0:04-0:07
आज हम discuss healthy cooking tips."""

    print("3. MIXED CONTENT TEST:")
    print(f"Original: {repr(mixed_content)}")
    mixed_cleaned = extract_clean_script(mixed_content)
    print(f"Cleaned: {repr(mixed_cleaned)}")
    mixed_lang = detect_content_language(mixed_cleaned)
    print(f"Detected Language: {mixed_lang}")
    print()

    # Test case 4: Hindi content with bracketed timestamps
    hindi_bracketed = """[0:00-0:03]
नमस्ते और हमारे वीडियो में आपका स्वागत है।

[0:04-0:07]
आज हम स्वस्थ खाना बनाने के बारे में बात करेंगे।"""

    print("4. HINDI WITH BRACKETED TIMESTAMPS:")
    print(f"Original: {repr(hindi_bracketed)}")
    hindi_bracketed_cleaned = extract_clean_script(hindi_bracketed)
    print(f"Cleaned: {repr(hindi_bracketed_cleaned)}")
    hindi_bracketed_lang = detect_content_language(hindi_bracketed_cleaned)
    print(f"Detected Language: {hindi_bracketed_lang}")
    print()

    # Test the extract_dialogue_with_timestamps function directly
    print("5. DIRECT FUNCTION TESTING:")
    print("Testing extract_dialogue_with_timestamps with Hindi content:")
    direct_result = extract_dialogue_with_timestamps(hindi_content)
    print(f"Direct result: {repr(direct_result)}")
    direct_lang = detect_content_language(direct_result)
    print(f"Language of direct result: {direct_lang}")
    print()

    # Check if timestamps are being detected properly
    print("6. TIMESTAMP DETECTION TESTING:")
    
    # Check the regex patterns used in the code
    bare_timestamp_pattern = r'(?:^|\n)\d+:\d+\s*[-–]\s*\d+:\d+(?:\n|$)'
    bracketed_timestamp_pattern = r'\[\d+:\d+\s*[-–]\s*\d+:\d+\]'
    
    print(f"Checking bare timestamps in Hindi content: {bool(re.search(bare_timestamp_pattern, hindi_content))}")
    print(f"Checking bracketed timestamps in Hindi content: {bool(re.search(bracketed_timestamp_pattern, hindi_bracketed))}")
    
    # Check line-by-line processing
    print("\n7. LINE-BY-LINE ANALYSIS:")
    lines = hindi_content.split('\n')
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        bare_match = re.match(r'^\d+:\d+\s*[-–]\s*\d+:\d+$', line_stripped)
        print(f"Line {i}: {repr(line_stripped)} -> Bare timestamp match: {bool(bare_match)}")

if __name__ == "__main__":
    test_hindi_timestamp_removal()
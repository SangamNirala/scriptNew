#!/usr/bin/env python3
"""
Debug exact characters in translation
"""

import requests
import json

# Get backend URL from frontend .env
BACKEND_URL = "https://818d214a-61c3-4c1b-9e85-1b348a4dafc5.preview.emergentagent.com/api"

def debug_characters():
    """Debug the exact characters in the translation"""
    
    test_payload = {
        "text": "(Voiceover) Welcome to our kitchen! [CAMERA: Close-up of hands]",
        "source_language": "en",
        "target_language": "hi"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/translate-script",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            translated_text = data["translated_text"]
            print("Translated text:", translated_text)
            
            # Find the placeholder-like pattern
            import re
            
            # Look for any pattern that looks like our placeholder
            patterns = re.findall(r'§§[^§]*§§', translated_text)
            print(f"Found patterns: {patterns}")
            
            # Check character by character around the placeholder area
            if "§§" in translated_text:
                start_idx = translated_text.find("§§")
                end_idx = translated_text.find("§§", start_idx + 2) + 2
                placeholder_part = translated_text[start_idx:end_idx]
                print(f"Placeholder part: '{placeholder_part}'")
                print(f"Character codes: {[ord(c) for c in placeholder_part]}")
                
                # Check if it matches our expected pattern
                expected = "§§BR_0§§"
                print(f"Expected: '{expected}'")
                print(f"Expected codes: {[ord(c) for c in expected]}")
                print(f"Match: {placeholder_part == expected}")
                
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    debug_characters()
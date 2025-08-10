#!/usr/bin/env python3
"""
Debug exact characters in translation - more detailed
"""

import requests
import json

# Get backend URL from frontend .env
BACKEND_URL = "https://818d214a-61c3-4c1b-9e85-1b348a4dafc5.preview.emergentagent.com/api"

def debug_characters_detailed():
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
            
            # Look for the section symbol character
            if "§" in translated_text:
                print("Found section symbol!")
                # Find all occurrences and their context
                for i, char in enumerate(translated_text):
                    if char == "§":
                        start = max(0, i-5)
                        end = min(len(translated_text), i+10)
                        context = translated_text[start:end]
                        print(f"Section symbol at position {i}: '{context}'")
                        
                        # Check the next few characters
                        if i+7 < len(translated_text):
                            potential_placeholder = translated_text[i:i+8]
                            print(f"Potential placeholder: '{potential_placeholder}'")
                            print(f"Character codes: {[ord(c) for c in potential_placeholder]}")
            else:
                print("No section symbol found")
                # Print all characters and their codes
                print("All characters:")
                for i, char in enumerate(translated_text):
                    print(f"{i}: '{char}' ({ord(char)})")
                
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    debug_characters_detailed()
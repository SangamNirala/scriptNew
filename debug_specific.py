#!/usr/bin/env python3
"""
Debug specific bracket preservation case
"""

import requests
import json

# Get backend URL from frontend .env
BACKEND_URL = "https://57ddad44-739c-4487-b1cc-36db80fa8192.preview.emergentagent.com/api"

def test_specific_case():
    """Test the specific failing case"""
    
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
            print("Original text:", data["original_text"])
            print("Translated text:", data["translated_text"])
            print("Success:", data["success"])
            
            # Check if bracket is preserved
            if "[CAMERA: Close-up of hands]" in data["translated_text"]:
                print("✅ Bracket preserved correctly")
            else:
                print("❌ Bracket not preserved")
                print("Looking for placeholder patterns...")
                if "§§BR_" in data["translated_text"] or "§§br_" in data["translated_text"]:
                    print("❌ Placeholder not replaced back")
                    # Show all placeholders
                    import re
                    placeholders = re.findall(r'§§[bB][rR]_\d+§§', data["translated_text"])
                    print(f"Found placeholders: {placeholders}")
                else:
                    print("❌ Placeholder completely missing")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_specific_case()
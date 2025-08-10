#!/usr/bin/env python3
"""
Debug Translation Bracket Preservation
"""

import requests
import json

# Get backend URL from frontend .env
BACKEND_URL = "https://fdb88e2d-1c56-4983-889f-10699a9a2d8a.preview.emergentagent.com/api"

def test_bracket_preservation():
    """Test bracket preservation with simple case"""
    
    test_payload = {
        "text": "Hello [CAMERA: Close-up]",
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
            if "[CAMERA: Close-up]" in data["translated_text"]:
                print("✅ Bracket preserved correctly")
            else:
                print("❌ Bracket not preserved")
                print("Looking for placeholder patterns...")
                if "§§BR_" in data["translated_text"]:
                    print("❌ Placeholder not replaced back")
                else:
                    print("❌ Placeholder completely missing")
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_bracket_preservation()
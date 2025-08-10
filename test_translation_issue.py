#!/usr/bin/env python3
"""
Test script to debug translation issue with AI IMAGE PROMPTS
"""

import requests
import json
import time

# Test script content with AI IMAGE PROMPTS in the format shown in the user's images
test_script = '''
VIDEO SCRIPT: CONQUER YOUR FEARS

[SCENE 1] AI IMAGE PROMPT: "Abstract scene, swirling dark smoke morphing into a flock of birds taking flight, dramatic chiaroscuro lighting, volumetric light rays cutting through the smoke, high contrast, moody and ethereal, dark teal and grey color palette, cinematic, ultra-high resolution, photorealistic, use octane render, trending on artstation."

[SCENE 2] (Emerging aspirational tone) "Imagine a life free from fear. What would you do?" AI IMAGE PROMPT: "A vast mountain range, golden hour lighting, wind blowing through her hair, standing on the edge of a cliff, fearless expression with bold looking, hiking gear, wide angle lens adventure photography style, cinematic, volumetric light rays cutting through the smoke, high contrast, moody and ethereal, dark teal and grey color palette, cinematic, ultra-high resolution, photorealistic, use octane render, trending on artstation." 

[SCENE 3] The human mind naturally gravitates toward safety and comfort. But what if I told you that AI IMAGE PROMPT: "Close-up portrait of a person's face split in half, one side showing fear with dark shadows, other side showing confidence with bright golden lighting, dramatic contrast, professional photography lighting, cinematic portrait style, shallow depth of field, dark background."
'''

def test_translation_api():
    backend_url = "http://localhost:8001/api"
    
    # Test the translation endpoint
    test_payload = {
        "text": test_script,
        "source_language": "hi", 
        "target_language": "en"
    }
    
    print("Testing Translation API...")
    print("Original text:")
    print(test_script)
    print("\n" + "="*80 + "\n")
    
    try:
        response = requests.post(
            f"{backend_url}/translate-script",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Translation API Response:")
            print(f"Success: {result['success']}")
            print(f"Source Language: {result['source_language']}")
            print(f"Target Language: {result['target_language']}")
            print(f"Translation Service: {result['translation_service']}")
            print("\nTranslated text:")
            print(result['translated_text'])
            
            # Check if AI IMAGE PROMPT content is preserved
            original_ai_prompts = []
            translated_ai_prompts = []
            
            # Extract AI IMAGE PROMPTs from original
            import re
            ai_pattern = re.compile(r'AI.*IMAGE.*PROMPT.*?[:\s]*["\'][^"\']*["\']', re.IGNORECASE | re.DOTALL)
            original_matches = ai_pattern.findall(test_script)
            translated_matches = ai_pattern.findall(result['translated_text'])
            
            print("\n" + "="*80)
            print("AI IMAGE PROMPT ANALYSIS:")
            print(f"Original AI prompts found: {len(original_matches)}")
            for i, match in enumerate(original_matches):
                print(f"  {i+1}: {match[:100]}...")
            
            print(f"\nTranslated AI prompts found: {len(translated_matches)}")
            for i, match in enumerate(translated_matches):
                print(f"  {i+1}: {match[:100]}...")
                
            # Check if any AI prompts were incorrectly translated
            if len(original_matches) != len(translated_matches):
                print("\n❌ ISSUE: Number of AI IMAGE PROMPTs changed during translation!")
            
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_translation_api()
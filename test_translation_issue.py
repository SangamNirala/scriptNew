#!/usr/bin/env python3
"""
Test script to debug translation issue with AI IMAGE PROMPTS
"""

import requests
import json
import time

# Test script content with AI IMAGE PROMPTS in the format shown in the user's images
test_script = '''
ठीक है, यहाँ एक स्क्रिप्ट है, बस यह करने के लिए डिजाइन की गई है, प्रत्येक शॉट को एक स्टैंडअलोन के रूप में तैयार किया गया है, रेडी-टू-यूज एआई इमेज प्रॉम्प्ट स्वयं साइड पर ध्यान केंद्रित करना और प्लेटफॉर्म पर संगत गुणवत्ता पर ध्यान केंद्रित करना: वीडियो स्क्रिप्ट: अपने डर को जीतें

Image_placeholder_AI छवि ग्रुप के माध्यम से काटना, उच्च विपरीत, मूडी और ईथर, डार्क टील और ग्रे रंग पैलेट, सिनेमैटिक, अल्ट्रा-हाई रिज़ॉल्यूशन, फोटोरियलिस्टिक, ऑक्टेन रेंडर का उपयोग करें, आर्टस्टेशन पर ट्रेंडिंग।"_Image_placeholder_(डरावना संकेतगर्दन द्वारा "डर से मुक्त जीवन की कल्पना करें। आप क्या करेंगे?"_Image_placeholder_ai छवि प्रॉम्प्ट: "एक विशाल पर्वत श्रृंखला, गोल्डन आवर लाइटिंग, उसके बातों के माध्यम से हवा उड़ने, निर्भीक अभिव्यक्ति के साथ एक चट्टान के किनारे पर खड़ी प्रवा महिला, हाइकिंग गियर, वाइड एंगल लेंस एडवेंचर फोटोग्राफी स्टाइल।
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
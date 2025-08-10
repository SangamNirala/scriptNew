#!/usr/bin/env python3

import sys
import re
import os

# Add backend directory to path
sys.path.append('/app/backend')

# Import the functions from server
from server import extract_clean_script, extract_dialogue_with_timestamps, detect_content_language

def test_user_hindi_content():
    print("=== Testing User's Exact Hindi Content ===\n")
    
    # The exact content provided by the user
    user_hindi_content = """(0: 00-0: 03
भावना अटक गई? आप अकेले नहीं हैं।

0: 03-0: 06
लेकिन ठहराव आपका भाग्य नहीं है। समय के भीतर अजेय बल को उजागर करने का समय।

0: 06-0: 09
दुनिया का इंतजार है।

0: 09-0: 12
आपके सहित हर एक व्यक्ति, अप्रयुक्त क्षमता रखता है।

0: 12-0: 15
आज, हम उस चिंगारी को प्रज्वलित करते हैं। सीमाओं को भूल जाओ।

0: 15-0: 18
जीवन कर्वबॉल फेंकता है। असफलताएं होती हैं। में रेंगता है।

0: 18-0: 21
अभिभूत महसूस करना ठीक है ...

0: 21-0: 25
... लेकिन यह वहाँ रहने के लिए * ठीक नहीं है।

0: 25-0: 28
यह आपके कथा के मालिक होने के बारे में है, तब भी जब स्क्रिप्ट फिर से लिखी जाती है।

0: 28-0: 31
लचीलापन गिरने से बचने के बारे में नहीं है; यह हर बार मजबूत होने के बारे में है।

0: 31-0: 34
यह सीखने, अनुकूलन और विकसित होने के बारे में है।

0: 34-0: 37
छोटा शुरू करो। प्राप्त करने योग्य लक्ष्य निर्धारित करें। हर जीत का जश्न मनाएं ...

0: 37-0: 40
... कृतज्ञता का अभ्यास करें। सकारात्मक प्रभावों के साथ अपने आप को घेरें।

0: 40-0: 43
सफलता की कल्पना करें।

0: 43-0: 46
मानसिकता आपकी महाशक्ति है।

0: 46-0: 49
आप जितना सोचते हैं उससे कहीं अधिक सक्षम हैं।

0: 49-0: 52
अपनी क्षमता पर विश्वास करो। आंतरिक आलोचक को चुप कराएं।

0: 52-0: 55
अपनी प्रवृत्ति पर भरोसा करें। एकमात्र सीमाएँ वे हैं जिन्हें आप अपने लिए निर्धारित करते हैं।

0: 55-0: 58
आप अपने सबसे बड़े वकील हैं।

0: 58-1: 01
यह * आपका * पल है।

1: 01-1: 04
अपनी आंतरिक ताकत को हटा दें। चुनौती को गले लगाओ।

1: 04-1: 07
स्टेपिंग स्टोन्स में बाधाओं को बदल दें। भविष्य बनाने के लिए आपका है।

1: 07-1: 10
आज आप क्या हासिल करेंगे? टिप्पणियों में अपने लक्ष्यों को साझा करें!

1: 10-1: 13
किसी ऐसे व्यक्ति को टैग करें जिसे इस संदेश की आवश्यकता है। आइए अजेय व्यक्तियों के एक समुदाय का निर्माण करें!

1: 13-1: 15
आगे बढ़ो और जीतो!)"""

    print("USER'S HINDI CONTENT TEST:")
    print(f"Original length: {len(user_hindi_content)} characters")
    print(f"First 200 chars: {repr(user_hindi_content[:200])}")
    
    # Test the cleaned result
    cleaned_result = extract_clean_script(user_hindi_content)
    print(f"\nCleaned length: {len(cleaned_result)} characters")
    print(f"First 200 chars of cleaned: {repr(cleaned_result[:200])}")
    
    # Check if any timestamps remain
    timestamp_patterns = [
        r'\(\d+:\s*\d+\s*[-–]\s*\d+:\s*\d+',  # (0: 00-0: 03
        r'\d+:\s*\d+\s*[-–]\s*\d+:\s*\d+',    # 0: 00-0: 03
        r'\d+:\d+\s*[-–]\s*\d+:\d+',           # 0:00-0:03
    ]
    
    timestamps_found = []
    for pattern in timestamp_patterns:
        matches = re.findall(pattern, cleaned_result)
        if matches:
            timestamps_found.extend(matches)
    
    if timestamps_found:
        print(f"\n❌ PROBLEM: Found {len(timestamps_found)} timestamps in cleaned result:")
        for ts in timestamps_found[:5]:  # Show first 5
            print(f"  - {repr(ts)}")
    else:
        print(f"\n✅ SUCCESS: No timestamps found in cleaned result!")
    
    # Detect language
    detected_lang = detect_content_language(cleaned_result)
    print(f"Detected language: {detected_lang}")
    
    # Test specific problematic lines
    print(f"\nTESTING SPECIFIC TIMESTAMP FORMATS:")
    test_lines = [
        "(0: 00-0: 03",
        "0: 03-0: 06", 
        "1: 13-1: 15",
        "भावना अटक गई? आप अकेले नहीं हैं।"
    ]
    
    for line in test_lines:
        clean_line = extract_clean_script(line)
        print(f"  '{line}' → '{clean_line}'")
    
    print(f"\nFULL CLEANED TEXT:")
    print(f"{cleaned_result}")

if __name__ == "__main__":
    test_user_hindi_content()
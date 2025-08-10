#!/usr/bin/env python3
"""
Debug the regex pattern to understand why third AI IMAGE PROMPT is not being preserved
"""

import re

test_script = '''
VIDEO SCRIPT: CONQUER YOUR FEARS

[SCENE 1] AI IMAGE PROMPT: "Abstract scene, swirling dark smoke morphing into a flock of birds taking flight, dramatic chiaroscuro lighting, volumetric light rays cutting through the smoke, high contrast, moody and ethereal, dark teal and grey color palette, cinematic, ultra-high resolution, photorealistic, use octane render, trending on artstation."

[SCENE 2] (Emerging aspirational tone) "Imagine a life free from fear. What would you do?" AI IMAGE PROMPT: "A vast mountain range, golden hour lighting, wind blowing through her hair, standing on the edge of a cliff, fearless expression with bold looking, hiking gear, wide angle lens adventure photography style, cinematic, volumetric light rays cutting through the smoke, high contrast, moody and ethereal, dark teal and grey color palette, cinematic, ultra-high resolution, photorealistic, use octane render, trending on artstation." 

[SCENE 3] The human mind naturally gravitates toward safety and comfort. But what if I told you that AI IMAGE PROMPT: "Close-up portrait of a person's face split in half, one side showing fear with dark shadows, other side showing confidence with bright golden lighting, dramatic contrast, professional photography lighting, cinematic portrait style, shallow depth of field, dark background."
'''

# Test both patterns
pattern1 = re.compile(r'(AI\s+IMAGE\s+PROMPT\s*:?\s*)(["\'])([^"\']*?)(\2)', re.IGNORECASE | re.DOTALL)
pattern2 = re.compile(r'(AI\s+IMAGE\s+PROMPT\s*:?\s*["\'])(.*?)(["\'])', re.IGNORECASE | re.DOTALL)

print("Pattern 1 matches:")
matches1 = pattern1.findall(test_script)
for i, match in enumerate(matches1):
    print(f"Match {i+1}: {match[0]}{match[1]}{match[2][:50]}...{match[3]}")

print(f"\nTotal Pattern 1 matches: {len(matches1)}")

print("\nPattern 2 matches:")
matches2 = pattern2.findall(test_script)
for i, match in enumerate(matches2):
    print(f"Match {i+1}: {match[0]}{match[1][:50]}...{match[2]}")

print(f"\nTotal Pattern 2 matches: {len(matches2)}")

# Let's also try with substitution to see what gets replaced
print("\n" + "="*80)
print("SUBSTITUTION TEST:")
preserved_segments = {}
masked_text = test_script
placeholder_counter = 1000

def ai_replacer(match):
    global placeholder_counter
    full_match = match.group(0)  
    placeholder = f"999{placeholder_counter}999"
    preserved_segments[placeholder] = full_match
    print(f"Preserving: {full_match[:100]}...")
    placeholder_counter += 1
    return placeholder

masked_text = pattern1.sub(ai_replacer, masked_text)
print(f"\nMasked text:\n{masked_text}")
print(f"\nPreserved segments: {len(preserved_segments)}")
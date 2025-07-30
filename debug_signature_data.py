#!/usr/bin/env python3

import base64
from PIL import Image as PILImage
import io

# Test the signature data
signature_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="

print("🔍 DEBUG: Analyzing signature base64 data")
print(f"Length: {len(signature_data)}")

try:
    # Decode base64
    decoded_data = base64.b64decode(signature_data)
    print(f"Decoded length: {len(decoded_data)} bytes")
    
    # Try to open with PIL
    with PILImage.open(io.BytesIO(decoded_data)) as img:
        print(f"✅ Valid PNG image: {img.format}, size: {img.size}, mode: {img.mode}")
        
        # Check if it's a 1x1 pixel image (test image)
        if img.size == (1, 1):
            print("⚠️ WARNING: This is a 1x1 pixel test image, not a real signature!")
        
except Exception as e:
    print(f"❌ Error processing signature: {e}")

print("\n🔍 Let's check what a real signature should look like...")
print("A real signature image should be much larger (typically 5000+ characters when base64 encoded)")
print("This appears to be test data from the testing agent, not real signature uploads")
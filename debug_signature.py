#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append('/app/backend')

from server import db, LegalMateAgents
import base64
from PIL import Image as PILImage
import io
import logging

async def debug_signature():
    """Debug signature data retrieval and processing"""
    
    print("🔍 DEBUG: Signature Data Investigation")
    
    # Find a contract with signatures
    contracts_with_sigs = await db.contracts.find({
        "$or": [
            {"first_party_signature": {"$ne": None}},
            {"second_party_signature": {"$ne": None}}
        ]
    }).to_list(5)
    
    if not contracts_with_sigs:
        print("❌ No contracts with signatures found in database")
        return
    
    contract = contracts_with_sigs[0]
    print(f"📄 Found contract with signatures: {contract.get('id', 'No ID')}")
    
    # Check first party signature
    fp_sig = contract.get('first_party_signature')
    sp_sig = contract.get('second_party_signature')
    
    print(f"🖊️ First Party Signature: {'Present' if fp_sig else 'None'}")
    if fp_sig:
        print(f"   Type: {type(fp_sig)}")
        print(f"   Length: {len(fp_sig) if fp_sig else 0}")
        if isinstance(fp_sig, str) and len(fp_sig) > 50:
            print(f"   Starts with: {fp_sig[:50]}...")
        
        # Test signature processing
        try:
            print("   Testing signature processing...")
            processed = LegalMateAgents.process_signature_image(fp_sig)
            print(f"   ✅ Signature processing successful, result type: {type(processed)}")
            
            # Test PIL image opening
            try:
                with PILImage.open(processed) as img:
                    print(f"   ✅ PIL can open image: {img.format}, {img.size}")
            except Exception as pil_e:
                print(f"   ❌ PIL error: {pil_e}")
                
        except Exception as e:
            print(f"   ❌ Signature processing failed: {e}")
    
    print(f"🖊️ Second Party Signature: {'Present' if sp_sig else 'None'}")
    if sp_sig:
        print(f"   Type: {type(sp_sig)}")
        print(f"   Length: {len(sp_sig) if sp_sig else 0}")
        
        # Test signature processing
        try:
            print("   Testing signature processing...")
            processed = LegalMateAgents.process_signature_image(sp_sig)
            print(f"   ✅ Signature processing successful, result type: {type(processed)}")
        except Exception as e:
            print(f"   ❌ Signature processing failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_signature())
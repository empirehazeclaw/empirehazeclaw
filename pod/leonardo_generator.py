#!/usr/bin/env python3
"""
Leonardo.ai Image Generator
Uses Leonardo.ai API for image generation
"""

import os
import requests
import json
import sys

# Leonardo.ai API
LEONARDO_API_KEY = os.environ.get("LEONARDO_API_KEY", "")
LEONARDO_URL = "https://cloud.leonardo.ai/api/rest/v1/generations"

def generate_image(prompt: str, output_path: str = None):
    """Generate image using Leonardo.ai API"""
    
    if not LEONARDO_API_KEY:
        return {"error": "No LEONARDO_API_KEY set"}
    
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use a popular model
    payload = {
        "prompt": prompt,
        "modelId": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9",  # Leonardo Phoenix
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "guidance_scale": 7,
        "num_inference_steps": 30
    }
    
    try:
        response = requests.post(LEONARDO_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generation_id = result.get("generationId")
            
            # Poll for result
            return {"pending": True, "generation_id": generation_id}
        else:
            return {
                "error": f"API Error: {response.status_code}",
                "message": response.text[:200]
            }
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "A cute cartoon snake with sunglasses, colorful background, POD design"
    
    print(f"🎨 Generating: {prompt}")
    
    result = generate_image(prompt)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('error')}")
    elif result.get("pending"):
        print(f"⏳ Generation started: {result['generation_id']}")
        print("\n📝 To use:")
        print("1. Get Leonardo API key: https://app.leonardo.ai/api-access")
        print("2. Set: export LEONARDO_API_KEY='your_key'")
        print("3. Run again")

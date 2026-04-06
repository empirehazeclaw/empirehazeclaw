#!/usr/bin/env python3
"""
Ideogram Image Generator
Uses Ideogram API to generate images from prompts
"""

import os
import requests
import json

# Ideogram API configuration
IDEOGRAM_API_KEY = os.environ.get("IDEOGRAM_API_KEY", "")
IDEOGRAM_URL = "https://api.ideogram.ai/v1/generate"

def generate_image(prompt: str, style: str = "AUTO", aspect_ratio: str = "1:1"):
    """Generate image from text prompt using Ideogram API"""
    
    if not IDEOGRAM_API_KEY:
        return {"error": "No IDEOGRAM_API_KEY set. Get one at https://ideogram.ai/settings/api"}
    
    headers = {
        "Api-Key": IDEOGRAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": prompt,
        "style": style,
        "aspect_ratio": aspect_ratio,
        "resolution": "1536x1024"
    }
    
    try:
        response = requests.post(IDEOGRAM_URL, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            # Return the image URL
            if result.get("data") and len(result["data"]) > 0:
                return {
                    "success": True,
                    "image_url": result["data"][0].get("url"),
                    "prompt": prompt
                }
        else:
            return {
                "error": f"API Error: {response.status_code}",
                "message": response.text
            }
            
    except Exception as e:
        return {"error": str(e)}

def generate_pod_design(prompt: str, output_path: str = None):
    """Generate POD design and optionally save"""
    
    result = generate_image(prompt)
    
    if result.get("success"):
        print(f"✅ Image generated!")
        print(f"   Prompt: {result['prompt'][:50]}...")
        print(f"   URL: {result['image_url']}")
        
        if output_path:
            # Download image
            img_response = requests.get(result["image_url"])
            if img_response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                print(f"   Saved to: {output_path}")
        
        return result
    else:
        print(f"❌ Error: {result.get('error')}")
        return result

if __name__ == "__main__":
    import sys
    
    # Example usage
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "A cute snake with sunglasses, cartoon style, transparent background"
    
    print(f"🎨 Generating: {prompt}")
    generate_pod_design(prompt)

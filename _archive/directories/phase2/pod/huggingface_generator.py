#!/usr/bin/env python3
"""
Hugging Face Image Generator - Free!
Uses free inference API for image generation
"""

import os
import requests
import json
import sys

# Hugging Face API - Free inference endpoint
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
HF_TOKEN = os.environ.get("HF_TOKEN", "")

def generate_image(prompt: str, output_path: str = None):
    """Generate image using Hugging Face Inference API"""
    
    if not HF_TOKEN:
        return {"error": "No HF_TOKEN set. Get free token at https://huggingface.co/settings/tokens"}
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "guidance_scale": 7.5,
            "num_inference_steps": 30
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            image_bytes = response.content
            
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                print(f"✅ Saved to: {output_path}")
            
            return {
                "success": True,
                "prompt": prompt,
                "saved_to": output_path
            }
        else:
            return {
                "error": f"API Error: {response.status_code}",
                "message": response.text[:200]
            }
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Default prompt or from command line
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "A cute cartoon snake with sunglasses, colorful background, POD design"
    
    print(f"🎨 Generating: {prompt}")
    print("⏳ This may take 30-60 seconds...")
    
    result = generate_image(prompt)
    
    if result.get("success"):
        print("✅ Image generated successfully!")
    else:
        print(f"❌ Error: {result.get('error')}")
        print("\n📝 To use:")
        print("1. Get free token: https://huggingface.co/settings/tokens")
        print("2. Set: export HF_TOKEN='your_token'")
        print("3. Run again")

#!/usr/bin/env python3
"""
🎨 fal.ai Integration
Image & Video Generation API
"""
import os
import requests

FAL_KEY = os.getenv("FAL_API_KEY", "")

# Popular Models on fal.ai
MODELS = {
    # Image
    "flux": "fal-ai/flux/dev",
    "sdxl": "fal-ai/stable-diffusion-xl",
    # Video
    "kling": "fal-ai/kling-video/v1/standard",
    "luma": "fal-ai/luma-photon",
    "animov": "fal-ai/animov",
}

def generate_image(prompt, model="flux", key=None):
    """Generate image using fal.ai"""
    api_key = key or FAL_KEY
    
    if not api_key:
        return {"error": "No API Key - get from fal.ai"}
    
    url = f"https://queue.fal.run/{MODELS.get(model, MODELS['flux'])}"
    
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {"prompt": prompt}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def generate_video(prompt, model="kling", key=None):
    """Generate video using fal.ai"""
    api_key = key or FAL_KEY
    
    if not api_key:
        return {"error": "No API Key"}
    
    url = f"https://queue.fal.run/{MODELS.get(model, MODELS['kling'])}"
    
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {"prompt": prompt}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🎨 fal.ai Integration")
    print("Available Models:")
    for name, model in MODELS.items():
        print(f"  {name}: {model}")

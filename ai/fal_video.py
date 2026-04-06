#!/usr/bin/env python3
"""
🎬 fal.ai Video Generator
Funktioniert mit minimax-video
"""
import os
import requests
import time

FAL_KEY = os.getenv("FAL_API_KEY", "")

def generate_video(prompt, model="minimax-video", key=None):
    """Generate video using fal.ai"""
    api_key = key or FAL_KEY
    
    if not api_key:
        return {"error": "No API Key"}
    
    url = f"https://queue.fal.run/fal-ai/{model}"
    
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {"prompt": prompt}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        if "request_id" in result:
            request_id = result["request_id"]
            print(f"⏳ Video wird generiert... Request ID: {request_id}")
            
            # Poll for completion
            status_url = result["status_url"]
            while True:
                time.sleep(10)
                status_response = requests.get(status_url, headers=headers)
                status = status_response.json()
                
                if status.get("status") == "COMPLETED":
                    # Get result
                    final_response = requests.get(result["response_url"], headers=headers)
                    return final_response.json()
                elif "detail" in status:
                    return {"error": status["detail"]}
        
        return result
    except Exception as e:
        return {"error": str(e)}

# Test
if __name__ == "__main__":
    print("🎬 fal.ai Video Generator")
    print("Funktionierende Models: minimax-video")
    print("")
    print("Usage:")
    print('  generate_video("a hero fighting", model="minimax-video")')

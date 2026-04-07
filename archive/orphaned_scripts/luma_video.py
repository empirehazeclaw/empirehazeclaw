#!/usr/bin/env python3
"""
Luma Dream Machine Integration
Video generation with AI

Hinweis: Luma API erfordert API Key von https://lumalabs.ai
"""

import os
import json
import requests
import time

# Config
LUMA_API_KEY = os.environ.get("LUMA_API_KEY", "")
LUMA_API_URL = "https://api.lumalabs.ai/dream-machine/v1"

def generate_video(prompt: str, duration: int = 5) -> dict:
    """Generiert Video mit Luma Dream Machine"""
    
    if not LUMA_API_KEY:
        return {
            "status": "error",
            "message": "LUMA_API_KEY nicht gesetzt!"
        }
    
    headers = {
        "Authorization": f"Bearer {LUMA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "duration": duration
    }
    
    try:
        # Video generieren
        response = requests.post(
            f"{LUMA_API_URL}/generations",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "generation_id": data.get("id"),
                "message": "Video wird generiert..."
            }
        else:
            return {
                "status": "error",
                "message": f"API Error: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def check_status(generation_id: str) -> dict:
    """Prüft Status der Video-Generierung"""
    
    if not LUMA_API_KEY:
        return {"status": "error", "message": "No API Key"}
    
    headers = {"Authorization": f"Bearer {LUMA_API_KEY}"}
    
    try:
        response = requests.get(
            f"{LUMA_API_URL}/generations/{generation_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": data.get("status"),
                "video_url": data.get("assets", {}).get("video"),
                "progress": data.get("progress", 0) * 100
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
🎬 Luma Dream Machine Video Generator

Usage: 
  python3 luma_video.py generate "dein prompt"
  python3 luma_video.py status <generation_id>
  python3 luma_video.py setup

Setup:
  export LUMA_API_KEY="dein_api_key"
""")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "setup":
        print("""
🔧 Luma Setup:

1. Gehe zu https://lumalabs.ai
2. Account erstellen (kostenlos)
3. API Key generieren
4. Setze den Key:
   export LUMA_API_KEY="dein_key"
   
Gratis: 5 Videos/Monat
        """)
    
    elif command == "generate":
        prompt = " ".join(sys.argv[2:])
        result = generate_video(prompt)
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        gen_id = sys.argv[2] if len(sys.argv) > 2 else ""
        if not gen_id:
            print("Bitte Generation ID angeben")
        else:
            print(json.dumps(check_status(gen_id), indent=2))
    
    else:
        print(f"Unbekannter Befehl: {command}")

if __name__ == "__main__":
    main()

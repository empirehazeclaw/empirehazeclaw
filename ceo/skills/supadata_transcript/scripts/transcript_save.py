#!/usr/bin/env python3
"""Speichert YouTube Transcript in KG + Research Memory."""

import sys
import os
import json
import requests
import re
from datetime import datetime

SUPADATA_API_KEY = ""  # wird aus secrets.env geladen

def load_secrets():
    path = os.path.expanduser("~/.openclaw/secrets/secrets.env")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if line.startswith("SUPADATA_API_KEY="):
                    return line.split("=", 1)[1].strip()
    return os.environ.get("SUPADATA_API_KEY", "")

def extract_video_id(url: str) -> str:
    if "youtube.com/watch" in url:
        params = dict(p.split("=") for p in url.split("?")[1].split("&") if "v=" in p)
        return params.get("v", "")
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/shorts/" in url:
        return url.split("shorts/")[1].split("?")[0]
    return url

def get_transcript(video_id: str, api_key: str) -> str:
    url = "https://api.supadata.ai/v1/youtube/transcript"
    headers = {"x-api-key": api_key}
    params = {"videoId": video_id}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        content = data.get("content", [])
        return " ".join([seg.get("text", "") for seg in content])
    elif resp.status_code == 404:
        return "NOT_FOUND"
    else:
        return f"ERROR_{resp.status_code}"

def save_to_kg(video_id: str, url: str, transcript: str):
    """Speichert Transcript als KG Entity."""
    kg_path = os.path.expanduser("~/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json")
    
    with open(kg_path, 'r') as f:
        kg = json.load(f)
    
    entity_key = f"YouTube-Transcript-{video_id}"
    timestamp = datetime.utcnow().isoformat()
    
    kg['entities'][entity_key] = {
        "type": "transcript",
        "category": "transcript",
        "facts": [{
            "content": transcript[:8000],  # KG-Tokens schonen
            "source_url": url,
            "extracted_at": timestamp,
            "confidence": 0.95,
            "category": "transcript"
        }],
        "priority": "MEDIUM",
        "created": timestamp,
        "last_accessed": timestamp,
        "access_count": 1,
        "decay_score": 1
    }
    
    with open(kg_path, 'w') as f:
        json.dump(kg, f, indent=2)
    
    return entity_key

def save_to_research(video_id: str, url: str, transcript: str):
    """Speichert Transcript in Research Memory."""
    research_dir = os.path.expanduser("~/.openclaw/workspace/ceo/research/")
    os.makedirs(research_dir, exist_ok=True)
    
    safe_name = f"{video_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    filepath = os.path.join(research_dir, f"{safe_name}.txt")
    
    with open(filepath, 'w') as f:
        f.write(f"# YouTube Transcript\n")
        f.write(f"URL: {url}\n")
        f.write(f"Video ID: {video_id}\n")
        f.write(f"Extracted: {datetime.utcnow().isoformat()}\n")
        f.write(f"\n---\n\n")
        f.write(transcript)
    
    return filepath

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcript_save.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    video_id = extract_video_id(url)
    
    api_key = load_secrets()
    if not api_key:
        print("Error: SUPADATA_API_KEY not found")
        sys.exit(1)
    
    print(f"Fetching transcript for {video_id}...")
    transcript = get_transcript(video_id, api_key)
    
    if transcript == "NOT_FOUND":
        print("No transcript available for this video.")
        sys.exit(1)
    elif transcript.startswith("ERROR_"):
        print(f"API Error: {transcript}")
        sys.exit(1)
    
    print(f"Transcript ({len(transcript)} chars) fetched.")
    
    entity_key = save_to_kg(video_id, url, transcript)
    print(f"✅ Saved to KG: {entity_key}")
    
    filepath = save_to_research(video_id, url, transcript)
    print(f"✅ Saved to research: {filepath}")

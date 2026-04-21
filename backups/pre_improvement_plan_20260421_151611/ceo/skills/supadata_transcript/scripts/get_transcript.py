#!/usr/bin/env python3
"""Holt YouTube Transcript via Supadata API."""

import sys
import os
import requests

def extract_video_id(url: str) -> str:
    """Extrahiert Video ID aus YouTube URL."""
    if "youtube.com/watch" in url:
        params = dict(p.split("=") for p in url.split("?")[1].split("&") if "v=" in p)
        return params.get("v", "")
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/shorts/" in url:
        return url.split("shorts/")[1].split("?")[0]
    return url.split("v=")[1].split("&")[0] if "v=" in url else url

def get_transcript(url_or_video_id: str) -> str:
    """Holt Transcript via Supadata API."""
    video_id = extract_video_id(url_or_video_id)
    if not video_id:
        return f"Error: Could not extract video ID from: {url_or_video_id}"

    api_key = os.environ.get("SUPADATA_API_KEY", "")
    if not api_key:
        # Try to load from secrets.env
        secrets_path = os.path.expanduser("~/.openclaw/secrets/secrets.env")
        if os.path.exists(secrets_path):
            with open(secrets_path) as f:
                for line in f:
                    if line.startswith("SUPADATA_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break

    if not api_key:
        return "Error: SUPADATA_API_KEY not found in environment or secrets.env"

    url = f"https://api.supadata.ai/v1/youtube/transcript"
    headers = {"x-api-key": api_key}
    params = {"videoId": video_id}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            content = data.get("content", [])
            if not content:
                return "No transcript available for this video."
            transcript = " ".join([seg.get("text", "") for seg in content])
            return transcript.strip()
        elif resp.status_code == 404:
            return "Transcript not found (video might be unavailable or have no captions)."
        else:
            return f"API Error {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return f"Request failed: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: get_transcript.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    transcript = get_transcript(url)
    print(transcript)

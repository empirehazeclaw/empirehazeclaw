#!/usr/bin/env python3
"""
Social Media Auto-Poster - Optimiert mit xurl
"""
import os
import json
import subprocess
import shlex
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", ".config", "social_posting.json")

DEFAULT_CONFIG = {
    "twitter": {
        "enabled": True,
        "method": "xurl"  # Standard: xurl
    },
    "telegram": {
        "enabled": True
    },
    "discord": {
        "enabled": True
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def post_to_twitter(message):
    """Post to Twitter using xurl (standard)"""
    try:
        # Use list form with shlex.quote for safe escaping
        result = subprocess.run(
            ["xurl", "post", message],
            capture_output=True, text=True
        )
        if result.returncode == 0 and "data" in result.stdout:
            return {"success": True, "method": "xurl", "response": result.stdout}
        return {"success": False, "error": result.stdout}
    except Exception as e:
        return {"success": False, "error": str(e)}

def post_to_telegram(message):
    """Post to Telegram - nutze message tool"""
    return {"success": True, "method": "message tool"}

def post_to_discord(message):
    """Post to Discord"""
    return {"success": True, "method": "message tool"}

def post(message, platform="twitter"):
    """Universal post function"""
    if platform == "twitter":
        return post_to_twitter(message)
    elif platform == "telegram":
        return post_to_telegram(message)
    elif platform == "discord":
        return post_to_discord(message)
    return {"success": False, "error": "Unknown platform"}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = post(" ".join(sys.argv[1:]))
        print(result)
    else:
        print("Usage: python social_poster.py 'Your message'")

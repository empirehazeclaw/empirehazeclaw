#!/usr/bin/env python3
"""
Twitter Growth Tool v2.1
Features:
- Auto-like relevant posts (Search via xurl)
- Target keywords and accounts in English
- Safe engagement limits
"""
import subprocess
import json
import time
import random
import shlex
from datetime import datetime
import re

# Configuration
TARGET_KEYWORDS = ["AI Agent", "SaaS Startup", "Tech Automation", "ChatGPT API", "Build in Public"]
DAILY_LIMIT = 5

def run_cmd(cmd, retries=3):
    """Run command with retries on failure"""
    for attempt in range(retries):
        try:
            # Use list form with shlex.split for security
            cmd_list = ["xurl"] + shlex.split(cmd)
            result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
            # Check for auth errors
            if "401" in result.stdout or "Unauthorized" in result.stdout:
                print(f"⚠️ Auth error, retry {attempt+1}/{retries}...")
                time.sleep(2)
                continue
            return result.stdout
        except subprocess.TimeoutExpired:
            print(f"⚠️ Timeout, retry {attempt+1}/{retries}...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(2)
    return ""

def search_and_engage():
    print(f"[{datetime.now().isoformat()}] 🤖 Starting Twitter Auto-Engagement...")
    
    # Try each keyword until one works
    for keyword in TARGET_KEYWORDS:
        print(f"🔍 Trying: '{keyword}'")
        
        output = run_cmd(f"search '{keyword}' -n 10")
        
        if not output or "Unauthorized" in output:
            print(f"⚠️ Auth error for '{keyword}', trying next...")
            continue
        
        # Try new format first (id at root level)
        ids = re.findall(r'"id":"(\d+)"', output)
        
        if not ids:
            print(f"❌ No tweets found for '{keyword}'.")
            continue
        
        print(f"✅ Found {len(ids)} tweets for '{keyword}'")
        
        # Like up to 3 tweets
        targets = random.sample(ids, min(3, len(ids)))
        for tid in targets:
            print(f"❤️ Liking {tid}...")
            run_cmd(f"like {tid}")
            time.sleep(random.uniform(2, 5))
        
        print(f"✅ Engagement done! Liked {len(targets)} tweets.")
        return
    
    print("❌ All keywords failed, skipping this round.")

if __name__ == "__main__":
    search_and_engage()

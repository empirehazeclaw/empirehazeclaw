#!/usr/bin/env python3
"""
Twitter Growth Tool v3.0 - WITH AUTO-REPLY
Features:
- Auto-like relevant posts
- Auto-reply to mentions (SAFE: only 2-3 per day, very natural)
- Target keywords and accounts in English
- Safe engagement limits to avoid bans
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
DAILY_LIKE_LIMIT = 5
DAILY_REPLY_LIMIT = 2  # Keep low to avoid bans!

# Auto-reply templates (natural, not spammy)
REPLY_TEMPLATES = [
    "Great point! 🤔",
    "Totally agree! 💯",
    "This is exactly what we need in B2B!",
    "Love this approach 🚀",
    "Interesting perspective! Thanks for sharing.",
    "Couldn't agree more! 🔥",
]

def run_cmd(cmd, *args):
    """Run xurl command safely without shell=True"""
    try:
        cmd_list = ["xurl", cmd] + list(args)
        result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception as e:
        print(f"Error: {e}")
        return ""

def auto_like():
    print(f"[{datetime.now().isoformat()}] ❤️ Auto-Like...")
    
    keyword = random.choice(TARGET_KEYWORDS)
    output = run_cmd("search", keyword, "-n", "10")
    
    ids = re.findall(r'"id":\s*"(\d+)"', output)
    if not ids:
        print("❌ No tweets found.")
        return 0
    
    targets = random.sample(ids, min(3, len(ids)))
    for tid in targets:
        print(f"  ❤️ Liking {tid}...")
        run_cmd("like", tid)
        time.sleep(random.uniform(3, 6))
    
    print(f"✅ Liked {len(targets)} tweets.")
    return len(targets)

def auto_reply():
    print(f"[{datetime.now().isoformat()}] 💬 Auto-Reply to mentions...")
    
    # Get mentions
    output = run_cmd("mentions", "-n", "5")
    
    # Extract tweet IDs
    ids = re.findall(r'"id":\s*"(\d+)"', output)
    if not ids:
        print("❌ No new mentions.")
        return 0
    
    # Reply to max 2 mentions
    targets = random.sample(ids, min(2, len(ids)))
    
    for tid in targets:
        reply = random.choice(REPLY_TEMPLATES)
        print(f"  💬 Replying to {tid}: {reply}")
        # Escape reply properly for shell
        run_cmd("reply", tid, "--text", reply)
        time.sleep(random.uniform(5, 10))
    
    print(f"✅ Replied to {len(targets)} mentions.")
    return len(targets)

def main():
    print(f"[{datetime.now().isoformat()}] 🐦 Twitter Growth v3.0 Starting...")
    
    likes = auto_like()
    time.sleep(random.uniform(5, 10))
    replies = auto_reply()
    
    print(f"✅ Done! {likes} likes, {replies} replies.")

if __name__ == "__main__":
    main()

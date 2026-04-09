#!/usr/bin/env python3
"""
Twitter Growth Script - Uses xurl (Twitter API v2)
"""
import subprocess
import time

def post_tweet(text):
    """Post a tweet using xurl"""
    result = subprocess.run(
        ["xurl", "post", text],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return True, result.stdout
    return False, result.stderr

def search_tweets(query, limit=10):
    """Search tweets using xurl"""
    # xurl doesn't have search, so we'll skip this for now
    return [], "xurl doesn't support search yet"

# Test
print("Testing xurl post...")
success, msg = post_tweet("🚀 Test from EmpireHazeClaw! #AI")
if success:
    print("✅ Posted successfully!")
else:
    print(f"❌ Error: {msg}")

#!/usr/bin/env python3
"""
Twitter Growth Tool v3 - XURL ONLY
Verwendet xurl für alle Twitter-Operationen
Status: 25.03.2026 - API Cap erreicht, NUR POST funktioniert
"""
import subprocess
import json
import time
import shlex
from datetime import datetime

def run_cmd(cmd, retries=3):
    """Run xurl command safely without shell=True"""
    for attempt in range(retries):
        try:
            # Use list form - split cmd into parts safely
            cmd_list = ["xurl"] + shlex.split(cmd)
            result = subprocess.run(
                cmd_list, 
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout + result.stderr
            if "401" in output or "Unauthorized" in output:
                print(f"⚠️ Auth error, retry {attempt+1}/{retries}...")
                time.sleep(2)
                continue
            return output
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(2)
    return ""

def post_tweet(text):
    """Post a tweet"""
    print(f"📤 Posting: {text[:50]}...")
    output = run_cmd(f'post "{text}"')
    if "data" in output and "id" in output:
        print(f"✅ Posted successfully!")
        return True
    print(f"⚠️ Post failed: {output[:100]}")
    return False

def get_whoami():
    """Get current user info"""
    output = run_cmd("whoami")
    try:
        return json.loads(output)
    except:
        return None

def main():
    print(f"[{datetime.now().isoformat()}] 🤖 Twitter Growth Tool v3 (xurl only)")
    print("=" * 50)
    
    # Check whoami
    user = get_whoami()
    if user:
        print(f"✅ Logged in as: @{user.get('username', 'unknown')}")
    else:
        print("❌ Not logged in - check xurl auth")
        return
    
    # Test post
    test_tweet = "🤖 AI agents automating everything - managed hosting für deutsche Unternehmen 🇩🇪 #AI #ChatGPT #SaaS"
    post_tweet(test_tweet)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🛡️ Social Media Safety Lock
Blockiert alle Posts bis Nico approved
"""
import os
import sys
import json
from datetime import datetime

APPROVAL_FILE = "/home/clawbot/.openclaw/workspace/.social_approval"

def check_approval():
    """Prüft ob Social Media Posting erlaubt ist"""
    
    # Check ob Datei existiert mit gültigem Token
    if not os.path.exists(APPROVAL_FILE):
        return False
    
    with open(APPROVAL_FILE, 'r') as f:
        data = json.load(f)
    
    # Check ob Token gültig ist
    token = data.get('token', '')
    expires = data.get('expires', '')
    
    if not token or not expires:
        return False
    
    # Check ob abgelaufen
    expiry_date = datetime.fromisoformat(expires)
    if datetime.now() > expiry_date:
        return False
    
    return True

def request_approval(platform):
    """Request approval from Nico"""
    print(f"⛔ BLOCKIERT: {platform} Posting")
    print("")
    print("Du musst erst Nico fragen!")
    print(f"Frage: 'Kann ich auf {platform} posten?'")
    print("")
    sys.exit(1)

def block_if_social(cmd):
    """Blockt CMD falls social media"""
    cmd_lower = cmd.lower()
    
    # Keywords die auf posting hindeuten
    social_keywords = [
        'xurl post', 'xurl reply', 'xurl retweet',
        'buffer', 'tiktok', 'twitter', 'instagram',
        'facebook', 'linkedin', 'post to', 'tweet'
    ]
    
    for keyword in social_keywords:
        if keyword in cmd_lower:
            if not check_approval():
                request_approval(keyword)

if __name__ == "__main__":
    # Test Modus
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        block_if_social(cmd)
    else:
        print("🛡️ Social Safety Lock aktiv")
        print(f"Approval Status: {'✅ ERLAUBT' if check_approval() else '❌ GESPERRT'}")

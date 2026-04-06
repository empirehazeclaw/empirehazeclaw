#!/usr/bin/env python3
"""
Discord Message Sender
Sendet Nachrichten an Discord ohne Agent-Kontext
"""

import os
import requests
import sys

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")

def send_discord(message):
    """Send message via Discord Webhook"""
    if not DISCORD_WEBHOOK:
        print("❌ DISCORD_WEBHOOK nicht gesetzt")
        return False
    
    data = {"content": message}
    try:
        r = requests.post(DISCORD_WEBHOOK, json=data, timeout=10)
        if r.status_code in [200, 204]:
            print("✅ Nachricht gesendet!")
            return True
        else:
            print(f"❌ Error: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Test"
    send_discord(msg)

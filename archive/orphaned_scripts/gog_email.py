#!/usr/bin/env python3
"""
📧 Gmail via gog - For outreach
"""
import os
import subprocess

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")

def send_email(to, subject, body):
    """Send email via gog"""
    if not TOKEN:
        return {"error": "No token"}
    
    result = subprocess.run([
        "gog", "gmail", "send",
        "--to", to,
        "--subject", subject,
        "--body", body,
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    
    return {"success": True, "output": result.stdout}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 3:
        print(send_email(sys.argv[1], sys.argv[2], sys.argv[3]))

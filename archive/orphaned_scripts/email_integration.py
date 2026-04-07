#!/usr/bin/env python3
"""
📧 EMAIL INTEGRATION
====================
Ready for when Gmail auth is complete
"""

import subprocess
import json

# Configuration
ACCOUNT = "empirehazeclaw@gmail.com"

def is_authenticated():
    """Check if Gmail is authenticated"""
    result = subprocess.run(
        ["gog", "gmail", "search", "test"],
        capture_output=True,
        text=True
    )
    return "No auth" not in result.stderr

def check_emails(query="newer_than:1d"):
    """Check emails with given query"""
    if not is_authenticated():
        return {"error": "Not authenticated", "action_needed": "gog auth add empirehazeclaw@gmail.com --services gmail"}
    
    result = subprocess.run(
        ["gog", "--account", ACCOUNT, "gmail", "search", query],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return {"success": True, "emails": result.stdout}
    return {"error": result.stderr}

def get_outlook_responses():
    """Get emails that might be responses to outreach"""
    return check_emails("subject:Re OR subject:AW OR subject:Antwort")

# CLI
if __name__ == "__main__":
    print("📧 Email Integration")
    print(f"Authenticated: {is_authenticated()}")
    
    if is_authenticated():
        print("\nRecent emails:")
        print(check_emails())
    else:
        print("\n⚠️ Run: gog auth add empirehazeclaw@gmail.com --services gmail")

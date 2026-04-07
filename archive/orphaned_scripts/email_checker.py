#!/usr/bin/env python3
"""
📧 EMAIL CHECKER
===============
Checks for new emails using gog CLI
"""

import subprocess
import json
from datetime import datetime

def check_gmail():
    """Check Gmail using gog CLI"""
    try:
        # Try to list recent emails
        result = subprocess.run(
            ["gog", "--account", "empirehazeclaw@gmail.com", "gmail", "search", "newer_than:1h"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return {
                "status": "success",
                "emails": len(lines),
                "details": lines[:5]
            }
        else:
            return {
                "status": "error",
                "message": result.stderr or "Auth needed"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_unread_count():
    """Get unread email count"""
    result = check_gmail()
    if result.get("status") == "success":
        return result.get("emails", 0)
    return 0

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "count":
        print(f"Unread: {get_unread_count()}")
    else:
        result = check_gmail()
        print(f"Status: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"Emails: {result.get('emails')}")
        else:
            print(f"Error: {result.get('message')}")

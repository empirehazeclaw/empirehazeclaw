#!/usr/bin/env python3
"""
"""
import os

RESEND_KEY = os.getenv("RESEND_API_KEY")

def send_email(to, subject, html):
    if not RESEND_KEY:
        print("RESEND_API_KEY not set")
        return False
    
    
    try:
            "to": to,
            "subject": subject,
            "html": html
        })
        return r
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        send_email(sys.argv[1], sys.argv[2], sys.argv[3])

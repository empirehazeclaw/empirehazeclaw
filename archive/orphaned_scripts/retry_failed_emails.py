#!/usr/bin/env python3
"""
📧 Retry Failed Emails
Liest emails aus der queue und versucht sie erneut zu senden.
"""

import json
from pathlib import Path
from datetime import datetime

def retry_queue():
    queue_file = Path.home() / ".openclaw" / "workspace" / "data" / "email_queue" / "failed_emails.json"
    
    if not queue_file.exists():
        print("✅ Queue ist leer")
        return
    
    with open(queue_file, 'r') as f:
        queue = json.load(f)
    
    if not queue:
        print("✅ Queue ist leer")
        return
    
    print(f"📧 {len(queue)} Emails in der Queue...")
    
    # Import send_email
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from lib.gmail_api import send_email
    
    success = []
    failed = []
    
    for email in queue:
        ok, msg = send_email(
            email.get("to"),
            email.get("subject"),
            email.get("body")
        )
        
        if ok:
            success.append(email)
            print(f"  ✅ {email.get('to')}")
        else:
            failed.append(email)
            print(f"  ❌ {email.get('to')}: {msg}")
    
    # Save remaining failed
    if failed:
        with open(queue_file, 'w') as f:
            json.dump(failed, f, indent=2)
        print(f"\n⚠️ {len(failed)} Emails noch in Queue")
    else:
        queue_file.unlink()
        print(f"\n✅ Alle Emails gesendet!")

if __name__ == "__main__":
    retry_queue()

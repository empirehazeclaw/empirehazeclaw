#!/usr/bin/env python3
"""
📧 Gmail API Direct Sender
Uses existing OAuth token from gogcli
"""

import os
import sys
import json
import base64
import urllib.request
from pathlib import Path

TOKEN_FILE = Path.home() / ".config/gogcli/token.env"

def get_token():
    """Get access token from gogcli token file"""
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        for line in f:
            if line.startswith("access_token="):
                return line.split("=", 1)[1].strip()
    return None

def send_email(to_email, subject, body, from_email="empirehazeclaw@gmail.com"):
    """Send email via Gmail API with queue fallback"""
    from pathlib import Path
    
    # Ensure queue directory exists
    queue_dir = Path.home() / ".openclaw" / "workspace" / "data" / "email_queue"
    queue_dir.mkdir(parents=True, exist_ok=True)
    
    token = get_token()
    if not token:
        # Save to retry queue
        queue_file = queue_dir / "failed_emails.json"
        import json
        from datetime import datetime
        
        queue = []
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                try:
                    queue = json.load(f)
                except:
                    queue = []
        
        queue.append({
            "to": to_email,
            "subject": subject,
            "body": body,
            "from": from_email,
            "failed_at": datetime.now().isoformat()
        })
        
        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
        
        return False, f"Token missing - saved to queue ({len(queue)} pending)"
    
    # ... rest of send_email
    
    # Build RFC 2822 email with proper UTF-8 encoding
    # For UTF-8 subjects, we need to use encoded-word format
    subject_encoded = f"=?utf-8?B?{base64.b64encode(subject.encode('utf-8')).decode('ascii')}?="
    
    email_lines = [
        f"To: {to_email}",
        f"From: EmpireHazeClaw <{from_email}>",
        f"Subject: {subject_encoded}",
        "Content-Type: text/plain; charset=utf-8",
        "",
        body
    ]
    email = "\r\n".join(email_lines)
    
    # Base64url encode
    encoded = base64.urlsafe_b64encode(email.encode()).decode()
    encoded = encoded.rstrip("=")
    
    # Send via Gmail API
    data = json.dumps({"raw": encoded}).encode()
    
    req = urllib.request.Request(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return True, f"Sent! ID: {result.get('id', 'unknown')}"
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        return False, f"HTTP {e.code}: {error.get('error', {}).get('message', e.reason)}"
    except Exception as e:
        return False, str(e)

def test_connection():
    """Test token validity"""
    token = get_token()
    if not token:
        return False, "No token"
    
    req = urllib.request.Request(
        "https://gmail.googleapis.com/gmail/v1/users/me/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return True, f"Connected as: {data.get('emailAddress')}"
    except urllib.error.HTTPError as e:
        return False, f"Token expired or invalid: {e.code}"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    if args.test:
        ok, msg = test_connection()
        print(f"{'✅' if ok else '❌'} {msg}")
    else:
        ok, msg = send_email(args.to, args.subject, args.body)
        print(f"{'✅' if ok else '❌'} {msg}")

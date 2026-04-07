#!/usr/bin/env python3
"""
Bounce Handler - Automatisch Bounces erkennen und löschen (GOG Version)
Nutzt GOG CLI für Gmail
"""
import subprocess
import os
import json
from pathlib import Path

BOUNCED_FILE = "data/bounced_leads.json"
TOKEN_FILE = os.path.expanduser("~/.config/gogcli/token.env")

def get_token():
    """Liest Access Token aus token.env"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            for line in f:
                if line.startswith('access_token='):
                    return line.split('=')[1].strip()
    except:
        pass
    return None

def gog_command(args):
    """Führt GOG Befehl aus mit korrektem Token"""
    token = get_token()
    if not token:
        print("❌ Kein GOG Token gefunden")
        return None, 1
    
    env = os.environ.copy()
    env['GOG_ACCESS_TOKEN'] = token
    
    result = subprocess.run(
        ['gog'] + args,
        capture_output=True,
        text=True,
        env=env
    )
    return result.stdout, result.returncode

def get_bounce_emails():
    """Hole alle Bounce-Notification IDs - erweiterter Filter"""
    search_queries = [
        # Deutsche Bounce-Meldungen
        "subject:Zustellungsfehler",
        "subject:Nicht zustellbar",
        "subject:E-Mail konnte nicht zugestellt werden",
        "subject:Übermittlung fehlgeschlagen",
        
        # Englische Bounce-Meldungen
        "subject:delivery status",
        "subject:undeliverable",
        "subject:bounce",
        "subject:delivery failed",
        "subject:mail delivery failed",
        "subject:returned to sender",
        "subject:message rejected",
        "subject:address not found",
        "subject:invalid recipient",
        "subject:550 5.1.1",
        "subject:550 5.1.2",
        "subject:554 5.7.1",
        
        # Von Mailer-Daemon
        "from:mailer-daemon",
        "from:postmaster",
        
        # Automated messages
        "subject:Automated message",
        "subject:Auto-Reply",
        "subject:Out of Office",
        
        #Failure notifications
        "subject:Failure notice",
        "subject:DNS error",
        "subject:host not found",
    ]
    
    ids = []
    for query in search_queries:
        stdout, code = gog_command([
            "gmail", "search", query,
            "--account", "empirehazeclaw@gmail.com",
            "--limit", "100"
        ])
        
        if code == 0 and stdout:
            for line in stdout.split('\n'):
                if line.startswith('19d'):
                    parts = line.split()
                    if parts:
                        msg_id = parts[0]
                        if msg_id not in ids:
                            ids.append(msg_id)
    
    return ids

def trash_email(msg_id):
    """Verschiebe Email in Trash via GOG modify"""
    stdout, code = gog_command([
        "gmail", "messages", "modify", msg_id,
        "--remove", "INBOX",
        "--add", "TRASH",
        "--account", "empirehazeclaw@gmail.com"
    ])
    return code == 0

def main():
    print("=== 🗑️ BOUNCE HANDLER (GOG) ===")
    print()
    
    # Get bounce IDs
    bounce_ids = get_bounce_emails()
    
    print(f"📪 {len(bounce_ids)} Bounce-Mails gefunden")
    
    if not bounce_ids:
        print("✅ Keine Bounces zu löschen")
        return
    
    deleted = 0
    for msg_id in bounce_ids:
        if trash_email(msg_id):
            deleted += 1
            print(f"   🗑️ In Trash verschoben: {msg_id}")
    
    print(f"\n✅ {deleted} Bounce-Emails in Trash!")

if __name__ == "__main__":
    main()

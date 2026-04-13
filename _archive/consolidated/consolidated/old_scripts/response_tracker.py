#!/usr/bin/env python3
"""
📊 Response Tracker - Skill
Trackt Antworten auf unsere Outreach Emails

Nutzung: python3 scripts/response_tracker.py
"""
import smtplib
import imaplib
import email
from email.header import decode_header
import os
import json
from datetime import datetime, timedelta

CONFIG = {
    "imap_server": "imap.gmail.com",
    "email": "empirehazeclaw@gmail.com",
    "app_password": "export GMAIL_APP_PASSWORD"  # From secrets
}

DATA_DIR = "/home/clawbot/.openclaw/workspace/data"
RESPONSES_FILE = f"{DATA_DIR}/email_responses.json"
SENT_FILE = f"{DATA_DIR}/sent_emails_2026-03-29.csv"

def decode_str(s):
    """Decode email header string"""
    if not s:
        return ""
    parts = decode_header(s)
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            result.append(part.decode(enc or "utf-8", errors="ignore"))
        else:
            result.append(part)
    return "".join(result)

def get_sent_emails():
    """Lade Liste der gesendeten Emails"""
    sent = {}
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE) as f:
            next(f, None)  # skip header
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    sent[parts[0].lower()] = {
                        "email": parts[0],
                        "company": parts[1] if len(parts) > 1 else "",
                        "date": parts[2] if len(parts) > 2 else ""
                    }
    return sent

def check_inbox_for_responses():
    """Prüfe ob wir Antworten auf unsere Outreach Emails bekommen haben"""
    try:
        mail = imaplib.IMAP4_SSL(CONFIG["imap_server"])
        mail.login(CONFIG["email"], CONFIG["app_password"])
        mail.select("inbox")
        
        # Suche nach Emails die auf unsere gesendet wurden (Antworten)
        # Diese haben normalerweise "Re:" im Subject
        
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        
        sent = get_sent_emails()
        responses = []
        
        # Check letzte 7 Tage
        week_ago = datetime.now() - timedelta(days=7)
        
        for eid in email_ids[-100:]:  # Check letzte 100 Emails
            status, data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            
            # Parse Datum
            date_str = msg.get("Date", "")
            try:
                email_date = email.utils.parsedate_to_datetime(date_str)
                if email_date < week_ago:
                    continue  # Zu alt
            except:
                continue
            
            from_addr = decode_str(msg.get("From", ""))
            subject = decode_str(msg.get("Subject", ""))
            
            # Extrahiere Email Adresse
            if "<" in from_addr:
                addr = from_addr.split("<")[1].split(">")[0].lower()
            else:
                addr = from_addr.lower()
            
            # Check ob von einem unserer Leads
            if addr in sent:
                responses.append({
                    "from": addr,
                    "company": sent[addr].get("company", ""),
                    "subject": subject,
                    "date": date_str
                })
        
        mail.logout()
        return responses
        
    except Exception as e:
        print(f"Error checking inbox: {e}")
        return []

def save_responses(responses):
    """Speichere gefundene Responses"""
    existing = []
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE) as f:
            existing = json.load(f)
    
    # Füge neue Responses hinzu (noch nicht gespeicherte)
    existing_emails = {r.get("from") for r in existing}
    for r in responses:
        if r["from"] not in existing_emails:
            existing.append(r)
            existing_emails.add(r["from"])
    
    with open(RESPONSES_FILE, 'w') as f:
        json.dump(existing[-50:], f, indent=2)  # Keep last 50

def main():
    print("📊 Response Tracker")
    print("=" * 50)
    
    responses = check_inbox_for_responses()
    
    if responses:
        print(f"\n🔔 {len(responses)} neue Antwort(en) gefunden!")
        for r in responses:
            print(f"  - {r['company']}: {r['subject'][:50]}")
        save_responses(responses)
    else:
        print("\n😴 Keine Antworten auf Outreach Emails")
        print("   (Das ist normal - wir haben erst 123 Emails gesendet)")
    
    # Zeige auch alte Responses
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE) as f:
            all_responses = json.load(f)
        if all_responses:
            print(f"\n📋 Alle Responses bisher: {len(all_responses)}")
    
    return 0 if responses else 1

if __name__ == "__main__":
    exit(main())

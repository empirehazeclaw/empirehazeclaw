#!/usr/bin/env python3
"""
📧 Email AI Agent - Generic Version
Automatisiert E-Mail Beantwortung für KMUs
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime

CONFIG_FILE = "config/email_config.json"
LOG_FILE = "data/email_log.json"

# Standard-Antworten
AUTO_RESPONSES = {
    " reservierung": "Vielen Dank für Ihre Reservierungsanfrage. Wir melden uns innerhalb von 2 Stunden bei Ihnen.",
    " termin": "Vielen Dank für Ihre Terminanfrage. Wir melden uns innerhalb von 2 Stunden bei Ihnen.",
    " öffnungszeit": "Unsere Öffnungszeiten finden Sie auf unserer Website. Bei weiteren Fragen helfen wir gerne.",
    "默认": "Vielen Dank für Ihre E-Mail. Wir werden uns schnellstmöglich bei Ihnen melden."
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_server": "imap.gmail.com",
        "email": "empirehazeclaw@gmail.com",
        "app_password": os.environ.get("GMAIL_APP_PASSWORD", "")
    }

def get_auto_response(subject, body):
    """Wähle passende Auto-Antwort"""
    combined = (subject + " " + body).lower()
    for keyword, response in AUTO_RESPONSES.items():
        if keyword in combined:
            return response
    return AUTO_RESPONSES["默认"]

def fetch_unread_emails(config):
    """Hole ungelesene Emails"""
    try:
        mail = imaplib.IMAP4_SSL(config["imap_server"])
        mail.login(config["email"], config["app_password"])
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        results = []
        for eid in email_ids[:10]:  # Max 10 auf einmal
            status, data = mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            
            subject = email.header.decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode("utf-8", errors="ignore")
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            
            results.append({
                "from": msg["From"],
                "to": msg["To"],
                "subject": subject,
                "body": body[:500],
                "date": msg["Date"]
            })
        
        mail.logout()
        return results
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []

def send_email(config, to_email, subject, body):
    """Sende Email"""
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = config["email"]
        msg["To"] = to_email
        
        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["email"], config["app_password"])
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def process_emails():
    """Haupt-Loop"""
    config = load_config()
    
    if not config.get("app_password"):
        print("⚠️ No app password configured")
        return
    
    unread = fetch_unread_emails(config)
    print(f"📬 {len(unread)} ungelesene Emails")
    
    for msg in unread:
        # Auto-Response generieren
        response_text = get_auto_response(msg["subject"], msg["body"])
        
        # Extract sender email
        sender = msg["from"]
        if "<" in sender:
            sender_email = sender.split("<")[1].split(">")[0]
        else:
            sender_email = sender
        
        # Skip if from ourselves
        if sender_email == config["email"]:
            continue
        
        # Send auto-response
        subject = f"Re: {msg['subject']}" if not msg['subject'].startswith("Re:") else msg['subject']
        
        if send_email(config, sender_email, subject, response_text):
            print(f"✅ Auto-geantwortet an: {sender_email}")
            log_email(msg, response_text)

def log_email(original, response):
    """Log Email für Statistik"""
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    
    log.append({
        "timestamp": datetime.now().isoformat(),
        "from": original["from"],
        "subject": original["subject"],
        "response": response[:100]
    })
    
    with open(LOG_FILE, 'w') as f:
        json.dump(log[-100:], f, indent=2)  # Keep last 100

if __name__ == "__main__":
    print("📧 Email Agent gestartet...")
    process_emails()
    print("✅ Email Agent fertig")

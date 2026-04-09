#!/usr/bin/env python3
"""
📧 LLM-Powered Email Agent - Generic Version
Echte KI-Antworten statt Keyword-Matching
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
import json
import os
import sys
from datetime import datetime

# LLM Integration
LLM_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_MODEL = "gpt-4o-mini"  # Schnell + günstig

CONFIG_FILE = "config/email_config.json"
LOG_FILE = "data/email_log.json"
CONTEXT_FILE = "data/business_context.json"
PROMPT_FILE = "config/system_prompt.txt"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"business": {"name": "Unser Unternehmen"}, "email": {}}

def load_context():
    """Lade Business Context für bessere Antworten"""
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE) as f:
            return json.load(f)
    return {
        "business_name": "Unser Unternehmen",
        "industry": "Service",
        "products": [],
        "opening_hours": "Mo-Fr 9-18 Uhr",
        "contact": "info@firma.de, +49 XXX"
    }

def get_business_prompt():
    """Generiere System Prompt für LLM"""
    context = load_context()
    
    prompt = f"""Du bist ein professioneller Email-Assistent für "{context['business_name']}".

ÜBER DAS UNTERNEHMEN:
- Branche: {context['industry']}
- Produkte/Dienstleistungen: {', '.join(context['products']) if context['products'] else 'Unsere Dienstleistungen'}
- Öffnungszeiten: {context['opening_hours']}
- Kontakt: {context['contact']}

REGELN:
1. Antworte NUR auf Deutsch
2. Sei freundlich, professionell und hilfsbereit
3. Wenn du etwas nicht weißt, sage ehrlich dass jemand sich melden wird
4. Halte Antworten kurz und präzise (max 3 Sätze für Standard-Anfragen)
5. Bei Termin-/Reservierungsanfragen: Bitte um telefonischen Kontakt oder nimm die Details auf
6. Bei Beschwerden: Entschuldige dich und eskaliere an menschlichen Support

FORMAT:
- Betreff: Re: [Original Subject]
- Text: Freundliche, präzise Antwort
"""
    
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE) as f:
            prompt += "\n\nZUSÄTZLICHE REGELN:\n" + f.read()
    
    return prompt

def generate_llm_response(user_email, subject, body, system_prompt):
    """Generiere LLM-Antwort"""
    if not LLM_API_KEY:
        return None, "No API key"
    
    try:
        import urllib.request
        import urllib.error
        
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Kunde schrieb:\nFrom: {user_email}\nSubject: {subject}\n\nNachricht:\n{body}"}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"], None
            
    except Exception as e:
        return None, str(e)

def extract_email_address(from_header):
    """Extrahiere Email aus From-Header"""
    if "<" in from_header:
        return from_header.split("<")[1].split(">")[0]
    return from_header

def fetch_unread_emails(config):
    """Hole ungelesene Emails"""
    try:
        mail = imaplib.IMAP4_SSL(config.get("email", {}).get("imap_server", "imap.gmail.com"))
        mail.login(config.get("email", {}).get("address", ""), 
                   config.get("email", {}).get("app_password", ""))
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        results = []
        for eid in email_ids[:10]:
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
                "message_id": msg["Message-ID"],
                "from": msg["From"],
                "from_email": extract_email_address(msg["From"]),
                "subject": subject,
                "body": body[:2000],  # Limit für LLM
                "date": msg["Date"]
            })
        
        mail.logout()
        return results
    except Exception as e:
        print(f"❌ Error fetching: {e}")
        return []

def send_email(config, to_email, subject, body):
    """Sende Email"""
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = config.get("email", {}).get("address", "")
        msg["To"] = to_email
        msg["In-Reply-To"] = ""
        msg["References"] = ""
        
        smtp_server = config.get("email", {}).get("smtp_server", "smtp.gmail.com")
        smtp_port = config.get("email", {}).get("smtp_port", 587)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(
                config.get("email", {}).get("address", ""),
                config.get("email", {}).get("app_password", "")
            )
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"❌ Error sending: {e}")
        return False

def log_interaction(original, response, success):
    """Log für Analytics"""
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    
    log.append({
        "timestamp": datetime.now().isoformat(),
        "from": original["from_email"],
        "subject": original["subject"],
        "response_preview": response[:100] if response else "FAILED",
        "success": success,
        "llm_used": True
    })
    
    with open(LOG_FILE, 'w') as f:
        json.dump(log[-500:], f, indent=2)  # Keep last 500

def process_emails():
    """Haupt-Loop"""
    config = load_config()
    
    if not config.get("email", {}).get("app_password"):
        print("⚠️ No email configured")
        return
    
    if not LLM_API_KEY:
        print("⚠️ No OpenAI API key - using fallback")
    
    system_prompt = get_business_prompt()
    unread = fetch_unread_emails(config)
    
    print(f"📬 {len(unread)} ungelesene Emails")
    
    for msg in unread:
        # Skip if from ourselves
        our_email = config.get("email", {}).get("address", "")
        if msg["from_email"] == our_email:
            continue
        
        # Generate LLM response
        response_text, error = generate_llm_response(
            msg["from_email"],
            msg["subject"],
            msg["body"],
            system_prompt
        )
        
        if error:
            print(f"❌ LLM Error: {error}")
            # Fallback response
            response_text = f"""Sehr geehrte/r Kunde,

vielen Dank für Ihre Nachricht.

Wir haben Ihre Anfrage erhalten und melden uns innerhalb von 24 Stunden bei Ihnen.

Mit freundlichen Grüßen
{config['business']['name']}"""
        
        # Send response
        reply_subject = f"Re: {msg['subject']}" if not msg['subject'].startswith("Re:") else msg['subject']
        
        if send_email(config, msg["from_email"], reply_subject, response_text):
            print(f"✅ Geantwortet an: {msg['from_email'][:30]}...")
            log_interaction(msg, response_text, True)
        else:
            log_interaction(msg, response_text, False)
        
        # Small delay to avoid rate limits
        import time
        time.sleep(1)

if __name__ == "__main__":
    print("📧 LLM Email Agent gestartet...")
    print(f"🤖 Model: {LLM_MODEL}")
    print(f"🔑 API Key: {'✅' if LLM_API_KEY else '❌'}")
    process_emails()
    print("✅ Fertig!")

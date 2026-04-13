#!/usr/bin/env python3
"""
Automated Outreach via Gmail SMTP
Sends emails using Google App Password
"""
import smtplib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
SENT_FILE = DATA_DIR / "sent_emails.json"
SEQUENCES_FILE = DATA_DIR / "email_sequences.json"
STATUS_FILE = DATA_DIR / "lead_status.json"

# Gmail SMTP Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "empirehazeclaw@gmail.com"
APP_PASSWORD = "GOOGLE_APP_PASSWORD_PLACEHOLDER"  # Google App Password

def load_json(path, default):
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return default

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def send_email(to_email, subject, body):
    """Send email via Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        return True, "Sent"
    except Exception as e:
        return False, str(e)

def get_email_content(email, step, name, company):
    """Get email template"""
    templates = {
        1: {
            "subject": "Wie {company} von KI-Assistenz profitiert",
            "body": """Sehr geehrte/r {name},

ich bin auf {company} aufmerksam geworden und wollte mich kurz vorstellen.

Ich helfe lokalen Unternehmen wie Ihrem, Routineaufgaben zu automatisieren:

✅ Terminbuchungen ohne Telefon
✅ E-Mail-Support ohne Personal
✅ Erinnerungen & Follow-ups automatisch

Wäre das interessant für Sie?

Gerne zeige ich Ihnen in einem 15-minütigen Call, wie das konkret funktioniert.

Beste Grüße,
Nico von EmpireHazeClaw"""
        },
        2: {
            "subject": "Re: Wie {company} von KI-Assistenz profitiert",
            "body": """Hallo {name},

ich wollte kurz nachhaken wegen meiner letzten Nachricht.

Könnten Sie sich 15 Minuten Zeit nehmen für einen kurzen Austausch?

Falls gerade nicht passt, gerne auch nächste Woche.

Beste Grüße,
Nico"""
        },
        3: {
            "subject": "Kurze Frage zu KI für {company}",
            "body": """Hi {name},

ich mache es kurz:

Wir haben gerade einem Restaurant in Ihrer Region geholfen, 20 Stunden/Monat bei der Terminbuchung zu sparen.

Ähnliches wäre auch für {company} möglich.

Interesse an einem kurzen Video-Call diese Woche?

Beste Grüße,
Nico"""
        },
        4: {
            "subject": "Letzter Versuch: 2 Fragen",
            "body": """{name},

wenn Sie aktuell keine Zeit oder kein Interesse haben, kein Problem - ich melde mich dann nicht mehr.

Falls sich das aber ändert:
- Website: empirehazeclaw.de
- Email: empirehazeclaw@gmail.com

Beste Grüße,
Nico"""
        }
    }
    
    template = templates.get(step, templates[1])
    subject = template["subject"].format(name=name, company=company)
    body = template["body"].format(name=name, company=company)
    return subject, body

def get_pending_leads():
    """Get leads ready to email"""
    sequences = load_json(SEQUENCES_FILE, {})
    pending = []
    now = datetime.now()
    
    for email, seq in sequences.items():
        if seq.get('status') != 'active':
            continue
        next_send = datetime.fromisoformat(seq['next_send'])
        if next_send <= now:
            pending.append((email, seq))
    
    return pending

def mark_sent(email, step):
    """Mark email as sent"""
    sent = load_json(SENT_FILE, {})
    sent[email] = {
        "step": step,
        "sent_at": datetime.now().isoformat(),
        "status": "sent"
    }
    save_json(SENT_FILE, sent)

def advance_sequence(email):
    """Move to next step"""
    sequences = load_json(SEQUENCES_FILE, {})
    if email not in sequences:
        return None
    
    seq = sequences[email]
    current_step = seq.get('step', 1)
    
    if current_step >= 4:
        sequences[email]['status'] = 'completed'
    else:
        next_step = current_step + 1
        delays = [0, 3, 7, 14]
        delay = delays[next_step - 1] if next_step <= 4 else 0
        sequences[email]['step'] = next_step
        sequences[email]['next_send'] = (datetime.now() + timedelta(days=delay)).isoformat()
        if next_step >= 4:
            sequences[email]['status'] = 'completed'
    
    save_json(SEQUENCES_FILE, sequences)
    return sequences[email].get('step')

def process_outreach():
    """Main outreach processing"""
    pending = get_pending_leads()
    
    if not pending:
        print(f"[{datetime.now()}] No pending emails")
        return
    
    print(f"[{datetime.now()}] Processing {len(pending)} emails...")
    
    for email, seq in pending:
        step = seq.get('step', 1)
        name = seq.get('name', ' ')
        company = seq.get('company', 'Unternehmen')
        
        subject, body = get_email_content(email, step, name, company)
        
        print(f"  Sending [{step}/4] to {email}...", end=" ")
        success, result = send_email(email, subject, body)
        
        if success:
            mark_sent(email, step)
            new_step = advance_sequence(email)
            print(f"✅ (→ step {new_step})")
        else:
            print(f"❌ {result[:50]}")
        
        time.sleep(1)  # Rate limiting

if __name__ == "__main__":
    import sys
    
    if "--dry-run" in sys.argv:
        pending = get_pending_leads()
        print(f"📬 {len(pending)} emails ready:")
        for email, seq in pending:
            print(f"  [{seq['step']}/4] {email}")
    else:
        process_outreach()

#!/usr/bin/env python3
"""
📅 Demo Scheduler - Skill
Wenn ein Lead auf unsere Outreach Email antwortet, automatisch einen Demo-Call vorschlagen

Nutzung: python3 scripts/demo_scheduler.py --email "lead@example.com" --name "Max Mustermann"
"""
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import json
import os

CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "empirehazeclaw@gmail.com",
    "app_password": "export GMAIL_APP_PASSWORD"
}

DATA_DIR = "/home/clawbot/.openclaw/workspace/data"
DEMOS_FILE = f"{DATA_DIR}/demo_requests.json"

# Demo-Slots (Montag bis Freitag, 9-17 Uhr)
DEMO_SLOTS = []
for day_offset in range(1, 8):  # Nächste 7 Tage
    date = datetime.now() + timedelta(days=day_offset)
    if date.weekday() < 5:  # Mo-Fr
        for hour in [9, 10, 11, 14, 15, 16]:
            DEMO_SLOTS.append({
                "date": date.strftime("%Y-%m-%d"),
                "time": f"{hour}:00",
                "available": True
            })

def load_demos():
    if os.path.exists(DEMOS_FILE):
        with open(DEMOS_FILE) as f:
            return json.load(f)
    return []

def save_demos(demos):
    with open(DEMOS_FILE, 'w') as f:
        json.dump(demos, f, indent=2)

def create_demo_request(lead_email, lead_name, company):
    """Erstelle Demo-Anfrage"""
    demos = load_demos()
    
    # Freien Slot finden
    slot = None
    for s in DEMO_SLOTS:
        if s["available"]:
            slot = s
            s["available"] = False
            break
    
    demo = {
        "id": len(demos) + 1,
        "lead_email": lead_email,
        "lead_name": lead_name,
        "company": company,
        "slot": slot,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    demos.append(demo)
    save_demos(demos)
    
    return demo, slot

def send_confirmation(lead_email, lead_name, company, slot):
    """Sende Bestätigung mit Demo-Vorschlag"""
    slot_str = f"{slot['date']} um {slot['time']} Uhr"
    
    body = f"""Hallo {lead_name},

vielen Dank für Ihre Rückmeldung!

Gerne möchte ich Ihnen in einem 15-minütigen Call zeigen, wie ein KI-Mitarbeiter konkret für {company} arbeiten würde.

Mein Vorschlag: {slot_str}

Passt das bei Ihnen? Wenn nicht, nennen Sie mir gerne einen anderen Termin.

Alternativ können Sie hier direkt einen Slot buchen:
https://empirehazeclaw.de/demo

Mit freundlichen Grüßen
Nico

EmpireHazeClaw
KI-Mitarbeiter für Unternehmen"""

    msg = MIMEText(body)
    msg["Subject"] = f"Re: Demo-Call: KI-Mitarbeiter für {company}"
    msg["From"] = CONFIG["email"]
    msg["To"] = lead_email
    
    try:
        with smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(CONFIG["email"], CONFIG["app_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending: {e}")
        return False

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python3 demo_scheduler.py --email <email> --name <name> --company <company>")
        return 1
    
    args = dict(arg.split("=") for arg in sys.argv[1:] if "=" in arg)
    
    lead_email = args.get("--email", "")
    lead_name = args.get("--name", "Kunde")
    company = args.get("--company", "Ihr Unternehmen")
    
    if not lead_email:
        print("Error: --email is required")
        return 1
    
    print("📅 Demo Scheduler")
    print("=" * 50)
    print(f"Lead: {lead_name} <{lead_email}>")
    print(f"Unternehmen: {company}")
    
    demo, slot = create_demo_request(lead_email, lead_name, company)
    
    if slot:
        print(f"\n✅ Demo-Anfrage erstellt: {slot['date']} um {slot['time']}")
        if send_confirmation(lead_email, lead_name, company, slot):
            print(f"📧 Bestätigung gesendet an {lead_email}")
        else:
            print(f"⚠️ Bestätigung konnte nicht gesendet werden")
    else:
        print("\n⚠️ Keine freien Slots verfügbar - bitte manuell Termin anbieten")
    
    return 0

if __name__ == "__main__":
    import sys
    exit(main())

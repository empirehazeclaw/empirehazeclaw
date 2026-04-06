#!/usr/bin/env python3
"""
📧 Improved Outreach Generator - Skill
Erstellt personalisierte Outreach Emails basierend auf Lead-Daten

Nutzung: python3 scripts/improved_outreach.py --lead "Restaurant Beispiel" --industry gastro --email test@firma.de
"""
import smtplib
from email.mime.text import MIMEText
import csv
import os
import sys
import json
from datetime import datetime

CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "empirehazeclaw@gmail.com",
    "app_password": "export GMAIL_APP_PASSWORD"
}

DATA_DIR = "/home/clawbot/.openclaw/workspace/data"
TEMPLATES_FILE = f"{DATA_DIR}/email_templates.json"

# Personalisierte Templates nach Branche
TEMPLATES = {
    "gastro": {
        "subject": "15-minütiger Call: KI für Ihr Restaurant?",
        "pain": "Reservierungsanfragen, E-Mails und Kundenfragen kosten viel Zeit.",
        "solution": "Ein KI-Mitarbeiter beantwortet alles 24/7 - sofort und zuverlässig.",
        "cta": "Haben Sie 15 Minuten für einen kurzen Call diese Woche?"
    },
    "zahnarzt": {
        "subject": "15-minütiger Call: KI für Ihre Zahnarztpraxis?",
        "pain": "Terminkoordination und Patientenanfragen binden unnötig Zeit.",
        "solution": "KI-Terminbuchung und automatisierte Erinnerungen reduzieren No-Shows.",
        "cta": "Kurz mal quatschen? Ich zeige Ihnen wie das funktioniert."
    },
    "werkstatt": {
        "subject": "15-minütiger Call: KI für Ihre Werkstatt?",
        "pain": "Angebote, Terminvereinbarungen und Kundenkommunikation kosten Zeit.",
        "solution": "KI-gestützte Anfragebearbeitung und automatische Offerten.",
        "cta": "Darf ich Ihnen das mal kurz zeigen?"
    },
    "physio": {
        "subject": "15-minütiger Call: KI für Ihre Praxis?",
        "pain": "Terminmanagement und Erstkontakte kosten viel Verwaltungszeit.",
        "solution": "Automatisierte Terminbuchung und Vorab-Informationen per KI.",
        "cta": "Haben Sie 15 Minuten diese Woche?"
    },
    "default": {
        "subject": "15-minütiger Call: KI für Ihr Unternehmen?",
        "pain": "Wiederkehrende Anfragen kosten Zeit die Sie fürs Wesentliche brauchen.",
        "solution": "KI übernimmt Routinekommunikation - Sie haben mehr Zeit.",
        "cta": "Kurz mal reden?"
    }
}

def get_industry_key(industry):
    """Erkenne Industry Key"""
    industry = industry.lower()
    if any(w in industry for w in ['restaurant', 'gastro', 'cafe', 'hotel', 'bar', 'bistro']):
        return 'gastro'
    if any(w in industry for w in ['zahn', 'arzt', 'praxis', 'medizin']):
        return 'zahnarzt'
    if any(w in industry for w in ['werkstatt', 'kfz', 'auto', 'mechanic']):
        return 'werkstatt'
    if any(w in industry for w in ['physio', 'therap', 'reha', 'heil']):
        return 'physio'
    return 'default'

def personalize_email(company, industry):
    """Erstelle personalisierte Email"""
    key = get_industry_key(industry)
    t = TEMPLATES[key]
    
    body = f"""Sehr geehrte/r {company},

vielen Dank für Ihre Zeit.

Ich schreibe Ihnen, weil {t['pain']}

Wir haben eine Lösung: Ein KI-Mitarbeiter, der {t['solution']}

Das beste: In nur 2 Wochen könnte das für Sie live sein.

{t['cta']}

Viele Grüße
Nico

P.S. Falls jetzt gerade nicht passt - kein Problem. Einfach kurz antworten."""

    return {
        "subject": t["subject"],
        "body": body,
        "industry_key": key
    }

def send_email(to_email, subject, body):
    """Sende Email"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = CONFIG["email"]
    msg["To"] = to_email
    
    try:
        with smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(CONFIG["email"], CONFIG["app_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        # Test
        result = personalize_email("Café am Platz", "Restaurant")
        print("📧 Test Email:")
        print(f"Subject: {result['subject']}")
        print(f"Body:\n{result['body']}")
        print(f"Industry: {result['industry_key']}")
        return 0
    
    # Parse args
    args = dict(arg.split("=", 1) for arg in sys.argv[1:] if "=" in arg)
    
    company = args.get("--company", "Kunde")
    email_addr = args.get("--email", "")
    industry = args.get("--industry", "")
    
    if not email_addr:
        print("Error: --email is required")
        return 1
    
    result = personalize_email(company, industry)
    
    print("📧 Personalisierte Email:")
    print(f"An: {email_addr}")
    print(f"Subject: {result['subject']}")
    print(f"Industry: {result['industry_key']}")
    print(f"\n{result['body']}")
    
    if "--send" in args:
        if send_email(email_addr, result['subject'], result['body']):
            print(f"\n✅ Gesendet an {email_addr}")
        else:
            print(f"\n❌ Senden fehlgeschlagen")
    
    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Quick Outreach - Sendet personalisierte E-Mails an Leads.
Usage: python3 quick_outreach.py --limit 10
"""
import csv
import sys
import time
import subprocess
import os
import random

GOG_PATH = "/home/clawbot/.local/bin/gog"
LEADS_FILE = "/home/clawbot/.openclaw/workspace/data/crm_leads.csv"
SENT_FILE = "/home/clawbot/.openclaw/workspace/data/sent_quick.json"
LOG_FILE = "/home/clawbot/.openclaw/workspace/data/outreach_log.txt"

# Templates für Gastro
TEMPLATES = {
    "gastro": """Sehr geehrte/r {name},

ich bin Mitarbeiter von EmpireHazeClaw und schreibe Ihnen, weil wir Restaurants wie Ihres unterstützen.

Unsere KI-Mitarbeiter übernehmen:
- 📧 E-Mail-Support (sofortige Antworten, 24/7)
- 📅 Terminbuchungen (automatisch)
- 📱 Kundenanfragen (ohne Wartezeit)

Kostenersparnis: Bis zu 10 Stunden/Monat.

Können wir in einem 15-minütigen Call besprechen, ob das für Sie interessant ist?

Viele Grüße
EmpireHazeClaw Team""",

    "default": """Sehr geehrte/r {name},

ich schreibe Ihnen von EmpireHazeClaw. Wir helfen Unternehmen mit KI-Mitarbeitern, die 24/7 arbeiten.

Haben Sie Interesse an einem unverbindlichen 15-Minuten-Call?

Viele Grüße
EmpireHazeClaw Team"""
}

def load_sent():
    """Lade bereits gesendete IDs"""
    if os.path.exists(SENT_FILE):
        import json
        with open(SENT_FILE) as f:
            return set(json.load(f))
    return set()

def save_sent(sent_ids):
    """Speichere gesendete IDs"""
    import json
    with open(SENT_FILE, 'w') as f:
        json.dump(list(sent_ids), f)

def get_industry(email):
    """Rate industry basierend auf Email/Domain"""
    gastro_keywords = ['restaurant', 'cafe', 'hotel', 'gastro', 'bar', 'bistro', 'pizza', 'imbiss']
    email_lower = email.lower()
    for kw in gastro_keywords:
        if kw in email_lower:
            return 'gastro'
    return 'default'

def humanize_name(company):
    """Extrahiere einen Vornamen aus Firmenname"""
    parts = company.split()
    if len(parts) > 0:
        return parts[0]
    return "Inhaber"

def send_email(to_email, subject, body):
    """Sende E-Mail via GOG CLI"""
    try:
        result = subprocess.run(
            [GOG_PATH, 'send', '--to', to_email, '--subject', subject, '--body', body],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def main():
    limit = 20
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        limit = int(sys.argv[idx+1])
    
    sent_ids = load_sent()
    sent_count = 0
    error_count = 0
    
    with open(LEADS_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('email', '').strip()
            if not email or email in sent_ids or '?' in email:
                continue
            
            # Industry-Template wählen
            industry = row.get('industry', '').lower()
            template_key = 'gastro' if 'gastro' in industry else 'default'
            template = TEMPLATES[template_key]
            
            # Personalisieren
            name = humanize_name(row.get('company', ''))
            body = template.format(name=name)
            subject = "15-minütiger Call: KI für Ihr Unternehmen?"
            
            # Zufällige Pause (1-3 Sekunden)
            time.sleep(random.uniform(1, 3))
            
            # Senden
            success, msg = send_email(email, subject, body)
            
            if success:
                sent_ids.add(email)
                sent_count += 1
                print(f"✅ {email} - {row.get('company', '')[:30]}")
            else:
                error_count += 1
                print(f"❌ {email} - {msg[:50]}")
            
            if sent_count >= limit:
                break
    
    save_sent(sent_ids)
    print(f"\n📊 Erfolg: {sent_count}, Fehler: {error_count}")
    
    # Log
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] Outreach: {sent_count} gesendet, {error_count} Fehler\n")

if __name__ == "__main__":
    main()

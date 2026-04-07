#!/usr/bin/env python3
"""
📧 Email Sequence for EMPIREHAZECLAW Outreach

3-Step Campaign for Managed AI Hosting
Target: German SMEs (Handwerk, Gastronomie, Service)

Step 1: Initial Outreach (Day 0)
Step 2: Follow-up (Day 3)
Step 3: Final Breakup (Day 7)

Usage:
    python3 email_sequence.py --lead "company@email.com" --step 1
    python3 email_sequence.py --campaign --count 10
"""

import os
import sys
import csv
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.file_lock import locked_write, locked_read

# Config
LEADS_FILE = Path("/home/clawbot/.openclaw/workspace/data/crm_leads.csv")
BOUNCED_FILE = Path("/home/clawbot/.openclaw/workspace/data/bounced_leads.json")
SENT_FILE = Path("/home/clawbot/.openclaw/workspace/data/sent_emails.json")
SEQUENCE_LOG = Path("/home/clawbot/.openclaw/workspace/data/sequence_log.json")

# Use Gmail API directly
from lib.gmail_api import send_email as gmail_send

FROM_EMAIL = "empirehazeclaw@gmail.com"

# === EMAIL TEMPLATES ===

SUBJECT_STEP1 = "Mal was anderes: KI-Mitarbeiter für Ihr Unternehmen"
SUBJECT_STEP2 = "Frage zu meinem letzten Schreiben"
SUBJECT_STEP3 = "Letzte Chance: Kostenlose KI-Analyse"

BODY_STEP1 = """Guten Tag {name},

kurz eine Frage: Haben Sie schonmal darüber nachgedacht, eigene KI-Mitarbeiter für Ihr Unternehmen einzusetzen?

Ich bin dabei, deutschen Kleinunternehmern zu helfen, ihre eigene KI-Infrastruktur aufzusetzen - ohne sich um Server, Updates oder US-Cloud kümmern zu müssen.

Warum das interessant sein könnte:
- 🇩🇪 Ihre Daten bleiben in Deutschland (DSGVO-konform)
- 🤖 KI-Mitarbeiter statt teurer Agenturen
- 💰 Fixe Kosten, keine Überraschungen

Ich biete aktuell eine kostenlose Erstberatung an (15 Min, unverbindlich).

Haben Sie 15 Minuten in der nächsten Woche?

Viele Grüße
Nico

P.S.: Falls das gerade nicht passt - kein Problem, einfach ignore."""

BODY_STEP2 = """Guten Tag {name},

ich wollte kurz nachhaken, ob meine letzte Email angekommen ist.

Ich biete deutschen Unternehmen aktuell eine kostenlose KI-Analyse an - ich schaue mir an, wo Sie von Automatisierung profitieren könnten.

Kein Verkauf, keine Verpflichtung - einfach ein ehrlicher Blick.

Lohnt sich für Sie zu prüfen?

Viele Grüße
Nico"""

BODY_STEP3 = """Guten Tag {name},

ich melde mich noch einmal - danach hören Sie von mir.

Falls Sie bereits jemanden für KI-Themen haben, ignorieren Sie diese Email einfach.

Falls nicht: Ich biete eine kostenlose Erstberatung an.

Kurzer Link zur Terminbuchung: [CALENDLY_LINK]

Viele Grüße
Nico

P.S.: Dies ist meine letzte Nachricht - versprochen."""

def load_leads():
    """Load leads from CSV"""
    if not LEADS_FILE.exists():
        return []
    
    with open(LEADS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_bounced():
    """Load bounced emails"""
    return locked_read(str(BOUNCED_FILE), [])

def load_sent():
    """Load sent email log"""
    return locked_read(str(SENT_FILE), {})

def save_sent(sent_log):
    """Save sent email log"""
    locked_write(str(SENT_FILE), sent_log)

def is_bounced(email):
    """Check if email bounced"""
    bounced = load_bounced()
    return any(b.get("email") == email for b in bounced)

def get_sequence_state(email):
    """Get which step of sequence email is at"""
    sent = load_sent()
    if email not in sent:
        return 0  # Not contacted
    return sent[email].get("step", 0)

def mark_sent(email, step):
    """Mark email as sent at step"""
    sent = load_sent()
    sent[email] = {
        "step": step,
        "sent_at": datetime.now().isoformat(),
        "name": "Unknown"
    }
    save_sent(sent)

def send_email(to_email, subject, body, name=""):
    """Send email via Gmail API"""
    if is_bounced(to_email):
        return False, "Bounced"
    
    # Handle missing name gracefully
    if not name or name == " ":
        name_part = ""
    else:
        name_part = name
    
    try:
        success, msg = gmail_send(
            to_email,
            subject,
            body.format(name=name_part),
            from_email=FROM_EMAIL
        )
        return success, msg
    except Exception as e:
        return False, str(e)[:100]

def run_sequence_for_lead(lead, step):
    """Run specific step for a lead"""
    email = lead.get("email", "")
    name = lead.get("contact_name", "") or lead.get("name", "") or " "
    company = lead.get("company", "")
    
    if step == 1:
        subject = SUBJECT_STEP1
        body = BODY_STEP1
    elif step == 2:
        subject = SUBJECT_STEP2
        body = BODY_STEP2
    elif step == 3:
        subject = SUBJECT_STEP3
        body = BODY_STEP3
    else:
        return False, "Invalid step"
    
    success, msg = send_email(email, subject, body, name)
    
    if success:
        mark_sent(email, step)
    
    return success, msg

def run_campaign(count=10, start_step=1):
    """Run campaign for first N leads"""
    leads = load_leads()
    bounced = load_bounced()
    
    # Filter out bounced
    active_leads = [l for l in leads if l.get("status") == "new"]
    
    sent = load_sent()
    # Get leads not yet at this step
    campaign_leads = [
        l for l in active_leads 
        if get_sequence_state(l.get("email", "")) < start_step
    ][:count]
    
    results = []
    for lead in campaign_leads:
        success, msg = run_sequence_for_lead(lead, start_step)
        results.append({
            "email": lead.get("email"),
            "company": lead.get("company"),
            "success": success,
            "msg": msg
        })
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Email Sequence for Outreach")
    parser.add_argument("--lead", help="Single lead email")
    parser.add_argument("--step", type=int, default=1, help="Sequence step (1, 2, or 3)")
    parser.add_argument("--campaign", action="store_true", help="Run for all new leads")
    parser.add_argument("--count", type=int, default=10, help="Number of leads for campaign")
    parser.add_argument("--status", action="store_true", help="Show campaign status")
    
    args = parser.parse_args()
    
    if args.status:
        leads = load_leads()
        sent = load_sent()
        bounced = load_bounced()
        
        print("\n📊 CAMPAIGN STATUS")
        print("="*50)
        print(f"Total leads: {len(leads)}")
        print(f"Bounced: {len(bounced)}")
        print(f"Contacted: {len(sent)}")
        print(f"New (not contacted): {len([l for l in leads if l.get('email') not in sent])}")
        print()
        
        for step in [1, 2, 3]:
            step_sent = sum(1 for s in sent.values() if s.get("step") == step)
            print(f"Step {step}: {step_sent} sent")
        return
    
    if args.lead:
        success, msg = send_email(args.lead, "Test", f"Test email to {args.lead}")
        print(f"{'✅' if success else '❌'} {msg}")
        return
    
    if args.campaign:
        results = run_campaign(count=args.count, start_step=args.step)
        print(f"\n📤 CAMPAIGN STEP {args.step}")
        print("="*50)
        for r in results:
            icon = "✅" if r["success"] else "❌"
            print(f"{icon} {r['email']} - {r['msg']}")
        return
    
    print("Usage:")
    print("  email_sequence.py --status              # Show status")
    print("  email_sequence.py --campaign --step 1    # Run step 1 for 10 leads")
    print("  email_sequence.py --lead test@e.com     # Send test email")

if __name__ == "__main__":
    main()

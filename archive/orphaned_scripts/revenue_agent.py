#!/usr/bin/env python3
"""
🤖 Revenue Agent - Optimiert mit Auto-Follow-up
Automatisches Follow-up nach 3 Tagen ohne Antwort
"""

import sys
import csv
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from lib.file_lock import locked_read, locked_write
from lib.gmail_api import send_email, test_connection

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CRM_FILE = WORKSPACE / "data/crm_leads.csv"
SENT_FILE = WORKSPACE / "data/sent_emails.json"
BOUNCED_FILE = WORKSPACE / "data/bounced_leads.json"
QUEUE_FILE = WORKSPACE / "data/followup_queue.json"
LOG_FILE = WORKSPACE / "logs/outreach.log"

# Email Templates
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

def get_followup_emails():
    """
    Findet alle Emails die Follow-up brauchen.
    Regeln:
    - Step 1 gesendet + 3 Tage keine Antwort → Step 2
    - Step 2 gesendet + 3 Tage keine Antwort → Step 3
    - Step 3 = Ende der Sequenz
    """
    sent = locked_read(str(SENT_FILE), {})
    now = datetime.now()
    followups = []
    
    for email, data in sent.items():
        step = data.get("step", 0)
        sent_at = data.get("sent_at", "")
        
        if not sent_at or step >= 3:
            continue
        
        try:
            sent_date = datetime.fromisoformat(sent_at.replace("Z", "+00:00"))
            days_since = (now - sent_date.replace(tzinfo=None)).days
            
            if days_since >= 3:
                # Check if we got a response (manual check via Stripe or reply)
                # For now: assume no response
                followups.append({
                    "email": email,
                    "company": data.get("company", ""),
                    "name": data.get("name", ""),
                    "current_step": step,
                    "days": days_since,
                    "next_step": step + 1
                })
        except Exception as e:
            continue
    
    return followups

def check_for_responses():
    """
    Prüft ob es Antworten auf gesendete Emails gab.
    Für jetzt: Nur Stripe Events (checkout.session.completed)
    """
    # Check Stripe for new customers
    customers_file = WORKSPACE / "data/customers.json"
    if customers_file.exists():
        customers = locked_read(str(customers_file), [])
        # If customer exists in Stripe, they responded
        return {c.get("email") for c in customers}
    
    return set()

def send_followup(followup):
    """Sendet Follow-up Email"""
    email = followup["email"]
    name = followup["name"] or ""
    next_step = followup["next_step"]
    company = followup["company"]
    
    if next_step == 2:
        subject = SUBJECT_STEP2
        body = BODY_STEP2.format(name=name)
    elif next_step == 3:
        subject = SUBJECT_STEP3
        body = BODY_STEP3.format(name=name)
    else:
        return False, "Invalid step"
    
    success, msg = send_email(email, subject, body)
    
    return success, msg

def run_auto_followup():
    """
    Haupt-Funktion: Automatisches Follow-up.
    Sollte täglich (z.B. via cron um 10:00) laufen.
    """
    print(f"[{datetime.now().isoformat()}] 🔄 Auto-Follow-up Starting...")
    
    # Get responses (Stripe customers = answered)
    responses = check_for_responses()
    print(f"   📥 Known responses: {len(responses)}")
    
    # Get emails needing follow-up
    followups = get_followup_emails()
    print(f"   📬 Follow-ups needed: {len(followups)}")
    
    if not followups:
        print("   ✅ No follow-ups due")
        return
    
    # Filter out responses
    pending = [f for f in followups if f["email"] not in responses]
    print(f"   ⏳ Pending (no response): {len(pending)}")
    
    sent = locked_read(str(SENT_FILE), {})
    
    for followup in pending:
        email = followup["email"]
        next_step = followup["next_step"]
        company = followup["company"]
        
        success, msg = send_followup(followup)
        
        if success:
            # Update sent log
            sent[email] = {
                "step": next_step,
                "sent_at": datetime.now().isoformat(),
                "company": company,
                "name": followup.get("name", ""),
                "auto_followup": True
            }
            print(f"   ✅ Step {next_step} → {company} ({email})")
        else:
            print(f"   ❌ {company}: {msg}")
    
    # Save updated log
    locked_write(str(SENT_FILE), sent)
    
    # Log
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] AUTO-FOLLOWUP: {len(pending)} emails\n")
    
    print(f"   🎯 Auto-Follow-up complete")

def send_campaign(count=10):
    """
    Sendet Kampagne an neue Leads (Step 1).
    """
    sent = locked_read(str(SENT_FILE), {})
    
    if not CRM_FILE.exists():
        print("❌ CRM file not found")
        return
    
    with open(CRM_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        targets = [l for l in reader if l.get("email") not in sent]
    
    if not targets:
        print("✅ All leads already contacted")
        return
    
    targets = targets[:count]
    
    print(f"📤 Sending Step 1 to {len(targets)} leads...")
    
    sent_log = locked_read(str(SENT_FILE), {})
    success_count = 0
    
    for lead in targets:
        email = lead.get("email", "")
        company = lead.get("company", "")
        name = lead.get("contact_name", "") or ""
        
        body = BODY_STEP1.format(name=name)
        
        ok, msg = send_email(email, SUBJECT_STEP1, body)
        
        if ok:
            sent_log[email] = {
                "step": 1,
                "sent_at": datetime.now().isoformat(),
                "company": company,
                "name": name,
                "auto_followup": False
            }
            success_count += 1
            print(f"   ✅ {company}")
        else:
            print(f"   ❌ {company}: {msg}")
    
    locked_write(str(SENT_FILE), sent_log)
    print(f"   🎯 {success_count}/{len(targets)} sent")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Revenue Agent")
    parser.add_argument("--followup", action="store_true", help="Run auto-followup")
    parser.add_argument("--campaign", action="store_true", help="Send campaign")
    parser.add_argument("--count", type=int, default=10, help="Number of leads for campaign")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    if args.status:
        followups = get_followup_emails()
        sent = locked_read(str(SENT_FILE), {})
        print(f"""
╔═══════════════════════════════════════╗
║     REVENUE AGENT STATUS             ║
╚═══════════════════════════════════════╝
Campaign Emails Sent:  {len(sent)}
Follow-ups Due:         {len(followups)}
""")
        for f in followups:
            print(f"  ⚠️  {f['company'][:30]:<30} Step {f['current_step']} → {f['next_step']} ({f['days']} Tage)")
    
    elif args.followup:
        run_auto_followup()
    
    elif args.campaign:
        send_campaign(count=args.count)
    
    else:
        print("Usage:")
        print("  revenue_agent.py --status       # Show status")
        print("  revenue_agent.py --followup     # Run auto-followup")
        print("  revenue_agent.py --campaign     # Send campaign")

if __name__ == "__main__":
    main()

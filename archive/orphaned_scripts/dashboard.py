#!/usr/bin/env python3
"""
📊 EmpireHazeClaw Dashboard
Sendet alle 6 Stunden einen Status-Report.

Usage:
    python3 dashboard.py              # Sofort-Report
    python3 dashboard.py --send     # Report per Email
    python3 dashboard.py --cron     # Für Crontab (automated)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from email.header import decode_header

# Add lib
sys.path.insert(0, str(Path(__file__).parent))
from lib.file_lock import locked_read, locked_write
from lib.gmail_api import send_email, test_connection

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
REVENUE_FILE = WORKSPACE / "REVENUE.md"
SYSTEM_FILE = WORKSPACE / "SYSTEM_CORE.md"
CRM_FILE = WORKSPACE / "data/crm_leads.csv"
SENT_FILE = WORKSPACE / "data/sent_emails.json"
WATCHDOG_LOG = WORKSPACE / "logs/watchdog.log"
OUTREACH_LOG = WORKSPACE / "logs/outreach.log"
HEALTH_FILE = WORKSPACE / "data/autonomous_state.json"

def get_crm_stats():
    """Lead-Statistiken aus CRM"""
    import csv
    
    stats = {
        "total": 0,
        "contacted": 0,
        "new": 0,
        "converted": 0
    }
    
    if not CRM_FILE.exists():
        return stats
    
    try:
        with open(CRM_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            leads = list(reader)
            stats["total"] = len(leads)
            stats["contacted"] = sum(1 for l in leads if l.get("status") != "new")
            stats["new"] = sum(1 for l in leads if l.get("status") == "new")
    except:
        pass
    
    return stats

def get_sent_stats():
    """Email-Statistiken"""
    sent = locked_read(str(SENT_FILE), {})
    
    stats = {
        "total_sent": len(sent),
        "step1": 0,
        "step2": 0,
        "step3": 0
    }
    
    for email, data in sent.items():
        step = data.get("step", 0)
        if step == 1:
            stats["step1"] += 1
        elif step == 2:
            stats["step2"] += 1
        elif step == 3:
            stats["step3"] += 1
    
    return stats

def get_watchdog_status():
    """Watchdog-Status"""
    status = {
        "last_check": "Unknown",
        "issues": 0,
        "healthy": True
    }
    
    # Read watchdog log
    if WATCHDOG_LOG.exists():
        try:
            with open(WATCHDOG_LOG, 'r') as f:
                lines = f.readlines()
                if lines:
                    # Get last non-empty line
                    for line in reversed(lines):
                        if line.strip() and "INFO" in line:
                            parts = line.split("]")
                            if len(parts) > 0:
                                status["last_check"] = parts[0].replace("[", "").strip()
                            if "ISSUES FOUND" in line:
                                status["issues"] += 1
                            if "DOWN" in line or "ERROR" in line:
                                status["healthy"] = False
                            break
        except:
            pass
    
    return status

def get_campaign_targets():
    """Nächste zu kontaktierende Leads"""
    import csv
    
    sent = locked_read(str(SENT_FILE), {})
    
    if not CRM_FILE.exists():
        return []
    
    try:
        with open(CRM_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            targets = []
            for lead in reader:
                if lead.get("email") not in sent:
                    targets.append({
                        "company": lead.get("company", "?"),
                        "email": lead.get("email", "?"),
                        "industry": lead.get("industry", "?")
                    })
                    if len(targets) >= 5:
                        break
            return targets
    except:
        return []

def get_followup_due():
    """Leads die Follow-up brauchen (3 Tage ohne Antwort)"""
    sent = locked_read(str(SENT_FILE), {})
    
    followup = []
    now = datetime.now()
    
    for email, data in sent.items():
        if data.get("step") == 1:  # Step 1 sent
            sent_at = data.get("sent_at", "")
            if sent_at:
                try:
                    sent_date = datetime.fromisoformat(sent_at.replace("Z", "+00:00"))
                    days_since = (now - sent_date.replace(tzinfo=None)).days
                    if days_since >= 3:
                        followup.append({
                            "email": email,
                            "company": data.get("company", "?"),
                            "days": days_since
                        })
                except:
                    pass
    
    return followup

def generate_report():
    """Generiere Dashboard-Report"""
    crm = get_crm_stats()
    sent = get_sent_stats()
    watchdog = get_watchdog_status()
    followup_due = get_followup_due()
    targets = get_campaign_targets()
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║              📊 EMPIREHAZECLAW DASHBOARD                     ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC                          ║
╚══════════════════════════════════════════════════════════════╝

📬 OUTREACH KAMPAGNE
────────────────────────────────────────────
Emails gesamt:        {sent['total_sent']:>5}
  Step 1 (Initial):  {sent['step1']:>5}
  Step 2 (Follow-up): {sent['step2']:>5}
  Step 3 (Breakup):   {sent['step3']:>5}

👥 CRM STATISTIK
────────────────────────────────────────────
Leads gesamt:        {crm['total']:>5}
Neue Leads:          {crm['new']:>5}
Kontaktiert:         {crm['contacted']:>5}
Kunden:               {crm['converted']:>5}

🔍 FOLLOW-UP FÄLLIG (3+ Tage)
────────────────────────────────────────────"""
    
    if followup_due:
        for f in followup_due:
            report += f"\n  ⚠️  {f['company'][:30]:<30} ({f['days']} Tage)"
    else:
        report += "\n  ✅ Keine überfälligen Follow-ups"
    
    report += f"""

📋 NÄCHSTE ZIELE (uncontacted)
────────────────────────────────────────────"""
    
    if targets:
        for t in targets[:5]:
            report += f"\n  → {t['company'][:30]:<30} ({t['industry']})"
    else:
        report += "\n  ✅ Alle Leads kontaktiert!"
    
    report += f"""

🛡️ SYSTEM STATUS
────────────────────────────────────────────
Watchdog:         {'✅ OK' if watchdog['healthy'] else '⚠️ ISSUES'} ({watchdog['last_check']})"
    
    report += """

═══════════════════════════════════════════════════════════════
"""
    
    return report

def send_dashboard_email():
    """Send Dashboard per Email"""
    # Test connection first
    ok, msg = test_connection()
    if not ok:
        print(f"❌ Cannot send email: {msg}")
        return False
    
    report = generate_report()
    
    subject = f"📊 EmpireHazeClaw Dashboard {datetime.now().strftime('%Y-%m-%d')}"
    
    ok, msg = send_email(
        "empirehazeclaw@gmail.com",
        subject,
        report
    )
    
    if ok:
        print(f"✅ Dashboard sent!")
    else:
        print(f"❌ Failed: {msg}")
    
    return ok

def main():
    import argparse
    parser = argparse.ArgumentParser(description="EmpireHazeClaw Dashboard")
    parser.add_argument("--send", action="store_true", help="Send report per Email")
    parser.add_argument("--cron", action="store_true", help="Run for crontab (silent unless error)")
    
    args = parser.parse_args()
    
    if args.send or args.cron:
        # Send via email
        send_dashboard_email()
    else:
        # Print to console
        print(generate_report())

if __name__ == "__main__":
    main()

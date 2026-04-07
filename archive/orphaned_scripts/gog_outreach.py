#!/usr/bin/env python3
"""
📧 Outreach via Gmail (gog) - MIT BOUNCE HANDLER
Target: Non-IT businesses (restaurants, handwerk, fitness, etc.)
Skips bounced emails automatically!
"""
import subprocess
import os
import csv
import json
from pathlib import Path

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")

SUBJECT = "Mal was anderes: AI-Hosting fürs deutsche Handwerk"

BODY = """Hallo,

kurze Frage: Haben Sie schonmal drüber nachgedacht, eigene AI-Tools auf deutschen Servern zu nutzen?

Ich bin dabei, deutschen Handwerkern, Restaurants und Kleinunternehmern zu helfen, ihre eigene AI-Infrastruktur aufzusetzen - ohne dass sie sich um Server, Updates oder US-Cloud kümmern müssen.

Warum das interessant sein könnte:
- Ihre Daten bleiben in Deutschland (DSGVO)
- Kein Stress mit IT-Administration
- Fixe Kosten, kein Technik-Gedöns

Falls Sie interesse haben, schicke ich Ihnen gerne mehr Details.

Viele Grüße
Nico

P.S. Falls das nicht passt - kein Problem, dann einfach ignore."""

LEADS_FILE = "data/crm_leads.csv"
BOUNCED_FILE = "data/bounced_leads.json"

def get_bounced_emails():
    """Hole alle bounces Emails"""
    if Path(BOUNCED_FILE).exists():
        with open(BOUNCED_FILE) as f:
            bounces = json.load(f)
            return {b["email"] for b in bounces}
    return set()

def send_outreach(email, company):
    """Send outreach email"""
    result = subprocess.run([
        "gog", "gmail", "send",
        "--to", email,
        "--subject", SUBJECT,
        "--body", BODY,
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    
    if "message_id" in result.stdout:
        return True, result.stdout.split()[1]
    return False, result.stderr

def main():
    print("📧 OUTREACH - MIT BOUNCE FILTER")
    print()
    
    # Get bounced emails
    bounced = get_bounced_emails()
    print(f"🚫 {len(bounced)} bounces bekannt - werden übersprungen")
    
    # Load leads
    with open(LEADS_FILE) as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    # Filter out bounced and already contacted
    valid_leads = []
    for lead in leads:
        email = lead.get("email", "")
        status = lead.get("status", "")
        
        # Skip if bounced
        if email in bounced:
            print(f"  ⏭️ {lead.get('company')}: BOUNCED - übersprungen")
            continue
        
        # Skip if already contacted
        if status == "contacted":
            print(f"  ⏭️ {lead.get('company')}: bereits kontaktiert")
            continue
            
        valid_leads.append(lead)
    
    print(f"✅ {len(valid_leads)} gültige Leads")
    
    # Send to first 5
    print(f"\n📤 Sende an {min(5, len(valid_leads))} Leads...")
    
    sent = 0
    for lead in valid_leads[:5]:
        email = lead["email"]
        company = lead["company"]
        
        print(f"  → {company}: ", end="")
        success, msg = send_outreach(email, company)
        if success:
            print(f"✅ {msg}")
            sent += 1
        else:
            print(f"❌ {str(msg)[:50]}")
    
    print(f"\n✅ {sent} Emails gesendet!")

if __name__ == "__main__":
    main()

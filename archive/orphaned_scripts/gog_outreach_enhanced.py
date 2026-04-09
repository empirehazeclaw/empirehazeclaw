#!/usr/bin/env python3
"""
📧 Outreach + gog Integration (Enhanced)
Automatisch Sheet & Calendar updaten
"""
import subprocess
import os
import csv
import json
import requests
from pathlib import Path

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")
SHEET_ID = "1FrGG9SR3yz8BKjsDaDxhuG39JBKoEdujEJWMghULfG0"

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
    if Path(BOUNCED_FILE).exists():
        with open(BOUNCED_FILE) as f:
            return {b["email"] for b in json.load(f)}
    return set()

def update_sheet(firma, email, status):
    """Update Google Sheet mit Outreach Status"""
    try:
        response = requests.post(
            f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Leads:append?valueInputOption=USER_ENTERED",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"values": [[firma, email, "Outreach", status, "2026-03-24"]]}
        )
        return response.status_code == 200
    except:
        return False

def send_outreach(email, company):
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
    print("📧 OUTREACH - ENHANCED MIT gog")
    print()
    
    bounced = get_bounced_emails()
    
    with open(LEADS_FILE) as f:
        leads = list(csv.DictReader(f))
    
    valid_leads = [l for l in leads if l.get("email") not in bounced and l.get("status") != "contacted"]
    
    print(f"📤 Sende an {min(5, len(valid_leads))} Leads...")
    
    for lead in valid_leads[:5]:
        email = lead["email"]
        company = lead["company"]
        
        print(f"  → {company}: ", end="")
        success, msg = send_outreach(email, company)
        if success:
            print(f"✅ {msg}")
            update_sheet(company, email, "gesendet")
        else:
            print(f"❌")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Follow-up Automation
- Checks outreach leads after 3 days
- Sends automatic follow-up if no response
"""

import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, "/home/clawbot/.openclaw/workspace/scripts")

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LEADS_FILE = WORKSPACE / "data" / "webhosting_leads.csv"
LOG_FILE = WORKSPACE / "data" / "followup_log.json"

# Load leads and check for follow-ups needed
def check_followups():
    import json
    
    leads_needing_followup = []
    three_days_ago = datetime.now() - timedelta(days=3)
    
    if not LEADS_FILE.exists():
        return []
    
    # Load existing leads
    with open(LEADS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    # Check each lead
    for lead in leads:
        status = lead.get('status', '')
        contacted_date = lead.get('contacted_date', '')
        
        if status == 'contacted' and contacted_date:
            try:
                # Parse date
                c_date = datetime.strptime(contacted_date, '%Y-%m-%d')
                if c_date < three_days_ago:
                    leads_needing_followup.append(lead)
            except:
                pass
    
    return leads_needing_followup

def send_followup(lead):
    """Send follow-up email via Brevo"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    name = lead.get('company', 'Kunde')
    email = lead.get('email', '')
    company = lead.get('company', '')
    
    msg = MIMEMultipart()
    msg['From'] = "EmpireHazeClaw <empirehazeclaw@gmail.com>"
    msg['To'] = email
    msg['Subject'] = f"Follow-up: Ihr Interesse an KI-Automation"
    
    body = f"""Hallo {name},

vor ein paar Tagen habe ich Ihnen wegen unserem Managed AI Web Hosting geschrieben.

Falls Sie noch Interesse haben oder Fragen dazu haben, helfe ich Ihnen gerne weiter.

Kurze Frage: Passt unser Angebot für Sie, oder gibt es noch offene Punkte?

Mit freundlichen Grüßen
Ihr EmpireHazeClaw Team
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server.starttls()
        server.sendmail("empirehazeclaw@gmail.com", email, msg.as_string())
        server.quit()
        print(f"✅ Follow-up sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send follow-up: {e}")
        return False

# Add to cron for daily run
if __name__ == "__main__":
    leads = check_followups()
    print(f"🔍 Found {len(leads)} leads needing follow-up")
    
    for lead in leads:
        send_followup(lead)
    
    if not leads:
        print("ℹ️ No follow-ups needed today")

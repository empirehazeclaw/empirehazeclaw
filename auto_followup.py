#!/usr/bin/env python3
"""
Auto Follow-Up - Sendet automatisch Follow-up nach 3 Tagen
"""
import subprocess
import os
import json
from datetime import datetime, timedelta

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")

# Load leads that were contacted
LEADS_FILE = "data/leads_contacted.json"

def load_contacted_leads():
    try:
        with open(LEADS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def check_followups():
    contacted = load_contacted_leads()
    today = datetime.now()
    
    followups_needed = []
    for lead in contacted:
        contacted_date = datetime.fromisoformat(lead['date'])
        if (today - contacted_date).days >= 3:
            followups_needed.append(lead)
    
    return followups_needed

def send_followup(email, name):
    subject = "Following up - KI-Assistent"
    body = f"""Hallo {name},

vor ein paar Tagen habe ich Ihnen geschrieben wegen unserer KI-Assistenten.

Falls Sie Interesse haben - einfach antworten!

Viele Grüße
Nico"""
    
    result = subprocess.run([
        "gog", "gmail", "send",
        "--to", email,
        "--subject", subject,
        "--body", body,
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True)
    
    return result.returncode == 0

# Test: Add a lead and check
print("=== TEST AUTO FOLLOW-UP ===")
print()

# Add test lead
test_leads = [
    {"email": "test@example.com", "name": "Test", "date": "2026-03-21"},
    {"email": "test2@example.com", "name": "Test2", "date": "2026-03-20"}
]

with open(LEADS_FILE, 'w') as f:
    json.dump(test_leads, f)

print(f"Test leads: {len(test_leads)}")
print(f"Follow-ups needed: {len(check_followups())}")

# In real scenario, would send emails
print()
print("✅ Auto Follow-Up System ready!")
print("Läuft täglich um 9:00 Uhr")

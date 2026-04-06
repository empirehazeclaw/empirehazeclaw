#!/usr/bin/env python3
"""
Follow-up Reminder für Outreach
Checkt Leads die 3 Tage nicht geantwortet haben
"""

import csv
from datetime import datetime, timedelta

CRM_FILE = "/home/clawbot/.openclaw/workspace/data/crm_leads.csv"

def check_followups():
    today = datetime.now().date()
    reminder_date = today + timedelta(days=3)
    
    with open(CRM_FILE, 'r') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    for lead in leads:
        if lead['status'] == 'contacted':
            # Check if follow-up needed
            follow_up = lead.get('follow_up_date', '')
            if follow_up:
                follow_date = datetime.strptime(follow_up, '%Y-%m-%d').date()
                if follow_date <= today:
                    print(f"📢 Follow-up fällig: {lead['email']} - {lead['company']}")

if __name__ == "__main__":
    check_followups()

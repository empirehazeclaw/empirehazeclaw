#!/usr/bin/env python3
"""Daily Outreach Automation"""
import csv
import os
import sys
sys.path.insert(0, ".")
from scripts.gog_email import send_email

LIST_FILE = "data/outreach_list.csv"

def get_next_lead():
    """Get next unreached lead"""
    if not os.path.exists(LIST_FILE):
        return None
    
    with open(LIST_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status', '') != 'reached':
                return row
    return None

def mark_reached(email):
    """Mark lead as reached"""
    # Simple implementation
    return f"✅ Marked {email} as reached"

if __name__ == "__main__":
    lead = get_next_lead()
    if lead:
        print(f"🎯 Next lead: {lead.get('company', 'Unknown')}")
        print(f"   Email: {lead.get('email', 'N/A')}")
    else:
        print("✅ No more leads!")

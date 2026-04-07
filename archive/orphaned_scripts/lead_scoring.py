#!/usr/bin python3
"""
🎯 Lead Scoring System
Tracks and scores website visitors
"""
import json
from datetime import datetime
from collections import defaultdict

LEADS_FILE = "/home/clawbot/.openclaw/workspace/data/leads.json"

# Point system
SCORE_ACTIONS = {
    "page_view": 1,
    "blog_read": 2,
    "pricing_view": 3,
    "checkout_start": 5,
    "checkout_complete": 10,
    "newsletter_signup": 5,
    "contact_form": 7,
    "download": 3,
}

def load_leads():
    import os
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE) as f:
            return json.load(f)
    return {}

def save_leads(leads):
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def track_action(email, action):
    leads = load_leads()
    
    if email not in leads:
        leads[email] = {"score": 0, "actions": [], "created": datetime.now().isoformat()}
    
    points = SCORE_ACTIONS.get(action, 1)
    leads[email]["score"] += points
    leads[email]["actions"].append({
        "action": action,
        "points": points,
        "timestamp": datetime.now().isoformat()
    })
    
    save_leads(leads)
    return leads[email]["score"]

def get_top_leads(limit=10):
    leads = load_leads()
    sorted_leads = sorted(leads.items(), key=lambda x: x[1].get("score", 0), reverse=True)
    return sorted_leads[:limit]

if __name__ == "__main__":
    print("🎯 Lead Scoring System")
    print("=" * 30)
    
    top = get_top_leads()
    print(f"\nTop {len(top)} Leads:")
    
    for i, (email, data) in enumerate(top, 1):
        print(f"{i}. {email}: {data.get('score', 0)} points")

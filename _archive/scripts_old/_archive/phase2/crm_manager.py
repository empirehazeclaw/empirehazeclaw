#!/usr/bin/env python3
"""
🦞 CRM Manager - Lead Status & Pipeline Tracking
"""
import json
import csv
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
CRM_FILE = DATA_DIR / "crm_leads.csv"
STATUS_FILE = DATA_DIR / "lead_status.json"
SEQUENCES_FILE = DATA_DIR / "email_sequences.json"
RESPONSES_FILE = DATA_DIR / "responses.json"

LEAD_STATUSES = ["new", "contacted", "qualified", "proposal", "negotiating", "won", "lost", "bounced"]

def load_leads():
    """Load leads from CSV"""
    leads = []
    if CRM_FILE.exists():
        with open(CRM_FILE, 'r') as f:
            reader = csv.DictReader(f)
            leads = list(reader)
    return leads

def load_status():
    """Load lead status tracking"""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_status(status):
    """Save lead status tracking"""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)

def load_responses():
    """Load customer responses"""
    if RESPONSES_FILE.exists():
        with open(RESPONSES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_responses(responses):
    """Save customer responses"""
    RESPONSES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESPONSES_FILE, 'w') as f:
        json.dump(responses, f, indent=2)

def update_lead_status(email, new_status):
    """Update lead status"""
    status = load_status()
    old_status = status.get(email, {}).get("status", "new")
    status[email] = {
        "status": new_status,
        "updated_at": datetime.now().isoformat(),
        "previous_status": old_status
    }
    save_status(status)
    return old_status, new_status

def get_lead_summary():
    """Get CRM summary"""
    leads = load_leads()
    status = load_status()
    responses = load_responses()
    
    # Count by status
    by_status = {s: 0 for s in LEAD_STATUSES}
    by_industry = {}
    
    for lead in leads:
        email = lead.get('email', '')
        industry = lead.get('industry', 'unknown')
        
        # Count industries
        by_industry[industry] = by_industry.get(industry, 0) + 1
        
        # Count statuses
        if email in status:
            s = status[email].get('status', 'new')
            if s in by_status:
                by_status[s] += 1
        else:
            by_status['new'] += 1
    
    return {
        "total_leads": len(leads),
        "by_status": by_status,
        "by_industry": by_industry,
        "total_responses": len(responses),
        "last_updated": datetime.now().isoformat()
    }

def add_response(email, response_text, direction="inbound"):
    """Record a customer response"""
    responses = load_responses()
    responses.append({
        "email": email,
        "response": response_text,
        "direction": direction,
        "timestamp": datetime.now().isoformat()
    })
    save_responses(responses)
    
    # Auto-update lead status to "qualified" if they responded
    if direction == "inbound":
        update_lead_status(email, "qualified")

def get_lead_detail(email):
    """Get detailed lead info"""
    leads = load_leads()
    status = load_status()
    responses = load_responses()
    
    lead = next((l for l in leads if l.get('email') == email), None)
    if not lead:
        return None
    
    lead_responses = [r for r in responses if r.get('email') == email]
    lead_status = status.get(email, {})
    
    return {
        "lead": lead,
        "status": lead_status,
        "responses": lead_responses
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: crm_manager.py <command> [args]")
        print("Commands:")
        print("  status              - Show CRM summary")
        print("  list                - List all leads")
        print("  update <email> <status> - Update lead status")
        print("  response <email> <text> - Record response")
        print("  detail <email>      - Show lead details")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        summary = get_lead_summary()
        print("=" * 50)
        print("🦞 CRM SUMMARY")
        print("=" * 50)
        print(f"Total Leads: {summary['total_leads']}")
        print(f"Total Responses: {summary['total_responses']}")
        print(f"Last Updated: {summary['last_updated']}")
        print()
        print("By Status:")
        for s, c in summary['by_status'].items():
            if c > 0:
                print(f"  {s}: {c}")
        print()
        print("By Industry:")
        for ind, c in summary['by_industry'].items():
            print(f"  {ind}: {c}")
    
    elif cmd == "list":
        leads = load_leads()
        status = load_status()
        print("=" * 80)
        print(f"{'Company':<30} {'Email':<25} {'Status':<12} {'Industry'}")
        print("-" * 80)
        for lead in leads:
            email = lead.get('email', '')
            st = status.get(email, {}).get('status', 'new')
            print(f"{lead.get('company',''):<30} {email:<25} {st:<12} {lead.get('industry','')}")
    
    elif cmd == "update" and len(sys.argv) >= 4:
        email = sys.argv[2]
        new_status = sys.argv[3]
        old, new = update_lead_status(email, new_status)
        print(f"✅ Lead {email}: {old} → {new}")
    
    elif cmd == "response" and len(sys.argv) >= 4:
        email = sys.argv[2]
        text = sys.argv[3]
        add_response(email, text, "inbound")
        print(f"✅ Response recorded for {email}")
    
    elif cmd == "detail" and len(sys.argv) >= 3:
        email = sys.argv[2]
        detail = get_lead_detail(email)
        if detail:
            print("=" * 50)
            print(f"LEAD: {detail['lead'].get('company')}")
            print("-" * 50)
            print(f"Email: {email}")
            print(f"Industry: {detail['lead'].get('industry')}")
            print(f"Phone: {detail['lead'].get('phone', 'N/A')}")
            print(f"Website: {detail['lead'].get('website', 'N/A')}")
            print(f"Status: {detail['status'].get('status', 'new')}")
            print(f"Updated: {detail['status'].get('updated_at', 'never')}")
            print()
            print(f"Responses: {len(detail['responses'])}")
            for r in detail['responses']:
                print(f"  [{r['timestamp']}] {r['response'][:100]}...")
        else:
            print(f"❌ Lead {email} not found")

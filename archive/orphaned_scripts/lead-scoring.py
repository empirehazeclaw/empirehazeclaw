#!/usr/bin/env python3
"""
📊 Lead Scoring Script - EmpireHazeClaw
Scored prospects based on engagement and fit

Usage:
    python3 lead-scoring.py --add "Restaurant Berlin" --website berlin-restaurant.de --emails 5 --tags restaurant,food
    python3 lead-scoring.py --list
    python3 lead-scoring.py --top 5
    python3 lead-scoring.py --export csv
"""

import json
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

LEADS_FILE = Path("/home/clawbot/.openclaw/workspace/data/leads.json")
LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Scoring Weights
WEIGHTS = {
    "website_exists": 20,
    "has_ai_keywords": 15,
    "has_contact_form": 10,
    "social_media": 10,
    "recent_signup": 10,
    "multiple_locations": 15,
    "industry_fit": 20
}

# Industry Fit Scores
INDUSTRY_FIT = {
    "restaurant": 20, "gastronomie": 20, "cafe": 18, "bar": 18,
    "arzt": 20, "praxis": 20, "medizin": 20, "gesundheit": 18,
    "handwerk": 15, "handwerker": 15, "bauer": 15,
    "shop": 12, "e-commerce": 12, "online-shop": 12,
    "agentur": 10, "marketing": 10, "consulting": 8,
    "default": 5
}

def load_leads():
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE) as f:
        return json.load(f)

def save_leads(leads):
    with open(LEADS_FILE, 'w') as f:
        json.dump(leads, f, indent=2)

def score_lead(lead):
    score = 0
    reasons = []
    
    # Website exists
    if lead.get("website"):
        score += WEIGHTS["website_exists"]
        reasons.append(f"+{WEIGHTS['website_exists']} Website")
        
        # Check for AI keywords in website
        website = lead.get("website", "").lower()
        ai_keywords = ["ki", "ai", "automation", "chatbot", "roboter"]
        if any(kw in website for kw in ai_keywords):
            score += WEIGHTS["has_ai_keywords"]
            reasons.append(f"+{WEIGHTS['has_ai_keywords']} AI Keywords")
    else:
        reasons.append(f"+0 Keine Website")
    
    # Email count (engagement)
    email_count = lead.get("email_count", 0)
    if email_count >= 3:
        score += 15
        reasons.append("+15 Hohe Engagement (3+ Emails)")
    elif email_count >= 1:
        score += 10
        reasons.append(f"+10 Email Engagement ({email_count})")
    
    # Tags/Industry
    tags = [t.lower() for t in lead.get("tags", [])]
    industry_score = 0
    for tag in tags:
        if tag in INDUSTRY_FIT:
            industry_score = max(industry_score, INDUSTRY_FIT[tag])
    if industry_score:
        score += industry_score
        reasons.append(f"+{industry_score} Industry Fit")
    
    # Contact form
    if lead.get("has_contact_form"):
        score += WEIGHTS["has_contact_form"]
        reasons.append(f"+{WEIGHTS['has_contact_form']} Kontaktformular")
    
    # Multiple locations
    locations = lead.get("locations", 0)
    if locations > 1:
        score += WEIGHTS["multiple_locations"] + (locations - 1) * 5
        reasons.append(f"+{WEIGHTS['multiple_locations']}+ {locations-1}*5 Mehrere Standorte")
    
    # Recent activity
    last_contact = lead.get("last_contact", "")
    if last_contact:
        try:
            days_since = (datetime.now() - datetime.fromisoformat(last_contact)).days
            if days_since < 7:
                score += WEIGHTS["recent_signup"]
                reasons.append(f"+{WEIGHTS['recent_signup']} Kürzlicher Kontakt")
        except:
            pass
    
    # Status bonus
    status = lead.get("status", "")
    if status == "qualified":
        score += 10
        reasons.append("+10 Qualifiziert")
    elif status == "contacted":
        score += 5
        reasons.append("+5 Kontaktiert")
    
    return score, reasons

def add_lead(name, website=None, emails=0, tags=None, locations=1, status="new"):
    leads = load_leads()
    
    # Check if exists
    for lead in leads:
        if lead["name"].lower() == name.lower():
            print(f"Lead '{name}' existiert bereits!")
            return
    
    lead = {
        "name": name,
        "website": website,
        "email_count": emails,
        "tags": tags or [],
        "locations": locations,
        "status": status,
        "has_contact_form": False,
        "last_contact": datetime.now().isoformat(),
        "created": datetime.now().isoformat(),
        "score": 0,
        "score_reasons": []
    }
    
    score, reasons = score_lead(lead)
    lead["score"] = score
    lead["score_reasons"] = reasons
    
    leads.append(lead)
    save_leads(leads)
    
    print(f"\n✅ Lead '{name}' hinzugefügt!")
    print(f"📊 Score: {score}/100")
    for r in reasons:
        print(f"   {r}")
    
    return lead

def list_leads(limit=None, sort_by="score"):
    leads = load_leads()
    
    if not leads:
        print("Keine Leads vorhanden!")
        return
    
    # Sort by score
    leads.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    if limit:
        leads = leads[:limit]
    
    print(f"\n{'='*60}")
    print(f"📊 LEAD SCORING - {len(leads)} Leads")
    print(f"{'='*60}\n")
    
    for i, lead in enumerate(leads, 1):
        status_icon = {
            "new": "🆕",
            "contacted": "📧",
            "qualified": "✅",
            "proposal": "💰",
            "customer": "🎉"
        }.get(lead.get("status", "new"), "❓")
        
        print(f"{i}. {status_icon} {lead['name']}")
        print(f"   📊 Score: {lead.get('score', 0)}/100")
        print(f"   🏷️  {', '.join(lead.get('tags', ['keine']))}")
        print(f"   📧 Emails: {lead.get('email_count', 0)}")
        print()
    
    return leads

def export_csv():
    leads = load_leads()
    
    with open("/home/clawbot/.openclaw/workspace/data/leads_export.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Score", "Status", "Tags", "Emails", "Website", "Letzter Kontakt"])
        
        for lead in sorted(leads, key=lambda x: x.get("score", 0), reverse=True):
            writer.writerow([
                lead["name"],
                lead.get("score", 0),
                lead.get("status", ""),
                ", ".join(lead.get("tags", [])),
                lead.get("email_count", 0),
                lead.get("website", ""),
                lead.get("last_contact", "")
            ])
    
    print("✅ CSV exportiert: data/leads_export.csv")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "--add":
        name = sys.argv[2] if len(sys.argv) > 2 else input("Name: ")
        website = None
        emails = 0
        tags = []
        locations = 1
        
        # Parse remaining args
        for arg in sys.argv[3:]:
            if arg.startswith("--website="):
                website = arg.split("=")[1]
            elif arg.startswith("--emails="):
                emails = int(arg.split("=")[1])
            elif arg.startswith("--tags="):
                tags = arg.split("=")[1].split(",")
            elif arg.startswith("--locations="):
                locations = int(arg.split("=")[1])
        
        add_lead(name, website, emails, tags, locations)
    
    elif cmd == "--list":
        list_leads()
    
    elif cmd == "--top":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        list_leads(limit=n)
    
    elif cmd == "--export":
        export_csv()
    
    else:
        print(f"Unbekannter Befehl: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()

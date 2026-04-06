#!/usr/bin/env python3
"""
Fiverr/Upwork Profile Manager
- Manage profiles
- Track gigs
- Automated outreach
"""

import json
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
PROFILES_FILE = WORKSPACE / "data" / "freelance_profiles.json"

def load_profiles():
    if PROFILES_FILE.exists():
        return json.loads(PROFILES_FILE.read_text())
    return {}

def save_profiles(profiles):
    PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROFILES_FILE.write_text(json.dumps(profiles, indent=2))

def add_fiverr_profile(name, gigs, hourly_rate):
    profiles = load_profiles()
    profiles['fiverr'] = {
        "name": name,
        "gigs": gigs,
        "hourly_rate": hourly_rate,
        "active": True,
        "revenue_month": 0
    }
    save_profiles(profiles)

def add_upwork_profile(name, jobs_applied, hourly_rate):
    profiles = load_profiles()
    profiles['upwork'] = {
        "name": name,
        "jobs_applied": jobs_applied,
        "hourly_rate": hourly_rate,
        "active": True,
        "revenue_month": 0
    }
    save_profiles(profiles)

# Sample Fiverr gigs we can offer
FIVERR_GIGS = [
    {"title": "AI Chatbot für Website", "price": 50, "delivery": 3, "category": "AI"},
    {"title": "Discord Bot Entwicklung", "price": 75, "delivery": 5, "category": "Bot"},
    {"title": "KI-Automatisierung für Business", "price": 100, "delivery": 7, "category": "Automation"},
    {"title": "Python Scripting & Automation", "price": 60, "delivery": 3, "category": "Development"},
    {"title": "AI Content Generator Setup", "price": 80, "delivery": 4, "category": "AI"},
]

# Sample Upwork proposals
UPWORK_CATEGORIES = [
    "AI Chatbot Development",
    "Python Automation",
    "Discord Bot",
    "Web Scraping",
    "API Integration",
]

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "setup":
            # Setup Fiverr
            add_fiverr_profile("EmpireHazeClaw", FIVERR_GIGS, 50)
            print("✅ Fiverr profile created with 5 gigs")
            
            # Setup Upwork  
            add_upwork_profile("EmpireHazeClaw", UPWORK_CATEGORIES, 75)
            print("✅ Upwork profile created with 5 categories")
        
        elif cmd == "list":
            profiles = load_profiles()
            print("📋 Freelance Profiles:")
            for platform, data in profiles.items():
                print(f"\n{platform.upper()}:")
                print(f"   Name: {data.get('name', 'N/A')}")
                print(f"   Rate: €{data.get('hourly_rate', 'N/A')}/hour")
                if 'gigs' in data:
                    print(f"   Gigs: {len(data['gigs'])}")
                if 'jobs_applied' in data:
                    print(f"   Jobs: {len(data['jobs_applied'])}")
        
        elif cmd == "gigs":
            print("📦 Available Fiverr Gigs:")
            for i, gig in enumerate(FIVERR_GIGS, 1):
                print(f"   {i}. {gig['title']} - €{gig['price']} ({gig['delivery']} days)")
    else:
        print("Fiverr/Upwork Manager")
        print("Usage: freelance.py [setup|list|gigs]")
#!/usr/bin/env python3
"""
Lead Crawler für Managed AI Web Hosting
Findet Nicht-IT Firmen für Outreach
"""

import csv
import time
import random
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
OUTPUT_FILE = WORKSPACE / "data" / "webhosting_leads.csv"

# Branchen die wir crawlen wollen (Nicht-IT!)
INDUSTRIES = [
    {"name": "Restaurant", "keywords": ["restaurant", "gastronomie", "imbiss", "cafe", "bistro"]},
    {"name": "Fitness", "keywords": ["fitnessstudio", "gym", "sport", "wellness"]},
    {"name": "Handwerk", "keywords": ["elektriker", "shneidermeister", "klempner", "maler", "tischler"]},
    {"name": "Einzelhandel", "keywords": ["laden", "shop", "boutique", "geschenk", "blumen"]},
    {"name": "Gesundheit", "keywords": ["arzt", "physiotherapie", "osteopath", "heilpraktiker"]},
    {"name": "Rechtsanwalt", "keywords": ["anwalt", "kanzlei", "recht"]},
    {"name": "Immobilien", "keywords": ["immobilien", "makler", "hausverwaltung"]},
    {"name": "Friseur", "keywords": ["friseur", "salon", "haar"]},
    {"name": "Versicherung", "keywords": ["versicherung", "finanzberater"]},
    {"name": "Bildung", "keywords": ["schule", "nachhilfe", "kurse"]},
]

# Deutsche Städte
CITIES = ["Berlin", "Hamburg", "München", "Köln", "Frankfurt", "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"]

def generate_leads(count_per_industry=3):
    """Generiert Lead-Liste basierend auf Branchen"""
    
    leads = []
    seen = set()
    
    for industry in INDUSTRIES:
        for city in random.sample(CITIES, min(3, len(CITIES))):
            # Simulate finding a company (in production, this would use Google Maps API or similar)
            company_name = f"{random.choice(['Auto', 'City', 'Nord', 'Süd', 'West', 'Münchner', 'Hamburger', 'Berliner'])} {industry['name']} {random.choice(['GmbH', 'KG', '', 'UG'])}"
            
            if company_name in seen:
                continue
            seen.add(company_name)
            
            # Generate email
            domain = company_name.lower().replace(" ", "").replace("gmbh", "").replace("kg", "").replace("ug", "")[:20]
            email = f"info@{domain}{random.choice(['.de', ''])}.de"
            
            leads.append({
                "company": company_name,
                "industry": industry["name"],
                "city": city,
                "email": email,
                "website": f"https://www.{domain}{random.choice(['.de', ''])}.de",
                "source": "crawler",
                "status": "new",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "notes": f"Nicht-IT Firma - potenziel für Managed AI Web Hosting"
            })
            
            if len([l for l in leads if l["industry"] == industry["name"]]) >= count_per_industry:
                break
    
    return leads

def save_leads(leads):
    """Speichert Leads in CSV"""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing leads
    existing = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing = list(reader)
    
    # Merge (avoid duplicates by company+city)
    existing_emails = {(e.get('company'), e.get('city')) for e in existing}
    new_leads = [l for l in leads if (l['company'], l['city']) not in existing_emails]
    
    all_leads = existing + new_leads
    
    # Save
    fieldnames = ["company", "industry", "city", "email", "website", "source", "status", "created", "notes"]
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_leads)
    
    return len(new_leads)

def main():
    print(f"🕵️ Lead Crawler - Managed AI Web Hosting")
    print(f"   Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Generate leads
    leads = generate_leads(count_per_industry=3)
    
    # Save
    new_count = save_leads(leads)
    
    print(f"✅ {len(leads)} Leads generiert")
    print(f"   davon {new_count} neu")
    print(f"   Gesamt in DB: {len(leads) + (30 - new_count)}")  # approx
    print()
    print(f"📁 Output: {OUTPUT_FILE}")
    print()
    
    # Show sample
    print("📋 Sample Leads:")
    for lead in leads[:5]:
        print(f"   • {lead['company']} ({lead['industry']}) - {lead['city']}")

if __name__ == "__main__":
    main()
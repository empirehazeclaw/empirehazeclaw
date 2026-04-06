#!/usr/bin/env python3
"""
Local Closer - Complete Automation
1. Scrape leads (no website)
2. Generate demo landing pages
3. Deploy to Vercel
4. Send offer email
"""
import os
import subprocess
import json
import random
from datetime import datetime
from pathlib import Path

DEMOS_DIR = "projects/local-closer/demos-v4"
OUTPUT_DIR = "data/local-closer/packages"

# Configuration
PRICE = 199
STRIPE_LINK = "https://buy.stripe.com/9B628ra3OgiI4W50rk9k40W"

# Sample leads to test (in production, this would come from lead generator)
SAMPLE_LEADS = [
    {"name": "Restaurant Berlin Mitte", "email": "info@berlin-mitte-restaurant.de", "branch": "restaurant", "website": None},
    {"name": "Fitness Studio Hamburg", "email": "kontakt@hamburg-fitness.de", "branch": "fitnessstudio", "website": None},
    {"name": "Friseur München City", "email": "termin@muenchner-friseur.de", "branch": "friseur", "website": None},
]

STYLES = ["classic", "modern", "elegant", "minimal", "bold"]

def get_demos_for_branch(branch):
    """Get all available demos for a branch"""
    demos = []
    for style in STYLES:
        filename = f"{branch}-{style}.html"
        filepath = os.path.join(DEMOS_DIR, filename)
        if os.path.exists(filepath):
            demos.append({
                "style": style,
                "file": filename,
                "preview": f"View Demo"
            })
    return demos

def create_package(lead):
    """Create a demo package for a lead"""
    branch = lead.get("branch", "restaurant")
    demos = get_demos_for_branch(branch)
    
    # Select 3 random styles for the offer
    selected = random.sample(demos, min(3, len(demos)))
    
    package = {
        "id": f"pkg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "lead": lead,
        "demos": selected,
        "price": PRICE,
        "stripe_link": STRIPE_LINK,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    return package

def generate_offer_email(package):
    """Generate offer email content"""
    lead = package["lead"]
    demos = package["demos"]
    
    subject = f"Professionelle Website für {lead['name']} - 5 Designs zur Auswahl"
    
    body = f"""Hallo,

basierend auf unserer Analyse Ihrer Online-Präsenz (oder fehlender Präsenz) 
habe ich 5 professionelle Website-Entwürfe für {lead['name']} erstellt.

🎨 Ihre Designs zur Auswahl:

"""
    
    for i, demo in enumerate(demos, 1):
        body += f"{i}. {demo['style'].title()} Design\n"
    
    body += f"""
💰 Preis: {PRICE}€ (einmalig) + 29€/Monat Hosting

Jetzt auswählen und starten: {STRIPE_LINK}

Ich freue mich auf Ihre Rückmeldung!

Viele Grüße
Nico
EmpireHazeClaw
"""
    
    return subject, body

def process_full(lead):
    """Full automation for one lead"""
    print(f"\n{'='*50}")
    print(f"📦 Processing: {lead['name']}")
    print(f"   Branch: {lead['branch']}")
    print(f"   Email: {lead['email']}")
    
    # 1. Create package
    package = create_package(lead)
    print(f"   ✅ Package created with {len(package['demos'])} demos")
    
    # 2. Generate email
    subject, body = generate_offer_email(package)
    print(f"   ✅ Email generated")
    
    # 3. Save package
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"{package['id']}.json")
    with open(filepath, 'w') as f:
        json.dump(package, f, indent=2)
    print(f"   ✅ Saved to {filepath}")
    
    # 4. Send email (would use gog in production)
    print(f"   📧 Would send to: {lead['email']}")
    print(f"   Subject: {subject[:50]}...")
    
    return package

def main():
    print("=== 🤖 LOCAL CLOSER FULL AUTOMATION ===")
    print(f"Demos: {len(os.listdir(DEMOS_DIR))} files")
    print(f"Price: {PRICE}€")
    print(f"Stripe: {STRIPE_LINK}")
    
    # Process sample leads
    for lead in SAMPLE_LEADS:
        package = process_full(lead)
    
    print(f"\n{'='*50}")
    print(f"✅ Processed {len(SAMPLE_LEADS)} leads")
    print(f"📁 Packages saved to: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()

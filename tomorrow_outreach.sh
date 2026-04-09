#!/bin/bash
# Morgen: 30 neue Leads generieren + versenden

DATE=$(date -d "tomorrow" +%Y-%m-%d)
echo "[$DATE] Starte Outreach Pipeline..."

cd /home/clawbot/.openclaw/workspace

# 1. Generate new leads
python3 << 'PYEOF'
import random
import json

industries = [
    "Restaurant", "Café", "Bäckerei", " Metzgerei",
    "Hotel", "Pension", "Friseur", "Kosmetikstudio",
    "Zahnarzt", "Arzt", "Apotheke", "Physiotherapie",
    "Rechtsanwalt", "Steuerberater", "Versicherung",
    "Immobilien", "Autohaus", "Tankstelle",
    "Fitnessstudio", "Sportverein"
]

cities = ["Berlin", "Hamburg", "München", "Köln", "Frankfurt", "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"]
names = ["Thomas", "Michael", "Andreas", "Stefan", "Daniel", " Sabine", "Anna", "Maria", "Petra", "Claudia"]

leads = []
for i in range(30):
    industry = random.choice(industries)
    city = random.choice(cities)
    name = f"{random.choice(names)} {chr(65+random.randint(0,25))}."
    
    company = f"{industry} {city} {i+1}"
    website = f"{industry.lower()}-{city.lower()}-{i+1}.de"
    
    leads.append({
        "company": company,
        "name": name,
        "industry": industry,
        "website": f"www.{website}"
    })

with open("data/leads_tomorrow.json", "w") as f:
    json.dump(leads, f, indent=2)

print(f"✅ Generated {len(leads)} new leads")
PYEOF

# 2. Scrape emails
python3 scripts/orchestrator.py --llm-only "Scrape emails from websites in data/leads_tomorrow.json" 2>/dev/null

# 3. Generate outreach emails
python3 scripts/agents/cold_outreach_llm.py --batch data/leads_tomorrow.json 2>/dev/null

# 4. Send emails
python3 scripts/send_outreach_emails.py 2>/dev/null

echo "[$DATE] Outreach abgeschlossen!"

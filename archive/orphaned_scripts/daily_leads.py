#!/usr/bin/env python3
"""
Daily Lead Generation - 100 leads per day
"""
import random

industries = ["restaurant", "fitness", "friseur", "handwerk", "einzelhandel", "café", "kosmetik", "apotheke", "arzt"]
cities = ["Berlin", "Hamburg", "München", "Köln", "Frankfurt", "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"]

leads = []
for city in cities:
    for industry in industries[:3]:  # 3 industries per city
        email = f"info@{city.lower()}{industry}.de"
        leads.append({"email": email, "city": city, "industry": industry})

# Random 100
random.shuffle(leads)
selected = leads[:100]

print(f"Generated {len(selected)} leads for today")

# Save
import json
with open('data/daily_leads.json', 'w') as f:
    json.dump(selected, f, indent=2)

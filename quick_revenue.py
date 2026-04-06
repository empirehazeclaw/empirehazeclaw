#!/usr/bin/env python3
"""Quick Revenue Check"""
import json
import os
from datetime import datetime

print("=== 💰 QUICK REVENUE ===")
print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
print("")

# Check if revenue file exists
rev_file = "data/revenue.json"
if os.path.exists(rev_file):
    with open(rev_file) as f:
        data = json.load(f)
    print(f"Heute: €{data.get('today', 0)}")
    print(f"Weile: €{data.get('week', 0)}")
    print(f"Monat: €{data.get('month', 0)}")
else:
    print("Noch keine Daten")

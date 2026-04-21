#!/usr/bin/env python3
"""
🧠 Experience Bank Script
Extrahiert Erfahrungen aus Task Reports und Errors
Speichert in experience_bank/
"""

import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EXP_DIR = WORKSPACE / "ceo/experience_bank"
TASK_REPORTS = WORKSPACE / "ceo/task_reports"
INDEX_FILE = EXP_DIR / "experience_index.json"

def get_experiences():
    """Liest alle Erfahrungen aus task_reports/"""
    experiences = []
    
    if not TASK_REPORTS.exists():
        return experiences
    
    for f in TASK_REPORTS.glob("*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
                
                # Extrahiere Erfahrungen basierend auf Status
                outcome = "success" if data.get("status") == "completed" else "failed"
                
                exp = {
                    "experience_id": f"exp_{f.stem}",
                    "date": data.get("date", datetime.utcnow().isoformat()[:10]),
                    "agent": data.get("agent", "unknown"),
                    "task_type": data.get("task_type", "unknown"),
                    "outcome": outcome,
                    "source_file": str(f),
                    "details": data
                }
                
                experiences.append(exp)
        except Exception as e:
            print(f"Warning: Could not read {f}: {e}")
    
    return experiences

def save_experiences(experiences):
    """Speichert Erfahrungen in der Bank"""
    os.makedirs(EXP_DIR, exist_ok=True)
    
    # Nach Monat gruppieren
    by_month = {}
    for exp in experiences:
        month = exp["date"][:7]  # YYYY-MM
        if month not in by_month:
            by_month[month] = []
        by_month[month].append(exp)
    
    # Pro Monat speichern
    for month, exps in by_month.items():
        month_file = EXP_DIR / f"experience_{month}.json"
        with open(month_file, "w") as f:
            json.dump(exps, f, indent=2)
        print(f"✅ Saved {len(exps)} experiences to {month_file.name}")
    
    # Index aktualisieren
    index = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "total_experiences": len(experiences),
        "months": list(by_month.keys()),
        "by_agent": {},
        "by_outcome": {"success": 0, "failed": 0}
    }
    
    for exp in experiences:
        agent = exp["agent"]
        if agent not in index["by_agent"]:
            index["by_agent"][agent] = 0
        index["by_agent"][agent] += 1
        
        index["by_outcome"][exp["outcome"]] += 1
    
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    
    return index

def run():
    print("🧠 Experience Bank — Extracting experiences...")
    
    experiences = get_experiences()
    print(f"📊 Found {len(experiences)} experiences")
    
    if experiences:
        index = save_experiences(experiences)
        print(f"✅ Index updated: {index['total_experiences']} total")
        print(f"   Success: {index['by_outcome']['success']}")
        print(f"   Failed: {index['by_outcome']['failed']}")
    else:
        print("⚠️ No experiences found")

if __name__ == "__main__":
    run()
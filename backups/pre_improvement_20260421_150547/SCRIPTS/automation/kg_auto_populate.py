#!/usr/bin/env python3
"""
kg_auto_populate.py — Knowledge Graph Auto-Population
Orphan reconstruction + entity enhancement for KG quality.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LOG_FILE = WORKSPACE / "logs/kg_auto.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_kg():
    with open(KG_PATH, 'r') as f:
        return json.load(f)

def save_kg(kg):
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)

def find_orphans(kg):
    connected = set()
    for r in kg['relations'].values():
        connected.add(r['from'])
        connected.add(r['to'])
    return [k for k in kg['entities'].keys() if k not in connected]

def connect_orphans(kg):
    orphans = find_orphans(kg)
    if not orphans:
        log(f"✅ No orphans found")
        return 0
    
    # Add system_root if not exists
    if "system_root" not in kg['entities']:
        kg['entities']["system_root"] = {
            "type": "system",
            "name": "System Root",
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
    
    # Connect orphans
    new_id = max(int(r) for r in kg['relations'].keys()) + 1 if kg['relations'] else 0
    for orphan in orphans:
        kg['relations'][str(new_id)] = {
            "from": orphan,
            "to": "system_root",
            "type": "connects_to",
            "created_at": datetime.now().isoformat(),
            "context": "Auto-connect by kg_auto_populate"
        }
        new_id += 1
    
    log(f"Connected {len(orphans)} orphans")
    return len(orphans)

def main():
    log("=== KG Auto-Population ===")
    
    try:
        kg = load_kg()
        count = connect_orphans(kg)
        if count > 0:
            save_kg(kg)
            log(f"✅ Saved with {count} new relations")
        else:
            log("✅ KG is clean")
    except Exception as e:
        log(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

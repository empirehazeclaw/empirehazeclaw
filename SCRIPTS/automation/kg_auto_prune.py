#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — KG Auto-Prune
Automatically removes orphaned entities when orphan rate > 30%

Runs via cron or can be triggered manually.
Based on thresholds in DECISION_FRAMEWORK.md
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_FILE = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LOG_FILE = WORKSPACE / "logs" / "kg_prune.log"

ORPHAN_THRESHOLD = 0.30  # 30%
DRY_RUN = False  # Set to True for testing

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_kg():
    if not KG_FILE.exists():
        return None
    with open(KG_FILE) as f:
        return json.load(f)

def save_kg(kg):
    with open(KG_FILE, "w") as f:
        json.dump(kg, f, indent=2)

def get_connected_entities(relations):
    connected = set()
    if isinstance(relations, dict):
        for rel in relations.values():
            if rel.get("from"): connected.add(rel["from"])
            if rel.get("to"): connected.add(rel["to"])
    elif isinstance(relations, list):
        for rel in relations:
            if rel.get("source"): connected.add(rel["source"])
            if rel.get("target"): connected.add(rel["target"])
    return connected

def prune_orphans(kg, dry_run=False):
    entities = kg.get("entities", {})
    relations = kg.get("relations", {})
    
    connected = get_connected_entities(relations)
    entity_ids = set(entities.keys())
    
    orphans = entity_ids - connected
    orphan_rate = len(orphans) / len(entity_ids) if entity_ids else 0
    
    log(f"KG Status: {len(entity_ids)} entities, {len(orphans)} orphans ({orphan_rate:.1%})")
    
    if orphan_rate <= ORPHAN_THRESHOLD:
        log(f"Orphan rate {orphan_rate:.1%} <= threshold {ORPHAN_THRESHOLD:.0%} — no prune needed")
        return {"status": "skipped", "reason": "below_threshold", "orphan_rate": orphan_rate}
    
    if dry_run:
        log(f"DRY RUN: Would remove {len(orphans)} orphaned entities")
        return {"status": "dry_run", "orphans_removed": len(orphans), "orphan_rate": orphan_rate}
    
    # Remove orphaned entities
    removed = []
    for orphan_id in orphans:
        if orphan_id in entities:
            del entities[orphan_id]
            removed.append(orphan_id)
    
    # Update timestamp
    kg["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_kg(kg)
    
    log(f"PRUNED: Removed {len(removed)} orphaned entities")
    
    return {
        "status": "pruned",
        "orphans_removed": len(removed),
        "orphan_rate": orphan_rate,
        "remaining_entities": len(entities)
    }

def main():
    log("KG Auto-Prune START")
    
    kg = load_kg()
    if not kg:
        log("KG file not found", "ERROR")
        return
    
    result = prune_orphans(kg, dry_run=DRY_RUN)
    
    log(f"KG Auto-Prune END: {result}")
    print(f"✅ KG Prune: {result}")

if __name__ == "__main__":
    main()
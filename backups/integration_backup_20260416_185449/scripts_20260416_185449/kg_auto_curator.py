#!/usr/bin/env python3
"""
🧠 KG Auto-Curator — Sir HazeClaw
Weekly knowledge graph quality assurance and maintenance.

Checks:
1. Stale entities (not updated in X days)
2. Duplicate/very similar entities
3. Orphan relations (relations to deleted entities)
4. Gaps in knowledge (missing obvious connections)
5. Entity freshness scoring

Reports to:
- KG quality score
- Telegram alert only on issues
- Updates KG metadata

Usage:
    python3 kg_auto_curator.py        # Full curation
    python3 kg_auto_curator.py --status  # Quick status
    python3 kg_auto_curator.py --fix     # Auto-fix issues
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_DIR = WORKSPACE / "core_ultralight" / "memory"
KG_JSON = KG_DIR / "knowledge_graph.json"
KG_META = KG_DIR / "kg_metadata.json"
LOG_FILE = WORKSPACE / "logs/kg_curator.log"
STATE_FILE = WORKSPACE / "data/kg_curator_state.json"

# Thresholds
STALE_DAYS = 30  # Entity not updated in 30 days = stale
DUPLICATE_SIMILARITY = 0.9  # 90% similarity = duplicate
ORPHAN_THRESHOLD = 5  # More than 5 orphans = issue

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_kg() -> Dict:
    if KG_JSON.exists():
        with open(KG_JSON) as f:
            return json.load(f)
    return {"entities": [], "relations": []}

def save_kg(kg: Dict):
    with open(KG_JSON, "w") as f:
        json.dump(kg, f, indent=2)

def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_run": None, "last_score": 0, "issues_found": []}

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ============ ANALYSIS ============

def analyze_stale_entities(kg: Dict) -> List[Dict]:
    """Find entities not updated in STALE_DAYS days."""
    stale = []
    cutoff = datetime.now() - timedelta(days=STALE_DAYS)
    
    entities = kg.get("entities", {})
    if isinstance(entities, dict):
        # KG format: entities is a dict {name: data}
        for name, data in entities.items():
            if isinstance(data, dict):
                updated = data.get("updated_at", data.get("created_at", ""))
            else:
                updated = ""
            if updated:
                try:
                    updated_date = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    if updated_date < cutoff:
                        days_old = (datetime.now() - updated_date).days
                        stale.append({
                            "id": name,
                            "name": name,
                            "type": data.get("type", "unknown") if isinstance(data, dict) else "unknown",
                            "days_old": days_old
                        })
                except:
                    pass
    elif isinstance(entities, list):
        # Alternative format: entities is a list
        for entity in entities:
            if isinstance(entity, dict):
                updated = entity.get("updated_at", entity.get("created_at", ""))
            else:
                continue
            if updated:
                try:
                    updated_date = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    if updated_date < cutoff:
                        days_old = (datetime.now() - updated_date).days
                        stale.append({
                            "id": entity.get("id", "?"),
                            "name": entity.get("name", entity.get("id", "?")),
                            "type": entity.get("type", "unknown"),
                            "days_old": days_old
                        })
                except:
                    pass
    
    return stale

def analyze_duplicates(kg: Dict) -> List[Dict]:
    """Find very similar entities based on name + type."""
    duplicates = []
    entities = kg.get("entities", {})
    
    if isinstance(entities, dict):
        entity_list = [(name, data) for name, data in entities.items()]
    else:
        entity_list = [(e.get("id", "?"), e) for e in entities if isinstance(e, dict)]
    
    # Group by type
    by_type = defaultdict(list)
    for name, data in entity_list:
        etype = data.get("type", "unknown") if isinstance(data, dict) else "unknown"
        by_type[etype].append((name, data))
    
    for etype, group in by_type.items():
        # Compare names within type
        for i, (name1, data1) in enumerate(group):
            for name2, data2 in group[i+1:]:
                n1 = name1.lower().strip()
                n2 = name2.lower().strip()
                
                if not n1 or not n2:
                    continue
                
                # Simple similarity: same words
                words1 = set(n1.split())
                words2 = set(n2.split())
                
                if words1 and words2:
                    intersection = len(words1 & words2)
                    union = len(words1 | words2)
                    similarity = intersection / union if union > 0 else 0
                    
                    if similarity >= DUPLICATE_SIMILARITY:
                        duplicates.append({
                            "entity1": name1,
                            "entity2": name2,
                            "name1": name1,
                            "name2": name2,
                            "similarity": similarity,
                            "type": etype
                        })
    
    return duplicates

def analyze_orphans(kg: Dict) -> List[Dict]:
    """Find relations pointing to non-existent entities."""
    orphans = []
    entities = kg.get("entities", {})
    
    if isinstance(entities, dict):
        entity_ids = set(entities.keys())
    else:
        entity_ids = {e.get("id") for e in entities if isinstance(e, dict)}
    
    relations = kg.get("relations", []) or kg.get("relationships", [])
    
    for relation in relations:
        if isinstance(relation, dict):
            from_id = relation.get("from_id") or relation.get("from")
            to_id = relation.get("to_id") or relation.get("to")
            rel_id = relation.get("id", f"{from_id}-{to_id}")
            rel_type = relation.get("type", relation.get("relation_type", "unknown"))
        else:
            continue
        
        if from_id not in entity_ids or to_id not in entity_ids:
            orphans.append({
                "relation_id": rel_id,
                "from": from_id,
                "to": to_id,
                "type": rel_type
            })
    
    return orphans

def analyze_gaps(kg: Dict) -> List[Dict]:
    """Find obvious missing connections."""
    gaps = []
    entities = kg.get("entities", {})
    
    if isinstance(entities, dict):
        entity_list = list(entities.keys())
    else:
        entity_list = [e.get("id") for e in entities if isinstance(e, dict)]
    
    relations = kg.get("relations", []) or kg.get("relationships", [])
    
    # Find entities with many relations
    entity_relation_count = defaultdict(lambda: {"out": 0, "in": 0})
    
    for rel in relations:
        if isinstance(rel, dict):
            from_id = rel.get("from_id") or rel.get("from")
            to_id = rel.get("to_id") or rel.get("to")
            entity_relation_count[from_id]["out"] += 1
            entity_relation_count[to_id]["in"] += 1
    
    # Find "hub" entities (many relations) that aren't connected to each other
    hubs = [(eid, data["out"] + data["in"]) for eid, data in entity_relation_count.items()]
    hubs.sort(key=lambda x: x[1], reverse=True)
    hubs = [h[0] for h in hubs[:5]]  # Top 5 hubs
    
    for i, hub1 in enumerate(hubs):
        for hub2 in hubs[i+1:]:
            # Check if they're connected
            connected = any(
                (r.get("from_id") == hub1 and r.get("to_id") == hub2) or
                (r.get("from_id") == hub2 and r.get("to_id") == hub1)
                for r in relations
                if isinstance(r, dict)
            )
            
            if not connected:
                gaps.append({
                    "from": hub1,
                    "to": hub2,
                    "from_name": hub1,
                    "to_name": hub2,
                    "reason": "Hub entities not directly connected"
                })
    
    return gaps[:10]  # Limit to top 10

def calculate_quality_score(kg: Dict, stale: List, dupes: List, orphans: List, gaps: List) -> float:
    """Calculate KG quality score 0.0-1.0."""
    score = 1.0
    entities = kg.get("entities", {})
    entity_count = len(entities) if isinstance(entities, dict) else len(entities)
    relations = kg.get("relations", []) or kg.get("relationships", [])
    relation_count = len(relations)
    
    # Penalize for issues
    score -= min(len(stale) / max(entity_count, 1) * 0.3, 0.3)
    score -= min(len(dupes) / max(entity_count, 1) * 0.2, 0.2)
    score -= min(len(orphans) / max(relation_count, 1) * 0.2, 0.2)
    score -= min(len(gaps) / 10 * 0.1, 0.1)
    
    # Boost for good relation density
    expected_relations = entity_count * 1.5
    if relation_count > expected_relations:
        score += 0.1
    
    return max(0.0, min(1.0, score))

# ============ FIXES ============

def fix_duplicates(dupes: List[Dict]) -> int:
    """Merge duplicate entities."""
    if not dupes:
        return 0
    
    kg = load_kg()
    removed = 0
    entities = kg.get("entities", {})
    
    for dupe in dupes:
        e1_id = dupe["entity1"]
        e2_id = dupe["entity2"]
        
        if e1_id in entities and e2_id in entities:
            # Update relations to point to e1
            relations = kg.get("relations", []) or kg.get("relationships", [])
            for rel in relations:
                if isinstance(rel, dict):
                    if rel.get("to_id") == e2_id:
                        rel["to_id"] = e1_id
                    if rel.get("from_id") == e2_id:
                        rel["from_id"] = e1_id
            
            # Remove e2
            del entities[e2_id]
            removed += 1
            log(f"Merged duplicate: {e2_id} → {e1_id}", "ACTION")
    
    if removed > 0:
        save_kg(kg)
    return removed

def fix_orphans(orphans: List[Dict]) -> int:
    """Remove orphan relations."""
    if not orphans:
        return 0
    
    kg = load_kg()
    relations = kg.get("relations", []) or kg.get("relationships", [])
    orphan_ids = {o.get("relation_id") for o in orphans}
    
    before = len(relations)
    kg["relations"] = [r for r in relations if r.get("id") not in orphan_ids]
    removed = before - len(kg["relations"])
    
    if removed > 0:
        save_kg(kg)
        log(f"Removed {removed} orphan relations", "ACTION")
    
    return removed

def main():
    log("=== KG Auto-Curator Run ===")
    
    dry_run = "--dry-run" in sys.argv
    auto_fix = "--fix" in sys.argv
    
    kg = load_kg()
    entity_count = len(kg.get("entities", []))
    relation_count = len(kg.get("relations", []))
    
    log(f"KG size: {entity_count} entities, {relation_count} relations")
    
    # Analyze
    stale = analyze_stale_entities(kg)
    dupes = analyze_duplicates(kg)
    orphans = analyze_orphans(kg)
    gaps = analyze_gaps(kg)
    
    log(f"Issues: {len(stale)} stale, {len(dupes)} duplicates, {len(orphans)} orphans, {len(gaps)} gaps")
    
    # Score
    score = calculate_quality_score(kg, stale, dupes, orphans, gaps)
    log(f"Quality score: {score:.2f}")
    
    # Auto-fix if requested
    fixed_count = 0
    if auto_fix and not dry_run:
        fixed = fix_duplicates(dupes)
        fixed_count += fixed
        fixed = fix_orphans(orphans)
        fixed_count += fixed
        
        if fixed_count > 0:
            log(f"Auto-fixed {fixed_count} issues", "ACTION")
    
    # Save state
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    state["last_score"] = score
    state["last_counts"] = {
        "entities": entity_count,
        "relations": relation_count,
        "stale": len(stale),
        "duplicates": len(dupes),
        "orphans": len(orphans),
        "gaps": len(gaps)
    }
    save_state(state)
    
    # Alert if issues
    if stale or dupes or orphans or gaps:
        if score < 0.7:
            log(f"KG QUALITY WARNING: score={score:.2f} | stale={len(stale)} dupes={len(dupes)} orphans={len(orphans)} gaps={len(gaps)}", "WARN")
    
    return score

if __name__ == "__main__":
    main()

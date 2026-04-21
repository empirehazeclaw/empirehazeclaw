#!/usr/bin/env python3
"""
Learning Loop → KG Sync
========================
Bridges Learning Loop outputs to the central Knowledge Graph.
Reads patterns and improvements, creates KG entities and relations.

Usage:
  python3 learning_to_kg_sync.py --dry-run
  python3 learning_to_kg_sync.py --apply

Phase 2 of System Integration Plan
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LEARNING_DIR = WORKSPACE / "data/learning_loop"
STATE_FILE = WORKSPACE / "data/learning_loop/kg_sync_state.json"

def load_kg() -> dict:
    with open(KG_PATH) as f:
        return json.load(f)

def save_kg(kg: dict):
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"synced_patterns": [], "synced_improvements": [], "last_sync": None}

def save_state(state: dict):
    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_patterns() -> List[dict]:
    patterns_file = LEARNING_DIR / "patterns.json"
    if not patterns_file.exists():
        return []
    with open(patterns_file) as f:
        data = json.load(f)
    return data.get("patterns", [])

def load_improvements() -> List[dict]:
    impr_file = LEARNING_DIR / "improvements.json"
    if not impr_file.exists():
        return []
    with open(impr_file) as f:
        data = json.load(f)
    return data.get("improvements", [])

def pattern_to_entity_id(pattern_id: str) -> str:
    return f"LearningPattern_{pattern_id}"

def improvement_to_entity_id(improvement: dict) -> str:
    ts = improvement.get("timestamp", "").replace(":", "-").replace(".", "-")
    title = improvement.get("title", "unknown")[:30].replace(" ", "-").replace("[", "").replace("]", "")
    return f"Improvement_{ts}_{title}"

def entity_id_exists(kg: dict, entity_id: str) -> bool:
    """Check if entity_id exists in dict-based KG."""
    return entity_id in kg.get("entities", {})

def next_rel_id(kg: dict) -> str:
    """Get next available relation ID for dict-based KG."""
    rels = kg.get("relations", {})
    if isinstance(rels, dict):
        # Dict-based KG: keys are string numbers
        existing = [int(k) for k in rels.keys() if str(k).isdigit()]
    else:
        # List-based KG fallback
        existing = [int(r.get("id", 0)) for r in rels if str(r.get("id", "")).isdigit()]
    return str(max(existing + [0]) + 1)

def add_pattern_to_kg(kg: dict, pattern: dict) -> bool:
    """Add a learning pattern as KG entity. Returns True if added."""
    pid = pattern.get("id")
    if not pid:
        return False
    
    entity_id = pattern_to_entity_id(pid)
    if entity_id_exists(kg, entity_id):
        return False  # Already exists
    
    # Create entity
    entity = {
        "id": entity_id,
        "type": "LearningPattern",
        "name": pid,
        "description": pattern.get("description", ""),
        "error_type": pattern.get("error_type"),
        "solution": pattern.get("solution"),
        "confidence": pattern.get("confidence", 0),
        "validated": pattern.get("validated", False),
        "source": pattern.get("source", "learning_loop"),
        "first_seen": pattern.get("first_seen"),
        "last_validated": pattern.get("last_validated"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    kg["entities"][entity_id] = entity
    
    # Create relation to Learning Loop
    rel_id = next_rel_id(kg)
    rels = kg.get("relations", {})
    if isinstance(rels, dict):
        rels[rel_id] = {
            "id": int(rel_id),
            "from": entity_id,
            "to": "Learning-Loop",
            "type": "part_of",
            "weight": 0.9,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    else:
        rels.append({
            "id": int(rel_id),
            "from": entity_id,
            "to": "Learning-Loop",
            "type": "part_of",
            "weight": 0.9,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    return True

def add_improvement_to_kg(kg: dict, improvement: dict) -> bool:
    """Add an improvement as KG entity. Returns True if added."""
    title = improvement.get("title")
    if not title:
        return False
    
    entity_id = improvement_to_entity_id(improvement)
    if entity_id_exists(kg, entity_id):
        return False  # Already exists
    
    validation = improvement.get("validation_details", {})
    tests = validation.get("tests", [])
    passed = validation.get("passed", False)
    
    # Create entity
    entity = {
        "id": entity_id,
        "type": "Improvement",
        "name": title[:100],
        "description": title,
        "validated": passed,
        "timestamp": improvement.get("timestamp"),
        "test_count": len(tests),
        "tests_passed": sum(1 for t in tests if t.get("passed")),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    kg["entities"][entity_id] = entity
    
    # Create relation to Learning Loop
    rel_id = next_rel_id(kg)
    rels = kg.get("relations", {})
    if isinstance(rels, dict):
        rels[rel_id] = {
            "id": int(rel_id),
            "from": "Learning-Loop",
            "to": entity_id,
            "type": "created",
            "weight": 0.9,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    else:
        rels.append({
            "id": int(rel_id),
            "from": "Learning-Loop",
            "to": entity_id,
            "type": "created",
            "weight": 0.9,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # If validated, link to the pattern it validates
    if passed:
        rel_id2 = next_rel_id(kg)
        if isinstance(rels, dict):
            rels[rel_id2] = {
                "id": int(rel_id2),
                "from": entity_id,
                "to": "Learning-Loop",
                "type": "validates",
                "weight": 0.8,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            rels.append({
                "id": int(rel_id2),
                "from": entity_id,
                "to": "Learning-Loop",
                "type": "validates",
                "weight": 0.8,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
    
    return True

def sync_learning_to_kg(dry_run: bool = True) -> dict:
    """Main sync function."""
    state = load_state()
    synced_patterns: Set[str] = set(state.get("synced_patterns", []))
    synced_improvements: Set[str] = set(state.get("synced_improvements", []))
    
    patterns = load_patterns()
    improvements = load_improvements()
    
    stats = {"patterns_new": 0, "improvements_new": 0, "relations_added": 0}
    
    if dry_run:
        print(f"[DRY RUN] Would sync:")
    else:
        print(f"Syncing Learning Loop → KG...")
        kg = load_kg()
    
    # Sync new patterns
    for pattern in patterns:
        pid = pattern.get("id")
        if pid and pid not in synced_patterns:
            if dry_run:
                print(f"  + Pattern: {pid} (confidence={pattern.get('confidence', 0):.2f})")
            else:
                if add_pattern_to_kg(kg, pattern):
                    synced_patterns.add(pid)
                    stats["patterns_new"] += 1
                    stats["relations_added"] += 1
    
    # Sync new improvements
    for improvement in improvements:
        title = improvement.get("title")
        key = improvement.get("timestamp", title)
        if title and key not in synced_improvements:
            if dry_run:
                validated = improvement.get("validation_details", {}).get("passed", False)
                print(f"  + Improvement: {title[:60]}... (validated={validated})")
            else:
                if add_improvement_to_kg(kg, improvement):
                    synced_improvements.add(key)
                    stats["improvements_new"] += 1
                    stats["relations_added"] += 1
    
    if not dry_run:
        save_kg(kg)
        state["synced_patterns"] = list(synced_patterns)
        state["synced_improvements"] = list(synced_improvements)
        save_state(state)
        print(f"✅ Synced: {stats['patterns_new']} patterns, {stats['improvements_new']} improvements, {stats['relations_added']} relations")
    
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Learning Loop → KG Sync")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    args = parser.parse_args()
    
    dry_run = not args.apply
    sync_learning_to_kg(dry_run=dry_run)
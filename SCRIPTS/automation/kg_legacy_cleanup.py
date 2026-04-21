#!/usr/bin/env python3
"""
KG Legacy Cleanup — Phase 4 of Improvement Plan
================================================
Cleans up:
1. Orphan entities (entities with no relations)
2. Stale entities (not accessed in >30 days)
3. Legacy arxiv entities (external source no longer relevant)

Run manually or via cron.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
BACKUP_DIR = WORKSPACE / "backups/kg_cleanup"
LOG_FILE = WORKSPACE / "logs/kg_cleanup.log"

ORPHAN_THRESHOLD = 0.60  # Prune if >60% orphans
STALE_DAYS = 30  # Entities not accessed in 30 days


def log(msg: str, level: str = "INFO"):
    """Log to file and print."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_kg():
    """Load knowledge graph."""
    with open(KG_PATH) as f:
        return json.load(f)


def save_kg(kg):
    """Save knowledge graph."""
    with open(KG_PATH, "w") as f:
        json.dump(kg, f, indent=2)


def backup_kg(kg, reason: str):
    """Create backup before modifications."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"kg_before_{reason}_{timestamp}.json"
    backup_file.write_text(json.dumps(kg, indent=2))
    log(f"Backup created: {backup_file.name}")
    return backup_file


def get_linked_entities(kg) -> set:
    """Get set of all entity IDs that have relations."""
    linked = set()
    
    # Top-level relations (dict format)
    relations = kg.get("relations", {})
    if isinstance(relations, dict):
        for rel in relations.values():
            if isinstance(rel, dict):
                if rel.get("from"): linked.add(rel["from"])
                if rel.get("to"): linked.add(rel["to"])
    elif isinstance(relations, list):
        for rel in relations:
            if rel.get("source"): linked.add(rel["source"])
            if rel.get("target"): linked.add(rel["target"])
    
    # Embedded relations in entities
    entities = kg.get("entities", {})
    for eid, entity in entities.items():
        for rel in entity.get("relations", []):
            if isinstance(rel, dict):
                if rel.get("target"): linked.add(rel["target"])
                if rel.get("source"): linked.add(rel["source"])
            elif isinstance(rel, str):
                linked.add(rel)
    
    return linked


def find_orphans(kg) -> list:
    """Find all orphan entities."""
    entities = kg.get("entities", {})
    linked = get_linked_entities(kg)
    all_ids = set(entities.keys())
    orphans = all_ids - linked
    return list(orphans)


def find_stale(kg, days: int = STALE_DAYS) -> list:
    """Find entities not accessed in given days."""
    entities = kg.get("entities", {})
    cutoff = datetime.now() - timedelta(days=days)
    stale = []
    
    for eid, entity in entities.items():
        last_access = entity.get("last_access", entity.get("last_updated", ""))
        if last_access:
            try:
                access_date = datetime.fromisoformat(last_access)
                if access_date < cutoff:
                    stale.append(eid)
            except:
                pass
    
    return stale


def find_legacy_entities(kg) -> dict:
    """Find legacy entities that should be removed."""
    entities = kg.get("entities", {})
    legacy = {
        "arxiv": [],      # arxiv source entities
        "paper": [],      # paper-related entities
        "external": [],   # entities with external source markers
    }
    
    for eid, entity in entities.items():
        # Check entity type/name for arxiv indicators
        name = entity.get("name", "").lower()
        entity_type = entity.get("type", "").lower()
        source = entity.get("source", "").lower()
        
        if "arxiv" in name or "arxiv" in entity_type or "arxiv" in source:
            legacy["arxiv"].append(eid)
        elif "paper" in name or "paper" in entity_type or "paper" in source:
            legacy["paper"].append(eid)
        elif entity_type == "external" or "external_source" in entity:
            legacy["external"].append(eid)
    
    return legacy


def prune_entities(kg, to_remove: list, reason: str) -> dict:
    """Remove entities and return stats."""
    if not to_remove:
        return {"removed": 0, "reason": reason, "skipped": 0}
    
    entities = kg.get("entities", {})
    original_count = len(entities)
    
    # Backup before modification
    backup_kg(kg, reason)
    
    # Remove entities
    removed = []
    for eid in to_remove:
        if eid in entities:
            del entities[eid]
            removed.append(eid)
    
    # Update timestamp
    kg["last_updated"] = datetime.now().isoformat()
    save_kg(kg)
    
    return {
        "removed": len(removed),
        "reason": reason,
        "original_count": original_count,
        "remaining": len(entities)
    }


def run_cleanup(dry_run: bool = True, aggressive: bool = False) -> dict:
    """Run full cleanup cycle."""
    log("KG Legacy Cleanup: Starting")
    
    kg = load_kg()
    entities = kg.get("entities", {})
    
    stats = {
        "original_count": len(entities),
        "orphans_found": 0,
        "stale_found": 0,
        "legacy_found": 0,
        "removed": 0,
        "dry_run": dry_run
    }
    
    # 1. Find and remove orphans if threshold exceeded
    orphans = find_orphans(kg)
    orphan_rate = len(orphans) / len(entities) if entities else 0
    stats["orphans_found"] = len(orphans)
    stats["orphan_rate"] = orphan_rate
    
    log(f"Orphan analysis: {len(orphans)} orphans ({orphan_rate:.1%})")
    
    if orphan_rate > ORPHAN_THRESHOLD:
        log(f"Orphan rate {orphan_rate:.1%} > threshold {ORPHAN_THRESHOLD:.0%}")
        if not dry_run:
            result = prune_entities(kg, orphans, "orphan_cleanup")
            stats["removed"] += result["removed"]
            log(f"Removed {result['removed']} orphan entities")
        else:
            stats["would_remove_orphans"] = len(orphans)
            log(f"DRY RUN: Would remove {len(orphans)} orphans")
    
    # 2. Find stale entities
    stale = find_stale(kg)
    stats["stale_found"] = len(stale)
    log(f"Stale entities (>30 days): {len(stale)}")
    
    if aggressive and stale and not dry_run:
        result = prune_entities(kg, stale, "stale_cleanup")
        stats["removed"] += result["removed"]
        log(f"Removed {result['removed']} stale entities")
    
    # 3. Find legacy entities
    legacy = find_legacy_entities(kg)
    total_legacy = sum(len(v) for v in legacy.values())
    stats["legacy_found"] = total_legacy
    stats["legacy_breakdown"] = {k: len(v) for k, v in legacy.items()}
    log(f"Legacy entities: {total_legacy} ({legacy['arxiv']} arxiv, {legacy['paper']} papers)")
    
    if aggressive and total_legacy > 0 and not dry_run:
        all_legacy = legacy["arxiv"] + legacy["paper"] + legacy["external"]
        # Deduplicate
        all_legacy = list(set(all_legacy))
        result = prune_entities(kg, all_legacy, "legacy_cleanup")
        stats["removed"] += result["removed"]
        log(f"Removed {result['removed']} legacy entities")
    
    # Summary
    remaining = len(kg.get("entities", {}))
    stats["remaining_count"] = remaining
    stats["final_orphan_rate"] = len(find_orphans(kg)) / remaining if remaining else 0
    
    log(f"Cleanup complete: {stats}")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KG Legacy Cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    parser.add_argument("--aggressive", action="store_true", help="Also remove stale/legacy entities")
    parser.add_argument("--remove-orphans", action="store_true", help="Remove orphans regardless of threshold")
    
    args = parser.parse_args()
    
    print(f"KG Legacy Cleanup")
    print(f"  Dry run: {args.dry_run or not args.remove_orphans}")
    print(f"  Aggressive: {args.aggressive}")
    print()
    
    if args.remove_orphans or args.aggressive:
        results = run_cleanup(dry_run=args.dry_run, aggressive=args.aggressive)
    else:
        # Just show analysis
        kg = load_kg()
        entities = kg.get("entities", {})
        orphans = find_orphans(kg)
        orphan_rate = len(orphans) / len(entities) if entities else 0
        stale = find_stale(kg)
        legacy = find_legacy_entities(kg)
        
        print(f"KG Analysis:")
        print(f"  Total entities: {len(entities)}")
        print(f"  Orphan entities: {len(orphans)} ({orphan_rate:.1%})")
        print(f"  Stale entities (>30 days): {len(stale)}")
        print(f"  Legacy entities: {sum(len(v) for v in legacy.values())}")
        print(f"    - arxiv: {len(legacy['arxiv'])}")
        print(f"    - paper: {len(legacy['paper'])}")
        print(f"    - external: {len(legacy['external'])}")
        print()
        print(f"Threshold for auto-prune: {ORPHAN_THRESHOLD:.0%}")
        print(f"Current orphan rate: {orphan_rate:.1%}")
        
        if orphan_rate > ORPHAN_THRESHOLD:
            print(f"\n⚠️  Orphan rate exceeds threshold!")
            print(f"Run with --remove-orphans to clean up")
        else:
            print(f"\n✅ Orphan rate within threshold")
    
    print("\nDone.")
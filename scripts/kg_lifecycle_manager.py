#!/usr/bin/env python3
"""
kg_lifecycle_manager.py - Manage Knowledge Graph growth and quality
Sir HazeClaw - 2026-04-11

Usage:
    python3 kg_lifecycle_manager.py          # Show KG stats
    python3 kg_lifecycle_manager.py --dedup  # Deduplicate entities
    python3 kg_lifecycle_manager.py --age    # Mark stale entities
    python3 kg_lifecycle_manager.py --enforce # Enforce max entities limit
    python3 kg_lifecycle_manager.py --all     # Run all maintenance
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

# Configuration
KG_PATH = Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json")
MAX_ENTITIES = 500
STALE_THRESHOLD_DAYS = 30
DEDUP_THRESHOLD = 0.85


def load_kg() -> Dict:
    """Load knowledge graph."""
    if KG_PATH.exists():
        with open(KG_PATH) as f:
            return json.load(f)
    return {"entities": {}, "relations": []}


def save_kg(kg: Dict):
    """Save knowledge graph."""
    with open(KG_PATH, "w") as f:
        json.dump(kg, f, indent=2)


def get_entity_content(entity_id: str, entity_data: Dict) -> str:
    """Get text content of an entity for comparison."""
    facts = entity_data.get("facts", [])
    content = " ".join([
        f.get("content", "") for f in facts
    ])
    return f"{entity_id} {content}".lower()


def jaccard_similarity(a: str, b: str) -> float:
    """Calculate Jaccard similarity between two texts."""
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def dedupe_kg(kg: Dict) -> Dict:
    """Remove duplicate entities based on content similarity."""
    entities = kg.get("entities", {})
    unique_entities = {}
    removed = []
    seen_contents: List[str] = []
    
    for entity_id, entity_data in entities.items():
        content = get_entity_content(entity_id, entity_data)
        
        is_duplicate = False
        best_match = None
        best_similarity = 0
        
        for seen_content in seen_contents:
            similarity = jaccard_similarity(content, seen_content)
            if similarity > DEDUP_THRESHOLD and similarity > best_similarity:
                best_match = seen_content
                best_similarity = similarity
                is_duplicate = True
        
        if not is_duplicate:
            unique_entities[entity_id] = entity_data
            seen_contents.append(content)
        else:
            removed.append((entity_id, best_similarity))
    
    kg["entities"] = unique_entities
    return kg, removed


def age_kg(kg: Dict) -> Dict:
    """Mark stale entities (not accessed in 30 days)."""
    entities = kg.get("entities", {})
    now = datetime.now().timestamp()
    stale_threshold = STALE_THRESHOLD_DAYS * 86400
    
    stale_count = 0
    for entity_id, entity_data in entities.items():
        last_accessed = entity_data.get("last_accessed", now)
        age_days = (now - last_accessed) / 86400
        
        if age_days > STALE_THRESHOLD_DAYS:
            entity_data["status"] = "stale"
            entity_data["stale_since"] = datetime.now().isoformat()
            stale_count += 1
    
    return kg, stale_count


def enforce_limit(kg: Dict) -> Dict:
    """Enforce max entities limit by removing oldest stale entities first."""
    entities = kg.get("entities", {})
    
    if len(entities) <= MAX_ENTITIES:
        return kg, 0
    
    # Sort entities: stale first, then by last_accessed
    sorted_entities = sorted(
        entities.items(),
        key=lambda x: (
            x[1].get("status") == "active",  # stale first (False < True)
            x[1].get("last_accessed", 0)
        )
    )
    
    # Remove oldest until under limit
    removed_count = 0
    entities_to_keep = dict(sorted_entities[:MAX_ENTITIES])
    
    removed_count = len(entities) - len(entities_to_keep)
    kg["entities"] = entities_to_keep
    
    return kg, removed_count


def get_stats(kg: Dict) -> Dict:
    """Get KG statistics."""
    entities = kg.get("entities", {})
    relations = kg.get("relations", [])
    
    stale_count = sum(1 for e in entities.values() if e.get("status") == "stale")
    
    return {
        "total_entities": len(entities),
        "max_entities": MAX_ENTITIES,
        "total_relations": len(relations),
        "stale_entities": stale_count,
        "active_entities": len(entities) - stale_count,
        "utilization": len(entities) / MAX_ENTITIES if MAX_ENTITIES > 0 else 0
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="KG Lifecycle Manager")
    parser.add_argument("--dedup", action="store_true", help="Deduplicate entities")
    parser.add_argument("--age", action="store_true", help="Mark stale entities")
    parser.add_argument("--enforce", action="store_true", help="Enforce max entities limit")
    parser.add_argument("--all", action="store_true", help="Run all maintenance")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    args = parser.parse_args()
    
    kg = load_kg()
    
    print("=" * 50)
    print("🦞 KG LIFECYCLE MANAGER")
    print("=" * 50)
    
    # Always show stats
    stats = get_stats(kg)
    print(f"\n📊 Current Statistics:")
    print(f"   Total Entities:    {stats['total_entities']}/{stats['max_entities']}")
    print(f"   Active Entities:   {stats['active_entities']}")
    print(f"   Stale Entities:    {stats['stale_entities']}")
    print(f"   Relations:         {stats['total_relations']}")
    print(f"   Utilization:       {stats['utilization']:.1%}")
    
    if args.stats:
        return
    
    if args.all:
        args.dedup = args.age = args.enforce = True
    
    total_removed = 0
    
    if args.dedup:
        print("\n🔄 Deduplicating entities...")
        kg, removed = dedupe_kg(kg)
        print(f"   Removed {len(removed)} duplicates")
        for entity_id, sim in removed[:5]:
            print(f"      - {entity_id[:30]}... ({sim:.0%} similar)")
        total_removed += len(removed)
    
    if args.age:
        print("\n🔄 Marking stale entities...")
        kg, stale_count = age_kg(kg)
        print(f"   Marked {stale_count} entities as stale")
    
    if args.enforce:
        print("\n🔄 Enforcing entity limit...")
        kg, removed_count = enforce_limit(kg)
        print(f"   Removed {removed_count} entities to enforce limit")
        total_removed += removed_count
    
    if args.dedup or args.age or args.enforce:
        save_kg(kg)
        print(f"\n✅ Total entities removed: {total_removed}")
        print(f"   Entities remaining: {len(kg.get('entities', {}))}")


if __name__ == "__main__":
    main()

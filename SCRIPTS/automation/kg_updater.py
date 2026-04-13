#!/usr/bin/env python3
"""
Sir HazeClaw Knowledge Graph Manager
====================================
Consolidates: kg_updater.py + kg_enhancer.py + kg_lifecycle_manager.py + kg_relation_cleaner.py

Modes:
  add               Add entity to KG
  list              List all entities
  stats             Show KG statistics
  search <query>    Search entities
  add-relation      Add relation between entities
  
  enhance           Bulk add entries (from kg_enhancer)
  lifecycle         KG maintenance (dedup, age, enforce)
  clean-relations   Clean low-quality relations

Usage:
  python3 kg_updater.py stats
  python3 kg_updater.py add --type skill --name "New Skill" --content "..."
  python3 kg_updater.py enhance
  python3 kg_updater.py lifecycle --all
  python3 kg_updater.py clean-relations --dry-run
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

KG_PATH = Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json")

# ============================================================
# CORE FUNCTIONS (from kg_updater.py)
# ============================================================

def load_kg():
    """Lädt den Knowledge Graph."""
    if not KG_PATH.exists():
        print(f"❌ KG nicht gefunden: {KG_PATH}")
        sys.exit(1)
    
    with open(KG_PATH) as f:
        return json.load(f)

def save_kg(kg):
    """Speichert den Knowledge Graph."""
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)

def init_kg():
    """Initialisiert KG falls nicht vorhanden."""
    if not KG_PATH.exists():
        kg = {"entities": {}, "relations": [], "last_updated": datetime.now().isoformat()}
        save_kg(kg)
        print(f"✅ KG initialisiert: {KG_PATH}")

def add_entity(entity_type: str, name: str, content: str, tags: List[str] = None, priority: str = "MEDIUM"):
    """Fügt Entity zum KG hinzu."""
    kg = load_kg()
    entities = kg.get('entities', {})
    
    if name in entities:
        print(f"⚠️ Entity existiert bereits: {name}")
        return
    
    entity = {
        "type": entity_type,
        "facts": [{"content": content, "source": "user", "confidence": 0.9}],
        "tags": tags or [],
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "last_accessed": datetime.now().isoformat(),
        "access_count": 0,
        "status": "active"
    }
    
    entities[name] = entity
    kg['entities'] = entities
    kg['last_updated'] = datetime.now().isoformat()
    
    save_kg(kg)
    print(f"✅ Entity hinzugefügt: {name} ({entity_type})")

def list_entities():
    """Listet alle Entities auf."""
    kg = load_kg()
    entities = kg.get('entities', {})
    
    if not entities:
        print("📭 KG ist leer")
        return
    
    print(f"📊 {len(entities)} Entities:")
    for name, data in sorted(entities.items()):
        entity_type = data.get('type', 'unknown')
        status = data.get('status', 'active')
        facts_count = len(data.get('facts', []))
        print(f"  • {name} [{entity_type}] ({status}) — {facts_count} facts")

def stats():
    """Zeigt KG Statistiken."""
    kg = load_kg()
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    
    print("=" * 50)
    print("📊 KG Statistics")
    print("=" * 50)
    print(f"  Entities: {len(entities)}")
    print(f"  Relations: {len(relations)}")
    
    # Type breakdown
    types = defaultdict(int)
    for e in entities.values():
        types[e.get('type', 'unknown')] += 1
    
    print("\n  By Type:")
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"    {t}: {count}")
    
    # Status breakdown
    statuses = defaultdict(int)
    for e in entities.values():
        statuses[e.get('status', 'active')] += 1
    
    print("\n  By Status:")
    for s, count in sorted(statuses.items()):
        print(f"    {s}: {count}")

def search(query: str):
    """Sucht Entities."""
    kg = load_kg()
    entities = kg.get('entities', {})
    
    query_lower = query.lower()
    results = []
    
    for name, data in entities.items():
        if query_lower in name.lower():
            results.append((name, data, "name match"))
        else:
            facts = data.get('facts', [])
            for fact in facts:
                if query_lower in fact.get('content', '').lower():
                    results.append((name, data, f"fact: {fact.get('content', '')[:50]}"))
                    break
    
    if results:
        print(f"🔍 {len(results)} results for '{query}':")
        for name, data, reason in results[:10]:
            print(f"  • {name} [{data.get('type', '?')}] — {reason}")
    else:
        print(f"🔍 No results for '{query}'")

def add_relation(from_entity: str, to_entity: str, relation_type: str, weight: float = 0.7):
    """Fügt Relation hinzu."""
    kg = load_kg()
    relations = kg.get('relations', [])
    
    # Check if entity exists
    entities = kg.get('entities', {})
    if from_entity not in entities:
        print(f"⚠️ Entity nicht gefunden: {from_entity}")
        return
    if to_entity not in entities:
        print(f"⚠️ Entity nicht gefunden: {to_entity}")
        return
    
    # Check if relation exists
    for rel in relations:
        if rel.get('from') == from_entity and rel.get('to') == to_entity:
            print(f"⚠️ Relation existiert bereits: {from_entity} → {to_entity}")
            return
    
    relation = {
        "from": from_entity,
        "to": to_entity,
        "type": relation_type,
        "weight": weight,
        "created_at": datetime.now().isoformat()
    }
    
    relations.append(relation)
    kg['relations'] = relations
    kg['last_updated'] = datetime.now().isoformat()
    
    save_kg(kg)
    print(f"✅ Relation hinzugefügt: {from_entity} --{relation_type}--> {to_entity}")

# ============================================================
# ENHANCE FUNCTIONS (from kg_enhancer.py)
# ============================================================

# Predefined entities and relations for bulk import
NEW_ENTITIES = {
    "Sir-HazeClaw-Self-Improvement": {
        "type": "pattern",
        "facts": [
            {"content": "Meta-Improvement Pattern: Analyze errors → Generate hypotheses → Validate → Deploy", "source": "kg_enhancer"},
            {"content": "Self-Play GVU Pattern: Generate → Validate → Update based on real errors", "source": "kg_enhancer"}
        ],
        "tags": ["self-improvement", "pattern", "meta"],
        "priority": "HIGH"
    },
}

NEW_RELATIONS = [
    {"from": "Sir-HazeClaw", "to": "Self-Improvement-Patterns", "type": "follows"},
    {"from": "Sir-HazeClaw", "to": "Good-Patterns-SirHazeClaw", "type": "follows"},
    {"from": "Self-Evaluation", "to": "Self-Improvement-Patterns", "type": "tracks"},
]

def enhance_run():
    """Bulk add entries to KG."""
    kg = load_kg()
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    
    added_entities = 0
    added_relations = 0
    
    # Add entities
    for entity_name, entity_data in NEW_ENTITIES.items():
        if entity_name not in entities:
            entities[entity_name] = entity_data
            added_entities += 1
        else:
            # Update facts
            existing = entities[entity_name]
            if 'facts' not in existing:
                existing['facts'] = []
            existing_facts = set(f['content'] for f in existing.get('facts', []))
            for fact in entity_data.get('facts', []):
                if fact['content'] not in existing_facts:
                    existing['facts'].append(fact)
                    added_entities += 1
    
    # Add relations
    existing_relations = set((r['from'], r['to'], r['type']) for r in relations)
    for rel in NEW_RELATIONS:
        if (rel['from'], rel['to'], rel['type']) not in existing_relations:
            relations.append(rel)
            added_relations += 1
    
    kg['entities'] = entities
    kg['relations'] = relations
    kg['last_updated'] = datetime.now().isoformat()
    save_kg(kg)
    
    print(f"✅ Enhanced KG: {added_entities} entity updates, {added_relations} new relations")
    return added_entities, added_relations

# ============================================================
# LIFECYCLE FUNCTIONS (from kg_lifecycle_manager.py)
# ============================================================

MAX_ENTITIES = 500

def dedupe_kg(kg: Dict) -> Tuple[Dict, List]:
    """Deduplicate similar entities using Jaccard similarity."""
    entities = kg.get("entities", {})
    entity_ids = list(entities.keys())
    removed = []
    
    for i, id1 in enumerate(entity_ids):
        if id1 not in entities:
            continue
        
        e1_content = " ".join(f.get("content", "") for f in entities[id1].get("facts", []))
        
        for id2 in entity_ids[i+1:]:
            if id2 not in entities:
                continue
            
            e2_content = " ".join(f.get("content", "") for f in entities[id2].get("facts", []))
            
            if jaccard_similarity(e1_content, e2_content) > 0.8:
                # Keep the one with more facts/access
                e1_score = len(entities[id1].get("facts", [])) + entities[id1].get("access_count", 0)
                e2_score = len(entities[id2].get("facts", [])) + entities[id2].get("access_count", 0)
                
                to_remove = id2 if e1_score >= e2_score else id1
                removed.append((to_remove, id1 if to_remove == id2 else id2))
                del entities[to_remove]
    
    kg["entities"] = entities
    return kg, removed

def jaccard_similarity(a: str, b: str) -> float:
    """Calculate Jaccard similarity between two strings."""
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words or not b_words:
        return 0.0
    intersection = len(a_words & b_words)
    union = len(a_words | b_words)
    return intersection / union if union > 0 else 0.0

def age_kg(kg: Dict) -> Tuple[Dict, int]:
    """Mark stale entities (not accessed in 30 days)."""
    entities = kg.get("entities", {})
    stale_count = 0
    
    cutoff = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30 days ago
    
    for entity_id, entity_data in entities.items():
        last_accessed_ts = entity_data.get("last_accessed")
        if last_accessed_ts:
            try:
                last_dt = datetime.fromisoformat(last_accessed_ts.replace("Z", "+00:00"))
                if last_dt.timestamp() < cutoff and entity_data.get("status") != "stale":
                    entity_data["status"] = "stale"
                    stale_count += 1
            except (ValueError, TypeError):
                # datetime parsing failed - skip this entity
                pass
    
    kg["entities"] = entities
    return kg, stale_count

def enforce_limit(kg: Dict) -> Tuple[Dict, int]:
    """Enforce max entities limit by removing lowest priority stale entities."""
    entities = kg.get("entities", {})
    removed_count = 0
    
    if len(entities) <= MAX_ENTITIES:
        return kg, 0
    
    # Find stale entities to remove
    stale = [(eid, edata) for eid, edata in entities.items() if edata.get("status") == "stale"]
    stale.sort(key=lambda x: x[1].get("priority", "LOW"))
    
    while len(entities) > MAX_ENTITIES and stale:
        eid, _ = stale.pop(0)
        del entities[eid]
        removed_count += 1
    
    kg["entities"] = entities
    return kg, removed_count

def lifecycle_stats(kg: Dict) -> Dict:
    """Get lifecycle statistics."""
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

def lifecycle_run(args):
    """Run lifecycle management."""
    kg = load_kg()
    
    print("=" * 50)
    print("🦞 KG LIFECYCLE MANAGER")
    print("=" * 50)
    
    # Always show stats
    stats_dict = lifecycle_stats(kg)
    print(f"\n📊 Current Statistics:")
    print(f"   Total Entities:    {stats_dict['total_entities']}/{stats_dict['max_entities']}")
    print(f"   Active Entities:   {stats_dict['active_entities']}")
    print(f"   Stale Entities:    {stats_dict['stale_entities']}")
    print(f"   Relations:         {stats_dict['total_relations']}")
    print(f"   Utilization:       {stats_dict['utilization']:.1%}")
    
    if args.stats:
        return
    
    total_removed = 0
    
    if args.dedup:
        print("\n🔄 Deduplicating entities...")
        kg, removed = dedupe_kg(kg)
        print(f"   Removed {len(removed)} duplicates")
        for entity_id1, entity_id2 in removed[:5]:
            print(f"      - {entity_id1[:30]}... similar to {entity_id2[:30]}...")
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

# ============================================================
# CLEAN RELATIONS (from kg_relation_cleaner.py)
# ============================================================

def analyze_relations(kg: Dict) -> Dict:
    """Analyze relations by type."""
    relations = kg.get("relations", [])
    type_counts = defaultdict(int)
    
    for rel in relations:
        rel_type = rel.get("type", "unknown")
        type_counts[rel_type] += 1
    
    print("\n📊 Relation Type Analysis:")
    for rel_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(relations) if relations else 0
        print(f"   {rel_type}: {count} ({pct:.1f}%)")
    
    return dict(type_counts)

def clean_relations(kg: Dict, dry_run: bool = True, aggressive: bool = False) -> List:
    """Clean low-quality relations."""
    relations = kg.get("relations", [])
    LOW_QUALITY_TYPES = {"shares_category"} if not aggressive else {"shares_category", "related_to"}
    
    total_before = len(relations)
    
    if aggressive:
        relations_to_keep = [r for r in relations if r.get("type") not in LOW_QUALITY_TYPES]
    else:
        # Keep high-weight or relations with good types
        relations_to_keep = [r for r in relations 
                           if r.get("type") not in LOW_QUALITY_TYPES 
                           or r.get("weight", 0) >= 0.8]
    
    removed = total_before - len(relations_to_keep)
    print(f"\n🧹 Relation Cleaner:")
    print(f"   Before: {total_before}")
    print(f"   After:  {len(relations_to_keep)}")
    print(f"   Removed: {removed} relations")
    print(f"   Reduction: {100*removed/total_before:.1f}%")
    
    if dry_run:
        print("\n⚠️  DRY RUN - No changes made. Use --execute to apply.")
    else:
        print("\n✅ Applying changes...")
        kg['relations'] = relations_to_keep
        save_kg(kg)
    
    return relations_to_keep if dry_run else kg

def clean_relations_run(args):
    """Run relation cleaner."""
    kg = load_kg()
    
    print("=" * 60)
    print("🧹 KG RELATION CLEANER")
    print("=" * 60)
    
    type_counts = analyze_relations(kg)
    
    if args.analyze_only:
        return
    
    if args.dry_run or not args.execute:
        clean_relations(kg, dry_run=True, aggressive=args.aggressive)
        if args.execute:
            print("\n❌ Use --execute to apply changes")
    else:
        clean_relations(kg, dry_run=False, aggressive=args.aggressive)

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Sir HazeClaw Knowledge Graph Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  python3 kg_updater.py stats
  python3 kg_updater.py list
  python3 kg_updater.py add --type skill --name "Name" --content "..."
  python3 kg_updater.py search "query"
  python3 kg_updater.py add-relation --from A --to B --type relates_to
  python3 kg_updater.py enhance
  python3 kg_updater.py lifecycle --all
  python3 kg_updater.py clean-relations --dry-run
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # add command
    add_parser = subparsers.add_parser('add', help='Add entity')
    add_parser.add_argument('--type', required=True, help='Entity type')
    add_parser.add_argument('--name', required=True, help='Entity name')
    add_parser.add_argument('--content', required=True, help='Entity content')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    add_parser.add_argument('--priority', default='MEDIUM', help='Priority')
    
    # add-relation command
    rel_parser = subparsers.add_parser('add-relation', help='Add relation')
    rel_parser.add_argument('--from', required=True, dest='from_e', help='Source entity')
    rel_parser.add_argument('--to', required=True, dest='to_e', help='Target entity')
    rel_parser.add_argument('--type', required=True, help='Relation type')
    rel_parser.add_argument('--weight', type=float, default=0.7, help='Weight')
    
    # search command
    search_parser = subparsers.add_parser('search', help='Search entities')
    search_parser.add_argument('query', help='Search query')
    
    # list command
    subparsers.add_parser('list', help='List entities')
    
    # stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # enhance command
    subparsers.add_parser('enhance', help='Bulk add entries (from kg_enhancer)')
    
    # lifecycle command
    lifecycle_parser = subparsers.add_parser('lifecycle', help='KG lifecycle management')
    lifecycle_parser.add_argument('--dedup', action='store_true', help='Deduplicate entities')
    lifecycle_parser.add_argument('--age', action='store_true', help='Mark stale entities')
    lifecycle_parser.add_argument('--enforce', action='store_true', help='Enforce max entities limit')
    lifecycle_parser.add_argument('--all', action='store_true', help='Run all maintenance')
    lifecycle_parser.add_argument('--stats', action='store_true', help='Show stats only')
    
    # clean-relations command
    clean_parser = subparsers.add_parser('clean-relations', help='Clean low-quality relations')
    clean_parser.add_argument('--dry-run', action='store_true', help='Show what would be cleaned')
    clean_parser.add_argument('--execute', action='store_true', help='Execute the cleaning')
    clean_parser.add_argument('--analyze-only', action='store_true', help='Just analyze')
    clean_parser.add_argument('--aggressive', action='store_true', help='More aggressive cleaning')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'add':
        tags = args.tags.split(',') if args.tags else []
        add_entity(args.type, args.name, args.content, tags, args.priority)
    
    elif args.command == 'list':
        list_entities()
    
    elif args.command == 'stats':
        stats()
    
    elif args.command == 'search':
        search(args.query)
    
    elif args.command == 'add-relation':
        add_relation(args.from_e, args.to_e, args.type, args.weight)
    
    elif args.command == 'enhance':
        enhance_run()
    
    elif args.command == 'lifecycle':
        lifecycle_run(args)
    
    elif args.command == 'clean-relations':
        clean_relations_run(args)
    
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

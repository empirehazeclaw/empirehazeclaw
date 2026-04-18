#!/usr/bin/env python3
"""
KG Optimizer - Phase 4
======================
Adds indexes, temporal tracking, and query optimization to KG.
Based on Graphiti-style temporal knowledge graphs.

Usage:
    python3 kg_optimizer.py --indexes     # Create indexes
    python3 kg_optimizer.py --temporal     # Add temporal tracking
    python3 kg_optimizer.py --query <type> # Test query
    python3 kg_optimizer.py --full         # Full optimization
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
KG_FILE = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"
BACKUP_DIR = WORKSPACE / "backups" / f"kg_optimize_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def load_kg():
    return json.loads(KG_FILE.read_text())

def save_kg(kg):
    KG_FILE.write_text(json.dumps(kg, indent=2, ensure_ascii=False))

def create_indexes(kg):
    """Create pre-computed indexes for fast queries."""
    print("\n📊 Creating indexes...")
    
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    if isinstance(relations, dict):
        relations = list(relations.values())
    
    # Index by type
    by_type = defaultdict(list)
    for name, entity in entities.items():
        entity_type = entity.get('type', 'unknown')
        by_type[entity_type].append(name)
    
    # Index by source/timestamp
    by_timestamp = defaultdict(list)
    for name, entity in entities.items():
        created = entity.get('created_at', '')
        if created:
            date = created[:10]
            by_timestamp[date].append(name)
    
    # Index by source system
    by_source = defaultdict(list)
    for name, entity in entities.items():
        source = entity.get('source', entity.get('provenance', 'unknown'))
        by_source[source].append(name)
    
    # Index relations by type
    rel_by_type = defaultdict(list)
    for i, rel in enumerate(relations):
        rel_type = rel.get('type', 'unknown')
        rel_by_type[rel_type].append(i)
    
    # Create index structure
    indexes = {
        'by_type': dict(by_type),
        'by_timestamp': dict(by_timestamp),
        'by_source': dict(by_source),
        'relations_by_type': dict(rel_by_type),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    kg['indexes'] = indexes
    
    print(f"   ✅ by_type: {len(indexes['by_type'])} types")
    print(f"   ✅ by_timestamp: {len(indexes['by_timestamp'])} dates")
    print(f"   ✅ by_source: {len(indexes['by_source'])} sources")
    print(f"   ✅ relations_by_type: {len(indexes['relations_by_type'])} types")
    
    return kg

def add_temporal_tracking(kg):
    """Add temporal tracking to all entities."""
    print("\n⏰ Adding temporal tracking...")
    
    entities = kg.get('entities', {})
    now = datetime.now(timezone.utc).isoformat()
    updated = 0
    
    for name, entity in entities.items():
        # Add created_at if missing
        if 'created_at' not in entity:
            entity['created_at'] = now
        
        # Add version_history if missing
        if 'version_history' not in entity:
            entity['version_history'] = [{
                'timestamp': entity.get('created_at', now),
                'action': 'created'
            }]
        
        # Update last_accessed for frequently accessed entities
        if 'last_accessed' not in entity:
            entity['last_accessed'] = entity.get('created_at', now)
        
        # Add provenance if missing
        if 'provenance' not in entity:
            entity['provenance'] = 'learning_system'
        
        updated += 1
    
    # Update relations with temporal info
    relations = kg.get('relations', [])
    if isinstance(relations, list):
        for rel in relations:
            if 'created_at' not in rel:
                rel['created_at'] = now
            if 'version_history' not in rel:
                rel['version_history'] = [{
                    'timestamp': rel.get('created_at', now),
                    'action': 'created'
                }]
    
    kg['updated_at'] = now
    
    print(f"   ✅ Updated {updated} entities with temporal tracking")
    print(f"   ✅ Updated {len(relations)} relations")
    
    return kg

def add_provenance(kg):
    """Add provenance tracking."""
    print("\n🔍 Adding provenance tracking...")
    
    entities = kg.get('entities', {})
    provenance_counts = defaultdict(int)
    
    for name, entity in entities.items():
        if 'provenance' not in entity:
            # Infer provenance from entity name/type
            if 'learning' in name.lower():
                entity['provenance'] = 'learning_loop'
            elif 'failure' in name.lower() or 'error' in name.lower():
                entity['provenance'] = 'failure_logger'
            elif 'meta' in name.lower():
                entity['provenance'] = 'meta_learning'
            elif 'exploration' in name.lower():
                entity['provenance'] = 'exploration_budget'
            elif 'sre' in name.lower() or 'incident' in name.lower():
                entity['provenance'] = 'sre_culture'
            else:
                entity['provenance'] = 'unknown'
        
        provenance_counts[entity['provenance']] += 1
    
    print(f"   ✅ Provenance types: {dict(provenance_counts)}")
    
    return kg

def optimize_queries(kg):
    """Optimize query performance."""
    print("\n⚡ Optimizing queries...")
    
    # Add commonly accessed entity cache
    entities = kg.get('entities', {})
    
    # Pre-compute learning entities (frequently accessed)
    learning_entities = []
    for name, entity in entities.items():
        if entity.get('type') == 'learning':
            learning_entities.append(name)
    
    # Add query hints
    kg['query_hints'] = {
        'learning_entities_count': len(learning_entities),
        'frequently_accessed': learning_entities[:10],
        'cache_age_seconds': 300,
        'optimized_at': datetime.now(timezone.utc).isoformat()
    }
    
    print(f"   ✅ Learning entities: {len(learning_entities)}")
    print(f"   ✅ Frequently accessed: {len(learning_entities[:10])}")
    
    return kg

def test_query(kg, query_type):
    """Test a query using indexes."""
    print(f"\n🔍 Testing query: {query_type}")
    
    if 'indexes' not in kg:
        print("   ❌ No indexes found. Run --indexes first.")
        return
    
    indexes = kg['indexes']
    
    if query_type == 'learning':
        results = indexes.get('by_type', {}).get('learning', [])
        print(f"   ✅ Found {len(results)} learning entities")
    elif query_type == 'recent':
        # Get entities from last 7 days
        now = datetime.now(timezone.utc)
        recent = []
        for date in indexes.get('by_timestamp', {}).keys():
            try:
                dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                if (now - dt).days <= 7:
                    recent.extend(indexes['by_timestamp'][date])
            except:
                pass
        print(f"   ✅ Found {len(recent)} entities from last 7 days")
    elif query_type == 'relations':
        co_occurs = indexes.get('relations_by_type', {}).get('co_occurs', [])
        learned = indexes.get('relations_by_type', {}).get('learned_from', [])
        print(f"   ✅ Relations: {len(co_occurs)} co_occurs, {len(learned)} learned_from")
    else:
        print(f"   ❌ Unknown query type: {query_type}")
    
    return kg

def full_optimization():
    """Run full KG optimization."""
    print("=" * 60)
    print("🔧 KG OPTIMIZER - FULL OPTIMIZATION")
    print("=" * 60)
    
    kg = load_kg()
    
    # Create backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUP_DIR / "knowledge_graph.json.pre_optimize"
    backup_file.write_text(json.dumps(kg, indent=2))
    print(f"\n💾 Backup saved: {backup_file}")
    
    # Phase 1: Create indexes
    kg = create_indexes(kg)
    
    # Phase 2: Temporal tracking
    kg = add_temporal_tracking(kg)
    
    # Phase 3: Provenance
    kg = add_provenance(kg)
    
    # Phase 4: Query optimization
    kg = optimize_queries(kg)
    
    # Save
    kg['optimized_at'] = datetime.now(timezone.utc).isoformat()
    kg['optimization_version'] = '1.0'
    save_kg(kg)
    
    print("\n" + "=" * 60)
    print("✅ KG OPTIMIZATION COMPLETE")
    print("=" * 60)
    print(f"   Entities: {len(kg.get('entities', {}))}")
    print(f"   Relations: {len(kg.get('relations', []))}")
    print(f"   Indexes: {len(kg.get('indexes', {}))} types")
    print(f"   Optimized at: {kg.get('optimized_at', 'N/A')[:19]}")

def show_stats():
    """Show KG stats with optimization info."""
    kg = load_kg()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           KG OPTIMIZER - STATUS                          ║
╠══════════════════════════════════════════════════════════╣
║  Entities: {len(kg.get('entities', {})):<47}║
║  Relations: {len(kg.get('relations', [])):<45}║
║  Indexes: {len(kg.get('indexes', {}).get('by_type', {})):<48}║
║  Optimized: {kg.get('optimized_at', 'Never')[:19]:<44}║
╠══════════════════════════════════════════════════════════╣
║  INDEX TYPES:                                            ║""")
    
    if 'indexes' in kg:
        for idx_type in kg['indexes']:
            if idx_type != 'created_at':
                data = kg['indexes'][idx_type]
                if isinstance(data, dict):
                    print(f"║    - {idx_type}: {len(data)} entries{'':>35}║")
                elif isinstance(data, list):
                    print(f"║    - {idx_type}: {len(data)} entries{'':>35}║")
    else:
        print("║    No indexes yet. Run --full to optimize.               ║")
    
    print("╚══════════════════════════════════════════════════════════╝")

def main():
    parser = argparse.ArgumentParser(description="KG Optimizer")
    parser.add_argument("--indexes", action="store_true", help="Create indexes only")
    parser.add_argument("--temporal", action="store_true", help="Add temporal tracking")
    parser.add_argument("--query", metavar="TYPE", help="Test query")
    parser.add_argument("--full", action="store_true", help="Full optimization")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    if args.status:
        show_stats()
    
    if args.indexes:
        kg = load_kg()
        kg = create_indexes(kg)
        save_kg(kg)
        print("✅ Indexes created and saved")
    
    if args.temporal:
        kg = load_kg()
        kg = add_temporal_tracking(kg)
        kg = add_provenance(kg)
        save_kg(kg)
        print("✅ Temporal tracking added")
    
    if args.query:
        kg = load_kg()
        test_query(kg, args.query)
    
    if args.full:
        full_optimization()

if __name__ == "__main__":
    main()
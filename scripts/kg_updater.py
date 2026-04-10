#!/usr/bin/env python3
"""
Sir HazeClaw Knowledge Graph Updater
Fügt neue Entries zum Knowledge Graph hinzu.

⚠️ WICHTIG: Dieser Script verwendet das echte KG Format (entities/relations)
   NICHT das alte nodes/edges Format!

Usage:
    python3 kg_updater.py add --type skill --name "New Skill" --content "Description"
    python3 kg_updater.py list
    python3 kg_updater.py stats
    python3 kg_updater.py search "query"
    python3 kg_updater.py add-relation --from "EntityA" --to "EntityB" --type "relates_to"
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

KG_PATH = Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json")

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
        KG_PATH.parent.mkdir(parents=True, exist_ok=True)
        kg = {
            "entities": {},
            "relations": [],
            "relationships": [],
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        with open(KG_PATH, 'w') as f:
            json.dump(kg, f, indent=2)

def add_entity(entity_type, name, content, tags=None, priority="MEDIUM"):
    """Fügt Entity zum KG hinzu."""
    kg = load_kg()
    
    # Generate ID
    entity_id = f"{entity_type}_{name.lower().replace(' ', '_').replace('-', '_')}"
    timestamp = datetime.now().strftime('%Y%m%d')
    entity_id_full = f"{entity_id}_{timestamp}"
    
    # Check if already exists
    if entity_id_full in kg['entities']:
        print(f"⚠️ Entity existiert bereits: {entity_id_full}")
        return
    
    # Create entity (echtes KG Format)
    entity = {
        "type": entity_type,
        "category": entity_type,
        "facts": [{
            "content": content,
            "confidence": 0.9,
            "extracted_at": datetime.now().isoformat(),
            "category": entity_type
        }],
        "priority": priority,
        "created": datetime.now().isoformat(),
        "last_accessed": ""
    }
    
    if tags:
        entity['tags'] = tags
    
    kg['entities'][entity_id_full] = entity
    kg['last_updated'] = datetime.now().isoformat()
    
    save_kg(kg)
    print(f"✅ Added: {entity_id_full}")

def list_entities():
    """Listet alle Entities nach Typ."""
    kg = load_kg()
    
    entities = kg.get('entities', {})
    if not entities:
        print("Keine Entities im Knowledge Graph")
        return
    
    # Group by type
    by_type = {}
    for entity_id, entity in entities.items():
        entity_type = entity.get('type', 'unknown')
        if entity_type not in by_type:
            by_type[entity_type] = []
        by_type[entity_type].append((entity_id, entity))
    
    for entity_type, items in sorted(by_type.items()):
        print(f"\n## {entity_type} ({len(items)})")
        for entity_id, entity in items[:10]:
            name = entity.get('facts', [{}])[0].get('content', 'unnamed')[:60]
            print(f"  - {entity_id}: {name}")

def stats():
    """Zeigt KG Stats."""
    kg = load_kg()
    
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    
    print(f"📊 Knowledge Graph Stats:")
    print(f"  Entities: {len(entities)}")
    print(f"  Relations: {len(relations)}")
    print(f"  Updated: {kg.get('last_updated', 'unknown')}")
    
    # Type distribution
    by_type = {}
    for entity in entities.values():
        t = entity.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
    
    print(f"\n📁 Type Distribution:")
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")

def search(query):
    """Sucht nach Entities."""
    kg = load_kg()
    entities = kg.get('entities', {})
    
    query_lower = query.lower()
    results = []
    
    for entity_id, entity in entities.items():
        # Search in ID
        if query_lower in entity_id.lower():
            results.append((entity_id, entity, 1.0))
            continue
        
        # Search in facts
        for fact in entity.get('facts', []):
            content = fact.get('content', '').lower()
            if query_lower in content:
                results.append((entity_id, entity, 0.8))
                break
    
    if not results:
        print(f"Keine Ergebnisse für: {query}")
        return
    
    print(f"🔍 Suchergebnisse für '{query}':")
    for entity_id, entity, score in results[:10]:
        fact = entity.get('facts', [{}])[0].get('content', '')[:80]
        print(f"  [{score:.1f}] {entity_id}")
        print(f"      {fact}")

def add_relation(from_entity, to_entity, relation_type, weight=0.7):
    """Fügt Relation hinzu."""
    kg = load_kg()
    
    # Check entities exist
    entities = kg.get('entities', {})
    if from_entity not in entities:
        print(f"❌ Entity nicht gefunden: {from_entity}")
        return
    if to_entity not in entities:
        print(f"❌ Entity nicht gefunden: {to_entity}")
        return
    
    # Check if relation already exists
    for rel in kg.get('relations', []):
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
    
    kg['relations'].append(relation)
    kg['relationships'].append(relation)
    kg['last_updated'] = datetime.now().isoformat()
    
    save_kg(kg)
    print(f"✅ Relation hinzugefügt: {from_entity} --{relation_type}--> {to_entity}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'add':
        # Parse args
        args = sys.argv[2:]
        entity_type = name = content = None
        tags = []
        priority = "MEDIUM"
        
        i = 0
        while i < len(args):
            if args[i] == '--type' and i+1 < len(args):
                entity_type = args[i+1]
                i += 2
            elif args[i] == '--name' and i+1 < len(args):
                name = args[i+1]
                i += 2
            elif args[i] == '--content' and i+1 < len(args):
                content = args[i+1]
                i += 2
            elif args[i] == '--tags' and i+1 < len(args):
                tags = args[i+1].split(',')
                i += 2
            elif args[i] == '--priority' and i+1 < len(args):
                priority = args[i+1]
                i += 2
            else:
                i += 1
        
        if not entity_type or not name or not content:
            print("❌ Usage: kg_updater.py add --type <type> --name <name> --content <content>")
            sys.exit(1)
        
        add_entity(entity_type, name, content, tags, priority)
    
    elif cmd == 'list':
        list_entities()
    
    elif cmd == 'stats':
        stats()
    
    elif cmd == 'search':
        if len(sys.argv) < 3:
            print("❌ Usage: kg_updater.py search <query>")
            sys.exit(1)
        search(sys.argv[2])
    
    elif cmd == 'add-relation':
        args = sys.argv[2:]
        from_e = to_e = rel_type = None
        weight = 0.7
        
        i = 0
        while i < len(args):
            if args[i] == '--from' and i+1 < len(args):
                from_e = args[i+1]
                i += 2
            elif args[i] == '--to' and i+1 < len(args):
                to_e = args[i+1]
                i += 2
            elif args[i] == '--type' and i+1 < len(args):
                rel_type = args[i+1]
                i += 2
            elif args[i] == '--weight' and i+1 < len(args):
                weight = float(args[i+1])
                i += 2
            else:
                i += 1
        
        if not from_e or not to_e or not rel_type:
            print("❌ Usage: kg_updater.py add-relation --from <entity> --to <entity> --type <relation>")
            sys.exit(1)
        
        add_relation(from_e, to_e, rel_type, weight)
    
    else:
        print(f"❌ Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    main()
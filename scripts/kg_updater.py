#!/usr/bin/env python3
"""
Sir HazeClaw Knowledge Graph Updater
Fügt neue Entries zum Knowledge Graph hinzu.

Usage:
    python3 kg_updater.py add --type skill --name "New Skill" --content "Description"
    python3 kg_updater.py list
    python3 kg_updater.py stats
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

KG_PATH = Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json")
KG_DB = Path("/home/clawbot/.openclaw/memory/main.sqlite")

def init_kg():
    """Initialisiert Knowledge Graph."""
    if not KG_PATH.exists():
        KG_PATH.parent.mkdir(parents=True, exist_ok=True)
        KG_PATH.write_text(json.dumps({
            "nodes": {},
            "edges": [],
            "meta": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }, indent=2))

def add_entity(entity_type, name, content, tags=None):
    """Fügt Entity zum KG hinzu."""
    init_kg()
    
    with open(KG_PATH) as f:
        kg = json.load(f)
    
    # Generate ID
    entity_id = f"{entity_type}_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
    
    # Add node
    kg['nodes'][entity_id] = {
        "type": entity_type,
        "name": name,
        "content": content,
        "tags": tags or [],
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    
    # Save
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)
    
    print(f"✅ Added: {entity_id}")

def list_entities():
    """Listet alle Entities."""
    init_kg()
    
    with open(KG_PATH) as f:
        kg = json.load(f)
    
    nodes = kg.get('nodes', {})
    
    if not nodes:
        print("No entities in Knowledge Graph")
        return
    
    # Group by type
    by_type = {}
    for node_id, node in nodes.items():
        node_type = node.get('type', 'unknown')
        if node_type not in by_type:
            by_type[node_type] = []
        by_type[node_type].append(node)
    
    for node_type, items in by_type.items():
        print(f"\n## {node_type} ({len(items)})")
        for item in items[:5]:
            print(f"  - {item.get('name', 'unnamed')}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")

def stats():
    """Zeigt KG Stats."""
    init_kg()
    
    with open(KG_PATH) as f:
        kg = json.load(f)
    
    nodes = kg.get('nodes', {})
    edges = kg.get('edges', [])
    
    print(f"Knowledge Graph Stats:")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    
    # By type
    by_type = {}
    for node in nodes.values():
        t = node.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
    
    print(f"\nBy Type:")
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")

def add_from_file(file_path, entity_type="document"):
    """Fügt File zum KG hinzu."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    content = path.read_text()[:1000]  # First 1000 chars
    
    add_entity(
        entity_type=entity_type,
        name=path.name,
        content=content,
        tags=["auto-added"]
    )

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Knowledge Graph Updater')
    subparsers = parser.add_subparsers(dest='command')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add entity')
    add_parser.add_argument('--type', required=True, help='Entity type')
    add_parser.add_argument('--name', required=True, help='Entity name')
    add_parser.add_argument('--content', required=True, help='Content')
    add_parser.add_argument('--tags', help='Tags (comma separated)')
    
    # List command
    subparsers.add_parser('list', help='List entities')
    
    # Stats command
    subparsers.add_parser('stats', help='Show stats')
    
    # Add from file
    add_file_parser = subparsers.add_parser('add-file', help='Add file to KG')
    add_file_parser.add_argument('file', help='File path')
    add_file_parser.add_argument('--type', default='document', help='Entity type')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        tags = args.tags.split(',') if args.tags else None
        add_entity(args.type, args.name, args.content, tags)
    elif args.command == 'list':
        list_entities()
    elif args.command == 'stats':
        stats()
    elif args.command == 'add-file':
        add_from_file(args.file, args.type)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
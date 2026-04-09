#!/usr/bin/env python3
"""
Quick Add to Knowledge Graph
Usage: python3 kg_quick_add.py "Entity Name" "fact content" [type]
"""
import sys
import json
from datetime import datetime
from pathlib import Path

KG_FILE = Path("/home/clawbot/.openclaw/workspace/memory/knowledge_graph.json")

def load_kg():
    with open(KG_FILE) as f:
        return json.load(f)

def save_kg(kg):
    with open(KG_FILE, 'w') as f:
        json.dump(kg, f, indent=2)

def quick_add(name, fact, etype="concept"):
    kg = load_kg()
    
    if name in kg['entities']:
        # Add fact to existing entity
        kg['entities'][name]['facts'].append({
            "content": fact,
            "confidence": 0.8,
            "extracted_at": datetime.now().isoformat(),
            "category": "quick-add"
        })
        kg['entities'][name]['last_accessed'] = datetime.now().isoformat()
        kg['entities'][name]['access_count'] += 1
        print(f"✅ Added fact to existing entity: {name}")
    else:
        # Create new entity
        kg['entities'][name] = {
            "type": etype,
            "category": "quick-add",
            "facts": [{
                "content": fact,
                "confidence": 0.8,
                "extracted_at": datetime.now().isoformat(),
                "category": "quick-add"
            }],
            "priority": "MEDIUM",
            "created": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 1,
            "decay_score": 1.0
        }
        print(f"✅ Created new entity: {name}")
    
    save_kg(kg)
    print(f"📊 Total entities: {len(kg['entities'])}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 kg_quick_add.py 'Entity Name' 'fact content' [type]")
        sys.exit(1)
    
    name = sys.argv[1]
    fact = sys.argv[2]
    etype = sys.argv[3] if len(sys.argv) > 3 else "concept"
    
    quick_add(name, fact, etype)

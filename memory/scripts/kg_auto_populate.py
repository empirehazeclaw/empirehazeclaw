#!/usr/bin/env python3
"""
Knowledge Graph Auto-Population
Scans new/decisions/learnings files and extracts entities to knowledge_graph.json
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path

KG_FILE = Path("/home/clawbot/.openclaw/workspace/memory/knowledge_graph.json")
DECISIONS_DIR = Path("/home/clawbot/.openclaw/workspace/memory/decisions")
LEARNINGS_DIR = Path("/home/clawbot/.openclaw/workspace/memory/learnings")
NOTES_DIR = Path("/home/clawbot/.openclaw/workspace/memory/notes")
MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/memory")

# Pattern for entity extraction
ENTITY_PATTERNS = [
    (r'\*\*([A-Z][a-zA-Z]+)\*\*', 'concept'),  # **ConceptName**
    (r'## ([A-Z][a-zA-Z]+)', 'topic'),           # ## Topic
    (r'### ([A-Z][a-zA-Z\s]+)', 'subtopic'),    # ### Subtopic
    (r'^- \*\*(.+?)\*\*:', 'feature'),           # - **Feature**:
]

def load_kg():
    if KG_FILE.exists():
        with open(KG_FILE) as f:
            return json.load(f)
    return {"entities": {}, "relationships": []}

def save_kg(kg):
    with open(KG_FILE, 'w') as f:
        json.dump(kg, f, indent=2)
    print(f"✅ Knowledge Graph updated: {len(kg['entities'])} entities")

def extract_entities_from_file(filepath):
    """Extract potential entities from a markdown file."""
    entities = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract title
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            entities.append({
                "name": title_match.group(1).strip(),
                "type": "note",
                "source": str(filepath)
            })
        
        # Extract patterns
        for pattern, etype in ENTITY_PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 3 and len(match) < 100:
                    entities.append({
                        "name": match.strip(),
                        "type": etype,
                        "source": str(filepath)
                    })
        
        # Extract decisions
        if 'decision' in str(filepath).lower():
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(filepath))
            if date_match:
                entities.append({
                    "name": f"Decision {date_match.group(1)}",
                    "type": "decision",
                    "source": str(filepath)
                })
        
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    
    return entities

def add_to_kg(kg, new_entities):
    """Add new entities to knowledge graph."""
    added = 0
    for entity in new_entities:
        name = entity['name']
        if not name or name in kg['entities']:
            continue
        
        kg['entities'][name] = {
            "type": entity['type'],
            "category": "auto-extracted",
            "facts": [{
                "content": f"Source: {entity['source']}",
                "confidence": 0.6,
                "extracted_at": datetime.now().isoformat(),
                "category": "auto"
            }],
            "priority": "MEDIUM",
            "created": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0,
            "decay_score": 1.0
        }
        added += 1
    
    return added

def scan_and_update():
    """Main function to scan and update knowledge graph."""
    print("=== 🧠 Knowledge Graph Auto-Population ===\n")
    
    kg = load_kg()
    print(f"Current entities: {len(kg['entities'])}")
    
    # Scan new files (last 7 days)
    new_files = []
    for directory in [DECISIONS_DIR, LEARNINGS_DIR, NOTES_DIR]:
        if not directory.exists():
            continue
        for f in directory.rglob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            if age_days <= 7:
                new_files.append(f)
    
    print(f"New files (last 7 days): {len(new_files)}")
    
    total_added = 0
    for filepath in new_files:
        entities = extract_entities_from_file(filepath)
        added = add_to_kg(kg, entities)
        if added > 0:
            print(f"  + {added} entities from {filepath.name}")
        total_added += added
    
    if total_added > 0:
        save_kg(kg)
        print(f"\n✅ Added {total_added} new entities")
    else:
        print("\nℹ️  No new entities to add")

if __name__ == "__main__":
    scan_and_update()

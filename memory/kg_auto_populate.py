#!/usr/bin/env python3
"""
Knowledge Graph Auto-Populate
Automatically generates relations between entities based on:
- Shared categories
- Co-occurrence in facts
- Shared terms/keywords
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from knowledge_graph import KnowledgeGraph

# Input validation patterns
VALID_ARGS = {'--dry-run'}
SAFE_PATTERN = r'^[a-zA-Z0-9_\-\[\]]+$'

def validate_args(args):
    """Validate command line arguments"""
    for arg in args:
        if arg not in VALID_ARGS:
            if not re.match(SAFE_PATTERN, arg):
                print(f"❌ Invalid argument: {arg}")
                return False
    return True

# Stopwords for term extraction
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
    'und', 'für', 'der', 'die', 'das', 'mit', 'von', 'und', 'ist'
}

def extract_terms(text: str) -> set:
    """Extract meaningful terms from text"""
    # Lowercase and split
    words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]{3,}\b', text.lower())
    # Filter stopwords and short words
    return {w for w in words if w not in STOPWORDS and len(w) > 2}

def find_category_relations(kg: KnowledgeGraph) -> list:
    """Find entities that share the same category"""
    relations = []
    entities = kg.data.get("entities", {})
    
    # Group entities by category
    by_category = defaultdict(list)
    for entity, data in entities.items():
        cat = data.get("category", "general")
        by_category[cat].append(entity)
    
    # Create relations for entities sharing category
    for category, entity_list in by_category.items():
        if len(entity_list) < 2:
            continue
        for i, e1 in enumerate(entity_list):
            for e2 in entity_list[i+1:]:
                relations.append({
                    "from": e1,
                    "to": e2,
                    "type": "shares_category",
                    "weight": 0.7,
                    "meta": {"category": category}
                })
    
    return relations

def find_cooccurrence_relations(kg: KnowledgeGraph) -> list:
    """Find entities that co-occur in notes/other entities' facts"""
    relations = []
    entities = kg.data.get("entities", {})
    
    # Collect all fact content per entity
    entity_texts = {}
    for entity, data in entities.items():
        texts = []
        for fact in data.get("facts", []):
            texts.append(fact.get("content", ""))
        entity_texts[entity] = " ".join(texts).lower()
    
    # Check co-occurrence: if entity A's name appears in entity B's fact
    for e1, text1 in entity_texts.items():
        for e2, text2 in entity_texts.items():
            if e1 >= e2:
                continue
            
            # Count co-occurrences
            count = 0
            # e1 name in e2 text or e2 name in e1 text
            if e1.lower() in text2 or e2.lower() in text1:
                # Also check if they share significant terms
                terms1 = extract_terms(text1)
                terms2 = extract_terms(text2)
                shared = terms1 & terms2
                if len(shared) >= 3:  # At least 3 shared meaningful terms
                    count = len(shared)
            
            if count >= 3:
                weight = min(0.9, 0.3 + (count * 0.05))
                relations.append({
                    "from": e1,
                    "to": e2,
                    "type": "co_occurs",
                    "weight": weight,
                    "meta": {"shared_terms": count}
                })
    
    return relations

def find_term_based_relations(kg: KnowledgeGraph, min_shared: int = 4) -> list:
    """Find entities with shared terms in their facts"""
    relations = []
    entities = kg.data.get("entities", {})
    
    # Extract terms per entity
    entity_terms = {}
    for entity, data in entities.items():
        all_text = " ".join(f.get("content", "") for f in data.get("facts", []))
        entity_terms[entity] = extract_terms(all_text)
    
    # Compare entity pairs
    entity_list = list(entities.keys())
    for i, e1 in enumerate(entity_list):
        for e2 in entity_list[i+1:]:
            shared = entity_terms[e1] & entity_terms[e2]
            if len(shared) >= min_shared:
                weight = min(0.8, 0.2 + (len(shared) * 0.03))
                relations.append({
                    "from": e1,
                    "to": e2,
                    "type": "related_terms",
                    "weight": weight,
                    "meta": {"shared_terms": list(shared)[:10]}  # Limit stored terms
                })
    
    return relations

def deduplicate_relations(new_relations: list, existing: list) -> list:
    """Remove duplicate relations"""
    existing_pairs = set()
    for rel in existing:
        key = (rel["from"], rel["to"])
        existing_pairs.add(key)
    
    unique = []
    for rel in new_relations:
        key = (rel["from"], rel["to"])
        if key not in existing_pairs and (key[1], key[0]) not in existing_pairs:
            unique.append(rel)
    
    return unique

def run(auto_populate: bool = True):
    """Run auto-populate for relations"""
    kg = KnowledgeGraph()
    
    existing_relations = kg.data.get("relations", [])
    print(f"📊 Current KG: {len(kg.data['entities'])} entities, {len(existing_relations)} relations")
    
    if not auto_populate:
        print("Dry run - showing what would be created")
        return
    
    # Find all relation types
    print("\n🔍 Finding category relations...")
    cat_rels = find_category_relations(kg)
    print(f"   Found {len(cat_rels)} category relations")
    
    print("🔍 Finding co-occurrence relations...")
    cooc_rels = find_cooccurrence_relations(kg)
    print(f"   Found {len(cooc_rels)} co-occurrence relations")
    
    print("🔍 Finding term-based relations...")
    term_rels = find_term_based_relations(kg)
    print(f"   Found {len(term_rels)} term-based relations")
    
    # Combine and deduplicate
    all_new = cat_rels + cooc_rels + term_rels
    unique_new = deduplicate_relations(all_new, existing_relations)
    
    print(f"\n✅ Adding {len(unique_new)} new unique relations...")
    
    # Add relations
    for rel in unique_new:
        kg.add_relation(rel["from"], rel["to"], rel["type"], rel["weight"])
    
    # Stats
    stats = kg.get_stats()
    print(f"\n📊 Updated KG Stats:")
    print(f"   Entities: {stats['total_entities']}")
    print(f"   Relations: {stats['total_relations']}")
    
    # Relation type breakdown
    rel_types = defaultdict(int)
    for rel in kg.data.get("relations", []):
        rel_types[rel["type"]] += 1
    print(f"   By type: {dict(rel_types)}")

if __name__ == "__main__":
    if not validate_args(sys.argv[1:]):
        print("Usage: python3 kg_auto_populate.py [--dry-run]")
        sys.exit(1)
    
    dry_run = "--dry-run" in sys.argv
    run(auto_populate=not dry_run)

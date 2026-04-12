#!/usr/bin/env python3
"""
KG Relation Cleaner — Phase 2 of KG Quality Plan
Removes excessive shares_category relations and improves relation quality.

Usage:
    python3 kg_relation_cleaner.py --dry-run
    python3 kg_relation_cleaner.py --execute
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

KG_FILE = Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json")
BACKUP_DIR = Path("/home/clawbot/.openclaw/backups/kg_relation_cleaner")

# Relation types that are HIGH QUALITY (keep all)
HIGH_QUALITY_TYPES = {
    'implements', 'uses', 'solves', 'creates', 'manages', 'enforces',
    'follows', 'supports', 'enables', 'based_on', 'affects', 'avoids',
    'tests', 'specializes', 'owns', 'employs', 'same_as', 'related_terms',
    'co_occurs', 'related_to', 'part_of', 'requires', 'produces', 'causes',
    'precedes', 'has_property', 'competitor', 'alternative', 'upgrade'
}

# Relation types that are LOW QUALITY (consider removing)
LOW_QUALITY_TYPES = {
    'shares_category', 'belongs_to', 'associated_with', 'linked_to'
}

def load_kg():
    """Load KG from file."""
    with open(KG_FILE) as f:
        return json.load(f)

def save_kg(kg, backup=True):
    """Save KG to file with optional backup."""
    if backup:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"kg_before_clean_{timestamp}.json"
        with open(backup_file, 'w') as f:
            json.dump(kg, f, indent=2)
        print(f"📦 Backup saved: {backup_file}")
    
    with open(KG_FILE, 'w') as f:
        json.dump(kg, f, indent=2)
    print(f"💾 KG saved: {KG_FILE}")

def analyze_relations(kg):
    """Analyze current relation state."""
    relations = kg.get('relations', [])
    
    print("\n📊 RELATION ANALYSIS:")
    print(f"   Total relations: {len(relations)}")
    
    # Count by type
    type_counts = Counter(r.get('type', 'unknown') for r in relations)
    
    print("\n📈 By Type:")
    high_quality = 0
    low_quality = 0
    
    for t, c in type_counts.most_common():
        quality = "✅" if t in HIGH_QUALITY_TYPES else "❌"
        print(f"   {quality} {t}: {c}")
        if t in HIGH_QUALITY_TYPES:
            high_quality += c
        elif t in LOW_QUALITY_TYPES:
            low_quality += c
    
    print(f"\n📊 Summary:")
    print(f"   High quality: {high_quality} ({100*high_quality/len(relations):.1f}%)")
    print(f"   Low quality: {low_quality} ({100*low_quality/len(relations):.1f}%)")
    print(f"   Other: {len(relations) - high_quality - low_quality}")
    
    return type_counts

def clean_relations(kg, dry_run=True, aggressive=False):
    """Remove excessive low-quality relations.
    
    Args:
        dry_run: If True, only simulate
        aggressive: If True, remove ALL shares_category. If False, keep some.
    """
    relations = kg.get('relations', [])
    entities = kg.get('entities', {})
    
    # Current stats
    total_before = len(relations)
    shares_cat_before = sum(1 for r in relations if r.get('type') == 'shares_category')
    
    print(f"\n🧹 CLEANING RELATIONS (dry_run={dry_run}, aggressive={aggressive}):")
    print(f"   Before: {total_before} relations ({shares_cat_before} shares_category)")
    
    # Separate relations by quality
    shares_cat_relations = [r for r in relations if r.get('type') == 'shares_category']
    other_relations = [r for r in relations if r.get('type') != 'shares_category']
    
    if aggressive:
        # Remove ALL shares_category relations
        relations_to_keep = other_relations
        removed = len(shares_cat_relations)
        shares_cat_after = 0
    else:
        # Keep only top 5 shares_category per entity
        MAX_SHARES_PER_ENTITY = 5
        relations_to_keep = list(other_relations)
        
        from_counts = Counter(r.get('from') for r in shares_cat_relations)
        
        for entity_from, count in from_counts.items():
            entity_relations = [r for r in shares_cat_relations if r.get('from') == entity_from]
            
            if count <= MAX_SHARES_PER_ENTITY:
                relations_to_keep.extend(entity_relations)
            else:
                sorted_rels = sorted(entity_relations, key=lambda r: r.get('weight', 0.5), reverse=True)
                relations_to_keep.extend(sorted_rels[:MAX_SHARES_PER_ENTITY])
        
        shares_cat_after = sum(1 for r in relations_to_keep if r.get('type') == 'shares_category')
        removed = shares_cat_before - shares_cat_after
    
    total_after = len(relations_to_keep)
    
    print(f"   After: {total_after} relations ({shares_cat_after} shares_category)")
    print(f"   Removed: {removed} relations")
    print(f"   Reduction: {100*removed/total_before:.1f}%")
    
    if dry_run:
        print("\n⚠️  DRY RUN - No changes made. Use --execute to apply.")
    else:
        print("\n✅ Applying changes...")
        kg['relations'] = relations_to_keep
        save_kg(kg)
    
    return relations_to_keep if dry_run else kg

def main():
    parser = argparse.ArgumentParser(description='KG Relation Cleaner')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be cleaned')
    parser.add_argument('--execute', action='store_true', help='Execute the cleaning')
    parser.add_argument('--analyze-only', action='store_true', help='Just analyze')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧹 KG RELATION CLEANER — Phase 2")
    print("=" * 60)
    
    kg = load_kg()
    type_counts = analyze_relations(kg)
    
    if args.analyze_only:
        return
    
    if args.dry_run or not args.execute:
        clean_relations(kg, dry_run=True)
        if args.execute:
            print("\n❌ Use --execute to apply changes")
    else:
        clean_relations(kg, dry_run=False)

if __name__ == '__main__':
    main()

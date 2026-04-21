#!/usr/bin/env python3
"""
KG Schema Fix - Phase 1
======================
Converts relations from dict-of-dicts to list-of-dicts format.
Creates proper list structure for better query performance.

Usage:
    python3 kg_schema_fix.py --dry-run    # Preview changes
    python3 kg_schema_fix.py --apply      # Apply fixes
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
KG_FILE = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"
BACKUP_DIR = WORKSPACE / "backups" / f"kg_schema_fix_{datetime.now().time().strftime('%Y%m%d_%H%M%S')}"

def load_kg():
    return json.loads(KG_FILE.read_text())

def save_kg(kg):
    KG_FILE.write_text(json.dumps(kg, indent=2, ensure_ascii=False))

def analyze_current_state(kg):
    """Analyze current KG state."""
    print("\n📊 Current KG State:")
    print(f"   Entities: {len(kg['entities'])}")
    print(f"   Relations: {len(kg['relations'])}")
    print(f"   Relations type: {type(kg['relations']).__name__}")
    
    if isinstance(kg['relations'], dict):
        print(f"   ⚠️  Relations stored as dict (key: value pairs)")
        first_key = list(kg['relations'].keys())[0]
        print(f"   Sample: {kg['relations'][first_key]}")
    else:
        print(f"   ✅ Relations stored as list")
    
    return {
        "entities": len(kg['entities']),
        "relations": len(kg['relations']),
        "is_dict": isinstance(kg['relations'], dict)
    }

def convert_relations(kg):
    """Convert relations from dict to list format."""
    if not isinstance(kg['relations'], dict):
        print("   ✅ Relations already in list format")
        return kg
    
    print("\n🔄 Converting relations...")
    old_relations = kg['relations']
    
    # Convert dict to sorted list (by numeric key)
    new_relations = []
    for key in sorted(old_relations.keys(), key=lambda x: int(x)):
        rel = old_relations[key].copy()
        new_relations.append(rel)
    
    kg['relations'] = new_relations
    
    print(f"   ✅ Converted {len(new_relations)} relations")
    return kg

def validate_kg(kg):
    """Validate KG structure after conversion."""
    print("\n✅ Validation:")
    
    errors = []
    warnings = []
    
    # Check entities
    if not isinstance(kg.get('entities'), dict):
        errors.append("entities is not a dict")
    else:
        print(f"   ✅ entities: {len(kg['entities'])} items")
    
    # Check relations
    if not isinstance(kg.get('relations'), list):
        errors.append("relations is not a list")
    else:
        print(f"   ✅ relations: {len(kg['relations'])} items")
        # Check first relation has required fields
        if kg['relations']:
            first = kg['relations'][0]
            required = ['from', 'to', 'type']
            for field in required:
                if field not in first:
                    errors.append(f"relation missing '{field}' field")
            print(f"   ✅ Sample relation: {first.get('type')} ({first.get('from')} → {first.get('to')})")
    
    # Check updated_at
    if 'updated_at' in kg:
        print(f"   ✅ updated_at: {kg['updated_at'][:19]}")
    else:
        warnings.append("no updated_at field")
    
    if errors:
        print(f"\n❌ ERRORS:")
        for e in errors:
            print(f"   - {e}")
        return False
    
    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for w in warnings:
            print(f"   - {w}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="KG Schema Fix")
    parser.add_argument("--dry-run", action="store_true", help="Preview without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        parser.print_help()
        return
    
    print("=" * 50)
    print("🔧 KG Schema Fix - Phase 1")
    print("=" * 50)
    
    kg = load_kg()
    state = analyze_current_state(kg)
    
    if state['is_dict']:
        kg = convert_relations(kg)
        kg['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        if validate_kg(kg):
            if args.apply:
                # Create backup first
                BACKUP_DIR.mkdir(parents=True, exist_ok=True)
                backup_file = BACKUP_DIR / "knowledge_graph.json.bak"
                original = json.loads(KG_FILE.read_text())
                backup_file.write_text(json.dumps(original, indent=2))
                print(f"\n💾 Backup saved: {BACKUP_DIR / backup_file.name}")
                
                save_kg(kg)
                print(f"\n✅ KG Schema Fix APPLIED")
                print(f"   Relations now: {len(kg['relations'])} items as list")
            else:
                print("\n✅ Preview complete - use --apply to save changes")
        else:
            print("\n❌ Validation failed - not applying changes")
    else:
        print("\n✅ No changes needed - relations already in list format")

if __name__ == "__main__":
    main()
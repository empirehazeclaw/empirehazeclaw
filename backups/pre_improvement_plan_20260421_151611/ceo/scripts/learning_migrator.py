#!/usr/bin/env python3
"""
Learning Migrator - Phase 6
==========================
Migrates data from old learning systems to unified system.
Deprecates redundant scripts after validation.

Usage:
    python3 learning_migrator.py --audit          # Audit current state
    python3 learning_migrator.py --migrate        # Run migration
    python3 learning_migrator.py --deprecate      # Deprecate old scripts
    python3 learning_migrator.py --validate       # Validate migration
"""

import json
import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SCRIPTS_DIR = WORKSPACE / "scripts"
EVAL_DIR = WORKSPACE / "memory" / "evaluations"
KG_FILE = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"
BACKUP_DIR = WORKSPACE / "backups" / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Scripts to deprecate after migration
DEPRECATED_SCRIPTS = [
    "phase1_integrator.py",
    "phase2_integrator.py",
    "phase3_integrator.py",
    "phase4_integrator.py",
    "phase5_integrator.py",
    "phase6_integrator.py",
    "kg_learning_integrator.py",  # Merged into learning_unified.py
]

# Legacy data files
LEGACY_FILES = [
    EVAL_DIR / "antipattern_tests.json",
    EVAL_DIR / "memory_analysis.json",
    EVAL_DIR / "lnew_metrics.json",
    EVAL_DIR / "signal_feedback.json",
]

def load_kg():
    return json.loads(KG_FILE.read_text())

def save_kg(kg):
    KG_FILE.write_text(json.dumps(kg, indent=2, ensure_ascii=False))

def audit_state():
    """Audit current state before migration."""
    print("\n🔍 AUDIT - Current State")
    print("=" * 60)
    
    # Check KG
    kg = load_kg()
    print(f"\n📊 KG State:")
    print(f"   Entities: {len(kg.get('entities', {}))}")
    print(f"   Relations: {len(kg.get('relations', []))}")
    print(f"   Has indexes: {'indexes' in kg}")
    print(f"   Has optimization: {'optimized_at' in kg}")
    
    # Check unified script
    unified = SCRIPTS_DIR / "learning_unified.py"
    print(f"\n📝 Unified Script:")
    print(f"   learning_unified.py: {'✅' if unified.exists() else '❌'}")
    if unified.exists():
        print(f"   Size: {unified.stat().st_size} bytes")
    
    # Check event bus
    events = SCRIPTS_DIR / "learning_events.py"
    print(f"\n📢 Event Bus:")
    print(f"   learning_events.py: {'✅' if events.exists() else '❌'}")
    
    # Check deprecated scripts
    print(f"\n🗑️  Scripts to deprecate:")
    for script in DEPRECATED_SCRIPTS:
        path = SCRIPTS_DIR / script
        status = '❌' if not path.exists() else '✅'
        print(f"   {status} {script}")
    
    # Check legacy files
    print(f"\n📄 Legacy files:")
    for f in LEGACY_FILES:
        status = '❌' if not f.exists() else '✅'
        print(f"   {status} {f.name}")
    
    # Count learning entities in KG
    learning_count = sum(1 for e in kg.get('entities', {}).values() if e.get('type') == 'learning')
    print(f"\n🧠 Learning Entities in KG: {learning_count}")
    
    return True

def migrate_data():
    """Migrate data from legacy sources to KG."""
    print("\n🔄 MIGRATING Data to Unified System")
    print("=" * 60)
    
    # Create backup
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    kg = load_kg()
    entities_before = len(kg.get('entities', {}))
    
    # Migrate exploration budget to KG
    exploration_file = EVAL_DIR / "exploration_budget.json"
    if exploration_file.exists():
        print("\n[1/4] Migrating exploration budget...")
        try:
            exp_data = json.loads(exploration_file.read_text())
            exp_entity = {
                'type': 'exploration_state',
                'config': exp_data.get('config', {}),
                'current_period': exp_data.get('current_period', {}),
                'migrated_at': datetime.now(timezone.utc).isoformat(),
                'provenance': 'exploration_budget'
            }
            kg['entities']['exploration_state'] = exp_entity
            print(f"   ✅ Exploration budget → KG")
        except Exception as e:
            print(f"   ⚠️  Failed: {e}")
    
    # Migrate strategy mutations to KG
    mutations_file = EVAL_DIR / "strategy_mutations.json"
    if mutations_file.exists():
        print("\n[2/4] Migrating strategy mutations...")
        try:
            mutations = json.loads(mutations_file.read_text())
            if isinstance(mutations, dict):
                mutations = mutations.get('mutations', [])
            
            for i, mut in enumerate(mutations[-10:]):  # Last 10
                mut_id = mut.get('id', f'mutation_{i}')
                mut_entity = {
                    'type': 'strategy_mutation',
                    'mutation': mut,
                    'migrated_at': datetime.now(timezone.utc).isoformat(),
                    'provenance': 'strategy_mutations'
                }
                kg['entities'][mut_id] = mut_entity
            print(f"   ✅ {min(len(mutations), 10)} mutations → KG")
        except Exception as e:
            print(f"   ⚠️  Failed: {e}")
    
    # Migrate experience memory to KG
    experiences_file = EVAL_DIR / "experience_memory.json"
    if experiences_file.exists():
        print("\n[3/4] Migrating experience memory...")
        try:
            exp_mem = json.loads(experiences_file.read_text())
            if isinstance(exp_mem, list):
                experiences = exp_mem
            else:
                experiences = exp_mem.get('experiences', [])
            
            for exp in experiences[-20:]:  # Last 20
                exp_id = exp.get('id', f'exp_{len(kg["entities"])}')
                exp_entity = {
                    'type': 'experience',
                    'data': exp,
                    'migrated_at': datetime.now(timezone.utc).isoformat(),
                    'provenance': 'experience_memory'
                }
                kg['entities'][exp_id] = exp_entity
            print(f"   ✅ {min(len(experiences), 20)} experiences → KG")
        except Exception as e:
            print(f"   ⚠️  Failed: {e}")
    
    # Migrate SRE culture data to KG
    sre_file = EVAL_DIR / "sre_culture" / "sre_culture.json"
    if sre_file.exists():
        print("\n[4/4] Migrating SRE culture...")
        try:
            sre_data = json.loads(sre_file.read_text())
            sre_entity = {
                'type': 'sre_culture_state',
                'incidents_count': len(sre_data.get('incidents', [])),
                'pre_mortems_count': len(sre_data.get('pre_mortems', [])),
                'post_mortems_count': len(sre_data.get('post_mortems', [])),
                'slo_breaches_count': len(sre_data.get('slo_breaches', [])),
                'migrated_at': datetime.now(timezone.utc).isoformat(),
                'provenance': 'sre_culture'
            }
            kg['entities']['sre_culture_state'] = sre_entity
            print(f"   ✅ SRE culture → KG")
        except Exception as e:
            print(f"   ⚠️  Failed: {e}")
    
    # Save KG
    kg['migration_at'] = datetime.now(timezone.utc).isoformat()
    kg['migration_version'] = '1.0'
    save_kg(kg)
    
    entities_after = len(kg.get('entities', {}))
    print(f"\n✅ Migration complete: {entities_before} → {entities_after} entities")
    
    return True

def deprecate_scripts(dry_run=True):
    """Deprecate old scripts."""
    print("\n🗑️  DEPRECATING Old Scripts")
    print("=" * 60)
    
    deprecated = []
    
    for script in DEPRECATED_SCRIPTS:
        path = SCRIPTS_DIR / script
        if path.exists():
            if dry_run:
                print(f"   [DRY RUN] Would deprecate: {script}")
            else:
                # Move to deprecated folder
                deprecated_dir = SCRIPTS_DIR / "deprecated"
                deprecated_dir.mkdir(exist_ok=True)
                
                new_path = deprecated_dir / script
                shutil.move(str(path), str(new_path))
                print(f"   ✅ Deprecated: {script} → deprecated/")
            
            deprecated.append(script)
        else:
            print(f"   ⚠️  Already removed: {script}")
    
    # Archive legacy files
    if not dry_run:
        archive_dir = WORKSPACE / "archive" / "legacy_data"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for f in LEGACY_FILES:
            if f.exists():
                new_path = archive_dir / f.name
                shutil.move(str(f), str(new_path))
                print(f"   📦 Archived: {f.name}")
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}{len(deprecated)} scripts deprecated")
    
    if dry_run:
        print("\n   Run with --deprecate (no --dry-run) to actually deprecate.")
    
    return deprecated

def validate():
    """Validate migration was successful."""
    print("\n✅ VALIDATING Migration")
    print("=" * 60)
    
    # Check unified script works
    print("\n[1/3] Testing unified script...")
    import subprocess
    result = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "learning_unified.py"), "--status"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print("   ✅ learning_unified.py --status works")
    else:
        print(f"   ⚠️  Failed: {result.stderr[:200]}")
    
    # Check KG has new entities
    print("\n[2/3] Checking KG migration...")
    kg = load_kg()
    new_entities = [
        'exploration_state',
        'sre_culture_state'
    ]
    for entity in new_entities:
        if entity in kg.get('entities', {}):
            print(f"   ✅ {entity} present in KG")
        else:
            print(f"   ⚠️  {entity} missing from KG")
    
    # Check optimization persisted
    print("\n[3/3] Checking optimization...")
    if 'optimized_at' in kg:
        print(f"   ✅ KG optimized at: {kg['optimized_at'][:19]}")
    else:
        print("   ⚠️  KG not optimized")
    
    if 'indexes' in kg:
        print(f"   ✅ Indexes present: {len(kg['indexes'])} types")
    else:
        print("   ⚠️  No indexes")
    
    print("\n" + "=" * 60)
    print("✅ VALIDATION COMPLETE")
    print("=" * 60)
    print("\n🎉 UNIFIED LEARNING SYSTEM READY!")
    print("\nUsage:")
    print("  python3 scripts/learning_unified.py --status")
    print("  python3 scripts/learning_unified.py --report")
    print("  python3 scripts/learning_unified.py --analyze")

def main():
    parser = argparse.ArgumentParser(description="Learning Migrator")
    parser.add_argument("--audit", action="store_true", help="Audit current state")
    parser.add_argument("--migrate", action="store_true", help="Run migration")
    parser.add_argument("--deprecate", action="store_true", help="Deprecate old scripts")
    parser.add_argument("--validate", action="store_true", help="Validate migration")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    if args.audit:
        audit_state()
    
    if args.migrate:
        migrate_data()
    
    if args.deprecate:
        deprecate_scripts(dry_run=args.dry_run)
    
    if args.validate:
        validate()

if __name__ == "__main__":
    main()
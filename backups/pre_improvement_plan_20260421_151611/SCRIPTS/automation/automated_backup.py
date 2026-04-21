#!/usr/bin/env python3
"""
CEO Automated Backup — Weekly System Backup
==========================================
Creates a complete backup of all critical CEO data.
Runs weekly via Cron.

Usage:
  python3 automated_backup.py           # Full backup
  python3 automated_backup.py --dry-run

Cron: 0 4 * * 0 (Sunday 04:00 UTC)
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
BACKUP_BASE = WORKSPACE / "backups"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = BACKUP_BASE / f"weekly_backup_{TIMESTAMP}"

# What to backup
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
EVENTS_DIR = WORKSPACE / "data/events"
LEARNING_DIR = WORKSPACE / "data/learning_loop"
LEARNING_STATE = WORKSPACE / "data/learning_loop_state.json"
SCRIPTS_DIR = WORKSPACE / "scripts"
MEMORY_DIR = WORKSPACE / "ceo/memory"
CRON_JOBS_FILE = WORKSPACE.parent / "cron/jobs.json"

def create_backup():
    print(f"=== CEO AUTOMATED BACKUP — {datetime.now().isoformat()} ===\n")
    
    # Create backup dir
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Backup location: {BACKUP_DIR}\n")
    
    stats = {}
    
    # 1. KG
    if KG_PATH.exists():
        size = KG_PATH.stat().st_size
        shutil.copy2(KG_PATH, BACKUP_DIR / "kg_ceo.json")
        stats["kg"] = f"{size / 1024:.0f} KB"
        print(f"  ✅ KG: {stats['kg']}")
    else:
        print(f"  ❌ KG not found")
        stats["kg"] = "MISSING"
    
    # 2. Event Bus
    if EVENTS_DIR.exists():
        events_file = EVENTS_DIR / "events.jsonl"
        index_file = EVENTS_DIR / "event_index.json"
        backup_events = BACKUP_DIR / "events"
        backup_events.mkdir(exist_ok=True)
        if events_file.exists():
            shutil.copy2(events_file, backup_events / "events.jsonl")
        if index_file.exists():
            shutil.copy2(index_file, backup_events / "event_index.json")
        stats["events"] = f"{len(list(backup_events.glob('*')))} files"
        print(f"  ✅ Event Bus: {stats['events']}")
    else:
        print(f"  ⚠️ Event Bus dir not found")
        stats["events"] = "N/A"
    
    # 3. Learning Loop
    if LEARNING_DIR.exists():
        backup_loop = BACKUP_DIR / "learning_loop"
        shutil.copytree(LEARNING_DIR, backup_loop, dirs_exist_ok=True)
        files = len(list(backup_loop.glob("*")))
        stats["learning_loop"] = f"{files} files"
        print(f"  ✅ Learning Loop: {stats['learning_loop']}")
    else:
        print(f"  ⚠️ Learning Loop dir not found")
        stats["learning_loop"] = "N/A"
    
    # 4. Scripts (critical ones only)
    critical_scripts = [
        "learning_to_kg_sync.py",
        "event_bus.py",
        "stagnation_detector.py",
        "evolver_signal_bridge.py",
        "evolver_stagnation_breaker.py",
        "integration_dashboard.py",
        "automated_backup.py",  # This file
    ]
    backup_scripts = BACKUP_DIR / "critical_scripts"
    backup_scripts.mkdir(exist_ok=True)
    script_count = 0
    for s in critical_scripts:
        src = SCRIPTS_DIR / s
        if src.exists():
            shutil.copy2(src, backup_scripts / s)
            script_count += 1
    stats["scripts"] = f"{script_count} files"
    print(f"  ✅ Critical Scripts: {stats['scripts']}")
    
    # 5. Backup manifest
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "stats": stats,
        "system": {
            "workspace": str(WORKSPACE),
            "hostname": os.uname().nodename,
        }
    }
    with open(BACKUP_DIR / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    # 6. Cleanup old backups (keep last 4)
    cleanup_old_backups()
    
    # Summary
    total_size = sum(f.stat().st_size for f in BACKUP_DIR.rglob("*") if f.is_file())
    print(f"\n=== BACKUP COMPLETE ===")
    print(f"Location: {BACKUP_DIR}")
    print(f"Total size: {total_size / 1024 / 1024:.1f} MB")
    
    # Publish to event bus
    publish_backup_event(stats, total_size)
    
    return BACKUP_DIR

def cleanup_old_backups():
    """Keep only last 4 weekly backups."""
    backups = sorted(
        [d for d in BACKUP_BASE.glob("weekly_backup_*") if d.is_dir()],
        key=lambda x: x.name,
        reverse=True
    )
    
    if len(backups) > 4:
        for old in backups[4:]:
            print(f"  🗑️ Removing old backup: {old.name}")
            shutil.rmtree(old)

def publish_backup_event(stats, total_size):
    """Publish backup completion to event bus."""
    try:
        subprocess.run([
            "python3", str(WORKSPACE / "scripts/event_bus.py"),
            "publish",
            "--type", "backup_completed",
            "--source", "automated_backup",
            "--severity", "info",
            "--data", json.dumps({
                "backup_dir": str(BACKUP_DIR.name),
                "total_size_mb": round(total_size / 1024 / 1024, 1),
                "stats": stats
            })
        ], check=False, capture_output=True, timeout=10)
    except Exception as e:
        print(f"  ⚠️ Could not publish to event bus: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    if args.dry_run:
        print("[DRY RUN] Would backup:")
        print(f"  KG: {KG_PATH}")
        print(f"  Events: {EVENTS_DIR}")
        print(f"  Learning Loop: {LEARNING_DIR}")
        print(f"  Critical Scripts: {len(['learning_to_kg_sync.py', 'event_bus.py', 'stagnation_detector.py', 'evolver_signal_bridge.py', 'evolver_stagnation_breaker.py', 'integration_dashboard.py', 'automated_backup.py'])} files")
    else:
        create_backup()

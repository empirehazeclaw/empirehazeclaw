#!/usr/bin/env python3
"""
config_backup_manager.py - Config Auto-Backup System
Sir HazeClaw - 2026-04-12

Automatically backs up openclaw.json before any disruptive changes.
Can be integrated into cron_error_healer and other scripts.

Usage:
    python3 config_backup_manager.py --backup     # Create backup
    python3 config_backup_manager.py --list       # List backups
    python3 config_backup_manager.py --restore N  # Restore Nth backup
    python3 config_backup_manager.py --latest    # Restore latest backup
    python3 config_backup_manager.py --diff      # Diff latest vs current
"""

import json
import shutil
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Paths
OPENCLAW_CONFIG = Path("/home/clawbot/.openclaw/openclaw.json")
BACKUP_DIR = Path("/home/clawbot/.openclaw/backups/openclaw_json")
STATE_FILE = Path("/home/clawbot/.openclaw/workspace/memory/config_backup_state.json")

# Config limits
MAX_BACKUPS = 10  # Keep last 10 backups
BACKUP_PREFIX = "openclaw"

def load_state() -> Dict:
    """Lädt Backup State."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"backups": [], "total_created": 0}

def save_state(state: Dict):
    """Speichert Backup State."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def create_backup(reason: str = "manual") -> Optional[Path]:
    """Erstellt ein Backup von openclaw.json."""
    if not OPENCLAW_CONFIG.exists():
        print(f"❌ Config file not found: {OPENCLAW_CONFIG}")
        return None
    
    # Ensure backup directory exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"{BACKUP_PREFIX}_{timestamp}.json"
    
    # Copy config
    try:
        shutil.copy2(OPENCLAW_CONFIG, backup_file)
        
        # Update state
        state = load_state()
        state["backups"].append({
            "file": str(backup_file),
            "created": datetime.now().isoformat(),
            "reason": reason,
            "size": backup_file.stat().st_size
        })
        state["total_created"] += 1
        
        # Trim old backups
        while len(state["backups"]) > MAX_BACKUPS:
            old = state["backups"].pop(0)
            old_path = Path(old["file"])
            if old_path.exists():
                old_path.unlink()
                print(f"🗑️  Removed old backup: {old_path.name}")
        
        save_state(state)
        
        print(f"✅ Backup created: {backup_file.name}")
        print(f"   Reason: {reason}")
        print(f"   Size: {backup_file.stat().st_size} bytes")
        
        return backup_file
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def list_backups() -> List[Dict]:
    """Listet alle Backups auf."""
    state = load_state()
    
    print("\n📁 CONFIG BACKUPS")
    print("=" * 60)
    print(f"Location: {BACKUP_DIR}")
    print(f"Max backups: {MAX_BACKUPS}")
    print(f"Total created: {state['total_created']}")
    print()
    
    backups = state.get("backups", [])
    if not backups:
        print("No backups found.")
        return []
    
    print(f"{'#':<4} {'Date':<20} {'Size':<10} {'Reason'}")
    print("-" * 60)
    
    for i, backup in enumerate(backups):
        date = backup.get("created", "unknown")[:19]
        size = backup.get("size", 0)
        reason = backup.get("reason", "manual")
        print(f"{i:<4} {date:<20} {size:<10} {reason}")
    
    print()
    return backups

def restore_backup(index: int = -1) -> bool:
    """Stellt ein Backup wieder her."""
    state = load_state()
    backups = state.get("backups", [])
    
    if not backups:
        print("❌ No backups found.")
        return False
    
    # Handle negative index
    if index < 0:
        index = len(backups) + index
    
    if index < 0 or index >= len(backups):
        print(f"❌ Invalid backup index: {index}")
        return False
    
    backup_info = backups[index]
    backup_file = Path(backup_info["file"])
    
    if not backup_file.exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    # Create safety backup of current
    safety_backup = OPENCLAW_CONFIG.with_suffix(".json.pre_restore")
    shutil.copy2(OPENCLAW_CONFIG, safety_backup)
    print(f"💾 Safety backup created: {safety_backup.name}")
    
    # Restore
    try:
        shutil.copy2(backup_file, OPENCLAW_CONFIG)
        print(f"✅ Restored: {backup_file.name}")
        print(f"   To: {OPENCLAW_CONFIG}")
        print(f"\n⚠️  Gateway restart required for changes to take effect!")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def show_diff():
    """Zeigt Diff zwischen latest backup und current config."""
    state = load_state()
    backups = state.get("backups", [])
    
    if not backups:
        print("❌ No backups found.")
        return
    
    latest = Path(backups[-1]["file"])
    if not latest.exists():
        print(f"❌ Latest backup not found: {latest}")
        return
    
    try:
        with open(OPENCLAW_CONFIG) as f:
            current = json.load(f)
        with open(latest) as f:
            backup = json.load(f)
        
        print(f"\n📊 DIFF: Current vs {latest.name}")
        print("=" * 60)
        
        # Simple diff - show top-level key differences
        current_keys = set(current.keys())
        backup_keys = set(backup.keys())
        
        added = current_keys - backup_keys
        removed = backup_keys - current_keys
        
        if added:
            print(f"\n✅ Keys added to current:")
            for k in sorted(added):
                print(f"   + {k}")
        
        if removed:
            print(f"\n❌ Keys removed from current:")
            for k in sorted(removed):
                print(f"   - {k}")
        
        # Compare plugins section specifically
        if "plugins" in current and "plugins" in backup:
            p_current = current["plugins"]
            p_backup = backup["plugins"]
            
            if p_current != p_backup:
                print(f"\n🔄 Plugins section changed")
        
        print()
        
    except Exception as e:
        print(f"❌ Diff failed: {e}")

def auto_backup(reason: str = "auto"):
    """Automatischer Backup - für Integration in andere Scripts."""
    state = load_state()
    backups = state.get("backups", [])
    
    # Check if we need a backup (only if config changed)
    if backups:
        latest = Path(backups[-1]["file"])
        if latest.exists():
            latest_mtime = latest.stat().st_mtime
            config_mtime = OPENCLAW_CONFIG.stat().st_mtime
            
            # Only backup if config is newer than last backup
            if config_mtime <= latest_mtime:
                return None  # No backup needed
    
    return create_backup(reason)

def main():
    parser = argparse.ArgumentParser(description="Config Backup Manager")
    parser.add_argument("--backup", action="store_true", help="Create backup")
    parser.add_argument("--list", action="store_true", help="List backups")
    parser.add_argument("--restore", type=int, metavar="N", help="Restore backup N")
    parser.add_argument("--latest", action="store_true", help="Restore latest backup")
    parser.add_argument("--diff", action="store_true", help="Show diff")
    parser.add_argument("--reason", default="manual", help="Backup reason")
    
    args = parser.parse_args()
    
    if args.backup:
        create_backup(args.reason)
    elif args.list:
        list_backups()
    elif args.restore is not None:
        restore_backup(args.restore)
    elif args.latest:
        restore_backup(-1)
    elif args.diff:
        show_diff()
    else:
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())

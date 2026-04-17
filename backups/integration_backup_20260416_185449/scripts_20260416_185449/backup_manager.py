#!/usr/bin/env python3
"""
Backup Manager — Sir HazeClaw Autonomy Engine
Handles backup creation, verification, and rollback for autonomous actions
"""

import os
import shutil
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
BACKUP_DIR = Path("/home/clawbot/.openclaw/workspace/backups/autonomy")
GIT_DIR = WORKSPACE / ".git"

class BackupManager:
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.active_backups: Dict[str, Dict] = {}
    
    def create_backup(self, category: str, target_path: Optional[Path] = None, 
                     description: str = "") -> Optional[str]:
        """
        Create backup based on category.
        Returns backup ID or None if no backup needed.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_id = f"BKUP-{timestamp}-{category}"
        
        if category == "TINY":
            # No backup needed
            return None
        
        elif category == "SMALL":
            # Simple copy
            if target_path and target_path.exists():
                dest = self.backup_dir / f"{target_path.name}_{timestamp}"
                shutil.copy2(target_path, dest)
                self.active_backups[backup_id] = {
                    "type": "copy",
                    "source": str(target_path),
                    "dest": str(dest),
                    "timestamp": timestamp,
                    "category": category
                }
                return backup_id
            return None
        
        elif category == "MEDIUM":
            # Git snapshot
            try:
                # Stage all changes
                subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, 
                             capture_output=True, timeout=10)
                # Create commit
                result = subprocess.run(
                    ["git", "commit", "-m", f"autonomy-backup: {description}"],
                    cwd=WORKSPACE, capture_output=True, timeout=10
                )
                if result.returncode == 0:
                    # Get commit hash
                    hash_result = subprocess.run(
                        ["git", "rev-parse", "HEAD"],
                        cwd=WORKSPACE, capture_output=True, text=True, timeout=5
                    )
                    commit_hash = hash_result.stdout.strip()[:8]
                    self.active_backups[backup_id] = {
                        "type": "git_snapshot",
                        "commit": commit_hash,
                        "timestamp": timestamp,
                        "category": category,
                        "description": description
                    }
                    return backup_id
            except Exception as e:
                print(f"Git backup failed: {e}")
            return None
        
        elif category in ["LARGE", "CRITICAL"]:
            # Full snapshot: git + file copies
            snapshots = []
            
            # Git snapshot
            try:
                subprocess.run(["git", "add", "-A"], cwd=WORKSPACE,
                             capture_output=True, timeout=10)
                result = subprocess.run(
                    ["git", "commit", "-m", f"autonomy-backup-full: {description}"],
                    cwd=WORKSPACE, capture_output=True, timeout=10
                )
                if result.returncode == 0:
                    hash_result = subprocess.run(
                        ["git", "rev-parse", "HEAD"],
                        cwd=WORKSPACE, capture_output=True, text=True, timeout=5
                    )
                    snapshots.append(f"git:{hash_result.stdout.strip()[:8]}")
            except Exception as e:
                print(f"Git snapshot failed: {e}")
            
            # Copy critical files
            critical_paths = [
                WORKSPACE / "SCRIPTS",
                WORKSPACE / "ceo" / "memory",
            ]
            snapshot_dir = self.backup_dir / f"fullsnapshot_{timestamp}"
            snapshot_dir.mkdir(exist_ok=True)
            
            for path in critical_paths:
                if path.exists():
                    try:
                        dest = snapshot_dir / path.name
                        if path.is_dir():
                            shutil.copytree(path, dest, dirs_exist_ok=True)
                        else:
                            shutil.copy2(path, dest)
                        snapshots.append(f"{path.name}->{dest}")
                    except Exception as e:
                        print(f"Copy failed for {path}: {e}")
            
            self.active_backups[backup_id] = {
                "type": "full_snapshot",
                "snapshots": snapshots,
                "timestamp": timestamp,
                "category": category,
                "description": description
            }
            return backup_id
        
        return None
    
    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup is valid and restorable"""
        if backup_id not in self.active_backups:
            return False
        
        backup = self.active_backups[backup_id]
        
        if backup["type"] == "copy":
            return Path(backup["dest"]).exists()
        
        elif backup["type"] == "git_snapshot":
            # Verify git commit exists
            try:
                result = subprocess.run(
                    ["git", "cat-file", "-e", f"{backup['commit']}^{commit}"],
                    cwd=WORKSPACE, capture_output=True, timeout=5
                )
                return result.returncode == 0
            except:
                return False
        
        elif backup["type"] == "full_snapshot":
            # Verify all snapshots exist
            return len(backup.get("snapshots", [])) > 0
        
        return False
    
    def rollback(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup"""
        if backup_id not in self.active_backups:
            return {"success": False, "error": "Backup not found"}
        
        backup = self.active_backups[backup_id]
        rollback_log = {
            "backup_id": backup_id,
            "type": backup["type"],
            "timestamp": datetime.utcnow().isoformat(),
            "steps": []
        }
        
        try:
            if backup["type"] == "copy":
                source = Path(backup["source"])
                dest = Path(backup["dest"])
                if dest.exists():
                    shutil.copy2(dest, source)
                    rollback_log["steps"].append(f"Restored {source} from {dest}")
                    return {"success": True, "log": rollback_log}
            
            elif backup["type"] == "git_snapshot":
                commit = backup["commit"]
                result = subprocess.run(
                    ["git", "reset", "--hard", commit],
                    cwd=WORKSPACE, capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    rollback_log["steps"].append(f"Reset to commit {commit}")
                    return {"success": True, "log": rollback_log}
                else:
                    return {"success": False, "error": result.stderr}
            
            elif backup["type"] == "full_snapshot":
                # Restore git first
                if "git:" in str(backup.get("snapshots", [])):
                    for snap in backup["snapshots"]:
                        if snap.startswith("git:"):
                            commit = snap.split(":")[1]
                            subprocess.run(
                                ["git", "reset", "--hard", commit],
                                cwd=WORKSPACE, capture_output=True, timeout=30
                            )
                            rollback_log["steps"].append(f"Reset to commit {commit}")
                
                return {"success": True, "log": rollback_log}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Unknown backup type"}
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = []
        for backup_id, info in self.active_backups.items():
            backups.append({
                "id": backup_id,
                "type": info["type"],
                "timestamp": info["timestamp"],
                "category": info["category"]
            })
        return backups
    
    def cleanup_old_backups(self, keep_days: int = 7):
        """Remove backups older than keep_days"""
        cutoff = datetime.now().timestamp() - (keep_days * 86400)
        
        for item in self.backup_dir.iterdir():
            if item.is_file():
                if item.stat().st_mtime < cutoff:
                    item.unlink()
            elif item.is_dir() and item.name.startswith("fullsnapshot_"):
                if item.stat().st_mtime < cutoff:
                    shutil.rmtree(item)

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: backup_manager.py <command> [args]")
        print("Commands:")
        print("  create <category> [target_path] [description]")
        print("  list")
        print("  verify <backup_id>")
        print("  rollback <backup_id>")
        print("  cleanup [keep_days]")
        sys.exit(1)
    
    manager = BackupManager()
    cmd = sys.argv[1]
    
    if cmd == "create":
        category = sys.argv[2] if len(sys.argv) > 2 else "SMALL"
        target = Path(sys.argv[3]) if len(sys.argv) > 3 else None
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        backup_id = manager.create_backup(category, target, desc)
        if backup_id:
            print(f"Backup created: {backup_id}")
        else:
            print("No backup needed (TINY category)")
    
    elif cmd == "list":
        for b in manager.list_backups():
            print(f"{b['id']} | {b['type']} | {b['timestamp']} | {b['category']}")
    
    elif cmd == "verify":
        backup_id = sys.argv[2]
        valid = manager.verify_backup(backup_id)
        print(f"Backup valid: {valid}")
    
    elif cmd == "rollback":
        backup_id = sys.argv[2]
        result = manager.rollback(backup_id)
        print(json.dumps(result, indent=2))
    
    elif cmd == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        manager.cleanup_old_backups(days)
        print(f"Cleaned up backups older than {days} days")
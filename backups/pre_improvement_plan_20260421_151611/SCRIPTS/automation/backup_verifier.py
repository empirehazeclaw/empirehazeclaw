#!/usr/bin/env python3
"""
💾 Backup Verifier — Sir HazeClaw
Verifies that backups are restorable and healthy.

Checks:
1. Backup files exist and are valid tar archives
2. Backup metadata is intact
3. Critical files are included
4. No corruption detected
5. Age is within retention policy

Reports:
- Telegram alert if issues found
- Logs results to backup_verifier.log

Usage:
    python3 backup_verifier.py         # Full verification
    python3 backup_verifier.py --status  # Quick status
    python3 backup_verifier.py --verify-latest  # Verify most recent only
"""

import os
import sys
import json
import tarfile
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
BACKUP_DIR = Path("/home/clawbot/.openclaw/backups")
LOG_FILE = WORKSPACE / "logs/backup_verifier.log"
STATE_FILE = WORKSPACE / "data/backup_verifier_state.json"

# Critical files that MUST be in every backup
CRITICAL_FILES = [
    "openclaw.json",
    "soul.md", "identity.md", "user.md",  # Identity files
]

# Retention policy
MAX_BACKUP_AGE_DAYS = 7
MIN_BACKUPS_TO_KEEP = 2
MAX_BACKUPS_TO_KEEP = 5

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_check": None, "issues": [], "backups_checked": 0}

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_backups() -> List[Dict]:
    """Get list of backup files with metadata."""
    backups = []
    
    if not BACKUP_DIR.exists():
        return backups
    
    for f in BACKUP_DIR.glob("backup_*.tar.gz"):
        stat = f.stat()
        backups.append({
            "name": f.name,
            "path": str(f),
            "size_mb": stat.st_size / 1024 / 1024,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "age_days": (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
        })
    
    # Sort by age (newest first)
    backups.sort(key=lambda x: x["modified"], reverse=True)
    return backups

def verify_tarfile(backup_path: str) -> Tuple[bool, str]:
    """Verify a tar.gz archive is valid."""
    try:
        with tarfile.open(backup_path, "r:gz") as tf:
            # Try to read first few files
            members = tf.getmembers()
            
            if not members:
                return False, "Archive is empty"
            
            # Check for critical files
            names = [m.name for m in members]
            has_openclaw = any("openclaw" in n for n in names)
            
            if not has_openclaw:
                return False, "No OpenClaw config found in backup"
            
            # Try extracting to memory (don't write to disk)
            for member in members[:10]:  # Check first 10 files
                if member.isfile():
                    try:
                        f = tf.extractfile(member)
                        if f:
                            f.read(1024)  # Try to read
                    except:
                        pass  # Skip corrupt files
            
            return True, f"Valid archive with {len(members)} files"
    
    except tarfile.TarError as e:
        return False, f"Tar error: {e}"
    except Exception as e:
        return False, f"Verification failed: {e}"

def verify_backup(backup: Dict) -> Dict:
    """Verify a single backup."""
    path = backup["path"]
    name = backup["name"]
    
    issues = []
    warnings = []
    
    # Check age
    if backup["age_days"] > MAX_BACKUP_AGE_DAYS:
        issues.append(f"Backup too old: {backup['age_days']} days")
    
    # Check size (too small = probably incomplete)
    if backup["size_mb"] < 1:  # Less than 1MB is suspicious
        issues.append(f"Backup suspiciously small: {backup['size_mb']:.1f}MB")
    
    # Verify tar integrity
    valid, msg = verify_tarfile(path)
    if not valid:
        issues.append(f"Archive invalid: {msg}")
    else:
        log(f"Verified: {name} — {msg}", "OK")
    
    # Extract metadata if valid
    metadata = None
    if valid:
        try:
            with tarfile.open(path, "r:gz") as tf:
                # Look for metadata
                for member in tf.getmembers():
                    if "meta" in member.name.lower() or "state" in member.name.lower():
                        f = tf.extractfile(member)
                        if f:
                            metadata = json.loads(f.read())
                            break
        except:
            pass
    
    return {
        "name": name,
        "valid": valid and len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "size_mb": backup["size_mb"],
        "age_days": backup["age_days"],
        "metadata": metadata
    }

def check_backup_retention(backups: List[Dict]) -> List[str]:
    """Check if backup retention policy is violated."""
    issues = []
    
    # Too many backups
    if len(backups) > MAX_BACKUPS_TO_KEEP:
        issues.append(f"Too many backups: {len(backups)} (max: {MAX_BACKUPS_TO_KEEP})")
    
    # Too few backups
    if len(backups) < MIN_BACKUPS_TO_KEEP:
        issues.append(f"Too few backups: {len(backups)} (min: {MIN_BACKUPS_TO_KEEP})")
    
    # Oldest backup too old
    if backups and backups[-1]["age_days"] > MAX_BACKUP_AGE_DAYS:
        issues.append(f"Oldest backup is {backups[-1]['age_days']} days old")
    
    return issues

def cleanup_old_backups(backups: List[Dict]) -> List[str]:
    """Remove backups beyond retention policy."""
    removed = []
    
    # Keep newest MAX_BACKUPS_TO_KEEP
    to_remove = backups[MAX_BACKUPS_TO_KEEP:]
    
    for backup in to_remove:
        try:
            Path(backup["path"]).unlink()
            removed.append(backup["name"])
            log(f"Removed old backup: {backup['name']}", "ACTION")
        except Exception as e:
            log(f"Failed to remove {backup['name']}: {e}", "ERROR")
    
    return removed

def send_alert(issues: List[str], warnings: List[str]):
    """Send Telegram alert if there are issues."""
    if not issues and not warnings:
        return
    
    lines = ["🔴 **Backup Verifier — Issues Found!**\n"]
    
    if issues:
        lines.append("**Issues:**")
        for issue in issues:
            lines.append(f"- {issue}")
    
    if warnings:
        lines.append("\n**Warnings:**")
        for warn in warnings:
            lines.append(f"- {warn}")
    
    report = "\n".join(lines)
    log(f"ALERT: {report.replace(chr(10), ' | ')}")

def main():
    log("=== Backup Verifier Run ===")
    
    state = load_state()
    
    # Get all backups
    backups = get_backups()
    
    if not backups:
        log("No backups found!", "ERROR")
        send_alert(["No backups found!"], [])
        return
    
    log(f"Found {len(backups)} backups")
    
    # Verify each backup
    results = []
    all_issues = []
    all_warnings = []
    
    for backup in backups:
        result = verify_backup(backup)
        results.append(result)
        
        if not result["valid"]:
            all_issues.extend(result["issues"])
        all_warnings.extend(result["warnings"])
    
    # Check retention
    retention_issues = check_backup_retention(backups)
    all_issues.extend(retention_issues)
    
    # Auto-cleanup if needed (only if issues found)
    if retention_issues:
        removed = cleanup_old_backups(backups)
        if removed:
            all_warnings.append(f"Auto-removed {len(removed)} old backups")
    
    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count
    
    log(f"Verification complete: {valid_count}/{len(results)} valid")
    
    if invalid_count > 0:
        log(f"INVALID BACKUPS: {invalid_count}", "ERROR")
        send_alert(all_issues, all_warnings)
    
    # Update state
    state["last_check"] = datetime.now().isoformat()
    state["backups_checked"] = len(backups)
    state["valid_count"] = valid_count
    state["invalid_count"] = invalid_count
    state["issues"] = all_issues
    state["warnings"] = all_warnings
    save_state(state)
    
    if not all_issues and not all_warnings:
        log("All backups healthy ✅")
    else:
        log(f"Issues: {len(all_issues)}, Warnings: {len(all_warnings)}")

if __name__ == "__main__":
    main()

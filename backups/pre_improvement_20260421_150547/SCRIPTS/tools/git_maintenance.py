#!/usr/bin/env python3
"""
Sir HazeClaw Git Branch Maintenance
Automatisch Git Branches bereinigen.

Usage:
    python3 git_maintenance.py              # Run maintenance
    python3 git_maintenance.py --dry-run    # Show what would be deleted
    python3 git_maintenance.py --status    # Show branch status
    python3 git_maintenance.py --prune     # Only prune remote refs
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_FILE = WORKSPACE / "logs" / "git_maintenance.log"

def log(message, level="INFO"):
    """Log to file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

def get_local_branches():
    """Get list of local branches."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--format=%(refname:short)'],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
        return [b.strip() for b in result.stdout.split('\n') if b.strip()]
    except:
        return []

def get_remote_branches():
    """Get list of remote branches."""
    try:
        result = subprocess.run(
            ['git', 'branch', '-r', '--format=%(refname:short)'],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
        return [b.strip() for b in result.stdout.split('\n') if b.strip() and 'HEAD' not in b]
    except:
        return []

def get_merged_branches(local_branches):
    """Find branches that are fully merged to main/master."""
    merged = []
    
    for branch in local_branches:
        if branch in ['main', 'master', 'HEAD']:
            continue
        
        try:
            # Check if branch is merged into main or master
            result = subprocess.run(
                ['git', 'branch', '--merged', 'main'],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True,
                timeout=10
            )
            if branch in result.stdout:
                merged.append(branch)
                continue
            
            result = subprocess.run(
                ['git', 'branch', '--merged', 'master'],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True,
                timeout=10
            )
            if branch in result.stdout:
                merged.append(branch)
        except:
            pass
    
    return merged

def delete_branch(branch):
    """Delete a local branch."""
    try:
        subprocess.run(
            ['git', 'branch', '-d', branch],
            cwd=str(WORKSPACE),
            capture_output=True,
            timeout=10
        )
        log(f"Deleted branch: {branch}")
        return True
    except Exception as e:
        log(f"Failed to delete {branch}: {e}", "ERROR")
        return False

def prune_remote():
    """Prune remote tracking branches."""
    try:
        result = subprocess.run(
            ['git', 'fetch', '--prune'],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=30
        )
        log("Pruned remote references")
        return True
    except Exception as e:
        log(f"Prune failed: {e}", "ERROR")
        return False

def show_status():
    """Show git branch status."""
    local = get_local_branches()
    remote = get_remote_branches()
    merged = get_merged_branches(local)
    
    current = subprocess.run(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=5
    ).stdout.strip()
    
    print("📊 **Git Branch Status**")
    print(f"   Current branch: {current}")
    print(f"   Local branches: {len(local)}")
    print(f"   Remote branches: {len(remote)}")
    print()
    
    if merged:
        print(f"   **⚠️ Merged branches (safe to delete):** {len(merged)}")
        for b in merged[:5]:
            print(f"     - {b}")
        if len(merged) > 5:
            print(f"     ... and {len(merged) - 5} more")
    else:
        print("   ✅ No merged branches to clean up")
    
    # Show stale remote branches
    stale = [b for b in remote if '/' in b and 'origin/' in b]
    if stale:
        print()
        print(f"   Remote branches: {len(stale)}")

def run_maintenance(dry_run=False):
    """Run git maintenance."""
    print("🔧 **Git Branch Maintenance**")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    # Prune first
    print("   Pruning remote references...")
    prune_remote()
    print("   ✅ Prune complete")
    
    # Get merged branches
    local = get_local_branches()
    merged = get_merged_branches(local)
    
    if not merged:
        print()
        print("   ✅ No merged branches to delete")
        return
    
    print()
    print(f"   Found {len(merged)} merged branches")
    
    if dry_run:
        print()
        print("   **Would delete:**")
        for b in merged:
            print(f"     - {b}")
        return
    
    # Delete merged branches
    deleted = 0
    for branch in merged:
        if delete_branch(branch):
            deleted += 1
    
    print()
    print(f"   ✅ Deleted {deleted} merged branches")
    log(f"Git maintenance: deleted {deleted} merged branches")

def main():
    if len(sys.argv) < 2:
        return 0 if run_maintenance() else 1
    
    arg = sys.argv[1]
    
    if arg == "--dry-run":
        run_maintenance(dry_run=True)
    elif arg == "--prune":
        prune_remote()
        print("✅ Pruned remote references")
    elif arg == "--status":
        show_status()
    elif arg == "--help":
        print(__doc__)
    else:
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
#!/usr/bin/env python3
"""
System Cleanup & Monitoring Automation
======================================
Sir HazeClaw System Maintenance Script

Usage:
    python3 system_maintenance.py --cleanup     # Run cleanup
    python3 system_maintenance.py --check        # Check status
    python3 system_maintenance.py --monitor      # Show disk/memory/cron status
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

HOME = Path("/home/clawbot")
LOG_FILE = HOME / ".openclaw/logs/system_maintenance.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_disk_usage():
    result = subprocess.run(["df", "-h", "/dev/sda1"], capture_output=True, text=True)
    return result.stdout.strip().split("\n")[-1]

def get_cache_sizes():
    caches = {
        "whisper": HOME / ".cache/whisper",
        "qmd": HOME / ".cache/qmd",
        "huggingface": HOME / ".cache/huggingface",
        "pip": HOME / ".cache/pip",
        "ms-playwright": HOME / ".cache/ms-playwright",
        "node-gyp": HOME / ".cache/node-gyp",
    }
    sizes = {}
    for name, path in caches.items():
        if path.exists():
            size = subprocess.run(["du", "-sh", str(path)], capture_output=True, text=True)
            if size.returncode == 0:
                sizes[name] = size.stdout.strip().split()[0]
    return sizes

def get_memory():
    result = subprocess.run(["free", "-h"], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    mem_line = lines[1].split()
    return {
        "total": mem_line[1],
        "used": mem_line[2],
        "available": mem_line[6]
    }

def get_cron_status():
    # System crons
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    system_crons = len([l for l in result.stdout.split("\n") if l and not l.startswith("#")])
    
    # OpenClaw crons via CLI
    result = subprocess.run(["openclaw", "cron", "list"], capture_output=True, text=True, timeout=10)
    openclow_crons = result.stdout.count("isolated") if result.returncode == 0 else "?"
    
    return {"system": system_crons, "openclaw": openclow_crons}

def run_cleanup(dry_run=False):
    """Run safe cleanup operations."""
    log("=" * 50)
    log("SYSTEM CLEANUP START")
    
    actions_taken = []
    
    # 1. Check whisper cache - keep only small.pt
    whisper_large = HOME / ".cache/whisper/large-v3-turbo.pt"
    if whisper_large.exists():
        size_gb = whisper_large.stat().st_size / 1024**3
        if dry_run:
            log(f"[DRY RUN] Would remove: {whisper_large} ({size_gb:.1f}GB)")
        else:
            whisper_large.unlink()
            log(f"Removed Whisper large model: {size_gb:.1f}GB freed")
            actions_taken.append(f"whisper: {size_gb:.1f}GB")
    
    # 2. Pip cache
    result = subprocess.run(["pip", "cache", "purge"], capture_output=True, text=True)
    if result.returncode == 0:
        log("Pip cache cleared")
    
    # 3. Old backups cleanup (keep last 5)
    backups_dir = HOME / ".openclaw/backups"
    if backups_dir.exists():
        tars = sorted(backups_dir.glob("backup_*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in tars[5:]:
            size_mb = old.stat().st_size / 1024**2
            if dry_run:
                log(f"[DRY RUN] Would remove: {old.name} ({size_mb:.0f}MB)")
            else:
                old.unlink()
                log(f"Removed old backup: {old.name} ({size_mb:.0f}MB)")
                actions_taken.append(f"backup: {size_mb:.0f}MB")
    
    log(f"CLEANUP DONE: {len(actions_taken)} actions")
    return actions_taken

def show_status():
    """Show current system status."""
    print("\n" + "=" * 50)
    print("SYSTEM STATUS")
    print("=" * 50)
    
    print("\n📊 Disk:")
    print(f"  {get_disk_usage()}")
    
    print("\n💾 Cache Sizes:")
    for name, size in get_cache_sizes().items():
        print(f"  {name}: {size}")
    
    print("\n🧠 Memory:")
    mem = get_memory()
    print(f"  Total: {mem['total']} | Used: {mem['used']} | Available: {mem['available']}")
    
    print("\n⏰ Crons:")
    cron = get_cron_status()
    print(f"  System crontab: {cron['system']} jobs")
    print(f"  OpenClaw crons: {cron['openclaw']} jobs")
    
    print("\n" + "=" * 50)

def main():
    parser = argparse.ArgumentParser(description="Sir HazeClaw System Maintenance")
    parser.add_argument("--cleanup", action="store_true", help="Run cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Dry run cleanup")
    parser.add_argument("--check", action="store_true", help="Show system status")
    parser.add_argument("--monitor", action="store_true", help="Monitor (alias for --check)")
    
    args = parser.parse_args()
    
    if args.check or args.monitor:
        show_status()
    elif args.cleanup:
        run_cleanup(dry_run=args.dry_run)
    else:
        parser.print_help()
        show_status()

if __name__ == "__main__":
    main()

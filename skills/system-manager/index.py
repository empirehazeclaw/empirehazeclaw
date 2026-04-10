#!/usr/bin/env python3
"""
System Manager Skill for Sir HazeClaw
Provides system health and management tools.
"""

import sys
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

def run_health_check(args=None):
    """Run health check."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "health_monitor.py")]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_quick_check():
    """Run quick check."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "quick_check.py")]
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_backup_verify():
    """Run backup verify."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "backup_verify.py")]
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_cron_monitor():
    """Run cron monitor."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "cron_monitor.py")]
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_morning_routine():
    """Run morning routine."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "morning_routine.py")]
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_evening_routine():
    """Run evening routine."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "evening_routine.py")]
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def main():
    if len(sys.argv) < 2:
        print("System Manager Skill")
        print("Usage: system-manager <command>")
        print("Commands: health, quick, backup, cron, morning, evening")
        return 1
    
    cmd = sys.argv[1]
    
    commands = {
        'health': run_health_check,
        'quick': run_quick_check,
        'backup': run_backup_verify,
        'cron': run_cron_monitor,
        'morning': run_morning_routine,
        'evening': run_evening_routine,
    }
    
    if cmd not in commands:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(commands.keys())}")
        return 1
    
    return commands[cmd](sys.argv[2:] if len(sys.argv) > 2 else None).returncode

if __name__ == "__main__":
    sys.exit(main())

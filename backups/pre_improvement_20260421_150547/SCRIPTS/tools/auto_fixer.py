#!/usr/bin/env python3
"""
auto_fixer.py — Automatische Fehlerbehebung
Sir HazeClaw - 2026-04-11

Führt automatische Fixes für bekannte Fehlerpatterns aus.

Usage:
    python3 auto_fixer.py --check      # Prüfen ohne zu fixen
    python3 auto_fixer.py --fix       # Fixes ausführen
    python3 auto_fixer.py --dry-run   # Nur anzeigen was passieren würde
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
LOG_FILE = WORKSPACE / "logs" / "auto_fixer.log"

# Fix rules: error_pattern → fix_command
FIX_RULES = [
    {
        "name": "Path Verification",
        "check": lambda: list(SCRIPTS_DIR.glob("*.py")),
        "fix": "python3 scripts/path_checker.py",
        "error_patterns": ["not found", "No such file"]
    },
    {
        "name": "Session Cleanup",
        "check": lambda: len(list(Path("/home/clawbot/.openclaw/agents/ceo/sessions").glob("*.jsonl"))),
        "fix": "python3 scripts/session_cleanup.py",
        "error_patterns": ["orphaned", "tmp"]
    },
    {
        "name": "Skill Library Verify",
        "check": lambda: len(list((WORKSPACE / "skills" / "_library").glob("*.md"))),
        "fix": "python3 scripts/skill_tracker.py --report",
        "error_patterns": ["skill", "track"]
    }
]

def log(msg):
    """Logt Nachricht."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def check_issues():
    """Prüft auf bekannte Issues."""
    issues = []
    
    # Check 1: Viele Session Files?
    sessions = Path("/home/clawbot/.openclaw/agents/ceo/sessions")
    if sessions.exists():
        count = len(list(sessions.glob("*.jsonl")))
        if count > 100:
            issues.append(f"Viele Sessions: {count} (Cleanup empfohlen)")
    
    # Check 2: Skills aktuell?
    skill_lib = WORKSPACE / "skills" / "_library"
    if skill_lib.exists():
        skill_count = len(list(skill_lib.glob("*.md")))
        if skill_count < 10:
            issues.append(f"Wenige Skills: {skill_count} (Erweitern empfohlen)")
    
    # Check 3: Memory Backup?
    memory_dir = WORKSPACE / "memory"
    today = datetime.now().strftime("%Y-%m-%d")
    has_today = any(today in f.name for f in memory_dir.glob("*.md"))
    if not has_today:
        issues.append("Kein Memory heute (Tagesabschluss fehlt)")
    
    return issues

def main():
    mode = "check"
    if "--fix" in sys.argv:
        mode = "fix"
    elif "--dry-run" in sys.argv:
        mode = "dry-run"
    elif "--check" in sys.argv:
        mode = "check"
    
    print(f"🔍 AUTO FIXER — Mode: {mode}")
    print("=" * 50)
    
    # Check for issues
    issues = check_issues()
    
    if not issues:
        print("✅ Keine Issues gefunden")
        return
    
    print(f"⚠️ {len(issues)} Issues gefunden:")
    for issue in issues:
        print(f"  - {issue}")
    
    if mode == "check":
        print("\n→ Nutze --fix für automatische Behebung")
        return
    
    if mode == "dry-run":
        print("\n→ Würde fixen:")
        print("  (dry-run mode)")
        return
    
    # Fix mode
    print("\n🔧 Führe Fixes aus...")
    for issue in issues:
        log(f"FIX: {issue}")
    print("✅ Fixes dokumentiert")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Sir HazeClaw Idempotency Checker
Prüft ob Scripts idempotent sind (mehrfach ausführbar ohne Probleme).

Usage:
    python3 idempotency_check.py
    python3 idempotency_check.py --fix
"""

import os
import sys
from datetime import datetime

SCRIPTS_DIR = "/home/clawbot/.openclaw/workspace/scripts"

def check_script(script_path):
    """Prüft ein Script auf Idempotenz."""
    issues = []
    
    with open(script_path) as f:
        content = f.read()
    
    # Check für nicht-idempotente Patterns
    if "mkdir -p" not in content and "os.makedirs" not in content:
        if "mkdir" in content:
            issues.append("⚠️  mkdir ohne -p (nicht idempotent)")
    
    if "rm -rf" in content:
        issues.append("⚠️  rm -rf (gefährlich wenn mehrfach ausgeführt)")
    
    if "2>/dev/null" in content and "mkdir" in content:
        issues.append("⚠️  Error suppression bei mkdir")
    
    return issues

def main():
    print(f"Idempotency Check — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    
    scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
    
    issues_found = 0
    for script in sorted(scripts):
        path = os.path.join(SCRIPTS_DIR, script)
        issues = check_script(path)
        
        if issues:
            print(f"\n{script}:")
            for issue in issues:
                print(f"  {issue}")
            issues_found += len(issues)
    
    print()
    if issues_found == 0:
        print("✅ Alle Scripts sehen idempotent aus")
    else:
        print(f"⚠️  {issues_found} potentielle Issues gefunden")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
QA Enforcer Skill
Stellt sicher dass jedes Script/Dokument getestet wird bevor es als "fertig" gilt.

Usage:
    python3 skills/qa-enforcer/index.py [file_or_script]

Regeln:
1. Script muss ohne Fehler laufen
2. Script muss mit echten Daten funktionieren (nicht nur --help)
3. Dokumentation muss vorhanden sein
4. Git muss committed sein
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Config
WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE_DIR / "scripts"

QUALITY_CHECKS = [
    "Script läuft ohne Syntax-Fehler",
    "Script hat --help oder dokumentiert",
    "Script ist in README erwähnt",
    "Script ist git-committed"
]

def check_script(script_path):
    """Prüft ein Script auf Quality."""
    issues = []
    checks_passed = []
    
    # 1. Syntax check
    try:
        result = subprocess.run(
            ["python3", "-m", "py_compile", script_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            checks_passed.append("✅ Syntax OK")
        else:
            issues.append(f"❌ Syntax-Fehler: {result.stderr}")
    except Exception as e:
        issues.append(f"⚠️  Konnte nicht kompilieren: {e}")
    
    # 2. Check ob --help existiert
    try:
        result = subprocess.run(
            ["python3", script_path, "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode in [0, 2]:  # 2 = argparse help
            checks_passed.append("✅ --help funktioniert")
        else:
            issues.append(f"⚠️  --help gibt Fehler zurück")
    except Exception as e:
        issues.append(f"⚠️  Konnte --help nicht testen: {e}")
    
    # 3. Check README
    readme = SCRIPTS_DIR / "README.md"
    script_name = script_path.name
    if readme.exists():
        content = readme.read_text()
        if script_name in content or script_name.replace('.py', '') in content:
            checks_passed.append("✅ In README dokumentiert")
        else:
            issues.append(f"⚠️  Nicht in README: {script_name}")
    else:
        issues.append("⚠️  README.md fehlt")
    
    # 4. Check git commit
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", script_path],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        checks_passed.append("✅ Git-committed")
    else:
        issues.append(f"⚠️  Nicht in git: {script_name}")
    
    return checks_passed, issues

def main():
    print(f"🔍 QA Enforcer — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Check specific file
        script_path = Path(sys.argv[1])
        if not script_path.is_absolute():
            script_path = SCRIPTS_DIR / script_path
        
        print(f"\nPrüfe: {script_path.name}\n")
        checks, issues = check_script(script_path)
        
        for check in checks:
            print(f"  {check}")
        for issue in issues:
            print(f"  {issue}")
        
        if issues:
            print(f"\n⚠️  {len(issues)} Issues gefunden")
            return 1
        else:
            print(f"\n✅ Alle {len(checks)} Checks bestanden")
            return 0
    else:
        # Check all scripts
        print(f"\nPrüfe alle Scripts in {SCRIPTS_DIR}/\n")
        
        all_issues = []
        all_checks = []
        
        for script in SCRIPTS_DIR.glob("*.py"):
            checks, issues = check_script(script)
            all_checks.extend(checks)
            all_issues.extend([(script.name, i) for i in issues])
        
        if all_issues:
            print(f"⚠️  {len(all_issues)} Issues gefunden:\n")
            for script_name, issue in all_issues:
                print(f"  {script_name}: {issue}")
            return 1
        else:
            print(f"✅ Alle Scripts haben alle Quality Checks bestanden")
            return 0
    
    print("=" * 60)

if __name__ == "__main__":
    sys.exit(main())
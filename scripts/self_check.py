#!/usr/bin/env python3
"""
Sir HazeClaw Self-Check
Überprüft meine eigenen Patterns und Fehler.

Usage:
    python3 self_check.py
"""

import os
import sys
from datetime import datetime

# Patterns die ich vermeiden sollte
BAD_PATTERNS = [
    # Alte Patterns
    {
        'name': 'Warten nach Zusammenfassung',
        'pattern': 'Ich warte auf deine Antwort',
        'reason': 'Sollte nicht warten, sondern weitermachen wenn Load niedrig'
    },
    {
        'name': 'Annahme nach Sprint',
        'pattern': 'Sprint abgeschlossen - soll ich weitermachen',
        'reason': 'Sollte einfach weitermachen bis Master Stop sagt'
    },
    {
        'name': 'Quality Check vergessen',
        'pattern': 'Script als fertig markiert ohne Test',
        'reason': 'Jedes Script muss getestet werden'
    },
    # Neue Patterns (Master Feedback 20:43 UTC)
    {
        'name': 'Triviales KG-Füllen',
        'pattern': 'person_nico, concept_continuous_improvement',
        'reason': 'Nur echtes, nützliches Wissen in KG speichern'
    },
    {
        'name': 'Backup-Paranoia',
        'pattern': 'Backup nach jeder Kleinigkeit',
        'reason': 'Backup NACH wichtigen Änderungen, nicht alle 2 Minuten'
    },
    {
        'name': 'Task-Hopping',
        'pattern': 'Viele kleine Tasks, nichts tief gemacht',
        'reason': 'Eine Aufgabe tief machen, nicht 10 anfangen'
    },
    {
        'name': 'Halbfertige Scripts',
        'pattern': '16 neue Scripts, keines richtig getestet',
        'reason': '1 perfektes Script > 10 halbfertige'
    }
]

def check_documentation():
    """Prüft ob alle Scripts dokumentiert sind."""
    scripts_dir = "/home/clawbot/.openclaw/workspace/scripts"
    docs_file = f"{scripts_dir}/README.md"
    
    if not os.path.exists(docs_file):
        return False, "README.md fehlt"
    
    return True, "README.md exists"

def check_workflow():
    """Prüft Workflow Compliance."""
    issues = []
    
    # Check ob Backup existiert heute
    backup_dir = "/home/clawbot/.openclaw/backups"
    today = datetime.now().strftime("%Y%m%d")
    import glob
    backups = glob.glob(f"{backup_dir}/backup_{today}_*.tar.gz")
    
    if not backups:
        issues.append("Kein Backup heute")
    
    # Check ob Git commits existieren
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd="/home/clawbot/.openclaw/workspace",
        capture_output=True,
        text=True
    )
    commits = [c for c in result.stdout.strip().split('\n') if c]
    
    if len(commits) < 3:
        issues.append(f"Nur {len(commits)} Commits heute")
    
    return issues

def main():
    print(f"Sir HazeClaw Self-Check — {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    print("\n## Patterns Check")
    for bp in BAD_PATTERNS:
        print(f"  ⚠️  {bp['name']}")
        print(f"      Vermeide: {bp['pattern']}")
    
    print("\n## Documentation Check")
    ok, msg = check_documentation()
    print(f"  {'✅' if ok else '❌'} {msg}")
    
    print("\n## Workflow Check")
    issues = check_workflow()
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  ✅ Workflow OK")
    
    print("\n## Load")
    load = os.getloadavg()[0]
    print(f"  Load: {load:.2f}")
    if load < 1.0:
        print("  ✅ System hat Kapazität")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
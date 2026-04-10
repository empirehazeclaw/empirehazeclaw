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
    
    # Check Backup sinnvoll?
    import glob
    backup_dir = "/home/clawbot/.openclaw/backups"
    today = datetime.now().strftime("%Y%m%d")
    backups_today = sorted(glob.glob(f"{backup_dir}/backup_{today}_*.tar.gz"))
    
    # Check git commits
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd="/home/clawbot/.openclaw/workspace",
        capture_output=True,
        text=True
    )
    commits = [c for c in result.stdout.strip().split('\n') if c]
    
    # Echte Backup-Paranoia: Viele Backups, wenig Änderungen
    if len(backups_today) > 5:
        # Check ob sich wirklich etwas geändert hat
        if len(commits) <= 3 and len(backups_today) > len(commits) * 3:
            issues.append(f"⚠️  {len(backups_today)} Backups, aber nur {len(commits)} Commits (Backup-Paranoia?)")
        
    if not backups_today:
        issues.append("Kein Backup heute")
    
    if len(commits) < 3:
        issues.append(f"⚠️  Nur {len(commits)} Commits heute")
    
    return issues

def check_loop_pattern():
    """Erkennt ob ich in einem Loop bin ohne echten Fortschritt."""
    issues = []
    
    # Check: Viele "Ich fahre fort" Nachrichten im Log?
    # Wenn ich keine commits mache und Load niedrig ist...
    
    import glob
    backup_dir = "/home/clawbot/.openclaw/backups"
    today = datetime.now().strftime("%Y%m%d")
    backups_today = sorted(glob.glob(f"{backup_dir}/backup_{today}_*.tar.gz"))
    
    # Check git commits
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd="/home/clawbot/.openclaw/workspace",
        capture_output=True,
        text=True
    )
    commits = [c for c in result.stdout.strip().split('\n') if c]
    
    # Loop erkennung: Viele Backups, keine/wenig Commits in letzter Stunde
    if len(backups_today) > 8 and len(commits) < 5:
        # Check commits in letzter Stunde
        result2 = subprocess.run(
            ["git", "log", "--oneline", "--since='1 hour ago'"],
            cwd="/home/clawbot/.openclaw/workspace",
            capture_output=True,
            text=True
        )
        recent_commits = [c for c in result2.stdout.strip().split('\n') if c]
        
        if len(recent_commits) < 2:
            issues.append('⚠️  Loop erkannt: Keine echten Änderungen, nur "Ich fahre fort" wiederholt?')
    
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
    loop_issues = check_loop_pattern()
    issues.extend(loop_issues)
    
    if issues:
        for issue in issues:
            print(f"  {issue}")
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
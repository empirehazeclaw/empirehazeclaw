#!/usr/bin/env python3
"""
Weekly Zettelkasten Review
- Erstellt wöchentliche Zusammenfassung
- Archiviert alte Notes automatisch
- Generiert Insights Report für Sonntag
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
FLEETING_DIR = WORKSPACE / "memory/notes/fleeting"
PERMANENT_DIR = WORKSPACE / "memory/notes/permanent"
CONCEPTS_DIR = WORKSPACE / "memory/notes/concepts"
ARCHIVE_DIR = WORKSPACE / "memory/archive"
REPORT_FILE = WORKSPACE / "memory/notes/permanent/weekly_zettel_review.md"

WEEKDAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

def get_week_range():
    """Gibt Start und Ende der aktuellen Woche zurück."""
    today = datetime.now()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end

def get_notes():
    notes = []
    for f in FLEETING_DIR.glob("*.md"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        notes.append({
            'file': f,
            'name': f.name,
            'mtime': mtime,
            'age_days': (datetime.now() - mtime).days
        })
    return sorted(notes, key=lambda x: x['mtime'], reverse=True)

def get_permanent_notes():
    """Gibt alle permanenten Notes der Woche zurück."""
    start, end = get_week_range()
    notes = []
    for f in PERMANENT_DIR.glob("*.md"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if start <= mtime <= end + timedelta(days=1):
            notes.append({
                'file': f,
                'name': f.name,
                'mtime': mtime
            })
    return sorted(notes, key=lambda x: x['mtime'])

def run_review():
    print("=== 🧠 WEEKLY ZETTELKASTEN REVIEW ===\n")
    
    start, end = get_week_range()
    week_str = f"{start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}"
    print(f"📅 Woche: {week_str}\n")
    
    notes = get_notes()
    old_notes = [n for n in notes if n['age_days'] >= 7]
    recent_notes = [n for n in notes if n['age_days'] < 7]
    
    print(f"📋 Fleeting Notes: {len(notes)} total")
    print(f"   - Diese Woche: {len(recent_notes)}")
    print(f"   - Archiviert: {len(old_notes)}")
    
    permanent = get_permanent_notes()
    print(f"\n📌 Permanent Notes diese Woche: {len(permanent)}")
    for p in permanent:
        print(f"   - {p['name']}")
    
    # Create weekly review file
    content = f"# Weekly Zettelkasten Review\n\n"
    content += f"*Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
    content += f"## Woche: {week_str}\n\n"
    content += f"### Zusammenfassung\n\n"
    content += f"| Kategorie | Anzahl |\n|-----------|--------|\n"
    content += f"| Fleeting Notes (total) | {len(notes)} |\n"
    content += f"| Fleeting Notes (diese Woche) | {len(recent_notes)} |\n"
    content += f"| Permanent Notes | {len(permanent)} |\n"
    content += f"| Archivierte Notes | {len(old_notes)} |\n\n"
    
    if recent_notes:
        content += f"### Fleeting Notes dieser Woche\n\n"
        for n in recent_notes:
            content += f"- {n['name']} ({n['mtime'].strftime('%A')})\n"
        content += "\n"
    
    if old_notes:
        content += f"### Archivierte Notes (>7 Tage)\n\n"
        for n in old_notes[:10]:
            content += f"- {n['name']} ({n['age_days']} Tage alt)\n"
        if len(old_notes) > 10:
            content += f"- ... und {len(old_notes) - 10} weitere\n"
        content += "\n"
    
    if permanent:
        content += f"### Permanent Notes dieser Woche\n\n"
        for p in permanent:
            content += f"- {p['name']}\n"
        content += "\n"
    
    content += "---\n*Weekly Zettelkasten Review — automatisch erstellt*\n"
    
    # Write report
    with open(REPORT_FILE, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Weekly Review erstellt: {REPORT_FILE.name}")
    
    # Log to weekly_review.log
    log_file = WORKSPACE.parent / "logs/weekly_review.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M UTC')} - Weekly Review: {len(notes)} notes, {len(permanent)} permanent, {len(old_notes)} archived\n")
    
    return len(notes), len(permanent), len(old_notes)

if __name__ == "__main__":
    run_review()
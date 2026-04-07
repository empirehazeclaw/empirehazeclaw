#!/usr/bin/env python3
"""
Weekly Zettelkasten Review
- Lists all fleeting notes from the past week
- Suggests which to promote/archive/delete
- Creates summary of the week's insights
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

FLEETING_DIR = Path("/home/clawbot/.openclaw/workspace/memory/notes/fleeting")
LEARNINGS_DIR = Path("/home/clawbot/.openclaw/workspace/memory/learnings")
PERMANENT_DIR = Path("/home/clawbot/.openclaw/workspace/memory/notes/permanent")
CONCEPTS_DIR = Path("/home/clawbot/.openclaw/workspace/memory/notes/concepts")

CUTOFF_DAYS = 7

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

def run_review():
    print("=== 🧠 WEEKLY ZETTELKASTEN REVIEW ===\n")
    
    notes = get_notes()
    old_notes = [n for n in notes if n['age_days'] >= CUTOFF_DAYS]
    
    print(f"📋 Fleeting Notes: {len(notes)} total, {len(old_notes)} older than {CUTOFF_DAYS} days\n")
    
    if not old_notes:
        print("✅ No old fleeting notes to review!")
        return
    
    print("📌 NOTES TO REVIEW:\n")
    for n in old_notes:
        print(f"  [{n['age_days']} days] {n['name']}")
    
    print("\n🎯 ACTIONS:")
    print("  1. Read each note")
    print("  2. Promote to concepts/insights/permanent/ OR delete")
    print("  3. Update this script when done")
    
    print("\n📝 PROMOTION TEMPLATES:")
    print(f"  mv '{old_notes[0]['file']}' {PERMANENT_DIR}/  (if important)")
    print(f"  mv '{old_notes[0]['file']}' {CONCEPTS_DIR}/  (if concept)")
    
    return old_notes

if __name__ == "__main__":
    run_review()

#!/usr/bin/env python3
"""
📝 MEMORY.md Auto-Update Script
Extracts key insights from daily notes and updates MEMORY.md
"""
import os
import re
from datetime import datetime

MEMORY_DIR = '/home/clawbot/.openclaw/workspace/memory'
MEMORY_FILE = os.path.join(MEMORY_DIR, 'MEMORY.md')
DAILY_DIR = os.path.join(MEMORY_DIR, 'daily')

def get_recent_daily_notes(days=7):
    """Get recent daily notes"""
    notes = []
    if not os.path.exists(DAILY_DIR):
        return notes
    
    for root, dirs, files in os.walk(DAILY_DIR):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                with open(path) as file:
                    content = file.read()
                    notes.append({
                        'file': f,
                        'content': content
                    })
    
    return notes[-days:]

def extract_key_events(content):
    """Extract key events from content"""
    events = []
    
    # Look for key patterns
    patterns = [
        r'[Ee]rstellt: (.+)',
        r'[Ii]mplementiert: (.+)',
        r'[Oo]ptimiert: (.+)',
        r'[Vv]erbes[s]ert: (.+)',
        r'[Ee]rledigt: (.+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        events.extend(matches)
    
    return events[:5]

def update_memory():
    """Update MEMORY.md with recent insights"""
    notes = get_recent_daily_notes(7)
    
    if not notes:
        print("No recent notes found")
        return
    
    # Extract events
    all_events = []
    for note in notes:
        events = extract_key_events(note['content'])
        for e in events:
            all_events.append(f"- {e} ({note['file'][:10]})")
    
    if not all_events:
        print("No key events found")
        return
    
    # Add to MEMORY.md
    section = f"\n\n## {datetime.now().strftime('%Y-%m')}\n"
    section += "\n".join(all_events[:10])
    
    with open(MEMORY_FILE, 'a') as f:
        f.write(section)
    
    print(f"✅ Updated MEMORY.md with {len(all_events)} events")

if __name__ == "__main__":
    update_memory()

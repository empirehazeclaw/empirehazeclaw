#!/usr/bin/env python3
"""
Evening Capture - Zettelkasten Daily Reminder
Creates a new fleeting note template for today
"""
import os
from datetime import datetime
from pathlib import Path

NOTES_DIR = Path("/home/clawbot/.openclaw/workspace/memory/notes/fleeting")
TEMPLATE = """---
title: "{title}"
created: {date}
type: fleeting
tags: [{tags}]
---

# {title}

## Was ist passiert?
> 

## Warum wichtig?
> 

## Nächste Action
- [ ] 

## Quelle
- [[]]

---
*Fleeting Note - Needs processing*
"""

def create_daily_note():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = NOTES_DIR / f"{today}-insight.md"
    
    if filename.exists():
        print(f"Note for {today} already exists: {filename}")
        return
    
    content = TEMPLATE.format(
        title=f"Evening Insights {today}",
        date=today,
        tags="insight,evening,capture"
    )
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✅ Created: {filename}")
    print(f"📝 Open and fill in your 3 insights for today!")
    return str(filename)

if __name__ == "__main__":
    create_daily_note()

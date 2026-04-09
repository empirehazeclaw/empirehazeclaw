#!/usr/bin/env python3
"""
Memory Manager - Automatische tägliche Memory Updates
"""
import os
from datetime import datetime

MEMORY_FILE = "/home/clawbot/.openclaw/workspace/memory/"

def get_today_file():
    """Get today's memory file"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"{MEMORY_FILE}{today}.md"

def append_to_memory(content):
    """Append content to today's memory"""
    filepath = get_today_file()
    with open(filepath, "a") as f:
        f.write(f"\n{content}")
    print(f"Appended to {filepath}")

def create_entry(title, content):
    """Create a structured memory entry"""
    entry = f"""
## {title}
{content}
---
*Erstellt: {datetime.now().strftime("%H:%M")}*
"""
    append_to_memory(entry)

# Daily summary template
def daily_summary():
    """Create daily summary"""
    entry = """
# Tageszusammenfassung

## Erledigt
- 

## Gelernt
- 

## Nächste Schritte
- 

---
"""
    append_to_memory(entry)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "summary":
            daily_summary()
        else:
            create_entry(sys.argv[1], " ".join(sys.argv[2:]))

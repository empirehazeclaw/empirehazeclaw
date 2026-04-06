#!/usr/bin/env python3
"""
Weekly Knowledge Review
Automatically creates weekly summary
"""
from datetime import datetime
import os

KNOWLEDGE = "/home/clawbot/.openclaw/workspace/knowledge"
TEMPLATE = """# Weekly Review - {week}

## Achievements
- 

## Metrics
- Revenue:
- Traffic:
- Customers:

## Learnings
- 
- 

## Next Week Goals
- [ ] 
- [ ]

## Knowledge Updates
- Added:
- Updated:

---

*Created: {date}*
"""

if __name__ == "__main__":
    week = datetime.now().strftime("%Y-W%U")
    filename = f"{KNOWLEDGE}/learnings/weekly-{week}.md"
    
    with open(filename, 'w') as f:
        f.write(TEMPLATE.format(week=week, date=datetime.now()))
    
    print(f"✅ Created weekly review: {filename}")

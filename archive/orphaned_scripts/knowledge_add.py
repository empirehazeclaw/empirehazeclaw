#!/usr/bin/env python3
"""Quick add to knowledge"""
import sys

TEMPLATE = """
# {title}

{content}

---

*Erstellt: {date}*
"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: knowledge_add.py <category> <title>")
        print("Categories: revenue, tech, marketing, learnings")
        sys.exit(1)
    
    category = sys.argv[1]
    title = sys.argv[2]
    from datetime import datetime
    
    filename = f"/home/clawbot/.openclaw/workspace/knowledge/{category}/{title}.md"
    
    with open(filename, 'w') as f:
        f.write(TEMPLATE.format(title=title, content="- ", date=datetime.now()))
    
    print(f"✅ Created: {filename}")

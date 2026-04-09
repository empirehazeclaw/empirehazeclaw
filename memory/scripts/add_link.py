#!/usr/bin/env python3
"""
Knowledge Brain - Add Link
Fuegt einen Backlink zu einer Note hinzu

Usage:
  python3 add_link.py <note-path> <target-note> [--context 'why']
"""
import sys
import os

MEMORY_DIR = "/home/clawbot/.openclaw/workspace/memory"
BACKLINKS_FILE = MEMORY_DIR + "/backlinks/index.md"

def add_backlink(source_note, target_note, context=""):
    if not os.path.exists(source_note):
        print("Note nicht gefunden: " + source_note)
        return False
    
    with open(source_note) as f:
        content = f.read()
    
    link_markdown = "- [[" + target_note + "]]"
    if context:
        link_markdown += " -- " + context
    
    if "## Connections" in content:
        content = content.replace("## Connections", link_markdown + "\n\n## Connections")
    elif "## Tags" in content:
        content = content.replace("## Tags", "## Connections\n" + link_markdown + "\n\n## Tags")
    else:
        content += "\n\n## Connections\n" + link_markdown + "\n"
    
    with open(source_note, 'w') as f:
        f.write(content)
    
    # Update backlinks index
    if not os.path.exists(os.path.dirname(BACKLINKS_FILE)):
        os.makedirs(os.path.dirname(BACKLINKS_FILE))
    entry = "- [[" + os.path.basename(source_note) + "]] -> [[" + target_note + "]]"
    with open(BACKLINKS_FILE, 'a') as f:
        f.write("\n" + entry)
    
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 add_link.py <note-path> <target-note>")
        print("  python3 add_link.py notes/ideas/test.md 'Andere Note'")
        return 1
    
    source = sys.argv[1]
    target = sys.argv[2]
    context = ""
    
    for arg in sys.argv[3:]:
        if arg.startswith("--context="):
            context = arg.split("=", 1)[1]
    
    if not target.startswith("[["):
        target = "[[" + target + "]]"
    
    if add_backlink(source, target, context):
        print("Link hinzugefuegt!")
        print("  Von: " + source)
        print("  Zu: " + target)
    
    return 0

if __name__ == "__main__":
    exit(main())

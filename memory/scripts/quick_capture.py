#!/usr/bin/env python3
"""
Knowledge Brain - Quick Capture
Schnell eine Idee/Note ins Second Brain packen

Usage:
  python3 quick_capture.py "Meine Idee"
  python3 quick_capture.py "Meine Idee" --tags idea,business
  python3 quick_capture.py "Meine Idee" --type permanent
"""
import sys
import os
import re
from datetime import datetime

MEMORY_DIR = "/home/clawbot/.openclaw/workspace/memory"
NOTES_DIR = MEMORY_DIR + "/notes"
BACKLINKS_FILE = MEMORY_DIR + "/backlinks/index.md"

NOTE_TYPES = {
    "fleeting": NOTES_DIR + "/ideas",
    "permanent": NOTES_DIR + "/concepts",
    "insights": NOTES_DIR + "/insights",
    "learnings": NOTES_DIR + "/learnings",
    "ideas": NOTES_DIR + "/ideas",
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]

def create_note(title, tags, note_type, content=""):
    note_dir = NOTE_TYPES.get(note_type, NOTE_TYPES["fleeting"])
    if not os.path.exists(note_dir):
        os.makedirs(note_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = note_dir + "/" + date_str + "-" + slug + ".md"
    
    tags_str = ", ".join(tags) if tags else "untagged"
    tags_formatted = " ".join("#" + t for t in tags) if tags else ""
    
    note_content = """---
title: TITLE_PLACEHOLDER
created: DATE_PLACEHOLDER
type: TYPE_PLACEHOLDER
tags: [TAGS_PLACEHOLDER]
---

# TITLE_PLACEHOLDER

## Summary
One sentence summary of this note.

## Main Content

CONTENT_PLACEHOLDER

## Connections

- [[Related Note 1]]
- [[Related Note 2]]

## Tags
TAGS_FORMATTED_PLACEHOLDER

---
*Permanent Note - Evergreen Content*
*Last modified: DATE_PLACEHOLDER*
"""
    
    note_content = note_content.replace("TITLE_PLACEHOLDER", title)
    note_content = note_content.replace("DATE_PLACEHOLDER", datetime.now().strftime("%Y-%m-%d %H:%M"))
    note_content = note_content.replace("TYPE_PLACEHOLDER", note_type)
    note_content = note_content.replace("TAGS_PLACEHOLDER", tags_str)
    note_content = note_content.replace("TAGS_FORMATTED_PLACEHOLDER", tags_formatted)
    note_content = note_content.replace("CONTENT_PLACEHOLDER", content or "Enter your note content here...")
    
    with open(filename, 'w') as f:
        f.write(note_content)
    
    return filename

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h"]:
        print("Knowledge Brain - Quick Capture")
        print("=" * 40)
        print("")
        print("Usage:")
        print("  python3 quick_capture.py 'Meine Idee'")
        print("  python3 quick_capture.py 'Meine Idee' --tags idea,business")
        print("  python3 quick_capture.py 'Meine Idee' --type permanent")
        print("")
        print("Types: fleeting, permanent, insights, learnings, ideas")
        return 0
    
    title = sys.argv[1]
    tags = []
    note_type = "fleeting"
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--tags" and i + 1 < len(sys.argv):
            tags = sys.argv[i + 1].split(",")
            i += 2
        elif arg.startswith("--tags="):
            tags = arg.split("=")[1].split(",")
            i += 1
        elif arg == "--type" and i + 1 < len(sys.argv):
            note_type = sys.argv[i + 1]
            i += 2
        elif arg.startswith("--type="):
            note_type = arg.split("=")[1]
            i += 1
        else:
            i += 1
    
    filename = create_note(title, tags, note_type)
    
    print("Note erstellt!")
    print("  Pfad: " + filename)
    print("  Tags: " + ", ".join(tags) if tags else "keine")
    print("  Type: " + note_type)
    
    return 0

if __name__ == "__main__":
    exit(main())

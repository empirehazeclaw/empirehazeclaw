#!/usr/bin/env python3
"""
Knowledge Brain - Daily Review (Kurz)
Schnelles taegliches Review - 5 Minuten

Usage:
  python3 daily_review.py
"""
import os
import re
from datetime import datetime, timedelta

MEMORY_DIR = "/home/clawbot/.openclaw/workspace/memory"
NOTES_DIR = MEMORY_DIR + "/notes"

def get_recent_notes(days=1):
    recent = []
    cutoff = datetime.now() - timedelta(days=days)
    for root, dirs, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                if mtime >= cutoff:
                    recent.append({'path': path, 'file': file, 'mtime': mtime})
    return recent

def extract_tags(content):
    return re.findall(r'#([\w-]+)', content)

def extract_links(content):
    return re.findall(r'\[\[([^\]]+)\]\]', content)

def daily_review():
    print("Knowledge Brain - Daily Review (5 Minuten)")
    print("=" * 40)
    
    today = get_recent_notes(1)
    print("\nHeute: " + str(len(today)) + " Notes")
    for note in today:
        print("  - " + note['file'])
    
    unlinked = []
    for root, dirs, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path) as f:
                    content = f.read()
                links = extract_links(content)
                if not links:
                    unlinked.append(file)
    
    if unlinked:
        print("\nUnverlinkte Notes: " + str(len(unlinked)))
        for f in unlinked[:3]:
            print("  - " + f)
    
    all_tags = {}
    for root, dirs, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path) as f:
                    content = f.read()
                tags = extract_tags(content)
                for tag in tags:
                    all_tags[tag] = all_tags.get(tag, 0) + 1
    
    if all_tags:
        sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:5]
        print("\nTop Tags:")
        for tag, count in sorted_tags:
            print("  #" + tag + ": " + str(count))
    
    print("\nDaily Review done!")
    return 0

if __name__ == "__main__":
    exit(daily_review())

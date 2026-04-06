#!/usr/bin/env python3
"""
Knowledge Brain - Weekly Review
Ueberprueft alle Notes der letzten Woche

Usage:
  python3 weekly_review.py
"""
import os
import re
from datetime import datetime, timedelta

MEMORY_DIR = "/home/clawbot/.openclaw/workspace/memory"
NOTES_DIR = MEMORY_DIR + "/notes"
REVIEW_FILE = MEMORY_DIR + "/weekly-review.md"

def get_recent_notes(days=7):
    recent = []
    cutoff = datetime.now() - timedelta(days=days)
    for root, dirs, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                if mtime >= cutoff:
                    recent.append({'path': path, 'file': file, 'mtime': mtime})
    return sorted(recent, key=lambda x: x['mtime'], reverse=True)

def extract_links(content):
    return re.findall(r'\[\[([^\]]+)\]\]', content)

def extract_tags(content):
    return re.findall(r'#([\w-]+)', content)

def generate_review():
    print("Knowledge Brain - Weekly Review")
    print("=" * 50)
    
    recent = get_recent_notes(7)
    print("\nNotes diese Woche: " + str(len(recent)))
    for note in recent:
        print("  - " + note['file'] + " (" + note['mtime'].strftime('%d.%m') + ")")
    
    all_notes = []
    for root, dirs, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path) as f:
                    content = f.read()
                all_notes.append({
                    'path': path,
                    'file': file,
                    'links': extract_links(content),
                    'tags': extract_tags(content)
                })
    
    linked_files = set()
    for note in all_notes:
        for link in note['links']:
            linked_files.add(link)
    
    orphaned = []
    for note in all_notes:
        note_name = note['file'].replace('.md', '')
        if note_name not in linked_files and not note['links']:
            orphaned.append(note['file'])
    
    if orphaned:
        print("\nOrphaned notes: " + str(len(orphaned)))
        for f in orphaned[:5]:
            print("  - " + f)
    else:
        print("\nKeine orphaned notes!")
    
    all_tags = {}
    for note in all_notes:
        for tag in note['tags']:
            all_tags[tag] = all_tags.get(tag, 0) + 1
    
    sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
    print("\nTop Tags:")
    for tag, count in sorted_tags[:10]:
        print("  #" + tag + ": " + str(count))
    
    review = "# Weekly Review - " + datetime.now().strftime('%Y-W%W') + "\n\n"
    review += "Notes diese Woche:\n"
    for note in recent:
        review += "- [[" + note['file'] + "]]\n"
    
    review += "\nOrphaned Notes:\n"
    if orphaned:
        for f in orphaned:
            review += "- [[" + f + "]]\n"
    else:
        review += "Keine!\n"
    
    review += "\nTop Tags:\n"
    for tag, count in sorted_tags[:10]:
        review += "- #" + tag + ": " + str(count) + "\n"
    
    review += "\nActions:\n"
    review += "- [ ] Review orphaned notes\n"
    review += "- [ ] Add connections\n"
    review += "- [ ] Update outdated notes\n"
    
    with open(REVIEW_FILE, 'w') as f:
        f.write(review)
    
    print("\nReview gespeichert: " + REVIEW_FILE)
    return 0

if __name__ == "__main__":
    exit(generate_review())

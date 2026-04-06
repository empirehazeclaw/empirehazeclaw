#!/usr/bin/env python3
"""
Knowledge Brain - Suggest Links
Schlaegt Verbindungen zwischen Notes vor

Usage:
  python3 suggest_links.py
"""
import os
import re
from collections import defaultdict

MEMORY_DIR = "/home/clawbot/.openclaw/workspace/memory"
NOTES_DIR = MEMORY_DIR + "/notes"

def extract_tags(content):
    return re.findall(r'#([\w-]+)', content)

def extract_keywords(content):
    words = re.findall(r'\b[A-Z][a-z]+\b', content)
    stopwords = {'This', 'That', 'The', 'And', 'For', 'With', 'Note', 'Notes', 'Memory', 'Knowledge', 'Brain'}
    return [w for w in set(words) if w not in stopwords and len(w) > 3]

def suggest_links():
    print("Link Suggestions")
    print("=" * 40)
    
    tag_index = defaultdict(list)
    note_tags = {}
    note_keywords = {}
    
    for root, dirs, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                with open(path) as f:
                    content = f.read()
                
                note_name = file.replace('.md', '')
                tags = extract_tags(content)
                keywords = extract_keywords(content)
                
                note_tags[note_name] = tags
                note_keywords[note_name] = keywords
                
                for tag in tags:
                    tag_index[tag].append(note_name)
    
    suggestions = []
    seen = set()
    
    # Find connections via shared tags
    for note_name, tags in note_tags.items():
        for tag in tags:
            for other in tag_index.get(tag, []):
                if other != note_name:
                    pair = tuple(sorted([note_name, other]))
                    if pair not in seen:
                        seen.add(pair)
                        suggestions.append((note_name, other, "Shared tag: #" + tag))
    
    # Find connections via shared keywords
    for note_name, keywords in note_keywords.items():
        for kw in keywords:
            for other_name, other_kw in note_keywords.items():
                if other_name != note_name and kw in other_kw:
                    pair = tuple(sorted([note_name, other_name]))
                    if pair not in seen:
                        seen.add(pair)
                        suggestions.append((note_name, other_name, "Shared keyword: " + kw))
    
    if suggestions:
        print("\n" + str(len(suggestions)) + " Verbindungs-Vorschlaege:")
        for i, (from_note, to_note, reason) in enumerate(suggestions[:10]):
            print("  " + str(i+1) + ". [[" + from_note + "]] -> [[" + to_note + "]] (" + reason + ")")
    else:
        print("\nKeine neuen Verbindungs-Vorschlaege")
    
    return suggestions[:10]

if __name__ == "__main__":
    suggest_links()

#!/usr/bin/env python3
"""
Knowledge Search - Find anything in knowledge base
Usage: python3 knowledge_search.py [query]
"""
import os
import sys

KNOWLEDGE_DIR = "/home/clawbot/.openclaw/workspace/knowledge"
IGNORE = ["archive", ".git", "__pycache__", "templates"]

def search(query, directory):
    """Search all files in directory"""
    results = []
    query = query.lower()
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORE]
        
        for file in files:
            if file.endswith(('.md', '.txt', '.json')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read().lower()
                        if query in content:
                            rel_path = filepath.replace(KNOWLEDGE_DIR + '/', '')
                            # Get context
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if query in line:
                                    results.append({
                                        'file': rel_path,
                                        'line': line.strip()[:100]
                                    })
                except:
                    pass
    return results

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "revenue"
    
    print(f"🔍 Searching for: {query}")
    print()
    
    results = search(query, KNOWLEDGE_DIR)
    
    if results:
        for r in results[:10]:
            print(f"📄 {r['file']}")
            print(f"   {r['line']}")
            print()
    else:
        print("No results found.")

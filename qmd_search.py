#!/usr/bin/env python3
"""
🔍 QMD Search for Memory System
Wrapper for qmd CLI
"""
import subprocess
import sys

MEMORY_PATH = '/home/clawbot/.openclaw/workspace/memory'

def search(query, method='query'):
    """Search memory using QMD"""
    cmd = ['qmd', method, query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def main():
    if len(sys.argv) < 2:
        print("Usage: python qmd_search.py <query>")
        print("Example: python qmd_search.py 'Notion Templates'")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    print(f"🔍 Searching: {query}")
    print("-" * 50)
    
    # Try hybrid query first
    result = search(query, 'query')
    if result:
        print(result)
    else:
        # Try keyword search
        result = search(query, 'search')
        print(result)

if __name__ == "__main__":
    main()

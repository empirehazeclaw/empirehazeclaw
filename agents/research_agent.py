#!/usr/bin/env python3
"""
Research Agent - Simple Web Search
"""
import sys
import os
import json

# Simple web search using web_fetch
def search_web(query):
    """Simple web search"""
    from urllib.parse import quote
    try:
        import requests
        # Using a simple search endpoint
        url = f"https://duckduckgo.com/html/?q={quote(query)}"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        return resp.text[:2000]
    except Exception as e:
        return f"Search error: {e}"

def main():
    # Get task from args
    task = ""
    for i, arg in enumerate(sys.argv):
        if arg == "--task" and i + 1 < len(sys.argv):
            task = sys.argv[i + 1]
            break
    
    if not task:
        # Interactive mode
        task = input("Research task: ")
    
    print(f"🔍 Researching: {task}")
    
    # Do simple search
    results = search_web(task)
    print(f"📊 Found results for: {task}")
    print(results[:500] if results else "No results")

if __name__ == "__main__":
    main()

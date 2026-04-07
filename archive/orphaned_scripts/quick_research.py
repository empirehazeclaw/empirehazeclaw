#!/usr/bin/env python3
"""Quick Research - Web Search + Save"""
import sys
sys.path.insert(0, ".")
from scripts.free_search import search

query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "AI news"

if __name__ == "__main__":
    print(f"🔍 Research: {query}")
    results = search(query, count=5)
    for i, r in enumerate(results[:5], 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")

#!/usr/bin/env python3
"""
Tavily Search - Free AI Search
1000 searches/month gratis!
"""

import os
from tavily import TavilyClient

def search(query: str, max_results: int = 5) -> dict:
    """Sucht mit Tavily (1000/month gratis)"""
    
    api_key = os.environ.get("TAVILY_API_KEY", "")
    
    if not api_key:
        return {
            "status": "error",
            "message": "TAVILY_API_KEY nicht gesetzt!",
            "setup": "1. Gehe zu https://tavily.com\n2. API Key holen\n3. export TAVILY_API_KEY='dein_key'"
        }
    
    try:
        client = TavilyClient(api_key=api_key)
        results = client.search(query=query, max_results=max_results)
        
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content", "")[:200]
                }
                for r in results.get("results", [])
            ]
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("""
🔍 Tavily Search - 1000 Searches/Monat Gratis!

Usage: 
  python3 tavily_search.py "dein suchbegriff"
  python3 tavily_search.py setup

Setup:
  1. Gehe zu https://tavily.com
  2. Account erstellen (kostenlos)
  3. API Key kopieren
  4. Setze Key:
     export TAVILY_API_KEY="dein_key"
     
Limit: 1000 Searches/Monat
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "setup":
        print("""
🔧 Tavily Setup:

1. Gehe zu https://tavily.com
2. Klicke "Get API Key"
3. Kopiere den Key
4. Setze in Terminal:
   export TAVILY_API_KEY="PASTE_KEY_HERE"
   
5. Testen:
   python3 ~/.openclaw/workspace/scripts/tavily_search.py "KI news"
   
Gratis: 1000 Suchen/Monat
        """)
        return
    
    query = " ".join(sys.argv[1:])
    result = search(query)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

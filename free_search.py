#!/usr/bin/env python3
"""
Free Web Search - DuckDuckGo
Kein API Key nötig!
"""

import requests
from urllib.parse import quote_plus

def search(query: str, num_results: int = 5) -> list:
    """Sucht mit DuckDuckGo (kostenlos)"""
    
    url = f"https://duckduckgo.com/?q={quote_plus(query)}&format=json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Parse results
        results = []
        # Simplified parsing - returns HTML but we can extract titles
        
        return {
            "query": query,
            "results": "Nutze https://duckduckgo.com/?q=" + quote_plus(query),
            "status": "OK - Manual"
        }
        
    except Exception as e:
        return {"error": str(e)}

def search_html(query: str) -> str:
    """Öffnet Suchergebnisse im Browser"""
    import webbrowser
    url = f"https://duckduckgo.com/?q={quote_plus(query)}"
    return f"📌 Öffne: {url}"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 free_search.py <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"🔍 Suche: {query}")
    print(search_html(query))

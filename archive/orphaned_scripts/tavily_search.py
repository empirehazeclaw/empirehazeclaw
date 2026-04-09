#!/usr/bin/env python3
"""
Tavily Search - Standard Web Search for OpenClaw
Uses Tavily API as default search engine.
"""
import sys
import os

# Try to load Tavily API key from env
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '')

if not TAVILY_API_KEY:
    # Try to get from config
    try:
        import yaml
        with open('/home/clawbot/.openclaw/config.yaml') as f:
            config = yaml.safe_load(f)
            TAVILY_API_KEY = config.get('tavily', {}).get('api_key', '')
    except:
        pass

if not TAVILY_API_KEY:
    TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

def search(query, max_results=10):
    """Perform search using Tavily."""
    from tavily import TavilyClient
    
    client = TavilyClient(api_key=TAVILY_API_KEY)
    results = client.search(query, max_results=max_results)
    
    return results.get('results', [])

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tavily_search.py <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    results = search(query)
    
    print(f"🔍 Search: {query}")
    print("=" * 50)
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['title']}")
        print(f"   {r['url']}")
        print(f"   {r['content'][:200]}...")
    
    print(f"\n📊 Total: {len(results)} results")

if __name__ == "__main__":
    main()

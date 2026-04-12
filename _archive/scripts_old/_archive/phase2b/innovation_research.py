#!/usr/bin/env python3
"""
innovation_research.py — AI Innovation Research
Sir HazeClaw - 2026-04-11

Sucht nach neuen AI Agent Patterns und Innovationen.
Nutzt arXiv API für echte Research Papers.

Usage:
    python3 innovation_research.py
    python3 innovation_research.py --daily
    python3 innovation_research.py --weekly
"""

import json
import re
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
RESEARCH_LOG = WORKSPACE / "data" / "innovation_research_log.json"
KG_PATH = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"

# arXiv categories for AI/ML research
ARXIV_CATEGORIES = {
    "cs.AI": "Artificial Intelligence",
    "cs.LG": "Machine Learning", 
    "cs.MA": "Multiagent Systems",
    "cs.RO": "Robotics",
    "cs.CL": "Computation and Language",
}

RESEARCH_QUERIES = {
    "daily": [
        "self-improving AI agents",
        "autonomous AI agent learning",
        "LLM agent self-modification",
    ],
    "weekly": [
        "AI agent capability evolution",
        "self-evolving neural networks",
        "multi-agent reinforcement learning",
        "AI agent prompt engineering",
    ]
}

# Timeout for web requests
TIMEOUT = 15

def load_research_log():
    if RESEARCH_LOG.exists():
        with open(RESEARCH_LOG) as f:
            return json.load(f)
    return {"entries": [], "last_full_research": None}

def save_research_log(log):
    RESEARCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(RESEARCH_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def search_arxiv(query, max_results=5):
    """Sucht arXiv nach Papers basierend auf Query."""
    try:
        # arXiv API: search by title, abstract, or all fields
        url = f"http://export.arxiv.org/api/query"
        params = {
            'search_query': f'all:{quote_plus(query)}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(resp.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        results = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            published = entry.find('atom:published', ns)
            link = entry.find('atom:id', ns)
            
            if title is not None:
                paper = {
                    'title': title.text.strip().replace('\n', ' '),
                    'summary': (summary.text.strip().replace('\n', ' ')[:300] + '...') if summary is not None else '',
                    'published': published.text[:10] if published is not None else '',
                    'url': link.text if link is not None else '',
                }
                results.append(paper)
        
        return results
        
    except Exception as e:
        return [{"error": str(e)[:100]}]

def search_hackernews(keyword, max_results=5):
    """Sucht Hacker News via Algolia API."""
    try:
        url = f"https://hn.algolia.com/api/v1/search"
        params = {
            'query': keyword,
            'tags': 'story',
            'hitsPerPage': max_results
        }
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for hit in data.get('hits', [])[:max_results]:
                results.append({
                    'title': hit.get('title', hit.get('story_text', '')[:100]),
                    'url': hit.get('url', hit.get('story_url', '')),
                    'points': hit.get('points', 0),
                    'date': hit.get('created_at', '')[:10]
                })
            return results
    except Exception as e:
        return [{"error": str(e)[:100]}]
    return []

def add_to_kg(insights, query_count):
    """Fügt Innovation Insights zum Knowledge Graph hinzu."""
    if not KG_PATH.exists():
        return False
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        today = datetime.now().strftime('%Y%m%d')
        entity_id = f"innovation_research_{today}"
        
        # Truncate insights if too long
        if len(insights) > 2000:
            insights = insights[:2000] + "..."
        
        entity = {
            "type": "research",
            "category": "ai_agent_innovation",
            "facts": [{
                "content": insights,
                "confidence": 0.8,
                "extracted_at": datetime.now().isoformat(),
                "category": "innovation_research"
            }],
            "priority": "MEDIUM",
            "created": datetime.now().isoformat(),
            "tags": ["innovation", "research", "ai_agent", "2026", "arxiv"]
        }
        
        kg['entities'][entity_id] = entity
        kg['last_updated'] = datetime.now().isoformat()
        
        with open(KG_PATH, 'w') as f:
            json.dump(kg, f, indent=2)
        
        return True
    except Exception as e:
        print(f"  ⚠️ KG update failed: {e}")
        return False

def run_research(mode="daily"):
    """Führt Research im specified mode aus."""
    queries = RESEARCH_QUERIES.get(mode, RESEARCH_QUERIES["daily"])
    
    print(f"🔍 Innovation Research — {mode.upper()}")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    all_results = []
    
    # Search arXiv for each query
    for query in queries:
        print(f"📚 Searching arXiv: {query}...")
        papers = search_arxiv(query, max_results=3)
        
        if papers and 'error' not in papers[0]:
            for paper in papers[:2]:
                print(f"   ✅ {paper['title'][:70]}...")
                print(f"      ({paper.get('published', 'n.d.')})")
                all_results.append({
                    'source': 'arXiv',
                    'query': query,
                    'paper': paper
                })
        else:
            print(f"   ⚠️ No results or error")
    
    # Also search Hacker News for latest discussions
    print(f"\n📰 Checking HackerNews for: {queries[0]}...")
    hn_results = search_hackernews(queries[0], max_results=3)
    for hn in hn_results[:2]:
        if 'error' not in hn:
            print(f"   ✅ {hn.get('title', '')[:70]}... (↑{hn.get('points', 0)})")
            all_results.append({
                'source': 'HackerNews',
                'query': queries[0],
                'discussion': hn
            })
    
    # Log results
    log = load_research_log()
    log["entries"].append({
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "queries": len(queries),
        "results": all_results
    })
    log["last_full_research"] = datetime.now().isoformat()
    save_research_log(log)
    
    # Add to KG
    insights_lines = []
    for r in all_results:
        if 'paper' in r:
            p = r['paper']
            insights_lines.append(f"## arXiv: {p['title'][:80]}\n{p.get('summary', '')[:200]}\n")
        elif 'discussion' in r:
            d = r['discussion']
            insights_lines.append(f"## HN: {d.get('title', '')[:80]}\nURL: {d.get('url', 'n/a')}\n")
    
    insights = "\n".join(insights_lines)
    kg_updated = add_to_kg(insights, len(queries))
    
    print()
    print("=" * 50)
    print(f"✅ Research complete")
    print(f"   arXiv Papers: {sum(1 for r in all_results if 'paper' in r)}")
    print(f"   HN Discussions: {sum(1 for r in all_results if 'discussion' in r)}")
    print(f"   KG Updated: {'Yes' if kg_updated else 'No'}")
    print()
    print("📊 Summary:")
    print(f"   Log file: {RESEARCH_LOG}")
    
    return True

def main():
    import sys
    mode = "daily"
    
    if "--weekly" in sys.argv:
        mode = "weekly"
    elif "--daily" in sys.argv:
        mode = "daily"
    
    run_research(mode)

if __name__ == "__main__":
    main()

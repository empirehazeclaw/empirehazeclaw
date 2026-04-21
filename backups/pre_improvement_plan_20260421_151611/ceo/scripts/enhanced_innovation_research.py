#!/usr/bin/env python3
"""
enhanced_innovation_research.py — Maximum Innovation Research
=============================================================
Erweiterte Version mit mehr Quellen und tieferer Synthesis.

Sources:
- arXiv (AI/ML papers)
- GitHub Trending (neue Tools/Frameworks)
- Hacker News (Industry insights)
- Tech Blogs (OpenAI, Anthropic, etc.)
- KG Synthesis (bestehendes Wissen verbinden)

Usage:
    python3 enhanced_innovation_research.py        # Full research
    python3 enhanced_innovation_research.py --daily   # Daily scan
    python3 enhanced_innovation_research.py --deep     # Deep dive
"""

import json
import re
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
KG_FILE = WORKSPACE / "memory/kg/knowledge_graph.json"
RESEARCH_LOG = WORKSPACE / "data/enhanced_innovation_research_log.json"

# Extended research queries
DAILY_QUERIES = [
    "self-improving AI agents",
    "autonomous AI agent learning",
    "LLM agent self-modification",
    "AI agent capability amplification",
    "neural network self-evolution",
    "multi-agent collaboration patterns",
]

WEEKLY_QUERIES = [
    "AI agent architecture patterns 2024",
    "self-modifying AI systems",
    "AI learning without forgetting",
    "agent prompt engineering best practices",
    "autonomous AI improvement loops",
    "AI system self-debugging",
]

# Additional sources config
GITHUB_TRENDING_URL = "https://api.github.com/search/repositories"
HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

TIMEOUT = 10


def load_kg():
    with open(KG_FILE) as f:
        return json.load(f)


def save_kg(kg):
    with open(KG_FILE, 'w') as f:
        json.dump(kg, f, indent=2)


def kg_entities_add(kg, new_entities):
    """"Add new entities to KG regardless of format (dict or list)."""
    if isinstance(kg.get('entities'), dict):
        for entity in new_entities:
            eid = entity.get('id')
            if eid:
                kg['entities'][eid] = entity
    else:
        kg['entities'].extend(new_entities)


def kg_entities_count(kg):
    """"Return entity count regardless of format."""
    entities = kg.get('entities', {})
    if isinstance(entities, dict):
        return len(entities)
    return len(entities)


def load_research_log():
    if RESEARCH_LOG.exists():
        with open(RESEARCH_LOG) as f:
            return json.load(f)
    return {"entries": [], "last_full_research": None, "sources_searched": 0}


def save_research_log(log):
    RESEARCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(RESEARCH_LOG, 'w') as f:
        json.dump(log, f, indent=2)


# ============ Source 1: arXiv ============

def search_arxiv(query, max_results=5):
    """arXiv paper search."""
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': f'all:{quote_plus(query)}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        
        root = ET.fromstring(resp.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        results = []
        for entry in root.findall('atom:entry', ns)[:max_results]:
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            published = entry.find('atom:published', ns)
            link = entry.find('atom:id', ns)
            
            if title is not None:
                results.append({
                    'title': title.text.strip().replace('\n', ' ')[:150],
                    'summary': (summary.text.strip().replace('\n', ' ')[:300] + '...') if summary else '',
                    'published': published.text[:10] if published else '',
                    'url': link.text if link else '',
                    'source': 'arXiv'
                })
        return results
    except Exception as e:
        return [{'error': str(e), 'source': 'arXiv'}]


# ============ Source 2: GitHub Trending ============

def get_github_trending(limit=10):
    """Get trending AI/ML repositories from GitHub."""
    try:
        # Search for recently updated AI/ML repos
        query = "AI OR machine-learning OR LLM OR agent in:name,description&sort=updated"
        params = {
            'q': query,
            'per_page': limit,
            'sort': 'stars',
            'order': 'desc'
        }
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        resp = requests.get(GITHUB_TRENDING_URL, params=params, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data.get('items', [])[:limit]:
            results.append({
                'title': item.get('name', ''),
                'description': item.get('description', '')[:200] or 'No description',
                'url': item.get('html_url', ''),
                'stars': item.get('stargazers_count', 0),
                'language': item.get('language', 'Unknown'),
                'updated': item.get('updated_at', '')[:10],
                'source': 'GitHub'
            })
        return results
    except Exception as e:
        return [{'error': str(e), 'source': 'GitHub'}]


# ============ Source 3: Knowledge Synthesis ============

def synthesize_knowledge(kg):
    """Synthesize new insights from existing KG."""
    # Handle both dict (current) and list (legacy) formats
    entities_raw = kg.get('entities', {})
    if isinstance(entities_raw, dict):
        entities = list(entities_raw.values())
    else:
        entities = entities_raw
    
    insights = []
    
    # 1. Find high-value entity clusters
    topics = [e for e in entities if e.get('type') == 'topic']
    improvements = [e for e in entities if e.get('type') == 'improvement']
    patterns = [e for e in entities if 'pattern' in e.get('type', '').lower()]
    
    # 2. Generate synthesis insights
    if len(topics) >= 5:
        insights.append({
            'title': f'Knowledge Cluster: {len(topics)} Topics inter-connected',
            'content': f'Found {len(topics)} topic entities forming knowledge network. '
                      f'Topics: {[t.get("id", "")[:30] for t in topics[:5]]}',
            'type': 'synthesis',
            'confidence': 0.85
        })
    
    if len(improvements) >= 10:
        insights.append({
            'title': f'Improvement Pipeline: {len(improvements)} optimizations tracked',
            'content': f'Active improvement pipeline with {len(improvements)} tracked optimizations. '
                      f'Success rate: {sum(1 for i in improvements if i.get("priority") == "HIGH") / len(improvements) * 100:.0f}% high-priority',
            'type': 'synthesis',
            'confidence': 0.9
        })
    
    if len(patterns) >= 10:
        insights.append({
            'title': f'Pattern Library: {len(patterns)} patterns discovered',
            'content': f'Cross-task pattern mining found {len(patterns)} patterns. '
                      f'Types: success_patterns, error_patterns, meta_patterns.',
            'type': 'synthesis',
            'confidence': 0.88
        })
    
    # 3. Find missing knowledge areas
    all_types = set(e.get('type', 'unknown') for e in entities)
    knowledge_gaps = []
    for gap_type in ['concept', 'principle', 'methodology', 'framework']:
        if gap_type not in all_types:
            knowledge_gaps.append(gap_type)
    
    if knowledge_gaps:
        insights.append({
            'title': 'Knowledge Gaps Identified',
            'content': f'Underrepresented types: {", ".join(knowledge_gaps)}. '
                      f'Consider expanding into these knowledge areas.',
            'type': 'gap_analysis',
            'confidence': 0.75
        })
    
    # 4. High-impact connections
    high_priority = [e for e in entities if e.get('priority') == 'HIGH' and len(e.get('facts', [])) >= 3]
    if high_priority:
        insights.append({
            'title': f'Rich Entities: {len(high_priority)} well-developed high-priority concepts',
            'content': f'These entities have deep fact coverage: '
                      f'{[e.get("id", "")[:20] for e in high_priority[:3]]}',
            'type': 'entity_analysis',
            'confidence': 0.82
        })
    
    return insights


# ============ Source 4: KG Entity Generation ============

def generate_kg_insights(kg, new_findings):
    """Generate KG entities from new findings."""
    new_entities_raw = kg.get('entities', {})
    existing_entities = list(new_entities_raw.values()) if isinstance(new_entities_raw, dict) else new_entities_raw
    existing_ids = set(e.get('id', '') for e in existing_entities)
    
    new_entities = []
    
    # Convert findings to KG entities
    for finding in new_findings:
        if 'title' not in finding:
            continue
        
        # Generate entity ID
        base_id = finding.get('title', 'insight')[:40].replace(' ', '-').replace('/', '-')
        entity_id = f"research_{base_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if entity_id not in existing_ids:
            entity = {
                'id': entity_id,
                'type': finding.get('source', 'research_finding').lower().replace(' ', '-'),
                'category': 'research',
                'facts': [{
                    'content': finding.get('title', '')[:200],
                    'confidence': finding.get('confidence', 0.8),
                    'extracted_at': datetime.now().isoformat(),
                    'category': 'research_finding'
                }],
                'priority': 'MEDIUM',
                'created': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 1,
                'decay_score': 10
            }
            
            # Add summary as second fact
            if 'description' in finding:
                entity['facts'].append({
                    'content': finding['description'][:200],
                    'confidence': 0.7,
                    'extracted_at': datetime.now().isoformat(),
                    'category': 'context'
                })
            elif 'summary' in finding:
                entity['facts'].append({
                    'content': finding['summary'][:200],
                    'confidence': 0.7,
                    'extracted_at': datetime.now().isoformat(),
                    'category': 'context'
                })
            
            new_entities.append(entity)
    
    return new_entities


# ============ Main Research Pipeline ============

def run_research(mode='full'):
    """Run the enhanced innovation research pipeline."""
    print("🔬 Enhanced Innovation Research — Maximum Knowledge Focus")
    print("=" * 60)
    
    kg = load_kg()
    log = load_research_log()
    
    all_findings = []
    sources_used = 0
    
    # 1. arXiv papers
    print("\n📚 Searching arXiv...")
    queries = DAILY_QUERIES if mode == 'daily' else DAILY_QUERIES + WEEKLY_QUERIES
    for query in queries[:5]:  # Limit for speed
        results = search_arxiv(query, max_results=3)
        if results and 'error' not in results[0]:
            all_findings.extend(results)
            sources_used += 1
    print(f"   Found {len(all_findings)} papers")
    
    # 2. GitHub Trending
    print("\n⚡ Scanning GitHub Trending...")
    github_results = get_github_trending(limit=8)
    github_ok = [r for r in github_results if 'error' not in r]
    if github_ok:
        all_findings.extend(github_ok)
        sources_used += 1
    print(f"   Found {len(github_ok)} repositories")
    
    # 3. Knowledge Synthesis
    print("\n🧠 Running Knowledge Synthesis...")
    synthesis_insights = synthesize_knowledge(kg)
    synthesis_findings = [{
        'title': s['title'],
        'description': s['content'],
        'source': 'kg_synthesis',
        'confidence': s['confidence'],
        'type': s['type']
    } for s in synthesis_insights]
    all_findings.extend(synthesis_findings)
    sources_used += 1
    print(f"   Generated {len(synthesis_insights)} insights")
    
    # 4. Generate KG entities from findings
    print("\n📊 Generating KG Entities...")
    new_entities = generate_kg_insights(kg, all_findings)
    
    if new_entities:
        kg_entities_add(kg, new_entities)
        print(f"   Created {len(new_entities)} new entities")
        
        # Save enriched KG
        save_kg(kg)
        print(f"   KG now has {kg_entities_count(kg)} entities")
    
    # 5. Update log
    log['entries'].append({
        'timestamp': datetime.now().isoformat(),
        'mode': mode,
        'sources_used': sources_used,
        'findings_count': len(all_findings),
        'new_entities': len(new_entities)
    })
    log['last_full_research'] = datetime.now().isoformat()
    log['sources_searched'] += sources_used
    save_research_log(log)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Research Complete")
    print(f"   Sources queried: {sources_used}")
    print(f"   Total findings: {len(all_findings)}")
    print(f"   New KG entities: {len(new_entities)}")
    
    # Show top findings
    print("\n📋 Top Findings:")
    for i, f in enumerate(all_findings[:5]):
        source_icon = '📝' if f.get('source') == 'arXiv' else '⚡' if f.get('source') == 'GitHub' else '🧠'
        title = f.get('title', f.get('description', 'N/A'))[:60]
        print(f"   {source_icon} {title}")
    
    return {
        'findings': all_findings,
        'new_entities': len(new_entities),
        'sources_used': sources_used
    }


def show_status():
    """Show research status."""
    log = load_research_log()
    kg = load_kg()
    
    print("\n📊 Innovation Research Status")
    print("=" * 40)
    print(f"Total searches: {log.get('sources_searched', 0)}")
    last = log.get('last_full_research', 'Never') or 'Never'
    print(f"Last full research: {last[:19] if last != 'Never' else last}")
    print(f"KG entities: {len(kg.get('entities', []))}")
    print(f"Research log entries: {len(log.get('entries', []))}")


def main():
    if '--daily' in sys.argv:
        run_research(mode='daily')
    elif '--deep' in sys.argv:
        run_research(mode='deep')
    elif '--status' in sys.argv:
        show_status()
    else:
        run_research(mode='full')


if __name__ == '__main__':
    main()
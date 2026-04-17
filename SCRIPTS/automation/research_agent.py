#!/usr/bin/env python3
"""
Research Agent — Sir HazeClaw Multi-Agent Architecture
=====================================================
Dedicated web research + knowledge gathering agent.

Role: Investigator — Web search, arXiv, HN, fact checking
Trigger: Cron (stündlich/täglich) + Event-basiert

Usage:
    python3 research_agent.py --daily      # Daily full research
    python3 research_agent.py --topics     # List current topics
    python3 research_agent.py --test       # Test mode

Phase 2 of Multi-Agent Architecture
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "SCRIPTS" / "automation"
DATA_DIR = WORKSPACE / "data"
EVENTS_DIR = DATA_DIR / "events"
LOGS_DIR = WORKSPACE / "logs"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
RESEARCH_STATE_FILE = DATA_DIR / "research_agent_state.json"

# Research config
ARXIV_DAYS = 7  # How recent arXiv papers should be
HN_STORIES = 10  # Top HN stories to analyze
WEB_RESULTS = 5  # Web search results per topic

# Topics to research (rotating)
RESEARCH_TOPICS = [
    "AI agent self-improvement",
    "LLM reasoning optimization", 
    "autonomous learning systems",
    "token efficiency llm",
    "multi-agent collaboration",
    "knowledge graph retrieval",
    "AI safety alignment",
]

def log(msg: str, level: str = "INFO"):
    """Simple logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "research_agent.log"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": msg
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def load_state() -> Dict:
    """Load research agent state."""
    if RESEARCH_STATE_FILE.exists():
        try:
            return json.load(open(RESEARCH_STATE_FILE))
        except:
            pass
    return {
        "last_research": None,
        "research_count": 0,
        "topics_researched": [],
        "hypotheses_generated": 0,
        "kg_updates": 0,
    }

def save_state(state: Dict):
    """Save research agent state."""
    RESEARCH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESEARCH_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_kg() -> Dict:
    """Load knowledge graph."""
    if KG_PATH.exists():
        try:
            return json.load(open(KG_PATH))
        except:
            return {"entities": {}, "relations": []}
    return {"entities": {}, "relations": []}

def save_kg(kg: Dict):
    """Save knowledge graph."""
    KG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KG_PATH, "w") as f:
        json.dump(kg, f, indent=2)

def search_arxiv(topic: str, max_results: int = 5) -> List[Dict]:
    """Search arXiv for recent papers."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://export.arxiv.org/api/query?search_query=all:{topic}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        papers = []
        entries = re.findall(r'<entry>.*?</entry>', result.stdout, re.DOTALL)
        
        for entry in entries[:max_results]:
            title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            published_match = re.search(r'<published>(.*?)</published>', entry)
            
            if title_match:
                papers.append({
                    "title": title_match.group(1).strip().replace('\n', ' '),
                    "summary": summary_match.group(1).strip()[:500] if summary_match else "",
                    "published": published_match.group(1) if published_match else "",
                    "topic": topic,
                })
        
        log(f"arXiv: Found {len(papers)} papers on {topic}", "INFO")
        return papers
    except Exception as e:
        log(f"arXiv search failed: {e}", "ERROR")
        return []

def search_hackernews(topic: str, max_results: int = 5) -> List[Dict]:
    """Get top HN stories related to topic."""
    # HN Algolia API
    try:
        import urllib.parse
        encoded_topic = urllib.parse.quote(topic)
        result = subprocess.run(
            ["curl", "-s", f"https://hn.algolia.com/api/v1/search?query={encoded_topic}&tags=story&hitsPerPage={max_results}"],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        data = json.loads(result.stdout)
        stories = []
        
        for hit in data.get('hits', [])[:max_results]:
            stories.append({
                "title": hit.get('title', 'N/A'),
                "url": hit.get('url', ''),
                "points": hit.get('points', 0),
                "topic": topic,
            })
        
        log(f"HN: Found {len(stories)} stories on {topic}", "INFO")
        return stories
    except Exception as e:
        log(f"HN search failed: {e}", "ERROR")
        return []

def search_web(topic: str, max_results: int = 5) -> List[Dict]:
    """Web search for topic."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://duckduckgo.com/html/?q={topic.replace(' ', '+')}&h=&format=json"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        # Simple parsing - extract titles and URLs
        results = []
        lines = result.stdout.split('\n')
        for line in lines:
            if '<a href="' in line and 'rel="nof' not in line:
                url_match = re.search(r'href="(https?://[^"]+)"', line)
                title_match = re.search(r'>([^<]+)</a>', line)
                if url_match and title_match:
                    results.append({
                        "title": title_match.group(1).strip(),
                        "url": url_match.group(1),
                        "topic": topic,
                    })
        
        log(f"Web: Found {len(results)} results on {topic}", "INFO")
        return results[:max_results]
    except Exception as e:
        log(f"Web search failed: {e}", "ERROR")
        return []

def generate_hypotheses(research_data: Dict, topic: str) -> List[Dict]:
    """Generate actionable improvement hypotheses from research.
    
    Analyzes patterns in research results to create
    specific, testable improvement hypotheses.
    """
    hypotheses = []
    
    # Pattern: AI agent + self-improvement = capability evolution
    if any(kw in topic.lower() for kw in ['AI agent', 'autonomous', 'self-improve']):
        hypotheses.append({
            "title": f"Apply {topic} pattern",
            "category": "capability_evolution",
            "source": "research",
            "priority": "HIGH",
            "approach": f"Investigate and implement {topic} techniques",
            "expected_impact": "HIGH",
            "confidence": 0.7,
            "research_summary": research_data.get('summary', '')[:200],
        })
    
    # Pattern: token efficiency = cost reduction
    if 'token' in topic.lower() or 'efficiency' in topic.lower():
        hypotheses.append({
            "title": f"Optimize for {topic}",
            "category": "token_optimization",
            "source": "research", 
            "priority": "MEDIUM",
            "approach": f"Apply {topic} to reduce token usage",
            "expected_impact": "MEDIUM",
            "confidence": 0.8,
            "research_summary": research_data.get('summary', '')[:200],
        })
    
    # Pattern: multi-agent = collaboration
    if 'multi-agent' in topic.lower() or 'collaboration' in topic.lower():
        hypotheses.append({
            "title": f"Implement {topic}",
            "category": "multi_agent",
            "source": "research",
            "priority": "HIGH",
            "approach": f"Design and implement {topic} for Sir HazeClaw",
            "expected_impact": "HIGH",
            "confidence": 0.6,
            "research_summary": research_data.get('summary', '')[:200],
        })
    
    return hypotheses

def add_to_kg(kg: Dict, research: Dict, topic: str):
    """Add research results to knowledge graph."""
    entity_id = f"research_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
    
    kg['entities'][entity_id] = {
        "type": "research",
        "category": "research_agent",
        "facts": [{
            "content": f"Research on {topic}: {len(research.get('papers', []))} papers, {len(research.get('stories', []))} HN stories, {len(research.get('web_results', []))} web results",
            "confidence": 0.9,
            "extracted_at": datetime.now().isoformat(),
            "category": "research_summary"
        }],
        "papers": research.get('papers', [])[:3],
        "hn_stories": research.get('stories', [])[:3],
        "topics": [topic],
        "priority": "MEDIUM",
        "created": datetime.now().isoformat(),
        "tags": ["research", "agent", topic.replace(' ', '_')]
    }
    
    return entity_id

def run_daily_research(topic: str = None) -> Dict:
    """Run full research cycle on a topic."""
    state = load_state()
    kg = load_kg()
    
    # Select topic (rotate through list)
    if not topic:
        last_topic_idx = state.get('last_topic_index', -1)
        next_idx = (last_topic_idx + 1) % len(RESEARCH_TOPICS)
        topic = RESEARCH_TOPICS[next_idx]
        state['last_topic_index'] = next_idx
    
    log(f"Starting research on: {topic}", "INFO")
    
    research_results = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "papers": [],
        "stories": [],
        "web_results": [],
        "hypotheses": [],
    }
    
    # Gather research from multiple sources
    research_results['papers'] = search_arxiv(topic, max_results=3)
    research_results['stories'] = search_hackernews(topic, max_results=3)
    research_results['web_results'] = search_web(topic, max_results=3)
    
    # Generate hypotheses
    research_results['hypotheses'] = generate_hypotheses(research_results, topic)
    
    # Add to KG
    entity_id = add_to_kg(kg, research_results, topic)
    research_results['kg_entity_id'] = entity_id
    
    save_kg(kg)
    
    # Update state
    state['last_research'] = datetime.now().isoformat()
    state['research_count'] += 1
    state['topics_researched'].append(topic)
    state['topics_researched'] = state['topics_researched'][-20:]  # Keep last 20
    state['hypotheses_generated'] += len(research_results['hypotheses'])
    state['kg_updates'] += 1
    save_state(state)
    
    log(f"Research complete: {topic} - {len(research_results['hypotheses'])} hypotheses", "INFO")
    
    return research_results

def publish_event(event_type: str, data: Dict):
    """Publish event to event bus."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    event = {
        "type": event_type,
        "source": "research_agent",
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    event_file = EVENTS_DIR / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(event_file, "w") as f:
        json.dump(event, f, indent=2)

def print_research_results(results: Dict):
    """Print research results."""
    print(f"\n🔍 Research Agent — {results['timestamp']}")
    print("=" * 60)
    print(f"📋 Topic: {results['topic']}")
    print(f"\n📚 arXiv Papers: {len(results['papers'])}")
    for p in results['papers'][:3]:
        print(f"   • {p['title'][:70]}...")
    
    print(f"\n📰 HN Stories: {len(results['stories'])}")
    for s in results['stories'][:3]:
        print(f"   • {s['title'][:70]}... ({s.get('points', 0)} pts)")
    
    print(f"\n🌐 Web Results: {len(results['web_results'])}")
    for w in results['web_results'][:3]:
        print(f"   • {w['title'][:70]}")
    
    print(f"\n💡 Hypotheses Generated: {len(results['hypotheses'])}")
    for h in results['hypotheses']:
        print(f"   • [{h['priority']}] {h['title']} ({h['category']})")
    
    print(f"\n📊 KG Entity: {results.get('kg_entity_id', 'N/A')}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Research Agent')
    parser.add_argument('--daily', action='store_true', help='Run daily research')
    parser.add_argument('--topics', action='store_true', help='List research topics')
    parser.add_argument('--test', action='store_true', help='Test mode')
    parser.add_argument('--topic', type=str, help='Specific topic to research')
    args = parser.parse_args()
    
    if args.topics:
        state = load_state()
        print("\n📚 Research Topics (rotating):")
        for i, t in enumerate(RESEARCH_TOPICS):
            current = " ← current" if i == state.get('last_topic_index', -1) + 1 else ""
            print(f"   {i+1}. {t}{current}")
        print(f"\nState: {state.get('research_count', 0)} researches, {state.get('hypotheses_generated', 0)} hypotheses")
        return
    
    if args.daily or args.topic or not args.test:
        results = run_daily_research(args.topic)
        print_research_results(results)
        
        # Publish event
        publish_event('research.completed', {
            'topic': results['topic'],
            'hypotheses_count': len(results['hypotheses']),
            'kg_entity_id': results.get('kg_entity_id'),
        })
    else:
        # Test mode
        print("🔍 Research Agent — Test Mode")
        print("Run with --daily for actual research")
        
        state = load_state()
        print(f"\n📊 State: {state.get('research_count', 0)} researches")
        print(f"📋 Next topic: {RESEARCH_TOPICS[(state.get('last_topic_index', -1) + 1) % len(RESEARCH_TOPICS)]}")

if __name__ == "__main__":
    main()

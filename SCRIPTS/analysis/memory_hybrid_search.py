#!/usr/bin/env python3
"""
Sir HazeClaw Hybrid Memory Search — IMPROVED
Combines Keyword + Semantic + Context-Aware Search.

Improvements:
- Context awareness (current situation)
- Date-based relevance weighting
- Better snippet extraction
- KG entity search improved
- Recent memories prioritized

Usage:
    python3 memory_hybrid_search.py <query>
    python3 memory_hybrid_search.py <query> --limit 10
    python3 memory_hybrid_search.py <query> --days 7
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# Import reranker
sys.path.insert(0, str(Path(__file__).parent))
try:
    from memory_reranker import rerank as rerank_candidates, deduplicate_results
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
MEMORY_DIR = WORKSPACE / "memory"

# Search weights
KW_WEIGHT = 0.3
SEM_WEIGHT = 0.5
RECENCY_WEIGHT = 0.2

# Config
MAX_RESULTS = 5
RECENCY_WINDOW_DAYS = 7

def get_file_age_days(filepath: Path) -> int:
    """Gibt Alter einer Datei in Tagen zurück."""
    try:
        mtime = filepath.stat().st_mtime
        return (datetime.now().timestamp() - mtime) / 86400
    except:
        return 999

def calculate_recency_score(filepath: Path) -> float:
    """Berechnet Recency Score (jünger = höherer Score)."""
    age_days = get_file_age_days(filepath)
    
    if age_days <= 1:
        return 1.0
    elif age_days <= 7:
        return 0.7
    elif age_days <= 30:
        return 0.4
    else:
        return 0.1

def keyword_search(query: str, files: List[str]) -> List[Tuple[str, float]]:
    """Sucht nach Keywords in Dateien."""
    results = []
    query_lower = query.lower()
    query_words = re.findall(r'\w+', query_lower)
    
    for filepath in files:
        path = Path(filepath)
        
        if not path.exists():
            continue
        
        if path.is_dir():
            for mf in path.glob('*.md'):
                score = calculate_keyword_score(query_words, mf)
                if score > 0:
                    results.append((str(mf), score))
        elif path.suffix == '.md':
            score = calculate_keyword_score(query_words, path)
            if score > 0:
                results.append((filepath, score))
    
    return results

def calculate_keyword_score(query_words: List[str], filepath: Path) -> float:
    """Berechnet Keyword Match Score."""
    try:
        with open(filepath) as f:
            content = f.read().lower()
        
        score = 0
        for word in query_words:
            # Title match (first 200 chars) = higher score
            if word in content[:200]:
                score += 3
            # Body match
            score += content.count(word) * 0.5
        
        # Normalize by content length
        content_len = len(content) / 1000
        return score / max(content_len, 0.1)
    except Exception:
        return 0

def semantic_search(query: str, limit: int = 20) -> List[Tuple[str, float]]:
    """Sucht semantisch im Knowledge Graph.
    
    NOTE: After search, call update_kg_access() to track KG usage!
    """
    results = []
    accessed_entities = []  # Track accessed entities
    
    if not KG_PATH.exists():
        return results
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        query_words = set(re.findall(r'\w+', query.lower()))
        
        for entity_id, data in kg.get('entities', {}).items():
            entity_lower = entity_id.lower()
            entity_score = 0.0
            
            # Exact entity match
            if any(word in entity_lower for word in query_words):
                entity_score = 0.9
            
            # Fact content match
            for fact in data.get('facts', []):
                fact_content = fact.get('content', '').lower()
                
                # Title match in facts
                if any(word in entity_lower for word in query_words):
                    entity_score = max(entity_score, 0.7)
                
                # Content match
                matched_words = sum(1 for word in query_words if word in fact_content)
                if matched_words > 0:
                    word_score = matched_words / len(query_words)
                    entity_score = max(entity_score, word_score * 0.6)
            
            if entity_score > 0:
                results.append((f"entity:{entity_id}", entity_score))
                accessed_entities.append(entity_id)  # Track for access_count update
        
        # Sort by score
        results.sort(key=lambda x: -x[1])
        
        # Update KG access tracking
        if accessed_entities:
            update_kg_access(accessed_entities)
        
        return results[:limit]
    
    except Exception as e:
        return []


def update_kg_access(entity_names: List[str], kg_path: Path = KG_PATH) -> None:
    """Update access_count and last_accessed for KG entities.
    
    This is the VERIFY/闭环 phase - tracking KG usage!
    Without this, KG access_count stays 0 forever.
    """
    if not kg_path.exists() or not entity_names:
        return
    
    try:
        with open(kg_path) as f:
            kg = json.load(f)
        
        now = datetime.now().isoformat()
        updated = 0
        
        for name in entity_names:
            if name in kg.get('entities', {}):
                entity = kg['entities'][name]
                entity['last_accessed'] = now
                entity['access_count'] = entity.get('access_count', 0) + 1
                updated += 1
        
        if updated > 0:
            # Save updated KG
            with open(kg_path, 'w') as f:
                json.dump(kg, f, indent=2)
            
            # Log KG hit rate
            log_kg_hit_rate(updated, len(entity_names))
    
    except Exception as e:
        pass  # Don't fail search if KG update fails


KG_HIT_LOG = Path("/home/clawbot/.openclaw/workspace/logs/kg_hit_rate.log")

def log_kg_hit_rate(hits: int, queried: int) -> None:
    """Log KG usage for tracking."""
    try:
        KG_HIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(KG_HIT_LOG, 'a') as f:
            f.write(f"[{timestamp}] KG hits: {hits}/{queried} entities accessed\n")
    except:
        pass

def extract_snippet(filepath: str, query_words: List[str], max_len: int = 200) -> str:
    """Extrahiert relevanten Snippet aus Datei."""
    try:
        with open(filepath) as f:
            content = f.read()
        
        content_lower = content.lower()
        
        # Find best position (first keyword match)
        best_pos = 0
        best_score = 0
        
        for i, word in enumerate(query_words):
            pos = content_lower.find(word)
            if pos != -1:
                # Earlier match = better
                score = 1000 - pos
                if score > best_score:
                    best_score = score
                    best_pos = max(0, pos - 50)
        
        # Extract snippet
        snippet = content[best_pos:best_pos + max_len]
        snippet = snippet.replace('\n', ' ').strip()
        
        # Add context markers if truncated
        if best_pos > 0:
            snippet = "..." + snippet
        if best_pos + max_len < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    except Exception:
        return ""

def hybrid_search(query: str, limit: int = 5, days: int = 30) -> List[Dict]:
    """Führt kombinierte Suche durch."""
    kw_weight = KW_WEIGHT
    sem_weight = SEM_WEIGHT
    rec_weight = RECENCY_WEIGHT
    
    # Find search paths
    search_paths = []
    
    # Core files
    for name in ['SOUL.md', 'USER.md', 'IDENTITY.md', 'HEARTBEAT.md', 'MEMORY_ARCHITECTURE.md']:
        path = WORKSPACE / name
        if path.exists():
            search_paths.append(path)
    
    # Memory directory
    if MEMORY_DIR.exists():
        search_paths.append(MEMORY_DIR)
    
    # CEO directory
    ceo_dir = WORKSPACE / "ceo"
    if ceo_dir.exists():
        search_paths.append(ceo_dir)
    
    # Collect all files
    all_files = []
    for path in search_paths:
        if path.is_dir():
            for pattern in ['*.md', '*.txt']:
                all_files.extend(path.glob(pattern))
        else:
            all_files.append(path)
    
    # Filter by date if specified
    if days > 0:
        max_age = days
        all_files = [f for f in all_files if get_file_age_days(f) <= max_age]
    
    # Keyword search
    keyword_results = keyword_search(query, [str(f) for f in all_files])
    
    # Semantic search in KG
    semantic_results = semantic_search(query, limit * 2)
    
    # Combine results
    combined = {}
    
    for filepath, score in keyword_results:
        recency = calculate_recency_score(Path(filepath))
        combined[filepath] = score * kw_weight + recency * rec_weight
    
    for ref, score in semantic_results:
        # Semantic results don't have recency
        if ref in combined:
            combined[ref] += score * sem_weight
        else:
            combined[ref] = score * sem_weight
    
    # Sort by combined score
    sorted_results = sorted(combined.items(), key=lambda x: -x[1])[:limit]
    
    # Build output
    output = []
    query_words = re.findall(r'\w+', query.lower())
    
    for filepath, score in sorted_results:
        if filepath.startswith('entity:'):
            output.append({
                'type': 'entity',
                'source': filepath,
                'score': round(score, 3),
                'relevance': 'high' if score > 0.6 else 'medium' if score > 0.3 else 'low'
            })
        else:
            snippet = extract_snippet(filepath, query_words)
            output.append({
                'type': 'file',
                'source': filepath.replace(str(WORKSPACE), ''),
                'score': round(score, 3),
                'snippet': snippet,
                'relevance': 'high' if score > 0.4 else 'medium' if score > 0.2 else 'low'
            })
    
    # Load full content for reranking (files only)
    if RERANKER_AVAILABLE:
        for r in output:
            if r['type'] == 'file':
                # Fix path: remove leading slash to make it relative
                rel_path = r['source'].lstrip('/')
                filepath = WORKSPACE / rel_path
                if filepath.exists():
                    try:
                        with open(filepath) as f:
                            r['content'] = f.read()[:2000]  # First 2000 chars
                    except:
                        r['content'] = r.get('snippet', '')
                else:
                    r['content'] = r.get('snippet', '')
            else:
                # For entities, use empty content (reranker will skip)
                r['content'] = ''
    
    # Apply reranking if available
    if RERANKER_AVAILABLE and output:
        output = rerank_candidates(query, output)
    
    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: memory_hybrid_search.py <query> [--limit N] [--days N]")
        sys.exit(1)
    
    query = sys.argv[1]
    limit = MAX_RESULTS
    days = 0  # No date filter by default
    
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        limit = int(sys.argv[idx + 1])
    
    if '--days' in sys.argv:
        idx = sys.argv.index('--days')
        days = int(sys.argv[idx + 1])
    
    results = hybrid_search(query, limit, days)
    
    print(f"\n🔍 **Results for:** '{query}'\n")
    
    if not results:
        print("_No results found_")
        return
    
    for i, r in enumerate(results, 1):
        relevance_emoji = '🟢' if r.get('relevance') == 'high' else '🟡' if r.get('relevance') == 'medium' else '⚪'
        
        if r['type'] == 'entity':
            entity_name = r['source'].replace('entity:', '')
            print(f"{i}. {relevance_emoji} **[ENTITY]** `{entity_name}`")
            print(f"   Score: {r['score']}")
        else:
            print(f"{i}. {relevance_emoji} **[FILE]** `{r['source']}`")
            print(f"   Score: {r['score']}")
            if r.get('snippet'):
                print(f"   _{r['snippet'][:120]}..._")
        print()

if __name__ == '__main__':
    main()

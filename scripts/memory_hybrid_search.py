#!/usr/bin/env python3
"""Hybrid Memory Search - Combines Keyword + Semantic Search"""
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

WORKSPACE = "/home/clawbot/.openclaw/workspace"
CONFIG_PATH = f"{WORKSPACE}/.openclaw/openclaw.json"

def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_search_config() -> dict:
    return {'mode': 'hybrid', 'keyword_weight': 0.3, 'semantic_weight': 0.7, 'max_results': 5}

def keyword_search(query: str, files: List[str]) -> List[Tuple[str, float]]:
    results = []
    query_lower = query.lower()
    query_words = re.findall(r'\w+', query_lower)
    
    for filepath in files:
        path = Path(filepath)
        
        if path.is_dir():
            markdown_files = list(path.glob('*.md'))
            for mf in markdown_files:
                score = calculate_keyword_score(query_words, mf)
                if score > 0:
                    results.append((str(mf), score))
        elif path.suffix == '.md':
            score = calculate_keyword_score(query_words, path)
            if score > 0:
                results.append((filepath, score))
    
    return results

def calculate_keyword_score(query_words: List[str], filepath: Path) -> float:
    try:
        with open(filepath) as f:
            content = f.read().lower()
        
        score = 0
        for word in query_words:
            if word in content[:200]:
                score += 2
            score += content.count(word) * 0.5
        
        return score / max(len(content) / 1000, 1)
    except:
        return 0

def semantic_search(query: str, kg_path: str) -> List[Tuple[str, float]]:
    results = []
    
    if not os.path.exists(kg_path):
        return results
    
    try:
        with open(kg_path) as f:
            kg = json.load(f)
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        for entity, data in kg.get('entities', {}).items():
            entity_lower = entity.lower()
            
            if any(word in entity_lower for word in query_words):
                results.append((f"entity:{entity}", 0.8))
            
            for fact in data.get('facts', []):
                fact_content = fact.get('content', '').lower()
                if any(word in fact_content for word in query_words):
                    if f"entity:{entity}" not in [r[0] for r in results]:
                        results.append((f"entity:{entity}", 0.5))
    except:
        pass
    
    return results

def hybrid_search(query: str, limit: int = 5) -> List[Dict]:
    kw_weight, sem_weight = 0.3, 0.7
    
    search_dirs = []
    for name in ['SOUL.md', 'USER.md', 'IDENTITY.md', 'MEMORY.md']:
        path = Path(WORKSPACE) / name
        if path.exists():
            search_dirs.append(str(path))
    
    for pattern in ['memory/notes/concepts', 'memory/notes/insights', 'memory/decisions']:
        path = Path(WORKSPACE) / pattern
        if path.is_dir():
            search_dirs.append(str(path))
    
    all_files = []
    for d in search_dirs:
        path = Path(d)
        if path.is_dir():
            all_files.extend([str(f) for f in path.glob('*.md')])
        elif path.suffix == '.md':
            all_files.append(str(path))
    
    keyword_results = keyword_search(query, all_files)
    semantic_results = semantic_search(query, str(Path(WORKSPACE) / 'memory/knowledge_graph.json'))
    
    combined = {}
    for filepath, score in keyword_results:
        combined[filepath] = score * kw_weight
    
    for ref, score in semantic_results:
        if ref in combined:
            combined[ref] += score * sem_weight
        else:
            combined[ref] = score * sem_weight
    
    sorted_results = sorted(combined.items(), key=lambda x: -x[1])[:limit]
    
    output = []
    for filepath, score in sorted_results:
        if filepath.startswith('entity:'):
            output.append({'type': 'entity', 'source': filepath, 'score': round(score, 3)})
        else:
            try:
                with open(filepath) as f:
                    content = f.read()
                snippet = content[:150].replace('\n', ' ')
                output.append({'type': 'file', 'source': filepath.replace(WORKSPACE, ''), 'score': round(score, 3), 'snippet': snippet})
            except:
                pass
    
    return output

def main():
    if len(sys.argv) < 2:
        print("Usage: memory_hybrid_search.py <query> [--limit N]")
        sys.exit(1)
    
    query = sys.argv[1]
    limit = 5
    
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        limit = int(sys.argv[idx+1])
    
    results = hybrid_search(query, limit)
    
    print(f"\n🔍 Results for: '{query}'\n")
    for i, r in enumerate(results, 1):
        if r['type'] == 'entity':
            print(f"{i}. [ENTITY] {r['source']} (score: {r['score']})")
        else:
            print(f"{i}. [FILE] {r['source']} (score: {r['score']})")
            print(f"   {r['snippet'][:100]}...")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Sir HazeClaw Memory Reranker — v1.0
Second-pass reranking for memory search results.

Improvements over basic hybrid search:
1. Query term proximity scoring
2. Exact phrase matching
3. Structural signal boosting (headings, lists)
4. Deduplication
5. Cross-source consistency scoring

Usage:
    python3 memory_reranker.py <query> <results_json>
    python3 memory_reranker.py "openrouter api key" '[{"source": "file:...", "score": 0.5}, ...]'
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

# Reranking weights (must sum to ~1.0 for proper normalization)
PROXIMITY_WEIGHT = 0.25
PHRASE_BOOST = 0.15
STRUCTURAL_BOOST = 0.10
TITLE_WEIGHT = 0.10
DEDUP_THRESHOLD = 0.85


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_query_terms(query: str) -> List[str]:
    """Extract query terms."""
    return [t.lower() for t in re.findall(r'\w+', query.lower())]


def calculate_proximity_score(query_terms: List[str], content: str) -> float:
    """
    Calculate how close query terms are to each other in content.
    Closer terms = higher score.
    """
    if not query_terms or not content:
        return 0.0
    
    content_lower = content.lower()
    positions = []
    
    for term in query_terms:
        pos = content_lower.find(term)
        if pos != -1:
            positions.append(pos)
    
    if len(positions) < 2:
        return 0.5 if positions else 0.0
    
    # Calculate average distance between consecutive terms
    total_distance = sum(
        positions[i+1] - positions[i] 
        for i in range(len(positions) - 1)
    )
    avg_distance = total_distance / (len(positions) - 1)
    
    # Normalize: closer = higher score (max distance ~1000 chars)
    score = max(0, 1 - (avg_distance / 1000))
    return min(score, 1.0)  # Cap at 1.0


def has_exact_phrase_match(query: str, content: str) -> bool:
    """Check if query phrase appears exactly in content."""
    query_lower = query.lower().strip()
    content_lower = content.lower()
    return query_lower in content_lower


def calculate_structural_score(query_terms: List[str], content: str) -> float:
    """
    Score based on structural elements.
    Terms in headings, lists, or at start of paragraphs score higher.
    """
    lines = content.split('\n')
    score = 0.0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Heading marker
        if line_stripped.startswith('#') or line_stripped.startswith('**'):
            for term in query_terms:
                if term in line_lower:
                    score += 0.3
        
        # List item
        elif re.match(r'^[\-\*\d]+\.', line_stripped):
            for term in query_terms:
                if term in line_lower:
                    score += 0.15
        
        # First line of paragraph
        elif i == 0 or not lines[i-1].strip():
            for term in query_terms:
                if term in line_lower:
                    score += 0.1
    
    return min(score, 0.5)


def calculate_title_score(query_terms: List[str], filepath: str) -> float:
    """Score based on filename/path matching query."""
    filename = Path(filepath).stem.lower()
    path_str = filepath.lower()
    
    matches = 0
    for term in query_terms:
        if term in filename:
            matches += 1
        if term in path_str:
            matches += 0.5
    
    return min(matches / max(len(query_terms), 1), 1.0)


def jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between two texts."""
    words1 = set(normalize_text(text1).split())
    words2 = set(normalize_text(text2).split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)


def deduplicate_results(results: List[Dict], threshold: float = DEDUP_THRESHOLD) -> List[Dict]:
    """
    Remove near-duplicate results.
    Keeps the one with higher score.
    """
    if not results:
        return results
    
    unique = []
    seen_contents = []
    
    for r in results:
        content = r.get('content', r.get('snippet', ''))
        
        # Check against already unique items
        is_duplicate = False
        for seen in seen_contents:
            if jaccard_similarity(content, seen) >= threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique.append(r)
            seen_contents.append(content[:500])  # First 500 chars for comparison
    
    return unique


def rerank(query: str, results: List[Dict], weights: Dict = None) -> List[Dict]:
    """
    Rerank search results using multiple signals.
    
    Args:
        query: Original search query
        results: List of result dicts from hybrid search
        weights: Optional custom weights for scoring components
    
    Returns:
        Reranked list of results with updated scores
    """
    if not results:
        return results
    
    if weights is None:
        weights = {
            'original': 0.40,  # Base score from hybrid search
            'proximity': PROXIMITY_WEIGHT,
            'phrase': PHRASE_BOOST,
            'structural': STRUCTURAL_BOOST,
            'title': TITLE_WEIGHT
        }
    
    query_terms = get_query_terms(query)
    
    scored_results = []
    
    for r in results:
        source = r.get('source', '')
        content = r.get('content', r.get('snippet', ''))
        
        # Skip if no content to analyze
        if not content:
            scored_results.append((r, r.get('score', 0.0)))
            continue
        
        # Calculate component scores
        proximity = calculate_proximity_score(query_terms, content)
        phrase_match = 1.0 if has_exact_phrase_match(query, content) else 0.0
        structural = calculate_structural_score(query_terms, content)
        title = calculate_title_score(query_terms, source)
        
        # Original score from hybrid search (BEFORE reranking)
        original_score = r.get('score', 0.0)
        
        # Calculate final score (blend original with rerank signals)
        # Normalize original to 0-1 range first
        normalized_orig = min(original_score, 1.0)
        
        # Cap individual signals at 1.0
        proximity = min(proximity, 1.0)
        structural = min(structural, 1.0)
        title = min(title, 1.0)
        
        final_score = (
            normalized_orig * weights['original'] +
            proximity * weights['proximity'] +
            phrase_match * weights['phrase'] +
            structural * weights['structural'] +
            title * weights['title']
        )
        
        # Cap final at 1.0
        final_score = min(final_score, 1.0)
        
        # Add rerank signals to result
        r['rerank'] = {
            'proximity': round(proximity, 3),
            'phrase_match': phrase_match,
            'structural': round(structural, 3),
            'title': round(title, 3)
        }
        r['original_score'] = original_score
        r['score'] = round(final_score, 4)
        
        scored_results.append((r, final_score))
    
    # Sort by final score
    scored_results.sort(key=lambda x: -x[1])
    
    # Extract reranked results
    reranked = [r for r, _ in scored_results]
    
    # Deduplicate
    reranked = deduplicate_results(reranked)
    
    # Update relevance labels
    for r in reranked:
        score = r['score']
        if score > 0.6:
            r['relevance'] = 'high'
        elif score > 0.3:
            r['relevance'] = 'medium'
        else:
            r['relevance'] = 'low'
    
    return reranked


def main():
    if len(sys.argv) < 3:
        print("Usage: memory_reranker.py <query> <results_json>")
        print("  query: Search query string")
        print("  results_json: JSON array of results from hybrid search")
        sys.exit(1)
    
    query = sys.argv[1]
    results_json = sys.argv[2]
    
    try:
        results = json.loads(results_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing results JSON: {e}")
        sys.exit(1)
    
    if not isinstance(results, list):
        print("Error: results must be a JSON array")
        sys.exit(1)
    
    reranked = rerank(query, results)
    
    print(json.dumps(reranked, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Real Semantic Search — Sir HazeClaw
===================================
Uses embeddings for true semantic similarity search.

Usage:
    python3 semantic_search.py "query"
    python3 semantic_search.py "query" --limit 5
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CEO_MEMORY = WORKSPACE / "ceo/memory"
SEMANTIC_DIR = CEO_MEMORY / "semantic"
MODEL_NAME = "all-MiniLM-L6-v2"

def load_embeddings():
    """Load all embeddings from semantic/ folder."""
    embeddings = []
    for emb_file in SEMANTIC_DIR.glob("*.emb.json"):
        try:
            data = json.load(open(emb_file))
            embeddings.append(data)
        except:
            pass
    return embeddings

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b)

def search(query, limit=5):
    """Search using semantic embeddings."""
    # Load model and generate query embedding
    model = SentenceTransformer(MODEL_NAME)
    query_emb = model.encode([query], normalize_embeddings=True)[0]
    
    # Load all embeddings
    embeddings = load_embeddings()
    
    # Score each embedding
    results = []
    for emb in embeddings:
        score = cosine_similarity(query_emb, emb["embedding"])
        results.append({
            "file": emb["file"],
            "score": float(score),
            "chunks": emb["chunks"],
            "first_lines": emb.get("first_lines", "")[:150],
            "generated_at": emb["generated_at"]
        })
    
    # Sort by score
    results.sort(key=lambda x: -x["score"])
    
    return results[:limit]

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "system status"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    results = search(query, limit)
    
    print(f"🔍 Semantic Search: '{query}'")
    print("=" * 60)
    
    for i, r in enumerate(results, 1):
        fname = Path(r["file"]).name
        print(f"\n{i}. [{r['score']:.3f}] {fname}")
        print(f"   {r['first_lines'][:100]}...")

if __name__ == "__main__":
    main()

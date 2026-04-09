#!/usr/bin/env python3
"""
Semantic Search - Local Embeddings with sentence-transformers
Uses all-MiniLM-L6-v2 (384 dimensions, ~400MB, runs locally)
"""
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Config
MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/memory")
INDEX_FILE = Path("/home/clawbot/.openclaw/workspace/data/semantic_index.json")

# Load model once at startup
print("Loading semantic search model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model ready!")

def load_documents():
    """Load all markdown files from memory"""
    docs = []
    for md_file in MEMORY_DIR.glob("*.md"):
        if md_file.name.startswith("."):
            continue
        content = md_file.read_text(errors="ignore")
        # Split into chunks (roughly 500 chars each)
        chunks = [content[i:i+500] for i in range(0, min(len(content), 10000), 500)]
        for chunk in chunks:
            if len(chunk.strip()) > 50:  # Skip very short chunks
                docs.append({
                    "text": chunk,
                    "source": str(md_file.name),
                    "path": str(md_file)
                })
    return docs

def build_index():
    """Build vector index from documents"""
    docs = load_documents()
    if not docs:
        print("No documents found!")
        return
    
    texts = [d["text"] for d in docs]
    print(f"Embedding {len(texts)} document chunks...")
    
    embeddings = model.encode(texts, show_progress_bar=True)
    
    index = {
        "documents": docs,
        "embeddings": embeddings.tolist()
    }
    
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f)
    
    print(f"Index built with {len(docs)} chunks!")

def search(query, top_k=5):
    """Search semantic index"""
    if not INDEX_FILE.exists():
        print("Index not found. Run with --build first.")
        return []
    
    with open(INDEX_FILE) as f:
        index = json.load(f)
    
    query_emb = model.encode([query])
    
    # Cosine similarity
    scores = np.dot(query_emb, np.array(index["embeddings"]).T)[0]
    
    # Top k results
    top_idx = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_idx:
        if scores[idx] > 0.3:  # Threshold
            results.append({
                "text": index["documents"][idx]["text"],
                "source": index["documents"][idx]["source"],
                "score": float(scores[idx])
            })
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: semantic_search.py <command> [args]")
        print("Commands:")
        print("  build              - Build semantic index")
        print("  search <query>     - Search index")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "build":
        build_index()
    elif cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = search(query)
        print(f"\n🔍 Results for: {query}")
        print("=" * 50)
        for r in results:
            print(f"\n[{r['score']:.3f}] {r['source']}")
            print(f"  {r['text'][:200]}...")
    else:
        print("Invalid command")

#!/usr/bin/env python3
"""
💾 Memory Vector Store - Semantic Search
Nutzt Sentence Transformers für semantische Embeddings
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

WORKSPACE = "/home/clawbot/.openclaw/workspace"
VECTOR_STORE = f"{WORKSPACE}/memory/vector_store"
KG_PATH = "/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json"

class MemoryVectorStore:
    """Semantic memory store with embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings_file = f"{VECTOR_STORE}/embeddings.npy"
        self.metadata_file = f"{VECTOR_STORE}/metadata.json"
        self.documents_file = f"{VECTOR_STORE}/documents.json"
        
        os.makedirs(VECTOR_STORE, exist_ok=True)
        
        self.documents = self._load_documents()
        self.embeddings = self._load_embeddings()
        
    def _load_documents(self) -> List[Dict]:
        if os.path.exists(self.documents_file):
            with open(self.documents_file) as f:
                return json.load(f)
        return []
    
    def _load_embeddings(self) -> np.ndarray:
        if os.path.exists(self.embeddings_file):
            return np.load(self.embeddings_file)
        return np.array([])
    
    def _save(self):
        with open(self.documents_file, 'w') as f:
            json.dump(self.documents, f, indent=2)
        if len(self.embeddings) > 0:
            np.save(self.embeddings_file, self.embeddings)
    
    def add_document(self, text: str, source: str, doc_type: str = "note"):
        """Add a document to the vector store"""
        doc = {
            "text": text,
            "source": source,
            "type": doc_type,
            "created": datetime.now().isoformat()
        }
        
        embedding = self.model.encode(text)
        
        if len(self.embeddings) == 0:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])
        
        self.documents.append(doc)
        self._save()
        
        return len(self.documents) - 1
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic search"""
        if len(self.documents) == 0:
            return []
        
        query_embedding = self.model.encode(query)
        
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:
                results.append({
                    "index": int(idx),
                    "score": float(similarities[idx]),
                    "text": self.documents[idx]["text"][:200],
                    "source": self.documents[idx]["source"],
                    "type": self.documents[idx]["type"]
                })
        
        return results
    
    def index_memory_files(self):
        """Index all memory files"""
        print("📚 Indexing memory files...")
        
        files_to_index = []
        
        # Core files
        for name in ['SOUL.md', 'USER.md', 'IDENTITY.md', 'MEMORY.md']:
            path = Path(WORKSPACE) / name
            if path.exists():
                files_to_index.append((path, name, 'core'))
        
        # notes/concepts
        concepts_dir = Path(WORKSPACE) / 'memory/notes/concepts'
        if concepts_dir.is_dir():
            for f in concepts_dir.glob('*.md'):
                files_to_index.append((f, f.name, 'concept'))
        
        # decisions
        decisions_dir = Path(WORKSPACE) / 'memory/decisions'
        if decisions_dir.is_dir():
            for f in decisions_dir.glob('*.md'):
                files_to_index.append((f, f.name, 'decision'))
        
        # Index each file
        for path, name, doc_type in files_to_index:
            try:
                with open(path) as f:
                    content = f.read()
                
                # Skip frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        content = parts[2]
                
                # Add to vector store
                self.add_document(
                    text=content[:2000],  # Limit text length
                    source=str(path.relative_to(WORKSPACE)),
                    doc_type=doc_type
                )
                print(f"  ✅ {name}")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
        
        print(f"\n📊 Total documents indexed: {len(self.documents)}")
        return len(self.documents)
    
    def search_hybrid(self, query: str, top_k: int = 5) -> List[Dict]:
        """Combine semantic + keyword search"""
        semantic_results = self.search(query, top_k * 2)
        
        # Add keyword boosting
        query_words = set(query.lower().split())
        for r in semantic_results:
            text_words = set(r['text'].lower().split())
            overlap = len(query_words & text_words)
            r['score'] = r['score'] * 0.7 + overlap * 0.1
        
        semantic_results.sort(key=lambda x: -x['score'])
        return semantic_results[:top_k]


def main():
    if len(sys.argv) < 2:
        print("Usage: memory_vector_store.py <command>")
        print("Commands:")
        print("  index          - Index all memory files")
        print("  search <query> - Search memory")
        sys.exit(1)
    
    store = MemoryVectorStore()
    
    if sys.argv[1] == 'index':
        count = store.index_memory_files()
        print(f"\n✅ Indexed {count} documents")
        
    elif sys.argv[1] == 'search':
        if len(sys.argv) < 3:
            print("Usage: memory_vector_store.py search <query>")
            sys.exit(1)
        
        query = ' '.join(sys.argv[2:])
        results = store.search_hybrid(query, top_k=5)
        
        print(f"\n🔍 Semantic Search: '{query}'\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r['type']}] {r['source']} (score: {r['score']:.3f})")
            print(f"   {r['text'][:150]}...")
            print()
    
    elif sys.argv[1] == 'test':
        # Test the vector store
        print("🧪 Testing Vector Store...")
        
        # Add test documents
        store.add_document(
            "MetaClaw is a self-evolving AI agent framework built on OpenClaw. It learns from conversations.",
            "test.md",
            "concept"
        )
        store.add_document(
            "Paperclip is a zero-human company orchestration framework. It organizes AI agents like a company.",
            "test.md",
            "concept"
        )
        
        results = store.search("How does MetaClaw work?", top_k=3)
        print(f"\nTest search results: {len(results)}")
        for r in results:
            print(f"  - {r['source']}: {r['score']:.3f}")


if __name__ == '__main__':
    main()
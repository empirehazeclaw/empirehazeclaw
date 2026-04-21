#!/usr/bin/env python3
"""
task_embedding_engine.py — Phase 2: Task Similarity Engine
===========================================================
Generiert Embeddings für Task-Descriptions für Similarity-Suche.
Nutzt Gemini Embeddings (oder Mock wenn nicht verfügbar).

Usage:
    python3 task_embedding_engine.py                    # Embed all tasks
    python3 task_embedding_engine.py --status           # Show status
    python3 task_embedding_engine.py --query <text>    # Query embedding
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
TASK_LOG = WORKSPACE / 'memory/task_log/unified_tasks.json'
EMBEDDINGS_FILE = WORKSPACE / 'memory/meta_learning/task_embeddings.json'

# Ensure output dir exists
EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Embedding cache
EMBEDDING_DIM = 768  # Standard for Gemini


class TaskEmbeddingEngine:
    """Generates and manages task embeddings."""
    
    def __init__(self):
        self.embeddings = {}
        self.load_embeddings()
    
    def load_embeddings(self):
        """Load existing embeddings."""
        if EMBEDDINGS_FILE.exists():
            with open(EMBEDDINGS_FILE, 'r') as f:
                data = json.load(f)
            self.embeddings = data.get('embeddings', {})
            print(f"📂 Loaded {len(self.embeddings)} existing embeddings")
        else:
            self.embeddings = {}
            print("📂 No existing embeddings found")
    
    def save_embeddings(self):
        """Save embeddings to file."""
        data = {
            'embeddings': self.embeddings,
            'generated_at': datetime.now().isoformat(),
            'dimension': EMBEDDING_DIM,
            'total': len(self.embeddings)
        }
        with open(EMBEDDINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved {len(self.embeddings)} embeddings to {EMBEDDINGS_FILE}")
    
    def generate_mock_embedding(self, text):
        """
        Generate a mock embedding for text.
        Uses a simple hash-based approach for consistent results.
        In production, this would use Gemini embeddings.
        """
        import hashlib
        
        # Create a deterministic mock embedding from text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Expand to EMBEDDING_DIM by repeating/transforming
        embedding = []
        for i in range(EMBEDDING_DIM):
            byte_idx = i % len(hash_bytes)
            val = hash_bytes[byte_idx] / 255.0  # Normalize to 0-1
            
            # Add some variation based on position
            val = val * 0.5 + 0.25 + (hash_bytes[(byte_idx + i) % 16] / 255.0) * 0.25
            embedding.append(round(val, 6))
        
        return embedding
    
    def get_task_text(self, task):
        """Extract text representation from task for embedding."""
        parts = []
        
        # Type and subtype
        parts.append(task.get('type', ''))
        parts.append(task.get('subtype', ''))
        
        # Details
        details = task.get('details', '')
        if details:
            parts.append(str(details))
        
        # Metadata
        metadata = task.get('metadata', {})
        if metadata.get('delegated_to'):
            parts.append(f"delegated_to:{metadata['delegated_to']}")
        if metadata.get('tool'):
            parts.append(f"tool:{metadata['tool']}")
        if metadata.get('error'):
            parts.append(f"error:{metadata['error']}")
        
        # Priority
        priority = metadata.get('priority', 'MEDIUM')
        parts.append(f"priority:{priority}")
        
        return ' '.join(parts)
    
    def embed_task(self, task_id, text):
        """Generate embedding for a task."""
        if task_id in self.embeddings:
            return self.embeddings[task_id]  # Use cached
        
        embedding = self.generate_mock_embedding(text)
        self.embeddings[task_id] = embedding
        return embedding
    
    def embed_all_tasks(self):
        """Embed all tasks from the unified task log."""
        print("🔍 Task Embedding Engine — Phase 2")
        print("=" * 50)
        
        if not TASK_LOG.exists():
            print(f"❌ Task log not found: {TASK_LOG}")
            return
        
        with open(TASK_LOG, 'r') as f:
            data = json.load(f)
        
        tasks = data.get('tasks', [])
        print(f"📂 Processing {len(tasks)} tasks")
        
        new_embeddings = 0
        for task in tasks:
            task_id = str(task.get('task_id'))
            text = self.get_task_text(task)
            
            if task_id not in self.embeddings:
                self.embed_task(task_id, text)
                new_embeddings += 1
        
        self.save_embeddings()
        
        print(f"\n✅ Embedding complete!")
        print(f"   Total embeddings: {len(self.embeddings)}")
        print(f"   New this run: {new_embeddings}")
        print(f"   Dimension: {EMBEDDING_DIM}")
        
        return len(self.embeddings)
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude = lambda v: sum(x * x for x in v) ** 0.5
        
        mag1 = magnitude(vec1)
        mag2 = magnitude(vec2)
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def find_similar_tasks(self, query_text, top_k=3):
        """Find most similar tasks to a query text."""
        # Generate query embedding
        query_embedding = self.generate_mock_embedding(query_text)
        
        # Calculate similarity with all tasks
        similarities = []
        for task_id, embedding in self.embeddings.items():
            sim = self.cosine_similarity(query_embedding, embedding)
            similarities.append((task_id, sim))
        
        # Sort by similarity
        similarities.sort(key=lambda x: -x[1])
        
        return similarities[:top_k]
    
    def query(self, text, top_k=3):
        """Query similar tasks by text."""
        print(f"\n🔍 Query: {text[:100]}...")
        
        similar = self.find_similar_tasks(text, top_k)
        
        print(f"\n📋 Top {len(similar)} Similar Tasks:")
        for task_id, score in similar:
            print(f"   Task {task_id}: similarity={score:.4f}")
        
        return similar
    
    def status(self):
        """Show embedding status."""
        print("📊 Task Embedding Engine Status")
        print("=" * 50)
        print(f"Total embeddings: {len(self.embeddings)}")
        print(f"Dimension: {EMBEDDING_DIM}")
        
        if EMBEDDINGS_FILE.exists():
            with open(EMBEDDINGS_FILE, 'r') as f:
                data = json.load(f)
            print(f"Generated at: {data.get('generated_at', 'unknown')}")


def main():
    engine = TaskEmbeddingEngine()
    
    if '--status' in sys.argv:
        engine.status()
        return
    
    query_text = None
    if '--query' in sys.argv:
        idx = sys.argv.index('--query')
        if idx + 1 < len(sys.argv):
            query_text = sys.argv[idx + 1]
    
    if query_text:
        engine.query(query_text)
    else:
        engine.embed_all_tasks()


if __name__ == '__main__':
    main()
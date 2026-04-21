#!/usr/bin/env python3
"""
task_similarity_index.py — Phase 2: Task Similarity Index
===========================================================
Indexiert Tasks nach Embedding-Similarity für schnelle Lookups.

Usage:
    python3 task_similarity_index.py                 # Build index
    python3 task_similarity_index.py --status       # Show index status
    python3 task_similarity_index.py --similar <id> # Find similar to task
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
EMBEDDINGS_FILE = WORKSPACE / 'memory/meta_learning/task_embeddings.json'
TASK_LOG = WORKSPACE / 'memory/task_log/unified_tasks.json'
INDEX_FILE = WORKSPACE / 'memory/meta_learning/task_similarity_index.json'


class TaskSimilarityIndex:
    """Index for fast task similarity lookups."""
    
    def __init__(self):
        self.embeddings = {}
        self.tasks = {}
        self.index = {}  # task_id -> [(similar_id, score), ...]
        self.load_data()
    
    def load_data(self):
        """Load embeddings and tasks."""
        # Load embeddings
        if EMBEDDINGS_FILE.exists():
            with open(EMBEDDINGS_FILE, 'r') as f:
                data = json.load(f)
            self.embeddings = data.get('embeddings', {})
        
        # Load task details
        if TASK_LOG.exists():
            with open(TASK_LOG, 'r') as f:
                data = json.load(f)
            for t in data.get('tasks', []):
                self.tasks[str(t.get('task_id'))] = t
        
        print(f"📂 Loaded {len(self.embeddings)} embeddings, {len(self.tasks)} tasks")
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude = lambda v: sum(x * x for x in v) ** 0.5
        
        mag1 = magnitude(vec1)
        mag2 = magnitude(vec2)
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def build_index(self, top_k=5):
        """Build similarity index for all tasks."""
        print("🔍 Building Task Similarity Index")
        print("=" * 50)
        
        task_ids = list(self.embeddings.keys())
        total = len(task_ids)
        
        self.index = {}
        
        for i, task_id in enumerate(task_ids):
            if i % 20 == 0:
                print(f"   Processing {i}/{total}...")
            
            embedding = self.embeddings[task_id]
            similarities = []
            
            for other_id, other_embedding in self.embeddings.items():
                if other_id == task_id:
                    continue
                
                sim = self.cosine_similarity(embedding, other_embedding)
                similarities.append((other_id, sim))
            
            # Sort and keep top_k
            similarities.sort(key=lambda x: -x[1])
            self.index[task_id] = similarities[:top_k]
        
        self.save_index()
        
        print(f"\n✅ Index built for {len(self.index)} tasks")
        print(f"   Each task indexed with top {top_k} similar tasks")
        
        return self.index
    
    def save_index(self):
        """Save index to file."""
        data = {
            'index': self.index,
            'generated_at': datetime.now().isoformat(),
            'total_tasks': len(self.index)
        }
        with open(INDEX_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved index to {INDEX_FILE}")
    
    def load_index(self):
        """Load existing index."""
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r') as f:
                data = json.load(f)
            self.index = data.get('index', {})
            print(f"📂 Loaded index for {len(self.index)} tasks")
            return True
        return False
    
    def find_similar(self, task_id, top_k=3):
        """Find similar tasks to the given task_id."""
        if not self.index:
            self.load_index()
        
        if str(task_id) not in self.index:
            # Try to find in embeddings
            if task_id in self.embeddings:
                # Calculate on the fly
                embedding = self.embeddings[task_id]
                similarities = []
                for other_id, other_embedding in self.embeddings.items():
                    if other_id == task_id:
                        continue
                    sim = self.cosine_similarity(embedding, other_embedding)
                    similarities.append((other_id, sim))
                similarities.sort(key=lambda x: -x[1])
                return similarities[:top_k]
            return []
        
        return self.index[str(task_id)][:top_k]
    
    def get_similar_tasks(self, task_id, top_k=3):
        """Get similar tasks with full details."""
        similar = self.find_similar(task_id, top_k)
        
        results = []
        for similar_id, score in similar:
            task_info = {
                'task_id': similar_id,
                'similarity_score': score,
                'task_details': self.tasks.get(similar_id, {})
            }
            results.append(task_info)
        
        return results
    
    def query(self, task_id):
        """Query similar tasks for a given task_id."""
        print(f"\n🔍 Finding tasks similar to Task {task_id}")
        
        similar = self.find_similar(task_id)
        
        if not similar:
            print(f"❌ No similar tasks found for {task_id}")
            return []
        
        print(f"\n📋 Top Similar Tasks:")
        for similar_id, score in similar:
            task = self.tasks.get(similar_id, {})
            details = task.get('details', 'N/A')[:50]
            print(f"   Task {similar_id}: score={score:.4f} | {details}...")
        
        return similar
    
    def status(self):
        """Show index status."""
        print("📊 Task Similarity Index Status")
        print("=" * 50)
        print(f"Indexed tasks: {len(self.index)}")
        print(f"Embeddings loaded: {len(self.embeddings)}")
        
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r') as f:
                data = json.load(f)
            print(f"Index generated: {data.get('generated_at', 'unknown')}")


def main():
    index = TaskSimilarityIndex()
    
    if '--status' in sys.argv:
        index.status()
        return
    
    similar_id = None
    if '--similar' in sys.argv:
        idx = sys.argv.index('--similar')
        if idx + 1 < len(sys.argv):
            similar_id = sys.argv[idx + 1]
    
    if similar_id:
        index.query(similar_id)
    else:
        if not index.index:
            index.load_index()
        if not index.index:
            if not index.embeddings:
                print("❌ No embeddings found. Run task_embedding_engine.py first.")
            else:
                index.build_index()


if __name__ == '__main__':
    main()
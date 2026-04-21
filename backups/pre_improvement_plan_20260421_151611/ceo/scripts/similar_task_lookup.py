#!/usr/bin/env python3
"""
similar_task_lookup.py — Phase 2: Similar Task Lookup
======================================================
Findet ähnliche vergangene Tasks und gibt deren Erfolgs-Approach zurück.
Nutzt den Task Similarity Index für schnelle Lookups.

Usage:
    python3 similar_task_lookup.py --task <description>     # Find similar by description
    python3 similar_task_lookup.py --id <task_id>          # Find similar to task_id
    python3 similar_task_lookup.py --classify <desc>        # Classify new task type
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
TASK_LOG = WORKSPACE / 'memory/task_log/unified_tasks.json'
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'
SIMILARITY_INDEX = WORKSPACE / 'memory/meta_learning/task_similarity_index.json'
TASK_FEATURES = WORKSPACE / 'memory/meta_learning/task_features.json'


class SimilarTaskLookup:
    """Fast lookup for similar past tasks."""
    
    def __init__(self):
        self.tasks = {}
        self.patterns = []
        self.features = []
        self.similarity_index = {}
        self.load_data()
    
    def load_data(self):
        """Load all required data."""
        # Load tasks
        if TASK_LOG.exists():
            with open(TASK_LOG, 'r') as f:
                data = json.load(f)
            self.tasks = {str(t.get('task_id')): t for t in data.get('tasks', [])}
        
        # Load patterns
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
            self.patterns = data.get('patterns', [])
        
        # Load features
        if TASK_FEATURES.exists():
            with open(TASK_FEATURES, 'r') as f:
                data = json.load(f)
            self.features = data.get('task_features', [])
        
        # Load similarity index
        if SIMILARITY_INDEX.exists():
            with open(SIMILARITY_INDEX, 'r') as f:
                data = json.load(f)
            self.similarity_index = data.get('index', {})
        
        print(f"📂 Loaded: {len(self.tasks)} tasks, {len(self.patterns)} patterns")
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag = sum(x * x for x in vec) ** 0.5
        return dot_product / (sum(x*x for x in vec1)**0.5 * sum(x*x for x in vec2)**0.5 + 1e-10)
    
    def get_mock_embedding(self, text):
        """Generate mock embedding for text."""
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        emb = []
        for i in range(768):
            val = h[i % len(h)] / 255.0
            val = val * 0.6 + 0.2 + (h[(i+3) % 16] / 255.0) * 0.2
            emb.append(round(val, 4))
        return emb
    
    def find_similar_by_description(self, description, top_k=3):
        """Find tasks similar to a description text."""
        desc_embedding = self.get_mock_embedding(description)
        
        # Search through features for similar descriptions
        similarities = []
        for f in self.features:
            task_text = f.get('details', '') + ' ' + f.get('type', '') + ' ' + f.get('subtype', '')
            task_embedding = self.get_mock_embedding(task_text)
            sim = self.cosine_similarity(desc_embedding, task_embedding)
            similarities.append((f.get('task_id'), sim, f))
        
        similarities.sort(key=lambda x: -x[1])
        return similarities[:top_k]
    
    def find_similar_by_id(self, task_id, top_k=3):
        """Find tasks similar to a specific task_id."""
        # Use similarity index
        if str(task_id) in self.similarity_index:
            similar = self.similarity_index[str(task_id)][:top_k]
            results = []
            for sim_id, score in similar:
                task = self.tasks.get(sim_id, {})
                results.append({
                    'task_id': sim_id,
                    'score': score,
                    'details': task.get('details'),
                    'outcome': task.get('outcome'),
                    'type': task.get('type'),
                    'subtype': task.get('subtype')
                })
            return results
        
        # Fallback: search through features
        task = self.tasks.get(str(task_id), {})
        if not task:
            return []
        
        task_text = task.get('details', '') + ' ' + task.get('type', '')
        return self.find_similar_by_description(task_text, top_k)
    
    def get_success_approach(self, task_id):
        """Get the success approach for a task."""
        task = self.tasks.get(str(task_id), {})
        if not task:
            return None
        
        approach = {
            'task_id': task_id,
            'outcome': task.get('outcome'),
            'type': task.get('type'),
            'subtype': task.get('subtype'),
            'details': task.get('details'),
            'metadata': task.get('metadata', {}),
            'recommendations': []
        }
        
        # Find matching patterns
        for pattern in self.patterns:
            trigger = pattern.get('trigger', {})
            match = True
            
            for key, value in trigger.items():
                if key == 'subtype':
                    if task.get('subtype') != value:
                        match = False
                        break
                elif key == 'type':
                    if task.get('type') != value:
                        match = False
                        break
                elif key == 'delegated_to':
                    if task.get('metadata', {}).get('delegated_to') != value:
                        match = False
                        break
            
            if match:
                approach['recommendations'].append({
                    'pattern_id': pattern.get('pattern_id'),
                    'action': pattern.get('action'),
                    'description': pattern.get('description'),
                    'confidence': pattern.get('success_rate', 0)
                })
        
        return approach
    
    def classify_task(self, description):
        """Classify a new task and suggest approach."""
        similar = self.find_similar_by_description(description, top_k=5)
        
        if not similar:
            return {
                'classification': 'unknown',
                'confidence': 0,
                'suggested_approach': 'direct_execution'
            }
        
        # Aggregate similar task types
        subtypes = {}
        for task_id, score, feature in similar:
            subtype = feature.get('subtype', 'unknown')
            subtypes[subtype] = subtypes.get(subtype, 0) + score
        
        # Find dominant subtype
        dominant = max(subtypes.items(), key=lambda x: x[1])
        
        # Find matching pattern
        pattern = None
        for p in self.patterns:
            if p.get('trigger', {}).get('subtype') == dominant[0]:
                pattern = p
                break
        
        classification = {
            'classification': dominant[0],
            'confidence': dominant[1] / sum(subtypes.values()),
            'suggested_approach': pattern.get('action', {}).get('approach', 'direct') if pattern else 'direct_execution',
            'similar_tasks': len(similar),
            'pattern_id': pattern.get('pattern_id') if pattern else None
        }
        
        return classification
    
    def lookup(self, query, by='description'):
        """Main lookup function."""
        if by == 'id':
            results = self.find_similar_by_id(query)
            print(f"\n🔍 Similar tasks to Task {query}:")
        else:
            results = self.find_similar_by_description(query)
            print(f"\n🔍 Tasks similar to '{query[:50]}...':")
        
        if not results:
            print("   No similar tasks found.")
            return []
        
        for r in results:
            if by == 'id':
                print(f"   Task {r['task_id']}: score={r['score']:.3f}")
                print(f"      type={r['type']}, subtype={r['subtype']}")
                print(f"      outcome={r['outcome']}")
            else:
                tid, score, feat = r
                print(f"   Task {tid}: score={score:.3f}")
                print(f"      type={feat.get('type')}, subtype={feat.get('subtype')}")
        
        return results
    
    def status(self):
        """Show status."""
        print("📊 Similar Task Lookup Status")
        print("=" * 50)
        print(f"Tasks loaded: {len(self.tasks)}")
        print(f"Patterns loaded: {len(self.patterns)}")
        print(f"Features loaded: {len(self.features)}")
        print(f"Similarity index entries: {len(self.similarity_index)}")


def main():
    lookup = SimilarTaskLookup()
    
    if '--status' in sys.argv:
        lookup.status()
        return
    
    task_desc = None
    task_id = None
    classify_text = None
    
    if '--task' in sys.argv:
        idx = sys.argv.index('--task')
        if idx + 1 < len(sys.argv):
            task_desc = sys.argv[idx + 1]
    
    if '--id' in sys.argv:
        idx = sys.argv.index('--id')
        if idx + 1 < len(sys.argv):
            task_id = sys.argv[idx + 1]
    
    if '--classify' in sys.argv:
        idx = sys.argv.index('--classify')
        if idx + 1 < len(sys.argv):
            classify_text = sys.argv[idx + 1]
    
    if task_id:
        result = lookup.find_similar_by_id(task_id)
        approach = lookup.get_success_approach(task_id)
        print(f"\n📋 Similar tasks and approach for Task {task_id}:")
        for r in result:
            print(f"   Task {r['task_id']}: {r.get('outcome')} ({r.get('type')})")
        if approach and approach.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in approach['recommendations'][:3]:
                print(f"   [{rec['pattern_id']}] {rec['description']}")
    elif classify_text:
        classification = lookup.classify_task(classify_text)
        print(f"\n📊 Task Classification:")
        print(f"   Type: {classification['classification']}")
        print(f"   Confidence: {classification['confidence']:.1%}")
        print(f"   Suggested Approach: {classification['suggested_approach']}")
        print(f"   Similar Tasks: {classification['similar_tasks']}")
    elif task_desc:
        lookup.lookup(task_desc, by='description')
    else:
        lookup.status()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
kg_meta_learner.py — Phase 4: KG als Meta-Learner
==================================================
Nutzt KG-Embedding-Space für Meta-Learning.
Findet ähnliche Tasks durch KG-Traversal.

Usage:
    python3 kg_meta_learner.py                    # Run meta-learning via KG
    python3 kg_meta_learner.py --query <task>    # Query KG for task advice
    python3 kg_meta_learner.py --status          # Show KG meta state
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
KG_DIR = WORKSPACE / 'memory/kg'
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'


class KGMetaLearner:
    """Uses KG as a meta-learning engine."""
    
    def __init__(self):
        self.kg_entities = []
        self.kg_relations = []
        self.patterns = []
        self._entities_format = 'list'  # Track original format
        self._relations_raw = None  # Store raw relations to preserve format
        self.load_kg()
    
    def load_kg(self):
        """Load KG data."""
        # Load main KG
        kg_file = KG_DIR / 'knowledge_graph.json'
        if kg_file.exists():
            with open(kg_file, 'r') as f:
                data = json.load(f)
            
            # Track original format
            entities_data = data.get('entities', {})
            self._entities_format = 'dict' if isinstance(entities_data, dict) else 'list'
            self._relations_raw = data.get('relations', data.get('relationships', []))
            
            # Entities can be dict or list - normalize to list for processing
            if isinstance(entities_data, dict):
                self.kg_entities = []
                for entity_id, entity in entities_data.items():
                    if isinstance(entity, dict):
                        entity['id'] = entity.get('id', entity_id)
                        self.kg_entities.append(entity)
            else:
                self.kg_entities = entities_data if isinstance(entities_data, list) else []
            
            # Relations can be dict or list - normalize to list for processing
            relations_data = data.get('relations', data.get('relationships', {}))
            if isinstance(relations_data, dict):
                self.kg_relations = []
                for rel_id, rel_obj in relations_data.items():
                    if isinstance(rel_obj, dict):
                        self.kg_relations.append(rel_obj)
                    elif isinstance(rel_obj, list):
                        for target in rel_obj:
                            self.kg_relations.append({'source': str(rel_id), 'target': target, 'type': 'related'})
            else:
                self.kg_relations = relations_data if isinstance(relations_data, list) else []
        
        # Load meta patterns
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
            self.patterns = data.get('patterns', [])
        
        print(f"📂 KG loaded: {len(self.kg_entities)} entities, {len(self.kg_relations)} relations")
        print(f"📂 Meta patterns: {len(self.patterns)}")
    
    def find_similar_via_kg(self, task_type, subtype=None, context=None):
        """Find similar tasks via KG traversal."""
        print(f"\n🔍 KG Meta-Learning Query")
        print(f"   Task type: {task_type}")
        if subtype:
            print(f"   Subtype: {subtype}")
        if context:
            print(f"   Context: {context[:50]}...")
        
        # Find matching entities
        similar_entities = []
        
        # 1. Find entities of same type
        type_matches = [e for e in self.kg_entities if e.get('type') == task_type]
        
        # 2. Find meta_pattern entities
        pattern_matches = [e for e in self.kg_entities if e.get('type') == 'meta_pattern']
        
        # 3. Find learning entities
        learning_matches = [e for e in self.kg_entities if 'learning' in e.get('type', '').lower()]
        
        # Combine results
        all_matches = type_matches + pattern_matches + learning_matches
        
        print(f"\n📋 Found {len(all_matches)} relevant KG entities:")
        
        results = []
        for e in all_matches[:10]:
            results.append({
                'id': e.get('id'),
                'type': e.get('type'),
                'name': e.get('name', '')[:50],
                'properties': e.get('properties', {})
            })
            print(f"   - {e.get('id')} ({e.get('type')})")
            print(f"     {e.get('name', '')[:60]}")
        
        return results
    
    def extract_meta_relations(self):
        """Extract meta-relations from KG for meta-learning."""
        print("\n🔗 Extracting Meta-Relations from KG")
        print("=" * 50)
        
        meta_relations = []
        
        # Find relations between pattern entities
        for rel in self.kg_relations:
            rel_type = rel.get('type', '')
            source = rel.get('source', '')
            target = rel.get('target', '')
            
            # Look for meta-learning relevant relations
            if any(x in rel_type.lower() for x in ['similar', 'learns', 'improves', 'derived']):
                meta_relations.append(rel)
        
        print(f"   Found {len(meta_relations)} meta-relations")
        
        for r in meta_relations[:5]:
            print(f"   - {r.get('source')} → {r.get('type')} → {r.get('target')}")
        
        return meta_relations
    
    def generate_meta_insights(self):
        """Generate meta-insights from KG structure."""
        print("\n💡 Generating Meta-Insights from KG")
        print("=" * 50)
        
        insights = []
        
        # Analyze entity types
        type_counts = {}
        for e in self.kg_entities:
            t = e.get('type', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        insights.append({
            'type': 'entity_distribution',
            'finding': f"KG has {len(self.kg_entities)} entities across {len(type_counts)} types",
            'data': sorted(type_counts.items(), key=lambda x: -x[1])[:5]
        })
        
        # Analyze pattern coverage
        if self.patterns:
            pattern_entities = [e for e in self.kg_entities if e.get('type') == 'meta_pattern']
            insights.append({
                'type': 'pattern_coverage',
                'finding': f"Patterns cover {len(pattern_entities)} KG entities",
                'data': len(pattern_entities)
            })
        
        # Find highly connected entities (hubs)
        connection_counts = {}
        for rel in self.kg_relations:
            source = rel.get('source', '')
            target = rel.get('target', '')
            connection_counts[source] = connection_counts.get(source, 0) + 1
            connection_counts[target] = connection_counts.get(target, 0) + 1
        
        top_hubs = sorted(connection_counts.items(), key=lambda x: -x[1])[:5]
        if top_hubs:
            insights.append({
                'type': 'hub_entities',
                'finding': f"Top KG hubs: {top_hubs[0][0]} ({top_hubs[0][1]} connections)",
                'data': top_hubs
            })
        
        for insight in insights:
            print(f"\n📊 {insight['type']}:")
            print(f"   {insight['finding']}")
        
        return insights
    
    def sync_patterns_to_kg(self):
        """Sync meta_patterns to KG as entities."""
        print("\n🔄 Syncing Patterns to KG")
        print("=" * 50)
        
        # Load existing meta patterns KG entities
        meta_patterns_kg = KG_DIR / 'meta_patterns_entities.json'
        
        synced = 0
        for pattern in self.patterns:
            pattern_id = pattern.get('pattern_id')
            
            # Check if entity exists
            existing = [e for e in self.kg_entities if e.get('id') == pattern_id]
            
            if not existing:
                # Create new entity
                new_entity = {
                    'id': pattern_id,
                    'type': 'meta_pattern',
                    'name': pattern.get('description', '')[:50],
                    'properties': {
                        'trigger': json.dumps(pattern.get('trigger', {})),
                        'action': json.dumps(pattern.get('action', {})),
                        'success_rate': pattern.get('success_rate', 1.0),
                        'generalization_score': pattern.get('generalization_score', 0),
                        'cross_task_valid': pattern.get('cross_task_valid', False),
                        'synced_at': datetime.now().isoformat()
                    },
                    'relations': []
                }
                
                # Add relations based on trigger
                trigger = pattern.get('trigger', {})
                if 'delegated_to' in trigger:
                    agent = trigger['delegated_to']
                    if agent:
                        new_entity['relations'].append({
                            'type': 'optimized_by',
                            'target': f'agent:{agent}'
                        })
                
                if pattern.get('cross_task_valid', False):
                    new_entity['relations'].append({
                        'type': 'applies_to',
                        'target': 'cross_task_domain'
                    })
                
                self.kg_entities.append(new_entity)
                synced += 1
        
        # Save updated KG preserving format
        kg_file = KG_DIR / 'knowledge_graph.json'
        
        # Preserve original entity format
        if self._entities_format == 'dict':
            entities_dict = {}
            for entity in self.kg_entities:
                entity_id = entity.get('id')
                if entity_id:
                    entities_dict[entity_id] = entity
            entities_output = entities_dict
        else:
            entities_output = self.kg_entities
        
        # Preserve original relations format
        if self._relations_raw is not None:
            relations_output = self._relations_raw
        else:
            relations_output = self.kg_relations
        
        with open(kg_file, 'w') as f:
            json.dump({
                'entities': entities_output,
                'relations': relations_output,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2, default=str)
        
        print(f"   Synced {synced} patterns to KG")
        print(f"   Total KG entities: {len(self.kg_entities)} (format: {self._entities_format})")
        
        return synced
    
    def run_meta_learning(self):
        """Run full KG-based meta-learning."""
        print("🧠 KG Meta-Learner — Phase 4")
        print("=" * 50)
        
        # Extract meta relations
        meta_relations = self.extract_meta_relations()
        
        # Generate insights
        insights = self.generate_meta_insights()
        
        # Sync patterns
        synced = self.sync_patterns_to_kg()
        
        print(f"\n✅ KG Meta-Learning Complete")
        print(f"   Meta-relations: {len(meta_relations)}")
        print(f"   Insights: {len(insights)}")
        print(f"   Patterns synced: {synced}")
        
        return {
            'meta_relations': len(meta_relations),
            'insights': insights,
            'synced': synced
        }
    
    def query(self, task_description):
        """Query KG for task advice."""
        print(f"\n🔍 KG Query: {task_description[:50]}...")
        
        # Find relevant entities
        results = self.find_similar_via_kg(
            task_type='subagent_task',
            context=task_description
        )
        
        if results:
            print(f"\n💡 KG recommends based on {len(results)} similar entities:")
            for r in results[:3]:
                print(f"   - {r.get('name', r.get('id'))}")
        
        return results
    
    def status(self):
        """Show KG meta-learner status."""
        print("🧠 KG Meta-Learner Status")
        print("=" * 50)
        print(f"KG Entities: {len(self.kg_entities)}")
        print(f"KG Relations: {len(self.kg_relations)}")
        print(f"Meta Patterns: {len(self.patterns)}")


def main():
    learner = KGMetaLearner()
    
    if '--status' in sys.argv:
        learner.status()
        return
    
    query_text = None
    if '--query' in sys.argv:
        idx = sys.argv.index('--query')
        if idx + 1 < len(sys.argv):
            query_text = sys.argv[idx + 1]
    
    if query_text:
        learner.query(query_text)
    else:
        learner.run_meta_learning()


if __name__ == '__main__':
    main()
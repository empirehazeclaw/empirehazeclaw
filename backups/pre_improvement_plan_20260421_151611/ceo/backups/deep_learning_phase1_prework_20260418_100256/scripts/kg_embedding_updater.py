#!/usr/bin/env python3
"""
kg_embedding_updater.py — Phase 4: KG Embedding Updater
========================================================
Fügt Meta-Information zu KG-Entities hinzu.

Usage:
    python3 kg_embedding_updater.py              # Update all embeddings
    python3 kg_embedding_updater.py --entity <id> # Update specific entity
    python3 kg_embedding_updater.py --status      # Show update status
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
KG_DIR = WORKSPACE / 'memory/kg'
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'


class KGEmbeddingUpdater:
    """Updates KG with meta-learning information."""
    
    def __init__(self):
        self.kg_entities = []
        self.kg_relations = []
        self.patterns = []
        self._entities_format = 'list'  # Track original format
        self._kg_raw = None  # Store raw KG for format preservation
        self._relations_raw = None  # Store raw relations to preserve on save
        self.load_kg()
    
    def load_kg(self):
        """Load KG data."""
        kg_file = KG_DIR / 'knowledge_graph.json'
        if kg_file.exists():
            with open(kg_file, 'r') as f:
                data = json.load(f)
            
            # Store raw KG to preserve original structure
            self._kg_raw = data
            
            # Track original format
            entities_data = data.get('entities', {})
            self._entities_format = 'dict' if isinstance(entities_data, dict) else 'list'
            
            # Entities can be dict or list - normalize to list for processing
            if isinstance(entities_data, dict):
                self.kg_entities = []
                for entity_id, entity in entities_data.items():
                    if isinstance(entity, dict):
                        entity['id'] = entity.get('id', entity_id)
                        self.kg_entities.append(entity)
            else:
                self.kg_entities = entities_data if isinstance(entities_data, list) else []
            
            # Store raw relations to preserve original format
            self._relations_raw = data.get('relations', data.get('relationships', []))
            
            # Parse relations for internal use (list format with from/to/source/target)
            relations_data = data.get('relations', data.get('relationships', {}))
            if isinstance(relations_data, dict):
                self.kg_relations = []
                for rel_id, rel_obj in relations_data.items():
                    if isinstance(rel_obj, dict):
                        # Format: {id: {from, to, type, ...}}
                        self.kg_relations.append(rel_obj)
                    elif isinstance(rel_obj, list):
                        # Format: {source: [targets]}
                        for target in rel_obj:
                            self.kg_relations.append({'source': str(rel_id), 'target': target, 'type': 'related'})
            else:
                self.kg_relations = relations_data if isinstance(relations_data, list) else []
        else:
            self.kg_relations = []
            self._kg_raw = {'entities': {}, 'relations': []}
            self._relations_raw = []
        
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
            self.patterns = data.get('patterns', [])
        
        print(f"📂 KG: {len(self.kg_entities)} entities, {len(self.kg_relations)} relations")
    
    def save_kg(self):
        """Save updated KG preserving original format."""
        kg_file = KG_DIR / 'knowledge_graph.json'
        
        # SAFETY: Verify loaded format matches expected format
        with open(kg_file) as f:
            current = json.load(f)
        current_entities_format = 'dict' if isinstance(current.get('entities'), dict) else 'list'
        if current_entities_format != self._entities_format:
            print(f"⚠️ FORMAT MISMATCH! Expected {self._entities_format} but found {current_entities_format}. Restoring from backup.")
            # Restore from backup
            bak_file = KG_DIR / 'knowledge_graph.json.bak'
            if bak_file.exists():
                import shutil
                shutil.copy(bak_file, kg_file)
                print("💾 Restored from backup")
            return
        
        # Preserve original entity format (dict vs list)
        if self._entities_format == 'dict':
            # Convert list back to dict {entity_id: entity}
            entities_dict = {}
            for entity in self.kg_entities:
                entity_id = entity.get('id')
                if entity_id:
                    entities_dict[entity_id] = entity
            entities_output = entities_dict
        else:
            entities_output = self.kg_entities
        
        # Preserve original relations format - use raw if available
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
        print(f"💾 Saved KG with {len(self.kg_entities)} entities (format: {self._entities_format})")
    
    def update_entity_embeddings(self):
        """Update entity embeddings with meta-learning info."""
        print("\n🔄 Updating Entity Embeddings")
        print("=" * 50)
        
        updates = 0
        
        for entity in self.kg_entities:
            entity_id = entity.get('id')
            
            # Check if this entity matches a pattern
            matching_patterns = []
            for pattern in self.patterns:
                trigger = pattern.get('trigger', {})
                
                # Simple matching based on trigger keys
                if 'delegated_to' in trigger:
                    agent = trigger['delegated_to']
                    if agent and (agent in entity_id or agent in str(entity.get('properties', {}))):
                        matching_patterns.append(pattern.get('pattern_id'))
                
                if 'subtype' in trigger:
                    subtype = trigger['subtype']
                    if subtype in str(entity.get('properties', {})):
                        matching_patterns.append(pattern.get('pattern_id'))
            
            # Add meta-learning properties
            if matching_patterns:
                props = entity.get('properties', {})
                props['meta_patterns'] = matching_patterns
                props['pattern_count'] = len(matching_patterns)
                props['meta_learned'] = True
                props['updated_at'] = datetime.now().isoformat()
                entity['properties'] = props
                updates += 1
        
        print(f"   Updated {updates} entities with meta-learning info")
        
        return updates
    
    def add_meta_learning_relations(self):
        """Add meta-learning relations between entities."""
        print("\n🔗 Adding Meta-Learning Relations")
        print("=" * 50)
        
        new_relations = []
        
        # Find pattern entities and connect them
        pattern_entities = [e for e in self.kg_entities if e.get('type') == 'meta_pattern']
        
        # Connect patterns to relevant task entities
        for pattern in self.patterns:
            pattern_id = pattern.get('pattern_id')
            
            # Find entities that match this pattern's trigger
            trigger = pattern.get('trigger', {})
            
            if 'delegated_to' in trigger:
                agent = trigger['delegated_to']
                # Find entities related to this agent
                agent_entity_id = f"agent:{agent}"
                
                # Add relation: pattern improves agent
                new_relations.append({
                    'type': 'improves',
                    'source': pattern_id,
                    'target': agent_entity_id
                })
            
            if 'subtype' in trigger:
                subtype = trigger['subtype']
                # Add relation: pattern applies_to subtype
                new_relations.append({
                    'type': 'applies_to',
                    'source': pattern_id,
                    'target': f"subtype:{subtype}"
                })
        
        # Add cross-task relations
        for pattern in self.patterns:
            if pattern.get('cross_task_valid', False):
                pattern_id = pattern.get('pattern_id')
                new_relations.append({
                    'type': 'cross_task_valid',
                    'source': pattern_id,
                    'target': 'cross_task_domain'
                })
        
        # Add to existing relations
        existing_sources = set((r.get('source'), r.get('type')) for r in self.kg_relations)
        for rel in new_relations:
            if (rel.get('source'), rel.get('type')) not in existing_sources:
                self.kg_relations.append(rel)
        
        print(f"   Added {len(new_relations)} meta-learning relations")
        print(f"   Total relations: {len(self.kg_relations)}")
        
        return len(new_relations)
    
    def update_learning_entities(self):
        """Update learning entities with performance info."""
        print("\n📊 Updating Learning Entities")
        print("=" * 50)
        
        # Find learning-type entities
        learning_entities = [e for e in self.kg_entities if 'learning' in e.get('type', '').lower()]
        
        updates = 0
        for entity in learning_entities:
            props = entity.get('properties', {})
            
            # Add performance metrics if available
            if 'pattern_id' in entity.get('id', ''):
                # Find corresponding pattern
                for pattern in self.patterns:
                    if pattern.get('pattern_id') == entity.get('id'):
                        props['success_rate'] = pattern.get('success_rate', 1.0)
                        props['generalization_score'] = pattern.get('generalization_score', 0)
                        props['matching_tasks'] = pattern.get('matching_tasks', 0)
                        updates += 1
                        break
            
            # Add last accessed time
            props['last_meta_update'] = datetime.now().isoformat()
            entity['properties'] = props
        
        print(f"   Updated {updates} learning entities")
        
        return updates
    
    def run_update(self):
        """Run full embedding update."""
        print("🔄 KG Embedding Updater — Phase 4")
        print("=" * 50)
        
        # Update entity embeddings
        entity_updates = self.update_entity_embeddings()
        
        # Add meta-learning relations
        relation_updates = self.add_meta_learning_relations()
        
        # Update learning entities
        learning_updates = self.update_learning_entities()
        
        # Save updated KG
        self.save_kg()
        
        print(f"\n✅ KG Update Complete")
        print(f"   Entity updates: {entity_updates}")
        print(f"   Relation additions: {relation_updates}")
        print(f"   Learning entity updates: {learning_updates}")
        
        return {
            'entity_updates': entity_updates,
            'relation_updates': relation_updates,
            'learning_updates': learning_updates
        }
    
    def status(self):
        """Show updater status."""
        print("📊 KG Embedding Updater Status")
        print("=" * 50)
        print(f"KG Entities: {len(self.kg_entities)}")
        print(f"KG Relations: {len(self.kg_relations)}")
        print(f"Patterns: {len(self.patterns)}")


def main():
    updater = KGEmbeddingUpdater()
    
    if '--status' in sys.argv:
        updater.status()
    else:
        updater.run_update()


if __name__ == '__main__':
    main()
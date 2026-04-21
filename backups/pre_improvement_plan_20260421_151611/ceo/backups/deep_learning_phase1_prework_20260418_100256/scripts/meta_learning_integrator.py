#!/usr/bin/env python3
"""
meta_learning_integrator.py — Phase 1a: Pattern Integration into Learning Loop
================================================================================
Takes discovered meta_patterns and integrates them into the Learning Loop.

Usage:
    python3 meta_learning_integrator.py              # Full integration
    python3 meta_learning_integrator.py --status    # Show current state
    python3 meta_learning_integrator.py --validate   # Validate pattern quality
"""

import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
META_LEARNING_DIR = WORKSPACE / 'memory/meta_learning'
PATTERNS_FILE = META_LEARNING_DIR / 'meta_patterns.json'
LEARNING_SIGNAL = WORKSPACE / 'memory/evaluations/learning_loop_signal.json'
KG_DIR = WORKSPACE / 'memory/kg'

# Ensure directories exist
META_LEARNING_DIR.mkdir(parents=True, exist_ok=True)


class MetaLearningIntegrator:
    """Integrates meta_patterns into the Learning Loop."""
    
    def __init__(self):
        self.patterns = []
        self.signal = {}
        
    def load_patterns(self):
        """Load meta patterns from file."""
        if not PATTERNS_FILE.exists():
            print(f"❌ No patterns found at {PATTERNS_FILE}")
            return []
        
        with open(PATTERNS_FILE, 'r') as f:
            data = json.load(f)
        self.patterns = data.get('patterns', [])
        print(f"📂 Loaded {len(self.patterns)} patterns")
        return self.patterns
    
    def load_learning_signal(self):
        """Load current learning signal."""
        if LEARNING_SIGNAL.exists():
            with open(LEARNING_SIGNAL, 'r') as f:
                self.signal = json.load(f)
        else:
            self.signal = {
                'timestamp': datetime.now().isoformat(),
                'source': 'meta_learning_integrator',
                'metrics': {},
                'learnings': []
            }
    
    def analyze_patterns(self):
        """Analyze patterns and generate insights."""
        if not self.patterns:
            return None
        
        analysis = {
            'total_patterns': len(self.patterns),
            'cross_task_patterns': sum(1 for p in self.patterns if p.get('cross_task_valid', False)),
            'high_confidence_patterns': sum(1 for p in self.patterns if p.get('success_rate', 0) >= 1.0),
            'coverage': sum(p.get('matching_tasks', 0) for p in self.patterns),
            'best_pattern': None,
            'patterns_by_type': {}
        }
        
        # Find best pattern
        best = max(self.patterns, key=lambda p: p.get('generalization_score', 0))
        analysis['best_pattern'] = {
            'id': best.get('pattern_id'),
            'description': best.get('description'),
            'generalization': best.get('generalization_score', 0)
        }
        
        # Group by trigger type
        for p in self.patterns:
            trigger_keys = list(p.get('trigger', {}).keys())
            key = trigger_keys[0] if trigger_keys else 'unknown'
            if key not in analysis['patterns_by_type']:
                analysis['patterns_by_type'][key] = []
            analysis['patterns_by_type'][key].append(p.get('pattern_id'))
        
        return analysis
    
    def create_meta_learning_signal(self):
        """Create learning signal from meta patterns."""
        analysis = self.analyze_patterns()
        
        # Load current signal
        self.load_learning_signal()
        
        # Build meta-learning section
        meta_learning = {
            'meta_patterns_discovered': len(self.patterns),
            'cross_task_patterns': analysis.get('cross_task_patterns', 0),
            'best_pattern': analysis.get('best_pattern'),
            'timestamp': datetime.now().isoformat(),
            'patterns': []
        }
        
        # Add top patterns (limit to 5 most valuable)
        sorted_patterns = sorted(
            self.patterns, 
            key=lambda p: (p.get('cross_task_valid', False), p.get('generalization_score', 0)),
            reverse=True
        )
        
        for p in sorted_patterns[:5]:
            meta_learning['patterns'].append({
                'pattern_id': p.get('pattern_id'),
                'trigger': p.get('trigger'),
                'action': p.get('action'),
                'description': p.get('description'),
                'success_rate': p.get('success_rate', 0),
                'generalization': p.get('generalization_score', 0),
                'cross_task': p.get('cross_task_valid', False),
                'matching_tasks': p.get('matching_tasks', 0)
            })
        
        # Generate learnings from patterns
        learnings = []
        
        # Pattern-based learnings
        for p in sorted_patterns[:3]:
            if p.get('cross_task_valid', False) and p.get('success_rate', 0) >= 1.0:
                learnings.append({
                    'type': 'meta_pattern',
                    'priority': 'HIGH',
                    'pattern_id': p.get('pattern_id'),
                    'observation': p.get('description'),
                    'action': f"Use trigger {p.get('trigger')} for similar tasks",
                    'confidence': p.get('generalization_score', 0)
                })
        
        # Update signal
        self.signal['meta_learning'] = meta_learning
        self.signal['meta_learning_timestamp'] = datetime.now().isoformat()
        
        # Add to learnings
        self.signal['learnings'] = self.signal.get('learnings', []) + learnings
        
        return meta_learning, learnings
    
    def save_signal(self):
        """Save updated learning signal."""
        with open(LEARNING_SIGNAL, 'w') as f:
            json.dump(self.signal, f, indent=2, default=str)
        print(f"💾 Updated learning signal: {LEARNING_SIGNAL}")
    
    def create_kg_entities(self):
        """Create KG entities for meta patterns."""
        kg_dir = KG_DIR
        kg_dir.mkdir(parents=True, exist_ok=True)
        
        entities = []
        
        for p in self.patterns:
            entity = {
                'id': p.get('pattern_id'),
                'type': 'meta_pattern',
                'name': p.get('description', '')[:50],
                'properties': {
                    'trigger': json.dumps(p.get('trigger', {})),
                    'action': json.dumps(p.get('action', {})),
                    'success_rate': p.get('success_rate', 0),
                    'generalization_score': p.get('generalization_score', 0),
                    'cross_task_valid': p.get('cross_task_valid', False),
                    'matching_tasks': p.get('matching_tasks', 0),
                    'sample_task_ids': p.get('sample_task_ids', []),
                    'discovered_at': p.get('timestamp', datetime.now().isoformat())
                },
                'relations': []
            }
            
            # Add relations based on pattern type
            trigger = p.get('trigger', {})
            if 'delegated_to' in trigger:
                agent = trigger['delegated_to']
                if agent:
                    entity['relations'].append({
                        'type': 'improves',
                        'target': f'agent:{agent}'
                    })
            
            if p.get('cross_task_valid', False):
                entity['relations'].append({
                    'type': 'applies_to',
                    'target': 'cross_task'
                })
            
            entities.append(entity)
        
        # Save entity file
        entity_file = kg_dir / 'meta_patterns_entities.json'
        with open(entity_file, 'w') as f:
            json.dump({
                'entities': entities,
                'generated_at': datetime.now().isoformat(),
                'total': len(entities)
            }, f, indent=2)
        
        print(f"💾 Created {len(entities)} KG entities: {entity_file}")
        return entities
    
    def sync(self):
        """Run full integration."""
        print("🔄 Meta Learning Integrator — Phase 1a")
        print("=" * 50)
        
        # Load patterns
        self.load_patterns()
        
        if not self.patterns:
            print("❌ No patterns to integrate")
            return None
        
        # Analyze
        analysis = self.analyze_patterns()
        print(f"\n📊 Pattern Analysis:")
        print(f"   Total patterns: {analysis['total_patterns']}")
        print(f"   Cross-task patterns: {analysis['cross_task_patterns']}")
        print(f"   High-confidence patterns: {analysis['high_confidence_patterns']}")
        print(f"   Total coverage: {analysis['coverage']} tasks")
        
        if analysis.get('best_pattern'):
            bp = analysis['best_pattern']
            print(f"   Best pattern: {bp['id']} (gen={bp['generalization']:.2f})")
        
        # Create meta-learning signal
        meta_learning, learnings = self.create_meta_learning_signal()
        
        # Save signal
        self.save_signal()
        
        # Create KG entities
        self.create_kg_entities()
        
        # Print summary
        print(f"\n📋 Integration Summary:")
        print(f"   Patterns integrated: {len(meta_learning['patterns'])}")
        print(f"   New learnings created: {len(learnings)}")
        print(f"   KG entities created: {len(self.patterns)}")
        
        if learnings:
            print(f"\n💡 Top Learnings:")
            for l in learnings[:3]:
                print(f"   [{l['priority']}] {l['observation']}")
        
        return meta_learning
    
    def status(self):
        """Show current integration status."""
        print("📊 Meta Learning Status")
        print("=" * 50)
        
        if not PATTERNS_FILE.exists():
            print("❌ No patterns file found")
            return
        
        with open(PATTERNS_FILE, 'r') as f:
            data = json.load(f)
        
        patterns = data.get('patterns', [])
        print(f"Patterns: {len(patterns)}")
        
        # Load signal
        if LEARNING_SIGNAL.exists():
            with open(LEARNING_SIGNAL, 'r') as f:
                signal = json.load(f)
            
            if 'meta_learning' in signal:
                ml = signal['meta_learning']
                print(f"Last integration: {ml.get('timestamp', 'unknown')}")
                print(f"Patterns in signal: {len(ml.get('patterns', []))}")
            else:
                print("⚠️ No meta_learning in signal yet")
        
        # KG entities
        kg_file = KG_DIR / 'meta_patterns_entities.json'
        if kg_file.exists():
            with open(kg_file, 'r') as f:
                kg = json.load(f)
            print(f"KG entities: {kg.get('total', 0)}")
        else:
            print("KG entities: ❌ Not created yet")


def main():
    integrator = MetaLearningIntegrator()
    
    action = 'sync'
    args = [a for a in __import__('sys').argv[1:] if not a.startswith('--')]
    
    if '--status' in __import__('sys').argv:
        action = 'status'
    elif '--validate' in __import__('sys').argv:
        action = 'validate'
    
    if action == 'sync':
        integrator.sync()
    elif action == 'status':
        integrator.status()
    elif action == 'validate':
        integrator.load_patterns()
        print(f"📋 Validating {len(integrator.patterns)} patterns...")
        for p in integrator.patterns:
            gen = p.get('generalization_score', 0)
            ct = p.get('cross_task_valid', False)
            sr = p.get('success_rate', 0)
            status = '✅' if (gen > 0.3 or ct) and sr >= 1.0 else '⚠️'
            print(f"   {status} {p.get('pattern_id')}: gen={gen:.2f}, ct={ct}, sr={sr:.0%}")


if __name__ == '__main__':
    main()
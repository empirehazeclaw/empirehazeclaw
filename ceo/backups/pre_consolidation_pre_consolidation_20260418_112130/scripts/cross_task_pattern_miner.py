#!/usr/bin/env python3
"""
cross_task_pattern_miner.py — Phase 1: Cross-Task Pattern Mining
Findet通用 Patterns die über Task-Typen hinweg gelten.
Output: meta_patterns.json

Usage:
    python3 cross_task_pattern_miner.py                 # Full mining
    python3 cross_task_pattern_miner.py --status         # Show current patterns
    python3 cross_task_pattern_miner.py --validate      # Validate existing patterns
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import math

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent
TASK_LOG = WORKSPACE / "memory/task_log/unified_tasks.json"
TASK_FEATURES = WORKSPACE / "memory/meta_learning/task_features.json"
OUTPUT_FILE = WORKSPACE / "memory/meta_learning/meta_patterns.json"

# Ensure output dir exists
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Pattern quality thresholds
MIN_PATTERN_TASKS = 2
MIN_GENERALIZATION_SCORE = 0.1


class PatternMiner:
    """Mines cross-task patterns from task features."""
    
    def __init__(self):
        self.tasks = []
        self.patterns = []
        self.pattern_id_counter = 0
    
    def load_tasks(self):
        """Load tasks from unified task logger."""
        with open(TASK_LOG, 'r') as f:
            data = json.load(f)
        self.tasks = data.get('tasks', [])
        print(f"📂 Loaded {len(self.tasks)} tasks")
    
    def extract_context_features(self, task):
        """Extract contextual features for pattern detection."""
        metadata = task.get('metadata', {})
        details = str(task.get('details', '')).lower()
        
        features = {
            'task_id': task.get('task_id'),
            'type': task.get('type', 'unknown'),
            'subtype': task.get('subtype', task.get('type', 'unknown')),
            'outcome': task.get('outcome', 'unknown'),
            'duration_ms': metadata.get('duration_ms'),
            'delegated_to': metadata.get('delegated_to'),
            'priority': metadata.get('priority', 'MEDIUM'),
            'tool': metadata.get('tool'),
            'error': metadata.get('error'),
        }
        
        # Context type detection
        context_types = ['file_operation', 'api_call', 'data_processing', 
                        'decision_making', 'learning', 'orchestration', 
                        'monitoring', 'analysis', 'automation', 'delegation']
        features['context_type'] = 'unknown'
        for ctx in context_types:
            if ctx.replace('_', ' ') in details or ctx in details:
                features['context_type'] = ctx
                break
        
        # Approach detection
        if metadata.get('delegated_to'):
            features['approach'] = 'delegated'
            if 'health' in str(metadata.get('delegated_to', '')).lower():
                features['approach'] = 'delegated_health'
            elif 'research' in str(metadata.get('delegated_to', '')).lower():
                features['approach'] = 'delegated_research'
        elif 'retry' in details:
            features['approach'] = 'retry'
        elif 'fallback' in details or 'alternative' in details:
            features['approach'] = 'fallback'
        else:
            features['approach'] = 'direct'
        
        # Duration bucket
        dur = features.get('duration_ms', 0) or 0
        if dur < 60000:
            features['duration_bucket'] = 'fast'
        elif dur < 300000:
            features['duration_bucket'] = 'medium'
        else:
            features['duration_bucket'] = 'slow'
        
        # Success indicator
        features['success'] = task.get('outcome') == 'success'
        
        return features
    
    def find_pattern(self, trigger_conditions, action_pattern, description):
        """Find tasks matching trigger conditions and analyze action outcomes."""
        matching_tasks = []
        
        for task in self.tasks:
            f = self.extract_context_features(task)
            match = True
            for key, expected in trigger_conditions.items():
                actual = f.get(key)
                if expected is None:
                    # Match if actual is None (no delegation)
                    if actual is not None:
                        match = False
                        break
                elif isinstance(expected, list):
                    if actual not in expected:
                        match = False
                        break
                elif actual != expected:
                    match = False
                    break
            
            if match:
                matching_tasks.append(f)
        
        if len(matching_tasks) < MIN_PATTERN_TASKS:
            return None
        
        # Calculate pattern performance
        success_count = sum(1 for t in matching_tasks if t['success'])
        success_rate = success_count / len(matching_tasks)
        
        # Calculate generalization score
        unique_types = len(set(t['type'] for t in matching_tasks))
        unique_subtypes = len(set(t['subtype'] for t in matching_tasks))
        generalization_score = min(1.0, (unique_types * unique_subtypes) / 10)
        
        pattern = {
            'pattern_id': f'meta_pattern_{self.pattern_id_counter:03d}',
            'trigger': trigger_conditions,
            'action': action_pattern,
            'description': description,
            'matching_tasks': len(matching_tasks),
            'success_rate': success_rate,
            'generalization_score': generalization_score,
            'sample_task_ids': [t['task_id'] for t in matching_tasks[:5]],
            'cross_task_valid': unique_types > 1,
            'timestamp': datetime.now().isoformat()
        }
        
        self.pattern_id_counter += 1
        return pattern
    
    def mine_patterns(self):
        """Mine all cross-task patterns."""
        print("\n🔬 Mining cross-task patterns...")
        patterns = []
        
        # Agent-based patterns
        for agent in ['health_agent', 'research_agent', 'data_agent']:
            p = self.find_pattern(
                {'delegated_to': agent},
                {'approach': f'delegate_to_{agent}'},
                f'Tasks delegated to {agent} show consistent success'
            )
            if p:
                patterns.append(p)
        
        # Subtype patterns
        for subtype in ['health_check', 'learning_sync', 'subagent_task']:
            p = self.find_pattern(
                {'subtype': subtype},
                {'approach': f'{subtype}_execution'},
                f'{subtype} tasks perform well with their dedicated approach'
            )
            if p:
                patterns.append(p)
        
        # Duration patterns
        for bucket in ['fast', 'medium']:
            p = self.find_pattern(
                {'duration_bucket': bucket},
                {'approach': f'{bucket}_execution'},
                f'{bucket.title()} tasks (<60s) have highest success with direct execution'
            )
            if p:
                patterns.append(p)
        
        # Slow tasks pattern
        p = self.find_pattern(
            {'duration_bucket': 'slow'},
            {'approach': 'monitored_execution'},
            'Slow tasks (>5min) may benefit from more monitoring'
        )
        if p:
            patterns.append(p)
        
        # Direct execution pattern (main agent)
        p = self.find_pattern(
            {'delegated_to': None},
            {'approach': 'direct_execution'},
            'Direct execution works well for main-agent tasks'
        )
        if p:
            patterns.append(p)
        
        self.patterns = [p for p in patterns if p and p['generalization_score'] >= MIN_GENERALIZATION_SCORE]
        print(f"   Found {len(self.patterns)} patterns with generalization >= {MIN_GENERALIZATION_SCORE}")
        
        return self.patterns
    
    def save_patterns(self):
        """Save patterns to file."""
        if not self.patterns:
            # Ensure directory exists
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                json.dump({'patterns': [], 'generated_at': datetime.now().isoformat()}, f, indent=2)
            return
        
        # Ensure directory exists
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            'patterns': self.patterns,
            'generated_at': datetime.now().isoformat(),
            'total_patterns': len(self.patterns),
            'total_tasks_analyzed': len(self.tasks),
            'pattern_coverage': sum(p['matching_tasks'] for p in self.patterns) / len(self.tasks) if self.tasks else 0
        }
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n💾 Saved {len(self.patterns)} patterns to {OUTPUT_FILE}")
        print(f"   Pattern coverage: {output['pattern_coverage']:.1%}")
    
    def print_patterns(self):
        """Print discovered patterns."""
        if not self.patterns:
            print("❌ No patterns found yet.")
            return
        
        print(f"\n📋 DISCOVERED PATTERNS ({len(self.patterns)})")
        print("=" * 60)
        
        for i, p in enumerate(sorted(self.patterns, key=lambda x: -x['generalization_score']), 1):
            print(f"\n{i}. {p['pattern_id']}")
            print(f"   Description: {p['description']}")
            print(f"   Trigger: {p['trigger']}")
            print(f"   Success Rate: {p['success_rate']:.1%}")
            print(f"   Generalization: {p['generalization_score']:.2f}")
            print(f"   Matching Tasks: {p['matching_tasks']}")
            print(f"   Cross-Task Valid: {p['cross_task_valid']}")


def run_mining():
    """Main mining execution."""
    print("🔍 Cross-Task Pattern Miner — Phase 1")
    print("=" * 50)
    
    miner = PatternMiner()
    miner.load_tasks()
    miner.mine_patterns()
    miner.save_patterns()
    miner.print_patterns()
    
    # Check success criteria
    print("\n📊 SUCCESS CRITERIA CHECK")
    print(f"   Patterns found: {len(miner.patterns)} (target: ≥5)")
    
    if miner.patterns:
        coverage = sum(p['matching_tasks'] for p in miner.patterns) / len(miner.tasks)
        print(f"   Pattern coverage: {coverage:.1%} (target: ≥50%)")
        
        cross_task = sum(1 for p in miner.patterns if p['cross_task_valid'])
        print(f"   Cross-task patterns: {cross_task} (target: ≥5)")
    
    return miner.patterns


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Cross-Task Pattern Miner')
    parser.add_argument('--status', action='store_true', help='Show current patterns')
    parser.add_argument('--validate', action='store_true', help='Validate patterns')
    args = parser.parse_args()
    
    if args.status or args.validate:
        try:
            with open(OUTPUT_FILE, 'r') as f:
                data = json.load(f)
            patterns = data.get('patterns', [])
            print(f"📋 Current patterns: {len(patterns)}")
            for p in patterns:
                print(f"   - {p['pattern_id']}: {p['description'][:50]}...")
        except FileNotFoundError:
            print("❌ No patterns found. Run mining first.")
    else:
        run_mining()
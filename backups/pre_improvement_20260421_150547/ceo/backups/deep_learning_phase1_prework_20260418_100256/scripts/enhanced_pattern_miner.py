#!/usr/bin/env python3
"""
enhanced_pattern_miner.py — Advanced Cross-Task Pattern Mining
============================================================
Finds deeper, more actionable patterns than basic mining.

Usage:
    python3 enhanced_pattern_miner.py           # Run enhanced mining
    python3 enhanced_pattern_miner.py --count  # Show pattern count
    python3 enhanced_pattern_miner.py --list   # List all patterns
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
TASK_LOG = WORKSPACE / 'memory/task_log/unified_tasks.json'
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'
WEIGHTS_FILE = WORKSPACE / 'memory/meta_learning/algorithm_weights.json'


def load_tasks():
    """Load task log."""
    with open(TASK_LOG) as f:
        data = json.load(f)
    return data.get('tasks', data)


def load_patterns():
    """Load existing patterns."""
    if PATTERNS_FILE.exists():
        with open(PATTERNS_FILE) as f:
            return json.load(f).get('patterns', [])
    return []


def save_patterns(patterns):
    """Save patterns."""
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATTERNS_FILE, 'w') as f:
        json.dump({
            'patterns': patterns,
            'updated_at': datetime.now().isoformat(),
            'total_patterns': len(patterns)
        }, f, indent=2)


def analyze_task_features(tasks):
    """Extract comprehensive features from tasks."""
    features = {
        'delegation_patterns': defaultdict(list),
        'duration_patterns': defaultdict(list),
        'time_patterns': defaultdict(list),
        'type_patterns': defaultdict(list),
        'success_correlations': [],
    }
    
    for t in tasks:
        meta = t.get('metadata', {})
        task_type = t.get('type', t.get('subtype', 'unknown'))
        outcome = t.get('outcome', 'success')
        duration = meta.get('duration_ms', 0)
        delegated_to = meta.get('delegated_to', 'main')
        priority = meta.get('priority', 'MEDIUM')
        
        # Convert duration to seconds for analysis
        dur_sec = duration / 1000
        
        # 1. Delegation patterns
        delegation_key = f"delegated_to_{delegated_to}"
        features['delegation_patterns'][delegation_key].append({
            'outcome': outcome,
            'duration': dur_sec,
            'type': task_type
        })
        
        # 2. Duration patterns (more granular)
        if dur_sec < 10:
            dur_key = 'duration_<10s'
        elif dur_sec < 30:
            dur_key = 'duration_10-30s'
        elif dur_sec < 60:
            dur_key = 'duration_30-60s'
        elif dur_sec < 120:
            dur_key = 'duration_1-2min'
        elif dur_sec < 300:
            dur_key = 'duration_2-5min'
        else:
            dur_key = 'duration_>5min'
        features['duration_patterns'][dur_key].append({
            'outcome': outcome,
            'delegated_to': delegated_to
        })
        
        # 3. Type patterns
        features['type_patterns'][task_type].append({
            'outcome': outcome,
            'duration': dur_sec,
            'delegated_to': delegated_to
        })
        
        # 4. Priority patterns
        priority_key = f"priority_{priority}"
        features['delegation_patterns'][priority_key].append({
            'outcome': outcome,
            'duration': dur_sec
        })
    
    return features


def calculate_pattern_metrics(occurrences):
    """Calculate metrics for a pattern."""
    if not occurrences:
        return {'success_rate': 0, 'avg_duration': 0, 'count': 0}
    
    successes = sum(1 for o in occurrences if o.get('outcome') == 'success')
    durations = [o.get('duration', 0) for o in occurrences if o.get('duration')]
    
    return {
        'success_rate': successes / len(occurrences) * 100,
        'avg_duration': sum(durations) / len(durations) if durations else 0,
        'count': len(occurrences)
    }


def generate_patterns(features, tasks):
    """Generate comprehensive patterns from features."""
    patterns = []
    pattern_id = 0
    
    # 1. Delegation success patterns
    for key, occurrences in features['delegation_patterns'].items():
        if not key.startswith('delegated_to_'):
            continue
        
        metrics = calculate_pattern_metrics(occurrences)
        if metrics['count'] < 3:  # Skip rare patterns
            continue
        
        pattern = {
            'pattern_id': f'meta_pattern_{pattern_id:03d}',
            'description': f'Tasks {key.replace("delegated_to_", "delegated to ")} show {metrics["success_rate"]:.0f}% success rate',
            'trigger': {key: True},
            'success_rate': metrics['success_rate'],
            'generalization_score': min(1.0, metrics['count'] / 50),
            'matching_tasks': metrics['count'],
            'cross_task_valid': metrics['count'] >= 20,
            'avg_duration_sec': metrics['avg_duration'],
            'type': 'delegation_pattern',
            'discovered_at': datetime.now().isoformat()
        }
        patterns.append(pattern)
        pattern_id += 1
    
    # 2. Duration success patterns
    for key, occurrences in features['duration_patterns'].items():
        metrics = calculate_pattern_metrics(occurrences)
        if metrics['count'] < 3:
            continue
        
        # Determine recommended execution mode based on duration
        if metrics['avg_duration'] < 60:
            recommended_mode = 'direct_execution'
        else:
            recommended_mode = 'delegated_or_monitored'
        
        pattern = {
            'pattern_id': f'meta_pattern_{pattern_id:03d}',
            'description': f'{key} tasks ({metrics["count"]} samples) - recommend {recommended_mode}',
            'trigger': {'duration_bucket': key.replace('duration_', '')},
            'success_rate': metrics['success_rate'],
            'generalization_score': min(1.0, metrics['count'] / 30),
            'matching_tasks': metrics['count'],
            'cross_task_valid': True,
            'recommended_execution': recommended_mode,
            'type': 'duration_pattern',
            'discovered_at': datetime.now().isoformat()
        }
        patterns.append(pattern)
        pattern_id += 1
    
    # 3. Task type patterns
    for task_type, occurrences in features['type_patterns'].items():
        metrics = calculate_pattern_metrics(occurrences)
        if metrics['count'] < 3:
            continue
        
        # What works best for this type?
        delegated = sum(1 for o in occurrences if o.get('delegated_to') != 'main')
        direct = metrics['count'] - delegated
        
        if delegated > direct * 2:
            recommended = 'delegated'
        elif direct > delegated * 2:
            recommended = 'direct'
        else:
            recommended = 'hybrid'
        
        pattern = {
            'pattern_id': f'meta_pattern_{pattern_id:03d}',
            'description': f'{task_type} tasks ({metrics["count"]}) work best with {recommended} execution',
            'trigger': {'task_type': task_type},
            'success_rate': metrics['success_rate'],
            'generalization_score': min(1.0, metrics['count'] / 40),
            'matching_tasks': metrics['count'],
            'cross_task_valid': metrics['count'] >= 20,
            'recommended_execution': recommended,
            'type': 'type_pattern',
            'discovered_at': datetime.now().isoformat()
        }
        patterns.append(pattern)
        pattern_id += 1
    
    # 4. Priority patterns
    for key, occurrences in features['delegation_patterns'].items():
        if not key.startswith('priority_'):
            continue
        
        metrics = calculate_pattern_metrics(occurrences)
        if metrics['count'] < 3:
            continue
        
        pattern = {
            'pattern_id': f'meta_pattern_{pattern_id:03d}',
            'description': f'{key.replace("_", " ").title()} priority tasks: {metrics["count"]} samples, {metrics["success_rate"]:.0f}% success',
            'trigger': {'priority': key.replace('priority_', '')},
            'success_rate': metrics['success_rate'],
            'generalization_score': min(0.8, metrics['count'] / 50),
            'matching_tasks': metrics['count'],
            'cross_task_valid': False,
            'type': 'priority_pattern',
            'discovered_at': datetime.now().isoformat()
        }
        patterns.append(pattern)
        pattern_id += 1
    
    # 5. Composite patterns (high-value combinations)
    # Find delegation + duration combinations
    composite_patterns = []
    for t in tasks:
        meta = t.get('metadata', {})
        dur = meta.get('duration_ms', 0) / 1000
        delegated = meta.get('delegated_to', 'main')
        outcome = t.get('outcome', 'success')
        
        if dur < 60 and delegated != 'main':
            composite_patterns.append({
                'trigger': 'fast_delegated',
                'outcome': outcome,
                'duration': dur
            })
    
    if len(composite_patterns) >= 10:
        successes = sum(1 for p in composite_patterns if p['outcome'] == 'success')
        pattern = {
            'pattern_id': f'meta_pattern_{pattern_id:03d}',
            'description': f'Fast delegated tasks (<60s): {len(composite_patterns)} samples, {successes/len(composite_patterns)*100:.0f}% success',
            'trigger': {'duration_bucket': 'fast', 'delegated': True},
            'success_rate': successes / len(composite_patterns) * 100,
            'generalization_score': min(1.0, len(composite_patterns) / 50),
            'matching_tasks': len(composite_patterns),
            'cross_task_valid': True,
            'type': 'composite_pattern',
            'discovered_at': datetime.now().isoformat()
        }
        patterns.append(pattern)
    
    return patterns


def run_enhanced_mining():
    """Run the enhanced pattern mining."""
    print("🧠 Enhanced Pattern Miner — Advanced Cross-Task Patterns")
    print("=" * 60)
    
    # Load data
    tasks = load_tasks()
    existing_patterns = load_patterns()
    
    print(f"📂 Loaded {len(tasks)} tasks, {len(existing_patterns)} existing patterns")
    
    # Analyze features
    print("\n🔍 Analyzing task features...")
    features = analyze_task_features(tasks)
    
    # Generate new patterns
    print("\n⛏️ Mining patterns...")
    new_patterns = generate_patterns(features, tasks)
    
    print(f"   Found {len(new_patterns)} new patterns")
    
    # Merge with existing, avoid duplicates
    existing_ids = set(p.get('pattern_id') for p in existing_patterns)
    merged_patterns = list(existing_patterns)
    
    added = 0
    for p in new_patterns:
        if p['pattern_id'] not in existing_ids:
            merged_patterns.append(p)
            added += 1
    
    print(f"   Added {added} new patterns (total: {len(merged_patterns)})")
    
    # Save
    save_patterns(merged_patterns)
    print(f"\n💾 Saved {len(merged_patterns)} patterns to {PATTERNS_FILE}")
    
    # Show pattern summary
    print("\n📋 Pattern Summary:")
    patterns_by_type = defaultdict(list)
    for p in merged_patterns:
        patterns_by_type[p.get('type', 'unknown')].append(p)
    
    for ptype, plist in sorted(patterns_by_type.items()):
        print(f"   {ptype}: {len(plist)} patterns")
    
    return merged_patterns


def show_pattern_count():
    """Show current pattern count."""
    patterns = load_patterns()
    print(f"📊 Current patterns: {len(patterns)}")
    
    if patterns:
        types = defaultdict(int)
        for p in patterns:
            types[p.get('type', 'unknown')] += 1
        for t, c in sorted(types.items(), key=lambda x: -x[1]):
            print(f"   {t}: {c}")


def list_patterns():
    """List all patterns."""
    patterns = load_patterns()
    print(f"📋 All Patterns ({len(patterns)}):")
    print("=" * 60)
    
    for p in sorted(patterns, key=lambda x: -x.get('matching_tasks', 0)):
        print(f"\n{p['pattern_id']}: {p.get('description', 'N/A')[:70]}")
        print(f"   Type: {p.get('type')}, Success: {p.get('success_rate', 0):.0f}%, "
              f"Tasks: {p.get('matching_tasks', 0)}")


def main():
    if '--count' in sys.argv:
        show_pattern_count()
    elif '--list' in sys.argv:
        list_patterns()
    else:
        run_enhanced_mining()


if __name__ == '__main__':
    main()
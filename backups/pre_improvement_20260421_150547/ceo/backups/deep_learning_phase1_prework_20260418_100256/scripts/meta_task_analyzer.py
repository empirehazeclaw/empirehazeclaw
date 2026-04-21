#!/usr/bin/env python3
"""
meta_task_analyzer.py — Phase 1: Cross-Task Pattern Mining
Analysiert alle Tasks nach gemeinsamen Erfolgsfaktoren.
Output: task_features.json

Usage:
    python3 meta_task_analyzer.py                    # Full analysis
    python3 meta_task_analyzer.py --summary          # Quick summary
    python3 meta_task_analyzer.py --task-type <type> # Filter by type
"""

import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent  # /workspace/ceo
TASK_LOG = WORKSPACE / "memory/task_log/unified_tasks.json"
OUTPUT_DIR = WORKSPACE / "memory/meta_learning"
OUTPUT_FILE = OUTPUT_DIR / "task_features.json"

# Ensure output dir exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Feature extraction patterns
CONTEXT_TYPES = [
    "file_operation", "api_call", "data_processing", "decision_making",
    "learning", "orchestration", "monitoring", "analysis", "automation"
]

APPROACHES = [
    "direct_execution", "retry", "fallback", "decomposition", 
    "parallel_execution", "query_based", "search_based"
]

SUCCESS_INDICATORS = ["completed", "success", "passed", "done"]
FAILURE_INDICATORS = ["failed", "error", "timeout", "exception", "aborted"]


def load_tasks():
    """Load tasks from unified_task_logger."""
    with open(TASK_LOG, 'r') as f:
        data = json.load(f)
    return data.get('tasks', [])


def extract_task_features(task):
    """Extract features from a single task for pattern analysis."""
    features = {
        'task_id': task.get('task_id'),
        'type': task.get('type', 'unknown'),
        'subtype': task.get('subtype', task.get('type', 'unknown')),
        'outcome': task.get('outcome', 'unknown'),
        'timestamp': task.get('timestamp'),
    }
    
    # Extract from metadata
    metadata = task.get('metadata', {})
    features['delegated_to'] = metadata.get('delegated_to')
    features['duration_ms'] = metadata.get('duration_ms')
    features['priority'] = metadata.get('priority', 'MEDIUM')
    features['tool'] = metadata.get('tool')
    features['error'] = metadata.get('error')
    
    # Extract from details
    details = task.get('details', '')
    features['details'] = details
    features['has_error'] = any(e in str(details).lower() for e in FAILURE_INDICATORS)
    features['success'] = task.get('outcome') == 'success'
    
    # Context features
    details_lower = str(details).lower()
    features['context_type'] = 'unknown'
    for ctx in CONTEXT_TYPES:
        if ctx.replace('_', ' ') in details_lower or ctx in details_lower:
            features['context_type'] = ctx
            break
    
    # Approach detection
    features['approach'] = 'direct_execution'
    if 'retry' in details_lower:
        features['approach'] = 'retry'
    elif 'fallback' in details_lower or 'alternative' in details_lower:
        features['approach'] = 'fallback'
    elif metadata.get('delegated_to'):
        features['approach'] = 'delegated'
    elif 'search' in details_lower or 'find' in details_lower:
        features['approach'] = 'search_based'
    
    # Success factors
    features['fast_completion'] = (
        features.get('duration_ms', 0) < 60000 if features.get('duration_ms') else None
    )
    
    return features


def analyze_success_factors(tasks):
    """Analyze common success factors across all tasks."""
    success_tasks = [t for t in tasks if t.get('outcome') == 'success']
    failed_tasks = [t for t in tasks if t.get('outcome') != 'success']
    
    factors = {
        'total_tasks': len(tasks),
        'success_count': len(success_tasks),
        'failure_count': len(failed_tasks),
        'success_rate': len(success_tasks) / len(tasks) if tasks else 0,
        
        # Success by type
        'success_by_type': {},
        # Success by subtype  
        'success_by_subtype': {},
        # Success by delegated_to
        'success_by_agent': {},
        # Average duration
        'avg_duration_ms': 0,
        # Common failure modes
        'failure_reasons': Counter(),
        # Duration buckets
        'duration_buckets': Counter(),
    }
    
    duration_sum = 0
    duration_count = 0
    
    for task in tasks:
        t = extract_task_features(task)
        outcome = task.get('outcome', 'unknown')
        
        # By type
        task_type = t['type']
        if task_type not in factors['success_by_type']:
            factors['success_by_type'][task_type] = {'total': 0, 'success': 0}
        factors['success_by_type'][task_type]['total'] += 1
        if outcome == 'success':
            factors['success_by_type'][task_type]['success'] += 1
        
        # By subtype
        subtype = t['subtype']
        if subtype not in factors['success_by_subtype']:
            factors['success_by_subtype'][subtype] = {'total': 0, 'success': 0}
        factors['success_by_subtype'][subtype]['total'] += 1
        if outcome == 'success':
            factors['success_by_subtype'][subtype]['success'] += 1
        
        # By agent
        agent = t.get('delegated_to', 'main')
        if agent not in factors['success_by_agent']:
            factors['success_by_agent'][agent] = {'total': 0, 'success': 0}
        factors['success_by_agent'][agent]['total'] += 1
        if outcome == 'success':
            factors['success_by_agent'][agent]['success'] += 1
        
        # Duration
        dur = t.get('duration_ms')
        if dur:
            duration_sum += dur
            duration_count += 1
            if dur < 30000:
                factors['duration_buckets']['<30s'] += 1
            elif dur < 120000:
                factors['duration_buckets']['30s-2min'] += 1
            elif dur < 300000:
                factors['duration_buckets']['2-5min'] += 1
            else:
                factors['duration_buckets']['>5min'] += 1
        
        # Failure reasons
        if outcome != 'success':
            err = t.get('error') or metadata.get('error', 'unknown')
            factors['failure_reasons'][err] += 1
    
    factors['avg_duration_ms'] = duration_sum / duration_count if duration_count else 0
    
    # Calculate success rates
    for cat in ['success_by_type', 'success_by_subtype', 'success_by_agent']:
        for key in factors[cat]:
            total = factors[cat][key]['total']
            success = factors[cat][key]['success']
            factors[cat][key]['rate'] = success / total if total > 0 else 0
    
    return factors


def generate_insights(factors):
    """Generate actionable insights from success factors."""
    insights = []
    
    # Best performing agents
    agent_rates = [(k, v['success']/v['total']) for k, v in factors['success_by_agent'].items() if v['total'] >= 5]
    agent_rates.sort(key=lambda x: -x[1])
    if agent_rates:
        insights.append({
            'type': 'agent_performance',
            'finding': f"Best agent: {agent_rates[0][0]} ({agent_rates[0][1]:.1%} success rate)",
            'data': agent_rates[:5]
        })
    
    # Task type performance
    type_rates = [(k, v['rate']) for k, v in factors['success_by_type'].items() if v['total'] >= 5]
    type_rates.sort(key=lambda x: -x[1])
    if type_rates:
        insights.append({
            'type': 'task_type_performance',
            'finding': f"Best task type: {type_rates[0][0]} ({type_rates[0][1]:.1%} success rate)",
            'data': type_rates[:5]
        })
    
    # Duration impact on success
    fast_tasks = [t for t in factors['duration_buckets'].keys() if '<' in t or '30s' in t]
    slow_tasks = [t for t in factors['duration_buckets'].keys() if '>' in t]
    
    # Failure patterns
    if factors['failure_reasons']:
        top_failures = factors['failure_reasons'].most_common(3)
        insights.append({
            'type': 'failure_patterns',
            'finding': f"Top failure: {top_failures[0][0]} ({top_failures[0][1]}x)",
            'data': top_failures
        })
    
    # Success rate trend (if timestamp data available)
    # Will be computed in cross_task_pattern_miner
    
    return insights


def run_analysis(filter_type=None, summary_only=False):
    """Main analysis runner."""
    print("🔍 Meta Task Analyzer — Phase 1")
    print("=" * 50)
    
    # Load tasks
    print(f"📂 Loading tasks from {TASK_LOG}...")
    tasks = load_tasks()
    print(f"   Loaded {len(tasks)} tasks")
    
    # Filter if requested
    if filter_type:
        tasks = [t for t in tasks if t.get('type') == filter_type]
        print(f"   Filtered to {len(tasks)} tasks of type '{filter_type}'")
    
    # Extract features
    print("\n📊 Extracting features...")
    features = []
    for task in tasks:
        f = extract_task_features(task)
        features.append(f)
    
    # Analyze
    print("🔬 Analyzing success factors...")
    factors = analyze_success_factors(tasks)
    
    # Generate insights
    insights = generate_insights(factors)
    
    # Output
    if summary_only:
        print("\n📈 SUMMARY")
        print(f"   Total tasks: {factors['total_tasks']}")
        print(f"   Success rate: {factors['success_rate']:.1%}")
        print(f"   Avg duration: {factors['avg_duration_ms']/1000:.1f}s")
        print(f"   Failure reasons: {len(factors['failure_reasons'])} unique")
    else:
        # Full analysis
        result = {
            'generated_at': datetime.now().isoformat(),
            'total_tasks': len(tasks),
            'factors': factors,
            'insights': insights,
            'task_features': features[:100]  # First 100 for detailed review
        }
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Output: {OUTPUT_FILE}")
        print(f"   Success rate: {factors['success_rate']:.1%}")
        print(f"   Insights generated: {len(insights)}")
        
        # Print top insights
        if insights:
            print("\n📋 TOP INSIGHTS:")
            for insight in insights[:3]:
                print(f"   [{insight['type']}] {insight['finding']}")
    
    return factors, insights


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Meta Task Analyzer')
    parser.add_argument('--summary', action='store_true', help='Quick summary only')
    parser.add_argument('--task-type', type=str, help='Filter by task type')
    parser.add_argument('--output', type=str, help='Output file path')
    args = parser.parse_args()
    
    run_analysis(filter_type=args.task_type, summary_only=args.summary)
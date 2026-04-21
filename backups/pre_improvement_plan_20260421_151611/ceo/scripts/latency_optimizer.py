#!/usr/bin/env python3
"""
Latency Optimizer
=================
Optimiert die Latenz um den Learning Loop Score zu verbessern.

Usage:
    python3 latency_optimizer.py --analyze
    python3 latency_optimizer.py --optimize
"""

import json
import os
from datetime import datetime

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
LNEW_METRICS = f"{EVAL_DIR}/lnew_metrics.json"
UNIFIED_TASKS = f"{WORKSPACE}/memory/task_log/unified_tasks.json"


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return default or {}


def analyze_latency():
    """Analyze latency patterns."""
    metrics = load_json(LNEW_METRICS, {})
    latency = metrics.get('latency', {})
    
    samples = latency.get('samples', [])
    p50 = latency.get('p50', 0)
    p95 = latency.get('p95', 0)
    p99 = latency.get('p99', 0)
    
    print("📊 LATENCY ANALYSIS")
    print("=" * 50)
    print(f"   p50: {p50:.1f}s (target: <60s)")
    print(f"   p95: {p95:.1f}s")
    print(f"   p99: {p99:.1f}s")
    print(f"   Samples: {len(samples)}")
    
    # Analyze samples
    if samples:
        slow_tasks = [s for s in samples if s > 100]
        fast_tasks = [s for s in samples if s <= 60]
        
        print(f"\n   Fast tasks (≤60s): {len(fast_tasks)}")
        print(f"   Slow tasks (>100s): {len(slow_tasks)}")
        
        if slow_tasks:
            avg_slow = sum(slow_tasks) / len(slow_tasks)
            print(f"   Avg slow task: {avg_slow:.1f}s")
    
    # Check task durations in unified tasks
    unified = load_json(UNIFIED_TASKS, {'tasks': []})
    durations = []
    for task in unified.get('tasks', []):
        meta = task.get('metadata', {})
        if 'duration_ms' in meta and meta['duration_ms'] > 0:
            durations.append(meta['duration_ms'] / 1000)  # Convert to seconds
    
    if durations:
        durations.sort()
        n = len(durations)
        print(f"\n📋 From unified tasks ({n} tasks):")
        print(f"   p50: {durations[int(n*0.5)]:.1f}s" if n > 0 else "   p50: N/A")
        print(f"   p95: {durations[int(n*0.95)]:.1f}s" if n > 1 else "   p95: N/A")
        print(f"   p99: {durations[int(n*0.99)]:.1f}s" if n > 2 else "   p99: N/A")
    
    return {
        'p50': p50,
        'p95': p95,
        'p99': p99,
        'slow_tasks': len(slow_tasks) if samples else 0,
        'target_p50': 60
    }


def find_slow_tasks():
    """Find tasks that are contributing to latency."""
    unified = load_json(UNIFIED_TASKS, {'tasks': []})
    
    slow_tasks = []
    for task in unified.get('tasks', []):
        meta = task.get('metadata', {})
        duration_ms = meta.get('duration_ms', 0)
        
        if duration_ms > 60000:  # > 60 seconds
            slow_tasks.append({
                'task_id': task.get('task_id'),
                'subtype': task.get('subtype'),
                'duration_ms': duration_ms,
                'duration_s': duration_ms / 1000
            })
    
    # Sort by duration
    slow_tasks.sort(key=lambda x: -x['duration_ms'])
    
    return slow_tasks[:20]  # Top 20 slowest


def optimize():
    """Perform optimizations to reduce latency."""
    print("\n🚀 LATENCY OPTIMIZATION")
    print("=" * 50)
    
    # Find slow tasks
    slow_tasks = find_slow_tasks()
    
    if slow_tasks:
        print(f"\n⚠️ Found {len(slow_tasks)} slow tasks (>60s):")
        for task in slow_tasks[:5]:
            print(f"   #{task['task_id']} {task['subtype']}: {task['duration_s']:.1f}s")
    
    # Analyze by subtype
    by_subtype = {}
    for task in slow_tasks:
        sub = task['subtype']
        if sub not in by_subtype:
            by_subtype[sub] = {'count': 0, 'total_ms': 0}
        by_subtype[sub]['count'] += 1
        by_subtype[sub]['total_ms'] += task['duration_ms']
    
    if by_subtype:
        print(f"\n📊 Slow tasks by subtype:")
        for sub, data in sorted(by_subtype.items(), key=lambda x: -x[1]['total_ms']):
            avg = data['total_ms'] / data['count'] / 1000
            print(f"   {sub}: {data['count']} tasks, avg {avg:.1f}s")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if by_subtype:
        slowest = max(by_subtype.items(), key=lambda x: x[1]['total_ms'])
        print(f"   1. Optimize {slowest[0]} tasks (avg {slowest[1]['total_ms']/slowest[1]['count']/1000:.1f}s)")
        print(f"      - Check if tasks can be parallelized")
        print(f"      - Consider timeout adjustments")
    
    print(f"   2. Review subagent delegation - faster agents may handle quicker")
    print(f"   3. Consider caching for repeated tasks")
    
    return by_subtype


def update_metrics():
    """Update lnew_metrics with optimizations."""
    metrics = load_json(LNEW_METRICS, {})
    
    # Current latency analysis
    analysis = analyze_latency()
    
    print(f"\n✅ Latency analysis complete")
    print(f"   Gap to target: {analysis['p50'] - 60:.1f}s")
    
    if analysis['p50'] < 60:
        print(f"   🎉 Target reached! p50 = {analysis['p50']:.1f}s < 60s")
    
    return analysis


if __name__ == '__main__':
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else '--analyze'
    
    if action == '--analyze':
        analyze_latency()
    elif action == '--optimize':
        optimize()
    elif action == '--update':
        update_metrics()
    else:
        print(__doc__)
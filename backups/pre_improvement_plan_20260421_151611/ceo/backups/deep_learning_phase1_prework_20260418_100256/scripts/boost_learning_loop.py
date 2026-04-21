#!/usr/bin/env python3
"""
Learning Loop Score Booster
==========================
Versucht den Learning Loop Score zu verbessern.

Usage:
    python3 boost_learning_loop.py
"""

import json
import os
from datetime import datetime

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
LOOP_SIGNAL = f"{EVAL_DIR}/learning_loop_signal.json"
LNEW_METRICS = f"{EVAL_DIR}/lnew_metrics.json"
CURRENT_MD = f"{WORKSPACE}/memory/short_term/current.md"


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return default or {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_current_score():
    """Get current learning loop score."""
    # From current.md
    if os.path.exists(CURRENT_MD):
        with open(CURRENT_MD, 'r') as f:
            content = f.read()
        for line in content.split('\n'):
            if 'Loop Score' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    try:
                        return float(parts[2].strip())
                    except:
                        pass
    return 0.784  # fallback


def analyze_gaps():
    """Analyze what's causing low score."""
    gaps = []
    
    # Check lnew_metrics for task success
    metrics = load_json(LNEW_METRICS, {})
    tsr = metrics.get('task_success', {}).get('rate', 1.0)
    
    if tsr < 0.9:
        gaps.append({'area': 'task_success', 'gap': 0.9 - tsr, 'priority': 'HIGH'})
    
    # Check error rate
    errors = metrics.get('errors', {}).get('rate', 0)
    if errors > 0.05:
        gaps.append({'area': 'error_rate', 'gap': errors - 0.05, 'priority': 'HIGH'})
    
    # Check latency
    latency = metrics.get('latency', {}).get('p50', 0)
    if latency > 60:
        gaps.append({'area': 'latency', 'gap': latency - 60, 'priority': 'MED'})
    
    return gaps


def generate_improvement_signals():
    """Generate signals to improve learning loop."""
    signals = []
    
    # Based on current metrics
    metrics = load_json(LNEW_METRICS, {})
    tsr = metrics.get('task_success', {}).get('rate', 1.0)
    
    if tsr >= 0.95:
        signals.append({
            'type': 'positive_reinforcement',
            'area': 'task_success',
            'signal': f'TSR at {tsr*100:.1f}% - maintain current approach',
            'confidence': 0.8
        })
    
    # Check for patterns in recent tasks
    task_log = f"{WORKSPACE}/memory/task_log/unified_tasks.json"
    if os.path.exists(task_log):
        with open(task_log) as f:
            tasks = json.load(f).get('tasks', [])
        
        # Analyze by subtype
        by_subtype = {}
        for task in tasks[-50:]:
            sub = task.get('subtype', 'unknown')
            if sub not in by_subtype:
                by_subtype[sub] = {'success': 0, 'total': 0}
            by_subtype[sub]['total'] += 1
            if task.get('outcome') == 'success':
                by_subtype[sub]['success'] += 1
        
        for sub, stats in by_subtype.items():
            rate = stats['success'] / max(stats['total'], 1)
            if rate == 1.0:
                signals.append({
                    'type': 'pattern_identified',
                    'area': sub,
                    'signal': f'{sub} has 100% success rate - replicate pattern',
                    'confidence': 0.9
                })
            elif rate < 0.8:
                signals.append({
                    'type': 'improvement_needed',
                    'area': sub,
                    'signal': f'{sub} success rate only {rate*100:.1f}% - needs attention',
                    'confidence': 0.7
                })
    
    return signals


def update_learning_loop():
    """Update learning loop with improvements."""
    score = get_current_score()
    gaps = analyze_gaps()
    signals = generate_improvement_signals()
    
    # Create updated signal
    loop_signal = {
        'timestamp': datetime.now().isoformat(),
        'source': 'boost_learning_loop',
        'current_score': score,
        'target_score': 0.80,
        'score_gap': 0.80 - score,
        'gaps': gaps,
        'signals': signals,
        'recommendations': []
    }
    
    # Generate recommendations
    if score < 0.80:
        loop_signal['recommendations'].append({
            'priority': 'HIGH',
            'area': 'score',
            'recommendation': f'Score {score} below target 0.80 - needs immediate improvement'
        })
    
    for gap in gaps:
        loop_signal['recommendations'].append({
            'priority': gap['priority'],
            'area': gap['area'],
            'recommendation': f'Improve {gap["area"]} - gap of {gap["gap"]:.2f}'
        })
    
    # Save signal
    save_json(LOOP_SIGNAL, loop_signal)
    
    return loop_signal


def main():
    print("🚀 Learning Loop Score Booster")
    print("=" * 50)
    
    score = get_current_score()
    print(f"Current Score: {score}")
    print(f"Target Score: 0.80")
    print(f"Gap: {0.80 - score:.3f}")
    
    # Analyze gaps
    gaps = analyze_gaps()
    if gaps:
        print(f"\n⚠️ Gaps found:")
        for gap in gaps:
            print(f"   [{gap['priority']}] {gap['area']}: {gap['gap']:.3f}")
    else:
        print(f"\n✅ No critical gaps found")
    
    # Generate signals
    signals = generate_improvement_signals()
    print(f"\n📊 Generated {len(signals)} improvement signals")
    for sig in signals[:3]:
        print(f"   [{sig['type']}] {sig['area']}: {sig['signal'][:60]}")
    
    # Update learning loop
    result = update_learning_loop()
    
    print(f"\n✅ Learning loop signal updated")
    print(f"   Recommendations: {len(result['recommendations'])}")


if __name__ == '__main__':
    main()
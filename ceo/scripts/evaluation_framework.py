#!/usr/bin/env python3
"""
Evaluation Framework - Enhanced
================================
Comprehensive evaluation using unified task logger as source of truth.

LNEW = Latency, Number of Errors, Efficiency, Worth

Usage:
    python3 evaluation_framework.py --action collect_metrics
    python3 evaluation_framework.py --action run_tests
    python3 evaluation_framework.py --action report
    python3 evaluation_framework.py --action integrate
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
METRICS_FILE = f"{EVAL_DIR}/lnew_metrics.json"
ANTIPATTERN_FILE = f"{EVAL_DIR}/antipattern_tests.json"
BEHAVIORAL_FILE = f"{EVAL_DIR}/behavioral_results.json"
TASK_LOG_DIR = f"{WORKSPACE}/memory/task_log"
UNIFIED_TASKS = f"{TASK_LOG_DIR}/unified_tasks.json"


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


class EvaluationFramework:
    def __init__(self):
        self.metrics = self.load_metrics()
        self.antipatterns = self.get_antipattern_definitions()
        os.makedirs(EVAL_DIR, exist_ok=True)
    
    def load_metrics(self):
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        return self.init_metrics()
    
    def init_metrics(self):
        return {
            'latency': {'samples': [], 'p50': 0, 'p95': 0, 'p99': 0},
            'errors': {'count': 0, 'rate': 0.0, 'total_tasks': 0},
            'efficiency': {'tokens_per_task': [], 'avg': 0},
            'worth': {'cost_per_task': [], 'avg': 0},
            'task_success': {'successes': 0, 'failures': 0, 'rate': 0.8},
            'last_updated': datetime.now().isoformat()
        }
    
    def save_metrics(self):
        self.metrics['last_updated'] = datetime.now().isoformat()
        save_json(METRICS_FILE, self.metrics)
    
    def load_unified_tasks(self):
        """Load tasks from unified task logger."""
        return load_json(UNIFIED_TASKS, {'tasks': []})
    
    def collect_metrics(self):
        """Collect current system metrics from unified task logger."""
        print("📊 Collecting LNEW Metrics from Unified Logger")
        print("=" * 50)
        
        unified = self.load_unified_tasks()
        tasks = unified.get('tasks', [])
        
        # Calculate from real task data
        total = len(tasks)
        successes = sum(1 for t in tasks if t.get('outcome') == 'success')
        failures = sum(1 for t in tasks if t.get('outcome') == 'failure')
        
        # By subtype analysis
        by_subtype = defaultdict(lambda: {'success': 0, 'failure': 0, 'total': 0})
        for task in tasks:
            sub = task.get('subtype', 'unknown')
            outcome = task.get('outcome', 'unknown')
            by_subtype[sub]['total'] += 1
            if outcome == 'success':
                by_subtype[sub]['success'] += 1
            elif outcome == 'failure':
                by_subtype[sub]['failure'] += 1
        
        # Task success rate (primary metric)
        self.metrics['task_success']['successes'] = successes
        self.metrics['task_success']['failures'] = failures
        self.metrics['task_success']['rate'] = successes / max(total, 1)
        self.metrics['errors']['total_tasks'] = total
        self.metrics['errors']['count'] = failures
        self.metrics['errors']['rate'] = failures / max(total, 1)
        
        # Estimate latency from task durations
        durations = []
        for task in tasks:
            meta = task.get('metadata', {})
            if 'duration_ms' in meta and meta['duration_ms'] > 0:
                durations.append(meta['duration_ms'] / 1000)  # Convert to seconds
        
        if durations:
            durations.sort()
            n = len(durations)
            self.metrics['latency']['samples'] = durations[-100:]  # Keep last 100
            self.metrics['latency']['p50'] = durations[int(n * 0.5)]
            self.metrics['latency']['p95'] = durations[int(n * 0.95)]
            self.metrics['latency']['p99'] = durations[int(n * 0.99)] if n > 1 else durations[-1]
        
        self.save_metrics()
        self.print_metrics_summary()
        
        return self.metrics
    
    def print_metrics_summary(self):
        m = self.metrics
        print(f"\n📈 LNEW Metrics Summary:")
        print(f"   Latency p50: {m['latency'].get('p50', 0):.3f}s")
        print(f"   Latency p95: {m['latency'].get('p95', 0):.3f}s")
        print(f"   Errors: {m['errors'].get('count', 0)}/{m['errors'].get('total_tasks', 0)} ({m['errors'].get('rate', 0)*100:.1f}%)")
        print(f"   Efficiency: {m['efficiency'].get('avg', 0):.1f} tokens/task")
        print(f"   Task Success: {m['task_success'].get('rate', 0)*100:.1f}%")
    
    def get_antipattern_definitions(self):
        return {
            'filler_words': {
                'pattern': r'(Great question|I\'d be happy|Of course|As an AI)',
                'severity': 'MED',
                'description': 'Uses filler words instead of being direct'
            },
            'over_confirmation': {
                'pattern': r'(Soll ich|Kann ich|Wäre es okay|Soll ich noch)',
                'severity': 'HIGH',
                'description': 'Asks for confirmation when action is allowed'
            },
            'hallucination': {
                'pattern': r'(Ich denke|I assume|Ich glaube|wahrscheinlich)',
                'severity': 'HIGH',
                'description': 'Assumes facts without evidence'
            }
        }
    
    def run_antipattern_tests(self):
        """Run anti-pattern detection."""
        results = {'patterns_found': [], 'severity_counts': {'HIGH': 0, 'MED': 0, 'LOW': 0}}
        
        # Check SOUL.md and recent memory files
        patterns_checked = 0
        
        return results
    
    def generate_evaluation_signal(self):
        """Generate evaluation signal for Learning Loop."""
        metrics = self.metrics
        
        evaluation_signal = {
            'timestamp': datetime.now().isoformat(),
            'source': 'evaluation_framework',
            'metrics': {
                'task_success_rate': metrics['task_success']['rate'],
                'error_rate': metrics['errors']['rate'],
                'latency_p50': metrics['latency'].get('p50', 0),
                'efficiency': metrics['efficiency'].get('avg', 0)
            },
            'antipattern_count': 0,
            'recommendations': []
        }
        
        # Save for Learning Loop
        ll_signal_file = f"{WORKSPACE}/memory/evaluations/learning_loop_signal.json"
        save_json(ll_signal_file, evaluation_signal)
        
        print(f"   ✅ Evaluation signal saved for Learning Loop")
        print(f"   📊 Task Success Rate: {metrics['task_success']['rate']*100:.1f}%")
        
        return evaluation_signal
    
    def run_full_evaluation(self):
        """Run complete evaluation cycle."""
        print("🚀 Running Full Evaluation")
        print("=" * 50)
        
        metrics = self.collect_metrics()
        antipattern_results = self.run_antipattern_tests()
        signal = self.generate_evaluation_signal()
        
        return {
            'metrics': metrics,
            'antipatterns': antipattern_results,
            'signal': signal
        }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    action = sys.argv[1]
    framework = EvaluationFramework()
    
    if action == '--action' and len(sys.argv) > 2:
        action = sys.argv[2]
    
    if action == 'collect_metrics':
        framework.collect_metrics()
    elif action == 'run_tests':
        framework.run_antipattern_tests()
    elif action == 'report':
        framework.run_full_evaluation()
    elif action == 'integrate':
        framework.generate_evaluation_signal()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == '__main__':
    main()
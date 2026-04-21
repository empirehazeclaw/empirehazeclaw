#!/usr/bin/env python3
"""
Task Failure Analyzer
====================
Analyzes why tasks fail and feeds insights to Learning Loop.

Usage:
    python3 task_failure_analyzer.py --analyze
    python3 task_failure_analyzer.py --report
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
ORCHESTRATOR_STATE = WORKSPACE / 'memory/evaluations/orchestrator_state.json'
FAILURE_LOG = WORKSPACE / 'memory/evaluations/failure_analysis.json'
LEARNING_LOOP_SIGNAL = WORKSPACE / 'memory/evaluations/learning_loop_signal.json'


class TaskFailureAnalyzer:
    def __init__(self):
        self.state = self.load_state()
        self.failures = self.load_failures()
    
    def load_state(self):
        if ORCHESTRATOR_STATE.exists():
            with open(ORCHESTRATOR_STATE, 'r') as f:
                return json.load(f)
        return {}
    
    def load_failures(self):
        if FAILURE_LOG.exists():
            with open(FAILURE_LOG, 'r') as f:
                return json.load(f)
        return {'analyses': [], 'patterns': {}, 'total_failures': 0}
    
    def save_failures(self):
        with open(FAILURE_LOG, 'w') as f:
            json.dump(self.failures, f, indent=2)
    
    def analyze_failed_tasks(self):
        """Analyze recent failed tasks."""
        failed_tasks = self.state.get('failed_tasks', [])
        
        if not failed_tasks:
            print("No failed tasks to analyze")
            return
        
        print(f"Analyzing {len(failed_tasks)} failed tasks...")
        
        patterns = defaultdict(list)
        
        for task in failed_tasks:
            task_type = task.get('type', 'unknown')
            error = task.get('error', 'unknown')
            agent = task.get('delegated_to', 'unknown')
            
            key = f"{task_type}_{error}"
            patterns[key].append({
                'task_id': task.get('task_id'),
                'agent': agent,
                'timestamp': task.get('failed_at'),
            })
        
        # Find top patterns
        top_patterns = sorted(patterns.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        print("\nTop Failure Patterns:")
        for pattern, occurrences in top_patterns:
            print(f"  {pattern}: {len(occurrences)} occurrences")
        
        # Update failure log
        self.failures['analyses'].append({
            'timestamp': datetime.now().isoformat(),
            'total_failures': len(failed_tasks),
            'patterns_found': len(patterns),
            'top_patterns': [{'pattern': p, 'count': len(o)} for p, o in top_patterns]
        })
        self.failures['total_failures'] += len(failed_tasks)
        
        # Save
        self.save_failures()
        
        return top_patterns
    
    def generate_learning_signal(self):
        """Generate learning signal from failure patterns."""
        if not self.failures['analyses']:
            return None
        
        last_analysis = self.failures['analyses'][-1]
        
        if last_analysis['total_failures'] == 0:
            return None
        
        learnings = []
        
        for pattern_info in last_analysis.get('top_patterns', []):
            pattern = pattern_info['pattern']
            count = pattern_info['count']
            
            if count >= 2:
                # Parse pattern
                parts = pattern.rsplit('_', 1)
                task_type = parts[0] if parts else 'unknown'
                error = parts[1] if len(parts) > 1 else 'unknown'
                
                learnings.append({
                    'type': 'task_failure_pattern',
                    'task_type': task_type,
                    'error': error,
                    'count': count,
                    'priority': 'HIGH' if count >= 3 else 'MED',
                    'timestamp': datetime.now().isoformat(),
                    'recommendation': f'Fix {task_type} task failures ({count}x): check agent implementation'
                })
        
        if learnings:
            # Update learning loop signal
            signal = {
                'timestamp': datetime.now().isoformat(),
                'learnings': learnings,
                'source': 'task_failure_analyzer'
            }
            
            with open(LEARNING_LOOP_SIGNAL, 'w') as f:
                json.dump(signal, f, indent=2)
            
            print(f"\nGenerated {len(learnings)} learning signals")
        
        return learnings
    
    def run_analysis(self):
        """Run full failure analysis."""
        print("🔍 Task Failure Analyzer")
        print("=" * 50)
        
        # Analyze
        self.analyze_failed_tasks()
        
        # Generate learning signal
        learnings = self.generate_learning_signal()
        
        if learnings:
            print("\n📚 Insights for Learning Loop:")
            for l in learnings:
                print(f"  [{l['priority']}] {l['type']}: {l['task_type']} task ({l['count']} failures)")
        
        return learnings


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Task Failure Analyzer')
    parser.add_argument('--analyze', action='store_true', help='Analyze failures')
    parser.add_argument('--report', action='store_true', help='Show report')
    
    args = parser.parse_args()
    
    analyzer = TaskFailureAnalyzer()
    
    if args.analyze or args.report:
        analyzer.run_analysis()
    else:
        parser.print_help()
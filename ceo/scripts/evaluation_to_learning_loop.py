#!/usr/bin/env python3
"""
Evaluation → Learning Loop Integration
=====================================
Takes evaluation framework results and feeds them into the Learning Loop.

Usage:
    python3 evaluation_to_learning_loop.py --action sync
    python3 evaluation_to_learning_loop.py --action status
"""

import json
import os
import sys
from datetime import datetime

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
LEARNING_SIGNAL_FILE = f"{EVAL_DIR}/learning_loop_signal.json"


class EvaluationToLearningLoop:
    def __init__(self):
        self.evaluation_file = f"{EVAL_DIR}/lnew_metrics.json"
        self.antipattern_file = f"{EVAL_DIR}/antipattern_tests.json"
        self.memory_analysis = f"{EVAL_DIR}/memory_analysis.json"
    
    def load_evaluation_data(self):
        """Load all evaluation data."""
        data = {}
        
        if os.path.exists(self.evaluation_file):
            with open(self.evaluation_file, 'r') as f:
                data['metrics'] = json.load(f)
        
        if os.path.exists(self.antipattern_file):
            with open(self.antipattern_file, 'r') as f:
                data['antipatterns'] = json.load(f)
        
        if os.path.exists(self.memory_analysis):
            with open(self.memory_analysis, 'r') as f:
                data['memory'] = json.load(f)
        
        return data
    
    def create_learning_signal(self):
        """Create a learning signal from evaluation data."""
        data = self.load_evaluation_data()
        
        signal = {
            'timestamp': datetime.now().isoformat(),
            'source': 'evaluation_framework',
            'type': 'evaluation_feedback',
            'data': {}
        }
        
        # Extract key metrics
        if 'metrics' in data:
            m = data['metrics']
            signal['data']['task_success_rate'] = m.get('task_success', {}).get('rate', 0.763)
            signal['data']['error_rate'] = m.get('errors', {}).get('rate', 0.03)
            signal['data']['latency_p50'] = m.get('latency', {}).get('p50', 1.0)
            signal['data']['efficiency'] = m.get('efficiency', {}).get('avg', 186)
        
        # Extract antipattern findings
        if 'antipatterns' in data:
            ap = data['antipatterns']
            signal['data']['antipattern_count'] = ap.get('severity_counts', {}).get('HIGH', 0)
            signal['data']['antipattern_issues'] = ap.get('patterns_found', [])
        
        # Extract memory health
        if 'memory' in data:
            mem = data['memory']
            signal['data']['memory_files'] = mem.get('files_scanned', 0)
            signal['data']['memory_clean'] = len(mem.get('recommendations', [])) == 0
        
        # Generate learnings/recommendations
        signal['learnings'] = self.generate_learnings(signal['data'])
        
        return signal
    
    def generate_learnings(self, data):
        """Generate learning entries from evaluation data."""
        learnings = []
        
        # Task success rate
        tsr = data.get('task_success_rate', 0)
        if tsr < 0.8:
            learnings.append({
                'type': 'performance_gap',
                'priority': 'HIGH',
                'observation': f'Task success rate is {tsr*100:.1f}% (target: 80%+)',
                'action': 'Focus on improving task completion rate'
            })
        
        # Error rate
        er = data.get('error_rate', 0)
        if er > 0.05:
            learnings.append({
                'type': 'error_pattern',
                'priority': 'HIGH',
                'observation': f'Error rate is {er*100:.1f}% (target: <5%)',
                'action': 'Implement better error handling'
            })
        
        # Efficiency
        eff = data.get('efficiency', 0)
        if eff > 300:
            learnings.append({
                'type': 'efficiency',
                'priority': 'MED',
                'observation': f'Tokens per task: {eff:.0f} (high)',
                'action': 'Reduce token usage per task'
            })
        
        # Anti-patterns
        ap_count = data.get('antipattern_count', 0)
        if ap_count > 0:
            learnings.append({
                'type': 'anti_pattern',
                'priority': 'HIGH',
                'observation': f'{ap_count} HIGH severity anti-patterns detected',
                'action': 'Review and fix anti-patterns in prompts'
            })
        
        # Memory health
        if data.get('memory_clean', False):
            learnings.append({
                'type': 'system_health',
                'priority': 'LOW',
                'observation': 'Memory is clean, no duplicates or stale facts',
                'action': 'Continue current maintenance routine'
            })
        
        return learnings
    
    def sync_to_learning_loop(self):
        """Sync evaluation data to Learning Loop signal file."""
        print("🔄 Syncing Evaluation → Learning Loop")
        print("=" * 50)
        
        signal = self.create_learning_signal()
        
        # Save to signal file
        with open(LEARNING_SIGNAL_FILE, 'w') as f:
            json.dump(signal, f, indent=2)
        
        print(f"\n📊 Evaluation Summary:")
        data = signal['data']
        print(f"   Task Success Rate: {data.get('task_success_rate', 0)*100:.1f}%")
        print(f"   Error Rate: {data.get('error_rate', 0)*100:.1f}%")
        print(f"   Latency p50: {data.get('latency_p50', 0):.2f}s")
        print(f"   Efficiency: {data.get('efficiency', 0):.0f} tokens/task")
        print(f"   Anti-Pattern Count (HIGH): {data.get('antipattern_count', 0)}")
        print(f"   Memory Files: {data.get('memory_files', 0)}")
        print(f"   Memory Clean: {data.get('memory_clean', False)}")
        
        print(f"\n💡 Generated Learnings ({len(signal['learnings'])}):")
        for l in signal['learnings']:
            print(f"   [{l['priority']}] {l['observation']}")
        
        print(f"\n💾 Signal saved to: {LEARNING_SIGNAL_FILE}")
        
        # Also create KG update suggestion
        kg_update = {
            'type': 'evaluation_metrics',
            'timestamp': signal['timestamp'],
            'task_success_rate': data.get('task_success_rate', 0),
            'error_rate': data.get('error_rate', 0),
            'learning_count': len(signal['learnings'])
        }
        
        kg_file = f"{WORKSPACE}/memory/short_term/evaluation_for_kg.json"
        with open(kg_file, 'w') as f:
            json.dump(kg_update, f, indent=2)
        
        print(f"📊 KG update saved to: {kg_file}")
        
        return signal
    
    def run(self, action='sync'):
        """Run requested action."""
        if action == 'sync':
            return self.sync_to_learning_loop()
        elif action == 'status':
            data = self.load_evaluation_data()
            print(f"📊 Evaluation Data Available:")
            print(f"   Metrics: {'✅' if 'metrics' in data else '❌'}")
            print(f"   Antipatterns: {'✅' if 'antipatterns' in data else '❌'}")
            print(f"   Memory: {'✅' if 'memory' in data else '❌'}")
            return data
        else:
            print(f"Unknown action: {action}")
            return None


def main():
    integrator = EvaluationToLearningLoop()
    
    action = 'sync'
    args = sys.argv[1:]
    if '--action' in args:
        idx = args.index('--action')
        if idx + 1 < len(args):
            action = args[idx + 1]
    
    integrator.run(action)


if __name__ == '__main__':
    main()

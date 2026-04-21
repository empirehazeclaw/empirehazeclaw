#!/usr/bin/env python3
"""
Evaluation Improver
===================
Improves task success rate tracking and generates actionable insights.

Features:
- Tracks TSR (Task Success Rate) over time
- Detects failure patterns by task type
- Generates specific improvement recommendations
- Updates learning_loop_signal.json with new learnings

Usage:
    python3 eval_improver.py --action analyze
    python3 eval_improver.py --action report
    python3 eval_improver.py --action improve
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
EVAL_DIR = WORKSPACE / 'memory/evaluations'
LEARNING_STATE_FILE = EVAL_DIR / 'learning_loop_state.json'
LEARNING_SIGNAL_FILE = EVAL_DIR / 'learning_loop_signal.json'
ORCHESTRATOR_STATE = EVAL_DIR / 'orchestrator_state.json'

# Target thresholds
TARGET_TSR = 0.80  # 80%
TSR_DROP_THRESHOLD = 0.03  # Alert if TSR drops by 3%


class EvalImprover:
    def __init__(self):
        self.state = self.load_state()
        self.orchestrator = self.load_orchestrator()
        
    # ========== STATE MANAGEMENT ==========
    
    def load_state(self) -> Dict:
        """Load learning loop state from file."""
        if LEARNING_STATE_FILE.exists():
            with open(LEARNING_STATE_FILE, 'r') as f:
                return json.load(f)
        return self.init_state()
    
    def init_state(self) -> Dict:
        """Initialize fresh state structure."""
        return {
            'tsr_history': [],  # [{timestamp, rate, sample_size}]
            'task_type_stats': {},  # {task_type: {successes, failures, total}}
            'failure_patterns': {},  # {pattern_key: count}
            'last_updated': datetime.now().isoformat(),
            'tsr_trend': 'stable',  # stable, improving, declining
            'last_improvement': None,
            'recommendations_generated': 0
        }
    
    def save_state(self):
        """Save state to file."""
        self.state['last_updated'] = datetime.now().isoformat()
        with open(LEARNING_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_orchestrator(self) -> Dict:
        """Load orchestrator state for task analysis."""
        if ORCHESTRATOR_STATE.exists():
            with open(ORCHESTRATOR_STATE, 'r') as f:
                return json.load(f)
        return {'completed_tasks': [], 'failed_tasks': []}
    
    # ========== TSR TRACKING ==========
    
    def update_tsr(self, new_tsr: float, sample_size: int = 10) -> Dict:
        """Update TSR history with new measurement."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'rate': new_tsr,
            'sample_size': sample_size
        }
        
        self.state['tsr_history'].append(entry)
        
        # Keep only last 30 entries
        if len(self.state['tsr_history']) > 30:
            self.state['tsr_history'] = self.state['tsr_history'][-30:]
        
        # Calculate trend
        self.calculate_tsr_trend()
        
        self.save_state()
        return entry
    
    def calculate_tsr_trend(self):
        """Calculate TSR trend from history."""
        history = self.state['tsr_history']
        if len(history) < 2:
            self.state['tsr_trend'] = 'stable'
            return
        
        # Compare last 5 vs previous 5
        recent = history[-5:] if len(history) >= 5 else history
        earlier = history[-10:-5] if len(history) >= 10 else history[:len(history)//2]
        
        if not earlier:
            self.state['tsr_trend'] = 'stable'
            return
        
        recent_avg = sum(e['rate'] for e in recent) / len(recent)
        earlier_avg = sum(e['rate'] for e in earlier) / len(earlier)
        
        diff = recent_avg - earlier_avg
        if diff > 0.01:
            self.state['tsr_trend'] = 'improving'
        elif diff < -0.01:
            self.state['tsr_trend'] = 'declining'
        else:
            self.state['tsr_trend'] = 'stable'
    
    def compute_tsr_from_orchestrator(self) -> Optional[float]:
        """Compute TSR directly from orchestrator task data (source of truth)."""
        completed = self.orchestrator.get('completed_tasks', [])
        failed = self.orchestrator.get('failed_tasks', [])
        
        if not completed and not failed:
            return None  # No data yet
        
        success_count = sum(1 for t in completed if t.get('result', {}).get('success', True))
        failure_count = len(failed)
        failure_count += sum(1 for t in completed if not t.get('result', {}).get('success', True))
        total = success_count + failure_count
        
        if total == 0:
            return None
        
        return success_count / total
    
    def get_tsr_stats(self) -> Dict:
        """Get TSR statistics."""
        history = self.state['tsr_history']
        if not history:
            return {'current': 0.763, 'average': 0.763, 'trend': 'stable', 'entries': 0}
        
        current = history[-1]['rate']
        average = sum(e['rate'] for e in history) / len(history)
        
        return {
            'current': current,
            'average': average,
            'min': min(e['rate'] for e in history),
            'max': max(e['rate'] for e in history),
            'trend': self.state['tsr_trend'],
            'entries': len(history),
            'target_gap': TARGET_TSR - current
        }
    
    # ========== TASK TYPE ANALYSIS ==========
    
    def analyze_task_types(self) -> Dict:
        """Analyze success/failure rates by task type."""
        completed = self.orchestrator.get('completed_tasks', [])
        failed = self.orchestrator.get('failed_tasks', [])
        
        # Aggregate by task type
        task_stats = defaultdict(lambda: {'successes': 0, 'failures': 0, 'total': 0})
        
        for task in completed:
            task_type = task.get('type', 'unknown')
            success = task.get('result', {}).get('success', True)
            task_stats[task_type]['total'] += 1
            if success:
                task_stats[task_type]['successes'] += 1
            else:
                task_stats[task_type]['failures'] += 1
        
        for task in failed:
            task_type = task.get('type', 'unknown')
            task_stats[task_type]['total'] += 1
            task_stats[task_type]['failures'] += 1
        
        # Convert to dict and calculate rates
        result = {}
        for task_type, stats in task_stats.items():
            total = stats['total']
            if total > 0:
                rate = stats['successes'] / total
            else:
                rate = 1.0
            result[task_type] = {
                'successes': stats['successes'],
                'failures': stats['failures'],
                'total': total,
                'success_rate': rate
            }
        
        self.state['task_type_stats'] = result
        self.save_state()
        return result
    
    def get_worst_task_types(self, limit: int = 3) -> List[Dict]:
        """Get task types with lowest success rates."""
        task_stats = self.analyze_task_types()
        
        # Filter to types with at least 1 failure and sort by rate
        failing_types = [
            {'type': t, **s} for t, s in task_stats.items() 
            if s['failures'] > 0
        ]
        failing_types.sort(key=lambda x: x['success_rate'])
        
        return failing_types[:limit]
    
    # ========== FAILURE PATTERN DETECTION ==========
    
    def detect_failure_patterns(self) -> Dict:
        """Detect patterns in task failures."""
        failed = self.orchestrator.get('failed_tasks', [])
        
        if not failed:
            return {'patterns': [], 'total_failures': 0}
        
        patterns = defaultdict(lambda: {'count': 0, 'examples': []})
        
        for task in failed:
            task_type = task.get('type', 'unknown')
            error = task.get('error', 'unknown')
            agent = task.get('delegated_to', 'unknown')
            
            # Create pattern key
            pattern_key = f"{task_type}:{error}"
            patterns[pattern_key]['count'] += 1
            patterns[pattern_key]['task_type'] = task_type
            patterns[pattern_key]['error'] = error
            patterns[pattern_key]['agent'] = agent
            
            if len(patterns[pattern_key]['examples']) < 2:
                patterns[pattern_key]['examples'].append(task.get('task_id'))
        
        # Convert to list sorted by count
        pattern_list = sorted(
            [{'pattern': k, **v} for k, v in patterns.items()],
            key=lambda x: x['count'],
            reverse=True
        )
        
        self.state['failure_patterns'] = {p['pattern']: p['count'] for p in pattern_list}
        self.save_state()
        
        return {'patterns': pattern_list, 'total_failures': len(failed)}
    
    # ========== RECOMMENDATIONS ==========
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate specific improvement recommendations."""
        recommendations = []
        tsr_stats = self.get_tsr_stats()
        worst_types = self.get_worst_task_types()
        failure_data = self.detect_failure_patterns()
        
        # 1. TSR-based recommendations
        current_tsr = tsr_stats['current']
        if current_tsr < TARGET_TSR:
            gap = TARGET_TSR - current_tsr
            recommendations.append({
                'priority': 'HIGH',
                'category': 'tsr',
                'issue': f'Task Success Rate is {current_tsr*100:.1f}% (target: {TARGET_TSR*100:.0f}%)',
                'recommendation': f'Need {gap*100:.1f}% improvement to reach target',
                'action': 'Focus on completing tasks fully before reporting success'
            })
        
        # 2. TSR trend recommendations
        if tsr_stats['trend'] == 'declining':
            recommendations.append({
                'priority': 'HIGH',
                'category': 'tsr_trend',
                'issue': 'TSR is declining over recent measurements',
                'recommendation': 'Investigate recent changes that may have caused regression',
                'action': 'Review recent code/prompt changes for correlation'
            })
        
        # 3. Task type recommendations
        for wt in worst_types:
            if wt['success_rate'] < 0.7:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'task_type',
                    'issue': f"Task type '{wt['type']}' has {wt['success_rate']*100:.0f}% success rate",
                    'recommendation': f"Improve {wt['type']} task handling",
                    'action': f"Check {wt.get('agent', 'agent')} implementation for {wt['type']} tasks"
                })
        
        # 4. Failure pattern recommendations
        for fp in failure_data['patterns'][:3]:  # Top 3
            if fp['count'] >= 2:
                recommendations.append({
                    'priority': 'HIGH' if fp['count'] >= 3 else 'MED',
                    'category': 'failure_pattern',
                    'issue': f"Pattern '{fp['pattern']}' occurred {fp['count']} times",
                    'recommendation': f"Fix recurring {fp['task_type']} task failures",
                    'action': f"Review error handling for {fp['error']} in {fp['agent']}"
                })
        
        # 5. Antipattern check
        antipattern_file = EVAL_DIR / 'antipattern_tests.json'
        if antipattern_file.exists():
            with open(antipattern_file, 'r') as f:
                ap_data = json.load(f)
            
            high_count = ap_data.get('severity_counts', {}).get('HIGH', 0)
            if high_count > 0:
                recommendations.append({
                    'priority': 'MED',
                    'category': 'anti_patterns',
                    'issue': f'{high_count} HIGH severity anti-patterns detected',
                    'recommendation': 'Fix anti-patterns in SOUL.md and AGENTS.md',
                    'action': 'Review and remove filler words, over-confirmations, etc.'
                })
        
        return recommendations
    
    # ========== SIGNAL UPDATE ==========
    
    def update_learning_signal(self, recommendations: List[Dict]) -> Dict:
        """Update learning_loop_signal.json with new learnings."""
        signal = {
            'timestamp': datetime.now().isoformat(),
            'source': 'eval_improver',
            'type': 'evaluation_improvement',
            'tsr_stats': self.get_tsr_stats(),
            'task_type_analysis': self.get_worst_task_types(3),
            'failure_patterns': self.detect_failure_patterns()['patterns'][:5],
            'recommendations': recommendations,
            'state_file': str(LEARNING_STATE_FILE)
        }
        
        with open(LEARNING_SIGNAL_FILE, 'w') as f:
            json.dump(signal, f, indent=2)
        
        self.state['recommendations_generated'] += len(recommendations)
        self.save_state()
        
        return signal
    
    # ========== MAIN ACTIONS ==========
    
    def analyze(self) -> Dict:
        """Run full analysis."""
        print("📊 Eval Improver — Analysis")
        print("=" * 50)
        
        # Update TSR - compute directly from orchestrator data (source of truth)
        current_tsr = self.compute_tsr_from_orchestrator()
        
        # Fallback to metrics file if orchestrator has no data
        if current_tsr is None:
            metrics_file = EVAL_DIR / 'lnew_metrics.json'
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                    current_tsr = metrics.get('task_success', {}).get('rate', 0.763)
            else:
                current_tsr = 0.763
        
        self.update_tsr(current_tsr, sample_size=10)
        
        # Analyze
        tsr_stats = self.get_tsr_stats()
        task_types = self.analyze_task_types()
        worst_types = self.get_worst_task_types()
        failure_data = self.detect_failure_patterns()
        recommendations = self.generate_recommendations()
        
        # Print summary
        print(f"\n📈 TSR Stats:")
        print(f"   Current: {tsr_stats['current']*100:.1f}%")
        print(f"   Average: {tsr_stats['average']*100:.1f}%")
        print(f"   Trend: {tsr_stats['trend']}")
        print(f"   Gap to target: {tsr_stats['target_gap']*100:.1f}%")
        
        if worst_types:
            print(f"\n⚠️ Worst Task Types:")
            for wt in worst_types:
                print(f"   {wt['type']}: {wt['success_rate']*100:.0f}% ({wt['failures']} failures)")
        
        if failure_data['patterns']:
            print(f"\n🔴 Failure Patterns:")
            for fp in failure_data['patterns'][:3]:
                print(f"   {fp['pattern']}: {fp['count']}x")
        
        return {
            'tsr_stats': tsr_stats,
            'task_types': task_types,
            'worst_types': worst_types,
            'failure_patterns': failure_data,
            'recommendations': recommendations
        }
    
    def improve(self) -> Dict:
        """Analyze and update learning signal."""
        print("🚀 Eval Improver — Improve")
        print("=" * 50)
        
        results = self.analyze()
        recommendations = results['recommendations']
        
        # Update signal
        signal = self.update_learning_signal(recommendations)
        
        print(f"\n💡 Generated {len(recommendations)} Recommendations:")
        for r in recommendations:
            print(f"   [{r['priority']}] {r['issue']}")
            print(f"      → {r['action']}")
        
        print(f"\n💾 Signal updated: {LEARNING_SIGNAL_FILE}")
        
        return signal
    
    def report(self) -> Dict:
        """Generate status report."""
        print("📊 Eval Improver — Report")
        print("=" * 50)
        
        # Reload fresh metrics before reporting
        metrics_file = EVAL_DIR / 'lnew_metrics.json'
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                fresh_tsr = metrics.get('task_success', {}).get('rate', 0.763)
                self.update_tsr(fresh_tsr, sample_size=10)
        
        tsr_stats = self.get_tsr_stats()
        recommendations = self.generate_recommendations()
        
        print(f"\n📈 TSR: {tsr_stats['current']*100:.1f}% ({tsr_stats['trend']})")
        print(f"   Target gap: {tsr_stats['target_gap']*100:.1f}%")
        print(f"   History entries: {tsr_stats['entries']}")
        
        print(f"\n💡 Recommendations: {len(recommendations)}")
        for r in recommendations[:5]:
            print(f"   [{r['priority']}] {r['category']}: {r['issue'][:50]}...")
        
        return {'tsr_stats': tsr_stats, 'recommendations': recommendations}
    
    def run(self, action: str = 'report'):
        """Run requested action."""
        if action == 'analyze':
            return self.analyze()
        elif action == 'improve':
            return self.improve()
        elif action == 'report':
            return self.report()
        else:
            print(f"Unknown action: {action}")
            return None


def main():
    improver = EvalImprover()
    
    action = 'report'
    args = sys.argv[1:]
    if '--action' in args:
        idx = args.index('--action')
        if idx + 1 < len(args):
            action = args[idx + 1]
    
    result = improver.run(action)
    
    if action == 'report':
        print("\n✅ Report complete")


if __name__ == '__main__':
    main()

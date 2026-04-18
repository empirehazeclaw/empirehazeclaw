#!/usr/bin/env python3
"""
meta_feedback_bridge.py — Phase 3: Meta-Feedback Bridge
========================================================
Schließt den Loop: Outcome → Algorithmus-Änderung.
Analysiert welche Patterns sich bewährt haben und passt an.

Usage:
    python3 meta_feedback_bridge.py              # Run feedback cycle
    python3 meta_feedback_bridge.py --status      # Show feedback state
    python3 meta_feedback_bridge.py --history    # Show adjustment history
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
TASK_LOG = WORKSPACE / 'memory/task_log/unified_tasks.json'
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'
FEEDBACK_FILE = WORKSPACE / 'memory/meta_learning/meta_feedback.json'


class MetaFeedbackBridge:
    """Bridges task outcomes to algorithm changes."""
    
    def __init__(self):
        self.tasks = []
        self.patterns = []
        self.feedback_log = []
        self.load_data()
    
    def load_data(self):
        """Load required data."""
        # Load tasks
        if TASK_LOG.exists():
            with open(TASK_LOG, 'r') as f:
                data = json.load(f)
            self.tasks = data.get('tasks', [])
        
        # Load patterns
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
            self.patterns = data.get('patterns', [])
        
        # Load feedback log
        if FEEDBACK_FILE.exists():
            with open(FEEDBACK_FILE, 'r') as f:
                self.feedback_log = json.load(f).get('feedback', [])
        
        print(f"📂 Loaded: {len(self.tasks)} tasks, {len(self.patterns)} patterns")
    
    def analyze_outcomes(self):
        """Analyze recent task outcomes."""
        print("\n🔍 Analyzing Task Outcomes")
        print("=" * 50)
        
        # Group by outcome
        success_tasks = [t for t in self.tasks if t.get('outcome') == 'success']
        failed_tasks = [t for t in self.tasks if t.get('outcome') != 'success']
        
        print(f"   Total tasks: {len(self.tasks)}")
        print(f"   Success: {len(success_tasks)} ({len(success_tasks)/len(self.tasks)*100:.1f}%)")
        print(f"   Failed: {len(failed_tasks)} ({len(failed_tasks)/len(self.tasks)*100:.1f}%)")
        
        # Analyze failure patterns
        if failed_tasks:
            print(f"\n⚠️ Failed task analysis:")
            failure_types = {}
            for task in failed_tasks:
                err = task.get('metadata', {}).get('error', 'unknown')
                failure_types[err] = failure_types.get(err, 0) + 1
            
            for err, count in sorted(failure_types.items(), key=lambda x: -x[1])[:5]:
                print(f"   {err}: {count}x")
        
        return {
            'total': len(self.tasks),
            'success': len(success_tasks),
            'failed': len(failed_tasks),
            'success_rate': len(success_tasks) / len(self.tasks) if self.tasks else 0
        }
    
    def identify_pattern_effectiveness(self):
        """Identify which patterns are most effective."""
        print("\n📊 Pattern Effectiveness Analysis")
        print("=" * 50)
        
        pattern_stats = []
        
        for pattern in self.patterns:
            trigger = pattern.get('trigger', {})
            pattern_id = pattern.get('pattern_id')
            
            # Find matching tasks
            matching = []
            for task in self.tasks:
                match = True
                for key, value in trigger.items():
                    if key == 'subtype':
                        if task.get('subtype', '') != value:
                            match = False
                    elif key == 'delegated_to':
                        if task.get('metadata', {}).get('delegated_to') != value:
                            match = False
                    elif key == 'duration_bucket':
                        dur = task.get('metadata', {}).get('duration_ms', 0) or 0
                        if value == 'fast' and dur >= 60000:
                            match = False
                        elif value == 'medium' and (dur < 60000 or dur >= 300000):
                            match = False
                        elif value == 'slow' and dur < 300000:
                            match = False
                
                if match:
                    matching.append(task)
            
            # Calculate effectiveness
            if matching:
                success_count = sum(1 for t in matching if t.get('outcome') == 'success')
                success_rate = success_count / len(matching)
            else:
                success_rate = 1.0
                success_count = 0
            
            pattern_stats.append({
                'pattern_id': pattern_id,
                'description': pattern.get('description', '')[:50],
                'matching_tasks': len(matching),
                'success_count': success_count,
                'observed_rate': success_rate,
                'expected_rate': pattern.get('success_rate', 1.0),
                'delta': success_rate - pattern.get('success_rate', 1.0)
            })
        
        # Sort by delta
        pattern_stats.sort(key=lambda x: x['delta'])
        
        print("\n📋 Pattern Performance:")
        for p in pattern_stats:
            delta = p['delta']
            symbol = '📈' if delta > 0 else '📉' if delta < 0 else '➡️'
            print(f"   {symbol} {p['pattern_id']}: obs={p['observed_rate']:.1%} exp={p['expected_rate']:.1%} ({p['matching_tasks']} tasks)")
        
        # Best and worst
        if pattern_stats:
            worst = pattern_stats[0]
            best = pattern_stats[-1]
            print(f"\n   Worst: {worst['pattern_id']} (delta={worst['delta']:.1%})")
            print(f"   Best: {best['pattern_id']} (delta={best['delta']:.1%})")
        
        return pattern_stats
    
    def apply_feedback(self, pattern_stats):
        """Apply feedback to patterns and learning system."""
        print("\n⚙️ Applying Feedback Adjustments")
        print("=" * 50)
        
        adjustments = []
        
        for stat in pattern_stats:
            if abs(stat['delta']) > 0.05:  # Significant delta
                # Update pattern success rate
                for p in self.patterns:
                    if p['pattern_id'] == stat['pattern_id']:
                        # Blend observed and expected
                        new_rate = p.get('success_rate', 1.0) * 0.5 + stat['observed_rate'] * 0.5
                        p['success_rate'] = new_rate
                        
                adjustments.append({
                    'pattern_id': stat['pattern_id'],
                    'old_expected': stat['expected_rate'],
                    'new_expected': stat['observed_rate'],
                    'delta': stat['delta']
                })
        
        # Save updated patterns
        with open(PATTERNS_FILE, 'w') as f:
            json.dump({
                'patterns': self.patterns,
                'generated_at': datetime.now().isoformat()
            }, f, indent=2)
        
        # Log feedback
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'adjustments_count': len(adjustments),
            'adjustments': adjustments
        }
        self.feedback_log.append(feedback_entry)
        
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump({
                'feedback': self.feedback_log[-100:],  # Keep last 100
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"   Adjusted {len(adjustments)} patterns")
        
        return adjustments
    
    def run_feedback_cycle(self):
        """Run complete feedback cycle."""
        print("🔄 Meta Feedback Bridge — Phase 3")
        print("=" * 50)
        print(f"Started: {datetime.now().isoformat()}")
        
        # Analyze outcomes
        outcomes = self.analyze_outcomes()
        
        # Identify pattern effectiveness
        pattern_stats = self.identify_pattern_effectiveness()
        
        # Apply feedback
        adjustments = self.apply_feedback(pattern_stats)
        
        print(f"\n✅ Feedback Cycle Complete")
        print(f"   Tasks analyzed: {outcomes['total']}")
        print(f"   Success rate: {outcomes['success_rate']:.1%}")
        print(f"   Patterns adjusted: {len(adjustments)}")
        
        return {
            'outcomes': outcomes,
            'adjustments': adjustments,
            'pattern_stats': pattern_stats
        }
    
    def status(self):
        """Show feedback bridge status."""
        print("📊 Meta Feedback Bridge Status")
        print("=" * 50)
        print(f"Tasks analyzed: {len(self.tasks)}")
        print(f"Patterns tracked: {len(self.patterns)}")
        print(f"Feedback entries: {len(self.feedback_log)}")
        
        if self.feedback_log:
            last = self.feedback_log[-1]
            print(f"Last feedback: {last.get('timestamp')}")
            print(f"Adjustments: {last.get('adjustments_count')}")
    
    def history(self):
        """Show feedback history."""
        print("\n📜 Feedback History")
        print("=" * 50)
        
        for i, entry in enumerate(self.feedback_log[-10:]):
            print(f"\n{i+1}. {entry.get('timestamp')}")
            print(f"   Adjustments: {entry.get('adjustments_count')}")
            for adj in entry.get('adjustments', [])[:3]:
                print(f"      {adj['pattern_id']}: {adj['old_expected']:.1%} → {adj['new_expected']:.1%}")


def main():
    bridge = MetaFeedbackBridge()
    
    if '--status' in sys.argv:
        bridge.status()
    elif '--history' in sys.argv:
        bridge.history()
    else:
        bridge.run_feedback_cycle()


if __name__ == '__main__':
    main()
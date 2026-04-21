#!/usr/bin/env python3
"""
meta_learning_controller.py — Phase 3: Meta-Learning Loop Integration
=======================================================================
Steuert den Meta-Learning Zyklus: Meta-Training + Meta-Testing.

Usage:
    python3 meta_learning_controller.py              # Run full cycle
    python3 meta_learning_controller.py --status      # Show status
    python3 meta_learning_controller.py --test       # Run meta-testing
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
PARENT_WORKSPACE = Path('/home/clawbot/.openclaw/workspace')
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'
TASK_LOG = WORKSPACE / 'memory/task_log/unified_tasks.json'
LEARNING_SIGNAL = WORKSPACE / 'memory/evaluations/learning_loop_signal.json'
OUTPUT_DIR = WORKSPACE / 'memory/meta_learning'
EVENT_BUS = PARENT_WORKSPACE / 'SCRIPTS/automation/event_bus.py'

# Learnings Service
sys.path.insert(0, str(PARENT_WORKSPACE / 'SCRIPTS/automation'))
try:
    from learnings_service import LearningsService
except:
    LearningsService = None  # Fallback if not available


class MetaLearningController:
    """Orchestrates meta-learning cycles."""
    
    def __init__(self):
        self.patterns = []
        self.tasks = []
        self.signal = {}
        self.learnings = LearningsService() if LearningsService else None
        self.load_data()
    
    def get_learning_context(self) -> dict:
        """Get learnings relevant for Meta Learning decisions."""
        if not self.learnings:
            return {"learnings": [], "strategy_insights": {}}
        
        # Get learnings for meta learning
        context = self.learnings.get_context_for_task("pattern_matching")
        
        # Record that we're using these learnings
        for l in context.get("learnings", []):
            self.learnings.mark_learning_used(l["id"])
        
        return context
    
    def record_meta_learning(self, pattern: dict, outcome: str):
        """Record a meta learning result."""
        if not self.learnings:
            return
        
        self.learnings.record_learning(
            source="Meta Learning",
            category="pattern",
            learning=f"Pattern {pattern.get('trigger')} -> {outcome}",
            context="pattern_matching",
            outcome=outcome
        )
    
    def load_data(self):
        """Load required data."""
        # Load patterns
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
            self.patterns = data.get('patterns', [])
        
        # Load tasks
        if TASK_LOG.exists():
            with open(TASK_LOG, 'r') as f:
                data = json.load(f)
            self.tasks = data.get('tasks', [])
        
        # Load signal
        if LEARNING_SIGNAL.exists():
            with open(LEARNING_SIGNAL, 'r') as f:
                self.signal = json.load(f)
        
        print(f"📂 Loaded: {len(self.patterns)} patterns, {len(self.tasks)} tasks")
    
    def meta_training(self):
        """Generate meta_patterns from task history."""
        print("\n📊 Meta-Training: Learning from Task History")
        print("=" * 50)
        
        # Analyze pattern performance
        pattern_performance = []
        
        for pattern in self.patterns:
            trigger = pattern.get('trigger', {})
            matching_count = 0
            success_count = 0
            
            for task in self.tasks:
                task_subtype = task.get('subtype', '')
                task_type = task.get('type', '')
                delegated_to = task.get('metadata', {}).get('delegated_to')
                
                match = True
                for key, value in trigger.items():
                    if key == 'subtype' and task_subtype != value:
                        match = False
                    elif key == 'delegated_to' and delegated_to != value:
                        match = False
                    elif key == 'duration_bucket':
                        # Check duration
                        dur = task.get('metadata', {}).get('duration_ms', 0) or 0
                        if value == 'fast' and dur >= 60000:
                            match = False
                        elif value == 'medium' and (dur < 60000 or dur >= 300000):
                            match = False
                        elif value == 'slow' and dur < 300000:
                            match = False
                
                if match:
                    matching_count += 1
                    if task.get('outcome') == 'success':
                        success_count += 1
            
            if matching_count > 0:
                observed_success_rate = success_count / matching_count
            else:
                observed_success_rate = 1.0  # Default if no data
            
            pattern_performance.append({
                'pattern_id': pattern.get('pattern_id'),
                'observed_success_rate': observed_success_rate,
                'matching_tasks': matching_count,
                'expected_success_rate': pattern.get('success_rate', 1.0),
                'generalization': pattern.get('generalization_score', 0)
            })
        
        # Sort by performance delta
        pattern_performance.sort(key=lambda x: x['observed_success_rate'] - x['expected_success_rate'])
        
        print("\n📋 Pattern Performance Analysis:")
        for p in pattern_performance[:5]:
            delta = p['observed_success_rate'] - p['expected_success_rate']
            status = '📈' if delta > 0 else '📉' if delta < 0 else '➡️'
            print(f"   {status} {p['pattern_id']}: observed={p['observed_success_rate']:.1%} expected={p['expected_success_rate']:.1%} delta={delta:+.1%}")
        
        return pattern_performance
    
    def meta_testing(self):
        """Test patterns on recent tasks."""
        print("\n🧪 Meta-Testing: Evaluating Patterns on Recent Tasks")
        print("=" * 50)
        
        # Get recent tasks (last 20)
        recent_tasks = self.tasks[-20:]
        if not recent_tasks:
            print("❌ No recent tasks for testing")
            return []
        
        test_results = []
        
        for task in recent_tasks:
            task_id = task.get('task_id')
            subtype = task.get('subtype', '')
            delegated_to = task.get('metadata', {}).get('delegated_to')
            
            # Find matching patterns
            matches = []
            for pattern in self.patterns:
                trigger = pattern.get('trigger', {})
                match = False
                
                for key, value in trigger.items():
                    if key == 'subtype' and subtype == value:
                        match = True
                    elif key == 'delegated_to' and delegated_to == value:
                        match = True
                
                if match:
                    matches.append(pattern)
            
            # Calculate prediction
            if matches:
                avg_confidence = sum(p.get('success_rate', 1.0) for p in matches) / len(matches)
                predicted = 'success'
            else:
                avg_confidence = 0.5
                predicted = 'unknown'
            
            actual = task.get('outcome', 'unknown')
            correct = (predicted == actual) or (predicted == 'unknown')
            
            test_results.append({
                'task_id': task_id,
                'predicted': predicted,
                'actual': actual,
                'correct': correct,
                'confidence': avg_confidence,
                'matches': len(matches)
            })
        
        # Calculate accuracy
        correct_count = sum(1 for r in test_results if r['correct'])
        accuracy = correct_count / len(test_results) if test_results else 0
        
        print(f"\n📊 Test Results on {len(test_results)} recent tasks:")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   Correct: {correct_count}/{len(test_results)}")
        
        # Confidence calibration
        high_conf = [r for r in test_results if r['confidence'] >= 0.9]
        high_conf_correct = sum(1 for r in high_conf if r['correct'])
        if high_conf:
            high_conf_acc = high_conf_correct / len(high_conf)
            print(f"   High Confidence Accuracy: {high_conf_acc:.1%} ({len(high_conf)} tasks)")
        
        return test_results
    
    def adjust_pattern_weights(self, performance_data):
        """Adjust pattern weights based on performance."""
        print("\n⚙️ Adjusting Pattern Weights")
        print("=" * 50)
        
        adjustments = []
        
        for perf in performance_data:
            delta = perf['observed_success_rate'] - perf['expected_success_rate']
            
            if abs(delta) > 0.05:  # Only adjust if significant
                adjustment = {
                    'pattern_id': perf['pattern_id'],
                    'delta': delta,
                    'action': 'increase_weight' if delta > 0 else 'decrease_weight',
                    'reason': f"observed={perf['observed_success_rate']:.1%} vs expected={perf['expected_success_rate']:.1%}"
                }
                adjustments.append(adjustment)
                
                # Update pattern in memory
                for p in self.patterns:
                    if p['pattern_id'] == perf['pattern_id']:
                        # Adjust success rate slightly toward observed
                        p['success_rate'] = (p.get('success_rate', 1.0) * 0.7 + perf['observed_success_rate'] * 0.3)
        
        # Save updated patterns
        if adjustments:
            with open(PATTERNS_FILE, 'w') as f:
                json.dump({'patterns': self.patterns, 'generated_at': datetime.now().isoformat()}, f, indent=2)
            print(f"   Adjusted {len(adjustments)} patterns")
        
        return adjustments
    
    def run_cycle(self):
        """Run full meta-learning cycle."""
        print("🔄 Meta Learning Controller — Phase 3")
        print("=" * 50)
        print(f"Started: {datetime.now().isoformat()}")
        
        # Meta-Training: Learn from history
        performance = self.meta_training()
        
        # Meta-Testing: Validate on recent tasks
        test_results = self.meta_testing()
        
        # Adjust weights based on findings
        adjustments = self.adjust_pattern_weights(performance)
        
        # Update learning signal
        self.signal['meta_learning'] = {
            'phase': 3,
            'timestamp': datetime.now().isoformat(),
            'patterns_tested': len(self.patterns),
            'test_accuracy': sum(1 for r in test_results if r['correct']) / len(test_results) if test_results else 0,
            'adjustments_made': len(adjustments),
            'performance': performance[:5],
            'test_results_summary': {
                'total': len(test_results),
                'correct': sum(1 for r in test_results if r['correct'])
            }
        }
        
        with open(LEARNING_SIGNAL, 'w') as f:
            json.dump(self.signal, f, indent=2, default=str)
        
        print(f"\n✅ Meta-Learning Cycle Complete")
        print(f"   Patterns tested: {len(self.patterns)}")
        print(f"   Test accuracy: {self.signal['meta_learning']['test_accuracy']:.1%}")
        print(f"   Adjustments: {len(adjustments)}")
        
        return self.signal['meta_learning']
    
    def status(self):
        """Show controller status."""
        print("📊 Meta Learning Controller Status")
        print("=" * 50)
        print(f"Patterns: {len(self.patterns)}")
        print(f"Tasks: {len(self.tasks)}")
        
        if 'meta_learning' in self.signal:
            ml = self.signal['meta_learning']
            print(f"Last run: {ml.get('timestamp', 'unknown')}")
            print(f"Test accuracy: {ml.get('test_accuracy', 0):.1%}")
            print(f"Adjustments: {ml.get('adjustments_made', 0)}")

    # ============ PHASE 7: EVENT BUS INTEGRATION ============
    
    def read_learning_loop_feedback(self, limit=10):
        """Read recent learning_loop feedback events from Event Bus."""
        try:
            EVENT_FILE = Path("/home/clawbot/.openclaw/workspace/data/events/events.jsonl")
            if not EVENT_FILE.exists():
                return []
            
            events = []
            with open(EVENT_FILE) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if 'learning_meta_feedback' in line:
                        try:
                            obj = json.loads(line)
                            if obj.get('type') == 'learning_meta_feedback':
                                events.append(obj)
                        except:
                            pass
                    if len(events) >= limit:
                        break
            
            if events:
                print(f"   Received {len(events)} feedback events from Learning Loop")
                for fb in events:
                    data = fb.get('data', {})
                    print(f"   - Iteration {data.get('iteration')}: score={data.get('score', 'N/A')}, success_rate={data.get('success_rate', 'N/A'):.2%}")
            
            return events
        except Exception as e:
            print(f"   ⚠️ Failed to read Learning Loop feedback: {e}")
        return []
    
    def emit_pattern_weights(self, weights_data):
        """Emit updated pattern weights to Event Bus for Learning Loop."""
        try:
            data_json = json.dumps(weights_data, default=str)
            result = subprocess.run(
                ['python3', str(EVENT_BUS), 'publish',
                 '--type', 'meta_pattern_weights_updated',
                 '--source', 'meta_controller',
                 '--severity', 'info',
                 '--data', data_json],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"   📡 Event emitted: meta_pattern_weights_updated")
                return True
        except Exception as e:
            print(f"   ⚠️ Failed to emit pattern weights: {e}")
        return False
    
    def emit_meta_insight(self, insight_type, content, confidence=0.5):
        """Emit meta insight to KG and Event Bus."""
        insight_data = {
            'type': 'meta_insight',
            'insight_type': insight_type,
            'content': content,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'source': 'meta_learning_controller'
        }
        try:
            result = subprocess.run(
                ['python3', str(EVENT_BUS), 'publish',
                 '--type', 'meta_insight_generated',
                 '--source', 'meta_controller',
                 '--severity', 'info',
                 '--data', json.dumps(insight_data, default=str)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"   📡 Event emitted: meta_insight_generated ({insight_type})")
        except Exception as e:
            print(f"   ⚠️ Failed to emit meta insight: {e}")
    
    def run_cycle_with_events(self):
        """Phase 7: Run meta-learning cycle with Event Bus integration."""
        print("🔄 Meta Learning Controller — Phase 7 (with Event Bus)")
        print("=" * 50)
        print(f"Started: {datetime.now().isoformat()}")
        
        # PHASE 7.1: Read Learning Loop feedback from Event Bus
        print("\n📥 Phase 7.1: Reading Learning Loop feedback...")
        loop_feedback = self.read_learning_loop_feedback()
        if loop_feedback:
            print(f"   Received {len(loop_feedback)} feedback events from Learning Loop")
            for fb in loop_feedback:
                pattern_id = fb.get('data', {}).get('pattern_id', 'unknown')
                success_rate = fb.get('data', {}).get('success_rate', 0)
                print(f"   - Pattern {pattern_id}: success_rate={success_rate:.2%}")
        else:
            print("   No Learning Loop feedback events found")
        
        # Standard meta-learning cycle
        performance = self.meta_training()
        test_results = self.meta_testing()
        adjustments = self.adjust_pattern_weights(performance)
        
        # PHASE 7.2: Emit pattern weights to Event Bus
        print("\n📤 Phase 7.2: Emitting pattern weights to Event Bus...")
        weights_data = {
            'meta_iteration': self.signal.get('meta_learning', {}).get('phase', 0),
            'timestamp': datetime.now().isoformat(),
            'patterns_count': len(self.patterns),
            'test_accuracy': sum(1 for r in test_results if r['correct']) / len(test_results) if test_results else 0,
            'adjustments': adjustments,
            'performance_summary': [{
                'pattern_id': p['pattern_id'],
                'success_rate': p.get('success_rate', 1.0)
            } for p in self.patterns[:5]]
        }
        self.emit_pattern_weights(weights_data)
        
        # PHASE 7.3: Emit meta insights
        print("\n💡 Phase 7.3: Emitting meta insights...")
        if performance:
            best = max(performance, key=lambda x: x.get('observed_success_rate', 0))
            self.emit_meta_insight('best_pattern', f"Pattern {best['pattern_id']} performs best", best.get('observed_success_rate', 0.5))
        if test_results:
            accuracy = sum(1 for r in test_results if r['correct']) / len(test_results)
            self.emit_meta_insight('test_accuracy', f"Meta-testing accuracy: {accuracy:.1%}", accuracy)
        
        # Update learning signal
        self.signal['meta_learning'] = {
            'phase': 7,
            'timestamp': datetime.now().isoformat(),
            'patterns_tested': len(self.patterns),
            'test_accuracy': sum(1 for r in test_results if r['correct']) / len(test_results) if test_results else 0,
            'adjustments_made': len(adjustments),
            'loop_feedback_received': len(loop_feedback),
            'performance': performance[:5],
            'test_results_summary': {
                'total': len(test_results),
                'correct': sum(1 for r in test_results if r['correct'])
            }
        }
        
        with open(LEARNING_SIGNAL, 'w') as f:
            json.dump(self.signal, f, indent=2, default=str)
        
        print(f"\n✅ Meta-Learning Cycle Complete (Phase 7)")
        print(f"   Patterns tested: {len(self.patterns)}")
        print(f"   Test accuracy: {self.signal['meta_learning']['test_accuracy']:.1%}")
        print(f"   Adjustments: {len(adjustments)}")
        print(f"   Loop feedback received: {len(loop_feedback)}")
        
        return self.signal['meta_learning']


def main():
    controller = MetaLearningController()
    
    if '--status' in sys.argv:
        controller.status()
    elif '--test' in sys.argv:
        controller.meta_testing()
    elif '--with-events' in sys.argv:
        controller.run_cycle_with_events()
    else:
        controller.run_cycle()


if __name__ == '__main__':
    main()
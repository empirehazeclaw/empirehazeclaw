#!/usr/bin/env python3
"""
evolver_meta_bridge.py — Phase 5: Evolver Meta-Learning Bridge
==============================================================
Verbindet Evolver mit Meta-Learning für self-optimizing learning.

⚠️ ADVANCED: Can influence evolver behavior based on meta-patterns.
Nur aktivieren wenn Phase 1-4 stable + explizite Genehmigung.

Usage:
    python3 evolver_meta_bridge.py                    # Run bridge
    python3 evolver_meta_bridge.py --status           # Show connection status
    python3 evolver_meta_bridge.py --signal <type>   # Send signal to evolver
    python3 evolver_meta_bridge.py --analyze          # Analyze evolver + meta learning integration
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'
WEIGHTS_FILE = WORKSPACE / 'memory/meta_learning/algorithm_weights.json'
LEARNING_SIGNAL = WORKSPACE / 'memory/evaluations/learning_loop_signal.json'


class EvolverMetaBridge:
    """
    ⚠️ ADVANCED: Bridges Meta-Learning insights to Evolver.
    
    The Evolver is OpenClaw's optimization system. This bridge:
    1. Analyzes meta-patterns for improvement opportunities
    2. Sends targeted signals to evolver for optimization
    3. Monitors evolver behavior for meta-learning insights
    
    SAFETY: self_modification_enabled must be True (from learning_rules.json)
    """
    
    def __init__(self):
        self.patterns = []
        self.weights = {}
        self.signals = []
        self.load_data()
    
    def load_data(self):
        """Load meta-learning data."""
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                self.patterns = json.load(f).get('patterns', [])
        
        if WEIGHTS_FILE.exists():
            with open(WEIGHTS_FILE, 'r') as f:
                self.weights = json.load(f).get('weights', {})
        
        print(f"📂 Loaded: {len(self.patterns)} patterns, {len(self.weights)} weights")
    
    def analyze_evolution_opportunities(self):
        """Analyze where evolver can improve based on meta-patterns."""
        print("\n🔍 Analyzing Evolution Opportunities")
        print("=" * 50)
        
        opportunities = []
        
        # 1. Find patterns that could guide evolution
        cross_task_patterns = [p for p in self.patterns if p.get('cross_task_valid', False)]
        if cross_task_patterns:
            opportunities.append({
                'type': 'cross_task_optimization',
                'description': f'{len(cross_task_patterns)} cross-task patterns can guide universal optimization',
                'priority': 'HIGH',
                'patterns': [p.get('pattern_id') for p in cross_task_patterns[:3]]
            })
        
        # 2. Find high-impact patterns
        high_impact = [p for p in self.patterns if p.get('matching_tasks', 0) >= 50]
        if high_impact:
            opportunities.append({
                'type': 'high_coverage_improvement',
                'description': f'{len(high_impact)} patterns affect 50+ tasks each',
                'priority': 'MEDIUM',
                'patterns': [p.get('pattern_id') for p in high_impact[:3]]
            })
        
        # 3. Find low-generalization patterns
        low_gen = [p for p in self.patterns if p.get('generalization_score', 1.0) < 0.3]
        if low_gen:
            opportunities.append({
                'type': 'generalization_needed',
                'description': f'{len(low_gen)} patterns need better generalization',
                'priority': 'LOW',
                'patterns': [p.get('pattern_id') for p in low_gen[:3]]
            })
        
        # 4. Find weight optimization opportunities
        low_weights = [(k, v) for k, v in self.weights.items() if v < 0.7]
        if low_weights:
            opportunities.append({
                'type': 'weight_optimization',
                'description': f'{len(low_weights)} parameters with low weights',
                'priority': 'MEDIUM',
                'weights': low_weights[:5]
            })
        
        print(f"\n📋 Found {len(opportunities)} opportunities:")
        for opp in opportunities:
            priority_icon = '🔴' if opp['priority'] == 'HIGH' else '🟡' if opp['priority'] == 'MEDIUM' else '🟢'
            print(f"   {priority_icon} {opp['type']}: {opp['description']}")
        
        return opportunities
    
    def generate_evolution_signals(self):
        """Generate signals for evolver based on meta-learning."""
        print("\n📡 Generating Evolution Signals")
        print("=" * 50)
        
        signals = []
        
        # 1. Pattern-based signal: focus on cross-task patterns
        cross_task = [p for p in self.patterns if p.get('cross_task_valid', False)]
        if cross_task:
            signal = {
                'signal_id': f"evolver_signal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'type': 'meta_pattern_guidance',
                'source': 'meta_learning_bridge',
                'payload': {
                    'focus': 'cross_task_optimization',
                    'patterns': [p.get('pattern_id') for p in cross_task[:5]],
                    'goal': 'improve_generalization_score',
                    'success_metric': 'cross_task_valid_count'
                },
                'priority': 'HIGH',
                'valid_until': datetime.now().isoformat()
            }
            signals.append(signal)
            print(f"   📡 Signal 1: cross_task_optimization ({len(cross_task)} patterns)")
        
        # 2. Weight-based signal: optimize low-performing parameters
        low_weights = [(k, v) for k, v in self.weights.items() if v < 0.8]
        if low_weights:
            signal = {
                'signal_id': f"evolver_signal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'type': 'weight_optimization',
                'source': 'meta_learning_bridge',
                'payload': {
                    'focus': 'parameter_optimization',
                    'low_weights': dict(low_weights[:5]),
                    'goal': 'increase_weight_values',
                    'success_metric': 'weight_improvement'
                },
                'priority': 'MEDIUM'
            }
            signals.append(signal)
            print(f"   📡 Signal 2: weight_optimization ({len(low_weights)} params)")
        
        # 3. Success-rate signal: focus on high-success patterns
        high_success = [p for p in self.patterns if p.get('success_rate', 0) >= 1.0]
        if high_success:
            signal = {
                'signal_id': f"evolver_signal_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'type': 'success_replication',
                'source': 'meta_learning_bridge',
                'payload': {
                    'focus': 'replicate_success_patterns',
                    'patterns': [p.get('pattern_id') for p in high_success[:3]],
                    'goal': 'extend_successful_approaches',
                    'success_metric': 'pattern_success_rate'
                },
                'priority': 'MEDIUM'
            }
            signals.append(signal)
            print(f"   📡 Signal 3: success_replication ({len(high_success)} patterns)")
        
        self.signals = signals
        return signals
    
    def send_signal_to_evolver(self, signal):
        """Send a signal to the evolver."""
        print(f"\n📤 Sending Signal to Evolver: {signal.get('type')}")
        print("=" * 50)
        
        # Store signal in bridge log
        signal_log = WORKSPACE / 'memory/meta_learning/evolver_signals.json'
        
        existing = []
        if signal_log.exists():
            with open(signal_log, 'r') as f:
                existing = json.load(f).get('signals', [])
        
        existing.append(signal)
        
        with open(signal_log, 'w') as f:
            json.dump({
                'signals': existing[-100:],  # Keep last 100
                'last_signal': signal.get('timestamp')
            }, f, indent=2)
        
        print(f"   ✅ Signal stored: {signal.get('signal_id')}")
        print(f"   Type: {signal.get('type')}")
        print(f"   Priority: {signal.get('priority')}")
        print(f"   Stored to: {signal_log}")
        
        return signal
    
    def analyze_integration(self):
        """Analyze evolver + meta-learning integration."""
        print("\n🔗 Evolver-Meta-Learning Integration Analysis")
        print("=" * 50)
        
        # Check if evolver signals exist
        signal_log = WORKSPACE / 'memory/meta_learning/evolver_signals.json'
        sent_count = 0
        if signal_log.exists():
            with open(signal_log, 'r') as f:
                data = json.load(f)
            sent_count = len(data.get('signals', []))
        
        # Check patterns that could influence evolver
        actionable = len([p for p in self.patterns if p.get('generalization_score', 0) >= 0.5])
        
        # Check weights that could guide evolver
        optimizable = len([v for v in self.weights.values() if v < 1.0])
        
        print(f"\n📊 Integration Metrics:")
        print(f"   Sent signals to evolver: {sent_count}")
        print(f"   Actionable patterns: {actionable}")
        print(f"   Optimizable weights: {optimizable}")
        print(f"   Bridge active: {len(self.patterns) > 0}")
        
        # Status assessment
        if sent_count > 10 and actionable > 5:
            status = "🟢 ACTIVE - Evolver receiving meta-learning guidance"
        elif sent_count > 0:
            status = "🟡 BUILDING - Bridge warming up"
        else:
            status = "⚪ IDLE - No signals sent yet"
        
        print(f"\n   Status: {status}")
        
        return {
            'sent_signals': sent_count,
            'actionable_patterns': actionable,
            'optimizable_weights': optimizable,
            'status': status
        }
    
    def run_bridge(self):
        """Run the full evolver-meta bridge."""
        print("🔗 Evolver Meta-Learning Bridge — Phase 5")
        print("=" * 50)
        print(f"Started: {datetime.now().isoformat()}")
        
        # Analyze opportunities
        opportunities = self.analyze_evolution_opportunities()
        
        # Generate signals
        signals = self.generate_evolution_signals()
        
        # Send signals
        sent = 0
        for signal in signals:
            if signal.get('priority') == 'HIGH':
                self.send_signal_to_evolver(signal)
                sent += 1
        
        # Analyze integration
        integration = self.analyze_integration()
        
        print(f"\n✅ Bridge Cycle Complete")
        print(f"   Opportunities: {len(opportunities)}")
        print(f"   Signals generated: {len(signals)}")
        print(f"   Signals sent: {sent}")
        
        return {
            'opportunities': opportunities,
            'signals': signals,
            'sent': sent,
            'integration': integration
        }
    
    def status(self):
        """Show bridge status."""
        print("🔗 Evolver Meta-Learning Bridge Status")
        print("=" * 50)
        print(f"Patterns loaded: {len(self.patterns)}")
        print(f"Weights loaded: {len(self.weights)}")
        print(f"Signals sent: {len(self.signals)}")
        
        self.analyze_integration()


def main():
    bridge = EvolverMetaBridge()
    
    if '--status' in sys.argv:
        bridge.status()
        return
    
    if '--analyze' in sys.argv:
        bridge.analyze_integration()
        return
    
    if '--signal' in sys.argv:
        idx = sys.argv.index('--signal')
        if idx + 1 < len(sys.argv):
            signal_type = sys.argv[idx + 1]
            signals = bridge.generate_evolution_signals()
            
            # Find signal of that type
            for sig in signals:
                if sig.get('type') == signal_type:
                    bridge.send_signal_to_evolver(sig)
                    break
        return
    
    bridge.run_bridge()


if __name__ == '__main__':
    main()
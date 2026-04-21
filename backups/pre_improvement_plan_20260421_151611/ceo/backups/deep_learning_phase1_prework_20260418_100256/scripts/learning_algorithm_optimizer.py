#!/usr/bin/env python3
"""
learning_algorithm_optimizer.py — Phase 3: Learning Algorithm Optimizer
======================================================================
Passt die LERN-Parameter an basierend auf Pattern-Performance.
Vergleichbar mit MAML's "learn to learn".

Usage:
    python3 learning_algorithm_optimizer.py              # Run optimization
    python3 learning_algorithm_optimizer.py --status       # Show weights
    python3 learning_algorithm_optimizer.py --reset        # Reset to defaults
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'
WEIGHTS_FILE = WORKSPACE / 'memory/meta_learning/algorithm_weights.json'


class LearningAlgorithmOptimizer:
    """Optimizes learning algorithm parameters."""
    
    # Default weights for pattern-based routing
    DEFAULT_WEIGHTS = {
        'duration_fast': 1.0,
        'duration_medium': 0.8,
        'duration_slow': 0.6,
        'delegated_health': 1.0,
        'delegated_research': 0.9,
        'delegated_data': 0.9,
        'direct_execution': 0.8,
        'subtype_health_check': 1.0,
        'subtype_learning_sync': 0.9,
        'subtype_subagent_task': 0.8,
        'default': 0.7
    }
    
    def __init__(self):
        self.weights = self.DEFAULT_WEIGHTS.copy()
        self.history = []
        self.load_weights()
    
    def load_weights(self):
        """Load weights from file."""
        if WEIGHTS_FILE.exists():
            with open(WEIGHTS_FILE, 'r') as f:
                data = json.load(f)
            self.weights = data.get('weights', self.DEFAULT_WEIGHTS)
            self.history = data.get('history', [])
            print(f"📂 Loaded weights: {len(self.weights)} parameters")
        else:
            print("📂 Using default weights")
    
    def save_weights(self):
        """Save weights to file."""
        data = {
            'weights': self.weights,
            'history': self.history[-50:],  # Keep last 50
            'updated_at': datetime.now().isoformat()
        }
        with open(WEIGHTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved weights to {WEIGHTS_FILE}")
    
    def get_route_weight(self, task_type=None, subtype=None, delegated_to=None, duration_ms=None):
        """Get routing weight for a task based on learned parameters."""
        # Check duration-based weights
        if duration_ms is not None:
            if duration_ms < 60000:
                dur_weight = self.weights.get('duration_fast', 1.0)
            elif duration_ms < 300000:
                dur_weight = self.weights.get('duration_medium', 0.8)
            else:
                dur_weight = self.weights.get('duration_slow', 0.6)
        else:
            dur_weight = 0.8  # Default
        
        # Check delegated-based weights
        if delegated_to:
            if 'health' in str(delegated_to).lower():
                agent_weight = self.weights.get('delegated_health', 1.0)
            elif 'research' in str(delegated_to).lower():
                agent_weight = self.weights.get('delegated_research', 0.9)
            elif 'data' in str(delegated_to).lower():
                agent_weight = self.weights.get('delegated_data', 0.9)
            else:
                agent_weight = self.weights.get('direct_execution', 0.8)
        else:
            agent_weight = self.weights.get('direct_execution', 0.8)
        
        # Check subtype-based weights
        if subtype:
            subtype_key = f"subtype_{subtype}"
            subtype_weight = self.weights.get(subtype_key, self.weights.get('default', 0.7))
        else:
            subtype_weight = self.weights.get('default', 0.7)
        
        # Combined weight (average)
        combined = (dur_weight + agent_weight + subtype_weight) / 3
        
        return combined
    
    def optimize_from_patterns(self, patterns):
        """Optimize weights based on pattern performance."""
        print("\n⚙️ Optimizing Algorithm Weights from Patterns")
        print("=" * 50)
        
        for pattern in patterns:
            trigger = pattern.get('trigger', {})
            success_rate = pattern.get('success_rate', 1.0)
            
            # Extract trigger keys
            for key, value in trigger.items():
                if key == 'duration_bucket':
                    weight_key = f"duration_{value}"
                    self.weights[weight_key] = min(1.0, success_rate)
                elif key == 'delegated_to':
                    if value and 'health' in str(value).lower():
                        self.weights['delegated_health'] = min(1.0, success_rate)
                    elif value and 'research' in str(value).lower():
                        self.weights['delegated_research'] = min(1.0, success_rate)
                    elif value and 'data' in str(value).lower():
                        self.weights['delegated_data'] = min(1.0, success_rate)
                elif key == 'subtype':
                    weight_key = f"subtype_{value}"
                    self.weights[weight_key] = min(1.0, success_rate)
        
        # Record optimization
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'patterns_processed': len(patterns),
            'weights_updated': True
        })
        
        self.save_weights()
        
        print("✅ Weight optimization complete")
        for key, value in sorted(self.weights.items()):
            print(f"   {key}: {value:.2f}")
        
        return self.weights
    
    def optimize_from_feedback(self, task_id, predicted_weight, actual_success):
        """Adjust weights based on task outcome feedback."""
        delta = 1.0 if actual_success else -0.1
        
        # Simple adjustment based on prediction accuracy
        if abs(predicted_weight - (1.0 if actual_success else 0.0)) > 0.2:
            # Prediction was wrong, adjust default weight
            self.weights['default'] = max(0.5, min(1.0, self.weights.get('default', 0.7) + delta * 0.1))
            
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'task_id': task_id,
                'adjustment': delta,
                'new_default': self.weights['default']
            })
            
            self.save_weights()
        
        return self.weights
    
    def get_optimal_route(self, task_info):
        """Get optimal route for a task based on learned weights."""
        subtype = task_info.get('subtype')
        delegated_to = task_info.get('delegated_to')
        duration_ms = task_info.get('duration_ms')
        
        weight = self.get_route_weight(
            subtype=subtype,
            delegated_to=delegated_to,
            duration_ms=duration_ms
        )
        
        # Determine route
        if delegated_to and weight >= 0.85:
            route = 'delegate'
            agent = delegated_to
        elif weight >= 0.75:
            route = 'direct'
        else:
            route = 'monitored'
        
        return {
            'route': route,
            'weight': weight,
            'agent': delegated_to if route == 'delegate' else None,
            'confidence': 'high' if weight >= 0.9 else 'medium' if weight >= 0.7 else 'low'
        }
    
    def reset_weights(self):
        """Reset weights to default."""
        self.weights = self.DEFAULT_WEIGHTS.copy()
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'reset'
        })
        self.save_weights()
        print("✅ Weights reset to defaults")
    
    def status(self):
        """Show optimizer status."""
        print("📊 Learning Algorithm Optimizer Status")
        print("=" * 50)
        print(f"Weight parameters: {len(self.weights)}")
        print(f"History entries: {len(self.history)}")
        print(f"\n📋 Current Weights:")
        for key, value in sorted(self.weights.items()):
            print(f"   {key}: {value:.2f}")


def main():
    optimizer = LearningAlgorithmOptimizer()
    
    if '--status' in sys.argv:
        optimizer.status()
    elif '--reset' in sys.argv:
        optimizer.reset_weights()
    else:
        # Run optimization from patterns
        patterns = []
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
            patterns = data.get('patterns', [])
        
        optimizer.optimize_from_patterns(patterns)


if __name__ == '__main__':
    main()
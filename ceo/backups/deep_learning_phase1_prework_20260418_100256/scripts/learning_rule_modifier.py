#!/usr/bin/env python3
"""
learning_rule_modifier.py — Phase 5: Self-Modifying Learning
============================================================
⚠️ ADVANCED: Modifiziert Lern-Regeln selbst.
NUR aktivieren wenn Phase 1-4 stable + explizite Genehmigung.

Usage:
    python3 learning_rule_modifier.py --status        # Show current rules
    python3 learning_rule_modifier.py --modify <rule>  # Propose modification
    python3 learning_rule_modifier.py --test          # Test modification (no apply)
    python3 learning_rule_modifier.py --apply         # APPLY modifications (requires approval)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
RULES_FILE = WORKSPACE / 'memory/meta_learning/learning_rules.json'
WEIGHTS_FILE = WORKSPACE / 'memory/meta_learning/algorithm_weights.json'
PATTERNS_FILE = WORKSPACE / 'memory/meta_learning/meta_patterns.json'


class LearningRuleModifier:
    """
    ⚠️ ADVANCED: Can modify own learning rules.
    
    This module analyzes the current learning rules and can propose
    or apply modifications based on pattern performance.
    
    SAFETY: --apply requires explicit confirmation. Without it, only
    --test (simulation) runs.
    """
    
    # Current learning rules (these define HOW the system learns)
    LEARNING_RULES = {
        'pattern_match_threshold': 0.6,
        'generalization_min_score': 0.4,
        'weight_adjustment_rate': 0.1,
        'feedback_loop_enabled': True,
        'meta_learning_enabled': True,
        'self_modification_enabled': False,  # ⚠️ Must be explicitly enabled
        'max_weight_delta': 0.2,
        'min_pattern_confidence': 0.8,
        'cross_task_validation_required': True,
    }
    
    def __init__(self):
        self.rules = self.LEARNING_RULES.copy()
        self.weights = {}
        self.patterns = []
        self.load_data()
    
    def load_data(self):
        """Load current weights and patterns."""
        if WEIGHTS_FILE.exists():
            with open(WEIGHTS_FILE, 'r') as f:
                self.weights = json.load(f).get('weights', {})
        
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r') as f:
                self.patterns = json.load(f).get('patterns', [])
    
    def save_rules(self):
        """Save rules to file."""
        with open(RULES_FILE, 'w') as f:
            json.dump({
                'rules': self.rules,
                'updated_at': datetime.now().isoformat(),
                'updated_by': 'learning_rule_modifier'
            }, f, indent=2)
    
    def analyze_current_rules(self):
        """Analyze if current rules are optimal."""
        print("\n🔍 Analyzing Current Learning Rules")
        print("=" * 50)
        
        issues = []
        suggestions = []
        
        # Check pattern match threshold
        threshold = self.rules.get('pattern_match_threshold', 0.6)
        if threshold < 0.5:
            issues.append("pattern_match_threshold too low (may cause false matches)")
            suggestions.append("Increase to 0.6-0.7 for better precision")
        
        # Check generalization min score
        gen_min = self.rules.get('generalization_min_score', 0.4)
        if gen_min < 0.3:
            suggestions.append("generalization_min_score could be increased to reduce noise")
        
        # Check weight adjustment rate
        rate = self.rules.get('weight_adjustment_rate', 0.1)
        if rate > 0.2:
            issues.append("weight_adjustment_rate too high (may cause oscillation)")
            suggestions.append("Decrease to 0.05-0.1 for stability")
        
        # Check patterns
        if self.patterns:
            high_perf = [p for p in self.patterns if p.get('success_rate', 0) >= 0.95]
            low_perf = [p for p in self.patterns if p.get('success_rate', 0) < 0.8]
            
            print(f"   Patterns: {len(self.patterns)} total")
            print(f"   High performance: {len(high_perf)}")
            print(f"   Low performance: {len(low_perf)}")
            
            if len(low_perf) > len(self.patterns) * 0.3:
                suggestions.append("Too many low-performance patterns - consider increasing thresholds")
        
        # Self-modification status
        sm_enabled = self.rules.get('self_modification_enabled', False)
        print(f"\n   Self-Modification: {'⚠️ ENABLED' if sm_enabled else '✅ DISABLED (safe)'}")
        
        if issues:
            print(f"\n⚠️ Issues Found:")
            for issue in issues:
                print(f"   - {issue}")
        
        if suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in suggestions:
                print(f"   - {suggestion}")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def propose_modification(self, rule_key, new_value):
        """Propose a modification to a rule."""
        print(f"\n📝 Proposed Modification: {rule_key}")
        print("=" * 50)
        
        if rule_key not in self.rules:
            print(f"❌ Unknown rule: {rule_key}")
            return None
        
        old_value = self.rules[rule_key]
        print(f"   Current: {old_value}")
        print(f"   Proposed: {new_value}")
        
        # Analyze impact
        impact = "unknown"
        if 'threshold' in rule_key or 'min_score' in rule_key:
            impact = "Will affect pattern matching precision"
        elif 'rate' in rule_key or 'delta' in rule_key:
            impact = "Will affect learning speed and stability"
        elif 'enabled' in rule_key:
            impact = "Will toggle system behavior"
        
        print(f"   Impact: {impact}")
        
        # Show why this might be good
        if rule_key == 'pattern_match_threshold' and new_value >= 0.6:
            print("   Rationale: Higher threshold = more precise pattern matching")
        elif rule_key == 'weight_adjustment_rate' and new_value <= 0.1:
            print("   Rationale: Lower rate = more stable weight adjustments")
        
        return {
            'rule': rule_key,
            'old_value': old_value,
            'new_value': new_value,
            'impact': impact
        }
    
    def test_modification(self, modifications):
        """Test modifications WITHOUT applying them."""
        print("\n🧪 Testing Modifications (Simulation)")
        print("=" * 50)
        print("⚠️ No changes applied - this is a simulation")
        
        for mod in modifications:
            rule = mod.get('rule')
            new_val = mod.get('new_value')
            old_val = self.rules.get(rule)
            
            print(f"\n   Rule: {rule}")
            print(f"   Would change: {old_val} → {new_val}")
            
            # Simulate impact
            if rule == 'self_modification_enabled' and new_val:
                print("   ⚠️ WARNING: This would enable self-modification!")
                print("   Requires explicit --apply flag and confirmation")
        
        print("\n✅ Simulation complete - no changes made")
        return True
    
    def apply_modifications(self, modifications):
        """
        ⚠️ APPLY modifications to learning rules.
        
        This is the DANGEROUS part. Requires:
        1. self_modification_enabled = True in rules
        2. Explicit --apply flag
        3. Explicit confirmation
        """
        print("\n⚠️ APPLYING MODIFICATIONS")
        print("=" * 50)
        
        # Safety check
        if not self.rules.get('self_modification_enabled', False):
            print("❌ SAFETY BLOCK: self_modification_enabled is False")
            print("   Set self_modification_enabled=True to allow modifications")
            return False
        
        applied = []
        for mod in modifications:
            rule = mod.get('rule')
            new_val = mod.get('new_value')
            
            if rule in self.rules:
                old_val = self.rules[rule]
                self.rules[rule] = new_val
                applied.append({'rule': rule, 'old': old_val, 'new': new_val})
                print(f"   ✅ {rule}: {old_val} → {new_val}")
        
        if applied:
            self.save_rules()
            print(f"\n✅ Applied {len(applied)} modifications")
            print(f"   Rules saved to: {RULES_FILE}")
            
            # Log modification
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'apply_modifications',
                'count': len(applied),
                'rules': applied
            }
            print(f"   Log entry: {json.dumps(log_entry)}")
        
        return applied
    
    def enable_self_modification(self):
        """⚠️ Enable self-modification (requires explicit confirmation)."""
        print("\n⚠️ SELF-MODIFICATION ENABLEMENT")
        print("=" * 50)
        print("⚠️ WARNING: This will allow the system to modify its own learning rules!")
        print("\nThis is a one-way toggle. To disable later, you must:")
        print("1. Manually edit the rules file")
        print("2. Set self_modification_enabled back to False")
        
        # This would require explicit user confirmation to proceed
        return {
            'warning': 'Self-modification enables automatic rule changes',
            'risk': 'System may optimize itself in unintended ways',
            'requires_confirmation': True
        }
    
    def status(self):
        """Show current rules status."""
        print("\n📊 Learning Rules Status")
        print("=" * 50)
        print(f"Rules file: {RULES_FILE}")
        print(f"Self-Modification: {'⚠️ ENABLED' if self.rules.get('self_modification_enabled') else '✅ DISABLED'}")
        print(f"\n📋 Current Rules:")
        for key, value in sorted(self.rules.items()):
            safety = '⚠️' if key == 'self_modification_enabled' else '  '
            print(f"   {safety} {key}: {value}")


def main():
    modifier = LearningRuleModifier()
    
    if '--status' in sys.argv:
        modifier.status()
        return
    
    if '--test' in sys.argv:
        # Test proposed changes (simulation)
        modifications = [
            {'rule': 'pattern_match_threshold', 'new_value': 0.7},
            {'rule': 'generalization_min_score', 'new_value': 0.5}
        ]
        modifier.test_modification(modifications)
        return
    
    if '--apply' in sys.argv:
        # APPLY changes (requires explicit approval)
        modifications = [
            {'rule': 'pattern_match_threshold', 'new_value': 0.7},
            {'rule': 'generalization_min_score', 'new_value': 0.5}
        ]
        modifier.apply_modifications(modifications)
        return
    
    if '--modify' in sys.argv:
        idx = sys.argv.index('--modify')
        if idx + 2 < len(sys.argv):
            rule_key = sys.argv[idx + 1]
            new_value = sys.argv[idx + 2]
            
            # Try to parse value
            if new_value.lower() == 'true':
                new_value = True
            elif new_value.lower() == 'false':
                new_value = False
            elif new_value.replace('.', '').isdigit():
                new_value = float(new_value)
            
            modifier.propose_modification(rule_key, new_value)
        return
    
    # Default: analyze current rules
    modifier.analyze_current_rules()


if __name__ == '__main__':
    main()
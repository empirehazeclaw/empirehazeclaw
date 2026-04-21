#!/usr/bin/env python3
"""
Sir HazeClaw Learnings Agent
============================
Integrates learnings into my daily decision-making.
I use learnings to improve my responses and actions.

Now uses Decision Engine for unified decision-making.
"""

import sys
sys.path.insert(0, 'SCRIPTS/automation')
from learnings_service import LearningsService
from decision_engine import DecisionEngine

def review_and_act():
    """Review learnings and act on them."""
    ls = LearningsService()
    engine = DecisionEngine()
    
    print("🦞 Sir HazeClaw — Learnings Review")
    print("=" * 50)
    
    # Get context for myself
    ctx = ls.get_agent_context("Sir HazeClaw")
    
    print(f"\n📊 Strategy Insights:")
    for s in ctx.get('top_strategies', [])[:5]:
        print(f"   {s['strategy']}: {s['score']} ({s['verdict']})")
    
    print(f"\n💡 Recommendations:")
    for r in ctx.get('recommendations', []):
        print(f"   → {r}")
    
    # Use Decision Engine for next actions
    print(f"\n🎯 Decision Engine Recommendations:")
    for context in ['pattern_matching', 'learning_optimization', 'system_optimization']:
        action = engine.get_next_action(context)
        print(f"   [{context}]")
        print(f"     → {action['action']}")
        print(f"       Strategy: {action['strategy']} (conf: {action['confidence']:.2f})")
    
    # Get recent learnings
    print(f"\n📝 Recent Learnings:")
    for l in ctx.get('learnings', [])[:5]:
        print(f"   [{l['category']}] {l['learning'][:60]}...")
    
    return ctx


if __name__ == "__main__":
    review_and_act()


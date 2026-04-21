#!/usr/bin/env python3
"""
Sir HazeClaw Learnings Agent
============================
Integrates learnings into my daily decision-making.
I use learnings to improve my responses and actions.
"""

import sys
sys.path.insert(0, 'SCRIPTS/automation')
from learnings_service import LearningsService

def review_and_act():
    """Review learnings and act on them."""
    ls = LearningsService()
    
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
    
    # Get recent learnings that might be useful
    print(f"\n📝 Recent Learnings:")
    for l in ctx.get('learnings', [])[:5]:
        print(f"   [{l['category']}] {l['learning'][:60]}...")
    
    # Record a learning from my current session
    print("\n📤 Recording current session insights...")
    
    # Check if there are learnings to record
    recent = ls.get_relevant_learnings(limit=5)
    if recent:
        print(f"   Found {len(recent)} recent learnings")
    else:
        print("   No new learnings to record")
    
    return ctx

if __name__ == "__main__":
    review_and_act()

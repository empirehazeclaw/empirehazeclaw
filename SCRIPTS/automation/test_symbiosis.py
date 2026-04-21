#!/usr/bin/env python3
"""
Test Symbiosis — Phase 8 of Learning-Memory Symbiosis
=====================================================

Comprehensive test suite for all Learning-Memory integration.

Tests:
1. Bidirectional KG ↔ Learnings Sync
2. Consolidation Engine (Events → KG → Learnings)
3. Strategy Effectiveness Feedback Loop
4. Decision Engine API
5. Memory Decay & Confidence Scoring
6. Cross-Agent Learning Federation
7. Memory Consolidator

Usage:
    python3 test_symbiosis.py
    python3 test_symbiosis.py --phase 1
    python3 test_symbiosis.py --quick
"""

import sys
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

sys.path.insert(0, str(WORKSPACE / 'SCRIPTS/automation'))

# Import all modules
from learnings_service import LearningsService
from consolidation_engine import ConsolidationEngine
from decision_engine import DecisionEngine


class TestResult:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
    
    def record(self, name: str, passed: bool, details: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        self.tests.append({"name": name, "status": status, "passed": passed, "details": details})
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        print(f"  {status}: {name}")
        if details:
            print(f"       {details}")
    
    def summary(self):
        total = self.passed + self.failed
        print()
        print("=" * 50)
        print(f"RESULTS: {self.passed}/{total} passed")
        print("=" * 50)
        return self.failed == 0


def test_learnings_service(result):
    """Test Phase 1 & 5: Learnings Service core functionality."""
    print("\n📚 PHASE 1 & 5: Learnings Service")
    print("-" * 40)
    
    try:
        ls = LearningsService()
        
        # Test: record_learning
        lid = ls.record_learning(
            source="Test Suite",
            category="test",
            learning="Test learning for validation",
            context="testing",
            outcome="success"
        )
        result.record("record_learning()", lid.startswith("lrn_"), f"ID: {lid}")
        
        # Test: get_relevant_learnings with confidence
        learnings = ls.get_relevant_learnings(context="testing", limit=5)
        has_confidence = all("confidence" in l for l in learnings)
        result.record("get_relevant_learnings() has confidence", has_confidence)
        
        # Test: get_confidence_score
        conf = ls.get_confidence_score(lid)
        result.record("get_confidence_score()", 0 <= conf <= 1, f"confidence={conf}")
        
        # Test: prune_old_learnings
        prune_result = ls.prune_old_learnings(days=30, dry_run=True)
        result.record("prune_old_learnings()", "count" in prune_result)
        
        # Test: strategy effectiveness
        ls.record_strategy_feedback("test_strategy", "success", "testing")
        effectiveness = ls.index.get("strategy_effectiveness", {})
        result.record("strategy_effectiveness tracking", "test_strategy" in effectiveness)
        
        # Test: get_agent_context
        ctx = ls.get_agent_context("Sir HazeClaw")
        result.record("get_agent_context()", "learnings" in ctx, f"learnings={len(ctx.get('learnings', []))}")
        
    except Exception as e:
        result.record("Learnings Service", False, str(e))


def test_bidirectional_sync(result):
    """Test Phase 1: Bidirectional KG ↔ Learnings Sync."""
    print("\n🔄 PHASE 1: Bidirectional KG Sync")
    print("-" * 40)
    
    try:
        ls = LearningsService()
        
        # Test: sync_from_kg (dry run)
        sync_result = ls.sync_from_kg(dry_run=True)
        result.record("sync_from_kg()", "patterns" in sync_result, str(sync_result))
        
        # Test: sync_to_kg (dry run)
        sync_result = ls.sync_to_kg(dry_run=True)
        result.record("sync_to_kg()", "patterns" in sync_result, str(sync_result))
        
    except Exception as e:
        result.record("Bidirectional Sync", False, str(e))


def test_consolidation_engine(result):
    """Test Phase 2: Consolidation Engine."""
    print("\n⚙️ PHASE 2: Consolidation Engine")
    print("-" * 40)
    
    try:
        engine = ConsolidationEngine()
        
        # Test: extract_event_patterns
        patterns = engine.extract_event_patterns(24)
        result.record("extract_event_patterns()", len(patterns) > 0, f"patterns={len(patterns)}")
        
        # Test: consolidate_episodic_to_semantic (dry run)
        sem_result = engine.consolidate_episodic_to_semantic(dry_run=True)
        result.record("consolidate_episodic_to_semantic()", "entities_created" in sem_result)
        
        # Test: consolidate_semantic_to_procedural (dry run)
        proc_result = engine.consolidate_semantic_to_procedural(dry_run=True)
        result.record("consolidate_semantic_to_procedural()", "learnings_created" in proc_result)
        
    except Exception as e:
        result.record("Consolidation Engine", False, str(e))


def test_strategy_feedback(result):
    """Test Phase 3: Strategy Effectiveness Feedback."""
    print("\n📈 PHASE 3: Strategy Feedback Loop")
    print("-" * 40)
    
    try:
        ls = LearningsService()
        
        # Test: record_strategy_feedback
        fb_result = ls.record_strategy_feedback("test_feedback", "success", "testing")
        result.record("record_strategy_feedback()", "new_score" in fb_result, str(fb_result))
        
        # Test: get_recommended_strategy
        rec = ls.get_recommended_strategy(context="testing")
        result.record("get_recommended_strategy()", "strategy" in rec, f"strategy={rec.get('strategy')}")
        
        # Test: strategy has reasoning
        result.record("recommendation has reasoning", "reasoning" in rec)
        
    except Exception as e:
        result.record("Strategy Feedback", False, str(e))


def test_decision_engine(result):
    """Test Phase 4: Decision Engine API."""
    print("\n🎯 PHASE 4: Decision Engine")
    print("-" * 40)
    
    try:
        engine = DecisionEngine()
        
        # Test: get_next_action
        action = engine.get_next_action("pattern_matching")
        result.record("get_next_action()", "action" in action, f"action={action.get('action')}")
        
        # Test: get_strategy_for_task
        strat = engine.get_strategy_for_task("improve_score")
        result.record("get_strategy_for_task()", "strategy" in strat, f"strategy={strat.get('strategy')}")
        
        # Test: decide_with_confidence
        options = [
            {"id": "1", "name": "Option A", "strategy": "diversity"},
            {"id": "2", "name": "Option B", "strategy": "adaptive_lr"}
        ]
        decision = engine.decide_with_confidence(options)
        result.record("decide_with_confidence()", "selected" in decision)
        
        # Test: get_decision_context
        ctx = engine.get_decision_context("Sir HazeClaw")
        result.record("get_decision_context()", "recommended_actions" in ctx)
        
    except Exception as e:
        result.record("Decision Engine", False, str(e))


def test_cross_agent_federation(result):
    """Test Phase 6: Cross-Agent Learning Federation."""
    print("\n🔗 PHASE 6: Cross-Agent Federation")
    print("-" * 40)
    
    try:
        ls = LearningsService()
        
        # Test: get_all_agents
        agents = ls.get_all_agents()
        result.record("get_all_agents()", len(agents) > 0, f"agents={len(agents)}")
        
        # Test: get_learning_for_agent
        fed = ls.get_learning_for_agent("Ralph Learning")
        result.record("get_learning_for_agent()", "learnings_from_others" in fed)
        
        # Test: record_cross_agent_learning
        lid = ls.record_cross_agent_learning(
            source_agent="Test Agent",
            target_agent="Ralph Learning",
            category="test",
            learning="Cross-agent test learning",
            context="testing"
        )
        result.record("record_cross_agent_learning()", lid.startswith("lrn_"))
        
    except Exception as e:
        result.record("Cross-Agent Federation", False, str(e))


def test_memory_consolidator(result):
    """Test Phase 7: Memory Consolidator."""
    print("\n💾 PHASE 7: Memory Consolidator")
    print("-" * 40)
    
    try:
        from memory_consolidator import MemoryConsolidator
        
        consolidator = MemoryConsolidator()
        
        # Test: consolidate_weekly (KG health)
        weekly = consolidator.consolidate_weekly()
        result.record("consolidate_weekly()", "health_percent" in weekly, f"health={weekly.get('health_percent')}%")
        
        # Test: memory files exist
        kg_file = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
        result.record("KG file exists", kg_file.exists())
        
    except Exception as e:
        result.record("Memory Consolidator", False, str(e))


def test_integration(result):
    """Test integration between all phases."""
    print("\n🔗 INTEGRATION TEST")
    print("-" * 40)
    
    try:
        ls = LearningsService()
        
        # Test: Complete flow
        # 1. Record learning
        lid1 = ls.record_learning(
            source="Integration Test",
            category="integration_test",
            learning="Testing complete flow",
            context="testing",
            outcome="success"
        )
        
        # 2. Query with confidence
        learnings = ls.get_relevant_learnings(context="integration_test", limit=5)
        result.record("Integration: query with confidence", len(learnings) > 0)
        
        # 3. Get recommended strategy
        rec = ls.get_recommended_strategy(context="testing")
        result.record("Integration: strategy recommendation", rec.get("strategy") is not None)
        
        # 4. Record feedback
        ls.record_strategy_feedback(rec.get("strategy", "diversity"), "success", "testing")
        
        # 5. Verify feedback was recorded
        effect = ls.index.get("strategy_effectiveness", {})
        has_feedback = any(v > 0 for v in effect.values())
        result.record("Integration: feedback recorded", has_feedback)
        
    except Exception as e:
        result.record("Integration Test", False, str(e))


def main():
    print("=" * 50)
    print("LEARNING-MEMORY SYMBIOSIS TEST SUITE")
    print(f"Run: {datetime.utcnow().isoformat()}")
    print("=" * 50)
    
    result = TestResult()
    
    # Run all tests
    test_learnings_service(result)
    test_bidirectional_sync(result)
    test_consolidation_engine(result)
    test_strategy_feedback(result)
    test_decision_engine(result)
    test_cross_agent_federation(result)
    test_memory_consolidator(result)
    test_integration(result)
    
    # Summary
    success = result.summary()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Learning-Memory Symbiosis")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    args = parser.parse_args()
    
    sys.exit(main())

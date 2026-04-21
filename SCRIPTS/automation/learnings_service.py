#!/usr/bin/env python3
"""
Learnings Service — Unified Learning Feedback API
================================================
Single API for all systems to read/write learnings.
Implements closed-loop learning: Learn → Sync → Use → Learn

This is the CORE of the learning system - learnings must flow
back into all decision-making systems.

Usage:
    from learnings_service import LearningsService
    ls = LearningsService()
    
    # Record a learning
    ls.record_learning("Ralph Learning", "success", "Score improved when using X strategy")
    
    # Get learnings for a context
    relevant = ls.get_relevant_learnings(context="pattern_matching", limit=5)
    
    # Get strategic insights
    insights = ls.get_strategy_insights()

Phase 8 of System Improvement Plan
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict, Counter

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
RALPH_LEARNINGS = WORKSPACE / "ceo/memory/ralph_learnings.md"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LEARNINGS_INDEX = WORKSPACE / "data/learnings/index.json"
META_LEARNINGS = WORKSPACE / "data/learnings/meta_learnings.json"


class LearningsService:
    """Unified Learnings API for all systems."""
    
    def __init__(self):
        self.kg = self._load_kg()
        self.index = self._load_index()
    
    def _load_kg(self) -> dict:
        """Load Knowledge Graph."""
        try:
            with open(KG_PATH) as f:
                return json.load(f)
        except:
            return {"entities": {}, "relations": {}}
    
    def _load_index(self) -> dict:
        """Load or create learnings index."""
        if LEARNINGS_INDEX.exists():
            with open(LEARNINGS_INDEX) as f:
                return json.load(f)
        return {
            "by_category": defaultdict(list),
            "by_context": defaultdict(list),
            "by_strategy": defaultdict(list),
            "recent": [],
            "strategy_effectiveness": {},
        }
    
    def _save_index(self):
        """Save learnings index."""
        LEARNINGS_INDEX.parent.mkdir(parents=True, exist_ok=True)
        with open(LEARNINGS_INDEX, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def record_learning(
        self,
        source: str,
        category: str,
        learning: str,
        context: Optional[str] = None,
        strategy: Optional[str] = None,
        outcome: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Record a new learning.
        
        Args:
            source: Which system recorded this (e.g., "Ralph Learning", "Meta Learning")
            category: Type of learning ("success", "failure", "pattern", "insight")
            learning: The learning text
            context: Optional context (e.g., "pattern_matching", "score_optimization")
            strategy: Optional strategy used
            outcome: Outcome of the action
            metadata: Additional metadata
            
        Returns:
            learning_id: Unique ID for this learning
        """
        learning_id = f"lrn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.index['recent'])}"
        
        entry = {
            "id": learning_id,
            "source": source,
            "category": category,
            "learning": learning,
            "context": context,
            "strategy": strategy,
            "outcome": outcome,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "used": False,  # Track if this learning was used in a decision
            "useful": None,  # Will be updated after feedback
        }
        
        # Add to index
        self.index["recent"].append(entry)
        
        # Keep only last 500 learnings
        if len(self.index["recent"]) > 500:
            self.index["recent"] = self.index["recent"][-500:]
        
        # Categorize
        if category:
            self.index["by_category"][category].append(learning_id)
        
        if context:
            self.index["by_context"][context].append(learning_id)
        
        if strategy:
            self.index["by_strategy"][strategy].append(learning_id)
            # Track strategy effectiveness
            if outcome == "success":
                self.index["strategy_effectiveness"][strategy] = \
                    self.index["strategy_effectiveness"].get(strategy, 0) + 1
            elif outcome == "failure":
                self.index["strategy_effectiveness"][strategy] = \
                    self.index["strategy_effectiveness"].get(strategy, 0) - 1
        
        self._save_index()
        self._sync_to_kg(entry)
        
        return learning_id
    
    def get_relevant_learnings(
        self,
        context: Optional[str] = None,
        category: Optional[str] = None,
        strategy: Optional[str] = None,
        min_effectiveness: Optional[int] = None,
        limit: int = 10,
        include_used: bool = False
    ) -> List[dict]:
        """
        Get relevant learnings based on filters.
        
        Returns learnings most likely to be useful for current decisions.
        """
        candidates = self.index["recent"]
        
        if not include_used:
            candidates = [l for l in candidates if not l.get("used")]
        
        # Filter by context
        if context:
            context_ids = set(self.index["by_context"].get(context, []))
            candidates = [l for l in candidates if l["id"] in context_ids]
        
        # Filter by category
        if category:
            cat_ids = set(self.index["by_category"].get(category, []))
            candidates = [l for l in candidates if l["id"] in cat_ids]
        
        # Filter by strategy effectiveness
        if min_effectiveness is not None:
            effective_strategies = {
                s for s, v in self.index["strategy_effectiveness"].items()
                if v >= min_effectiveness
            }
            candidates = [
                l for l in candidates
                if l.get("strategy") in effective_strategies
            ]
        
        # Sort by recency and usefulness
        candidates.sort(key=lambda x: (
            x.get("metadata", {}).get("priority", 0),
            x.get("useful", 0) if x.get("useful") else -1,
            x["timestamp"]
        ), reverse=True)
        
        return candidates[:limit]
    
    def get_strategy_insights(self) -> Dict[str, any]:
        """
        Get insights about which strategies work best.
        
        Returns:
            Dict with strategy rankings, effectiveness scores, etc.
        """
        effectiveness = self.index["strategy_effectiveness"]
        
        # Rank strategies
        ranked = sorted(
            effectiveness.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "top_strategies": [
                {"strategy": s, "score": v, "verdict": "HIGHLY_EFFECTIVE" if v >= 3 else "EFFECTIVE" if v >= 1 else "NEUTRAL" if v >= 0 else "INEFFECTIVE"}
                for s, v in ranked[:10]
            ],
            "failed_strategies": [
                {"strategy": s, "score": v}
                for s, v in ranked
                if v < 0
            ],
            "untested_strategies": self._get_untested_strategies(),
            "total_strategies": len(effectiveness),
        }
    
    def _get_untested_strategies(self) -> List[str]:
        """Get strategies that haven't been tested yet."""
        all_strategies = {
            "exploration", "exploitation", "pattern_matching",
            "novelty_injection", "cross_pattern", "decay",
            "adaptive_lr", "thompson_sampling", "ucb1",
            "diversity", "intensification", "innovation",
            "repair", "reconstruction", "optimization"
        }
        tested = set(self.index["strategy_effectiveness"].keys())
        return list(all_strategies - tested)
    
    def mark_learning_used(self, learning_id: str) -> bool:
        """Mark a learning as having been used in a decision."""
        for learning in self.index["recent"]:
            if learning["id"] == learning_id:
                learning["used"] = True
                self._save_index()
                return True
        return False
    
    def provide_feedback(self, learning_id: str, useful: bool):
        """
        Provide feedback on whether a learning was useful.
        
        This closes the loop: learnings get better over time.
        """
        for learning in self.index["recent"]:
            if learning["id"] == learning_id:
                current = learning.get("useful", 0)
                learning["useful"] = current + (1 if useful else -1)
                self._save_index()
                return True
        return False
    
    def get_context_for_task(self, task: str) -> Dict[str, any]:
        """
        Get learnings relevant for a specific task type.
        
        Maps task types to learning contexts.
        """
        # Task type to learning context mapping
        task_context_map = {
            "pattern_matching": ["pattern", "cross_pattern", "efficiency"],
            "score_optimization": ["score", "improvement", "optimization"],
            "novelty_generation": ["novelty", "exploration", "innovation"],
            "stagnation_escape": ["stagnation", "plateau", "break"],
            "validation": ["validation", "test", "verification"],
            "kg_update": ["kg", "entity", "relation"],
            "cron_health": ["cron", "health", "monitoring"],
            "general": ["success", "failure", "pattern", "insight"],
        }
        
        contexts = task_context_map.get(task, ["general"])
        
        learnings = []
        for ctx in contexts:
            learnings.extend(
                self.get_relevant_learnings(context=ctx, limit=5)
            )
        
        # Deduplicate
        seen = set()
        unique = []
        for l in learnings:
            if l["id"] not in seen:
                seen.add(l["id"])
                unique.append(l)
        
        return {
            "task": task,
            "contexts": contexts,
            "learnings": unique[:10],
            "strategy_insights": self.get_strategy_insights(),
        }
    
    def _sync_to_kg(self, learning: dict):
        """Sync learning to Knowledge Graph."""
        try:
            # Create learning entity
            entity_id = learning["id"]
            self.kg["entities"][entity_id] = {
                "type": "Learning",
                "category": learning["category"],
                "source": learning["source"],
                "learning": learning["learning"][:200],
                "context": learning.get("context"),
                "timestamp": learning["timestamp"],
                "fact_count": 1,
            }
            
            # Create relation to source
            source_entity = learning["source"].replace(" ", "-")
            if source_entity in self.kg["entities"]:
                relation_id = f"rel_{len(self.kg['relations'])}"
                self.kg["relations"][relation_id] = {
                    "from": entity_id,
                    "to": source_entity,
                    "type": "learned_from"
                }
            
            # Save KG
            with open(KG_PATH, 'w') as f:
                json.dump(self.kg, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to sync to KG: {e}")
    
    def get_agent_context(self, agent_name: str) -> Dict[str, any]:
        """
        Get learnings relevant for a specific agent.
        
        Args:
            agent_name: Name of agent (e.g., "Ralph Learning", "Meta Learning", "Capability Evolver")
            
        Returns:
            Dict with agent-specific learnings and recommendations
        """
        # Map agents to their learning needs
        agent_contexts = {
            "Ralph Learning": ["learning", "improvement", "optimization", "Ralph"],
            "Meta Learning": ["pattern", "weight", "strategy", "accuracy"],
            "Capability Evolver": ["gene", "mutation", "capability", "evolution", "stagnation"],
            "Self-Improver": ["code", "improvement", "refactor", "bug", "fix"],
            "Learning Loop": ["score", "pattern", "novelty", "validation"],
            "Sir HazeClaw": ["decision", "insight", "pattern", "strategy"],
        }
        
        contexts = agent_contexts.get(agent_name, ["general"])
        
        learnings = []
        for ctx in contexts:
            learnings.extend(
                self.get_relevant_learnings(context=ctx, limit=5)
            )
        
        # Get strategy insights
        insights = self.get_strategy_insights()
        
        return {
            "agent": agent_name,
            "relevant_contexts": contexts,
            "learnings": learnings[:10],
            "top_strategies": insights["top_strategies"][:5],
            "recommendations": self._generate_recommendations(learnings, insights),
        }
    
    def _generate_recommendations(
        self,
        learnings: List[dict],
        insights: dict
    ) -> List[str]:
        """Generate recommendations based on learnings and strategy insights."""
        recommendations = []
        
        # Recommend top strategies
        top = insights.get("top_strategies", [])
        if top:
            recommendations.append(
                f"Top performing strategy: {top[0]['strategy']} (score: {top[0]['score']})"
            )
        
        # Recommend using successful patterns
        successful = [l for l in learnings if l.get("outcome") == "success"]
        if successful:
            recommendations.append(
                f"Apply {len(successful)} successful patterns from recent learnings"
            )
        
        # Warn about failed strategies
        failed = insights.get("failed_strategies", [])
        if failed:
            recommendations.append(
                f"Avoid {len(failed)} ineffective strategies: {[f['strategy'] for f in failed[:3]]}"
            )
        
        return recommendations


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    ls = LearningsService()
    parser = argparse.ArgumentParser(description="Learnings Service")
    
    sub = parser.add_subparsers(dest="cmd")
    
    # Record learning
    p = sub.add_parser("record", help="Record a new learning")
    p.add_argument("--source", required=True)
    p.add_argument("--category", required=True)
    p.add_argument("--learning", required=True)
    p.add_argument("--context")
    p.add_argument("--strategy")
    p.add_argument("--outcome")
    
    # Get learnings
    p = sub.add_parser("get", help="Get relevant learnings")
    p.add_argument("--context")
    p.add_argument("--category")
    p.add_argument("--limit", type=int, default=10)
    
    # Get agent context
    p = sub.add_parser("agent", help="Get learnings for an agent")
    p.add_argument("--name", required=True)
    
    # Get insights
    sub.add_parser("insights", help="Get strategy insights")
    
    args = parser.parse_args()
    
    if args.cmd == "record":
        lid = ls.record_learning(
            source=args.source,
            category=args.category,
            learning=args.learning,
            context=args.context,
            strategy=args.strategy,
            outcome=args.outcome
        )
        print(f"Recorded: {lid}")
    
    elif args.cmd == "get":
        learnings = ls.get_relevant_learnings(
            context=args.context,
            category=args.category,
            limit=args.limit
        )
        print(f"Found {len(learnings)} learnings:")
        for l in learnings:
            print(f"  [{l['category']}] {l['learning'][:80]}...")
    
    elif args.cmd == "agent":
        ctx = ls.get_agent_context(args.name)
        print(f"Learnings for {ctx['agent']}:")
        print(f"\nTop Strategies:")
        for s in ctx['top_strategies']:
            print(f"  - {s['strategy']}: {s['score']} ({s['verdict']})")
        print(f"\nRecommendations:")
        for r in ctx['recommendations']:
            print(f"  - {r}")
        print(f"\nRecent Learnings:")
        for l in ctx['learnings'][:5]:
            print(f"  [{l['category']}] {l['learning'][:60]}...")
    
    elif args.cmd == "insights":
        insights = ls.get_strategy_insights()
        print("Strategy Insights:")
        print(f"\nTop Strategies:")
        for s in insights['top_strategies']:
            print(f"  {s['strategy']}: {s['score']} ({s['verdict']})")
        print(f"\nFailed Strategies:")
        for f in insights['failed_strategies']:
            print(f"  {f['strategy']}: {f['score']}")
        print(f"\nUntested Strategies:")
        for s in insights['untested_strategies']:
            print(f"  - {s}")
    
    else:
        parser.print_help()

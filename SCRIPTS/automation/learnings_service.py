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
                data = json.load(f)
            # Convert to defaultdict for backwards compatibility
            return {
                "by_category": defaultdict(list, data.get("by_category", {})),
                "by_context": defaultdict(list, data.get("by_context", {})),
                "by_strategy": defaultdict(list, data.get("by_strategy", {})),
                "recent": data.get("recent", []),
                "strategy_effectiveness": data.get("strategy_effectiveness", {}),
            }
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
    
    # ============ BIDIRECTIONAL KG SYNC ============
    
    def sync_from_kg(self, dry_run: bool = False) -> Dict:
        """Sync KG entities to Learnings (Semantic → Procedural)."""
        self.kg = self._load_kg()
        synced = {"patterns": 0, "genes": 0, "strategies": 0}
        existing_ids = {l.get("id") for l in self.index["recent"]}
        
        # Collect items to sync first (avoid dict size change during iteration)
        to_sync = []
        for entity_id, entity in self.kg.get("entities", {}).items():
            entity_type = entity.get("type", "")
            
            if entity_type == "LearningPattern" and f"kg_{entity_id}" not in existing_ids:
                to_sync.append(("pattern", entity.get("name", entity_id), "pattern_matching"))
            elif "gene" in entity_id.lower() and f"kg_{entity_id}" not in existing_ids:
                to_sync.append(("gene", entity.get("name", entity_id), "evolution"))
        
        # Now apply sync
        for cat, name, ctx in to_sync:
            if not dry_run:
                self.record_learning(
                    source="KG Consolidation",
                    category=cat,
                    learning=f"{cat.title()} from KG: {name}",
                    context=ctx,
                    outcome="success"
                )
            synced[cat + "s"] += 1
        
        return synced
    
    def sync_to_kg(self, dry_run: bool = False) -> Dict:
        """Sync Learnings to KG (Procedural → Semantic)."""
        self.kg = self._load_kg()
        synced = {"patterns": 0, "insights": 0}
        existing = set(self.kg.get("entities", {}).keys())
        
        for learning in self.index["recent"]:
            if learning.get("outcome") != "success":
                continue
            
            lid = learning.get("id", "")
            cat = learning.get("category", "")
            
            if cat == "pattern" and f"learning_{lid}" not in existing:
                self.kg.setdefault("entities", {})[f"learning_{lid}"] = {
                    "type": "LearningPattern",
                    "name": learning.get("learning", "")[:100],
                    "facts": [f"Source: {learning.get('source', 'Unknown')}"]
                }
                synced["patterns"] += 1
            elif cat == "insight" and f"insight_{lid}" not in existing:
                self.kg.setdefault("entities", {})[f"insight_{lid}"] = {
                    "type": "Insight",
                    "name": learning.get("learning", "")[:100],
                    "facts": [f"Context: {learning.get('context', 'general')}"]
                }
                synced["insights"] += 1
        
        if not dry_run and (synced["patterns"] > 0 or synced["insights"] > 0):
            KG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(KG_PATH, 'w') as f:
                json.dump(self.kg, f, indent=2)
        
        return synced
    
    def prune_old_learnings(self, days: int = 30, dry_run: bool = False) -> Dict:
        """Remove learnings older than specified days (memory decay)."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        remaining = []
        removed = {"count": 0, "by_category": defaultdict(int)}
        
        for learning in self.index["recent"]:
            try:
                learning_date = datetime.fromisoformat(learning.get("timestamp", "2020-01-01"))
                if learning_date > cutoff:
                    remaining.append(learning)
                else:
                    removed["count"] += 1
                    removed["by_category"][learning.get("category", "unknown")] += 1
            except:
                remaining.append(learning)
        
        if not dry_run:
            self.index["recent"] = remaining
            self._rebuild_indexes()
            self._save_index()
        
        removed["remaining"] = len(remaining)
        return removed
    
    def _rebuild_indexes(self):
        """Rebuild all indexes from recent learnings."""
        self.index["by_category"] = defaultdict(list)
        self.index["by_context"] = defaultdict(list)
        self.index["by_strategy"] = defaultdict(list)
        
        for learning in self.index["recent"]:
            self.index["by_category"][learning.get("category", "unknown")].append(learning.get("id", ""))
            self.index["by_context"][learning.get("context", "general")].append(learning.get("id", ""))
            if learning.get("strategy"):
                self.index["by_strategy"][learning.get("strategy")].append(learning.get("id", ""))
    
    def get_confidence_score(self, learning_id: str) -> float:
        """Get confidence score for a learning (0.0-1.0) based on recency + outcome."""
        for learning in self.index["recent"]:
            if learning.get("id") == learning_id:
                base, recency, outcome_mult = 0.5, 0.5, 1.0
                try:
                    days_old = (datetime.utcnow() - datetime.fromisoformat(learning.get("timestamp", "2020-01-01"))).days
                    recency = pow(0.95, days_old)
                except:
                    pass
                if learning.get("outcome") == "success":
                    outcome_mult = 1.5
                elif learning.get("outcome") == "failure":
                    outcome_mult = 0.5
                return min(1.0, round(base * recency * outcome_mult, 3))
        return 0.0
    
    def get_learning_with_confidence(self, learning_id: str) -> Optional[Dict]:
        """Get learning with confidence score attached."""
        for learning in self.index["recent"]:
            if learning.get("id") == learning_id:
                result = learning.copy()
                result["confidence"] = self.get_confidence_score(learning_id)
                return result
        return None
    
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
        
        # Add confidence scores to results
        results = []
        for l in candidates[:limit]:
            l_with_conf = l.copy()
            l_with_conf["confidence"] = self.get_confidence_score(l.get("id", ""))
            results.append(l_with_conf)
        
        return results
    
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
    
    def record_strategy_feedback(self, strategy: str, outcome: str, context: Optional[str] = None) -> Dict:
        """
        Record the outcome of using a strategy.
        
        This closes the feedback loop:
        Strategy used → Outcome recorded → Strategy effectiveness updated → Next recommendation better
        
        Args:
            strategy: The strategy that was used
            outcome: "success" or "failure"
            context: Optional context where strategy was used
        
        Returns:
            Updated strategy effectiveness scores
        """
        effectiveness = self.index.setdefault("strategy_effectiveness", {})
        
        # Update strategy score
        current = effectiveness.get(strategy, 0)
        if outcome == "success":
            effectiveness[strategy] = current + 1
        elif outcome == "failure":
            effectiveness[strategy] = current - 1
        
        # Track by context too
        if context:
            context_effectiveness = self.index.setdefault("context_effectiveness", {})
            ctx_scores = context_effectiveness.setdefault(context, {})
            current_ctx = ctx_scores.get(strategy, 0)
            if outcome == "success":
                ctx_scores[strategy] = current_ctx + 1
            elif outcome == "failure":
                ctx_scores[strategy] = current_ctx - 1
        
        self._save_index()
        
        return {
            "strategy": strategy,
            "outcome": outcome,
            "new_score": effectiveness[strategy],
            "total_strategies_tracked": len(effectiveness)
        }
    
    def get_recommended_strategy(self, context: Optional[str] = None, available_strategies: Optional[List[str]] = None) -> Dict:
        """
        Get the recommended strategy for a context.
        
        Uses:
        1. Context-specific effectiveness (if context provided)
        2. General strategy effectiveness
        3. Exploration bonus for untested strategies
        
        Args:
            context: The context/task type
            available_strategies: List of strategies to choose from
        
        Returns:
            Dict with recommended strategy and reasoning
        """
        effectiveness = self.index.get("strategy_effectiveness", {})
        context_effectiveness = self.index.get("context_effectiveness", {})
        
        # Start with all strategies or available ones
        candidates = set(available_strategies) if available_strategies else set(effectiveness.keys())
        
        # If context provided, use context-specific scores
        if context and context in context_effectiveness:
            ctx_scores = context_effectiveness[context]
            # Combine general and context-specific (weighted toward context)
            scored = {}
            for s in candidates:
                general = effectiveness.get(s, 0)
                specific = ctx_scores.get(s, 0)
                # Weight context-specific more heavily
                combined = general * 0.3 + specific * 0.7
                # Add exploration bonus for untested
                if s not in ctx_scores:
                    combined += 0.5  # Exploration bonus
                scored[s] = combined
        else:
            # Use general effectiveness
            scored = {s: effectiveness.get(s, 0) + (0.5 if s not in effectiveness else 0) for s in candidates}
        
        if not scored:
            return {"strategy": "diversity", "reasoning": "Default (no data)", "confidence": 0.0}
        
        # Pick best
        best = max(scored.items(), key=lambda x: x[1])
        
        return {
            "strategy": best[0],
            "score": best[1],
            "confidence": min(1.0, abs(best[1]) / 5),  # Normalize to 0-1
            "reasoning": f"Score {best[1]:.2f} based on historical effectiveness",
            "all_candidates": dict(sorted(scored.items(), key=lambda x: -x[1])[:5])
        }
    
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
    
    # ============ CROSS-AGENT FEDERATION ============
    
    def get_all_agents(self) -> List[str]:
        """Get list of all agents that have contributed learnings."""
        agents = set()
        for learning in self.index["recent"]:
            source = learning.get("source", "Unknown")
            # Clean up source name
            if "[" in source:
                source = source.split("]")[1].strip() if "]" in source else source
            agents.add(source)
        return sorted(list(agents))
    
    def get_learning_for_agent(self, agent_name: str, context: Optional[str] = None, limit: int = 5) -> Dict:
        """
        Get learnings FROM other agents that would benefit this agent.
        
        Cross-agent federation: Agent X can learn from what Agent Y discovered.
        
        Args:
            agent_name: The agent that needs learnings
            context: Optional specific context to filter by
            limit: Max learnings to return
        
        Returns:
            Dict with learnings from other agents and recommendations
        """
        # Map agent → what they can learn from other agents
        federation_map = {
            "Ralph Learning": {
                "from": ["Meta Learning", "Capability Evolver", "Health Monitor", "Consolidation Engine"],
                "contexts": ["pattern", "strategy", "gene", "health_issue"]
            },
            "Meta Learning": {
                "from": ["Ralph Learning", "Capability Evolver", "Self-Improver"],
                "contexts": ["pattern", "improvement", "accuracy"]
            },
            "Capability Evolver": {
                "from": ["Ralph Learning", "Learning Loop", "Health Monitor"],
                "contexts": ["gene", "mutation", "score", "health_issue"]
            },
            "Self-Improver": {
                "from": ["Ralph Learning", "Meta Learning", "Health Monitor"],
                "contexts": ["improvement", "fix", "bug", "pattern"]
            },
            "Sir HazeClaw": {
                "from": ["Ralph Learning", "Meta Learning", "Capability Evolver", "Self-Improver", "Health Monitor"],
                "contexts": ["decision", "insight", "pattern", "strategy", "improvement"]
            }
        }
        
        federation = federation_map.get(agent_name, {
            "from": ["Ralph Learning", "Meta Learning", "Capability Evolver"],
            "contexts": ["general"]
        })
        
        # Get learnings from other agents
        cross_learnings = []
        for learning in self.index["recent"]:
            source = learning.get("source", "")
            # Skip self
            if source == agent_name:
                continue
            # Check if source is in federation list
            clean_source = source.split("]")[-1].strip() if "]" in source else source
            if clean_source not in federation["from"]:
                continue
            # Filter by context if specified
            if context:
                if learning.get("context") != context:
                    continue
            cross_learnings.append(learning)
        
        # Sort by confidence and recency
        cross_learnings.sort(key=lambda x: (
            self.get_confidence_score(x.get("id", "")),
            x.get("timestamp", "")
        ), reverse=True)
        
        return {
            "agent": agent_name,
            "federation_sources": federation["from"],
            "learnings_from_others": cross_learnings[:limit],
            "count_by_source": self._count_by_source(cross_learnings)
        }
    
    def _count_by_source(self, learnings: List[dict]) -> Dict[str, int]:
        """Count learnings by source agent."""
        counts = defaultdict(int)
        for l in learnings:
            source = l.get("source", "Unknown")
            clean = source.split("]")[-1].strip() if "]" in source else source
            counts[clean] += 1
        return dict(counts)
    
    def record_cross_agent_learning(
        self,
        source_agent: str,
        target_agent: str,
        category: str,
        learning: str,
        context: Optional[str] = None
    ) -> str:
        """
        Explicitly share a learning from one agent to benefit another.
        
        Args:
            source_agent: Who discovered this
            target_agent: Who should benefit from this
            category: Type of learning
            learning: The learning text
            context: Optional context
        
        Returns:
            Learning ID
        """
        # Record with special notation for federation
        full_source = f"[→{target_agent}] {source_agent}"
        
        return self.record_learning(
            source=full_source,
            category=category,
            learning=learning,
            context=context,
            outcome="shared"
        )


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
    
    # Prune old learnings
    p = sub.add_parser("prune", help="Prune old learnings")
    p.add_argument("--days", type=int, default=30)
    
    # Sync KG ↔ Learnings
    sub.add_parser("sync-kg", help="Bidirectional KG ↔ Learnings sync")
    
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
    
    elif args.cmd == "prune":
        days = getattr(args, 'days', 30)
        print(f"Pruning learnings older than {days} days...")
        result = ls.prune_old_learnings(days=days, dry_run=False)
        print(f"Removed: {result['count']} learnings")
        print(f"Remaining: {result['remaining']}")
        if result.get('by_category'):
            print("By category:")
            for cat, cnt in dict(result['by_category']).items():
                print(f"  {cat}: {cnt}")
    
    elif args.cmd == "sync-kg":
        print("Syncing Learnings → KG...")
        result = ls.sync_to_kg(dry_run=False)
        print(f"Synced: {result}")
        print("Syncing KG → Learnings...")
        result = ls.sync_from_kg(dry_run=False)
        print(f"Synced: {result}")
    
    else:
        parser.print_help()

# Heartbeat Integration
def heartbeat_check():
    """Called by heartbeat to review and act on learnings."""
    ls = LearningsService()
    
    # Get insights for myself
    ctx = ls.get_agent_context("Sir HazeClaw")
    
    # Log if there are new recommendations
    if ctx.get('recommendations'):
        print(f"💡 Learnings Insight: {ctx['recommendations'][0]}")
    
    # Get learnings I should act on
    learnings = ls.get_relevant_learnings(context="decision", limit=3)
    
    return {
        "new_insights": len(learnings),
        "top_recommendations": ctx.get('recommendations', [])[:2],
    }

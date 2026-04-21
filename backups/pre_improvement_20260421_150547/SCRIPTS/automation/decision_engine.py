#!/usr/bin/env python3
"""
Decision Engine — Phase 4 of Learning-Memory Symbiosis
=====================================================

Single API for agents to ask: "What should I do next?"

Provides:
- get_next_action(context): What to do given current state
- get_strategy_for_task(task): Recommended strategy for task
- decide_with_confidence(context, options): Pick best option with confidence

Based on research:
- Mem0: Purpose-built memory cuts decisions costs 90%
- Letta: Confidence scoring for decisions
- NeurIPS 2025: Strategy effectiveness tracking

Usage:
    python3 decision_engine.py decide --context pattern_matching
    python3 decision_engine.py strategy --task optimization
    python3 decision_engine.py confidence --id lrn_xxx
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

sys.path.insert(0, str(WORKSPACE / 'SCRIPTS/automation'))
try:
    from learnings_service import LearningsService
except:
    LearningsService = None


class DecisionEngine:
    """
    Unified decision-making API for all agents.
    
    Agents ask: "What should I do?"
    Engine answers based on:
    1. Historical learnings
    2. Strategy effectiveness
    3. Confidence scores
    4. Context
    """
    
    def __init__(self):
        self.learnings = LearningsService() if LearningsService else None
        
        # Context → available strategies mapping
        self.CONTEXT_STRATEGIES = {
            "pattern_matching": ["diversity", "adaptive_lr", "dynamic_weights", "mutation_tuning", "exploration"],
            "score_optimization": ["adaptive_lr", "intensification", "exploitation"],
            "learning_optimization": ["exploration", "diversity", "adaptive_lr", "thompson_sampling"],
            "evolution": ["mutation_tuning", "repair", "innovation", "diversity"],
            "system_optimization": ["optimization", "repair", "exploration"],
            "general": ["diversity", "exploration", "exploitation"]
        }
        
        # Task priorities (higher = more important)
        self.TASK_PRIORITY = {
            "pattern_matching": 0.9,
            "score_optimization": 0.8,
            "learning_optimization": 0.85,
            "evolution": 0.7,
            "system_optimization": 0.6,
            "maintenance": 0.5
        }
    
    def get_next_action(self, context: str = "general", force_explore: bool = False) -> Dict:
        """
        Get the recommended next action for a context.
        
        Args:
            context: The current context (e.g., "pattern_matching")
            force_explore: If True, prefer untested strategies (for exploration)
        
        Returns:
            Dict with action, strategy, reasoning, confidence
        """
        if not self.learnings:
            return {
                "action": "explore",
                "strategy": "diversity",
                "confidence": 0.0,
                "reasoning": "No learnings available - defaulting to diversity"
            }
        
        # Get available strategies for context
        available = self.CONTEXT_STRATEGIES.get(context, self.CONTEXT_STRATEGIES["general"])
        
        # Get recommendation
        recommendation = self.learnings.get_recommended_strategy(
            context=context,
            available_strategies=available
        )
        
        # If force_explore, pick untested strategy
        if force_explore:
            untested = self.learnings._get_untested_strategies()
            unexplored = [s for s in available if s in untested]
            if unexplored:
                recommendation = {
                    "strategy": unexplored[0],
                    "reasoning": "Exploration mode - selecting untested strategy",
                    "confidence": 0.3  # Lower confidence for untested
                }
        
        # Determine action based on strategy
        action = self._strategy_to_action(recommendation.get("strategy", "diversity"))
        
        return {
            "action": action,
            "strategy": recommendation.get("strategy"),
            "confidence": recommendation.get("confidence", 0.5),
            "reasoning": recommendation.get("reasoning", "Based on historical effectiveness"),
            "context": context,
            "available_strategies": available
        }
    
    def _strategy_to_action(self, strategy: str) -> str:
        """Map strategy to concrete action."""
        strategy_actions = {
            "diversity": "Apply multiple patterns simultaneously",
            "adaptive_lr": "Adjust learning rate based on score trend",
            "dynamic_weights": "Re-balance pattern weights",
            "mutation_tuning": "Tune gene mutation parameters",
            "exploration": "Try new pattern combinations",
            "exploitation": "Focus on best-performing pattern",
            "intensification": "Double down on current strategy",
            "thompson_sampling": "Probabilistically balance explore/exploit",
            "ucb1": "Upper confidence bound for selection",
            "repair": "Fix broken patterns or relations",
            "innovation": "Generate novel pattern types",
            "optimization": "Refine existing processes"
        }
        return strategy_actions.get(strategy, f"Apply {strategy} strategy")
    
    def get_strategy_for_task(self, task: str) -> Dict:
        """
        Get recommended strategy for a specific task.
        
        Args:
            task: Task type (e.g., "improve_score", "fix_bug", "explore")
        
        Returns:
            Dict with recommended strategy and reasoning
        """
        # Map tasks to contexts and strategies
        task_map = {
            "improve_score": {
                "context": "score_optimization",
                "strategy": "adaptive_lr",
                "reasoning": "Learning rate adaptation most effective for score improvement"
            },
            "fix_bug": {
                "context": "system_optimization",
                "strategy": "repair",
                "reasoning": "Debugging requires systematic repair approach"
            },
            "explore": {
                "context": "learning_optimization",
                "strategy": "exploration",
                "reasoning": "Exploration needed to discover new patterns"
            },
            "optimize": {
                "context": "system_optimization",
                "strategy": "optimization",
                "reasoning": "Fine-tuning existing processes"
            },
            "evolve": {
                "context": "evolution",
                "strategy": "mutation_tuning",
                "reasoning": "Evolution requires controlled mutation"
            }
        }
        
        if task not in task_map:
            return {
                "task": task,
                "strategy": "diversity",
                "reasoning": "Unknown task - defaulting to diversity"
            }
        
        return task_map[task]
    
    def decide_with_confidence(self, options: List[Dict], context: str = "general") -> Dict:
        """
        Pick best option from list with confidence scoring.
        
        Each option should have: {id, name, score?, strategy?}
        
        Args:
            options: List of options to choose from
            context: Context for decision
        
        Returns:
            Dict with selected option and reasoning
        """
        if not options:
            return {"error": "No options provided"}
        
        if len(options) == 1:
            return {
                "selected": options[0],
                "confidence": 1.0,
                "reasoning": "Only one option available"
            }
        
        if not self.learnings:
            # No learnings - pick first option
            return {
                "selected": options[0],
                "confidence": 0.0,
                "reasoning": "No learnings - random selection"
            }
        
        # Score each option
        scored = []
        for opt in options:
            confidence = 0.5
            
            # If option has a strategy, use its effectiveness
            if "strategy" in opt:
                strat_score = self.learnings.index.get("strategy_effectiveness", {}).get(opt["strategy"], 0)
                confidence = min(1.0, abs(strat_score) / 3)
            
            # If option has a learning_id, use its confidence
            if "learning_id" in opt:
                learning_conf = self.learnings.get_confidence_score(opt["learning_id"])
                confidence = max(confidence, learning_conf)
            
            scored.append((opt, confidence))
        
        # Sort by confidence
        scored.sort(key=lambda x: -x[1])
        
        return {
            "selected": scored[0][0],
            "confidence": scored[0][1],
            "reasoning": f"Highest confidence ({scored[0][1]:.2f}) among {len(options)} options",
            "all_options": [{"option": s[0].get("name", s[0].get("id")), "confidence": s[1]} for s in scored]
        }
    
    def get_decision_context(self, agent: str = "Sir HazeClaw") -> Dict:
        """
        Get full decision context for an agent.
        
        Includes:
        - Recommended actions
        - Top strategies
        - Recent learnings
        - Strategy effectiveness
        """
        if not self.learnings:
            return {"error": "LearningsService unavailable"}
        
        ctx = self.learnings.get_agent_context(agent)
        
        # Add next actions for common contexts
        next_actions = {}
        for context in ["pattern_matching", "score_optimization", "learning_optimization"]:
            next_actions[context] = self.get_next_action(context)
        
        return {
            "agent": agent,
            "recommended_actions": next_actions,
            "top_strategies": ctx.get("top_strategies", []),
            "recent_learnings": ctx.get("learnings", [])[:5],
            "strategy_effectiveness": self.learnings.index.get("strategy_effectiveness", {}),
            "timestamp": datetime.utcnow().isoformat()
        }


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  decision_engine.py decide --context <context>")
        print("  decision_engine.py strategy --task <task>")
        print("  decision_engine.py context --agent <agent>")
        print("  decision_engine.py confidence --id <learning_id>")
        sys.exit(1)
    
    engine = DecisionEngine()
    cmd = sys.argv[1]
    
    if cmd == "decide":
        context = "general"
        for i, arg in enumerate(sys.argv):
            if arg == "--context" and i+1 < len(sys.argv):
                context = sys.argv[i+1]
        result = engine.get_next_action(context)
        print(json.dumps(result, indent=2))
    
    elif cmd == "strategy":
        task = "explore"
        for i, arg in enumerate(sys.argv):
            if arg == "--task" and i+1 < len(sys.argv):
                task = sys.argv[i+1]
        result = engine.get_strategy_for_task(task)
        print(json.dumps(result, indent=2))
    
    elif cmd == "context":
        agent = "Sir HazeClaw"
        for i, arg in enumerate(sys.argv):
            if arg == "--agent" and i+1 < len(sys.argv):
                agent = sys.argv[i+1]
        result = engine.get_decision_context(agent)
        print(json.dumps(result, indent=2, default=str))
    
    elif cmd == "confidence":
        if LearningsService:
            ls = LearningsService()
            for i, arg in enumerate(sys.argv):
                if arg == "--id" and i+1 < len(sys.argv):
                    lid = sys.argv[i+1]
                    conf = ls.get_confidence_score(lid)
                    print(f"Confidence for {lid}: {conf}")
        else:
            print("LearningsService unavailable")
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()

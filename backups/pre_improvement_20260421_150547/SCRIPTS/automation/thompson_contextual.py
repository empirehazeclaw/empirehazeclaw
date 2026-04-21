#!/usr/bin/env python3
"""
Contextual Thompson Sampling — Sir HazeClaw Phase 4 Enhancement
===============================================================
Thompson Sampling with contextual features for better action selection.

Based on research:
- Contextual Bandits (Li et al., 2010) — Thompson Sampling with context
- Generator-Mediated Bandits (2025) — Contextual features improve selection
- Feel-Good Thompson Sampling (2024) — Better posterior sampling

Key Innovation:
- Instead of ONE Beta distribution per category
- We track Beta distributions CONDITIONED on context features:
  - time_of_day (morning/afternoon/evening/night)
  - day_of_week (weekday/weekend)
  - task_complexity (simple/medium/complex)
  - error_type category

This allows the system to learn:
- "Mornings are good for coding tasks"
- "Weekdays are better for cron fixes"
- "Complex tasks work better in afternoon"

Usage:
    python3 thompson_contextual.py --stats
    python3 thompson_contextual.py --sample --context '{"time_of_day":"morning","task_type":"cron_fix"}'
    python3 thompson_contextual.py --update --category cron_fix --success --context '{"time_of_day":"morning"}'

Phase 4 of Self-Improvement Plan
"""

import os
import sys
import json
import math
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
THOMPSON_CONTEXT_FILE = DATA_DIR / "thompson_context.json"

# Context feature definitions
TIME_BUCKETS = {
    "morning": (6, 12),
    "afternoon": (12, 17),
    "evening": (17, 21),
    "night": (21, 6)
}

DAY_BUCKETS = {
    "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "weekend": ["Saturday", "Sunday"]
}

TASK_COMPLEXITY = {
    "simple": ["script_fix", "config_update", "typo_fix"],
    "medium": ["cron_fix", "api_fix", "error_handling"],
    "complex": ["architecture", "refactor", "integration", "learning_loop"]
}


def get_time_bucket(dt: datetime = None) -> str:
    """Get current time bucket."""
    dt = dt or datetime.now()
    hour = dt.hour
    for bucket, (start, end) in TIME_BUCKETS.items():
        if start <= hour < end:
            return bucket
    return "night"


def get_day_bucket(dt: datetime = None) -> str:
    """Get current day bucket."""
    dt = dt or datetime.now()
    day = dt.strftime("%A")
    for bucket, days in DAY_BUCKETS.items():
        if day in days:
            return bucket
    return "weekday"


def get_task_complexity(task_type: str) -> str:
    """Estimate task complexity from type."""
    task_lower = task_type.lower()
    for complexity, keywords in TASK_COMPLEXITY.items():
        if any(kw in task_lower for kw in keywords):
            return complexity
    return "medium"


def load_context_rewards() -> Dict:
    """Load contextual Thompson rewards."""
    if THOMPSON_CONTEXT_FILE.exists():
        try:
            return json.load(open(THOMPSON_CONTEXT_FILE))
        except:
            pass
    return {
        "rewards": {},  # {category: {context_key: {alpha, beta, success, total}}}
        "contexts": {},  # {context_key: {feature: value}}
        "version": "1.0"
    }


def save_context_rewards(data: Dict):
    """Save contextual Thompson rewards."""
    THOMPSON_CONTEXT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(THOMPSON_CONTEXT_FILE, "w") as f:
        json.dump(data, f, indent=2)


def build_context_key(context: Dict) -> str:
    """
    Build a deterministic context key from context features.
    
    Features:
    - time_of_day: morning/afternoon/evening/night
    - day_bucket: weekday/weekend
    - task_complexity: simple/medium/complex
    
    Returns something like: "morning_weekday_medium"
    """
    time = context.get("time_of_day", get_time_bucket())
    day = context.get("day_bucket", get_day_bucket())
    complexity = context.get("task_complexity", "medium")
    return f"{time}_{day}_{complexity}"


def sample_with_context(category: str, context: Dict, candidates: List[Dict]) -> List[Dict]:
    """
    Thompson Sampling with contextual features.
    
    For each candidate:
    1. Get base Beta distribution (from all-time rewards)
    2. Get contextual Beta distribution (from similar past contexts)
    3. Combine them (contextual has more weight for similar contexts)
    4. Sample from combined distribution
    
    Args:
        category: Current category being selected
        context: Context features (time_of_day, task_complexity, etc.)
        candidates: List of candidate actions with metadata
    
    Returns:
        List of candidates with Thompson samples, sorted by score
    """
    data = load_context_rewards()
    context_key = build_context_key(context)
    
    samples = []
    total_trials = sum(
        data["rewards"].get(c.get("category", "unknown"), {}).get("_total", {}).get("total", 1)
        for c in candidates
    ) + 1
    
    for c in candidates:
        cat = c.get("category", "unknown")
        
        # Base distribution (all-time)
        base_alpha, base_beta = 1, 1
        if cat in data["rewards"]:
            base_alpha = data["rewards"][cat].get("_total", {}).get("alpha", 1)
            base_beta = data["rewards"][cat].get("_total", {}).get("beta", 1)
        
        # Contextual distribution (from similar contexts)
        # Weight by how similar the context is
        ctx_alpha, ctx_beta = base_alpha, base_beta
        
        # Check for exact context match
        if cat in data["rewards"] and context_key in data["rewards"][cat]:
            ctx_data = data["rewards"][cat][context_key]
            ctx_alpha = ctx_data.get("alpha", 1)
            ctx_beta = ctx_data.get("beta", 1)
        
        # Combine: contextual has 0.7 weight if we have data, else use base
        if ctx_alpha > 1 or ctx_beta > 1:
            # We have contextual data - blend it
            alpha = 0.3 * base_alpha + 0.7 * ctx_alpha
            beta = 0.3 * base_beta + 0.7 * ctx_beta
        else:
            # No contextual data - use base
            alpha, beta = base_alpha, base_beta
        
        # Thompson Sampling: Sample from Beta distribution
        try:
            thompson_sample = random.betavariate(max(0.1, alpha), max(0.1, beta))
        except:
            thompson_sample = 0.5
        
        # UCB1 bonus for unexplored actions
        cat_trials = data["rewards"].get(cat, {}).get("_total", {}).get("total", 0)
        if cat_trials > 0:
            mean = (alpha - 1) / max(1, cat_trials)
            ucb_bonus = math.sqrt(2 * math.log(total_trials) / cat_trials)
        else:
            mean = 0.5
            ucb_bonus = 1.0  # High bonus for never-tried
        
        # Context match bonus: if this context worked well before
        ctx_bonus = 0
        consecutive_failures = 0
        
        # Check exact context match first
        if cat in data["rewards"] and context_key in data["rewards"][cat]:
            ctx_data = data["rewards"][cat][context_key]
            ctx_trials = ctx_data.get("total", 0)
            consecutive_failures = ctx_data.get("_consecutive_failures", 0)
            if ctx_trials >= 3:  # Only if we have enough data
                ctx_success_rate = (ctx_data.get("success", 0) / ctx_trials)
                ctx_bonus = (ctx_success_rate - 0.5) * 0.2  # ±0.1 bonus
        else:
            # No exact context match - check category-level consecutive failures
            # This catches cases where same category keeps failing in different contexts
            cat_consec_failures = data["rewards"].get(cat, {}).get("_consecutive_failures", 0)
            if cat_consec_failures > consecutive_failures:
                consecutive_failures = cat_consec_failures
        
        # Also check category-level success rate for ctx_bonus if no exact context
        if ctx_bonus == 0 and cat in data["rewards"]:
            cat_total = data["rewards"][cat].get("_total", {})
            cat_trials = cat_total.get("total", 0)
            if cat_trials >= 5:
                cat_success_rate = cat_total.get("success", 0) / cat_trials
                ctx_bonus = (cat_success_rate - 0.5) * 0.15  # Slight bonus/penalty from category
        
        # Penalty for consecutive failures: if 2+ failures in same context, heavily penalize
        failure_penalty = 0
        if consecutive_failures >= 2:
            failure_penalty = -0.3 * (consecutive_failures - 1)  # -0.3 per extra failure after 2
        
        # Combine with failure penalty
        final_sample = thompson_sample + ucb_bonus + ctx_bonus + failure_penalty + c.get("priority_base", 0)
        
        samples.append({
            "candidate": c,
            "thompson_sample": thompson_sample,
            "ucb_bonus": ucb_bonus,
            "ctx_bonus": ctx_bonus,
            "failure_penalty": failure_penalty,
            "consecutive_failures": consecutive_failures,
            "final_sample": final_sample,
            "context_key": context_key
        })
    
    # Sort by final sample
    samples.sort(key=lambda x: x["final_sample"], reverse=True)
    return samples


def update_reward(category: str, success: bool, context: Dict):
    """
    Update Thompson rewards with contextual information.
    
    Key insight:
    - Successes: Strong positive signal (alpha += 1)
    - Failures: After 2+ consecutive failures in same context, START learning (beta += 1)
    - This prevents the system from getting stuck on unsolvable problems
    
    Args:
        category: The category/action that was executed
        success: Whether the validation passed
        context: Context features at time of execution
    """
    data = load_context_rewards()
    context_key = build_context_key(context)
    
    # Initialize if needed
    if category not in data["rewards"]:
        data["rewards"][category] = {"_total": {"alpha": 1, "beta": 1, "success": 0, "total": 0}, "_consecutive_failures": 0}
    
    if context_key not in data["rewards"][category]:
        data["rewards"][category][context_key] = {"alpha": 1, "beta": 1, "success": 0, "total": 0, "_consecutive_failures": 0}
    
    # Get consecutive failures for this context
    prev_failures = data["rewards"][category][context_key].get("_consecutive_failures", 0)
    
    if success:
        # Reset consecutive failures on success
        data["rewards"][category]["_consecutive_failures"] = 0
        data["rewards"][category][context_key]["_consecutive_failures"] = 0
        
        # Update total (base) distribution - STRONG positive
        total = data["rewards"][category]["_total"]
        total["alpha"] = total.get("alpha", 1) + 1
        total["success"] = total.get("success", 0) + 1
        total["total"] = total.get("total", 0) + 1
        
        # Update contextual distribution - STRONG positive
        ctx = data["rewards"][category][context_key]
        ctx["alpha"] = ctx.get("alpha", 1) + 1
        ctx["success"] = ctx.get("success", 0) + 1
        ctx["total"] = ctx.get("total", 0) + 1
    else:
        # Increment consecutive failures
        prev_failures += 1
        data["rewards"][category]["_consecutive_failures"] = prev_failures
        data["rewards"][category][context_key]["_consecutive_failures"] = prev_failures
        
        # Only start learning from failures AFTER 2 consecutive failures
        # This prevents early termination of promising but slow-starting approaches
        if prev_failures >= 2:
            # Update total (base) distribution - WEAK negative
            total = data["rewards"][category]["_total"]
            total["beta"] = total.get("beta", 1) + 0.5  # Half weight
            total["total"] = total.get("total", 0) + 1
            
            # Update contextual distribution - WEAK negative
            ctx = data["rewards"][category][context_key]
            ctx["beta"] = ctx.get("beta", 1) + 0.5
            ctx["total"] = ctx.get("total", 0) + 1
        else:
            # Just increment total, no beta update yet
            total = data["rewards"][category]["_total"]
            total["total"] = total.get("total", 0) + 1
            ctx = data["rewards"][category][context_key]
            ctx["total"] = ctx.get("total", 0) + 1
    
    # Store context features for reference
    if context_key not in data["contexts"]:
        data["contexts"][context_key] = context
    
    save_context_rewards(data)
    
    return prev_failures  # Return for logging


def get_stats() -> Dict:
    """Get contextual Thompson sampling statistics."""
    data = load_context_rewards()
    
    stats = {
        "categories": len(data.get("rewards", {})),
        "contexts": list(data.get("contexts", {}).keys()),
        "version": data.get("version", "unknown")
    }
    
    # Per-category stats
    cat_stats = {}
    for cat, cat_data in data.get("rewards", {}).items():
        total = cat_data.get("_total", {})
        cat_stats[cat] = {
            "alpha": total.get("alpha", 1),
            "beta": total.get("beta", 1),
            "success": total.get("success", 0),
            "total": total.get("total", 0),
            "success_rate": total.get("success", 0) / max(1, total.get("total", 1)),
            "contexts": len([k for k in cat_data.keys() if not k.startswith("_")])
        }
    stats["categories"] = cat_stats
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Contextual Thompson Sampling")
    subparsers = parser.add_subparsers(dest="command")
    
    # Stats command
    subparsers.add_parser("stats", help="Show Thompson sampling statistics")
    
    # Sample command
    sample_parser = subparsers.add_parser("sample", help="Sample with context")
    sample_parser.add_argument("--context", required=True, help="JSON context object")
    sample_parser.add_argument("--candidates", required=True, help="JSON list of candidates")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update rewards")
    update_parser.add_argument("--category", required=True)
    update_parser.add_argument("--success", action="store_true")
    update_parser.add_argument("--context", required=True, help="JSON context object")
    
    args = parser.parse_args()
    
    if args.command == "stats":
        stats = get_stats()
        print("=== Contextual Thompson Sampling Stats ===")
        print(f"Version: {stats['version']}")
        print(f"Known contexts: {stats['contexts']}")
        print(f"\nCategories:")
        for cat, cat_stats in stats["categories"].items():
            print(f"  {cat}:")
            print(f"    Success rate: {cat_stats['success_rate']:.2%} ({cat_stats['success']}/{cat_stats['total']})")
            print(f"    Beta({cat_stats['alpha']:.1f}, {cat_stats['beta']:.1f})")
            print(f"    Contexts tracked: {cat_stats['contexts']}")
    
    elif args.command == "sample":
        context = json.loads(args.context)
        candidates = json.loads(args.candidates)
        samples = sample_with_context("general", context, candidates)
        print("=== Thompson Sampling Results ===")
        for i, s in enumerate(samples[:5]):
            print(f"{i+1}. {s['final_sample']:.3f} [TS={s['thompson_sample']:.2f}, UCB=+{s['ucb_bonus']:.2f}, CTX=+{s['ctx_bonus']:.2f}]")
            print(f"   {s['candidate'].get('title', s['candidate'].get('name', 'unknown'))[:50]}")
            print(f"   Context: {s['context_key']}")
    
    elif args.command == "update":
        context = json.loads(args.context)
        update_reward(args.category, args.success, context)
        print(f"Updated {args.category}: success={args.success}, context={build_context_key(context)}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

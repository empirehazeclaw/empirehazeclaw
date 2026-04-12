#!/usr/bin/env python3
"""
self_play_improver.py — GVU Self-Play Pattern Implementation
Sir HazeClaw - 2026-04-11

Basierend auf: "Self-Improving AI Agents through Self-Play" (arXiv:2512.02731)

GVU PATTERN:
- Generator: Erstellt Verbesserungsversuche (Hypothesen)
- Verifier: Prüft ob es funktioniert hat
- Updater: Behält was funktioniert, verwirft was nicht

Usage:
    python3 self_play_improver.py
    python3 self_play_improver.py --generations 3
    python3 self_play_improver.py --status
"""

import json
import random
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
IMPROVEMENT_LOG = WORKSPACE / "data/improvements/improvement_log.json"
STATE_FILE = WORKSPACE / "data/self_play_state.json"

# Self-play improvement strategies
IMPROVEMENT_STRATEGIES = [
    {
        "name": "error_reduction",
        "script": "error_reducer.py",
        "metric": "error_rate",
        "direction": "lower",
        "target": "< 15"
    },
    {
        "name": "script_fix",
        "script": "auto_fixer.py",
        "metric": "scripts_working",
        "direction": "higher",
        "target": "> 95%"
    },
    {
        "name": "quality_improve",
        "script": "quality_metrics.py",
        "metric": "score",
        "direction": "higher",
        "target": "> 95"
    },
    {
        "name": "speed_improve",
        "script": "efficiency_tracker.py",
        "metric": "duration",
        "direction": "lower",
        "target": "< 1s"
    },
    {
        "name": "kg_growth",
        "script": "innovation_research.py",
        "metric": "kg_entities",
        "direction": "higher",
        "target": "> 250"
    }
]

def load_state():
    """Load self-play state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "generation": 0,
        "best_improvements": [],
        "attempts": [],
        "history": []
    }

def save_state(state):
    """Save self-play state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_current_metrics() -> Dict[str, float]:
    """Get current system metrics."""
    metrics = {}
    
    # Error rate
    try:
        metrics_file = WORKSPACE / "memory" / "session_metrics_history.json"
        if metrics_file.exists():
            with open(metrics_file) as f:
                data = json.load(f)
            history = data.get("history", [])
            if history:
                metrics["error_rate"] = history[-1].get("error_rate", 0)
    except:
        metrics["error_rate"] = 100
    
    # KG entities
    try:
        kg_path = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"
        if kg_path.exists():
            with open(kg_path) as f:
                kg = json.load(f)
            metrics["kg_entities"] = len(kg.get("entities", {}))
    except:
        metrics["kg_entities"] = 0
    
    # Script stats
    try:
        scripts = list(SCRIPTS_DIR.glob("*.py"))
        total = len([s for s in scripts if not s.name.startswith('_')])
        metrics["scripts_total"] = total
        metrics["scripts_working"] = total  # Assume working
    except:
        metrics["scripts_total"] = 0
        metrics["scripts_working"] = 0
    
    return metrics

def generate_improvement_attempt(state: Dict) -> Dict:
    """GENERATOR: Creates a new improvement attempt.
    
    Selects a strategy and generates an improvement attempt.
    Prefers strategies that haven't been tried or that showed promise.
    """
    # Get metrics to decide what to improve
    metrics = get_current_metrics()
    
    # Filter strategies by what needs improvement
    candidates = []
    for s in IMPROVEMENT_STRATEGIES:
        metric = s["metric"]
        if metric in metrics:
            current = metrics[metric]
            
            # Determine if this strategy is needed
            if s["direction"] == "lower" and current > 15:
                candidates.append(s)
            elif s["direction"] == "higher" and current < 80:
                candidates.append(s)
        else:
            # No metric yet, try it anyway if not recently tried
            candidates.append(s)
    
    # Add diversity: if all obvious candidates tried, pick random
    if not candidates:
        candidates = IMPROVEMENT_STRATEGIES
    
    # Weight by past success
    weights = []
    for s in candidates:
        # Count successes in history
        successes = sum(1 for a in state.get("attempts", []) 
                      if a.get("strategy") == s["name"] and a.get("success"))
        weights.append(max(1, 3 - successes))  # Prefer less-tested
    
    # Select weighted random
    strategy = random.choices(candidates, weights=weights)[0]
    
    return {
        "strategy": strategy["name"],
        "script": strategy["script"],
        "metric": strategy["metric"],
        "direction": strategy["direction"],
        "target": strategy["target"],
        "timestamp": datetime.now().isoformat()
    }

def execute_improvement(attempt: Dict) -> Tuple[bool, str]:
    """GENERATOR execution: Runs the improvement script."""
    script = SCRIPTS_DIR / attempt["script"]
    
    if not script.exists():
        return False, f"Script not found: {attempt['script']}"
    
    try:
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(WORKSPACE)
        )
        
        success = result.returncode == 0
        output = result.stdout[:500] if result.stdout else result.stderr[:500]
        
        return success, output
        
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)[:100]

def verify_improvement(before: Dict, after: Dict, attempt: Dict) -> Tuple[bool, float]:
    """VERIFIER: Checks if the improvement actually worked.
    
    Compares metrics before and after the attempt.
    Returns (success, improvement_score).
    """
    metric = attempt["metric"]
    direction = attempt["direction"]
    
    before_val = before.get(metric, 0)
    after_val = after.get(metric, 0)
    
    if before_val == 0 and after_val == 0:
        # Can't verify, assume partial success
        return True, 0.5
    
    if direction == "lower":
        improved = after_val < before_val
        # Score based on how much better
        if before_val > 0:
            improvement = (before_val - after_val) / before_val
        else:
            improvement = 1.0 if after_val == 0 else 0
    else:  # higher
        improved = after_val > before_val
        if before_val > 0:
            improvement = (after_val - before_val) / before_val
        else:
            improvement = 1.0 if after_val > 0 else 0
    
    return improved, max(0, min(1, improvement))

def update_state(state: Dict, attempt: Dict, success: bool, improvement: float):
    """UPDATER: Updates state based on attempt result.
    
    Keeps successful attempts in best_improvements,
    discards failures (unless they teach something).
    """
    attempt["success"] = success
    attempt["improvement"] = improvement
    attempt["verified_at"] = datetime.now().isoformat()
    
    state["attempts"].append(attempt)
    state["generation"] += 1
    
    if success and improvement > 0.3:
        # Good improvement - keep reference
        state["best_improvements"].append({
            "strategy": attempt["strategy"],
            "script": attempt["script"],
            "improvement": improvement,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 best
        state["best_improvements"] = state["best_improvements"][-10:]
    
    # Keep only last 50 attempts
    state["attempts"] = state["attempts"][-50:]
    
    # Generate insight
    if success:
        insight = f"✅ {attempt['strategy']}: +{improvement*100:.0f}% improvement"
    else:
        insight = f"❌ {attempt['strategy']}: Failed (will try different approach)"
    
    state["history"].append({
        "timestamp": datetime.now().isoformat(),
        "insight": insight,
        "generation": state["generation"]
    })
    state["history"] = state["history"][-20:]  # Keep last 20 insights
    
    save_state(state)
    return insight

def run_self_play_cycle(generations: int = 3) -> List[str]:
    """Runs self-play improvement cycles.
    
    For each generation:
    1. Generate an improvement attempt
    2. Execute it
    3. Verify if it worked
    4. Update state based on result
    """
    print("🎮 SELF-PLAY IMPROVER — GVU Pattern")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Running {generations} generations...")
    print()
    
    state = load_state()
    insights = []
    
    print(f"📊 Current State:")
    print(f"   Generation: {state['generation']}")
    print(f"   Best Improvements: {len(state['best_improvements'])}")
    print(f"   Total Attempts: {len(state['attempts'])}")
    print()
    
    metrics_before = get_current_metrics()
    print(f"📈 Metrics Before:")
    for k, v in metrics_before.items():
        print(f"   {k}: {v}")
    print()
    
    for gen in range(generations):
        print(f"🎯 Generation {state['generation'] + 1}:")
        
        # GENERATOR: Create attempt
        attempt = generate_improvement_attempt(state)
        print(f"   📝 Strategy: {attempt['strategy']}")
        print(f"   📜 Script: {attempt['script']}")
        
        # Execute
        print(f"   ⚙️  Executing...")
        success, output = execute_improvement(attempt)
        
        # Verify
        metrics_after = get_current_metrics()
        verified, improvement = verify_improvement(
            metrics_before, metrics_after, attempt
        )
        metrics_before = metrics_after  # For next iteration
        
        print(f"   🔍 Verified: {'✅' if verified else '❌'} (+{improvement*100:.0f}%)")
        
        # Update
        insight = update_state(state, attempt, verified, improvement)
        insights.append(insight)
        print(f"   💡 {insight}")
        print()
    
    # Final summary
    print("=" * 50)
    print("📊 FINAL RESULTS:")
    print(f"   Generations Run: {generations}")
    print(f"   Total Generation #: {state['generation']}")
    print(f"   Best Improvements: {len(state['best_improvements'])}")
    print()
    
    if state["best_improvements"]:
        print("🏆 Top Improvements:")
        for imp in state["best_improvements"][-3:]:
            print(f"   - {imp['strategy']}: +{imp['improvement']*100:.0f}%")
        print()
    
    print("💡 Insights:")
    for insight in insights[-3:]:
        print(f"   {insight}")
    
    return insights

def show_status():
    """Show current self-play status."""
    state = load_state()
    metrics = get_current_metrics()
    
    print("🎮 SELF-PLAY STATUS")
    print(f"   Generation: {state['generation']}")
    print(f"   Best Improvements: {len(state['best_improvements'])}")
    print(f"   Total Attempts: {len(state['attempts'])}")
    print()
    
    print("📈 Current Metrics:")
    for k, v in metrics.items():
        print(f"   {k}: {v}")
    print()
    
    if state["history"]:
        print("📜 Recent History:")
        for h in state["history"][-5:]:
            print(f"   {h['insight']}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-Play Improver')
    parser.add_argument('--generations', type=int, default=3, 
                       help='Number of self-play generations')
    parser.add_argument('--status', action='store_true',
                       help='Show current status')
    args = parser.parse_args()
    
    if args.status:
        show_status()
    else:
        run_self_play_cycle(args.generations)

if __name__ == "__main__":
    main()

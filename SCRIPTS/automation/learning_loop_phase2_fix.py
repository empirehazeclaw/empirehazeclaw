#!/usr/bin/env python3
"""
Learning Loop Phase 2 Fix — Sir HazeClaw
Fixes: Epsilon Schedule + Thompson Sampling + State Update

Usage:
    python3 learning_loop_phase2_fix.py [--dry-run]
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data/learning_loop"
PATTERNS_FILE = DATA_DIR / "learning_loop/patterns.json"
STATE_FILE = WORKSPACE / "data/learning_loop_state.json"
THOMPSON_FILE = DATA_DIR / "learning_loop/thompson_rewards.json"

DRY_RUN = "--dry-run" in __import__("sys").argv


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    if DRY_RUN:
        print(f"  [DRY-RUN] Would save {path}")
        return
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_epsilon(state: dict) -> float:
    """
    Dynamic epsilon mit Plateau-Erkennung.
    
    Best Practices (NeurIPS 2025 / Thompson Sampling):
    - Lineare Decay ist NICHT gut
    - Bei Plateau: Epsilon erhöhen (mehr exploration)
    - Exponentiell mit Annealing + Plateau-Bonus
    """
    iteration = state.get("iteration", 1)
    score_history = state.get("score_history", [])
    
    # Base annealing: epsilon * 0.99 pro iteration
    base_epsilon = max(0.15, 0.35 * (0.99 ** iteration))
    
    # Plateau detection: wenn std < 0.01 über letzte 20 Iterationen
    if len(score_history) >= 20:
        recent = score_history[-20:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        std = variance ** 0.5
        
        if std < 0.01:
            # Plateau! Erhöhe exploration
            plateau_bonus = min(0.25, (iteration - 100) * 0.001)
            return min(0.60, base_epsilon + plateau_bonus)
    
    return base_epsilon


def init_thompson_rewards(patterns: list) -> dict:
    """
    Initialize Thompson rewards für alle Categories.
    
    Beta-Verteilung pro Category:
    - successes: wie oft diese Category positive Results hatte
    - failures: wie oft negative Results
    
    Für neue Categories: prior (2, 1) = leicht optimistisch
    """
    # Load existing rewards
    existing = {}
    if THOMPSON_FILE.exists():
        existing = load_json(THOMPSON_FILE)
    
    # Collect all categories from patterns
    categories = set()
    for p in patterns:
        cat = p.get("category", "general")
        categories.add(cat)
    
    # Add categories from state if exists
    state = {}
    if STATE_FILE.exists():
        state = load_json(STATE_FILE)
        if "thompson_rewards" in state:
            for cat in state["thompson_rewards"]:
                categories.add(cat)
    
    # Initialize missing categories with default prior (2, 1)
    rewards = {}
    for cat in categories:
        if cat in existing:
            rewards[cat] = existing[cat]
        else:
            rewards[cat] = {"successes": 2, "failures": 1}
    
    return rewards


def update_state_epsilon(state: dict) -> dict:
    """Compute und speichere new epsilon in state."""
    new_epsilon = get_epsilon(state)
    old_epsilon = state.get("epsilon", "unknown")
    state["epsilon"] = new_epsilon
    
    print(f"📊 Epsilon Update:")
    print(f"  iteration: {state.get('iteration', '?')}")
    print(f"  old epsilon: {old_epsilon}")
    print(f"  new epsilon: {new_epsilon:.4f}")
    print(f"  score_history: {len(state.get('score_history', []))} entries")
    
    # Plateau info
    score_history = state.get("score_history", [])
    if len(score_history) >= 20:
        recent = score_history[-20:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        std = (variance ** 0.5) * 100  # in percent
        print(f"  recent std: {std:.3f}% (Plateau if < 1%)")
    
    return state


def main():
    print("=" * 60)
    print("🔧 Learning Loop Phase 2 Fix")
    print("=" * 60)
    
    # 1. Load patterns and init Thompson rewards
    print("\n📊 Thompson Rewards — Category Initialization")
    patterns_data = load_json(PATTERNS_FILE)
    patterns = patterns_data.get("patterns", [])
    active_patterns = [p for p in patterns if p.get("active") is not False]
    
    rewards = init_thompson_rewards(active_patterns)
    print(f"  Total categories: {len(rewards)}")
    print(f"  Active patterns: {len(active_patterns)}")
    
    for cat, data in sorted(rewards.items()):
        s = data.get("successes", 0)
        f = data.get("failures", 0)
        total = s + f
        print(f"  - {cat}: successes={s}, failures={f}, total={total}")
    
    # Save Thompson rewards
    if not DRY_RUN:
        THOMPSON_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_json(THOMPSON_FILE, rewards)
    print(f"\n✅ Thompson rewards saved to {THOMPSON_FILE}")
    
    # 2. Update state with new epsilon
    print("\n📊 State — Epsilon Update")
    state = load_json(STATE_FILE)
    state = update_state_epsilon(state)
    
    # Add iteration metadata
    state["phase2_fix_applied"] = datetime.utcnow().isoformat() + "Z"
    state["epsilon_schedule"] = "exponential_annealing_with_plateau_detection"
    
    save_json(STATE_FILE, state)
    print(f"\n✅ State saved: epsilon={state['epsilon']:.4f}")
    
    # 3. Show summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY — Changes Made")
    print("=" * 60)
    print("""
1. ✅ Thompson Sampling Categories Initialisiert:
   - Alle Categories aus Patterns bekommen Prior (2, 1)
   - Beta-Verteilung für probabilistic selection
   - File: data/learning_loop/thompson_rewards.json

2. ✅ Epsilon Schedule Gefixt:
   - Alt: max(0.10, 0.3 - iteration * 0.01) = 0.10 bei iter 131
   - Neu: Exponential Annealing + Plateau Detection
     * base: 0.35 * 0.99^iteration (min 0.15)
     * plateau bonus: wenn std < 1% über 20 iterations → +0.25
     * max: 0.60

3. ✅ State Aktualisiert:
   - epsilon in state file geschrieben
   - phase2_fix_applied timestamp
   - epsilon_schedule version markiert
""")


if __name__ == "__main__":
    main()

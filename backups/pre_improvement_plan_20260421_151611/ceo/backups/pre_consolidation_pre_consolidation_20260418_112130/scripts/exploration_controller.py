#!/usr/bin/env python3
"""
Exploration Controller — Phase 3, Day 3
=========================================
Adaptive exploration controller using:
- ε-greedy with adaptive decay
- Softmax exploration (better than ε-greedy)
- Stagnation detection
- Strategy selection

Usage:
    python3 exploration_controller.py --select          # Select best strategy for next task
    python3 exploration_controller.py --update <s> <r> # Update strategy reward
    python3 exploration_controller.py --status          # Show controller status
    python3 exploration_controller.py --reset           # Reset controller
    python3 exploration_controller.py --methods        # Compare exploration methods
"""

import json
import argparse
import sys
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
CONTROLLER_FILE = WORKSPACE / "memory" / "evaluations" / "exploration_controller.json"

# Default configuration
DEFAULT_CONFIG = {
    "method": "softmax",           # "epsilon_greedy" or "softmax"
    "epsilon": 0.1,                # For epsilon-greedy
    "epsilon_decay": 0.995,         # Decay rate per episode
    "epsilon_min": 0.01,            # Minimum epsilon
    "temperature": 1.0,            # For softmax
    "temperature_decay": 0.99,      # Softmax temperature decay
    "temperature_min": 0.1,
    "learning_rate": 0.1,          # For Q-value updates
    "discount_factor": 0.9,         # Future reward discount
    "stagnation_window": 10,        # Window for stagnation detection
    "stagnation_threshold": 0.05,  # Max change to trigger stagnation
}

def load_controller():
    if CONTROLLER_FILE.exists():
        return json.loads(CONTROLLER_FILE.read_text())
    
    return {
        "config": DEFAULT_CONFIG.copy(),
        "strategies": {},
        "episode_count": 0,
        "total_reward": 0.0,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "stagnation_count": 0,
        "version": "1.0"
    }

def save_controller(controller):
    CONTROLLER_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTROLLER_FILE.write_text(json.dumps(controller, indent=2))

def init_strategy(controller, strategy_name: str):
    """Initialize a strategy with Q-values."""
    if strategy_name not in controller["strategies"]:
        controller["strategies"][strategy_name] = {
            "name": strategy_name,
            "q_value": 0.5,          # Initial Q-value (uncertain)
            "visit_count": 0,
            "total_reward": 0.0,
            "last_reward": None,
            "history": []            # Last N rewards for stagnation
        }

def epsilon_greedy(controller, available_strategies: list = None) -> str:
    """Select strategy using ε-greedy."""
    config = controller["config"]
    epsilon = config["epsilon"]
    
    if available_strategies is None:
        available_strategies = list(controller["strategies"].keys())
    
    if not available_strategies:
        return "default_execution"
    
    # Ensure all strategies exist
    for s in available_strategies:
        init_strategy(controller, s)
    
    # Exploration
    if random.random() < epsilon:
        return random.choice(available_strategies)
    
    # Exploitation - pick best Q-value
    best = max(available_strategies, key=lambda s: controller["strategies"][s]["q_value"])
    return best

def softmax(controller, available_strategies: list = None) -> str:
    """Select strategy using Softmax exploration."""
    config = controller["config"]
    temperature = config["temperature"]
    
    if available_strategies is None:
        available_strategies = list(controller["strategies"].keys())
    
    if not available_strategies:
        return "default_execution"
    
    # Ensure all strategies exist
    for s in available_strategies:
        init_strategy(controller, s)
    
    # Calculate softmax probabilities
    q_values = {s: controller["strategies"][s]["q_value"] for s in available_strategies}
    
    # Softmax with temperature
    exp_q = {s: math.exp(q / max(temperature, 0.01)) for s, q in q_values.items()}
    sum_exp = sum(exp_q.values())
    probs = {s: exp_q[s] / sum_exp for s in available_strategies}
    
    # Random selection based on probabilities
    r = random.random()
    cumulative = 0.0
    for s in available_strategies:
        cumulative += probs[s]
        if r <= cumulative:
            return s
    
    return available_strategies[-1]  # Fallback

def ucb(controller, available_strategies: list = None, c: float = 1.414) -> str:
    """Select using Upper Confidence Bound."""
    if available_strategies is None:
        available_strategies = list(controller["strategies"].keys())
    
    if not available_strategies:
        return "default_execution"
    
    for s in available_strategies:
        init_strategy(controller, s)
    
    total_visits = sum(controller["strategies"][s]["visit_count"] for s in available_strategies)
    
    ucb_values = {}
    for s in available_strategies:
        strat = controller["strategies"][s]
        n = strat["visit_count"]
        if n == 0:
            ucb_values[s] = float('inf')  # Unexplored = high priority
        else:
            q = strat["q_value"]
            ucb = c * math.sqrt(math.log(total_visits) / n)
            ucb_values[s] = q + ucb
    
    return max(ucb_values, key=ucb_values.get)

def select_strategy(controller, available_strategies: list = None) -> dict:
    """Select a strategy using the configured method."""
    config = controller["config"]
    method = config["method"]
    
    if available_strategies is None:
        available_strategies = list(controller["strategies"].keys())
    
    if not available_strategies:
        # Return default if no strategies
        return {
            "strategy": "default_execution",
            "method": method,
            "epsilon": config.get("epsilon"),
            "temperature": config.get("temperature"),
            "q_value": 0.5,
            "reason": "no_strategies_available"
        }
    
    # Ensure all strategies exist
    for s in available_strategies:
        init_strategy(controller, s)
    
    # Select based on method
    if method == "epsilon_greedy":
        selected = epsilon_greedy(controller, available_strategies)
    elif method == "softmax":
        selected = softmax(controller, available_strategies)
    elif method == "ucb":
        selected = ucb(controller, available_strategies)
    else:
        selected = softmax(controller, available_strategies)  # Default
    
    strat_info = controller["strategies"][selected]
    
    return {
        "strategy": selected,
        "method": method,
        "epsilon": config.get("epsilon"),
        "temperature": config.get("temperature"),
        "q_value": strat_info["q_value"],
        "visit_count": strat_info["visit_count"],
        "reason": "selected"
    }

def update_strategy(controller, strategy_name: str, reward: float):
    """Update Q-value for a strategy after receiving reward."""
    config = controller["config"]
    
    init_strategy(controller, strategy_name)
    strat = controller["strategies"][strategy_name]
    
    # Q-learning update
    lr = config["learning_rate"]
    gamma = config["discount_factor"]
    
    old_q = strat["q_value"]
    # Get max Q for next state (for discount)
    max_next_q = max((s["q_value"] for s in controller["strategies"].values()), default=0)
    
    # Update Q-value
    new_q = old_q + lr * (reward + gamma * max_next_q - old_q)
    strat["q_value"] = max(0.0, min(1.0, new_q))  # Clamp to [0, 1]
    
    # Update stats
    strat["visit_count"] += 1
    strat["total_reward"] += reward
    strat["last_reward"] = reward
    strat["history"].append(reward)
    if len(strat["history"]) > config["stagnation_window"]:
        strat["history"] = strat["history"][-config["stagnation_window"]:]
    
    controller["episode_count"] += 1
    controller["total_reward"] += reward
    controller["last_update"] = datetime.now(timezone.utc).isoformat()
    
    # Check for stagnation
    check_stagnation(controller)
    
    # Decay epsilon or temperature
    if config["method"] == "epsilon_greedy":
        config["epsilon"] = max(config["epsilon_min"], config["epsilon"] * config["epsilon_decay"])
    else:
        config["temperature"] = max(config["temperature_min"], config["temperature"] * config["temperature_decay"])
    
    save_controller(controller)
    
    return {
        "strategy": strategy_name,
        "old_q": old_q,
        "new_q": new_q,
        "reward": reward,
        "epsilon": config.get("epsilon"),
        "temperature": config.get("temperature")
    }

def check_stagnation(controller):
    """Check if Q-values have stagnated."""
    if len(controller["strategies"]) < 2:
        return
    
    q_values = [s["q_value"] for s in controller["strategies"].values()]
    if len(q_values) < 2:
        return
    
    # Check if all Q-values are similar
    avg_q = sum(q_values) / len(q_values)
    max_diff = max(abs(q - avg_q) for q in q_values)
    
    if max_diff < controller["config"]["stagnation_threshold"]:
        controller["stagnation_count"] += 1
        
        # If stagnated, increase exploration temporarily
        if controller["config"]["method"] == "epsilon_greedy":
            controller["config"]["epsilon"] = min(0.3, controller["config"]["epsilon"] * 1.5)
        else:
            controller["config"]["temperature"] = min(2.0, controller["config"]["temperature"] * 1.5)
        
        print(f"[!] Stagnation detected ({controller['stagnation_count']} times). Increasing exploration.")
    else:
        controller["stagnation_count"] = 0

def compare_methods(controller, n_simulations: int = 1000) -> dict:
    """Compare exploration methods."""
    results = {
        "epsilon_greedy": [],
        "softmax": [],
        "ucb": []
    }
    
    # Simulate each method
    for method in ["epsilon_greedy", "softmax", "ucb"]:
        original_method = controller["config"]["method"]
        controller["config"]["method"] = method
        
        rewards = []
        for _ in range(n_simulations):
            # Simple reward simulation (some strategies better than others)
            strat = select_strategy(controller, ["strategy_a", "strategy_b", "strategy_c"])
            
            # Simulated reward (strategy_b is best, reward depends on selection)
            if strat["strategy"] == "strategy_b":
                reward = 0.9 + random.gauss(0, 0.1)
            elif strat["strategy"] == "strategy_a":
                reward = 0.5 + random.gauss(0, 0.1)
            else:
                reward = 0.3 + random.gauss(0, 0.1)
            
            rewards.append(reward)
            update_strategy(controller, strat["strategy"], reward)
        
        results[method] = {
            "avg_reward": sum(rewards) / len(rewards),
            "std_reward": (sum((r - sum(rewards)/len(rewards))**2 for r in rewards) / len(rewards)) ** 0.5
        }
        
        # Reset
        controller["strategies"] = {}
        controller["episode_count"] = 0
        controller["config"]["method"] = original_method
    
    return results

def show_status():
    """Show exploration controller status."""
    controller = load_controller()
    config = controller["config"]
    
    print(f"""
📊 Exploration Controller Status
{'=' * 45}
Method:        {config['method']}
Epsilon:       {config.get('epsilon', 'N/A'):.4f}
Temperature:    {config.get('temperature', 'N/A'):.4f}
Learning Rate: {config['learning_rate']}
Discount:       {config['discount_factor']}

Stagnation:    {controller['stagnation_count']} (threshold: {config['stagnation_threshold']})
Episodes:      {controller['episode_count']}
Total Reward:  {controller['total_reward']:.2f}

Strategies ({len(controller['strategies'])}):
""")
    
    for name, strat in sorted(controller["strategies"].items(), key=lambda x: -x[1]["q_value"]):
        avg_r = strat["total_reward"] / max(strat["visit_count"], 1)
        print(f"  {name}:")
        print(f"    Q-value: {strat['q_value']:.3f} | Visits: {strat['visit_count']} | Avg Reward: {avg_r:.3f}")

def reset_controller():
    """Reset the controller to initial state."""
    save_controller({
        "config": DEFAULT_CONFIG.copy(),
        "strategies": {},
        "episode_count": 0,
        "total_reward": 0.0,
        "last_update": datetime.now(timezone.utc).isoformat(),
        "stagnation_count": 0,
        "version": "1.0"
    })
    print("[*] Controller reset.")

def main():
    parser = argparse.ArgumentParser(description="Exploration Controller")
    parser.add_argument("--select", action="store_true", help="Select best strategy")
    parser.add_argument("--strategies", nargs="+", help="Available strategies for selection")
    parser.add_argument("--update", nargs=2, metavar=("STRATEGY", "REWARD"), help="Update strategy with reward")
    parser.add_argument("--status", action="store_true", help="Show controller status")
    parser.add_argument("--reset", action="store_true", help="Reset controller")
    parser.add_argument("--methods", action="store_true", help="Compare exploration methods")
    parser.add_argument("--set-method", metavar="METHOD", help="Set exploration method")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    controller = load_controller()
    
    if args.set_method:
        if args.set_method in ["epsilon_greedy", "softmax", "ucb"]:
            controller["config"]["method"] = args.set_method
            save_controller(controller)
            print(f"[*] Method set to {args.set_method}")
        else:
            print(f"[!] Invalid method: {args.set_method}")
    
    if args.status:
        show_status()
    
    if args.select:
        result = select_strategy(controller, args.strategies)
        print(f"\n🔀 Selected Strategy: {result['strategy']}")
        print(f"   Method: {result['method']}")
        print(f"   Q-value: {result['q_value']:.3f}")
        print(f"   Visits: {result.get('visit_count', 0)}")
        if result['method'] == 'epsilon_greedy':
            print(f"   Epsilon: {result.get('epsilon', 'N/A'):.4f}")
        else:
            print(f"   Temperature: {result.get('temperature', 'N/A'):.4f}")
    
    if args.update:
        strategy, reward_str = args.update
        try:
            reward = float(reward_str)
        except ValueError:
            print(f"[!] Invalid reward: {reward_str}")
            return
        
        result = update_strategy(controller, strategy, reward)
        print(f"\n✅ Updated {strategy}:")
        print(f"   Q-value: {result['old_q']:.3f} → {result['new_q']:.3f}")
        print(f"   Reward: {result['reward']}")
    
    if args.methods:
        print("\n🔬 Comparing exploration methods (1000 simulations)...")
        results = compare_methods(controller)
        print("\nResults:")
        for method, stats in sorted(results.items(), key=lambda x: -x[1]["avg_reward"]):
            print(f"  {method}: avg_reward={stats['avg_reward']:.3f}, std={stats['std_reward']:.3f}")
    
    if args.reset:
        reset_controller()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Break Score Plateau – Novelty‑Enhanced Q‑Learning
================================================
A simple 2‑D grid world environment with a Q‑learning agent.
The training script monitors the average reward per block of episodes.
If the reward stops improving (a plateau) a novelty‑bonus is introduced
to encourage exploration of rarely visited states, thus breaking the plateau.

Features
--------
* Fully self‑contained (stdlib only).
* Error handling with try/except around the main loop.
* argparse for optional hyper‑parameter tuning.
* Rolling‑average plateau detection.
* Novelty reward that depends on visit frequency.
"""

import argparse
import collections
import random
import sys
import time
from typing import Deque, Dict, List, Optional, Tuple

# ----------------------------------------------------------------------
# 1. Grid‑World Environment
# ----------------------------------------------------------------------
class GridWorld:
    """
    Simple grid world with a single target.
    States are integer positions (x, y).  The agent receives:
        +10 for reaching the target,
        -0.1 for each move (to encourage shortest paths).
    """

    def __init__(self, width: int = 5, height: int = 5, seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.target = (width - 1, height - 1)  # bottom‑right corner
        self.rng = random.Random(seed)
        self.state: Tuple[int, int] = (0, 0)

    def reset(self) -> Tuple[int, int]:
        """Return a random start position, avoiding the target."""
        self.state = (
            self.rng.randint(0, self.width - 1),
            self.rng.randint(0, self.height - 1),
        )
        # Ensure start != target
        while self.state == self.target:
            self.state = (
                self.rng.randint(0, self.width - 1),
                self.rng.randint(0, self.height - 1),
            )
        return self.state

    def step(self, action: int) -> Tuple[Tuple[int, int], float, bool]:
        """
        Perform one move.
        action: 0=up, 1=down, 2=left, 3=right.
        Returns (new_state, reward, done).
        """
        x, y = self.state
        if action == 0:
            y = max(0, y - 1)
        elif action == 1:
            y = min(self.height - 1, y + 1)
        elif action == 2:
            x = max(0, x - 1)
        elif action == 3:
            x = min(self.width - 1, x + 1)
        else:
            raise ValueError("Invalid action (0‑3).")

        self.state = (x, y)
        done = self.state == self.target
        reward = 10.0 if done else -0.1
        return self.state, reward, done

    @property
    def state_space(self) -> int:
        return self.width * self.height

    @property
    def action_space(self) -> int:
        return 4

    def state_to_index(self, state: Tuple[int, int]) -> int:
        """Flatten a (x,y) tuple to a single integer for Q‑table indexing."""
        return state[1] * self.width + state[0]

    def index_to_state(self, idx: int) -> Tuple[int, int]:
        """Reverse of state_to_index."""
        return (idx % self.width, idx // self.width)


# ----------------------------------------------------------------------
# 2. Q‑Learning Agent
# ----------------------------------------------------------------------
class QAgent:
    """Tabular Q‑learning with epsilon‑greedy exploration."""

    def __init__(
        self,
        state_space: int,
        action_space: int,
        learning_rate: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        seed: Optional[int] = None,
    ):
        self.state_space = state_space
        self.action_space = action_space
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.rng = random.Random(seed)

        # Q‑table: list of lists (state -> actions)
        self.q: List[List[float]] = [
            [0.0] * action_space for _ in range(state_space)
        ]

    def choose_action(self, state_idx: int, epsilon: Optional[float] = None) -> int:
        """Epsilon‑greedy action selection."""
        if epsilon is None:
            epsilon = self.epsilon
        if self.rng.random() < epsilon:
            return self.rng.randint(0, self.action_space - 1)
        # Greedy: pick the action with highest Q‑value.
        q_vals = self.q[state_idx]
        return max(range(self.action_space), key=lambda a: q_vals[a])

    def update(
        self,
        state_idx: int,
        action: int,
        reward: float,
        next_state_idx: int,
        done: bool,
    ):
        """Update Q(s,a) using the Q‑learning rule."""
        best_next_q = 0.0 if done else max(self.q[next_state_idx])
        td_target = reward + self.gamma * best_next_q
        self.q[state_idx][action] += self.lr * (td_target - self.q[state_idx][action])

    def decay_epsilon(self):
        """Decay epsilon towards epsilon_min."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


# ----------------------------------------------------------------------
# 3. Training Loop with Plateau Detection & Novelty Bonus
# ----------------------------------------------------------------------
class TrainingStats:
    """Collects statistics and detects plateau based on rolling average."""

    def __init__(
        self,
        window: int = 50,
        threshold: float = 0.5,
        consecutive: int = 2,
    ):
        self.window = window
        self.threshold = threshold
        self.consecutive = consecutive
        self.history: Deque[float] = collections.deque(maxlen=window)
        self.prev_avg: Optional[float] = None
        self.plateau_counter: int = 0
        self.plateau_reached: bool = False

    def add(self, score: float):
        self.history.append(score)

    def check_plateau(self) -> bool:
        """Return True if the average reward has stalled."""
        if len(self.history) < self.window:
            return False
        avg = sum(self.history) / self.window
        if self.prev_avg is not None:
            if abs(avg - self.prev_avg) < self.threshold:
                self.plateau_counter += 1
            else:
                self.plateau_counter = 0
            if self.plateau_counter >= self.consecutive:
                self.plateau_reached = True
        self.prev_avg = avg
        return self.plateau_reached


def run_training(
    env: GridWorld,
    agent: QAgent,
    episodes: int,
    plateau_window: int = 50,
    plateau_threshold: float = 0.5,
    novelty_bonus: float = 1.0,
    seed: Optional[int] = None,
    verbose: bool = True,
) -> Tuple[QAgent, List[float]]:
    """
    Train the agent, detect plateau and apply a novelty bonus once.
    Returns the trained agent and the list of episode rewards.
    """
    rng = random.Random(seed)
    visit_counts: Dict[int, int] = collections.defaultdict(int)
    novelty_active = False
    novelty_applied = False
    episode_rewards: List[float] = []

    stats = TrainingStats(
        window=plateau_window,
        threshold=plateau_threshold,
        consecutive=2,
    )

    try:
        for ep in range(episodes):
            state = env.reset()
            state_idx = env.state_to_index(state)
            done = False
            total_reward = 0.0

            while not done:
                action = agent.choose_action(state_idx)
                next_state, reward, done = env.step(action)
                next_idx = env.state_to_index(next_state)

                # Novelty bonus when plateau has been detected
                if novelty_active:
                    visit_counts[state_idx] += 1
                    novelty = novelty_bonus / (visit_counts[state_idx] + 1)
                    reward += novelty

                agent.update(state_idx, action, reward, next_idx, done)
                state_idx = next_idx
                total_reward += reward

            episode_rewards.append(total_reward)
            stats.add(total_reward)
            agent.decay_epsilon()

            # Detect plateau
            if not novelty_applied and stats.check_plateau():
                novelty_active = True
                novelty_applied = True
                if verbose:
                    print(
                        f"[Plateau detected at episode {ep + 1}] "
                        "Activating novelty bonus to break plateau."
                    )
            if verbose and (ep + 1) % 100 == 0:
                avg = sum(episode_rewards[-100:]) / 100
                print(
                    f"Episode {ep + 1}/{episodes} | "
                    f"Avg reward (last 100): {avg:.2f} | "
                    f"Epsilon: {agent.epsilon:.4f}"
                )
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
    except Exception as exc:
        print(f"\nUnexpected error during training: {exc}", file=sys.stderr)
        raise

    return agent, episode_rewards


# ----------------------------------------------------------------------
# 4. Utility: Print Summary
# ----------------------------------------------------------------------
def print_summary(rewards: List[float], window: int = 100):
    """Print a concise final report."""
    if not rewards:
        print("No reward data collected.")
        return
    total = len(rewards)
    overall_avg = sum(rewards) / total
    last_n = rewards[-window:] if len(rewards) >= window else rewards
    last_avg = sum(last_n) / len(last_n)
    print("\n========== Training Summary ==========")
    print(f"Total episodes : {total}")
    print(f"Overall avg reward: {overall_avg:.3f}")
    print(f"Last {len(last_n)} episode avg reward: {last_avg:.3f}")
    print(f"Max single‑episode reward: {max(rewards):.3f}")
    print(f"Min single‑episode reward: {min(rewards):.3f}")
    print("======================================\n")


# ----------------------------------------------------------------------
# 5. Command‑Line Interface
# ----------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Break score plateau using novelty‑enhanced Q‑learning."
    )
    parser.add_argument(
        "--episodes", "-e", type=int, default=2000, help="Number of training episodes"
    )
    parser.add_argument(
        "--width", type=int, default=5, help="Grid width"
    )
    parser.add_argument(
        "--height", type=int, default=5, help="Grid height"
    )
    parser.add_argument(
        "--lr", type=float, default=0.1, help="Learning rate"
    )
    parser.add_argument(
        "--gamma", type=float, default=0.99, help="Discount factor"
    )
    parser.add_argument(
        "--epsilon", type=float, default=1.0, help="Initial exploration rate"
    )
    parser.add_argument(
        "--epsilon_decay", type=float, default=0.995, help="Epsilon decay per episode"
    )
    parser.add_argument(
        "--epsilon_min", type=float, default=0.05, help="Minimum epsilon"
    )
    parser.add_argument(
        "--plateau_window", type=int, default=50, help="Window for plateau detection"
    )
    parser.add_argument(
        "--plateau_threshold", type=float, default=0.5, help="Reward change threshold for plateau"
    )
    parser.add_argument(
        "--novelty_bonus", type=float, default=1.0, help="Strength of novelty bonus"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress per‑100 episode output"
    )
    return parser.parse_args()


# ----------------------------------------------------------------------
# 6. Main Entry Point
# ----------------------------------------------------------------------
def main():
    args = parse_args()

    # Initialise environment and agent
    env = GridWorld(width=args.width, height=args.height, seed=args.seed)
    agent = QAgent(
        state_space=env.state_space,
        action_space=env.action_space,
        learning_rate=args.lr,
        gamma=args.gamma,
        epsilon=args.epsilon,
        epsilon_min=args.epsilon_min,
        epsilon_decay=args.epsilon_decay,
        seed=args.seed,
    )

    print(
        f"Starting training for {args.episodes} episodes "
        f"on a {args.width}x{args.height} grid world."
    )
    start_time = time.time()

    trained_agent, rewards = run_training(
        env=env,
        agent=agent,
        episodes=args.episodes,
        plateau_window=args.plateau_window,
        plateau_threshold=args.plateau_threshold,
        novelty_bonus=args.novelty_bonus,
        seed=args.seed,
        verbose=not args.quiet,
    )

    elapsed = time.time() - start_time
    print(f"Training completed in {elapsed:.2f} seconds.")
    print_summary(rewards)

    # Optional: show final Q‑values for each state (optional output)
    if not args.quiet:
        print("\nSample Q‑values (first 5 states):")
        for s_idx in range(min(5, env.state_space)):
            state = env.index_to_state(s_idx)
            q_vals = trained_agent.q[s_idx]
            print(f"  State {state}: Q = {q_vals}")


if __name__ == "__main__":
    main()
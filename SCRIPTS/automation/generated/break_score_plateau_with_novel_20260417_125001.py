#!/usr/bin/env python3
"""
Break Score Plateau with Novel Approach

This module demonstrates a common scenario where a simple incremental
strategy leads to a score plateau, and shows how a "novel approach"
can be used to break that plateau.

The naive approach: start at a given score and keep adding a fixed
increment (e.g., +1) until the improvement falls below a tolerance.
The novel approach: use an adaptive increment mechanism that
oscillates or changes based on recent performance, allowing the
score to escape the plateau and continue rising.

The script can be run standalone and will produce a textual report
of the evolution of the score under both strategies.
"""

import random
import sys
from typing import List, Optional, Tuple

# Optional: try to import matplotlib for plotting; if not available, skip.
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ScorePlateau:
    """
    Simulates a scoring system that may plateau when using a naive
    incremental approach. Provides methods to detect a plateau and
    apply a novel approach to overcome it.
    """

    def __init__(
        self,
        initial_score: float = 0.0,
        seed: Optional[int] = None,
    ) -> None:
        """
        Args:
            initial_score: The starting score before any increments.
            seed: Optional random seed for reproducibility.
        """
        self.initial_score = initial_score
        self.score = initial_score
        self.history: List[float] = [self.score]
        self._rng = random.Random(seed)

    def reset(self) -> None:
        """Reset the score to the initial value and clear history."""
        self.score = self.initial_score
        self.history.clear()
        self.history.append(self.score)

    # --- Naive approach -------------------------------------------------
    def naive_increment(self, delta: float = 1.0) -> float:
        """
        Simple increase of the score by a fixed delta.
        Returns the new score.
        """
        self.score += delta
        self.history.append(self.score)
        return self.score

    # --- Plateau detection -----------------------------------------------
    def is_plateau(self, epsilon: float = 1e-3, window: int = 10) -> bool:
        """
        Determine if the score has entered a plateau.
        A plateau is defined as the situation where the absolute difference
        between the maximum and minimum score values over the last `window`
        iterations is below `epsilon`.

        Args:
            epsilon: Minimum change threshold.
            window: Number of recent iterations to consider.

        Returns:
            True if plateau detected, False otherwise.
        """
        if len(self.history) < window:
            # Not enough history to decide, assume not plateau.
            return False
        recent = self.history[-window:]
        max_score = max(recent)
        min_score = min(recent)
        return (max_score - min_score) < epsilon

    # --- Novel approach --------------------------------------------------
    def novel_approach(
        self,
        max_iter: int = 1000,
        epsilon: float = 1e-3,
        boost_factor: float = 2.0,
        oscillation_range: float = 0.5,
    ) -> "ScorePlateau":
        """
        Apply a novel, adaptive strategy to break a plateau.

        The algorithm works as follows:
        1. Compute a dynamic step size based on the variance of recent scores.
        2. Occasionally "boost" the step size by a factor to escape flat regions.
        3. Add a small oscillatory component to explore neighboring solutions.
        4. Continue iterating until a new improvement larger than `epsilon`
           is observed or `max_iter` iterations are reached.

        Args:
            max_iter: Maximum number of iterations to attempt breaking plateau.
            epsilon: Minimum improvement required to consider the plateau broken.
            boost_factor: Multiplier for the step size when a plateau is detected.
            oscillation_range: Amplitude of the sinusoidal exploration term.

        Returns:
            Self (for method chaining) after applying the novel approach.
        """
        # If we are not already in a plateau, we simply continue with the
        # naive increment; otherwise we switch strategies.
        if not self.is_plateau():
            # No plateau, nothing to break; just increment once.
            self.naive_increment(delta=1.0)
            return self

        current = self.score
        step = 1.0  # initial step size
        improved = False

        for i in range(max_iter):
            # Detect if we are still in a plateau.
            if self.is_plateau():
                # Increase step size to escape flat region.
                step *= boost_factor
            else:
                # If we have left the plateau, we can reduce step size.
                step = max(step / boost_factor, 1.0)

            # Compute a small oscillatory term.
            osc = oscillation_range * self._rng.uniform(-1, 1)

            # Propose a candidate new score.
            candidate = current + step + osc

            # Accept candidate if it improves the score.
            if candidate > current + epsilon:
                current = candidate
                self.score = current
                self.history.append(self.score)
                improved = True
                # Once we see improvement, we can break early.
                if not self.is_plateau():
                    break
            else:
                # If candidate does not improve, we still log the attempt.
                self.history.append(current)

        # If after the loop we still have not improved, we log a note.
        if not improved:
            # Append the current score again to indicate failure (optional).
            self.history.append(current)

        return self

    # --- Reporting ------------------------------------------------------
    def summary(self) -> str:
        """Return a concise summary of the scoring evolution."""
        lines = [
            f"Initial score : {self.initial_score}",
            f"Final score   : {self.score}",
            f"Total steps   : {len(self.history) - 1}",
            f"Max score     : {max(self.history):.4f}",
            f"Min score     : {min(self.history):.4f}",
        ]
        return "\n".join(lines)

    def plot_history(self, title: Optional[str] = None) -> None:
        """
        Plot the score history using matplotlib.
        Only available if matplotlib is installed.
        """
        if not MATPLOTLIB_AVAILABLE:
            print(
                "matplotlib is not available. Skipping plot.",
                file=sys.stderr,
            )
            return

        if not self.history:
            print("No data to plot.", file=sys.stderr)
            return

        plt.figure(figsize=(10, 6))
        plt.plot(self.history, label="Score", color="steelblue")
        plt.title(title or "Score Evolution")
        plt.xlabel("Iteration")
        plt.ylabel("Score")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()


def naive_run(
    start: float = 0.0,
    steps: int = 100,
    delta: float = 1.0,
) -> ScorePlateau:
    """
    Run a naive linear increase for a given number of steps.

    Args:
        start: Starting score.
        steps: Number of increments to apply.
        delta: Increment per step.

    Returns:
        ScorePlateau instance after the run.
    """
    plate = ScorePlateau(initial_score=start)
    for _ in range(steps):
        plate.naive_increment(delta=delta)
        # Stop early if we are already in a plateau.
        if plate.is_plateau():
            break
    return plate


def novel_run(
    start: float = 0.0,
    steps: int = 100,
    **kwargs,
) -> ScorePlateau:
    """
    Run the novel approach for a given number of steps.

    Args:
        start: Starting score.
        steps: Number of iterations for the novel approach.
        **kwargs: Additional keyword arguments passed to novel_approach.

    Returns:
        ScorePlateau instance after the run.
    """
    plate = ScorePlateau(initial_score=start)
    plate.novel_approach(max_iter=steps, **kwargs)
    return plate


def compare_strategies(
    start: float = 0.0,
    steps: int = 200,
) -> Tuple[ScorePlateau, ScorePlateau]:
    """
    Run both naive and novel strategies and return the resulting
    ScorePlateau objects for comparison.
    """
    naive_plate = naive_run(start=start, steps=steps)
    # Reset for a fair comparison.
    novel_plate = novel_run(start=start, steps=steps)
    return naive_plate, novel_plate


def main() -> None:
    """
    Entry point. Demonstrates the difference between naive and novel
    approaches and prints a summary. Optionally plots the results.
    """
    # Parameters for the demonstration.
    start_score = 0.0
    num_steps = 200
    seed = 42  # For reproducibility.

    # Set the seed for the global random generator (used by ScorePlateau).
    if seed is not None:
        random.seed(seed)

    print("=" * 60)
    print("Breaking Score Plateau – Novel Approach Demo")
    print("=" * 60)

    # Compare naive vs novel.
    try:
        naive, novel = compare_strategies(start=start_score, steps=num_steps)
    except Exception as e:
        print(f"Error during comparison: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n--- Naive Strategy ---")
    print(naive.summary())

    print("\n--- Novel Strategy ---")
    print(novel.summary())

    # Determine which strategy achieved a higher final score.
    if novel.score > naive.score:
        print("\nThe novel approach achieved a higher final score.")
    elif novel.score == naive.score:
        print("\nBoth strategies converged to the same score.")
    else:
        print("\nThe naive strategy outperformed the novel approach (unexpected).")

    # Optional plotting.
    if MATPLOTLIB_AVAILABLE:
        try:
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

            axes[0].plot(naive.history, color="red", label="Naive")
            axes[0].set_title("Naive Strategy")
            axes[0].set_xlabel("Iteration")
            axes[0].set_ylabel("Score")
            axes[0].grid(True)
            axes[0].legend()

            axes[1].plot(novel.history, color="green", label="Novel")
            axes[1].set_title("Novel Strategy")
            axes[1].set_xlabel("Iteration")
            axes[1].set_ylabel("Score")
            axes[1].grid(True)
            axes[1].legend()

            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Warning: Could not generate plot: {e}", file=sys.stderr)
    else:
        print("\n(Plotting skipped because matplotlib is not installed.)")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Break Score Plateau – Novel Approach

This script simulates a scoring environment where the average score per action
tends to plateau after some time. It detects such a plateau and applies a
"novel approach" (Dynamic Difficulty Adjustment with periodic score boosts)
to break the plateau and improve overall performance.

The script can work with:
    * a CSV file containing a list of scores (one per line), or
    * a built‑in synthetic simulation.

Usage:
    python3 break_score_plateau.py [--file <csv_file>] [--steps <int>] [--seed <int>]

Options:
    --file   Path to a CSV file with scores (optional).
    --steps  Number of simulation steps when no file is provided (default: 1000).
    --seed   Random seed for reproducibility (optional).

Error handling is included for file I/O, data parsing, plateau detection,
and optional plotting. The script gracefully falls back when matplotlib is
not available.
"""

import argparse
import sys
import random
import math
from typing import List, Optional, Tuple

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    """Parse command‑line arguments."""
    parser = argparse.ArgumentParser(
        description="Break score plateau with a novel approach."
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to CSV file containing scores (one per line).",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=1000,
        help="Number of simulation steps when generating synthetic data.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    return parser.parse_args()


def load_scores_from_file(path: str) -> List[float]:
    """
    Load scores from a text file (one numeric value per line).

    Raises:
        IOError: If the file cannot be opened or read.
        ValueError: If a line does not contain a valid float.
    """
    scores: List[float] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                stripped = line.strip()
                if not stripped:
                    # Skip empty lines
                    continue
                try:
                    scores.append(float(stripped))
                except ValueError:
                    raise ValueError(
                        f"Invalid numeric value on line {line_no}: '{stripped}'"
                    )
    except OSError as e:
        raise IOError(f"Failed to read file '{path}': {e}")
    return scores


def moving_average(data: List[float], window: int) -> List[float]:
    """
    Compute a simple moving average with the given window size.

    Args:
        data: List of numeric values.
        window: Size of the averaging window (must be > 0).

    Returns:
        A list of the same length with averaged values.
    """
    if window <= 0:
        raise ValueError("Window size must be greater than zero.")
    result: List[float] = []
    for i, _ in enumerate(data):
        start = max(0, i - window + 1)
        segment = data[start:i + 1]
        result.append(sum(segment) / len(segment))
    return result


def detect_plateau(mov_avg: List[float], threshold: float = 0.01, lookback: int = 20) -> bool:
    """
    Determine whether the moving average has reached a plateau.

    The detection uses a simple linear regression over the last ``lookback``
    points. If the absolute slope is below ``threshold``, a plateau is reported.

    Args:
        mov_avg:   Moving average series.
        threshold: Minimum slope magnitude to be considered non‑plateau.
        lookback:  Number of most recent points to consider.

    Returns:
        True if a plateau is detected, otherwise False.
    """
    if len(mov_avg) < lookback:
        return False

    recent = mov_avg[-lookback:]
    n = len(recent)
    if n == 0:
        return False

    # Simple linear regression: y = a * x + b
    x_vals = list(range(n))
    mean_x = sum(x_vals) / n
    mean_y = sum(recent) / n

    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, recent))
    denominator = sum((x - mean_x) ** 2 for x in x_vals)

    if denominator == 0:
        return False

    slope = numerator / denominator
    return abs(slope) < threshold


def simulate_base_scorer(base_rate: float, variance: float, steps: int, seed: Optional[int]) -> List[float]:
    """
    Simulate a simple scoring process where each action yields a score drawn
    from a normal distribution centred on ``base_rate``.

    Args:
        base_rate: Mean score per action.
        variance:  Standard deviation of the score.
        steps:     Number of actions to simulate.
        seed:      Optional random seed for reproducibility.

    Returns:
        List of scores, one per action.
    """
    if seed is not None:
        random.seed(seed)

    scores: List[float] = []
    for _ in range(steps):
        # Guard against extremely unlikely extreme values by clipping
        score = random.gauss(base_rate, variance)
        scores.append(score)
    return scores


def apply_novel_approach(scores: List[float], mov_avg_window: int = 20) -> Tuple[List[float], str]:
    """
    Detect a plateau in the provided scores and, if found, apply a novel
    approach to break it.

    The implemented novel approach is *Dynamic Difficulty Adjustment*:
    after the plateau start, a periodic boost (2×) is applied every 30 steps.
    This mimics power‑ups or acquisition of new skills in a game context.

    Args:
        scores:          List of scores (one per action).
        mov_avg_window:  Window size for moving average (used for plateau detection).

    Returns:
        A tuple (modified_scores, description). ``description`` explains which
        approach was taken.
    """
    if len(scores) < mov_avg_window:
        return scores, "Not enough data for reliable plateau detection."

    mov_avg = moving_average(scores, mov_avg_window)

    if not detect_plateau(mov_avg):
        return scores, "No plateau detected – no changes applied."

    # Plateau start is approximated as the first index of the last window
    plateau_start = len(scores) - mov_avg_window
    boost_interval = 30
    boost_factor = 2.0

    modified = scores.copy()
    for i in range(plateau_start, len(modified)):
        if (i - plateau_start) % boost_interval == 0:
            # Apply a boost to break the plateau
            modified[i] *= boost_factor

    description = (
        "Plateau detected. Applied *Dynamic Difficulty Adjustment*: "
        f"Every {boost_interval} steps after the plateau start, scores are multiplied by {boost_factor}."
    )
    return modified, description


def compute_statistics(scores: List[float]) -> dict:
    """
    Compute basic descriptive statistics for a list of scores.

    Returns:
        Dictionary containing:
            - count
            - total
            - mean
            - std (population standard deviation)
            - min
            - max
    """
    if not scores:
        return {}

    n = len(scores)
    total = sum(scores)
    mean = total / n
    variance = sum((x - mean) ** 2 for x in scores) / n
    std = math.sqrt(variance)

    return {
        "count": n,
        "total": total,
        "mean": mean,
        "std": std,
        "min": min(scores),
        "max": max(scores),
    }


def print_statistics(label: str, stats: dict) -> None:
    """Pretty‑print a statistics dictionary."""
    print(f"\n=== {label} ===")
    if not stats:
        print("  (no data)")
        return
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")


def plot_scores(scores: List[float], title: str, output_path: Optional[str] = None) -> None:
    """
    Plot the score series using matplotlib (if available).

    Args:
        scores:      Score series to plot.
        title:       Title for the plot.
        output_path: If provided, save the figure to this path.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed – skipping plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(scores, label="Score per action", alpha=0.6)

    # Overlay a moving average if we have enough points
    if len(scores) >= 20:
        mov_avg = moving_average(scores, 20)
        plt.plot(mov_avg, label="Moving average (20)", linewidth=2)

    plt.title(title)
    plt.xlabel("Action index")
    plt.ylabel("Score")
    plt.legend()
    plt.grid(True)

    if output_path:
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")
    else:
        plt.show()


# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------

def main() -> None:
    """Orchestrate loading/generating data, analysis, plateau breaking, and output."""
    args = parse_arguments()

    # -------------------------------------------------
    # 1. Acquire score data
    # -------------------------------------------------
    try:
        if args.file:
            # Load from file
            raw_scores = load_scores_from_file(args.file)
            # If the user supplied --steps, we can limit the data to that many entries
            if args.steps and len(raw_scores) > args.steps:
                raw_scores = raw_scores[: args.steps]
        else:
            # Synthetic simulation
            base_rate = 10.0
            variance = 2.0
            raw_scores = simulate_base_scorer(
                base_rate=base_rate,
                variance=variance,
                steps=args.steps,
                seed=args.seed,
            )
    except Exception as exc:
        sys.stderr.write(f"[ERROR] While preparing data: {exc}\n")
        sys.exit(1)

    # -------------------------------------------------
    # 2. Pre‑intervention statistics
    # -------------------------------------------------
    stats_before = compute_statistics(raw_scores)
    print_statistics("Pre‑intervention statistics", stats_before)

    # -------------------------------------------------
    # 3. Plateau detection & novel approach
    # -------------------------------------------------
    try:
        modified_scores, approach_description = apply_novel_approach(raw_scores)
    except Exception as exc:
        sys.stderr.write(f"[ERROR] During plateau detection or intervention: {exc}\n")
        sys.exit(1)

    print(f"\n{approach_description}")

    # -------------------------------------------------
    # 4. Post‑intervention statistics
    # -------------------------------------------------
    stats_after = compute_statistics(modified_scores)
    print_statistics("Post‑intervention statistics", stats_after)

    # -------------------------------------------------
    # 5. Optional visualisation
    # -------------------------------------------------
    try:
        plot_scores(modified_scores, "Score progression after novel approach")
    except Exception as exc:
        sys.stderr.write(f"[WARNING] Could not render plot: {exc}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user – exiting gracefully.")
        sys.exit(0)
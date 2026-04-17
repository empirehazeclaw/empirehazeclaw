#!/usr/bin/env python3
"""
Cross‑Pattern Analyzer

A simple script that generates random binary patterns, assigns binary
labels, and computes a classification error rate using K‑fold
cross‑validation.  The result is printed in the same format as the
example in the problem statement:

    [CROSS-PATTERN] [CROSS-PATTERN] 📈 Real Error Rate: X.XX%

Usage
-----
    python3 cross_pattern.py [--samples N] [--features M] [--folds K] [--seed S]

Options
-------
--samples   Number of generated samples (default: 200)
--features  Number of binary features per sample (default: 50)
--folds     Number of cross‑validation folds (default: 5)
--seed      Random seed for reproducibility (default: 42)

The script is self‑contained and requires only the Python 3 standard
library.
"""

import sys
import argparse
import random
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command‑line arguments."""
    parser = argparse.ArgumentParser(
        description="Cross‑Pattern Analyzer – compute a real error rate "
        "for a synthetic binary‑pattern data set."
    )
    parser.add_argument(
        "--samples", type=int, default=200,
        help="Number of samples to generate (default: 200)"
    )
    parser.add_argument(
        "--features", type=int, default=50,
        help="Number of binary features per sample (default: 50)"
    )
    parser.add_argument(
        "--folds", type=int, default=5,
        help="Number of cross‑validation folds (default: 5)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    return parser.parse_args()


def generate_binary_matrix(num_samples: int, num_features: int, rng: random.Random) -> List[List[int]]:
    """Create a matrix of binary values (0/1) of shape (num_samples, num_features)."""
    return [
        [rng.randint(0, 1) for _ in range(num_features)]
        for _ in range(num_samples)
    ]


def assign_labels(matrix: List[List[int]], rng: random.Random) -> List[int]:
    """
    Assign binary labels to each row of the matrix.
    The label is the parity (sum modulo 2) of the row, which introduces a
    slight correlation with the data while keeping the classification
    non‑trivial.
    """
    return [sum(row) % 2 for row in matrix]


def hamming_distance(a: List[int], b: List[int]) -> int:
    """Return the Hamming distance between two binary vectors."""
    return sum(x != y for x, y in zip(a, b))


def knn_predict(
    train_data: List[List[int]],
    train_labels: List[int],
    test_sample: List[int],
    k: int = 3
) -> int:
    """
    Predict the label of a single test sample using k‑nearest neighbours
    with Hamming distance as the similarity metric.
    """
    # Compute distances to all training samples
    distances = [
        (hamming_distance(train_data[i]), train_labels[i])
        for i in range(len(train_data))
    ]
    # Sort by distance (ascending)
    distances.sort(key=lambda x: x[0])
    # Take the k closest neighbours
    top_k_labels = [label for _, label in distances[:k]]
    # Majority vote
    return 1 if sum(top_k_labels) > k // 2 else 0


def kfold_indices(n: int, k: int, rng: random.Random) -> List[List[int]]:
    """
    Return a list of k folds, each containing the indices of a validation split.
    The data is shuffled before splitting.
    """
    indices = list(range(n))
    rng.shuffle(indices)
    fold_size = n // k
    # If n is not evenly divisible by k, some samples at the end are omitted
    return [indices[i * fold_size:(i + 1) * fold_size] for i in range(k)]


def cross_validate(
    data: List[List[int]],
    labels: List[int],
    k_folds: int,
    rng: random.Random
) -> float:
    """
    Perform k‑fold cross‑validation and return the overall error rate.
    For each fold a KNN classifier (k=3) is trained on the complementary
    training set and evaluated on the fold's validation set.
    """
    folds = kfold_indices(len(data), k_folds, rng)
    total_errors = 0
    total_samples = 0

    for fold_idx in range(k_folds):
        # Validation indices for this fold
        val_indices = folds[fold_idx]
        # Training indices are all indices not in the validation set
        train_indices = [idx for i, fold in enumerate(folds) if i != fold_idx for idx in fold]

        # Extract corresponding data subsets
        train_data = [data[i] for i in train_indices]
        train_labels = [labels[i] for i in train_indices]
        val_data = [data[i] for i in val_indices]
        val_labels = [labels[i] for i in val_indices]

        # Predict on the validation set
        for sample, true_label in zip(val_data, val_labels):
            pred = knn_predict(train_data, train_labels, sample, k=3)
            if pred != true_label:
                total_errors += 1
            total_samples += 1

    # Avoid division by zero (should not happen because n > 0)
    return total_errors / total_samples if total_samples > 0 else 0.0


def format_error_rate(rate: float) -> str:
    """Convert a decimal error rate to a percentage string with two decimal places."""
    return f"{rate * 100:.2f}"


def main() -> int:
    """
    Entry point.  Parses arguments, generates data, runs cross‑validation,
    and prints the result.
    """
    args = parse_args()

    try:
        # Initialise a deterministic random generator
        rng = random.Random(args.seed)

        # ----- Data generation -------------------------------------------------
        data = generate_binary_matrix(args.samples, args.features, rng)
        labels = assign_labels(data, rng)

        # ----- Cross‑validation -------------------------------------------------
        error_rate = cross_validate(data, labels, args.folds, rng)
        error_pct = format_error_rate(error_rate)

        # ----- Output ------------------------------------------------------------
        # The output format mirrors the one shown in the problem description.
        print(f"[CROSS-PATTERN] [CROSS-PATTERN] 📈 Real Error Rate: {error_pct}%")
        return 0

    except Exception as exc:
        # Minimal error handling – print the exception to stderr and exit cleanly.
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


# ----------------------------------------------------------------------
# Boilerplate
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
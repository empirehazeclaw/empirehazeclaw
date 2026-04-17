#!/usr/bin/env python3
"""
Break Score Plateau – Novel Approach

This script demonstrates a simple linear regression where the training loss may
reach a plateau. A plateau detector watches the (negative) loss and, once a
plateau is identified, applies a *novel* intervention: a temporary learning‑rate
boost combined with random weight perturbations. This can help the optimizer
escape shallow local minima and resume improvement.
"""

import sys
import csv
import argparse
import random
import math

# ----------------------------------------------------------------------
# Synthetic data generation
# ----------------------------------------------------------------------
def generate_synthetic_data(num_samples, num_features, noise=0.1, seed=None):
    """Create a linear dataset with Gaussian features and additive noise."""
    if seed is not None:
        random.seed(seed)

    # True weights (unknown to the model)
    true_weights = [random.gauss(0, 1.0) for _ in range(num_features)]

    # Feature matrix
    X = [[random.gauss(0, 1.0) for _ in range(num_features)] for _ in range(num_samples)]

    # Target vector
    y = [
        sum(w * xi for w, xi in zip(true_weights, x_i)) + random.gauss(0, noise)
        for x_i in X
    ]
    return X, y


# ----------------------------------------------------------------------
# Simple linear model trained with gradient descent
# ----------------------------------------------------------------------
class SimpleLinearModel:
    """Linear model (weights + bias) trained by vanilla gradient descent."""

    def __init__(self, n_features, learning_rate=0.01, regularization=0.001):
        self.weights = [0.0] * n_features
        self.bias = 0.0
        self.lr = learning_rate
        self.reg = regularization

    def predict(self, X):
        """Compute predictions for all samples."""
        return [self._dot(x) + self.bias for x in X]

    def _dot(self, x):
        return sum(w * xi for w, xi in zip(self.weights, x))

    def loss(self, X, y):
        """Mean‑squared error plus L2 regularisation."""
        n = len(y)
        mse = sum((p - t) ** 2 for p, t in zip(self.predict(X), y)) / n
        reg = self.reg * sum(w * w for w in self.weights) / n
        return mse + reg

    def gradient(self, X, y):
        """Compute gradients of MSE + regularisation w.r.t. weights & bias."""
        n = len(y)
        pred = self.predict(X)
        grad_w = [0.0] * len(self.weights)
        grad_b = 0.0

        for x_i, y_i, p_i in zip(X, y, pred):
            err = p_i - y_i
            for j, x_ij in enumerate(x_i):
                grad_w[j] += 2.0 * err * x_ij / n
            grad_b += 2.0 * err / n

        # Regularisation gradient
        for j in range(len(self.weights)):
            grad_w[j] += 2.0 * self.reg * self.weights[j] / n

        return grad_w, grad_b

    def update(self, grad_w, grad_b):
        """Perform a single gradient‑descent step."""
        for j in range(len(self.weights)):
            self.weights[j] -= self.lr * grad_w[j]
        self.bias -= self.lr * grad_b


# ----------------------------------------------------------------------
# Plateau detection & novel intervention
# ----------------------------------------------------------------------
class PlateauBreaker:
    """
    Monitors a scalar score (higher is better). When the average improvement
    over a sliding window falls below a threshold, a plateau is declared.
    The *novel* remedy consists of:
        1) Temporarily multiplying the learning rate by a constant factor.
        2) Injecting Gaussian noise into all model parameters.
    """

    def __init__(self, model, plateau_window=5, min_improvement=1e-4, noise_scale=0.02):
        self.model = model
        self.plateau_window = plateau_window
        self.min_improvement = min_improvement
        self.noise_scale = noise_scale
        self.history = []

    def update(self, score):
        """
        Append a new score, keep the last ``plateau_window`` entries, and
        return True if a plateau is detected.
        """
        self.history.append(score)
        if len(self.history) < self.plateau_window:
            return False

        # Keep only the most recent window
        self.history = self.history[-self.plateau_window:]

        # Average improvement over the window
        diffs = [self.history[i] - self.history[i - 1] for i in range(1, len(self.history))]
        avg_imp = sum(diffs) / len(diffs)

        # If improvement is negligible, we are stuck on a plateau
        return abs(avg_imp) < self.min_improvement

    def apply_novel_approach(self):
        """
        Apply the *novel* intervention:
        - Boost learning rate (temporary)
        - Add Gaussian noise to all parameters
        Returns the previous learning rate for logging.
        """
        old_lr = self.model.lr

        # 1) Learning‑rate boost (factor 5)
        self.model.lr = old_lr * 5.0

        # 2) Parameter perturbation
        for i in range(len(self.model.weights)):
            self.model.weights[i] += random.gauss(0, self.noise_scale)
        self.model.bias += random.gauss(0, self.noise_scale)

        return old_lr


# ----------------------------------------------------------------------
# Command‑line interface
# ----------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Break score plateau using a novel approach."
    )
    parser.add_argument(
        "--epochs", type=int, default=200, help="Number of training epochs."
    )
    parser.add_argument(
        "--lr", type=float, default=0.01, help="Initial learning rate."
    )
    parser.add_argument(
        "--reg", type=float, default=0.001, help="L2 regularisation strength."
    )
    parser.add_argument(
        "--plateau_window",
        type=int,
        default=5,
        help="Number of epochs to consider for plateau detection.",
    )
    parser.add_argument(
        "--min_improvement",
        type=float,
        default=1e-4,
        help="Minimum average improvement to consider non‑plateau.",
    )
    parser.add_argument(
        "--noise_scale",
        type=float,
        default=0.02,
        help="Scale of Gaussian noise injected when breaking plateau.",
    )
    parser.add_argument(
        "--samples", type=int, default=500, help="Number of synthetic samples."
    )
    parser.add_argument(
        "--features", type=int, default=10, help="Number of input features."
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for reproducibility."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="training_log.csv",
        help="CSV file to log scores per epoch.",
    )
    return parser.parse_args()


def write_csv(filepath, rows):
    """Write a list of dictionaries to a CSV file."""
    try:
        with open(filepath, "w", newline="") as f:
            if rows:
                writer = csv.DictWriter(
                    f, fieldnames=list(rows[0].keys())
                )
                writer.writeheader()
                writer.writerows(rows)
    except Exception as e:
        print(f"[ERROR] Failed to write CSV '{filepath}': {e}", file=sys.stderr)


# ----------------------------------------------------------------------
# Main training loop
# ----------------------------------------------------------------------
def main():
    args = parse_args()

    # ----- Synthetic data -------------------------------------------------
    try:
        X, y = generate_synthetic_data(
            num_samples=args.samples,
            num_features=args.features,
            noise=0.1,
            seed=args.seed,
        )
    except Exception as e:
        print(f"[ERROR] Data generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # ----- Model ---------------------------------------------------------
    model = SimpleLinearModel(
        n_features=args.features,
        learning_rate=args.lr,
        regularization=args.reg,
    )

    # ----- Plateau breaker -----------------------------------------------
    breaker = PlateauBreaker(
        model,
        plateau_window=args.plateau_window,
        min_improvement=args.min_improvement,
        noise_scale=args.noise_scale,
    )

    # ----- Training log ---------------------------------------------------
    log = []

    print("Start training...")
    for epoch in range(1, args.epochs + 1):
        # Compute loss
        try:
            loss = model.loss(X, y)
        except Exception as e:
            print(
                f"[ERROR] Loss computation failed at epoch {epoch}: {e}",
                file=sys.stderr,
            )
            break

        # Use negative loss as the score (higher is better)
        score = -loss

        # Detect plateau
        is_plateau = breaker.update(score)

        intervention = False
        if is_plateau:
            try:
                old_lr = breaker.apply_novel_approach()
                intervention = True
                print(
                    f"Epoch {epoch}: Plateau detected. "
                    f"Novel approach applied (LR {old_lr:.6f} → {model.lr:.6f})."
                )
            except Exception as e:
                print(
                    f"[ERROR] Intervention failed at epoch {epoch}: {e}",
                    file=sys.stderr,
                )

        # Log this epoch
        log.append(
            {
                "epoch": epoch,
                "loss": loss,
                "score": score,
                "plateau_detected": is_plateau,
                "intervention": intervention,
            }
        )

        # Perform gradient‑descent step
        try:
            grad_w, grad_b = model.gradient(X, y)
            model.update(grad_w, grad_b)
        except Exception as e:
            print(
                f"[ERROR] Gradient update failed at epoch {epoch}: {e}",
                file=sys.stderr,
            )
            break

        if epoch % 20 == 0:
            print(f"Epoch {epoch}/{args.epochs} – Loss: {loss:.6f}")

    # ----- Save results ---------------------------------------------------
    write_csv(args.output, log)
    print(f"Training complete. Log saved to '{args.output}'.")


if __name__ == "__main__":
    main()
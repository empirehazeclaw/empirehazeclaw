#!/usr/bin/env python3
"""
Cross‑Pattern Error Rate Calculator

This script reads a configuration file (JSON) and a data file (CSV) that contain
cross‑pattern information and expected/actual results. It computes the real error
rate (percentage) and prints a summary.

Usage:
    python3 cross_pattern_error.py [--config CONFIG_FILE] [--data DATA_FILE]

If no arguments are provided, the script attempts to load default files
("config.json" and "data.csv") from the current directory.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Any, Optional

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def load_json_file(path: str) -> Dict[str, Any]:
    """Load and parse a JSON file. Raises exceptions on failure."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in '{path}': {e}") from e


def load_csv_file(path: str, delimiter: str = ",") -> List[Dict[str, str]]:
    """Load a CSV file into a list of dictionaries."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"CSV file not found: {path}")
    rows: List[Dict[str, str]] = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                rows.append(row)
    except csv.Error as e:
        raise ValueError(f"Error reading CSV '{path}': {e}") from e
    return rows


def parse_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and extract relevant configuration settings.
    Expected keys:
        - "patterns": list of pattern identifiers (strings)
        - "threshold": optional float for some analysis (default 0.5)
        - "labels": optional mapping for label translation
    """
    patterns = config.get("patterns", [])
    if not isinstance(patterns, list):
        raise ValueError("'patterns' in config must be a list.")
    threshold = config.get("threshold", 0.5)
    if not isinstance(threshold, (int, float)):
        raise ValueError("'threshold' in config must be a number.")
    labels = config.get("labels", {})
    if not isinstance(labels, dict):
        raise ValueError("'labels' in config must be a dictionary.")
    return {
        "patterns": patterns,
        "threshold": float(threshold),
        "labels": labels,
    }


def detect_cross_patterns(data: List[Dict[str, str]], config: Dict[str, Any]) -> Dict[str, int]:
    """
    Detect occurrences of each configured pattern in the data.
    A pattern is considered present if its identifier appears in any column.
    Returns a dictionary mapping pattern -> occurrence count.
    """
    pattern_counts: Dict[str, int] = defaultdict(int)
    patterns = config["patterns"]
    for row in data:
        # Concatenate all column values (case‑insensitive) for simplicity
        row_text = " ".join(row.values()).lower()
        for pat in patterns:
            if pat.lower() in row_text:
                pattern_counts[pat] += 1
    return dict(pattern_counts)


def compute_error_rate(data: List[Dict[str, str]],
                       config: Dict[str, Any]) -> float:
    """
    Compute the real error rate based on expected vs. actual columns.
    Expected columns:
        - "expected" (ground truth)
        - "actual" (predicted)
    The error rate is the proportion of rows where expected != actual.
    """
    expected_key = "expected"
    actual_key = "actual"
    total = 0
    errors = 0
    for row in data:
        if expected_key not in row or actual_key not in row:
            raise ValueError("Each row must contain 'expected' and 'actual' columns.")
        exp = row[expected_key].strip()
        act = row[actual_key].strip()
        total += 1
        if exp != act:
            errors += 1
    if total == 0:
        # No data rows -> define error rate as 0%
        return 0.0
    return (errors / total) * 100.0


def print_summary(error_rate: float,
                  pattern_counts: Dict[str, int],
                  config: Dict[str, Any]) -> None:
    """Print a formatted summary of the analysis."""
    print("\n" + "=" * 50)
    print("       CROSS‑PATTERN ERROR ANALYSIS")
    print("=" * 50)

    # Real error rate
    print(f"\n📈 Real Error Rate: {error_rate:.2f}%")

    # Cross‑pattern occurrences
    print("\n📊 Cross‑Pattern Occurrences:")
    if pattern_counts:
        for pat, cnt in pattern_counts.items():
            print(f"   • {pat}: {cnt}")
    else:
        print("   (none)")

    # Threshold info (if applicable)
    threshold = config["threshold"]
    print(f"\n🔧 Threshold used for analysis: {threshold}")

    print("\n" + "=" * 50)
    print("Analysis complete.\n")


# ----------------------------------------------------------------------
# Main logic
# ----------------------------------------------------------------------

def parse_arguments(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Cross‑Pattern Error Rate Calculator"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to JSON configuration file (default: config.json)",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data.csv",
        help="Path to CSV data file (default: data.csv)",
    )
    parser.add_argument(
        "--delimiter",
        type=str,
        default=",",
        help="CSV delimiter (default: ',')",
    )
    return parser.parse_args(args)


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point of the script."""
    if argv is None:
        argv = sys.argv[1:]

    # ------------------------------------------------------------------
    # Argument parsing
    # ------------------------------------------------------------------
    try:
        args = parse_arguments(argv)
    except SystemExit:
        # User asked for help or gave invalid arguments
        sys.exit(0)

    # ------------------------------------------------------------------
    # Load configuration
    # ------------------------------------------------------------------
    try:
        config_raw = load_json_file(args.config)
        config = parse_config(config_raw)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] Failed to load configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    try:
        data = load_csv_file(args.data, delimiter=args.delimiter)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] Failed to load data: {e}", file=sys.stderr)
        sys.exit(1)

    if not data:
        print("[WARNING] Data file is empty. Nothing to analyze.", file=sys.stderr)
        sys.exit(0)

    # ------------------------------------------------------------------
    # Detect cross patterns
    # ------------------------------------------------------------------
    try:
        pattern_counts = detect_cross_patterns(data, config)
    except Exception as e:
        print(f"[ERROR] During cross‑pattern detection: {e}", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Compute error rate
    # ------------------------------------------------------------------
    try:
        error_rate = compute_error_rate(data, config)
    except Exception as e:
        print(f"[ERROR] During error rate computation: {e}", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Output summary
    # ------------------------------------------------------------------
    print_summary(error_rate, pattern_counts, config)


if __name__ == "__main__":
    main()
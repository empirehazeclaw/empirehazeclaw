#!/usr/bin/env python3
"""
CROSS-PATTERN Real Error Rate Calculator

This script parses log files that contain entries like:
    [CROSS-PATTERN] 📈 Real Error Rate: 2.21%
and calculates the average real error rate across all matching lines.

It also provides a simple generator to create a sample log file for testing.

Usage
-----
    # Parse a log file and report the average error rate
    python3 cross_pattern_error.py parse <log_file>

    # Generate a sample log file with random error rates
    python3 cross_pattern_error.py generate <output_file> [--lines N]

Examples
--------
    python3 cross_pattern_error.py parse sample.log
    python3 cross_pattern_error.py generate sample.log --lines 100
"""

import argparse
import re
import sys
import random
from pathlib import Path
from typing import List, Optional


# ----------------------------------------------------------------------
# Core parsing logic
# ----------------------------------------------------------------------

def extract_error_rates(content: str) -> List[float]:
    """
    Extract all numeric error rates (in percent) from *content*.
    Looks for lines that contain the literal pattern
    ``[CROSS-PATTERN]`` followed by ``Real Error Rate: <value>%``.
    """
    pattern = re.compile(
        r'\[CROSS-PATTERN\]\s*📈\s*Real Error Rate:\s*(\d+(?:\.\d+)?)%',
        re.IGNORECASE
    )
    rates = []
    for line in content.splitlines():
        match = pattern.search(line)
        if match:
            try:
                rates.append(float(match.group(1)))
            except ValueError:
                # Should never happen because regex guarantees a number,
                # but we keep it for robustness.
                continue
    return rates


def average_error_rate(rates: List[float]) -> Optional[float]:
    """Return the arithmetic mean of a list of rates, or None if empty."""
    if not rates:
        return None
    return sum(rates) / len(rates)


def parse_log_file(filepath: Path) -> int:
    """
    Read *filepath*, extract error rates and print statistics.

    Returns exit code:
        0 – success (even if no rates found)
        1 – file could not be read
    """
    try:
        with filepath.open("r", encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        print(f"❌ Failed to read file {filepath}: {exc}", file=sys.stderr)
        return 1

    rates = extract_error_rates(content)

    if not rates:
        print("⚠️  No CROSS-PATTERN error rates found in the file.")
        return 0

    avg = average_error_rate(rates)
    print(f"📊 Parsed {len(rates)} entries.")
    print(f"📈 Real Error Rate (average): {avg:.2f}%")
    print(f"📉 Minimum: {min(rates):.2f}%  |  Maximum: {max(rates):.2f}%")
    return 0


# ----------------------------------------------------------------------
# Sample log generator (for demonstration)
# ----------------------------------------------------------------------

def generate_sample_log(filepath: Path, lines: int = 20) -> int:
    """
    Create a text file containing *lines* random CROSS-PATTERN log entries.
    Each line contains a plausible real error rate between 0.0% and 100.0%.

    Returns exit code:
        0 – success
        1 – file could not be written
    """
    try:
        with filepath.open("w", encoding="utf-8") as f:
            for _ in range(lines):
                rate = random.uniform(0.0, 100.0)
                # Format the line similar to the example provided.
                f.write(f"[CROSS-PATTERN] 📈 Real Error Rate: {rate:.2f}%\n")
    except OSError as exc:
        print(f"❌ Failed to write file {filepath}: {exc}", file=sys.stderr)
        return 1

    print(f"✅ Sample log with {lines} entries written to {filepath}")
    return 0


# ----------------------------------------------------------------------
# CLI argument handling
# ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct the command‑line argument parser."""
    parser = argparse.ArgumentParser(
        description="CROSS-PATTERN Real Error Rate Calculator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: parse
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse a log file and compute the average real error rate."
    )
    parse_parser.add_argument(
        "log_file",
        type=Path,
        help="Path to the log file to parse."
    )

    # Subcommand: generate
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate a sample log file for testing."
    )
    gen_parser.add_argument(
        "output_file",
        type=Path,
        help="Path where the sample log file will be written."
    )
    gen_parser.add_argument(
        "--lines",
        type=int,
        default=20,
        dest="line_count",
        help="Number of log entries to generate (default: 20)."
    )

    return parser


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "parse":
        exit_code = parse_log_file(args.log_file)
        sys.exit(exit_code)

    if args.command == "generate":
        if args.line_count <= 0:
            print("❌ Number of lines must be a positive integer.", file=sys.stderr)
            sys.exit(1)
        exit_code = generate_sample_log(args.output_file, args.line_count)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
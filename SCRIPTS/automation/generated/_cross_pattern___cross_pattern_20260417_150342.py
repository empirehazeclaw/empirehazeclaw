#!/usr/bin/env python3
"""
Cross-Pattern Real Error Rate Calculator

This script calculates the real error rate for a cross‑pattern detection task.
It can either read a CSV file containing actual and predicted values, or
generate synthetic binary classification data for demonstration.

Usage:
    python3 cross_pattern_error_rate.py -f data.csv
    python3 cross_pattern_error_rate.py --generate --size 5000 --error-prob 0.0221

The output prints the real error rate in percent.
"""

import sys
import argparse
import csv
import random
import os

def parse_arguments():
    """Parse command‑line arguments."""
    parser = argparse.ArgumentParser(
        description='Calculate Real Error Rate for Cross‑Pattern detection.'
    )
    parser.add_argument(
        '-f', '--file',
        help='Path to CSV file with actual and predicted values. '
             'Expected columns: actual, predicted (or first two numeric columns).',
        default=None
    )
    parser.add_argument(
        '-d', '--delimiter',
        help='CSV delimiter character.',
        default=','
    )
    parser.add_argument(
        '--size',
        type=int,
        help='Number of samples to generate if --generate is used.',
        default=1000
    )
    parser.add_argument(
        '--error-prob',
        type=float,
        help='Probability of misclassification for synthetic data (default: 0.0221).',
        default=0.0221
    )
    parser.add_argument(
        '--output',
        help='Optional path to write the generated CSV (implies --generate).',
        default=None
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate synthetic binary classification data instead of reading a file.'
    )
    return parser.parse_args()

def _is_numeric(value):
    """Return True if value can be interpreted as a number."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def _extract_columns(iterator, col_indices, first_row=None):
    """
    Extract actual and predicted columns from rows.
    col_indices: tuple (actual_index, predicted_index)
    first_row: first row already read (if any)
    """
    rows = []
    if first_row is not None:
        try:
            actual = int(first_row[col_indices[0]])
            predicted = int(first_row[col_indices[1]])
            rows.append((actual, predicted))
        except (ValueError, IndexError):
            # skip malformed first row
            pass
    for row in iterator:
        try:
            actual = int(row[col_indices[0]])
            predicted = int(row[col_indices[1]])
            rows.append((actual, predicted))
        except (ValueError, IndexError):
            # skip malformed rows
            continue
    return rows

def load_csv_data(filepath, delimiter):
    """
    Load actual and predicted values from a CSV file.
    Returns a list of tuples (actual, predicted) after skipping invalid rows.
    """
    rows = []
    try:
        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            first_row = next(reader, None)
            if first_row is None:
                raise ValueError("CSV file is empty.")
            # Detect header: if any cell is non‑numeric, treat as header
            has_header = any(not _is_numeric(cell) for cell in first_row)
            if has_header:
                header = first_row
                header_lower = [col.lower().strip() for col in header]
                if 'actual' in header_lower and 'predicted' in header_lower:
                    act_idx = header_lower.index('actual')
                    pred_idx = header_lower.index('predicted')
                else:
                    # fallback to first two columns
                    act_idx, pred_idx = 0, 1
                rows = _extract_columns(reader, (act_idx, pred_idx), first_row)
            else:
                rows = _extract_columns(reader, (0, 1), first_row)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        raise
    except csv.Error as e:
        print(f"CSV parsing error: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Unexpected error while loading CSV: {e}", file=sys.stderr)
        raise
    return rows

def generate_synthetic_data(size, error_prob):
    """
    Generate synthetic binary classification data.
    Returns a list of tuples (actual, predicted) where the probability
    of a mismatched prediction equals error_prob.
    """
    data = []
    for _ in range(size):
        actual = random.choice([0, 1])
        # Flip prediction with error_prob probability
        if random.random() < error_prob:
            predicted = 1 - actual
        else:
            predicted = actual
        data.append((actual, predicted))
    return data

def compute_confusion_matrix(data):
    """
    Compute confusion matrix counts (TP, TN, FP, FN) for binary classification.
    data: list of (actual, predicted) tuples with values 0 or 1.
    Returns dict with keys 'TP', 'TN', 'FP', 'FN'.
    """
    tp = tn = fp = fn = 0
    for actual, predicted in data:
        if actual not in (0, 1) or predicted not in (0, 1):
            continue
        if actual == 1:
            if predicted == 1:
                tp += 1
            else:
                fn += 1
        else:  # actual == 0
            if predicted == 1:
                fp += 1
            else:
                tn += 1
    return {'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn}

def compute_error_rate(confusion):
    """
    Compute real error rate as percentage.
    Error rate = (FP + FN) / total * 100
    """
    total = confusion['TP'] + confusion['TN'] + confusion['FP'] + confusion['FN']
    if total == 0:
        return float('nan')
    errors = confusion['FP'] + confusion['FN']
    return (errors / total) * 100

def write_csv_data(data, filepath, delimiter):
    """Write data to a CSV file with header 'actual,predicted'."""
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter)
            writer.writerow(['actual', 'predicted'])
            for actual, predicted in data:
                writer.writerow([actual, predicted])
    except IOError as e:
        print(f"Failed to write CSV file: {e}", file=sys.stderr)
        raise

def print_results(confusion, error_rate):
    """Print the confusion matrix and error rate."""
    print("Confusion Matrix:")
    print(f"  TP (True Positives)  : {confusion['TP']}")
    print(f"  TN (True Negatives)  : {confusion['TN']}")
    print(f"  FP (False Positives) : {confusion['FP']}")
    print(f"  FN (False Negatives) : {confusion['FN']}")
    total = confusion['TP'] + confusion['TN'] + confusion['FP'] + confusion['FN']
    print(f"\nTotal samples : {total}")
    print(f"Real Error Rate: {error_rate:.2f}%")

def main():
    args = parse_arguments()
    try:
        if args.generate or args.file is None:
            # Generate synthetic data
            data = generate_synthetic_data(args.size, args.error_prob)
            if args.output:
                write_csv_data(data, args.output, args.delimiter)
                print(f"Synthetic data written to {args.output}")
        else:
            # Load from CSV
            data = load_csv_data(args.file, args.delimiter)
            if not data:
                print("No valid data rows found in the CSV file.", file=sys.stderr)
                sys.exit(1)
        # Compute confusion matrix
        confusion = compute_confusion_matrix(data)
        # Compute real error rate
        error_rate = compute_error_rate(confusion)
        # Output results
        print_results(confusion, error_rate)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
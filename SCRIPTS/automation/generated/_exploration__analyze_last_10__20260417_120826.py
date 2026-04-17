#!/usr/bin/env python3
"""
Analyze the last 10 feedback entries and identify one processing gap.

The script reads a CSV file containing feedback records, extracts the most recent
10 (or fewer if the file contains less), performs a simple analysis, and reports
the first processing gap it encounters (e.g., unprocessed entries, missing
comments, slow processing times, etc.). If no gap is found, it reports that the
pipeline appears healthy.

The CSV is expected to have the following columns:
    id          – unique identifier (int or str)
    timestamp   – ISO‑8601 datetime string
    user        – user name or id
    rating      – integer 1‑5 (optional)
    comment     – free‑text feedback (optional)
    processed   – "true"/"false" indicating whether the entry has been processed
    proc_time   – processing time in seconds (optional)

If the file does not exist, the script can generate a sample dataset for
demonstration purposes (use --generate-sample).
"""

import argparse
import csv
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# --------------------------------------------------------------------------- #
# Helper data structures
# --------------------------------------------------------------------------- #

class FeedbackRecord:
    """Simple container for a feedback entry."""
    __slots__ = ('id', 'timestamp', 'user', 'rating', 'comment',
                 'processed', 'proc_time')

    def __init__(self, row: Dict[str, str]):
        self.id = row.get('id', '').strip()
        self.timestamp = row.get('timestamp', '').strip()
        self.user = row.get('user', '').strip()
        # rating may be absent or empty
        try:
            self.rating = int(row.get('rating', '').strip() or 0)
        except ValueError:
            self.rating = 0
        self.comment = row.get('comment', '').strip()
        # processed is expected to be "true"/"false" (case‑insensitive)
        processed_str = row.get('processed', '').strip().lower()
        self.processed = processed_str == 'true'
        # proc_time may be absent or non‑numeric
        try:
            self.proc_time = float(row.get('proc_time', '').strip() or 0.0)
        except ValueError:
            self.proc_time = 0.0

    def has_missing_comment(self) -> bool:
        return not self.comment

    def __repr__(self) -> str:
        return (f"FeedbackRecord(id={self.id}, timestamp={self.timestamp}, "
                f"processed={self.processed})")


# --------------------------------------------------------------------------- #
# I/O helpers
# --------------------------------------------------------------------------- #

def create_sample_csv(path: Path, num_entries: int = 25) -> None:
    """
    Generate a realistic sample CSV for testing purposes.

    The generated data includes a mix of:
        * Processed / unprocessed entries
        * Missing comments
        * Varied processing times
    """
    fieldnames = ['id', 'timestamp', 'user', 'rating', 'comment',
                  'processed', 'proc_time']

    base_time = datetime.now() - timedelta(days=2)
    users = ["alice", "bob", "carol", "dave", "eve"]
    comments_pool = [
        "Great service!",
        "",
        "Could be better.",
        "I love it!",
        "",
        "No comment.",
        "Terrible experience.",
        "Average.",
    ]

    try:
        with path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(1, num_entries + 1):
                # Randomize the timestamp – newer entries toward the end
                offset = timedelta(minutes=random.randint(0, 2880))
                ts = (base_time + offset + timedelta(minutes=i * 5)).isoformat()
                user = random.choice(users)
                rating = random.randint(1, 5)
                comment = random.choice(comments_pool)
                processed = random.choice(['true', 'true', 'true', 'false'])
                # Some unprocessed entries may have long proc_time, others none
                if processed == 'true':
                    proc_time = round(random.uniform(0.1, 8.0), 2)
                else:
                    proc_time = 0.0

                writer.writerow({
                    'id': i,
                    'timestamp': ts,
                    'user': user,
                    'rating': rating,
                    'comment': comment,
                    'processed': processed,
                    'proc_time': proc_time,
                })
        print(f"[INFO] Sample CSV generated at {path}")
    except OSError as e:
        print(f"[ERROR] Failed to write sample CSV: {e}", file=sys.stderr)
        sys.exit(1)


def load_feedback(path: Path) -> List[FeedbackRecord]:
    """
    Load feedback entries from a CSV file.

    Returns:
        List of FeedbackRecord objects ordered as they appear in the file.
    """
    records: List[FeedbackRecord] = []
    try:
        with path.open('r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    records.append(FeedbackRecord(row))
                except Exception as e:
                    # Skip malformed rows but keep processing the rest
                    print(f"[WARNING] Skipping malformed row: {row} ({e})",
                          file=sys.stderr)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        raise
    except OSError as e:
        print(f"[ERROR] Unable to read file {path}: {e}", file=sys.stderr)
        raise
    return records


# --------------------------------------------------------------------------- #
# Core analysis logic
# --------------------------------------------------------------------------- #

def get_last_n(records: List[FeedbackRecord], n: int) -> List[FeedbackRecord]:
    """Return the most recent `n` entries based on their order in the file."""
    # The file is assumed to be ordered chronologically (oldest first)
    return records[-n:] if len(records) >= n else records


def detect_processing_gap(records: List[FeedbackRecord]) -> Optional[str]:
    """
    Analyze a list of FeedbackRecord objects and return a description of the
    first processing gap encountered, or None if the pipeline looks healthy.

    Detection priority:
        1. Unprocessed entries.
        2. Missing comments.
        3. Slow processing (average > 5 seconds).
    """
    if not records:
        return None

    # 1) Unprocessed entries
    unprocessed = [r for r in records if not r.processed]
    if unprocessed:
        ids = ', '.join(str(r.id) for r in unprocessed[:5])  # show first 5
        return (f"Unprocessed entries found: {len(unprocessed)} "
                f"(IDs: {ids})")

    # 2) Missing comments
    missing_comments = [r for r in records if r.has_missing_comment()]
    if missing_comments:
        ids = ', '.join(str(r.id) for r in missing_comments[:5])
        return (f"Entries missing comments: {len(missing_comments)} "
                f"(IDs: {ids})")

    # 3) Slow processing – consider only processed entries with proc_time > 0
    processed_with_time = [r for r in records if r.processed and r.proc_time > 0]
    if processed_with_time:
        avg_time = sum(r.proc_time for r in processed_with_time) / len(processed_with_time)
        threshold = 5.0  # seconds
        if avg_time > threshold:
            ids = ', '.join(str(r.id) for r in processed_with_time[:5])
            return (f"Average processing time ({avg_time:.2f}s) exceeds "
                    f"threshold ({threshold}s) – IDs: {ids}")

    # No obvious gap
    return None


def format_summary(records: List[FeedbackRecord], gap: Optional[str]) -> str:
    """Build a human‑readable summary string."""
    lines = []
    lines.append("=" * 60)
    lines.append("Feedback Analysis Summary")
    lines.append("=" * 60)
    lines.append(f"Total entries examined: {len(records)}")
    if records:
        processed = sum(1 for r in records if r.processed)
        lines.append(f"  Processed: {processed}")
        lines.append(f"  Unprocessed: {len(records) - processed}")
        missing = sum(1 for r in records if r.has_missing_comment())
        lines.append(f"  Missing comments: {missing}")
        times = [r.proc_time for r in records if r.processed and r.proc_time > 0]
        if times:
            avg = sum(times) / len(times)
            lines.append(f"  Average processing time: {avg:.2f}s")
    lines.append("-" * 60)
    if gap:
        lines.append("PROCESSING GAP DETECTED:")
        lines.append(f"  {gap}")
    else:
        lines.append("No processing gap detected – pipeline looks healthy.")
    lines.append("=" * 60)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI & main entry point
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze last 10 feedback entries for processing gaps."
    )
    parser.add_argument(
        'file',
        nargs='?',
        default='feedback.csv',
        help="Path to feedback CSV (default: feedback.csv).",
    )
    parser.add_argument(
        '-n', '--number',
        type=int,
        default=10,
        help="Number of most recent entries to analyze (default: 10).",
    )
    parser.add_argument(
        '--generate-sample',
        action='store_true',
        help="Generate a sample CSV file if it does not exist and exit.",
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help="Random seed for reproducible sample generation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Optional random seed for reproducible sample data
    if args.seed is not None:
        random.seed(args.seed)

    path = Path(args.file)

    # If the file does not exist and the user asked for a sample, create it.
    if not path.is_file():
        if args.generate_sample:
            create_sample_csv(path)
            # After generation we still want to run the analysis,
            # so fall‑through to the normal flow.
        else:
            print(
                f"[ERROR] File '{path}' not found. "
                "Run with --generate-sample to create a demo file.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Load all feedback entries
    try:
        all_records = load_feedback(path)
    except Exception:
        # load_feedback already printed an error; propagate cleanly.
        sys.exit(1)

    # Grab the last `n` entries for analysis
    last_n = get_last_n(all_records, args.number)

    # Perform gap detection
    gap = detect_processing_gap(last_n)

    # Output results
    print(format_summary(last_n, gap))

    # Exit code indicates whether a gap was found
    sys.exit(0 if gap is None else 1)


if __name__ == '__main__':
    main()
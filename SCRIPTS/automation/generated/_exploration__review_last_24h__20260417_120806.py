#!/usr/bin/env python3
"""
Find the most inefficient API call from the last 24 hours of logs.

The script expects a JSON‑Lines file where each line contains a JSON object
with at least the following keys:
    timestamp   – ISO‑8601 formatted datetime string (e.g. "2023-12-01T10:00:00Z")
    endpoint    – the API endpoint (string)
    method      – HTTP method (string)
    status_code – HTTP status code (int)
    response_time_ms – time taken to respond in milliseconds (float/int)
    request_size_bytes – size of the request payload in bytes (int)
    response_size_bytes – size of the response payload in bytes (int)

Any additional fields are ignored.

The inefficiency score is a weighted sum:
    score = response_time_ms/1000
            + (request_size_bytes + response_size_bytes) / 1024 * 0.1
            + (1 if status_code >= 500 else 0) * 5

The call with the highest score in the last 24 h (by default) is reported.
If no file is supplied the script generates a small set of dummy logs for
demonstration purposes.

Usage
-----
    python3 find_inefficient_api_call.py [--log-file PATH]
                                         [--response-time-threshold MS]
                                         [--hours HOURS]
                                         [--output-json]
"""

import argparse
import datetime
import json
import random
import sys
import typing
from pathlib import Path

# ----------------------------------------------------------------------
# Types
# ----------------------------------------------------------------------
LogEntry = typing.Dict[str, typing.Any]

# ----------------------------------------------------------------------
# Configuration defaults (can be overridden via CLI)
# ----------------------------------------------------------------------
DEFAULT_RESPONSE_TIME_THRESHOLD_MS = 1000.0  # ms
DEFAULT_LOOKBACK_HOURS = 24
DEFAULT_WEIGHTS = {
    "response_time": 1.0,          # weight per second (ms/1000)
    "payload_penalty": 0.1,        # weight per KB
    "server_error": 5.0            # flat penalty if status >= 500
}
ISO_FMT = "%Y-%m-%dT%H:%M:%S"

# ----------------------------------------------------------------------
# Helper: timestamp parsing
# ----------------------------------------------------------------------
def parse_timestamp(ts_str: str) -> datetime.datetime:
    """
    Parse an ISO‑8601 timestamp. Accepts both 'Z' suffix and explicit offset.
    Returns a timezone‑aware datetime in UTC.
    """
    # Normalize 'Z' to +00:00 for fromisoformat compatibility
    if ts_str.endswith("Z"):
        ts_str = ts_str[:-1] + "+00:00"
    try:
        return datetime.datetime.fromisoformat(ts_str)
    except ValueError:
        # Fallback for strict ISO‑8601 without timezone
        dt = datetime.datetime.strptime(ts_str, ISO_FMT)
        return dt.replace(tzinfo=datetime.timezone.utc)


# ----------------------------------------------------------------------
# Helper: log entry validation
# ----------------------------------------------------------------------
REQUIRED_FIELDS = {
    "timestamp",
    "endpoint",
    "method",
    "status_code",
    "response_time_ms",
    "request_size_bytes",
    "response_size_bytes",
}

def validate_entry(entry: typing.Dict[str, typing.Any]) -> bool:
    """Return True if the entry contains all required fields."""
    return REQUIRED_FIELDS.issubset(entry.keys())


# ----------------------------------------------------------------------
# Helper: inefficiency scoring
# ----------------------------------------------------------------------
def compute_score(entry: LogEntry, weights: typing.Dict[str, float]) -> float:
    """
    Compute an inefficiency score for a single log entry.
    Higher scores indicate worse performance.
    """
    try:
        response_time_s = float(entry.get("response_time_ms", 0)) / 1000.0
        req_size_kb = float(entry.get("request_size_bytes", 0)) / 1024.0
        resp_size_kb = float(entry.get("response_size_bytes", 0)) / 1024.0
        status = int(entry.get("status_code", 200))
    except (ValueError, TypeError):
        # If any numeric conversion fails, treat entry as neutral.
        return 0.0

    score = (
        response_time_s * weights.get("response_time", 1.0)
        + (req_size_kb + resp_size_kb) * weights.get("payload_penalty", 0.1)
        + (5.0 if status >= 500 else 0.0) * weights.get("server_error", 1.0)
    )
    return score


# ----------------------------------------------------------------------
# Core logic
# ----------------------------------------------------------------------
def load_logs(path: typing.Optional[Path]) -> typing.List[LogEntry]:
    """
    Load JSON‑Lines log file and return a list of entries.
    If path is None, generate a small sample dataset.
    """
    if path is None:
        # Produce demo data for the last 2 hours
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        sample_logs = []
        for i in range(20):
            # Random timestamp within last 2 h
            delta = datetime.timedelta(
                minutes=random.randint(0, 120),
                seconds=random.randint(0, 59)
            )
            ts = now - delta
            entry: LogEntry = {
                "timestamp": ts.isoformat(),
                "endpoint": random.choice(["/api/users", "/api/orders", "/api/products"]),
                "method": random.choice(["GET", "POST", "PUT"]),
                "status_code": random.choices(
                    [200, 201, 400, 404, 500, 502],
                    weights=[60, 10, 10, 10, 5, 5]
                )[0],
                "response_time_ms": random.choices(
                    [50, 150, 300, 800, 1200, 3000],
                    weights=[40, 30, 15, 8, 4, 3]
                )[0],
                "request_size_bytes": random.randint(0, 5000),
                "response_size_bytes": random.randint(100, 200000),
            }
            sample_logs.append(entry)
        return sample_logs

    # Real file loading
    logs: typing.List[LogEntry] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    print(
                        f"[WARNING] Skipping line {line_no} due to JSON decode error: {e}",
                        file=sys.stderr,
                    )
                    continue
                if not validate_entry(entry):
                    print(
                        f"[WARNING] Skipping line {line_no} – missing required fields.",
                        file=sys.stderr,
                    )
                    continue
                logs.append(entry)
    except OSError as e:
        print(f"[ERROR] Unable to read log file {path}: {e}", file=sys.stderr)
        sys.exit(1)
    return logs


def filter_last_hours(
    logs: typing.List[LogEntry],
    hours: int = DEFAULT_LOOKBACK_HOURS,
    reference_time: typing.Optional[datetime.datetime] = None,
) -> typing.List[LogEntry]:
    """
    Return only those log entries whose timestamp falls within the last `hours`
    hours before `reference_time` (defaults to now).
    """
    if reference_time is None:
        reference_time = datetime.datetime.now(tz=datetime.timezone.utc)
    cutoff = reference_time - datetime.timedelta(hours=hours)

    filtered: typing.List[LogEntry] = []
    for entry in logs:
        try:
            ts = parse_timestamp(entry["timestamp"])
        except Exception as e:
            print(
                f"[WARNING] Could not parse timestamp '{entry.get('timestamp')}': {e}",
                file=sys.stderr,
            )
            continue
        if ts >= cutoff:
            filtered.append(entry)
    return filtered


def find_most_inefficient(
    logs: typing.List[LogEntry],
    response_time_threshold_ms: float = DEFAULT_RESPONSE_TIME_THRESHOLD_MS,
    weights: typing.Dict[str, float] = None,
) -> typing.Optional[LogEntry]:
    """
    Find the log entry with the highest inefficiency score.
    If `response_time_threshold_ms` is > 0, entries below this threshold are
    ignored (unless no entry exceeds the threshold, in which case the worst
    overall is returned).
    Returns None if the input list is empty.
    """
    if not logs:
        return None
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Compute scores for all entries
    scored = []
    for entry in logs:
        score = compute_score(entry, weights)
        # Optionally filter out entries below the response‑time threshold
        if (
            response_time_threshold_ms > 0
            and entry.get("response_time_ms", 0) < response_time_threshold_ms
        ):
            # keep but mark as low‑priority by adding a huge penalty to avoid selecting it
            # unless nothing else qualifies.
            low_priority = True
        else:
            low_priority = False
        scored.append((score, low_priority, entry))

    # Sort: primary key = score descending, secondary = low_priority ascending
    scored.sort(key=lambda x: (x[0], 0 if x[1] else 1), reverse=True)

    # Return the top entry (if there are low‑priority entries only, they'll be returned)
    return scored[0][2] if scored else None


def format_entry(entry: LogEntry, score: float) -> str:
    """Create a human‑readable representation of the selected entry."""
    ts = entry.get("timestamp", "N/A")
    endpoint = entry.get("endpoint", "N/A")
    method = entry.get("method", "N/A")
    status = entry.get("status_code", "N/A")
    resp_time = entry.get("response_time_ms", "N/A")
    req_size = entry.get("request_size_bytes", "N/A")
    resp_size = entry.get("response_size_bytes", "N/A")

    lines = [
        "=" * 60,
        "Most inefficient API call (last 24 h)",
        "=" * 60,
        f"  Timestamp           : {ts}",
        f"  Endpoint            : {endpoint}",
        f"  Method              : {method}",
        f"  Status Code         : {status}",
        f"  Response Time (ms)  : {resp_time}",
        f"  Request Size (B)    : {req_size}",
        f"  Response Size (B)   : {resp_size}",
        f"  Inefficiency Score  : {score:.3f}",
        "=" * 60,
    ]
    return "\n".join(lines)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find the most inefficient API call from recent logs."
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Path to a JSON‑Lines file containing API call logs. "
        "If omitted, a built‑in sample dataset is used.",
    )
    parser.add_argument(
        "--response-time-threshold-ms",
        type=float,
        default=DEFAULT_RESPONSE_TIME_THRESHOLD_MS,
        help="Minimum response time (ms) to consider a call potentially inefficient. "
        f"Default: {DEFAULT_RESPONSE_TIME_THRESHOLD_MS}",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=DEFAULT_LOOKBACK_HOURS,
        help=f"Number of hours to look back from now. Default: {DEFAULT_LOOKBACK_HOURS}",
    )
    parser.add_argument(
        "--reference-time",
        type=str,
        default=None,
        help="ISO‑8601 timestamp to use as 'now' (overrides system time). "
        "Example: 2024-01-15T12:00:00Z",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output the selected log entry as JSON (including the computed score) "
        "instead of human‑readable text.",
    )
    return parser


def main(argv: typing.List[str] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Determine reference time
    reference_time: typing.Optional[datetime.datetime] = None
    if args.reference_time:
        try:
            reference_time = parse_timestamp(args.reference_time)
        except Exception as e:
            print(
                f"[ERROR] Invalid reference time format: {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    # Load logs
    logs = load_logs(args.log_file)

    # Filter to last N hours
    filtered_logs = filter_last_hours(logs, hours=args.hours, reference_time=reference_time)

    if not filtered_logs:
        print("[INFO] No API calls found within the specified time window.")
        sys.exit(0)

    # Find the most inefficient call
    candidate = find_most_inefficient(
        filtered_logs,
        response_time_threshold_ms=args.response_time_threshold_ms,
        weights=DEFAULT_WEIGHTS,
    )

    if candidate is None:
        print("[INFO] Unable to determine an inefficient call.")
        sys.exit(0)

    # Compute its score for reporting
    score = compute_score(candidate, DEFAULT_WEIGHTS)

    # Output
    if args.output_json:
        result = dict(candidate)
        result["inefficiency_score"] = score
        print(json.dumps(result, indent=2))
    else:
        print(format_entry(candidate, score))


if __name__ == "__main__":
    main()
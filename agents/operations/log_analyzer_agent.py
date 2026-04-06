#!/usr/bin/env python3
"""
Log Analyzer Agent - Operations
Analyzes log files for errors, warnings, patterns and anomalies.
Based on SOUL.md principles: proactive monitoring, quick issue detection.
"""

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "log_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LogAnalyzer")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_CACHE_FILE = DATA_DIR / "log_analysis_cache.json"

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"]


def parse_log_line(line: str) -> Dict:
    """Parse a single log line and extract components."""
    result = {
        "raw": line,
        "timestamp": None,
        "level": None,
        "source": None,
        "message": line
    }
    
    # Common timestamp patterns
    timestamp_patterns = [
        r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)',
        r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
        r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',
    ]
    
    for pattern in timestamp_patterns:
        match = re.search(pattern, line)
        if match:
            result["timestamp"] = match.group(1)
            break
    
    # Log level pattern
    level_match = re.search(r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)\b', line, re.IGNORECASE)
    if level_match:
        result["level"] = level_match.group(1).upper()
    
    # Source pattern (often in brackets or before colon)
    source_match = re.search(r'\[([^\]]+)\]|\<([^\>]+)\>|([\w\.]+):', line)
    if source_match:
        result["source"] = source_match.group(1) or source_match.group(2) or source_match.group(3)
    
    return result


def analyze_log_file(filepath: str, max_lines: int = 10000) -> Dict:
    """Analyze a log file and return statistics and findings."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")
    
    stats = {
        "filepath": str(path),
        "total_lines": 0,
        "levels": Counter(),
        "sources": Counter(),
        "errors": [],
        "warnings": [],
        "patterns": Counter(),
        "anomalies": [],
        "time_range": None,
        "parsed_at": datetime.utcnow().isoformat()
    }
    
    timestamps = []
    error_patterns = [
        r'exception',
        r'error',
        r'failed',
        r'failure',
        r'cannot',
        r'unable to',
        r'timeout',
        r'connection refused',
        r'permission denied',
    ]
    
    try:
        with open(path, 'r', errors='ignore') as f:
            lines = f.readlines()[-max_lines:]  # Read last N lines
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                stats["total_lines"] += 1
                parsed = parse_log_line(line)
                
                # Count levels
                if parsed["level"]:
                    stats["levels"][parsed["level"]] += 1
                
                # Count sources
                if parsed["source"]:
                    stats["sources"][parsed["source"]] += 1
                
                # Track timestamps
                if parsed["timestamp"]:
                    timestamps.append(parsed["timestamp"])
                
                # Collect errors
                if parsed["level"] in ["ERROR", "CRITICAL", "FATAL"]:
                    stats["errors"].append({
                        "line": stats["total_lines"],
                        "message": parsed["message"][:200],
                        "timestamp": parsed["timestamp"],
                        "source": parsed["source"]
                    })
                elif any(re.search(p, line, re.IGNORECASE) for p in error_patterns):
                    if parsed["level"] not in ["ERROR", "CRITICAL"]:
                        stats["warnings"].append({
                            "line": stats["total_lines"],
                            "message": parsed["message"][:200],
                            "timestamp": parsed["timestamp"]
                        })
                
                # Detect patterns (extract meaningful tokens)
                words = re.findall(r'\b\w{4,}\b', line.lower())
                for word in words[:5]:  # First 5 words
                    if word not in ['error', 'info', 'warn', 'debug', 'the', 'and', 'for']:
                        stats["patterns"][word] += 1
        
        # Time range
        if timestamps:
            stats["time_range"] = {
                "first": timestamps[0],
                "last": timestamps[-1]
            }
        
        # Detect anomalies
        stats["anomalies"] = detect_anomalies(stats)
        
        logger.info(f"Analyzed {stats['total_lines']} lines from {filepath}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to analyze log file: {e}")
        raise


def detect_anomalies(stats: Dict) -> List[Dict]:
    """Detect anomalies in log statistics."""
    anomalies = []
    
    # Too many errors
    error_count = sum(stats["levels"].get(l, 0) for l in ["ERROR", "CRITICAL", "FATAL"])
    if stats["total_lines"] > 0:
        error_rate = error_count / stats["total_lines"]
        if error_rate > 0.05:  # More than 5% errors
            anomalies.append({
                "type": "high_error_rate",
                "severity": "high",
                "message": f"Error rate is {error_rate*100:.1f}% ({error_count} errors)"
            })
    
    # New error sources
    if len(stats["errors"]) > 5:
        recent_errors = stats["errors"][-5:]
        error_sources = set(e.get("source") for e in recent_errors)
        if len(error_sources) > 3:
            anomalies.append({
                "type": "multiple_error_sources",
                "severity": "medium",
                "message": f"Multiple error sources detected: {', '.join(error_sources)}"
            })
    
    # Repeated patterns
    for pattern, count in stats["patterns"].most_common(10):
        if count > stats["total_lines"] * 0.1:  # Same pattern > 10% of log
            anomalies.append({
                "type": "repeated_pattern",
                "severity": "low",
                "message": f"Pattern '{pattern}' appears {count} times"
            })
            break
    
    return anomalies


def search_logs(filepath: str, pattern: str, case_sensitive: bool = False,
                context_lines: int = 2) -> List[Dict]:
    """Search logs for a pattern with context."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")
    
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern, flags)
    
    results = []
    try:
        with open(path, 'r', errors='ignore') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if regex.search(line):
                context = {
                    "line_number": i + 1,
                    "match": line.strip(),
                    "before": [lines[j].strip() for j in range(max(0, i-context_lines), i)],
                    "after": [lines[j].strip() for j in range(i+1, min(len(lines), i+context_lines+1))]
                }
                results.append(context)
                
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise
    
    return results


def get_recent_errors(filepath: str, hours: int = 24, limit: int = 50) -> List[Dict]:
    """Get recent errors from a log file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")
    
    errors = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    try:
        with open(path, 'r', errors='ignore') as f:
            for line in f:
                parsed = parse_log_line(line)
                if parsed["level"] in ["ERROR", "CRITICAL", "FATAL"]:
                    # Simple timestamp check (assumes recent logs)
                    if parsed["timestamp"]:
                        try:
                            ts = datetime.fromisoformat(parsed["timestamp"].replace("Z", "+00:00"))
                            if ts > cutoff:
                                errors.append({
                                    "message": parsed["message"][:300],
                                    "source": parsed["source"],
                                    "timestamp": parsed["timestamp"]
                                })
                        except:
                            # If timestamp parsing fails, include anyway
                            errors.append({
                                "message": parsed["message"][:300],
                                "source": parsed["source"],
                                "timestamp": parsed["timestamp"]
                            })
                if len(errors) >= limit:
                    break
                    
    except Exception as e:
        logger.error(f"Failed to get recent errors: {e}")
        raise
    
    return errors


def generate_report(filepath: str, output_format: str = "text") -> str:
    """Generate a formatted analysis report."""
    stats = analyze_log_file(filepath)
    
    if output_format == "json":
        # Convert Counter objects to dicts for JSON serialization
        stats_json = stats.copy()
        stats_json["levels"] = dict(stats["levels"])
        stats_json["sources"] = dict(stats["sources"])
        stats_json["patterns"] = dict(stats["patterns"])
        return json.dumps(stats_json, indent=2)
    
    # Text format
    report = []
    report.append("=" * 60)
    report.append(f"LOG ANALYSIS REPORT: {filepath}")
    report.append("=" * 60)
    report.append(f"\nParsed at: {stats['parsed_at']}")
    report.append(f"Total lines analyzed: {stats['total_lines']:,}")
    
    if stats["time_range"]:
        report.append(f"\nTime range: {stats['time_range']['first']} to {stats['time_range']['last']}")
    
    report.append("\n" + "-" * 40)
    report.append("LOG LEVEL DISTRIBUTION")
    report.append("-" * 40)
    for level in LOG_LEVELS:
        count = stats["levels"].get(level, 0)
        if count > 0:
            pct = count / stats["total_lines"] * 100
            bar = "█" * int(pct / 2)
            report.append(f"  {level:8} {count:6,} ({pct:5.1f}%) {bar}")
    
    report.append("\n" + "-" * 40)
    report.append("TOP SOURCES")
    report.append("-" * 40)
    for source, count in stats["sources"].most_common(10):
        report.append(f"  {source}: {count:,}")
    
    if stats["errors"]:
        report.append("\n" + "-" * 40)
        report.append(f"RECENT ERRORS ({len(stats['errors'])} total)")
        report.append("-" * 40)
        for err in stats["errors"][-10:]:
            report.append(f"  [Line {err['line']}] {err['message'][:80]}")
    
    if stats["anomalies"]:
        report.append("\n" + "-" * 40)
        report.append("DETECTED ANOMALIES")
        report.append("-" * 40)
        for anomaly in stats["anomalies"]:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(anomaly["severity"], "⚪")
            report.append(f"  {severity_icon} {anomaly['type']}: {anomaly['message']}")
    
    report.append("\n" + "=" * 60)
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Log Analyzer Agent - Analyze log files for errors and patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze --file /var/log/syslog
  %(prog)s analyze --file /home/clawbot/.openclaw/workspace/logs/ticket_manager.log --max-lines 5000
  %(prog)s search --file /var/log/syslog --pattern "error|failed"
  %(prog)s errors --file /var/log/syslog --hours 24
  %(prog)s report --file /var/log/syslog
  %(prog)s report --file /var/log/syslog --format json
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a log file")
    analyze_parser.add_argument("--file", "-f", required=True, help="Path to log file")
    analyze_parser.add_argument("--max-lines", "-n", type=int, default=10000, help="Max lines to analyze")

    # Search
    search_parser = subparsers.add_parser("search", help="Search logs for pattern")
    search_parser.add_argument("--file", "-f", required=True, help="Path to log file")
    search_parser.add_argument("--pattern", "-p", required=True, help="Search pattern (regex)")
    search_parser.add_argument("--case-sensitive", "-c", action="store_true", help="Case sensitive")
    search_parser.add_argument("--context", type=int, default=2, help="Context lines")

    # Errors
    errors_parser = subparsers.add_parser("errors", help="Get recent errors")
    errors_parser.add_argument("--file", "-f", required=True, help="Path to log file")
    errors_parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    errors_parser.add_argument("--limit", "-l", type=int, default=50, help="Max errors to return")

    # Report
    report_parser = subparsers.add_parser("report", help="Generate full analysis report")
    report_parser.add_argument("--file", "-f", required=True, help="Path to log file")
    report_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "analyze":
            stats = analyze_log_file(args.file, max_lines=args.max_lines)
            print(f"\n📊 Analysis of: {stats['filepath']}")
            print(f"   Total lines: {stats['total_lines']:,}")
            print(f"   Errors: {stats['levels'].get('ERROR', 0)}")
            print(f"   Warnings: {stats['levels'].get('WARNING', 0)}")
            print(f"   Anomalies detected: {len(stats['anomalies'])}")

        elif args.command == "search":
            print(f"🔍 Searching for: {args.pattern}\n")
            results = search_logs(args.file, args.pattern,
                                 case_sensitive=args.case_sensitive,
                                 context_lines=args.context)
            if not results:
                print("No matches found.")
            else:
                print(f"Found {len(results)} match(es):\n")
                for r in results[:20]:
                    print(f"  Line {r['line_number']}:")
                    for before in r['before']:
                        print(f"    │ {before}")
                    print(f"    → {r['match']}")
                    for after in r['after']:
                        print(f"    │ {after}")
                    print()

        elif args.command == "errors":
            print(f"⚠️  Recent errors (last {args.hours} hours):\n")
            errors = get_recent_errors(args.file, hours=args.hours, limit=args.limit)
            if not errors:
                print("No recent errors found.")
            else:
                for err in errors:
                    print(f"  [{err.get('timestamp', '?')}] {err['message'][:80]}")

        elif args.command == "report":
            report = generate_report(args.file, output_format=args.format)
            print(report)

        return 0

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

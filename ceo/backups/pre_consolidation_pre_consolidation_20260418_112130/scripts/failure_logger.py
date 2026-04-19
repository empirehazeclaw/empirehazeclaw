#!/usr/bin/env python3
"""
Failure Logger — Phase 1, Day 1
===============================
Erfasst alle Failures systematisch für das Deep Learning Improvement Plan Projekt.

Usage:
    python3 failure_logger.py --log "<description>" [--severity high|medium|low] [--cause cause_type] [--tags tag1,tag2]
    python3 failure_logger.py --list [--severity high] [--limit 10]
    python3 failure_logger.py --stats
    python3 failure_logger.py --export
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# === CONFIG ===
WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
LOG_DIR = WORKSPACE / "memory" / "failures"
LOG_FILE = LOG_DIR / "failure_log.json"
METRICS_FILE = LOG_DIR / "failure_metrics.json"
CAUSE_ONTOLOGY_FILE = LOG_DIR / "cause_ontology.json"

SEVERITY_LEVELS = ["critical", "high", "medium", "low"]
CAUSE_TYPES = [
    "timeout", "api_error", "validation_error", "permission_denied",
    "resource_exhausted", "network_failure", "dependency_missing",
    "invalid_input", "logic_error", "unknown", "design_gap", "bias_confirmed",
    "context_truncation", "model_weakness", "tool_failure", "orchestration_error"
]

# === INIT ===
def init_dirs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text(json.dumps({"failures": [], "version": "1.0"}))
    if not METRICS_FILE.exists():
        METRICS_FILE.write_text(json.dumps({
            "total": 0, "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "by_cause": {}, "last_updated": datetime.now(timezone.utc).isoformat()
        }))
    if not CAUSE_ONTOLOGY_FILE.exists():
        CAUSE_ONTOLOGY_FILE.write_text(json.dumps({
            "ontology": CAUSE_TYPES,
            "descriptions": {
                "timeout": "Operation exceeded time limit",
                "api_error": "External API returned error",
                "validation_error": "Input validation failed",
                "permission_denied": "Access permission issue",
                "resource_exhausted": "Memory/CPU/disk limits hit",
                "network_failure": "Network connectivity issue",
                "dependency_missing": "Required dependency not found",
                "invalid_input": "Input data malformed or out of range",
                "logic_error": "Internal logic produced wrong result",
                "unknown": "Cause could not be determined",
                "design_gap": "System design missed a use case",
                "bias_confirmed": "Model bias observed in output",
                "context_truncation": "Context window overflow",
                "model_weakness": "Model capability limitation",
                "tool_failure": "Tool/script execution failed",
                "orchestration_error": "Multi-step coordination failed"
            }
        }, indent=2))

# === CORE LOGGING ===
def log_failure(
    description: str,
    severity: str = "medium",
    cause: str = "unknown",
    tags: Optional[list] = None,
    context: Optional[dict] = None,
    resolution: Optional[str] = None,
    related_learning: Optional[str] = None
) -> dict:
    """Log a new failure entry."""
    init_dirs()
    
    data = json.loads(LOG_FILE.read_text())
    
    failure = {
        "id": len(data["failures"]) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": description,
        "severity": severity,
        "cause": cause,
        "tags": tags or [],
        "context": context or {},
        "resolution": resolution,
        "related_learning": related_learning,
        "status": "open"
    }
    
    data["failures"].append(failure)
    LOG_FILE.write_text(json.dumps(data, indent=2))
    
    update_metrics(severity, cause)
    
    print(f"✅ [#{failure['id']}] Failure logged: {description[:60]}...")
    print(f"   Severity: {severity} | Cause: {cause}")
    return failure

def update_metrics(severity: str, cause: str):
    """Update aggregated metrics."""
    metrics = json.loads(METRICS_FILE.read_text())
    metrics["total"] += 1
    metrics["by_severity"][severity] = metrics["by_severity"].get(severity, 0) + 1
    metrics["by_cause"][cause] = metrics["by_cause"].get(cause, 0) + 1
    metrics["last_updated"] = datetime.now(timezone.utc).isoformat()
    METRICS_FILE.write_text(json.dumps(metrics, indent=2))

# === QUERY ===
def list_failures(severity: Optional[str] = None, limit: int = 20, status: Optional[str] = None):
    """List failures with optional filters."""
    init_dirs()
    data = json.loads(LOG_FILE.read_text())
    
    failures = data["failures"]
    if severity:
        failures = [f for f in failures if f.get("severity") == severity]
    if status:
        failures = [f for f in failures if f.get("status") == status]
    
    failures = sorted(failures, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    if not failures:
        print("📭 Keine Failures gefunden.")
        return
    
    print(f"\n📋 Failure Log ({len(failures)} von {data['failures'].__len__()} angezeigt)\n")
    for f in failures:
        ts = f["timestamp"][:16]
        print(f"  [{f['severity'].upper():8}] #{f['id']} @ {ts}")
        print(f"             {f['description'][:70]}")
        print(f"             Cause: {f['cause']} | Tags: {', '.join(f.get('tags', [])) or 'none'}")
        if f.get("resolution"):
            print(f"             ✅ {f['resolution'][:50]}")
        print()

def stats():
    """Show failure statistics."""
    init_dirs()
    metrics = json.loads(METRICS_FILE.read_text())
    
    print("\n📊 Failure Statistics")
    print("=" * 40)
    print(f"  Total:       {metrics['total']}")
    print(f"  Critical:    {metrics['by_severity'].get('critical', 0)}")
    print(f"  High:        {metrics['by_severity'].get('high', 0)}")
    print(f"  Medium:      {metrics['by_severity'].get('medium', 0)}")
    print(f"  Low:         {metrics['by_severity'].get('low', 0)}")
    print("\n  By Cause:")
    for cause, count in sorted(metrics["by_cause"].items(), key=lambda x: -x[1]):
        print(f"    {cause:25} {count}")
    print()

def export():
    """Export all failures as structured JSON."""
    init_dirs()
    data = json.loads(LOG_FILE.read_text())
    export_path = LOG_DIR / f"failure_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    export_path.write_text(json.dumps(data, indent=2))
    print(f"📦 Exportiert: {export_path}")
    return export_path

def resolve_failure(failure_id: int, resolution: str):
    """Mark a failure as resolved."""
    init_dirs()
    data = json.loads(LOG_FILE.read_text())
    
    for f in data["failures"]:
        if f["id"] == failure_id:
            f["status"] = "resolved"
            f["resolution"] = resolution
            f["resolved_at"] = datetime.now(timezone.utc).isoformat()
            LOG_FILE.write_text(json.dumps(data, indent=2))
            print(f"✅ [#{failure_id}] Marked as resolved: {resolution[:60]}")
            return
    
    print(f"❌ Failure #{failure_id} nicht gefunden.")

# === CLI ===
def main():
    parser = argparse.ArgumentParser(description="Failure Logger — Deep Learning Phase 1")
    parser.add_argument("--log", help="Failure description")
    parser.add_argument("--severity", default="medium", choices=SEVERITY_LEVELS)
    parser.add_argument("--cause", default="unknown", choices=CAUSE_TYPES)
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--context", help="JSON context object")
    parser.add_argument("--resolution", help="Resolution description")
    parser.add_argument("--related-learning", help="Related learning entity ID")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--resolve", type=int, help="Resolve failure by ID")
    parser.add_argument("--resolve-text", help="Resolution text for --resolve")
    parser.add_argument("--severity-filter", help="Filter by severity for --list")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--status", help="Filter by status (open/resolved)")
    
    args = parser.parse_args()
    
    if args.log:
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        context = json.loads(args.context) if args.context else None
        log_failure(
            description=args.log,
            severity=args.severity,
            cause=args.cause,
            tags=tags,
            context=context,
            resolution=args.resolution,
            related_learning=args.related_learning
        )
    elif args.list:
        list_failures(severity=args.severity_filter, limit=args.limit, status=args.status)
    elif args.stats:
        stats()
    elif args.export:
        export()
    elif args.resolve:
        resolve_failure(args.resolve, args.resolve_text or "Resolved")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

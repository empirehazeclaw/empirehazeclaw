#!/usr/bin/env python3
"""
blast_radius_estimator.py — Estimate and Track Change Impact
Sir HazeClaw - 2026-04-11

Estimates blast radius BEFORE changes, tracks actual AFTER.

Usage:
    python3 blast_radius_estimator.py --estimate
    python3 blast_radius_estimator.py --log --actual 50 --estimated 30
    python3 blast_radius_estimator.py --accuracy
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
BLAST_LOG = WORKSPACE / "data" / "blast_radius_log.json"

def load_log():
    if BLAST_LOG.exists():
        with open(BLAST_LOG) as f:
            return json.load(f)
    return {"estimates": [], "accuracy": []}

def save_log(data):
    BLAST_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(BLAST_LOG, "w") as f:
        json.dump(data, f, indent=2)

def estimate_blast_radius():
    """Estimate blast radius of pending changes."""
    # Get git status
    result = subprocess.run( 
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=WORKSPACE
    )
    
    files = result.stdout.strip().split("\n")
    files = [f for f in files if f]
    
    # Categorize by impact
    high_impact = ["core_ultralight", "scripts/learning", "scripts/cron"]
    medium_impact = ["scripts", "skills", "memory"]
    low_impact = ["docs", "skills/_library", "logs"]
    
    estimated_files = len(files)
    estimated_lines = 0
    
    for f in files:
        path = f.split()[1] if len(f.split()) > 1 else f
        for hi in high_impact:
            if hi in path:
                estimated_files += 5  # High impact = more files affected
        for mi in medium_impact:
            if mi in path:
                estimated_files += 2
    
    return {
        "files_changed": estimated_files,
        "estimated": True,
        "timestamp": datetime.now().isoformat()
    }

def log_actual(actual, estimated):
    """Log actual blast radius vs estimated."""
    data = load_log()
    
    entry = {
        "actual": actual,
        "estimated": estimated,
        "ratio": actual / estimated if estimated > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    
    data["accuracy"].append(entry)
    data["accuracy"] = data["accuracy"][-20:]  # Keep last 20
    
    save_log(data)
    
    ratio = entry["ratio"]
    accuracy = 1 - abs(ratio - 1)
    
    print(f"📊 Blast Radius Logging:")
    print(f"   Estimated: {estimated} files")
    print(f"   Actual: {actual} files")
    print(f"   Ratio: {ratio:.2f}x")
    print(f"   Accuracy: {accuracy * 100:.0f}%")
    
    if ratio > 2:
        print(f"   ⚠️ WARNING: Ratio > 2x — estimation needs improvement!")
    
    return ratio

def show_accuracy():
    """Show blast radius accuracy stats."""
    data = load_log()
    accuracy = data.get("accuracy", [])
    
    print("📊 BLAST RADIUS ACCURACY")
    print("=" * 50)
    
    if not accuracy:
        print("No data yet. Log evolution results with --log")
        return
    
    # Calculate stats
    ratios = [e["ratio"] for e in accuracy]
    avg_ratio = sum(ratios) / len(ratios)
    min_ratio = min(ratios)
    max_ratio = max(ratios)
    
    # Good accuracy = ratio close to 1.0
    good_count = sum(1 for r in ratios if 0.7 <= r <= 1.5)
    bad_count = len(ratios) - good_count
    
    print(f"\n📈 Statistics:")
    print(f"   Average Ratio: {avg_ratio:.2f}x")
    print(f"   Min Ratio: {min_ratio:.2f}x")
    print(f"   Max Ratio: {max_ratio:.2f}x")
    print(f"   Good Accuracy (< 1.5x): {good_count}/{len(ratios)}")
    print(f"   Poor Accuracy (> 2x): {bad_count}/{len(ratios)}")
    
    print(f"\n📋 Recent Logs:")
    for e in accuracy[-5:]:
        ratio = e["ratio"]
        status = "✅" if ratio <= 1.5 else "⚠️" if ratio <= 2 else "❌"
        date = e["timestamp"][:10]
        print(f"   {status} {date}: {ratio:.2f}x ({e['estimated']} → {e['actual']})")
    
    if bad_count > len(ratios) / 2:
        print("\n⚠️ ACTION NEEDED: Estimation needs training!")
        print("   → Log more results to improve accuracy")

def main():
    if "--log" in sys.argv:
        actual = estimated = None
        for i, arg in enumerate(sys.argv):
            if arg == "--actual" and i + 1 < len(sys.argv):
                actual = float(sys.argv[i + 1])
            if arg == "--estimated" and i + 1 < len(sys.argv):
                estimated = float(sys.argv[i + 1])
        
        if actual and estimated:
            log_actual(actual, estimated)
        return
    
    if "--accuracy" in sys.argv:
        show_accuracy()
        return
    
    # Default: estimate
    result = estimate_blast_radius()
    print(f"📊 BLAST RADIUS ESTIMATE:")
    print(f"   Files: ~{result['files_changed']}")
    print(f"   Note: Run --accuracy to see historical accuracy")

if __name__ == "__main__":
    main()

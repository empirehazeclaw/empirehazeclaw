#!/usr/bin/env python3
"""
Contrastive Analyzer — Phase 1, Day 3
======================================
Findet Success/Failure Paare bei ähnlichen Tasks und analysiert die Unterschiede.

Usage:
    python3 contrastive_analyzer.py --analyze
    python3 contrastive_analyzer.py --pairs [--limit 20]
    python3 contrastive_analyzer.py --mine
    python3 contrastive_analyzer.py --stats
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional, List, Dict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
MEMORY_DIR = WORKSPACE / "memory"
FAILURE_LOG = MEMORY_DIR / "failures" / "failure_log.json"
LEARNING_SIGNAL = MEMORY_DIR / "evaluations" / "learning_loop_signal.json"
CONTRAST_DIR = MEMORY_DIR / "evaluations" / "contrastive"
PAIRS_FILE = CONTRAST_DIR / "contrast_pairs.json"
STATS_FILE = CONTRAST_DIR / "contrastive_stats.json"

def init_dirs():
    CONTRAST_DIR.mkdir(parents=True, exist_ok=True)
    if not PAIRS_FILE.exists():
        PAIRS_FILE.write_text(json.dumps({"pairs": [], "version": "1.0"}))
    if not STATS_FILE.exists():
        STATS_FILE.write_text(json.dumps({
            "total_pairs": 0, "analyzed_pairs": 0, "insights_found": 0,
            "by_type": {}, "last_analysis": None
        }))

def load_failures():
    if not FAILURE_LOG.exists():
        return []
    return json.loads(FAILURE_LOG.read_text()).get("failures", [])

def load_learning_signal():
    if not LEARNING_SIGNAL.exists():
        return {"task_history": [], "patterns": [], "evaluations": []}
    return json.loads(LEARNING_SIGNAL.read_text())

def load_pairs():
    init_dirs()
    return json.loads(PAIRS_FILE.read_text())

def save_pairs(data):
    PAIRS_FILE.write_text(json.dumps(data, indent=2))

def load_stats():
    init_dirs()
    return json.loads(STATS_FILE.read_text())

def save_stats(data):
    STATS_FILE.write_text(json.dumps(data, indent=2))

def extract_task_context(task: dict) -> dict:
    """Extract normalized context from a task for comparison."""
    return {
        "type": task.get("task_type", task.get("type", "unknown")),
        "time_bucket": get_time_bucket(task.get("timestamp", "")),
        "user": task.get("user", "system"),
        "tags": sorted(task.get("tags", [])),
        "has_context": bool(task.get("context")),
        "attempt": task.get("attempt", 1)
    }

def get_time_bucket(timestamp: str) -> str:
    """Bucket timestamp into time-of-day categories."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        hour = dt.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 23:
            return "evening"
        else:
            return "night"
    except:
        return "unknown"

def normalize_context(ctx: dict) -> str:
    """Create a normalized context signature for comparison."""
    parts = [
        ctx.get("type", "?"),
        ctx.get("time_bucket", "?"),
        ctx.get("user", "?"),
        str(ctx.get("has_context", False)),
        str(ctx.get("attempt", 1))
    ]
    return "|".join(parts)

def find_contrast_pairs() -> List[dict]:
    """Find pairs of similar tasks where one succeeded and one failed."""
    failures = load_failures()
    learning = load_learning_signal()
    
    # Build task history from learning signal
    task_history = learning.get("task_history", [])
    successful_tasks = [t for t in task_history if t.get("status") == "success" or t.get("success")]
    
    # Add successful task context extraction
    success_contexts = {}
    for task in successful_tasks:
        ctx = extract_task_context(task)
        sig = normalize_context(ctx)
        if sig not in success_contexts:
            success_contexts[sig] = []
        success_contexts[sig].append(task)
    
    pairs = []
    pair_id = 1
    
    for failure in failures:
        fail_ctx = extract_task_context(failure)
        fail_sig = normalize_context(fail_ctx)
        
        # Find matching successes
        if fail_sig in success_contexts:
            for success in success_contexts[fail_sig][:3]:  # Max 3 matches per failure
                pairs.append({
                    "pair_id": pair_id,
                    "failure_id": failure["id"],
                    "success_task_id": success.get("task_id", "unknown"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "context_signature": fail_sig,
                    "failure_context": fail_ctx,
                    "success_context": extract_task_context(success),
                    "failure_description": failure["description"],
                    "success_outcome": success.get("outcome", "success"),
                    "similarity": "high",
                    "insights": [],
                    "analyzed": False
                })
                pair_id += 1
        
        # Also try partial matching (same type, different time)
        for sig, tasks in success_contexts.items():
            if sig != fail_sig:
                sig_parts = sig.split("|")
                fail_parts = fail_sig.split("|")
                # Same type?
                if sig_parts[0] == fail_parts[0] and sig_parts[0] != "?":
                    # Check time bucket
                    if sig_parts[1] != fail_parts[1]:
                        for success in tasks[:1]:
                            pairs.append({
                                "pair_id": pair_id,
                                "failure_id": failure["id"],
                                "success_task_id": success.get("task_id", "unknown"),
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "context_signature": f"{sig_parts[0]}|DIFF_TIME",
                                "failure_context": fail_ctx,
                                "success_context": extract_task_context(success),
                                "failure_description": failure["description"],
                                "success_outcome": success.get("outcome", "success"),
                                "similarity": "medium",
                                "insights": [],
                                "analyzed": False
                            })
                            pair_id += 1
    
    return pairs

def analyze_pair(pair: dict) -> dict:
    """Analyze a contrastive pair to extract insights."""
    insights = []
    
    fctx = pair.get("failure_context", {})
    sctx = pair.get("success_context", {})
    
    # Time-of-day difference
    if fctx.get("time_bucket") != sctx.get("time_bucket"):
        insights.append({
            "type": "time_pattern",
            "observation": f"Failure occurred in {fctx.get('time_bucket')}, similar task succeeded in {sctx.get('time_bucket')}",
            "hypothesis": "Time-of-day affects task outcome"
        })
    
    # Context presence
    if fctx.get("has_context") != sctx.get("has_context"):
        has_c = "with" if fctx.get("has_context") else "without"
        had_c = "with" if sctx.get("has_context") else "without"
        insights.append({
            "type": "context_dependency",
            "observation": f"Failure happened {has_c} context, success happened {had_c}",
            "hypothesis": "Context availability affects outcome"
        })
    
    # Attempt number
    if fctx.get("attempt", 1) != sctx.get("attempt", 1):
        insights.append({
            "type": "retry_benefit",
            "observation": f"Failure on attempt {fctx.get('attempt')}, success on attempt {sctx.get('attempt')}",
            "hypothesis": "Retries improve success rate"
        })
    
    # Tags
    if fctx.get("tags") != sctx.get("tags"):
        diff = set(fctx.get("tags", [])) ^ set(sctx.get("tags", []))
        if diff:
            insights.append({
                "type": "tag_influence",
                "observation": f"Different tags: {diff}",
                "hypothesis": "Tags correlate with outcome"
            })
    
    pair["insights"] = insights
    pair["analyzed"] = True
    return pair

def mine_pairs():
    """Find and analyze all contrastive pairs."""
    print("🔍 Mining contrastive pairs...")
    
    pairs = find_contrast_pairs()
    print(f"   {len(pairs)} rohe Paare gefunden")
    
    # Load existing
    data = load_pairs()
    existing_ids = {p["pair_id"] for p in data["pairs"]}
    
    # Add new pairs
    new_pairs = [p for p in pairs if p["pair_id"] not in existing_ids]
    data["pairs"].extend(new_pairs)
    
    # Analyze new pairs
    analyzed = 0
    for pair in new_pairs:
        if pair["similarity"] == "high":
            pair = analyze_pair(pair)
            analyzed += 1
    
    save_pairs(data)
    
    # Update stats
    stats = load_stats()
    stats["total_pairs"] = len(data["pairs"])
    stats["analyzed_pairs"] = len([p for p in data["pairs"] if p.get("analyzed")])
    stats["insights_found"] = len([i for p in data["pairs"] for i in p.get("insights", [])])
    stats["by_type"] = defaultdict(int)
    for p in data["pairs"]:
        stats["by_type"][p.get("similarity", "unknown")] += 1
    stats["last_analysis"] = datetime.now(timezone.utc).isoformat()
    save_stats(stats)
    
    print(f"✅ {len(new_pairs)} neue Paare hinzugefügt, {analyzed} analysiert")
    print(f"   Gesamt: {stats['total_pairs']} Paare, {stats['insights_found']} Insights")

def show_pairs(limit: int = 20):
    """Show recent contrastive pairs."""
    data = load_pairs()
    pairs = sorted(data["pairs"], key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    if not pairs:
        print("📭 Keine Contrastive Pairs gefunden. Starte --mine zuerst.")
        return
    
    print(f"\n🔍 Contrastive Pairs ({len(pairs)} von {len(data['pairs'])} angezeigt)\n")
    for p in pairs:
        status = "✅" if p.get("analyzed") else "⏳"
        print(f"  {status} [#{p['pair_id']:3}] {p.get('similarity', '?'):6} — Failure #{p.get('failure_id')}")
        print(f"        Context: {p.get('context_signature', 'N/A')}")
        print(f"        Failure: {p.get('failure_description', 'N/A')[:50]}")
        if p.get("insights"):
            for i in p["insights"][:2]:
                print(f"        💡 {i.get('type')}: {i.get('hypothesis', 'N/A')[:50]}")
        print()

def show_stats():
    """Show contrastive analysis statistics."""
    stats = load_stats()
    
    print("\n📊 Contrastive Analysis Stats")
    print("=" * 40)
    print(f"  Total Pairs:      {stats['total_pairs']}")
    print(f"  Analyzed:         {stats['analyzed_pairs']}")
    print(f"  Insights Found:   {stats['insights_found']}")
    print(f"  By Similarity:")
    for t, c in stats.get("by_type", {}).items():
        print(f"    {t:10} {c}")
    print(f"  Last Analysis:    {stats.get('last_analysis', 'Never')}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Contrastive Analyzer")
    parser.add_argument("--analyze", action="store_true", help="Find and analyze pairs")
    parser.add_argument("--mine", action="store_true", help="Mine new pairs")
    parser.add_argument("--pairs", action="store_true", help="Show contrastive pairs")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--limit", type=int, default=20, help="Limit for --pairs")
    
    args = parser.parse_args()
    
    if args.mine or args.analyze:
        mine_pairs()
    elif args.pairs:
        show_pairs(args.limit)
    elif args.stats:
        show_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

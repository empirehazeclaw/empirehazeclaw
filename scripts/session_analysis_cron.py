#!/usr/bin/env python3
"""
session_analysis_cron.py — Automated Session Analysis
Sir HazeClaw - 2026-04-11

Läuft täglich via Cron und trackt Error Rate Trends.

Usage:
    python3 session_analysis_cron.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SESSION_DIR = Path("/home/clawbot/.openclaw/agents/ceo/sessions")
METRICS_FILE = WORKSPACE / "memory" / "session_metrics_history.json"

ERROR_PATTERNS = ["status: error", "failed", "crash"]
FRICTION_PATTERNS = ["retry", "loop", "stuck", "again"]

def load_history():
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {"history": []}

def save_history(data):
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def analyze():
    """Analysiert Sessions der letzten 24h."""
    cutoff = datetime.now() - timedelta(days=1)
    
    sessions = 0
    errors = 0
    friction = 0
    
    for f in SESSION_DIR.glob("*.jsonl"):
        if ".checkpoint." in f.name:
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime > cutoff:
            sessions += 1
            try:
                content = open(f).read().lower()
                for p in ERROR_PATTERNS:
                    if p in content:
                        errors += 1
                        break
                for p in FRICTION_PATTERNS:
                    if p in content:
                        friction += 1
            except:
                pass
    
    error_rate = (errors / sessions * 100) if sessions > 0 else 0
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sessions": sessions,
        "errors": errors,
        "friction": friction,
        "error_rate": round(error_rate, 1)
    }

def main():
    print("📊 SESSION ANALYSIS CRON")
    print("=" * 50)
    
    history = load_history()
    metrics = analyze()
    
    history["history"].append(metrics)
    # Keep only last 30 days
    history["history"] = history["history"][-30:]
    
    save_history(history)
    
    print(f"\n📅 Date: {metrics['date']}")
    print(f"📊 Sessions: {metrics['sessions']}")
    print(f"🚨 Errors: {metrics['errors']}")
    print(f"🔄 Friction: {metrics['friction']}")
    print(f"📈 Error Rate: {metrics['error_rate']}%")
    
    # Trend analysis
    if len(history["history"]) >= 2:
        prev = history["history"][-2]["error_rate"]
        curr = metrics["error_rate"]
        diff = curr - prev
        
        if diff < 0:
            print(f"\n📉 Trend: {abs(diff):.1f}% better!")
        elif diff > 0:
            print(f"\n📈 Trend: {diff:.1f}% worse!")
        else:
            print(f"\n➖ Trend: No change")
    
    # Alert if error rate > 30%
    if metrics["error_rate"] > 30:
        print(f"\n⚠️ ALERT: Error Rate {metrics['error_rate']}% > 30%!")
        print("   → Consider running error_reducer.py")

if __name__ == "__main__":
    main()

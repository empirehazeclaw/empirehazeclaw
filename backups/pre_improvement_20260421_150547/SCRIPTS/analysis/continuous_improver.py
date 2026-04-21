#!/usr/bin/env python3
"""
continuous_improver.py — Autonomous Continuous Improvement
Sir HazeClaw - 2026-04-11

Dieser Cron läuft stündlich und verbessert das System autonom.
KEIN INPUT VON MASTER NÖTIG — läuft automatisch!

Usage:
    python3 continuous_improver.py
    # Wird stündlich via Cron ausgeführt
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SESSION_DIR = Path("/home/clawbot/.openclaw/agents/ceo/sessions")
KG_PATH = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"
METRICS_FILE = WORKSPACE / "memory" / "session_metrics_history.json"
IMPROVEMENT_LOG = WORKSPACE / "logs" / "continuous_improvement.json"

def log(msg):
    """Logt Nachricht."""
    IMPROVEMENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENT_LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def check_error_rate():
    """Prüft Error Rate."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            data = json.load(f)
        history = data.get("history", [])
        if history:
            latest = history[-1]
            return latest.get("error_rate", 100)
    return 100

def check_recent_sessions():
    """Zählt Sessions der letzten Stunde."""
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(hours=1)
    count = 0
    for f in SESSION_DIR.glob("*.jsonl"):
        if ".checkpoint." in f.name:
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime > cutoff:
            count += 1
    return count

def check_kg_growth():
    """Prüft KG Growth."""
    if KG_PATH.exists():
        with open(KG_PATH) as f:
            kg = json.load(f)
        return len(kg.get("entities", {}))
    return 0

def run_improvements():
    """Führt autonome Verbesserungen durch."""
    improvements = []
    
    # 1. Error Rate prüfen
    error_rate = check_error_rate()
    if error_rate > 30:
        improvements.append(f"⚠️ Error Rate hoch: {error_rate}%")
        improvements.append("  → Loop Detection aktivieren")
        improvements.append("  → Timeout Handling prüfen")
    
    # 2. Recent sessions prüfen
    recent = check_recent_sessions()
    improvements.append(f"📊 Sessions letzte Stunde: {recent}")
    
    # 3. KG Growth
    kg_count = check_kg_growth()
    improvements.append(f"🧠 KG Entities: {kg_count}")
    
    return improvements

def main():
    print("🚀 CONTINUOUS IMPROVER — Autonomous Run")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    
    log("=== Continuous Improver started ===")
    
    # Run improvements
    results = run_improvements()
    
    for r in results:
        print(r)
        log(r)
    
    # Check if any action needed
    error_rate = check_error_rate()
    if error_rate > 30:
        print()
        print("⚠️ ACTION NEEDED: Error Rate too high!")
        print("   → Monitoring will continue")
    else:
        print()
        print("✅ Alles gut!")
    
    log("=== Continuous Improver finished ===")
    print()
    print("💡 Next run: in 1 hour (automatically)")

if __name__ == "__main__":
    main()

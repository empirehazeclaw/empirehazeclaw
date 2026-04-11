#!/usr/bin/env python3
"""
session_analyzer.py — Sir HazeClaw Session Analysis
Analysiert Session Logs für Patterns.

Usage:
    python3 session_analyzer.py              # Analysiert letzte 24h
    python3 session_analyzer.py --days 7     # Letzte 7 Tage
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SESSION_DIR = Path("/home/clawbot/.openclaw/agents/ceo/sessions")

# Success/Error patterns
SUCCESS_PATTERNS = ["success", "completed", "✅", "done", "finished", "status: ok"]
ERROR_PATTERNS = ["error", "failed", "❌", "crash", "timeout", "exception", "traceback", "status: error"]
FRICTION_PATTERNS = ["retry", "again", "repeated", "loop", "stuck", "multiple attempts"]

def analyze_file(filepath):
    """Analysiert eine Session-Datei."""
    try:
        size = os.path.getsize(filepath)
        content = open(filepath).read().lower()
        
        # Count patterns
        success_count = sum(1 for p in SUCCESS_PATTERNS if p in content)
        error_count = sum(1 for p in ERROR_PATTERNS if p in content)
        friction_count = sum(1 for p in FRICTION_PATTERNS if p in content)
        
        # Determine status
        if error_count > success_count:
            status = "error"
        elif success_count > error_count:
            status = "success"
        else:
            status = "neutral"
        
        return {
            "file": filepath.name,
            "size_kb": size // 1024,
            "status": status,
            "success_count": success_count,
            "error_count": error_count,
            "friction_count": friction_count
        }
    except Exception as e:
        return {"file": filepath.name, "error": str(e)}

def main():
    days = 1  # Default
    
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            days = int(sys.argv[idx + 1])
    
    cutoff = datetime.now() - timedelta(days=days)
    
    # Find sessions
    sessions = []
    for f in SESSION_DIR.glob("*.jsonl"):
        if ".checkpoint." in f.name:
            continue  # Skip checkpoints
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime > cutoff:
            sessions.append(f)
    
    # Analyze
    results = []
    stats = {"total": len(sessions), "success": 0, "error": 0, "neutral": 0, "total_friction": 0}
    
    for session in sessions:
        r = analyze_file(session)
        results.append(r)
        if "error" not in r:
            status = r["status"]
            if status == "success":
                stats["success"] += 1
            elif status == "error":
                stats["error"] += 1
            else:
                stats["neutral"] += 1
            stats["total_friction"] += r["friction_count"]
    
    # Output
    print(f"\n📊 Session Analyse — Letzte {days} Tag(e)")
    print("=" * 50)
    print(f"Total Sessions: {stats['total']}")
    print(f"✅ Success: {stats['success']}")
    print(f"❌ Errors: {stats['error']}")
    print(f"⚪ Neutral: {stats['neutral']}")
    print(f"🔄 Friction Events: {stats['total_friction']}")
    
    # Insights
    insights = []
    if stats['total'] > 0:
        error_rate = stats['error'] / stats['total'] * 100
        if error_rate > 30:
            insights.append(f"⚠️ Hohe Fehlerquote: {error_rate:.0f}%")
        if stats['total_friction'] > stats['total']:
            insights.append("🔄 Hohe Reibung erkannt")
    
    if insights:
        print("\n💡 Insights:")
        for i in insights:
            print(f"  {i}")
    
    # Save
    output = WORKSPACE / "memory" / f"session_analysis_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output, "w") as f:
        json.dump({"stats": stats, "sessions": len(results), "date": datetime.now().isoformat()}, f, indent=2)
    
    print(f"\n💾 Gespeichert: {output}")

if __name__ == "__main__":
    main()

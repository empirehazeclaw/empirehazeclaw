#!/usr/bin/env python3
"""
session_analyzer.py — Sir HazeClaw Session Analysis
Analysiert Session Logs für Patterns.

Usage:
    python3 session_analyzer.py              # Analysiert letzte 24h
    python3 session_analyzer.py --days 7     # Letzte 7 Tage
    python3 session_analyzer.py --session <id>
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SESSION_DIR = Path("/home/clawbot/.openclaw/sessions")

# Success/Error patterns
SUCCESS_PATTERNS = [
    "success", "completed", "✅", "done", "finished",
    "error: none", "status: ok", "status: success"
]

ERROR_PATTERNS = [
    "error", "failed", "❌", "crash", "timeout",
    "exception", "traceback", "status: error"
]

FRICTION_PATTERNS = [
    "retry", "again", "repeated", "loop", "stuck",
    "multiple attempts", "second time"
]

def parse_session_file(session_file):
    """Parst eine Session-Datei."""
    try:
        with open(session_file) as f:
            content = f.read()
        
        # Extract messages
        messages = []
        lines = content.split("\n")
        
        for line in lines:
            if '"role":"user"' in line or '"role":"assistant"' in line:
                try:
                    msg = json.loads(line)
                    if "content" in msg:
                        messages.append({
                            "role": msg.get("role"),
                            "content": str(msg["content"])[:200]
                        })
                except:
                    pass
        
        return {
            "file": str(session_file),
            "messages": messages,
            "size": os.path.getsize(session_file)
        }
    except Exception as e:
        return {"file": str(session_file), "error": str(e), "messages": []}

def analyze_content(content: str) -> dict:
    """Analysiert Content auf Patterns."""
    content_lower = content.lower()
    
    # Count success/error indicators
    success_count = sum(1 for p in SUCCESS_PATTERNS if p in content_lower)
    error_count = sum(1 for p in ERROR_PATTERNS if p in content_lower)
    friction_count = sum(1 for p in FRICTION_PATTERNS if p in content_lower)
    
    # Determine status
    if error_count > success_count:
        status = "error"
    elif success_count > error_count:
        status = "success"
    else:
        status = "neutral"
    
    return {
        "success_count": success_count,
        "error_count": error_count,
        "friction_count": friction_count,
        "status": status
    }

def generate_insights(sessions: list) -> dict:
    """Generiert Insights aus Sessions."""
    stats = {
        "total_sessions": len(sessions),
        "successful": 0,
        "errors": 0,
        "neutral": 0,
        "total_friction": 0,
        "categories": defaultdict(int)
    }
    
    all_insights = []
    
    for session in sessions:
        if "error" in session:
            continue
            
        analysis = analyze_content(session.get("file", ""))
        stats[analysis["status"] + "s"] += 1
        stats["total_friction"] += analysis["friction_count"]
        
        # Category detection
        content = session.get("file", "").lower()
        if "debug" in content or "error" in content:
            stats["categories"]["debugging"] += 1
        if "research" in content or "search" in content:
            stats["categories"]["research"] += 1
        if "coding" in content or "script" in content:
            stats["categories"]["coding"] += 1
    
    # Generate recommendations
    insights = []
    
    if stats["errors"] > stats["successful"] * 0.5:
        insights.append({
            "type": "warning",
            "text": f"Hohe Fehlerquote: {stats['errors']} Fehler bei {stats['total_sessions']} Sessions"
        })
    
    if stats["total_friction"] > stats["total_sessions"]:
        insights.append({
            "type": "friction",
            "text": "Hohe Reibung erkannt - viele Retry/Loop Patterns"
        })
    
    if stats["categories"]:
        top_cat = max(stats["categories"], key=stats["categories"].get)
        insights.append({
            "type": "info",
            "text": f"Meistgenutzte Kategorie: {top_cat} ({stats['categories'][top_cat]} Sessions)"
        })
    
    return {"stats": stats, "insights": insights}

def main():
    days = 1  # Default: letzte 24h
    
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            days = int(sys.argv[idx + 1])
    
    # Find recent sessions
    sessions = []
    cutoff = datetime.now() - timedelta(days=days)
    
    if SESSION_DIR.exists():
        for session_file in SESSION_DIR.glob("*.jsonl"):
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
            if mtime > cutoff:
                parsed = parse_session_file(session_file)
                if parsed.get("messages"):
                    sessions.append(parsed)
    
    # Analyze
    results = generate_insights(sessions)
    
    # Output
    print(f"\n📊 Session Analyse — Letzte {days} Tag(e)")
    print("=" * 50)
    print(f"Total Sessions: {results['stats']['total_sessions']}")
    print(f"✅ Success: {results['stats']['successful']}")
    print(f"❌ Errors: {results['stats']['errors']}")
    print(f"⚪ Neutral: {results['stats']['neutral']}")
    print(f"🔄 Friction Events: {results['stats']['total_friction']}")
    
    if results['stats']['categories']:
        print("\n📂 Kategorien:")
        for cat, count in results['stats']['categories'].items():
            print(f"  {cat}: {count}")
    
    print("\n💡 Insights:")
    for insight in results['insights']:
        emoji = {"warning": "⚠️", "friction": "🔄", "info": "ℹ️"}.get(insight['type'], "•")
        print(f"  {emoji} {insight['text']}")
    
    # Save to memory
    output_file = WORKSPACE / "memory" / f"session_analysis_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Gespeichert: {output_file}")

if __name__ == "__main__":
    main()

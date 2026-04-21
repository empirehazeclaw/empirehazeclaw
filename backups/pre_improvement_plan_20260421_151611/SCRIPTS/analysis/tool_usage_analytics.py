#!/usr/bin/env python3
"""
Sir HazeClaw Tool Usage Analytics
Trackt Tool-Nutzung für Observability + Optimierung.

Basierend auf MCP/LangSmith Research.

Usage:
    python3 tool_usage_analytics.py              # Zeigt Dashboard
    python3 tool_usage_analytics.py --track <tool> <duration_ms> <success>
    python3 tool_usage_analytics.py --top        # Top 10 Tools
    python3 tool_usage_analytics.py --errors     # Error Analyse
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
ANALYTICS_FILE = WORKSPACE / "data/tool_usage_analytics.json"

def load_analytics():
    """Load existing analytics data."""
    if ANALYTICS_FILE.exists():
        with open(ANALYTICS_FILE) as f:
            return json.load(f)
    return {
        "tool_usage": [],
        "last_updated": datetime.now().isoformat()
    }

def save_analytics(data):
    """Save analytics data."""
    data["last_updated"] = datetime.now().isoformat()
    with open(ANALYTICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def track_tool(tool_name, duration_ms, success):
    """
    Track a tool execution.
    
    Args:
        tool_name: Name des Tools (z.B. "exec", "read", "memory_search")
        duration_ms: Dauer in Millisekunden
        success: True/False oder "partial"
    """
    data = load_analytics()
    
    data["tool_usage"].append({
        "tool": tool_name,
        "duration_ms": duration_ms,
        "success": success,
        "timestamp": datetime.now().isoformat()
    })
    
    save_analytics(data)
    print(f"✅ Tracked: {tool_name} ({duration_ms}ms, {success})")

def show_dashboard():
    """Zeigt Analytics Dashboard."""
    data = load_analytics()
    usage = data.get("tool_usage", [])
    
    if not usage:
        print("📊 Tool Usage Analytics — No data yet")
        print("Usage: tool_usage_analytics.py --track <tool> <duration_ms> <success>")
        return
    
    # Basic stats
    total_calls = len(usage)
    
    # Duration stats
    durations = [u["duration_ms"] for u in usage]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Success rate
    successes = sum(1 for u in usage if u.get("success") == True)
    success_rate = (successes / total_calls * 100) if total_calls > 0 else 0
    
    # Tool Counter
    tool_counts = Counter(u["tool"] for u in usage)
    top_tools = tool_counts.most_common(10)
    
    print("📊 Tool Usage Analytics")
    print("=" * 50)
    print(f"Total Calls: {total_calls}")
    print(f"Avg Duration: {avg_duration:.1f}ms")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    print("🔝 Top 10 Tools:")
    for tool, count in top_tools:
        print(f"  {tool}: {count} calls")
    
    print()
    print(f"Last updated: {data.get('last_updated', 'never')}")

def show_top(n=10):
    """Zeigt Top n Tools."""
    data = load_analytics()
    usage = data.get("tool_usage", [])
    
    if not usage:
        print("No data")
        return
    
    tool_counts = Counter(u["tool"] for u in usage)
    top_tools = tool_counts.most_common(n)
    
    print(f"🔝 Top {n} Tools:")
    for i, (tool, count) in enumerate(top_tools, 1):
        print(f"  {i}. {tool}: {count} calls")

def show_errors():
    """Zeigt Error Analyse."""
    data = load_analytics()
    usage = data.get("tool_usage", [])
    
    errors = [u for u in usage if u.get("success") != True]
    
    if not errors:
        print("✅ No errors found")
        return
    
    error_counts = Counter(e["tool"] for e in errors)
    
    print(f"❌ Errors ({len(errors)} total):")
    for tool, count in error_counts.most_common():
        print(f"  {tool}: {count} errors")

def integration_example():
    """Zeigt wie man ins Coordinator integriert."""
    example = '''
# Integration in learning_coordinator.py:

import tool_usage_analytics as tua

# Am Start jeder Tool-Nutzung:
start = time.time()
result = execute_tool(tool_name)
duration = (time.time() - start) * 1000
tua.track_tool(tool_name, duration, success=result is not None)

# Oder am Ende eines Cycles:
tua.show_dashboard()
'''
    print(example)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_dashboard()
    elif sys.argv[1] == "--track":
        if len(sys.argv) != 5:
            print("Usage: --track <tool> <duration_ms> <success>")
            sys.exit(1)
        tool_name = sys.argv[2]
        duration_ms = int(sys.argv[3])
        success = sys.argv[4].lower() in ["true", "1", "yes", "success"]
        track_tool(tool_name, duration_ms, success)
    elif sys.argv[1] == "--top":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_top(n)
    elif sys.argv[1] == "--errors":
        show_errors()
    elif sys.argv[1] == "--integration":
        integration_example()
    else:
        print(__doc__)
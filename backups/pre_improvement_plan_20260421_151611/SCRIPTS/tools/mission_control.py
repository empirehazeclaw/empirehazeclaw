#!/usr/bin/env python3
"""
mission_control.py — Sir HazeClaw Mission Control Dashboard
============================================================
Shows all critical metrics in Telegram-friendly format.

Usage:
    python3 mission_control.py              # Show dashboard
    python3 mission_control.py --json       # JSON output
    python3 mission_control.py --cron       # Cron-friendly output

Metrics:
    - Gateway Status
    - Cron Health (active/errors)
    - Error Rate
    - KG Quality
    - Healing Loop Status
    - Recent Activity
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CRON_JOBS = Path("/home/clawbot/.openclaw/cron/jobs.json")
KG_FILE = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
HEALER_LOG = WORKSPACE / "logs/cron_healer.log"
HEALER_STATE = WORKSPACE / "data/healer_state.json"
ERROR_LOG = WORKSPACE / "logs/error_rate.json"

# Colors for Telegram
GREEN = "✅"
YELLOW = "🟡"
RED = "❌"
BLUE = "🔵"
PURPLE = "🟣"

def get_gateway_status():
    """Check Gateway status via openclaw CLI."""
    import subprocess
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True, text=True, timeout=5
        )
        if "running" in result.stdout.lower() or "active" in result.stdout.lower():
            return GREEN + " LIVE", True
        elif "stopped" in result.stdout.lower() or "inactive" in result.stdout.lower():
            return RED + " DOWN", False
        return YELLOW + " UNKNOWN", None
    except:
        return YELLOW + " CHECK FAILED", None

def get_cron_stats():
    """Get cron job statistics."""
    if not CRON_JOBS.exists():
        return None, None, None
    
    with open(CRON_JOBS) as f:
        data = json.load(f)
    
    jobs = data.get("jobs", [])
    total = len(jobs)
    active = sum(1 for j in jobs if j.get("enabled", True))
    errors = sum(1 for j in jobs if j.get("lastRunStatus") == "error")
    
    return total, active, errors

def get_healer_status():
    """Get error healer status."""
    stats = {"runs": 0, "healed": 0, "errors": 0, "circuit_breaks": 0}
    
    if HEALER_STATE.exists():
        with open(HEALER_STATE) as f:
            state = json.load(f)
            stats["circuit_breaks"] = state.get("circuit_breaker", {}).get("restart_count", 0)
    
    # Parse healer log
    if HEALER_LOG.exists():
        with open(HEALER_LOG) as f:
            lines = f.readlines()
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_lines = [l for l in lines if l.startswith(f"[{today}")]
        
        stats["runs"] = len(today_lines)
        stats["healed"] = sum(1 for l in today_lines if "HEALED" in l or "healed" in l)
        stats["errors"] = sum(1 for l in today_lines if "ERROR" in l or "error" in l)
    
    return stats

def get_kg_quality():
    """Get KG quality metrics."""
    if not KG_FILE.exists():
        return None
    
    with open(KG_FILE) as f:
        kg = json.load(f)
    
    entities = kg.get("entities", {})
    relations = kg.get("relations", [])
    
    # Count shares_category
    shares_cat = sum(1 for r in relations if r.get("type") == "shares_category")
    shares_cat_ratio = shares_cat / len(relations) * 100 if relations else 0
    
    # Access count
    access_counts = [e.get("access_count", 0) for e in entities.values()]
    avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
    max_access = max(access_counts) if access_counts else 0
    
    return {
        "entities": len(entities),
        "relations": len(relations),
        "shares_cat_ratio": shares_cat_ratio,
        "avg_access": avg_access,
        "max_access": max_access
    }

def get_error_rate():
    """Get error rate from error_rate_monitor."""
    if ERROR_LOG.exists():
        with open(ERROR_LOG) as f:
            data = json.load(f)
        
        # Get last 24h stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today in data:
            day_data = data[today]
            total = day_data.get("total", 0)
            errors = day_data.get("errors", 0)
            rate = errors / total * 100 if total > 0 else 0
            return round(rate, 1), errors, total
    
    return None, 0, 0

def format_dashboard():
    """Format dashboard for Telegram."""
    lines = []
    lines.append(f"📊 **MISSION CONTROL** — {datetime.now().strftime('%H:%M UTC')}")
    lines.append("=" * 50)
    lines.append("")
    
    # Gateway
    gw_status, gw_ok = get_gateway_status()
    lines.append(f"🚪 **Gateway:** {gw_status}")
    lines.append("")
    
    # Cron Health
    total, active, errors = get_cron_stats()
    if total is not None:
        error_emoji = RED if errors > 0 else GREEN
        lines.append(f"⏰ **Cron Jobs:** {active}/{total} active {error_emoji}{errors} errors")
    lines.append("")
    
    # Error Rate
    rate, err_count, total_count = get_error_rate()
    if rate is not None:
        rate_emoji = GREEN if rate < 5 else YELLOW if rate < 15 else RED
        lines.append(f"📉 **Error Rate:** {rate_emoji}{rate}% ({err_count}/{total_count})")
    else:
        lines.append(f"📉 **Error Rate:** {YELLOW}No data")
    lines.append("")
    
    # KG Quality
    kg = get_kg_quality()
    if kg:
        sc_emoji = GREEN if kg["shares_cat_ratio"] < 50 else YELLOW if kg["shares_cat_ratio"] < 70 else RED
        access_emoji = GREEN if kg["avg_access"] > 0.1 else YELLOW if kg["avg_access"] > 0 else RED
        lines.append(f"🧠 **KG Quality:**")
        lines.append(f"   Entities: {kg['entities']} | Relations: {kg['relations']}")
        lines.append(f"   shares_cat: {sc_emoji}{kg['shares_cat_ratio']:.1f}%")
        lines.append(f"   Avg Access: {access_emoji}{kg['avg_access']:.2f}")
    lines.append("")
    
    # Healer Status
    healer = get_healer_status()
    if healer["runs"] > 0:
        lines.append(f"🏥 **Healer Today:**")
        lines.append(f"   Runs: {healer['runs']} | Healed: {GREEN}{healer['healed']} | Errors: {RED if healer['errors'] > 0 else GREEN}{healer['errors']}")
        if healer["circuit_breaks"] > 0:
            lines.append(f"   Circuit Breaks: {YELLOW}{healer['circuit_breaks']}")
    lines.append("")
    
    lines.append("—" * 50)
    lines.append("🌐 clawhub.ai | 📖 docs/openclaw.ai")
    
    return "\n".join(lines)

def format_json():
    """Format as JSON."""
    total, active, errors = get_cron_stats()
    rate, err_count, total_count = get_error_rate()
    kg = get_kg_quality()
    gw_status, gw_ok = get_gateway_status()
    healer = get_healer_status()
    
    return json.dumps({
        "timestamp": datetime.now().isoformat(),
        "gateway": {"status": gw_status, "ok": gw_ok},
        "cron": {"total": total, "active": active, "errors": errors},
        "error_rate": {"rate": rate, "errors": err_count, "total": total_count},
        "kg": kg,
        "healer": healer
    }, indent=2)

def main():
    if "--json" in sys.argv:
        print(format_json())
    elif "--cron" in sys.argv:
        # Cron-friendly: just show key metrics
        total, active, errors = get_cron_stats()
        rate, _, _ = get_error_rate()
        gw_status, gw_ok = get_gateway_status()
        print(f"GATEWAY={gw_ok} CRON_ERRORS={errors} ERROR_RATE={rate}")
    else:
        print(format_dashboard())

if __name__ == "__main__":
    main()

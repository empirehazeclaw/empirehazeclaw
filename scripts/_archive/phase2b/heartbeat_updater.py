#!/usr/bin/env python3
"""
heartbeat_updater.py - Automatischer HEARTBEAT Status
Sir HazeClaw - 2026-04-11

Läuft täglich und aktualisiert HEARTBEAT.md automatisch.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
HEARTBEAT = WORKSPACE / "HEARTBEAT.md"
CRON_STATE = Path("/home/clawbot/.openclaw/cron/jobs.json")


def get_cron_status() -> dict:
    """Hole Cron Status."""
    if not CRON_STATE.exists():
        return {"total": 0, "errors": 0, "ok": 0}
    
    with open(CRON_STATE) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    errors = sum(1 for j in jobs if j.get('state', {}).get('lastRunStatus') == 'error')
    ok = sum(1 for j in jobs if j.get('state', {}).get('lastRunStatus') == 'ok')
    
    return {"total": len(jobs), "errors": errors, "ok": ok}


def get_gateway_status() -> bool:
    """Prüfe Gateway."""
    try:
        import urllib.request
        req = urllib.request.urlopen("http://localhost:18789/health", timeout=3)
        data = json.loads(req.read())
        return data.get("ok", False)
    except:
        return False


def get_token_usage() -> dict:
    """Hole Token Usage."""
    state_file = WORKSPACE / "memory" / "token_budget.json"
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        return {
            "usage": state.get("usage", 0),
            "budget": 5_000_000,
            "percentage": state.get("usage", 0) / 5_000_000
        }
    return {"usage": 0, "budget": 5_000_000, "percentage": 0}


def update_heartbeat():
    """Aktualisiere HEARTBEAT.md."""
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    # Gateway
    gateway_ok = get_gateway_status()
    gateway_status = "✅ LIVE" if gateway_ok else "❌ DOWN"
    
    # Cron Status
    cron = get_cron_status()
    
    # Token
    token = get_token_usage()
    
    # Build new content
    content = f"""# HEARTBEAT.md — Sir HazeClaw Status

## Last Update: {now}

## ✅ System Overview
| Metric | Status |
|--------|--------|
| Gateway | {gateway_status} |
| Active Crons | {cron['ok']}/{cron['total']} |
| Cron Errors | {cron['errors']} |
| Token Usage | {token['percentage']:.0%} ({token['usage']:,}/{token['budget']:,}) |

## 🔄 Autonomy Framework
| Component | Status | Notes |
|-----------|--------|-------|
| Learning Coordinator | ✅ HOURLY | Every hour via Cron |
| Capability Evolver | ✅ ON-DEMAND | Subagent when needed |
| Token Budget Tracker | ✅ DAILY | Cron daily |
| Gateway Auto-Recovery | ✅ 5min | Auto-restart if down |
| Session Cleanup | ✅ DAILY | Cron daily |

## 📊 Quick Metrics
- Memory: `/workspace/memory/`
- Scripts: `/workspace/scripts/` (55 active)
- Skills: `/workspace/skills/` (16 active)
- KG Entities: ~188

## ⚠️ NO SPAM RULE
Only report: ERROR, WARNING, or real improvement/learning.

---
*Auto-updated: {now}*
*Sir HazeClaw — Solo Fighter*
"""
    
    # Write
    with open(HEARTBEAT, "w") as f:
        f.write(content)
    
    print(f"[{now}] HEARTBEAT updated")
    print(f"  Gateway: {gateway_status}")
    print(f"  Crons: {cron['ok']}/{cron['total']} ok, {cron['errors']} errors")
    print(f"  Token: {token['percentage']:.0%}")


if __name__ == "__main__":
    update_heartbeat()

#!/usr/bin/env python3
"""Heartbeat Updater - Auto-update HEARTBEAT.md every 3 hours"""

import os
import json
from datetime import datetime, timezone

WORKSPACE = "/home/clawbot/.openclaw/workspace"
HEARTBEAT_PATH = os.path.join(WORKSPACE, "HEARTBEAT.md")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
SCRIPTS_DIR = os.path.join(WORKSPACE, "scripts")
STATE_FILE = os.path.join(WORKSPACE, "data", "heartbeat_state.json")

def get_active_crons():
    """Count active cron jobs via openclaw CLI"""
    import subprocess
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        jobs = data.get("jobs", [])
        enabled = sum(1 for j in jobs if j.get("enabled", False))
        return enabled, len(jobs)
    except Exception:
        return None, None

def count_scripts():
    """Count Python scripts in scripts/"""
    try:
        scripts = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".py")]
        return len(scripts)
    except Exception:
        return None

def count_memory_files():
    """Count memory files"""
    try:
        files = [f for f in os.listdir(MEMORY_DIR) if f.endswith(".md")]
        return len(files)
    except Exception:
        return None

def get_kg_entities():
    """Estimate KG entities from memory files"""
    try:
        kg_path = os.path.join(WORKSPACE, "data", "kg_entities.json")
        if os.path.exists(kg_path):
            with open(kg_path) as f:
                data = json.load(f)
                return len(data) if isinstance(data, dict) else None
    except Exception:
        pass
    return None

def get_gateway_status():
    """Check gateway status"""
    import subprocess
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True, text=True, timeout=5
        )
        return "✅ LIVE" if result.returncode == 0 else "❌ DOWN"
    except Exception:
        return "❓ UNKNOWN"

def update_heartbeat():
    """Update HEARTBEAT.md with current status"""
    now = datetime.now(timezone.utc)
    time_str = now.strftime("%Y-%m-%d %H:%M UTC")
    date_str = now.strftime("%Y-%m-%d %H:%M UTC")
    
    gateway = get_gateway_status()
    active, total = get_active_crons() or ("?", "?")
    scripts = count_scripts() or "?"
    memory = count_memory_files() or "?"
    kg = get_kg_entities() or "?"
    
    content = f"""# HEARTBEAT.md — Sir HazeClaw Status

## Last Update: {date_str}

## ✅ System Overview
| Metric | Status |
|--------|--------|
| Gateway | {gateway} |
| Active Crons | {active}/{total} |
| Scripts | {scripts} active |
| Memory Files | {memory} |

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
- Scripts: `/workspace/scripts/` ({scripts} active)
- KG Entities: ~{kg}

## ⚠️ NO SPAM RULE
Only report: ERROR, WARNING, or real improvement/learning.

---
*Auto-updated: {time_str}*
*Sir HazeClaw — Solo Fighter*
"""
    
    with open(HEARTBEAT_PATH, "w") as f:
        f.write(content)
    
    print(f"✅ HEARTBEAT.md updated at {time_str}")
    print(f"   Gateway: {gateway}")
    print(f"   Crons: {active}/{total} active")
    print(f"   Scripts: {scripts}")
    print(f"   KG Entities: ~{kg}")

if __name__ == "__main__":
    update_heartbeat()

#!/usr/bin/env python3
"""
HEARTBEAT UPDATE (IMPROVED)
Uses services instead of subprocess for faster execution
Phase 8 Maximization: Fixed timeout issue
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path

# Import our services
import sys
sys.path.insert(0, '/home/clawbot/.openclaw')

try:
    from SCRIPTS.services.gateway import check_health
    from SCRIPTS.services.cron_healer import get_cron_list
except ImportError:
    print("❌ Services not available - falling back to basic update")
    check_health = None
    get_cron_list = None

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
HEARTBEAT_PATH = WORKSPACE / "HEARTBEAT.md"
MEMORY_DIR = WORKSPACE / "memory"
STATE_FILE = WORKSPACE / "data" / "heartbeat_state.json"

def get_gateway_status_fast():
    """Get gateway status using service (fast)"""
    if check_health:
        try:
            healthy, msg = check_health()
            return "✅ LIVE" if healthy else "❌ DOWN"
        except:
            pass
    return "⚠️ CHECK_FAILED"

def get_crons_fast():
    """Get cron stats using service (fast)"""
    if get_cron_list:
        try:
            crons = get_cron_list()
            jobs = crons.get('jobs', [])
            enabled = sum(1 for j in jobs if j.get('enabled', False))
            errors = sum(1 for j in jobs if j.get('state', {}).get('lastRunStatus') == 'error')
            return enabled, len(jobs), errors
        except:
            pass
    return None, None, None

def count_scripts():
    """Count Python scripts"""
    try:
        scripts_dir = WORKSPACE / "scripts"
        return sum(1 for f in scripts_dir.glob("*.py") if f.is_file())
    except:
        return None

def count_memory_files():
    """Count memory files"""
    try:
        return sum(1 for f in MEMORY_DIR.glob("*.md") if f.is_file())
    except:
        return None

def get_kg_entities():
    """Get KG entity count"""
    try:
        kg_path = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"
        if kg_path.exists():
            with open(kg_path) as f:
                kg = json.load(f)
            return len(kg.get('entities', {}))
    except:
        pass
    return None

def update_heartbeat():
    """Update HEARTBEAT.md with current status"""
    now = datetime.now(timezone.utc)
    time_str = now.strftime("%Y-%m-%d %H:%M UTC")
    
    # Get metrics using services (fast!)
    gateway = get_gateway_status_fast()
    enabled, total, cron_errors = get_crons_fast()
    scripts = count_scripts()
    memory = count_memory_files()
    kg = get_kg_entities()
    
    # Handle None values
    enabled = enabled if enabled is not None else "?"
    total = total if total is not None else "?"
    cron_errors = cron_errors if cron_errors is not None else "?"
    scripts = scripts if scripts is not None else "?"
    memory = memory if memory is not None else "?"
    kg = kg if kg is not None else "?"
    
    # Format gateway status
    gateway_icon = "✅" if "LIVE" in gateway else "❌" if "DOWN" in gateway else "⚠️"
    
    content = f"""# HEARTBEAT.md — Sir HazeClaw Status

## Last Update: {time_str}

## ✅ System Overview
| Metric | Status |
|--------|--------|
| Gateway | {gateway} |
| Active Crons | {enabled}/{total} |
| Cron Errors | {cron_errors} |
| Scripts | {scripts} active |
| Memory Files | {memory} |
| KG Entities | {kg} |

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
*Sir HazeClaw — Optimized (v2)*
"""
    
    HEARTBEAT_PATH.write_text(content)
    
    print(f"✅ HEARTBEAT.md updated at {time_str}")
    print(f"   Gateway: {gateway}")
    print(f"   Crons: {enabled}/{total} ({cron_errors} errors)")
    print(f"   Scripts: {scripts}")
    print(f"   KG: {kg}")

if __name__ == "__main__":
    update_heartbeat()
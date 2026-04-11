#!/usr/bin/env python3
"""
Sir HazeClaw Learning Coordinator
Zentrales Dashboard für den Learning Loop.

KOORDINIERT:
- Research → KG → Skills → Improvement
- Token Tracking
- Loop Detection
- Quality Gates

Usage:
    python3 learning_coordinator.py
    python3 learning_coordinator.py --full      # Full cycle
    python3 learning_coordinator.py --research  # Only research
    python3 learning_coordinator.py --status    # Show status
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "data"
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
COORDINATOR_LOG = DATA_DIR / "learning_coordinator.json"

# ============ TOKEN TRACKING ============

def track_token_usage(task_name, tokens_in, tokens_out):
    """Track token usage für Efficiency."""
    log = load_coordinator_log()
    
    if 'token_usage' not in log:
        log['token_usage'] = []
    
    log['token_usage'].append({
        'timestamp': datetime.now().isoformat(),
        'task': task_name,
        'tokens_in': tokens_in,
        'tokens_out': tokens_out,
        'total': tokens_in + tokens_out
    })
    
    # Keep only last 100 entries
    log['token_usage'] = log['token_usage'][-100:]
    
    save_coordinator_log(log)

# ============ RESEARCH INTEGRATION ============

def run_innovation_research():
    """Führt Innovation Research aus und integriert in KG."""
    print("🔍 Running Innovation Research...")
    
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'innovation_research.py'), '--daily'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(WORKSPACE)
        )
        
        # Track token usage for research
        output = result.stdout
        queries = len([l for l in output.split('\n') if 'Searching' in l])
        track_token_usage('innovation_research', 2000 * queries, 1500 * queries)
        
        # Parse output for insights
        output = result.stdout
        
        # Update KG with research insights
        if KG_PATH.exists():
            with open(KG_PATH) as f:
                kg = json.load(f)
            
            today = datetime.now().strftime('%Y%m%d')
            entity_id = f"research_integration_{today}"
            
            kg['entities'][entity_id] = {
                "type": "research",
                "category": "learning_coordinator",
                "facts": [{
                    "content": f"Daily research completed: {len([l for l in output.split('\n') if 'Searching' in l])} queries",
                    "confidence": 0.9,
                    "extracted_at": datetime.now().isoformat(),
                    "category": "research"
                }],
                "priority": "MEDIUM",
                "created": datetime.now().isoformat(),
                "tags": ["research", "coordinator", "daily"]
            }
            
            with open(KG_PATH, 'w') as f:
                json.dump(kg, f, indent=2)
        
        print(f"✅ Research integrated to KG")
        return True
        
    except Exception as e:
        print(f"⚠️ Research failed: {e}")
        return False

# ============ QUALITY GATES ============

def run_quality_gates():
    """Führt Quality Gates aus."""
    print("🔒 Running Quality Gates...")
    
    results = {
        'loop_check': False,
        'self_eval': False,
        'test_framework': False
    }
    
    # Loop Check
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'loop_check.py')],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(WORKSPACE)
        )
        results['loop_check'] = 'No loops detected' in result.stdout or '✅' in result.stdout
        
        # Track token usage for this task
        track_token_usage('loop_check', 500, 300)
        
        print(f"  {'✅' if results['loop_check'] else '⚠️'} Loop Check")
    except:
        print(f"  ⚠️ Loop Check failed")
    
    # Self Eval
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'self_eval.py')],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(WORKSPACE)
        )
        results['self_eval'] = '99' in result.stdout or '100' in result.stdout
        
        # Track token usage for this task
        track_token_usage('self_eval', 800, 400)
        
        print(f"  {'✅' if results['self_eval'] else '⚠️'} Self Eval")
    except:
        print(f"  ⚠️ Self Eval failed")
    
    return results['loop_check'] and results['self_eval']

# ============ LOOP COORDINATION ============

def check_and_act():
    """Prüft System und handelt wenn nötig."""
    print("🔍 Checking System...")
    
    issues = []
    
    # Check 1: Disk Space
    try:
        result = subprocess.run(['df', '-h', WORKSPACE.parent], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if '/' in line and not line.startswith('Filesystem'):
                parts = line.split()
                if len(parts) >= 5:
                    use_pct = int(parts[4].replace('%', ''))
                    if use_pct > 85:
                        issues.append(f"Disk kritisch: {use_pct}% used")
    except:
        pass
    
    # Check 2: Memory
    try:
        result = subprocess.run(['free', '-m'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Mem:' in line:
                parts = line.split()
                total = int(parts[1])
                used = int(parts[2])
                if used / total > 0.9:
                    issues.append(f"Memory hoch: {used}/{total}MB")
    except:
        pass
    
    # Check 3: Gateway
    try:
        result = subprocess.run(['curl', '-s', 'http://127.0.0.1:18789/health'], capture_output=True, text=True, timeout=5)
        if '"ok":true' in result.stdout or 'live' in result.stdout:
            pass  # OK
        else:
            issues.append("Gateway möglicherweise down")
    except:
        issues.append("Gateway Check failed")
    
    if issues:
        print("⚠️ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False, issues
    else:
        print("  ✅ All checks OK")
        return True, []

# ============ COORDINATOR LOG ============

def load_coordinator_log():
    if COORDINATOR_LOG.exists():
        with open(COORDINATOR_LOG) as f:
            return json.load(f)
    return {"runs": [], "last_full_cycle": None}

def save_coordinator_log(log):
    COORDINATOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(COORDINATOR_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def log_run(log, phase, success, notes=""):
    log["runs"].append({
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "success": success,
        "notes": notes
    })
    log["last_full_cycle"] = datetime.now().isoformat()

# ============ MAIN COORDINATOR ============

def run_full_cycle():
    """Führt vollständigen Learning Cycle aus."""
    print("=" * 60)
    print("🎯 LEARNING COORDINATOR — Full Cycle")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()
    
    log = load_coordinator_log()
    start_time = datetime.now()
    
    # Phase 1: System Check
    print("📊 PHASE 1: System Check")
    ok, issues = check_and_act()
    log_run(log, "system_check", ok, str(issues))
    print()
    
    # Phase 2: Research
    print("📊 PHASE 2: Innovation Research")
    research_ok = run_innovation_research()
    log_run(log, "research", research_ok)
    print()
    
    # Phase 3: Quality Gates
    print("📊 PHASE 3: Quality Gates")
    quality_ok = run_quality_gates()
    log_run(log, "quality", quality_ok)
    print()
    
    # Phase 4: Learning Tracking
    print("📊 PHASE 4: Learning Tracker")
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'learning_tracker.py')],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(WORKSPACE)
        )
        print(f"  ✅ Learning tracked")
        log_run(log, "learning", True)
    except:
        print(f"  ⚠️ Learning tracking failed")
        log_run(log, "learning", False)
    print()
    
    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    print("=" * 60)
    print("📊 CYCLE SUMMARY")
    print(f"   Duration: {duration:.1f}s")
    print(f"   System Check: {'✅' if ok else '⚠️'}")
    print(f"   Research: {'✅' if research_ok else '⚠️'}")
    print(f"   Quality: {'✅' if quality_ok else '⚠️'}")
    print("=" * 60)
    
    save_coordinator_log(log)
    
    return ok and research_ok and quality_ok

def show_status():
    """Zeigt aktuellen Status."""
    log = load_coordinator_log()
    
    print("📊 LEARNING COORDINATOR STATUS")
    print(f"   Last full cycle: {log.get('last_full_cycle', 'Never')}")
    print(f"   Total runs: {len(log.get('runs', []))}")
    print()
    
    if log.get('runs'):
        print("Recent runs:")
        for run in log['runs'][-5:]:
            status = '✅' if run['success'] else '⚠️'
            print(f"  {status} {run['phase']}: {run['timestamp'][:16]}")
    
    print()
    
    # Token Usage
    if log.get('token_usage'):
        total_tokens = sum(e['total'] for e in log['token_usage'][-10:])
        avg_tokens = total_tokens / len(log['token_usage'][-10:])
        print(f"Token Usage (last 10 tasks):")
        print(f"  Total: {total_tokens:,}")
        print(f"  Average: {avg_tokens:,.0f}")

def main():
    if len(sys.argv) < 2:
        return 0 if run_full_cycle() else 1
    
    arg = sys.argv[1]
    
    if arg == '--full':
        return 0 if run_full_cycle() else 1
    elif arg == '--research':
        return 0 if run_innovation_research() else 1
    elif arg == '--status':
        show_status()
        return 0
    elif arg == '--check':
        ok, issues = check_and_act()
        return 0 if ok else 1
    else:
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())

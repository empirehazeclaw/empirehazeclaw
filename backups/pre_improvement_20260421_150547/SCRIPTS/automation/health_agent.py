#!/usr/bin/env python3
"""
Health Agent — Sir HazeClaw Multi-Agent Architecture
===================================================
Dedicated health monitoring and self-healing agent.

Role: Technician — System health, error detection, auto-healing
Trigger: Cron (alle 5 min) + Event-basiert

Usage:
    python3 health_agent.py --check        # Full health check
    python3 health_agent.py --quick       # Quick check
    python3 health_agent.py --daemon      # Run as daemon
    python3 health_agent.py --test        # Test mode (no alerts)

Phase 1 of Multi-Agent Architecture
"""

import os
import sys
import json
import signal
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "SCRIPTS" / "automation"
DATA_DIR = WORKSPACE / "data"
EVENTS_DIR = DATA_DIR / "events"
LOGS_DIR = WORKSPACE / "logs"
HEALTH_STATE_FILE = DATA_DIR / "health_agent_state.json"

# Config
CHECK_INTERVAL = 300  # 5 minutes
CRITICAL_COOLDOWN = 300  # 5 min between critical alerts to same recipient
STALE_THRESHOLD = 300  # 5 minutes = stale

# Layer definitions (from enhanced_self_healing.py)
LAYERS = {
    'process': {'name': 'Process', 'check': 'check_process'},
    'memory': {'name': 'Memory', 'check': 'check_memory'},
    'disk': {'name': 'Disk', 'check': 'check_disk'},
    'network': {'name': 'Network', 'check': 'check_network'},
    'gateway': {'name': 'Gateway', 'check': 'check_gateway'},
    'cron': {'name': 'Cron', 'check': 'check_cron'},
}

# Self-healing actions per layer
HEAL_ACTIONS = {
    'process': ['restart_service'],
    'memory': ['clear_cache', 'trigger_gc'],
    'disk': ['cleanup_temp', 'rotate_logs'],
    'network': ['check_dns', 'retry_connection'],
    'gateway': ['restart_gateway'],
    'cron': ['restart_cron', 'notify_error'],
}

def log(msg: str, level: str = "INFO"):
    """Simple logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "health_agent.log"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": msg
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def load_state() -> Dict:
    """Load health agent state."""
    if HEALTH_STATE_FILE.exists():
        try:
            return json.load(open(HEALTH_STATE_FILE))
        except:
            pass
    return {
        "last_check": None,
        "last_alert": None,
        "consecutive_failures": defaultdict(int),
        "last_heal_attempt": {},
        "health_history": [],
    }

def save_state(state: Dict):
    """Save health agent state."""
    HEALTH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HEALTH_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_process() -> Dict:
    """Check if main process is running."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "openclaw"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "healthy": len(result.stdout.strip().split('\n')) > 0,
            "pids": len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0,
            "details": f"{len(result.stdout.strip().split(chr(10)))} processes found"
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}

def check_memory() -> Dict:
    """Check memory usage."""
    try:
        result = subprocess.run(
            ["free", "-m"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            pct = (used / total * 100) if total > 0 else 0
            return {
                "healthy": pct < 90,
                "usage_pct": pct,
                "details": f"{used}MB / {total}MB ({pct:.1f}%)"
            }
    except Exception as e:
        return {"healthy": False, "error": str(e)}
    return {"healthy": True}

def check_disk() -> Dict:
    """Check disk usage."""
    try:
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            usage_pct = int(parts[4].replace('%', ''))
            return {
                "healthy": usage_pct < 90,
                "usage_pct": usage_pct,
                "details": f"{parts[2]} used / {parts[1]} ({usage_pct}%)"
            }
    except Exception as e:
        return {"healthy": False, "error": str(e)}
    return {"healthy": True}

def check_network() -> Dict:
    """Check network connectivity."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "https://google.com", "--max-time", "5"],
            capture_output=True,
            text=True,
            timeout=10
        )
        http_code = result.stdout.strip()
        return {
            "healthy": http_code in ["200", "301", "302"],
            "http_code": http_code,
            "details": f"HTTP {http_code}"
        }
    except:
        return {"healthy": False, "details": "Network unreachable"}

def check_gateway() -> Dict:
    """Check if gateway is responding."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:18789/health", "--max-time", "5"],
            capture_output=True,
            text=True,
            timeout=10
        )
        http_code = result.stdout.strip()
        return {
            "healthy": http_code in ["200", "404"],
            "http_code": http_code,
            "details": f"Gateway HTTP {http_code}"
        }
    except:
        return {"healthy": False, "details": "Gateway unreachable"}

def check_cron() -> Dict:
    """Check recent cron activity."""
    try:
        now = datetime.now()
        recent_failures = []
        
        # Check cron error log
        cron_log = LOGS_DIR / "cron_error_healer.log"
        if cron_log.exists():
            content = cron_log.read_text()
            lines = content.strip().split('\n')
            recent = [l for l in lines[-50:] if 'ERROR' in l or 'FAIL' in l]
            recent_failures = recent[-3:]  # Last 3
        
        return {
            "healthy": len(recent_failures) == 0,
            "recent_failures": len(recent_failures),
            "details": f"{len(recent_failures)} recent errors"
        }
    except Exception as e:
        return {"healthy": False, "error": str(e)}

def run_health_check(quick: bool = False) -> Dict:
    """Run full health check on all layers."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "quick": quick,
        "layers": {},
        "overall_healthy": True,
        "issues": [],
    }
    
    layers_to_check = list(LAYERS.keys()) if not quick else ['process', 'gateway']
    
    for layer in layers_to_check:
        check_func = globals()[LAYERS[layer]['check']]
        result = check_func()
        results['layers'][layer] = result
        
        if not result.get('healthy', False):
            results['overall_healthy'] = False
            results['issues'].append({
                'layer': layer,
                'details': result.get('details', 'Unknown'),
                'severity': 'CRITICAL' if layer in ['gateway', 'process'] else 'WARNING'
            })
    
    return results

def try_heal(layer: str, issue: Dict) -> bool:
    """Attempt to heal an issue."""
    log(f"Attempting to heal {layer}: {issue['details']}", "INFO")
    
    heal_funcs = {
        'gateway': heal_gateway,
        'process': heal_process,
        'disk': heal_disk,
        'memory': heal_memory,
        'cron': heal_cron,
        'network': heal_network,
    }
    
    heal_func = heal_funcs.get(layer)
    if heal_func:
        return heal_func(issue)
    return False

def heal_gateway(issue: Dict) -> bool:
    """Restart gateway."""
    try:
        subprocess.run(["/home/clawbot/.npm-global/bin/openclaw", "gateway", "restart"], timeout=30)
        log("Gateway restarted", "INFO")
        return True
    except Exception as e:
        log(f"Gateway restart failed: {e}", "ERROR")
        return False

def heal_process(issue: Dict) -> bool:
    """Restart service."""
    try:
        subprocess.run(["/home/clawbot/.npm-global/bin/openclaw", "gateway", "restart"], timeout=30)
        return True
    except:
        return False

def heal_disk(issue: Dict) -> bool:
    """Clean up temp files."""
    try:
        subprocess.run(["python3", str(SCRIPTS_DIR / "cleanup_temp.py")], timeout=30)
        return True
    except:
        return False

def heal_memory(issue: Dict) -> bool:
    """Clear cache / trigger GC."""
    # For now, just log
    log("Memory issue detected - manual intervention needed", "WARN")
    return False

def heal_cron(issue: Dict) -> bool:
    """Restart cron."""
    try:
        subprocess.run(["/home/clawbot/.npm-global/bin/openclaw", "gateway", "restart"], timeout=30)
        return True
    except:
        return False

def heal_network(issue: Dict) -> bool:
    """Retry network."""
    log("Network issue - will retry on next check", "WARN")
    return False

def publish_event(event_type: str, data: Dict):
    """Publish event to event bus."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    event = {
        "type": event_type,
        "source": "health_agent",
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    event_file = EVENTS_DIR / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(event_file, "w") as f:
        json.dump(event, f, indent=2)

def send_alert(message: str, severity: str = "WARNING"):
    """Send Telegram alert."""
    # Check cooldown
    state = load_state()
    last_alert = state.get('last_alert', {})
    
    if severity == "CRITICAL":
        if last_alert.get('type') == 'CRITICAL':
            diff = (datetime.now() - datetime.fromisoformat(last_alert['time'])).seconds
            if diff < CRITICAL_COOLDOWN:
                log(f"Critical alert suppressed (cooldown): {message[:50]}", "INFO")
                return
    
    # Send via openclaw if available
    try:
        subprocess.run(
            ["/home/clawbot/.npm-global/bin/openclaw", "send", "--message", f"🦞 Health Alert [{severity}]: {message}"],
            timeout=10
        )
    except:
        pass
    
    # Update state
    state['last_alert'] = {
        'type': severity,
        'time': datetime.now().isoformat(),
        'message': message[:100]
    }
    save_state(state)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Health Agent')
    parser.add_argument('--check', action='store_true', help='Full health check')
    parser.add_argument('--quick', action='store_true', help='Quick check (process + gateway)')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--test', action='store_true', help='Test mode (no alerts)')
    args = parser.parse_args()
    
    if args.daemon:
        log("Health Agent starting in daemon mode", "INFO")
        run_daemon()
    elif args.check:
        results = run_health_check(quick=False)
        print_health_results(results, test_mode=args.test)
    elif args.quick:
        results = run_health_check(quick=True)
        print_health_results(results, test_mode=args.test)
    else:
        # Default: full check
        results = run_health_check(quick=False)
        print_health_results(results, test_mode=args.test)

def print_health_results(results: Dict, test_mode: bool = False):
    """Print health check results."""
    print(f"\n🦞 Health Agent — {results['timestamp']}")
    print("=" * 50)
    
    healthy_count = 0
    for layer, data in results['layers'].items():
        emoji = "✅" if data.get('healthy') else "❌"
        details = data.get('details', data.get('error', 'N/A'))
        print(f"{emoji} {LAYERS[layer]['name']}: {details}")
        if data.get('healthy'):
            healthy_count += 1
    
    pct = healthy_count / len(results['layers']) * 100
    print(f"\n📊 Health: {healthy_count}/{len(results['layers'])} ({pct:.0f}%)")
    
    if results['issues']:
        print(f"\n⚠️ Issues detected: {len(results['issues'])}")
        for issue in results['issues']:
            print(f"   [{issue['severity']}] {issue['layer']}: {issue['details']}")
    
    if not test_mode and not results['overall_healthy']:
        # Try to heal
        for issue in results['issues']:
            if issue['severity'] == 'CRITICAL':
                healed = try_heal(issue['layer'], issue)
                if healed:
                    print(f"   ✅ Self-healed: {issue['layer']}")
                else:
                    send_alert(f"{issue['layer']}: {issue['details']}", issue['severity'])

def run_daemon():
    """Run health agent as daemon."""
    import time
    
    log("Health Agent daemon started", "INFO")
    
    while True:
        try:
            results = run_health_check(quick=False)
            
            # Update state
            state = load_state()
            state['last_check'] = results['timestamp']
            state['health_history'].append({
                'timestamp': results['timestamp'],
                'healthy': results['overall_healthy'],
                'issue_count': len(results['issues'])
            })
            state['health_history'] = state['health_history'][-100:]  # Keep last 100
            save_state(state)
            
            # Handle issues
            if not results['overall_healthy']:
                for issue in results['issues']:
                    healed = try_heal(issue['layer'], issue)
                    if not healed and issue['severity'] == 'CRITICAL':
                        send_alert(f"{issue['layer']}: {issue['details']}", issue['severity'])
            
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            log("Health Agent stopped by user", "INFO")
            break
        except Exception as e:
            log(f"Health Agent error: {e}", "ERROR")
            time.sleep(60)

if __name__ == "__main__":
    main()

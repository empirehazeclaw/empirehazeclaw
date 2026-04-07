#!/usr/bin/env python3
"""
⚡ Autonomous Loop v2.0
Kurzintervall-Executor der:
- Alle 15min läuft
- Quick Checks macht
- Bei Bedarf Actions auslöst
- Self-Healing bei Fehlern
- File-Locking für atomic Writes

Usage: python3 autonomous_loop.py [--quick]
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Add lib to path for file_lock
sys.path.insert(0, str(Path(__file__).parent))

LOG = Path("/home/clawbot/.openclaw/workspace/logs/autonomous_loop.log")
STATE = Path("/home/clawbot/.openclaw/workspace/data/autonomous_state.json")

# Import file locking
try:
    from lib.file_lock import locked_write, locked_read, locked_append
    HAS_FILELOCK = True
except ImportError:
    HAS_FILELOCK = False

# Import self-healing
sys.path.insert(0, str(Path(__file__).parent))
from self_healing import SelfHealer

def log(msg: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    locked_append(str(LOG), line)

def check_websites():
    """Quick Website Check"""
    import requests
    sites = [
        ("Store", "https://empirehazeclaw.store"),
        ("DE", "https://empirehazeclaw.de"),
        ("Info", "https://empirehazeclaw.info"),
        ("COM", "https://empirehazeclaw.com"),
    ]
    
    issues = []
    for name, url in sites:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                issues.append(f"{name}: HTTP {r.status_code}")
        except Exception as e:
            issues.append(f"{name}: DOWN - {type(e).__name__}")
    
    return issues

def check_services():
    """Quick Service Check - DISABLED: External services on old VPS never set up
    Re-enabled with self-healing for local services
    """
    issues = []
    
    # Check local services with self-healing
    healer = SelfHealer()
    for name, config in healer.config["services"].items():
        if not healer.check_service(name, config):
            issues.append(f"{name}: DOWN")
            # Try to heal
            healer.heal_service(name, config)
    
    return issues

def check_critical_services():
    """Check if OpenClaw Gateway is running"""
    issues = []
    
    # Check if gateway process is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "openclaw"],
            capture_output=True, text=True
        )
        if not result.stdout.strip():
            issues.append("OpenClaw Gateway: DOWN")
    except:
        pass
    
    # Check if port 18789 is listening
    try:
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True, text=True
        )
        if "18789" not in result.stdout:
            issues.append("Gateway Port 18789: NOT LISTENING")
    except:
        pass
    
    return issues

def check_disk_space():
    """Prüft ob Disk fast voll"""
    import shutil
    usage = shutil.disk_usage("/")
    percent = (usage.used / usage.total) * 100
    
    if percent > 90:
        return [f"Disk at {percent:.1f}%"]
    return []

def check_memory():
    """Prüft ob Memory knapp wird"""
    import psutil
    mem = psutil.virtual_memory()
    
    if mem.percent > 90:
        return [f"Memory at {mem.percent:.1f}%"]
    return []

def check_git_status():
    """Check git status and push if needed"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True,
            cwd="/home/clawbot/.openclaw/workspace"
        )
        if result.stdout.strip():
            # There are changes - attempt backup commit
            subprocess.run(
                ["git", "add", "-A"],
                capture_output=True,
                cwd="/home/clawbot/.openclaw/workspace"
            )
            subprocess.run(
                ["git", "commit", "-m", "Auto-backup $(date -u +%Y-%m-%dT%H:%M:%SZ)"],
                capture_output=True,
                cwd="/home/clawbot/.openclaw/workspace"
            )
            return []
    except:
        pass
    return []

def run_self_healing():
    """Run self-healing cycle"""
    try:
        healer = SelfHealer()
        healed = healer.run_cycle()
        if healed:
            log(f"🔧 Self-healer repaired: {', '.join(healed)}")
        return healed
    except Exception as e:
        log(f"❌ Self-healing failed: {e}", "ERROR")
        return []

def update_state(issues: list):
    """Update autonomous state with file locking"""
    state = {
        "last_check": datetime.now().isoformat(),
        "issue_count": len(issues),
        "issues": issues[-5:]  # Keep last 5
    }
    
    if HAS_FILELOCK:
        locked_write(str(STATE), state)
    else:
        with open(STATE, "w") as f:
            import json
            json.dump(state, f, indent=2)

def main():
    log("="*50)
    log("AUTONOMOUS LOOP v2.0 STARTED")
    
    all_issues = []
    
    # Run self-healing first
    log("Running self-healing check...")
    run_self_healing()
    
    # Quick Checks
    log("Checking websites...")
    website_issues = check_websites()
    all_issues.extend(website_issues)
    
    log("Checking services...")
    service_issues = check_services()
    all_issues.extend(service_issues)
    
    log("Checking critical services...")
    critical_issues = check_critical_services()
    all_issues.extend(critical_issues)
    
    # Resource Checks
    log("Checking resources...")
    try:
        all_issues.extend(check_disk_space())
        all_issues.extend(check_memory())
    except Exception as e:
        log(f"Resource check failed: {e}", "WARN")
    
    # Git auto-backup
    log("Checking git status...")
    try:
        check_git_status()
    except Exception as e:
        log(f"Git check failed: {e}", "WARN")
    
    # Update state with file locking
    update_state(all_issues)
    
    # Report
    if all_issues:
        log(f"⚠️ ISSUES FOUND: {len(all_issues)}", "WARN")
        for issue in all_issues:
            log(f"  - {issue}")
        
        # Alert wenn kritisch
        critical = [i for i in all_issues if "DOWN" in i or "not running" in i]
        if critical:
            send_alert(critical)
    else:
        log("✅ All systems healthy")
    
    log("="*50)
    
    # Write heartbeat
    heartbeat = Path("/home/clawbot/.openclaw/workspace/logs/heartbeat.log")
    locked_write(str(heartbeat), {"timestamp": datetime.now().isoformat(), "status": "ok"})

def send_alert(issues):
    """Sendet Alert via multiple channels"""
    try:
        # Webhook
        webhook = os.environ.get("ALERT_WEBHOOK_URL")
        if webhook:
            try:
                import requests
                msg = "🤖 Autonomer Alert:\n" + "\n".join(issues)
                requests.post(webhook, json={"text": msg}, timeout=5)
                log("✅ Alert sent via webhook")
            except Exception as e:
                log(f"Webhook alert failed: {e}", "WARN")
        
        # Telegram fallback via gog
        try:
            import json
            alert_file = Path("/home/clawbot/.openclaw/workspace/logs/alerts_pending.json")
            alerts = locked_read(str(alert_file), [])
            alerts.extend(issues)
            locked_write(str(alert_file), alerts[-10:])  # Keep last 10
        except:
            pass
            
    except Exception as e:
        log(f"Alert system failed: {e}", "ERROR")

if __name__ == "__main__":
    main()

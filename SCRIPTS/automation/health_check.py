#!/usr/bin/env python3
"""
health_check.py — Consolidated System Health Checker
==================================================
Unified health check combining:
- quick_check.py (fast daily check)
- health_monitor.py (detailed monitoring)
- health_alert.py (alert generation)
- self_check.py (self-diagnostics)

Usage:
    python3 health_check.py --quick      # Fast daily check
    python3 health_check.py --full        # Detailed analysis
    python3 health_check.py --gateway    # Gateway only
    python3 health_check.py --disk       # Disk only
    python3 health_check.py --crons      # Cron jobs only
    python3 health_check.py --alert      # Generate alert
    python3 health_check.py --report     # Full report mode
"""

import os
import sys
import socket
import psutil
import sqlite3
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
CRON_PATH = WORKSPACE.parent / "cron/jobs.json"
GATEWAY_HOST = "127.0.0.1"
GATEWAY_PORT = 18789

# Thresholds
DISK_THRESHOLD = 15  # %
MEMORY_THRESHOLD = 85  # %
LOAD_THRESHOLD = 4.0
KG_MIN_ENTITIES = 100


class HealthCheck:
    """
    Unified Health Checker.
    
    Modes:
    - QUICK: Fast check, essential metrics only
    - FULL: Detailed analysis
    - SINGLE: Check specific component
    """
    
    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}
    
    def check_gateway(self) -> Tuple[bool, str]:
        """Check if gateway is responding."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((GATEWAY_HOST, GATEWAY_PORT))
            sock.close()
            
            if result == 0:
                return True, f"Gateway responding on {GATEWAY_HOST}:{GATEWAY_PORT}"
            else:
                return False, f"Gateway not reachable (port {GATEWAY_PORT})"
        except Exception as e:
            return False, f"Gateway check failed: {e}"
    
    def check_disk(self) -> Tuple[bool, str]:
        """Check disk space."""
        try:
            usage = psutil.disk_usage('/')
            percent = usage.percent
            free_gb = usage.free / (1024**3)
            
            if percent > (100 - DISK_THRESHOLD):
                return False, f"Disk almost full: {percent:.1f}% used, {free_gb:.1f}GB free"
            return True, f"Disk: {percent:.1f}% used, {free_gb:.1f}GB free"
        except Exception as e:
            return False, f"Disk check failed: {e}"
    
    def check_memory(self) -> Tuple[bool, str]:
        """Check system memory."""
        try:
            mem = psutil.virtual_memory()
            percent = mem.percent
            available_gb = mem.available / (1024**3)
            
            if percent > MEMORY_THRESHOLD:
                return False, f"Memory high: {percent:.1f}% used, {available_gb:.1f}GB available"
            return True, f"Memory: {percent:.1f}% used, {available_gb:.1f}GB available"
        except Exception as e:
            return False, f"Memory check failed: {e}"
    
    def check_load(self) -> Tuple[bool, str]:
        """Check system load."""
        try:
            load = psutil.getloadavg()[0]
            
            if load > LOAD_THRESHOLD:
                return False, f"Load high: {load:.2f} (threshold: {LOAD_THRESHOLD})"
            return True, f"Load: {load:.2f}"
        except Exception as e:
            return False, f"Load check failed: {e}"
    
    def check_crons(self) -> Tuple[bool, str]:
        """Check cron job health."""
        try:
            cron_file = CRON_PATH
            if not cron_file.exists():
                return True, "No cron jobs file (OK)"
            
            jobs = json.loads(cron_file.read_text())
            total = len(jobs.get('jobs', []))
            
            if total == 0:
                return True, "No cron jobs configured"
            
            # Count enabled vs disabled
            enabled = sum(1 for j in jobs.get('jobs', []) if j.get('enabled', True))
            
            return True, f"Crons: {enabled}/{total} enabled"
        except Exception as e:
            return False, f"Cron check failed: {e}"
    
    def check_kg(self) -> Tuple[bool, str]:
        """Check knowledge graph health."""
        try:
            if not KG_PATH.exists():
                return False, "KG file not found"
            
            kg = json.loads(KG_PATH.read_text())
            entities = kg.get('entities', {})
            relations = kg.get('relations', [])
            
            entity_count = len(entities)
            relation_count = len(relations)
            
            if entity_count < KG_MIN_ENTITIES:
                return False, f"KG low: {entity_count} entities (expected >{KG_MIN_ENTITIES})"
            
            # Check for entities with access
            accessed = sum(1 for e in entities.values() if e.get('access_count', 0) > 0)
            
            return True, f"KG: {entity_count} entities, {accessed} accessed, {relation_count} relations"
        except Exception as e:
            return False, f"KG check failed: {e}"
    
    def check_recent_errors(self) -> Tuple[bool, str]:
        """Check for recent errors in logs."""
        try:
            # Check error log
            error_log = WORKSPACE / "logs" / "error.log"
            if error_log.exists():
                # Get last 100 lines
                lines = error_log.read_text(errors='ignore').split('\n')[-100:]
                error_count = sum(1 for l in lines if 'ERROR' in l.upper())
                
                if error_count > 10:
                    return False, f"Many errors in log: {error_count} recent"
                elif error_count > 0:
                    return True, f"Errors in log: {error_count} recent"
            
            return True, "No recent errors"
        except Exception as e:
            return False, f"Error log check failed: {e}"
    
    def check_database(self) -> Tuple[bool, str]:
        """Check if database is accessible."""
        try:
            db_path = WORKSPACE.parent / "data" / "openclaw.db"
            if not db_path.exists():
                return True, "Database not found (OK for file-based)"
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            conn.close()
            
            return True, f"Database: {count} sessions"
        except Exception as e:
            return False, f"Database check failed: {e}"
    
    def run_quick_check(self) -> bool:
        """
        Quick check - fast daily health status.
        Returns True if all checks pass.
        """
        print(f"Sir HazeClaw Quick Check — {datetime.now().strftime('%H:%M:%S UTC')}")
        print("=" * 50)
        
        checks = [
            ("Gateway", self.check_gateway),
            ("Disk", self.check_disk),
            ("Memory", self.check_memory),
        ]
        
        all_ok = True
        for name, check_fn in checks:
            ok, msg = check_fn()
            symbol = "✅" if ok else "❌"
            print(f"{symbol} {name}: {msg}")
            if not ok:
                all_ok = False
        
        return all_ok
    
    def run_full_check(self) -> bool:
        """
        Full health check - all systems.
        Returns True if all checks pass.
        """
        print(f"Sir HazeClaw Health Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        print("=" * 60)
        
        checks = [
            ("Gateway", self.check_gateway),
            ("Disk", self.check_disk),
            ("Memory", self.check_memory),
            ("Load", self.check_load),
            ("Database", self.check_database),
            ("Cron Jobs", self.check_crons),
            ("Knowledge Graph", self.check_kg),
            ("Recent Errors", self.check_recent_errors),
        ]
        
        all_ok = True
        for name, check_fn in checks:
            ok, msg = check_fn()
            symbol = "✅" if ok else "❌"
            print(f"{symbol} {name}: {msg}")
            if not ok:
                all_ok = False
        
        print("=" * 60)
        if all_ok:
            print("✅ All systems healthy")
        else:
            print("❌ Some systems need attention")
        
        return all_ok
    
    def generate_alert(self) -> str:
        """Generate alert message for failed checks."""
        checks = [
            ("Gateway", self.check_gateway),
            ("Disk", self.check_disk),
            ("Memory", self.check_memory),
            ("KG", self.check_kg),
        ]
        
        failed = []
        for name, check_fn in checks:
            ok, msg = check_fn()
            if not ok:
                failed.append(f"{name}: {msg}")
        
        if not failed:
            return "✅ All systems healthy"
        
        return "🚨 System Alert:\n" + "\n".join(f"  - {f}" for f in failed)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sir HazeClaw Health Check")
    parser.add_argument("--quick", action="store_true", help="Quick daily check")
    parser.add_argument("--full", action="store_true", help="Full detailed check")
    parser.add_argument("--gateway", action="store_true", help="Gateway only")
    parser.add_argument("--disk", action="store_true", help="Disk only")
    parser.add_argument("--memory", action="store_true", help="Memory only")
    parser.add_argument("--crons", action="store_true", help="Cron jobs only")
    parser.add_argument("--kg", action="store_true", help="Knowledge graph only")
    parser.add_argument("--alert", action="store_true", help="Generate alert message")
    parser.add_argument("--report", action="store_true", help="Full report mode")
    
    args = parser.parse_args()
    
    checker = HealthCheck()
    
    # Default to quick check if no args
    if not any([args.quick, args.full, args.gateway, args.disk, 
                args.memory, args.crons, args.kg, args.alert, args.report]):
        args.quick = True
    
    exit_code = 0
    
    if args.quick:
        ok = checker.run_quick_check()
        exit_code = 0 if ok else 1
    
    elif args.full or args.report:
        ok = checker.run_full_check()
        exit_code = 0 if ok else 1
    
    elif args.gateway:
        ok, msg = checker.check_gateway()
        print(f"Gateway: {msg}")
        exit_code = 0 if ok else 1
    
    elif args.disk:
        ok, msg = checker.check_disk()
        print(f"Disk: {msg}")
        exit_code = 0 if ok else 1
    
    elif args.memory:
        ok, msg = checker.check_memory()
        print(f"Memory: {msg}")
        exit_code = 0 if ok else 1
    
    elif args.crons:
        ok, msg = checker.check_crons()
        print(f"Cron Jobs: {msg}")
        exit_code = 0 if ok else 1
    
    elif args.kg:
        ok, msg = checker.check_kg()
        print(f"Knowledge Graph: {msg}")
        exit_code = 0 if ok else 1
    
    elif args.alert:
        alert = checker.generate_alert()
        print(alert)
        exit_code = 0 if "All systems" in alert else 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

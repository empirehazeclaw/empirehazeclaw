#!/usr/bin/env python3
"""
Simple Security Audit - Lynis Alternative
Führt grundlegende Security-Checks durch
"""

import os
import subprocess
import sys

def check(name: str, cmd: str) -> tuple[bool, str]:
    """Führe einen Check aus"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()[:200]
    except Exception as e:
        return False, str(e)

def main():
    print("🛡️ Security Audit - Basic\n")
    print("=" * 50)
    
    checks = [
        ("Firewall (UFW)", "sudo ufw status | grep -q 'Status: active'"),
        ("Open Ports", "sudo netstat -tuln 2>/dev/null | wc -l"),
        ("SSH Config", "grep -q 'PermitRootLogin no' /etc/ssh/sshd_config 2>/dev/null && echo 'OK' || echo 'WARN'"),
        ("Fail2Ban", "systemctl is-active fail2ban 2>/dev/null"),
        ("Last Login", "last -1 2>/dev/null | head -1"),
        ("Failed Logins", "sudo grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -5"),
        ("Disk Usage", "df -h / | tail -1 | awk '{print $5}'"),
        ("RAM Usage", "free -m | grep Mem: | awk '{print $3/$2 * 100}'"),
        ("Running Services", "systemctl list-units --type=service --state=running 2>/dev/null | wc -l"),
    ]
    
    print(f"{'Check':<20} {'Status':<10} {'Details'}")
    print("-" * 50)
    
    for name, cmd in checks:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                status = "✅ OK"
                details = result.stdout.strip()[:40]
            else:
                status = "⚠️ WARN"
                details = result.stdout.strip()[:40] if result.stdout else "Check failed"
        except Exception as e:
            status = "❌ ERR"
            details = str(e)[:40]
        
        print(f"{name:<20} {status:<10} {details}")
    
    print("\n" + "=" * 50)
    print("🛡️ Basic Security Audit abgeschlossen!")
    print("\nFür vollständigen Scan: sudo lynis audit system")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
🔒 SECURITY AUDIT
==============
"""

import subprocess
from pathlib import Path

def check_ssh():
    result = subprocess.run(["grep", "PermitRootLogin", "/etc/ssh/sshd_config"], 
                         capture_output=True, text=True)
    return "no" in result.stdout.lower()

def check_fail2ban():
    result = subprocess.run(["pgrep", "fail2ban"], capture_output=True)
    return result.returncode == 0

def check_firewall():
    result = subprocess.run(["which", "ufw"], capture_output=True)
    return result.returncode == 0

def check_backups():
    backup_dir = Path("backups")
    return len(list(backup_dir.glob("*.tar.gz"))) > 0 if backup_dir.exists() else False

print("🔒 SECURITY AUDIT")
print("=" * 40)
print(f"SSH Root Login: {'✅ Disabled' if check_ssh() else '⚠️ Enabled'}")
print(f"Fail2ban: {'✅ Running' if check_fail2ban() else '❌ Not running'}")
print(f"UFW: {'✅ Installed' if check_firewall() else '❌ Not installed'}")
print(f"Backups: {'✅ Available' if check_backups() else '❌ Missing'}")
print("=" * 40)

#!/usr/bin/env python3
"""
Security Updater - Automatische Sicherheitsprüfungen
Läuft täglich um 4:00 Uhr
"""

import subprocess
import sys
import os
import shlex
from datetime import datetime

def run_command(cmd):
    """Führe Shell-Befehl aus"""
    try:
        # Use list form with shlex.split for security
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list, capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def has_root_access():
    """Prüfe ob wir Root-Rechte haben"""
    return os.geteuid() == 0

def check_system_updates():
    """Prüfe System-Updates"""
    print("🔄 Prüfe System-Updates...")
    
    if not has_root_access():
        success, stdout, _ = run_command("apt list --upgradable 2>/dev/null | grep -v 'Listing...'")
        if success and stdout.strip():
            count = len(stdout.strip().split("\n"))
            print(f"   ℹ️  {count} Updates verfügbar (kein Root)")
        else:
            print("   ✅ Keine Updates")
        return True
    
    success, stdout, stderr = run_command("apt list --upgradable 2>/dev/null | grep -v 'Listing...'")
    if success and stdout.strip():
        count = len(stdout.strip().split("\n"))
        print(f"   ⚠️  Updates verfügbar: {count}")
        return False
    print("   ✅ System aktuell")
    return True

def check_security_packages():
    """Prüfe Sicherheitspakete"""
    print("🔄 Prüfe Sicherheitspakete...")
    
    if not has_root_access():
        print("   ⏭️  Übersprungen (kein Root)")
        return True
    
    success, _, _ = run_command("which fail2ban")
    if not success:
        print("   ⚠️  fail2ban nicht installiert")
        return False
    print("   ✅ fail2ban installiert")
    return True

def check_firewall():
    """Prüfe Firewall-Status"""
    print("🔄 Prüfe Firewall...")
    
    # Check if ufw is available
    success, _, _ = run_command("which ufw")
    if not success:
        print("   ℹ️  ufw nicht verfügbar")
        return True
    
    success, stdout, _ = run_command("ufw status")
    if success and "Status: active" in stdout:
        print("   ✅ Firewall aktiv")
        return True
    print("   ⚠️  Firewall nicht aktiv")
    return False

def check_ssh_keys():
    """Prüfe SSH-Keys"""
    print("🔄 Prüfe SSH-Keys...")
    success, stdout, _ = run_command("ls -la ~/.ssh/ 2>/dev/null")
    if success and stdout:
        key_count = stdout.count("ssh-")
        print(f"   ✅ {key_count} SSH-Keys gefunden")
        return True
    print("   ℹ️  Keine SSH-Keys (optional)")
    return True

def check_open_ports():
    """Prüfe offene Ports"""
    print("🔄 Prüfe offene Ports...")
    success, stdout, _ = run_command("ss -tuln | grep LISTEN")
    if success:
        ports = len(stdout.strip().split("\n")) if stdout.strip() else 0
        print(f"   ℹ️  {ports} offene Ports")
    return True

def check_openclaw_security():
    """Prüfe OpenClaw-spezifische Sicherheit"""
    print("🔄 Prüfe OpenClaw Sicherheit...")
    
    # Check prompt injection shield
    shield_path = "/home/clawbot/.openclaw/workspace/scripts/prompt_injection_shield.py"
    if os.path.exists(shield_path):
        print("   ✅ Prompt Injection Shield aktiv")
    else:
        print("   ⚠️  Prompt Injection Shield fehlt")
        return False
    
    # Check config exists
    config_paths = [
        "/home/clawbot/.openclaw/openclaw.json",
        "/home/clawbot/.openclaw/config.json",
        os.path.expanduser("~/.openclaw/config.json")
    ]
    config_found = any(os.path.exists(p) for p in config_paths)
    if config_found:
        print("   ✅ Config vorhanden")
    else:
        print("   ⚠️  Config fehlt")
        return False
    
    return True

def main():
    print("🛡️ Security Updater Start...")
    print(f"   Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not has_root_access():
        print("   ℹ️  Limited user mode (kein Root)")
    
    print()
    
    checks = [
        ("System Updates", check_system_updates),
        ("Sicherheitspakete", check_security_packages),
        ("Firewall", check_firewall),
        ("SSH-Keys", check_ssh_keys),
        ("Offene Ports", check_open_ports),
        ("OpenClaw Sicherheit", check_openclaw_security),
    ]
    
    results = []
    for name, func in checks:
        try:
            results.append(func())
        except Exception as e:
            print(f"   ❌ {name} Fehler: {e}")
            results.append(False)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print(f"📊 Ergebnis: {passed}/{total} Checks bestanden")
    
    if passed == total:
        print("✅ System sicher")
        return 0
    elif passed >= total - 1:
        print("⚠️  Kleinere Issues")
        return 1
    else:
        print("❌ Handlungsbedarf")
        return 2

if __name__ == "__main__":
    sys.exit(main())

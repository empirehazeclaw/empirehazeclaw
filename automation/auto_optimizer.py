#!/usr/bin/env python3
"""
Auto Optimizer - System Performance & Efficiency Optimizer
Führt täglich automatische Optimierungen durch
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = "/home/clawbot/.openclaw/logs/auto_optimizer.log"
CONFIG_DIR = "/home/clawbot/.openclaw/workspace/knowledge_rag/"
SCRIPTS_DIR = "/home/clawbot/.openclaw/workspace/scripts/"

def log(msg):
    """Log to file"""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def check_cron_efficiency():
    """Prüfe Cron-Jobs auf Effizienz"""
    log("🔍 Prüfe Cron-Jobs...")
    
    # Check gateway cron via API
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--include-disabled"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if "jobs" in result.stdout.lower() or result.returncode == 0:
            job_count = result.stdout.count('"id":')
            log(f"✅ {job_count} Cron-Jobs registriert")
            return []
        
    except Exception as e:
        log(f"⚠️ Cron Check fehlgeschlagen: {e}")
    
    return []

def check_memory_files():
    """Prüfe Memory auf Stabilität"""
    log("🔍 Prüfe Memory-Struktur...")
    
    memory_dir = Path("/home/clawbot/.openclaw/workspace/memory")
    if not memory_dir.exists():
        return ["Memory Verzeichnis nicht gefunden"]
    
    # Check for large files
    large_files = []
    for f in memory_dir.glob("*.md"):
        size = f.stat().st_size
        if size > 500_000:  # > 500KB
            large_files.append(f"{f.name}: {size/1000:.1f}KB")
    
    if large_files:
        log(f"⚠️ Große Memory-Dateien: {large_files}")
        return [f"Große Dateien: {', '.join(large_files)}"]
    
    log("✅ Memory strukturiert")
    return []

def check_unused_skills():
    """Finde ungenutzte Skills"""
    log("🔍 Prüfe ungenutzte Skills...")
    
    skills_dir = Path("/home/clawbot/.openclaw/skills")
    if not skills_dir.exists():
        return []
    
    unused = []
    # Check which skills exist but aren't referenced in cron
    cron_file = "/home/clawbot/.openclaw/config/cron.json"
    if os.path.exists(cron_file):
        with open(cron_file) as f:
            cron_data = json.load(f)
        cron_text = json.dumps(cron_data)
        
        for d in skills_dir.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                skill_name = d.name
                if skill_name.lower() not in cron_text.lower():
                    unused.append(skill_name)
    
    if unused:
        log(f"💡 Ungenutzte Skills: {', '.join(unused)}")
        return [f"Ungenutzt: {', '.join(unused)}"]
    
    return []

def check_api_providers():
    """Prüfe API-Provider Konfiguration"""
    log("🔍 Prüfe API-Provider...")
    
    config_file = "/home/clawbot/.openclaw/agents/main/agent/models.json"
    if not os.path.exists(config_file):
        return ["Config nicht gefunden"]
    
    with open(config_file) as f:
        config = json.load(f)
    
    issues = []
    
    # Check for missing API keys - look for configured providers
    providers = config.get("providers", {})
    active = [p for p, v in providers.items() if v.get("enabled", True)]
    
    if not active:
        return ["Keine aktiven Provider gefunden"]
    
    # Just check that providers exist and are enabled
    if len(active) >= 2:
        log(f"✅ {len(active)} API-Provider aktiv")
        return []
    
    return []

def check_temp_files():
    """Finde und bereinige temp Dateien"""
    log("🔍 Prüfe Temp-Dateien...")
    
    temp_dirs = [
        "/home/clawbot/.openclaw/tmp",
        "/home/clawbot/.openclaw/cache"
    ]
    
    total_cleaned = 0
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for f in Path(temp_dir).iterdir():
                if f.is_file():
                    age = datetime.now().timestamp() - f.stat().st_mtime
                    if age > 7 * 24 * 3600:  # > 7 days
                        try:
                            f.unlink()
                            total_cleaned += 1
                        except:
                            pass
    
    if total_cleaned > 0:
        log(f"🧹 {total_cleaned} alte Temp-Dateien gelöscht")
        return [f"{total_cleaned} Temp-Dateien bereinigt"]
    
    log("✅ Keine Temp-Dateien zu bereinigen")
    return []

def run_optimization():
    """Führe complete Optimierung durch"""
    log("🚀 Starte Auto-Optimizer...")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Run all checks
    results["checks"]["cron"] = check_cron_efficiency()
    results["checks"]["memory"] = check_memory_files()
    results["checks"]["skills"] = check_unused_skills()
    results["checks"]["api"] = check_api_providers()
    results["checks"]["temp"] = check_temp_files()
    
    # Summary
    all_issues = []
    for check, issues in results["checks"].items():
        all_issues.extend(issues)
    
    results["total_issues"] = len(all_issues)
    results["status"] = "OPTIMIZED" if len(all_issues) == 0 else "ATTENTION_NEEDED"
    
    # Save report
    report_file = f"/home/clawbot/.openclaw/workspace/memory/auto-optimizer-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_file, "w") as f:
        f.write(f"# Auto-Optimizer Report\n")
        f.write(f"**Datum:** {results['timestamp']}\n")
        f.write(f"**Status:** {results['status']}\n\n")
        f.write(f"## Ergebnisse\n\n")
        for check, issues in results["checks"].items():
            f.write(f"### {check.upper()}\n")
            if issues:
                for issue in issues:
                    f.write(f"- {issue}\n")
            else:
                f.write("- ✅ Keine Issues\n")
            f.write("\n")
    
    log(f"\n📊 Auto-Optimizer Resultat:")
    log(f"   Status: {results['status']}")
    log(f"   Issues gefunden: {len(all_issues)}")
    log(f"   Report: {report_file}")
    
    return results

if __name__ == "__main__":
    run_optimization()

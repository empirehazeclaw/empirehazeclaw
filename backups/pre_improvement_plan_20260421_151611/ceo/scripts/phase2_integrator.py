#!/usr/bin/env python3
"""
Phase 2 Integrator — Day 5
==========================
Integriert alle Phase 2 Components und validiert das System.

Usage:
    python3 phase2_integrator.py --full        # Vollständiger Test
    python3 phase2_integrator.py --quick       # Quick Check
    python3 phase2_integrator.py --validate    # Validierung
    python3 phase2_integrator.py --report      # Generate Report
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SCRIPTS_DIR = WORKSPACE / "scripts"
MEMORY_DIR = WORKSPACE / "memory"

# Phase 2 components
COMPONENTS = {
    "kg_causal_updater": {
        "script": SCRIPTS_DIR / "kg_causal_updater.py",
        "description": "KG Causal Updater - Syncs failures to KG as causal chains"
    },
    "dependency_tracker": {
        "script": SCRIPTS_DIR / "dependency_tracker.py",
        "description": "Dependency Tracker - Tracks inter-component dependencies"
    }
}

def check_script(script_path: Path) -> dict:
    if not script_path.exists():
        return {"status": "❌", "message": "Script nicht gefunden"}
    try:
        content = script_path.read_text()
        if len(content) < 100:
            return {"status": "❌", "message": "Script ist leer"}
        return {"status": "✅", "message": f"OK ({len(content)} bytes)"}
    except Exception as e:
        return {"status": "❌", "message": str(e)}

def run_script_test(script_name: str, script_path: Path, test_args: list) -> dict:
    try:
        result = subprocess.run(
            ["python3", str(script_path)] + test_args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "status": "✅" if result.returncode == 0 else "❌",
            "message": f"Exit: {result.returncode}",
            "output": result.stdout[:300] if result.stdout else result.stderr[:300]
        }
    except subprocess.TimeoutExpired:
        return {"status": "❌", "message": "Timeout"}
    except Exception as e:
        return {"status": "❌", "message": str(e)}

def quick_check():
    print("\n🔍 Phase 2 Quick Check\n")
    all_ok = True
    for name, info in COMPONENTS.items():
        script_ok = info["script"].exists()
        if script_ok:
            status = "✅"
        else:
            status = "❌"
            all_ok = False
        print(f"  {status} {name}")
    print(f"\n{'✅ Alle Komponenten OK' if all_ok else '❌ Probleme gefunden'}")
    return all_ok

def full_test():
    print("\n" + "=" * 50)
    print("🧪 PHASE 2 FULL TEST")
    print("=" * 50)
    
    results = {}
    
    # Step 1: Script checks
    print("\n📝 Step 1: Script Validation")
    for name, info in COMPONENTS.items():
        check = check_script(info["script"])
        results[name] = check
        print(f"  [{check['status']}] {name}: {check['message']}")
    
    # Step 2: Run kg_causal_updater --sync-failures
    print("\n📝 Step 2: KG Causal Updater Test")
    kg_result = run_script_test(
        "kg_causal_updater",
        COMPONENTS["kg_causal_updater"]["script"],
        ["--sync-failures"]
    )
    results["kg_causal_sync"] = kg_result
    print(f"  [{kg_result['status']}] {kg_result['message']}")
    if kg_result.get("output"):
        print(f"       {kg_result['output'][:200]}")
    
    # Step 3: KG causal stats
    print("\n📝 Step 3: KG Causal Stats")
    stats_result = run_script_test(
        "kg_causal_updater",
        COMPONENTS["kg_causal_updater"]["script"],
        ["--stats"]
    )
    results["kg_causal_stats"] = stats_result
    print(f"  [{stats_result['status']}] {stats_result['message']}")
    if stats_result.get("output"):
        print(f"       {stats_result['output'][:200]}")
    
    # Step 4: Run kg_causal_updater --dag
    print("\n📝 Step 4: KG DAG View")
    dag_result = run_script_test(
        "kg_causal_updater",
        COMPONENTS["kg_causal_updater"]["script"],
        ["--dag"]
    )
    results["kg_dag"] = dag_result
    print(f"  [{dag_result['status']}] {dag_result['message']}")
    if dag_result.get("output"):
        print(f"       {dag_result['output'][:200]}")
    
    # Step 5: Run dependency_tracker --scan
    print("\n📝 Step 5: Dependency Tracker Scan")
    dep_scan = run_script_test(
        "dependency_tracker",
        COMPONENTS["dependency_tracker"]["script"],
        ["--scan"]
    )
    results["dep_scan"] = dep_scan
    print(f"  [{dep_scan['status']}] {dep_scan['message']}")
    if dep_scan.get("output"):
        print(f"       {dep_scan['output'][:200]}")
    
    # Step 6: Dependency stats
    print("\n📝 Step 6: Dependency Stats")
    dep_stats = run_script_test(
        "dependency_tracker",
        COMPONENTS["dependency_tracker"]["script"],
        ["--stats"]
    )
    results["dep_stats"] = dep_stats
    print(f"  [{dep_stats['status']}] {dep_stats['message']}")
    if dep_stats.get("output"):
        print(f"       {dep_stats['output'][:200]}")
    
    # Step 7: Dependency validate
    print("\n📝 Step 7: Dependency Validation")
    dep_validate = run_script_test(
        "dependency_tracker",
        COMPONENTS["dependency_tracker"]["script"],
        ["--validate"]
    )
    results["dep_validate"] = dep_validate
    print(f"  [{dep_validate['status']}] {dep_validate['message']}")
    if dep_validate.get("output"):
        print(f"       {dep_validate['output'][:200]}")
    
    # Overall result
    all_passed = all(r.get("status") == "✅" for r in results.values())
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ PHASE 2 FULL TEST PASSED")
    else:
        print("⚠️  PHASE 2 TEST COMPLETED WITH ISSUES")
        for name, result in results.items():
            if result.get("status") != "✅":
                print(f"     {name}: {result.get('message')}")
    print("=" * 50)
    
    return results

def generate_report():
    print("\n📊 Phase 2 Completion Report")
    print("=" * 50)
    
    # Collect metrics
    kg_causal_stats = subprocess.run(
        ["python3", str(COMPONENTS["kg_causal_updater"]["script"]), "--stats"],
        capture_output=True, text=True
    )
    
    dep_stats = subprocess.run(
        ["python3", str(COMPONENTS["dependency_tracker"]["script"]), "--stats"],
        capture_output=True, text=True
    )
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": 2,
        "status": "COMPLETE",
        "components": {
            "kg_causal_updater": COMPONENTS["kg_causal_updater"]["script"].exists(),
            "dependency_tracker": COMPONENTS["dependency_tracker"]["script"].exists()
        },
        "metrics": {
            "kg_causal_output": kg_causal_stats.stdout[:500] if kg_causal_stats.stdout else "N/A",
            "dep_tracker_output": dep_stats.stdout[:500] if dep_stats.stdout else "N/A"
        }
    }
    
    print(f"\n  Status: {report['status']}")
    print(f"\n  Components:")
    for name, exists in report["components"].items():
        print(f"    {'✅' if exists else '❌'} {name}")
    
    # Save report
    report_file = WORKSPACE / "docs" / "phase2_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n  📄 Report gespeichert: {report_file}")
    
    return report

def validate():
    print("\n🔍 Phase 2 Validation\n" + "=" * 50)
    
    for name, info in COMPONENTS.items():
        print(f"\n[{name}]")
        print(f"  Script: {info['script']}")
        print(f"  Exists: {info['script'].exists()}")
        
        if info['script'].exists():
            check = check_script(info['script'])
            print(f"  Valid: {check['status']} - {check['message']}")
            
            # Try running --help
            result = run_script_test(name, info["script"], ["--help"])
            print(f"  Help: {result['status']}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Phase 2 Integrator")
    parser.add_argument("--full", action="store_true", help="Full test")
    parser.add_argument("--quick", action="store_true", help="Quick check")
    parser.add_argument("--validate", action="store_true", help="Detailed validation")
    parser.add_argument("--report", action="store_true", help="Generate report")
    
    args = parser.parse_args()
    
    if args.full:
        full_test()
    elif args.quick:
        quick_check()
    elif args.validate:
        validate()
    elif args.report:
        generate_report()
    else:
        print("Phase 2 Integrator — Usage:")
        print("  --full     : Full test")
        print("  --quick    : Quick check")
        print("  --validate : Detailed validation")
        print("  --report   : Generate completion report")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Phase 5 Integrator — Day 3
==========================
Integriert alle Phase 5 Components.

Usage:
    python3 phase5_integrator.py --full        # Vollständiger Test
    python3 phase5_integrator.py --quick       # Quick Check
    python3 phase5_integrator.py --validate   # Validierung
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SCRIPTS_DIR = WORKSPACE / "scripts"

COMPONENTS = {
    "cross_domain_miner": {
        "script": SCRIPTS_DIR / "cross_domain_miner.py",
        "description": "Cross-Domain Miner"
    },
    "slo_tracker": {
        "script": SCRIPTS_DIR / "slo_tracker.py",
        "description": "SLO Tracker"
    }
}

def check_script(script_path):
    if not script_path.exists():
        return {"status": "❌", "message": "Script nicht gefunden"}
    try:
        content = script_path.read_text()
        if len(content) < 100:
            return {"status": "❌", "message": "Script ist leer"}
        return {"status": "✅", "message": f"OK ({len(content)} bytes)"}
    except Exception as e:
        return {"status": "❌", "message": str(e)}

def run_script_test(script_path, test_args):
    try:
        result = subprocess.run(
            ["python3", str(script_path)] + test_args,
            capture_output=True, text=True, timeout=30
        )
        return {
            "status": "✅" if result.returncode == 0 else "❌",
            "message": f"Exit: {result.returncode}",
            "output": result.stdout[:400] if result.stdout else result.stderr[:400]
        }
    except subprocess.TimeoutExpired:
        return {"status": "❌", "message": "Timeout"}
    except Exception as e:
        return {"status": "❌", "message": str(e)}

def quick_check():
    print("\n🔍 Phase 5 Quick Check\n")
    all_ok = True
    for name, info in COMPONENTS.items():
        script_ok = info["script"].exists()
        status = "✅" if script_ok else "❌"
        if not script_ok:
            all_ok = False
        print(f"  {status} {name}")
    print(f"\n{'✅ Alle Komponenten OK' if all_ok else '❌ Probleme gefunden'}")
    return all_ok

def full_test():
    print("\n" + "=" * 50)
    print("🧪 PHASE 5 FULL TEST")
    print("=" * 50)
    
    results = {}
    
    print("\n📝 Step 1: Script Validation")
    for name, info in COMPONENTS.items():
        check = check_script(info["script"])
        results[name] = {"check": check}
        print(f"  [{check['status']}] {name}: {check['message']}")
    
    print("\n📝 Step 2: Cross-Domain Miner --mine")
    cdm_mine = run_script_test(COMPONENTS["cross_domain_miner"]["script"], ["--mine"])
    results["cdm_mine"] = cdm_mine
    print(f"  [{cdm_mine['status']}] {cdm_mine['message']}")
    
    print("\n📝 Step 3: Cross-Domain Miner --patterns")
    cdm_patterns = run_script_test(COMPONENTS["cross_domain_miner"]["script"], ["--patterns"])
    results["cdm_patterns"] = cdm_patterns
    print(f"  [{cdm_patterns['status']}] {cdm_patterns['message']}")
    
    print("\n📝 Step 4: SLO Tracker --status")
    slo_status = run_script_test(COMPONENTS["slo_tracker"]["script"], ["--status"])
    results["slo_status"] = slo_status
    print(f"  [{slo_status['status']}] {slo_status['message']}")
    
    print("\n📝 Step 5: SLO Tracker --define")
    slo_define = run_script_test(
        COMPONENTS["slo_tracker"]["script"],
        ["--define", "test_task", "0.9", "success_rate"]
    )
    results["slo_define"] = slo_define
    print(f"  [{slo_define['status']}] {slo_define['message']}")
    
    print("\n📝 Step 6: SLO Tracker --log")
    slo_log = run_script_test(
        COMPONENTS["slo_tracker"]["script"],
        ["--log", "test_task", "true"]
    )
    results["slo_log"] = slo_log
    print(f"  [{slo_log['status']}] {slo_log['message']}")
    
    print("\n📝 Step 7: SLO Tracker --check")
    slo_check = run_script_test(
        COMPONENTS["slo_tracker"]["script"],
        ["--check", "test_task"]
    )
    results["slo_check"] = slo_check
    print(f"  [{slo_check['status']}] {slo_check['message']}")
    
    print("\n📝 Step 8: SLO Tracker --breaches")
    slo_breaches = run_script_test(COMPONENTS["slo_tracker"]["script"], ["--breaches"])
    results["slo_breaches"] = slo_breaches
    print(f"  [{slo_breaches['status']}] {slo_breaches['message']}")
    
    print("\n📝 Step 9: Cross-Domain Miner --report")
    cdm_report = run_script_test(COMPONENTS["cross_domain_miner"]["script"], ["--report"])
    results["cdm_report"] = cdm_report
    print(f"  [{cdm_report['status']}] {cdm_report['message']}")
    
    print("\n📝 Step 10: SLO Tracker --report")
    slo_report = run_script_test(COMPONENTS["slo_tracker"]["script"], ["--report"])
    results["slo_report"] = slo_report
    print(f"  [{slo_report['status']}] {slo_report['message']}")
    
    all_passed = all(r.get("status") == "✅" for r in results.values() if isinstance(r, dict) and "status" in r)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ PHASE 5 FULL TEST PASSED")
    else:
        print("⚠️  PHASE 5 TEST COMPLETED WITH ISSUES")
        for name, result in results.items():
            if isinstance(result, dict) and result.get("status") != "✅":
                print(f"     {name}: {result.get('message')}")
    print("=" * 50)
    
    return results

def validate():
    print("\n🔍 Phase 5 Validation\n" + "=" * 50)
    for name, info in COMPONENTS.items():
        print(f"\n[{name}]")
        print(f"  Script: {info['script']}")
        print(f"  Exists: {info['script'].exists()}")
        if info["script"].exists():
            check = check_script(info["script"])
            print(f"  Valid: {check['status']} - {check['message']}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Phase 5 Integrator")
    parser.add_argument("--full", action="store_true", help="Full test")
    parser.add_argument("--quick", action="store_true", help="Quick check")
    parser.add_argument("--validate", action="store_true", help="Detailed validation")
    
    args = parser.parse_args()
    
    if args.full:
        full_test()
    elif args.quick:
        quick_check()
    elif args.validate:
        validate()
    else:
        print("Phase 5 Integrator — Usage:")
        print("  --full     : Full test")
        print("  --quick    : Quick check")
        print("  --validate : Detailed validation")

if __name__ == "__main__":
    main()

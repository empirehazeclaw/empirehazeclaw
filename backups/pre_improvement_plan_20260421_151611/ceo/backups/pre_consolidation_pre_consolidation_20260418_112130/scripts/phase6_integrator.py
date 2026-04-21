#!/usr/bin/env python3
"""
Phase 6 Integrator — Day 3
==========================
Integriert alle Phase 6 Components (SRE Culture).

Usage:
    python3 phase6_integrator.py --full        # Vollständiger Test
    python3 phase6_integrator.py --quick       # Quick Check
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
    "sre_culture": {
        "script": SCRIPTS_DIR / "sre_culture.py",
        "description": "SRE Culture - Blameless post-mortems, incident learning"
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
    print("\n🔍 Phase 6 Quick Check\n")
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
    print("🧪 PHASE 6 FULL TEST (SRE Culture)")
    print("=" * 50)
    
    results = {}
    
    print("\n📝 Step 1: Script Validation")
    for name, info in COMPONENTS.items():
        check = check_script(info["script"])
        results[name] = {"check": check}
        print(f"  [{check['status']}] {name}: {check['message']}")
    
    print("\n📝 Step 2: Pre-Mortem")
    pre_mortem = run_script_test(
        COMPONENTS["sre_culture"]["script"],
        ["--pre-mortem", "Deploy new learning algorithm"]
    )
    results["pre_mortem"] = pre_mortem
    print(f"  [{pre_mortem['status']}] {pre_mortem['message']}")
    
    print("\n📝 Step 3: Log Incident")
    incident = run_script_test(
        COMPONENTS["sre_culture"]["script"],
        ["--incident", "API timeout in production", "--severity", "high", "--category", "performance"]
    )
    results["incident"] = incident
    print(f"  [{incident['status']}] {incident['message']}")
    
    print("\n📝 Step 4: Post-Mortem")
    postmortem = run_script_test(
        COMPONENTS["sre_culture"]["script"],
        ["--post-mortem", "INC-0001"]
    )
    results["postmortem"] = postmortem
    print(f"  [{postmortem['status']}] {postmortem['message']}")
    
    print("\n📝 Step 5: SLO Breach Learning")
    slo_breach = run_script_test(
        COMPONENTS["sre_culture"]["script"],
        ["--slo-breach", "fast_task", "0.85", "0.95"]
    )
    results["slo_breach"] = slo_breach
    print(f"  [{slo_breach['status']}] {slo_breach['message']}")
    
    print("\n📝 Step 6: Blameless Analysis")
    blameless = run_script_test(
        COMPONENTS["sre_culture"]["script"],
        ["--blameless", "INC-0001"]
    )
    results["blameless"] = blameless
    print(f"  [{blameless['status']}] {blameless['message']}")
    
    print("\n📝 Step 7: SRE Report")
    report = run_script_test(
        COMPONENTS["sre_culture"]["script"],
        ["--report"]
    )
    results["report"] = report
    print(f"  [{report['status']}] {report['message']}")
    
    all_passed = all(r.get("status") == "✅" for r in results.values() if isinstance(r, dict) and "status" in r)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ PHASE 6 FULL TEST PASSED")
    else:
        print("⚠️  PHASE 6 TEST COMPLETED WITH ISSUES")
        for name, result in results.items():
            if isinstance(result, dict) and result.get("status") != "✅":
                print(f"     {name}: {result.get('message')}")
    print("=" * 50)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Phase 6 Integrator")
    parser.add_argument("--full", action="store_true", help="Full test")
    parser.add_argument("--quick", action="store_true", help="Quick check")
    
    args = parser.parse_args()
    
    if args.full:
        full_test()
    elif args.quick:
        quick_check()
    else:
        print("Phase 6 Integrator — Usage:")
        print("  --full     : Full test")
        print("  --quick    : Quick check")

if __name__ == "__main__":
    main()

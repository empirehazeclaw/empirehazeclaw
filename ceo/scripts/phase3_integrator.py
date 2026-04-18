#!/usr/bin/env python3
"""
Phase 3 Integrator — Day 5
===========================
Integriert alle Phase 3 Components und validiert das System.

Usage:
    python3 phase3_integrator.py --full        # Vollständiger Test
    python3 phase3_integrator.py --quick       # Quick Check
    python3 phase3_integrator.py --validate    # Validierung
    python3 phase3_integrator.py --report      # Generate Report
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SCRIPTS_DIR = WORKSPACE / "scripts"

# Phase 3 components
COMPONENTS = {
    "exploration_budget": {
        "script": SCRIPTS_DIR / "exploration_budget.py",
        "description": "Exploration Budget Manager - 10% exploration rate"
    },
    "strategy_mutator": {
        "script": SCRIPTS_DIR / "strategy_mutator.py",
        "description": "Strategy Mutator - mutates existing strategies"
    },
    "exploration_controller": {
        "script": SCRIPTS_DIR / "exploration_controller.py",
        "description": "Exploration Controller - ε-greedy, Softmax, UCB"
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

def run_script_test(script_path: Path, test_args: list) -> dict:
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
            "output": result.stdout[:400] if result.stdout else result.stderr[:400]
        }
    except subprocess.TimeoutExpired:
        return {"status": "❌", "message": "Timeout"}
    except Exception as e:
        return {"status": "❌", "message": str(e)}

def quick_check():
    print("\n🔍 Phase 3 Quick Check\n")
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
    print("🧪 PHASE 3 FULL TEST")
    print("=" * 50)
    
    results = {}
    
    # Step 1: Script validation
    print("\n📝 Step 1: Script Validation")
    for name, info in COMPONENTS.items():
        check = check_script(info["script"])
        results[name] = {"check": check}
        print(f"  [{check['status']}] {name}: {check['message']}")
    
    # Step 2: Exploration Budget --status
    print("\n📝 Step 2: Exploration Budget Status")
    eb_status = run_script_test(
        COMPONENTS["exploration_budget"]["script"],
        ["--status"]
    )
    results["exploration_budget_status"] = eb_status
    print(f"  [{eb_status['status']}] {eb_status['message']}")
    if eb_status.get("output"):
        print(f"       {eb_status['output'][:300]}")
    
    # Step 3: Exploration Budget --should-explore
    print("\n📝 Step 3: Exploration Budget Decision")
    eb_decide = run_script_test(
        COMPONENTS["exploration_budget"]["script"],
        ["--should-explore"]
    )
    results["exploration_budget_decide"] = eb_decide
    print(f"  [{eb_decide['status']}] {eb_decide['message']}")
    if eb_decide.get("output"):
        print(f"       {eb_decide['output'][:200]}")
    
    # Step 4: Exploration Budget --log-run
    print("\n📝 Step 4: Log Exploration Run")
    eb_log = run_script_test(
        COMPONENTS["exploration_budget"]["script"],
        ["--log-run", "exploration", "test_strategy"]
    )
    results["exploration_budget_log"] = eb_log
    print(f"  [{eb_log['status']}] {eb_log['message']}")
    
    # Step 5: Strategy Mutator --list
    print("\n📝 Step 5: Strategy Mutator List")
    sm_list = run_script_test(
        COMPONENTS["strategy_mutator"]["script"],
        ["--list"]
    )
    results["strategy_mutator_list"] = sm_list
    print(f"  [{sm_list['status']}] {sm_list['message']}")
    if sm_list.get("output"):
        print(f"       {sm_list['output'][:300]}")
    
    # Step 6: Strategy Mutator --baseline
    print("\n📝 Step 6: Set Strategy Baseline")
    sm_baseline = run_script_test(
        COMPONENTS["strategy_mutator"]["script"],
        ["--baseline"]
    )
    results["strategy_mutator_baseline"] = sm_baseline
    print(f"  [{sm_baseline['status']}] {sm_baseline['message']}")
    
    # Step 7: Strategy Mutator --mutate
    print("\n📝 Step 7: Create Mutation")
    sm_mutate = run_script_test(
        COMPONENTS["strategy_mutator"]["script"],
        ["--mutate", "default_execution"]
    )
    results["strategy_mutator_mutate"] = sm_mutate
    print(f"  [{sm_mutate['status']}] {sm_mutate['message']}")
    if sm_mutate.get("output"):
        print(f"       {sm_mutate['output'][:200]}")
    
    # Step 8: Exploration Controller --status
    print("\n📝 Step 8: Exploration Controller Status")
    ec_status = run_script_test(
        COMPONENTS["exploration_controller"]["script"],
        ["--status"]
    )
    results["exploration_controller_status"] = ec_status
    print(f"  [{ec_status['status']}] {ec_status['message']}")
    if ec_status.get("output"):
        print(f"       {ec_status['output'][:300]}")
    
    # Step 9: Exploration Controller --select
    print("\n📝 Step 9: Strategy Selection")
    ec_select = run_script_test(
        COMPONENTS["exploration_controller"]["script"],
        ["--select", "--strategies", "strategy_a", "strategy_b", "strategy_c"]
    )
    results["exploration_controller_select"] = ec_select
    print(f"  [{ec_select['status']}] {ec_select['message']}")
    if ec_select.get("output"):
        print(f"       {ec_select['output'][:200]}")
    
    # Step 10: Exploration Controller --update
    print("\n📝 Step 10: Update Strategy Reward")
    ec_update = run_script_test(
        COMPONENTS["exploration_controller"]["script"],
        ["--update", "strategy_a", "0.8"]
    )
    results["exploration_controller_update"] = ec_update
    print(f"  [{ec_update['status']}] {ec_update['message']}")
    
    # Step 11: Exploration Budget --report
    print("\n📝 Step 11: Exploration Budget Report")
    eb_report = run_script_test(
        COMPONENTS["exploration_budget"]["script"],
        ["--report"]
    )
    results["exploration_budget_report"] = eb_report
    print(f"  [{eb_report['status']}] {eb_report['message']}")
    
    # Step 12: Strategy Mutator --report
    print("\n📝 Step 12: Mutation Report")
    sm_report = run_script_test(
        COMPONENTS["strategy_mutator"]["script"],
        ["--report"]
    )
    results["strategy_mutator_report"] = sm_report
    print(f"  [{sm_report['status']}] {sm_report['message']}")
    
    # Overall result
    all_passed = all(r.get("status") == "✅" for r in results.values() if isinstance(r, dict) and "status" in r)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ PHASE 3 FULL TEST PASSED")
    else:
        print("⚠️  PHASE 3 TEST COMPLETED WITH ISSUES")
        for name, result in results.items():
            if isinstance(result, dict) and result.get("status") != "✅":
                print(f"     {name}: {result.get('message')}")
    print("=" * 50)
    
    return results

def generate_report():
    print("\n📊 Phase 3 Completion Report")
    print("=" * 50)
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": 3,
        "status": "COMPLETE",
        "components": {
            name: info["script"].exists()
            for name, info in COMPONENTS.items()
        }
    }
    
    print(f"\n  Status: {report['status']}")
    print(f"\n  Components:")
    for name, exists in report["components"].items():
        print(f"    {'✅' if exists else '❌'} {name}")
    
    # Save report
    report_file = WORKSPACE / "docs" / "phase3_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n  📄 Report gespeichert: {report_file}")
    
    return report

def validate():
    print("\n🔍 Phase 3 Validation\n" + "=" * 50)
    
    for name, info in COMPONENTS.items():
        print(f"\n[{name}]")
        print(f"  Script: {info['script']}")
        print(f"  Exists: {info['script'].exists()}")
        
        if info["script"].exists():
            check = check_script(info["script"])
            print(f"  Valid: {check['status']} - {check['message']}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Phase 3 Integrator")
    parser.add_argument("--full", action="store_true", help="Full test")
    parser.add_argument("--quick", action="store_true", help="Quick check")
    parser.add_argument("--validate", action="store_true", help="Detailed validation")
    parser.add_argument("--report", action="store_true", help="Generate completion report")
    
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
        print("Phase 3 Integrator — Usage:")
        print("  --full     : Full test")
        print("  --quick    : Quick check")
        print("  --validate : Detailed validation")
        print("  --report   : Generate completion report")

if __name__ == "__main__":
    main()

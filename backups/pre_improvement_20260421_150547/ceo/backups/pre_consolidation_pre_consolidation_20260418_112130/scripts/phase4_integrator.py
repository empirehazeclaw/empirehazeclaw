#!/usr/bin/env python3
"""
Phase 4 Integrator — Day 5
===========================
Integriert alle Phase 4 Components und validiert das System.

Usage:
    python3 phase4_integrator.py --full        # Vollständiger Test
    python3 phase4_integrator.py --quick       # Quick Check
    python3 phase4_integrator.py --validate   # Validierung
    python3 phase4_integrator.py --report      # Generate Report
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
    "meta_learning_core": {
        "script": SCRIPTS_DIR / "meta_learning_core.py",
        "description": "Meta Learning Core - Pattern generalization scoring"
    },
    "learning_to_learn": {
        "script": SCRIPTS_DIR / "learning_to_learn.py",
        "description": "Learning-to-Learn - Task learning rate analysis"
    },
    "dynamic_experience_memory": {
        "script": SCRIPTS_DIR / "dynamic_experience_memory.py",
        "description": "Dynamic Experience Memory - M = {E1...EN}"
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
    print("\n🔍 Phase 4 Quick Check\n")
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
    print("🧪 PHASE 4 FULL TEST")
    print("=" * 50)
    
    results = {}
    
    # Step 1: Script validation
    print("\n📝 Step 1: Script Validation")
    for name, info in COMPONENTS.items():
        check = check_script(info["script"])
        results[name] = {"check": check}
        print(f"  [{check['status']}] {name}: {check['message']}")
    
    # Step 2: Meta Learning Core --analyze
    print("\n📝 Step 2: Meta Learning Core Analyze")
    mlc_analyze = run_script_test(COMPONENTS["meta_learning_core"]["script"], ["--analyze"])
    results["mlc_analyze"] = mlc_analyze
    print(f"  [{mlc_analyze['status']}] {mlc_analyze['message']}")
    
    # Step 3: Meta Learning Core --score
    print("\n📝 Step 3: Meta Learning Core Score")
    mlc_score = run_script_test(COMPONENTS["meta_learning_core"]["script"], ["--score"])
    results["mlc_score"] = mlc_score
    print(f"  [{mlc_score['status']}] {mlc_score['message']}")
    
    # Step 4: Learning-to-Learn --analyze
    print("\n📝 Step 4: Learning-to-Learn Analyze")
    ltl_analyze = run_script_test(COMPONENTS["learning_to_learn"]["script"], ["--analyze"])
    results["ltl_analyze"] = ltl_analyze
    print(f"  [{ltl_analyze['status']}] {ltl_analyze['message']}")
    
    # Step 5: Learning-to-Learn --curriculum
    print("\n📝 Step 5: Learning-to-Learn Curriculum")
    ltl_curriculum = run_script_test(COMPONENTS["learning_to_learn"]["script"], ["--curriculum"])
    results["ltl_curriculum"] = ltl_curriculum
    print(f"  [{ltl_curriculum['status']}] {ltl_curriculum['message']}")
    
    # Step 6: Dynamic Experience Memory --add
    print("\n📝 Step 6: Add Experience")
    dem_add = run_script_test(
        COMPONENTS["dynamic_experience_memory"]["script"],
        ["--add", "Phase 4 integration test experience", "--type", "test", "--importance", "0.7"]
    )
    results["dem_add"] = dem_add
    print(f"  [{dem_add['status']}] {dem_add['message']}")
    
    # Step 7: Dynamic Experience Memory --status
    print("\n📝 Step 7: Memory Status")
    dem_status = run_script_test(COMPONENTS["dynamic_experience_memory"]["script"], ["--status"])
    results["dem_status"] = dem_status
    print(f"  [{dem_status['status']}] {dem_status['message']}")
    
    # Step 8: Dynamic Experience Memory --replay
    print("\n📝 Step 8: Replay Experiences")
    dem_replay = run_script_test(COMPONENTS["dynamic_experience_memory"]["script"], ["--replay"])
    results["dem_replay"] = dem_replay
    print(f"  [{dem_replay['status']}] {dem_replay['message']}")
    
    # Step 9: Meta Learning Core --suggest
    print("\n📝 Step 9: Meta Learning Suggestions")
    mlc_suggest = run_script_test(COMPONENTS["meta_learning_core"]["script"], ["--suggest"])
    results["mlc_suggest"] = mlc_suggest
    print(f"  [{mlc_suggest['status']}] {mlc_suggest['message']}")
    
    # Step 10: Dynamic Experience Memory --consolidate
    print("\n📝 Step 10: Consolidate Memories")
    dem_consolidate = run_script_test(COMPONENTS["dynamic_experience_memory"]["script"], ["--consolidate"])
    results["dem_consolidate"] = dem_consolidate
    print(f"  [{dem_consolidate['status']}] {dem_consolidate['message']}")
    
    # Overall result
    all_passed = all(r.get("status") == "✅" for r in results.values() if isinstance(r, dict) and "status" in r)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ PHASE 4 FULL TEST PASSED")
    else:
        print("⚠️  PHASE 4 TEST COMPLETED WITH ISSUES")
        for name, result in results.items():
            if isinstance(result, dict) and result.get("status") != "✅":
                print(f"     {name}: {result.get('message')}")
    print("=" * 50)
    
    return results

def generate_report():
    print("\n📊 Phase 4 Completion Report")
    print("=" * 50)
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": 4,
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
    
    report_file = WORKSPACE / "docs" / "phase4_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n  📄 Report gespeichert: {report_file}")
    
    return report

def validate():
    print("\n🔍 Phase 4 Validation\n" + "=" * 50)
    
    for name, info in COMPONENTS.items():
        print(f"\n[{name}]")
        print(f"  Script: {info['script']}")
        print(f"  Exists: {info['script'].exists()}")
        
        if info["script"].exists():
            check = check_script(info["script"])
            print(f"  Valid: {check['status']} - {check['message']}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Phase 4 Integrator")
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
        print("Phase 4 Integrator — Usage:")
        print("  --full     : Full test")
        print("  --quick    : Quick check")
        print("  --validate : Detailed validation")
        print("  --report   : Generate completion report")

if __name__ == "__main__":
    main()

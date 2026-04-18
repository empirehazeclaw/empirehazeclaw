#!/usr/bin/env python3
"""
Phase 1 Integrator — Day 5
==========================
Integriert alle Phase 1 Components und validiert das System.

Usage:
    python3 phase1_integrator.py --full        # Vollständiger Test
    python3 phase1_integrator.py --quick       # Quick Check
    python3 phase1_integrator.py --validate    # Validierung
    python3 phase1_integrator.py --report      # Generate Report
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SCRIPTS_DIR = WORKSPACE / "scripts"
MEMORY_DIR = WORKSPACE / "memory"

# Phase 1 components
COMPONENTS = {
    "failure_logger": {
        "script": SCRIPTS_DIR / "failure_logger.py",
        "data": MEMORY_DIR / "failures",
        "description": "Failure Logger - erfasst alle Failures"
    },
    "postmortem_generator": {
        "script": SCRIPTS_DIR / "postmortem_generator.py",
        "data": MEMORY_DIR / "evaluations" / "postmortems",
        "description": "Post-Mortem Generator"
    },
    "contrastive_analyzer": {
        "script": SCRIPTS_DIR / "contrastive_analyzer.py",
        "data": MEMORY_DIR / "evaluations" / "contrastive",
        "description": "Contrastive Analyzer - Success/Failure Paare"
    },
    "causal_pattern_miner": {
        "script": SCRIPTS_DIR / "causal_pattern_miner.py",
        "data": MEMORY_DIR / "evaluations" / "causal",
        "description": "Causal Pattern Miner"
    }
}

def check_script(script_path: Path) -> dict:
    """Check if a script exists and is valid."""
    if not script_path.exists():
        return {"status": "❌", "message": "Script nicht gefunden"}
    
    try:
        content = script_path.read_text()
        if len(content) < 100:
            return {"status": "❌", "message": "Script ist leer"}
        if "__main__" not in content:
            return {"status": "⚠️", "message": "Kein __main__ block"}
        return {"status": "✅", "message": f"OK ({len(content)} bytes)"}
    except Exception as e:
        return {"status": "❌", "message": str(e)}

def check_data_dir(data_path: Path) -> dict:
    """Check if a data directory exists with content."""
    if not data_path.exists():
        return {"status": "⚠️", "message": "Data dir fehlt (wird bei erstem Run erstellt)", "count": 0}
    
    files = list(data_path.rglob("*"))
    json_files = [f for f in files if f.suffix == ".json"]
    md_files = [f for f in files if f.suffix == ".md"]
    
    return {
        "status": "✅",
        "message": f"{len(files)} files ({len(json_files)} JSON, {len(md_files)} MD)",
        "count": len(files),
        "files": [f.name for f in files[:5]]  # First 5
    }

def run_script_test(script_name: str, script_path: Path) -> dict:
    """Test a script with --stats or --help."""
    import subprocess
    
    if script_name == "failure_logger":
        test_args = ["--stats"]
    elif script_name == "postmortem_generator":
        test_args = ["--list"]
    elif script_name == "contrastive_analyzer":
        test_args = ["--stats"]
    elif script_name == "causal_pattern_miner":
        test_args = ["--stats"]
    else:
        test_args = ["--help"]
    
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
            "output": result.stdout[:200] if result.stdout else result.stderr[:200]
        }
    except subprocess.TimeoutExpired:
        return {"status": "❌", "message": "Timeout"}
    except Exception as e:
        return {"status": "❌", "message": str(e)}

def validate_integration() -> dict:
    """Validate Phase 1 integration."""
    print("\n🔍 Phase 1 Integration Validation\n" + "=" * 50)
    
    results = {}
    
    # 1. Check all components
    print("\n📦 Component Check:\n")
    for name, info in COMPONENTS.items():
        script_result = check_script(info["script"])
        data_result = check_data_dir(info["data"])
        
        results[name] = {
            "script": script_result,
            "data": data_result
        }
        
        print(f"  [{script_result['status']}] Script: {name}")
        print(f"       {script_result['message']}")
        print(f"  [{data_result['status']}] Data: {name}")
        print(f"       {data_result['message']}")
        if data_result.get("files"):
            print(f"       Files: {', '.join(data_result.get('files', []))}")
        print()
    
    # 2. Check cron job
    print("\n⏰ Cron Check:")
    try:
        from openclaw_core import cron
        jobs = cron.list_jobs() if hasattr(cron, 'list_jobs') else []
        failure_logger_cron = [j for j in jobs if "Failure Logger" in j.get("name", "")]
        if failure_logger_cron:
            print(f"  ✅ Cron 'Failure Logger' existiert")
            results["cron"] = {"status": "✅", "message": "Cron job found"}
        else:
            print(f"  ⚠️  Cron 'Failure Logger' nicht in Liste")
            results["cron"] = {"status": "⚠️", "message": "Cron not found"}
    except Exception as e:
        print(f"  ⚠️  Cron Check fehlgeschlagen: {e}")
        results["cron"] = {"status": "⚠️", "message": str(e)}
    
    # 3. Run script tests
    print("\n🧪 Script Tests:\n")
    for name, info in COMPONENTS.items():
        test_result = run_script_test(name, info["script"])
        results[name]["test"] = test_result
        print(f"  [{test_result['status']}] {name}")
        print(f"       {test_result['message']}")
        if test_result.get("output"):
            print(f"       {test_result['output'][:100]}")
    
    # 4. Data flow check
    print("\n🔄 Data Flow Check:")
    
    # Check if failure_logger creates data that postmortem can read
    failure_log = MEMORY_DIR / "failures" / "failure_log.json"
    if failure_log.exists():
        try:
            data = json.loads(failure_log.read_text())
            failure_count = len(data.get("failures", []))
            print(f"  ✅ Failure Log: {failure_count} Failures")
            results["data_flow"] = {"status": "✅", "failures": failure_count}
        except:
            print(f"  ❌ Failure Log ist corrupt")
            results["data_flow"] = {"status": "❌"}
    else:
        print(f"  ⚠️  Failure Log existiert noch nicht (normal vor erstem Failure)")
        results["data_flow"] = {"status": "⚠️", "message": "No failures yet"}
    
    return results

def generate_report() -> dict:
    """Generate Phase 1 completion report."""
    print("\n📊 Phase 1 Completion Report")
    print("=" * 50)
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "components": {},
        "metrics": {},
        "status": "unknown"
    }
    
    # Collect metrics from each component
    failure_log = MEMORY_DIR / "failures" / "failure_log.json"
    if failure_log.exists():
        data = json.loads(failure_log.read_text())
        report["metrics"]["total_failures"] = len(data.get("failures", []))
        report["metrics"]["by_severity"] = data.get("failures", [{}])[0].get("severity", "N/A") if data.get("failures") else "N/A"
    
    pm_index = MEMORY_DIR / "evaluations" / "postmortems" / "index.json"
    if pm_index.exists():
        pm_data = json.loads(pm_index.read_text())
        report["metrics"]["total_postmortems"] = len(pm_data.get("postmortems", []))
    
    contrast_pairs = MEMORY_DIR / "evaluations" / "contrastive" / "contrast_pairs.json"
    if contrast_pairs.exists():
        cp_data = json.loads(contrast_pairs.read_text())
        report["metrics"]["contrastive_pairs"] = len(cp_data.get("pairs", []))
    
    causal_chains = MEMORY_DIR / "evaluations" / "causal" / "causal_chains.json"
    if causal_chains.exists():
        cc_data = json.loads(causal_chains.read_text())
        report["metrics"]["causal_chains"] = len(cc_data.get("chains", []))
    
    # Overall status
    all_components_exist = all(
        COMPONENTS[c]["script"].exists() for c in COMPONENTS
    )
    
    report["status"] = "✅ COMPLETE" if all_components_exist else "⚠️ INCOMPLETE"
    
    print(f"\n  Status: {report['status']}")
    print(f"\n  Metrics:")
    for metric, value in report["metrics"].items():
        print(f"    {metric}: {value}")
    
    print(f"\n  Components:")
    for name in COMPONENTS:
        exists = COMPONENTS[name]["script"].exists()
        print(f"    {'✅' if exists else '❌'} {name}")
    
    # Save report
    report_file = WORKSPACE / "docs" / "phase1_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n  📄 Report gespeichert: {report_file}")
    
    return report

def full_test():
    """Run full Phase 1 test."""
    print("\n" + "=" * 50)
    print("🧪 PHASE 1 FULL TEST")
    print("=" * 50)
    
    # Step 1: Create test failure
    print("\n📝 Step 1: Test Failure erstellen...")
    import subprocess
    
    test_failure = subprocess.run([
        "python3", str(COMPONENTS["failure_logger"]["script"]),
        "--log", "INTEGRATION TEST FAILURE - Phase 1 Validierung",
        "--severity", "low",
        "--cause", "design_gap",
        "--tags", "test,integration,phase1"
    ], capture_output=True, text=True)
    
    if test_failure.returncode == 0:
        print("  ✅ Test Failure erstellt")
    else:
        print(f"  ⚠️  {test_failure.stderr[:100]}")
    
    # Step 2: Generate Post-Mortem
    print("\n📝 Step 2: Post-Mortem generieren...")
    pm_gen = subprocess.run([
        "python3", str(COMPONENTS["postmortem_generator"]["script"]),
        "--auto", "--since", "1"
    ], capture_output=True, text=True)
    
    if pm_gen.returncode == 0:
        print("  ✅ Post-Mortems generiert")
        print(f"     {pm_gen.stdout[:200]}")
    else:
        print(f"  ⚠️  {pm_gen.stderr[:100]}")
    
    # Step 3: Mine contrastive pairs
    print("\n📝 Step 3: Contrastive pairs mined...")
    contrast = subprocess.run([
        "python3", str(COMPONENTS["contrastive_analyzer"]["script"]),
        "--mine"
    ], capture_output=True, text=True)
    
    if contrast.returncode == 0:
        print("  ✅ Contrastive pairs mined")
        print(f"     {contrast.stdout[:200]}")
    else:
        print(f"  ⚠️  {contrast.stderr[:100]}")
    
    # Step 4: Mine causal patterns
    print("\n📝 Step 4: Causal patterns mined...")
    causal = subprocess.run([
        "python3", str(COMPONENTS["causal_pattern_miner"]["script"]),
        "--mine"
    ], capture_output=True, text=True)
    
    if causal.returncode == 0:
        print("  ✅ Causal patterns mined")
        print(f"     {causal.stdout[:200]}")
    else:
        print(f"  ⚠️  {causal.stderr[:100]}")
    
    # Step 5: Resolve test failure
    print("\n📝 Step 5: Test Failure auflösen...")
    resolve = subprocess.run([
        "python3", str(COMPONENTS["failure_logger"]["script"]),
        "--resolve", "1", "--resolve-text", "Integration Test - resolved"
    ], capture_output=True, text=True)
    
    if resolve.returncode == 0:
        print("  ✅ Test Failure resolved")
    else:
        print(f"  ⚠️  {resolve.stderr[:100]}")
    
    # Step 6: Generate report
    report = generate_report()
    
    print("\n" + "=" * 50)
    print("🧪 PHASE 1 FULL TEST COMPLETE")
    print("=" * 50)
    
    return report

def quick_check():
    """Quick validation check."""
    print("\n🔍 Phase 1 Quick Check\n")
    
    all_ok = True
    for name, info in COMPONENTS.items():
        script_ok = info["script"].exists()
        data_ok = info["data"].exists()
        
        if script_ok and data_ok:
            status = "✅"
        elif script_ok:
            status = "⚠️"
        else:
            status = "❌"
            all_ok = False
        
        print(f"  {status} {name}")
    
    print(f"\n{'✅ Alle Komponenten OK' if all_ok else '❌ Probleme gefunden'}")
    
    return all_ok

def main():
    parser = argparse.ArgumentParser(description="Phase 1 Integrator")
    parser.add_argument("--full", action="store_true", help="Full test including data flow")
    parser.add_argument("--quick", action="store_true", help="Quick component check")
    parser.add_argument("--validate", action="store_true", help="Detailed validation")
    parser.add_argument("--report", action="store_true", help="Generate report")
    
    args = parser.parse_args()
    
    if args.full:
        full_test()
    elif args.quick:
        quick_check()
    elif args.validate:
        validate_integration()
    elif args.report:
        generate_report()
    else:
        print("Phase 1 Integrator — Usage:")
        print("  --full     : Full test with data flow")
        print("  --quick    : Quick component check")
        print("  --validate : Detailed validation")
        print("  --report   : Generate completion report")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Sir HazeClaw Simple Test Framework
Einfaches Test-Framework für Scripts.

Usage:
    python3 test_framework.py
    python3 test_framework.py --run morning_brief
    python3 test_framework.py --list
"""

import sys
import importlib.util
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

# Test definitions
TESTS = {
    'morning_brief': {
        'script': 'morning_brief.py',
        'type': 'import_no_args',
        'test_func': 'generate_brief',
        'description': 'Morning Brief Generator'
    },
    'health_monitor': {
        'script': 'health_monitor.py',
        'type': 'import_no_args',
        'test_func': 'generate_report',
        'description': 'Health Monitor'
    },
    'self_check': {
        'script': 'self_check.py',
        'type': 'import_no_args',
        'test_func': 'generate_report',
        'description': 'Self Check'
    },
    'cron_monitor': {
        'script': 'cron_monitor.py',
        'type': 'import_with_args',
        'test_func': 'generate_report',
        'test_args': ('text',),
        'description': 'Cron Monitor'
    },
    'daily_summary': {
        'script': 'daily_summary.py',
        'type': 'import_no_args',
        'test_func': 'generate_summary',
        'description': 'Daily Summary'
    },
    'evening_summary': {
        'script': 'evening_summary.py',
        'type': 'import_no_args',
        'test_func': 'generate_summary',
        'description': 'Evening Summary'
    },
    'quality_metrics': {
        'script': 'quality_metrics.py',
        'type': 'import_no_args',
        'test_func': 'calculate_metrics',
        'description': 'Quality Metrics'
    },
    'memory_hybrid_search': {
        'script': 'memory_hybrid_search.py',
        'type': 'import_with_args',
        'test_func': 'hybrid_search',
        'test_args': ('quality',),
        'description': 'Memory Hybrid Search'
    },
    'auto_backup': {
        'script': 'auto_backup.py',
        'type': 'import_no_args',
        'test_func': 'get_backup_stats',
        'description': 'Auto Backup'
    },
    'auto_doc': {
        'script': 'auto_doc.py',
        'type': 'import_with_args',
        'test_func': 'get_script_info',
        'test_args': (SCRIPTS_DIR / 'test_framework.py',),
        'description': 'Auto Documentation'
    },
    'self_eval': {
        'script': 'self_eval.py',
        'type': 'import_no_args',
        'test_func': 'calculate_scores',
        'description': 'Self Evaluation'
    },
}

def load_script(script_name):
    """Lädt ein Script als Module."""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        return None, f"Script not found: {script_name}"
    
    spec = importlib.util.spec_from_file_location("test_module", script_path)
    if not spec or not spec.loader:
        return None, "Failed to load spec"
    
    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = module
        spec.loader.exec_module(module)
        return module, None
    except Exception as e:
        return None, str(e)

def run_test(test_name, test_def):
    """Führt einen einzelnen Test aus."""
    print(f"\n{'='*50}")
    print(f"🧪 Test: {test_def['description']}")
    print(f"   Script: {test_def['script']}")
    print(f"{'='*50}")
    
    script_path = SCRIPTS_DIR / test_def['script']
    if not script_path.exists():
        print(f"  ❌ FAIL: Script not found")
        return False, "Script not found"
    
    # Load script
    module, error = load_script(test_def['script'])
    if error:
        print(f"  ❌ FAIL: {error}")
        return False, error
    
    # Get test function
    test_func_name = test_def.get('test_func')
    if not test_func_name:
        print(f"  ⚠️  No test function defined")
        return True, "No test"
    
    if not hasattr(module, test_func_name):
        print(f"  ❌ FAIL: Function '{test_func_name}' not found")
        return False, f"Function not found: {test_func_name}"
    
    test_func = getattr(module, test_func_name)
    
    # Run test
    try:
        test_type = test_def['type']
        
        if test_type == 'import_no_args':
            result = test_func()
        elif test_type == 'import_with_args':
            args = test_def.get('test_args', ())
            kwargs = test_def.get('test_kwargs', {})
            result = test_func(*args, **kwargs)
        else:
            print(f"  ⚠️  Unknown test type: {test_type}")
            return True, "Unknown type"
        
        # Handle tuple returns (report, exit_code)
        if isinstance(result, tuple):
            result = result[0]  # Take the first element (the report/string)
        
        if result is None:
            print(f"  ❌ FAIL: Function returned None")
            return False, "Returned None"
        
        # Check result based on function
        if 'report' in test_func_name or 'summary' in test_func_name or 'generate' in test_func_name:
            if isinstance(result, str) and len(result) > 10:
                print(f"  ✅ PASS: Generated {len(result)} chars")
                return True, None
            elif isinstance(result, dict):
                print(f"  ✅ PASS: Returned dict with {len(result)} keys")
                return True, None
        elif 'metrics' in test_func_name or 'calculate' in test_func_name:
            if isinstance(result, dict):
                print(f"  ✅ PASS: Returned {len(result)} metrics")
                return True, None
        elif 'search' in test_func_name:
            if isinstance(result, list):
                print(f"  ✅ PASS: Returned {len(result)} results")
                return True, None
        elif 'stats' in test_func_name:
            if isinstance(result, dict):
                print(f"  ✅ PASS: Returned dict with {len(result)} keys")
                return True, None
        else:
            print(f"  ✅ PASS: Function executed successfully")
            print(f"     Result type: {type(result).__name__}")
            return True, None
        
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False, str(e)

def run_all_tests():
    """Führt alle Tests aus."""
    results = []
    
    print("🧪 Sir HazeClaw Test Suite")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   {len(TESTS)} tests")
    
    passed = 0
    failed = 0
    
    for test_name, test_def in sorted(TESTS.items()):
        ok, error = run_test(test_name, test_def)
        if ok:
            passed += 1
            results.append((test_name, 'PASS', None))
        else:
            failed += 1
            results.append((test_name, 'FAIL', error))
    
    # Summary
    print()
    print("=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"   Total:  {len(results)}")
    print(f"   Passed: {passed} ✅")
    print(f"   Failed: {failed} ❌")
    print()
    
    if failed > 0:
        print("   Failed tests:")
        for name, status, error in results:
            if status == 'FAIL':
                print(f"   - {name}: {error}")
    
    return passed, failed

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sir HazeClaw Test Framework')
    parser.add_argument('--run', help='Run specific test')
    parser.add_argument('--list', action='store_true', help='List all tests')
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available Tests:")
        for name, test_def in sorted(TESTS.items()):
            print(f"  - {name}: {test_def['description']}")
        print()
        print(f"  Total: {len(TESTS)} tests")
        return
    
    if args.run:
        if args.run not in TESTS:
            print(f"❌ Test not found: {args.run}")
            print(f"   Available: {', '.join(TESTS.keys())}")
            return 1
        
        ok, error = run_test(args.run, TESTS[args.run])
        return 0 if ok else 1
    
    # Run all
    passed, failed = run_all_tests()
    
    # Save results
    results_file = WORKSPACE / "task_reports" / "test_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    results_data = {
        'timestamp': datetime.now().isoformat(),
        'total': len(TESTS),
        'passed': passed,
        'failed': failed,
        'test_coverage': f"{len(TESTS)}/{len(list(SCRIPTS_DIR.glob('*.py')))} scripts tested"
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"📄 Results saved: {results_file}")

if __name__ == "__main__":
    sys.exit(main())

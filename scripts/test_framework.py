#!/usr/bin/env python3
"""
Sir HazeClaw Simple Test Framework
=================================
Test-Framework für Scripts.

Usage:
    python3 test_framework.py              # Run all tests
    python3 test_framework.py --list      # List all tests
    python3 test_framework.py --run <name> # Run specific test
    python3 test_framework.py --category <cat> # Run by category
"""

import sys
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

# Valid test definitions (verified 2026-04-11)
# Format: 'test_name': {'script': 'script.py', 'type': 'import', 'func': 'function_name', 'description': '...'}
TESTS: Dict[str, Dict] = {
    # Core Scripts
    'morning_brief': {
        'script': 'morning_brief.py',
        'type': 'import',
        'description': 'Morning Brief Generator'
    },
    'health_check': {
        'script': 'health_check.py',
        'type': 'import',
        'args': ['--quick'],
        'description': 'Health Check'
    },
    'mission_control': {
        'script': 'mission_control.py',
        'type': 'import',
        'description': 'Mission Control Dashboard'
    },
    'session_analyzer': {
        'script': 'session_analyzer.py',
        'type': 'module',
        'description': 'Session Analyzer'
    },
    
    # Memory Scripts
    'memory_sanitizer': {
        'script': 'memory_sanitizer.py',
        'type': 'import',
        'description': 'Memory Sanitizer'
    },
    'memory_audit': {
        'script': 'memory_audit.py',
        'type': 'import',
        'description': 'Memory Audit Log'
    },
    'memory_versioning': {
        'script': 'memory_versioning.py',
        'type': 'import',
        'description': 'Memory Versioning'
    },
    'memory_validator': {
        'script': 'memory_validator.py',
        'type': 'import',
        'description': 'Memory Validator'
    },
    'memory_isolation': {
        'script': 'memory_isolation.py',
        'type': 'import',
        'description': 'Memory Isolation'
    },
    'memory_freshness': {
        'script': 'memory_freshness.py',
        'type': 'import',
        'description': 'Memory Freshness Tracker'
    },
    'stale_memory_cleanup': {
        'script': 'stale_memory_cleanup.py',
        'type': 'import',
        'description': 'Stale Memory Cleanup'
    },
    
    # Self-Healing Patterns
    'self_verifier': {
        'script': 'self_verifier.py',
        'type': 'import',
        'description': 'Self-Verification Loop'
    },
    'graceful_degradation': {
        'script': 'graceful_degradation.py',
        'type': 'import',
        'description': 'Graceful Degradation'
    },
    # Archived
    'context_compressor': {
        'script': 'context_compressor.py',
        'type': 'import',
        'description': 'Context Compression'
    },
    
    # KG Scripts  
    'kg_updater': {
        'script': 'kg_updater.py',
        'type': 'module',
        'description': 'KG Updater (consolidates kg_enhancer, kg_lifecycle, kg_relation_cleaner)'
    },
    
    # Skills & Learning
    # Archived
    # Archived
    # Archived
    # Archived
    
    # Monitoring
    'cron_error_healer': {
        'script': 'cron_error_healer.py',
        'type': 'module',
        'description': 'Cron Error Healer'
    },
    'cron_watchdog': {
        'script': 'cron_watchdog.py',
        'type': 'module',
        'description': 'Cron Watchdog (consolidates cron_monitor)'
    },
    'token_tracker': {
        'script': 'token_tracker.py',
        'type': 'module',
        'description': 'Token Tracker'
    },
    'token_budget_tracker': {
        'script': 'token_budget_tracker.py',
        'type': 'module',
        'description': 'Token Budget Tracker'
    },
    # Archived: performance_dashboard.py (consolidated into efficiency_tracker + cron_watchdog)
    
    # Analysis
    'quality_metrics': {
        'script': 'quality_metrics.py',
        'type': 'module',
        'description': 'Quality Metrics'
    },
    'session_compressor': {
        'script': 'session_compressor.py',
        'type': 'module',
        'description': 'Session Compressor'
    },
    
    # Archive
    'script_archiver': {
        'script': 'script_archiver.py',
        'type': 'import',
        'description': 'Script Archiver'
    },
}


def load_script(script_name: str) -> Optional[Any]:
    """Load a script module."""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        return None
    
    spec = importlib.util.spec_from_file_location("script", script_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    return None


def run_test(test_name: str, test_def: Dict) -> Tuple[bool, str, Any]:
    """
    Run a single test.
    
    Returns:
        Tuple of (passed, message, result)
    """
    script_name = test_def.get('script', '')
    script_path = SCRIPTS_DIR / script_name
    
    # Check if script exists
    if not script_path.exists():
        return False, f"Script not found: {script_name}", None
    
    # Try to load
    try:
        module = load_script(script_name)
        if module is None:
            return False, f"Failed to load: {script_name}", None
        
        return True, f"Loaded successfully", module
        
    except Exception as e:
        return False, f"Error: {str(e)[:100]}", None


def run_all_tests() -> Dict:
    """
    Run all tests.
    
    Returns:
        Dict with results
    """
    results = {
        'total': len(TESTS),
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'failures': [],
        'skips': [],
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"\n🧪 Running {results['total']} tests...")
    print("=" * 60)
    
    for test_name, test_def in TESTS.items():
        passed, msg, result = run_test(test_name, test_def)
        
        if passed:
            results['passed'] += 1
            print(f"  ✅ {test_name}: {msg}")
        else:
            results['failed'] += 1
            results['failures'].append((test_name, msg))
            print(f"  ❌ {test_name}: {msg}")
    
    return results


def run_category(category: str) -> Dict:
    """Run tests in a specific category."""
    filtered = {k: v for k, v in TESTS.items() if v.get('category') == category}
    
    if not filtered:
        return {'error': f'No tests in category: {category}'}
    
    results = {
        'total': len(filtered),
        'passed': 0,
        'failed': 0,
        'failures': []
    }
    
    print(f"\n🧪 Running {results['total']} tests in [{category}]...")
    print("=" * 60)
    
    for test_name, test_def in filtered.items():
        passed, msg, result = run_test(test_name, test_def)
        
        if passed:
            results['passed'] += 1
            print(f"  ✅ {test_name}")
        else:
            results['failed'] += 1
            results['failures'].append((test_name, msg))
            print(f"  ❌ {test_name}: {msg}")
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sir HazeClaw Test Framework")
    parser.add_argument("--list", action="store_true", help="List all tests")
    parser.add_argument("--run", metavar="NAME", help="Run specific test")
    parser.add_argument("--category", metavar="CAT", help="Run by category")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    
    args = parser.parse_args()
    
    if args.list:
        print(f"📋 Available Tests ({len(TESTS)}):")
        print("=" * 60)
        for name, test in sorted(TESTS.items()):
            desc = test.get('description', '')
            script = test.get('script', '')
            print(f"  {name:30} - {desc} ({script})")
        return
    
    elif args.run:
        if args.run not in TESTS:
            print(f"❌ Unknown test: {args.run}")
            print(f"   Available: {', '.join(sorted(TESTS.keys()))}")
            return
        
        test_def = TESTS[args.run]
        passed, msg, result = run_test(args.run, test_def)
        
        if passed:
            print(f"✅ PASS: {args.run}")
            print(f"   {msg}")
        else:
            print(f"❌ FAIL: {args.run}")
            print(f"   {msg}")
        return
    
    elif args.category:
        results = run_category(args.category)
        if 'error' in results:
            print(f"❌ {results['error']}")
        else:
            print(f"\n📊 Category Results: {results['passed']}/{results['total']} passed")
        return
    
    else:
        # Run all tests
        results = run_all_tests()
        
        print()
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"   Total:  {results['total']}")
        print(f"   Passed: ✅ {results['passed']}")
        print(f"   Failed: ❌ {results['failed']}")
        
        if results['failures']:
            print()
            print("Failed Tests:")
            for name, msg in results['failures']:
                print(f"  ❌ {name}: {msg[:60]}")


if __name__ == "__main__":
    main()

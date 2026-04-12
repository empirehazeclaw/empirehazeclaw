#!/usr/bin/env python3
"""
Sir HazeClaw Fast Test Runner v2
Runs tests with subprocess timeouts.
"""

import sys
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

TIMEOUT_PER_TEST = 10  # seconds

# Quick tests only (fast ones)
QUICK_TESTS = [
    ('morning_brief', 'morning_brief.py', 'generate_brief'),
    ('health_monitor', 'health_monitor.py', 'generate_report'),
    ('self_check', 'self_check.py', 'generate_report'),
    ('cron_watchdog', 'cron_watchdog.py', 'watchdog_run'),
    ('daily_summary', 'daily_summary.py', 'generate_summary'),
    ('evening_summary', 'evening_summary.py', 'generate_summary'),
    ('quality_metrics', 'quality_metrics.py', 'calculate_metrics'),
    ('memory_hybrid_search', 'memory_hybrid_search.py', 'hybrid_search'),
    ('auto_backup', 'auto_backup.py', 'get_backup_stats'),
    ('self_eval', 'self_eval.py', 'calculate_scores'),
    ('deep_reflection', 'deep_reflection.py', 'generate_deep_reflection'),
    ('memory_cleanup', 'memory_cleanup.py', 'show_report'),
    ('backup_verify', 'backup_verify.py', 'generate_report'),
    ('habit_tracker', 'habit_tracker.py', 'generate_report'),
    ('quick_check', 'quick_check.py', 'main'),
    ('kg_updater', 'kg_updater.py', 'stats'),
]

def run_test(name, script, func):
    """Führt Test aus mit Timeout."""
    cmd = [
        'python3', '-c',
        f"""
import sys
sys.path.insert(0, '{SCRIPTS_DIR}')
import importlib.util
spec = importlib.util.spec_from_file_location('m', '{SCRIPTS_DIR}/{script}')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
func = getattr(m, '{func}')
result = func()
print('OK' if result is not None else 'NONE')
"""
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_PER_TEST,
            cwd=str(WORKSPACE)
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return name, 'PASS', output
        else:
            return name, 'FAIL', result.stderr[:100] if result.stderr else 'Unknown error'
            
    except subprocess.TimeoutExpired:
        return name, 'FAIL', f'Timeout ({TIMEOUT_PER_TEST}s)'
    except Exception as e:
        return name, 'FAIL', str(e)[:100]

def main():
    print("🧪 Fast Test Runner v2")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Timeout per test: {TIMEOUT_PER_TEST}s")
    print(f"   Tests: {len(QUICK_TESTS)}")
    print()
    
    results = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(run_test, name, script, func): name 
                   for name, script, func in QUICK_TESTS}
        
        for future in as_completed(futures):
            name, status, msg = future.result()
            emoji = '✅' if status == 'PASS' else '❌'
            print(f"{emoji} {name}: {status} {msg[:40] if msg else ''}")
            results.append((name, status))
    
    passed = sum(1 for _, s in results if s == 'PASS')
    failed = sum(1 for _, s in results if s == 'FAIL')
    
    print()
    print(f"📊 Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print(f"   Coverage: {passed}/{len(QUICK_TESTS)} = {passed*100//len(QUICK_TESTS)}%")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

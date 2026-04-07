#!/usr/bin/env python3
"""
Reporting System Bundle
Konsolidiert: daily_report, weekly_report, quick_stats, security_report
"""
import sys
import importlib.util

MODULES = {
    "daily": "daily_report.py",
    "weekly": "weekly_report.py",
    "stats": "quick_stats.py",
    "security": "security_report.py"
}

def run(module_name):
    if module_name not in MODULES:
        print(f"Verfügbar: {', '.join(MODULES.keys())}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(module_name, MODULES[module_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "stats")

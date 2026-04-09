#!/usr/bin/env python3
"""
Trend Intelligence Bundle
Konsolidiert: trend_hunter + trend_research + viral_thread_creator
"""
import sys
import importlib.util

MODULES = {
    "hunter": "trend_hunter.py",
    "research": "trend_research.py",
    "viral": "viral_thread_creator.py"
}

def run(module_name):
    if module_name not in MODULES:
        print(f"Verfügbar: {', '.join(MODULES.keys())}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(module_name, MODULES[module_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "hunter")

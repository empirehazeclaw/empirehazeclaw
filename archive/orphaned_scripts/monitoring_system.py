#!/usr/bin/env python3
"""
Monitoring System Bundle
Konsolidiert: dashboard_api, dashboard_enhanced, json_api_server
"""
import sys
import importlib.util

MODULES = {
    "api": "dashboard_api.py",
    "enhanced": "dashboard_enhanced.py",
    "json": "json_api_server.py"
}

def run(module_name):
    if module_name not in MODULES:
        print(f"Verfügbar: {', '.join(MODULES.keys())}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(module_name, MODULES[module_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "api")

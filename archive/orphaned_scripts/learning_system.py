#!/usr/bin/env python3
"""
Learning System Bundle
Konsolidiert: learning_mode + self_learning_v2 + auto_optimizer + profile_optimizer
"""
import sys
import importlib.util

MODULES = {
    "mode": "learning_mode.py",
    "self": "self_learning_v2.py",
    "auto": "auto_optimizer.py",
    "profile": "profile_optimizer.py"
}

def run(module_name):
    if module_name not in MODULES:
        print(f"Verfügbar: {', '.join(MODULES.keys())}")
        print("Usage: python3 learning_system.py [mode|self|auto|profile]")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(module_name, MODULES[module_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "auto")

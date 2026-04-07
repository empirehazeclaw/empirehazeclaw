#!/usr/bin/env python3
"""
Memory & Knowledge Bundle
Konsolidiert: memory_integrated + knowledge_manager
"""
import sys
import importlib.util

MODULES = {
    "memory": "memory_integrated.py",
    "knowledge": "knowledge_manager.py"
}

def run(module_name):
    if module_name not in MODULES:
        print(f"Verfügbar: {', '.join(MODULES.keys())}")
        print("Usage: python3 memory_knowledge.py [memory|knowledge]")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(module_name, MODULES[module_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "memory")

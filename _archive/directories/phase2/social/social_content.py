#!/usr/bin/env python3
"""
Social Content Bundle
Konsolidiert: social_post_generator + social_content_calendar + content_reposter
"""
import sys
import importlib.util

MODULES = {
    "post": "social_post_generator.py",
    "calendar": "social_content_calendar.py",
    "repost": "social_content_reposter.py"
}

def run(module_name):
    if module_name not in MODULES:
        print(f"Verfügbar: {', '.join(MODULES.keys())}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(module_name, MODULES[module_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "post")

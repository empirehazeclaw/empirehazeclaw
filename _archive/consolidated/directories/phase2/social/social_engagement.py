#!/usr/bin/env python3
"""
Social Engagement Bundle
Konsolidiert: social_analytics + social_auto_engagement + twitter_growth
"""
import sys
import importlib.util

MODULES = {
    "analytics": "social_analytics.py",
    "auto_engagement": "social_auto_engagement.py", 
    "twitter_growth": "twitter_growth.py"
}

def run(module_name):
    if module_name not in MODULES:
        print(f"Verfügbar: {', '.join(MODULES.keys())}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location(module_name, MODULES[module_name])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "analytics")

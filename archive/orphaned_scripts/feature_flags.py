#!/usr/bin/env python3
"""
Feature Flags - Gradual rollouts
"""
import json

FLAGS_FILE = "data/feature_flags.json"

def get_flag(flag_name, default=False):
    """Check if feature is enabled"""
    try:
        with open(FLAGS_FILE, 'r') as f:
            flags = json.load(f)
        return flags.get(flag_name, default)
    except:
        return default

def set_flag(flag_name, enabled):
    """Enable/disable feature"""
    try:
        with open(FLAGS_FILE, 'r') as f:
            flags = json.load(f)
    except:
        flags = {}
    
    flags[flag_name] = enabled
    
    with open(FLAGS_FILE, 'w') as f:
        json.dump(flags, f, indent=2)

def is_enabled(feature):
    """Check with percentage rollout"""
    # Could add % rollout
    return get_flag(feature, False)

#!/usr/bin/env python3
"""
A/B Testing Framework
"""
import random
import json

EXPERIMENTS = {}

def create_experiment(name, variants):
    """Create A/B test"""
    EXPERIMENTS[name] = {"variants": variants, "results": {v: 0 for v in variants}}

def get_variant(experiment):
    """Get random variant"""
    if experiment not in EXPERIMENTS:
        return None
    variants = list(EXPERIMENTS[experiment]["variants"].keys())
    return random.choice(variants)

def track_conversion(experiment, variant):
    """Track conversion"""
    if experiment in EXPERIMENTS:
        EXPERIMENTS[experiment]["results"][variant] += 1

# Usage
create_experiment("signup_button", {"color_a": "green", "color_b": "blue"})
variant = get_variant("signup_button")
print(f"Showing: {variant}")

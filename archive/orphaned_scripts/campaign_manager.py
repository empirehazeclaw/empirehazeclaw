#!/usr/bin/env python3
"""Campaign Manager - Run outreach campaigns"""
import subprocess
import sys
import json
import os

CAMPAIGNS = {
    "managed_ai": "scripts/campaign_managed_ai.py",
    "hosting": "scripts/campaign_managed_hosting.py",
    "prompt_cache": "scripts/campaign_prompt_cache.py"
}

def run_campaign(name):
    if name not in CAMPAIGNS:
        return f"❌ Unknown: {name}\nAvailable: {list(CAMPAIGNS.keys())}"
    
    result = subprocess.run(["python3", CAMPAIGNS[name]], capture_output=True, text=True)
    return result.stdout[:500]

def list_campaigns():
    return list(CAMPAIGNS.keys())

if __name__ == "__main__":
    campaign = sys.argv[1] if len(sys.argv) > 1 else ""
    if not campaign:
        print("=== 📧 CAMPAIGN MANAGER ===")
        print(f"Available: {list_campaigns()}")
    else:
        print(f"Running: {campaign}")
        print(run_campaign(campaign))

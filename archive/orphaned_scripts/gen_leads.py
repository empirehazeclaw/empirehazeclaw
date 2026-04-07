#!/usr/bin/env python3
"""Lead Generator - Find businesses"""
import subprocess
import sys
import json

def generate_leads(industry, location, count=10):
    """Generate leads for industry/location"""
    print(f"🎯 Generating {count} leads for {industry} in {location}...")
    
    # Use the lead crawler
    cmd = ["python3", "scripts/lead_crawler_v2.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return result.stdout if result.returncode == 0 else f"❌ {result.stderr}"

if __name__ == "__main__":
    ind = sys.argv[1] if len(sys.argv) > 1 else "restaurant"
    loc = sys.argv[2] if len(sys.argv) > 2 else "Berlin"
    cnt = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    print(generate_leads(ind, loc, cnt))

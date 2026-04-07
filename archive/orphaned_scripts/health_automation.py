#!/usr/bin/env python3
"""
🏥 Health Automation
System health monitoring
"""

import subprocess

# Check websites
sites = ["empirehazeclaw.com", "empirehazeclaw.de", "empirehazeclaw.store", "empirehazeclaw.info"]
results = {}

for site in sites:
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"https://{site}"],
        capture_output=True, text=True
    )
    results[site] = result.stdout == "200"

# Check services
services = ["openclaw", "docker"]
service_results = {}
for svc in services:
    result = subprocess.run(["pgrep", "-f", svc], capture_output=True)
    service_results[svc] = result.returncode == 0

print("🏥 Health Status:")
print(f"   Websites: {sum(results.values())}/{len(results)}")
print(f"   Services: {sum(service_results.values())}/{len(service_results)}")

if sum(results.values()) == len(results) and sum(service_results.values()) == len(service_results):
    print("   ✅ All healthy!")
else:
    print("   ⚠️ Issues found")

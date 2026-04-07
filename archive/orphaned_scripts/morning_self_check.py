#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

print(f"[{datetime.now().isoformat()}] 🌅 MORNING SELF CHECK (System Health & TODOs)")

workspace = "/home/clawbot/.openclaw/workspace"

# Check TODOs
try:
    with open(os.path.join(workspace, "TODO.md"), "r") as f:
        todos = [line.strip() for line in f if "- [ ]" in line]
        print(f"Offene TODOs heute: {len(todos)}")
        for t in todos[:5]: print(f"  {t}")
except:
    print("Keine TODO.md gefunden.")

# Check Server Health
ports = [8896, 8001, 8888, 8895] # Directory, Trading, Dashboard, Prompt Cache
print("\nService Health:")
for port in ports:
    try:
        import urllib.request
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}", timeout=2)
        print(f"  Port {port}: ONLINE ({req.getcode()})")
    except Exception as e:
        print(f"  Port {port}: FEHLER ({e})")

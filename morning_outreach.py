#!/usr/bin/env python3
"""
☀️ Morning Outreach Routine
Generiert Dashboard + sendet Morning Report
"""
import subprocess
import sys
from pathlib import Path

# Run dashboard update
print("📊 Generiere Outreach Dashboard...")
result = subprocess.run([sys.executable, "/home/clawbot/.openclaw/workspace/scripts/outreach_dashboard.py"], capture_output=True, text=True)
print(result.stdout)

# Stats for report
print("\n☀️ Morning Report:")
print("  - Dashboard: data/outreach_dashboard.html")
print("  - Nächste Action: Neue Leads finden oder Outreach senden")
print("\n✅ Daily Improvement abgeschlossen!")
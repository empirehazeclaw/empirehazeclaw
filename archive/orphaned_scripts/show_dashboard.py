#!/usr/bin/env python3
"""Open Dashboard in Browser"""
import subprocess
import sys
import webbrowser

DASHBOARDS = {
    "revenue": "scripts/revenue_dashboard.html",
    "metrics": "scripts/metrics.html",
    "combined": "scripts/combined_dashboard.html",
    "main": "scripts/dashboard.html"
}

def open_dashboard(name="revenue"):
    if name not in DASHBOARDS:
        return f"❌ Not found: {name}"
    
    path = os.path.abspath(DASHBOARDS[name])
    url = f"file://{path}"
    webbrowser.open(url)
    return f"✅ Opened: {name}"

import os
if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "revenue"
    print(open_dashboard(name))

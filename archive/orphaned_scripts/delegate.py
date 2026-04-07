#!/usr/bin/env python3
"""
🤖 AUTO-DELEGATE v3 - Autonomous Agent Manager
==============================================
Runs hourly, assigns tasks to OpenClaw agents.
"""

import os
import json
import subprocess
import requests
from datetime import datetime

AGENTS = {
    "dev": "Development & Bug Fixes",
    "researcher": "Research & Analysis",
    "content": "Content Creation",
    "pod": "Print on Demand",
    "social": "Social Media",
    "outreach": "Customer Outreach"
}

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def check_openclaw():
    """Check if OpenClaw API is available"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:18789/health"],
            capture_output=True, timeout=3
        )
        return result.returncode == 0
    except:
        return False

def get_curl_command(agent_id, task):
    """Build curl command to spawn agent"""
    return [
        "curl", "-s", "-X", "POST",
        "http://127.0.0.1:18789/api/sessions",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "runtime": "subagent",
            "agentId": agent_id,
            "task": task,
            "mode": "run"
        })
    ]

#!/usr/bin/env python3
"""
🤖 SMART AUTO-DELEGATE v4
==========================
Uses Task Router + Definition of Done
"""

import json
import subprocess
import sys
sys.path.insert(0, "/home/clawbot/.openclaw/workspace/scripts")

from task_router import route_task, AGENTS
from definition_of_done import validate_task, DONE_CRITERIA
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M')}] {msg}")

def run_agent(agent_id, task):
    """Spawn agent via sessions_spawn"""
    # This would call the OpenClaw API in production
    log(f"  → Starting {agent_id}: {task[:50]}...")
    return {"status": "started", "agent": agent_id}

def main():
    log("🤖 Smart Auto-Delegate v4 startet...")
    
    # Get current hour
    hour = datetime.now().hour
    
    # Define tasks by hour
    tasks = {
        7: "Research latest AI trends and competitors",
        8: "Fix any website errors",
        9: "Send outreach emails to potential clients",
        10: "Write blog post for this week",
        11: "Research new product opportunities",
        12: "Post on social media about products",
        14: "Check Etsy orders and create new design",
        15: "Follow up with previous leads",
        16: "Optimize chatbot features",
        17: "Update website content",
        18: "Post on Twitter and LinkedIn",
        19: "Analyze competitor strategies",
        20: "Prepare newsletter content"
    }
    
    # Get task for current hour or default
    task_text = tasks.get(hour, "Check system health and optimize")
    
    # Route task to correct agent
    log(f"📋 Task: {task_text}")
    routing = route_task(task_text)
    
    log(f"🎯 Routed to: {routing['agent']} ({routing['role']})")
    
    # Show Definition of Done
    criteria = DONE_CRITERIA.get(routing['agent'], {})
    if criteria:
        log(f"📝 Success Criteria:")
        for c in criteria.get("criteria", [])[:2]:
            log(f"   ✓ {c}")
    
    # Start agent
    result = run_agent(routing['agent'], task_text)
    
    log(f"✅ Task delegated to {routing['agent']}")

if __name__ == "__main__":
    main()

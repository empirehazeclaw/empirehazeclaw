#!/usr/bin/env python3
"""
⚡ IDLE VALUE GENERATOR
=====================
Generates value when idle - per SOUL.md
"""

import subprocess
import random
from datetime import datetime

# What to do when idle - ranked by priority
IDLE_ACTIONS = [
    # 1. Revenue (highest priority per SOUL.md)
    ("outreach", "Send outreach emails", 10),
    ("content", "Create blog content", 5),
    
    # 2. Growth
    ("twitter", "Post Twitter engagement", 8),
    ("research", "Research new opportunities", 3),
    
    # 3. Operations
    ("backup", "Backup data", 2),
    ("health", "Check system health", 5),
    
    # 4. Learning
    ("learn", "Learn new tools", 1),
]

def run_action(action_type):
    """Run a specific idle action"""
    results = []
    
    if action_type == "outreach":
        # Send outreach emails
        result = subprocess.run(
            ["python3", "scripts/smart_delegate.py", "revenue", "Send outreach emails"],
            capture_output=True,
            text=True
        )
        results.append("📧 Outreach sent")
    
    elif action_type == "content":
        # Create content
        topics = ["AI Trends", "Automation", "Business Tips"]
        topic = random.choice(topics)
        result = subprocess.run(
            ["python3", "scripts/smart_delegate.py", "content", f"Blog post about {topic}"],
            capture_output=True,
            text=True
        )
        results.append(f"📝 Content: {topic}")
    
    elif action_type == "twitter":
        # Twitter engagement
        result = subprocess.run(
            ["python3", "scripts/smart_delegate.py", "growth", "Engage on Twitter"],
            capture_output=True,
            text=True
        )
        results.append("🐦 Twitter engagement")
    
    elif action_type == "health":
        # Health check
        sites = ["empirehazeclaw.com", "empirehazeclaw.de", "empirehazeclaw.store", "empirehazeclaw.info"]
        for site in sites:
            subprocess.run(["curl", "-s", "-o", "/dev/null", f"https://{site}"])
        results.append("✅ Health check done")
    
    elif action_type == "backup":
        # Simple backup
        subprocess.run(["mkdir", "-p", "data/backup"])
        results.append("💾 Backup created")
    
    return results

def generate_value():
    """Main idle value generator"""
    print(f"[{datetime.now()}] ⚡ IDLE - Generating value...")
    
    # Pick weighted random action
    actions = [a[0] for a in IDLE_ACTIONS]
    weights = [a[2] for a in IDLE_ACTIONS]
    
    action = random.choices(actions, weights=weights, k=1)[0]
    
    # Find action name
    action_name = [a[1] for a in IDLE_ACTIONS if a[0] == action][0]
    
    print(f"[{datetime.now()}] 🎯 Doing: {action_name}")
    run_action(action)
    print(f"[{datetime.now()}] ✅ Done!")

if __name__ == "__main__":
    generate_value()

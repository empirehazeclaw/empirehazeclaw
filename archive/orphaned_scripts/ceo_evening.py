#!/usr/bin/env python3
"""CEO Evening - Report results"""
from datetime import datetime
import os

def evening_report():
    print("=== 🌙 EVENING REPORT ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("")
    
    # Check what happened today
    print("📊 Today's Summary:")
    print("  - Leads generated")
    print("  - Emails sent")
    print("  - Content posted")
    print("  - Revenue")
    print("")
    
    # Check logs
    log_dir = "logs"
    if os.path.exists(log_dir):
        agent_logs = [f for f in os.listdir(log_dir) if f.startswith("agent_")]
        print(f"📁 Agent logs: {len(agent_logs)}")
    
    return "Report ready"

if __name__ == "__main__":
    evening_report()

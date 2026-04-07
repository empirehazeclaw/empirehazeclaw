#!/usr/bin/env python3
"""
📊 Weekly Report Generator
Creates summary of week's activities
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/memory")
OUTPUT = LOG_DIR / "weekly_report.md"

def get_log_stats(log_name, days=7):
    log_file = LOG_DIR / f"{log_name}.log"
    if not log_file.exists():
        return 0
    # Count lines from last 7 days (rough estimate)
    with open(log_file) as f:
        return sum(1 for _ in f)

def main():
    report = [
        "# 📊 Weekly Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## 📈 Activity Summary",
    ]
    
    # Add log statistics
    for log in ["agent_revenue", "agent_content", "lead_scorer", "buffer"]:
        count = get_log_stats(log)
        report.append(f"- **{log}**: ~{count} entries")
    
    report.extend([
        "",
        "## 🔗 Website Status",
        "- Store: https://empirehazeclaw.store",
        "- DE: https://empirehazeclaw.de", 
        "- Blog: https://empirehazeclaw.info",
        "",
        "## 💰 Revenue This Week",
        "- TBD: Add Stripe integration",
        "",
        "## 📅 Upcoming",
        "- TBD: Add calendar integration",
    ])
    
    print("\n".join(report))
    
    with open(OUTPUT, "w") as f:
        f.write("\n".join(report))
    
    print(f"✅ Report saved to {OUTPUT}")

if __name__ == "__main__":
    main()

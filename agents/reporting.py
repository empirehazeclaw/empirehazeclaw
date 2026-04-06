#!/usr/bin/env python3
"""
📊 Agent Reporting System
"""
import json
from datetime import datetime
import os

REPORTS_DIR = "/home/clawbot/.openclaw/workspace/data/agent_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

class AgentReport:
    def __init__(self, agent_name):
        self.agent = agent_name
        self.timestamp = datetime.now().isoformat()
        self.tasks = []
        self.metrics = {}
        self.issues = []
    
    def add_task(self, task, status, notes=""):
        self.tasks.append({
            "task": task,
            "status": status,
            "notes": notes,
            "time": datetime.now().isoformat()
        })
    
    def add_metric(self, key, value):
        self.metrics[key] = value
    
    def add_issue(self, issue):
        self.issues.append(issue)
    
    def save(self):
        filename = f"{REPORTS_DIR}/{self.agent}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump({
                "agent": self.agent,
                "timestamp": self.timestamp,
                "tasks": self.tasks,
                "metrics": self.metrics,
                "issues": self.issues
            }, f, indent=2)
        return filename

# Example usage for Revenue Agent
def revenue_daily_report():
    report = AgentReport("revenue")
    report.add_task("outreach_emails", "completed", "Sent 5 emails")
    report.add_metric("emails_sent", 5)
    report.add_metric("responses", 2)
    
    # Notify CEO
    report.save()
    return report

if __name__ == "__main__":
    print("📊 Reporting System Ready")

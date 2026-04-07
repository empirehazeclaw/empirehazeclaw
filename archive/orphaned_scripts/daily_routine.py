#!/usr/bin/env python3
"""Daily Routine - Morning Automation"""
import subprocess
import sys

def run_daily():
    print("=== ☀️ DAILY ROUTINE ===")
    
    # 1. System Status
    print("\n1️⃣ Services:")
    subprocess.run(["python3", "scripts/system_status.py"])
    
    # 2. Revenue
    print("\n2️⃣ Revenue:")
    subprocess.run(["python3", "scripts/quick_revenue.py"])
    
    # 3. Leads
    print("\n3️⃣ Next Lead:")
    subprocess.run(["python3", "scripts/run_outreach.py"])
    
    # 4. Memory
    print("\n4️⃣ Memory:")
    subprocess.run(["python3", "scripts/morning_reminder.sh"])
    
    return "✅ Morning routine complete!"

if __name__ == "__main__":
    print(run_daily())

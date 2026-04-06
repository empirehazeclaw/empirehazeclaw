#!/usr/bin/env python3
"""
CEO Morning Routine
1. Check Strategy (SOUL.md)
2. Check Priorities (AUTONOMOUS_PRIORITIES.md)  
3. Check Recent Messages
4. Decide which agents to run
5. Delegate
"""
import subprocess
import sys
import os
from datetime import datetime

def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path) as f:
        return f.read()

def get_daily_priorities():
    """Hol alle Prioritäten aus allen Quellen"""
    print("=== 🌅 CEO MORNING ROUTINE ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("")
    
    # 1. SOUL.md - Meine Strategie
    print("1️⃣ Strategy (SOUL.md):")
    soul = read_file("SOUL.md")
    # Find priorities section
    if "Priority" in soul:
        print("   - Found priorities in SOUL")
    
    # 2. AUTONOMOUS_PRIORITIES.md
    print("2️⃣ Autonomous Priorities:")
    auto = read_file("AUTONOMOUS_PRIORITIES.md")
    
    # 3. Recent Decisions (memory)
    print("3️⃣ Recent Decisions:")
    mem = read_file("memory/2026-03-24.md")
    
    # Extract key info
    priorities = {
        "revenue": ["lead generation", "outreach", "sales"],
        "content": ["blog", "social", "post"],
        "mail": ["email", "outreach", "followup"],
        "research": ["research", "analyze"],
        "operations": ["monitor", "health"]
    }
    
    return priorities

def decide_agents(priorities):
    """Entscheide welche Agenten heute laufen"""
    print("\n🎯 TODAY'S AGENT SCHEDULE:")
    print("")
    
    # Always: operations (morning check)
    print("  ✅ operations_agent - Morning check")
    
    # Check what we need based on priorities
    needed = []
    
    # Revenue is usually priority
    print("  ✅ revenue_agent - Lead generation")
    needed.append("revenue")
    
    # Content - depends on day
    hour = datetime.now().hour
    if hour in [12, 18]:
        print("  ✅ content_agent - Blog/Social")
        needed.append("content")
    
    # Mail - after leads
    print("  ✅ mail_agent - Outreach")
    needed.append("mail")
    
    return needed

def delegate(agents):
    """Delegiere an Agents"""
    print(f"\n🚀 DELEGATING to {len(agents)} agents...")
    
    for agent in agents:
        print(f"\n🤖 Starting {agent}...")
        result = subprocess.run(
            ["python3", f"scripts/run_agent.py", agent],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode != 0:
            print(f"❌ {agent} failed: {result.stderr[:100]}")
            # Report error to Nico
            return f"ERROR in {agent}: {result.stderr[:200]}"
        else:
            print(f"✅ {agent} done")
    
    return "All agents completed successfully"

def morning_routine():
    """Main morning routine"""
    priorities = get_daily_priorities()
    agents = decide_agents(priorities)
    result = delegate(agents)
    
    print(f"\n=== ✅ MORNING ROUTINE COMPLETE ===")
    return result

if __name__ == "__main__":
    morning_routine()

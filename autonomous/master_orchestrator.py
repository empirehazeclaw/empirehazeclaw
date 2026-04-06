#!/usr/bin/env python3
"""
🎛️ MASTER ORCHESTRATOR INTEGRATION
================================
Coordinates all agents into one autonomous workflow!
"""

import subprocess
import json
from datetime import datetime

# All our agents
AGENTS = {
    "validation": "scripts/autonomous/agents/validation_agent.py",
    "research": "scripts/autonomous/agents/research_agent.py", 
    "content": "scripts/autonomous/agents/content_agent.py",
    "sales": "scripts/autonomous/agents/sales_agent.py",
    "outreach": "scripts/autonomous/agents/outreach_agent.py",
}

def run_agent(name, script):
    """Run a single agent"""
    print(f"\n🎯 Running: {name}")
    try:
        result = subprocess.run(
            ["python3", script],
            capture_output=True,
            text=True,
            timeout=300
        )
        return {"agent": name, "status": "success", "output": result.stdout[:500]}
    except Exception as e:
        return {"agent": name, "status": "error", "error": str(e)}

def run_workflow(workflow):
    """Run coordinated workflow"""
    print("=" * 60)
    print(f"🎛️ MASTER ORCHESTRATOR - {datetime.now()}")
    print(f"📋 Workflow: {workflow}")
    print("=" * 60)
    
    results = []
    
    # Morning Workflow
    if workflow == "morning":
        # 1. Research first
        results.append(run_agent("research", AGENTS["research"]))
        
        # 2. Validate opportunities
        results.append(run_agent("validation", AGENTS["validation"]))
        
        # 3. Create content
        results.append(run_agent("content", AGENTS["content"]))
        
        # 4. Sales outreach
        results.append(run_agent("sales", AGENTS["sales"]))
    
    # Evening Workflow
    elif workflow == "evening":
        # 1. More content
        results.append(run_agent("content", AGENTS["content"]))
        
        # 2. Follow up outreach
        results.append(run_agent("outreach", AGENTS["outreach"]))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 WORKFLOW SUMMARY:")
    print("=" * 60)
    
    for r in results:
        status = "✅" if r["status"] == "success" else "❌"
        print(f"{status} {r['agent']}: {r['status']}")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n🎯 Success: {success_count}/{len(results)}")
    
    return results

if __name__ == "__main__":
    import sys
    
    workflow = sys.argv[1] if len(sys.argv) > 1 else "morning"
    run_workflow(workflow)

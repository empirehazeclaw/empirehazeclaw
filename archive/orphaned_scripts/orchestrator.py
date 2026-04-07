#!/usr/bin/env python3
"""
🎯 TASK ORCHESTRATOR v7.0
Now with SMART LLM ROUTING built-in!

Usage:
    python3 orchestrator.py "Find Restaurant Leads"
    python3 orchestrator.py --task "Write blog post" --llm
    python3 orchestrator.py --llm-only "What is AI?"
    python3 orchestrator.py --status
    python3 orchestrator.py --list
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

AGENTS_DIR = Path("/home/clawbot/.openclaw/workspace/scripts/agents")
LLM_ROUTER = Path("/home/clawbot/.openclaw/workspace/scripts/llm_router.py")

def load_llm_router():
    """Load LLM router if available."""
    if LLM_ROUTER.exists():
        sys.path.insert(0, str(LLM_ROUTER.parent))
        try:
            from llm_router import LLMRouter
            return LLMRouter()
        except Exception as e:
            print(f"Warning: Could not load LLM router: {e}")
    return None

def query_llm(prompt, priority="balanced", use_cache=True):
    """Query LLM with smart routing."""
    router = load_llm_router()
    if router:
        return router.query(prompt=prompt, priority=priority, use_cache=use_cache)
    return {"success": False, "error": "LLM router not available"}

def scan_agents():
    """Scan all actual agent files."""
    agents = {"root": [], "categories": {}}
    
    if not AGENTS_DIR.exists():
        return agents
    
    # Scan root level
    for f in sorted(AGENTS_DIR.glob("*_agent.py")):
        agents["root"].append(f.name)
    
    # Scan categories
    for cat_dir in sorted(AGENTS_DIR.iterdir()):
        if cat_dir.is_dir() and not cat_dir.name.startswith("__"):
            cat_agents = []
            for f in sorted(cat_dir.glob("*_agent.py")):
                cat_agents.append(f"{cat_dir.name}/{f.name}")
            if cat_agents:
                agents["categories"][cat_dir.name] = cat_agents
    
    return agents

def get_total():
    """Get total agent count."""
    agents = scan_agents()
    return len(agents["root"]) + sum(len(c) for c in agents["categories"].values())

def list_agents():
    """List all actual agents."""
    agents = scan_agents()
    total = get_total()
    
    print("\n" + "=" * 60)
    print(f"📋 ORCHESTRATOR v7.0 - {total} AGENTS + LLM ROUTING")
    print("=" * 60)
    
    # Categories
    for cat in sorted(agents["categories"].keys()):
        cat_agents = agents["categories"][cat]
        primary = cat_agents[0].split("/")[1] if "/" in cat_agents[0] else cat_agents[0]
        print(f"\n📁 {cat.upper()} ({len(cat_agents)} agents)")
        print(f"   Primary: {primary}")
        for a in cat_agents[:3]:
            print(f"   • {a}")
        if len(cat_agents) > 3:
            print(f"   ... +{len(cat_agents)-3} more")
    
    # Root
    print(f"\n📁 ROOT ({len(agents['root'])} agents)")
    print(f"   Primary: sales_executor_agent.py")
    for a in agents["root"][:5]:
        print(f"   • {a}")
    if len(agents["root"]) > 5:
        print(f"   ... +{len(agents['root'])-5} more")
    
    print("\n" + "=" * 60)

def show_status():
    """Show status."""
    agents = scan_agents()
    total = get_total()
    
    router = load_llm_router()
    llm_status = "✅ Loaded" if router else "⚠️ Not available"
    
    print(f"""
🎯 ORCHESTRATOR v7.0 STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Agent Directory: {AGENTS_DIR}
🤖 Total Agents: {total}
🔗 LLM Router: {llm_status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LLM Routing Priorities:
  speed    - Fastest response (Gemini 2.5 Flash)
  quality  - Best quality (Gemini 2.5 Pro, Claude)
  cost     - Free only (Gemini 2.5 Flash/Pro)
  balanced - Mix (default)

Examples:
  orchestrator.py --llm-only "What is AI?"
  orchestrator.py --task "Code review" --llm
  orchestrator.py --llm-priority speed "Quick question"
""")

def route_task(task, priority="balanced"):
    """Route a task intelligently using LLM when appropriate."""
    
    # Detect if task is LLM-appropriate
    llm_keywords = ["what", "how", "why", "explain", "write", "analyze", 
                    "create", "generate", "summarize", "translate", "compare",
                    "german", "deutsch", "email", "text", "post", "content",
                    "blog", "文案", "schreiben"]
    
    task_lower = task.lower()
    is_llm_task = any(kw in task_lower for kw in llm_keywords)
    
    # If short query or general question, use LLM directly
    if len(task) < 200 or is_llm_task:
        print(f"\n🎯 Routing to LLM (task detected as LLM-appropriate)")
        return query_llm(task, priority=priority)
    
    # Otherwise, route to appropriate agent
    agents = scan_agents()
    
    # Try to find matching category
    for cat in agents["categories"].keys():
        if cat in task_lower:
            primary = agents["categories"][cat][0]
            print(f"\n🎯 Routing to {cat} agent: {primary}")
            return {"success": True, "routed_to": primary, "type": "agent"}
    
    # Default to LLM for general tasks
    print(f"\n🎯 Defaulting to LLM for general task")
    return query_llm(task, priority=priority)

def main():
    parser = argparse.ArgumentParser(description="🎯 Task Orchestrator v7.0")
    parser.add_argument("task", nargs="?", help="Task description")
    parser.add_argument("--llm", "-l", action="store_true", help="Force LLM routing")
    parser.add_argument("--llm-only", action="store_true", help="LLM only (no agent)")
    parser.add_argument("--llm-priority", "-p", default="balanced",
                       choices=["speed", "quality", "cost", "balanced"],
                       help="LLM priority")
    parser.add_argument("--status", "-s", action="store_true")
    parser.add_argument("--list", action="store_true")
    
    args = parser.parse_args()
    
    if args.list:
        list_agents()
    elif args.status:
        show_status()
    elif args.llm_only:
        print(f"\n🔮 LLM Only Mode")
        result = query_llm(args.task, priority=args.llm_priority)
        if result["success"]:
            print(f"\n✅ Response from {result.get('model', 'LLM')}")
            if result.get('cached'):
                print("(from cache)")
            print(f"\n{result['response']}")
        else:
            print(f"\n❌ Error: {result.get('error')}")
    elif args.llm:
        print(f"\n🔮 LLM Routing Mode")
        result = query_llm(args.task, priority=args.llm_priority)
        if result["success"]:
            print(f"\n✅ Response from {result.get('model', 'LLM')}")
            print(f"\n{result['response']}")
        else:
            print(f"\n❌ Error: {result.get('error')}")
    elif args.task:
        result = route_task(args.task)
        if result.get("success") and result.get("type") == "agent":
            print(f"   Run: orchestrator.py --run {result['routed_to'].split('/')[0]}")
        elif not result.get("success"):
            print(f"\n❌ Error: {result.get('error')}")
    else:
        print("""🎯 Task Orchestrator v7.0 - NOW WITH LLM ROUTING!

Usage:
  orchestrator.py "Find Restaurant Leads"
  orchestrator.py --llm "What is AI?"
  orchestrator.py --llm-only "Write German email"
  orchestrator.py --llm-priority speed "Quick question"
  orchestrator.py --status
  orchestrator.py --list

NEW! Use --llm flag to route ANY task to the smart LLM router!
""")

if __name__ == "__main__":
    main()

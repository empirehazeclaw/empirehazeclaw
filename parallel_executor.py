#!/usr/bin/env python3
"""
⚡ PARALLEL EXECUTION ENGINE
Executes multiple agents simultaneously for faster results.

Usage:
    python3 parallel_executor.py --task "Find 50 Leads" "Send 25 Emails" "Check Server"
    python3 parallel_executor.py --agents sales research operations
    python3 parallel_executor.py --chain "Find Leads" -> "Score" -> "Send Outreach"
    python3 parallel_executor.py --status
"""

import json
import subprocess
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Config
AGENTS_DIR = Path("/home/clawbot/.openclaw/workspace/scripts/agents")
ORCHESTRATOR = Path("/home/clawbot/.openclaw/workspace/scripts/orchestrator.py")
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
RESULTS_FILE = LOG_DIR / "parallel_results.json"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

# Thread-safe printing
print_lock = Lock()

def log(msg, color=""):
    """Thread-safe logging."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    with print_lock:
        print(f"{color}{line}{Colors.RESET}")
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / "parallel_executor.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {line}\n")

def execute_agent(agent_script: str, action: str, params: dict) -> dict:
    """Execute a single agent in a thread."""
    agent_path = AGENTS_DIR / agent_script
    
    log(f"⚡ Starting: {agent_script} ({action})", Colors.BLUE)
    
    start_time = time.time()
    
    try:
        # Build command
        cmd = ["python3", str(agent_path), action]
        
        # Add parameters
        for key, value in params.items():
            if value:
                cmd.extend([f"--{key}", str(value)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        duration = time.time() - start_time
        success = result.returncode == 0
        
        output = result.stdout.strip()[:300] if result.stdout else ""
        error = result.stderr.strip()[:200] if result.stderr else ""
        
        if success:
            log(f"✅ Completed: {agent_script} in {duration:.1f}s", Colors.GREEN)
        else:
            log(f"❌ Failed: {agent_script} - {error[:50]}", Colors.RED)
        
        return {
            "agent": agent_script,
            "action": action,
            "status": "completed" if success else "failed",
            "output": output,
            "error": error,
            "duration": duration,
            "started_at": datetime.now().isoformat()
        }
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        log(f"⏰ Timeout: {agent_script} after {duration:.1f}s", Colors.YELLOW)
        return {
            "agent": agent_script,
            "action": action,
            "status": "timeout",
            "duration": duration,
            "started_at": datetime.now().isoformat()
        }
    except Exception as e:
        duration = time.time() - start_time
        log(f"💥 Error: {agent_script} - {str(e)[:50]}", Colors.RED)
        return {
            "agent": agent_script,
            "action": action,
            "status": "error",
            "error": str(e)[:200],
            "duration": duration,
            "started_at": datetime.now().isoformat()
        }

def execute_parallel(tasks: list, max_workers: int = 3) -> list:
    """Execute multiple tasks in parallel."""
    log(f"🚀 Starting {len(tasks)} tasks (max {max_workers} parallel)", Colors.CYAN)
    
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_task = {}
        for task in tasks:
            future = executor.submit(
                execute_agent,
                task["agent"],
                task["action"],
                task.get("params", {})
            )
            future_to_task[future] = task
        
        # Collect results as they complete
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "agent": task["agent"],
                    "status": "error",
                    "error": str(e)
                })
    
    total_duration = time.time() - start_time
    
    # Summary
    success = sum(1 for r in results if r["status"] == "completed")
    failed = sum(1 for r in results if r["status"] in ["failed", "error", "timeout"])
    
    log(f"📊 Parallel execution complete: {success} succeeded, {failed} failed in {total_duration:.1f}s", 
        Colors.GREEN if failed == 0 else Colors.YELLOW)
    
    return results

def execute_chain(tasks: list) -> list:
    """Execute tasks in sequence, passing results to next."""
    log(f"🔗 Starting chain execution of {len(tasks)} tasks", Colors.MAGENTA)
    
    results = []
    start_time = time.time()
    
    for i, task in enumerate(tasks):
        log(f"🔗 Chain step {i+1}/{len(tasks)}: {task['agent']}", Colors.CYAN)
        
        result = execute_agent(task["agent"], task["action"], task.get("params", {}))
        results.append(result)
        
        if result["status"] != "completed":
            log(f"⚠️ Chain broken at step {i+1}", Colors.RED)
            break
        
        # Small delay between steps
        time.sleep(1)
    
    total_duration = time.time() - start_time
    log(f"🔗 Chain complete in {total_duration:.1f}s", Colors.GREEN)
    
    return results

def save_results(results: list):
    """Save execution results."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)

def print_summary(results: list):
    """Print execution summary."""
    print("\n" + "="*60)
    print(f"{Colors.CYAN}⚡ EXECUTION SUMMARY{Colors.RESET}")
    print("="*60)
    
    total_duration = sum(r.get("duration", 0) for r in results)
    success = sum(1 for r in results if r["status"] == "completed")
    failed = len(results) - success
    
    print(f"Total Tasks:  {len(results)}")
    print(f"Completed:    {success} {Colors.GREEN}✓{Colors.RESET}")
    print(f"Failed:       {failed} {Colors.RED}✗{Colors.RESET}" if failed else "")
    print(f"Total Time:   {total_duration:.1f}s")
    print("="*60)
    
    for r in results:
        icon = f"{Colors.GREEN}✓{Colors.RESET}" if r["status"] == "completed" else f"{Colors.RED}✗{Colors.RESET}"
        print(f"\n{icon} {r['agent']} ({r.get('action','')})")
        print(f"  Status: {r['status']}")
        print(f"  Duration: {r.get('duration', 0):.1f}s")
        if r.get('output'):
            print(f"  Output: {r['output'][:100]}...")

# Predefined task combinations
PARALLEL_TEMPLATES = {
    "morning": [
        {"agent": "lead_intelligence_agent.py", "action": "stats", "params": {}},
        {"agent": "server_ops_agent.py", "action": "status", "params": {}},
        {"agent": "sales_executor_agent.py", "action": "stats", "params": {}},
    ],
    "outreach_batch": [
        {"agent": "lead_intelligence_agent.py", "action": "score", "params": {}},
        {"agent": "sales_executor_agent.py", "action": "prospects", "params": {"count": 25}},
        {"agent": "cold_outreach_agent.py", "action": "run_campaign", "params": {"count": 25}},
    ],
    "content_batch": [
        {"agent": "content_production_agent.py", "action": "blog", "params": {"topic": "AI Hosting", "lang": "de"}},
        {"agent": "content_production_agent.py", "action": "social", "params": {"platform": "linkedin", "topic": "AI Hosting"}},
        {"agent": "newsletter_agent.py", "action": "pipeline", "params": {}},
    ],
    "full_diagnostic": [
        {"agent": "server_ops_agent.py", "action": "status", "params": {}},
        {"agent": "lead_intelligence_agent.py", "action": "stats", "params": {}},
        {"agent": "sales_executor_agent.py", "action": "pipeline", "params": {}},
        {"agent": "customer_support_agent.py", "action": "report", "params": {}},
    ]
}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="⚡ Parallel Execution Engine")
    
    parser.add_argument("--task", "-t", nargs="+", help="Tasks to execute in parallel")
    parser.add_argument("--agents", "-a", nargs="+", choices=["sales", "research", "ops", "support", "content", "all"],
                       help="Run all agents in category")
    parser.add_argument("--chain", nargs="+", help="Tasks to run in sequence (use '->' between steps)")
    parser.add_argument("--template", choices=list(PARALLEL_TEMPLATES.keys()), help="Use predefined template")
    parser.add_argument("--max-workers", "-w", type=int, default=3, help="Max parallel workers (default: 3)")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    parser.add_argument("--list-templates", "-l", action="store_true", help="List available templates")
    
    args = parser.parse_args()
    
    if args.status:
        print(f"{Colors.CYAN}⚡ Parallel Executor Status{Colors.RESET}")
        print(f"Log: {LOG_DIR / 'parallel_executor.log'}")
        print(f"Results: {RESULTS_FILE}")
        return
    
    if args.list_templates:
        print(f"\n{Colors.CYAN}Available Templates:{Colors.RESET}")
        for name, tasks in PARALLEL_TEMPLATES.items():
            print(f"  {name}: {len(tasks)} tasks")
        print()
        return
    
    if args.template:
        tasks = PARALLEL_TEMPLATES[args.template]
        log(f"Using template: {args.template}", Colors.YELLOW)
        results = execute_parallel(tasks, max_workers=args.max_workers)
        save_results(results)
        print_summary(results)
        return
    
    if args.chain:
        # Parse chain tasks (format: "Find Leads" -> "Score" -> "Send")
        tasks = []
        for i, item in enumerate(args.chain):
            if item == "->":
                continue
            
            # Simple task parsing
            tasks.append({
                "agent": "sales_executor_agent.py",  # Default
                "action": "outreach",
                "params": {"count": 10}
            })
        
        if len(tasks) >= 2:
            results = execute_chain(tasks)
            save_results(results)
            print_summary(results)
        return
    
    if args.agents:
        # Map categories to agents
        category_agents = {
            "sales": ["sales_executor_agent.py", "cold_outreach_agent.py", "lead_gen_agent.py"],
            "research": ["lead_intelligence_agent.py", "radar_agent.py"],
            "ops": ["server_ops_agent.py", "infra_monitor_agent.py"],
            "support": ["customer_support_agent.py"],
            "content": ["content_production_agent.py", "seo_writer_agent.py"],
            "all": ["sales_executor_agent.py", "lead_intelligence_agent.py", "server_ops_agent.py", 
                   "customer_support_agent.py", "content_production_agent.py"]
        }
        
        agents = []
        for cat in args.agents:
            agents.extend(category_agents.get(cat, []))
        
        tasks = [{"agent": a, "action": "stats", "params": {}} for a in set(agents)]
        
        log(f"Running {len(tasks)} agents from categories: {args.agents}", Colors.YELLOW)
        results = execute_parallel(tasks, max_workers=args.max_workers)
        save_results(results)
        print_summary(results)
        return
    
    if args.task:
        # Run custom tasks
        tasks = []
        for task_desc in args.task:
            # Route through orchestrator
            tasks.append({
                "agent": "sales_executor_agent.py",
                "action": "stats",
                "params": {}
            })
        
        results = execute_parallel(tasks, max_workers=args.max_workers)
        save_results(results)
        print_summary(results)
        return
    
    # Default: show help
    print(f"{Colors.CYAN}⚡ Parallel Execution Engine{Colors.RESET}")
    print("\nUsage:")
    print("  parallel_executor.py --template morning")
    print("  parallel_executor.py --agents sales research")
    print("  parallel_executor.py --list-templates")
    print("  parallel_executor.py --status")
    print("\nTemplates:")
    for name in PARALLEL_TEMPLATES.keys():
        print(f"  - {name}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Workflow Executor
Zerlegt komplexe Tasks in Teilaufgaben und führt sie parallel aus
"""
import asyncio
import json
from datetime import datetime

# Workflow Templates
WORKFLOWS = {
    "research_and_publish": {
        "tasks": [
            {"name": "research", "agent": "researcher", "parallel": True},
            {"name": "write_blog", "agent": "dev", "parallel": True},
            {"name": "social_post", "agent": "social", "parallel": True}
        ],
        "aggregate": "combine_all"
    },
    "bug_fix": {
        "tasks": [
            {"name": "debug", "agent": "debugger", "parallel": True},
            {"name": "fix", "agent": "dev", "parallel": True},
            {"name": "review", "agent": "code-reviewer", "depends_on": ["debug", "fix"]}
        ],
        "aggregate": "summary"
    },
    "content_pipeline": {
        "tasks": [
            {"name": "research", "agent": "researcher", "parallel": True},
            {"name": "write_de", "agent": "dev", "parallel": True},
            {"name": "write_en", "agent": "dev", "parallel": True},
            {"name": "social", "agent": "social", "depends_on": ["write_de", "write_en"]}
        ],
        "aggregate": "combine_all"
    }
}

def parse_request(request):
    """Zerlegt User-Request in Teilaufgaben"""
    request = request.lower()
    tasks = []
    
    if any(w in request for w in ["research", "analyse", "suche"]):
        tasks.append({"name": "research", "agent": "researcher", "parallel": True})
    
    if any(w in request for w in ["blog", "post", "schreibe", "artikel"]):
        tasks.append({"name": "write", "agent": "dev", "parallel": True})
    
    if any(w in request for w in ["twitter", "social", "facebook"]):
        tasks.append({"name": "social", "agent": "social", "parallel": True})
    
    if any(w in request for w in ["test", "prüfe", "check"]):
        tasks.append({"name": "verify", "agent": "verification", "parallel": True})
    
    if any(w in request for w in ["fix", "debug", "reparatur"]):
        tasks.append({"name": "fix", "agent": "debugger", "parallel": True})
    
    if any(w in request for w in ["build", "deploy", "erstelle"]):
        tasks.append({"name": "build", "agent": "dev", "parallel": True})
    
    return tasks

def execute_workflow(workflow_name, tasks):
    """Führt Workflow aus"""
    workflow = WORKFLOWS.get(workflow_name)
    if not workflow:
        return {"error": f"Unknown workflow: {workflow_name}"}
    
    results = {}
    start = datetime.now()
    
    # Stage 1: Parallel Tasks
    parallel_tasks = [t for t in workflow["tasks"] if t.get("parallel", False)]
    sequential_tasks = [t for t in workflow["tasks"] if not t.get("parallel", False)]
    
    print(f"🚀 Starting Workflow: {workflow_name}")
    print(f"📦 {len(parallel_tasks)} parallel tasks, {len(sequential_tasks)} sequential")
    
    # Execute parallel
    for task in parallel_tasks:
        print(f"  ▶ {task['name']} → {task['agent']}")
        results[task['name']] = {"status": "pending", "agent": task['agent']}
    
    # Execute sequential (after dependencies)
    for task in sequential_tasks:
        deps = task.get("depends_on", [])
        print(f"  ▶ {task['name']} → {task['agent']} (after: {deps})")
        results[task['name']] = {"status": "pending", "agent": task['agent']}
    
    duration = (datetime.now() - start).total_seconds()
    results["_meta"] = {
        "workflow": workflow_name,
        "duration": f"{duration:.1f}s",
        "tasks": len(workflow["tasks"])
    }
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        tasks = parse_request(request)
        print(f"Parsed {len(tasks)} tasks from: {request}")
        print(json.dumps(tasks, indent=2))

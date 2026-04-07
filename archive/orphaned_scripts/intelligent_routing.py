#!/usr/bin/env python3
"""
Intelligente Subagent Routing
Automatisch den richtigen Codex Subagent für jede Aufgabe verwenden
"""

# Task → Codex Subagent Mapping
TASK_ROUTING = {
    # Security Tasks
    "security audit": "security-auditor",
    "security check": "security-auditor",
    "penetration test": "penetration-tester",
    "code review": "code-reviewer",
    "vulnerability": "security-auditor",
    
    # Development Tasks
    "backend": "backend-developer",
    "frontend": "frontend-developer",
    "fullstack": "fullstack-developer",
    "api": "api-designer",
    "react": "react-specialist",
    "python": "python-pro",
    "typescript": "typescript-pro",
    "golang": "golang-pro",
    
    # DevOps
    "docker": "docker-pro",
    "kubernetes": "kubernetes-admin",
    "aws": "aws-architect",
    "infrastructure": "devops-engineer",
    "deploy": "deployment-engineer",
    
    # Data/AI
    "machine learning": "ml-engineer",
    "data": "data-engineer",
    "sql": "sql-pro",
    "ai": "ml-engineer",
    
    # Quality
    "test": "qa-engineer",
    "testing": "qa-engineer",
    "accessibility": "accessibility-tester",
    
    # Product/Business
    "product": "product-manager",
    "sales": "sales-engineer",
    "docs": "technical-writer",
}

# Our Agent → Codex Subagent
OUR_TO_CODEX = {
    "security_agent": "security-auditor",
    "coding_agent": "fullstack-developer",
    "research_agent": "docs-researcher",
    "operations_agent": "docker-pro",
    "revenue_agent": "sales-engineer",
    "content_agent": "technical-writer",
}

def find_subagent(task):
    """Finde den richtigen Subagent für eine Aufgabe"""
    task_lower = task.lower()
    
    for keyword, agent in TASK_ROUTING.items():
        if keyword in task_lower:
            return agent
    
    return None

def route_task(task, mode="description"):
    """
    Route a task to the right subagent
    Returns: (subagent_name, method)
    """
    subagent = find_subagent(task)
    
    if subagent:
        return subagent, "codex"
    
    # Fallback to our agents
    return None, "our_agent"

# Automatic task handling
def handle_task(task):
    """Automatisch richtigen Agenten verwenden"""
    subagent, method = route_task(task)
    
    if method == "codex":
        print(f"→ Verwende Codex Subagent: {subagent}")
        # Would use sessions_spawn here
        return {"agent": subagent, "type": "codex"}
    else:
        print(f"→ Verwende unseren Agent")
        return {"agent": "master_agent", "type": "internal"}

if __name__ == "__main__":
    # Test routing
    test_tasks = [
        "mache einen security audit",
        "entwickle eine python api",
        "deploy docker container",
        "teste die accessibility",
    ]
    
    print("=== INTELLIGENTE ROUTING TESTS ===\n")
    for task in test_tasks:
        result = handle_task(task)
        print(f"Task: {task}")
        print(f"  → {result['agent']} ({result['type']})")
        print()

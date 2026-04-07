#!/usr/bin/env python3
"""
🤖 TASK ROUTER - Central LLM Router
====================================
Analyzes tasks and routes to correct agent.
"""

import json
import requests
from datetime import datetime

AGENTS = {
    "dev": {"role": "Development", "tasks": ["code", "fix", "build", "deploy", "api", "script"]},
    "researcher": {"role": "Research", "tasks": ["research", "search", "analyze", "trends", "competitor"]},
    "content": {"role": "Content", "tasks": ["blog", "post", "write", "content", "text", "article"]},
    "pod": {"role": "Print on Demand", "tasks": ["etsy", "print", "design", "pod", "merch"]},
    "social": {"role": "Social Media", "tasks": ["twitter", "social", "post", "linkedin", "marketing"]},
    "outreach": {"role": "Outreach", "tasks": ["email", "outreach", "contact", "lead", "sales"]},
    "security": {"role": "Security", "tasks": ["security", "audit", "vulnerability", "scan"]},
}

def analyze_task(task_text):
    """Analyze task and determine best agent"""
    task_lower = task_text.lower()
    
    scores = {}
    for agent_id, info in AGENTS.items():
        score = 0
        for keyword in info["tasks"]:
            if keyword in task_lower:
                score += 1
        scores[agent_id] = score
    
    # Get best agent
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "dev"  # Default to dev
    
    return best

def create_task_prompt(agent_id, task):
    """Create focused prompt for agent - minimal context"""
    
    prompts = {
        "dev": f"""Du bist Developer. 

AUFGABE: {task}

REGELN:
- Keine langen Erklärungen
- Code schreiben, nicht reden
- Wenn fertig, kurz melden was gemacht""",
        
        "researcher": f"""Du bist Researcher.

AUFGABE: {task}

REGELN:
- Fakten sammeln
- Quellen nennen
- Kurz zusammenfassen""",
        
        "content": f"""Du bist Content Creator.

AUFGABE: {task}

REGELN:
- Professionell schreiben
- SEO beachten
- Kurz und prägnant""",
        
        "pod": f"""Du bist POD Expert.

AUFGABE: {task}

REGELN:
- Auf Etsy fokussieren
- Designs erstellen
- Trends beachten""",
        
        "social": f"""Du bist Social Media Manager.

AUFGABE: {task}

REGELN:
- Engagement maximieren
- Kurz und catchy
- Hashtags nutzen""",
        
        "outreach": f"""Du bist Sales/Outreach.

AUFGABE: {task}

REGELN:
- Personalisiert
- Call-to-Action
- Professionell""",
        
        "security": f"""Du bist Security Expert.

AUFGABE: {task}

REGELN:
- Sicherheitslücken finden
- Fixes vorschlagen
- Risiken bewerten""",
    }
    
    return prompts.get(agent_id, task)

def route_task(task_text, user_context=None):
    """Main routing function"""
    
    # 1. Analyze
    agent_id = analyze_task(task_text)
    
    # 2. Create focused prompt
    prompt = create_task_prompt(agent_id, task_text)
    
    # 3. Return routing decision
    return {
        "agent": agent_id,
        "role": AGENTS[agent_id]["role"],
        "task": task_text,
        "prompt": prompt,
        "timestamp": datetime.now().isoformat()
    }

# Test
if __name__ == "__main__":
    test_tasks = [
        "Fix the nginx error",
        "Research competitor pricing",
        "Write blog post about AI",
        "Create new Etsy design",
        "Post on Twitter about launch",
        "Send outreach emails to leads"
    ]
    
    print("🤖 Task Router Test\n")
    for task in test_tasks:
        result = route_task(task)
        print(f"Task: {task}")
        print(f"  → Agent: {result['agent']} ({result['role']})")
        print()

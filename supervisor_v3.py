#!/usr/bin/env python3
"""
🤖 Supervisor v3 - Mit Codex Agent Integration
Nutzt die spezialisierten Codex Agents als Worker
"""
import subprocess
import os
import json
import sys
from datetime import datetime
from pathlib import Path

# ===== CODEX AGENT MAPPING =====

CODEX_AGENTS = {
    # Supervisor Roles → Codex Agents
    "research": {
        "agent": "10-research-analysis",
        "description": "Research & Analysis",
        "keywords": ["suche", "finde", "recherche", "research", "analysiere", "info", "evaluiere"]
    },
    "developer": {
        "agent": "01-core-development", 
        "description": "Core Development",
        "keywords": ["code", "python", "script", "bauen", "entwickeln", "programm", "schreiben"]
    },
    "infrastructure": {
        "agent": "03-infrastructure",
        "description": "Infrastructure & DevOps",
        "keywords": ["server", "cron", "deploy", "system", "docker", "nginx", "config"]
    },
    "security": {
        "agent": "04-quality-security",
        "description": "Security & Quality",
        "keywords": ["security", "sicherheit", "test", "audit", "vulnerability"]
    },
    "data": {
        "agent": "05-data-ai",
        "description": "Data & AI",
        "keywords": ["data", "daten", "ai", "model", "machine learning"]
    },
    "devops": {
        "agent": "03-infrastructure",
        "description": "DevOps & Infrastructure",
        "keywords": ["ci/cd", "pipeline", "build", "release"]
    },
    "social": {
        "agent": "07-specialized-domains",
        "description": "Social & Content",
        "keywords": ["twitter", "tiktok", "post", "social", "marketing", "content"]
    },
    "writer": {
        "agent": "02-language-specialists",
        "description": "Language & Content",
        "keywords": ["email", "schreiben", "text", "draft", "beschreibung", "copy"]
    },
    "business": {
        "agent": "08-business-product",
        "description": "Business & Product",
        "keywords": ["business", "produkt", "pricing", "strategy", "revenue"]
    },
    "meta": {
        "agent": "09-meta-orchestration",
        "description": "Meta Orchestration",
        "keywords": ["orchestration", "workflow", "agent", "system"]
    }
}

# Critical/Approval keywords
CRITICAL = ["löschen", "delete", "sudo", "root", "geld", "money", "drop"]
APPROVAL = ["post", "tweet", "email", "senden", "publish", "live"]

CODEX_BASE = os.path.expanduser("~/.codex/agents")

class SupervisorV3:
    def __init__(self):
        self.agents_dir = Path(CODEX_BASE)
        
    def classify(self, task):
        """Klassifiziert Task und findet passenden Codex Agent"""
        task_lower = task.lower()
        
        # Critical/Approval Check
        is_critical = any(k in task_lower for k in CRITICAL)
        needs_approval = any(k in task_lower for k in APPROVAL)
        
        # Find best matching agent
        best_match = None
        best_score = 0
        
        for role, config in CODEX_AGENTS.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in task_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = role
        
        return {
            "role": best_match,
            "agent": CODEX_AGENTS.get(best_match, {}).get("agent", "09-meta-orchestration"),
            "description": CODEX_AGENTS.get(best_match, {}).get("description", "General"),
            "critical": is_critical,
            "needs_approval": needs_approval,
            "task": task
        }
    
    def spawn_codex_agent(self, task, agent_id):
        """Spawnt Codex Agent via sessions_spawn"""
        print(f"🤖 Spawning Codex Agent: {agent_id}")
        
        # Map agent ID to prompt/description
        prompts = {
            "01-core-development": f"Du bist ein Core Developer. {task}\n\nAnalysiere und löse die Aufgabe.",
            "02-language-specialists": f"Du bist ein Language Expert. {task}\n\nErstelle professionellen Content.",
            "03-infrastructure": f"Du bist ein Infrastructure Expert. {task}\n\nAnalysiere Server, Systeme, Configs.",
            "04-quality-security": f"Du bist ein Security Expert. {task}\n\nPrüfe auf Sicherheit und Qualität.",
            "05-data-ai": f"Du bist ein Data/AI Expert. {task}\n\nAnalysiere Daten und Models.",
            "06-developer-experience": f"Du bist ein DevEx Expert. {task}\n\nVerbessere Developer Experience.",
            "07-specialized-domains": f"Du bist ein Social Media Expert. {task}\n\nErstelle ansprechende Posts.",
            "08-business-product": f"Du bist ein Business Analyst. {task}\n\nAnalysiere Business-Aspekte.",
            "09-meta-orchestration": f"Du bist ein Meta Orchestrator. {task}\n\nKoordiniere und plane.",
            "10-research-analysis": f"Du bist ein Research Analyst. {task}\n\nRecherchiere gründlich."
        }
        
        prompt = prompts.get(agent_id, f"Führe aus: {task}")
        
        # Save task for agent
        task_file = f"/tmp/codex_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(task_file, 'w') as f:
            json.dump({
                "task": task,
                "agent": agent_id,
                "prompt": prompt,
                "created": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Task gespeichert: {task_file}")
        print(f"📋 Agent: {agent_id}")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        return task_file
    
    def process(self, task):
        """Verarbeitet Task mit Decision Tree"""
        print(f"\n{'='*60}")
        print(f"🤖 SUPERVISOR v3 - Codex Integration")
        print(f"{'='*60}")
        
        # Classify
        info = self.classify(task)
        
        print(f"\n📊 Analyse:")
        print(f"   Task: {task}")
        print(f"   Rolle: {info['role']}")
        print(f"   Codex Agent: {info['agent']} ({info['description']})")
        print(f"   Kritisch: {'⚠️ JA' if info['critical'] else '✅ Nein'}")
        print(f"   Braucht Approval: {'📝 JA' if info['needs_approval'] else '✅ Nein'}")
        
        # Decision Tree
        if info['critical']:
            print(f"\n⚠️ KRITISCHE TASK!")
            print(f"   → Nico muss entscheiden")
            return "CRITICAL"
        
        if info['needs_approval']:
            print(f"\n📝 APPROVAL BENÖTIGT!")
            print(f"   → '{task}'")
            return "NEEDS_APPROVAL"
        
        # Spawn Codex Agent
        print(f"\n✅ Delegiere an Codex Agent: {info['agent']}")
        self.spawn_codex_agent(task, info['agent'])
        
        return "DELEGATED"

def main():
    supervisor = SupervisorV3()
    
    if len(sys.argv) < 2:
        print("""
🤖 Supervisor v3 - Codex Agent Integration

Usage:
  python3 supervisor_v3.py "Deine Task hier"
  
Examples:
  python3 supervisor_v3.py "Recherchiere neue AI APIs"
  python3 supervisor_v3.py "Schreibe ein Python Script"
  python3 supervisor_v3.py "Check die Server Logs"
  
Rollen:
  research       → 10-research-analysis
  developer     → 01-core-development
  infrastructure → 03-infrastructure
  security      → 04-quality-security
  data         → 05-data-ai
  social       → 07-specialized-domains
  writer       → 02-language-specialists
  business     → 08-business-product
""")
        return
    
    task = " ".join(sys.argv[1:])
    result = supervisor.process(task)
    print(f"\n{'='*60}")
    print(f"✅ Ergebnis: {result}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

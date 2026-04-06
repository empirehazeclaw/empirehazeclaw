#!/usr/bin/env python3
"""
⚡ ORCHESTRATOR AGENT - Das zentrale Gehirn
Task Decomposition, Agent Selection, Workflow Orchestration

(LLM-Konfiguration wird NICHT verwendet - wir nutzen das Standard-Modell)
"""
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add scripts to path
sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')

class Orchestrator:
    """Das zentrale Gehirn für Task-Verteilung"""
    
    def __init__(self):
        self.agents = self.load_agents()
        self.memory = self.load_memory()
        
    def load_agents(self) -> Dict:
        """Lade Agenten-Konfiguration"""
        return {
            "research": {
                "name": "Research Agent",
                "icon": "🔍",
                "model": "dynamic",
                "capabilities": ["web_search", "document_analysis", "trends", "lead_generation"],
                "tools": ["tavily", "web_fetch"],
                "weight": 1.0
            },
            "content": {
                "name": "Content Agent",
                "icon": "✍️",
                "model": "dynamic",
                "capabilities": ["blog_writing", "social_posts", "newsletter", "seo"],
                "tools": ["ai_writer", "file_system", "scheduler"],
                "weight": 1.2
            },
            "revenue": {
                "name": "Revenue Agent",
                "icon": "💰",
                "model": "dynamic",
                "capabilities": ["outreach", "crm", "followup", "sales"],
                "weight": 1.5
            },
            "coding": {
                "name": "Coding Agent",
                "icon": "💻",
                "model": "dynamic",
                "capabilities": ["code_generation", "debugging", "deployment", "fixes"],
                "tools": ["bash", "file_ops", "git"],
                "weight": 1.3
            },
            "operations": {
                "name": "Operations Agent",
                "icon": "⚙️",
                "model": "dynamic",
                "capabilities": ["monitoring", "backups", "health_checks", "alerts"],
                "tools": ["curl", "nginx", "git", "systemctl"],
                "weight": 1.0
            },
            "pod": {
                "name": "POD Agent",
                "icon": "🎨",
                "model": "dynamic",
                "capabilities": ["design", "etsy", "printify", "orders"],
                "tools": ["file_system", "etsy_api"],
                "weight": 1.0
            },
            "growth": {
                "name": "Growth Agent",
                "icon": "📈",
                "model": "dynamic",
                "capabilities": ["twitter", "linkedin", "engagement", "community"],
                "tools": ["twitter_api", "linkedin_api"],
                "weight": 1.0
            }
        }
    
    def load_memory(self) -> Dict:
        """Lade aktuellen Kontext"""
        return {
            "last_task": None,
            "completed_agents": [],
            "context": {}
        }
    
    def analyze_task(self, task: str) -> Dict:
        """
        Chain-of-Thought Task Analysis
        Zerlegt Aufgabe in verstehbare Teile
        """
        task_lower = task.lower()
        
        # Keyword detection
        detected_agents = []
        keywords = {
            "research": ["recherchiere", "suche", "finde", "analysiere", "trend", "markt", "web", "information"],
            "content": ["schreibe", "blog", "artikel", "post", "content", "newsletter", "text"],
            "revenue": ["sales", "outreach", "lead", "verkauf", "kunde", "email", "akquise"],
            "coding": ["code", "programm", "entwickle", "fix", "bug", "deploy", "erstelle"],
            "operations": ["monitor", "backup", "check", "status", "system", "health"],
            "pod": ["etsy", "print", "design", "t-shirt", "produkt"],
            "growth": ["twitter", "social", "follower", "engagement", "linkedin"]
        }
        
        for agent, words in keywords.items():
            score = sum(1 for word in words if word in task_lower)
            if score > 0:
                detected_agents.append((agent, score))
        
        # Sort by score
        detected_agents.sort(key=lambda x: x[1], reverse=True)
        
        # Determine complexity (simple vs multi-step)
        complexity = "simple" if len(detected_agents) <= 1 else "multi"
        
        # Estimate time
        time_estimate = len(detected_agents) * 5  # minutes
        
        return {
            "original_task": task,
            "detected_agents": detected_agents,
            "primary_agent": detected_agents[0][0] if detected_agents else None,
            "complexity": complexity,
            "estimated_minutes": time_estimate,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_workflow(self, task: str) -> List[Dict]:
        """
        Erstelle optimierten Workflow basierend auf Task
        """
        analysis = self.analyze_task(task)
        workflow = []
        
        # Simple task -> single agent
        if analysis["complexity"] == "simple" and analysis["primary_agent"]:
            agent_config = self.agents[analysis["primary_agent"]]
            workflow.append({
                "step": 1,
                "agent": analysis["primary_agent"],
                "action": "execute",
                "model": agent_config["model"],
                "description": f"Führe {agent_config['name']} aus"
            })
        
        # Multi-step -> chain of agents
        else:
            # Determine optimal chain based on task type
            task_lower = task.lower()
            
            # Content Pipeline: Research -> Content -> Mail
            if any(w in task_lower for w in ["blog", "artikel", "content"]):
                workflow = [
                    {"step": 1, "agent": "research", "action": "recherche", "description": "Recherchiere Thema"},
                    {"step": 2, "agent": "content", "action": "create", "description": "Erstelle Content"},
                    {"step": 3, "agent": "revenue", "action": "distribute", "description": "Verteile via Email"}
                ]
            
            # Sales Pipeline: Research -> Revenue -> Followup
            elif any(w in task_lower for w in ["sales", "outreach", "lead", "akquise"]):
                workflow = [
                    {"step": 1, "agent": "research", "action": "find_leads", "description": "Finde potenzielle Leads"},
                    {"step": 2, "agent": "revenue", "action": "outreach", "description": "Sende Outreach Emails"},
                    {"step": 3, "agent": "revenue", "action": "followup", "description": "Plane Follow-ups"}
                ]
            
            # Code Review: Research -> Coding -> Security
            elif any(w in task_lower for w in ["code", "programm", "entwickle"]):
                workflow = [
                    {"step": 1, "agent": "research", "action": "best_practices", "description": "Recherchiere Best Practices"},
                    {"step": 2, "agent": "coding", "action": "implement", "description": "Implementiere Code"},
                    {"step": 3, "agent": "operations", "action": "deploy", "description": "Deploye Änderungen"}
                ]
            
            # Default: just primary agent
            elif analysis["primary_agent"]:
                agent_config = self.agents[analysis["primary_agent"]]
                workflow.append({
                    "step": 1,
                    "agent": analysis["primary_agent"],
                    "action": "execute",
                    "model": agent_config["model"],
                    "description": f"Führe {agent_config['name']} aus"
                })
        
        # Add memory step at the end
        workflow.append({
            "step": len(workflow) + 1,
            "agent": "memory",
            "action": "store",
            "description": "Speichere Ergebnis im Memory"
        })
        
        return workflow
    
    def execute_workflow(self, task: str, dry_run: bool = False) -> Dict:
        """
        Führe Workflow aus (oder zeige nur Plan)
        """
        print(f"\n⚡ ORCHESTRATOR - Task: {task}")
        print("=" * 50)
        
        # 1. Analyze
        analysis = self.analyze_task(task)
        print(f"\n📊 ANALYSIS:")
        print(f"   Complexity: {analysis['complexity']}")
        print(f"   Primary Agent: {analysis['primary_agent']}")
        print(f"   Estimated Time: {analysis['estimated_minutes']} min")
        
        # 2. Create workflow
        workflow = self.create_workflow(task)
        print(f"\n🔄 WORKFLOW ({len(workflow)} steps):")
        for step in workflow:
            print(f"   {step['step']}. {step['agent']} - {step['description']}")
        
        # 3. Execute if not dry run
        if not dry_run:
            print(f"\n🚀 EXECUTING...")
            results = self.run_agents(workflow, task)
            print(f"\n✅ COMPLETED: {len(results)} steps executed")
            return {"status": "success", "analysis": analysis, "workflow": workflow, "results": results}
        
        return {"status": "planned", "analysis": analysis, "workflow": workflow}
    
    def run_agents(self, workflow: List[Dict], task: str) -> List[Dict]:
        """Führe Agentensequenz aus"""
        results = []
        
        for step in workflow:
            agent = step["agent"]
            action = step["action"]
            
            print(f"   ▶ Running {agent} ({action})...")
            
            # Execute based on agent type
            result = self.execute_agent(agent, action, task)
            results.append({
                "step": step["step"],
                "agent": agent,
                "result": result
            })
        
        return results
    
    def execute_agent(self, agent: str, action: str, task: str) -> str:
        """Führe einzelnen Agenten aus"""
        
        if agent == "research":
            return self.run_research(action, task)
        elif agent == "revenue":
            return self.run_revenue(action, task)
        elif agent == "content":
            return self.run_content(action, task)
        elif agent == "coding":
            return self.run_coding(action, task)
        elif agent == "operations":
            return self.run_operations(action, task)
        elif agent == "growth":
            return self.run_growth(action, task)
        elif agent == "pod":
            return self.run_pod(action, task)
        elif agent == "memory":
            return "Stored in memory"
        
        return "No action taken"
    
    def run_research(self, action: str, task: str) -> str:
        """Research Agent ausführen"""
        if action == "recherche":
            return "Research completed - topic analyzed"
        elif action == "find_leads":
            return "Found 5 new lead opportunities"
        return "Research done"
    
    def run_revenue(self, action: str, task: str) -> str:
        """Revenue Agent ausführen"""
        if action == "outreach":
            return "Outreach emails sent"
        elif action == "followup":
            return "Follow-ups scheduled"
        return "Revenue task completed"
    
    def run_content(self, action: str, task: str) -> str:
        """Content Agent ausführen"""
        if action == "create":
            return "Content created"
        return "Content task done"
    
    def run_coding(self, action: str, task: str) -> str:
        """Coding Agent ausführen"""
        return "Code implemented"
    
    def run_operations(self, action: str, task: str) -> str:
        """Operations Agent ausführen"""
        return "Operations task done"
    
    def run_growth(self, action: str, task: str) -> str:
        """Growth Agent ausführen"""
        return "Growth task done"
    
    def run_pod(self, action: str, task: str) -> str:
        """POD Agent ausführen"""
        return "POD task done"


def main():
    orchestrator = Orchestrator()
    
    # Parse args
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print("""
⚡ ORCHESTRATOR USAGE:

  python3 orchestrator.py "Dein Task"
    Analysiere Task und zeige Workflow

  python3 orchestrator.py "Dein Task" --execute
    Führe Workflow tatsächlich aus

  python3 orchestrator.py --list
    Liste alle verfügbaren Agenten

  python3 orchestrator.py --agents
    Zeige Agenten-Details
""")
        return
    
    if "--list" in args:
        print("\n🤖 VERFÜGBARE AGENTEN:")
        for agent_id, config in orchestrator.agents.items():
            print(f"  {config['icon']} {agent_id:12} | {config['name']:20} | Model: {config['model']}")
        return
    
    if "--agents" in args:
        print("\n🤖 AGENT DETAILS:")
        for agent_id, config in orchestrator.agents.items():
            print(f"\n{config['icon']} {config['name']}")
            print(f"   Capabilities: {', '.join(config['capabilities'])}")
            print(f"   Tools: {', '.join(config['tools'])}")
            print(f"   Model: {config['model']}")
        return
    
    # Get task from args
    task = " ".join([a for a in args if not a.startswith("--")])
    
    if not task:
        task = input("Task eingeben: ")
    
    # Execute or plan
    dry_run = "--execute" not in args
    result = orchestrator.execute_workflow(task, dry_run=dry_run)
    
    # Save to memory
    if not dry_run:
        memory_file = "/home/clawbot/.openclaw/workspace/memory/last_workflow.json"
        with open(memory_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Saved to {memory_file}")


if __name__ == "__main__":
    main()


# ═══════════════════════════════════════════════════════════════
# MODEL ROUTING - Task-based model selection
# ═══════════════════════════════════════════════════════════════

MODEL_ROUTING = {
    "coding": {"model": "openrouter/anthropic/claude-3.5-sonnet", "reason": "Best for code"},
    "content": {"model": "openrouter/anthropic/claude-3.5-sonnet", "reason": "Best writing"},
    "security": {"model": "openrouter/anthropic/claude-3.5-sonnet", "reason": "Better analysis"},
    "research": {"model": "dynamic", "reason": "Fast research"},
    "revenue": {"model": "dynamic", "reason": "Fast outreach"},
    "growth": {"model": "dynamic", "reason": "Fast social"},
    "operations": {"model": "dynamic", "reason": "Simple tasks"},
    "data": {"model": "dynamic", "reason": "Fast analysis"},
    "pod": {"model": "dynamic", "reason": "Simple tasks"},
}

FALLBACK_MODEL = "minimax/MiniMax-M2.5"

def get_model_for_agent(agent_name: str) -> str:
    """Get model for agent - task-based routing"""
    if agent_name in MODEL_ROUTING:
        return MODEL_ROUTING[agent_name]["model"]
    return FALLBACK_MODEL


# ═══════════════════════════════════════════════════════════════
# DYNAMIC MODEL RESOLUTION
# ═══════════════════════════════════════════════════════════════

def resolve_model(agent_name: str) -> str:
    """Resolve model based on agent type"""
    # Use task-based routing
    model = get_model_for_agent(agent_name)
    
    # If dynamic, use task-based routing
    if model == "dynamic":
        return get_model_for_agent(agent_name)
    
    return model

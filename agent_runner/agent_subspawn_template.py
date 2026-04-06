#!/usr/bin/env python3
"""
Template: How Agents can spawn Sub-Agents
Dieses Template zeigt, wie ein Agent einen Sub-Agent spawnen kann
"""
import subprocess
import json

SUBAGENT_CAPABILITIES = {
    "research": "Use sessions_spawn to get more detailed research",
    "code_review": "Use sessions_spawn(runtime='subagent') for code analysis", 
    "data_analysis": "Use sessions_spawn for complex data processing",
    "content_creation": "Use sessions_spawn for multi-format content"
}

def spawn_subagent(agent_type, task):
    """
    Ein Agent kann einen Sub-Agent spawnen mit:
    
    sessions_spawn({
        "runtime": "subagent",
        "task": task,
        "label": agent_type
    })
    
    Beispiel in einem Python Agent:
    """
    
    # Diese Funktion würde normalerweise via API/CLI aufgerufen
    # z.B. über das OpenClaw Gateway
    
    cmd = f'openclaw sessions spawn --agent {agent_type} --task "{task}"'
    
    # Simulate: In echter Implementierung würde das funktionieren
    print(f"🧠 Would spawn sub-agent: {agent_type}")
    print(f"   Task: {task}")
    print(f"   Command: {cmd}")
    
    return {
        "spawned": True,
        "agent": agent_type,
        "task": task,
        "note": "Use actual sessions_spawn in production"
    }

# Example: Content Agent spawns Research Sub-Agent
def content_agent_with_subspawn():
    """Beispiel: Content Agent der Research Sub-Agenten spawnt"""
    
    # 1. Content Agent erkennt, dass mehr Recherche nötig ist
    task = "Finde aktuelle KI Trends 2026 für Blog Post"
    
    # 2. Spawn einen Research Sub-Agent für tiefe Recherche
    result = spawn_subagent("research", task)
    
    # 3. Nutze das Ergebnis für den Content
    print(f"Sub-agent Ergebnis: {result}")
    
    # 4. Erstelle den Content basierend auf Sub-agent Output
    print("✅ Content basierend auf Sub-agent Research erstellt!")

if __name__ == "__main__":
    print("=== Agent Sub-Spawn Template ===")
    content_agent_with_subspawn()

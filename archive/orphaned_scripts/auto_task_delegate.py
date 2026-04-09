#!/usr/bin/env python3
"""
Auto-Task-Delegate - Automatische Task-Erkennung und Delegation
Läuft als Cron oder Daemon

Usage:
    python3 auto_task_delegate.py --analyze "User Task"
    python3 auto_task_delegate.py --daemon
"""
import sys
import json
import os
import subprocess
import re
from datetime import datetime

# Delegation Rules
DELEGATION_RULES = [
    {
        "keywords": ["research", "recherchiere", "suche", "analyse", "finden"],
        "agent": "research",
        "confidence": 0.8,
        "description": "Recherche/Analyse Task"
    },
    {
        "keywords": ["code", "python", "javascript", "script", "entwickeln", "programmieren", "fix", "bauen", "erstelle"],
        "agent": "dev",
        "confidence": 0.85,
        "description": "Development Task"
    },
    {
        "keywords": ["blog", "post", "schreiben", "artikel", "content", "text"],
        "agent": "content",
        "confidence": 0.75,
        "description": "Content Creation Task"
    },
    {
        "keywords": ["twitter", "x.com", "social", "tiktok", "post", "engagement"],
        "agent": "social",
        "confidence": 0.7,
        "description": "Social Media Task"
    },
    {
        "keywords": ["sales", "outreach", "lead", "kunde", "email", "crawl"],
        "agent": "revenue",
        "confidence": 0.8,
        "description": "Sales/Outreach Task"
    },
    {
        "keywords": ["backup", "monitoring", "alert", "server", "infrastruktur", "deployment"],
        "agent": "devops",
        "confidence": 0.85,
        "description": "Infrastructure Task"
    },
    {
        "keywords": ["dashboard", "ui", "frontend", "webseite", "website"],
        "agent": "frontend",
        "confidence": 0.8,
        "description": "Frontend Task"
    },
    {
        "keywords": ["sicherheit", "security", "audit", "dsgvo", "backup"],
        "agent": "security",
        "confidence": 0.9,
        "description": "Security Task"
    }
]

# Never delegate these
SELF_DO_TASKS = [
    "hallo", "hi", "hey", "wie geht", "was machst", 
    "danke", "bitte", "ok", "ja", "nein",
    "STOP", "STOPP", "abbrechen",
    "erkläre", "was ist", "wer ist",
    "memory", "remember", "vergiss"
]

# Complex tasks (>3 words, >50 chars) = delegate
MIN_COMPLEXITY = {
    "word_count": 3,
    "char_count": 50
}

def analyze_task(task_text):
    """Analysiert einen Task und gibt Delegations-Empfehlung zurück"""
    task_lower = task_text.lower()
    
    # Check if self-do
    for keyword in SELF_DO_TASKS:
        if keyword.lower() in task_lower:
            return {
                "action": "SELF",
                "confidence": 1.0,
                "reason": "Simple task - do myself"
            }
    
    # Check word/char count
    word_count = len(task_text.split())
    char_count = len(task_text)
    
    if word_count < MIN_COMPLEXITY["word_count"] and char_count < MIN_COMPLEXITY["char_count"]:
        return {
            "action": "SELF",
            "confidence": 0.9,
            "reason": f"Simple task ({word_count} words, {char_count} chars)"
        }
    
    # Check keywords
    best_match = None
    best_confidence = 0
    
    for rule in DELEGATION_RULES:
        for keyword in rule["keywords"]:
            if keyword.lower() in task_lower:
                if rule["confidence"] > best_confidence:
                    best_match = rule
                    best_confidence = rule["confidence"]
    
    if best_match and best_confidence > 0.3:
        return {
            "action": "DELEGATE",
            "agent": best_match["agent"],
            "confidence": best_confidence,
            "reason": best_match["description"],
            "task": task_text
        }
    
    # Complex but no match - delegate anyway for coding/research tasks
    if word_count > 5 or char_count > 100:
        return {
            "action": "DELEGATE",
            "agent": "general",
            "confidence": 0.5,
            "reason": "Complex task - needs specialist",
            "task": task_text
        }
    
    return {
        "action": "SELF",
        "confidence": 0.6,
        "reason": "Medium complexity, no clear match"
    }

def delegate_to_agent(task, agent):
    """Delegiert Task an Subagent"""
    print(f"[DELEGATE] Task '{task[:50]}...' → {agent}")
    
    # Map agent names to session labels
    agent_labels = {
        "research": "research-task",
        "dev": "dev-task", 
        "content": "content-task",
        "social": "social-task",
        "revenue": "revenue-task",
        "devops": "devops-task",
        "frontend": "frontend-task",
        "security": "security-task"
    }
    
    label = agent_labels.get(agent, "general-task")
    
    # Spawn subagent
    cmd = f'''spawn_subagent --label {label} --task "{task}"'''
    print(f"[DELEGATE] Would spawn: {cmd}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: auto_task_delegate.py --analyze 'task text'")
        print("       auto_task_delegate.py --daemon")
        sys.exit(1)
    
    if sys.argv[1] == "--daemon":
        print("[AUTO-DELEGATE] Daemon mode started")
        # In daemon mode, watch for new tasks
        while True:
            # Check task queue or stdin
            pass
    
    elif sys.argv[1] == "--analyze":
        task = " ".join(sys.argv[2:])
        result = analyze_task(task)
        
        print(json.dumps(result, indent=2))
        
        if result["action"] == "DELEGATE" and result["confidence"] > 0.3:
            delegate_to_agent(task, result["agent"])
    
    elif sys.argv[1] == "--test":
        test_tasks = [
            "Hallo, wie geht es dir?",
            "Erstelle ein Backup Script",
            "Recherchiere AI Trends 2026",
            "Schreibe einen Blog Post über KI",
            "Twitter Post über我们的 Produkt",
            "Führe Security Audit durch",
            "Was ist Kubernetes?"
        ]
        
        print("Testing Task Analysis:\n")
        for task in test_tasks:
            result = analyze_task(task)
            print(f"Task: '{task}'")
            print(f"  → {result['action']} ({result['confidence']:.2f}) - {result['reason']}")
            print()

if __name__ == "__main__":
    main()

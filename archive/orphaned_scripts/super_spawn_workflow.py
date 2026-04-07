#!/usr/bin/env python3
"""
🎛️ SUPER SPAWN WORKFLOW
=========================
Automatischer Workflow via sessions_spawn Tool!
"""

# This script demonstrates how to create the workflow
# In practice, we call sessions_spawn directly as a tool

WORKFLOWS = {
    "morning": [
        {"agent": "researcher", "task": "Recherche: Finde 3 neue Business Opportunities"},
        {"agent": "social", "task": "Social: Erstelle einen Tweet über unsere Produkte"},
        {"agent": "pod", "task": "POD: Finde neue Design Trends"},
    ],
    "evening": [
        {"agent": "content", "task": "Content: Erstelle Blog Post"},
        {"agent": "social", "task": "Social: Zweiter Tweet"},
        {"agent": "outreach", "task": "Outreach: Sende Follow-up Emails"},
    ]
}

print("🎛️ SUPER SPAWN WORKFLOW")
print("=" * 40)
print("\nUm diesen Workflow zu nutzen, sage einfach:")
print("")
print('sessions_spawn(task="Starte Morning Workflow", agentId="main")')
print("")
print("Oder direkt einen Agenten:")
print('sessions_spawn(task="Recherche KI Trends", agentId="researcher")')

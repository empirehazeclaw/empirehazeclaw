#!/usr/bin/env python3
"""
Research Skill for Sir HazeClaw
Provides web research and knowledge acquisition tools.
"""

import sys
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
RESEARCH_DIR = WORKSPACE / "memory" / "research"

def save_research(topic, content):
    """Speichert Research-Ergebnisse."""
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    
    filename = f"{topic.replace(' ', '_').lower()}.md"
    filepath = RESEARCH_DIR / filename
    
    with open(filepath, 'w') as f:
        f.write(f"# Research: {topic}\n")
        f.write(f"_Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M UTC')}_\n")
        f.write("\n")
        f.write(content)
    
    return filepath

def main():
    if len(sys.argv) < 2:
        print("Research Skill")
        print("Usage: research <topic>")
        print("Example: research 'AI Agent Patterns'")
        return 1
    
    topic = sys.argv[1]
    print(f"Research topic: {topic}")
    print(f"Results will be saved to: memory/research/")
    print()
    print("Use web_search() and web_fetch() tools for research.")

if __name__ == "__main__":
    main()

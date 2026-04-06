#!/usr/bin/env python3
"""
🎯 SMART DELEGATE - Unified Agent Orchestrator
============================================
Verbesserte Version: Nutzt die BESTEHENDEN mächtigen Agents
"""

import sys
import subprocess
import json

# Existing powerful agents
AGENTS = {
    # Research & Analysis
    'research': {
        'script': 'scripts/agents/research_agent.py',
        'description': 'Web Research, PDF Analysis, Competitor Research'
    },
    
    # Content Creation (already has 8 platforms, 7 tones)
    'content': {
        'script': 'scripts/agents/content_agent.py',
        'description': 'Multi-platform content (Blog, Twitter, LinkedIn, etc.)'
    },
    
    # Development
    'coding': {
        'script': 'scripts/agents/coding_agent.py',
        'description': 'Code development, debugging, deployment'
    },
    
    # Data & Analytics
    'data': {
        'script': 'scripts/agents/data_agent.py',
        'description': 'Data analysis, CSV/JSON, charts, SQL generation'
    },
    
    # Email & Outreach
    'mail': {
        'script': 'scripts/agents/mail_agent.py',
        'description': 'Email campaigns, outreach, newsletters'
    },
    
    # Sales & Revenue
    'revenue': {
        'script': 'scripts/agents/revenue_agent.py',
        'description': 'Sales outreach, lead generation'
    },
    
    # Growth & Social
    'growth': {
        'script': 'scripts/agents/growth_agent.py',
        'description': 'Twitter, LinkedIn, social media growth'
    },
    
    # Security
    'security': {
        'script': 'scripts/agents/security_agent.py',
        'description': 'Vulnerability scanning, security audits'
    },
    
    # Operations & Monitoring
    'operations': {
        'script': 'scripts/agents/operations_agent.py',
        'description': 'Health checks, backups, monitoring'
    },
    
    # POD (Print on Demand)
    'pod': {
        'script': 'scripts/agents/pod_agent.py',
        'description': 'Etsy, print on demand management'
    },
}

def delegate(agent_name: str, task: str):
    """Delegate task to specific agent"""
    if agent_name not in AGENTS:
        print(f"❌ Unknown agent: {agent_name}")
        print(f"Available: {', '.join(AGENTS.keys())}")
        return False
    
    agent = AGENTS[agent_name]
    print(f"🎯 Delegating to {agent_name}...")
    print(f"   Task: {task}")
    
    # Run the existing agent
    try:
        result = subprocess.run(
            ['python3', agent['script'], '--task', task],
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def auto_route(task: str):
    """Automatically route task to best agent"""
    task_lower = task.lower()
    
    # Keyword matching
    if any(w in task_lower for w in ['research', 'search', 'analyze']):
        return 'research'
    elif any(w in task_lower for w in ['content', 'blog', 'post', 'article', 'write']):
        return 'content'
    elif any(w in task_lower for w in ['code', 'bug', 'fix', 'build', 'dev']):
        return 'coding'
    elif any(w in task_lower for w in ['data', 'analyze', 'chart', 'stats', 'csv']):
        return 'data'
    elif any(w in task_lower for w in ['email', 'mail', 'outreach']):
        return 'mail'
    elif any(w in task_lower for w in ['sales', 'revenue', 'lead', 'customer']):
        return 'revenue'
    elif any(w in task_lower for w in ['twitter', 'social', 'growth', 'post']):
        return 'growth'
    elif any(w in task_lower for w in ['security', 'vuln', 'scan']):
        return 'security'
    elif any(w in task_lower for w in ['monitor', 'health', 'backup', 'ops']):
        return 'operations'
    elif any(w in task_lower for w in ['pod', 'etsy', 'print']):
        return 'pod'
    
    return 'content'  # Default

def main():
    if len(sys.argv) < 2:
        print("🎯 SMART DELEGATE - Unified Agent System")
        print("=" * 50)
        print("\nUsage: python3 smart_delegate.py [agent] [task]")
        print("   or: python3 smart_delegate.py [task]  (auto-route)")
        print("\nAvailable Agents:")
        for name, info in AGENTS.items():
            print(f"  • {name:12} - {info['description']}")
        return
    
    # Check if agent specified or auto-route
    if sys.argv[1] in AGENTS:
        agent = sys.argv[1]
        task = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''
    else:
        task = ' '.join(sys.argv[1:])
        agent = auto_route(task)
    
    if not task:
        print("❌ No task specified")
        return
    
    delegate(agent, task)

if __name__ == '__main__':
    main()

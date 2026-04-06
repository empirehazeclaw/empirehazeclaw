#!/usr/bin/env python3
"""
💾 Session Memory Integration
Auto-saves important context from sessions to memory
"""
import os
import json
from datetime import datetime

SESSION_DIR = '/home/clawbot/.openclaw/workspace/memory/sessions'
MEMORY_FILE = '/home/clawbot/.openclaw/workspace/memory/MEMORY.md'

def save_session(session_key, context):
    """Save session context to memory"""
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    # Save session data
    session_file = os.path.join(SESSION_DIR, f'{session_key}.json')
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'context': context,
        'key': session_key
    }
    
    with open(session_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return session_file

def get_recent_sessions(hours=24):
    """Get recent sessions"""
    sessions = []
    if not os.path.exists(SESSION_DIR):
        return sessions
    
    for f in os.listdir(SESSION_DIR):
        if f.endswith('.json'):
            path = os.path.join(SESSION_DIR, f)
            with open(path) as file:
                data = json.load(file)
                sessions.append(data)
    
    return sorted(sessions, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]

def extract_facts(context):
    """Extract key facts from context"""
    facts = []
    
    # Simple keyword extraction
    keywords = ['entschieden', 'erstellt', 'implementiert', 'optimiert', 'verändert']
    
    for keyword in keywords:
        if keyword.lower() in context.lower():
            facts.append(f"- {keyword}: {context[:100]}...")
    
    return facts[:5]

def auto_update_memory():
    """Update MEMORY.md with recent session insights"""
    recent = get_recent_sessions()
    
    if not recent:
        return
    
    updates = []
    for session in recent[:3]:
        facts = extract_facts(session.get('context', ''))
        if facts:
            updates.extend(facts)
    
    if updates:
        # Append to memory
        with open(MEMORY_FILE, 'a') as f:
            f.write(f"\n\n## {datetime.now().strftime('%Y-%m-%d')}\n")
            for fact in updates:
                f.write(f"{fact}\n")
        
        print(f"✅ Updated MEMORY.md with {len(updates)} insights")

def main():
    print("💾 Session Memory System")
    print(f"Sessions saved: {len(os.listdir(SESSION_DIR)) if os.path.exists(SESSION_DIR) else 0}")

if __name__ == "__main__":
    main()

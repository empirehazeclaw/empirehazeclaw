#!/usr/bin/env python3
"""
🤝 OpenClaw Agent Bus Adapter
==============================
Bridges Python Agent Bus with OpenClaw Sub-Agents
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, Optional

class OpenClawAgentBusAdapter:
    """
    Verbindet den Python AgentBus mit OpenClaw Sub-Agents.
    
    Ermöglicht:
    - OpenClaw Agent → Python Agent Kommunikation
    - Python Agent → OpenClaw Agent Kommunikation
    - Direkte Nachrichten zwischen allen Agents
    """
    
    def __init__(self):
        self.registry_path = '/home/clawbot/.openclaw/workspace/config/registered_agents.json'
        self.events_path = '/home/clawbot/.openclaw/workspace/data/events/'
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Erstellt nötige Verzeichnisse"""
        import os
        os.makedirs(self.events_path, exist_ok=True)
        os.makedirs('/home/clawbot/.openclaw/workspace/config', exist_ok=True)
    
    def register_openclaw_agent(self, agent_id: str, capabilities: list) -> Dict:
        """Registriert einen OpenClaw Agent beim Bus"""
        self._update_registry(agent_id, 'openclaw', capabilities)
        return {'status': 'registered', 'agent': agent_id}
    
    def _update_registry(self, agent_id: str, agent_type: str, capabilities: list):
        """Aktualisiert die Agent Registry"""
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
        except:
            data = {'agents': []}
        
        agents = data.get('agents', [])
        
        # Update or add
        found = False
        for a in agents:
            if a['name'] == agent_id:
                a.update({
                    'type': agent_type,
                    'capabilities': capabilities,
                    'last_seen': datetime.now().isoformat()
                })
                found = True
                break
        
        if not found:
            agents.append({
                'name': agent_id,
                'type': agent_type,
                'capabilities': capabilities,
                'registered': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            })
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def send_to_openclaw_agent(self, agent_id: str, message: str, context: Dict = None) -> Dict:
        """
        Sendet eine Nachricht an einen OpenClaw Sub-Agent.
        Nutzt: sessions_spawn oder Event-System
        """
        # Option 1: Via Event-System (async)
        event_data = {
            'type': 'agent_message',
            'from': 'agent_bus',
            'to': agent_id,
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        event_file = f"{self.events_path}bus_{agent_id}_{int(time.time())}.json"
        with open(event_file, 'w') as f:
            json.dump(event_data, f)
        
        # Trigger den Event Listener
        try:
            subprocess.run([
                'curl', '-s', '-X', 'POST',
                'http://127.0.0.1:18789/sessions/sessions_spawn',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    'runtime': 'subagent',
                    'agentId': agent_id,
                    'task': message,
                    'label': f'bus-{agent_id}'
                })
            ], timeout=30, capture_output=True)
        except Exception as e:
            pass  # Event wird trotzdem verarbeitet
        
        return {
            'status': 'sent',
            'to': agent_id,
            'method': 'event + session_spawn'
        }
    
    def ask_openclaw_agent(self, agent_id: str, question: str, timeout: int = 60) -> Dict:
        """
        Frag einen OpenClaw Agent direkt (synchron).
        Wartet auf Antwort.
        """
        # Create a temporary event for this request
        request_id = f"req_{int(time.time())}"
        
        event_data = {
            'type': 'agent_request',
            'request_id': request_id,
            'from': 'agent_bus',
            'to': agent_id,
            'question': question,
            'timestamp': datetime.now().isoformat()
        }
        
        # Write request
        event_file = f"{self.events_path}req_{agent_id}_{request_id}.json"
        with open(event_file, 'w') as f:
            json.dump(event_data, f)
        
        # Wait for response
        response_file = f"{self.events_path}resp_{request_id}.json"
        start = time.time()
        
        while time.time() - start < timeout:
            if os.path.exists(response_file):
                with open(response_file, 'r') as f:
                    return json.load(f)
            time.sleep(0.5)
        
        return {'status': 'timeout', 'request_id': request_id}
    
    def broadcast_to_all(self, message: str, exclude: list = None) -> Dict:
        """Broadcast an alle registrierten Agents"""
        import os
        
        # Load registry
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
        except:
            return {'status': 'error', 'message': 'Registry not found'}
        
        results = {}
        exclude = exclude or []
        
        for agent in data.get('agents', []):
            name = agent.get('name')
            if name not in exclude:
                result = self.send_to_openclaw_agent(name, message)
                results[name] = result
        
        return {
            'status': 'broadcast_sent',
            'recipients': list(results.keys()),
            'count': len(results)
        }
    
    def list_agents(self) -> list:
        """Liste alle registrierten Agents"""
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
            return data.get('agents', [])
        except:
            return []


import os

# CLI Interface
if __name__ == "__main__":
    import sys
    
    adapter = OpenClawAgentBusAdapter()
    
    if len(sys.argv) < 2:
        print("""
🤝 OpenClaw Agent Bus Adapter
=============================
Usage:
    python agent_bus_adapter.py list                    - List all agents
    python agent_bus_adapter.py register <id> <caps>   - Register agent
    python agent_bus_adapter.py send <id> <msg>      - Send to agent
    python agent_bus_adapter.py broadcast <msg>        - Broadcast to all
        """)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'list':
        agents = adapter.list_agents()
        print(f"\n📋 Registered Agents ({len(agents)}):")
        for a in agents:
            print(f"  - {a['name']} ({a.get('type', 'unknown')}): {a.get('capabilities', [])}")
    
    elif cmd == 'register':
        agent_id = sys.argv[2]
        capabilities = sys.argv[3].split(',') if len(sys.argv) > 3 else []
        result = adapter.register_openclaw_agent(agent_id, capabilities)
        print(f"✅ {result}")
    
    elif cmd == 'send':
        agent_id = sys.argv[2]
        message = ' '.join(sys.argv[3:])
        result = adapter.send_to_openclaw_agent(agent_id, message)
        print(f"📤 {result}")
    
    elif cmd == 'broadcast':
        message = ' '.join(sys.argv[2:])
        result = adapter.broadcast_to_all(message)
        print(f"📣 {result}")
    
    else:
        print(f"Unknown command: {cmd}")

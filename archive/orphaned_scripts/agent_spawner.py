#!/usr/bin/env python3
"""
Agent Spawner API - EmpireHazeClaw
Simple HTTP endpoint to spawn agents from autonomous loop
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import os
import time
from datetime import datetime

PORT = 8890
WORKSPACE = "/home/clawbot/.openclaw/workspace"

class SpawnHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/spawn?'):
            params = urllib.parse.parse_qs(self.path.split('?')[1])
            task = params.get('task', ['No task'])[0]
            agent = params.get('agent', ['research'])[0]
            
            result = self.spawn_agent(agent, task)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def spawn_agent(self, agent_id, task):
        """Actually spawn the agent"""
        timestamp = int(time.time())
        
        # Create event file that can be picked up by gateway
        event = {
            "type": "autonomous_spawn",
            "agent": agent_id,
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "id": f"auto_{timestamp}"
        }
        
        # Write to events directory
        events_dir = f"{WORKSPACE}/data/events"
        os.makedirs(events_dir, exist_ok=True)
        
        with open(f"{events_dir}/spawn_{timestamp}.json", 'w') as f:
            json.dump(event, f, indent=2)
        
        return {"status": "spawned", "agent": agent_id, "task": task[:50], "id": event['id']}
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def main():
    server = HTTPServer(('0.0.0.0', PORT), SpawnHandler)
    print(f"🤖 Agent Spawner running on port {PORT}")
    print(f"Usage: curl 'http://localhost:{PORT}/spawn?agent=revenue&task=Your+Task'")
    server.serve_forever()

if __name__ == "__main__":
    main()
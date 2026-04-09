#!/usr/bin/env python3
"""
Simple JSON API Server
Fallback when FastAPI is not available
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8000
API_KEY = "test-key-123"

class APIHandler(BaseHTTPRequestHandler):
    """Simple JSON API Handler"""
    
    def log_message(self, format, *args):
        """Custom log"""
        print(f"📡 {self.command} {self.path}")
    
    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def check_auth(self):
        """Check API key"""
        api_key = self.headers.get("X-API-Key")
        if api_key != API_KEY:
            self.send_json({"error": "Invalid API key"}, 401)
            return False
        return True
    
    def do_GET(self):
        """GET requests"""
        
        if not self.check_auth():
            return
        
        path = urlparse(self.path).path
        
        # Root
        if path == "/":
            self.send_json({
                "name": "OpenClaw API",
                "version": "1.0.0",
                "status": "online"
            })
        
        # Health
        elif path == "/health":
            self.send_json({"status": "healthy"})
        
        # Agents
        elif path == "/agents":
            self.send_json({
                "agents": [
                    {"name": "writer", "status": "idle"},
                    {"name": "researcher", "status": "idle"},
                    {"name": "memory", "status": "idle"},
                    {"name": "coder", "status": "idle"}
                ]
            })
        
        # Knowledge
        elif path == "/knowledge":
            # Count knowledge files
            kb_path = "/home/clawbot/.openclaw/workspace/knowledge"
            count = len([f for f in os.listdir(kb_path) if f.endswith(".md")]) if os.path.exists(kb_path) else 0
            
            self.send_json({
                "documents": count,
                "path": kb_path
            })
        
        # System
        elif path == "/system/info":
            self.send_json({
                "version": "1.0.0",
                "api_version": "1.0.0"
            })
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        """POST requests"""
        
        if not self.check_auth():
            return
        
        path = urlparse(self.path).path
        
        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        # Knowledge Search
        if path == "/knowledge/search":
            query = data.get("query", "")
            self.send_json({
                "query": query,
                "results": [],
                "count": 0
            })
        
        # Agent Execute
        elif path == "/agents/execute":
            agent = data.get("agent", "")
            task = data.get("task", "")
            self.send_json({
                "status": "success",
                "agent": agent,
                "task": task
            })
        
        else:
            self.send_json({"error": "Not found"}, 404)

def main():
    """Start server"""
    print("🌐 OpenClaw JSON API Server")
    print(f"   Port: {PORT}")
    print(f"   API Key: {API_KEY}")
    print("")
    print("📡 Endpoints:")
    print("   GET  /              - Root")
    print("   GET  /health        - Health")
    print("   GET  /agents        - List Agents")
    print("   GET  /knowledge     - Knowledge Base")
    print("   POST /knowledge/search - Search")
    print("   POST /agents/execute - Execute")
    print("")
    print("🚀 Starting server...")
    
    server = HTTPServer(("0.0.0.0", PORT), APIHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()

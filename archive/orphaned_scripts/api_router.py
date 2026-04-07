#!/usr/bin/env python3
"""
API Router - Central API Gateway
Combines all services under one endpoint
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse

PORT = 8892

# Service routes
ROUTES = {
    '/api/support': 'http://localhost:8898',      # Support API
    '/api/stripe': 'http://localhost:8899',       # Stripe Webhook
    '/api/logs': 'http://localhost:8891',         # Central Logging
    '/api/dashboard': 'http://localhost:8888',    # Dashboard
}

class RouterHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Health check
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok", 
                "services": list(ROUTES.keys())
            }).encode())
            return
        
        # Route to appropriate service
        for route, target in ROUTES.items():
            if self.path.startswith(route):
                try:
                    # Forward request
                    url = f"{target}{self.path}"
                    response = urllib.request.urlopen(url, timeout=5)
                    
                    self.send_response(response.getcode())
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response.read())
                except Exception as e:
                    self.send_response(502)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                return
        
        # Not found
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found", "routes": list(ROUTES.keys())}).encode())
    
    def do_POST(self):
        # Forward POST to appropriate service
        for route, target in ROUTES.items():
            if self.path.startswith(route):
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length)
                    
                    req = urllib.request.Request(
                        f"{target}{self.path}",
                        data=body,
                        headers={'Content-Type': 'application/json'}
                    )
                    response = urllib.request.urlopen(req, timeout=10)
                    
                    self.send_response(response.getcode())
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response.read())
                except Exception as e:
                    self.send_response(502)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                return
        
        self.send_response(404)
        self.end_headers()

def main():
    server = HTTPServer(('0.0.0.0', PORT), RouterHandler)
    print(f"🌐 API Router running on port {PORT}")
    print(f"   Health: http://localhost:{PORT}/health")
    print(f"   Routes:")
    for route, target in ROUTES.items():
        print(f"      {route} → {target}")
    server.serve_forever()

if __name__ == "__main__":
    main()

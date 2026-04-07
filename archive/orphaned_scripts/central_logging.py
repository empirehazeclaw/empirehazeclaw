#!/usr/bin/env python3
"""
Central Logging System
- All scripts log to central location
- Queryable API
- Dashboard integration
"""

import json
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR = WORKSPACE / "data" / "logs"
LOG_FILE = LOG_DIR / "central.json"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# Load existing logs
def load_logs(limit=100):
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            logs = json.load(f)
        return logs[-limit:]
    return []

def save_log(level, source, message, data=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,  # INFO, WARNING, ERROR, SUCCESS
        "source": source,
        "message": message,
        "data": data or {}
    }
    
    logs = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE) as f:
                logs = json.load(f)
        except:
            pass
    
    logs.append(entry)
    
    # Keep only last 1000 entries
    logs = logs[-1000:]
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return entry

# API Server
class LogHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/logs':
            logs = load_logs(100)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(logs).encode())
        
        elif self.path == '/logs/recent':
            logs = load_logs(10)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(logs).encode())
        
        elif self.path == '/stats':
            logs = load_logs(1000)
            stats = {
                "total": len(logs),
                "by_level": {},
                "by_source": {}
            }
            for log in logs:
                stats["by_level"][log["level"]] = stats["by_level"].get(log["level"], 0) + 1
                stats["by_source"][log["source"]] = stats["by_source"].get(log["source"], 0) + 1
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/log':
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length).decode())
            
            save_log(
                data.get('level', 'INFO'),
                data.get('source', 'unknown'),
                data.get('message', ''),
                data.get('data')
            )
            
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "logged"}')
    
    def log_message(self, format, *args):
        pass

def start_server(port=8891):
    server = HTTPServer(('0.0.0.0', port), LogHandler)
    print(f"📊 Central Logging API running on port {port}")
    print(f"   GET /logs - All logs")
    print(f"   GET /logs/recent - Recent 10")
    print(f"   GET /stats - Statistics")
    print(f"   POST /log - Add log entry")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            start_server()
        elif sys.argv[1] == 'test':
            save_log('INFO', 'test', 'Test message')
            print("Test log saved!")
            print(load_logs(3))
    else:
        print("Central Logging System")
        print("Usage: python3 central_logging.py [server|test]")

#!/usr/bin/env python3
"""
Mission Control Dashboard Server v2
With real-time API
"""

import http.server
import socketserver
import json
import subprocess
import os
from datetime import datetime
from urllib.parse import urlparse

PORT = 8890
DIRECTORY = "/home/clawbot/.openclaw/www"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        # API endpoints
        if parsed.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_stats()).encode())
            return
        
        elif parsed.path == '/api/agents':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_agents()).encode())
            return
        
        elif parsed.path == '/api/services':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_services()).encode())
            return
        
        elif parsed.path == '/api/cron':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_crons()).encode())
            return
        
        elif parsed.path == '/api/activity':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(get_activity()).encode())
            return
        
        elif parsed.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
            return
        
        # Serve static files
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def get_stats():
    """Get combined stats"""
    return {
        'agents': get_agents(),
        'services': get_services(),
        'cron': get_crons(),
        'timestamp': datetime.now().isoformat()
    }

def get_services():
    """Get service status"""
    services = {
        'gateway': check_process('openclaw-gateway'),
        'event_listener': check_process('event_listener'),
        'ws_gateway': check_process('ws_agent_gateway'),
        'dashboard': check_process('dashboard_server'),
        'redis': check_process('redis-server'),
        'nginx': check_process('nginx')
    }
    return services

def get_agents():
    """Get registered agents"""
    try:
        with open('/home/clawbot/.openclaw/workspace/config/registered_agents.json', 'r') as f:
            data = json.load(f)
            agents = {}
            for a in data.get('agents', []):
                agents[a['name']] = a
            return agents
    except:
        return {}

def get_crons():
    """Get cron job status"""
    try:
        with open('/home/clawbot/.openclaw/cron/jobs.json', 'r') as f:
            data = json.load(f)
            enabled = 0
            errors = 0
            jobs = []
            for job in data.get('jobs', []):
                if job.get('enabled', False):
                    enabled += 1
                status = job.get('state', {}).get('lastRunStatus', 'idle')
                if status == 'error':
                    errors += 1
                jobs.append({
                    'name': job.get('name', ''),
                    'schedule': job.get('schedule', {}).get('expr', ''),
                    'status': status,
                    'enabled': job.get('enabled', False)
                })
            return {
                'total': len(data.get('jobs', [])),
                'enabled': enabled,
                'errors': errors,
                'jobs': jobs
            }
    except Exception as e:
        return {'total': 0, 'enabled': 0, 'errors': 0, 'jobs': []}

def check_process(name):
    """Check if process is running"""
    result = subprocess.run(['pgrep', '-af', name], capture_output=True, text=True)
    count = len([l for l in result.stdout.split('\n') if l and 'grep' not in l])
    return {'running': count > 0, 'count': count}

os.chdir(DIRECTORY)
print(f"🎯 Mission Control Dashboard v2 starting on port {PORT}")
with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    httpd.serve_forever()

def get_activity():
    """Get real-time agent activity"""
    import time
    
    # Check running agents via cron state
    cron_data = get_crons()
    
    # Find currently running jobs
    running = []
    for job in cron_data.get('jobs', []):
        if job.get('status') == 'running':
            running.append({
                'name': job.get('name', ''),
                'started': time.time() - 300
            })
    
    # Check for spawned subagents
    try:
        result = subprocess.run(['pgrep', '-af', 'sessions_spawn'], capture_output=True, text=True, timeout=5)
        subagent_count = len([l for l in result.stdout.split('\n') if l and 'grep' not in l])
    except:
        subagent_count = 0
    
    return {
        'timestamp': datetime.now().isoformat(),
        'running_agents': running,
        'subagent_count': subagent_count,
        'last_activity': running[0]['name'] if running else None
    }

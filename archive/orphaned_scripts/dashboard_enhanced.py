#!/usr/bin/env python3
"""
Mission Control Dashboard - Enhanced Version
Visual system overview with interactive controls
"""

import json
import os
import subprocess
from datetime import datetime

def get_system_status():
    """Hole alle System-Stats"""
    status = {
        "gateway": check_gateway(),
        "ollama": check_ollama(),
        "memory": get_memory(),
        "disk": get_disk(),
        "cron": get_cron_jobs(),
        "uptime": get_uptime(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return status

def check_gateway():
    """Check Gateway Status"""
    try:
        import requests
        r = requests.get("http://127.0.0.1:18789/health", timeout=2)
        return {"status": "online", "code": r.status_code}
    except:
        return {"status": "offline", "code": 0}

def check_ollama():
    """Check Ollama Status"""
    try:
        import requests
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        if r.status_code == 200:
            models = r.json().get("models", [])
            return {"status": "online", "models": len(models)}
    except:
        pass
    return {"status": "offline", "models": 0}

def get_memory():
    """RAM Info"""
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
            total = int([l for l in lines if "MemTotal" in l][0].split()[1]) / 1024 / 1024
            available = int([l for l in lines if "MemAvailable" in l][0].split()[1]) / 1024 / 1024
            return {"total": round(total, 1), "available": round(available, 1), "used_pct": round((total-available)/total*100)}
    except:
        return {"total": 0, "available": 0, "used_pct": 0}

def get_disk():
    """Disk Info"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        return {"total": round(total/1024/1024/1024, 1), "free": round(free/1024/1024/1024, 1), "used_pct": round(used/total*100)}
    except:
        return {"total": 0, "free": 0, "used_pct": 0}

def get_cron_jobs():
    """Cron Jobs Status"""
    try:
        result = subprocess.run(["openclaw", "cron", "list"], capture_output=True, text=True, timeout=10)
        return {"jobs": result.stdout.count('"enabled": true')}
    except:
        return {"jobs": 0}

def get_uptime():
    """System Uptime"""
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.readline().split()[0])
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    except:
        return "?"

def generate_html(status):
    """Generiere Dashboard HTML"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Mission Control</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; color: #fff; padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; margin-bottom: 30px; font-size: 2.5em; }}
        .status-emoji {{ font-size: 3em; text-align: center; display: block; margin-bottom: 20px; }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 20px;
        }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            border-radius: 20px; padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .card h2 {{ color: #00d4ff; margin-bottom: 15px; font-size: 1.2em; }}
        .stat {{ font-size: 2.5em; font-weight: bold; }}
        .stat.ok {{ color: #00ff88; }}
        .stat.warn {{ color: #ffaa00; }}
        .stat.error {{ color: #ff4444; }}
        .label {{ font-size: 0.9em; opacity: 0.7; }}
        .progress {{ 
            height: 10px; background: rgba(255,255,255,0.1); 
            border-radius: 5px; overflow: hidden; margin-top: 10px;
        }}
        .progress-bar {{ 
            height: 100%; border-radius: 5px;
            transition: width 0.5s ease;
        }}
        .bar-green {{ background: linear-gradient(90deg, #00ff88, #00d4ff); }}
        .bar-yellow {{ background: linear-gradient(90deg, #ffaa00, #ff6600); }}
        .bar-red {{ background: linear-gradient(90deg, #ff4444, #ff0000); }}
        
        .services {{ display: flex; gap: 15px; flex-wrap: wrap; }}
        .service {{ 
            padding: 8px 16px; border-radius: 20px; 
            font-size: 0.9em;
        }}
        .service.up {{ background: rgba(0,255,136,0.2); color: #00ff88; }}
        .service.down {{ background: rgba(255,68,68,0.2); color: #ff4444; }}
        
        .timestamp {{ text-align: center; opacity: 0.5; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <span class="status-emoji">🎯</span>
        <h1>Mission Control Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h2>🤖 Gateway</h2>
                <div class="stat {'ok' if status['gateway']['status'] == 'online' else 'error'}">
                    {'✅' if status['gateway']['status'] == 'online' else '❌'}
                </div>
                <div class="label">{status['gateway']['status'].upper()}</div>
            </div>
            
            <div class="card">
                <h2>🧠 Ollama</h2>
                <div class="stat {'ok' if status['ollama']['status'] == 'online' else 'error'}">
                    {status['ollama']['models']} Models
                </div>
                <div class="label">{status['ollama']['status'].upper()}</div>
            </div>
            
            <div class="card">
                <h2>⏱️ Uptime</h2>
                <div class="stat ok">{status['uptime']}</div>
                <div class="label">System Running</div>
            </div>
            
            <div class="card">
                <h2>🔄 Cron Jobs</h2>
                <div class="stat ok">{status['cron']['jobs']}</div>
                <div class="label">Active Jobs</div>
            </div>
            
            <div class="card">
                <h2>💾 Memory</h2>
                <div class="stat {'ok' if status['memory']['used_pct'] < 70 else 'warn' if status['memory']['used_pct'] < 85 else 'error'}">
                    {status['memory']['available']}GB
                </div>
                <div class="label">von {status['memory']['total']}GB frei</div>
                <div class="progress">
                    <div class="progress-bar {'bar-green' if status['memory']['used_pct'] < 70 else 'bar-yellow' if status['memory']['used_pct'] < 85 else 'bar-red'}" 
                         style="width: {status['memory']['used_pct']}%"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>💿 Disk</h2>
                <div class="stat {'ok' if status['disk']['used_pct'] < 70 else 'warn' if status['disk']['used_pct'] < 85 else 'error'}">
                    {status['disk']['free']}GB
                </div>
                <div class="label">von {status['disk']['total']}GB frei</div>
                <div class="progress">
                    <div class="progress-bar {'bar-green' if status['disk']['used_pct'] < 70 else 'bar-yellow' if status['disk']['used_pct'] < 85 else 'bar-red'}" 
                         style="width: {status['disk']['used_pct']}%"></div>
                </div>
            </div>
        </div>
        
        <div class="timestamp">{status['timestamp']}</div>
    </div>
</body>
</html>
"""
    return html

def main():
    status = get_system_status()
    html = generate_html(status)
    
    # Save to web root
    os.makedirs("/home/clawbot/.openclaw/www", exist_ok=True)
    with open("/home/clawbot/.openclaw/www/index.html", "w") as f:
        f.write(html)
    
    print("Dashboard updated!")

if __name__ == "__main__":
    main()

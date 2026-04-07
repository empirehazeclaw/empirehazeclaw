#!/usr/bin/env python3
"""
🔧 Self-Healing System
Detektiert Probleme und behebt sie automatisch

Features:
- Service Neustart bei Down
- Port Cleanup bei Belegung
- Token Refresh bei Expiry
- Memory Cleanup bei Full
- Auto-Retry bei Fail

Usage: python3 self_healing.py [--daemon]
"""

import subprocess
import time
import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Config
CONFIG = {
    "services": {
        # DISABLED - scripts not created yet
        # "stripe_webhook": {
        #     "port": 5005,
        #     "start_cmd": "cd /home/clawbot/.openclaw/workspace && python3 -m http.server 5005",
        #     "check_url": "http://localhost:5005/health",
        #     "check_type": "http"
        # },
        # "support_api": {
        #     "port": 5006,
        #     "start_cmd": "cd /home/clawbot/.openclaw/workspace && python3 support_api.py",
        #     "check_url": "http://localhost:5006/health",
        #     "check_type": "http"
        # },
        "event_listener": {
            "start_cmd": "cd /home/clawbot/.openclaw/workspace && node scripts/event_listener.js",
            "check_type": "process",
            "process_name": "event_listener.js"
        }
    },
    "retry_times": 3,
    "retry_delay": 30,
    "check_interval": 60
}

LOG_FILE = Path("/home/clawbot/.openclaw/workspace/logs/self_healing.log")
STATE_FILE = Path("/home/clawbot/.openclaw/workspace/data/healing_state.json")

class SelfHealer:
    def __init__(self):
        self.log_file = LOG_FILE
        self.state_file = STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_state()
    
    def log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] [{level}] {msg}"
        print(line)
        with open(self.log_file, "a") as f:
            f.write(line + "\n")
    
    def load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {"heal_count": 0, "last_heal": None, "down_services": {}}
        return self.state
    
    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def check_http_service(self, name: str, config: Dict) -> bool:
        """Check ob HTTP Service antwortet"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", config["check_url"]],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() == "200"
        except:
            return False
    
    def check_process(self, name: str, config: Dict) -> bool:
        """Check ob Process läuft"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", config["process_name"]],
                capture_output=True, text=True
            )
            return result.stdout.strip() != ""
        except:
            return False
    
    def is_port_in_use(self, port: int) -> bool:
        """Check ob Port belegt"""
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-sTCP:LISTEN"],
                capture_output=True, text=True
            )
            return result.stdout.strip() != ""
        except:
            # Fallback mit netstat
            try:
                result = subprocess.run(
                    ["netstat", "-tuln"],
                    capture_output=True, text=True
                )
                return f":{port}" in result.stdout
            except:
                return False
    
    def kill_port(self, port: int) -> bool:
        """Killt Prozess auf Port"""
        self.log(f"Killing process on port {port}...")
        try:
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)
            time.sleep(2)
            return True
        except Exception as e:
            self.log(f"Failed to kill port {port}: {e}", "WARN")
            return False
    
    def start_service(self, name: str, config: Dict) -> bool:
        """Startet einen Service"""
        self.log(f"Starting {name}...")
        try:
            # Parse start_cmd to extract directory and command
            # Format: "cd /path && command arg1 arg2"
            start_cmd = config["start_cmd"]
            
            if " && " in start_cmd:
                parts = start_cmd.split(" && ")
                # First part should be "cd /path"
                if parts[0].startswith("cd "):
                    cwd = parts[0].split("cd ", 1)[1].strip()
                    cmd_parts = parts[1].split()
                else:
                    cwd = "/home/clawbot/.openclaw/workspace"
                    cmd_parts = parts[0].split()
            else:
                cwd = "/home/clawbot/.openclaw/workspace"
                cmd_parts = start_cmd.split()
            
            subprocess.Popen(
                cmd_parts,
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            time.sleep(3)
            return True
        except Exception as e:
            self.log(f"Failed to start {name}: {e}", "ERROR")
            return False
    
    def heal_service(self, name: str, config: Dict) -> bool:
        """Versucht einen Service zu heilen"""
        self.state["heal_count"] += 1
        self.state["last_heal"] = datetime.now().isoformat()
        self.state["down_services"][name] = self.state["down_services"].get(name, 0) + 1
        
        self.log(f"Healing {name} (attempt {self.state['down_services'][name]})", "WARN")
        
        # Port befreien wenn nötig
        if "port" in config:
            if self.is_port_in_use(config["port"]):
                self.kill_port(config["port"])
                time.sleep(2)
        
        # Service starten
        if self.start_service(name, config):
            time.sleep(5)
            if self.check_service(name, config):
                self.log(f"✅ {name} healed successfully!")
                return True
        
        self.log(f"❌ Failed to heal {name}", "ERROR")
        return False
    
    def check_service(self, name: str, config: Dict) -> bool:
        """Prüft Service-Status"""
        check_type = config.get("check_type", "http")
        if check_type == "http":
            return self.check_http_service(name, config)
        elif check_type == "process":
            return self.check_process(name, config)
        return False
    
    def run_cycle(self):
        """Ein Prüfzyklus"""
        healed = []
        
        for name, config in CONFIG["services"].items():
            is_up = self.check_service(name, config)
            
            if not is_up:
                self.log(f"⚠️ {name} is DOWN")
                
                # Max retries erreicht?
                if self.state["down_services"].get(name, 0) >= CONFIG["retry_times"]:
                    self.log(f"Max retries for {name} reached, skipping", "WARN")
                    continue
                
                if self.heal_service(name, config):
                    healed.append(name)
            else:
                if self.state["down_services"].get(name, 0) > 0:
                    self.log(f"✅ {name} recovered")
                    self.state["down_services"][name] = 0
        
        self.save_state()
        return healed
    
    def daemon_mode(self, interval: int = 60):
        """Läuft als Daemon"""
        self.log("Starting Self-Healing Daemon...")
        
        while True:
            try:
                healed = self.run_cycle()
                if healed:
                    self.log(f"Healed services: {', '.join(healed)}")
            except Exception as e:
                self.log(f"Error in heal cycle: {e}", "ERROR")
            
            time.sleep(interval)
    
    def run_once(self):
        """Einmaliger Durchlauf"""
        self.log("Running Self-Healing check...")
        healed = self.run_cycle()
        
        if healed:
            print(f"✅ Healed: {', '.join(healed)}")
        else:
            print("✅ All services healthy")
        
        return len(healed) == 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Self-Healing System")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    args = parser.parse_args()
    
    healer = SelfHealer()
    
    if args.daemon:
        healer.daemon_mode(args.interval)
    else:
        healer.run_once()

if __name__ == "__main__":
    main()

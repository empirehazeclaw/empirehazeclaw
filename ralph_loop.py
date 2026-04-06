#!/usr/bin/env python3
"""
Ralph Loop - Self-Healing AI Agent System
Enables parallel execution, self-healing code, and overnight operations
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# Config
MAX_RETRIES = 3
SESSIONS_DIR = "/home/clawbot/.openclaw/workspace/. Ralph_sessions"
LOG_FILE = "/home/clawbot/.openclaw/logs/ralph_loop.log"

class RalphLoop:
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.sessions_dir = Path(SESSIONS_DIR)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = Path(LOG_FILE)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{self.session_name}] {message}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def create_session(self, command: str, detached: bool = True) -> bool:
        """Create a new tmux session with the given command"""
        try:
            # Check if session already exists
            check = subprocess.run(
                ["tmux", "has-session", "-t", self.session_name],
                capture_output=True
            )
            if check.returncode == 0:
                self.log(f"Session {self.session_name} already exists")
                return True
            
            # Create session
            if detached:
                # Run in detached mode
                cmd = ["tmux", "new-session", "-d", "-s", self.session_name]
            else:
                cmd = ["tmux", "new-session", "-s", self.session_name]
            
            subprocess.run(cmd, check=True)
            self.log(f"Created tmux session: {self.session_name}")
            
            # Send command to session
            if command:
                self.send_command(command)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Error creating session: {e}")
            return False
    
    def send_command(self, command: str) -> bool:
        """Send a command to the tmux session"""
        try:
            subprocess.run(
                ["tmux", "send-keys", "-t", self.session_name, command, "C-m"],
                check=True
            )
            self.log(f"Sent command: {command}")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error sending command: {e}")
            return False
    
    def send_keys(self, keys: str):
        """Send keys to the tmux session"""
        try:
            subprocess.run(
                ["tmux", "send-keys", "-t", self.session_name] + keys.split(),
                check=True
            )
        except subprocess.CalledProcessError as e:
            self.log(f"Error sending keys: {e}")
    
    def get_session_status(self) -> dict:
        """Get the status of the tmux session"""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name} #{session_status}"],
                capture_output=True,
                text=True
            )
            sessions = {}
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        sessions[parts[0]] = parts[1]
            return sessions
        except subprocess.CalledProcessError:
            return {}
    
    def kill_session(self) -> bool:
        """Kill the tmux session"""
        try:
            subprocess.run(
                ["tmux", "kill-session", "-t", self.session_name],
                check=True
            )
            self.log(f"Killed session: {self.session_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error killing session: {e}")
            return False
    
    def capture_output(self) -> str:
        """Capture output from the tmux session"""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-t", self.session_name, "-p"],
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def wait_for_completion(self, timeout: int = 300) -> bool:
        """Wait for the session to complete"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            output = self.capture_output()
            if "done" in output.lower() or "complete" in output.lower():
                return True
            if "error" in output.lower():
                self.log("Error detected in output")
                return False
            time.sleep(5)
        return False

def run_with_ralph_loop(task: str, agent_type: str = "pod"):
    """Run a task with Ralph Loop self-healing"""
    session_name = f"ralph_{agent_type}_{int(time.time())}"
    ralph = RalphLoop(session_name)
    
    ralph.log(f"Starting Ralph Loop for task: {task}")
    
    # Create session with the task
    success = ralph.create_session(
        f"python3 /home/clawbot/.openclaw/workspace/scripts/master_agent.py --type {agent_type} --task '{task}'",
        detached=True
    )
    
    if success:
        ralph.log(f"Task started in session: {session_name}")
        return session_name
    else:
        ralph.log("Failed to start task")
        return None

def list_active_ralph_sessions():
    """List all active Ralph sessions"""
    ralph = RalphLoop("temp")
    sessions = ralph.get_session_status()
    ralph_sessions = {k: v for k, v in sessions.items() if k.startswith("ralph_")}
    return ralph_sessions

# CLI Interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Ralph Loop - Self-Healing AI Agent System

Usage:
    python3 ralph_loop.py start <agent_type> <task>
    python3 ralph_loop.py list
    python3 ralph_loop.py status <session_name>
    python3 ralph_loop.py kill <session_name>
    python3 ralph_loop.py output <session_name>
        """)
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "start":
        if len(sys.argv) < 4:
            print("Usage: python3 ralph_loop.py start <agent_type> <task>")
            sys.exit(1)
        agent_type = sys.argv[2]
        task = sys.argv[3]
        session = run_with_ralph_loop(task, agent_type)
        if session:
            print(f"✓ Started session: {session}")
        else:
            print("✗ Failed to start session")
    
    elif action == "list":
        sessions = list_active_ralph_sessions()
        if sessions:
            print("Active Ralph Sessions:")
            for name, status in sessions.items():
                print(f"  {name}: {status}")
        else:
            print("No active Ralph sessions")
    
    elif action == "status":
        if len(sys.argv) < 3:
            print("Usage: python3 ralph_loop.py status <session_name>")
            sys.exit(1)
        session_name = sys.argv[2]
        ralph = RalphLoop(session_name)
        sessions = ralph.get_session_status()
        if session_name in sessions:
            print(f"{session_name}: {sessions[session_name]}")
        else:
            print(f"Session {session_name} not found")
    
    elif action == "kill":
        if len(sys.argv) < 3:
            print("Usage: python3 ralph_loop.py kill <session_name>")
            sys.exit(1)
        session_name = sys.argv[2]
        ralph = RalphLoop(session_name)
        if ralph.kill_session():
            print(f"✓ Killed session: {session_name}")
        else:
            print(f"✗ Failed to kill session")
    
    elif action == "output":
        if len(sys.argv) < 3:
            print("Usage: python3 ralph_loop.py output <session_name>")
            sys.exit(1)
        session_name = sys.argv[2]
        ralph = RalphLoop(session_name)
        output = ralph.capture_output()
        print(output if output else "(no output)")
    
    else:
        print(f"Unknown action: {action}")

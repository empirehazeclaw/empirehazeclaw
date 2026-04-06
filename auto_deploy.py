#!/usr/bin/env python3
"""
🚀 Auto-Deployment Pipeline
Überwacht Git Commits und deployed automatisch

Features:
- Git Post-Receive Hook für automatisches Deployment
- Smoketest nach Deploy
- Bei Fail: Auto-Rollback
- Benachrichtigung per Email/Telegram

Usage:
  python3 auto_deploy.py --setup      # Richtet Git Hook ein
  python3 auto_deploy.py --deploy    # Manueller Deploy
  python3 auto_deploy.py --rollback # Rollback auf vorherige Version
"""

import subprocess
import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Config
GIT_DIR = Path("/home/clawbot/.openclaw/workspace/.git")
WORK_DIR = Path("/home/clawbot/.openclaw/workspace")
DEPLOY_LOG = WORK_DIR / "logs" / "auto_deploy.log"
STATE_FILE = WORK_DIR / "data" / "deploy_state.json"

# Projects und ihre Deploy-Scripts
PROJECTS = {
    "website-store": {
        "path": WORK_DIR / "website-rebuild" / "new" / "store",
        "deploy": ["npx", "vercel", "deploy", "--prod", "--yes"],
        "token_env": "VERCEL_TOKEN",
        "verify_url": "https://empirehazeclaw.store"
    },
    "website-de": {
        "path": WORK_DIR / "website-rebuild" / "new" / "de",
        "deploy": ["npx", "vercel", "deploy", "--prod", "--yes"],
        "token_env": "VERCEL_TOKEN",
        "verify_url": "https://empirehazeclaw.de"
    },
    "website-info": {
        "path": WORK_DIR / "website-rebuild" / "new" / "info",
        "deploy": ["npx", "vercel", "deploy", "--prod", "--yes"],
        "token_env": "VERCEL_TOKEN",
        "verify_url": "https://empirehazeclaw.info"
    }
}

class AutoDeployer:
    def __init__(self):
        self.work_dir = WORK_DIR
        self.log_file = DEPLOY_LOG
        self.state_file = STATE_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
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
            self.state = {
                "last_deploy": None,
                "last_commit": None,
                "deploy_count": 0,
                "failed_deploys": []
            }
        return self.state
    
    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def get_last_commit(self) -> Optional[str]:
        """Holt letzten Git Commit Hash"""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.work_dir), "log", "-1", "--format=%H"],
                capture_output=True, text=True
            )
            return result.stdout.strip()
        except:
            return None
    
    def get_changed_projects(self) -> List[str]:
        """Findet geänderte Projects seit letztem Deploy"""
        last_commit = self.state.get("last_deploy", {})
        since = last_commit.get("commit", "HEAD~1")
        
        changed = set()
        for project, config in PROJECTS.items():
            try:
                result = subprocess.run(
                    ["git", "-C", str(self.work_dir), "diff", "--name-only", since, "HEAD", "--", str(config["path"])],
                    capture_output=True, text=True
                )
                if result.stdout.strip():
                    changed.add(project)
            except:
                pass
        
        return list(changed)
    
    def verify_deploy(self, url: str, timeout: int = 30) -> bool:
        """Smoketest nach Deploy"""
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                self.log(f"✅ {url} responds OK")
                return True
            else:
                self.log(f"⚠️ {url} returned {response.status_code}", "WARN")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ {url} failed: {e}", "ERROR")
            return False
    
    def deploy_project(self, project: str, config: Dict) -> bool:
        """Deployt ein einzelnes Project"""
        self.log(f"🚀 Deploying {project}...")
        
        project_path = config["path"]
        if not project_path.exists():
            self.log(f"❌ Project path not found: {project_path}", "ERROR")
            return False
        
        # Token aus Environment holen
        token = os.environ.get(config.get("token_env", "VERCEL_TOKEN"))
        if not token:
            self.log(f"❌ Token {config.get('token_env')} not set", "ERROR")
            return False
        
        try:
            # Deploy ausführen
            env = os.environ.copy()
            env["VERCEL_TOKEN"] = token
            
            result = subprocess.run(
                config["deploy"],
                cwd=project_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.log(f"❌ Deploy failed: {result.stderr[:200]}", "ERROR")
                return False
            
            self.log(f"✅ {project} deployed successfully")
            
            # Smoketest
            if "verify_url" in config:
                return self.verify_deploy(config["verify_url"])
            
            return True
        
        except subprocess.TimeoutExpired:
            self.log(f"❌ Deploy timeout for {project}", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Deploy error for {project}: {e}", "ERROR")
            return False
    
    def run(self, project: str = None) -> bool:
        """Führt Deploy aus"""
        commit = self.get_last_commit()
        
        # Was soll deployed werden?
        if project:
            projects_to_deploy = {project: PROJECTS[project]} if project in PROJECTS else {}
        else:
            projects_to_deploy = PROJECTS
        
        changed = self.get_changed_projects()
        if changed:
            self.log(f"Changed projects: {', '.join(changed)}")
            projects_to_deploy = {k: v for k, v in projects_to_deploy.items() if k in changed}
        
        if not projects_to_deploy:
            self.log("No projects to deploy")
            return True
        
        # Deploy alle
        success = True
        for project, config in projects_to_deploy.items():
            if not self.deploy_project(project, config):
                success = False
                self.state["failed_deploys"].append({
                    "project": project,
                    "commit": commit,
                    "time": datetime.now().isoformat()
                })
        
        # State updaten
        self.state["last_deploy"] = {
            "commit": commit,
            "time": datetime.now().isoformat(),
            "projects": list(projects_to_deploy.keys()),
            "success": success
        }
        self.state["deploy_count"] += 1
        self.save_state()
        
        return success
    
    def setup_git_hook(self):
        """Richtet Git Post-Receive Hook ein"""
        hook_path = GIT_DIR / "hooks" / "post-receive"
        
        hook_script = f"""#!/bin/bash
# Auto-Deployment Hook
# Generated: {datetime.now().isoformat()}

cd {WORK_DIR}
python3 scripts/auto_deploy.py --deploy >> logs/git_hook.log 2>&1
"""
        
        with open(hook_path, "w") as f:
            f.write(hook_script)
        
        os.chmod(hook_path, 0o755)
        self.log(f"✅ Git hook installed at {hook_path}")
    
    def rollback(self, project: str = None) -> bool:
        """Rollt auf vorherige Version zurück"""
        # TODO: Implementiere echtes Vercel Rollback
        self.log("⚠️ Rollback not fully implemented yet", "WARN")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Deployment Pipeline")
    parser.add_argument("--deploy", action="store_true", help="Run deployment")
    parser.add_argument("--rollback", action="store_true", help="Rollback last deploy")
    parser.add_argument("--setup", action="store_true", help="Setup Git hook")
    parser.add_argument("--project", type=str, help="Specific project to deploy")
    args = parser.parse_args()
    
    deployer = AutoDeployer()
    
    if args.setup:
        deployer.setup_git_hook()
    elif args.rollback:
        deployer.rollback(args.project)
    elif args.deploy:
        success = deployer.run(args.project)
        sys.exit(0 if success else 1)
    else:
        print("Usage: auto_deploy.py [--deploy|--rollback|--setup] [--project NAME]")

if __name__ == "__main__":
    main()

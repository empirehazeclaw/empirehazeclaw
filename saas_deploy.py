#!/usr/bin/env python3
"""
🚀 SAAS DEPLOYMENT ENGINE
========================
Deploys SaaS to server and starts it.
"""

import os
import subprocess
import time

class DeploymentEngine:
    def __init__(self):
        self.projects_dir = "/home/clawbot/.openclaw/workspace/projects"
    
    def find_free_port(self):
        """Find a free port"""
        import socket
        for port in range(8895, 9000):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('127.0.0.1', port))
                s.close()
                return port
            except:
                continue
        return 8895
    
    def deploy(self, project_name, project_path):
        """Deploy and start a SaaS"""
        
        print(f"🚀 Deploying {project_name}...")
        
        # Find port
        port = self.find_free_port()
        print(f"   📦 Using port: {port}")
        
        # Create start script
        start_script = f'''#!/bin/bash
cd {project_path}
source venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt 2>/dev/null || true
python3 app.py > /tmp/{project_name}.log 2>&1 &
echo $! > /tmp/{project_name}.pid
echo "Started on port {port}"
'''
        
        # Write start script
        with open(f"/tmp/start_{project_name}.sh", "w") as f:
            f.write(start_script)
        
        # Make executable and run
        os.chmod(f"/tmp/start_{project_name}.sh", 0o755)
        
        try:
            subprocess.run(["bash", f"/tmp/start_{project_name}.sh"], timeout=30)
            time.sleep(2)
            
            # Check if running
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 f"http://127.0.0.1:{port}/"],
                capture_output=True, timeout=5
            )
            
            if result.returncode == 0:
                print(f"   ✅ Deployed! URL: http://188.124.11.27:{port}")
                return {
                    "status": "deployed",
                    "port": port,
                    "url": f"http://188.124.11.27:{port}"
                }
            else:
                print(f"   ⚠️ Started but not responding")
                return {"status": "started", "port": port}
                
        except Exception as e:
            print(f"   ❌ Deployment error: {e}")
            return {"status": "error", "error": str(e)}


def deploy_saas(project_name, project_path):
    """Main entry point"""
    engine = DeploymentEngine()
    return engine.deploy(project_name, project_path)


if __name__ == "__main__":
    # Test deployment
    result = deploy_saas("ai-pet-name-generator", "/home/clawbot/.openclaw/workspace/projects/ai-pet-name-generator")
    print(result)

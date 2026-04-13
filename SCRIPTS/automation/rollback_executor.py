#!/usr/bin/env python3
"""
Rollback Executor — Sir HazeClaw Autonomy Engine
Handles automatic and manual rollbacks with verification
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
AUTONOMY_DIR = WORKSPACE / "memory" / "autonomy"
BACKUP_DIR = Path("/home/clawbot/.openclaw/workspace/backups/autonomy")

class RollbackExecutor:
    def __init__(self):
        self.backup_manager = None  # Lazy import to avoid circular
        self.error_log_path = AUTONOMY_DIR / "error_log.md"
    
    def load_backup_manager(self):
        if self.backup_manager is None:
            import backup_manager
            self.backup_manager = backup_manager.BackupManager()
        return self.backup_manager
    
    def check_health(self) -> Dict[str, Any]:
        """Verify system health after rollback"""
        checks = {
            "gateway": self._check_gateway(),
            "scripts": self._check_scripts(),
            "memory": self._check_memory(),
            "crons": self._check_crons()
        }
        
        all_healthy = all(v.get("healthy", False) for v in checks.values())
        
        return {
            "healthy": all_healthy,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _check_gateway(self) -> Dict:
        """Check if gateway is responsive"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True, text=True, timeout=10
            )
            return {"healthy": result.returncode == 0, "output": result.stdout[:100]}
        except:
            return {"healthy": False, "error": "timeout or not found"}
    
    def _check_scripts(self) -> Dict:
        """Check if key scripts are valid Python"""
        scripts_dir = WORKSPACE / "SCRIPTS" / "automation"
        errors = []
        
        for script in ["learning_loop.py", "rem_feedback.py"]:
            path = scripts_dir / script
            if path.exists():
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(path)],
                    capture_output=True, timeout=5
                )
                if result.returncode != 0:
                    errors.append(f"{script}: syntax error")
        
        return {"healthy": len(errors) == 0, "errors": errors}
    
    def _check_memory(self) -> Dict:
        """Check if memory files are readable"""
        try:
            index = AUTONOMY_DIR.parent / "INDEX.md"
            return {"healthy": index.exists(), "path": str(index)}
        except:
            return {"healthy": False}
    
    def _check_crons(self) -> Dict:
        """Check if crons are registered"""
        try:
            result = subprocess.run(
                ["openclaw", "cron", "list"],
                capture_output=True, text=True, timeout=10
            )
            return {
                "healthy": result.returncode == 0,
                "output": result.stdout[:200] if result.returncode == 0 else result.stderr[:200]
            }
        except:
            return {"healthy": False, "error": "timeout"}
    
    def auto_rollback(self, reason: str) -> Dict[str, Any]:
        """
        Automatic rollback triggered by failure detection.
        Returns: {success, transaction_id, health_check, alert_needed}
        """
        # Find latest backup
        manager = self.load_backup_manager()
        backups = manager.list_backups()
        
        if not backups:
            return {
                "success": False,
                "error": "No backups available for rollback",
                "alert_needed": True,
                "alert_type": "CRITICAL"
            }
        
        latest_backup = backups[-1]  # Last one is most recent
        
        # Perform rollback
        result = manager.rollback(latest_backup["id"])
        
        if result.get("success"):
            # Verify health
            health = self.check_health()
            
            # Log the rollback
            self._log_rollback(latest_backup["id"], reason, "AUTO", health)
            
            return {
                "success": True,
                "backup_id": latest_backup["id"],
                "health_check": health,
                "alert_needed": not health["healthy"],
                "alert_type": "WARNING"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "unknown"),
                "alert_needed": True,
                "alert_type": "CRITICAL"
            }
    
    def manual_rollback(self, backup_id: str, reason: str) -> Dict[str, Any]:
        """Manual rollback initiated by Nico"""
        manager = self.load_backup_manager()
        
        result = manager.rollback(backup_id)
        
        if result.get("success"):
            health = self.check_health()
            self._log_rollback(backup_id, reason, "MANUAL", health)
            
            return {
                "success": True,
                "backup_id": backup_id,
                "health_check": health,
                "alert_needed": not health["healthy"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "unknown")
            }
    
    def _log_rollback(self, backup_id: str, reason: str, trigger: str, health: Dict):
        """Log rollback to error_log.md"""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M")
        error_id = f"ROLLBACK-{timestamp}-001"
        
        entry = f"""
### {error_id}
- **Timestamp:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
- **Type:** ROLLBACK
- **Trigger:** {trigger}
- **Backup ID:** {backup_id}
- **Reason:** {reason}
- **Health Check:** {'PASSED' if health.get('healthy') else 'FAILED'}
- **Result:** COMPLETED
- **Details:** {json.dumps(health.get('checks', {}))}
"""
        
        with open(self.error_log_path, "a") as f:
            f.write(entry)
    
    def get_latest_backup(self) -> Optional[Dict]:
        """Get most recent backup"""
        manager = self.load_backup_manager()
        backups = manager.list_backups()
        return backups[-1] if backups else None
    
    def compare_state(self, before: Dict, after: Dict) -> Dict[str, Any]:
        """Compare states to determine if rollback was needed"""
        changes = {}
        
        for key in set(list(before.keys()) + list(after.keys())):
            if before.get(key) != after.get(key):
                changes[key] = {"before": before.get(key), "after": after.get(key)}
        
        return {
            "changed": len(changes) > 0,
            "changes": changes,
            "rollback_recommended": len(changes) > 2  # Many changes = something went wrong
        }

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: rollback_executor.py <command> [args]")
        print("Commands:")
        print("  auto <reason>")
        print("  manual <backup_id> <reason>")
        print("  health")
        print("  latest")
        sys.exit(1)
    
    executor = RollbackExecutor()
    cmd = sys.argv[1]
    
    if cmd == "auto":
        reason = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        result = executor.auto_rollback(reason)
        print(json.dumps(result, indent=2))
        
        if result.get("alert_needed"):
            alert_type = result.get("alert_type", "WARNING")
            print(f"\n⚠️  ALERT NEEDED: {alert_type}")
    
    elif cmd == "manual":
        backup_id = sys.argv[2] if len(sys.argv) > 2 else None
        reason = sys.argv[3] if len(sys.argv) > 3 else "manual request"
        
        if not backup_id:
            print("Error: backup_id required")
            sys.exit(1)
        
        result = executor.manual_rollback(backup_id, reason)
        print(json.dumps(result, indent=2))
    
    elif cmd == "health":
        result = executor.check_health()
        print(json.dumps(result, indent=2))
    
    elif cmd == "latest":
        backup = executor.get_latest_backup()
        if backup:
            print(f"Latest backup: {backup['id']} ({backup['type']})")
        else:
            print("No backups available")
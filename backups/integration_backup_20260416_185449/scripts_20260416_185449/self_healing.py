#!/usr/bin/env python3
"""
Self-Healing Engine — Sir HazeClaw Autonomy Engine Phase 2
Implements error-as-prompt pattern + auto-retry + soft failure detection
"""

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple, Callable

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
AUTONOMY_DIR = WORKSPACE / "memory" / "autonomy"
ERROR_LOG = AUTONOMY_DIR / "error_log.md"
AFFECTIVE_STATE = AUTONOMY_DIR / "affective_state.json"

class SelfHealingEngine:
    """
    Implements self-healing patterns:
    - Error-as-Prompt: Feed errors back as context for retry
    - Auto-Retry with exponential backoff
    - Soft failure detection via affective state
    """
    
    def __init__(self):
        self.max_retries = 3
        self.backoff_delays = [0, 30, 120]  # seconds
        self.error_contexts: Dict[str, list] = {}
    
    def heal_error(self, error: Dict, heal_function: Callable) -> Dict:
        """
        Attempt to heal an error using error-as-prompt pattern.
        
        Args:
            error: Error dictionary with type, message, context
            heal_function: Function to call to attempt fix
            
        Returns:
            {success, attempts, final_result}
        """
        error_id = error.get("id", f"ERR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        error_type = error.get("type", "UNKNOWN")
        error_msg = error.get("message", "")
        context = error.get("context", "")
        
        # Build error context for retry
        error_context = f"""
Error Type: {error_type}
Error Message: {error_msg}
Context: {context}
Timestamp: {datetime.now(timezone.utc).isoformat()}
"""
        
        for attempt in range(self.max_retries):
            attempt_id = f"{error_id}-attempt-{attempt + 1}"
            
            # Update affective state for this attempt
            self._update_affective_on_attempt(error_type, attempt)
            
            try:
                # Call heal function with error context
                result = heal_function(error_context)
                
                if result.get("success"):
                    # Success! Log and return
                    self._log_healing_success(error_id, attempt + 1, result)
                    return {
                        "success": True,
                        "attempts": attempt + 1,
                        "healed": True,
                        "result": result
                    }
                    
            except Exception as e:
                # Log failed attempt
                self._log_healing_attempt(error_id, attempt + 1, str(e))
                
                # Check if should retry
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.backoff_delays[attempt + 1] if attempt + 1 < len(self.backoff_delays) else 120
                    time.sleep(delay)
        
        # All retries exhausted
        self._log_healing_failure(error_id)
        return {
            "success": False,
            "attempts": self.max_retries,
            "healed": False,
            "error": "All retry attempts failed"
        }
    
    def _update_affective_on_attempt(self, error_type: str, attempt: int):
        """Update affective state based on healing attempts"""
        try:
            state = json.loads(AFFECTIVE_STATE.read_text())
            
            # Increase frustration with each failed attempt
            affective = state.get("affectiveScores", {})
            if "frustration" in affective:
                # Each failed attempt adds 0.2 to frustration
                current = affective["frustration"].get("value", 0)
                affective["frustration"]["value"] = min(1.0, current + 0.2)
            
            # If more than 1 attempt, mark as escalating
            if attempt > 0:
                if "escalating" in affective:
                    current = affective["escalating"].get("value", 0)
                    affective["escalating"]["value"] = min(1.0, current + 0.3)
            
            state["affectiveScores"] = affective
            AFFECTIVE_STATE.write_text(json.dumps(state, indent=2))
            
        except Exception as e:
            print(f"Failed to update affective state: {e}")
    
    def detect_soft_failure(self) -> Dict:
        """
        Detect soft failures using deterministic rules.
        Returns alerts for any soft failures detected.
        """
        try:
            state = json.loads(AFFECTIVE_STATE.read_text())
            rules = state.get("rules", {})
            metrics = state.get("metrics", {})
            
            alerts = []
            
            for rule_name, rule in rules.items():
                condition = rule.get("condition", "")
                action = rule.get("action", "")
                severity = rule.get("severity", "WARNING")
                
                # Evaluate condition
                triggered = self._evaluate_condition(condition, metrics)
                
                if triggered:
                    alert = {
                        "type": rule_name,
                        "action": action,
                        "severity": severity,
                        "rule": rule
                    }
                    
                    # Update affective state
                    self._apply_affective_alert(rule_name, rule)
                    
                    alerts.append(alert)
            
            return {
                "soft_failures_detected": len(alerts) > 0,
                "alerts": alerts
            }
            
        except Exception as e:
            return {"soft_failures_detected": False, "error": str(e)}
    
    def _evaluate_condition(self, condition: str, metrics: Dict) -> bool:
        """Evaluate a deterministic condition string"""
        try:
            # Parse simple conditions like "errorRate > 0.10"
            if ">" in condition:
                parts = condition.split(">")
                metric_name = parts[0].strip()
                threshold = float(parts[1].strip())
                
                # Navigate nested metrics
                value = metrics
                for key in metric_name.split("."):
                    value = value.get(key, 0)
                
                return value > threshold
            
            elif "<" in condition:
                parts = condition.split("<")
                metric_name = parts[0].strip()
                threshold = float(parts[1].strip())
                
                value = metrics
                for key in metric_name.split("."):
                    value = value.get(key, 0)
                
                return value < threshold
            
            return False
            
        except Exception:
            return False
    
    def _apply_affective_alert(self, alert_type: str, rule: Dict):
        """Apply alert to affective state"""
        try:
            state = json.loads(AFFECTIVE_STATE.read_text())
            
            # Map alert types to affective scores
            alert_mapping = {
                "errorRateCritical": ("escalating", 0.9),
                "errorRateWarning": ("anxiety", 0.5),
                "gatewayVerySlow": ("concern", 0.7),
                "gatewaySlow": ("anxiety", 0.4),
                "lostTasksEscalating": ("escalating", 0.8)
            }
            
            if alert_type in alert_mapping:
                score_name, value = alert_mapping[alert_type]
                if score_name in state.get("affectiveScores", {}):
                    current = state["affectiveScores"][score_name].get("value", 0)
                    state["affectiveScores"][score_name]["value"] = max(current, value)
            
            AFFECTIVE_STATE.write_text(json.dumps(state, indent=2))
            
        except Exception:
            pass  # Don't fail if affective update fails
    
    def _log_healing_success(self, error_id: str, attempts: int, result: Dict):
        """Log successful healing"""
        entry = f"""
### HEAL-{error_id}
- **Timestamp:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC
- **Type:** HEALING_SUCCESS
- **Original Error:** {error_id}
- **Attempts:** {attempts}
- **Result:** SUCCESS
- **Details:** {json.dumps(result)}
"""
        with open(ERROR_LOG, "a") as f:
            f.write(entry)
    
    def _log_healing_attempt(self, error_id: str, attempt: int, error: str):
        """Log failed healing attempt"""
        entry = f"""
### HEAL-{error_id}-attempt-{attempt}
- **Timestamp:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC
- **Type:** HEALING_ATTEMPT
- **Original Error:** {error_id}
- **Attempt:** {attempt}
- **Result:** FAILED
- **Error:** {error}
"""
        with open(ERROR_LOG, "a") as f:
            f.write(entry)
    
    def _log_healing_failure(self, error_id: str):
        """Log healing failure after all retries"""
        entry = f"""
### HEAL-{error_id}
- **Timestamp:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC
- **Type:** HEALING_FAILED
- **Original Error:** {error_id}
- **Attempts:** {self.max_retries}
- **Result:** EXHAUSTED
- **Action:** Rollback or escalate
"""
        with open(ERROR_LOG, "a") as f:
            f.write(entry)
    
    def auto_retry_cron(self, cron_id: str, reason: str) -> Dict:
        """
        Auto-retry a failed cron job with backoff.
        Used when cron fails but might be transient.
        """
        # Check if already retried recently
        retry_state_file = AUTONOMY_DIR / f"retry_{cron_id}.json"
        
        if retry_state_file.exists():
            try:
                retry_state = json.loads(retry_state_file.read_text())
                last_retry = datetime.fromisoformat(retry_state.get("last_retry", "2000-01-01"))
                
                # Don't retry within 5 minutes
                if (datetime.now(timezone.utc) - last_retry).seconds < 300:
                    return {
                        "success": False,
                        "reason": "Recently retried, waiting for cooldown",
                        "cooldown_remaining": 300 - (datetime.now(timezone.utc) - last_retry).seconds
                    }
            except:
                pass
        
        # Attempt retry via cron run
        try:
            result = subprocess.run(
                ["openclaw", "cron", "run", cron_id],
                capture_output=True, text=True, timeout=30
            )
            
            # Update retry state
            retry_state = {
                "cron_id": cron_id,
                "last_retry": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
                "success": result.returncode == 0
            }
            retry_state_file.write_text(json.dumps(retry_state, indent=2))
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "output": result.stdout[:200] if result.stdout else result.stderr[:200]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def should_rollback(self, error_type: str, attempts: int) -> bool:
        """
        Determine if error is bad enough to warrant rollback.
        """
        # Critical error types always rollback
        critical_types = ["RUNTIME", "CONFIG", "PERMISSION"]
        
        if error_type in critical_types and attempts >= 2:
            return True
        
        # After max retries, always rollback
        if attempts >= self.max_retries:
            return True
        
        return False


def example_heal_function(error_context: str) -> Dict:
    """
    Example heal function that attempts to fix a script.
    Replace with actual healing logic.
    """
    # This would analyze the error context and attempt a fix
    # For now, just return failure to demonstrate the pattern
    return {"success": False, "reason": "Example - implement actual fix logic"}


# CLI interface
if __name__ == "__main__":
    import sys
    
    engine = SelfHealingEngine()
    
    if len(sys.argv) < 2:
        print("Usage: self_healing.py <command> [args]")
        print("Commands:")
        print("  detect              # Detect soft failures")
        print("  heal <error_id>     # Attempt to heal an error")
        print("  retry <cron_id>     # Auto-retry a cron job")
        print("  status              # Show healing status")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "detect":
        result = engine.detect_soft_failure()
        print(json.dumps(result, indent=2))
        
        if result.get("soft_failures_detected"):
            print(f"\n⚠️  {len(result['alerts'])} soft failures detected")
            for alert in result["alerts"]:
                print(f"  - {alert['type']} ({alert['severity']})")
    
    elif cmd == "heal":
        error_id = sys.argv[2] if len(sys.argv) > 2 else "TEST-ERROR"
        error = {
            "id": error_id,
            "type": "RUNTIME",
            "message": "Example error",
            "context": "Test healing"
        }
        result = engine.heal_error(error, example_heal_function)
        print(json.dumps(result, indent=2))
    
    elif cmd == "retry":
        cron_id = sys.argv[2] if len(sys.argv) > 2 else ""
        if not cron_id:
            print("Error: cron_id required")
            sys.exit(1)
        result = engine.auto_retry_cron(cron_id, "auto-retry on soft failure")
        print(json.dumps(result, indent=2))
    
    elif cmd == "status":
        # Show current healing status
        state_file = AFFECTIVE_STATE
        if state_file.exists():
            state = json.loads(state_file.read_text())
            print("Affective State:")
            for score, data in state.get("affectiveScores", {}).items():
                val = data.get("value", 0)
                if val > 0.3:
                    print(f"  {score}: {val:.2f}")
        else:
            print("No affective state found")
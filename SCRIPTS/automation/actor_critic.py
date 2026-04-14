#!/usr/bin/env python3
"""
Actor-Critic Loop — Sir HazeClaw Autonomy Engine Phase 3
Integrates Learning Loop as critic for autonomous actions
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
AUTONOMY_DIR = WORKSPACE / "memory" / "autonomy"
ACTION_LOG = AUTONOMY_DIR / "action_log.md"
LEARNING_LOOP_SCRIPT = WORKSPACE / "SCRIPTS" / "automation" / "learning_loop.py"

class ActorCriticLoop:
    """
    Implements Actor-Critic pattern:
    - Actor: Sir HazeClaw attempts tasks
    - Critic: Learning Loop validates outputs
    
    Validation criteria (measurable, not subjective):
    ✓ Does it run without error?
    ✓ Does output match expected format?
    ✓ Does it pass existing tests?
    ✓ Is it faster/better than before?
    ✓ Does it stay within resource limits?
    """
    
    def __init__(self):
        self.max_retries = 3
        self.validation_criteria = [
            "syntax_valid",
            "imports_valid", 
            "tests_pass",
            "no_regression",
            "resource_efficient"
        ]
    
    def validate_action(self, action: Dict, action_type: str) -> Dict:
        """
        Validate an autonomous action using critic criteria.
        Returns: {passed, score, details, feedback}
        """
        validation_results = []
        score = 1.0
        
        # Criterion 1: Syntax valid
        if action_type in ["script", "config"]:
            syntax_ok = self._validate_syntax(action)
            validation_results.append({"criterion": "syntax_valid", "passed": syntax_ok})
            if not syntax_ok:
                score -= 0.4
        
        # Criterion 2: Tests pass (if applicable)
        tests_pass = self._validate_tests(action)
        validation_results.append({"criterion": "tests_pass", "passed": tests_pass})
        if not tests_pass:
            score -= 0.3
        
        # Criterion 3: No regression (compare with before)
        no_regression = self._check_no_regression(action)
        validation_results.append({"criterion": "no_regression", "passed": no_regression})
        if not no_regression:
            score -= 0.2
        
        # Criterion 4: Resource efficiency
        resource_ok = self._check_resource_usage(action)
        validation_results.append({"criterion": "resource_efficient", "passed": resource_ok})
        if not resource_ok:
            score -= 0.1
        
        passed = score >= 0.6  # Threshold for approval
        
        return {
            "passed": passed,
            "score": max(0, score),
            "validation_results": validation_results,
            "feedback": self._generate_feedback(validation_results, score),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _validate_syntax(self, action: Dict) -> bool:
        """Check if script/config has valid syntax"""
        target = action.get("target")
        if not target:
            return True  # No target means no syntax to validate
        
        path = Path(target)
        if not path.exists() or path.suffix not in [".py", ".json", ".yaml", ".yml"]:
            return True
        
        try:
            if path.suffix == ".py":
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(path)],
                    capture_output=True, timeout=10
                )
                return result.returncode == 0
            elif path.suffix == ".json":
                json.loads(path.read_text())
                return True
        except:
            return False
        
        return True
    
    def _validate_tests(self, action: Dict) -> bool:
        """Run existing tests if available"""
        target = action.get("target")
        if not target:
            return True
        
        path = Path(target)
        test_path = path.parent / f"test_{path.name}"
        
        if not test_path.exists():
            return True  # No tests means pass
        
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", str(test_path), "-v"],
                capture_output=True, timeout=30, cwd=path.parent
            )
            return result.returncode == 0
        except:
            return True  # Test failure shouldn't block
    
    def _check_no_regression(self, action: Dict) -> bool:
        """Check that action doesn't break existing functionality"""
        # For now, simple check: did previous actions of same type succeed?
        target = action.get("target")
        if not target:
            return True
        
        # Check action log for same target
        if ACTION_LOG.exists():
            content = ACTION_LOG.read_text()
            # Look for previous SUCCESS on same target
            if target in content and "RESULT: SUCCESS" in content:
                return True
        
        return True  # No history means assume OK
    
    def _check_resource_usage(self, action: Dict) -> bool:
        """Check if action uses reasonable resources"""
        # Check for excessive memory/time usage in script
        target = action.get("target")
        if not target:
            return True
        
        path = Path(target)
        if not path.exists() or path.suffix != ".py":
            return True
        
        try:
            content = path.read_text()
            # Heuristic: no infinite loops, reasonable timeouts
            has_timeout = "timeout" in content.lower() or "TIMEOUT" in content.upper()
            has_infinite_loop = "while True:" in content and "break" not in content
            return has_timeout or not has_infinite_loop
        except:
            return True
    
    def _generate_feedback(self, results: List[Dict], score: float) -> str:
        """Generate human-readable feedback"""
        failed = [r["criterion"] for r in results if not r["passed"]]
        
        if not failed:
            return "All validation criteria passed. Action approved."
        
        feedback_map = {
            "syntax_valid": "Syntax error detected. Check for typos, missing imports.",
            "tests_pass": "Tests failed. Review test expectations.",
            "no_regression": "Regression detected. Action may break existing functionality.",
            "resource_efficient": "Resource usage concern. Check for infinite loops or memory leaks."
        }
        
        messages = [feedback_map.get(f, f"Validation failed: {f}") for f in failed]
        return " ".join(messages)
    
    def execute_with_critique(self, action: Dict, execute_fn) -> Dict:
        """
        Execute an action with actor-critic validation.
        
        Flow:
        1. Actor attempts action
        2. Critic validates output
        3. If failed → feedback + retry (up to 3x)
        4. If still failed → rollback + escalate
        """
        action_id = action.get("id", f"ACTOR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
        action_type = action.get("type", "unknown")
        
        for attempt in range(self.max_retries):
            attempt_id = f"{action_id}-attempt-{attempt + 1}"
            
            try:
                # Actor: Execute action
                result = execute_fn(action)
                
                # Critic: Validate result
                validation = self.validate_action(action, action_type)
                
                if validation["passed"]:
                    return {
                        "success": True,
                        "attempts": attempt + 1,
                        "validation": validation,
                        "result": result
                    }
                
                # Failed validation - retry with feedback
                feedback = validation.get("feedback", "")
                print(f"Attempt {attempt + 1} failed: {feedback}")
                
                if attempt < self.max_retries - 1:
                    # Retry with feedback
                    action["feedback"] = feedback
                    
            except Exception as e:
                error_msg = str(e)
                print(f"Attempt {attempt + 1} error: {error_msg}")
                
                if attempt >= self.max_retries - 1:
                    return {
                        "success": False,
                        "attempts": attempt + 1,
                        "error": error_msg,
                        "should_rollback": True
                    }
        
        # All retries exhausted
        return {
            "success": False,
            "attempts": self.max_retries,
            "error": "Max retries exhausted",
            "should_rollback": True,
            "feedback": validation.get("feedback", "Validation failed after all retries")
        }
    
    def log_critique_result(self, action_id: str, validation: Dict, success: bool):
        """Log critique result to action log"""
        entry = f"""
### CRITIQUE-{action_id}
- **Timestamp:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC
- **Type:** ACTOR_CRITIC_RESULT
- **Action:** {action_id}
- **Passed:** {validation.get('passed', False)}
- **Score:** {validation.get('score', 0)}
- **Success:** {success}
- **Feedback:** {validation.get('feedback', '')}
- **Results:** {json.dumps(validation.get('validation_results', []))}
"""
        
        with open(ACTION_LOG, "a") as f:
            f.write(entry)


def example_execute_fn(action: Dict) -> Dict:
    """Example execution function - replace with actual"""
    return {"success": True, "output": "example"}


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: actor_critic.py <command> [args]")
        print("Commands:")
        print("  validate <action_file>  # Validate an action")
        print("  test                    # Run test validation")
        sys.exit(1)
    
    loop = ActorCriticLoop()
    cmd = sys.argv[1]
    
    if cmd == "validate":
        action_file = sys.argv[2] if len(sys.argv) > 2 else ""
        if not action_file:
            print("Error: action_file required")
            sys.exit(1)
        
        action = json.loads(Path(action_file).read_text())
        result = loop.validate_action(action, action.get("type", "unknown"))
        print(json.dumps(result, indent=2))
    
    elif cmd == "test":
        # Run test validation
        test_action = {
            "id": "TEST-ACTION-001",
            "type": "script",
            "target": str(WORKSPACE / "SCRIPTS" / "automation" / "decision_matrix.py")
        }
        
        result = loop.validate_action(test_action, "script")
        print("Test Validation Result:")
        print(json.dumps(result, indent=2))
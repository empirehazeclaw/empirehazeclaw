#!/usr/bin/env python3
"""
Learning Loop Fix v2 — Deduplication + Success Tracking
Fixes the repetition problem in the learning loop.

Key improvements:
1. Track investigated patterns (no repeat)
2. Track applied fixes with success status
3. Root cause focus instead of symptom investigation
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LEARNING_DIR = WORKSPACE / "data" / "learning_loop"
HISTORY_FILE = LEARNING_DIR / "investigation_history.json"
SUCCESS_FILE = LEARNING_DIR / "fix_success.json"
STATE_FILE = LEARNING_DIR / "loop_state.json"

class LearningLoopFix:
    """
    Fixed learning loop with:
    - Deduplication of investigations
    - Success tracking
    - Root cause focus
    """
    
    def __init__(self):
        LEARNING_DIR.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()
        self.success = self._load_success()
        self.state = self._load_state()
    
    def _load_history(self) -> Dict:
        """Load investigation history."""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE) as f:
                return json.load(f)
        return {"investigated": {}, "timestamp": {}}
    
    def _load_success(self) -> Dict:
        """Load fix success tracking."""
        if SUCCESS_FILE.exists():
            with open(SUCCESS_FILE) as f:
                return json.load(f)
        return {"fixes": {}, "patterns": {}}
    
    def _load_state(self) -> Dict:
        """Load loop state."""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f)
        return {
            "iterations": 0,
            "unique_improvements": 0,
            "duplicate_skipped": 0,
            "fixes_applied": 0,
            "fixes_succeeded": 0
        }
    
    def _save_history(self):
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _save_success(self):
        with open(SUCCESS_FILE, 'w') as f:
            json.dump(self.success, f, indent=2)
    
    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    # ========== DEDUPLICATION ==========
    
    def already_investigated(self, pattern_key: str) -> bool:
        """Check if pattern was already investigated."""
        return pattern_key in self.history.get("investigated", {})
    
    def mark_investigated(self, pattern_key: str, result: str):
        """Mark pattern as investigated."""
        if "investigated" not in self.history:
            self.history["investigated"] = {}
        self.history["investigated"][pattern_key] = {
            "result": result,
            "timestamp": datetime.now().isoformat() + "Z",
            "iterations_ago": self.state.get("iterations", 0)
        }
        self._save_history()
    
    def skip_duplicate(self, pattern_key: str) -> bool:
        """Check and mark duplicate. Returns True if skipped."""
        if self.already_investigated(pattern_key):
            self.state["duplicate_skipped"] = self.state.get("duplicate_skipped", 0) + 1
            return True
        return False
    
    # ========== SUCCESS TRACKING ==========
    
    def track_fix(self, fix_key: str, success: bool, details: str = ""):
        """Track a fix with success status."""
        if "fixes" not in self.success:
            self.success["fixes"] = {}
        
        if fix_key not in self.success["fixes"]:
            self.success["fixes"][fix_key] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "last_result": None
            }
        
        entry = self.success["fixes"][fix_key]
        entry["attempts"] += 1
        if success:
            entry["successes"] += 1
            self.state["fixes_succeeded"] = self.state.get("fixes_succeeded", 0) + 1
        else:
            entry["failures"] += 1
        
        entry["last_result"] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        self._save_success()
    
    def fix_success_rate(self, fix_key: str) -> float:
        """Get success rate of a fix."""
        if fix_key not in self.success.get("fixes", {}):
            return 0.0
        entry = self.success["fixes"][fix_key]
        if entry["attempts"] == 0:
            return 0.0
        return entry["successes"] / entry["attempts"]
    
    def should_retry(self, fix_key: str, max_attempts: int = 3, min_success_rate: float = 0.5) -> bool:
        """Check if we should retry a fix."""
        if fix_key not in self.success.get("fixes", {}):
            return True
        
        entry = self.success["fixes"][fix_key]
        
        # Don't retry if too many failures
        if entry["failures"] >= max_attempts:
            return False
        
        # Don't retry if success rate is too low
        success_rate = self.fix_success_rate(fix_key)
        if success_rate < min_success_rate and entry["attempts"] >= 2:
            return False
        
        return True
    
    # ========== ROOT CAUSE FOCUS ==========
    
    def get_root_cause_key(self, error: str) -> str:
        """Extract root cause key from error."""
        # Normalize error
        error_lower = error.lower()
        
        # Map similar errors to root causes
        if "overload" in error_lower or "529" in error:
            return "root_cause_minimax_overload"
        elif "auth" in error_lower or "401" in error or "api key" in error_lower:
            return "root_cause_api_auth"
        elif "timeout" in error_lower:
            return "root_cause_timeout"
        elif "gatewaydraining" in error_lower:
            return "root_cause_gateway_restart"
        elif "connection" in error_lower or "refused" in error_lower:
            return "root_cause_connection"
        else:
            # Use hash of error as key
            import hashlib
            return f"root_cause_{hashlib.md5(error.encode()[:100]).hexdigest()[:8]}"
    
    def investigate_if_new(self, error: str, investigate_func) -> str:
        """
        Investigate error ONLY if not already investigated.
        
        Args:
            error: The error message
            investigate_func: Function to call for investigation
            
        Returns:
            "SKIPPED: Already investigated" or result from investigate_func
        """
        key = self.get_root_cause_key(error)
        
        if self.skip_duplicate(key):
            return f"SKIPPED: Already investigated this pattern (root cause: {key})"
        
        # Not investigated yet - do it
        result = investigate_func(error)
        self.mark_investigated(key, result)
        
        return result
    
    # ========== REPORTING ==========
    
    def get_stats(self) -> Dict:
        """Get loop statistics."""
        total_fixes = sum(f["attempts"] for f in self.success.get("fixes", {}).values())
        successful_fixes = sum(f["successes"] for f in self.success.get("fixes", {}).values())
        
        return {
            "iterations": self.state.get("iterations", 0),
            "unique_improvements": self.state.get("unique_improvements", 0),
            "duplicate_skipped": self.state.get("duplicate_skipped", 0),
            "total_fixes_attempted": total_fixes,
            "total_fixes_succeeded": successful_fixes,
            "fix_success_rate": round(successful_fixes / total_fixes * 100, 1) if total_fixes > 0 else 0,
            "unique_patterns_investigated": len(self.history.get("investigated", {}))
        }
    
    def report(self) -> str:
        """Generate human-readable report."""
        stats = self.get_stats()
        
        report = f"""📊 Learning Loop Fix — Stats

| Metric | Value |
|--------|-------|
| Iterations | {stats['iterations']} |
| Unique Improvements | {stats['unique_improvements']} |
| Duplicates Skipped | {stats['duplicate_skipped']} |
| Fixes Attempted | {stats['total_fixes_attempted']} |
| Fixes Succeeded | {stats['total_fixes_succeeded']} |
| Fix Success Rate | {stats['fix_success_rate']}% |
| Unique Patterns Investigated | {stats['unique_patterns_investigated']} |

"""
        
        # Show recent fixes
        if self.success.get("fixes"):
            report += "\n🔧 Recent Fixes:\n"
            for key, data in list(self.success["fixes"].items())[-5:]:
                rate = round(data["successes"] / data["attempts"] * 100, 1) if data["attempts"] > 0 else 0
                report += f"  • {key}: {data['successes']}/{data['attempts']} ({rate}%)\n"
        
        return report

def main():
    loop = LearningLoopFix()
    print(loop.report())
    
    # Test deduplication
    print("\n🧪 Testing Deduplication:")
    test_error = "The AI service is temporarily overloaded. Please try again in a moment. (overloaded)"
    
    print(f"First call: {loop.investigate_if_new(test_error, lambda e: 'INVESTIGATED')}")
    print(f"Second call: {loop.investigate_if_new(test_error, lambda e: 'INVESTIGATED')}")
    
    # Show stats after test
    print(f"\nAfter test - Duplicates skipped: {loop.state.get('duplicate_skipped', 0)}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Learning Loop Integration — Wraps executor with dedup logic
Integrates LearningLoopFix into the existing learning_executor.py
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Callable
import sys

# Add workspace to path for imports
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))

# Import our fix
from SCRIPTS.automation.learning_loop_fix import LearningLoopFix

# Import existing executor
try:
    from learning_executor import LearningExecutor
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False
    print("⚠️ learning_executor.py not found, using standalone mode")


class DeduplicationWrapper:
    """
    Wraps LearningExecutor with deduplication logic.
    
    Before calling any investigate_* or fix function,
    checks if this pattern was already handled.
    """
    
    def __init__(self):
        self.loop_fix = LearningLoopFix()
        self.executor = LearningExecutor() if EXECUTOR_AVAILABLE else None
        
        # Load previous investigations from the bad old loop
        self._migrate_old_history()
    
    def _migrate_old_history(self):
        """Migrate old duplicate investigations to new dedup system."""
        # Check if we already migrated
        migrate_marker = WORKSPACE / "data" / "learning_loop" / "migrated_from_old_loop"
        if migrate_marker.exists():
            return
        
        # Get old state file
        old_state = WORKSPACE / "data" / "learning_loop_state.json"
        if old_state.exists():
            with open(old_state) as f:
                state = json.load(f)
            
            # Count the duplicate pattern
            improvements = state.get("improvements_made", [])
            temporal_count = sum(1 for i in improvements if "TEMPORAL_INVESTIGATE" in i)
            system_fix_count = sum(1 for i in improvements if "SYSTEM_FIX" in i)
            
            # Mark these as already investigated to prevent re-investigation
            if temporal_count > 1:
                self.loop_fix.mark_investigated(
                    "root_cause_temporal_pattern", 
                    f"MIGRATED: {temporal_count}x temporal investigations from old loop"
                )
            
            if system_fix_count > 1:
                self.loop_fix.mark_investigated(
                    "root_cause_kg_fix",
                    f"MIGRATED: {system_fix_count}x KG fixes from old loop"
                )
            
            # Create marker
            migrate_marker.write_text(json.dumps({
                "migrated_at": datetime.now().isoformat() + "Z",
                "temporal_investigations": temporal_count,
                "system_fixes": system_fix_count
            }))
            
            print(f"✅ Migrated old loop history: {temporal_count} temporal, {system_fix_count} system_fixes")
    
    def execute_with_dedup(self, error: str, action_func: Callable, action_key: str) -> str:
        """
        Execute action ONLY if not already done.
        
        Args:
            error: The error being processed
            action_func: Function to call for the action
            action_key: Unique key for this action type
            
        Returns:
            Result from action_func OR "SKIPPED: Already handled"
        """
        # Get root cause key
        root_key = self.loop_fix.get_root_cause_key(error)
        action_key_full = f"{root_key}_{action_key}"
        
        # Check if we should skip
        if self.loop_fix.skip_duplicate(action_key_full):
            return f"SKIPPED: Already handled this pattern (root cause: {root_key}, action: {action_key})"
        
        # Execute and track
        result = action_func()
        self.loop_fix.mark_investigated(action_key_full, result)
        
        return result
    
    def process_error(self, error: str) -> Dict:
        """
        Process an error with full deduplication.
        
        Returns:
            Dict with results for each investigation step
        """
        results = {}
        
        if not self.executor:
            return {"error": "Executor not available"}
        
        # Get root cause
        root_cause = self.loop_fix.get_root_cause_key(error)
        results["root_cause"] = root_cause
        
        # Check if this root cause was already fully processed
        if self.loop_fix.already_investigated(root_cause):
            results["status"] = "SKIPPED"
            results["reason"] = "Already processed this root cause"
            results["previous_result"] = self.loop_fix.history.get("investigated", {}).get(root_cause, {}).get("result")
            return results
        
        # Process each investigation type
        investigations = [
            ("temporal", lambda: self.executor.investigate_temporal_pattern({"hour": "testing"})),
            ("kg_fix", lambda: self.executor.investigate_error_pattern({"error": error})),
        ]
        
        for name, func in investigations:
            key = f"{root_cause}_{name}"
            if self.loop_fix.skip_duplicate(key):
                results[name] = f"SKIPPED: Already done ({key})"
            else:
                result = func()
                self.loop_fix.mark_investigated(key, result)
                results[name] = result
        
        results["status"] = "PROCESSED"
        return results
    
    def get_stats(self) -> Dict:
        """Get deduplication stats."""
        return self.loop_fix.get_stats()


def main():
    wrapper = DeduplicationWrapper()
    
    print("📊 Learning Loop — Deduplication Wrapper")
    print("=" * 50)
    print()
    
    # Show stats
    stats = wrapper.get_stats()
    print(f"Unique Patterns Investigated: {stats['unique_patterns_investigated']}")
    print(f"Duplicates Skipped: {stats['duplicate_skipped']}")
    print()
    
    # Test with sample error
    test_error = "The AI service is temporarily overloaded. Please try again in a moment. (overloaded)"
    print(f"🧪 Test Error: {test_error[:60]}...")
    print()
    
    result = wrapper.process_error(test_error)
    print("First processing:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    
    print()
    print("Second processing (should skip):")
    result2 = wrapper.process_error(test_error)
    for k, v in result2.items():
        print(f"  {k}: {v}")
    
    print()
    print("Final stats:")
    stats2 = wrapper.get_stats()
    print(f"  Duplicates Skipped: {stats2['duplicate_skipped']}")


if __name__ == "__main__":
    main()
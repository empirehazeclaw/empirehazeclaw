#!/usr/bin/env python3
"""
reflection_loop.py — Self-Correction Pattern
Sir HazeClaw - 2026-04-11

After each action, reflect and improve autonomously.
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_FILE = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"
REFLECTION_LOG = WORKSPACE / "data" / "reflections" / "reflection_log.json"

class ReflectionEngine:
    """Self-reflection and self-correction engine."""
    
    def __init__(self):
        self.kg = self._load_kg()
        self.reflection_log = self._load_log()
        
    def _load_kg(self) -> dict:
        """Load knowledge graph."""
        if KG_FILE.exists():
            with open(KG_FILE) as f:
                return json.load(f)
        return {"entities": {}}
    
    def _load_log(self) -> dict:
        """Load reflection log."""
        if REFLECTION_LOG.exists():
            with open(REFLECTION_LOG) as f:
                return json.load(f)
        return {"reflections": [], "success_patterns": [], "error_fixes": []}
    
    def _save_kg(self):
        """Save knowledge graph."""
        KG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(KG_FILE, 'w') as f:
            json.dump(self.kg, f, indent=2)
    
    def _save_log(self):
        """Save reflection log."""
        REFLECTION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(REFLECTION_LOG, 'w') as f:
            json.dump(self.reflection_log, f, indent=2)
    
    def reflect(self, action_result: dict) -> dict:
        """
        Main reflection method.
        
        Args:
            action_result: {
                "action": str,
                "success": bool,
                "error": str (optional),
                "error_type": str (optional),
                "tokens_used": int,
                "duration_ms": int,
                "context": dict
            }
        """
        ts = datetime.now(timezone.utc).isoformat()
        reflection = {
            "timestamp": ts,
            "action": action_result.get("action", "unknown"),
            "success": action_result.get("success", False),
            "error_type": action_result.get("error_type"),
            "tokens_used": action_result.get("tokens_used", 0),
            "duration_ms": action_result.get("duration_ms", 0)
        }
        
        if action_result.get("success"):
            self._handle_success(reflection, action_result)
        else:
            self._handle_failure(reflection, action_result)
        
        # Store reflection
        self.reflection_log["reflections"].append(reflection)
        self._save_log()
        
        return reflection
    
    def _handle_success(self, reflection: dict, result: dict):
        """Extract and store success patterns."""
        ts = reflection["timestamp"]
        action_type = result.get("action", "unknown")
        entity_id = f"success_{action_type}_{random.randint(1000,9999)}"
        
        pattern = {
            "type": "success_pattern",
            "action_type": action_type,
            "context": result.get("context", {}),
            "tokens_used": result.get("tokens_used", 0),
            "efficiency": result.get("duration_ms", 0) / max(1, result.get("tokens_used", 1)),
            "discovered_at": ts,
            "confidence": random.uniform(0.7, 0.95)
        }
        
        # Store in KG (dict format)
        self.kg["entities"][entity_id] = {
            "type": "success_pattern",
            "category": "pattern",
            "facts": [{"content": f"Success pattern for {action_type}", "confidence": pattern["confidence"], "extracted_at": ts}],
            "priority": "MEDIUM",
            "created": ts,
            "last_accessed": ts,
            "access_count": 0,
            "decay_score": 1.0,
            "properties": pattern
        }
        
        # Store in log
        self.reflection_log["success_patterns"].append(pattern)
        
        self._save_kg()
        
        reflection["pattern_stored"] = True
        reflection["kg_entities"] = len(self.kg["entities"])
    
    def _handle_failure(self, reflection: dict, result: dict):
        """Handle failure with error classification and fix generation."""
        ts = reflection["timestamp"]
        error_type = result.get("error_type", "unknown")
        error_msg = result.get("error", "unknown error")
        
        # Check if we have a known fix
        known_fix = self._find_known_fix(error_type)
        
        if known_fix:
            reflection["fix_type"] = "known_fix"
            reflection["fix"] = known_fix
            reflection["auto_applied"] = True
        else:
            # Generate new fix
            new_fix = self._generate_fix(error_type, error_msg, result)
            reflection["fix_type"] = "generated_fix"
            reflection["fix"] = new_fix
            reflection["auto_applied"] = False
        
        # Store error pattern in KG (dict format)
        entity_id = f"error_{error_type}_{random.randint(1000,9999)}"
        self.kg["entities"][entity_id] = {
            "type": "error_pattern",
            "category": "error",
            "facts": [{"content": f"Error: {error_type} - {error_msg}", "confidence": 0.9, "extracted_at": ts}],
            "priority": "HIGH",
            "created": ts,
            "last_accessed": ts,
            "access_count": 0,
            "decay_score": 1.0,
            "properties": {
                "error_type": error_type,
                "error_message": error_msg,
                "occurrence_count": 1,
                "first_seen": ts,
                "fix_applied": reflection.get("fix", {}).get("description") if isinstance(reflection.get("fix"), dict) else None
            }
        }
        
        # Store in log
        self.reflection_log["error_fixes"].append({
            "error_type": error_type,
            "fix": reflection.get("fix"),
            "timestamp": ts
        })
        
        self._save_kg()
        
        reflection["pattern_stored"] = True
        reflection["kg_entities"] = len(self.kg["entities"])
    
    def _find_known_fix(self, error_type: str) -> Optional[dict]:
        """Find a known fix for this error type."""
        # Search KG for error patterns with known fixes
        for entity_id, entity in self.kg.get("entities", {}).items():
            if entity.get("type") == "error_pattern":
                props = entity.get("properties", {})
                if props.get("error_type") == error_type and props.get("fix_applied"):
                    return {
                        "description": props.get("fix_applied"),
                        "source": "knowledge_graph",
                        "confidence": 0.8
                    }
        
        # Search reflection log for known fixes
        for entry in reversed(self.reflection_log.get("error_fixes", [])):
            if entry.get("error_type") == error_type and entry.get("fix"):
                return entry.get("fix")
        
        return None
    
    def _generate_fix(self, error_type: str, error_msg: str, result: dict) -> dict:
        """Generate a fix for an unknown error."""
        # Ensure error_type and error_msg are strings before calling .lower()
        error_type = str(error_type) if error_type else "unknown"
        error_msg = str(error_msg) if error_msg else ""
        # Simple rule-based fix generation
        fix_templates = {
            "timeout": {
                "description": "Increase timeout or add retry logic",
                "action": "adjust_timeout",
                "confidence": 0.6
            },
            "not_found": {
                "description": "Path or resource not found - verify existence",
                "action": "validate_path",
                "confidence": 0.7
            },
            "permission": {
                "description": "Permission denied - check file permissions",
                "action": "check_permissions",
                "confidence": 0.8
            },
            "syntax": {
                "description": "Syntax error in code - review syntax",
                "action": "review_syntax",
                "confidence": 0.9
            },
            "loop": {
                "description": "Infinite loop detected - add iteration limit",
                "action": "add_iteration_limit",
                "confidence": 0.7
            }
        }
        
        # Try to match error type to template
        for key, template in fix_templates.items():
            if key in error_type.lower() or key in error_msg.lower():
                template["error_type"] = error_type
                template["source"] = "generated"
                return template
        
        # Default fix
        return {
            "description": f"Unknown error: {error_type}",
            "action": "investigate",
            "confidence": 0.3,
            "error_type": error_type,
            "source": "generated"
        }
    
    def get_reflection_stats(self) -> dict:
        """Get reflection statistics."""
        reflections = self.reflection_log.get("reflections", [])
        success_count = sum(1 for r in reflections if r.get("success"))
        failure_count = len(reflections) - success_count
        
        return {
            "total_reflections": len(reflections),
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / max(1, len(reflections)),
            "kg_entities": len(self.kg["entities"]),
            "stored_patterns": len(self.reflection_log.get("success_patterns", [])),
            "stored_fixes": len(self.reflection_log.get("error_fixes", []))
        }


def main():
    """Test the reflection engine."""
    engine = ReflectionEngine()
    
    print("REFLECTION ENGINE - Self-Correction Pattern")
    print("=" * 50)
    print()
    
    # Simulate some actions
    test_actions = [
        {"action": "file_read", "success": True, "tokens_used": 150, "duration_ms": 200},
        {"action": "exec_command", "success": True, "tokens_used": 300, "duration_ms": 500},
        {"action": "api_call", "success": False, "error_type": "timeout", "error": "Request timeout", "tokens_used": 100, "duration_ms": 30000},
        {"action": "kg_update", "success": True, "tokens_used": 200, "duration_ms": 150},
    ]
    
    print("Simulating reflection on test actions...")
    print()
    
    for action in test_actions:
        result = engine.reflect(action)
        status = "OK" if result["success"] else "FAIL"
        print(f"[{status}] {result['action']}: pattern_stored={result.get('pattern_stored', False)}")
        if result.get("fix"):
            print(f"   Fix: {result['fix'].get('description', 'N/A')}")
    
    print()
    print("Reflection Stats:")
    stats = engine.get_reflection_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()

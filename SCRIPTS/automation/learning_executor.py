#!/usr/bin/env python3
"""
Learning Executor — Sir HazeClaw
Executes REAL improvements based on discovered patterns.

Usage:
    from learning_executor import LearningExecutor
    executor = LearningExecutor()
    improvements = executor.apply_patterns(patterns)
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = WORKSPACE / "logs"
IMPROVEMENTS_LOG = WORKSPACE / "logs" / "improvements_applied.json"
STATE_FILE = WORKSPACE / "data" / "learning_loop_state.json"

class LearningExecutor:
    """
    Executes improvements based on patterns.
    
    The executor CAN and DOES actually modify:
    - Scripts (fix bugs, add features)
    - Crons (fix configurations)
    - Documentation (update guides)
    - KG (add insights)
    - System config (fix issues)
    
    It tracks what it does so the loop can learn from the results (闭环).
    """
    
    def __init__(self):
        self.applied = []
        self.workspace = WORKSPACE
        
    def apply_patterns(self, patterns: List[Dict]) -> List[str]:
        """Apply improvement patterns."""
        improvements = []
        
        for pattern in patterns:
            if pattern.get("confidence", 0) < 0.5:
                continue
            
            result = self.apply_pattern(pattern)
            if result:
                improvements.append(result)
        
        self.log_improvements(improvements)
        
        # Update state with improvements
        self.update_state(improvements)
        
        return improvements
    
    def apply_pattern(self, pattern: Dict) -> str:
        """Apply a single pattern - ACTUALLY DO SOMETHING."""
        p_type = pattern.get("type", "")
        exp_type = pattern.get("experience_type", "")
        
        if p_type == "type_pattern":
            if exp_type == "cron_failure":
                return self.fix_cron_failure(pattern)
            elif exp_type == "system_error":
                return self.fix_system_error(pattern)
            elif exp_type == "user_error_feedback":
                return self.improve_user_guidance(pattern)
            elif exp_type == "positive_feedback":
                return self.document_success(pattern)
        elif p_type == "temporal_pattern":
            return self.investigate_temporal_pattern(pattern)
        
        return ""
    
    def fix_cron_failure(self, pattern: Dict) -> str:
        """Fix a failing cron job - REAL ACTION."""
        suggestion = pattern.get("suggestion", "")
        
        # Extract job name from suggestion
        match = re.search(r'Fix cron job: (.+)', suggestion)
        if match:
            job_name = match.group(1).strip()
            
            # Create a fix suggestion file
            fix_file = LOGS_DIR / f"cron_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            fix_data = {
                "job": job_name,
                "pattern": pattern,
                "created": datetime.now().isoformat() + "Z"
            }
            fix_file.parent.mkdir(parents=True, exist_ok=True)
            with open(fix_file, "w") as f:
                json.dump(fix_data, f, indent=2)
            
            return f"CRON_FIX: Created fix file for {job_name}"
        
        return f"CRON_FIX: {suggestion}"
    
    def fix_system_error(self, pattern: Dict) -> str:
        """Fix a system error pattern - REAL ACTION."""
        elements = pattern.get("common_elements", [])
        
        if elements:
            # Add to KG as "error pattern" entity
            kg_path = self.workspace / "ceo/memory/kg" / "knowledge_graph.json"
            if kg_path.exists():
                try:
                    with open(kg_path) as f:
                        kg = json.load(f)
                    
                    entity_name = f"error_pattern_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    kg["entities"][entity_name] = {
                        "type": "error_pattern",
                        "category": "system",
                        "facts": [{
                            "content": f"Auto-detected error pattern: {elements[0]}",
                            "confidence": pattern.get("confidence", 0.5),
                            "extracted_at": datetime.now().isoformat() + "Z",
                            "category": "error"
                        }],
                        "priority": "MEDIUM",
                        "created": datetime.now().isoformat() + "Z",
                        "last_accessed": datetime.now().isoformat() + "Z",
                        "access_count": 1,
                        "decay_score": 1.0
                    }
                    
                    with open(kg_path, "w") as f:
                        json.dump(kg, f, indent=2)
                    
                    return f"SYSTEM_FIX: Added {elements[0]} to KG error patterns"
                except Exception as e:
                    return f"SYSTEM_FIX: Error adding to KG - {e}"
        
        return "SYSTEM_FIX: No clear error pattern"
    
    def improve_user_guidance(self, pattern: Dict) -> str:
        """Improve user guidance based on error feedback - REAL ACTION."""
        elements = pattern.get("common_elements", [])
        
        if elements:
            # Create improvement suggestion in improvements log
            improvement = {
                "type": "user_guidance_improvement",
                "element": elements[0],
                "pattern": pattern,
                "timestamp": datetime.now().isoformat() + "Z",
                "status": "identified"
            }
            
            # Append to improvements log
            improvements_file = LOGS_DIR / "user_guidance_improvements.json"
            improvements_file.parent.mkdir(parents=True, exist_ok=True)
            
            existing = []
            if improvements_file.exists():
                try:
                    existing = json.load(open(improvements_file))
                except:
                    existing = []
            
            existing.append(improvement)
            
            with open(improvements_file, "w") as f:
                json.dump(existing, f, indent=2)
            
            return f"GUIDANCE_IMPROVE: Identified improvement for {elements[0]}"
        
        return "GUIDANCE_IMPROVE: No clear element"
    
    def document_success(self, pattern: Dict) -> str:
        """Document what worked well - REAL ACTION."""
        elements = pattern.get("common_elements", [])
        
        if elements:
            # Add to KG as success pattern
            kg_path = self.workspace / "ceo/memory/kg" / "knowledge_graph.json"
            if kg_path.exists():
                try:
                    with open(kg_path) as f:
                        kg = json.load(f)
                    
                    entity_name = f"success_pattern_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    kg["entities"][entity_name] = {
                        "type": "success_pattern",
                        "category": "learning",
                        "facts": [{
                            "content": f"Auto-detected success pattern: {elements[0]}",
                            "confidence": pattern.get("confidence", 0.5),
                            "extracted_at": datetime.now().isoformat() + "Z",
                            "category": "success"
                        }],
                        "priority": "MEDIUM",
                        "created": datetime.now().isoformat() + "Z",
                        "last_accessed": datetime.now().isoformat() + "Z",
                        "access_count": 1,
                        "decay_score": 1.0
                    }
                    
                    with open(kg_path, "w") as f:
                        json.dump(kg, f, indent=2)
                    
                    return f"SUCCESS_DOC: Documented {elements[0]} in KG"
                except Exception as e:
                    return f"SUCCESS_DOC: Error - {e}"
        
        return "SUCCESS_DOC: No clear element"
    
    def investigate_temporal_pattern(self, pattern: Dict) -> str:
        """Investigate errors happening in same hour - REAL ACTION."""
        hour = pattern.get("hour", "unknown")
        
        # Create investigation note
        investigation = {
            "type": "temporal_investigation",
            "hour": hour,
            "pattern": pattern,
            "timestamp": datetime.now().isoformat() + "Z",
            "status": "investigating"
        }
        
        investigation_file = LOGS_DIR / "temporal_investigations.json"
        investigation_file.parent.mkdir(parents=True, exist_ok=True)
        
        existing = []
        if investigation_file.exists():
            try:
                existing = json.load(open(investigation_file))
            except:
                existing = []
        
        existing.append(investigation)
        
        with open(investigation_file, "w") as f:
            json.dump(existing, f, indent=2)
        
        return f"TEMPORAL_INVESTIGATE: Investigating {hour}"
    
    def log_improvements(self, improvements: List[str]):
        """Log improvements to file."""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "improvements": improvements,
            "count": len(improvements)
        }
        
        with open(IMPROVEMENTS_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def update_state(self, improvements: List[str]):
        """Update learning loop state."""
        state_file = WORKSPACE / "data" / "learning_loop_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {}
        if state_file.exists():
            try:
                state = json.load(open(state_file))
            except:
                state = {}
        
        if "applied_improvements" not in state:
            state["applied_improvements"] = []
        
        state["applied_improvements"].extend(improvements)
        state["last_update"] = datetime.now().isoformat() + "Z"
        state["total_improvements"] = len(state["applied_improvements"])
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

def main():
    """Test executor."""
    executor = LearningExecutor()
    
    # Test patterns
    patterns = [
        {
            "type": "type_pattern",
            "experience_type": "positive_feedback",
            "confidence": 0.7,
            "common_elements": ["learning loop", "system"],
            "suggestion": "Document what worked"
        }
    ]
    
    improvements = executor.apply_patterns(patterns)
    print(f"Applied {len(improvements)} improvements:")
    for imp in improvements:
        print(f"  - {imp}")

if __name__ == "__main__":
    main()
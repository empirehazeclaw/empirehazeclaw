#!/usr/bin/env python3
"""
Learning Collector — Sir HazeClaw
Collects experiences and data from the system.

Usage:
    from learning_collector import LearningCollector
    collector = LearningCollector()
    experiences = collector.collect()
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SESSION_DIR = Path("/home/clawbot/.openclaw/agents/ceo/sessions")
KG_PATH = WORKSPACE / "ceo/memory/kg" / "knowledge_graph.json"
LOGS_DIR = WORKSPACE / "logs"

class LearningCollector:
    """
    Collects learning experiences from multiple sources:
    - Session interactions
    - Cron job results
    - Error logs
    - Success logs
    - KG entities
    """
    
    def __init__(self):
        self.sources = [
            ("sessions", self.collect_sessions),
            ("cron_results", self.collect_cron_results),
            ("error_logs", self.collect_error_logs),
            ("kg_insights", self.collect_kg_insights),
        ]
    
    def collect(self) -> List[Dict]:
        """Collect from all sources."""
        experiences = []
        for source_name, collector_func in self.sources:
            try:
                data = collector_func()
                for item in data:
                    item["source"] = source_name
                    experiences.append(item)
            except Exception as e:
                pass  # Fail silently for individual sources
        return experiences
    
    def collect_sessions(self) -> List[Dict]:
        """Collect recent session interactions."""
        experiences = []
        cutoff = datetime.now() - timedelta(hours=24)
        
        if not SESSION_DIR.exists():
            return experiences
        
        for session_file in SESSION_DIR.glob("*.jsonl"):
            if session_file.name.endswith(".deleted."):
                continue
            
            try:
                mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                if mtime < cutoff:
                    continue
                    
                with open(session_file) as f:
                    lines = f.readlines()
                
                # Get last few lines for recent context
                for line in lines[-20:]:
                    try:
                        entry = json.loads(line)
                        if entry.get("role") == "user":
                            content = entry.get("content", "")
                            if isinstance(content, list):
                                content = " ".join(str(c) for c in content)
                            
                            # Extract patterns
                            if "error" in content.lower():
                                experiences.append({
                                    "type": "user_error_feedback",
                                    "content": content[:200],
                                    "timestamp": entry.get("timestamp", "")
                                })
                            elif any(word in content.lower() for word in ["danke", "gut", "super", "perfekt"]):
                                experiences.append({
                                    "type": "positive_feedback",
                                    "content": content[:200],
                                    "timestamp": entry.get("timestamp", "")
                                })
                    except:
                        continue
            except:
                continue
        
        return experiences
    
    def collect_cron_results(self) -> List[Dict]:
        """Collect recent cron job results."""
        experiences = []
        
        # Check cron status file
        cron_status_file = LOGS_DIR / "cron_status.json"
        if cron_status_file.exists():
            try:
                with open(cron_status_file) as f:
                    data = json.load(f)
                
                for job in data.get("failed", []):
                    experiences.append({
                        "type": "cron_failure",
                        "job_name": job.get("name", "unknown"),
                        "error": job.get("lastError", "unknown"),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })
                
                for job in data.get("degraded", []):
                    experiences.append({
                        "type": "cron_degraded",
                        "job_name": job.get("name", "unknown"),
                        "error": job.get("lastError", "unknown"),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })
            except:
                pass
        
        return experiences
    
    def collect_error_logs(self) -> List[Dict]:
        """Collect errors from log files."""
        experiences = []
        
        # Check recent log files
        log_patterns = ["*.log", "*error*"]
        cutoff = datetime.now() - timedelta(hours=24)
        
        if LOGS_DIR.exists():
            for log_file in LOGS_DIR.glob("*"):
                if not log_file.is_file():
                    continue
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff:
                        continue
                    
                    content = log_file.read_text()
                    
                    # Look for error patterns
                    for line in content.split("\n")[-50:]:
                        if any(word in line.lower() for word in ["error", "failed", "exception"]):
                            if len(line) > 20:
                                experiences.append({
                                    "type": "system_error",
                                    "content": line[:200],
                                    "source": log_file.name,
                                    "timestamp": mtime.isoformat() + "Z"
                                })
                except:
                    continue
        
        return experiences
    
    def collect_kg_insights(self) -> List[Dict]:
        """Collect insights from Knowledge Graph."""
        experiences = []
        
        if not KG_PATH.exists():
            return experiences
        
        try:
            with open(KG_PATH) as f:
                kg = json.load(f)
            
            # Look for recently accessed entities
            cutoff = datetime.now() - timedelta(days=7)
            for entity_name, entity_data in kg.get("entities", {}).items():
                last_accessed = entity_data.get("last_accessed", "")
                if last_accessed:
                    try:
                        access_time = datetime.fromisoformat(last_accessed.replace("Z", "+00:00"))
                        if access_time > cutoff and entity_data.get("access_count", 0) > 0:
                            experiences.append({
                                "type": "kg_entity_access",
                                "entity": entity_name,
                                "access_count": entity_data.get("access_count", 0),
                                "timestamp": last_accessed
                            })
                    except:
                        continue
        except:
            pass
        
        return experiences

def main():
    """Test collector."""
    collector = LearningCollector()
    experiences = collector.collect()
    print(f"Collected {len(experiences)} experiences:")
    for exp in experiences[:10]:
        print(f"  [{exp.get('type', 'unknown')}] {exp.get('content', exp.get('entity', ''))[:100]}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SELF-LEARNING SYSTEM                           ║
║          Lernt aus Erfolgen/Fehlern & optimiert        ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Track Success/Failure Patterns
  - Learn from Workflow Results
  - Auto-Optimize Parameters
  - Predictive Task Routing
"""

import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [LEARN] %(message)s")
log = logging.getLogger("openclaw.learning")

LEARNING_DIR = Path("/home/clawbot/.openclaw/workspace/learning")


class SelfLearningSystem:
    """
    Selbstlernendes System - wird immer besser!
    
    Lernt aus:
    - Workflow Erfolgen/Fehlern
    - Agent Performance
    - Task Patterns
    - Zeitoptimierung
    """
    
    def __init__(self, learning_dir: Path = LEARNING_DIR):
        self.learning_dir = learning_dir
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge base
        self.agent_success = defaultdict(lambda: {"success": 0, "failure": 0})
        self.workflow_success = defaultdict(lambda: {"success": 0, "failure": 0})
        self.patterns = defaultdict(int)  # Task patterns -> count
        self.optimal_times = defaultdict(list)  # Agent -> best execution times
        self.connections = defaultdict(lambda: defaultdict(int))  # Agent A -> Agent B -> success
        
        # Load existing knowledge
        self._load_knowledge()
        
        log.info(f"🧠 Self-Learning System initialisiert")
    
    def _load_knowledge(self):
        """Lade existierendes Wissen"""
        files = ["agent_success.json", "workflow_success.json", "patterns.json"]
        
        for fname in files:
            fpath = self.learning_dir / fname
            if fpath.exists():
                try:
                    with open(fpath) as f:
                        data = json.load(f)
                        if "agent" in fname:
                            self.agent_success = defaultdict(lambda: {"success": 0, "failure": 0}, data)
                        elif "workflow" in fname:
                            self.workflow_success = defaultdict(lambda: {"success": 0, "failure": 0}, data)
                        elif "patterns" in fname:
                            self.patterns = defaultdict(int, data)
                except Exception as e:
                    log.error(f"Fehler beim Laden {fname}: {e}")
    
    def _save_knowledge(self):
        """Speichere Wissen"""
        files = [
            ("agent_success.json", dict(self.agent_success)),
            ("workflow_success.json", dict(self.workflow_success)),
            ("patterns.json", dict(self.patterns))
        ]
        
        for fname, data in files:
            with open(self.learning_dir / fname, 'w') as f:
                json.dump(data, f, indent=2)
    
    # ─────────────────────────────────────────────────────────
    #  LEARNING
    # ─────────────────────────────────────────────────────────
    
    def learn_task(self, task: str, success: bool):
        """Lerne aus einer Task-Ausführung"""
        
        # Extract keywords
        keywords = self._extract_keywords(task)
        
        for kw in keywords:
            self.patterns[kw] += 1
            
            # Learn from success/failure
            if success:
                self.patterns[f"{kw}_success"] = self.patterns.get(f"{kw}_success", 0) + 1
            else:
                self.patterns[f"{kw}_failure"] = self.patterns.get(f"{kw}_failure", 0) + 1
        
        self._save_knowledge()
        log.info(f"🧠 Gelernt aus Task: {task[:30]}... ({'✅' if success else '❌'})")
    
    def learn_agent(self, agent: str, action: str, success: bool):
        """Lerne aus Agent-Ausführung"""
        
        key = f"{agent}:{action}"
        
        if success:
            self.agent_success[key]["success"] += 1
        else:
            self.agent_success[key]["failure"] += 1
        
        self._save_knowledge()
        log.info(f"🧠 Agent gelernt: {key} ({'✅' if success else '❌'})")
    
    def learn_connection(self, from_agent: str, to_agent: str, success: bool):
        """Lerne Agent-Verbindungen"""
        
        self.connections[from_agent][to_agent] += 1
        
        # Also learn reverse
        if success:
            self.connections[to_agent][f"{from_agent}_success"] = \
                self.connections[to_agent].get(f"{from_agent}_success", 0) + 1
        
        self._save_knowledge()
    
    def learn_timing(self, agent: str, duration: float, success: bool):
        """Lerne beste Ausführungszeiten"""
        
        if success and duration < 60:  # Only learn from reasonable times
            self.optimal_times[agent].append(duration)
            
            # Keep only last 100
            if len(self.optimal_times[agent]) > 100:
                self.optimal_times[agent] = self.optimal_times[agent][-100:]
    
    # ─────────────────────────────────────────────────────────
    #  INFERENCE
    # ─────────────────────────────────────────────────────────
    
    def get_best_agent(self, task: str) -> str:
        """Beste Agent für eine Task basierend auf gelernten Patterns"""
        
        keywords = self._extract_keywords(task)
        
        scores = {}
        
        # Score each agent based on patterns
        for kw in keywords:
            # Look for patterns like "blog_success", "email_success"
            success_key = f"{kw}_success"
            failure_key = f"{kw}_failure"
            
            success_count = self.patterns.get(success_key, 0)
            failure_count = self.patterns.get(failure_key, 0)
            
            if success_count + failure_count > 0:
                score = success_count / (success_count + failure_count)
                scores[kw] = score
        
        # Return best keyword
        if scores:
            best = max(scores, key=scores.get)
            
            # Map to agent
            agent_map = {
                "blog": "content", "post": "content", "article": "content",
                "email": "revenue", "outreach": "revenue", "sales": "revenue",
                "search": "research", "analyse": "research", "recherche": "research",
                "code": "coding", "programm": "coding", "entwickle": "coding",
                "security": "security", "scan": "security",
                "social": "growth", "twitter": "growth"
            }
            
            return agent_map.get(best, "research")
        
        return "research"  # Default
    
    def get_agent_success_rate(self, agent: str, action: str = None) -> float:
        """Erfolgsrate eines Agenten"""
        
        key = f"{agent}:{action}" if action else agent
        
        data = self.agent_success.get(key, {"success": 0, "failure": 0})
        
        total = data["success"] + data["failure"]
        
        if total == 0:
            return 0.5  # Unknown = neutral
        
        return data["success"] / total
    
    def get_best_connection(self, from_agent: str) -> str:
        """Beste Agent-Verbindung"""
        
        if from_agent not in self.connections:
            return "mail"  # Default
        
        connections = self.connections[from_agent]
        
        if not connections:
            return "mail"
        
        # Return agent with highest success count
        return max(connections, key=connections.get)
    
    def get_optimal_time(self, agent: str) -> Optional[float]:
        """Beste Ausführungszeit für Agent"""
        
        times = self.optimal_times.get(agent, [])
        
        if not times:
            return None
        
        return sum(times) / len(times)
    
    def predict_next_agent(self, current_agent: str) -> str:
        """Prädiziere nächsten Agenten basierend auf History"""
        
        # Look for successful chains
        for from_a, connections in self.connections.items():
            if from_a == current_agent:
                # Find best next
                best = max(connections, key=connections.get)
                if best.endswith("_success"):
                    return best.replace("_success", "")
                
                return best
        
        # Default chain
        chain = {
            "research": "content",
            "content": "mail",
            "mail": "revenue",
            "revenue": "research"
        }
        
        return chain.get(current_agent, "mail")
    
    # ─────────────────────────────────────────────────────────
    #  OPTIMIZATION
    # ─────────────────────────────────────────────────────────
    
    def get_optimizations(self) -> List[Dict]:
        """Gib Optimierungsvorschläge"""
        
        suggestions = []
        
        # Analyze agents
        for key, data in self.agent_success.items():
            total = data["success"] + data["failure"]
            
            if total >= 3:
                rate = data["success"] / total
                
                if rate < 0.5:
                    suggestions.append({
                        "type": "agent_failure",
                        "target": key,
                        "reason": f"Success rate only {rate:.0%}",
                        "action": "Consider alternative agent or retry logic"
                    })
                elif rate > 0.8:
                    suggestions.append({
                        "type": "agent_success",
                        "target": key,
                        "reason": f"Excellent success rate {rate:.0%}",
                        "action": "Use more often"
                    })
        
        # Analyze patterns
        for pattern, count in self.patterns.items():
            if pattern.endswith("_failure") and count > 2:
                base = pattern.replace("_failure", "")
                suggestions.append({
                    "type": "pattern_failure",
                    "target": base,
                    "reason": f"{count} failures with '{base}'",
                    "action": "Avoid or improve handling"
                })
        
        return suggestions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrahiere Keywords aus Text"""
        
        keywords = []
        
        # Task types
        task_types = [
            "blog", "post", "article", "content",
            "email", "outreach", "sales", "lead",
            "research", "analyse", "search",
            "code", "program", "develop",
            "security", "scan", "audit",
            "social", "twitter", "linkedin",
            "data", "analyze", "report"
        ]
        
        text_lower = text.lower()
        
        for kw in task_types:
            if kw in text_lower:
                keywords.append(kw)
        
        return keywords if keywords else ["general"]
    
    def get_stats(self) -> Dict:
        """Gib Lern-Statistiken"""
        
        total_tasks = sum(self.patterns.values())
        total_success = sum(
            v for k, v in self.patterns.items() 
            if k.endswith("_success")
        )
        
        return {
            "patterns_learned": len(self.patterns),
            "agents_tracked": len(self.agent_success),
            "connections_tracked": len(self.connections),
            "estimated_success_rate": total_success / max(total_tasks, 1),
            "optimizations_available": len(self.get_optimizations())
        }


# Global instance
_learning_system = None


def get_learning_system() -> SelfLearningSystem:
    """Hol das globale Learning System"""
    global _learning_system
    if _learning_system is None:
        _learning_system = SelfLearningSystem()
    return _learning_system


if __name__ == "__main__":
    # Test
    learning = get_learning_system()
    
    # Learn from examples
    learning.learn_task("Erstelle Blog Post", True)
    learning.learn_task("Sende Outreach Email", True)
    learning.learn_task("Sende Outreach Email", True)
    learning.learn_task("Sende Outreach Email", False)
    
    learning.learn_agent("research", "recherche", True)
    learning.learn_agent("content", "create", True)
    learning.learn_agent("revenue", "outreach", False)
    
    learning.learn_connection("research", "content", True)
    learning.learn_connection("content", "mail", True)
    
    # Get insights
    print("\n🧠 LEARNING STATS:")
    print(json.dumps(learning.get_stats(), indent=2))
    
    print("\n🎯 BEST AGENT FOR TASK:")
    print(f"   Blog Post → {learning.get_best_agent('Blog Post erstellen')}")
    print(f"   Email → {learning.get_best_agent('Outreach Email')}")
    
    print("\n💡 OPTIMIZATIONS:")
    for opt in learning.get_optimizations():
        print(f"   - {opt}")

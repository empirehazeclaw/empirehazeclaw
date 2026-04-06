#!/usr/bin/env python3
"""
Knowledge Graph - PARA Method
Atomic JSON storage with decay and priority management
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

class KnowledgeGraph:
    """Knowledge Graph with PARA method"""
    
    DECAY_RATE = 0.9  # 9% per week
    DECAY_PERIOD = 7  # days
    
    def __init__(self, path: str = None):
        if path is None:
            path = "/home/clawbot/.openclaw/workspace/memory/knowledge_graph.json"
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self.load()
    
    def load(self) -> dict:
        """Load knowledge graph"""
        if self.path.exists():
            return json.load(open(self.path))
        return {
            "entities": {},
            "last_updated": None,
            "created": datetime.now().isoformat()
        }
    
    def save(self):
        """Save knowledge graph"""
        self.data["last_updated"] = datetime.now().isoformat()
        json.dump(self.data, open(self.path, "w"), indent=2)
    
    def add_fact(self, entity: str, fact: str, category: str = "general", confidence: float = 0.8, priority: str = "MEDIUM"):
        """Add a fact to an entity"""
        
        # Determine PARA category
        para_category = self._get_para_category(category)
        
        if entity not in self.data["entities"]:
            self.data["entities"][entity] = {
                "type": para_category,
                "category": category,
                "facts": [],
                "priority": priority,
                "created": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0,
                "decay_score": 1.0
            }
        
        # Add fact
        self.data["entities"][entity]["facts"].append({
            "content": fact,
            "confidence": confidence,
            "extracted_at": datetime.now().isoformat(),
            "category": category
        })
        
        self.save()
    
    def _get_para_category(self, category: str) -> str:
        """Map category to PARA"""
        mapping = {
            "preference": "Areas",
            "goal": "Projects",
            "learning": "Resources",
            "pattern": "Areas",
            "project": "Projects",
            "system": "Resources",
            "person": "Areas",
            "business": "Projects",
            "product": "Projects",
            "skill": "Resources"
        }
        return mapping.get(category, "Resources")
    
    def query(self, search_term: str, priority_filter: str = None, limit: int = 10) -> List[dict]:
        """Query with decay and priority"""
        results = []
        
        for entity, data in self.data["entities"].items():
            # Apply decay
            decay = self._calculate_decay(data.get("last_accessed", data.get("created")))
            
            # Check priority filter
            if priority_filter and data.get("priority") != priority_filter:
                continue
            
            # Search facts
            for fact in data.get("facts", []):
                if search_term.lower() in fact["content"].lower():
                    score = fact["confidence"] * decay
                    results.append({
                        "entity": entity,
                        "fact": fact["content"],
                        "category": fact.get("category", "unknown"),
                        "priority": data.get("priority", "MEDIUM"),
                        "para": data.get("type", "Resources"),
                        "score": round(score, 3),
                        "last_accessed": data.get("last_accessed"),
                        "decay": round(decay, 3)
                    })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def _calculate_decay(self, last_accessed: str) -> float:
        """Calculate decay (9% per week)"""
        if not last_accessed:
            return 1.0
        try:
            days = (datetime.now() - datetime.fromisoformat(last_accessed)).days
            return self.DECAY_RATE ** (days / self.DECAY_PERIOD)
        except:
            return 1.0
    
    def track_access(self, entity: str):
        """Track access and boost recency"""
        if entity in self.data["entities"]:
            self.data["entities"][entity]["last_accessed"] = datetime.now().isoformat()
            self.data["entities"][entity]["access_count"] = self.data["entities"][entity].get("access_count", 0) + 1
            self._recalculate_priority(entity)
            self.save()
    
    def _recalculate_priority(self, entity: str):
        """Recalculate priority based on access"""
        data = self.data["entities"][entity]
        
        # Frequently accessed = CRITICAL
        if data.get("access_count", 0) > 10:
            data["priority"] = "CRITICAL"
        # Recently accessed = HIGH
        elif self._calculate_decay(data.get("last_accessed")) > 0.7:
            data["priority"] = "HIGH"
        else:
            data["priority"] = "MEDIUM"
    
    def get_stats(self) -> dict:
        """Get statistics"""
        priorities = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        para = {"Projects": 0, "Areas": 0, "Resources": 0, "Archives": 0}
        
        for entity, data in self.data["entities"].items():
            priorities[data.get("priority", "MEDIUM")] = priorities.get(data.get("priority", "MEDIUM"), 0) + 1
            para[data.get("type", "Resources")] = para.get(data.get("type", "Resources"), 0) + 1
        
        return {
            "total_entities": len(self.data["entities"]),
            "total_facts": sum(len(d.get("facts", [])) for d in self.data["entities"].values()),
            "priorities": priorities,
            "para_distribution": para,
            "last_updated": self.data.get("last_updated")
        }

# CLI
if __name__ == "__main__":
    import sys
    
    kg = KnowledgeGraph()
    
    if len(sys.argv) < 2:
        print("Knowledge Graph CLI")
        print("Usage:")
        print("  python3 knowledge_graph.py add <entity> <fact> [category]")
        print("  python3 knowledge_graph.py query <term>")
        print("  python3 knowledge_graph.py stats")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 4:
            print("Usage: python3 knowledge_graph.py add <entity> <fact> [category]")
            sys.exit(1)
        entity = sys.argv[2]
        fact = sys.argv[3]
        category = sys.argv[4] if len(sys.argv) > 4 else "general"
        kg.add_fact(entity, fact, category)
        print(f"✓ Added fact to {entity}")
    
    elif action == "query":
        if len(sys.argv) < 3:
            print("Usage: python3 knowledge_graph.py query <term>")
            sys.exit(1)
        term = sys.argv[2]
        results = kg.query(term)
        print(f"\n🔍 Results for '{term}':")
        for r in results:
            print(f"  [{r['priority']}] {r['entity']}: {r['fact'][:60]}... (score: {r['score']})")
    
    elif action == "stats":
        stats = kg.get_stats()
        print("\n📊 Knowledge Graph Stats:")
        print(f"  Entities: {stats['total_entities']}")
        print(f"  Facts: {stats['total_facts']}")
        print(f"  Priorities: {stats['priorities']}")
        print(f"  PARA: {stats['para_distribution']}")

#!/usr/bin/env python3
"""
Memory System v3.1 - Complete Integration
Combines Knowledge Graph, Daily Notes, and Fact Extraction
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_graph import KnowledgeGraph
from daily_notes import DailyNotes
from fact_extractor import FactExtractor

class MemorySystem:
    """Complete memory system v3.1"""
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = "/home/clawbot/.openclaw/workspace"
        
        self.workspace = workspace_path
        self.kg = KnowledgeGraph(f"{workspace_path}/memory/knowledge_graph.json")
        self.notes = DailyNotes(f"{workspace_path}/memory/daily")
        self.extractor = FactExtractor()
    
    def process_message(self, message: str, user: str = "Master"):
        """Process a message and update memory"""
        
        # 1. Extract facts
        facts = self.extractor.extract(message)
        
        # 2. Add facts to knowledge graph
        for fact in facts:
            self.kg.add_fact(
                entity=user,
                fact=fact["content"],
                category=fact["category"],
                confidence=fact["confidence"],
                priority=fact["priority"]
            )
        
        # 3. Log to daily notes
        self.notes.add_entry(message)
        
        # 4. Extract and return summary
        return {
            "facts_extracted": len(facts),
            "entities": self.extractor.extract_entities(message),
            "categories": list(set(f["category"] for f in facts))
        }
    
    def query(self, term: str, priority: str = None):
        """Query memory"""
        return self.kg.query(term, priority_filter=priority)
    
    def get_stats(self):
        """Get memory statistics"""
        return self.kg.get_stats()
    
    def get_today(self):
        """Get today's notes"""
        return self.notes.get_today()

# CLI
if __name__ == "__main__":
    memory = MemorySystem()
    
    if len(sys.argv) < 2:
        print("Memory System v3.1 CLI")
        print("Usage:")
        print("  python3 memory_system.py process <message>")
        print("  python3 memory_system.py query <term>")
        print("  python3 memory_system.py stats")
        print("  python3 memory_system.py today")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "process":
        if len(sys.argv) < 3:
            print("Usage: python3 memory_system.py process <message>")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        result = memory.process_message(message)
        print(f"✓ Processed: {result['facts_extracted']} facts extracted")
    
    elif action == "query":
        if len(sys.argv) < 3:
            print("Usage: python3 memory_system.py query <term>")
            sys.exit(1)
        term = sys.argv[2]
        results = memory.query(term)
        print(f"\n🔍 Results for '{term}':")
        for r in results[:5]:
            print(f"  [{r['priority']}] {r['entity']}: {r['fact'][:60]}")
    
    elif action == "stats":
        stats = memory.get_stats()
        print("\n📊 Memory Stats:")
        print(f"  Entities: {stats['total_entities']}")
        print(f"  Facts: {stats['total_facts']}")
        print(f"  Priorities: {stats['priorities']}")
    
    elif action == "today":
        print(memory.get_today())

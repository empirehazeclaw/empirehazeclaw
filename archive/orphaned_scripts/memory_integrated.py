#!/usr/bin/env python3
"""
Memory System Integration
Combines Memory System (Facts + Daily Notes) with RAG Search
"""

import sys
import os
from pathlib import Path

# Add paths
workspace = "/home/clawbot/.openclaw/workspace"
sys.path.insert(0, f"{workspace}/scripts/memory")
sys.path.insert(0, f"{workspace}/knowledge_rag")

class IntegratedMemory:
    """Combined Memory + RAG System"""
    
    def __init__(self):
        # Import existing memory system
        from memory_system import MemorySystem
        self.memory = MemorySystem(workspace)
        
        # Import RAG
        from src.query import QueryEngine
        self.rag = QueryEngine()
    
    def process(self, message, user="Master"):
        """Process message → Memory + RAG ready"""
        return self.memory.process_message(message, user)
    
    def search(self, query, limit=5):
        """Semantic search via RAG"""
        return self.rag.search(query, limit=limit, similarity_threshold=0.3)
    
    def query_memory(self, term):
        """Query knowledge graph"""
        return self.memory.query(term)
    
    def stats(self):
        """Get combined stats"""
        mem_stats = self.memory.get_stats()
        
        # Get RAG stats
        import sqlite3
        conn = sqlite3.connect(f"{workspace}/knowledge_rag/db/knowledge.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sources")
        rag_sources = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM chunks")
        rag_chunks = cursor.fetchone()[0]
        conn.close()
        
        return {
            "memory": mem_stats,
            "rag": {
                "sources": rag_sources,
                "chunks": rag_chunks
            }
        }

# CLI
if __name__ == "__main__":
    integrated = IntegratedMemory()
    
    if len(sys.argv) < 2:
        print("📦 Integrated Memory System")
        print("Commands:")
        print("  process <message>  - Process message to memory")
        print("  search <query>    - Semantic search via RAG")
        print("  query <term>      - Query knowledge graph")
        print("  stats             - Show combined stats")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "process":
        msg = " ".join(sys.argv[2:])
        result = integrated.process(msg)
        print(f"✅ Processed: {result['facts_extracted']} facts")
    
    elif action == "search":
        query = " ".join(sys.argv[2:])
        results = integrated.search(query)
        print(f"\n🔍 RAG Results for '{query}':")
        for r in results.get('results', [])[:3]:
            print(f"  [{r['similarity']}] {r['title']}")
            print(f"       {r['content'][:100]}...")
    
    elif action == "query":
        term = sys.argv[2]
        results = integrated.query_memory(term)
        print(f"\n🧠 Knowledge Graph for '{term}':")
        for r in results[:3]:
            print(f"  [{r['priority']}] {r['fact'][:80]}")
    
    elif action == "stats":
        stats = integrated.stats()
        print("\n📊 Combined Memory Stats:")
        print(f"  Memory Graph: {stats['memory']['total_facts']} facts, {stats['memory']['total_entities']} entities")
        print(f"  RAG: {stats['rag']['sources']} sources, {stats['rag']['chunks']} chunks")

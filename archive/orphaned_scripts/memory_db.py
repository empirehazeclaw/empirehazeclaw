#!/usr/bin/env python3
"""Memory Database with ChromaDB - Vector Search + SQLite"""
import chromadb
import sqlite3
import os
from datetime import datetime

DB_DIR = "data/memory"
os.makedirs(DB_DIR, exist_ok=True)

# Initialize ChromaDB (Vector)
chroma_client = chromadb.PersistentClient(path=f"{DB_DIR}/chroma")
memory_collection = chroma_client.get_or_create_collection("master_memory")

# Initialize SQLite (Structured)
sqlite_conn = sqlite3.connect(f"{DB_DIR}/memory.db")
sqlite_cursor = sqlite_conn.cursor()

# Create tables
sqlite_cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY,
        priority TEXT,
        category TEXT,
        content TEXT,
        created_at TEXT,
        updated_at TEXT
    )
""")
sqlite_conn.commit()

def add_memory(priority, category, content):
    """Add memory to both ChromaDB and SQLite"""
    now = datetime.utcnow().isoformat()
    
    # ChromaDB (for semantic search)
    memory_collection.add(
        documents=[content],
        ids=[f"mem_{datetime.utcnow().timestamp()}"],
        metadatas=[{"priority": priority, "category": category}]
    )
    
    # SQLite (for structured queries)
    sqlite_cursor.execute(
        "INSERT INTO memories (priority, category, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (priority, category, content, now, now)
    )
    sqlite_conn.commit()
    
    return "✅ Added"

def search_memory(query, priority_filter=None):
    """Search memories - vector + SQLite"""
    results = []
    
    # Vector search in ChromaDB
    vector_results = memory_collection.query(
        query_texts=[query],
        n_results=5
    )
    
    if vector_results and vector_results.get('documents'):
        for i, doc in enumerate(vector_results['documents'][0]):
            results.append({
                'type': 'vector',
                'content': doc,
                'priority': vector_results['metadatas'][0][i].get('priority') if vector_results.get('metadatas') else 'P3'
            })
    
    # SQLite search
    if priority_filter:
        sqlite_cursor.execute(
            "SELECT content, priority FROM memories WHERE priority = ? ORDER BY updated_at DESC LIMIT 5",
            (priority_filter,)
        )
    else:
        sqlite_cursor.execute(
            "SELECT content, priority FROM memories ORDER BY updated_at DESC LIMIT 5"
        )
    
    for row in sqlite_cursor.fetchall():
        results.append({'type': 'sqlite', 'content': row[0], 'priority': row[1]})
    
    return results

def get_priority(priority):
    """Get all memories of a specific priority"""
    sqlite_cursor.execute(
        "SELECT content FROM memories WHERE priority = ? ORDER BY updated_at DESC",
        (priority,)
    )
    return [row[0] for row in sqlite_cursor.fetchall()]

# Seed with current MASTER_MEMORY
def seed_master_memory():
    """Load MASTER_MEMORY into DB"""
    with open("MASTER_MEMORY.md", "r") as f:
        content = f.read()
    
    add_memory("P1", "rules", content)
    print("✅ Seeded MASTER_MEMORY to ChromaDB")

if __name__ == "__main__":
    # Test
    print("=== 🗄️ MEMORY DB TEST ===")
    seed_master_memory()
    results = search_memory("Twitter")
    print(f"\n🔍 Search 'Twitter': {len(results)} results")
    for r in results[:2]:
        print(f"  [{r['priority']}] {r['content'][:80]}...")

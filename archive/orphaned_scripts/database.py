#!/usr/bin/env python3
"""
Database Layer - Production Ready
SQLite Persistent Storage
"""

import os
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.expanduser("~/.openclaw/data/openclaw.db")

class Database:
    """SQLite Database Manager"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tables
            cursor.execute("""CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY, name TEXT UNIQUE, type TEXT, status TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            
            cursor.execute("""CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY, key TEXT UNIQUE, value TEXT, tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            
            cursor.execute("""CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY, title TEXT, content TEXT, doc_type TEXT, tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            
            cursor.execute("""CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY, metric_name TEXT, value REAL, unit TEXT, tags TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            
            cursor.execute("""CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY, job_id TEXT UNIQUE, name TEXT, command TEXT, schedule TEXT,
                status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            
            conn.commit()
    
    def set_memory(self, key: str, value: str):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key, value)
            )
    
    def get_memory(self, key: str):
        with self.get_connection() as conn:
            conn.cursor().execute("SELECT * FROM memory WHERE key = ?", (key,))
            row = conn.cursor().fetchone()
            return dict(row) if row else None
    
    def add_knowledge(self, title: str, content: str, doc_type: str = "general"):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO knowledge (title, content, doc_type) VALUES (?, ?, ?)",
                (title, content, doc_type)
            )
    
    def search_knowledge(self, query: str, limit: int = 10):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "SELECT * FROM knowledge WHERE title LIKE ? OR content LIKE ? LIMIT ?",
                (f"%{query}%", f"%{query}%", limit)
            )
            return [dict(row) for row in conn.cursor().fetchall()]
    
    def record_metric(self, name: str, value: float, unit: str = ""):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO metrics (metric_name, value, unit) VALUES (?, ?, ?)",
                (name, value, unit)
            )
    
    def get_stats(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}
            for table in ['agents', 'memory', 'knowledge', 'metrics', 'jobs']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            stats['size_bytes'] = os.path.getsize(self.db_path)
            stats['size_mb'] = round(stats['size_bytes'] / 1024 / 1024, 2)
            return stats


def main():
    import sys
    
    db = Database()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "stats":
            print(json.dumps(db.get_stats(), indent=2))
        
        elif cmd == "memory" and len(sys.argv) > 2:
            key = sys.argv[2]
            print(json.dumps(db.get_memory(key), indent=2))
        
        elif cmd == "search" and len(sys.argv) > 2:
            query = sys.argv[2]
            print(json.dumps(db.search_knowledge(query), indent=2))
        
        elif cmd == "set" and len(sys.argv) > 3:
            key, value = sys.argv[2], sys.argv[3]
            db.set_memory(key, value)
            print(f"Set {key} = {value}")
        
        else:
            print("""
💾 Database CLI
  stats          - Show stats
  set [key] [val] - Set memory
  memory [key]    - Get memory
  search [query]  - Search knowledge
            """)
    else:
        s = db.get_stats()
        print(f"💾 Database: {s.get('agents',0)} agents, {s.get('memory',0)} memory, {s.get('knowledge',0)} docs, {s.get('size_mb',0)} MB")

if __name__ == "__main__":
    main()

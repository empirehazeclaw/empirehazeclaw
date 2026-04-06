#!/usr/bin/env python3
"""
🧠 Persistent Memory System
Speichert Erfahrungen über Sessions hinweg
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/memory/persistent")
MEMORY_FILE = MEMORY_DIR / "memory.json"
CONTEXT_FILE = MEMORY_DIR / "context.json"

class PersistentMemory:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.context_file = CONTEXT_FILE
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> dict:
        """Lädt gesamtes Memory"""
        if self.memory_file.exists():
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {
            "sessions": [],
            "learnings": [],
            "preferences": {},
            "relationships": {},
            "projects": {}
        }
    
    def save(self, memory: dict):
        """Speichert Memory"""
        with open(self.memory_file, "w") as f:
            json.dump(memory, f, indent=2)
    
    def add_learning(self, key: str, value: Any, category: str = "general"):
        """Fügt neues Learning hinzu"""
        memory = self.load()
        
        memory["learnings"].append({
            "key": key,
            "value": value,
            "category": category,
            "created": datetime.now().isoformat(),
            "access_count": 0
        })
        
        self.save(memory)
        print(f"✅ Learning gespeichert: {key}")
    
    def get_learning(self, key: str) -> Optional[Any]:
        """Holt Learning nach Key"""
        memory = self.load()
        
        for i, entry in enumerate(memory.get("learnings", [])):
            if entry.get("key") == key:
                # Access Count erhöhen
                memory["learnings"][i]["access_count"] = entry.get("access_count", 0) + 1
                self.save(memory)
                return entry.get("value")
        
        return None
    
    def set_preference(self, key: str, value: Any):
        """Speichert Preference"""
        memory = self.load()
        memory["preferences"][key] = {
            "value": value,
            "updated": datetime.now().isoformat()
        }
        self.save(memory)
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Holt Preference"""
        memory = self.load()
        pref = memory.get("preferences", {}).get(key)
        return pref.get("value") if pref else default
    
    def record_interaction(self, who: str, what: str, sentiment: str = "neutral"):
        """Zeichnet Interaktion auf"""
        memory = self.load()
        
        if "relationships" not in memory:
            memory["relationships"] = {}
        
        if who not in memory["relationships"]:
            memory["relationships"][who] = {"interactions": []}
        
        memory["relationships"][who]["interactions"].append({
            "what": what,
            "sentiment": sentiment,
            "at": datetime.now().isoformat()
        })
        
        self.save(memory)
    
    def get_context(self, session_id: str) -> dict:
        """Holt Kontext für Session"""
        if self.context_file.exists():
            with open(self.context_file, "r") as f:
                contexts = json.load(f)
                return contexts.get(session_id, {})
        return {}
    
    def save_context(self, session_id: str, context: dict):
        """Speichert Kontext für Session"""
        contexts = {}
        if self.context_file.exists():
            with open(self.context_file, "r") as f:
                contexts = json.load(f)
        
        contexts[session_id] = context
        
        with open(self.context_file, "w") as f:
            json.dump(contexts, f, indent=2)
    
    def search(self, query: str) -> list:
        """Durchsucht Memory"""
        memory = self.load()
        query_lower = query.lower()
        results = []
        
        # Search learnings
        for entry in memory.get("learnings", []):
            if query_lower in str(entry.get("key", "")).lower() or \
               query_lower in str(entry.get("value", "")).lower():
                results.append(entry)
        
        # Search preferences
        for key, entry in memory.get("preferences", {}).items():
            if query_lower in key.lower() or query_lower in str(entry.get("value", "")).lower():
                results.append({"key": key, "value": entry.get("value")})
        
        return results

# Global instance
_memory = None

def get_memory() -> PersistentMemory:
    global _memory
    if _memory is None:
        _memory = PersistentMemory()
    return _memory

if __name__ == "__main__":
    import sys
    
    mem = get_memory()
    
    if len(sys.argv) < 2:
        print("🧠 Persistent Memory")
        print("")
        print("Usage:")
        print("  python3 persistent_memory.py add <key> <value>")
        print("  python3 persistent_memory.py get <key>")
        print("  python3 persistent_memory.py pref set <key> <value>")
        print("  python3 persistent_memory.py pref get <key>")
        print("  python3 persistent_memory.py search <query>")
        print("  python3 persistent_memory.py interact <who> <what>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "add" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = " ".join(sys.argv[3:])
        mem.add_learning(key, value)
    
    elif cmd == "get" and len(sys.argv) >= 3:
        key = sys.argv[2]
        value = mem.get_learning(key)
        print(f"→ {value}" if value else "Nicht gefunden")
    
    elif cmd == "pref":
        if len(sys.argv) >= 4:
            action = sys.argv[2]
            key = sys.argv[3]
            if action == "set" and len(sys.argv) >= 5:
                value = " ".join(sys.argv[4:])
                mem.set_preference(key, value)
            elif action == "get":
                print(mem.get_preference(key))
    
    elif cmd == "search" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        results = mem.search(query)
        for r in results:
            print(f"📌 {r.get('key', 'N/A')}: {r.get('value', 'N/A')}")
    
    elif cmd == "interact" and len(sys.argv) >= 4:
        who = sys.argv[2]
        what = " ".join(sys.argv[3:])
        mem.record_interaction(who, what)
        print(f"✅ Interaktion mit {who} gespeichert")

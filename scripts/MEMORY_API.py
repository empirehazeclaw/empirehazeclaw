#!/usr/bin/env python3
"""
MEMORY_API.py — Unified Memory Interface
=========================================
Single API for all memory systems.

Usage:
    from MEMORY_API import MemoryAPI
    api = MemoryAPI()
    
    # Search all memories
    results = api.search("error rate")
    
    # Get knowledge
    entities = api.get_entities("error")
    
    # Add to memory
    api.add_knowledge("New pattern", {"type": "pattern", "data": {...}})
    
    # Get daily notes
    daily = api.get_daily_notes()
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

class MemoryAPI:
    """Unified interface to all memory systems."""
    
    WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
    MEMORY_DIR = WORKSPACE / "memory"
    CEO_MEMORY_DIR = WORKSPACE / "ceo/memory"
    KG_FILE = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
    SEMANTIC_INDEX = WORKSPACE / "core_ultralight/memory/semantic_index.json"
    
    def __init__(self):
        self._kg_cache = None
        self._kg_cache_time = 0
        self._kg_cache_ttl = 3600  # 1 hour
    
    # ============ KNOWLEDGE GRAPH ============
    
    def get_kg(self, use_cache=True) -> Dict:
        """Get Knowledge Graph with optional caching."""
        now = datetime.now().timestamp()
        
        if use_cache and self._kg_cache and (now - self._kg_cache_time) < self._kg_cache_ttl:
            return self._kg_cache
        
        if self.KG_FILE.exists():
            with open(self.KG_FILE) as f:
                self._kg_cache = json.load(f)
                self._kg_cache_time = now
                return self._kg_cache
        return {"entities": [], "relations": []}
    
    def get_entities(self, filter_str: str = None) -> List[Dict]:
        """Get all entities, optionally filtered."""
        kg = self.get_kg()
        entities_dict = kg.get("entities", {})
        
        # KG uses dict structure: {entity_id: entity_data}
        # Convert to list for compatibility
        entities_list = []
        for entity_id, entity_data in entities_dict.items():
            # Add id to entity data for reference
            entity_copy = dict(entity_data)
            entity_copy['id'] = entity_id
            # Use first fact content as title if no title
            if 'title' not in entity_copy:
                facts = entity_copy.get('facts', [])
                entity_copy['title'] = facts[0].get('content', '')[:80] if facts else entity_id
            entities_list.append(entity_copy)
        
        if filter_str:
            filter_lower = filter_str.lower()
            entities_list = [e for e in entities_list if filter_lower in e.get('title', '').lower() or filter_lower in e.get('id', '').lower()]
        
        return entities_list
    
    def add_knowledge(self, title: str, data: Dict) -> bool:
        """Add new entity to knowledge graph."""
        kg = self.get_kg(use_cache=False)
        
        # Generate entity ID from title
        entity_id = f"entity_{len(kg.get('entities', {})) + 1}"
        timestamp = datetime.now().strftime('%Y%m%d')
        entity_id_full = f"{entity_id}_{timestamp}"
        
        entity = {
            "type": data.get("type", "knowledge"),
            "category": data.get("type", "knowledge"),
            "facts": [{
                "content": title,
                "confidence": 0.9,
                "extracted_at": datetime.now().isoformat(),
                "category": data.get("type", "knowledge")
            }],
            "priority": data.get("priority", "MEDIUM"),
            "created": datetime.now().isoformat(),
            "last_accessed": "",
            "access_count": 0
        }
        
        kg.setdefault("entities", {})[entity_id_full] = entity
        
        with open(self.KG_FILE, 'w') as f:
            json.dump(kg, f, indent=2)
        
        # Invalidate cache
        self._kg_cache = None
        return True
    
    # ============ DAILY NOTES ============
    
    def get_daily_notes(self, date: str = None) -> str:
        """Get daily notes for date (YYYY-MM-DD or None for today)."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        daily_file = self.MEMORY_DIR / f"{date}.md"
        
        if daily_file.exists():
            return daily_file.read_text()
        return ""
    
    def append_daily_note(self, entry: str) -> bool:
        """Append entry to today's daily notes."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = self.MEMORY_DIR / f"{today}.md"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        content = f"\n\n{timestamp} — {entry}"
        
        with open(daily_file, 'a') as f:
            f.write(content)
        
        return True
    
    # ============ CEO MEMORY ============
    
    def get_ceo_daily_notes(self, date: str = None) -> str:
        """Get CEO daily notes for date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        daily_file = self.CEO_MEMORY_DIR / "daily" / f"{date}.md"
        
        if daily_file.exists():
            return daily_file.read_text()
        return ""
    
    def list_ceo_daily_notes(self) -> List[str]:
        """List all CEO daily notes."""
        daily_dir = self.CEO_MEMORY_DIR / "daily"
        if not daily_dir.exists():
            return []
        
        return [f.name for f in sorted(daily_dir.glob("*.md"))]
    
    # ============ SEARCH ============
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search all memory systems."""
        results = []
        
        # Search KG entities (dict structure)
        kg = self.get_kg()
        query_lower = query.lower()
        
        for entity_id, entity_data in kg.get("entities", {}).items():
            # Check entity ID
            if query_lower in entity_id.lower():
                results.append({
                    "type": "entity",
                    "source": "knowledge_graph",
                    "title": entity_id,
                    "data": entity_data,
                    "score": 1.0
                })
                continue
            
            # Check facts content
            for fact in entity_data.get('facts', []):
                content = fact.get('content', '').lower()
                if query_lower in content:
                    results.append({
                        "type": "entity",
                        "source": "knowledge_graph",
                        "title": entity_id,
                        "data": entity_data,
                        "score": 0.8
                    })
                    break
        
        # Search daily notes (today)
        daily = self.get_daily_notes()
        if query_lower in daily.lower():
            results.append({
                "type": "file",
                "source": "daily_notes",
                "title": "Today's Daily Notes",
                "data": {"path": str(self.MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md")}
            })
        
        return results[:limit]
    
    # ============ EXPERIENCE BANK ============
    
    def get_experiences(self) -> List[Dict]:
        """Get all extracted experiences."""
        exp_file = self.CEO_MEMORY_DIR / "experience_bank" / "experience_2026-04.json"
        
        if exp_file.exists():
            with open(exp_file) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data.get("experiences", [])
                return data
        return []
    
    # ============ SYSTEM STATUS ============
    
    def get_status(self) -> Dict:
        """Get memory system status."""
        kg = self.get_kg()
        entities_dict = kg.get("entities", {})
        
        # Calculate shares_category ratio
        relations = kg.get("relations", [])
        shares_cat = sum(1 for r in relations if r.get('type') == 'shares_category')
        
        # Calculate average access_count
        access_counts = [e.get('access_count', 0) for e in entities_dict.values()]
        avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
        max_access = max(access_counts) if access_counts else 0
        
        return {
            "knowledge_graph": {
                "entities": len(entities_dict),
                "relations": len(relations),
                "shares_category_count": shares_cat,
                "shares_category_ratio": f"{100*shares_cat/len(relations):.1f}%" if relations else "0%",
                "size_mb": self.KG_FILE.stat().st_size / (1024 * 1024) if self.KG_FILE.exists() else 0,
                "avg_access_count": round(avg_access, 2),
                "max_access_count": max_access
            },
            "daily_notes": {
                "today": (self.MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md").exists()
            },
            "ceo_memory": {
                "daily_notes": len(self.list_ceo_daily_notes()),
                "experiences": len(self.get_experiences())
            },
            "semantic_index": {
                "exists": self.SEMANTIC_INDEX.exists()
            }
        }


# ============ CLI INTERFACE ============

if __name__ == "__main__":
    import sys
    
    api = MemoryAPI()
    
    if len(sys.argv) < 2:
        print("MEMORY_API.py — Unified Memory Interface")
        print()
        print("Usage:")
        print("  python3 MEMORY_API.py status")
        print("  python3 MEMORY_API.py search <query>")
        print("  python3 MEMORY_API.py entities [filter]")
        print("  python3 MEMORY_API.py daily [date]")
        print("  python3 MEMORY_API.py experiences")
        print()
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        status = api.get_status()
        print("📊 Memory System Status:")
        print(json.dumps(status, indent=2))
    
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        results = api.search(query)
        print(f"🔍 Search results for '{query}':")
        for r in results:
            print(f"  [{r['type']}] {r['title']}")
    
    elif cmd == "entities":
        filter_str = sys.argv[2] if len(sys.argv) > 2 else None
        entities = api.get_entities(filter_str)
        print(f"📦 Knowledge Graph Entities ({len(entities)}):")
        for e in entities[:20]:
            print(f"  - {e.get('title', e.get('id', 'unknown'))}")
    
    elif cmd == "daily":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        daily = api.get_daily_notes(date)
        print(f"📝 Daily Notes for {date or 'today'}:")
        print(daily[:1000] if daily else "(empty)")
    
    elif cmd == "experiences":
        experiences = api.get_experiences()
        print(f"🎓 Experience Bank ({len(experiences)} experiences):")
        for e in experiences[:10]:
            print(f"  - {e.get('id', 'unknown')}: {e.get('type', 'unknown')}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

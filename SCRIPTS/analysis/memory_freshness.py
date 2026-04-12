#!/usr/bin/env python3
"""
memory_freshness.py — Memory Freshness Tracker
==============================================
Tracks memory freshness and helps keep memory current.

Features:
- Track last access time per memory entity
- Track last modification time
- Identify stale memories (not accessed in X days)
- Automatic refresh suggestions
- Integration with KG for entity tracking

Usage:
    from memory_freshness import MemoryFreshness, get_freshness
    
    tracker = MemoryFreshness()
    
    # Record memory access
    tracker.record_access('memory_entity_id')
    
    # Get freshness report
    report = tracker.get_freshness_report()
    
    # Find stale memories
    stale = tracker.find_stale_memories(older_than_days=30)
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import hashlib


@dataclass
class MemoryFreshness:
    """Freshness info for a memory entity."""
    entity_id: str
    name: str
    last_accessed: Optional[str]
    last_modified: Optional[str]
    access_count: int
    freshness_score: float  # 0.0 (stale) to 1.0 (fresh)
    days_since_access: Optional[int]
    days_since_modified: Optional[int]


class MemoryFreshnessTracker:
    """
    Memory Freshness Tracker - keeps memory current.
    
    Tracks:
    - Last access time (when was memory used/queried)
    - Last modification time (when was memory updated)
    - Access frequency
    - Freshness score (0-1)
    
    Freshness Rules:
    - Accessed in last 7 days: HIGH (0.8-1.0)
    - Accessed in last 30 days: MEDIUM (0.5-0.8)
    - Accessed in last 90 days: LOW (0.2-0.5)
    - Not accessed in 90+ days: STALE (0.0)
    """
    
    # Freshness thresholds (days)
    HIGH_FRESHNESS_DAYS = 7
    MEDIUM_FRESHNESS_DAYS = 30
    LOW_FRESHNESS_DAYS = 90
    
    # Freshness scores
    HIGH_SCORE = 0.9
    MEDIUM_SCORE = 0.6
    LOW_SCORE = 0.3
    STALE_SCORE = 0.0
    
    def __init__(self, kg_file: Optional[str] = None):
        self.kg_file = Path(kg_file) if kg_file else Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json")
        self.freshness_cache: Dict[str, MemoryFreshness] = {}
    
    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:8]
    
    def load_kg(self) -> Dict:
        """Load knowledge graph."""
        if self.kg_file.exists():
            return json.loads(self.kg_file.read_text())
        return {"entities": {}, "relations": []}
    
    def save_kg(self, kg: Dict) -> None:
        """Save knowledge graph."""
        self.kg_file.write_text(json.dumps(kg, indent=2))
    
    def record_access(
        self,
        entity_id: str,
        entity_name: Optional[str] = None,
        content_hash: Optional[str] = None
    ) -> None:
        """
        Record that a memory entity was accessed.
        
        Args:
            entity_id: The entity ID in KG
            entity_name: Optional name for new entities
            content_hash: Hash of content (to detect changes)
        """
        kg = self.load_kg()
        entities = kg.get("entities", {})
        
        now = datetime.now()
        timestamp = now.isoformat()
        
        if entity_id in entities:
            # Update existing entity
            entities[entity_id]["last_accessed"] = timestamp
            entities[entity_id]["access_count"] = entities[entity_id].get("access_count", 0) + 1
            
            # Update modified if content changed
            if content_hash:
                old_hash = entities[entity_id].get("content_hash", "")
                if old_hash != content_hash:
                    entities[entity_id]["last_modified"] = timestamp
                    entities[entity_id]["content_hash"] = content_hash
        else:
            # Create new entity
            entities[entity_id] = {
                "id": entity_id,
                "name": entity_name or entity_id,
                "created": timestamp,
                "last_accessed": timestamp,
                "last_modified": timestamp,
                "access_count": 1,
                "content_hash": content_hash or "",
                "type": "memory"
            }
        
        kg["entities"] = entities
        self.save_kg(kg)
    
    def record_modification(
        self,
        entity_id: str,
        content_hash: Optional[str] = None
    ) -> None:
        """
        Record that a memory entity was modified.
        
        Args:
            entity_id: The entity ID
            content_hash: Hash of new content
        """
        kg = self.load_kg()
        entities = kg.get("entities", {})
        
        now = datetime.now()
        timestamp = now.isoformat()
        
        if entity_id in entities:
            entities[entity_id]["last_modified"] = timestamp
            if content_hash:
                entities[entity_id]["content_hash"] = content_hash
        else:
            # Create new entity (but don't count as access)
            entities[entity_id] = {
                "id": entity_id,
                "created": timestamp,
                "last_modified": timestamp,
                "last_accessed": None,
                "access_count": 0,
                "content_hash": content_hash or "",
                "type": "memory"
            }
        
        kg["entities"] = entities
        self.save_kg(kg)
    
    def get_freshness(self, entity_id: str) -> Optional[MemoryFreshness]:
        """
        Get freshness info for an entity.
        
        Returns:
            MemoryFreshness or None if not found
        """
        kg = self.load_kg()
        entities = kg.get("entities", {})
        
        if entity_id not in entities:
            return None
        
        entity = entities[entity_id]
        return self._calc_freshness(entity_id, entity)
    
    def _calc_freshness(self, entity_id: str, entity: Dict) -> MemoryFreshness:
        """Calculate freshness score for an entity."""
        now = datetime.now().replace(tzinfo=None)  # Naive for comparison
        
        last_accessed = entity.get("last_accessed")
        last_modified = entity.get("last_modified")
        access_count = entity.get("access_count", 0)
        
        # Calculate days since access
        days_since_access = None
        if last_accessed:
            access_time = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
            if access_time.tzinfo:
                access_time = access_time.replace(tzinfo=None)
            days_since_access = (now - access_time).days
        
        # Calculate days since modification
        days_since_modified = None
        if last_modified:
            mod_time = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
            if mod_time.tzinfo:
                mod_time = mod_time.replace(tzinfo=None)
            days_since_modified = (now - mod_time).days
        
        # Calculate freshness score
        if days_since_access is None:
            freshness_score = self.STALE_SCORE
        elif days_since_access <= self.HIGH_FRESHNESS_DAYS:
            freshness_score = self.HIGH_SCORE
        elif days_since_access <= self.MEDIUM_FRESHNESS_DAYS:
            freshness_score = self.MEDIUM_SCORE
        elif days_since_access <= self.LOW_FRESHNESS_DAYS:
            freshness_score = self.LOW_SCORE
        else:
            freshness_score = self.STALE_SCORE
        
        return MemoryFreshness(
            entity_id=entity_id,
            name=entity.get("name", entity_id),
            last_accessed=last_accessed,
            last_modified=last_modified,
            access_count=access_count,
            freshness_score=freshness_score,
            days_since_access=days_since_access,
            days_since_modified=days_since_modified
        )
    
    def get_freshness_report(self) -> Dict:
        """
        Get comprehensive freshness report.
        
        Returns:
            Dict with statistics and stale memories
        """
        kg = self.load_kg()
        entities = kg.get("entities", {})
        
        if not entities:
            return {
                "total_entities": 0,
                "fresh": 0,
                "aging": 0,
                "stale": 0,
                "never_accessed": 0,
                "avg_freshness": 0,
                "stale_memories": []
            }
        
        freshness_list = []
        stale = []
        never_accessed = 0
        
        for eid, entity in entities.items():
            freshness = self._calc_freshness(eid, entity)
            freshness_list.append(freshness)
            
            if freshness.access_count == 0:
                never_accessed += 1
            elif freshness.freshness_score <= self.STALE_SCORE:
                stale.append(freshness)
        
        avg_freshness = sum(f.freshness_score for f in freshness_list) / len(freshness_list)
        
        return {
            "total_entities": len(entities),
            "fresh": len([f for f in freshness_list if f.freshness_score >= self.HIGH_SCORE]),
            "aging": len([f for f in freshness_list if self.LOW_SCORE < f.freshness_score < self.HIGH_SCORE]),
            "stale": len(stale),
            "never_accessed": never_accessed,
            "avg_freshness": round(avg_freshness, 3),
            "stale_memories": [
                {
                    "entity_id": s.entity_id,
                    "name": s.name,
                    "days_since_access": s.days_since_access,
                    "last_modified": s.last_modified
                }
                for s in stale[:20]  # Top 20 stale
            ]
        }
    
    def find_stale_memories(
        self,
        older_than_days: int = 30,
        include_never_accessed: bool = True
    ) -> List[MemoryFreshness]:
        """
        Find stale memories.
        
        Args:
            older_than_days: Find memories not accessed in X days
            include_never_accessed: Include never-accessed memories
        
        Returns:
            List of MemoryFreshness objects
        """
        kg = self.load_kg()
        entities = kg.get("entities", {})
        
        stale = []
        cutoff = datetime.now() - timedelta(days=older_than_days)
        cutoff = cutoff.replace(tzinfo=None)  # Make naive
        
        for eid, entity in entities.items():
            last_accessed = entity.get("last_accessed")
            
            if last_accessed:
                access_time = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                if access_time.tzinfo:
                    access_time = access_time.replace(tzinfo=None)
                if access_time < cutoff:
                    stale.append(self._calc_freshness(eid, entity))
            elif include_never_accessed:
                # Never accessed
                stale.append(self._calc_freshness(eid, entity))
        
        # Sort by freshness (stale first)
        stale.sort(key=lambda f: f.freshness_score)
        
        return stale
    
    def suggest_refresh(
        self,
        limit: int = 10
    ) -> List[Dict]:
        """
        Suggest memories that should be refreshed.
        
        Returns:
            List of suggestions
        """
        stale = self.find_stale_memories(older_than_days=7)
        
        suggestions = []
        for f in stale[:limit]:
            reason = "Never accessed"
            if f.days_since_access:
                reason = f"Not accessed in {f.days_since_access} days"
            
            suggestions.append({
                "entity_id": f.entity_id,
                "name": f.name,
                "reason": reason,
                "last_modified": f.last_modified,
                "priority": "HIGH" if f.days_since_access and f.days_since_access > 30 else "MEDIUM"
            })
        
        return suggestions
    
    def get_top_accessed(
        self,
        limit: int = 10,
        min_count: int = 1
    ) -> List[MemoryFreshness]:
        """
        Get most accessed memories.
        
        Args:
            limit: Maximum to return
            min_count: Minimum access count
        
        Returns:
            List of MemoryFreshness objects
        """
        kg = self.load_kg()
        entities = kg.get("entities", {})
        
        accessed = []
        for eid, entity in entities.items():
            if entity.get("access_count", 0) >= min_count:
                accessed.append(self._calc_freshness(eid, entity))
        
        # Sort by access count
        accessed.sort(key=lambda f: f.access_count, reverse=True)
        
        return accessed[:limit]
    
    def prune_never_accessed(
        self,
        older_than_days: int = 90,
        dry_run: bool = True
    ) -> Tuple[int, List[str]]:
        """
        Find entities that were never accessed and are old.
        
        Returns:
            Tuple of (count, list of entity_ids)
        """
        kg = self.load_kg()
        entities = kg.get("entities", {})
        
        to_prune = []
        cutoff = datetime.now() - timedelta(days=older_than_days)
        
        for eid, entity in entities.items():
            if entity.get("access_count", 0) == 0:
                created = entity.get("created")
                if created:
                    created_time = datetime.fromisoformat(created)
                    if created_time < cutoff:
                        to_prune.append(eid)
        
        if not dry_run and to_prune:
            for eid in to_prune:
                del entities[eid]
            kg["entities"] = entities
            self.save_kg(kg)
        
        return len(to_prune), to_prune


# Convenience functions
def get_freshness(entity_id: str) -> Optional[float]:
    """Get freshness score for an entity."""
    tracker = MemoryFreshnessTracker()
    freshness = tracker.get_freshness(entity_id)
    return freshness.freshness_score if freshness else None


def record_memory_access(entity_id: str, name: str = None) -> None:
    """Record that a memory was accessed."""
    tracker = MemoryFreshnessTracker()
    tracker.record_access(entity_id, name)


# ============ CLI Interface ============

if __name__ == "__main__":
    print("Memory Freshness Tracker")
    print("=" * 50)
    print()
    
    tracker = MemoryFreshnessTracker()
    report = tracker.get_freshness_report()
    
    print("📊 Freshness Report:")
    print(f"   Total entities: {report['total_entities']}")
    print(f"   ✅ Fresh (7d): {report['fresh']}")
    print(f"   ⚠️  Aging: {report['aging']}")
    print(f"   ❌ Stale (90d+): {report['stale']}")
    print(f"   📭 Never accessed: {report['never_accessed']}")
    print(f"   Avg freshness: {report['avg_freshness']:.2f}")
    
    if report['stale_memories']:
        print()
        print("❌ Stale Memories (should refresh):")
        for m in report['stale_memories'][:5]:
            print(f"   {m['name']}")
            print(f"      Last modified: {m['last_modified']}")
            print(f"      Days since access: {m['days_since_access']}")
    
    # Suggestions
    suggestions = tracker.suggest_refresh(limit=5)
    if suggestions:
        print()
        print("💡 Refresh Suggestions:")
        for s in suggestions:
            print(f"   [{s['priority']}] {s['name']}")
            print(f"      {s['reason']}")
    
    # Top accessed
    top = tracker.get_top_accessed(limit=5)
    if top:
        print()
        print("🏆 Top Accessed:")
        for t in top:
            print(f"   {t.access_count}x {t.name}")

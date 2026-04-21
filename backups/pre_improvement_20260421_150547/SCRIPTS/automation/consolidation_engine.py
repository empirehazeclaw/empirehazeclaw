#!/usr/bin/env python3
"""
Consolidation Engine — Phase 2 of Learning-Memory Symbiosis
============================================================

Implements the TWO consolidation pathways from memory research:

1. EPISODIC → SEMANTIC (Events → KG)
   - Monitor Event Bus for repeated patterns
   - If event pattern appears 3+ times → create KG entity
   
2. SEMANTIC → PROCEDURAL (KG → Learnings)
   - KG entities that are "notable" → learnings
   - Successful patterns → strategies

Based on:
- Tulving Taxonomy (Episodic/Semantic/Procedural memory)
- Mem0 consolidation pipelines
- Claude Diary Pattern

Usage:
    python3 consolidation_engine.py run
    python3 consolidation_engine.py status
    python3 consolidation_engine.py test
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVENT_BUS = WORKSPACE / "data/events/events.jsonl"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LEARNINGS_INDEX = WORKSPACE / "data/learnings/index.json"

sys.path.insert(0, str(WORKSPACE / 'SCRIPTS/automation'))

try:
    from learnings_service import LearningsService
except:
    LearningsService = None


class ConsolidationEngine:
    """
    Extracts patterns from events and consolidates them:
    
    EPISODIC (Events) → SEMANTIC (KG) → PROCEDURAL (Learnings)
    """
    
    def __init__(self):
        self.events = self._load_events()
        self.kg = self._load_kg()
        self.learnings = LearningsService() if LearningsService else None
        
        # Thresholds
        self.PATTERN_THRESHOLD = 3  # Appear 3+ times in 24h → extract
        self.TIME_WINDOW_HOURS = 24
        
    def _load_events(self) -> List[Dict]:
        """Load recent events from Event Bus."""
        events = []
        if EVENT_BUS.exists():
            with open(EVENT_BUS) as f:
                for line in f:
                    try:
                        events.append(json.loads(line.strip()))
                    except:
                        pass
        return events
    
    def _load_kg(self) -> dict:
        """Load Knowledge Graph."""
        try:
            with open(KG_PATH) as f:
                return json.load(f)
        except:
            return {"entities": {}, "relations": {}}
    
    def _save_kg(self):
        """Save Knowledge Graph."""
        KG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(KG_PATH, 'w') as f:
            json.dump(self.kg, f, indent=2)
    
    def get_recent_events(self, hours: int = 24) -> List[Dict]:
        """Get events from last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = []
        for event in self.events:
            try:
                event_time = datetime.fromisoformat(event.get('timestamp', '2020-01-01'))
                if event_time > cutoff:
                    recent.append(event)
            except:
                pass
        return recent
    
    def extract_event_patterns(self, hours: int = 24) -> Dict[str, int]:
        """
        EPISODIC → SEMANTIC consolidation.
        
        Find repeated event types/patterns in recent events.
        Returns: {pattern: count}
        """
        recent = self.get_recent_events(hours)
        patterns = Counter()
        
        for event in recent:
            # Extract pattern key from event
            event_type = event.get('type', 'unknown')
            source = event.get('source', 'unknown')
            action = event.get('data', {}).get('action', '')
            
            # Create pattern key
            pattern_key = f"{event_type}:{source}:{action}" if action else f"{event_type}:{source}"
            patterns[pattern_key] += 1
            
            # Also track by type alone
            patterns[event_type] += 1
        
        return dict(patterns)
    
    def consolidate_episodic_to_semantic(self, dry_run: bool = False) -> Dict:
        """
        EPISODIC → SEMANTIC: Events that repeat 3+ times → KG entities.
        
        Example: 10x "cron_error" events → KG entity "CronErrorPattern"
        """
        patterns = self.extract_event_patterns(self.TIME_WINDOW_HOURS)
        existing_entities = set(self.kg.get('entities', {}).keys())
        
        consolidated = {"entities_created": 0, "relations_created": 0, "patterns": []}
        
        for pattern, count in patterns.items():
            if count >= self.PATTERN_THRESHOLD:
                # Create KG entity for this pattern
                entity_id = f"pattern_{pattern.replace(':', '_').replace(' ', '_')[:50]}"
                
                if entity_id not in existing_entities:
                    entity = {
                        "type": "ConsolidatedPattern",
                        "name": f"Pattern: {pattern}",
                        "facts": [
                            f"Appearances: {count} in last {self.TIME_WINDOW_HOURS}h",
                            f"First seen: {datetime.utcnow().isoformat()}",
                            f"Consolidation: episodic_to_semantic"
                        ],
                        "metadata": {
                            "pattern": pattern,
                            "count": count,
                            "consolidated_at": datetime.utcnow().isoformat()
                        }
                    }
                    
                    if not dry_run:
                        self.kg.setdefault("entities", {})[entity_id] = entity
                        self.kg.setdefault("relations", {})[f"rel_{len(self.kg.get('relations', {}))}"] = {
                            "from": entity_id,
                            "to": "ConsolidationEngine",
                            "type": "created_by"
                        }
                    
                    consolidated["entities_created"] += 1
                    consolidated["patterns"].append(f"{pattern} (x{count})")
        
        if not dry_run and consolidated["entities_created"] > 0:
            self._save_kg()
        
        return consolidated
    
    def consolidate_semantic_to_procedural(self, dry_run: bool = False) -> Dict:
        """
        SEMANTIC → PROCEDURAL: Notable KG entities → Learnings.
        
        Extract high-value entities from KG and convert to learnings
        that can influence decision-making.
        """
        if not self.learnings:
            return {"learnings_created": 0, "reason": "LearningsService unavailable"}
        
        existing_learning_ids = {l.get("id") for l in self.learnings.index["recent"]}
        
        consolidated = {"learnings_created": 0, "entities_processed": 0}
        
        # Find notable entity types
        notable_types = ["ConsolidatedPattern", "LearningPattern", "Insight", "Strategy"]
        
        for entity_id, entity in self.kg.get("entities", {}).items():
            entity_type = entity.get("type", "")
            if entity_type not in notable_types:
                continue
            
            consolidated["entities_processed"] += 1
            
            # Skip if already converted to learning
            if f"kg_{entity_id}" in existing_learning_ids:
                continue
            
            # Extract useful info
            name = entity.get("name", entity_id)
            facts = entity.get("facts", [])
            
            # Create learning from entity
            learning_text = f"From KG: {name}"
            if facts:
                learning_text += f" | {' | '.join(facts[:2])}"
            
            if not dry_run:
                self.learnings.record_learning(
                    source="Consolidation Engine",
                    category="pattern",
                    learning=learning_text[:200],
                    context="consolidated",
                    outcome="success"
                )
            
            consolidated["learnings_created"] += 1
        
        return consolidated
    
    def run_full_consolidation(self, dry_run: bool = False) -> Dict:
        """
        Run complete consolidation cycle:
        
        1. EPISODIC → SEMANTIC: Events → KG patterns
        2. SEMANTIC → PROCEDURAL: KG patterns → Learnings
        """
        print("=" * 50)
        print("CONSOLIDATION ENGINE - Full Cycle")
        print("=" * 50)
        
        # Step 1: Extract patterns from events
        print("\n[1/3] Analyzing event patterns...")
        patterns = self.extract_event_patterns(self.TIME_WINDOW_HOURS)
        top_patterns = sorted(patterns.items(), key=lambda x: -x[1])[:10]
        print(f"    Found {len(patterns)} unique patterns in last {self.TIME_WINDOW_HOURS}h")
        for p, c in top_patterns[:5]:
            if c >= self.PATTERN_THRESHOLD:
                print(f"    ⚠️  {p}: {c}x")
            else:
                print(f"    {p}: {c}x")
        
        # Step 2: Episodic → Semantic
        print("\n[2/3] Consolidating Episodic → Semantic (Events → KG)...")
        semantic_result = self.consolidate_episodic_to_semantic(dry_run)
        print(f"    Entities created: {semantic_result['entities_created']}")
        for p in semantic_result.get('patterns', [])[:5]:
            print(f"    ⚡ {p}")
        
        # Step 3: Semantic → Procedural
        print("\n[3/3] Consolidating Semantic → Procedural (KG → Learnings)...")
        procedural_result = self.consolidate_semantic_to_procedural(dry_run)
        print(f"    Learnings created: {procedural_result['learnings_created']}")
        
        total = (
            semantic_result['entities_created'] + 
            procedural_result['learnings_created']
        )
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Total consolidations: {total}")
        
        return {
            "patterns_found": len(patterns),
            "semantic": semantic_result,
            "procedural": procedural_result,
            "total_changes": total
        }


def status():
    """Show consolidation status."""
    engine = ConsolidationEngine()
    patterns = engine.extract_event_patterns(24)
    
    print("=" * 50)
    print("CONSOLIDATION ENGINE - Status")
    print("=" * 50)
    print(f"\nEvents analyzed: {len(engine.events)}")
    print(f"KG entities: {len(engine.kg.get('entities', {}))}")
    
    if LearningsService:
        ls = LearningsService()
        print(f"Learnings: {len(ls.index['recent'])}")
    
    print(f"\nPatterns in last 24h: {len(patterns)}")
    print("\nTop patterns (threshold >= 3):")
    for p, c in sorted(patterns.items(), key=lambda x: -x[1])[:10]:
        if c >= engine.PATTERN_THRESHOLD:
            print(f"  ⚠️  {p}: {c}x")
        else:
            print(f"     {p}: {c}x")
    
    print(f"\nPattern threshold: {engine.PATTERN_THRESHOLD} appearances")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: consolidation_engine.py [run|status|test]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        engine = ConsolidationEngine()
        engine.run_full_consolidation(dry_run=False)
    elif cmd == "status":
        status()
    elif cmd == "test":
        engine = ConsolidationEngine()
        result = engine.run_full_consolidation(dry_run=True)
        print(f"\n✅ Test complete. Would make {result['total_changes']} changes.")
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: consolidation_engine.py [run|status|test]")

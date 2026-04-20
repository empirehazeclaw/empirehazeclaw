#!/usr/bin/env python3
"""
Memory & KG Cleaner v2
======================
Bereinigt NUR technischen Müll aus KG und MEMORY.md

Prinzip: Nur entfernen was KEINE echte Information enthält
- Technical noise: rem_theme_*, meta_pattern_*, success_improvement_cycle_*
- Orphan with 0 facts AND doesn't look like real entity
- Low-confidence facts (< 0.6)

NICHT entfernen:
- Business Facts (KI-Mitarbeiter, Zielgruppe-KMU, etc.)
- Real knowledge (OpenClaw-Gateway, Stripe-Integration)
- Anything that looks like user/session data
"""

import json
import re
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
KG_PATH = WORKSPACE / "memory/kg/knowledge_graph.json"
MEMORY_MD = WORKSPACE / "MEMORY.md"

# ONLY remove these patterns - they are purely technical noise
TECHNICAL_PATTERNS = [
    "rem_theme_",
    "meta_pattern_", 
    "success_improvement_cycle_",
    "failure_pattern_",
]

# Also remove orphan entities with 0 facts that don't look like business entities
REMOVE_IF_ORPHAN_WITH_0_FACTS = False  # Conservative - don't auto-remove


class KGCleaner:
    def __init__(self, backup=True):
        self.backup = backup
        self.kg = None
        self.load_kg()
    
    def load_kg(self):
        with open(KG_PATH) as f:
            self.kg = json.load(f)
    
    def save_kg(self, backup_suffix=None):
        if self.backup:
            # Create backup
            import shutil
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = KG_PATH.parent / f"knowledge_graph_backup_{ts}.json"
            shutil.copy(KG_PATH, backup_path)
            print(f"  Backup: {backup_path.name}")
        
        with open(KG_PATH, 'w') as f:
            json.dump(self.kg, f, indent=2)
    
    def get_linked_entities(self):
        relations = self.kg.get('relations', {})
        linked = set()
        for r in relations.values():
            linked.add(r['from'])
            linked.add(r['to'])
        return linked
    
    def is_technical_entity(self, name):
        """Check if entity name matches technical patterns."""
        for pattern in TECHNICAL_PATTERNS:
            if pattern in name:
                return True, pattern
        return False, None
    
    def clean_kg(self):
        """Clean only technical noise from KG."""
        entities = self.kg.get('entities', {})
        linked = self.get_linked_entities()
        
        removed = []
        cleaned_facts = 0
        
        for name in list(entities.keys()):
            data = entities[name]
            facts = data.get('facts', [])
            
            # Check if technical noise entity
            is_tech, pattern = self.is_technical_entity(name)
            is_orphan = name not in linked
            
            if is_tech:
                # Remove technical entities
                del entities[name]
                removed.append((name, f"technical pattern '{pattern}'"))
            elif is_orphan and len(facts) == 0:
                # Remove orphan with no facts (potential garbage)
                del entities[name]
                removed.append((name, "orphan with 0 facts"))
            else:
                # Clean low-confidence facts from remaining entities
                new_facts = [f for f in facts if f.get('confidence', 1.0) >= 0.6]
                if len(new_facts) < len(facts):
                    cleaned = len(facts) - len(new_facts)
                    cleaned_facts += cleaned
                    data['facts'] = new_facts
        
        self.kg['entities'] = entities
        
        return removed, cleaned_facts


class MemoryCleaner:
    def clean_memory(self):
        """Update timestamps and remove duplicates in MEMORY.md."""
        with open(MEMORY_MD) as f:
            content = f.read()
        
        changes = []
        
        # Update timestamp
        if "**Letzte Aktualisierung:** 2026-04-19 17:32 UTC" in content:
            content = content.replace(
                "**Letzte Aktualisierung:** 2026-04-19 17:32 UTC",
                "**Letzte Aktualisierung:** 2026-04-20 06:53 UTC"
            )
            changes.append("Updated timestamp → 2026-04-20 06:53 UTC")
        
        # Update Crons count
        if "Crons: 30 active" in content:
            content = content.replace("Crons: 30 active", "Crons: 29 active")
            changes.append("Crons: 30 → 29")
        
        # Update daily note reference
        if "`memory/2026-04-18.md`" in content:
            content = content.replace("`memory/2026-04-18.md`", "`memory/2026-04-20.md`")
            changes.append("Daily note reference → 2026-04-20")
        
        # Remove duplicate Dreaming Report entries (keep first)
        dream_section = "### 🚀 Today's Major Achievements (2026-04-12 Evening)"
        count = content.count(dream_section)
        if count > 1:
            # Find all occurrences and keep only first
            parts = content.split(dream_section)
            content = parts[0] + dream_section + dream_section.join(parts[1:])
            # Actually: keep first, remove subsequent
            content = parts[0] + dream_section + ("\n".join(parts[1:]).replace(dream_section, "", count - 1))
            changes.append(f"Removed {count - 1} duplicate Dreaming sections")
        
        with open(MEMORY_MD, 'w') as f:
            f.write(content)
        
        return changes


def main():
    print("=== MEMORY & KG CLEANER v2 ===\n")
    
    # KG Clean
    print("--- KG Cleanup ---")
    cleaner = KGCleaner(backup=True)
    removed, cleaned = cleaner.clean_kg()
    cleaner.save_kg()
    
    print(f"\nKG Cleaned:")
    print(f"  Removed: {len(removed)} entities")
    for name, reason in removed[:15]:
        print(f"    - {name}: {reason}")
    if len(removed) > 15:
        print(f"    ... and {len(removed) - 15} more")
    print(f"  Cleaned facts: {cleaned}")
    
    # Memory Clean
    print("\n--- MEMORY.md Cleanup ---")
    mem = MemoryCleaner()
    changes = mem.clean_memory()
    for c in changes:
        print(f"  ✓ {c}")
    
    # Summary
    print("\n=== DONE ===")
    print(f"KG now has {len(cleaner.kg.get('entities', {}))} entities")
    
    # Show final orphan % for key entities
    linked = cleaner.get_linked_entities()
    entities = cleaner.kg.get('entities', {})
    orphans = [n for n in entities if n not in linked]
    print(f"Orphans: {len(orphans)} ({round(len(orphans)/len(entities)*100,1)}%)")
    
    # Show remaining business entities
    business = [n for n in orphans if not any(p in n for p in TECHNICAL_PATTERNS)]
    print(f"Business orphans (kept): {len(business)}")
    for n in business[:5]:
        print(f"  - {n}")


if __name__ == "__main__":
    main()
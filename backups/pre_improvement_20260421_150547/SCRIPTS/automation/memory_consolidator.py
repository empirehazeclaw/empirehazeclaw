#!/usr/bin/env python3
"""
Memory Consolidator — Phase 7 of Learning-Memory Symbiosis
==========================================================

Consolidates learnings into persistent memory files:
- Daily: Learnings summary → MEMORY.md
- Weekly: KG health report
- Monthly: Strategy effectiveness report
- Archive: Old learnings to memory/archive/

Based on Claude Diary Pattern (rlancemartin.github.io)

Usage:
    python3 memory_consolidator.py daily
    python3 memory_consolidator.py weekly
    python3 memory_consolidator.py monthly
    python3 memory_consolidator.py archive
    python3 memory_consolidator.py all
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "ceo/memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"
MEMORY_MD = MEMORY_DIR / "MEMORY.md"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LEARNINGS_INDEX = WORKSPACE / "data/learnings/index.json"

sys.path.insert(0, str(WORKSPACE / 'SCRIPTS/automation'))

try:
    from learnings_service import LearningsService
except:
    LearningsService = None


class MemoryConsolidator:
    """
    Consolidates learnings into persistent memory.
    
    Implements the Claude Diary Pattern:
    Session → Observations → Pattern Analysis → Rules Update
    """
    
    def __init__(self):
        self.learnings = LearningsService() if LearningsService else None
        self.today = datetime.utcnow().strftime("%Y-%m-%d")
        self.now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    def _load_kg(self):
        """Load KG."""
        try:
            with open(KG_PATH) as f:
                return json.load(f)
        except:
            return {"entities": {}, "relations": {}}
    
    def consolidate_daily(self) -> Dict:
        """
        Daily consolidation: Learnings → MEMORY.md
        
        Extracts key learnings from the day and adds to MEMORY.md
        """
        if not self.learnings:
            return {"error": "LearningsService unavailable"}
        
        result = {
            "learnings_summary": [],
            "strategies": {},
            "patterns": [],
            "issues": []
        }
        
        # Get learnings from last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = []
        for l in self.learnings.index["recent"]:
            try:
                lt = datetime.fromisoformat(l.get("timestamp", "2020-01-01"))
                if lt > cutoff:
                    recent.append(l)
            except:
                pass
        
        # Summarize by category
        categories = Counter(l.get("category") for l in recent)
        result["learnings_summary"] = [
            {"category": cat, "count": cnt}
            for cat, cnt in categories.most_common(5)
        ]
        
        # Get top strategies
        strategies = self.learnings.index.get("strategy_effectiveness", {})
        top = sorted(strategies.items(), key=lambda x: -x[1])[:5]
        result["strategies"] = {s: v for s, v in top}
        
        # Get recent patterns
        patterns = [l for l in recent if l.get("category") == "pattern"]
        result["patterns"] = [p.get("learning", "")[:80] for p in patterns[:5]]
        
        # Get issues/failures
        failures = [l for l in recent if l.get("outcome") == "failure"]
        result["issues"] = [f.get("learning", "")[:80] for f in failures[:3]]
        
        # Format for MEMORY.md
        md_section = self._format_daily_section(result)
        
        # Append to MEMORY.md
        MEMORY_MD.parent.mkdir(parents=True, exist_ok=True)
        with open(MEMORY_MD, "a") as f:
            f.write("\n" + md_section)
        
        result["written_to"] = str(MEMORY_MD)
        return result
    
    def _format_daily_section(self, data: Dict) -> str:
        """Format daily consolidation as markdown."""
        lines = [
            f"\n## {self.today} — Daily Learnings Summary",
            "",
            f"_Consolidated: {self.now}_",
            "",
        ]
        
        # Strategies
        if data.get("strategies"):
            lines.append("### Strategy Effectiveness")
            for s, v in data["strategies"].items():
                verdict = "EFFECTIVE" if v > 0 else "INEFFECTIVE" if v < 0 else "NEUTRAL"
                lines.append(f"- **{s}**: {v} ({verdict})")
            lines.append("")
        
        # Patterns
        if data.get("patterns"):
            lines.append("### Patterns Discovered")
            for p in data["patterns"]:
                lines.append(f"- {p}")
            lines.append("")
        
        # Issues
        if data.get("issues"):
            lines.append("### Issues Resolved")
            for i in data["issues"]:
                lines.append(f"- {i}")
            lines.append("")
        
        # Category summary
        if data.get("learnings_summary"):
            lines.append("### Learnings by Category")
            for c in data["learnings_summary"]:
                lines.append(f"- {c['category']}: {c['count']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def consolidate_weekly(self) -> Dict:
        """
        Weekly consolidation: KG health report
        """
        kg = self._load_kg()
        entities = kg.get("entities", {})
        relations = kg.get("relations", {})
        
        # Count by type
        types = Counter(e.get("type", "unknown") for e in entities.values())
        
        # Check for broken relations
        entity_names = set(entities.keys())
        broken_relations = []
        for rid, rel in relations.items():
            if rel.get("from") not in entity_names or rel.get("to") not in entity_names:
                broken_relations.append(rid)
        
        result = {
            "kg_entities": len(entities),
            "kg_relations": len(relations),
            "broken_relations": len(broken_relations),
            "entity_types": dict(types.most_common(10)),
            "health_percent": round((len(relations) - len(broken_relations)) / max(len(relations), 1) * 100, 1),
            "date": self.today
        }
        
        # Write to archive
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        report_file = ARCHIVE_DIR / f"kg_health_{self.today}.json"
        with open(report_file, "w") as f:
            json.dump(result, f, indent=2)
        
        result["written_to"] = str(report_file)
        return result
    
    def consolidate_monthly(self) -> Dict:
        """
        Monthly consolidation: Strategy effectiveness report
        """
        if not self.learnings:
            return {"error": "LearningsService unavailable"}
        
        # Get all strategy effectiveness data
        strategies = self.learnings.index.get("strategy_effectiveness", {})
        context_eff = self.learnings.index.get("context_effectiveness", {})
        
        result = {
            "total_strategies": len(strategies),
            "total_learnings": len(self.learnings.index["recent"]),
            "strategies": {},
            "contexts": {},
            "date": self.today
        }
        
        # Rank strategies
        ranked = sorted(strategies.items(), key=lambda x: -x[1])
        result["strategies"] = {
            "top": ranked[:5],
            "bottom": ranked[-5:] if len(ranked) > 5 else ranked,
            "all": strategies
        }
        
        # Context effectiveness
        result["contexts"] = dict(context_eff)
        
        # Write to archive
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        report_file = ARCHIVE_DIR / f"strategy_report_{self.today}.json"
        with open(report_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        result["written_to"] = str(report_file)
        return result
    
    def archive_old_learnings(self, days: int = 30) -> Dict:
        """
        Archive learnings older than specified days.
        """
        if not self.learnings:
            return {"error": "LearningsService unavailable"}
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        archived = []
        
        for l in self.learnings.index["recent"]:
            try:
                lt = datetime.fromisoformat(l.get("timestamp", "2020-01-01"))
                if lt < cutoff:
                    archived.append(l)
            except:
                pass
        
        # Write archive
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        archive_file = ARCHIVE_DIR / f"learnings_archive_{self.today}.json"
        
        with open(archive_file, "w") as f:
            json.dump({
                "archived_at": self.now,
                "count": len(archived),
                "learnings": archived
            }, f, indent=2, default=str)
        
        # Prune from active
        prune_result = self.learnings.prune_old_learnings(days=days, dry_run=False)
        
        return {
            "archived_count": len(archived),
            "archived_to": str(archive_file),
            "pruned_count": prune_result.get("count", 0),
            "remaining": prune_result.get("remaining", 0)
        }
    
    def run_all(self) -> Dict:
        """Run all consolidation tasks."""
        print("=" * 50)
        print("MEMORY CONSOLIDATION - Full Run")
        print("=" * 50)
        
        results = {}
        
        print("\n[1/4] Daily consolidation (→ MEMORY.md)...")
        results["daily"] = self.consolidate_daily()
        print(f"    Written: {results['daily'].get('written_to', 'N/A')}")
        
        print("\n[2/4] Weekly consolidation (KG health)...")
        results["weekly"] = self.consolidate_weekly()
        print(f"    KG Health: {results['weekly'].get('health_percent', 0)}%")
        
        print("\n[3/4] Monthly consolidation (Strategy report)...")
        results["monthly"] = self.consolidate_monthly()
        print(f"    Strategies tracked: {results['monthly'].get('total_strategies', 0)}")
        
        print("\n[4/4] Archiving old learnings...")
        results["archive"] = self.archive_old_learnings(days=30)
        print(f"    Archived: {results['archive'].get('archived_count', 0)}")
        
        print("\n" + "=" * 50)
        print("Consolidation complete!")
        print("=" * 50)
        
        return results


def main():
    if len(sys.argv) < 2:
        print("Usage: memory_consolidator.py [daily|weekly|monthly|archive|all]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    consolidator = MemoryConsolidator()
    
    if cmd == "daily":
        result = consolidator.consolidate_daily()
    elif cmd == "weekly":
        result = consolidator.consolidate_weekly()
    elif cmd == "monthly":
        result = consolidator.consolidate_monthly()
    elif cmd == "archive":
        result = consolidator.archive_old_learnings()
    elif cmd == "all":
        result = consolidator.run_all()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: memory_consolidator.py [daily|weekly|monthly|archive|all]")
        sys.exit(1)
    
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

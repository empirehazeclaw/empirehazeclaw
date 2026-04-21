#!/usr/bin/env python3
"""
Learnings Consumer — Phase 1 of Improvement Plan
================================================
Consumes learnings from memory/ files and syncs to LearningsService.
Provides closed-loop feedback: Learn → Index → Use → Outcome

Event Types Handled:
  - learning_discovered: New learning from any source
  - decision_made: Decision that used learnings
  - decision_outcome: Result of a decision

This closes the loop that was identified as broken.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE / "ceo/memory/learnings"
RALPH_LEARNINGS = WORKSPACE / "ceo/memory/ralph_learnings.md"
MEMORY_DIR = WORKSPACE / "ceo/memory"

# Import LearningsService
import sys
sys.path.insert(0, str(WORKSPACE / "SCRIPTS/automation"))
try:
    from learnings_service import LearningsService
except ImportError:
    LearningsService = None


class LearningsConsumer:
    """
    Consumes learnings from files and syncs to LearningsService.
    
    Sources:
    - memory/learnings/*.md (explicit learnings)
    - memory/ralph_learnings.md (Ralph Loop learnings)
    - memory/YYYY-MM-DD.md (daily memory with embedded learnings)
    """
    
    def __init__(self):
        self.learnings_service = LearningsService() if LearningsService else None
        self.state_file = WORKSPACE / "data/learnings/consumer_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load consumer state for incremental processing."""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {
            "last_processed_file": None,
            "last_processed_line": {},
            "processed_count": 0,
            "learnings_synced": 0
        }
    
    def _save_state(self):
        """Save consumer state."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def scan_learnings_directory(self) -> List[Dict]:
        """Scan learnings directory for new learnings to process."""
        if not LEARNINGS_DIR.exists():
            return []
        
        learnings = []
        for f in LEARNINGS_DIR.glob("*.md"):
            content = f.read_text()
            extracted = self._extract_learnings_from_file(f.name, content)
            learnings.extend(extracted)
        
        return learnings
    
    def _extract_learnings_from_file(self, filename: str, content: str) -> List[Dict]:
        """Extract learnings from a file."""
        learnings = []
        
        # Pattern for markdown learnings (## Learning: or - [timestamp])
        patterns = [
            # Pattern: ## Learning: YYYY-MM-DD — Title
            r'## Learning:\s*(\d{4}-\d{2}-\d{2}).*?\n(.*?)(?=##|\Z)',
            # Pattern: - [YYYY-MM-DD HH:MM] [category:outcome] Description
            r'\[\s*(\d{4}-\d{2}-\d{2})\s*\]\s*\[\s*([^:\]]+):(\s*\w+)\s*\]\s*(.*?)(?=\n-|\Z)',
        ]
        
        for match in re.finditer(patterns[1], content, re.MULTILINE):
            timestamp, category, outcome, description = match.groups()
            learnings.append({
                "source": filename,
                "timestamp": timestamp,
                "category": category.strip(),
                "outcome": outcome.strip() if outcome else None,
                "learning": description.strip()[:500],
                "type": "Ralph_style"
            })
        
        # Also extract from ## sections
        for match in re.finditer(patterns[0], content, re.DOTALL):
            date_str, body = match.groups()
            learnings.append({
                "source": filename,
                "timestamp": date_str,
                "category": self._extract_category_from_body(body),
                "learning": body.strip()[:500],
                "type": "Deep_Dive_style"
            })
        
        return learnings
    
    def _extract_category_from_body(self, body: str) -> str:
        """Extract category from learning body."""
        if "error" in body.lower() or "fail" in body.lower():
            return "error"
        elif "success" in body.lower() or "fixed" in body.lower():
            return "success"
        elif "insight" in body.lower() or "learned" in body.lower():
            return "insight"
        return "general"
    
    def scan_ralph_learnings(self) -> List[Dict]:
        """Scan ralph_learnings.md for new entries."""
        if not RALPH_LEARNINGS.exists():
            return []
        
        content = RALPH_LEARNINGS.read_text()
        learnings = []
        
        # Pattern: - [2026-04-20 07:34] [maintenance:success] Description
        pattern = r'\[\s*(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}\s*\]\s*\[\s*([^:\]]+):(\s*\w+)\s*\]\s*(.*?)(?=\n-|\Z)'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            date_str, category, outcome, description = match.groups()
            learnings.append({
                "source": "Ralph Learning",
                "timestamp": date_str,
                "category": category.strip(),
                "outcome": outcome.strip(),
                "learning": description.strip()[:500],
                "type": "Ralph_entry"
            })
        
        return learnings
    
    def scan_daily_memory(self, days: int = 7) -> List[Dict]:
        """Scan recent daily memory files for embedded learnings."""
        learnings = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for f in sorted(MEMORY_DIR.glob("memory/YYYY-MM-DD.md"), reverse=True)[:days]:
            try:
                file_date = datetime.strptime(f.stem.split("_")[0], "%Y-%m-%d")
                if file_date < cutoff:
                    continue
            except:
                pass
            
            content = f.read_text()
            
            # Extract ## Learning sections
            pattern = r'## Learning:\s*(.*?)(?=##|\Z)'
            for match in re.finditer(pattern, content, re.DOTALL):
                learnings.append({
                    "source": f.name,
                    "timestamp": f.stem[:10],
                    "category": "general",
                    "learning": match.group(1).strip()[:500],
                    "type": "daily_memory"
                })
        
        return learnings
    
    def sync_learnings_to_service(self, learnings: List[Dict]) -> int:
        """Sync learnings to LearningsService."""
        if not self.learnings_service:
            return 0
        
        synced = 0
        for learning in learnings:
            try:
                self.learnings_service.record_learning(
                    source=learning.get("source", "Unknown"),
                    category=learning.get("category", "general"),
                    learning=learning.get("learning", ""),
                    context=self._context_from_category(learning.get("category", "")),
                    outcome=learning.get("outcome"),
                    metadata={"type": learning.get("type", "unknown")}
                )
                synced += 1
            except Exception as e:
                print(f"Warning: Failed to sync learning: {e}")
        
        return synced
    
    def _context_from_category(self, category: str) -> str:
        """Map category to context for strategy selection."""
        mapping = {
            "error": "system_optimization",
            "failure": "system_optimization",
            "success": "score_optimization",
            "insight": "pattern_matching",
            "pattern": "pattern_matching",
            "maintenance": "general",
            "learning": "learning_optimization"
        }
        return mapping.get(category.lower(), "general")
    
    def record_decision_feedback(self, decision_id: str, outcome: str, score_delta: float = None) -> bool:
        """Record outcome of a decision that used learnings."""
        if not self.learnings_service:
            return False
        
        return self.learnings_service.record_decision_outcome(
            decision_id=decision_id,
            outcome=outcome,
            score_delta=score_delta
        )
    
    def run(self) -> Dict:
        """
        Run one consumption cycle.
        
        Returns:
            Dict with stats on what was processed
        """
        stats = {
            "learnings_found": 0,
            "learnings_synced": 0,
            "decisions_recorded": 0,
            "errors": []
        }
        
        # Scan all sources
        learnings = []
        learnings.extend(self.scan_learnings_directory())
        learnings.extend(self.scan_ralph_learnings())
        learnings.extend(self.scan_daily_memory())
        
        stats["learnings_found"] = len(learnings)
        
        if learnings:
            synced = self.sync_learnings_to_service(learnings)
            stats["learnings_synced"] = synced
            self.state["learnings_synced"] += synced
        
        self.state["processed_count"] += 1
        self._save_state()
        
        return stats
    
    def get_stats(self) -> Dict:
        """Get consumer statistics."""
        return {
            "total_processed": self.state.get("processed_count", 0),
            "total_synced": self.state.get("learnings_synced", 0),
            "last_file": self.state.get("last_processed_file"),
            "service_available": self.learnings_service is not None
        }


def main():
    import argparse
    
    consumer = LearningsConsumer()
    parser = argparse.ArgumentParser(description="Learnings Consumer")
    
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("run", help="Run consumption cycle")
    sub.add_parser("stats", help="Show consumer stats")
    
    # Manual sync
    p = sub.add_parser("sync", help="Force sync all learnings")
    p.add_argument("--source", default="all", help="Source to sync")
    
    args = parser.parse_args()
    
    if args.cmd == "run":
        print("Running Learnings Consumer...")
        stats = consumer.run()
        print(f"Learnings found: {stats['learnings_found']}")
        print(f"Learnings synced: {stats['learnings_synced']}")
        if stats.get('errors'):
            print(f"Errors: {stats['errors']}")
    
    elif args.cmd == "stats":
        s = consumer.get_stats()
        print("Learnings Consumer Stats:")
        print(f"  Processed runs: {s['total_processed']}")
        print(f"  Total learnings synced: {s['total_synced']}")
        print(f"  Last file: {s['last_file']}")
        print(f"  Service available: {s['service_available']}")
    
    elif args.cmd == "sync":
        print(f"Syncing from {args.source}...")
        all_learnings = []
        all_learnings.extend(consumer.scan_learnings_directory())
        all_learnings.extend(consumer.scan_ralph_learnings())
        if args.source == "all":
            all_learnings.extend(consumer.scan_daily_memory())
        synced = consumer.sync_learnings_to_service(all_learnings)
        print(f"Synced {synced} learnings")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
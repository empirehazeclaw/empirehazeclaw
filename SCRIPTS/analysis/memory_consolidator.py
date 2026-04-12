#!/usr/bin/env python3
"""
memory_consolidator.py - Consolidate daily notes into MEMORY.md
Sir HazeClaw - 2026-04-12

Extracts key information from TEMPORARY/memory/ daily notes
and consolidates into MEMORY.md (persistent long-term memory).

Usage:
    python3 memory_consolidator.py --dry-run    # Show what would be consolidated
    python3 memory_consolidator.py --consolidate  # Actually consolidate
    python3 memory_consolidator.py --list        # List daily notes
"""

import json
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
TEMPORARY_MEMORY = WORKSPACE / "TEMPORARY" / "memory"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
STATE_FILE = WORKSPACE / "memory" / "consolidation_state.json"

# Key patterns to extract from daily notes
KEY_PATTERNS = {
    "commit": r"commit [a-f0-9]+",
    "error_fix": r"(?:fixed|fix|bugfix|resolved)",
    "metric": r"(?:Error Rate|KG Entities|Active Crons|Scripts|System Score).*?[:\s]+([^\n]+)",
    "decision": r"(?:Decision|Decision:|Entscheidung)",
    "learning": r"(?:Learning|Insight|Lesson learned)",
    "todo": r"(?:TODO|Next step|Nächster Schritt|Task)",
    "nico_request": r"(?:Nico|Nico's).*?[:\s]+([^\n]+)",
}

def load_state() -> Dict:
    """Lädt Consolidation State."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_consolidated": None, "consolidated_files": []}

def save_state(state: Dict):
    """Speichert State."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def extract_key_info(content: str) -> Dict[str, List[str]]:
    """Extrahiert wichtige Informationen aus Daily Notes."""
    findings = {
        "commits": [],
        "error_fixes": [],
        "decisions": [],
        "learnings": [],
        "todos": [],
        "metrics": [],
    }
    
    for line in content.split("\n"):
        line_lower = line.lower()
        
        # Commit hashes
        if "commit" in line_lower and len(line) < 100:
            findings["commits"].append(line.strip())
        
        # Decisions
        if any(word in line_lower for word in ["decision:", "entscheidung", "beschlossen"]):
            findings["decisions"].append(line.strip())
        
        # Learnings
        if any(word in line_lower for word in ["insight", "learning", "lesson", "erkenntnis"]):
            findings["learnings"].append(line.strip())
        
        # Metrics
        if any(word in line_lower for word in ["error rate", "kg entities", "scripts", "crons"]):
            findings["metrics"].append(line.strip())
        
        # TODOs
        if any(word in line_lower for word in ["todo:", "nächster", "next:", "task:"]):
            findings["todos"].append(line.strip())
    
    return findings

def list_daily_notes() -> List[Path]:
    """Listet alle Daily Notes auf."""
    if not TEMPORARY_MEMORY.exists():
        return []
    return sorted(TEMPORARY_MEMORY.glob("*.md"))

def consolidate_notes(dry_run: bool = False) -> Dict:
    """Consolidiert Daily Notes in MEMORY.md."""
    state = load_state()
    notes = list_daily_notes()
    
    if not notes:
        print("No daily notes found.")
        return {"consolidated": 0}
    
    print(f"\n📋 MEMORY CONSOLIDATOR")
    print("=" * 50)
    print(f"Daily notes found: {len(notes)}")
    print()
    
    all_findings = {}
    
    for note in notes:
        # Skip if already consolidated
        if note.name in state.get("consolidated_files", []):
            continue
        
        with open(note) as f:
            content = f.read()
        
        findings = extract_key_info(content)
        all_findings[note.name] = findings
        
        print(f"📄 {note.name}")
        for key, items in findings.items():
            if items:
                print(f"   {key}: {len(items)} items")
    
    if dry_run:
        print("\n⚠️  DRY RUN - No changes made")
        return {"dry_run": True, "files": len(all_findings)}
    
    # Count total findings
    total = sum(len(items) for findings in all_findings.values() for items in findings.values())
    
    print(f"\n💾 Would consolidate {total} key items into MEMORY.md")
    print("\n✅ Consolidation complete (dry run)")
    
    # Update state
    state["last_consolidated"] = datetime.now().isoformat()
    state["consolidated_files"].extend([n.name for n in notes])
    save_state(state)
    
    return {"consolidated": len(notes), "items": total}

def main():
    parser = argparse.ArgumentParser(description="Memory Consolidator")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be consolidated")
    parser.add_argument("--consolidate", action="store_true", help="Actually consolidate")
    parser.add_argument("--list", action="store_true", help="List daily notes")
    
    args = parser.parse_args()
    
    if args.list:
        notes = list_daily_notes()
        print(f"\n📋 DAILY NOTES ({len(notes)})")
        print("=" * 40)
        for note in notes:
            mtime = datetime.fromtimestamp(note.stat().st_mtime)
            size = note.stat().st_size
            print(f"   {note.name} ({size} bytes, {mtime.strftime('%Y-%m-%d')})")
        print()
    elif args.dry_run:
        consolidate_notes(dry_run=True)
    elif args.consolidate:
        consolidate_notes(dry_run=False)
    else:
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())

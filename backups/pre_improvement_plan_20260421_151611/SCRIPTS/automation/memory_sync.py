#!/usr/bin/env python3
"""
Memory Sync Script — Sir HazeClaw
Aktualisiert short_term/current.md nach jeder Session.

Usage:
    python3 memory_sync.py              # Full sync
    python3 memory_sync.py --dry-run    # Preview only
    python3 memory_sync.py --quick     # Quick status update only
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "ceo" / "memory"
CURRENT_MD = MEMORY_DIR / "short_term" / "current.md"
RECENT_MD = MEMORY_DIR / "short_term" / "recent_sessions.md"
KG_PATH = MEMORY_DIR / "kg" / "knowledge_graph.json"
HEARTBEAT_STATE = MEMORY_DIR / "heartbeat-state.json"
FEEDBACK_LOG = WORKSPACE / "logs" / "learning_feedback.json"
LEARNING_LOOP_LOG = WORKSPACE / "logs" / "learning_loop_v3.log"

def log(msg):
    print(f"[MemorySync] {msg}")

def get_session_summary():
    """Sammelt Session-Info aus verfügbaren Quellen."""
    summary = {
        "timestamp": datetime.now().isoformat() + "Z",
        "active_crons": 0,
        "kg_entities": 0,
        "kg_relations": 0,
        "loop_score": None,
        "recent_feedback": 0,
        "issues": []
    }
    
    # KG Stats
    if KG_PATH.exists():
        try:
            with open(KG_PATH) as f:
                kg = json.load(f)
            summary["kg_entities"] = len(kg.get("entities", {}))
            summary["kg_relations"] = len(kg.get("relations", {}))
        except Exception as e:
            log(f"KG read failed: {e}")
    
    # Heartbeat State
    if HEARTBEAT_STATE.exists():
        try:
            with open(HEARTBEAT_STATE) as f:
                hb = json.load(f)
            summary["loop_score"] = hb.get("lastChecks", {}).get("loop_score")
            summary["issues"] = hb.get("knownIssues", [])
        except Exception as e:
            log(f"Heartbeat state read failed: {e}")
    
    # Feedback Count
    if FEEDBACK_LOG.exists():
        try:
            with open(FEEDBACK_LOG) as f:
                lines = f.readlines()
            summary["recent_feedback"] = len([l for l in lines if "processed" in l and "false" in l])
        except Exception as e:
            log(f"Feedback log read failed: {e}")
    
    # Cron Count (approximiert)
    cron_state_file = WORKSPACE / "data" / "cron_state.json"
    if cron_state_file.exists():
        try:
            with open(cron_state_file) as f:
                cron_data = json.load(f)
            summary["active_crons"] = len([c for c in cron_data if c.get("status") == "ok"])
        except:
            pass
    
    return summary

def update_current_md(summary, dry_run=False):
    """Schreibt current.md mit aktuellen Session-Daten."""
    
    # Generate content
    content = f"""# SHORT TERM — Aktuelle Session

_Letzte Aktualisierung: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}_

---

## 🔄 CURRENT SESSION

**Letzter Sync:** {summary['timestamp']}

### 📊 System Status
| Metric | Value |
|--------|-------|
| KG Entities | {summary['kg_entities']} |
| KG Relations | {summary['kg_relations']} |
| Loop Score | {summary['loop_score'] or 'N/A'} |
| Active Crons | {summary['active_crons']} |
| Unprocessed Feedback | {summary['recent_feedback']} |

"""
    
    if summary["issues"]:
        content += "### ⚠️ Bekannte Issues\n"
        for issue in summary["issues"]:
            content += f"- {issue}\n"
        content += "\n"
    
    content += """### 🔄 Letzte Aktivitäten

"""
    
    # Hier könnten wir aus Log-Files die letzten Aktivitäten extrahieren
    # Für now: nur eine generische Aussage
    content += """- Memory System läuft (Hybrid Search + KG)
- Learning Loop v3 sammelt stündlich Feedback
- Autonomy Supervisor läuft alle 5min

---

## 📋 Quick Links

| Frage | Lese aus |
|-------|----------|
| "Was ist gerade passiert?" | `short_term/current.md` |
| "Was weiß ich über Nico?" | `long_term/facts.md` |
| "Was habe ich gelernt?" | `long_term/preferences.md` |
| "Suche nach Konzept X" | `search/memory_hybrid_search.py` |

---

*Short-term wird nach jeder Session automatisch upgedated.*
*Letzte Änderung: {}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M UTC'))
    
    if dry_run:
        log("DRY RUN — Would write:")
        print(content[:500] + "...")
        return
    
    try:
        CURRENT_MD.parent.mkdir(parents=True, exist_ok=True)
        with open(CURRENT_MD, "w") as f:
            f.write(content)
        log(f"✅ current.md updated ({len(content)} bytes)")
    except Exception as e:
        log(f"❌ Write failed: {e}")

def update_recent_sessions(summary, dry_run=False):
    """Fügt今天的 Session zu recent_sessions.md hinzu."""
    
    today = datetime.now().strftime('%Y-%m-%d')
    entry = f"""
## 📅 {today} — Daily Sync

### {datetime.now().strftime('%H:%M UTC')}
- Memory Sync durchgeführt
- KG: {summary['kg_entities']} entities, {summary['kg_relations']} relations
- Loop Score: {summary['loop_score'] or 'N/A'}
- Unprocessed Feedback: {summary['recent_feedback']}
"""
    
    if summary["issues"]:
        entry += "- Issues: " + ", ".join(summary["issues"][:3]) + "\n"
    
    if dry_run:
        log(f"DRY RUN — Would append to recent_sessions.md")
        return
    
    try:
        if RECENT_MD.exists():
            with open(RECENT_MD) as f:
                existing = f.read()
            
            # Prüfe ob heute schon ein Eintrag existiert
            if today in existing:
                log("Today's entry already exists, skipping")
                return
            
            # Behalte nur die letzten 7 Tage (ca. 14 Einträge)
            lines = existing.split("\n")
            cutoff = 0
            for i, line in enumerate(lines):
                if line.startswith("## 📅 2026"):
                    cutoff = max(cutoff, i)
            
            new_content = "\n".join(lines[:cutoff]) + entry + "\n"
        else:
            new_content = f"""# RECENT SESSIONS — Letzte Sessions

_Letzte Aktualisierung: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}_

{entry}
"""
        
        RECENT_MD.parent.mkdir(parents=True, exist_ok=True)
        with open(RECENT_MD, "w") as f:
            f.write(new_content)
        log(f"✅ recent_sessions.md updated")
    except Exception as e:
        log(f"❌ recent_sessions update failed: {e}")

def add_to_timeline(summary, dry_run=False):
    """Fügt wichtige Events zur Timeline hinzu."""
    
    # Check if there's a significant change worth recording
    timeline_path = MEMORY_DIR / "episodes" / "timeline.md"
    
    today = datetime.now().strftime('%Y-%m-%d')
    significant = []
    
    # Check for score changes
    if summary["loop_score"]:
        try:
            loop_data = WORKSPACE / "data" / "learning_coordinator.json"
            if loop_data.exists():
                with open(loop_data) as f:
                    lc = json.load(f)
                prev_score = lc.get("last_score", 0)
                curr_score = summary["loop_score"]
                if abs(curr_score - prev_score) > 0.05:
                    significant.append(f"Learning Loop score changed: {prev_score:.3f} → {curr_score:.3f}")
        except:
            pass
    
    if not significant:
        return
    
    entry = f"""
### {today} — Timeline Event
"""
    for sig in significant:
        entry += f"- {sig}\n"
    
    if dry_run:
        log(f"DRY RUN — Would add to timeline: {significant}")
        return
    
    try:
        with open(timeline_path) as f:
            existing = f.read()
        new_content = existing + entry
        with open(timeline_path, "w") as f:
            f.write(new_content)
        log(f"✅ Added to timeline")
    except Exception as e:
        log(f"❌ Timeline update failed: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Memory Sync")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--quick", action="store_true", help="Quick status only")
    args = parser.parse_args()
    
    log("Starting Memory Sync")
    
    summary = get_session_summary()
    
    if args.quick:
        log(f"Quick Status: KG={summary['kg_entities']}, Score={summary['loop_score']}")
        return
    
    update_current_md(summary, args.dry_run)
    update_recent_sessions(summary, args.dry_run)
    
    if not args.dry_run:
        add_to_timeline(summary)
    
    log("Memory Sync complete!")

if __name__ == "__main__":
    exit(main())

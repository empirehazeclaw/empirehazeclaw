#!/usr/bin/env python3
"""
Post-Mortem Generator — Phase 1, Day 2
========================================
Erstellt strukturierte Post-Mortems für jeden Failure.

Usage:
    python3 postmortem_generator.py --failure-id <id>
    python3 postmortem_generator.py --auto --since <hours>
    python3 postmortem_generator.py --list
    python3 postmortem_generator.py --view <pm-id>
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
PM_DIR = WORKSPACE / "memory" / "evaluations" / "postmortems"
FAILURE_LOG = WORKSPACE / "memory" / "failures" / "failure_log.json"

TEMPLATE = """# Post-Mortem: {title}
**ID:** {pm_id}  
**Failure ID:** #{failure_id}  
**Datum:** {timestamp}  
**Severity:** {severity}  
**Status:** {status}

---

## 📋 Executive Summary
{brief_summary}

---

## 🔍 Failure Details

### Description
{failure_description}

### Cause (Root Cause Analysis)
{root_cause}

### Impact
{impact}

### Timeline
{timeline}

---

## ❓ Root Cause
{root_cause_analysis}

---

## 🛠️ Action Items

| Action | Owner | Priority | Status | Due Date |
|--------|-------|----------|--------|----------|
{action_items}

---

## 📊 Lessons Learned

### What Went Well
{what_went_well}

### What Could Be Improved
{what_could_be_improved}

### Preventive Measures
{preventive_measures}

---

## 📎 Related Entities (KG)
{related_entities}

---

**Geschrieben:** {created_at}
**Letztes Update:** {updated_at}
"""

def init_dirs():
    PM_DIR.mkdir(parents=True, exist_ok=True)
    index_file = PM_DIR / "index.json"
    if not index_file.exists():
        index_file.write_text(json.dumps({"postmortems": [], "version": "1.0"}))

def load_failures():
    if not FAILURE_LOG.exists():
        return []
    return json.loads(FAILURE_LOG.read_text()).get("failures", [])

def load_index():
    init_dirs()
    return json.loads((PM_DIR / "index.json").read_text())

def save_index(index):
    (PM_DIR / "index.json").write_text(json.dumps(index, indent=2))

def create_postmortem(failure_id: int, override: Optional[dict] = None) -> dict:
    """Generate a post-mortem for a specific failure."""
    failures = load_failures()
    failure = next((f for f in failures if f["id"] == failure_id), None)
    
    if not failure:
        print(f"❌ Failure #{failure_id} nicht gefunden.")
        return None
    
    init_dirs()
    index = load_index()
    
    pm_id = f"PM-{len(index['postmortems']) + 1:04d}"
    now = datetime.now(timezone.utc)
    
    # Extract override or use defaults
    data = override or {}
    
    # Build timeline from failure
    timeline = f"- {failure['timestamp']} — Failure aufgetreten (ID: #{failure['id']})\n"
    timeline += f"- {now.isoformat()} — Post-Mortem erstellt\n"
    
    # Default action items based on cause type
    default_actions = {
        "timeout": ["Timeout erhöhen", "Performance-Optimierung prüfen", "Lazy-Loading implementieren"],
        "api_error": ["API Retry-Logik hinzufügen", "API Health-Check implementieren", "Fallback-Strategie definieren"],
        "validation_error": ["Input-Validierung verstärken", "Edge Cases abdecken", "Type Checking verbessern"],
        "resource_exhausted": ["Resource Limits erhöhen", "Caching implementieren", "Resource Monitoring verbessern"],
        "design_gap": ["Design Review durchführen", "Use Case Abdeckung prüfen", "Architektur-Anpassung planen"],
        "bias_confirmed": ["Training Data balancieren", "Bias-Monitoring hinzufügen", "Fairness-Checks implementieren"],
        "model_weakness": ["Model-Prompt optimieren", "Fallback-Model definieren", "Model-Monitoring verbessern"],
        "tool_failure": ["Tool-Error Handling verbessern", "Alternative Tools evaluieren", "Tool-Monitoring hinzufügen"],
    }
    
    cause = failure.get("cause", "unknown")
    actions = data.get("action_items", default_actions.get(cause, ["Root Cause analysieren", "Fix implementieren", "Testen"]))
    
    action_items_str = ""
    for i, action in enumerate(actions[:5], 1):
        action_items_str += f"| {i}. {action} | System | medium | open | TBD |\n"
    
    pm = {
        "pm_id": pm_id,
        "failure_id": failure_id,
        "timestamp": now.isoformat(),
        "severity": failure.get("severity", "medium"),
        "title": f"Post-Mortem: {failure['description'][:60]}",
        "status": "in_progress",
        "brief_summary": data.get("brief_summary", f"Failure #{failure_id} — {cause} — wird analysiert."),
        "failure_description": failure["description"],
        "root_cause": data.get("root_cause", "Zu analysieren..."),
        "impact": data.get("impact", "Impact wurde noch nicht evaluiert."),
        "timeline": timeline,
        "root_cause_analysis": data.get("root_cause_analysis", "Root Cause Analyse läuft..."),
        "action_items": actions,
        "what_went_well": data.get("what_went_well", "Noch zu evaluieren."),
        "what_could_be_improved": data.get("what_could_be_improved", "Noch zu evaluieren."),
        "preventive_measures": data.get("preventive_measures", "Noch zu definieren."),
        "related_entities": data.get("related_entities", []),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "content": TEMPLATE.format(
            title=f"Post-Mortem: {failure['description'][:60]}",
            pm_id=pm_id,
            failure_id=failure_id,
            timestamp=now.isoformat(),
            severity=failure.get("severity", "medium"),
            status="in_progress",
            brief_summary=data.get("brief_summary", f"Failure #{failure_id} — {cause} — wird analysiert."),
            failure_description=failure["description"],
            root_cause=data.get("root_cause", "Zu analysieren..."),
            impact=data.get("impact", "Impact wurde noch nicht evaluiert."),
            timeline=timeline,
            root_cause_analysis=data.get("root_cause_analysis", "Root Cause Analyse läuft..."),
            action_items=action_items_str or "| TBD | System | medium | open | TBD |\n",
            what_went_well=data.get("what_went_well", "Noch zu evaluieren."),
            what_could_be_improved=data.get("what_could_be_improved", "Noch zu evaluieren."),
            preventive_measures=data.get("preventive_measures", "Noch zu definieren."),
            related_entities=data.get("related_entities", "None yet."),
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )
    }
    
    # Save post-mortem file
    pm_file = PM_DIR / f"{pm_id}.md"
    pm_file.write_text(pm["content"])
    
    # Update index
    index["postmortems"].append({
        "pm_id": pm_id,
        "failure_id": failure_id,
        "timestamp": now.isoformat(),
        "severity": failure.get("severity", "medium"),
        "title": pm["title"],
        "status": "in_progress",
        "file": str(pm_file)
    })
    save_index(index)
    
    print(f"✅ Post-Mortem {pm_id} erstellt für Failure #{failure_id}")
    print(f"   Datei: {pm_file}")
    
    return pm

def auto_generate(since_hours: int = 24):
    """Auto-generate post-mortems for recent failures without one."""
    failures = load_failures()
    index = load_index()
    existing_failure_ids = {pm["failure_id"] for pm in index["postmortems"]}
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    
    new_failures = [
        f for f in failures
        if f["id"] not in existing_failure_ids
        and datetime.fromisoformat(f["timestamp"].replace("Z", "+00:00")) > cutoff
    ]
    
    print(f"📋 Auto-Generate Post-Mortems (Failures seit {since_hours}h):")
    print(f"   {len(new_failures)} neue Failures gefunden")
    
    for failure in new_failures:
        create_postmortem(failure["id"])
    
    return new_failures

def list_postmortems():
    """List all post-mortems."""
    index = load_index()
    
    if not index["postmortems"]:
        print("📭 Keine Post-Mortems gefunden.")
        return
    
    print(f"\n📋 Post-Mortems ({len(index['postmortems'])} total)\n")
    for pm in sorted(index["postmortems"], key=lambda x: x["timestamp"], reverse=True):
        print(f"  [{pm['status'].upper():12}] {pm['pm_id']} — Failure #{pm['failure_id']}")
        print(f"                 {pm['title'][:60]}")
        print(f"                 Severity: {pm['severity']} | {pm['timestamp'][:10]}")
        print()

def view_postmortem(pm_id: str):
    """View a specific post-mortem."""
    pm_file = PM_DIR / f"{pm_id}.md"
    if not pm_file.exists():
        print(f"❌ Post-Mortem {pm_id} nicht gefunden.")
        return
    
    print(pm_file.read_text())

def update_postmortem(pm_id: str, field: str, value: str):
    """Update a field in a post-mortem."""
    index = load_index()
    pm_entry = next((p for p in index["postmortems"] if p["pm_id"] == pm_id), None)
    
    if not pm_entry:
        print(f"❌ Post-Mortem {pm_id} nicht gefunden.")
        return
    
    pm_file = Path(pm_entry["file"])
    content = pm_file.read_text()
    
    # Simple field updates
    updates = {
        "status": ("Status:", f"**Status:** {value}"),
        "root_cause": ("## ❓ Root Cause", f"## ❓ Root Cause\n{value}"),
        "action_items": ("## 🛠️ Action Items", f"## 🛠️ Action Items\n{value}"),
    }
    
    if field in updates:
        marker, replacement = updates[field]
        if marker in content:
            # Find the section and replace
            parts = content.split(marker, 2)
            if len(parts) == 3:
                # Keep header, replace content until next ## header
                rest = parts[2]
                next_header = rest.find("## ")
                if next_header > 0:
                    content = parts[0] + marker + "\n" + replacement + "\n" + rest[next_header:]
                else:
                    content = parts[0] + marker + "\n" + replacement
                pm_file.write_text(content)
                print(f"✅ {pm_id}: {field} aktualisiert")
                
                # Update status in index if needed
                if field == "status":
                    for p in index["postmortems"]:
                        if p["pm_id"] == pm_id:
                            p["status"] = value
                            save_index(index)
                return
    
    print(f"⚠️ Feld '{field}' nicht direkt updatebar. Manual edit erforderlich.")

def main():
    parser = argparse.ArgumentParser(description="Post-Mortem Generator")
    parser.add_argument("--failure-id", type=int, help="Failure ID für Post-Mortem")
    parser.add_argument("--auto", action="store_true", help="Auto-generate für alle recent failures")
    parser.add_argument("--since", type=int, default=24, help="Stunden für --auto (default: 24)")
    parser.add_argument("--list", action="store_true", help="Liste alle Post-Mortems")
    parser.add_argument("--view", help="Zeige spezifisches Post-Mortem")
    parser.add_argument("--update", nargs=3, metavar=("PM-ID", "FIELD", "VALUE"), help="Update field")
    
    args = parser.parse_args()
    
    if args.failure_id:
        create_postmortem(args.failure_id)
    elif args.auto:
        auto_generate(args.since)
    elif args.list:
        list_postmortems()
    elif args.view:
        view_postmortem(args.view)
    elif args.update:
        update_postmortem(args.update[0], args.update[1], args.update[2])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

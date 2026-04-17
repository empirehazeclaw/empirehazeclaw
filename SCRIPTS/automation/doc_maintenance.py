#!/usr/bin/env python3
"""
Doc Maintenance — Phase 4
=========================
Auto-generates and maintains documentation:
1. Script-Tracker JSON → SCRIPT_KATALOG.md
2. Doc-Audit: Checks for outdated docs
3. Auto-updates _index.md

Usage:
    python3 doc_maintenance.py --sync-scripts   # Sync script catalog
    python3 doc_maintenance.py --audit          # Check outdated docs
    python3 doc_maintenance.py --regenerate     # Regenerate _index.md
    python3 doc_maintenance.py --full           # All of the above
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
NOTES_DIR = WORKSPACE / "memory/notes"
SCRIPTS_AUTOMATION = WORKSPACE / "SCRIPTS/automation"
SCRIPTS_DIR = WORKSPACE / "scripts"
SCRIPT_TRACKER = WORKSPACE / "data/doc_script_tracker.json"

# Priority levels
PRIORITY_1 = ["learning_loop_v3.py", "autonomous_agent.py", "autonomy_supervisor.py",
              "gateway_recovery.py", "bug_scanner.py", "bug_fix_pipeline.py"]
PRIORITY_2 = ["run_smart_evolver.sh", "health_check.py", "cron_watchdog.py",
              "kg_access_updater.py", "learning_coordinator.py"]
PRIORITY_3 = ["context_compressor.py", "memory_sync.py", "heartbeat_updater.py",
              "morning_brief.py", "backup_manager.py"]
PRIORITY_4 = ["error_reducer.py", "cron_monitor.py", "cron_optimizer.py",
              "daily_summary.py", "session_cleanup.py", "decision_matrix.py"]


def get_script_priority(name: str) -> int:
    """Determine script priority level."""
    if name in PRIORITY_1:
        return 1
    elif name in PRIORITY_2:
        return 2
    elif name in PRIORITY_3:
        return 3
    elif name.endswith(".sh"):
        return 2
    else:
        return 4


def get_script_category(name: str) -> str:
    """Determine script category based on name patterns."""
    if any(x in name for x in ["learning", "loop", "coordinator"]):
        return "🧠 MEMORY & LEARNING"
    elif any(x in name for x in ["bug", "error", "fix"]):
        return "🐛 BUG HANDLING"
    elif any(x in name for x in ["health", "monitor", "watchdog", "recovery"]):
        return "📊 MONITORING"
    elif any(x in name for x in ["backup", "backup", "restore"]):
        return "💾 BACKUP & RECOVERY"
    elif any(x in name for x in ["evolver", "evolve", "bridge", "stagnation"]):
        return "📡 EVENT BUS & EVOLVER"
    elif any(x in name for x in ["morning", "evening", "daily", "summary", "session"]):
        return "📝 REPORTING"
    elif any(x in name for x in ["kg", "knowledge", "graph"]):
        return "🗃️ KNOWLEDGE GRAPH"
    elif any(x in name for x in ["token", "budget", "cost"]):
        return "💰 TOKEN & BUDGET"
    elif any(x in name for x in ["security", "audit"]):
        return "🔒 SECURITY"
    else:
        return "🔧 TOOLS & UTILITIES"


def scan_scripts() -> Dict:
    """Scan SCRIPTS directories and build tracker."""
    scripts = []
    
    # Scan SCRIPTS/automation
    if SCRIPTS_AUTOMATION.exists():
        for f in SCRIPTS_AUTOMATION.glob("*.py"):
            scripts.append({
                "name": f.name,
                "path": str(f.relative_to(WORKSPACE)),
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "category": get_script_category(f.name),
                "priority": get_script_priority(f.name)
            })
    
    # Scan scripts/
    if SCRIPTS_DIR.exists():
        for f in SCRIPTS_DIR.glob("*.sh"):
            scripts.append({
                "name": f.name,
                "path": str(f.relative_to(WORKSPACE)),
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "category": get_script_category(f.name),
                "priority": get_script_priority(f.name)
            })
    
    return {
        "last_scan": datetime.now().isoformat(),
        "total": len(scripts),
        "scripts": sorted(scripts, key=lambda x: (x["priority"], x["name"]))
    }


def sync_script_catalog(tracker: Dict) -> str:
    """Generate updated SCRIPT_KATALOG.md from tracker."""
    
    # Group by priority
    by_priority = {1: [], 2: [], 3: [], 4: []}
    for s in tracker["scripts"]:
        by_priority[s["priority"]].append(s)
    
    lines = [
        "# Script Katalog — Sir HazeClaw",
        "",
        f"**Letzte Aktualisierung:** {datetime.now().strftime('%Y-%m-%d %H:%M')} (auto-generated)",
        f"**Total:** {tracker['total']} Scripts | **Scan:** {tracker['last_scan'][:16]}",
        "",
        "---",
        "",
    ]
    
    priority_labels = {
        1: "🎯 KERN-SYSTEME (Must Work 24/7)",
        2: "📈 DAILY HEALTH (Sollte täglich laufen)",
        3: "⚙️ OPERATIONAL (Wöchentlich oder bei Bedarf)",
        4: "🔧 TOOLS & UTILITIES (On-Demand)"
    }
    
    for p in [1, 2, 3, 4]:
        if by_priority[p]:
            lines.append(f"## {priority_labels[p]}")
            lines.append("")
            lines.append("| Script | Kategorie | Priority |")
            lines.append("|--------|-----------|----------|")
            for s in by_priority[p]:
                lines.append(f"| `{s['name']}` | {s['category']} | P{p} |")
            lines.append("")
    
    lines.extend([
        "---",
        "",
        f"*Auto-generated: {datetime.now().isoformat()}*",
        "*Nutze `python3 doc_maintenance.py --sync-scripts` zum Updaten*"
    ])
    
    return "\n".join(lines)


def audit_docs() -> Dict:
    """Check for outdated or orphaned documentation."""
    findings = {
        "timestamp": datetime.now().isoformat(),
        "outdated_docs": [],
        "orphaned_refs": [],
        "missing_docs": []
    }
    
    cutoff = datetime.now() - timedelta(days=30)
    
    # Check docs in notes/
    for doc in NOTES_DIR.rglob("*.md"):
        if doc.name.startswith("_"):
            continue
        
        mtime = datetime.fromtimestamp(doc.stat().st_mtime)
        if mtime < cutoff:
            findings["outdated_docs"].append({
                "path": str(doc.relative_to(WORKSPACE)),
                "last_modified": mtime.isoformat(),
                "days_old": (datetime.now() - mtime).days
            })
    
    # Check for orphaned script refs in docs
    if SCRIPT_TRACKER.exists():
        tracker = json.loads(SCRIPT_TRACKER.read_text())
        active_scripts = {s["name"] for s in tracker["scripts"]}
        
        for doc in NOTES_DIR.rglob("*.md"):
            content = doc.read_text()
            # Check for script references
            for match in re.findall(r'`?([a-z_]+\.(py|sh))`?', content):
                script_name = match[0] if isinstance(match, tuple) else match
                if script_name not in active_scripts:
                    findings["orphaned_refs"].append({
                        "doc": str(doc.relative_to(WORKSPACE)),
                        "script": script_name
                    })
    
    return findings


def regenerate_index() -> str:
    """Regenerate _index.md from current notes/ structure."""
    
    def get_category_docs(category: Path) -> List[Dict]:
        docs = []
        if not category.exists():
            return docs
        for f in sorted(category.glob("*.md")):
            if f.name.startswith("_"):
                continue
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            docs.append({
                "name": f.name,
                "modified": mtime.strftime("%Y-%m-%d")
            })
        return docs
    
    lines = [
        "# 📚 Sir HazeClaw — Notes Master Index",
        "",
        f"**Letzte Aktualisierung:** {datetime.now().strftime('%Y-%m-%d %H:%M')} (auto-generated)",
        f"**Total Docs:** {len(list(NOTES_DIR.rglob('*.md')))}",
        "",
        "---",
        "",
    ]
    
    categories = {
        "SYSTEM": "🏗️ System",
        "SCRIPTS": "📋 Scripts",
        "LEARNING": "🧠 Learning",
        "OPERATIONS": "⚙️ Operations",
        "ARCHIVE": "📁 Archive"
    }
    
    for cat_dir, cat_label in categories.items():
        docs = get_category_docs(NOTES_DIR / cat_dir)
        if docs:
            lines.append(f"## {cat_label} (`notes/{cat_dir}/`)")
            lines.append("")
            lines.append("| Doc | Modified |")
            lines.append("|-----|----------|")
            for d in docs:
                lines.append(f"| [{d['name']}](./{cat_dir}/{d['name']}) | {d['modified']} |")
            lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 🔄 Maintenance",
        "",
        "```bash",
        "# Sync script catalog",
        "python3 SCRIPTS/automation/doc_maintenance.py --sync-scripts",
        "",
        "# Audit docs for issues",
        "python3 SCRIPTS/automation/doc_maintenance.py --audit",
        "",
        "# Full regeneration",
        "python3 SCRIPTS/automation/doc_maintenance.py --full",
        "```",
        "",
        f"*Auto-generated: {datetime.now().isoformat()}*"
    ])
    
    return "\n".join(lines)


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--help"]
    
    if "--help" in args:
        print(__doc__)
        return 0
    
    full = "--full" in args
    sync = "--sync-scripts" in args or full
    audit = "--audit" in args or full
    regenerate = "--regenerate" in args or full
    
    print("🔧 DOC MAINTENANCE")
    print("=" * 50)
    
    if sync:
        print("\n📝 Syncing script catalog...")
        tracker = scan_scripts()
        SCRIPT_TRACKER.parent.mkdir(parents=True, exist_ok=True)
        SCRIPT_TRACKER.write_text(json.dumps(tracker, indent=2))
        
        catalog_path = NOTES_DIR / "SCRIPTS/SCRIPT_KATALOG.md"
        if catalog_path.exists():
            new_content = sync_script_catalog(tracker)
            catalog_path.write_text(new_content)
            print(f"  ✅ Updated {catalog_path.name} ({tracker['total']} scripts)")
    
    if audit:
        print("\n🔍 Auditing documentation...")
        findings = audit_docs()
        if findings["outdated_docs"]:
            print(f"  ⚠️  {len(findings['outdated_docs'])} outdated docs (>30 days):")
            for d in findings["outdated_docs"][:5]:
                print(f"      - {d['path']} ({d['days_old']} days old)")
        else:
            print("  ✅ No outdated docs")
        
        if findings["orphaned_refs"]:
            print(f"  ⚠️  {len(findings['orphaned_refs'])} orphaned script refs:")
            for r in findings["orphaned_refs"][:5]:
                print(f"      - {r['doc']}: `{r['script']}` not in active scripts")
        else:
            print("  ✅ No orphaned script references")
    
    if regenerate:
        print("\n📋 Regenerating _index.md...")
        new_index = regenerate_index()
        index_path = NOTES_DIR / "_index.md"
        index_path.write_text(new_index)
        print(f"  ✅ Regenerated {index_path.name}")
    
    print("\n" + "=" * 50)
    print("✅ Doc maintenance complete")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

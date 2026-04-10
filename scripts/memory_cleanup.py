#!/usr/bin/env python3
"""
Memory Cleanup System — IMPROVED
Tägliche Speicherpflege mit Safety Checks.

Features:
- Fleeting Notes archivieren (7+ Tage)
- Weekly consolidation
- KG Pruning (Orphan Detection)
- Log Rotation (30+ Tage)
- Dry-run mode
- Backup vor Löschen
- Detailliertes Reporting

Usage:
    python3 memory_cleanup.py
    python3 memory_cleanup.py --dry-run
    python3 memory_cleanup.py --report
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"
LOG_DIR = WORKSPACE.parent / "logs"
FLEETING_DIR = MEMORY_DIR / "notes/fleeting"
PERMANENT_DIR = MEMORY_DIR / "notes/permanent"
KG_FILE = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
BACKUP_DIR = WORKSPACE.parent / "backups"

# Config
MAX_FLEETING_AGE_DAYS = 7
MAX_LOG_AGE_DAYS = 30
MAX_WEEKLY_ARCHIVE_DAYS = 35
DRY_RUN = False

REPORT = []
deleted_files = []
archived_files = []

def log(msg, emoji="  "):
    print(f"{emoji} {msg}")
    REPORT.append(msg)

def get_file_age_days(path):
    """Gibt das Alter einer Datei in Tagen zurück."""
    try:
        mtime = os.path.getmtime(path)
        age = (datetime.now() - datetime.fromtimestamp(mtime)).days
        return age
    except:
        return 0

def get_file_age_hours(path):
    """Gibt das Alter einer Datei in Stunden zurück."""
    try:
        mtime = os.path.getmtime(path)
        age = (datetime.now().timestamp() - mtime) / 3600
        return age
    except:
        return 0

def create_backup():
    """Erstellt Backup vor dem Cleanup."""
    if DRY_RUN:
        log("🧪 [DRY-RUN] Würde Backup erstellen...", "  ")
        return True
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_name = f"memory_cleanup_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / backup_name
    
    try:
        # Create tar of memory directory
        import tarfile
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(MEMORY_DIR, arcname="memory")
        
        size_mb = os.path.getsize(backup_path) / (1024*1024)
        log(f"✅ Backup erstellt: {backup_name} ({size_mb:.1f}MB)", "💾")
        return True
    except Exception as e:
        log(f"⚠️ Backup Fehler: {e}", "⚠️")
        return False

def cleanup_fleeting_notes():
    """Archiviert oder löscht alte fleeting notes."""
    if not FLEETING_DIR.exists():
        log("Fleeting Notes: Ordner nicht vorhanden", "ℹ️")
        return
    
    notes = list(FLEETING_DIR.glob("*.md"))
    count_before = len(notes)
    
    for note in notes:
        age = get_file_age_days(note)
        if age > MAX_FLEETING_AGE_DAYS:
            if DRY_RUN:
                log(f"🧪 [DRY-RUN] Würde archivieren: {note.name} (Alter: {age} Tage)", "📦")
                continue
            
            archive_path = ARCHIVE_DIR / f"fleeting_{note.name}"
            try:
                shutil.move(str(note), str(archive_path))
                archived_files.append(str(note.name))
                log(f"📦 Fleeting archiviert: {note.name} ({age} Tage alt)", "📦")
            except Exception as e:
                log(f"⚠️ Fleeting Fehler: {e}", "⚠️")
    
    count_after = len(list(FLEETING_DIR.glob("*.md")))
    log(f"✅ Fleeting Cleanup: {count_before} → {count_after} Notes", "📝")

def consolidate_weekly_notes():
    """Konsolidiert tägliche Notes zu wöchentlichen Summaries."""
    if not PERMANENT_DIR.exists():
        log("Permanent Notes: Ordner nicht vorhanden", "ℹ️")
        return
    
    daily_notes = list(PERMANENT_DIR.glob("*daily-operations.md"))
    
    if len(daily_notes) < 3:
        log(f"ℹ️ Weniger als 3 daily Notes, behalte sie ({len(daily_notes)} gefunden)", "📝")
        return
    
    if DRY_RUN:
        log(f"🧪 [DRY-RUN] Würde {len(daily_notes)} Notes konsolidieren", "📦")
        return
    
    # Group by week
    by_week = {}
    for note in daily_notes:
        mtime = datetime.fromtimestamp(note.stat().st_mtime)
        week_key = mtime.strftime('%Y-W%W')
        if week_key not in by_week:
            by_week[week_key] = []
        by_week[week_key].append(note)
    
    for week_key, notes in by_week.items():
        if len(notes) < 3:
            continue
        
        # Create weekly summary
        week_start = notes[0].stat().st_mtime
        week_dt = datetime.fromtimestamp(week_start)
        
        weekly_summary = PERMANENT_DIR / f"{week_key}-weekly-summary.md"
        content = f"# Weekly Summary — {week_key}\n\n"
        content += f"*Konsolidiert: {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        
        for note in sorted(notes):
            content += f"## Aus: {note.name}\n\n"
            try:
                content += note.read_text()[:500] + "\n\n---\n\n"
            except:
                pass
        
        try:
            with open(weekly_summary, 'w') as f:
                f.write(content)
            log(f"📝 Weekly Summary erstellt: {week_key}-weekly-summary.md ({len(notes)} Tage)", "📦")
            
            # Delete daily notes
            for note in notes:
                try:
                    note.unlink()
                    deleted_files.append(str(note.name))
                    log(f"🗑️ Daily Note gelöscht: {note.name}", "🗑️")
                except:
                    pass
        except Exception as e:
            log(f"⚠️ Weekly Konsolidierung Fehler: {e}", "⚠️")

def prune_knowledge_graph():
    """Entfernt Entities aus dem Knowledge Graph die keine Referenzen haben."""
    if not KG_FILE.exists():
        log("KG: Datei nicht vorhanden", "ℹ️")
        return
    
    try:
        with open(KG_FILE, 'r') as f:
            kg_data = json.load(f)
    except Exception as e:
        log(f"⚠️ KG: Konnte nicht lesen - {e}", "⚠️")
        return
    
    entities_dict = kg_data.get('entities', {})
    if not entities_dict:
        log("KG: Keine Entities vorhanden", "ℹ️")
        return
    
    # Find orphaned entities (no facts or empty facts)
    orphaned = []
    valid_entities = {}
    for name, entity in entities_dict.items():
        if isinstance(entity, dict):
            facts = entity.get('facts', [])
            if not facts or len(facts) == 0:
                orphaned.append(name)
            else:
                valid_entities[name] = entity
        else:
            orphaned.append(name)
    
    log(f"🧠 KG Status: {len(valid_entities)} Entities, {len(orphaned)} ohne Fakten", "📊")
    
    if len(orphaned) > 10 and not DRY_RUN:
        # Only prune if lots of orphans
        kg_data['entities'] = valid_entities
        kg_data['last_updated'] = datetime.now().isoformat()
        
        # Backup KG before modifying
        kg_backup = KG_FILE.with_suffix('.json.backup')
        try:
            shutil.copy2(KG_FILE, kg_backup)
            log(f"💾 KG Backup erstellt: {kg_backup.name}", "💾")
        except:
            pass
        
        with open(KG_FILE, 'w') as f:
            json.dump(kg_data, f, indent=2)
        
        log(f"🧹 KG Pruning: {len(orphaned)} Orphaned Entities entfernt", "🧹")
    elif DRY_RUN and orphaned:
        log(f"🧪 [DRY-RUN] Würde {len(orphaned)} Orphaned Entities entfernen", "🧹")

def rotate_logs():
    """Löscht Log-Dateien älter als 30 Tage."""
    if not LOG_DIR.exists():
        log("Logs: Ordner nicht vorhanden", "ℹ️")
        return
    
    log_files = list(LOG_DIR.glob("*.log"))
    deleted_count = 0
    
    for log_file in log_files:
        age = get_file_age_days(log_file)
        if age > MAX_LOG_AGE_DAYS:
            if DRY_RUN:
                log(f"🧪 [DRY-RUN] Würde löschen: {log_file.name} ({age} Tage alt)", "🗑️")
                continue
            
            try:
                log_file.unlink()
                deleted_count += 1
                deleted_files.append(str(log_file.name))
                log(f"🗑️ Log gelöscht: {log_file.name} ({age} Tage alt)", "🗑️")
            except Exception as e:
                log(f"⚠️ Log Fehler: {e}", "⚠️")
    
    if deleted_count > 0:
        log(f"✅ Log Rotation: {deleted_count} alte Logs gelöscht", "🧹")
    else:
        log(f"ℹ️ Keine alten Logs zum Löschen", "ℹ️")

def cleanup_dreampedia():
    """Archiviert alte Dream Reflections."""
    dreams_file = MEMORY_DIR / ".dreams/reflection_history.md"
    if not dreams_file.exists():
        return
    
    age = get_file_age_days(dreams_file)
    if age > MAX_WEEKLY_ARCHIVE_DAYS:
        if DRY_RUN:
            log(f"🧪 [DRY-RUN] Würde archivieren: Dream Reflections ({age} Tage alt)", "📦")
            return
        
        archive_path = ARCHIVE_DIR / f"dreampedia_reflection_{datetime.now().strftime('%Y-%m-%d')}.md"
        try:
            shutil.copy2(str(dreams_file), str(archive_path))
            log(f"📦 Dream Reflections archiviert: {age} Tage alt", "📦")
            
            # Reset file
            with open(dreams_file, 'w') as f:
                f.write(f"# Dream Reflection History\n*Gestartet: {datetime.now().strftime('%Y-%m-%d')}*\n\n")
            log(f"🆕 Dream Reflection History zurückgesetzt", "🆕")
        except Exception as e:
            log(f"⚠️ Dream Archivierung Fehler: {e}", "⚠️")

def show_report():
    """Zeigt detaillierten Report."""
    print("")
    print("=" * 50)
    print("📊 MEMORY CLEANUP REPORT")
    print("=" * 50)
    print(f"  Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Modus: {'DRY-RUN' if DRY_RUN else 'LIVE'}")
    print("")
    
    if deleted_files:
        print(f"  🗑️  Gelöschte Files ({len(deleted_files)}):")
        for f in deleted_files[:10]:
            print(f"      - {f}")
        if len(deleted_files) > 10:
            print(f"      ... und {len(deleted_files) - 10} weitere")
    else:
        print("  🗑️  Keine Files gelöscht")
    
    print("")
    
    if archived_files:
        print(f"  📦 Archivierte Files ({len(archived_files)}):")
        for f in archived_files[:5]:
            print(f"      - {f}")
        if len(archived_files) > 5:
            print(f"      ... und {len(archived_files) - 5} weitere")
    else:
        print("  📦 Keine Files archiviert")
    
    print("")
    
    # KG Stats
    if KG_FILE.exists():
        try:
            with open(KG_FILE) as f:
                kg = json.load(f)
            entities = len(kg.get('entities', {}))
            relations = len(kg.get('relations', []))
            print(f"  🧠 KG Stats: {entities} entities, {relations} relations")
        except:
            pass
    
    print("")
    print("=" * 50)

def save_json_report():
    """Speichert Report als JSON."""
    report_file = WORKSPACE / "task_reports/memory_cleanup_daily.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        "agent": "memory_cleanup",
        "timestamp": datetime.now().isoformat(),
        "dry_run": DRY_RUN,
        "deleted_files": deleted_files,
        "archived_files": archived_files,
        "status": "done"
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    log(f"📄 Report gespeichert: {report_file.name}", "📄")

def main():
    global DRY_RUN
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Cleanup System - Improved')
    parser.add_argument('--dry-run', action='store_true', help='Nur anzeigen was passieren würde')
    parser.add_argument('--report', action='store_true', help='Zeige Report')
    args = parser.parse_args()
    
    DRY_RUN = args.dry_run
    
    print("=" * 50)
    print("🧹 MEMORY CLEANUP SYSTEM")
    print(f"Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    if DRY_RUN:
        print("⚠️  DRY-RUN MODE - Keine Änderungen werden vorgenommen")
    print("=" * 50)
    
    # Create backup first (unless dry-run)
    if not DRY_RUN:
        create_backup()
    
    print("")
    
    # Run cleanup tasks
    cleanup_fleeting_notes()
    consolidate_weekly_notes()
    prune_knowledge_graph()
    rotate_logs()
    cleanup_dreampedia()
    
    print("")
    
    # Show report
    show_report()
    
    # Save JSON report
    if not DRY_RUN:
        save_json_report()
    
    total = len(deleted_files) + len(archived_files)
    if total > 0:
        print(f"✅ Memory Cleanup abgeschlossen! ({total} Aktionen)")
    else:
        print("ℹ️  Keine Aufräumarbeiten nötig.")
    
    return 0 if total >= 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
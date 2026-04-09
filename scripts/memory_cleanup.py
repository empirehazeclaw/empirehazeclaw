#!/usr/bin/env python3
"""
Memory Cleanup System — Tägliche Speicherpflege
Läuft jeden Tag um 02:00 UTC (vor sqlite_vacuum um 03:00)

Was es macht:
1. Fleeting Notes: Archiviert Notes älter als 7 Tage
2. Weekly Consolidation: Mehrere Daily Notes → Weekly Summary
3. KG Pruning: Entfernt Entities ohne Referenzen
4. Log Rotation: Löscht Logs älter als 30 Tage
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
KG_FILE = MEMORY_DIR / "knowledge_graph.json"

# Config
MAX_FLEETING_AGE_DAYS = 7
MAX_LOG_AGE_DAYS = 30
MAX_WEEKLY_ARCHIVE_DAYS = 35  # After 5 weeks, archive weekly summaries

REPORT = []
deleted_files = []
archived_files = []

def log(msg):
    print(f"  {msg}")
    REPORT.append(msg)

def get_file_age_days(path):
    """Gibt das Alter einer Datei in Tagen zurück."""
    try:
        mtime = os.path.getmtime(path)
        age = (datetime.now() - datetime.fromtimestamp(mtime)).days
        return age
    except:
        return 0

def cleanup_fleeting_notes():
    """Archiviert oder löscht alte fleeting notes."""
    if not FLEETING_DIR.exists():
        return
    
    count_before = len(list(FLEETING_DIR.glob("*.md")))
    for note in FLEETING_DIR.glob("*.md"):
        age = get_file_age_days(note)
        if age > MAX_FLEETING_AGE_DAYS:
            # Move to archive
            archive_path = ARCHIVE_DIR / f"fleeting_{note.name}"
            try:
                shutil.move(str(note), str(archive_path))
                archived_files.append(str(note.name))
                log(f"📦 Fleeting archiviert: {note.name} (Alter: {age} Tage)")
            except Exception as e:
                log(f"⚠️ Fleeting Fehler: {e}")
    
    count_after = len(list(FLEETING_DIR.glob("*.md")))
    log(f"✅ Fleeting Cleanup: {count_before} → {count_after} Notes")

def consolidate_weekly_notes():
    """Konsolidiert tägliche Notes zu wöchentlichen Summaries."""
    if not PERMANENT_DIR.exists():
        return
    
    # Find daily notes from same week
    daily_notes = []
    for note in PERMANENT_DIR.glob("*daily-operations.md"):
        daily_notes.append(note)
    
    if len(daily_notes) < 3:
        # Keep daily notes if less than 3
        return
    
    # Group by week (extract week number from filename)
    weeks = {}
    for note in daily_notes:
        # Extract date from filename like 2026-04-08-daily-operations.md
        date_str = note.stem.split('-')[0:3]
        if len(date_str) == 3:
            try:
                date = datetime.strptime('-'.join(date_str), "%Y-%m-%d")
                week = date.isocalendar()[1]
                year = date.isocalendar()[0]
                key = f"{year}-W{week:02d}"
                if key not in weeks:
                    weeks[key] = []
                weeks[key].append(note)
            except:
                pass
    
    # Create weekly summaries
    for week_key, notes in weeks.items():
        if len(notes) < 3:
            continue
        
        # Check if weekly summary already exists
        weekly_summary = PERMANENT_DIR / f"{week_key}-weekly-summary.md"
        if weekly_summary.exists():
            continue
        
        # Build weekly summary
        content = f"# Weekly Summary — {week_key}\n\n"
        content += f"*Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        content += "## Tagebuch dieser Woche\n\n"
        
        for note in sorted(notes):
            with open(note, 'r') as f:
                content += f"### {note.stem}\n\n"
                content += f.read()
                content += "\n\n---\n\n"
        
        content += "---\n*Konsolidiert aus täglichen Notes*\n"
        
        with open(weekly_summary, 'w') as f:
            f.write(content)
        
        log(f"📝 Weekly Summary erstellt: {week_key}-weekly-summary.md ({len(notes)} Tage)")
        
        # Delete daily notes that are now consolidated
        for note in notes:
            try:
                note.unlink()
                deleted_files.append(str(note.name))
                log(f"🗑️ Daily Note gelöscht: {note.name}")
            except:
                pass

def prune_knowledge_graph():
    """Entfernt Entities aus dem Knowledge Graph die keine Referenzen haben."""
    if not KG_FILE.exists():
        return
    
    try:
        with open(KG_FILE, 'r') as f:
            kg_data = json.load(f)
    except:
        log("⚠️ KG: Konnte knowledge_graph.json nicht lesen")
        return
    
    entities_dict = kg_data.get('entities', {})
    if not entities_dict:
        return
    
    # Find entities with no facts (orphan entities)
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
            # Skip non-dict entities (malformed)
            orphaned.append(name)
    
    original_count = len(entities_dict)
    
    if len(orphaned) > 10:
        # Only prune if we have lots of orphans (avoid over-pruning)
        kg_data['entities'] = valid_entities
        
        with open(KG_FILE, 'w') as f:
            json.dump(kg_data, f, indent=2)
        
        log(f"🧠 KG Pruning: {original_count} → {len(valid_entities)} Entities ({len(orphaned)} Orphaned entfernt)")
    else:
        log(f"🧠 KG Status: {len(valid_entities)} Entities, {len(orphaned)} ohne Fakten (OK)")

def rotate_logs():
    """Löscht Log-Dateien älter als 30 Tage."""
    if not LOG_DIR.exists():
        return
    
    log_files = list(LOG_DIR.glob("*.log"))
    deleted_count = 0
    
    for log_file in log_files:
        age = get_file_age_days(log_file)
        if age > MAX_LOG_AGE_DAYS:
            try:
                log_file.unlink()
                deleted_count += 1
                deleted_files.append(str(log_file.name))
                log(f"🗑️ Log gelöscht: {log_file.name} (Alter: {age} Tage)")
            except Exception as e:
                log(f"⚠️ Log Fehler: {e}")
    
    if deleted_count > 0:
        log(f"✅ Log Rotation: {deleted_count} alte Logs gelöscht")
    else:
        log(f"✅ Log Rotation: Keine alten Logs gefunden")

def cleanup_dreampedia():
    """Archiviert alte Dream Reflections."""
    dreams_file = MEMORY_DIR / ".dreams/reflection_history.md"
    if not dreams_file.exists():
        return
    
    age = get_file_age_days(dreams_file)
    if age > MAX_WEEKLY_ARCHIVE_DAYS:
        archive_path = ARCHIVE_DIR / f"dreampedia_reflection_{datetime.now().strftime('%Y-%m-%d')}.md"
        try:
            shutil.copy2(str(dreams_file), str(archive_path))
            log(f"📦 Dream Reflections archiviert: {age} Tage alt")
            
            # Start fresh file
            with open(dreams_file, 'w') as f:
                f.write(f"# Dream Reflection History\n*Gestartet: {datetime.now().strftime('%Y-%m-%d')}*\n\n")
            log(f"🆕 Dream Reflection History zurückgesetzt")
        except Exception as e:
            log(f"⚠️ Dream Archivierung Fehler: {e}")

def main():
    print("=" * 50)
    print("🧹 MEMORY CLEANUP SYSTEM")
    print(f"Gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    
    log("")
    cleanup_fleeting_notes()
    consolidate_weekly_notes()
    prune_knowledge_graph()
    rotate_logs()
    cleanup_dreampedia()
    
    print("")
    print("=" * 50)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 50)
    print(f"  🗑️  Gelöschte Files: {len(deleted_files)}")
    for f in deleted_files[:10]:
        print(f"      - {f}")
    if len(deleted_files) > 10:
        print(f"      ... und {len(deleted_files) - 10} weitere")
    
    print(f"  📦 Archivierte Files: {len(archived_files)}")
    for f in archived_files[:5]:
        print(f"      - {f}")
    
    print("")
    print("✅ Memory Cleanup abgeschlossen!")
    
    # Write report
    report_file = WORKSPACE / "task_reports/memory_cleanup_daily.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "agent": "memory_cleanup",
        "timestamp": datetime.now().isoformat(),
        "deleted_files": deleted_files,
        "archived_files": archived_files,
        "status": "done"
    }
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return len(deleted_files) + len(archived_files)

if __name__ == "__main__":
    main()

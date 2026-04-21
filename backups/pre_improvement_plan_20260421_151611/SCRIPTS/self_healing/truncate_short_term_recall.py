#!/usr/bin/env python3
"""
Truncate Short-Term Recall After Dreaming Promotion
Räumt .dreams/short-term-recall.json nach der Memory Dreaming Promotion auf.

Usage:
    python3 SCRIPTS/self_healing/truncate_short_term_recall.py
    python3 SCRIPTS/self_healing/truncate_short_term_recall.py --dry-run
    python3 SCRIPTS/self_healing/truncate_short_term_recall.py --aggressive
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
RECALL_FILE = WORKSPACE / "ceo" / "memory" / ".dreams" / "short-term-recall.json"
BACKUP_DIR = WORKSPACE / "ceo" / "memory" / ".dreams" / "backups"
LOG_FILE = WORKSPACE / "logs" / "short_term_recall_cleanup.log"

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_retention_hours():
    """Wie viele Stunden sollen wir behalten?"""
    if "--aggressive" in sys.argv:
        return 24  # Nur die letzten 24h
    return 72  # Standard: 72h

def load_recall():
    """Lädt das Recall File."""
    if not RECALL_FILE.exists():
        log("RECALL_FILE existiert nicht, nichts zu tun")
        return None
    
    try:
        with open(RECALL_FILE) as f:
            return json.load(f)
    except Exception as e:
        log(f"Fehler beim Laden: {e}", "ERROR")
        return None

MIN_SCORE_THRESHOLD = 0.4  # Minimum score to keep an entry (lowered from 0.7 - scores 0.58-0.62 are valid)

def get_entries_to_keep(recall_data, max_age_hours=72):
    """Filtert Entries die nach Retention-Periode + Score-Schwelle noch relevant sind."""
    if not recall_data or "entries" not in recall_data:
        return {}
    
    now = datetime.now()
    cutoff_seconds = max_age_hours * 3600
    entries = recall_data.get("entries", {})
    
    kept = {}
    dropped_by_age = 0
    dropped_by_score = 0
    
    for key, value in entries.items():
        # Check age
        last_recalled = value.get("lastRecalledAt") or value.get("firstRecalledAt")
        age_valid = True
        
        if last_recalled:
            try:
                if isinstance(last_recalled, str):
                    last_dt = datetime.fromisoformat(last_recalled.replace("Z", "+00:00"))
                    age_seconds = (now - last_dt.replace(tzinfo=None)).total_seconds()
                    age_valid = age_seconds < cutoff_seconds
                else:
                    age_valid = False
            except:
                age_valid = False
        
        # Check score
        total_score = value.get("totalScore", 0)
        score_valid = total_score >= MIN_SCORE_THRESHOLD
        
        if age_valid and score_valid:
            kept[key] = value
        elif not age_valid:
            dropped_by_age += 1
        else:
            dropped_by_score += 1
    
    log(f"  → {dropped_by_age} durch Alter entfernt, {dropped_by_score} durch Score (<{MIN_SCORE_THRESHOLD}) entfernt")
    return kept

def save_truncated(recall_data, kept_entries, dry_run=False):
    """Speichert die gekürzte Version."""
    if dry_run:
        log("DRY RUN — Würde speichern:")
        return
    
    # Backup erstellen
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUP_DIR / f"short-term-recall_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.bak"
    
    try:
        with open(RECALL_FILE) as f:
            original_content = f.read()
        with open(backup_file, "w") as f:
            f.write(original_content)
        log(f"Backup erstellt: {backup_file.name}")
    except Exception as e:
        log(f"Backup fehlgeschlagen: {e}", "WARNING")
    
    # Truncated Version schreiben
    truncated = {
        "version": recall_data.get("version", 1),
        "updatedAt": datetime.now().isoformat() + "Z",
        "entries": kept_entries
    }
    
    try:
        with open(RECALL_FILE, "w") as f:
            json.dump(truncated, f)
        new_size = RECALL_FILE.stat().st_size
        log(f"✅ Truncation complete: {len(kept_entries)} Entries behalten, {new_size} bytes")
    except Exception as e:
        log(f"Speichern fehlgeschlagen: {e}", "ERROR")

def rotate_backups():
    """Entfernt alte Backups (behalte nur die letzten 7)."""
    if not BACKUP_DIR.exists():
        return
    
    backups = sorted(BACKUP_DIR.glob("short-term-recall_*.json.bak"), key=lambda p: p.stat().st_mtime)
    
    if len(backups) > 7:
        for old in backups[:-7]:
            try:
                old.unlink()
                log(f"Altes Backup gelöscht: {old.name}")
            except Exception as e:
                log(f"Löschen fehlgeschlagen: {e}", "WARNING")

def main():
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        log("=== DRY RUN MODE ===")
    
    log("=== Short-Term Recall Cleanup ===")
    
    # 1. Load
    recall_data = load_recall()
    if recall_data is None:
        return  # Nichts zu tun
    
    original_count = len(recall_data.get("entries", {}))
    log(f"Original Entries: {original_count}")
    
    # 2. Filter
    max_age = get_retention_hours()
    kept_entries = get_entries_to_keep(recall_data, max_age)
    kept_count = len(kept_entries)
    dropped_count = original_count - kept_count
    
    log(f"Behalten: {kept_count} Entries ({dropped_count} werden entfernt)")
    
    if dropped_count == 0:
        log("Keine Entries zum Entfernen — nichts zu tun")
        return
    
    # 3. Save
    save_truncated(recall_data, kept_entries, dry_run=dry_run)
    
    # 4. Rotate Backups
    rotate_backups()
    
    log("=== Cleanup Complete ===")

if __name__ == "__main__":
    main()

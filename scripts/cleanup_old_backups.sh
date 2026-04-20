#!/bin/bash
#===========================================
# Cleanup Old Backups — Sir HazeClaw
#===========================================
# Removes old backups keeping only recent ones
# Run: bash cleanup_old_backups.sh [--dry-run]
#===========================================

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - no changes will be made"
fi

LOG_FILE="/home/clawbot/.openclaw/logs/cleanup_backups.log"
BACKUP_HOME="/home/clawbot/backups"
BACKUP_WS="/home/clawbot/.openclaw/workspace/backups"

log() { echo "[$(date -Iseconds)] $1" | tee -a "$LOG_FILE"; }

log "========================================"
log "BACKUP CLEANUP START"
log "========================================"

TOTAL_FREED=0

#---------------------------------------
# HOME backups - keep 3 most recent
#---------------------------------------
log "--- HOME/backups ---"
cd "$BACKUP_HOME" || exit 1

# Find directories older than 7 days
find . -maxdepth 1 -type d ! -name "." ! -name ".." -mtime +7 | while read dir; do
    SIZE=$(du -sh "$dir" 2>/dev/null | cut -f1)
    if [ "$DRY_RUN" = "true" ]; then
        log "  [DRY] Would remove: $dir ($SIZE)"
    else
        rm -rf "$dir"
        log "  ✓ Removed: $dir ($SIZE)"
    fi
    TOTAL_FREED=$((TOTAL_FREED + 1))
done

# Find .tar.gz older than 7 days
find . -maxdepth 1 -name "*.tar.gz" -mtime +7 | while read file; do
    SIZE=$(du -sh "$file" 2>/dev/null | cut -f1)
    if [ "$DRY_RUN" = "true" ]; then
        log "  [DRY] Would remove: $file ($SIZE)"
    else
        rm -f "$file"
        log "  ✓ Removed: $file ($SIZE)"
    fi
done

#---------------------------------------
# WORKSPACE backups - keep post_integration
#---------------------------------------
log "--- WORKSPACE/backups ---"
cd "$BACKUP_WS" || exit 1

# Keep: post_integration, complete-2026 (from home)
# Remove: stale kg backups, old openclaw updates, empty dirs

# Remove stale KG backup
if [ -f "core_ultralight_kg_stale_20260416.json" ]; then
    SIZE=$(du -sh "core_ultralight_kg_stale_20260416.json" | cut -f1)
    if [ "$DRY_RUN" = "true" ]; then
        log "  [DRY] Would remove: core_ultralight_kg_stale_20260416.json ($SIZE)"
    else
        rm -f "core_ultralight_kg_stale_20260416.json"
        log "  ✓ Removed: core_ultralight_kg_stale (stale)"
    fi
fi

# Remove old openclaw update tars (Apr 15)
find . -name "openclaw_update_backup_20260415*.tar.gz" -mtime +5 | while read file; do
    SIZE=$(du -sh "$file" | cut -f1)
    if [ "$DRY_RUN" = "true" ]; then
        log "  [DRY] Would remove: $file ($SIZE)"
    else
        rm -f "$file"
        log "  ✓ Removed: $file"
    fi
done

#---------------------------------------
# Empty autonomy dir
#---------------------------------------
if [ -d "autonomy" ] && [ -z "$(ls -A autonomy)" ]; then
    if [ "$DRY_RUN" = "true" ]; then
        log "  [DRY] Would remove: autonomy/ (empty)"
    else
        rmdir autonomy
        log "  ✓ Removed: autonomy/ (empty)"
    fi
fi

#---------------------------------------
# Cleanup empty workspace dirs (not used)
#---------------------------------------
log "--- Workspace empty dirs check ---"
for d in apps dashboard pipeline processes prompts queue reference revenue workflows tech templates; do
    WS_DIR="/home/clawbot/.openclaw/workspace/$d"
    if [ -d "$WS_DIR" ] && [ -z "$(ls -A $WS_DIR)" ]; then
        if [ "$DRY_RUN" = "true" ]; then
            log "  [DRY] Would remove: $d/ (empty)"
        else
            rmdir "$WS_DIR" 2>/dev/null && log "  ✓ Removed: $d/ (empty)"
        fi
    fi
done

#---------------------------------------
# Summary
#---------------------------------------
log "========================================"
if [ "$DRY_RUN" = "false" ]; then
    echo "" >> "$LOG_FILE"
    echo "Current backup sizes:" >> "$LOG_FILE"
    du -sh "$BACKUP_HOME" "$BACKUP_WS" >> "$LOG_FILE"
fi
log "BACKUP CLEANUP END"
log "========================================"
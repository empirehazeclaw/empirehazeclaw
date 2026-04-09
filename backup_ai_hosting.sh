#!/bin/bash
# Managed AI Hosting Backup Script
# Runs at 04:00 daily

LOG="/home/clawbot/.openclaw/workspace/logs/ai_backup.log"
BACKUP_DIR="/home/clawbot/approval-dashboard/backup"

echo "[$(date)] AI Hosting Backup started" >> $LOG

# Source .env if exists
if [ -f "$BACKUP_DIR/.env" ]; then
    set -a
    source "$BACKUP_DIR/.env"
    set +a
fi

# Run backup if script exists
if [ -f "$BACKUP_DIR/backup.sh" ]; then
    cd "$BACKUP_DIR"
    ./backup.sh backup >> $LOG 2>&1
    echo "[$(date)] AI Hosting Backup completed" >> $LOG
else
    echo "[$(date)] Backup script not found: $BACKUP_DIR/backup.sh" >> $LOG
fi

#!/bin/bash
# compress_old_sessions.sh - Monthly session compression
# Archives sessions older than 30 days

SESSIONS_DIR="/home/clawbot/.openclaw/agents/ceo/sessions"
ARCHIVE_DIR="/home/clawbot/backups/sessions"
DAYS=30

mkdir -p "$ARCHIVE_DIR"

# Find and compress old sessions
find "$SESSIONS_DIR" -name "*.jsonl" -mtime +$DAYS -print -o -name "*.checkpoint*" -mtime +$DAYS -print | while read f; do
    tar -czf "$ARCHIVE_DIR/sessions_$(date +%Y%m).tar.gz" "$f" 2>/dev/null && rm -f "$f"
done

echo "Session compression done. Archived $(date +%Y%m)"

#!/bin/bash
# Cleanup Script - Weekly Full Cleanup
# Führt alle notwendigen Cleanup-Aufgaben durch

DATE=$(date +%Y%m%d)
LOGFILE="/home/clawbot/.openclaw/logs/cleanup_$DATE.log"

echo "=== Cleanup gestartet: $(date) ===" >> $LOGFILE

# 1. Temp Files
echo "1. Temp Files Cleanup..." >> $LOGFILE
rm -rf /tmp/openclaw/* 2>/dev/null
echo "   Temp gelöscht" >> $LOGFILE

# 2. Alte Sessions (30 Tage)
echo "2. Alte Sessions Cleanup..." >> $LOGFILE
find ~/.openclaw/agents/main/sessions -name "*.jsonl" -mtime +30 -delete 2>/dev/null
echo "   Sessions >30 Tage gelöscht" >> $LOGFILE

# 3. Cron Logs (7 Tage)
echo "3. Cron Logs Cleanup..." >> $LOGFILE
find ~/.openclaw/logs -name "*.log" -mtime +7 -delete 2>/dev/null
echo "   Logs >7 Tage gelöscht" >> $LOGFILE

# 4. Backups (nur 2 behalten)
echo "4. Backups Cleanup..." >> $LOGFILE
cd ~/.openclaw/backups/
ls -t openclaw_backup_*.tar.gz 2>/dev/null | tail -n +3 | xargs rm -f 2>/dev/null
ls -t backup_*.tar.gz 2>/dev/null | tail -n +3 | xargs rm -f 2>/dev/null
echo "   Backups bereinigt" >> $LOGFILE

# 5. Alte Memory-Dateien archivieren (90 Tage)
echo "5. Memory Archivierung..." >> $LOGFILE
find ~/.openclaw/memory -name "*.md" -mtime +90 -exec gzip {} \; 2>/dev/null
echo "   Memory >90 Tage komprimiert" >> $LOGFILE

echo "=== Cleanup beendet: $(date) ===" >> $LOGFILE
echo "Fertig!" >> $LOGFILE

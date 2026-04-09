#!/bin/bash

# Memory Auto-Sync Cron Setup
# Fügt einen täglichen Cron Job hinzu, der um 23:00 läuft

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="$(dirname "$SCRIPT_DIR")"
NODE_PATH=$(which node)

# Cron Job Definition
CRON_JOB="0 23 * * * cd $MEMORY_DIR && $NODE_PATH scripts/autosync.js --sync >> /var/log/autosync.log 2>&1"

# Check if cron is installed
if ! command -v crontab &> /dev/null; then
    echo "❌ Cron nicht installiert. Bitte installieren mit:"
    echo "   apt-get install cron (Debian/Ubuntu)"
    echo "   yum install crontabs (CentOS)"
    exit 1
fi

# Check if job already exists
EXISTING=$(crontab -l 2>/dev/null | grep "autosync.js --sync")

if [ -n "$EXISTING" ]; then
    echo "⚠️  Cron Job existiert bereits:"
    echo "   $EXISTING"
    echo ""
    echo "Zum Entfernen: crontab -l | grep -v 'autosync.js' | crontab -"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron Job hinzugefügt:"
    echo "   $CRON_JOB"
fi

# Create log file
mkdir -p /var/log
touch /var/log/autosync.log

echo ""
echo "📋 Aktuelle Cron Jobs:"
crontab -l 2>/dev/null | grep -E "(autosync|memory)" || echo "   Keine Memory-Cron Jobs"

echo ""
echo "🔧 Commands:"
echo "   Cron starten:     systemctl start cron"
echo "   Cron stoppen:    systemctl stop cron"
echo "   Cron Status:     systemctl status cron"
echo "   Logs ansehen:    tail -f /var/log/autosync.log"

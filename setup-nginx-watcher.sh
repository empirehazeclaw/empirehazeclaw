#!/bin/bash
#
# File Watcher Setup für /var/www → nginx reload
# 
# Usage:
#   ./setup-nginx-watcher.sh start   - Starte File Watcher im Hintergrund
#   ./setup-nginx-watcher.sh stop    - Stoppe File Watcher
#   ./setup-nginx-watcher.sh status  - Zeige Status
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/filewatcher-nginx.log"
PID_FILE="/tmp/filewatcher-nginx.pid"

# Konfiguration
WATCH_DIR="/var/www"
COMMAND="nginx -s reload"
EXTENSIONS="html,css,js,php"

start_watcher() {
    echo "📁 Starte File Watcher für $WATCH_DIR..."
    echo "   Command: $COMMAND"
    echo "   Extensions: $EXTENSIONS"
    
    # Prüfe ob bereits läuft
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo "⚠️  File Watcher läuft bereits (PID: $OLD_PID)"
            exit 1
        fi
    fi
    
    # Starte im Hintergrund
    node "$SCRIPT_DIR/filewatcher.js" \
        --dir "$WATCH_DIR" \
        --command "$COMMAND" \
        --extensions "$EXTENSIONS" \
        --verbose \
        >> "$LOG_FILE" 2>&1 &
    
    PID=$!
    echo $PID > "$PID_FILE"
    echo "✅ File Watcher gestartet (PID: $PID)"
    echo "   Log: $LOG_FILE"
}

stop_watcher() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "🛑 Stoppe File Watcher (PID: $PID)..."
            kill "$PID"
            rm -f "$PID_FILE"
            echo "✅ File Watcher gestoppt"
        else
            echo "⚠️  Prozess nicht gefunden, lösche PID-Datei"
            rm -f "$PID_FILE"
        fi
    else
        echo "❌ Kein File Watcher gestartet (keine PID-Datei)"
    fi
}

status_watcher() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ File Watcher läuft (PID: $PID)"
        else
            echo "❌ PID-Datei existiert aber Prozess läuft nicht"
        fi
    else
        echo "❌ File Watcher läuft nicht"
    fi
    
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "📝 Letzte Log-Einträge:"
        tail -10 "$LOG_FILE"
    fi
}

case "$1" in
    start)
        start_watcher
        ;;
    stop)
        stop_watcher
        ;;
    status)
        status_watcher
        ;;
    restart)
        stop_watcher
        sleep 1
        start_watcher
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac

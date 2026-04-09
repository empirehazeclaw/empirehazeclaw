#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 📊 Uptime Monitor - EmpireHazeClaw
# ═══════════════════════════════════════════════════════════════════
# Prüft alle 5 Minuten ob Services laufen
# Bei Ausfall: Email-Benachrichtigung
# ═══════════════════════════════════════════════════════════════════

GOG="/home/linuxbrew/.linuxbrew/bin/gog"
TOKEN=$(grep access_token ~/.config/gogcli/token.env | cut -d= -f2)
ALERT_EMAIL="empirehazeclaw@gmail.com"

send_alert() {
    local service=$1
    local error=$2
    local time=$(date '+%Y-%m-%d %H:%M:%S')
    
    export GOG_ACCESS_TOKEN="$TOKEN"
    $GOG send --to "$ALERT_EMAIL" \
        --subject "🚨 Service Down: $service" \
        --body "Service $service ist ausgefallen!

Zeit: $time
Fehler: $error

Bitte Server prüfen: srv1432586

- OpenClaw Health Check"
}

check_service() {
    local name=$1
    local url=$2
    
    if ! curl -sf --max-time 10 "$url" > /dev/null 2>&1; then
        send_alert "$name" "HTTP Request failed"
        return 1
    fi
    return 0
}

echo "[$(date)] Uptime Check gestartet..."

# Services prüfen
FAILED=0

check_service "Mission Control" "https://187.124.11.27:8889/" || ((FAILED++))
check_service "empirehazeclaw.com" "https://empirehazeclaw.com/" || ((FAILED++))
check_service "empirehazeclaw.de" "https://empirehazeclaw.de/" || ((FAILED++))
check_service "empirehazeclaw.store" "https://empirehazeclaw.store/" || ((FAILED++))
check_service "empirehazeclaw.info" "https://empirehazeclaw.info/" || ((FAILED++))

if [[ $FAILED -eq 0 ]]; then
    echo "[$(date)] ✅ Alle Services OK"
else
    echo "[$(date)] ❌ $FAILED Service(s) ausgefallen"
fi

exit $FAILED

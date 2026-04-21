#!/bin/bash
# system_health_check.sh - Daily health check
# Runs via cron daily @ 08:00

LOG="/home/clawbot/.openclaw/workspace/ceo/logs/health_check.log"
DATE=$(date "+%Y-%m-%d %H:%M UTC")

echo "[$DATE] Health Check Start" >> $LOG

# 1. Gateway
if curl -s http://127.0.0.1:18789/ > /dev/null 2>&1; then
    echo "[OK] Gateway" >> $LOG
else
    echo "[ERROR] Gateway DOWN" >> $LOG
fi

# 2. KG Health
KG_SIZE=$(stat -c%s /home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json 2>/dev/null || echo 0)
if [ "$KG_SIZE" -gt 100000 ]; then
    echo "[OK] KG size: $KG_SIZE bytes" >> $LOG
else
    echo "[WARN] KG suspiciously small: $KG_SIZE" >> $LOG
fi

# 3. Disk Space
DISK_USED=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USED" -gt 90 ]; then
    echo "[ERROR] Disk at ${DISK_USED}%">> $LOG
elif [ "$DISK_USED" -gt 80 ]; then
    echo "[WARN] Disk at ${DISK_USED}%">> $LOG
else
    echo "[OK] Disk at ${DISK_USED}%" >> $LOG
fi

# 4. RAM
RAM_AVAILABLE=$(free -m | grep Mem | awk '{print $7}')
if [ "$RAM_AVAILABLE" -lt 500 ]; then
    echo "[WARN] RAM low: ${RAM_AVAILABLE}MB available" >> $LOG
else
    echo "[OK] RAM: ${RAM_AVAILABLE}MB available" >> $LOG
fi

# 5. Cron Status (count errors)
CRON_ERRORS=$(openclaw cron list 2>/dev/null | grep -c "error" || echo 0)
if [ "$CRON_ERRORS" -gt 0 ]; then
    echo "[WARN] $CRON_ERRORS cron errors" >> $LOG
else
    echo "[OK] All crons OK" >> $LOG
fi

echo "[$DATE] Health Check End" >> $LOG
echo "---"

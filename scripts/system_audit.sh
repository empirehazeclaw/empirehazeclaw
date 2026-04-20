#!/bin/bash
#===========================================
# System Audit — Sir HazeClaw
#===========================================
# Monitors: CPU, RAM, Disk, Services, Crons, KG
# Run: bash system_audit.sh
# Schedule: Daily via cron
#===========================================

LOG_FILE="/home/clawbot/.openclaw/logs/system_audit.log"
WORKSPACE="/home/clawbot/.openclaw/workspace"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "[$(date -Iseconds)] $1" | tee -a "$LOG_FILE"; }

log "========================================"
log "SIR HAZECLAW SYSTEM AUDIT"
log "========================================"

ISSUES=0

#---------------------------------------
# 1. Gateway Process
#---------------------------------------
log "--- Gateway ---"
GATEWAY_PID=$(pgrep -f "openclaw-gateway" | head -1)
if [ -n "$GATEWAY_PID" ]; then
    GATEWAY_MEM=$(ps -o rss= -p $GATEWAY_PID 2>/dev/null | tr -d ' ')
    GATEWAY_CPU=$(ps -o %cpu= -p $GATEWAY_PID 2>/dev/null | tr -d ' ')
    MEM_MB=$((GATEWAY_MEM / 1024))
    log "  Gateway: PID $GATEWAY_PID | CPU: ${GATEWAY_CPU}% | MEM: ${MEM_MB}MB"
    if [ $MEM_MB -gt 2000 ]; then
        log "  ${RED}⚠️  WARNING: Gateway memory > 2GB${NC}"
        ISSUES=$((ISSUES + 1))
    fi
else
    log "  ${RED}✗ Gateway NOT RUNNING${NC}"
    ISSUES=$((ISSUES + 1))
fi

#---------------------------------------
# 2. Disk Usage
#---------------------------------------
log "--- Disk ---"
DISK_PCT=$(df /dev/sda1 | tail -1 | awk '{print $5}' | tr -d '%')
DISK_USED=$(df -h /dev/sda1 | tail -1 | awk '{print $3}')
DISK_TOTAL=$(df -h /dev/sda1 | tail -1 | awk '{print $2}')
log "  Disk: ${DISK_USED}/${DISK_TOTAL} (${DISK_PCT}% used)"
if [ $DISK_PCT -gt 80 ]; then
    log "  ${RED}⚠️  CRITICAL: Disk > 80%${NC}"
    ISSUES=$((ISSUES + 1))
elif [ $DISK_PCT -gt 70 ]; then
    log "  ${YELLOW}⚠️  WARNING: Disk > 70%${NC}"
fi

#---------------------------------------
# 3. RAM Usage
#---------------------------------------
log "--- RAM ---"
RAM_AVAILABLE=$(free -m | grep Mem | awk '{print $7}')
RAM_TOTAL=$(free -m | grep Mem | awk '{print $2}')
log "  RAM: ${RAM_AVAILABLE}MB available / ${RAM_TOTAL}MB total"
if [ $RAM_AVAILABLE -lt 500 ]; then
    log "  ${RED}⚠️  CRITICAL: RAM < 500MB${NC}"
    ISSUES=$((ISSUES + 1))
fi

#---------------------------------------
# 4. Services
#---------------------------------------
log "--- Services ---"
for svc in fail2ban ssh rsyslog udev; do
    if systemctl is-active --quiet $svc 2>/dev/null; then
        log "  ✓ $svc"
    else
        log "  ${RED}✗ $svc NOT running${NC}"
        ISSUES=$((ISSUES + 1))
    fi
done

#---------------------------------------
# 5. OpenClaw Crons Status
#---------------------------------------
log "--- OpenClaw Crons ---"
CRON_COUNT=$(openclaw cron list 2>/dev/null | grep -c "isolated\|main" || echo "0")
ERROR_CRONS=$(openclaw cron list 2>/dev/null | grep -c "error" || echo "0")
log "  Active crons: $CRON_COUNT"
if [ "$ERROR_CRONS" -gt 0 ]; then
    log "  ${YELLOW}⚠️  $ERROR_CRONS crons in ERROR state${NC}"
fi

#---------------------------------------
# 6. KG Health
#---------------------------------------
log "--- Knowledge Graph ---"
KG_FILE="$WORKSPACE/ceo/memory/kg/knowledge_graph.json"
if [ -f "$KG_FILE" ]; then
    KG_SIZE=$(du -sh "$KG_FILE" | cut -f1)
    ENTITY_COUNT=$(python3 -c "import json; kg=json.load(open('$KG_FILE')); print(len(kg.get('entities', {})))" 2>/dev/null || echo "?")
    log "  KG: $ENTITY_COUNT entities ($KG_SIZE)"
    
    # Orphan check
    ORPHANS=$(python3 -c "
import json
kg=json.load(open('$KG_FILE'))
entities=set(kg.get('entities', {}).keys())
linked=set()
for r in kg.get('relations', {}).values():
    linked.add(r.get('from'))
    linked.add(r.get('to'))
orphans=len(entities-linked)
total=len(entities)
print(f'{orphans}/{total} ({100*orphans/total:.1f}%)' if total > 0 else '0/0')
" 2>/dev/null || echo "?")
    log "  Orphans: $ORPHANS"
else
    log "  ${YELLOW}⚠️  KG file not found${NC}"
fi

#---------------------------------------
# 7. Workspace Size
#---------------------------------------
log "--- Workspace ---"
WS_SIZE=$(du -sh $WORKSPACE 2>/dev/null | cut -f1)
log "  Workspace: $WS_SIZE"

#---------------------------------------
# 8. Logs Check
#---------------------------------------
log "--- Recent Errors ---"
ERROR_COUNT=$(journalctl --since "24h ago" -p err --no-pager 2>/dev/null | wc -l)
log "  Errors in last 24h: $ERROR_COUNT"
if [ $ERROR_COUNT -gt 10 ]; then
    log "  ${YELLOW}⚠️  High error count${NC}"
fi

#---------------------------------------
# Summary
#---------------------------------------
log "========================================"
if [ $ISSUES -eq 0 ]; then
    log "✅ System OK — $ISSUES critical issues"
else
    log "⚠️  ISSUES FOUND: $ISSUES"
fi
log "========================================"

# Exit code for cron monitoring
exit $ISSUES
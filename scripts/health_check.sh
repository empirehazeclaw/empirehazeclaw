#!/bin/bash
#===========================================
# Health Check Script — Sir HazeClaw
#===========================================
# Monitors: CPU, RAM, Disk, Services, Crons
# Run: bash health_check.sh
#===========================================

echo "🏥 Sir HazeClaw Health Check"
echo "==============================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ISSUES=0

#---------------------------------------
# 1. Gateway Process
#---------------------------------------
echo -n "🔴 Gateway: "
GATEWAY_PID=$(pgrep -f "openclaw-gateway" | head -1)
if [ -n "$GATEWAY_PID" ]; then
    GATEWAY_MEM=$(ps -o rss= -p $GATEWAY_PID 2>/dev/null | tr -d ' ')
    GATEWAY_CPU=$(ps -o %cpu= -p $GATEWAY_PID 2>/dev/null | tr -d ' ')
    echo "${GREEN}✓${NC} PID $GATEWAY_PID | CPU: ${GATEWAY_CPU}% | MEM: $(numfmt --to=iec $GATEWAY_MEM 2>/dev/null || echo "${GATEWAY_MEM}KB")"
else
    echo "${RED}✗${NC} NOT RUNNING"
    ISSUES=$((ISSUES + 1))
fi

#---------------------------------------
# 2. RAM Usage
#---------------------------------------
echo -n "💾 RAM: "
RAM_TOTAL=$(free -b | awk '/^Mem:/ {print $2}')
RAM_AVAILABLE=$(free -b | awk '/^Mem:/ {print $7}')
RAM_USED=$(($RAM_TOTAL - $RAM_AVAILABLE))
RAM_PCT=$((RAM_USED * 100 / RAM_TOTAL))

if [ "$RAM_PCT" -lt 80 ]; then
    echo "${GREEN}✓${NC} ${RAM_PCT}% used ($(numfmt --to=iec $RAM_AVAILABLE) available)"
elif [ "$RAM_PCT" -lt 90 ]; then
    echo "${YELLOW}⚠️${NC} ${RAM_PCT}% used (running low)"
else
    echo "${RED}✗${NC} ${RAM_PCT}% used (critical)"
    ISSUES=$((ISSUES + 1))
fi

#---------------------------------------
# 3. Disk Usage
#---------------------------------------
echo -n "💿 Disk: "
DISK_PCT=$(df -h /dev/sda1 | tail -1 | awk '{print $5}' | tr -d '%')
DISK_AVAIL=$(df -h /dev/sda1 | tail -1 | awk '{print $4}')

if [ "$DISK_PCT" -lt 80 ]; then
    echo "${GREEN}✓${NC} ${DISK_PCT}% used ($DISK_AVAIL available)"
elif [ "$DISK_PCT" -lt 90 ]; then
    echo "${YELLOW}⚠️${NC} ${DISK_PCT}% used ($DISK_AVAIL available)"
else
    echo "${RED}✗${NC} ${DISK_PCT}% used (critical)"
    ISSUES=$((ISSUES + 1))
fi

#---------------------------------------
# 4. Swap Status
#---------------------------------------
echo -n "🔄 Swap: "
SWAP_TOTAL=$(free -b | awk '/^Swap:/ {print $2}')
if [ "$SWAP_TOTAL" -gt 0 ]; then
    echo "${GREEN}✓${NC} $(numfmt --to=iec $SWAP_TOTAL) configured"
else
    echo "${YELLOW}⚠️${NC} No swap configured"
fi

#---------------------------------------
# 5. System Crons
#---------------------------------------
echo -n "⏰ System Crons: "
CRON_COUNT=$(crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
echo "${GREEN}✓${NC} $CRON_COUNT entries"

#---------------------------------------
# 6. OpenClaw Crons
#---------------------------------------
echo -n "🔁 OpenClaw Crons: "
if command -v openclaw &> /dev/null; then
    TOTAL=$(openclaw cron list 2>/dev/null | grep -c "cron" || echo "0")
    FAILED=$(openclaw cron list 2>/dev/null | grep -c "error" || echo "0")
    if [ "$FAILED" -gt 0 ]; then
        echo "${YELLOW}⚠️${NC} $TOTAL total, $FAILED failed"
    else
        echo "${GREEN}✓${NC} $TOTAL total, all ok"
    fi
else
    echo "${YELLOW}⚠️${NC} openclaw CLI not found"
fi

#---------------------------------------
# 7. Failed System Services
#---------------------------------------
echo -n "🔧 System Services: "
FAILED_SVCS=$(systemctl --failed --no-pager 2>/dev/null | grep -c "failed" || echo "0")
# Fix: handle multi-line output
if [ "$FAILED_SVCS" -gt 0 ] 2>/dev/null; then
    echo "${RED}✗${NC} $FAILED_SVCS failed services"
    ISSUES=$((ISSUES + 1))
else
    echo "${GREEN}✓${NC} All services healthy"
fi

#---------------------------------------
# 8. Critical Processes
#---------------------------------------
echo -n "⚙️  Critical: "
CRITICAL_OK=0
for proc in "node" "python3" "fail2ban"; do
    if pgrep -x "$proc" > /dev/null 2>&1; then
        CRITICAL_OK=$((CRITICAL_OK + 1))
    fi
done
echo "${GREEN}✓${NC} $CRITICAL_OK/3 critical processes running"

#---------------------------------------
# 9. Network Ports
#---------------------------------------
echo -n "🌐 Ports: "
PORTS=""
for port in "22" "18789"; do
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
        PORTS="$PORTS$port "
    fi
done
echo "${GREEN}✓${NC} $PORTS(listening)"

#---------------------------------------
# 10. Uptime
#---------------------------------------
echo -n "⏱️  Uptime: "
UP=$(uptime -p 2>/dev/null || uptime)
echo "${GREEN}✓${NC} $UP"

#---------------------------------------
# Summary
#---------------------------------------
echo ""
echo "==============================="
if [ "$ISSUES" -eq 0 ]; then
    echo "✅ All systems healthy"
else
    echo "⚠️  $ISSUES issue(s) detected"
fi
echo ""

# Exit with error code if issues found
exit $ISSUES
#!/bin/bash
#===========================================
# System Cleanup Script — Sir HazeClaw
#===========================================
# Führt sichere Aufräumarbeiten durch
# Run: bash system_cleanup.sh
#===========================================

set -e

echo "🧹 Sir HazeClaw System Cleanup"
echo "==============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track freed space
FREED=0

#---------------------------------------
# 1. Broken Symlinks
#---------------------------------------
echo -n "🔗 Cleaning broken symlinks... "
BROKEN=$(find /home/clawbot -type l ! -exec test -e {} \; -print 2>/dev/null | wc -l)
if [ "$BROKEN" -gt 0 ]; then
    find /home/clawbot -type l ! -exec test -e {} \; -delete 2>/dev/null
    echo "${GREEN}✓${NC} ($BROKEN removed)"
else
    echo "${GREEN}✓${NC} (none found)"
fi

#---------------------------------------
# 2. Temp files
#---------------------------------------
echo -n "📁 Cleaning temp files... "
TEMP_BEFORE=$(du -sb /tmp 2>/dev/null | cut -f1 || echo 0)
# Only clean files older than 1 day
find /tmp -type f -atime +1 -delete 2>/dev/null || true
TEMP_AFTER=$(du -sb /tmp 2>/dev/null | cut -f1 || echo 0)
TEMP_FREED=$((TEMP_BEFORE - TEMP_AFTER))
if [ "$TEMP_FREED" -gt 0 ]; then
    echo "${GREEN}✓${NC} ($(numfmt --to=iec $TEMP_FREED) freed)"
    FREED=$((FREED + TEMP_FREED))
else
    echo "${GREEN}✓${NC}"
fi

#---------------------------------------
# 3. Log rotation check
#---------------------------------------
echo -n "📋 Checking log sizes... "
LOG_DIR="/home/clawbot/.openclaw/logs"
if [ -d "$LOG_DIR" ]; then
    LOG_SIZE=$(du -sb "$LOG_DIR" 2>/dev/null | cut -f1 || echo 0)
    if [ "$LOG_SIZE" -gt 52428800 ]; then  # > 50MB
        echo "${YELLOW}⚠️${NC} Logs at $(numfmt --to=iec $LOG_SIZE)"
        # Rotate if needed
        for log in "$LOG_DIR"/*.log; do
            [ -f "$log" ] && [ $(stat -c%s "$log" 2>/dev/null || echo 0) -gt 10485760 ] && \
                mv "$log" "${log}.$(date +%Y%m%d_%H%M%S)" 2>/dev/null
        done
        echo "   ${GREEN}✓ Rotated large logs${NC}"
    else
        echo "${GREEN}✓${NC} ($(numfmt --to=iec $LOG_SIZE))"
    fi
else
    echo "${GREEN}✓${NC} (no log dir)"
fi

#---------------------------------------
# 4. __pycache__ cleanup
#---------------------------------------
echo -n "🐍 Cleaning __pycache__... "
PYC_COUNT=$(find /home/clawbot -name "__pycache__" -type d 2>/dev/null | wc -l)
if [ "$PYC_COUNT" -gt 0 ]; then
    find /home/clawbot -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "${GREEN}✓${NC} ($PYC_COUNT dirs removed)"
else
    echo "${GREEN}✓${NC}"
fi

#---------------------------------------
# 5. .pyc cleanup
#---------------------------------------
echo -n "📄 Cleaning .pyc files... "
PYC_FILES=$(find /home/clawbot -name "*.pyc" 2>/dev/null | wc -l)
find /home/clawbot -name "*.pyc" -delete 2>/dev/null || true
echo "${GREEN}✓${NC} ($PYC_FILES files removed)"

#---------------------------------------
# 6. Old node modules in workspace
#---------------------------------------
echo -n "📦 Checking for orphaned node_modules... "
MOD_COUNT=$(find /home/clawbot/.openclaw/workspace -name "node_modules" -type d 2>/dev/null | wc -l)
if [ "$MOD_COUNT" -gt 0 ]; then
    echo "${YELLOW}⚠️${NC} Found $MOD_COUNT node_modules dirs in workspace"
    for dir in $(find /home/clawbot/.openclaw/workspace -name "node_modules" -type d 2>/dev/null); do
        SIZE=$(du -sb "$dir" 2>/dev/null | cut -f1)
        echo "   $dir: $(numfmt --to=iec $SIZE)"
    done
    echo "   ${YELLOW}Manual review needed${NC}"
else
    echo "${GREEN}✓${NC}"
fi

#---------------------------------------
# Summary
#---------------------------------------
echo ""
echo "==============================="
echo "✅ Cleanup complete"
echo ""
echo "Disk usage:"
df -h /dev/sda1 | tail -1 | awk '{print "   "$0}'
echo ""
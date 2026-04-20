#!/bin/bash
#===========================================
# Backup Verification Script — Sir HazeClaw
#===========================================
# Verifies OpenClaw backup integrity
# Run: bash backup_verify.sh
#===========================================

echo "💾 Sir HazeClaw Backup Verification"
echo "====================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="/home/clawbot/backups"
OPENCLAW_CONFIG="/home/clawbot/.openclaw/openclaw.json"
CHECKS_PASSED=0
CHECKS_TOTAL=0

#---------------------------------------
# 1. Check OpenClaw config exists
#---------------------------------------
echo -n "📋 OpenClaw config: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "${GREEN}✓${NC} exists"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "${RED}✗${NC} MISSING"
fi

#---------------------------------------
# 2. Check backup directory exists
#---------------------------------------
echo -n "📁 Backup directory: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if [ -d "$BACKUP_DIR" ]; then
    echo "${GREEN}✓${NC} exists"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "${RED}✗${NC} MISSING"
fi

#---------------------------------------
# 3. Check recent backups
#---------------------------------------
echo -n "🔄 Recent backups: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
BACKUP_COUNT=$(find "$BACKUP_DIR" -type d -name "*backup*" -mtime -7 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo "${GREEN}✓${NC} $BACKUP_COUNT in last 7 days"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "${YELLOW}⚠️${NC} No backups in last 7 days"
fi

#---------------------------------------
# 4. Check backup size
#---------------------------------------
echo -n "📊 Backup size: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if [ -d "$BACKUP_DIR" ]; then
    BACKUP_SIZE=$(du -sb "$BACKUP_DIR" 2>/dev/null | cut -f1)
    if [ "$BACKUP_SIZE" -gt 1000 ]; then
        echo "${GREEN}✓${NC} $(numfmt --to=iec $BACKUP_SIZE)"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo "${RED}✗${NC} Backup dir is empty"
    fi
else
    echo "${RED}✗${NC} No backup dir"
fi

#---------------------------------------
# 5. Check critical files in backup
#---------------------------------------
echo -n "🔐 Critical files: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
CRITICAL_FOUND=0
for file in "MEMORY.md" "secrets.env" "openclaw.json"; do
    if find "$BACKUP_DIR" -name "$file" -type f 2>/dev/null | head -1 | grep -q .; then
        CRITICAL_FOUND=$((CRITICAL_FOUND + 1))
    fi
done
if [ "$CRITICAL_FOUND" -ge 2 ]; then
    echo "${GREEN}✓${NC} $CRITICAL_FOUND/3 critical files found"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "${YELLOW}⚠️${NC} Only $CRITICAL_FOUND/3 critical files"
fi

#---------------------------------------
# 6. Verify JSON files are valid
#---------------------------------------
echo -n "📄 JSON validity: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
INVALID_JSON=0
for json in $(find "$BACKUP_DIR" -name "*.json" -type f 2>/dev/null | head -5); do
    python3 -c "import json; json.load(open('$json'))" 2>/dev/null || INVALID_JSON=$((INVALID_JSON + 1))
done
if [ "$INVALID_JSON" -eq 0 ]; then
    echo "${GREEN}✓${NC} All checked JSON files valid"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "${YELLOW}⚠️${NC} $INVALID_JSON invalid JSON files"
fi

#---------------------------------------
# 7. Check KG backup
#---------------------------------------
echo -n "🧠 KG state: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
KG_BACKUP=$(find "$BACKUP_DIR" -name "*kg*" -type f 2>/dev/null | head -1)
if [ -n "$KG_BACKUP" ]; then
    KG_SIZE=$(stat -c%s "$KG_BACKUP" 2>/dev/null || echo 0)
    echo "${GREEN}✓${NC} KG backup exists ($(numfmt --to=iec $KG_SIZE))"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "${YELLOW}⚠️${NC} No KG backup found"
fi

#---------------------------------------
# 8. Disk space for backups
#---------------------------------------
echo -n "💿 Disk space: "
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
DISK_AVAIL=$(df -B1 /dev/sda1 2>/dev/null | awk 'NR==2 {print $4}')
BACKUP_NEEDED=10737418240  # 10GB buffer
if [ "$DISK_AVAIL" -gt "$BACKUP_NEEDED" ]; then
    echo "${GREEN}✓${NC} $(numfmt --to=iec $DISK_AVAIL) available"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo "${RED}✗${NC} Only $(numfmt --to=iec $DISK_AVAIL) available"
fi

#---------------------------------------
# Summary
#---------------------------------------
echo ""
echo "====================================="
if [ "$CHECKS_PASSED" -eq "$CHECKS_TOTAL" ]; then
    echo "✅ All $CHECKS_TOTAL checks passed"
    exit 0
else
    echo "⚠️  $CHECKS_PASSED/$CHECKS_TOTAL checks passed"
    exit 1
fi
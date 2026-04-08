#!/bin/bash
# ================================================
# Data Manager — Daily System Check
# Erstellt: 2026-04-08
# Schedule: Täglich 11:31 UTC via OpenClaw cron
# =============================================

REPORT_FILE="/home/clawbot/.openclaw/workspace/data/daily_check_report.md"
MEMORY_FILE="/home/clawbot/.openclaw/workspace/MEMORY.md"
DB_DIR="/home/clawbot/.openclaw/memory"
ARCHIVE_DIR="/home/clawbot/.openclaw/workspace/memory/archive"
LOG_DIR="/home/clawbot/.openclaw/workspace/data"
MAX_MEMORY_KB=500
MAX_DB_MB=500

echo "# 📊 Daily Data Manager Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$REPORT_FILE"

# ================================================
# 1. MEMORY.md Größe prüfen
# ================================================
MEMORY_SIZE=$(wc -c < "$MEMORY_FILE" 2>/dev/null || echo 0)
MEMORY_KB=$((MEMORY_SIZE / 1024))

echo "" >> "$REPORT_FILE"
echo "## 🧠 MEMORY.md Status" >> "$REPORT_FILE"
if [ "$MEMORY_KB" -lt "$MAX_MEMORY_KB" ]; then
    echo "✅ OK: ${MEMORY_KB}KB (Limit: ${MAX_MEMORY_KB}KB)" >> "$REPORT_FILE"
else
    echo "🔴 WARNUNG: ${MEMORY_KB}KB (Limit: ${MAX_MEMORY_KB}KB) — KOMPRIMIERUNG NÖTIG!" >> "$REPORT_FILE"
fi

# ================================================
# 2. SQLite Datenbanken prüfen
# ================================================
echo "" >> "$REPORT_FILE"
echo "## 💾 SQLite Datenbanken" >> "$REPORT_FILE"
echo "| DB | Größe | Status |" >> "$REPORT_FILE"
echo "|----|-------|--------|" >> "$REPORT_FILE"

for db in "$DB_DIR"/*.sqlite; do
    [ -f "$db" ] || continue
    SIZE_MB=$(du -m "$db" 2>/dev/null | cut -f1)
    DB_NAME=$(basename "$db")
    if [ "$SIZE_MB" -lt "$MAX_DB_MB" ]; then
        echo "| $DB_NAME | ${SIZE_MB}MB | ✅ OK |" >> "$REPORT_FILE"
    else
        echo "| $DB_NAME | ${SIZE_MB}MB | 🔴 WARNUNG |" >> "$REPORT_FILE"
    fi
done

# ================================================
# 3. Archive Größe prüfen
# ================================================
echo "" >> "$REPORT_FILE"
echo "## 📦 Archive" >> "$REPORT_FILE"
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | cut -f1)
ARCHIVE_COUNT=$(find "$ARCHIVE_DIR" -type f | wc -l)
echo "Größe: $ARCHIVE_SIZE | Dateien: $ARCHIVE_COUNT" >> "$REPORT_FILE"

# Prüfe auf große Archive (>5MB)
LARGE_ARCHIVES=$(find "$ARCHIVE_DIR" -type f -size +5M 2>/dev/null)
if [ -n "$LARGE_ARCHIVES" ]; then
    echo "" >> "$REPORT_FILE"
    echo "⚠️ Grosse Archive gefunden:" >> "$REPORT_FILE"
    echo "$LARGE_ARCHIVES" | while read -r f; do
        S=$(du -h "$f" | cut -f1)
        echo "- $f ($S)" >> "$REPORT_FILE"
    done
fi

# ================================================
# 4. Knowledge Graph prüfen
# ================================================
echo "" >> "$REPORT_FILE"
echo "## 🕸️ Knowledge Graph" >> "$REPORT_FILE"
KG_FILE="/home/clawbot/.openclaw/workspace/memory/knowledge_graph.json"
if [ -f "$KG_FILE" ]; then
    KG_SIZE=$(du -h "$KG_FILE" | cut -f1)
    KG_NODES=$(grep -o '"node"' "$KG_FILE" 2>/dev/null | wc -l || echo "?")
    echo "Größe: $KG_SIZE | Nodes: $KG_NODES" >> "$REPORT_FILE"
else
    echo "⚠️ knowledge_graph.json nicht gefunden" >> "$REPORT_FILE"
fi

# ================================================
# 5. Session Count
# ================================================
echo "" >> "$REPORT_FILE"
echo "## 👥 Sessions" >> "$REPORT_FILE"
SESSION_COUNT=$(cat /home/clawbot/.openclaw/.session-count 2>/dev/null || echo "?")
echo "Aktive Sessions: $SESSION_COUNT" >> "$REPORT_FILE"

# ================================================
# Summary
# ================================================
echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "*Report generiert: $(date -u +%Y-%m-%dT%H:%M:%SZ)*" >> "$REPORT_FILE"

echo "✅ Daily Check Report erstellt: $REPORT_FILE"
cat "$REPORT_FILE"

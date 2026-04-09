#!/bin/bash
# Morning Routine - Wird täglich um 08:00 Uhr ausgeführt
echo "☀️ Starte Morning Routine..."

echo "🔍 Führe Memory Search nach wichtigen offenen Tasks durch..."
node /home/clawbot/.openclaw/workspace/scripts/autosync_v2.js --search "todo" || true

echo "📊 Baue INDEX.md neu..."
node /home/clawbot/.openclaw/workspace/scripts/autosync_v2.js --index

echo "✅ Morning Routine abgeschlossen."

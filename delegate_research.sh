#!/bin/bash
# Researcher Delegation Script
# Für Tasks die Research/Suche erfordern

TASK_FILE="$1"
TASK=$(cat "$TASK_FILE" 2>/dev/null | jq -r '.task' 2>/dev/null)

echo "🔍 RESEARCHER AGENT"
echo "=================="
echo "Task: $TASK"
echo ""

# Research durchführen
cd /home/clawbot/.openclaw/workspace

# Hier würde der echte Research laufen
# z.B. Web Search, Dateien analysieren, etc.

# Output speichern
echo "FERTIG: Research für '$TASK'" > "$TASK_FILE.done"

echo "✅ Research Agent fertig"

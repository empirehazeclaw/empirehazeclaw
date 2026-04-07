#!/bin/bash
# Nightly SQLite VACUUM for all OpenClaw memory databases
# Run: sqlite3 main.sqlite "VACUUM; ANALYZE;"

for db in /home/clawbot/.openclaw/memory/*.sqlite; do
    if [ -f "$db" ]; then
        size_before=$(stat -c%s "$db" 2>/dev/null || echo 0)
        python3 -c "
import sqlite3, sys
conn = sqlite3.connect('$db')
conn.execute('VACUUM')
conn.execute('ANALYZE')
conn.close()
" 2>/dev/null
        size_after=$(stat -c%s "$db" 2>/dev/null || echo 0)
        saved=$((size_before - size_after))
        echo "$(date) $db: ${size_before}B -> ${size_after}B (saved ${saved}B)"
    fi
done

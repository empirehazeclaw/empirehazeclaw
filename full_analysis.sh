#!/bin/bash
cd /home/clawbot/.openclaw/workspace

echo "=== 1. MEMORY STATUS ==="
python3 scripts/MEMORY_API.py status

echo ""
echo "=== 2. SCRIPTS & SKILLS COUNT ==="
echo "Scripts: $(ls scripts/*.py 2>/dev/null | wc -l)"
echo "Skills: $(ls skills/ 2>/dev/null | wc -l)"

echo ""
echo "=== 3. GITHUB COMMITS (today) ==="
git log --oneline --since="2026-04-11" | wc -l

echo ""
echo "=== 4. WORKSPACE SIZE ==="
du -sh . 2>/dev/null

echo ""
echo "=== 5. CRON STATUS ==="
openclaw cron list 2>/dev/null | grep -c "enabled" || echo "N/A"

echo ""
echo "=== COMPLETE ==="

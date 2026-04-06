#!/bin/bash
# Daily Automation Runner

echo "=== Daily Automation ==="
date

# Morning tasks
echo "1. Health Check..."
python3 scripts/health_check.py 2>/dev/null

echo "2. Local Closer..."
node scripts/local_closer.js all 2>/dev/null

echo "3. Content..."
python3 scripts/autonomous_brain.py 2>/dev/null

echo "4. Pipeline..."
python3 scripts/autonomous_pipeline.py 2>/dev/null

echo "5. Backup..."
bash scripts/github_backup.sh 2>/dev/null

echo "✅ Daily automation complete"

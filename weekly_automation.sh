#!/bin/bash
# Weekly Automation

echo "=== Weekly Automation ==="
date

# Weekly review
python3 scripts/daily_report.py

# Pipeline review
python3 projects/stages/final_report.py "Lead Generator SaaS"

# Backup
bash scripts/github_backup.sh

# Cleanup
python3 scripts/backup_rotation.py

echo "✅ Weekly complete"

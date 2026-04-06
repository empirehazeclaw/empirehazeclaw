#!/bin/bash
# GitHub Backup Script - Uses existing repo

REPO="empirehazeclaw/server-backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=== GitHub Backup to $REPO ==="

cd /home/clawbot/.openclaw/workspace

# Create archive (exclude large dirs)
tar -czf /tmp/backup_$DATE.tar.gz \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='logs' \
    --exclude='backups' \
    --exclude='videos' \
    --exclude='*.mp4' \
    .

# Upload as release asset
gh release create "backup-$DATE" --title "Backup $DATE" --notes "Auto backup" /tmp/backup_$DATE.tar.gz 2>/dev/null || \
echo "Release creation skipped (might already exist)"

echo "✅ GitHub Backup done: $DATE"
rm -f /tmp/backup_$DATE.tar.gz

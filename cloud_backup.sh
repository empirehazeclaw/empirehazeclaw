#!/bin/bash
# Cloud Backup zu Google Drive via gog CLI

echo "=== ☁️ START CLOUD BACKUP ==="
DATE=$(date +%Y%m%d_%H%M)

# Create backup
echo "📦 Creating backup..."
tar -czf /tmp/backup_$DATE.tar.gz data/ memory/ --exclude='*.git*' --exclude='node_modules'

# Get file size
SIZE=$(du -h /tmp/backup_$DATE.tar.gz | cut -f1)
echo "   Backup size: $SIZE"

# Upload to Drive
echo "☁️ Uploading to Google Drive..."
gog drive upload /tmp/backup_$DATE.tar.gz

# Cleanup
rm /tmp/backup_$DATE.tar.gz
echo "✅ Backup complete: backup_$DATE.tar.gz"

#!/bin/bash
# Smart Backup v2 - nur wichtige Daten sichern
# Läuft täglich um 2:00

BACKUP_DIR="/home/clawbot/.openclaw/workspace/backups"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"

cd /home/clawbot/.openclaw/workspace

# Alle Excludes - was NICHT sichern
EXCLUDE_STR="\
--exclude=node_modules\
--exclude=.git\
--exclude=__pycache__\
--exclude=*.pyc\
--exclude=logs\
--exclude=cache\
--exclude=.crawl4ai\
--exclude=.codex\
--exclude=ai_agents/cache\
--exclude=trading/data/raw\
--exclude=pod/workspace\
--exclude=tests\
--exclude=docs/_build\
--exclude=vercel-deployments\
--exclude=website-rebuild\
--exclude=videos\
--exclude=video-*\
--exclude=tiktok\
--exclude=backups\
--exclude=.npm-global\
--exclude=projects/website*\
--exclude=projects/store*\
--exclude=projects/demo*\
--exclude=knowledge_rag"

# Backup erstellen
tar -czf "$BACKUP_DIR/${DATE}.tar.gz" . $EXCLUDE_STR 2>/dev/null

# Backup Größe
SIZE=$(du -h "$BACKUP_DIR/${DATE}.tar.gz" | cut -f1)

# Alte Backups löschen (>7 Tage)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup erstellt: ${DATE}.tar.gz ($SIZE)"
echo "   - 7 Tage aufbewahren"
echo "   - Klein & kompakt"

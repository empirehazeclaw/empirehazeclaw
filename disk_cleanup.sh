#!/bin/bash
# Disk Cleanup & Optimization Script

echo "🧹 Starting Disk Cleanup..."

# 1. Compress old logs
echo "📦 Compressing logs..."
find /home/clawbot/.openclaw/logs -name "*.log" -type f ! -name "*.gz" -exec gzip {} \; 2>/dev/null

# 2. Clean old temp files
echo "🗑️ Cleaning temp files..."
rm -rf /tmp/openclaw* 2>/dev/null
rm -rf /home/clawbot/.openclaw/workspace/__pycache__ 2>/dev/null
find /home/clawbot/.openclaw -type d -name "__pycache__" -exec rm -rf {} \; 2>/dev/null

# 3. Clean old backups (keep last 3)
echo "💾 Cleaning old backups..."
cd /home/clawbot/.openclaw
ls -t backups/*.tar.gz 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null
ls -t *.tar.gz 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null

# 4. Show result
echo ""
echo "📊 Disk Usage after cleanup:"
du -sh /home/clawbot/.openclaw/* | sort -hr

echo ""
echo "✅ Cleanup complete!"

#!/bin/bash
# Nightly Bundle - Backup + Security + Cleanup
# Läuft um 3 Uhr

echo "🌙 Starting nightly bundle..."

# 1. Backup
echo "📦 Running backup..."
/home/clawbot/.openclaw/scripts/unified_backup.sh

# 2. Security Review
echo "🔒 Running security review..."
/home/clawbot/.openclaw/security/security-review.sh

# 3. Cache Cleanup
echo "🧹 Cleaning cache..."
python3 /home/clawbot/.openclaw/workspace/scripts/research_cache.py

# 4. System Cleanup
echo "✨ System cleanup..."
/home/clawbot/.openclaw/scripts/cleaner.sh

echo "✅ Nightly bundle complete!"

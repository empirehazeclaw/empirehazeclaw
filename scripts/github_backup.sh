#!/bin/bash
# GitHub Backup Script
# Commits and pushes workspace changes to GitHub
# Run: 0 23 * * * bash /home/clawbot/.openclaw/workspace/scripts/github_backup.sh

set -e

WORKSPACE="/home/clawbot/.openclaw/workspace"
GIT_DIR="$WORKSPACE/.git"
REMOTE="origin"
BRANCH="master"

cd "$WORKSPACE"

# Check if git repo exists
if [ ! -d "$GIT_DIR" ]; then
    echo "❌ Not a git repository. Run: cd $WORKSPACE && git init"
    exit 1
fi

# Configure git (if needed)
git config user.email "clawbot@empirehazeclaw.com" 2>/dev/null || true
git config user.name "ClawBot" 2>/dev/null || true

# Add all files except secrets and archives
git add . \
    -- ':!secrets/**' \
    -- ':!.secrets' \
    -- ':!archive/**' \
    -- ':!node_modules/**' \
    -- ':!*.sqlite' \
    -- ':!logs/**'

# Check if there are changes
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
    exit 0
fi

# Commit with timestamp
TIMESTAMP=$(date -u "+%Y-%m-%d %H:%M UTC")
git commit -m "Auto-backup: $TIMESTAMP" -m "Automated backup via github_backup.sh"

# Push to GitHub
git push "$REMOTE" "$BRANCH" 2>&1

echo "✅ GitHub backup complete: $TIMESTAMP"

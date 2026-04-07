#!/bin/bash
# GitHub Backup Script
# Commits and pushes workspace changes to GitHub
# Run: 0 23 * * * bash /home/clawbot/.openclaw/workspace/scripts/github_backup.sh

set -e

WORKSPACE="/home/clawbot/.openclaw/workspace"
GIT_DIR="$WORKSPACE/.git"
REMOTE="origin"

cd "$WORKSPACE"

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Check if git repo exists
if [ ! -d "$GIT_DIR" ]; then
    echo "❌ Not a git repository. Run: cd $WORKSPACE && git init"
    exit 1
fi

# Configure git (if needed)
git config user.email "clawbot@empirehazeclaw.com" 2>/dev/null || true
git config user.name "ClawBot" 2>/dev/null || true

# Find all files to add (exclude archives, node_modules, sqlite, logs)
# Use find to get the list, then filter with grep -v
FILES=$(find . -type f \
    ! -path "./.git/*" \
    ! -path "./archive/*" \
    ! -path "./.archive/*" \
    ! -path "./node_modules/*" \
    ! -path "./skills/semantic-search/node_modules/*" \
    ! -name "*.sqlite" \
    ! -name "*.sqlite.backup*" \
    ! -path "./logs/*" \
    ! -path "./.logs/*" \
    ! -path "./secrets/*" \
    ! -path "./.secrets" \
    ! -name "*.log" \
    ! -name ".DS_Store" \
    2>/dev/null)

# Check if there are files to add
if [ -z "$FILES" ]; then
    echo "✅ No files to commit"
    exit 0
fi

# Add all tracked + new files
echo "$FILES" | xargs git add -- 2>/dev/null || true

# Check if there are changes
if git diff --staged --quiet 2>/dev/null; then
    echo "✅ No changes to commit"
    exit 0
fi

# Commit with timestamp
TIMESTAMP=$(date -u "+%Y-%m-%d %H:%M UTC")
git commit -m "Auto-backup: $TIMESTAMP"

# Push to GitHub
git push "$REMOTE" "$BRANCH" 2>&1

echo "✅ GitHub backup complete: $TIMESTAMP"

#!/bin/bash
# Version Tracking - Track config changes

CONFIG_FILE="/home/clawbot/.openclaw/openclaw.json"
VERSION_DIR="/home/clawbot/.openclaw/versions"
LOG_FILE="/home/clawbot/.openclaw/versions/changelog.md"

mkdir -p "$VERSION_DIR"

# Create version
VERSION=$(date +%Y%m%d_%H%M)
HASH=$(md5sum "$CONFIG_FILE" | cut -d' ' -f1)

# Check if changed
LAST_HASH=$(cat "$VERSION_DIR/last_hash" 2>/dev/null)

if [ "$HASH" != "$LAST_HASH" ]; then
    echo "Config changed! Creating version..."
    
    # Save copy
    cp "$CONFIG_FILE" "$VERSION_DIR/config_$VERSION.json"
    
    # Update hash
    echo "$HASH" > "$VERSION_DIR/last_hash"
    
    # Log
    echo "## $VERSION" >> "$LOG_FILE"
    echo "- Config geändert: $HASH" >> "$LOG_FILE"
    echo "- Changes: $(git diff --stat 2>/dev/null)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    echo "✅ Version gespeichert: $VERSION"
else
    echo "Keine Änderung"
fi

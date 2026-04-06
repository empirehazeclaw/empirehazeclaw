#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 📱 TikTok Auto-Post Script
# ═══════════════════════════════════════════════════════════════════
# Automatisch neue TikTok Videos hochladen
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

TIKTOK_DIR="/home/clawbot/.openclaw/workspace/tiktok-marketing"
VIDEO_DIR="$TIKTOK_DIR/videos"
CONFIG="$TIKTOK_DIR/config.json"
LOG="$TIKTOK_DIR/upload_log.txt"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M)]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if new videos exist
check_new_videos() {
    local latest=$(ls -t "$VIDEO_DIR"/*.mp4 2>/dev/null | head -1)
    
    if [[ -z "$latest" ]]; then
        warn "Keine Videos in $VIDEO_DIR gefunden"
        return 1
    fi
    
    # Check if already uploaded today
    local today=$(date +%Y-%m-%d)
    if grep -q "$today.*$(basename $latest)" "$LOG" 2>/dev/null; then
        warn "Video bereits heute hochgeladen: $(basename $latest)"
        return 1
    fi
    
    echo "$latest"
}

# Upload to TikTok
upload_tiktok() {
    local video=$1
    local title="${2:-AI Hosting für Unternehmen}"
    local hashtag="${3:-#AI #ManagedHosting #KI #Deutschland}"
    
    log "Lade hoch: $(basename $video)"
    log "Titel: $title"
    
    # Hier würde TikTok API Aufruf kommen
    # Aktuell: Manuell über Telegram oder Web
    
    echo "$(date +%Y-%m-%d\ %H:%M) - $(basename $video) - $title" >> "$LOG"
    log "✅ Upload gestartet (manuell via Telegram)"
}

# Main
main() {
    log "📱 TikTok Auto-Post Script gestartet"
    
    video=$(check_new_videos) || exit 0
    
    # Defaut title from video name
    title=$(basename "$video" .mp4 | tr '-' ' ')
    title="🚀 $title | #AI #ManagedHosting"
    
    upload_tiktok "$video" "$title" "#AI #ManagedHosting #Deutschland"
    
    log "✅ Fertig!"
}

main "$@"

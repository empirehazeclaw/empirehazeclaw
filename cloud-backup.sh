#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# ☁️ Cloud Backup Script - EmpireHazeClaw
# ═══════════════════════════════════════════════════════════════════
# Usage: ./cloud-backup.sh [--setup] [--now]
#
# Supports: S3, Google Drive, Dropbox, B2, Wasabi, etc.
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

BACKUP_DIR="/home/clawbot/backups"
RCLONE_CONF="${HOME}/.config/rclone/rclone.conf"
REMOTE_NAME="empirehazeclaw-backup"
REMOTE_PATH="backups/$(hostname)/"

# ═══════════════════════════════════════════════════════════════════
# Setup rclone
# ═══════════════════════════════════════════════════════════════════

setup_rclone() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   ☁️ Cloud Backup Setup                                     ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Unterstützte Cloud-Anbieter:"
    echo "  1. Amazon S3"
    echo "  2. Google Drive"  
    echo "  3. Backblaze B2"
    echo "  4. Wasabi"
    echo "  5. Dropbox"
    echo ""
    read -p "Wähle einen Anbieter (1-5): " choice
    
    case $choice in
        1) setup_s3 ;;
        2) setup_gdrive ;;
        3) setup_b2 ;;
        4) setup_wasabi ;;
        5) setup_dropbox ;;
        *) echo "Ungültige Auswahl"; exit 1 ;;
    esac
}

setup_s3() {
    echo ""
    echo "=== Amazon S3 Setup ==="
    read -p "Access Key ID: " key_id
    read -s -p "Secret Access Key: " secret
    echo ""
    read -p "Bucket Name: " bucket
    read -p "Region (z.B. eu-central-1): " region
    
    mkdir -p "$(dirname $RCLONE_CONF)"
    
    cat >> "$RCLONE_CONF" << EOF
[empirehazeclaw-backup]
type = s3
provider = AWS
access_key_id = $key_id
secret_access_key = $secret
region = $region
endpoint = 
location_constraint = $region
acl = private
EOF
    
    echo "✅ S3 konfiguriert!"
}

setup_gdrive() {
    echo ""
    echo "=== Google Drive Setup ==="
    echo "Folge der Anleitung: https://rclone.org/drive/"
    rclone config
}

setup_b2() {
    echo ""
    echo "=== Backblaze B2 Setup ==="
    read -p "Account ID: " account
    read -s -p "Application Key: " key
    read -p "Bucket Name: " bucket
    
    mkdir -p "$(dirname $RCLONE_CONF)"
    
    cat >> "$RCLONE_CONF" << EOF
[empirehazeclaw-backup]
type = b2
account = $account
key = $key
bucket = $bucket
endpoint = 
EOF
    
    echo "✅ B2 konfiguriert!"
}

setup_wasabi() {
    echo ""
    echo "=== Wasabi Setup ==="
    read -p "Access Key: " key_id
    read -s -p "Secret Key: " secret
    echo ""
    read -p "Bucket Name: " bucket
    
    mkdir -p "$(dirname $RCLONE_CONF)"
    
    cat >> "$RCLONE_CONF" << EOF
[empirehazeclaw-backup]
type = s3
provider = Wasabi
access_key_id = $key_id
secret_access_key = $secret
endpoint = s3.wasabisys.com
location_constraint = eu-central-1
acl = private
EOF
    
    echo "✅ Wasabi konfiguriert!"
}

setup_dropbox() {
    echo ""
    echo "=== Dropbox Setup ==="
    rclone config
}

# ═══════════════════════════════════════════════════════════════════
# Backup to Cloud
# ═══════════════════════════════════════════════════════════════════

do_backup() {
    if ! rclone listremotes 2>/dev/null | grep -q "$REMOTE_NAME"; then
        echo "❌ Cloud nicht konfiguriert. Führe --setup aus."
        exit 1
    fi
    
    echo "📤 Backup zu Cloud wird gestartet..."
    
    # Find latest local backup
    LATEST=$(ls -td ${BACKUP_DIR}/2*/ 2>/dev/null | head -1)
    
    if [[ -z "$LATEST" ]]; then
        echo "❌ Kein lokales Backup gefunden"
        exit 1
    fi
    
    echo "📦 Backup: $LATEST"
    
    # Upload to cloud
    rclone copy "$LATEST" "${REMOTE_NAME}:${REMOTE_PATH}" \
        --progress \
        --transfers 4 \
        --checkers 8
    
    echo "✅ Cloud Backup abgeschlossen!"
    echo "📍 ${REMOTE_NAME}:${REMOTE_PATH}"
}

# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

case "${1:-}" in
    --setup|-s) setup_rclone ;;
    --now|-n) do_backup ;;
    *) echo "Usage: $0 [--setup|--now]"
       echo "  --setup : Cloud konfigurieren"
       echo "  --now   : Backup jetzt ausführen"
       ;;
esac

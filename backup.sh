#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 💾 EmpireHazeClaw - Backup Script
# ═══════════════════════════════════════════════════════════════════
# Usage: ./backup.sh [--client <name>] [--all]
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKUP_DIR="/home/clawbot/backups"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=${KEEP_DAYS:-7}

# ═══════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# ═══════════════════════════════════════════════════════════════════
# Backup Functions
# ═══════════════════════════════════════════════════════════════════

backup_workspace() {
    local client=${1:-}
    local backup_path="$BACKUP_DIR/$DATE"
    
    mkdir -p "$backup_path"
    
    log_info "Backing up workspace..."
    
    # Backup key directories
    tar -czf "$backup_path/workspace.tar.gz" \
        /home/clawbot/.openclaw/workspace/memory \
        /home/clawbot/.openclaw/workspace/projects \
        /home/clawbot/.openclaw/workspace/scripts \
        2>/dev/null || true
    
    # Backup configs
    cp /home/clawbot/.openclaw/openclaw.json "$backup_path/" 2>/dev/null || true
    
    # Backup MC if exists
    if [[ -d /home/clawbot/mission-control ]]; then
        tar -czf "$backup_path/mission-control.tar.gz" \
            /home/clawbot/mission-control/.env.local \
            /home/clawbot/mission-control/ecosystem.config.js \
            2>/dev/null || true
    fi
    
    # Backup nginx config
    cp /etc/nginx/sites-available/mc-8889 "$backup_path/" 2>/dev/null || true
    
    log_success "Workspace backup: $backup_path/workspace.tar.gz"
}

backup_configs() {
    local backup_path="$BACKUP_DIR/$DATE"
    
    mkdir -p "$backup_path/configs"
    
    log_info "Backing up configs..."
    
    # System configs
    cp ~/.config/systemd/user/openclaw-gateway.service "$backup_path/configs/" 2>/dev/null || true
    cp /home/clawbot/.bashrc "$backup_path/configs/" 2>/dev/null || true
    
    # Environment files
    cp ~/.openclaw/.env.api "$backup_path/configs/" 2>/dev/null || true
    
    log_success "Configs backup: $backup_path/configs/"
}

backup_databases() {
    local backup_path="$BACKUP_DIR/$DATE"
    
    mkdir -p "$backup_path/db"
    
    log_info "Backing up databases..."
    
    # PM2 dump
    pm2 save 2>/dev/null || true
    cp ~/.pm2/pm2.dump "$backup_path/db/" 2>/dev/null || true
    
    # MC database if exists
    if [[ -f /home/clawbot/mission-control/data/*.db ]]; then
        cp /home/clawbot/mission-control/data/*.db "$backup_path/db/" 2>/dev/null || true
    fi
    
    log_success "Database backup: $backup_path/db/"
}

cleanup_old_backups() {
    log_info "Cleaning up backups older than $KEEP_DAYS days..."
    
    find "$BACKUP_DIR" -type d -name "2*" -mtime +$KEEP_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    # Keep at least 3 backups
    backup_count=$(find "$BACKUP_DIR" -type d -name "2*" | wc -l)
    if [[ $backup_count -gt 3 ]]; then
        log_info "Kept $backup_count backups"
    fi
}

verify_backup() {
    local backup_path="$BACKUP_DIR/$DATE"
    
    log_info "Verifying backup..."
    
    errors=0
    
    # Check workspace archive
    if [[ -f "$backup_path/workspace.tar.gz" ]]; then
        if tar -tzf "$backup_path/workspace.tar.gz" &>/dev/null; then
            log_success "Workspace archive OK"
        else
            log_warn "Workspace archive corrupted"
            ((errors++))
        fi
    fi
    
    # Check size
    size=$(du -sh "$backup_path" 2>/dev/null | cut -f1)
    log_info "Backup size: $size"
}

# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

main() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   💾 EmpireHazeClaw - Backup Script                      ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    mkdir -p "$BACKUP_DIR"
    
    case "${1:-all}" in
        --all|-a)
            backup_workspace
            backup_configs
            backup_databases
            ;;
        --configs|-c)
            backup_configs
            ;;
        --workspace|-w)
            backup_workspace
            ;;
        --client|-m)
            backup_workspace "$2"
            ;;
        *)
            echo "Usage: $0 [--all|--configs|--workspace|--client <name>]"
            echo "Default: --all"
            exit 1
            ;;
    esac
    
    cleanup_old_backups
    verify_backup
    
    echo ""
    echo "💾 Backup Complete: $BACKUP_DIR/$DATE/"
    echo ""
    echo "To restore:"
    echo "  tar -xzf $BACKUP_DIR/$DATE/workspace.tar.gz -C /"
}

main "$@"

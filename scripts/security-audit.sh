#!/bin/bash
#==============================================================================
# SIR HAZECLAW — SECURITY AUDIT SCRIPT
# Based on: security-audit-toolkit (ClawHub) Pattern
# Version: 1.0.1 | Created: 2026-04-10
#==============================================================================

set -uo pipefail

# Configuration
AUDIT_DIR="${1:-/home/clawbot/.openclaw/workspace}"
AUDIT_MODE="${2:-normal}"
ISSUES=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()  { echo -e "${GREEN}[OK]${NC} $1"; ((ISSUES++)); }
warn(){ echo -e "${YELLOW}[WARN]${NC} $1"; ((WARNINGS++)); }
fail(){ echo -e "${RED}[FAIL]${NC} $1"; ((ISSUES++)); }

section() {
    echo ""
    echo "=========================================="
    echo -e "${BLUE}$1${NC}"
    echo "=========================================="
}

audit_secrets() {
    section "1. SECRET DETECTION"
    local secrets_found=0

    log "Checking for AWS keys..."
    if grep -rn 'AKIA[0-9A-Z]\{16\}' "$AUDIT_DIR" \
        --include='*.{js,ts,py,go,env,yml,yaml,json,xml,cfg,conf,ini}' \
        2>/dev/null | grep -v 'node_modules\|\.git' | grep -q .; then
        fail "AWS Access Keys found!"
        secrets_found=$((secrets_found+1))
    else
        ok "No AWS keys found"
    fi

    log "Checking for private keys..."
    if grep -rn 'BEGIN.*PRIVATE KEY' "$AUDIT_DIR" 2>/dev/null | grep -qv 'node_modules\|\.git'; then
        fail "Private keys found!"
        secrets_found=$((secrets_found+1))
    else
        ok "No private keys found"
    fi

    log "Checking for API keys and tokens..."
    if grep -rn -i 'api[_-]\?key\|api[_-]\?secret\|access[_-]\?token' \
        "$AUDIT_DIR" --include='*.{js,ts,py,go,env,yml,yaml,json}' \
        2>/dev/null | grep -v 'node_modules\|\.git\|example\|test\|mock\|placeholder' | grep -q .; then
        warn "Potential API keys found - review manually"
        secrets_found=$((secrets_found+1))
    else
        ok "No obvious API keys found"
    fi

    log "Checking for GitHub tokens..."
    if grep -rn 'ghp_[A-Za-z0-9]\{36\}' "$AUDIT_DIR" \
        --include='*.{js,py,go,env,yml,yaml,json}' 2>/dev/null | grep -qv 'node_modules\|\.git'; then
        fail "GitHub tokens found!"
        secrets_found=$((secrets_found+1))
    else
        ok "No GitHub tokens found"
    fi

    log "Checking for hardcoded passwords..."
    if grep -rn -i 'password\s*[:=]' "$AUDIT_DIR" \
        --include='*.{js,py,go,yml,yaml,json,env}' 2>/dev/null | \
        grep -v 'node_modules\|\.git\|example\|test\|mock\|placeholder\|changeme' | grep -q .; then
        warn "Potential hardcoded passwords found"
        secrets_found=$((secrets_found+1))
    else
        ok "No hardcoded passwords found"
    fi
}

audit_permissions() {
    section "3. FILE PERMISSION AUDIT"

    log "Checking for world-writable files..."
    if [ "$(find "$AUDIT_DIR" -type f -perm -o=w \
        -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | wc -l)" -gt 0 ]; then
        warn "World-writable files found:"
        find "$AUDIT_DIR" -type f -perm -o=w \
            -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | head -5
    else
        ok "No world-writable files"
    fi

    if [ -d "$HOME/.ssh" ]; then
        log "Checking SSH permissions..."
        local ssh_perms
        ssh_perms=$(stat -c '%a' "$HOME/.ssh" 2>/dev/null || echo "unknown")
        [ "$ssh_perms" != "700" ] && warn "~/.ssh has $ssh_perms, should be 700" || ok "SSH permissions OK"
    fi
}

audit_ssl() {
    section "4. SSL/TLS VERIFICATION"

    log "Checking for SSL verification bypasses..."
    if grep -rn "verify\s*=\s*False\|rejectUnauthorized.*false\|InsecureSkipVerify.*true" \
        "$AUDIT_DIR" --include='*.{py,js,yml,yaml}' 2>/dev/null | \
        grep -v 'node_modules\|\.git\|test\|spec' | grep -q .; then
        warn "SSL verification may be disabled in some files"
    else
        ok "No SSL verification bypasses found"
    fi

    log "Checking for CORS wildcards..."
    if grep -rn "Access-Control-Allow-Origin.*\*" "$AUDIT_DIR" \
        --include='*.{py,js,yml,yaml}' 2>/dev/null | grep -qv 'node_modules\|\.git'; then
        warn "CORS wildcard found"
    else
        ok "No CORS wildcards found"
    fi
}

audit_code_patterns() {
    section "5. CODE PATTERN AUDIT"

    log "Checking for command injection patterns..."
    if grep -rn "exec(\|spawn(\|system(\|popen(\|subprocess\|os\.system" \
        "$AUDIT_DIR/scripts" --include='*.{py,js,ts}' 2>/dev/null | \
        grep -qv 'node_modules\|\.git'; then
        warn "Potential command injection in scripts/"
    else
        ok "No obvious command injection vectors"
    fi

    log "Checking for eval() usage..."
    if grep -rn "eval(\|new Function(" "$AUDIT_DIR" \
        --include='*.{js,ts}' 2>/dev/null | grep -qv 'node_modules\|\.git'; then
        warn "eval() usage found"
    else
        ok "No eval() usage"
    fi

    log "Checking for debug mode..."
    if grep -rn "DEBUG\s*=\s*True\|debug:\s*true" "$AUDIT_DIR" \
        --include='*.{py,yml,yaml,json,env}' 2>/dev/null | \
        grep -v 'node_modules\|\.git\|test' | grep -q .; then
        warn "Debug mode enabled"
    else
        ok "No debug flags in production"
    fi
}

audit_gitignore() {
    section "6. GITIGNORE AUDIT"

    if [ ! -f "$AUDIT_DIR/.gitignore" ]; then
        warn "No .gitignore found"
        return
    fi

    log "Checking .gitignore coverage..."
    for entry in '.env' 'node_modules' '*.key' '*.pem' '*.log'; do
        grep -q "$entry" "$AUDIT_DIR/.gitignore" 2>/dev/null || warn "Missing: $entry"
    done
}

main() {
    echo ""
    echo -e "${GREEN}=========================================="
    echo -e "  Sir HazeClaw Security Audit v1.0.1"
    echo -e "  $(date -u '+%Y-%m-%d %H:%M UTC')"
    echo -e "==========================================${NC}"
    echo ""
    echo "Target: $AUDIT_DIR"
    echo ""

    audit_secrets
    audit_code_patterns
    audit_permissions
    audit_ssl
    audit_gitignore

    section "SUMMARY"
    echo -e "Issues: ${RED}$ISSUES${NC} | Warnings: ${YELLOW}$WARNINGS${NC}"
    echo ""

    [ $ISSUES -eq 0 ] && echo -e "${GREEN}✅ AUDIT PASSED${NC}" || echo -e "${RED}⚠️  ISSUES FOUND${NC}"
}

# Help
if [ "${1:-}" == "--help" ] || [ "${1:-}" == "-h" ]; then
    echo "Sir HazeClaw Security Audit v1.0.1"
    echo ""
    echo "Usage: $0 [directory] [--full]"
    echo "  $0 /path/to/project --full"
    exit 0
fi

main

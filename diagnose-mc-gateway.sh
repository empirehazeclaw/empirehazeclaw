#!/bin/bash
#
# ═══════════════════════════════════════════════════════════════
# 🔍 Mission Control + OpenClaw Gateway Diagnostic Tool
# ═══════════════════════════════════════════════════════════════
# Usage: ./diagnose-mc-gateway.sh [--fix] [--verbose]
# 
# Checks ALL aspects of MC + Gateway connectivity
# Outputs structured report with auto-fix suggestions
# ═══════════════════════════════════════════════════════════════

set -uo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Options
AUTO_FIX=false
VERBOSE=false
JSON_OUTPUT=false
if [[ "${1:-}" == "--fix" ]]; then AUTO_FIX=true; shift; fi
if [[ "${1:-}" == "--verbose" ]]; then VERBOSE=true; shift; fi
if [[ "${1:-}" == "--json" ]]; then JSON_OUTPUT=true; shift; fi

# Paths
OPENCLAW_CONFIG="/home/clawbot/.openclaw/openclaw.json"
MC_DIR="/home/clawbot/mission-control"
MC_ENV="$MC_DIR/.env.local"
MC_ECOSYSTEM="$MC_DIR/ecosystem.config.js"
GATEWAY_LOG="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
SYSTEMD_SERVICE="$HOME/.config/systemd/user/openclaw-gateway.service"

# Counters
PASS=0
FAIL=0
WARN=0
ISSUES=()

# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

log_pass() { echo -e "${GREEN}✅${NC} $1"; PASS=$((PASS+1)); }
log_fail() { echo -e "${RED}❌${NC} $1"; FAIL=$((FAIL+1)); ISSUES+=("$1"); }
log_warn() { echo -e "${YELLOW}⚠️${NC} $1"; WARN=$((WARN+1)); }
log_info() { echo -e "${BLUE}ℹ️${NC} $1"; }
log_verbose() { if $VERBOSE; then echo -e "${CYAN}  → $1${NC}"; fi; }
log_header() { echo -e "\n${BOLD}${CYAN}━━━ $1 ━━━${NC}"; }
log_fix() { echo -e "${YELLOW}  💡 FIX: $1${NC}"; }

# ═══════════════════════════════════════════════════════════════
# Section 1: Service Status
# ═══════════════════════════════════════════════════════════════

check_services() {
    log_header "SERVICE STATUS"
    
    # Gateway (systemd)
    if systemctl --user is-active --quiet openclaw-gateway 2>/dev/null; then
        log_pass "Gateway (systemd): running"
        GATEWAY_PID=$(systemctl --user show openclaw-gateway --property=MainPID --value 2>/dev/null)
        log_verbose "Gateway PID: $GATEWAY_PID"
    else
        log_fail "Gateway (systemd): NOT running"
    fi
    
    # Mission Control (PM2)
    if pm2 list 2>/dev/null | grep -q "mission-control.*online"; then
        log_pass "Mission Control (PM2): online"
        MC_PID=$(pm2 list 2>/dev/null | grep mission-control | awk 'NR==1{print $4}')
        log_verbose "MC PID: $MC_PID"
    else
        log_fail "Mission Control (PM2): NOT online"
    fi
    
    # nginx
    if pgrep -x nginx > /dev/null 2>&1; then
        log_pass "nginx: running"
    else
        log_fail "nginx: NOT running"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Section 2: Port Connectivity
# ═══════════════════════════════════════════════════════════════

check_ports() {
    log_header "PORT CONNECTIVITY"
    
    # Gateway port 18789
    if ss -tlnp 2>/dev/null | grep -q "18789"; then
        log_pass "Gateway port 18789: LISTENING"
        ss -tlnp 2>/dev/null | grep "18789" | head -1 | log_verbose "$(cat)"
    else
        log_fail "Gateway port 18789: NOT listening"
    fi
    
    # MC port 3000
    if ss -tlnp 2>/dev/null | grep -q ":3000 "; then
        log_pass "MC port 3000: LISTENING"
        ss -tlnp 2>/dev/null | grep ":3000" | head -1 | log_verbose "$(cat)"
    else
        log_fail "MC port 3000: NOT listening"
    fi
    
    # nginx SSL port 8889
    if ss -tlnp 2>/dev/null | grep -q ":8889 "; then
        log_pass "nginx port 8889: LISTENING"
    else
        log_fail "nginx port 8889: NOT listening"
    fi
    
    # WebSocket endpoint test
    if curl -sf --max-time 3 http://127.0.0.1:18789/ > /dev/null 2>&1; then
        log_pass "Gateway HTTP: responding"
    else
        log_fail "Gateway HTTP: NOT responding"
    fi
    
    if curl -sf --max-time 3 http://127.0.0.1:3000/ > /dev/null 2>&1; then
        log_pass "MC HTTP: responding"
    else
        log_fail "MC HTTP: NOT responding"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Section 3: Gateway Config
# ═══════════════════════════════════════════════════════════════

check_gateway_config() {
    log_header "GATEWAY CONFIG"
    
    if [[ ! -f "$OPENCLAW_CONFIG" ]]; then
        log_fail "Gateway config not found: $OPENCLAW_CONFIG"
        return
    fi
    
    # Extract values with python for reliable JSON parsing
    GATEWAY_AUTH_MODE=$(python3 -c "import json; c=json.load(open('$OPENCLAW_CONFIG')); print(c.get('gateway',{}).get('auth',{}).get('mode','NOT SET'))" 2>/dev/null || echo "ERROR")
    GATEWAY_TOKEN=$(python3 -c "import json; c=json.load(open('$OPENCLAW_CONFIG')); print(c.get('gateway',{}).get('auth',{}).get('token','NOT SET'))" 2>/dev/null || echo "ERROR")
    GATEWAY_BIND=$(python3 -c "import json; c=json.load(open('$OPENCLAW_CONFIG')); print(c.get('gateway',{}).get('bind','NOT SET'))" 2>/dev/null || echo "ERROR")
    DEVICE_AUTH=$(python3 -c "import json; c=json.load(open('$OPENCLAW_CONFIG')); print(c.get('gateway',{}).get('controlUi',{}).get('dangerouslyDisableDeviceAuth','NOT SET'))" 2>/dev/null || echo "ERROR")
    TRUSTED_PROXIES=$(python3 -c "import json; c=json.load(open('$OPENCLAW_CONFIG')); print(c.get('gateway',{}).get('trustedProxies','NOT SET'))" 2>/dev/null || echo "ERROR")
    ALLOWED_ORIGINS=$(python3 -c "import json; c=json.load(open('$OPENCLAW_CONFIG')); o=c.get('gateway',{}).get('controlUi',{}).get('allowedOrigins',[]); print(len(o), 'origins configured')" 2>/dev/null || echo "ERROR")
    
    # Auth Mode
    if [[ "$GATEWAY_AUTH_MODE" == "none" ]] || [[ "$GATEWAY_AUTH_MODE" == "disabled" ]]; then
        log_pass "Gateway auth.mode: $GATEWAY_AUTH_MODE (no token required)"
    elif [[ "$GATEWAY_AUTH_MODE" == "token" ]]; then
        log_warn "Gateway auth.mode: token (requires token)"
        log_fix "If MC can't connect, set: gateway config.patch '{\"gateway\":{\"auth\":{\"mode\":\"none\"}}}'"
    else
        log_warn "Gateway auth.mode: $GATEWAY_AUTH_MODE"
    fi
    
    # Bind mode
    if [[ "$GATEWAY_BIND" == "loopback" ]]; then
        log_info "Gateway bind: loopback (only local access)"
    else
        log_warn "Gateway bind: $GATEWAY_BIND"
    fi
    
    # Device Auth
    if [[ "$DEVICE_AUTH" == "true" ]]; then
        log_info "Device Auth DISABLED (intentional for MC) (dangerouslyDisableDeviceAuth=true)"
        log_verbose "This is OK for trusted local networks"
    elif [[ "$DEVICE_AUTH" == "false" ]]; then
        log_pass "Device Auth: enabled"
    else
        log_info "Device Auth: $DEVICE_AUTH"
    fi
    
    # Trusted Proxies
    if [[ "$TRUSTED_PROXIES" == "NOT SET" ]] || [[ "$TRUSTED_PROXIES" == "[]" ]]; then
        log_warn "trustedProxies: NOT configured (nginx may be treated as remote)"
        log_fix "Set trustedProxies: gateway config.patch '{\"gateway\":{\"trustedProxies\":[\"127.0.0.1\",\"::1\"]}}'"
    else
        log_pass "trustedProxies: $TRUSTED_PROXIES"
    fi
    
    # Allowed Origins count
    if [[ "$ALLOWED_ORIGINS" == "0 origins configured" ]]; then
        log_warn "allowedOrigins: none configured"
    else
        log_pass "allowedOrigins: $ALLOWED_ORIGINS"
    fi
    
    log_verbose "Gateway Token (first 20 chars): ${GATEWAY_TOKEN:0:20}..."
}

# ═══════════════════════════════════════════════════════════════
# Section 4: MC Config
# ═══════════════════════════════════════════════════════════════

check_mc_config() {
    log_header "MISSION CONTROL CONFIG"
    
    if [[ ! -f "$MC_ENV" ]]; then
        log_fail "MC env file not found: $MC_ENV"
        return
    fi
    
    # Extract MC env vars
    MC_GATEWAY_TOKEN=$(grep "OPENCLAW_GATEWAY_TOKEN=" "$MC_ENV" 2>/dev/null | cut -d= -f2 || echo "NOT SET")
    MC_GATEWAY_HOST=$(grep "OPENCLAW_GATEWAY_HOST=" "$MC_ENV" 2>/dev/null | cut -d= -f2 || echo "NOT SET")
    MC_GATEWAY_PORT=$(grep "OPENCLAW_GATEWAY_PORT=" "$MC_ENV" 2>/dev/null | cut -d= -f2 || echo "NOT SET")
    MC_PUBLIC_URL=$(grep "NEXT_PUBLIC_GATEWAY_URL=" "$MC_ENV" 2>/dev/null | cut -d= -f2 || echo "NOT SET")
    
    # MC Token
    if [[ "$MC_GATEWAY_TOKEN" == "NOT SET" ]] || [[ -z "$MC_GATEWAY_TOKEN" ]]; then
        log_fail "MC OPENCLAW_GATEWAY_TOKEN: NOT SET"
    else
        log_pass "MC OPENCLAW_GATEWAY_TOKEN: configured"
        log_verbose "Token (first 20 chars): ${MC_GATEWAY_TOKEN:0:20}..."
    fi
    
    # Gateway Host
    if [[ "$MC_GATEWAY_HOST" == "127.0.0.1" ]] || [[ "$MC_GATEWAY_HOST" == "localhost" ]]; then
        log_pass "MC OPENCLAW_GATEWAY_HOST: $MC_GATEWAY_HOST (correct for nginx)"
    else
        log_warn "MC OPENCLAW_GATEWAY_HOST: $MC_GATEWAY_HOST"
    fi
    
    # Public URL
    if [[ "$MC_PUBLIC_URL" == *"8889"* ]]; then
        log_pass "MC NEXT_PUBLIC_GATEWAY_URL: $MC_PUBLIC_URL"
    else
        log_warn "MC NEXT_PUBLIC_GATEWAY_URL: $MC_PUBLIC_URL"
        log_fix "Should point to nginx SSL port 8889"
    fi
    
    # Check ecosystem config
    if [[ -f "$MC_ECOSYSTEM" ]]; then
        log_pass "MC ecosystem.config.js: exists"
        if grep -q "OPENCLAW_GATEWAY_TOKEN" "$MC_ECOSYSTEM"; then
            log_pass "MC ecosystem has OPENCLAW_GATEWAY_TOKEN env var"
        else
            log_warn "MC ecosystem does NOT have OPENCLAW_GATEWAY_TOKEN"
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════
# Section 5: Token Match Check
# ═══════════════════════════════════════════════════════════════

check_token_match() {
    log_header "TOKEN MATCH CHECK"
    
    GATEWAY_TOKEN=$(python3 -c "import json; c=json.load(open('$OPENCLAW_CONFIG')); print(c.get('gateway',{}).get('auth',{}).get('token',''))" 2>/dev/null || echo "")
    MC_TOKEN=$(grep "OPENCLAW_GATEWAY_TOKEN=" "$MC_ENV" 2>/dev/null | cut -d= -f2 || echo "")
    
    if [[ "$GATEWAY_AUTH_MODE" == "none" ]]; then
        log_pass "Gateway auth.mode=none (no token required)"
    elif [[ -z "$GATEWAY_TOKEN" ]] || [[ "$GATEWAY_TOKEN" == "null" ]]; then
        log_info "Gateway has no token configured"
    elif [[ "$GATEWAY_TOKEN" == "$MC_TOKEN" ]]; then
        log_pass "Tokens MATCH between Gateway and MC"
        log_verbose "Gateway: ${GATEWAY_TOKEN:0:20}..."
        log_verbose "MC:     ${MC_TOKEN:0:20}..."
    else
        log_fail "Tokens DO NOT MATCH!"
        log_verbose "Gateway: ${GATEWAY_TOKEN:0:20}..."
        log_verbose "MC:     ${MC_TOKEN:0:20}..."
        log_fix "Either set gateway to auth.mode=none OR set correct token in MC"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Section 6: WebSocket Test
# ═══════════════════════════════════════════════════════════════

check_websocket() {
    log_header "WEBSOCKET FUNCTIONALITY"
    
    # Test 1: Direct to Gateway (plain TCP, no SSL for localhost)
    RESULT=$(python3 -c "
import socket, base64, os
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect(('127.0.0.1', 18789))
    key = base64.b64encode(os.urandom(16)).decode()
    sock.send(f'GET / HTTP/1.1\r\nHost: 127.0.0.1:18789\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: {key}\r\n\r\n'.encode())
    r = sock.recv(4096).decode()
    print('101' if '101' in r else 'FAIL:' + r[:100])
    sock.close()
except Exception as e:
    print('ERROR:' + str(e))
" 2>/dev/null || echo "ERROR")
    
    if [[ "$RESULT" == "101" ]]; then
        log_pass "WebSocket direct to Gateway: 101 Switching Protocols"
    else
        log_fail "WebSocket direct to Gateway: $RESULT"
    fi
    
    # Test 2: Through nginx
    RESULT=$(python3 -c "
import ssl, socket, base64, os
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    sock = ctx.wrap_socket(socket.socket(), server_hostname='187.124.11.27')
    sock.settimeout(5)
    sock.connect(('187.124.11.27', 8889))
    key = base64.b64encode(os.urandom(16)).decode()
    sock.send(f'GET /gateway-ws HTTP/1.1\r\nHost: 187.124.11.27:8889\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: {key}\r\nOrigin: https://187.124.11.27:8889\r\n\r\n'.encode())
    r = sock.recv(4096).decode()
    print('101' if '101' in r else 'FAIL:' + r[:100])
    sock.close()
except Exception as e:
    print('ERROR:' + str(e))
" 2>/dev/null || echo "ERROR")
    
    if [[ "$RESULT" == "101" ]]; then
        log_pass "WebSocket through nginx to Gateway: 101 Switching Protocols"
    else
        log_fail "WebSocket through nginx to Gateway: $RESULT"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Section 7: Recent Gateway Logs
# ═══════════════════════════════════════════════════════════════

check_gateway_logs() {
    log_header "RECENT GATEWAY LOGS (Last 3 min)"
    
    if [[ ! -f "$GATEWAY_LOG" ]]; then
        log_warn "Gateway log not found: $GATEWAY_LOG"
        return
    fi
    
    SINCE=$(date -d "3 minutes ago" +%H:%M:%S 2>/dev/null || echo "00:00:00")
    
    # Count errors
    ERROR_COUNT=$(grep -c "unauthorized\|token_mismatch\|error" "$GATEWAY_LOG" 2>/dev/null)
    
    # Get recent errors
    RECENT_ERRORS=$(python3 -c "
import json
errors = []
try:
    with open('$GATEWAY_LOG') as f:
        for line in f:
            try:
                d = json.loads(line.strip())
                t = d.get('time','')[11:19]
                msg = str(d.get('1', d.get('msg', '')))
                if any(x in msg.lower() for x in ['unauthorized', 'error', 'mismatch', 'failed']):
                    if t >= '$SINCE':
                        errors.append(t + ' ' + msg[:100])
            except: pass
except: pass
print('\n'.join(errors[-10:]) if errors else 'No recent errors')
" 2>/dev/null)
    
    if [[ "$ERROR_COUNT" == "0" ]]; then
        log_pass "No auth errors in gateway log"
    else
        log_warn "$ERROR_COUNT auth/error entries found in log"
        if $VERBOSE && [[ "$RECENT_ERRORS" != "No recent errors" ]]; then
            echo "$RECENT_ERRORS" | while read line; do
                log_verbose "$line"
            done
        fi
    fi
    
    # Check for successful connections
    SUCCESS_COUNT=$(grep -c "res ✓\|connect.challenge\|handshake.*pending" "$GATEWAY_LOG" 2>/dev/null | head -1)
    log_info "Recent successful gateway interactions: $SUCCESS_COUNT"
}

# ═══════════════════════════════════════════════════════════════
# Section 8: System Performance Vars
# ═══════════════════════════════════════════════════════════════

check_performance_vars() {
    log_header "SYSTEM PERFORMANCE"
    
    # Check systemd service environment
    if [[ -f "$SYSTEMD_SERVICE" ]]; then
        if grep -q "NODE_COMPILE_CACHE" "$SYSTEMD_SERVICE" 2>/dev/null; then
            log_pass "NODE_COMPILE_CACHE: set in systemd service"
        else
            log_warn "NODE_COMPILE_CACHE: NOT set (slow CLI startup)"
            log_fix "Add to $SYSTEMD_SERVICE: Environment=NODE_COMPILE_CACHE=/tmp/node_compile_cache"
        fi
        
        if grep -q "OPENCLAW_NO_RESPAWN" "$SYSTEMD_SERVICE" 2>/dev/null; then
            log_pass "OPENCLAW_NO_RESPAWN: set"
        else
            log_warn "OPENCLAW_NO_RESPAWN: NOT set"
            log_fix "Add to $SYSTEMD_SERVICE: Environment=OPENCLAW_NO_RESPAWN=1"
        fi
    else
        log_warn "Systemd service file not found: $SYSTEMD_SERVICE"
    fi
    
    # Check if services need restart
    GATEWAY_UPTIME=$(systemctl --user show openclaw-gateway --property=ActiveEnterTimestamp --value 2>/dev/null | head -1 || echo "unknown")
    log_verbose "Gateway started: $GATEWAY_UPTIME"
}

# ═══════════════════════════════════════════════════════════════
# Section 9: MC PM2 Status
# ═══════════════════════════════════════════════════════════════

check_mc_pm2() {
    log_header "MISSION CONTROL PM2 DETAILS"
    
    if pm2 list 2>/dev/null | grep -q "mission-control"; then
        MC_STATUS=$(pm2 list 2>/dev/null | grep mission-control | awk '{print $10, $12}')
        MC_RESTARTS=$(pm2 list 2>/dev/null | grep mission-control | awk '{print $13}')
        log_info "MC Status: $MC_STATUS"
        log_info "MC Restarts: $MC_RESTARTS"
        
        if echo "$MC_RESTARTS" | grep -qE "[0-9]+"; then
            RESTART_COUNT=$(echo "$MC_RESTARTS" | grep -oE "[0-9]+" || echo "0")
            if [[ "$RESTART_COUNT" -gt 3 ]]; then
                log_warn "MC has restarted $RESTART_COUNT times (possible crash loop)"
            fi
        fi
    else
        log_fail "Mission Control PM2 process not found"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Section 10: nginx Reverse Proxy Config
# ═══════════════════════════════════════════════════════════════

check_nginx_config() {
    log_header "NGINX REVERSE PROXY"
    
    NGINX_CONF=$(find /etc/nginx -name "mc-8889" -o -name "mission-control" 2>/dev/null | head -1)
    
    if [[ -n "$NGINX_CONF" ]] && [[ -f "$NGINX_CONF" ]]; then
        log_pass "nginx config found: $NGINX_CONF"
        
        # Check WebSocket proxy
        if grep -q "proxy_set_header Upgrade" "$NGINX_CONF" 2>/dev/null; then
            log_pass "nginx WebSocket proxy: configured"
        else
            log_fail "nginx WebSocket proxy: NOT configured"
        fi
        
        # Check SSL
        if grep -q "ssl_certificate" "$NGINX_CONF" 2>/dev/null; then
            log_pass "nginx SSL: enabled"
        else
            log_fail "nginx SSL: NOT enabled"
        fi
        
        # Check upstream to gateway
        if grep -q "18789" "$NGINX_CONF" 2>/dev/null; then
            log_pass "nginx upstream to gateway: configured"
        else
            log_fail "nginx upstream to gateway: NOT configured"
        fi
    else
        log_warn "nginx MC config not found in /etc/nginx"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Section 11: SSL Certificate
# ═══════════════════════════════════════════════════════════════

check_ssl_cert() {
    log_header "SSL CERTIFICATE"
    
    CERT="/etc/nginx/ssl/mc.crt"
    if [[ -f "$CERT" ]]; then
        EXPIRY=$(openssl x509 -enddate -noout -in "$CERT" 2>/dev/null | cut -d= -f2 || echo "unknown")
        log_pass "SSL Certificate exists"
        log_verbose "Expires: $EXPIRY"
        
        # Check if expiring soon
        if command -v openssl > /dev/null 2>&1; then
            DAYS_LEFT=$(openssl x509 -checkend 0 -in "$CERT" 2>/dev/null && echo "valid" || echo "expired/expiring")
            log_verbose "Certificate status: $DAYS_LEFT"
        fi
    else
        log_fail "SSL Certificate not found: $CERT"
    fi
}

# ═══════════════════════════════════════════════════════════════
# Auto-Fix Section
# ═══════════════════════════════════════════════════════════════

auto_fix() {
    log_header "AUTO-FIX SUGGESTIONS"
    
    echo -e "${YELLOW}To fix all issues automatically, run:${NC}"
    echo ""
    echo -e "${CYAN}# 1. Set trustedProxies:${NC}"
    echo "gateway config.patch '{\"gateway\":{\"trustedProxies\":[\"127.0.0.1\",\"::1\"]}}'"
    echo ""
    echo -e "${CYAN}# 2. Set auth.mode=none (if MC has no token):${NC}"
    echo "gateway config.patch '{\"gateway\":{\"auth\":{\"mode\":\"none\"}}}'"
    echo ""
    echo -e "${CYAN}# 3. Restart Gateway:${NC}"
    echo "systemctl --user restart openclaw-gateway"
    echo ""
    echo -e "${CYAN}# 4. Restart MC:${NC}"
    echo "pm2 restart mission-control"
    echo ""
    echo -e "${CYAN}# 5. Verify:${NC}"
    echo "./scripts/diagnose-mc-gateway.sh"
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════

print_summary() {
    log_header "SUMMARY"
    
    TOTAL=$((PASS + FAIL + WARN))
    
    echo -e "${BOLD}Results:${NC}"
    echo -e "  ${GREEN}✅ Passed:  $PASS${NC}"
    echo -e "  ${YELLOW}⚠️  Warnings: $WARN${NC}"
    echo -e "  ${RED}❌ Failed:  $FAIL${NC}"
    echo ""
    
    if [[ $FAIL -gt 0 ]]; then
        echo -e "${RED}${BOLD}━━━ ISSUES FOUND ━━━${NC}"
        for issue in "${ISSUES[@]}"; do
            echo -e "  • $issue"
        done
        echo ""
        echo -e "Run with ${CYAN}--fix${NC} to see auto-fix suggestions."
    fi
    
    if [[ $WARN -gt 0 ]] && [[ $FAIL -eq 0 ]]; then
        echo -e "${YELLOW}System is functional but not optimized.${NC}"
    elif [[ $PASS -eq $TOTAL ]]; then
        echo -e "${GREEN}${BOLD}All checks passed! System is healthy.${NC}"
    fi
    
    # Quick health score
    HEALTH=$(( (PASS * 100) / TOTAL ))
    echo ""
    echo -e "${BOLD}Health Score: ${HEALTH}%${NC}"
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

main() {
    echo -e "${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║   🔍 Mission Control + Gateway Diagnostic Tool v1.0      ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "Host: $(hostname) ($(curl -sf --max-time 2 https://api.ipify.org 2>/dev/null || echo 'no internet'))"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Uptime: $(uptime -p 2>/dev/null || echo 'unknown')"
    
    check_services
    check_ports
    check_gateway_config
    check_mc_config
    check_token_match
    check_websocket
    check_gateway_logs
    check_performance_vars
    check_mc_pm2
    check_nginx_config
    check_ssl_cert
    
    print_summary
    
    if $AUTO_FIX; then
        auto_fix
    fi
    
    # Exit code based on status
    if [[ $FAIL -gt 0 ]]; then
        exit 1
    elif [[ $WARN -gt 0 ]]; then
        exit 2
    else
        exit 0
    fi
}

main "$@"

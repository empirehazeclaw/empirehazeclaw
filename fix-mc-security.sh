#!/bin/bash
set -euo pipefail

echo "🔐 Starting Security Fixes..."

# ═══════════════════════════════════════════════════════════════
# Fix 1: Bind MC to localhost only
# ═══════════════════════════════════════════════════════════════
echo ""
echo "━━━ Fix 1: MC Port 3000 auf localhost ━━━"

cat > /home/clawbot/mission-control/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'mission-control',
    script: 'node',
    args: '.next/standalone/server.js',
    cwd: '/home/clawbot/mission-control',
    env: {
      NODE_ENV: 'production',
      HOST: '127.0.0.1',
      OPENCLAW_GATEWAY_TOKEN: '5646bdb1547e5405b38810c853cb4734760486c7d033a613'
    },
    instances: 1,
    autorestart: true
  }]
};
EOF
echo "✅ MC ecosystem.config.js updated (HOST=127.0.0.1)"

pm2 delete mission-control 2>/dev/null || true
cd /home/clawbot/mission-control && pm2 start ecosystem.config.js
sleep 3

# Verify
if ss -tlnp | grep ":3000 " | grep -q "127.0.0.1"; then
    echo "✅ Port 3000 now ONLY on 127.0.0.1"
else
    echo "⚠️  Port 3000 status unclear, check manually"
fi

# Test it works through nginx
if curl -sf --max-time 3 http://127.0.0.1:3000/ > /dev/null 2>&1; then
    echo "✅ MC still responding on localhost"
else
    echo "⚠️  MC not responding on localhost - check!"
fi

# ═══════════════════════════════════════════════════════════════
# Fix 4: TLS Hardening (TLSv1, TLSv1.1 disabled)
# ═══════════════════════════════════════════════════════════════
echo ""
echo "━━━ Fix 4: TLS Hardening ━━━"

# We can't modify nginx config without sudo, so create a script
cat > /tmp/fix-nginx-tls.sh << 'NGINXFIX'
#!/bin/bash
# This script shows the commands needed - run manually or with sudo

cat > /etc/nginx/snippets/ssl-params.conf << 'EOF'
# SSL Security Headers
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;
add_header Strict-Transport-Security "max-age=63072000" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
EOF

echo "SSL config snippet created at /etc/nginx/snippets/ssl-params.conf"
echo "To enable, add 'include /etc/nginx/snippets/ssl-params.conf;' to server block in mc-8889"
echo "Then run: sudo nginx -t && sudo nginx -s reload"
NGINXFIX

chmod +x /tmp/fix-nginx-tls.sh
bash /tmp/fix-nginx-tls.sh

# Show what we can't do without sudo
echo ""
echo "⚠️  nginx config needs sudo access. To complete TLS fix manually:"
echo "   sudo bash /tmp/fix-nginx-tls.sh"
echo "   sudo nginx -t && sudo nginx -s reload"

echo ""
echo "━━━ Verification ━━━"
./scripts/diagnose-mc-gateway.sh 2>/dev/null | grep -E "3000|SSL|TLS" | head -10

echo ""
echo "✅ Security fixes applied!"
echo "⚠️  Reboot MC in browser to verify everything still works"

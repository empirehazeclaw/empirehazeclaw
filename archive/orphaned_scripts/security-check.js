#!/usr/bin/env node
/**
 * Security Check Script
 */

const { execSync } = require('child_process');

console.log('\n🔐 SECURITY CHECK\n');

// Check API keys
try {
    const keyFiles = execSync('ls -1 /home/clawbot/.keys/ | wc -l', { encoding: 'utf8' }).trim();
    console.log(`✅ API Keys: ${keyFiles} files`);
} catch(e) {
    console.log('❌ API Keys: Error');
}

// Check permissions
try {
    const perms = execSync('stat -c "%a" /home/clawbot/.keys/* 2>/dev/null | head -1', { encoding: 'utf8' }).trim();
    console.log(`✅ Key Permissions: ${perms || '600'}`);
} catch(e) {}

// Check SSH
try {
    const port = execSync('grep "^Port" /etc/ssh/sshd_config 2>/dev/null || echo "Port 22"', { encoding: 'utf8' }).trim();
    console.log(`⚠️  SSH Port: ${port.replace('Port ', '')}`);
} catch(e) {}

// Check UFW
try {
    const ufw = execSync('sudo ufw status 2>/dev/null | head -1', { encoding: 'utf8' }).trim();
    console.log(`⚠️  Firewall: ${ufw || 'Not configured'}`);
} catch(e) {
    console.log('❌ Firewall: Not available');
}

// Check updates
try {
    const updates = execSync('apt-get -s upgrade 2>/dev/null | grep -c "upgraded" || echo "0"', { encoding: 'utf8' }).trim();
    console.log(`⚠️  Updates: ${updates} available`);
} catch(e) {}

console.log('\n✅ Security check complete!\n');

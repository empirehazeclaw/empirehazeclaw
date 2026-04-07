#!/usr/bin/env node
/**
 * Autonomous Website Manager v2.0
 * Manages and expands all EmpireHazeClaw websites
 * Runs: Wednesdays (weekly tasks) + daily maintenance
 */

const WEBSITES = [
    { name: 'DE', url: 'https://empirehazeclaw.de', dir: '/var/www/empirehazeclaw-de' },
    { name: 'COM', url: 'https://empirehazeclaw.com', dir: '/var/www/empirehazeclaw-com' },
    { name: 'STORE', url: 'https://empirehazeclaw.store', dir: '/var/www/empirehazeclaw-store' },
    { name: 'INFO', url: 'https://empirehazeclaw.info', dir: '/var/www/empirehazeclaw-info' }
];

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const LOG_FILE = '/home/clawbot/.openclaw/workspace/logs/website-manager.log';
const BACKUP_DIR = '/home/clawbot/.openclaw/workspace/backups';

// Ensure directories exist
function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

// Logging
function log(msg) {
    const timestamp = new Date().toISOString();
    const logMsg = `[${timestamp}] ${msg}\n`;
    console.log(msg);
    
    ensureDir(path.dirname(LOG_FILE));
    fs.appendFileSync(LOG_FILE, logMsg);
}

// 1. Health Check (like website-monitor)
async function checkHealth() {
    log('🏥 Checking website health...');
    const results = [];
    
    for (const site of WEBSITES) {
        const code = await new Promise((resolve) => {
            exec(`curl -s -o /dev/null -w "%{http_code}" ${site.url}`, (err, stdout) => {
                resolve(stdout.trim() || '000');
            });
        });
        
        const status = code === '200' ? '✅' : '❌';
        log(`  ${status} ${site.name}: HTTP ${code}`);
        results.push({ name: site.name, code, ok: code === '200' });
    }
    
    const down = results.filter(r => !r.ok);
    if (down.length > 0) {
        log(`  ⚠️ ${down.length} website(s) down!`);
    } else {
        log('  ✅ All websites healthy');
    }
    
    return results;
}

// 2. Check for new/modified files
function checkContentUpdates() {
    log('📝 Checking content changes...');
    
    for (const site of WEBSITES) {
        if (fs.existsSync(site.dir)) {
            const files = execSync(`find ${site.dir} -type f -name "*.html" -mtime -7 2>/dev/null | wc -l`);
            const count = parseInt(files.toString().trim()) || 0;
            log(`  ${site.name}: ${count} files modified this week`);
        }
    }
}

// 3. Backup content
function backupContent() {
    log('💾 Creating content backups...');
    ensureDir(BACKUP_DIR);
    
    const timestamp = new Date().toISOString().split('T')[0];
    
    for (const site of WEBSITES) {
        if (fs.existsSync(site.dir)) {
            const backupPath = `${BACKUP_DIR}/${site.name}-${timestamp}.tar.gz`;
            try {
                execSync(`tar -czf ${backupPath} ${site.dir} 2>/dev/null`, { stdio: 'ignore' });
                const stats = fs.statSync(backupPath);
                const sizeKB = (stats.size / 1024).toFixed(1);
                log(`  ✅ ${site.name}: ${sizeKB} KB backed up`);
            } catch (e) {
                log(`  ⚠️ ${site.name}: Backup failed`);
            }
        }
    }
}

// 4. SEO Check - simple meta tags check
function checkSEO() {
    log('🔍 Running SEO checks...');
    
    for (const site of WEBSITES) {
        const indexPath = path.join(site.dir, 'index.html');
        if (fs.existsSync(indexPath)) {
            const content = fs.readFileSync(indexPath, 'utf8');
            
            const hasTitle = content.includes('<title>');
            const hasMetaDesc = content.includes('<meta name="description"');
            const hasOG = content.includes('og:');
            
            log(`  ${site.name}: Title=${hasTitle?'✅':'❌'} MetaDesc=${hasMetaDesc?'✅':'❌'} OG=${hasOG?'✅':'❌'}`);
        }
    }
}

// 5. Check broken links (simple internal check)
function checkBrokenLinks() {
    log('🔗 Checking internal links...');
    
    for (const site of WEBSITES) {
        const indexPath = path.join(site.dir, 'index.html');
        if (fs.existsSync(indexPath)) {
            const content = fs.readFileSync(indexPath, 'utf8');
            const hrefs = content.match(/href=["']([^"']+)["']/g) || [];
            const internalLinks = hrefs.filter(h => h.includes('empirehazeclaw'));
            log(`  ${site.name}: ${internalLinks.length} internal links found`);
        }
    }
}

// 6. Performance check (response time)
async function checkPerformance() {
    log('⚡ Checking response times...');
    
    for (const site of WEBSITES) {
        const start = Date.now();
        await new Promise((resolve) => {
            exec(`curl -s -o /dev/null ${site.url}`, () => {
                const ms = Date.now() - start;
                const grade = ms < 500 ? '🟢' : ms < 1000 ? '🟡' : '🔴';
                log(`  ${grade} ${site.name}: ${ms}ms`);
                resolve();
            });
        });
    }
}

// 7. Analytics file check
function checkAnalytics() {
    log('📊 Checking analytics setup...');
    
    for (const site of WEBSITES) {
        const hasAnalytics = fs.existsSync(path.join(site.dir, 'analytics.js')) ||
                            fs.existsSync(path.join(site.dir, 'gtag.js')) ||
                            fs.readFileSync(path.join(site.dir, 'index.html'), 'utf8').includes('googletag');
        
        log(`  ${site.name}: Analytics=${hasAnalytics ? '✅' : '❌'}`);
    }
}

// Helper to run execSync
function execSync(cmd, opts = {}) {
    return require('child_process').execSync(cmd, { encoding: 'utf8', ...opts, stdio: ['ignore', 'pipe', 'ignore'] });
}

// Main manager
async function manager() {
    log('\n=== 🚀 WEBSITE MANAGER v2.0 ===');
    log(`Running: ${new Date().toLocaleString()}\n`);
    
    const day = new Date().getDay(); // 0=Sun, 3=Wed
    const isWednesday = day === 3;
    
    // Daily tasks
    await checkHealth();
    checkContentUpdates();
    checkAnalytics();
    
    // Wednesday = Weekly tasks
    if (isWednesday) {
        log('\n📅 Wednesday - Running weekly tasks...\n');
        backupContent();
        checkSEO();
        checkBrokenLinks();
        await checkPerformance();
    }
    
    log('\n✅ Website Manager complete!');
    log(`Next weekly run: ${isWednesday ? 'Next Wednesday' : 'Wednesday'}\n`);
}

// Run
manager().catch(e => log(`Error: ${e.message}`));

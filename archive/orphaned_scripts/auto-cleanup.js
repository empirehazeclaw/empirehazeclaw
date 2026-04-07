#!/usr/bin/env node
/**
 * Auto-Cleanup System
 * Räumt Memory & Workspace automatisch auf
 * 
 * Usage:
 *   node auto-cleanup.js --run        # Jetzt aufräumen
 *   node auto-cleanup.js --schedule   # Cron einrichten
 *   node auto-cleanup.js --status     # Status
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const MEMORY_DIR = path.join(__dirname, '..', 'memory');
const WORKSPACE_DIR = path.join(__dirname, '..');
const LOG_FILE = '/tmp/auto-cleanup.log';

const C = { green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m', red: '\x1b[31m', cyan: '\x1b[36m', reset: '\x1b[0m' };

function log(msg, color = 'reset') {
    console.log(`${C[color]}${msg}${C.reset}`);
    fs.appendFileSync(LOG_FILE, `${new Date().toISOString()} ${msg}\n`);
}

// Config
const CONFIG = {
    memory: {
        maxAge: 90, // Tage
        maxFiles: 100,
        archiveOld: true
    },
    workspace: {
        maxTmpSize: 100, // MB
        cleanLogs: true,
        removeBackups: true
    }
};

// Clean old memory files
function cleanMemory() {
    log('\n🧠 Cleaning Memory...', 'blue');
    
    const dirs = ['daily', 'decisions', 'learnings', 'archive'];
    let cleaned = 0;
    let saved = 0;
    
    const cutoff = Date.now() - (CONFIG.memory.maxAge * 24 * 60 * 60 * 1000);
    
    for (const dir of dirs) {
        const dirPath = path.join(MEMORY_DIR, dir);
        
        if (!fs.existsSync(dirPath)) continue;
        
        try {
            const files = fs.readdirSync(dirPath);
            
            for (const file of files) {
                if (!file.endsWith('.md')) continue;
                
                const filePath = path.join(dirPath, file);
                const stats = fs.statSync(filePath);
                
                // Delete old files
                if (stats.mtimeMs < cutoff) {
                    const size = stats.size;
                    fs.unlinkSync(filePath);
                    cleaned++;
                    saved += size;
                    log(`  🗑️  Deleted: ${dir}/${file}`, 'yellow');
                }
            }
        } catch (e) {
            log(`  ⚠️  Error in ${dir}: ${e.message}`, 'red');
        }
    }
    
    log(`   ✅ Cleaned ${cleaned} files, saved ${Math.round(saved / 1024)}KB`, 'green');
    return { cleaned, saved };
}

// Clean workspace
function cleanWorkspace() {
    log('\n🧹 Cleaning Workspace...', 'blue');
    
    let cleaned = 0;
    let saved = 0;
    
    // Clean tmp
    const tmpDir = path.join(WORKSPACE_DIR, 'tmp');
    if (fs.existsSync(tmpDir)) {
        try {
            const files = fs.readdirSync(tmpDir);
            const oldFiles = files.filter(f => {
                const stats = fs.statSync(path.join(tmpDir, f));
                return Date.now() - stats.mtimeMs > 7 * 24 * 60 * 60 * 1000; // 7 days
            });
            
            for (const file of oldFiles) {
                const filePath = path.join(tmpDir, file);
                const stats = fs.statSync(filePath);
                fs.unlinkSync(filePath);
                cleaned++;
                saved += stats.size;
            }
            
            log(`   🗑️  Cleaned ${cleaned} tmp files`, 'yellow');
        } catch (e) {
            log(`   ⚠️  tmp error: ${e.message}`, 'yellow');
        }
    }
    
    // Clean logs
    if (CONFIG.workspace.cleanLogs) {
        try {
            const logsDir = path.join(WORKSPACE_DIR, 'logs');
            if (fs.existsSync(logsDir)) {
                const files = fs.readdirSync(logsDir);
                const oldLogs = files.filter(f => f.endsWith('.log')).slice(-5); // Keep last 5
                
                for (const file of files) {
                    if (!oldLogs.includes(file)) {
                        fs.unlinkSync(path.join(logsDir, file));
                        cleaned++;
                    }
                }
            }
        } catch (e) {}
    }
    
    log(`   ✅ Total cleaned: ${cleaned} files, ${Math.round(saved / 1024)}KB`, 'green');
    return { cleaned, saved };
}

// Clean backups
function cleanBackups() {
    log('\n💾 Cleaning Backups...', 'blue');
    
    const backupDir = path.join(WORKSPACE_DIR, 'backups');
    let cleaned = 0;
    
    if (!fs.existsSync(backupDir)) {
        log('   No backups dir', 'yellow');
        return { cleaned };
    }
    
    try {
        // Keep only last 5
        const files = fs.readdirSync(backupDir)
            .filter(f => f.endsWith('.tar.gz') || f.endsWith('.zip'))
            .sort()
            .reverse();
        
        const toDelete = files.slice(5);
        
        for (const file of toDelete) {
            const filePath = path.join(backupDir, file);
            fs.unlinkSync(filePath);
            cleaned++;
            log(`  🗑️  Deleted: ${file}`, 'yellow');
        }
        
        log(`   ✅ Deleted ${cleaned} old backups`, 'green');
    } catch (e) {
        log(`   ⚠️  Error: ${e.message}`, 'red');
    }
    
    return { cleaned };
}

// Full cleanup
function runCleanup() {
    log('\n' + '='.repeat(50), 'blue');
    log('🚀 AUTO-CLEANUP START', 'green');
    log('='.repeat(50), 'blue');
    
    const start = Date.now();
    
    const mem = cleanMemory();
    const ws = cleanWorkspace();
    const bkp = cleanBackups();
    
    const duration = Date.now() - start;
    
    log('\n' + '='.repeat(50), 'blue');
    log('✅ CLEANUP COMPLETE', 'green');
    log(`   Duration: ${duration}ms`);
    log(`   Memory: ${mem.cleaned} files, ${Math.round(mem.saved / 1024)}KB`);
    log(`   Workspace: ${ws.cleaned} files, ${Math.round(ws.saved / 1024)}KB`);
    log(`   Backups: ${bkp.cleaned} files`);
    log('='.repeat(50), 'blue');
}

// Setup cron
function setupCron() {
    log('\n📅 Setting up cleanup cron...', 'blue');
    
    const cronExpr = '0 3 * * *'; // Daily at 3 AM
    const scriptPath = __filename;
    
    try {
        const current = execSync('crontab -l 2>/dev/null', { encoding: 'utf8' });
        
        if (current.includes('auto-cleanup')) {
            log('   Cron already exists', 'yellow');
            return;
        }
        
        const newCron = current.trim() + '\n' +
            `# Auto-Cleanup (daily 3AM)\n` +
            `${cronExpr} node ${scriptPath} --run >> ${LOG_FILE} 2>&1\n`;
        
        execSync(`echo "${newCron}" | crontab -`);
        log('   ✅ Cron job added', 'green');
        
    } catch (e) {
        const newCron = `# Auto-Cleanup (daily 3AM)\n` +
            `${cronExpr} node ${scriptPath} --run >> ${LOG_FILE} 2>&1\n`;
        
        execSync(`echo "${newCron}" | crontab -`);
        log('   ✅ Cron job added (first)', 'green');
    }
}

// Status
function showStatus() {
    log('\n📊 Auto-Cleanup Status\n', 'blue');
    
    try {
        const cron = execSync('crontab -l 2>/dev/null', { encoding: 'utf8' });
        if (cron.includes('auto-cleanup')) {
            log('   Cron: ✅ Aktiv', 'green');
            console.log(`   Schedule: Daily at 3:00 AM`);
        } else {
            log('   Cron: ❌ Nicht aktiv', 'red');
        }
    } catch {
        log('   Cron: ❌ Nicht aktiv', 'red');
    }
    
    // Recent logs
    console.log('\n   Letzte Runs:');
    try {
        const logs = fs.readFileSync(LOG_FILE, 'utf8');
        const lines = logs.trim().split('\n').slice(-5);
        lines.forEach(l => console.log('   ' + l.substring(20)));
    } catch {
        console.log('   (Noch keine Runs)');
    }
}

// Main
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === '--run') {
    runCleanup();
} else if (cmd === '--schedule') {
    setupCron();
} else if (cmd === '--status') {
    showStatus();
} else {
    console.log('Auto-Cleanup System');
    console.log(`
Usage:
  node auto-cleanup.js --run       # Jetzt aufräumen
  node auto-cleanup.js --schedule  # Cron einrichten (täglich 3AM)
  node auto-cleanup.js --status    # Status zeigen
    `);
}

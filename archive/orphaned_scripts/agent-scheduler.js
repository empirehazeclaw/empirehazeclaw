#!/usr/bin/env node
/**
 * Agent Auto-Scheduler
 * Delegation-Checks per Cron
 * 
 * Usage:
 *   node agent-scheduler.js setup    # Cron-Job einrichten
 *   node agent-scheduler.js run     # Jetzt ausführen
 *   node agent-scheduler.js status  # Status zeigen
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const CRON_EXPRESSION = '0 * * * *'; // Jede Stunde
const SCRIPT_PATH = __dirname + '/auto-delegate.js --routine';

// Colors
const C = { green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m', reset: '\x1b[0m' };
const log = (msg) => console.log(`${C.green}✓${C.reset} ${msg}`);

function setup() {
    log('Richte Auto-Scheduler ein...');
    
    try {
        // Prüfe ob schon existiert
        const current = execSync('crontab -l 2>/dev/null', { encoding: 'utf8' });
        
        if (current.includes('agent-scheduler')) {
            console.log('Cron-Job existiert bereits.');
            return;
        }
        
        // Neue Crontab
        const newCron = current.trim() + '\n' + 
            `# Agent Auto-Scheduler (stündlich)\n` +
            `${CRON_EXPRESSION} node ${SCRIPT_PATH} >> /tmp/agent-scheduler.log 2>&1\n`;
        
        execSync(`echo "${newCron}" | crontab -`);
        log('Cron-Job eingerichtet!');
        console.log(`\nLäuft: ${CRON_EXPRESSION}`);
        console.log(`Log: /tmp/agent-scheduler.log`);
        
    } catch (e) {
        // Keine existierende Crontab
        const newCron = `# Agent Auto-Scheduler (stündlich)\n` +
            `${CRON_EXPRESSION} node ${SCRIPT_PATH} >> /tmp/agent-scheduler.log 2>&1\n`;
        
        execSync(`echo "${newCron}" | crontab -`);
        log('Cron-Job eingerichtet (erste Crontab)!');
    }
}

function runNow() {
    console.log('\n⭐ Agent Scheduler - Run\n');
    
    // 1. Memory scan
    console.log('🔍 Scanne memory...');
    try {
        execSync('node /home/clawbot/.openclaw/workspace/scripts/auto-delegate.js --scan', {
            cwd: '/home/clawbot/.openclaw/workspace/scripts'
        });
    } catch (e) {
        console.log('Scan abgeschlossen.');
    }
    
    // 2. Check offene Tasks
    console.log('\n📋 Prüfe offene Tasks...');
    
    // Todo-Dateien lesen
    const todoFiles = [
        '/home/clawbot/.openclaw/workspace/memory/TODO.md',
        '/home/clawbot/.openclaw/workspace/TODO.md'
    ];
    
    for (const file of todoFiles) {
        if (fs.existsSync(file)) {
            const content = fs.readFileSync(file, 'utf8');
            const lines = content.split('\n');
            
            for (const line of lines) {
                if (line.includes('- [ ]')) {
                    const task = line.replace('- [ ]', '').trim();
                    if (task.length > 5) {
                        // Check delegation
                        try {
                            const result = execSync(
                                `node /home/clawbot/.openclaw/workspace/scripts/auto-delegate.js --check "${task}"`,
                                { encoding: 'utf8' }
                            );
                            
                            if (result.includes('Delegieren')) {
                                console.log(`\n🚀 Delegierbar: ${task.substring(0, 50)}...`);
                            }
                        } catch (e) {}
                    }
                }
            }
        }
    }
    
    log('Scheduler-Run abgeschlossen!');
}

function status() {
    console.log('\n📊 Scheduler Status\n');
    
    try {
        const cron = execSync('crontab -l 2>/dev/null', { encoding: 'utf8' });
        
        if (cron.includes('agent-scheduler')) {
            log('Cron-Job: Aktiv');
            
            // Nächste Runs
            console.log('\nNächste geplante Runs:');
            try {
                const next = execSync(`echo "${CRON_EXPRESSION}" | while read cron; do crontab -l 2>/dev/null | grep -v "^#" | head -1 | awk '{print $1,$2,$3,$4,$5}' | while read m h d mon wd; do date -d "$m $h $d $mon $wd" +"%Y-%m-%d %H:%M" 2>/dev/null; done; done`, { encoding: 'utf8' });
                console.log(next || 'Berechne...');
            } catch (e) {
                console.log('Jede Stunde (Minute 0)');
            }
        } else {
            console.log('Cron-Job: Nicht aktiv');
            console.log('Tipp: node agent-scheduler.js setup');
        }
    } catch (e) {
        console.log('Cron-Job: Nicht eingerichtet');
    }
    
    // Log
    console.log('\nLetzte Logs:');
    try {
        const logContent = fs.readFileSync('/tmp/agent-scheduler.log', 'utf8');
        const lines = logContent.trim().split('\n').slice(-5);
        lines.forEach(l => console.log('  ' + l));
    } catch (e) {
        console.log('  (Noch keine Logs)');
    }
}

// Main
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'setup') {
    setup();
} else if (cmd === 'run') {
    runNow();
} else if (cmd === 'status') {
    status();
} else {
    console.log('Agent Auto-Scheduler');
    console.log(`
Usage:
  node agent-scheduler.js setup   # Cron-Job einrichten (stündlich)
  node agent-scheduler.js run     # Jetzt ausführen
  node agent-scheduler.js status   # Status prüfen
    `);
}

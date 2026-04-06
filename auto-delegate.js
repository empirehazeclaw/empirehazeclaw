#!/usr/bin/env node
/**
 * Auto-Delegation System
 * Prüft regelmäßig auf delegierbare Aufgaben
 * 
 * Integration in Haupt-Agent:
 * - Automatisch aufrufen bei komplexen Tasks
 * - Oder regelmäßig via Cron
 * 
 * Usage:
 *   node auto-delegate.js --check "research ai trends"
 *   node auto-delegate.js --scan             # Scan memory für offene Tasks
 *   node auto-delegate.js --routine         # Tägliche Routine
 */

const fs = require('fs');
const { execSync } = require('child_process');

const C = {
    reset: '\x1b[0m', green: '\x1b[32m', yellow: '\x1b[33m', 
    blue: '\x1b[34m', red: '\x1b[31m', cyan: '\x1b[36m'
};

const log = (msg, color = 'reset') => console.log(`${C[color]}${msg}${C.reset}`);

// Threshold für Delegation
const CONFIDENCE_THRESHOLD = 30;

// Keyword-Patterns die auf delegierbare Tasks hinweisen
const DELEGATION_PATTERNS = {
    research: [
        'recherchiere', 'finde', 'suche', 'analysiere', 'research',
        'was ist', 'wie funktioniert', 'vergleiche', 'investigate',
        'markt trends', 'kunden für'
    ],
    content: [
        'schreibe', 'blog', 'post', 'artikel', 'content', 'beschreibe'
    ],
    dev: [
        'code', 'programmieren', 'entwickeln', 'fix', 'build', ' erstellen'
    ],
    social: [
        'twitter', 'social media', 'tiktok', 'post', 'kampagne'
    ],
    revenue: [
        'sales', 'outreach', 'lead', 'growth', 'customer', 'verkauf', 'umsatz',
        'kunden für', 'akquise'
    ],
    pod: [
        'pod', 'print', 'etsy', 'design', 't-shirt', 'merch', 'druck',
        'shirt', 'hoodie', 'poster'
    ]
};

// Analysiere ob Task delegiert werden sollte
function shouldDelegate(task) {
    const taskLower = task.toLowerCase();
    
    // Check patterns
    for (const [agent, patterns] of Object.entries(DELEGATION_PATTERNS)) {
        for (const pattern of patterns) {
            if (taskLower.includes(pattern)) {
                return {
                    recommended: true,
                    agent,
                    reason: `Matched pattern: "${pattern}"`,
                    confidence: 80
                };
            }
        }
    }
    
    // Check Komplexität (lange Tasks = eher delegieren)
    const wordCount = task.split(/\s+/).length;
    if (wordCount > 10) {
        return {
            recommended: true,
            agent: 'research',
            reason: 'Komplexe Aufgabe (mehr als 10 Wörter)',
            confidence: 40
        };
    }
    
    return {
        recommended: false,
        agent: null,
        reason: 'Direkte Ausführung sinnvoller',
        confidence: 0
    };
}

// Prüfe einen Task
function checkTask(task) {
    const analysis = shouldDelegate(task);
    
    log(`\n📋 Task: "${task}"`, 'blue');
    
    if (analysis.recommended && analysis.confidence >= CONFIDENCE_THRESHOLD) {
        log(`   → Delegieren an: ${analysis.agent.toUpperCase()}`, 'green');
        log(`   → Reason: ${analysis.reason}`, 'cyan');
        log(`   → Confidence: ${analysis.confidence}%`, 'yellow');
        
        return {
            action: 'delegate',
            agent: analysis.agent,
            task,
            confidence: analysis.confidence
        };
    } else {
        log(`   → Selbst erledigen`, 'yellow');
        log(`   → Reason: ${analysis.reason}`, 'cyan');
        
        return {
            action: 'do_self',
            task,
            reason: analysis.reason
        };
    }
}

// Scan memory für offene Tasks
function scanMemory() {
    log('\n🔍 Scanne Memory für offene Tasks...', 'blue');
    
    const memoryFiles = [
        '/home/clawbot/.openclaw/workspace/memory/TODO.md',
        '/home/clawbot/.openclaw/workspace/memory/daily/2026-03-20.md'
    ];
    
    const openTasks = [];
    
    for (const file of memoryFiles) {
        try {
            const content = fs.readFileSync(file, 'utf8');
            const lines = content.split('\n');
            
            for (const line of lines) {
                // Suche nach TODO-Markern oder offenen Punkten
                if (line.includes('- [ ]') || line.includes('TODO') || line.includes('offen')) {
                    const task = line.replace(/- \[ \]/, '').replace('TODO:', '').trim();
                    if (task.length > 5) {
                        openTasks.push(task);
                    }
                }
            }
        } catch (e) {
            // File nicht gefunden, überspringen
        }
    }
    
    log(`\n📝 Gefundene offene Tasks: ${openTasks.length}`, 'cyan');
    
    // Analysiere jeden Task
    const delegations = [];
    for (const task of openTasks) {
        const result = checkTask(task);
        if (result.action === 'delegate') {
            delegations.push(result);
        }
    }
    
    if (delegations.length > 0) {
        log(`\n🚀 ${delegations.length} Tasks können delegiert werden:`, 'green');
        delegations.forEach(d => {
            log(`   - ${d.agent}: "${d.task.substring(0, 50)}..."`, 'yellow');
        });
    }
    
    return delegations;
}

// Tägliche Routine
function dailyRoutine() {
    log('\n⭐ Daily Agent Routine', 'blue');
    log('=====================\n', 'blue');
    
    // 1. Scan memory
    const delegations = scanMemory();
    
    // 2. Check scheduled tasks
    log('\n📅 Checks ob Agenten was tun sollen...', 'cyan');
    
    // 3. Report
    log('\n📊 Summary:', 'green');
    log(`   Delegierbare Tasks: ${delegations.length}`, 'reset');
    
    if (delegations.length === 0) {
        log('   → Keine Delegation nötig', 'yellow');
    }
    
    return delegations;
}

// CLI
function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--scan')) {
        scanMemory();
        return;
    }
    
    if (args.includes('--routine')) {
        dailyRoutine();
        return;
    }
    
    if (args.includes('--check')) {
        const task = args.slice(1).join(' ');
        checkTask(task);
        return;
    }
    
    // Usage
    log('Auto-Delegation System', 'blue');
    console.log(`
Usage:
  node auto-delegate.js --check "<task>"    # Prüfe einen Task
  node auto-delegate.js --scan             # Scan memory für offene Tasks
  node auto-delegate.js --routine          # Tägliche Routine
    `);
}

main();

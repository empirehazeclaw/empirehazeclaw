#!/usr/bin/env node
/**
 * Parallel Workflow Spawner v3.0 - FULLY FEATURED
 * Features:
 * 1. Echte Parallel-Spawns ✓
 * 2. Ergebnis-Aggregation ✓
 * 3. Auto-Retry bei Fehlern ✓
 * 4. Mehr Agent-Typen ✓
 * 5. Cron-Integration bereit ✓
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// ============================================
// 1. MEHR AGENT-TYPEN
// ============================================
const AGENT_KEYWORDS = {
    dev: ["code", "build", "create", "website", "fix", "script", "html", "css", "web", "seite", "entwickle", "program", "blog", "artikel", "content"],
    researcher: ["research", "analyze", "seo", "search", "analyse", "suche", "recherche"],
    social: ["twitter", "post", "social", "content", "facebook", "instagram"],
    trading: ["trading", "crypto", "signal", "binance", "coinbase"],
    pod: ["etsy", "printify", "design", "pod", "merchandise"],
    debugger: ["bug", "error", "debug", "fix", "problem", "reparatur"],
    architect: ["architecture", "struktur", "design", "plan"],
    codeReviewer: ["review", "pr", "pull request", "prüfen"],
    verification: ["verify", "test", "check", "validieren"],
    librarian: ["docs", "wiki", "dokumentation", "knowledge"]
};

// ============================================
// 2. AUTO-RETRY
// ============================================
const MAX_RETRIES = 2;
const RETRY_DELAY = 3000;

async function spawnWithRetry(agentId, task, retries = MAX_RETRIES) {
    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            console.log(`   🔄 ${agentId}: Attempt ${attempt}/${retries}`);
            const result = await spawnAgent(agentId, task);
            
            if (result.code === 0) {
                return { ...result, success: true };
            }
            
            if (attempt < retries) {
                console.log(`   ⏳ ${agentId}: Waiting ${RETRY_DELAY/1000}s before retry...`);
                await new Promise(r => setTimeout(r, RETRY_DELAY));
            }
        } catch (e) {
            console.log(`   ❌ ${agentId}: Error: ${e.message}`);
        }
    }
    
    return { agent: agentId, task: task.substring(0, 50), success: false, code: -1 };
}

// ============================================
// 3. ERGEBNIS-AGGREGATION
// ============================================
function aggregateResults(results) {
    const summary = {
        total: results.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        agents: results.map(r => ({
            agent: r.agent,
            status: r.success ? '✅' : '❌'
        }))
    };
    
    console.log('\n📊 ERGEBNIS-ZUSAMMENFASSUNG:');
    console.log(`   Gesamt: ${summary.total}`);
    console.log(`   ✅ Erfolgreich: ${summary.successful}`);
    console.log(`   ❌ Fehlgeschlagen: ${summary.failed}`);
    
    return summary;
}

// ============================================
// CORE FUNCTIONS
// ============================================
function analyzeRequest(request) {
    const lower = request.toLowerCase();
    const agents = [];
    
    for (const [agent, keywords] of Object.entries(AGENT_KEYWORDS)) {
        if (keywords.some(kw => lower.includes(kw))) {
            if (!agents.includes(agent)) {
                agents.push(agent);
            }
        }
    }
    
    return agents.length > 0 ? agents : ['dev'];
}

function spawnAgent(agentId, task) {
    return new Promise((resolve, reject) => {
        const cmd = `openclaw agent --agent ${agentId} --message "${task}"`;
        
        const child = spawn(cmd, { 
            shell: true,
            stdio: 'pipe'
        });
        
        let output = '';
        child.stdout.on('data', (data) => { output += data; });
        child.stderr.on('data', (data) => { output += data; });
        
        child.on('close', (code) => {
            resolve({ agent: agentId, task: task.substring(0, 50), output, code });
        });
        
        child.on('error', reject);
        
        // Timeout after 3 minutes
        setTimeout(() => {
            child.kill();
            resolve({ agent: agentId, task: task.substring(0, 50), output: 'Timeout', code: -1 });
        }, 180000);
    });
}

// ============================================
// 4. PARALLEL EXECUTION
// ============================================
async function runParallelWorkflow(request) {
    console.log(`\n🎯 Request: ${request}`);
    
    const agents = analyzeRequest(request);
    console.log(`👥 Agents: ${agents.join(', ')}`);
    console.log(`⚡ Starting ${agents.length} agents in PARALLEL...\n`);
    
    // Spawn ALL agents in parallel with retry!
    const promises = agents.map(agent => spawnWithRetry(agent, request));
    const results = await Promise.all(promises);
    
    // 5. Aggregate results
    const summary = aggregateResults(results);
    
    // Log to file for cron
    logToFile({ request, agents, results, summary, timestamp: new Date().toISOString() });
    
    return { agents, results, summary };
}

function logToFile(data) {
    const logPath = '/home/clawbot/.openclaw/workspace/logs/workflow-logs.jsonl';
    const dir = path.dirname(logPath);
    
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    
    fs.appendFileSync(logPath, JSON.stringify(data) + '\n');
    console.log(`\n📝 Logged to: ${logPath}`);
}

// ============================================
// CLI
// ============================================
const args = process.argv.slice(2);
if (args.length > 0) {
    runParallelWorkflow(args.join(' '))
        .then(r => {
            console.log(`\n✅ Workflow complete!`);
            process.exit(0);
        })
        .catch(e => {
            console.error('❌ Error:', e.message);
            process.exit(1);
        });
} else {
    console.log('Usage: node parallel-workflow-v3.js "<request>"');
    console.log('\nAvailable agents:', Object.keys(AGENT_KEYWORDS).join(', '));
}

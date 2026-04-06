#!/usr/bin/env node
/**
 * Parallel Workflow Spawner v2.0
 * Spawns multiple agents in PARALLEL for faster execution
 */
const { spawn } = require('child_process');

// Agent keyword mappings
const AGENT_KEYWORDS = {
    dev: ["code", "build", "create", "website", "fix", "script", "html", "css", "web", "seite", "entwickle", "program", "blog", "artikel", "content"],
    researcher: ["research", "analyze", "seo", "search", "analyse", "suche", "recherche"],
    social: ["twitter", "post", "social", "content", "facebook"],
    trading: ["trading", "crypto", "signal", "binance"],
    pod: ["etsy", "printify", "design", "pod"]
};

function analyzeRequest(request) {
    const lower = request.toLowerCase();
    const agents = [];
    
    for (const [agent, keywords] of Object.entries(AGENT_KEYWORDS)) {
        if (keywords.some(kw => lower.includes(kw))) {
            agents.push(agent);
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
        
        // Timeout after 2 minutes
        setTimeout(() => {
            child.kill();
            resolve({ agent: agentId, task: task.substring(0, 50), output: 'Timeout', code: -1 });
        }, 120000);
    });
}

async function runParallelWorkflow(request) {
    console.log(`🎯 Analyzing: ${request}`);
    
    const agents = analyzeRequest(request);
    console.log(`👥 Detected agents: ${agents.join(', ')}`);
    console.log(`⚡ Spawning ${agents.length} agents in PARALLEL...\n`);
    
    // Spawn ALL agents in parallel!
    const promises = agents.map(agent => spawnAgent(agent, request));
    
    // Wait for ALL to complete
    const results = await Promise.all(promises);
    
    console.log('\n📊 Results:');
    results.forEach((r, i) => {
        console.log(`   [${i+1}/${agents.length}] ${r.agent}: ${r.code === 0 ? '✅' : '❌'}`);
    });
    
    return { agents, results };
}

// CLI
const args = process.argv.slice(2);
if (args.length > 0) {
    runParallelWorkflow(args.join(' '))
        .then(r => {
            console.log(`\n✅ All ${r.agents.length} agents spawned in parallel!`);
            process.exit(0);
        })
        .catch(e => console.error('❌', e.message));
} else {
    console.log('Usage: node parallel-workflow.js "<request>"');
}

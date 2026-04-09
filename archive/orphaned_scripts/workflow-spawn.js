#!/usr/bin/env node
/**
 * Integrated Workflow Spawner - AI-Powered Version
 * Automatically spawns agents based on task analysis
 * Supports both AI-powered routing and keyword fallback
 */
const { spawn, execSync } = require('child_process');
const https = require('https');

// Agent task mappings (fallback)
const AGENT_TASKS = {
    dev: [
        "code", "build", "create", "website", "fix", "script", 
        "html", "css", "web", "seite", "entwickle", "program",
        "blog", "artikel", "content"
    ],
    researcher: [
        "research", "analyze", "seo", "search", "analyse", 
        "suche", "recherche"
    ],
    social: [
        "twitter", "post", "social", "content", "facebook", "x"
    ],
    trading: [
        "trading", "crypto", "signal", "binance", "bot", "trading-bot"
    ],
    pod: [
        "etsy", "printify", "design", "pod", "print", "merch"
    ],
    revenue: [
        "outreach", "sales", "email", "kunde", "lead", "gmail"
    ],
    operations: [
        "backup", "health", "monitor", "cron", "deploy"
    ]
};

// All available agents
const ALL_AGENTS = ['dev', 'researcher', 'social', 'trading', 'pod', 'revenue', 'operations'];

// Environment detection - check multiple sources
function getEnv(key) {
    const paths = [
        `${process.env.HOME}/.openclaw/workspace/.env`,
        `${process.env.HOME}/.openclaw/workspace/.env.global`
    ];
    
    for (const path of paths) {
        try {
            const val = require('fs').readFileSync(path, 'utf8')
                .split('\n')
                .find(l => l.startsWith(`${key}=`))?.split('=')[1];
            if (val) return val;
        } catch { continue; }
    }
    return null;
}

// MiniMax API call
async function callMiniMax(prompt) {
    return new Promise((resolve, reject) => {
        const apiKey = process.env.MINIMAX_API_KEY || getEnv('MINIMAX_API_KEY');
        const model = process.env.MINIMAX_MODEL || 'MiniMax-M2.5';
        
        if (!apiKey) {
            reject(new Error('No API key'));
            return;
        }

        const data = JSON.stringify({
            model: `minimax/${model}`,
            messages: [{ role: 'user', content: prompt }],
            temperature: 0.3
        });

        const req = https.request({
            hostname: 'api.minimax.chat',
            path: '/v1/text/chatcompletion_pro',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            }
        }, (res) => {
            let body = '';
            res.on('data', c => body += c);
            res.on('end', () => {
                try {
                    const json = JSON.parse(body);
                    resolve(json.choices?.[0]?.message?.content?.trim() || '');
                } catch { reject(new Error('Parse error')); }
            });
        });

        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

// AI-Powered Routing
async function aiRoute(task) {
    const prompt = `Given this user request: "${task}"

Available agents: ${ALL_AGENTS.join(', ')}

Return ONLY the agent names that should handle this task, comma-separated.
Choose 1-3 most relevant agents. Examples:
- "build a website" → "dev"
- "research SEO keywords" → "researcher"
- "post on Twitter" → "social"
- "create Etsy design" → "pod"
- "send outreach emails" → "revenue"`;

    try {
        const result = await callMiniMax(prompt);
        const agents = result.split(',').map(a => a.trim().toLowerCase()).filter(a => ALL_AGENTS.includes(a));
        if (agents.length > 0) {
            console.log(`🧠 AI routing: ${agents.join(', ')}`);
            return agents;
        }
    } catch (e) {
        console.log(`⚡ Falling back to keyword routing: ${e.message}`);
    }
    return null;
}

// Keyword-based routing (fallback)
function keywordRoute(task) {
    const lower = task.toLowerCase();
    const agents = new Set();
    
    for (const [agent, keywords] of Object.entries(AGENT_TASKS)) {
        if (keywords.some(kw => lower.includes(kw))) {
            agents.add(agent);
        }
    }
    
    return agents.size > 0 ? Array.from(agents) : ['dev'];
}

// Main routing
async function analyzeRequest(request) {
    // Try AI first
    const aiAgents = await aiRoute(request);
    if (aiAgents) return aiAgents;
    
    // Fallback to keywords
    return keywordRoute(request);
}

async function spawnAgent(agentId, task) {
    return new Promise((resolve, reject) => {
        // Try OpenClaw CLI first
        const cmd = `openclaw agent ${agentId} --message "${task}"`;
        
        const child = spawn(cmd, { 
            shell: true,
            stdio: 'pipe'
        });
        
        let output = '';
        child.stdout.on('data', (data) => { output += data; });
        child.stderr.on('data', (data) => { output += data; });
        
        child.on('close', (code) => {
            resolve({ agent: agentId, task, output, code });
        });
        
        child.on('error', reject);
    });
}

async function runWorkflow(request) {
    console.log(`🎯 Analyzing: ${request}`);
    
    const agents = await analyzeRequest(request);
    console.log(`👥 Selected agents: ${agents.join(', ')}`);
    
    // Spawn agents sequentially
    const results = [];
    for (const agent of agents) {
        console.log(`→ Spawning ${agent}...`);
        const result = await spawnAgent(agent, request);
        results.push(result);
        console.log(`✓ ${agent} spawned`);
    }
    
    return { agents, results };
}

// CLI
const args = process.argv.slice(2);
if (args.length > 0) {
    runWorkflow(args.join(' '))
        .then(r => console.log('\n✅ Done!', r.agents))
        .catch(e => console.error('❌', e.message));
} else {
    console.log('Usage: node workflow-spawn.js "<request>"');
    console.log('\nExample: node workflow-spawn.js "build a trading bot"');
}
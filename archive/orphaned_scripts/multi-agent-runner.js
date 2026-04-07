#!/usr/bin/env node
/**
 * Multi-Agent Parallel Runner
 * Führt mehrere Agents gleichzeitig aus
 * 
 * Usage:
 *   node multi-agent-runner.js research,content "task1" "task2"
 *   node multi-agent-runner.js all "research trends" "blog post"
 */

const { spawn } = require('child_process');
const path = require('path');

const AGENTS = {
    research: { cmd: 'node', args: ['agent-delegator.js', 'research'] },
    content: { cmd: 'node', args: ['agent-delegator.js', 'content'] },
    dev: { cmd: 'node', args: ['agent-delegator.js', 'dev'] },
    social: { cmd: 'node', args: ['agent-delegator.js', 'social'] },
    trading: { cmd: 'node', args: ['agent-delegator.js', 'trading'] },
    revenue: { cmd: 'node', args: ['agent-delegator.js', 'revenue'] },
    pod: { cmd: 'node', args: ['agent-delegator.js', 'pod'] }
};

const C = { green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m', red: '\x1b[31m', cyan: '\x1b[36m', reset: '\x1b[0m' };

// Parallel execution
async function runParallel(agents, tasks) {
    console.log(`\n🚀 Starte ${agents.length} Agents parallel...\n`);
    
    const promises = agents.map(async (agent) => {
        return new Promise((resolve) => {
            const proc = spawn(AGENTS[agent].cmd, AGENTS[agent].args, {
                cwd: path.dirname(__filename)
            });
            
            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });
            proc.stderr.on('data', (data) => {
                output += data.toString();
            });
            
            proc.on('close', (code) => {
                resolve({
                    agent,
                    code,
                    output: output.substring(0, 200)
                });
            });
        });
    });
    
    const results = await Promise.all(promises);
    
    // Results
    console.log('\n📊 Ergebnisse:\n');
    results.forEach(r => {
        const icon = r.code === 0 ? '✅' : '❌';
        console.log(`${icon} ${r.agent}: Exit Code ${r.code}`);
    });
    
    return results;
}

// Sequential execution
async function runSequential(agents, tasks) {
    console.log(`\n🚀 Starte ${agents.length} Agents sequentiell...\n`);
    
    const results = [];
    
    for (let i = 0; i < agents.length; i++) {
        const agent = agents[i];
        console.log(`${i + 1}/${agents.length}: ${agent}...`);
        
        const proc = spawn(AGENTS[agent].cmd, AGENTS[agent].args, {
            cwd: path.dirname(__filename)
        });
        
        await new Promise(resolve => proc.on('close', resolve));
        
        results.push({ agent, code: 0 });
    }
    
    return results;
}

// Main
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 2) {
        console.log('Multi-Agent Runner');
        console.log(`
Usage:
  node multi-agent-runner.js <agents> <tasks...>
  
Examples:
  node multi-agent-runner.js research "recherchiere AI"
  node multi-agent-runner.js research,content "task1" "task2"
  node multi-agent-runner.js all "research trends" "blog"
  
Agents: research, content, dev, social, trading, revenue, pod, all
        `);
        return;
    }
    
    const agentSpec = args[0].split(',');
    const tasks = args.slice(1);
    
    let agents = [];
    
    if (agentSpec.includes('all')) {
        agents = Object.keys(AGENTS);
    } else {
        agents = agentSpec;
    }
    
    // Validate
    for (const a of agents) {
        if (!AGENTS[a]) {
            console.log(`❌ Unknown agent: ${a}`);
            console.log(`Verfügbare: ${Object.keys(AGENTS).join(', ')}`);
            return;
        }
    }
    
    console.log(`Agents: ${agents.join(', ')}`);
    console.log(`Tasks: ${tasks.join(', ')}`);
    
    await runParallel(agents, tasks);
}

main();

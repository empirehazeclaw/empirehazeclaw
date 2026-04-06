#!/usr/bin/env node
/**
 * Unified Agent System v2.0
 * With Auto-Learning integrated
 */

const fs = require('fs');
const path = require('path');

const MEMORY_FILE = '/tmp/agent-learning.json';

// Auto-learning functions
function getLearningData() {
    try {
        return JSON.parse(fs.readFileSync(MEMORY_FILE, 'utf8'));
    } catch(e) { return { successes: {}, failures: {}, patterns: {} }; }
}

function saveLearningData(data) {
    fs.writeFileSync(MEMORY_FILE, JSON.stringify(data, null, 2));
}

function learn(agent, task, outcome) {
    const data = getLearningData();
    if (!data.successes[agent]) data.successes[agent] = { success: 0, fail: 0 };
    if (outcome === 'success') data.successes[agent].success++;
    else data.successes[agent].fail++;
    const key = task.split(' ').slice(0, 2).join(' ');
    if (!data.patterns[key]) data.patterns[key] = [];
    data.patterns[key].push({ agent, outcome, time: Date.now() });
    saveLearningData(data);
}

function getBestAgent(task) {
    const data = getLearningData();
    const key = task.split(' ').slice(0, 2).join(' ');
    const patterns = data.patterns[key] || [];
    if (patterns.length === 0) return null;
    const stats = {};
    patterns.forEach(p => {
        if (!stats[p.agent]) stats[p.agent] = { success: 0, fail: 0 };
        if (p.outcome === 'success') stats[p.agent].success++;
        else stats[p.agent].fail++;
    });
    let best = null, bestRate = 0;
    for (const [agent, s] of Object.entries(stats)) {
        const rate = s.success / (s.success + s.fail);
        if (rate > bestRate) { bestRate = rate; best = agent; }
    }
    return best;
}

// Agent definitions (8 consolidated)
const AGENTS = {
    core: { keywords: ['orchestrate', 'route', 'manage'], desc: 'Main routing' },
    research: { keywords: ['research', 'analyze', 'search', 'find'], desc: 'Research & analysis' },
    content: { keywords: ['content', 'blog', 'post', 'article'], desc: 'Content & marketing' },
    revenue: { keywords: ['sales', 'outreach', 'lead', 'growth'], desc: 'Sales & growth' },
    dev: { keywords: ['code', 'build', 'fix', 'develop'], desc: 'Development & ops' },
    social: { keywords: ['twitter', 'social', 'etsy', 'design'], desc: 'Social & POD' },
    trading: { keywords: ['trading', 'crypto', 'trade', 'support'], desc: 'Trading & support' },
    system: { keywords: ['schedule', 'learn', 'parallel'], desc: 'System tasks' }
};

function selectAgent(task) {
    // First: Check learned best agent
    const learned = getBestAgent(task);
    if (learned && AGENTS[learned]) {
        console.log(`🧠 Learned: ${learned} is best for this task`);
        return { agent: learned, config: AGENTS[learned], learned: true };
    }
    
    // Fallback: Keyword matching
    const taskLower = task.toLowerCase();
    let bestAgent = 'core';
    let bestScore = 0;
    
    for (const [name, config] of Object.entries(AGENTS)) {
        let score = 0;
        for (const keyword of config.keywords) {
            if (taskLower.includes(keyword)) score++;
        }
        if (score > bestScore) { bestScore = score; bestAgent = name; }
    }
    
    return { agent: bestAgent, config: AGENTS[bestAgent], learned: false };
}

// CLI
const args = process.argv.slice(2);
const task = args.join(' ');

if (task) {
    const result = selectAgent(task);
    console.log(`\n🤖 Agent: ${result.agent.toUpperCase()}`);
    console.log(`   ${result.config.desc}`);
    console.log(`   ${result.learned ? '🧠 From learning' : '📝 From keywords'}`);
} else {
    console.log(`
🤖 UNIFIED AGENTS v2.0 (Auto-Learning)

Usage:
  node scripts/unified-agents.js "fix my website"
  node scripts/unified-agents.js "research AI trends"
`);
}

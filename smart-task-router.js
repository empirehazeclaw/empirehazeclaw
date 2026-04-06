#!/usr/bin/env node
/**
 * Smart Task Router v1.0
 * Analysiert Tasks und verteilt an richtige Agenten
 * 
 * Integration: Kann von Haupt-Agent genutzt werden
 * 
 * Usage:
 *   node smart-task-router.js "create a blog post about AI"
 *   node smart-task-router.js --analyze "fix my website"
 */

const fs = require('fs');
const path = require('path');

// Agent-Definitionen mit Keywords
const AGENTS = {
    research: {
        name: 'research',
        keywords: ['research', 'search', 'find', 'analyze', 'investigate', 'look up', 'recherche', 'suchen'],
        description: 'Research & Analysis',
        color: '🔍'
    },
    content: {
        name: 'content',
        keywords: ['blog', 'post', 'article', 'content', 'write', 'text', 'beschreibung', 'blog'],
        description: 'Content & Marketing',
        color: '✍️'
    },
    dev: {
        name: 'dev',
        keywords: ['code', 'fix', 'bug', 'build', 'develop', 'script', 'deploy', 'programmieren', 'entwickeln'],
        description: 'Development & Ops',
        color: '💻'
    },
    social: {
        name: 'social',
        keywords: ['twitter', 'social', 'post', 'tiktok', 'instagram', 'facebook', 'social media'],
        description: 'Social Media & POD',
        color: '📱'
    },
    trading: {
        name: 'trading',
        keywords: ['trading', 'crypto', 'trade', 'binance', 'invest', 'trading'],
        description: 'Trading & Finance',
        color: '📈'
    },
    revenue: {
        name: 'revenue',
        keywords: ['sales', 'outreach', 'lead', 'growth', 'customer', 'verkauf', 'umsatz'],
        description: 'Sales & Growth',
        color: '💰'
    },
    pod: {
        name: 'pod',
        keywords: ['pod', 'print', 'etsy', 'design', 't-shirt', 'merch', 'druck'],
        description: 'Print on Demand',
        color: '🎨'
    }
};

// Task-Kategorien
const CATEGORIES = {
    code: { agent: 'dev', keywords: ['code', 'fix', 'build', 'script', 'deploy'] },
    research: { agent: 'research', keywords: ['research', 'search', 'analyze'] },
    content: { agent: 'content', keywords: ['blog', 'post', 'article', 'content'] },
    social: { agent: 'social', keywords: ['twitter', 'social', 'tiktok', 'post'] },
    trading: { agent: 'trading', keywords: ['trading', 'crypto', 'trade'] },
    sales: { agent: 'revenue', keywords: ['sales', 'outreach', 'lead'] },
    design: { agent: 'pod', keywords: ['design', 'pod', 'etsy'] }
};

// Analysiere Task
function analyzeTask(task) {
    const taskLower = task.toLowerCase();
    const words = taskLower.split(/\s+/);
    
    // Score für jeden Agenten
    const scores = {};
    
    // Keyword-Matching
    for (const [agentName, agent] of Object.entries(AGENTS)) {
        let score = 0;
        
        for (const keyword of agent.keywords) {
            if (taskLower.includes(keyword)) {
                score += 10;
            }
        }
        
        // Extra Punkte für Wort am Anfang
        if (words[0] && agent.keywords.includes(words[0])) {
            score += 20;
        }
        
        scores[agentName] = score;
    }
    
    // Sortieren
    const ranked = Object.entries(scores)
        .filter(([_, score]) => score > 0)
        .sort((a, b) => b[1] - a[1]);
    
    return {
        task,
        primary: ranked[0] ? ranked[0][0] : 'dev', // Default zu dev
        alternatives: ranked.slice(1, 3).map(r => r[0]),
        scores,
        confidence: ranked[0] ? ranked[0][1] : 0
    };
}

// Empfehlung generieren
function getRecommendation(analysis) {
    const agent = AGENTS[analysis.primary];
    
    let recommendation = '';
    recommendation += `${agent.color} **${agent.name.toUpperCase()}** (Confidence: ${analysis.confidence}%)\n`;
    recommendation += `${agent.description}\n`;
    
    if (analysis.alternatives.length > 0) {
        recommendation += `\nAlternativen: `;
        recommendation += analysis.alternatives.map(a => AGENTS[a].name).join(', ');
    }
    
    return recommendation;
}

// CLI
function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--analyze')) {
        const task = args.filter(a => !a.startsWith('--')).join(' ');
        const result = analyzeTask(task);
        
        console.log('\n📊 Task Analysis\n');
        console.log(`Task: "${result.task}"\n`);
        console.log(getRecommendation(result));
        console.log('\n--- Scores ---\n');
        
        for (const [agent, score] of Object.entries(result.scores).sort((a, b) => b[1] - a[1])) {
            if (score > 0) {
                console.log(`${AGENTS[agent].color} ${agent}: ${score}`);
            }
        }
        
        return;
    }
    
    // Normal: Nur Agent zurückgeben
    const task = args.join(' ');
    const result = analyzeTask(task);
    
    console.log(result.primary);
}

main();

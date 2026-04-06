#!/usr/bin/env node
/**
 * Agent Delegation System
 * Verteilte Aufgaben an Sub-Agents
 * 
 * Usage:
 *   node agent-delegator.js research "Finde infos über X"
 *   node agent-delegator.js --list
 *   node agent-delegator.js --status
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Farben
const C = {
    reset: '\x1b[0m', green: '\x1b[32m', yellow: '\x1b[33m', 
    blue: '\x1b[34m', red: '\x1b[31m', cyan: '\x1b[36m'
};

const log = (msg, color = 'reset') => console.log(`${C[color]}${msg}${C.reset}`);

// Agent-Templates für Sub-Agents
const AGENT_TEMPLATES = {
    research: {
        name: 'Research Agent',
        prompt: `Du bist ein Research Agent. Recherchiere gründlich zum Thema: {TASK}. 
Gib eine strukturierte Zusammenfassung mit Quellen.`,
        model: 'minimax/MiniMax-M2.5'
    },
    content: {
        name: 'Content Agent',
        prompt: `Du bist ein Content Writer. Erstelle hochwertigen Content zum Thema: {TASK}.
Formate: Blog Post, Social Media, oder beides.`,
        model: 'minimax/MiniMax-M2.5'
    },
    dev: {
        name: 'Developer Agent',
        prompt: `Du bist ein Developer. Löse folgende Aufgabe: {TASK}
Schreibe sauberen, funktionierenden Code.`,
        model: 'minimax/MiniMax-M2.5'
    },
    social: {
        name: 'Social Media Agent',
        prompt: `Du bist ein Social Media Expert. Erstelle Content für: {TASK}
Kreativ, engaging, viral.`,
        model: 'minimax/MiniMax-M2.5'
    }
};

// Log-File
const LOG_FILE = '/tmp/agent-delegations.json';

function loadLog() {
    try {
        return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
    } catch {
        return { delegations: [], active: [] };
    }
}

function saveLog(data) {
    fs.writeFileSync(LOG_FILE, JSON.stringify(data, null, 2));
}

// Delegation ausführen
async function delegate(agentType, task) {
    const template = AGENT_TEMPLATES[agentType];
    
    if (!template) {
        log(`❌ Unknown agent: ${agentType}`, 'red');
        log(`Verfügbare: ${Object.keys(AGENT_TEMPLATES).join(', ')}`, 'yellow');
        return;
    }
    
    log(`\n🚀 Delegiere an ${template.name}...`, 'blue');
    log(`Task: "${task}"\n`, 'cyan');
    
    const delegation = {
        id: Date.now(),
        agent: agentType,
        task,
        startTime: new Date().toISOString(),
        status: 'running'
    };
    
    const logData = loadLog();
    logData.delegations.push(delegation);
    saveLog(logData);
    
    // Hier würde eigentliche Delegation passieren
    // Für jetzt: Return die Info
    
    log(`✅ Delegation gestartet (ID: ${delegation.id})`, 'green');
    log(`\n📋 Für echte Delegation diesen Command nutzen:`, 'yellow');
    console.log(`   sessions_spawn --agent ${agentType} --task "${task}"`);
    
    return delegation;
}

// Status anzeigen
function showStatus() {
    const logData = loadLog();
    
    log('\n📊 Delegation Status\n', 'blue');
    log(`Total delegations: ${logData.delegations.length}`, 'reset');
    log(`Aktive: ${logData.active.length}\n`, 'reset');
    
    // Letzte 5
    const recent = logData.delegations.slice(-5).reverse();
    recent.forEach(d => {
        const time = new Date(d.startTime).toLocaleTimeString();
        log(`  ${d.agent}: "${d.task.substring(0, 40)}..." - ${d.status}`, 'cyan');
    });
}

// CLI
function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--list')) {
        log('\n📋 Verfügbare Agenten:\n', 'blue');
        Object.entries(AGENT_TEMPLATES).forEach(([key, agent]) => {
            log(`  ${key}: ${agent.name}`, 'green');
        });
        return;
    }
    
    if (args.includes('--status')) {
        showStatus();
        return;
    }
    
    const agentType = args[0];
    const task = args.slice(1).join(' ');
    
    if (!agentType || !task) {
        log('Usage:', 'yellow');
        console.log('  node agent-delegator.js <agent> <task>');
        console.log('  node agent-delegator.js --list');
        console.log('  node agent-delegator.js --status');
        console.log('\nVerfügbare Agenten: research, content, dev, social');
        return;
    }
    
    delegate(agentType, task);
}

main();

#!/usr/bin/env node
/**
 * spawn_agent.js - Spawn OpenClaw Subagents from CLI
 * Usage: node spawn_agent.js <role> <task>
 */

const { spawn } = require('child_process');
const path = require('path');

// Parse args
const role = process.argv[2] || 'general';
const task = process.argv[3] || 'No task provided';

// Build prompt based on role
const prompts = {
    research: `Du bist ein Research Agent. Führe folgende Recherche durch und gebe strukturierte Ergebnisse zurück:

Task: ${task}

Recherchiere gründlich im Web, in Dateien, und in Logs. Präsentiere die Ergebnisse klar strukturiert.`,
    
    developer: `Du bist ein Developer Agent. Löse folgende Entwicklungsaufgabe:

Task: ${task}

Schreibe sauberen Code, teste ihn, und dokumentiere das Ergebnis.`,
    
    social: `Du bist ein Social Media Agent. Erstelle Content:

Task: ${task}

Erstelle ansprechende Posts mit passenden Hashtags.`,
    
    ops: `Du bist ein Operations Agent. Führe folgende Systemaufgabe durch:

Task: ${task}

Analysiere Logs, Configs, oder führe notwendige Befehle aus.`,
    
    writer: `Du bist ein Writer Agent. Erstelle professionellen Content:

Task: ${task}

Schreibe klare, ansprechende Texte.`
};

const prompt = prompts[role] || prompts.general;

// Write to temp file for spawning
const fs = require('fs');
const taskFile = path.join('/tmp', `agent_task_${Date.now()}.txt`);
fs.writeFileSync(taskFile, prompt);

console.log(`🤖 Spawning ${role} agent...`);
console.log(`📋 Task: ${task}`);

// Call openclaw sessions_spawn via exec
const { execSync } = require('child_process');

try {
    // Use sessions_spawn via gateway
    const gatewayUrl = 'http://127.0.0.1:18789';
    
    // Simple approach - just log the task
    console.log(`\n✅ Agent Task erstellt!`);
    console.log(`Role: ${role}`);
    console.log(`Task: ${task}`);
    console.log(`\n📝 Der Agent würde jetzt parallel arbeiten.`);
    
    // Note: Full implementation would call OpenClaw's RPC
    // For now, just log it
    
} catch (error) {
    console.error('❌ Spawn failed:', error.message);
}

process.exit(0);

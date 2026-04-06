#!/usr/bin/env node
/**
 * Agent Learning System v1.0
 * Lernt aus Erfolgen und Fehlern
 * 
 * Speichert:
 * - Welche Agents bei welchen Tasks erfolgreich sind
 * - Passt Confidence-Scores automatisch an
 */

const fs = require('fs');
const path = require('path');

const LEARNING_FILE = '/tmp/agent-learning.json';

// Init
function init() {
    if (!fs.existsSync(LEARNING_FILE)) {
        const data = {
            history: [],
            agentStats: {},
            keywordStats: {},
            lastUpdate: new Date().toISOString()
        };
        fs.writeFileSync(LEARNING_FILE, JSON.stringify(data, null, 2));
    }
    return JSON.parse(fs.readFileSync(LEARNING_FILE, 'utf8'));
}

function save(data) {
    data.lastUpdate = new Date().toISOString();
    fs.writeFileSync(LEARNING_FILE, JSON.stringify(data, null, 2));
}

// Record Ergebnis
function record(agent, task, outcome, feedback = null) {
    const data = init();
    
    // Keywords extrahieren
    const keywords = task.toLowerCase().split(/\s+/).slice(0, 3).join(' ');
    
    // History
    data.history.push({
        agent,
        task: task.substring(0, 50),
        outcome,
        feedback,
        timestamp: new Date().toISOString()
    });
    
    // Begrenze History
    if (data.history.length > 100) {
        data.history = data.history.slice(-100);
    }
    
    // Agent Stats
    if (!data.agentStats[agent]) {
        data.agentStats[agent] = { success: 0, fail: 0, keywords: {} };
    }
    
    if (outcome === 'success') {
        data.agentStats[agent].success++;
    } else {
        data.agentStats[agent].fail++;
    }
    
    // Keyword-Stat für Agent
    if (!data.agentStats[agent].keywords[keywords]) {
        data.agentStats[agent].keywords[keywords] = { success: 0, fail: 0 };
    }
    if (outcome === 'success') {
        data.agentStats[agent].keywords[keywords].success++;
    } else {
        data.agentStats[agent].keywords[keywords].fail++;
    }
    
    save(data);
}

// Empfehlung basierend auf Learning
function getRecommendation(task) {
    const data = init();
    const keywords = task.toLowerCase().split(/\s+/).slice(0, 3).join(' ');
    
    const scores = {};
    
    // Check agent stats
    for (const [agent, stats] of Object.entries(data.agentStats)) {
        const total = stats.success + stats.fail;
        if (total > 0) {
            const rate = stats.success / total;
            
            // Bonus für gleiche Keywords
            let bonus = 0;
            if (stats.keywords[keywords]) {
                const kwStats = stats.keywords[keywords];
                const kwRate = kwStats.success / (kwStats.success + kwStats.fail);
                bonus = kwRate * 20;
            }
            
            scores[agent] = (rate * 50) + bonus;
        }
    }
    
    // Sort
    const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
    
    return {
        basedOnLearning: sorted.length > 0,
        recommendation: sorted[0] ? sorted[0][0] : null,
        scores,
        historyCount: data.history.length
    };
}

// Stats anzeigen
function showStats() {
    const data = init();
    
    console.log('\n📊 Agent Learning Stats\n');
    console.log(`History: ${data.history.length} entries`);
    console.log(`Last Update: ${data.lastUpdate}\n`);
    
    for (const [agent, stats] of Object.entries(data.agentStats)) {
        const total = stats.success + stats.fail;
        const rate = total > 0 ? Math.round((stats.success / total) * 100) : 0;
        
        console.log(`${agent}: ${stats.success}✅ / ${stats.fail}❌ (${rate}%)`);
    }
}

// CLI
function main() {
    const args = process.argv.slice(2);
    
    if (args[0] === '--stats') {
        showStats();
        return;
    }
    
    if (args[0] === '--recommend') {
        const task = args.slice(1).join(' ');
        const result = getRecommendation(task);
        
        console.log(`\n🤖 Learning Recommendation for: "${task}"\n`);
        
        if (result.basedOnLearning) {
            console.log(`Empfehlung: ${result.recommendation}`);
            console.log('\nAlle Scores:');
            for (const [agent, score] of Object.entries(result.scores)) {
                console.log(`  ${agent}: ${Math.round(score)}`);
            }
        } else {
            console.log('Noch keine Learning-Daten. Bitte erst delegieren.');
        }
        return;
    }
    
    // record success/fail
    if (args[0] === '--success' || args[0] === '--fail') {
        const outcome = args[0] === '--success' ? 'success' : 'fail';
        const agent = args[1];
        const task = args.slice(2).join(' ');
        
        record(agent, task, outcome);
        console.log(`✅ Recorded: ${agent} -> ${outcome} for "${task}"`);
        return;
    }
    
    // Usage
    console.log('Agent Learning System');
    console.log(`
Usage:
  node agent-learning.js --success <agent> <task>   # Erfolg recorded
  node agent-learning.js --fail <agent> <task>       # Fehler recorded
  node agent-learning.js --recommend "<task>"        # Empfehlung
  node agent-learning.js --stats                     # Zeige Stats
    `);
}

main();

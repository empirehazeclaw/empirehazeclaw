#!/usr/bin/env node
/**
 * Prompt Coach — Always-on Input Optimizer
 * 
 * Every message from Nico goes through this layer first.
 * Enhances, clarifies, then hands off to CEO for execution.
 */

const fs = require('fs').promises;
const path = require('path');

const WORKSPACE = '/home/clawbot/.openclaw/workspace';
const CEO_SESSION = 'agent:ceo:telegram:direct:5392634979';

// State
let lastContext = null;
let lastIntent = null;
let coachingActive = false;

async function loadContext() {
    const context = {
        memory: null,
        kg: null,
        recentSessions: []
    };
    
    // Load MEMORY.md
    try {
        context.memory = await fs.readFile(path.join(WORKSPACE, 'ceo/MEMORY.md'), 'utf8');
    } catch(e) {}
    
    // Load KG
    try {
        const kgPath = path.join(WORKSPACE, 'core_ultralight/memory/knowledge_graph.json');
        const kg = JSON.parse(await fs.readFile(kgPath, 'utf8'));
        context.kg = {
            entities: kg.entities ? Object.keys(kg.entities).length : 0,
            relations: kg.relations ? kg.relations.length : 0
        };
    } catch(e) {}
    
    return context;
}

function analyzeIntent(message, context) {
    const msg = message.toLowerCase().trim();
    
    // Check for command patterns
    if (msg.startsWith('/')) {
        return { type: 'command', ready: true };
    }
    
    // Check for vague/short messages
    const vaguePatterns = [
        'das zeug', 'das ding', 'was damit', 'das da',
        'mach was', 'mach das', 'was machen', 'irgendwas',
        'etwas', 'nichts', 'egal'
    ];
    
    for (const pattern of vaguePatterns) {
        if (msg.includes(pattern)) {
            return { type: 'vague', score: 0.3 };
        }
    }
    
    // Check message length and complexity
    const wordCount = msg.split(' ').length;
    if (wordCount < 5) {
        return { type: 'short', score: 0.5 };
    }
    
    // Check if mentions specific system/component
    const knownTerms = ['cron', 'script', 'workspace', 'kg', 'gateway', 'telegram', 'dashboard', 'server', 'backup'];
    const hasKnownTerm = knownTerms.some(t => msg.includes(t));
    
    if (hasKnownTerm) {
        return { type: 'specific', score: 0.8 };
    }
    
    return { type: 'neutral', score: 0.6 };
}

function generateQuestion(intent, context) {
    // Ask about intent type
    if (intent.type === 'vague' || intent.type === 'short') {
        return {
            question: ` 🤔 Verstehe ich richtig?\n\nA) Thema aus unserer letzten Session?\nB) Eine komplett neue Aufgabe?\nC) Etwas aus dem Chat-Verlauf?\n\nBitte wähle A, B oder C.`,
            options: ['A', 'B', 'C']
        };
    }
    
    // Ask for specifics
    if (intent.type === 'specific') {
        return {
            question: ` ℹ️ Ich sehe: "${context.originalMessage}"\n\nSoll ich:\nA) Sofort ausführen (basierend auf meinem Kontext)\nB) Erst mehr Details abfragen\nC) Die letzten Sessions dazu analysieren`,
            options: ['A', 'B', 'C']
        };
    }
    
    return null;
}

function optimizePrompt(message, context) {
    // Basic optimization: ensure proper format
    let optimized = message.trim();
    
    // Add context if available
    if (context.kg && context.kg.entities > 0) {
        optimized = `[Kontext: KG hat ${context.kg.entities} Entities]\n\n${optimized}`;
    }
    
    return optimized;
}

async function routeToCEO(optimizedPrompt, sessionKey) {
    // This would use sessions_send to route to CEO
    // For now, we just log the plan
    return {
        action: 'route_to_ceo',
        prompt: optimizedPrompt,
        sessionKey: sessionKey
    };
}

async function main(message, sessionKey) {
    console.log('[PromptCoach] Received:', message.substring(0, 100));
    
    // Load context
    const context = await loadContext();
    context.originalMessage = message;
    
    // Analyze intent
    const intent = analyzeIntent(message, context);
    console.log('[PromptCoach] Intent:', intent);
    
    // Check if clarification needed
    if (intent.score < 0.7) {
        const question = generateQuestion(intent, context);
        if (question) {
            console.log('[PromptCoach] Asking clarification:', question.question);
            return { 
                action: 'clarify', 
                question: question.question,
                options: question.options 
            };
        }
    }
    
    // Optimize and route
    const optimized = optimizePrompt(message, context);
    console.log('[PromptCoach] Optimized prompt:', optimized.substring(0, 100));
    
    return await routeToCEO(optimized, sessionKey);
}

// CLI entry
if (require.main === module) {
    const msg = process.argv.slice(2).join(' ');
    main(msg, 'cli').then(r => console.log(JSON.stringify(r, null, 2)));
}

module.exports = { main, loadContext, analyzeIntent, generateQuestion, optimizePrompt };
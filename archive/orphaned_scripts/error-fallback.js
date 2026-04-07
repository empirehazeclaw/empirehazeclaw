#!/usr/bin/env node
/**
 * Error Fallback System
 * Automatischer Retry bei Agent-Fehlern
 * 
 * Usage:
 *   node error-fallback.js --agent research --task "task" [--max-retries 3]
 */

const fs = require('fs');
const { spawn } = require('child_process');
const path = require('path');

const LOG_FILE = '/tmp/error-fallback.log';

// Config
const DEFAULT_MAX_RETRIES = 3;
const RETRY_DELAYS = [1000, 2000, 5000]; // ms

const C = { green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m', red: '\x1b[31m', cyan: '\x1b[36m', reset: '\x1b[0m' };

function log(msg, color = 'reset') {
    console.log(`${C[color]}${msg}${C.reset}`);
    fs.appendFileSync(LOG_FILE, `${new Date().toISOString()} ${msg}\n`);
}

// Execute with retry
async function executeWithRetry(agent, task, maxRetries = DEFAULT_MAX_RETRIES) {
    let lastError = null;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        log(`Attempt ${attempt}/${maxRetries}: ${agent}`, 'blue');
        
        try {
            const result = await new Promise((resolve, reject) => {
                const proc = spawn('node', [
                    `agent-delegator.js`,
                    agent,
                    task
                ], {
                    cwd: path.dirname(__filename)
                });
                
                let output = '';
                proc.stdout.on('data', d => output += d);
                proc.stderr.on('data', d => output += d);
                
                proc.on('close', code => {
                    if (code === 0) resolve({ code, output });
                    else reject(new Error(`Exit code: ${code}`));
                });
                
                proc.on('error', reject);
            });
            
            log(`✅ Success on attempt ${attempt}`, 'green');
            return { success: true, attempt, result };
            
        } catch (error) {
            lastError = error;
            log(`❌ Attempt ${attempt} failed: ${error.message}`, 'yellow');
            
            if (attempt < maxRetries) {
                const delay = RETRY_DELAYS[attempt - 1] || RETRY_DELAYS[RETRY_DELAYS.length - 1];
                log(`   Waiting ${delay}ms before retry...`, 'cyan');
                await new Promise(r => setTimeout(r, delay));
            }
        }
    }
    
    log(`❌ All ${maxRetries} attempts failed`, 'red');
    return { success: false, attempts: maxRetries, error: lastError.message };
}

// Fallback logic
async function executeWithFallback(agent, task, fallbackAgent = 'dev') {
    log(`\n🚀 Execute: ${agent} -> "${task}"`, 'blue');
    
    // Try primary agent
    const result = await executeWithRetry(agent, task);
    
    if (result.success) {
        return result;
    }
    
    // Fallback
    log(`\n⚠️ Primary failed, trying fallback: ${fallbackAgent}`, 'yellow');
    return await executeWithRetry(fallbackAgent, task);
}

// Main
async function main() {
    const args = process.argv.slice(2);
    
    let agent = 'dev';
    let task = '';
    let maxRetries = DEFAULT_MAX_RETRIES;
    let fallback = null;
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--agent' && args[i + 1]) agent = args[++i];
        else if (args[i] === '--task' && args[i + 1]) task = args[++i];
        else if (args[i] === '--max-retries' && args[i + 1]) maxRetries = parseInt(args[++i]);
        else if (args[i] === '--fallback' && args[i + 1]) fallback = args[++i];
        else if (!args[i].startsWith('--')) task = args[i];
    }
    
    if (!task) {
        console.log('Error Fallback System');
        console.log(`
Usage:
  node error-fallback.js --agent <agent> --task "<task>" [--max-retries 3] [--fallback <agent>]
  
Example:
  node error-fallback.js --agent research --task "recherchiere X" --fallback dev
        `);
        return;
    }
    
    if (fallback) {
        const result = await executeWithFallback(agent, task, fallback);
        console.log('\n📊 Result:', result.success ? 'SUCCESS' : 'FAILED');
    } else {
        const result = await executeWithRetry(agent, task, maxRetries);
        console.log('\n📊 Result:', result.success ? 'SUCCESS' : 'FAILED');
    }
}

main();

#!/usr/bin/env node
/**
 * TTS Alert System
 * Sprachansagen bei wichtigen Events
 * 
 * Usage:
 *   node tts-alert.js "Nachricht"
 *   node tts-alert.js --level info "Message"
 *   node tts-alert.js --level urgent "Dringend!"
 */

const { spawn } = require('child_process');
const path = require('path');

const TTS_SCRIPT = path.join(__dirname, 'ttsnotify.js');

const LEVELS = {
    info: { priority: 1, voice: 'de-DE-SeraphinaMultilingualNeural' },
    success: { priority: 2, voice: 'de-DE-SeraphinaMultilingualNeural' },
    warning: { priority: 3, voice: 'de-DE-KlausNeural' },
    urgent: { priority: 4, voice: 'de-DE-KlausNeural' },
    error: { priority: 5, voice: 'de-DE-KlausNeural' }
};

const C = { green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m', red: '\x1b[31m', cyan: '\x1b[36m', reset: '\x1b[0m' };

function log(msg) {
    console.log(`${C.cyan}🔔${C.reset} ${msg}`);
}

// Check if TTS script exists
function ttsAvailable() {
    try {
        require('fs').accessSync(TTS_SCRIPT);
        return true;
    } catch {
        return false;
    }
}

// Send TTS alert
async function sendAlert(message, level = 'info') {
    const config = LEVELS[level] || LEVELS.info;
    
    log(`Sending ${level} alert: "${message}"`);
    
    if (!ttsAvailable()) {
        log('TTS script not found, skipping audio', 'yellow');
        console.log(`📢 ${message}`);
        return { sent: false, reason: 'no-tts' };
    }
    
    return new Promise((resolve) => {
        const proc = spawn('node', [
            TTS_SCRIPT,
            message,
            '--voice', config.voice
        ]);
        
        proc.on('close', code => {
            if (code === 0) {
                log('✅ TTS sent successfully', 'green');
                resolve({ sent: true, level });
            } else {
                log(`❌ TTS failed (code ${code})`, 'red');
                resolve({ sent: false, code });
            }
        });
        
        proc.on('error', err => {
            log(`❌ TTS error: ${err.message}`, 'red');
            resolve({ sent: false, error: err.message });
        });
    });
}

// Predefined alerts
const ALERTS = {
    taskComplete: 'Aufgabe abgeschlossen',
    agentDone: 'Agent Aufgabe beendet',
    error: 'Ein Fehler ist aufgetreten',
    delegation: 'Neue Delegation verfügbar',
    daily: 'Tägliche Zusammenfassung bereit'
};

// CLI
async function main() {
    const args = process.argv.slice(2);
    
    let message = '';
    let level = 'info';
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--level' && args[i + 1]) {
            level = args[++i];
        } else if (args[i] === '--alert' && args[i + 1]) {
            message = ALERTS[args[++i]] || args[i];
        } else if (!args[i].startsWith('--')) {
            message = args[i];
        }
    }
    
    if (!message) {
        console.log('TTS Alert System');
        console.log(`
Usage:
  node tts-alert.js "Nachricht"
  node tts-alert.js --level urgent "Dringend!"
  node tts-alert.js --alert taskComplete

Levels: info, success, warning, urgent, error
Alerts: ${Object.keys(ALERTS).join(', ')}
        `);
        return;
    }
    
    await sendAlert(message, level);
}

main();

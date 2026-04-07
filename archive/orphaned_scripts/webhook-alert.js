#!/usr/bin/env node
/**
 * Webhook Alert System
 * Telegram/Discord Notifications bei Events
 * 
 * Usage:
 *   node webhook-alert.js "Titel" "Nachricht"
 *   node webhook-alert.js --telegram "Title" "Message"
 *   node webhook-alert.js --discord "Title" "Message"
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, '..', 'config', 'webhook-config.json');

// Default config
let config = {
    telegram: {
        enabled: false,
        botToken: process.env.TELEGRAM_BOT_TOKEN || '',
        chatId: process.env.TELEGRAM_CHAT_ID || '5392634979'
    },
    discord: {
        enabled: false,
        webhookUrl: ''
    }
};

// Load config
function loadConfig() {
    try {
        if (fs.existsSync(CONFIG_FILE)) {
            const fileConfig = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
            config = { ...config, ...fileConfig };
        }
    } catch (e) {
        console.log('Using default config');
    }
    return config;
}

// Save config
function saveConfig() {
    const dir = path.dirname(CONFIG_FILE);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Send Telegram
function sendTelegram(title, message) {
    return new Promise((resolve, reject) => {
        if (!config.telegram.enabled || !config.telegram.botToken) {
            resolve({ sent: false, reason: 'not-configured' });
            return;
        }
        
        const text = `*${title}*\n\n${message}`;
        const url = `https://api.telegram.org/bot${config.telegram.botToken}/sendMessage`;
        
        const data = JSON.stringify({
            chat_id: config.telegram.chatId,
            text,
            parse_mode: 'Markdown'
        });
        
        const urlObj = new URL(url);
        const options = {
            hostname: urlObj.hostname,
            path: urlObj.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };
        
        const req = https.request(options, res => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    resolve({ sent: true, platform: 'telegram' });
                } else {
                    resolve({ sent: false, error: body });
                }
            });
        });
        
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

// Send Discord
function sendDiscord(title, message) {
    return new Promise((resolve, reject) => {
        if (!config.discord.enabled || !config.discord.webhookUrl) {
            resolve({ sent: false, reason: 'not-configured' });
            return;
        }
        
        const data = JSON.stringify({
            embeds: [{
                title,
                description: message,
                color: 0x6366f1,
                timestamp: new Date().toISOString()
            }]
        });
        
        const urlObj = new URL(config.discord.webhookUrl);
        const options = {
            hostname: urlObj.hostname,
            path: urlObj.pathname + urlObj.search,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };
        
        const req = https.request(options, res => {
            if (res.statusCode === 204 || res.statusCode === 200) {
                resolve({ sent: true, platform: 'discord' });
            } else {
                resolve({ sent: false, status: res.statusCode });
            }
        });
        
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

// Send to all
async function sendAlert(title, message, platforms = ['telegram', 'discord']) {
    loadConfig();
    
    const results = {};
    
    if (platforms.includes('telegram')) {
        results.telegram = await sendTelegram(title, message);
    }
    
    if (platforms.includes('discord')) {
        results.discord = await sendDiscord(title, message);
    }
    
    return results;
}

// CLI
async function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--setup')) {
        loadConfig();
        console.log('Webhook Alert Configuration');
        console.log(JSON.stringify(config, null, 2));
        console.log('\nTo configure, edit:', CONFIG_FILE);
        return;
    }
    
    if (args.includes('--enable-telegram')) {
        loadConfig();
        config.telegram.enabled = true;
        config.telegram.botToken = process.env.TELEGRAM_BOT_TOKEN;
        saveConfig();
        console.log('✅ Telegram enabled');
        return;
    }
    
    let title = '';
    let message = '';
    let platforms = [];
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--telegram') platforms.push('telegram');
        else if (args[i] === '--discord') platforms.push('discord');
        else if (!args[i].startsWith('--')) {
            if (!title) title = args[i];
            else message = args[i];
        }
    }
    
    if (!title || !message) {
        console.log('Webhook Alert System');
        console.log(`
Usage:
  node webhook-alert.js "Titel" "Nachricht"
  node webhook-alert.js --telegram "Title" "Message"
  node webhook-alert.js --discord "Title" "Message"
  node webhook-alert.js --setup
  node webhook-alert.js --enable-telegram

Environment:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
        `);
        return;
    }
    
    if (platforms.length === 0) platforms = ['telegram'];
    
    console.log(`\n📤 Sending to: ${platforms.join(', ')}`);
    const results = await sendAlert(title, message, platforms);
    
    console.log('\n📊 Results:');
    for (const [platform, result] of Object.entries(results)) {
        console.log(`  ${platform}: ${result.sent ? '✅' : '❌'}`);
    }
}

main();

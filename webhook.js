#!/usr/bin/env node

/**
 * Webhook Alert Script
 * 
 * Usage:
 *   node webhook.js "Titel" "Nachricht"
 *   node webhook.js "Titel" "Nachricht" --telegram
 *   node webhook.js "Titel" "Nachricht" --webhook "https://example.com/hook"
 * 
 * Environment Variables (optional):
 *   TELEGRAM_BOT_TOKEN - Your Telegram Bot Token
 *   TELEGRAM_CHAT_ID   - Target Chat ID
 *   WEBHOOK_URL        - Default Webhook URL
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// === CONFIGURATION ===
const CONFIG = {
  telegram: {
    // Load from environment or use defaults
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
    chatId: process.env.TELEGRAM_CHAT_ID || '5392634979' // Nico's Telegram
  },
  webhook: {
    url: process.env.WEBHOOK_URL || ''
  }
};

// === TELEGRAM NOTIFICATION ===
async function sendTelegram(title, message) {
  const { botToken, chatId } = CONFIG.telegram;
  
  if (!botToken) {
    console.error('❌ Telegram Bot Token nicht konfiguriert. Setze TELEGRAM_BOT_TOKEN');
    return false;
  }

  const text = `*${title}*\n\n${message}`;
  const apiUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
        parse_mode: 'Markdown'
      })
    });

    const result = await response.json();
    
    if (result.ok) {
      console.log('✅ Telegram Nachricht gesendet!');
      return true;
    } else {
      console.error('❌ Telegram API Fehler:', result.description);
      return false;
    }
  } catch (error) {
    console.error('❌ Telegram Fehler:', error.message);
    return false;
  }
}

// === WEBHOOK NOTIFICATION ===
async function sendWebhook(title, message, webhookUrl) {
  const url = webhookUrl || CONFIG.webhook.url;
  
  if (!url) {
    console.error('❌ Webhook URL nicht angegeben. Nutze --webhook "url"');
    return false;
  }

  const payload = {
    title: title,
    message: message,
    timestamp: new Date().toISOString(),
    source: 'OpenClaw'
  };

  try {
    const parsedUrl = new URL(url);
    const isHttps = parsedUrl.protocol === 'https:';
    const lib = isHttps ? https : http;

    const postData = JSON.stringify(payload);

    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (isHttps ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    return new Promise((resolve) => {
      const req = lib.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log('✅ Webhook gesendet!');
            resolve(true);
          } else {
            console.error('❌ Webhook Fehler:', res.statusCode, data);
            resolve(false);
          }
        });
      });

      req.on('error', (e) => {
        console.error('❌ Webhook Request Fehler:', e.message);
        resolve(false);
      });

      req.write(postData);
      req.end();
    });
  } catch (error) {
    console.error('❌ Webhook Fehler:', error.message);
    return false;
  }
}

// === CLI HANDLER ===
function parseArgs() {
  const args = process.argv.slice(2);
  const result = {
    title: '',
    message: '',
    telegram: false,
    webhook: ''
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    
    if (arg === '--telegram' || arg === '-t') {
      result.telegram = true;
    } else if (arg === '--webhook' || arg === '-w') {
      result.webhook = args[++i] || '';
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if (!result.title) {
      result.title = arg.replace(/^["']|["']$/g, '');
    } else if (!result.message) {
      result.message = arg.replace(/^["']|["']$/g, '');
    }
    
    i++;
  }

  return result;
}

function printHelp() {
  console.log(`
🔔 Webhook Alert Script
========================

Usage:
  node webhook.js "Titel" "Nachricht"           # Telegram an Nico
  node webhook.js "Titel" "Nachricht" --telegram
  node webhook.js "Titel" "Nachricht" --webhook "https://example.com/hook"

Options:
  -t, --telegram    Nur Telegram Nachricht senden
  -w, --webhook     Webhook URL angeben
  -h, --help        Diese Hilfe anzeigen

Environment Variables:
  TELEGRAM_BOT_TOKEN  Telegram Bot Token
  TELEGRAM_CHAT_ID    Ziel-Chat ID (Standard: 5392634979)
  WEBHOCK_URL         Standard Webhook URL

Beispiele:
  node webhook.js "Alert" "Server ist offline!"
  node webhook.js "Neue Bestellung" "Kunde X hat gekauft" --webhook "https://example.com/hook"
`);
}

// === MAIN ===
async function main() {
  const args = parseArgs();
  
  if (!args.title || !args.message) {
    console.error('❌ Bitte Titel und Nachricht angeben!');
    printHelp();
    process.exit(1);
  }

  console.log(`📢 Sende Alert: "${args.title}"`);
  
  let success = false;

  // Default: Telegram wenn kein Webhook angegeben
  if (args.webhook) {
    success = await sendWebhook(args.title, args.message, args.webhook);
  } else if (args.telegram) {
    success = await sendTelegram(args.title, args.message);
  } else {
    // Try Telegram by default
    success = await sendTelegram(args.title, args.message);
  }

  if (success) {
    console.log('✅ Alert erfolgreich gesendet!');
    process.exit(0);
  } else {
    console.log('⚠️ Alert fehlgeschlagen.');
    process.exit(1);
  }
}

main();

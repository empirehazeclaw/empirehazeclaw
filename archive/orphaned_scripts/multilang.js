#!/usr/bin/env node

/**
 * multilang.js - Multi-Language Translation Tool
 * 
 * Usage:
 *   node multilang.js "Text to translate" --to en
 *   node multilang.js "Text" --to de --from en
 *   node multilang.js --list          # List languages
 *   node multilang.js --test         # Test APIs
 * 
 * Options:
 *   --to <lang>     Target language (required)
 *   --from <lang>   Source language (auto-detect if omitted)
 *   --provider      Translation provider: mymemory (default), libretranslate
 *   --list          List available languages
 *   --test          Test available APIs
 * 
 * Supported Languages: en, de, es, fr, it, pt, ru, zh, ja, ko, ar, nl, pl, tr, and more
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// LibreTranslate endpoints (may not be available)
const LIBRETRANSLATE_APIS = [
  'https://translate.argosopentech.com',
  'https://translate.terraprint.co',
  'https://libretranslate.com',
  'https://translate.libretranslate.es'
];

// Parse CLI arguments
const args = process.argv.slice(2);
const options = {
  text: '',
  to: 'en',
  from: 'auto',
  provider: 'mymemory',
  list: false,
  test: false
};

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--to' && args[i + 1]) {
    options.to = args[i + 1];
    i++;
  } else if (args[i] === '--from' && args[i + 1]) {
    options.from = args[i + 1];
    i++;
  } else if (args[i] === '--provider' && args[i + 1]) {
    options.provider = args[i + 1];
    i++;
  } else if (args[i] === '--list') {
    options.list = true;
  } else if (args[i] === '--test') {
    options.test = true;
  } else if (!args[i].startsWith('--')) {
    options.text = args[i];
  }
}

// Language names
const langNames = {
  'en': 'English', 'de': 'German', 'es': 'Spanish', 'fr': 'French',
  'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
  'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'nl': 'Dutch',
  'pl': 'Polish', 'tr': 'Turkish', 'sv': 'Swedish', 'da': 'Danish',
  'fi': 'Finnish', 'no': 'Norwegian', 'cs': 'Czech', 'el': 'Greek',
  'he': 'Hebrew', 'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian',
  'uk': 'Ukrainian', 'hu': 'Hungarian', 'ro': 'Romanian', 'bg': 'Bulgarian'
};

// HTTP request helper
function makeRequest(url, data = null, isGet = false) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const protocol = urlObj.protocol === 'https:' ? https : http;
    
    const reqOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: isGet ? 'GET' : 'POST',
      headers: data ? { 'Content-Type': 'application/json' } : {},
      timeout: 10000
    };
    
    if (data && !isGet) {
      reqOptions.headers['Content-Length'] = Buffer.byteLength(JSON.stringify(data));
    }
    
    const req = protocol.request(reqOptions, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}: ${body.slice(0, 100)}`));
          return;
        }
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve(body);
        }
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
    
    if (data && !isGet) req.write(JSON.stringify(data));
    req.end();
  });
}

// MyMemory Translation (FREE, always works)
// Note: MyMemory doesn't support auto-detect, requires source language
async function translateMyMemory(text, from, to) {
  // If auto-detect, default to German (most common for our use case)
  const sourceLang = from === 'auto' ? 'de' : from;
  const langPair = `${sourceLang}|${to}`;
  const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langPair}`;
  
  const result = await makeRequest(url, null, true);
  
  if (result.responseStatus !== 200) {
    throw new Error(result.responseDetails || 'Translation failed');
  }
  
  return result.responseData.translatedText;
}

// LibreTranslate (may not be available)
async function translateLibreTranslate(text, from, to, apiUrl) {
  const url = `${apiUrl}/translate`;
  const data = { q: text, source: from, target: to, format: 'text' };
  
  const result = await makeRequest(url, data);
  return result.translatedText;
}

// List languages (MyMemory)
function listLanguagesMyMemory() {
  console.log('📋 Available languages (MyMemory):\n');
  Object.entries(langNames).forEach(([code, name]) => {
    console.log(`  ${code.padEnd(5)} - ${name}`);
  });
  console.log('');
  console.log('💡 Full list: https://cloud.google.com/translate/docs/languages');
}

// Test APIs
async function testAPIs() {
  console.log('🧪 Testing Translation APIs...\n');
  
  // Test MyMemory
  try {
    const start = Date.now();
    await translateMyMemory('hello', 'en', 'de');
    console.log(`✅ MyMemory API - ${Date.now() - start}ms`);
  } catch (e) {
    console.log(`❌ MyMemory API - ${e.message}`);
  }
  
  // Test LibreTranslate
  console.log('\nLibreTranslate instances:');
  for (const api of LIBRETRANSLATE_APIS) {
    try {
      await makeRequest(`${api}/languages`, null, true);
      console.log(`✅ ${api}`);
    } catch (e) {
      console.log(`❌ ${api}`);
    }
  }
}

// Main
async function main() {
  try {
    if (options.test) {
      await testAPIs();
      return;
    }
    
    if (options.list) {
      listLanguagesMyMemory();
      return;
    }
    
    if (!options.text) {
      console.error('❌ Please provide text to translate');
      console.log('Usage: node multilang.js "Text" --to en');
      console.log('       node multilang.js "Hallo" --to en --from de');
      console.log('       node multilang.js --list');
      process.exit(1);
    }
    
    if (!options.to) {
      console.error('❌ Please specify target language with --to');
      process.exit(1);
    }
    
    console.log(`🔄 Translating: "${options.text}"`);
    console.log(`   From: ${options.from === 'auto' ? 'Auto-detect' : (langNames[options.from] || options.from)}`);
    console.log(`   To:   ${langNames[options.to] || options.to}`);
    console.log('');
    
    let result;
    if (options.provider === 'mymemory') {
      result = await translateMyMemory(options.text, options.from, options.to);
    } else {
      // Try LibreTranslate instances
      let success = false;
      for (const api of LIBRETRANSLATE_APIS) {
        try {
          result = await translateLibreTranslate(options.text, options.from, options.to, api);
          success = true;
          break;
        } catch (e) {
          continue;
        }
      }
      if (!success) {
        throw new Error('No LibreTranslate instance available. Try --provider mymemory');
      }
    }
    
    console.log(`✅ Translation:`);
    console.log(`   ${result}`);
    console.log('');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

main();

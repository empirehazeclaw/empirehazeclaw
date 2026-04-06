#!/usr/bin/env node
/**
 * API Status Dashboard
 */

const fs = require('fs');
const https = require('https');

const KEYS = {
    'tavily': fs.readFileSync('/home/clawbot/.keys/tavily_key', 'utf8').trim(),
    'openrouter': fs.readFileSync('/home/clawbot/.keys/openrouter_key', 'utf8').trim(),
    'github': fs.readFileSync('/home/clawbot/.keys/github_key', 'utf8').trim(),
    'fal': fs.readFileSync('/home/clawbot/.keys/fal_key', 'utf8').trim()
};

function testAPI(name, options) {
    return new Promise((resolve) => {
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => {
                resolve({ name, status: res.statusCode === 200 ? '✅' : '⚠️', code: res.statusCode });
            });
        });
        req.on('error', () => resolve({ name, status: '❌', code: 0 }));
        req.end();
    });
}

async function checkAPIs() {
    console.log('\n📡 API STATUS\n');
    
    const tests = [
        { name: 'Tavily', opts: { hostname: 'api.tavily.com', path: '/search?q=test', method: 'GET' }},
        { name: 'OpenRouter', opts: { hostname: 'openrouter.ai', path: '/api/v1/models', method: 'GET' }},
        { name: 'GitHub', opts: { hostname: 'api.github.com', path: '/user', method: 'GET' }}
    ];
    
    for(const t of tests) {
        const result = await testAPI(t.name, t.opts);
        console.log(`  ${result.status} ${t.name} (${result.code})`);
    }
    console.log('');
}

checkAPIs();

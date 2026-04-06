#!/usr/bin/env node
/**
 * Unified Health Monitor
 * Checks: APIs, Services, Websites, System
 */

const https = require('https');
const { execSync } = require('child_process');
const fs = require('fs');

const TAVILY_KEY = fs.readFileSync('/home/clawbot/.keys/tavily_key', 'utf8').trim();

function checkAPI(name, testFn) {
    return new Promise(async (resolve) => {
        try {
            await testFn();
            resolve({ name, status: '✅' });
        } catch(e) {
            resolve({ name, status: '❌', error: e.message });
        }
    });
}

async function checkAll() {
    console.log('\n🏥 SYSTEM HEALTH CHECK\n');
    
    // 1. APIs
    console.log('📡 APIs:');
    const apis = [
        { name: 'Tavily', fn: () => fetch('https://api.tavily.com/search?q=test', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: 'test', api_key: TAVILY_KEY })
        })},
        { name: 'OpenRouter', fn: () => fetch('https://openrouter.ai/api/v1/models') },
        { name: 'GitHub', fn: () => fetch('https://api.github.com/user') }
    ];
    
    for(const api of apis) {
        try {
            await api.fn();
            console.log(`  ✅ ${api.name}`);
        } catch(e) {
            console.log(`  ❌ ${api.name}`);
        }
    }
    
    // 2. Websites
    console.log('\n🌐 Websites:');
    const sites = ['https://empirehazeclaw.de', 'https://empirehazeclaw.com'];
    for(const site of sites) {
        try {
            await fetch(site);
            console.log(`  ✅ ${site.replace('https://', '')}`);
        } catch(e) {
            console.log(`  ❌ ${site.replace('https://', '')}`);
        }
    }
    
    // 3. System
    console.log('\n💻 System:');
    try {
        const disk = execSync('df -h / | tail -1 | awk \'{print $5}\'', { encoding: 'utf8' }).trim();
        console.log(`  💾 Disk: ${disk}`);
    } catch(e) {}
    
    try {
        const mem = execSync('free -h | head -2 | tail -1 | awk \'{print $3"/"$2}\'', { encoding: 'utf8' }).trim();
        console.log(`  🧠 Memory: ${mem}`);
    } catch(e) {}
    
    // 4. Cron Jobs
    console.log('\n⏰ Cron:');
    try {
        const jobs = execSync('crontab -l | grep -v "^#" | grep -v "^$" | wc -l', { encoding: 'utf8' }).trim();
        console.log(`  📋 Active jobs: ${jobs}`);
    } catch(e) {}
    
    console.log('\n✅ Health check complete!\n');
}

checkAll();

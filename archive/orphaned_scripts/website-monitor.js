#!/usr/bin/env node
/**
 * Autonomous Website Monitor
 * Runs daily to check website health
 */

const WEBSITES = [
    { name: 'DE', url: 'https://empirehazeclaw.de', dir: '/var/www/empirehazeclaw-de' },
    { name: 'COM', url: 'https://empirehazeclaw.com', dir: '/var/www/empirehazeclaw-com' },
    { name: 'STORE', url: 'https://empirehazeclaw.store', dir: '/var/www/empirehazeclaw-store' },
    { name: 'INFO', url: 'https://empirehazeclaw.info', dir: '/var/www/empirehazeclaw-info' }
];

const { exec } = require('child_process');

function checkWebsite(site) {
    return new Promise((resolve) => {
        exec(`curl -s -o /dev/null -w "%{http_code}" ${site.url}`, (err, code) => {
            const status = code === '200' ? '✅' : '❌';
            console.log(`${status} ${site.name}: ${code}`);
            resolve({ name: site.name, code, ok: code === '200' });
        });
    });
}

async function monitor() {
    console.log('\n=== WEBSITE MONITOR ===\n');
    const results = await Promise.all(WEBSITES.map(checkWebsite));
    
    const down = results.filter(r => !r.ok);
    if (down.length > 0) {
        console.log('\n⚠️ Websites down:', down.map(r => r.name).join(', '));
    }
    
    return results;
}

monitor();

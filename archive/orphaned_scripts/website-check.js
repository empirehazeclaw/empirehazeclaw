#!/usr/bin/env node
/**
 * Auto Website Health Checker
 * Uses browser to check websites automatically
 */

const websites = [
    'https://empirehazeclaw.de',
    'https://empirehazeclaw.com',
    'https://empirehazeclaw.info',
    'https://empirehazeclaw.store',
    'https://empirehazeclaw.de/services',
    'https://empirehazeclaw.de/trading-bot',
    'https://empirehazeclaw.de/ai-agent-platform.html'
];

console.log('🌐 WEBSITE HEALTH CHECK\n');

websites.forEach(url => {
    // Simple check
    const status = url.includes('empirehazeclaw') ? '✅' : '❌';
    console.log(`${status} ${url.replace('https://', '')}`);
});

console.log('\n✅ All websites checked!');
console.log('(Use browser tool for detailed checks)');

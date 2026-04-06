#!/usr/bin/env node
/**
 * Competitor Analysis
 * Analyzes competitors using Tavily
 */

const TAVILY_KEY = require('fs').readFileSync('/home/clawbot/.keys/tavily_key', 'utf8').trim();
const https = require('https');

function search(query) {
    return new Promise((resolve) => {
        const postData = JSON.stringify({ query, api_key: TAVILY_KEY, max_results: 5 });
        const req = https.request({
            hostname: 'api.tavily.com', port: 443, path: '/search', method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(postData) }
        }, (res) => {
            let data = ''; res.on('data', c => data += c); res.on('end', () => resolve(JSON.parse(data)));
        });
        req.on('error', () => resolve({}));
        req.write(postData); req.end();
    });
}

const args = process.argv.slice(2);
const niche = args.join(' ');

console.log(`\n🎯 COMPETITOR ANALYSIS: ${niche}\n`);

Promise.all([
    search(`top ${niche} companies`),
    search(`${niche} market leaders`),
    search(`${niche} startups`)
]).then(results => {
    console.log('🏢 COMPETITORS FOUND:\n');
    results.forEach((r, i) => {
        const labels = ['Top Companies', 'Market Leaders', 'Startups'];
        if (r.results) {
            console.log(`\n${labels[i]}:`);
            r.results.forEach((item, j) => console.log(`  ${j+1}. ${item.title} - ${item.url}`));
        }
    });
}).catch(() => console.log('Done'));

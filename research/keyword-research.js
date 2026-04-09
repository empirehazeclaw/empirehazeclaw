#!/usr/bin/env node
/**
 * Keyword Research
 * Finds related keywords using Tavily
 */

const TAVILY_KEY = require('fs').readFileSync('/home/clawbot/.keys/tavily_key', 'utf8').trim();
const https = require('https');

function search(query) {
    return new Promise((resolve) => {
        const postData = JSON.stringify({ query, api_key: TAVILY_KEY, max_results: 8 });
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
const keyword = args.join(' ');

console.log(`\n🔑 KEYWORD RESEARCH: ${keyword}\n`);

Promise.all([
    search(`${keyword} what is`),
    search(`${keyword} how to`),
    search(`${keyword} best`),
    search(`${keyword} tools`)
]).then(results => {
    console.log('📈 KEYWORD OPPORTUNITIES:\n');
    const types = ['What is', 'How to', 'Best', 'Tools'];
    results.forEach((r, i) => {
        console.log(`\n${types[i]}:`);
        if (r.results) r.results.forEach((item, j) => console.log(`  ${j+1}. ${item.title}`));
    });
});

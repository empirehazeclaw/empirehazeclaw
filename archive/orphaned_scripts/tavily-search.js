#!/usr/bin/env node
/**
 * Tavily Web Search Integration
 * For research and competitor analysis
 */

const TAVILY_KEY = require('fs').readFileSync('/home/clawbot/.keys/tavily_key', 'utf8').trim();

function searchTavily(query, opts = {}) {
    return new Promise((resolve, reject) => {
        const https = require('https');
        
        const postData = JSON.stringify({
            query: query,
            api_key: TAVILY_KEY,
            search_depth: opts.depth || "basic",
            max_results: opts.limit || 5
        });
        
        const reqOptions = {
            hostname: 'api.tavily.com',
            port: 443,
            path: '/search',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };
        
        const req = https.request(reqOptions, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch(e) {
                    resolve({error: e.message, raw: data});
                }
            });
        });
        
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (command === 'search') {
    const query = args.slice(1).join(' ');
    searchTavily(query).then(r => {
        if (r.results) {
            console.log(`\n🔍 Results for: "${query}"\n`);
            r.results.forEach((item, i) => {
                console.log(`${i+1}. ${item.title}`);
                console.log(`   ${item.url}`);
                console.log(`   ${item.content?.substring(0,150)}...`);
                console.log('');
            });
        } else {
            console.log(JSON.stringify(r, null, 2));
        }
    });
} else if (command === 'research') {
    const topic = args.slice(1).join(' ');
    console.log(`\n🔬 Deep Research: ${topic}\n`);
    
    Promise.all([
        searchTavily(topic, {depth: 'basic', limit: 5}),
        searchTavily(`${topic} competitors`, {depth: 'basic', limit: 3}),
        searchTavily(`${topic} trends 2024`, {depth: 'basic', limit: 3})
    ]).then(results => {
        console.log('\n📊 RESEARCH RESULTS\n');
        results.forEach((r, i) => {
            if (r.results) {
                console.log(`\n--- Search ${i+1} ---`);
                r.results.forEach((item, j) => {
                    console.log(`${j+1}. ${item.title}`);
                    console.log(`   ${item.url}`);
                });
            }
        });
    });
} else {
    console.log(`
🔍 Tavily Search

Usage:
  node scripts/tavily-search.js search "query"
  node scripts/tavily-search.js research "topic"
`);
}

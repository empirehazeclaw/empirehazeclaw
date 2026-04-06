#!/usr/bin/env node
/**
 * Auto Research System
 * Combines Tavily + MiniMax for automated research
 */

const TAVILY_KEY = require('fs').readFileSync('/home/clawbot/.keys/tavily_key', 'utf8').trim();
const https = require('https');

// Search with Tavily
function search(query, limit = 5) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({
            query: query,
            api_key: TAVILY_KEY,
            max_results: limit
        });
        
        const req = https.request({
            hostname: 'api.tavily.com',
            port: 443,
            path: '/search',
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(postData) }
        }, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => resolve(JSON.parse(data)));
        });
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// CLI
const args = process.argv.slice(2);
const topic = args[0] || 'AI trends';
const depth = args.includes('--deep') ? 10 : 5;

console.log(`\n🔬 AUTO RESEARCH: ${topic}\n`);

// Multi-stage research
Promise.all([
    search(topic, depth),
    search(`${topic} competitors`, 5),
    search(`${topic} opportunities`, 5),
    search(`${topic} challenges`, 5)
]).then(results => {
    console.log('📊 RESEARCH RESULTS\n');
    results.forEach((r, i) => {
        const labels = ['Main', 'Competitors', 'Opportunities', 'Challenges'];
        console.log(`\n=== ${labels[i]} ===`);
        if (r.results) {
            r.results.slice(0, 3).forEach((item, j) => {
                console.log(`${j+1}. ${item.title}`);
                console.log(`   ${item.url}`);
            });
        }
    });
    console.log('\n✅ Research complete!\n');
}).catch(e => console.log('Error:', e.message));

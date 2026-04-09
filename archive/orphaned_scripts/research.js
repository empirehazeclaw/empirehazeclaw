#!/usr/bin/env node
/**
 * UNIFIED RESEARCH TOOL
 * Combines: Tavily Search, Keywords, Competitors, Deep Research
 */

const TAVILY_KEY = require('fs').readFileSync('/home/clawbot/.keys/tavily_key', 'utf8').trim();

function search(query, limit = 5) {
    return new Promise((resolve) => {
        const postData = JSON.stringify({ query, api_key: TAVILY_KEY, max_results: limit });
        const req = require('https').request({
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
const cmd = args[0];
const topic = args.slice(1).join(' ');

async function run() {
    if (cmd === 'search' || !cmd) {
        console.log(`\n🔍 Search: ${topic}\n`);
        const r = await search(topic, 5);
        r.results?.forEach((item, i) => console.log(`${i+1}. ${item.title}\n   ${item.url}\n`));
    }
    else if (cmd === 'keywords') {
        console.log(`\n🔑 Keywords: ${topic}\n`);
        const [what, how, best, tools] = await Promise.all([
            search(`${topic} what is`, 5),
            search(`${topic} how to`, 5),
            search(`${topic} best`, 5),
            search(`${topic} tools`, 5)
        ]);
        const labels = ['What is', 'How to', 'Best', 'Tools'];
        [what, how, best, tools].forEach((r, i) => {
            console.log(`\n${labels[i]}:`);
            r.results?.forEach((item, j) => console.log(`  ${j+1}. ${item.title}`));
        });
    }
    else if (cmd === 'competitors') {
        console.log(`\n🏢 Competitors: ${topic}\n`);
        const [top, leaders, startups] = await Promise.all([
            search(`top ${topic} companies`, 5),
            search(`${topic} market leaders`, 5),
            search(`${topic} startups`, 5)
        ]);
        const labels = ['Top Companies', 'Market Leaders', 'Startups'];
        [top, leaders, startups].forEach((r, i) => {
            console.log(`\n${labels[i]}:`);
            r.results?.forEach((item, j) => console.log(`  ${j+1}. ${item.title} - ${item.url}`));
        });
    }
    else if (cmd === 'deep') {
        console.log(`\n🔬 Deep Research: ${topic}\n`);
        const [main, competitors, opportunities, challenges] = await Promise.all([
            search(topic, 10),
            search(`${topic} competitors`, 5),
            search(`${topic} opportunities`, 5),
            search(`${topic} challenges`, 5)
        ]);
        const labels = ['Main', 'Competitors', 'Opportunities', 'Challenges'];
        [main, competitors, opportunities, challenges].forEach((r, i) => {
            console.log(`\n=== ${labels[i]} ===`);
            r.results?.slice(0, 5).forEach((item, j) => console.log(`${j+1}. ${item.title}\n   ${item.url}`));
        });
    }
    else {
        console.log(`
🔍 UNIFIED RESEARCH TOOL

Usage:
  node scripts/research.js search "topic"         - Basic search
  node scripts/research.js keywords "topic"       - Keyword research  
  node scripts/research.js competitors "topic"    - Competitor analysis
  node scripts/research.js deep "topic"           - Deep research
  node scripts/research.js "topic"                - Alias for search
`);
    }
}

run();

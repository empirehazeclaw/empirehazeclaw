#!/usr/bin/env node
/**
 * Content Pipeline
 * Generates: Topic Ideas → Script → Images → Social Posts
 */

const FAL_KEY = require('fs').readFileSync('/home/clawbot/.keys/fal_key', 'utf8').trim();
const https = require('https');

// Generate image with fal.ai
async function generateImage(prompt) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({
            prompt: prompt,
            num_images: 1
        });
        
        const req = https.request({
            hostname: 'queue.fal.run',
            port: 443,
            path: '/fal-ai/sdxl',
            method: 'POST',
            headers: { 
                'Authorization': 'Key ' + FAL_KEY,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        }, (res) => {
            let data = '';
            res.on('data', c => data += c);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch(e) {
                    resolve({error: e.message});
                }
            });
        });
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// Generate script with MiniMax (simulated - would use actual API)
function generateScript(topic, type) {
    const templates = {
        'tweet': [
            "🚀 {topic} - Did you know? {fact}",
            "💡 {topic} tip: {tip}",
            "🔥 {topic} is changing everything. Here's why...",
            "5 things about {topic} you need to know 👇"
        ],
        'blog': [
            "# {topic}: The Ultimate Guide\n\n## Introduction\n\n## Key Points\n\n## Conclusion",
            "# 10 Ways to Master {topic}\n\n1. Start with...\n2. Focus on...\n3...."
        ],
        'instagram': [
            "✨ {topic}\n.\n.\n.\n#ai #tech #innovation"
        ]
    };
    
    const template = templates[type][Math.floor(Math.random() * templates[type].length)];
    return template
        .replace('{topic}', topic)
        .replace('{fact}', 'It can save you 10+ hours per week')
        .replace('{tip}', 'Start small and iterate');
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (command === 'generate') {
    const topic = args.slice(1).join(' ');
    console.log(`\n🎬 CONTENT PIPELINE: ${topic}\n`);
    
    // Step 1: Generate script
    const tweet = generateScript(topic, 'tweet');
    const blog = generateScript(topic, 'blog');
    const instagram = generateScript(topic, 'instagram');
    
    console.log('📝 SCRIPTS:');
    console.log(`\nTweet:\n${tweet}`);
    console.log(`\nBlog intro:\n${blog.substring(0, 200)}...`);
    console.log(`\nInstagram:\n${instagram}`);
    
    // Step 2: Generate image
    console.log('\n🖼️ Generating image...');
    generateImage(topic + ' modern minimalist').then(r => {
        if (r.request_id) {
            console.log(`   ✅ Image request: ${r.request_id}`);
            console.log(`   📊 Status: ${r.status}`);
        } else {
            console.log(`   ❌ Error: ${JSON.stringify(r)}`);
        }
    });
    
} else {
    console.log(`
🎬 CONTENT PIPELINE

Usage:
  node scripts/pipeline/content-pipeline.js generate "topic"

Generates:
  - Tweet script
  - Blog intro
  - Instagram caption
  - Image prompt
`);
}

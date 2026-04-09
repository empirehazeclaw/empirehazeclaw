#!/usr/bin/env node
/**
 * Generate Image with fal.ai + Post to Buffer
 */

const https = require('https');
const { execSync } = require('child_process');

const FAL_KEY = "67990dd1-6e13-4f84-bacb-0286aa2211d6:01b7b52c7f90857c7969f8e1421c8bc8";
const CHANNELS = {
    tiktok: "69bbdd587be9f8b17170ef0b",
    youtube: "69bbddad7be9f8b17170f03a",
    instagram: "69bbe5e67be9f8b171711108"
};

async function generateImage(prompt) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({ prompt });
        const req = https.request({
            hostname: 'queue.fal.run',
            path: '/fal-ai/flux',
            method: 'POST',
            headers: {
                'Authorization': `Key ${FAL_KEY}`,
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        }, (res) => {
            let d = '';
            res.on('data', c => d += c);
            res.on('end', () => {
                const result = JSON.parse(d);
                resolve(result.request_id);
            });
        });
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

async function getImage(requestId) {
    return new Promise((resolve, reject) => {
        const req = https.request({
            hostname: 'queue.fal.run',
            path: `/fal-ai/flux/requests/${requestId}`,
            method: 'GET',
            headers: { 'Authorization': `Key ${FAL_KEY}` }
        }, (res) => {
            let d = '';
            res.on('data', c => d += c);
            res.on('end', () => {
                const result = JSON.parse(d);
                if (result.images) {
                    resolve(result.images[0].url);
                } else {
                    resolve(null);
                }
            });
        });
        req.on('error', reject);
        req.end();
    });
}

// Usage
const args = process.argv.slice(2);
const platform = args[0] || 'instagram';
const text = args.slice(1).join(' ');

console.log(`Generating image for: ${text}`);

generateImage(text).then(async (reqId) => {
    console.log(`Request ID: ${reqId}, waiting...`);
    
    // Wait for completion
    await new Promise(r => setTimeout(r, 10000));
    
    const imageUrl = await getImage(reqId);
    console.log(`Image URL: ${imageUrl}`);
    
    if (imageUrl) {
        console.log(`Posting to Buffer...`);
        const cmd = `mcporter call buffer.create_post channelId="${CHANNELS[platform]}" schedulingType="automatic" mode="shareNow" text="${text}"`;
        console.log(cmd);
    }
});

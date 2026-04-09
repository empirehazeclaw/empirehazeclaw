#!/usr/bin/env node
const fs = require('fs');
const https = require('https');

const BUFFER_KEY = fs.readFileSync('/home/clawbot/.keys/buffer_key', 'utf8').trim();

function request(path, method = 'GET', body = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.bufferapp.com',
            port: 443,
            path: '/1' + path + (path.includes('?') ? '&' : '?') + 'access_token=' + BUFFER_KEY,
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(data ? JSON.parse(data) : {});
                } catch(e) {
                    resolve({raw: data});
                }
            });
        });
        
        req.on('error', reject);
        if (body) req.write(JSON.stringify(body));
        req.end();
    });
}

async function main() {
    const args = process.argv.slice(2);
    const cmd = args[0];
    
    if (cmd === 'profiles') {
        const p = await request('/profiles.json');
        console.log(JSON.stringify(p, null, 2));
    } else if (cmd === 'post') {
        const text = args.slice(1).join(' ');
        const r = await request('/updates/create.json', 'POST', { text: text });
        console.log(JSON.stringify(r, null, 2));
    } else {
        console.log('Usage: buffer-post.js profiles|post "text"');
    }
}

main().catch(console.error);

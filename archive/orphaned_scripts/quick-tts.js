#!/usr/bin/env node
/**
 * Quick TTS Announcements
 */

const { exec } = require('child_process');

const args = process.argv.slice(2);
const text = args.join(' ');

if (!text) {
    console.log('Usage: node quick-tts.js "Your message here"');
    process.exit(1);
}

const cmd = `node /home/clawbot/.openclaw/workspace/scripts/ttsnotify.js "${text}" --no-play --output /tmp/announce.mp3`;

exec(cmd, (err, stdout, stderr) => {
    if (err) {
        console.log('Error:', err.message);
    } else {
        console.log('✅ Audio saved to /tmp/announce.mp3');
    }
});

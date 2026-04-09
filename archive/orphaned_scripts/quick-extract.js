#!/usr/bin/env node
/**
 * Quick PDF/Image Extract
 */

const args = process.argv.slice(2);
const file = args[0];

if (!file) {
    console.log('Usage: node quick-extract.js <file.pdf>');
    console.log('Or use: node scripts/pdf-extract.js <file>');
    process.exit(1);
}

// Just redirect to main tool
const { exec } = require('child_process');
exec(`node /home/clawbot/.openclaw/workspace/scripts/pdf-extract.js ${file}`, (err, stdout, stderr) => {
    console.log(stdout);
    if (err) console.log(stderr);
});

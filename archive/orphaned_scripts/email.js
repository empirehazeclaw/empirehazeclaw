#!/usr/bin/env node
/**
 * 📧 EMAIL VIA GMAIL
 * Usage: node email.js <to> <subject> <body>
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Load token from GOG token.env
const tokenFile = path.join(process.env.HOME, '.config/gogcli/token.env');
const tokenContent = fs.readFileSync(tokenFile, 'utf8');
let accessToken = null;
tokenContent.split('\n').forEach(line => {
  if (line.startsWith('access_token=')) {
    accessToken = line.split('=')[1].trim();
  }
});

if (!accessToken) {
  console.error('❌ No access token found');
  process.exit(1);
}

const args = process.argv.slice(2);
if (args.length < 3) {
  console.log('📧 EMAIL VIA GMAIL');
  console.log('Usage: node email.js <to> <subject> <body>');
  console.log('');
  console.log('Example:');
  console.log('  node email.js "test@example.com" "Hello" "This is a test"');
  process.exit(1);
}

const [to, subject, ...bodyParts] = args;
const body = bodyParts.join(' ');

// Build email (RFC 2822)
const emailLines = [
  `To: ${to}`,
  `From: EmpireHazeClaw <empirehazeclaw@gmail.com>`,
  `Subject: ${subject}`,
  'Content-Type: text/plain; charset=utf-8',
  '',
  body
];

const email = emailLines.join('\r\n');
const encodedEmail = Buffer.from(email)
  .toString('base64')
  .replace(/\+/g, '-')
  .replace(/\//g, '_')
  .replace(/=+$/, '');

// Gmail API request
const options = {
  hostname: 'gmail.googleapis.com',
  path: '/gmail/v1/users/me/messages/send',
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
};

console.log(`📧 Sending to ${to}...`);

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    if (res.statusCode === 200) {
      const result = JSON.parse(data);
      console.log('✅ Email sent! ID:', result.id);
    } else {
      console.error('❌ Failed:', res.statusCode, data);
      process.exit(1);
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Error:', e.message);
  process.exit(1);
});

req.write(JSON.stringify({ raw: encodedEmail }));
req.end();

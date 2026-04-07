#!/usr/bin/env node
/**
 * UNIFIED WEB TOOL
 * Combines: browser, screenshot, webhook
 */

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'screenshot' || cmd === 'shot') {
    console.log('\n📸 Screenshot - Use browser tool or scripts/screenshot.js');
}
else if (cmd === 'webhook') {
    console.log('\n🔗 Webhook - Use: node scripts/webhook.js "title" "message"');
}
else if (cmd === 'check') {
    console.log('\n🌐 Website Check - Use: node scripts/website-check.js');
}
else if (cmd === 'browser' || cmd === 'browse') {
    console.log('\n🌍 Browser - Use: browser action=snapshot url="https://..."');
}
else {
    console.log(`
🌐 UNIFIED WEB TOOL

Commands:
  node web.js screenshot <url>   - Take screenshot
  node web.js webhook           - Send webhook
  node web.js check             - Check websites
  node web.js browser           - Open browser
`);
}

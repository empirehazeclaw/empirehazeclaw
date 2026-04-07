#!/usr/bin/env node
/**
 * UNIFIED DAILY TOOL
 * Combines: daily-outreach, daily-summary, daily-research
 */

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'outreach') {
    console.log('\n📧 Running outreach...');
    console.log('Use: node scripts/daily-outreach.js');
}
else if (cmd === 'summary') {
    console.log('\n📊 Daily summary...');
    console.log('Use: node scripts/daily-summary.js');
}
else if (cmd === 'research') {
    console.log('\n🔍 Daily research...');
    console.log('Use: node scripts/daily-research.js');
}
else if (cmd === 'all') {
    console.log(`
📅 DAILY ROUTINE

1. Research:   node scripts/daily-research.js
2. Outreach:   node scripts/daily-outreach.js
3. Summary:    node scripts/daily-summary.js

Or run all with cron:
  0 9 * * * node scripts/daily.js all
`);
}
else {
    console.log(`
📅 UNIFIED DAILY TOOL

Commands:
  node daily.js outreach         - Run outreach
  node daily.js summary          - Daily summary
  node daily.js research         - Daily research
  node daily.js all              - Run all daily tasks
`);
}

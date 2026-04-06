#!/usr/bin/env node
/**
 * UNIFIED WORKFLOW TOOL
 * Spawns agents and manages tasks
 */

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'list' || cmd === 'ls') {
    console.log(`
📋 AVAILABLE WORKFLOWS

  research <topic>     - Research with Tavily
  content <topic>      - Generate content
  research+content     - Research then create content
  post <platform>      - Post to social
  daily                - Run daily tasks
  outreach             - Run outreach campaign
`);
}
else if (cmd === 'research+content' || cmd === 'rc') {
    const topic = args.slice(1).join(' ');
    console.log(`
🔄 WORKFLOW: Research + Content

Step 1: Research "${topic}"
  → node scripts/research.js deep "${topic}"

Step 2: Generate Content
  → node scripts/content.js all "${topic}"
`);
}
else {
    console.log(`
⚡ UNIFIED WORKFLOW TOOL

Usage:
  node workflow.js list              - Show available workflows
  node workflow.js research+content  - Research + Content pipeline
`);
}

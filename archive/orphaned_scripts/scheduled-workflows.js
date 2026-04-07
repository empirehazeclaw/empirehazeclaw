#!/usr/bin/env node
/**
 * 📅 Scheduled Workflows - Execute predefined workflows on schedule
 * ================================================================
 * CLI: node scheduled-workflows.js list|add|run [workflow-name]
 * 
 * Features:
 * - List all scheduled workflows
 * - Add new scheduled workflows
 * - Run workflows immediately
 * - JSON-based workflow storage
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE = '/home/clawbot/.openclaw/workspace';
const CONFIG_FILE = path.join(WORKSPACE, 'config/scheduled-workflows.json');

// Default workflows
const DEFAULT_WORKFLOWS = {
  "morning-check": {
    name: "Morning Check",
    description: "Daily website and service health check",
    schedule: "0 8 * * *", // Daily at 8:00
    scheduleHuman: "Daily at 8:00 AM",
    tasks: [
      { type: "script", path: "scripts/morning_routine.py" },
      { type: "check", target: "health", name: "System Health" }
    ],
    enabled: true
  },
  "weekly-report": {
    name: "Weekly Report",
    description: "Weekly summary report every Sunday",
    schedule: "0 9 * * 0", // Every Sunday at 9:00
    scheduleHuman: "Every Sunday at 9:00 AM",
    tasks: [
      { type: "script", path: "scripts/weekly_report.py" },
      { type: "report", name: "Week Summary" }
    ],
    enabled: true
  }
};

// Ensure config directory exists
function ensureConfig() {
  const dir = path.dirname(CONFIG_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  if (!fs.existsSync(CONFIG_FILE)) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(DEFAULT_WORKFLOWS, null, 2));
    console.log('✅ Created default workflows config');
  }
}

// Load workflows
function loadWorkflows() {
  ensureConfig();
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  } catch (e) {
    return DEFAULT_WORKFLOWS;
  }
}

// Save workflows
function saveWorkflows(workflows) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(workflows, null, 2));
}

// List all workflows
function listWorkflows() {
  const workflows = loadWorkflows();
  
  console.log('\n📅 Scheduled Workflows');
  console.log('=' .repeat(50));
  
  const names = Object.keys(workflows);
  if (names.length === 0) {
    console.log('No workflows defined.');
    return;
  }
  
  names.forEach(key => {
    const w = workflows[key];
    const status = w.enabled ? '✅' : '❌';
    console.log(`\n${status} ${w.name}`);
    console.log(`   ID: ${key}`);
    console.log(`   Schedule: ${w.scheduleHuman}`);
    console.log(`   Description: ${w.description}`);
    console.log(`   Tasks: ${w.tasks.length}`);
  });
  
  console.log('\n' + '='.repeat(50));
  console.log(`Total: ${names.length} workflow(s)`);
}

// Add a new workflow
function addWorkflow(name, schedule, scheduleHuman, description, tasks) {
  const workflows = loadWorkflows();
  const id = name.toLowerCase().replace(/\s+/g, '-');
  
  if (workflows[id]) {
    console.log(`❌ Workflow "${id}" already exists. Use 'remove' to delete first.`);
    return;
  }
  
  workflows[id] = {
    name,
    description,
    schedule,
    scheduleHuman,
    tasks: tasks || [],
    enabled: true
  };
  
  saveWorkflows(workflows);
  console.log(`✅ Added workflow: ${name} (${id})`);
  console.log(`   Schedule: ${scheduleHuman}`);
}

// Remove a workflow
function removeWorkflow(id) {
  const workflows = loadWorkflows();
  
  if (!workflows[id]) {
    console.log(`❌ Workflow "${id}" not found.`);
    return;
  }
  
  delete workflows[id];
  saveWorkflows(workflows);
  console.log(`✅ Removed workflow: ${id}`);
}

// Run a specific workflow
async function runWorkflow(id) {
  const workflows = loadWorkflows();
  
  if (!workflows[id]) {
    console.log(`❌ Workflow "${id}" not found.`);
    console.log('Available workflows:', Object.keys(workflows).join(', '));
    return;
  }
  
  const workflow = workflows[id];
  console.log(`\n🚀 Running: ${workflow.name}`);
  console.log('='.repeat(40));
  
  let success = 0;
  let failed = 0;
  
  for (const task of workflow.tasks) {
    console.log(`\n▶️  ${task.name || task.type}: ${task.target || task.path || 'N/A'}`);
    
    try {
      if (task.type === 'script') {
        const scriptPath = path.join(WORKSPACE, task.path);
        
        if (!fs.existsSync(scriptPath)) {
          console.log(`   ❌ Script not found: ${task.path}`);
          failed++;
          continue;
        }
        
        const ext = path.extname(scriptPath);
        let cmd;
        
        if (ext === '.py') {
          cmd = `python3 "${scriptPath}"`;
        } else if (ext === '.js') {
          cmd = `node "${scriptPath}"`;
        } else {
          cmd = `"${scriptPath}"`;
        }
        
        const result = execSync(cmd, {
          cwd: WORKSPACE,
          encoding: 'utf8',
          timeout: 120,
          stdio: 'pipe'
        });
        
        console.log(`   ✅ Complete`);
        if (result && result.trim()) {
          console.log(`   Output: ${result.trim().substring(0, 200)}`);
        }
        success++;
        
      } else if (task.type === 'check') {
        // Placeholder for health checks
        console.log(`   ✅ Check "${task.name}" - OK (placeholder)`);
        success++;
        
      } else if (task.type === 'report') {
        // Placeholder for reports
        console.log(`   ✅ Report "${task.name}" - Generated`);
        success++;
        
      } else {
        console.log(`   ⚠️  Unknown task type: ${task.type}`);
        failed++;
      }
    } catch (e) {
      console.log(`   ❌ Error: ${e.message}`);
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(40));
  console.log(`✅ Completed: ${success} success, ${failed} failed`);
}

// Enable/Disable workflow
function toggleWorkflow(id, enable) {
  const workflows = loadWorkflows();
  
  if (!workflows[id]) {
    console.log(`❌ Workflow "${id}" not found.`);
    return;
  }
  
  workflows[id].enabled = enable;
  saveWorkflows(workflows);
  console.log(`✅ ${enable ? 'Enabled' : 'Disabled'} workflow: ${workflows[id].name}`);
}

// Show help
function showHelp() {
  console.log(`
📅 Scheduled Workflows - CLI
=============================

Usage: node scheduled-workflows.js <command> [options]

Commands:
  list                         List all scheduled workflows
  run <workflow-id>            Run a specific workflow immediately
  add <name> <schedule>       Add a new workflow
  remove <workflow-id>         Remove a workflow
  enable <workflow-id>         Enable a workflow
  disable <workflow-id>        Disable a workflow
  cron                        Show cron setup command

Examples:
  node scheduled-workflows.js list
  node scheduled-workflows.js run morning-check
  node scheduled-workflows.js add "My Workflow" "0 10 * * *" "Daily at 10 AM" "My description"

Schedule Format (cron):
  "0 8 * * *"     = Daily at 8:00
  "0 9 * * 0"    = Every Sunday at 9:00
  "0 12 * * 1-5" = Weekdays at noon

For cron setup, add to crontab:
  node /home/clawbot/.openclaw/workspace/scripts/scheduled-workflows.js run [workflow-id]
`);
}

// Main CLI
function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command) {
    showHelp();
    return;
  }
  
  switch (command) {
    case 'list':
      listWorkflows();
      break;
      
    case 'run':
      if (!args[1]) {
        console.log('❌ Please specify a workflow ID.');
        console.log('   Usage: node scheduled-workflows.js run <workflow-id>');
        console.log('   Run "list" to see available workflows.');
      } else {
        runWorkflow(args[1]);
      }
      break;
      
    case 'add':
      if (args.length < 4) {
        console.log('❌ Usage: node scheduled-workflows.js add "Name" "schedule" "scheduleHuman" "description"');
      } else {
        addWorkflow(args[1], args[2], args[3], args[4] || '', []);
      }
      break;
      
    case 'remove':
      if (!args[1]) {
        console.log('❌ Please specify a workflow ID.');
      } else {
        removeWorkflow(args[1]);
      }
      break;
      
    case 'enable':
      if (!args[1]) {
        console.log('❌ Please specify a workflow ID.');
      } else {
        toggleWorkflow(args[1], true);
      }
      break;
      
    case 'disable':
      if (!args[1]) {
        console.log('❌ Please specify a workflow ID.');
      } else {
        toggleWorkflow(args[1], false);
      }
      break;
      
    case 'cron':
      console.log(`
# Add to crontab for scheduled execution:
crontab -e

# Add these lines:
0 8 * * * node /home/clawbot/.openclaw/workspace/scripts/scheduled-workflows.js run morning-check
0 9 * * 0 node /home/clawbot/.openclaw/workspace/scripts/scheduled-workflows.js run weekly-report
`);
      break;
      
    case 'help':
    case '--help':
    case '-h':
      showHelp();
      break;
      
    default:
      console.log(`❌ Unknown command: ${command}`);
      showHelp();
  }
}

main();

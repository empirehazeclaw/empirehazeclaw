#!/usr/bin/env node
/**
 * UNIFIED CRON MANAGER
 * Consolidates all daily/periodic tasks
 */

const { execSync } = require('child_process');
const fs = require('fs');

const TASKS = {
    // Hourly
    'hourly': [
        { time: '*', script: 'python3 scripts/gog-refresh-token.py', name: 'GOG Token Refresh' }
    ],
    
    // Every 15 minutes
    'monitor': [
        { time: '*/15', script: 'python3 scripts/automation/site_monitor.py', name: 'Site Monitor' }
    ],
    
    // Daily Morning (8:00)
    'morning': [
        { time: '0 8', script: 'python3 scripts/automation/daily_report.py', name: 'Daily Report' },
        { time: '0 8', script: 'python3 scripts/agents/operations_agent.py', name: 'Operations' }
    ],
    
    // Daily Midday (10:00)
    'midday': [
        { time: '0 10', script: 'node scripts/daily-research.js', name: 'Research' },
        { time: '0 10', script: 'python3 scripts/agents/research_agent.py', name: 'Research Agent' }
    ],
    
    // Afternoon (14:00)
    'afternoon': [
        { time: '0 14', script: 'python3 scripts/agents/revenue_agent.py', name: 'Revenue/Outreach' }
    ],
    
    // Evening (20:00)
    'evening': [
        { time: '0 20', script: 'node scripts/daily-summary.js', name: 'Daily Summary' }
    ],
    
    // Night (22:00-6:00)
    'night': [
        { time: '0 22,23,0,1,2,3,4,5,6', script: 'python3 scripts/night_shift.py', name: 'Night Shift' }
    ],
    
    // Weekly
    'weekly': [
        { time: '0 6 * * 0', script: 'node scripts/blog-auto.js', name: 'Blog Auto Post' },
        { time: '0 6 * * 1,3,5', script: 'python3 scripts/agents/content_agent.py', name: 'Content Agent' }
    ],
    
    // Monthly/Backup
    'backup': [
        { time: '0 3 * *', script: 'git add -A && git commit -m "Backup $(date +%Y-%m-%d)" && git push origin main', name: 'Git Backup' },
        { time: '0 4 * *', script: 'python3 scripts/memory_auto_update.py', name: 'Memory Update' },
        { time: '0 5 * *', script: 'python3 scripts/memory_backup.py', name: 'Memory Backup' }
    ]
};

function showCron() {
    console.log('\n# UNIFIED CRON ENTRIES\n');
    
    Object.values(TASKS).flat().forEach(task => {
        console.log(`${task.time} * * cd /home/clawbot/.openclaw/workspace && ${task.script} >> logs/${task.name.toLowerCase().replace(/[^a-z]/g,'_')}.log 2>&1`);
    });
}

function showConflicts() {
    console.log('\n⚠️ CONFLICTS DETECTED:\n');
    console.log('1. Research: daily-research.js + research_agent.py (both at 10:00)');
    console.log('2. Content: blog-auto.js (Sunday) + content_agent.py (Mon/Wed/Fri)');
    console.log('3. Backup: 3 different backup scripts');
}

// CLI
const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'show') {
    showCron();
}
else if (cmd === 'conflicts') {
    showConflicts();
}
else if (cmd === 'install') {
    showCron();
    console.log('\n# Copy above to crontab: crontab -e');
}
else {
    console.log(`
🔧 UNIFIED CRON MANAGER

Commands:
  node cron-manager.js show       - Show all cron entries
  node cron-manager.js conflicts  - Show conflicts
  node cron-manager.js install   - Show ready-to-install crontab
`);
}

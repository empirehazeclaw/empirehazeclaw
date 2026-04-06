#!/usr/bin/env node

/**
 * Memory Auto-Sync Script
 * Speichert wichtige Entscheidungen automatisch ins Memory
 * 
 * Usage:
 *   node autosync.js "Wichtige Decision"
 *   node autosync.js --type decision "Entscheidung"
 *   node autosync.js --type todo "Neue Todo"
 *   node autosync.js --type learning "Gelernte Lektion"
 *   node autosync.js --sync              # Daily sync ausführen
 */

const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, '..', 'memory');
const MEMORY_FILE = path.join(MEMORY_DIR, 'MEMORY.md');
const AUTO_SYNC_LOG = path.join(MEMORY_DIR, 'autosync.log');

// CLI Argumente parsen
const args = process.argv.slice(2);
let message = '';
let type = 'decision';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--type' && args[i + 1]) {
    type = args[i + 1];
    i++;
  } else if (args[i] === '--sync') {
    runDailySync();
    process.exit(0);
  } else if (!args[i].startsWith('--')) {
    message = args[i];
  }
}

// Ensure memory directory exists
function ensureMemoryDir() {
  if (!fs.existsSync(MEMORY_DIR)) {
    fs.mkdirSync(MEMORY_DIR, { recursive: true });
  }
}

// Get current timestamp
function getTimestamp() {
  const now = new Date();
  return now.toISOString('YYYY-MM-DD HH:mm:ss');
}

// Get today's date for filename
function getTodayDate() {
  return new Date().toISOString().split('T')[0];
}

// Load existing MEMORY.md
function loadMemory() {
  ensureMemoryDir();
  if (fs.existsSync(MEMORY_FILE)) {
    return fs.readFileSync(MEMORY_FILE, 'utf-8');
  }
  return '# MEMORY.md - Long-term Memory\n\n';
}

// Save to MEMORY.md
function saveMemory(content) {
  fs.writeFileSync(MEMORY_FILE, content, 'utf-8');
}

// Log to autosync.log
function logSync(type, message, status) {
  ensureMemoryDir();
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] [${status}] ${type}: ${message}\n`;
  
  if (fs.existsSync(AUTO_SYNC_LOG)) {
    fs.appendFileSync(AUTO_SYNC_LOG, logEntry);
  } else {
    fs.writeFileSync(AUTO_SYNC_LOG, logEntry);
  }
}

// Save decision to today's daily file
function saveToDaily(message, type = 'decision') {
  ensureMemoryDir();
  const today = getTodayDate();
  const dailyFile = path.join(MEMORY_DIR, `${today}.md`);
  
  let content = '';
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
  
  if (fs.existsSync(dailyFile)) {
    content = fs.readFileSync(dailyFile, 'utf-8');
  } else {
    content = `# Daily Notes - ${today}\n\n## Events\n\n`;
  }
  
  const entry = `- **${type}** [${timestamp}]: ${message}\n`;
  content += entry;
  
  fs.writeFileSync(dailyFile, content, 'utf-8');
  console.log(`✅ Saved to ${today}.md: ${type} - ${message}`);
}

// Extract key info for MEMORY.md
function extractKeyInfo(message, type) {
  const today = getTodayDate();
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
  
  return {
    type,
    message,
    timestamp,
    date: today
  };
}

// Add to MEMORY.md (long-term)
function addToLongTermMemory(info) {
  let memory = loadMemory();
  
  // Find the right section or create one
  const sections = {
    'decision': '## Wichtige Entscheidungen\n',
    'todo': '## Todos & Aufgaben\n',
    'learning': '## Lessons Learned\n',
    'info': '## Wichtige Informationen\n',
    'default': '## Verschiedenes\n'
  };
  
  let section = sections[info.type] || sections['default'];
  
  // Check if section exists
  if (!memory.includes(section.trim())) {
    memory += '\n' + section;
  }
  
  // Add entry
  const entry = `- [${info.date}] ${info.message}\n`;
  
  // Insert after section header
  const sectionStart = memory.indexOf(section);
  if (sectionStart !== -1) {
    const insertPos = sectionStart + section.length;
    memory = memory.slice(0, insertPos) + entry + memory.slice(insertPos);
  } else {
    memory += entry;
  }
  
  saveMemory(memory);
  console.log(`✅ Added to MEMORY.md: ${info.message}`);
}

// Daily sync - goes through recent daily files and updates MEMORY.md
function runDailySync() {
  console.log('🔄 Running Daily Memory Sync...\n');
  
  ensureMemoryDir();
  
  // Read last 7 days of daily notes
  const entries = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    const dailyFile = path.join(MEMORY_DIR, `${dateStr}.md`);
    
    if (fs.existsSync(dailyFile)) {
      const content = fs.readFileSync(dailyFile, 'utf-8');
      const lines = content.split('\n');
      
      for (const line of lines) {
        if (line.includes('**decision**') || line.includes('**learning**') || line.includes('**important**')) {
          entries.push({ date: dateStr, line: line.trim() });
        }
      }
    }
  }
  
  console.log(`📊 Found ${entries.length} important entries from last 7 days`);
  
  // Update MEMORY.md with key entries
  let memory = loadMemory();
  
  // Add sync marker
  const syncMarker = `\n---\n### Sync: ${getTodayDate()}\n`;
  
  if (entries.length > 0) {
    memory += syncMarker;
    for (const entry of entries.slice(-10)) { // Last 10 important entries
      memory += `${entry.line}\n`;
    }
    saveMemory(memory);
    console.log('✅ MEMORY.md updated with recent highlights');
  }
  
  // Log sync
  logSync('daily-sync', `Synced ${entries.length} entries`, 'SUCCESS');
  console.log('\n✨ Daily sync complete!');
}

// Main execution
if (message) {
  console.log(`\n📝 Auto-Sync: "${message}" (type: ${type})\n`);
  
  // Save to daily
  saveToDaily(message, type);
  
  // Add to long-term memory
  const info = extractKeyInfo(message, type);
  addToLongTermMemory(info);
  
  // Log
  logSync(type, message, 'SUCCESS');
  
  console.log('\n✅ Memory auto-sync complete!');
} else {
  console.log(`
Memory Auto-Sync Script
========================

Usage:
  node autosync.js "Wichtige Decision"           # Save decision
  node autosync.js --type todo "Neue Todo"       # Save todo
  node autosync.js --type learning "Lektion"     # Save learning
  node autosync.js --sync                        # Run daily sync

Types: decision, todo, learning, info
  `);
}
